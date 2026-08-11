import { useEffect, useRef, useState } from 'react';
import type { SceneModel, SceneNode } from './sceneModel';

type AnyMapSdk = any;

type BaiduSceneMapProps = {
  ak: string;
  model: SceneModel;
};

function loadBaiduSdk(ak: string): Promise<AnyMapSdk> {
  if (typeof window === 'undefined') {
    return Promise.reject(new Error('Baidu map requires a browser'));
  }
  const existing = (window as any).BMapGL;
  if (existing) {
    return Promise.resolve(existing);
  }

  const callbackName = `__lraBaiduMapReady_${Date.now()}_${Math.random().toString(16).slice(2)}`;
  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    const timeout = window.setTimeout(() => {
      cleanup();
      reject(new Error('百度地图 SDK 加载超时'));
    }, 12000);
    const cleanup = () => {
      window.clearTimeout(timeout);
      delete (window as any)[callbackName];
      script.remove();
    };
    (window as any)[callbackName] = () => {
      cleanup();
      if ((window as any).BMapGL) {
        resolve((window as any).BMapGL);
      } else {
        reject(new Error('百度地图 SDK 未初始化'));
      }
    };
    script.async = true;
    script.onerror = () => {
      cleanup();
      reject(new Error('百度地图 SDK 加载失败，请检查 AK 和域名白名单'));
    };
    script.src = `https://api.map.baidu.com/api?v=1.0&type=webgl&ak=${encodeURIComponent(ak)}&callback=${callbackName}`;
    document.head.appendChild(script);
  });
}



// 大头针图标：白描边 + 顶部高光 + 白色圆点（锚点取针尖）
function markerSvg(color: string, focused: boolean): string {
  const d = focused ? 44 : 30;
  const c = d / 2;
  const R = focused ? 20 : 13.5;
  return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="${d}" height="${d}" viewBox="0 0 ${d} ${d}"><circle cx="${c}" cy="${c}" r="${R}" fill="${color}" opacity="0.9"/><circle cx="${c}" cy="${c}" r="${R}" fill="none" stroke="#ffffff" stroke-width="${focused ? 3 : 2.5}" stroke-opacity="0.95"/><circle cx="${c}" cy="${c}" r="${(R * 0.36).toFixed(2)}" fill="#ffffff" opacity="0.95"/></svg>`)}`;
}

// 地面脉冲环（HTML Overlay，带动画扩散）
let pulseCtorRef: any = null;
function makePulseOverlay(sdk: AnyMapSdk): any {
  function PulseOverlay(this: any, point: any, color: string) {
    this._point = point;
    this._color = color;
  }
  PulseOverlay.prototype = Object.assign(Object.create(sdk.Overlay.prototype), PulseOverlay.prototype);
  PulseOverlay.prototype.initialize = function (map: any) {
    this._map = map;
    const div = document.createElement('div');
    div.style.cssText = 'position:absolute;left:0;top:0;width:0;height:0;pointer-events:none;';
        div.innerHTML =
      `<span style="position:absolute;left:-24px;top:-24px;width:48px;height:48px;border-radius:50%;border:2.5px solid ${this._color};animation:lra-ping 1.8s ease-out infinite;"></span>`;
    map.getPanes().floatPane.appendChild(div);
    this._div = div;
    return div;
  };
  PulseOverlay.prototype.draw = function () {
    const p = this._map.pointToOverlayPixel(this._point);
    this._div.style.left = p.x + 'px';
    this._div.style.top = p.y + 'px';
  };
  return PulseOverlay;
}

function validNode(node: SceneNode): node is SceneNode & { latitude: number; longitude: number } {
  return typeof node.latitude === 'number' && typeof node.longitude === 'number';
}

export function BaiduSceneMap({ ak, model }: BaiduSceneMapProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const modelRef = useRef<SceneModel>(model);
  modelRef.current = model;
  const resizeHandlerRef = useRef<(() => void) | null>(null);
  const mapRef = useRef<AnyMapSdk | null>(null);
  const sdkRef = useRef<AnyMapSdk | null>(null);
  const markersRef = useRef<Map<string, any>>(new Map());
  const markerTargetsRef = useRef<Map<string, { lat: number; lng: number }>>(new Map());
  const polylineRefs = useRef<any[]>([]);
  const distanceCacheRef = useRef<Map<string, { meters: number; durationSec: number | null }>>(new Map());
  const labelLayerRef = useRef<HTMLDivElement | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [sdkReady, setSdkReady] = useState(false);

  // auto-frame: keep every point (and its move target) inside the view,
  // re-fitted on window resize so the set always fills the screen
  const fitView = () => {
    try {
      const sdk = sdkRef.current;
      const map = mapRef.current;
      if (!sdk || !map) {
        return;
      }
    const pts: any[] = [];
    for (const node of modelRef.current.nodes) {
      if (!validNode(node)) {
        continue;
      }
      pts.push(new sdk.Point(node.longitude, node.latitude));
      const mv = node.moveTarget;
      if (mv && typeof mv.latitude === "number" && typeof mv.longitude === "number") {
        pts.push(new sdk.Point(mv.longitude, mv.latitude));
      }
    }
    if (pts.length === 0) {
      return;
    }
    try {
      // 比例留白（基于容器尺寸）：顶部容纳立杆+大头针+标签，其余留呼吸边距
      const size = map.getSize?.();
      const W = size?.width || containerRef.current?.clientWidth || 1920;
      const H = size?.height || containerRef.current?.clientHeight || 1080;
      const margins = [
        Math.round(H * 0.12),  // top
        Math.round(W * 0.04),  // right
        Math.round(H * 0.05),  // bottom
        Math.round(W * 0.04),  // left
      ];
      map.setViewport(pts, { enableAnimation: false, margins });
    } catch {
      map.setViewport(pts, { enableAnimation: false });
    }
    } catch (err) {
      console.error("[SceneMap fitView]", err);
    }
  };

  // label placement with collision avoidance: compute screen positions via
  // pointToPixel, place labels greedily in 8 directions, fall back to a
  // leader line; rerun on map move/zoom/resize and model updates
  const renderLabels = () => {
    try {
      const sdk = sdkRef.current;
      const map = mapRef.current;
      const layer = labelLayerRef.current;
      if (!sdk || !map || !layer) {
        return;
      }
    const model = modelRef.current;
    const nodes = model.nodes.filter(validNode);
    if (nodes.length === 0) {
      return;
    }
    const W = layer.clientWidth || 1200;
    const H = layer.clientHeight || 800;
    layer.innerHTML = "";
    const placed: Array<{ x: number; y: number; w: number; h: number }> = [];
    const lines: Array<{ x1: number; y1: number; x2: number; y2: number; color: string }> = [];
    const priority: Record<string, number> = { patient: 0, prime: 1, runner: 2, guide: 3, ambulance: 4 };
    const ordered = [...nodes].sort((a, b) => (priority[a.id] ?? 9) - (priority[b.id] ?? 9));
    const overlap = (x: number, y: number, w: number, h: number) =>
      placed.some((p) => x < p.x + p.w && x + w > p.x && y < p.y + p.h && y + h > p.y);
    const place = (
      px: number,
      py: number,
      w: number,
      h: number,
      color: string,
      main: string,
      sub?: string,
    ) => {
      const candidates: Array<[number, number]> = [
        [10, -h / 2],
        [-w - 10, -h / 2],
        [-w / 2, -h - 10],
        [-w / 2, 10],
        [10, -h - 10],
        [10, 10],
        [-w - 10, -h - 10],
        [-w - 10, 10],
      ];
      let chosen: [number, number] | null = null;
      for (const [dx, dy] of candidates) {
        const x = px + dx;
        const y = py + dy;
        if (x < 4 || x + w > W - 4 || y < 4 || y + h > H - 4) {
          continue;
        }
        if (overlap(x, y, w, h)) {
          continue;
        }
        chosen = [dx, dy];
        break;
      }
      if (!chosen) {
        for (let yy = 16; yy <= H - h - 4; yy += h + 4) {
          const fx = Math.max(4, Math.min(W - w - 4, px - w / 2));
          if (!overlap(fx, yy, w, h)) {
            chosen = [fx - px, yy - py];
            lines.push({ x1: px, y1: py, x2: fx + w / 2, y2: yy + h / 2, color });
            break;
          }
        }
      }
      if (!chosen) {
        chosen = [10, -h / 2];
        lines.push({ x1: px, y1: py, x2: px + 10, y2: py - h / 2, color });
      }
      const x = px + chosen[0];
      const y = py + chosen[1];
      placed.push({ x, y, w, h });
                  const el = document.createElement("div");
      el.style.cssText = `position:absolute;left:${x}px;top:${y}px;background:rgba(7,17,25,.85);border:1px solid ${color}99;border-left:3px solid ${color};border-radius:4px;padding:3px 8px;pointer-events:none;white-space:nowrap;box-shadow:0 2px 8px rgba(0,0,0,.4)`;
      const mainEl = document.createElement("div");
      mainEl.style.cssText = `color:#ffffff;font-size:12px;line-height:16px;font-weight:700;letter-spacing:.3px`;
      mainEl.textContent = main;
      el.appendChild(mainEl);
      if (sub) {
        const subEl = document.createElement("div");
        subEl.style.cssText = `color:rgba(255,255,255,.68);font-size:10px;line-height:14px`;
        subEl.textContent = sub;
        el.appendChild(subEl);
      }
      layer.appendChild(el);
    };
    for (const node of ordered) {
      const px = map.pointToPixel(new sdk.Point(node.longitude, node.latitude));
      if (px.x < -120 || px.x > W + 120 || px.y < -120 || px.y > H + 120) {
        continue;
      }
      const main = node.label.length > 12 ? `${node.label.slice(0, 12)}…` : node.label;
      const sub = node.sublabel || undefined;
      const mainW = [...main].reduce((acc, c) => acc + (c.charCodeAt(0) > 255 ? 13 : 8), 0);
      const w = Math.max(64, mainW + (sub ? 40 : 26));
      const h = sub ? 36 : 22;
      place(px.x, px.y, w, h, node.color, main, sub);
    }
    for (const link of model.links.filter((l) => l.kind === "fly")) {
      const from = nodes.find((n) => n.id === link.from);
      const to = nodes.find((n) => n.id === link.to);
      if (!from || !to) {
        continue;
      }
      const fl = from.realLatitude != null && from.realLongitude != null ? { lat: from.realLatitude, lng: from.realLongitude } : null;
      const tl = to.realLatitude != null && to.realLongitude != null ? { lat: to.realLatitude, lng: to.realLongitude } : null;
      if (!fl || !tl) {
        continue;
      }
      const key = `${fl.lat},${fl.lng}|${tl.lat},${tl.lng}`;
      const d = distanceCacheRef.current.get(key);
      if (!d) {
        continue;
      }
      const mid = map.pointToPixel(new sdk.Point((from.longitude + to.longitude) / 2, (from.latitude + to.latitude) / 2));
      if (mid.x < -120 || mid.x > W + 120 || mid.y < -120 || mid.y > H + 120) {
        continue;
      }
      const text = d.durationSec != null ? `${Math.round(d.meters)}m 路 ${Math.ceil(d.durationSec / 60)}min` : `${Math.round(d.meters)}m`;
      const w = [...text].reduce((acc, c) => acc + (c.charCodeAt(0) > 255 ? 13 : 8), 0) + 22;
      place(mid.x, mid.y, w, 20, "#17e5c3", text);
    }
    if (lines.length > 0) {
      const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      svg.setAttribute("style", "position:absolute;inset:0;width:100%;height:100%;pointer-events:none;");
      for (const line of lines) {
        const l = document.createElementNS("http://www.w3.org/2000/svg", "line");
        l.setAttribute("x1", String(line.x1));
        l.setAttribute("y1", String(line.y1));
        l.setAttribute("x2", String(line.x2));
        l.setAttribute("y2", String(line.y2));
        l.setAttribute("stroke", line.color);
        l.setAttribute("stroke-width", "1.2");
        l.setAttribute("stroke-dasharray", "4 4");
        l.setAttribute("opacity", "0.8");
        svg.appendChild(l);
      }
      layer.appendChild(svg);
      }
    } catch (err) {
      console.error("[SceneMap renderLabels]", err);
    }
  };

  useEffect(() => {
    let cancelled = false;
    loadBaiduSdk(ak)
      .then((sdk) => {
        if (cancelled || !containerRef.current) return;
        sdkRef.current = sdk;
        const patient = model.nodes.find((node) => node.id === 'patient' && validNode(node));
        const center = patient && validNode(patient)
          ? new sdk.Point(patient.longitude, patient.latitude)
          : new sdk.Point(116.465922, 39.915976);
        const map = new sdk.Map(containerRef.current);
        map.centerAndZoom(center, 15);
        map.enableScrollWheelZoom(true);
        map.enableDragging();
        // 3D 场景：倾斜视野 + 建筑（setViewport 会按当前 tilt 计算取景）
        try {
          if (map.setDisplay3D) map.setDisplay3D(true);
          if (map.setTilt) map.setTilt(50);
        } catch {}
        // 脉冲环动画关键帧
        const st = document.createElement('style');
        st.textContent = '@keyframes lra-ping{0%{transform:scale(.45);opacity:1}80%,100%{transform:scale(2.6);opacity:0}}';
        document.head.appendChild(st);
        pulseCtorRef = makePulseOverlay(sdk);
        mapRef.current = map;
        map.addEventListener('moveend', renderLabels);
        map.addEventListener('zoomend', renderLabels);
        const onResize = () => {
          fitView();
          renderLabels();
        };
        resizeHandlerRef.current = onResize;
        window.addEventListener("resize", onResize);
        setSdkReady(true);
      })
      .catch((reason: unknown) => {
        if (!cancelled) setError(reason instanceof Error ? reason.message : '百度地图加载失败');
      });
    return () => {
      cancelled = true;
      const onResize = resizeHandlerRef.current;
      if (onResize) {
        window.removeEventListener("resize", onResize);
      }
      resizeHandlerRef.current = null;
      const map = mapRef.current;
      if (map?.destroy) map.destroy();
      mapRef.current = null;
      sdkRef.current = null;
      setSdkReady(false);
    };
  }, [ak]);

  useEffect(() => {
    const sdk = sdkRef.current;
    const map = mapRef.current;
    if (!sdk || !map) return;

    const nodes = model.nodes.filter(validNode);
    const aliveIds = new Set(nodes.map((node) => node.id));
    for (const [id, marker] of markersRef.current) {
      if (!aliveIds.has(id)) {
        map.removeOverlay(marker);
        markersRef.current.delete(id);
        markerTargetsRef.current.delete(id);
      }
    }


    for (const node of nodes) {
      const move = node.moveTarget;
      const tLat = move && typeof move.latitude === 'number' ? move.latitude : node.latitude;
      const tLng = move && typeof move.longitude === 'number' ? move.longitude : node.longitude;
      const icon = new sdk.Icon(
        markerSvg(node.color, node.focused),
        new sdk.Size(node.focused ? 44 : 30, node.focused ? 44 : 30),
        { anchor: new sdk.Size(node.focused ? 22 : 15, node.focused ? 22 : 15) },
      );
      const existing = markersRef.current.get(node.id);
      if (existing) {
        // 更新移动目标与外观（位置由平滑移动动画逐帧插值）
        markerTargetsRef.current.set(node.id, { lat: tLat, lng: tLng });
        existing.setIcon(icon);
      } else {
        // 圆形光点直接贴地渲染
        const alt = 0;
        const marker = new sdk.Marker(new sdk.Point(node.longitude, node.latitude, alt), { icon });
        (marker as any)._hg = alt;
        map.addOverlay(marker);
        markersRef.current.set(node.id, marker);
        markerTargetsRef.current.set(node.id, { lat: tLat, lng: tLng });
        try {
          const ground = new sdk.Point(node.longitude, node.latitude);
          (marker as any)._pulse = new pulseCtorRef(ground, node.color);
          map.addOverlay((marker as any)._pulse);
        } catch {}
      }
    }

    // 飞线重建
    for (const line of polylineRefs.current) {
      map.removeOverlay(line);
    }
    polylineRefs.current = [];
    for (const link of model.links.filter((item) => item.kind === 'fly')) {
      const from = nodes.find((node) => node.id === link.from);
      const to = nodes.find((node) => node.id === link.to);
      if (!from || !to) continue;
      const line = new sdk.Polyline(
        [new sdk.Point(from.longitude, from.latitude), new sdk.Point(to.longitude, to.latitude)],
        {
          strokeColor: link.active ? '#4be3ff' : '#1778b5',
          strokeWeight: link.active ? 5 : 3,
          strokeOpacity: link.active ? 0.9 : 0.62,
          strokeStyle: 'dashed',
        },
      );
      map.addOverlay(line);
      polylineRefs.current.push(line);
      // real-world walking distance via server; the label is drawn by the
      // collision-free label layer (renderLabels)
      const fl = from.realLatitude != null && from.realLongitude != null ? { lat: from.realLatitude, lng: from.realLongitude } : null;
      const tl = to.realLatitude != null && to.realLongitude != null ? { lat: to.realLatitude, lng: to.realLongitude } : null;
      if (fl && tl) {
        const key = `${fl.lat},${fl.lng}|${tl.lat},${tl.lng}`;
        if (!distanceCacheRef.current.has(key)) {
          fetch(`/api/map/distance?fromLat=${fl.lat}&fromLng=${fl.lng}&toLat=${tl.lat}&toLng=${tl.lng}`)
            .then((response) => (response.ok ? response.json() : null))
            .then((data) => {
              if (data && typeof data.meters === 'number') {
                distanceCacheRef.current.set(key, { meters: data.meters, durationSec: data.durationSec ?? null });
                renderLabels();
              }
            })
            .catch(() => {});
        }
      }
    }
    fitView();
    renderLabels();
  }, [model, sdkReady]);

  // 平滑移动动画：逐帧向目标位置插值
  useEffect(() => {
    let raf = 0;
    const tick = () => {
      try {
        const sdk = sdkRef.current;
        const map = mapRef.current;
        if (sdk && map) {
        for (const [id, marker] of markersRef.current) {
          const target = markerTargetsRef.current.get(id);
          if (!target) continue;
          const pos = marker.getPosition();
          const dLat = target.lat - pos.lat;
          const dLng = target.lng - pos.lng;
          if (Math.abs(dLat) < 1e-7 && Math.abs(dLng) < 1e-7) continue;
          const hg = (marker as any)._hg || 0;
          const nlng = pos.lng + dLng * 0.06;
          const nlat = pos.lat + dLat * 0.06;
          marker.setPosition(new sdk.Point(nlng, nlat, hg));
          const pulse = (marker as any)._pulse;
          if (pulse) {
            pulse._point = new sdk.Point(nlng, nlat);
            pulse.draw();
          }
        }
      }
      } catch (err) {
        console.error("[SceneMap tick]", err);
      }
      raf = window.requestAnimationFrame(tick);
    };
    raf = window.requestAnimationFrame(tick);
    return () => {
      if (raf) window.cancelAnimationFrame(raf);
    };
  }, []);

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%', overflow: 'hidden', background: '#061321' }}>
      <div ref={containerRef} style={{ width: '100%', height: '100%', filter: 'saturate(.7) brightness(.72) contrast(1.08)' }} />
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          inset: 0,
          pointerEvents: 'none',
          background: 'linear-gradient(rgba(23,229,195,.055) 1px, transparent 1px), linear-gradient(90deg, rgba(23,229,195,.055) 1px, transparent 1px)',
          backgroundSize: '36px 36px',
          mixBlendMode: 'screen',
        }}
      />
      <div ref={labelLayerRef} style={{ position: 'absolute', inset: 0, overflow: 'hidden', pointerEvents: 'none' }} />
      <div
        style={{
          position: 'absolute',
          left: 14,
          top: 12,
          padding: '5px 9px',
          color: '#7feee0',
          background: 'rgba(3,16,28,.76)',
          border: '1px solid rgba(23,229,195,.45)',
          fontSize: 11,
          letterSpacing: 1,
          pointerEvents: 'none',
        }}
      >
        BAIDU MAP · REAL GEO LAYER
      </div>
      {error && (
        <div style={{ position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', color: '#ffb4c0', background: 'rgba(3,12,24,.82)', fontSize: 13 }}>
          {error}
        </div>
      )}
    </div>
  );
}

