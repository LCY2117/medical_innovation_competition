import { useEffect, useMemo, useRef, useState } from 'react';
import * as THREE from 'three';
import type { SceneModel, SceneNode } from './sceneModel';
import { BaiduSceneMap } from './BaiduSceneMap';

function detectWebGL(): boolean {
  if (typeof window === 'undefined') {
    return false;
  }
  try {
    const canvas = document.createElement('canvas');
    return Boolean(
      window.WebGLRenderingContext &&
        (canvas.getContext('webgl2') || canvas.getContext('webgl')),
    );
  } catch {
    return false;
  }
}

function makeGlowTexture(color: string): THREE.Texture {
  const size = 128;
  const canvas = document.createElement('canvas');
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext('2d');
  if (ctx) {
    const gradient = ctx.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
    gradient.addColorStop(0, color);
    gradient.addColorStop(0.35, color);
    gradient.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, size, size);
  }
  const texture = new THREE.CanvasTexture(canvas);
  texture.needsUpdate = true;
  return texture;
}

function makeRadarTexture(): THREE.Texture {
  const size = 256;
  const canvas = document.createElement('canvas');
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext('2d');
  if (ctx) {
    const gradient = ctx.createConicGradient(0, size / 2, size / 2);
    gradient.addColorStop(0, 'rgba(23,229,195,0)');
    gradient.addColorStop(0.18, 'rgba(23,229,195,0.55)');
    gradient.addColorStop(0.2, 'rgba(23,229,195,0)');
    gradient.addColorStop(0.5, 'rgba(78,190,255,0.18)');
    gradient.addColorStop(1, 'rgba(78,190,255,0)');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, size, size);
    ctx.strokeStyle = 'rgba(23,229,195,0.35)';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.arc(size / 2, size / 2, size / 2 - 2, 0, Math.PI * 2);
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(size / 2, size / 2, size / 3 - 1, 0, Math.PI * 2);
    ctx.stroke();
  }
  const texture = new THREE.CanvasTexture(canvas);
  texture.needsUpdate = true;
  return texture;
}

/**
 * 自绘“暗色校园地图”地面贴图：楼宇、道路、广场、水系。
 * 不依赖任何地图 API / 瓦片服务，离线可运行。
 */
function makeMapTexture(): THREE.Texture {
  const size = 1024;
  const canvas = document.createElement('canvas');
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext('2d');
  if (ctx) {
    // 底色
    ctx.fillStyle = '#050d18';
    ctx.fillRect(0, 0, size, size);

    // 楼宇区块
    const blocks: Array<[number, number, number, number]> = [
      [70, 90, 190, 150],
      [320, 90, 210, 170],
      [600, 70, 190, 150],
      [850, 90, 110, 170],
      [90, 330, 170, 180],
      [330, 340, 230, 190],
      [680, 330, 200, 180],
      [870, 340, 90, 180],
      [70, 640, 200, 170],
      [330, 650, 250, 190],
      [680, 640, 200, 190],
      [860, 650, 100, 170],
      [150, 880, 220, 90],
      [520, 890, 220, 80],
      [780, 880, 180, 90],
    ];
    for (const [x, y, w, h] of blocks) {
      ctx.fillStyle = 'rgba(17, 42, 68, 0.9)';
      ctx.strokeStyle = 'rgba(78, 190, 255, 0.16)';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.roundRect(x, y, w, h, 10);
      ctx.fill();
      ctx.stroke();
      // 楼宇内部细线（窗户感）
      ctx.strokeStyle = 'rgba(78, 190, 255, 0.08)';
      ctx.lineWidth = 1;
      for (let gy = y + 18; gy < y + h - 12; gy += 22) {
        ctx.beginPath();
        ctx.moveTo(x + 12, gy);
        ctx.lineTo(x + w - 12, gy);
        ctx.stroke();
      }
    }

    // 道路
    ctx.fillStyle = '#0e2238';
    ctx.fillRect(0, 300, size, 26);
    ctx.fillRect(0, 610, size, 30);
    ctx.fillRect(288, 0, 28, size);
    ctx.fillRect(620, 0, 26, size);
    ctx.strokeStyle = 'rgba(46, 122, 178, 0.55)';
    ctx.lineWidth = 2;
    ctx.setLineDash([22, 18]);
    ctx.beginPath(); ctx.moveTo(0, 313); ctx.lineTo(size, 313); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(0, 625); ctx.lineTo(size, 625); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(302, 0); ctx.lineTo(302, size); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(633, 0); ctx.lineTo(633, size); ctx.stroke();
    ctx.setLineDash([]);

    // 对角主路
    ctx.strokeStyle = '#0e2238';
    ctx.lineWidth = 22;
    ctx.beginPath(); ctx.moveTo(-40, 940); ctx.lineTo(1064, 300); ctx.stroke();
    ctx.strokeStyle = 'rgba(46, 122, 178, 0.5)';
    ctx.lineWidth = 2;
    ctx.setLineDash([20, 20]);
    ctx.beginPath(); ctx.moveTo(-40, 940); ctx.lineTo(1064, 300); ctx.stroke();
    ctx.setLineDash([]);

    // 中央广场
    ctx.fillStyle = 'rgba(23, 229, 195, 0.035)';
    ctx.strokeStyle = 'rgba(23, 229, 195, 0.3)';
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    ctx.ellipse(512, 470, 190, 120, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
    ctx.strokeStyle = 'rgba(23, 229, 195, 0.14)';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.ellipse(512, 470, 145, 88, 0, 0, Math.PI * 2);
    ctx.stroke();

    // 水系
    ctx.fillStyle = 'rgba(16, 74, 110, 0.55)';
    ctx.strokeStyle = 'rgba(78, 190, 255, 0.25)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.ellipse(870, 830, 105, 62, -0.3, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // 周边细网格（弱化）
    ctx.strokeStyle = 'rgba(78, 190, 255, 0.045)';
    ctx.lineWidth = 1;
    for (let x = 0; x <= size; x += 64) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, size); ctx.stroke();
    }
    for (let y = 0; y <= size; y += 64) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(size, y); ctx.stroke();
    }
  }
  const texture = new THREE.CanvasTexture(canvas);
  texture.needsUpdate = true;
  return texture;
}

function makeLabelSprite(text: string, color: string, sub?: string): THREE.Sprite {
  const width = 300;
  const height = 64;
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d');
  if (ctx) {
    ctx.clearRect(0, 0, width, height);
    const main = text.length > 12 ? `${text.slice(0, 12)}…` : text;
    ctx.font = 'bold 26px "Microsoft YaHei", "PingFang SC", sans-serif';
    const metrics = ctx.measureText(main);
    const boxWidth = Math.max(120, metrics.width + 36);
    const boxX = (width - boxWidth) / 2;
    ctx.fillStyle = 'rgba(3,12,24,0.82)';
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.roundRect(boxX, 2, boxWidth, height - 8, 6);
    ctx.fill();
    ctx.stroke();
    ctx.fillStyle = '#eafaff';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(main, width / 2, sub ? 22 : 31);
    if (sub) {
      ctx.font = '16px "Microsoft YaHei", "PingFang SC", sans-serif';
      ctx.fillStyle = color;
      const subText = sub.length > 18 ? `${sub.slice(0, 18)}…` : sub;
      ctx.fillText(subText, width / 2, 47);
    }
  }
  const texture = new THREE.CanvasTexture(canvas);
  texture.needsUpdate = true;
  const material = new THREE.SpriteMaterial({
    map: texture,
    transparent: true,
    depthTest: false,
  });
  const sprite = new THREE.Sprite(material);
  sprite.scale.set(46, 10, 1);
  return sprite;
}

interface NodeMeshes {
  id: string;
  group: THREE.Group;
  core: THREE.Mesh;
  halo: THREE.Sprite;
  ring: THREE.Mesh;
  label: THREE.Sprite;
  baseScale: number;
  focus: number;
  targetX: number;
  targetZ: number;
}

interface FlyLine {
  id: string;
  curve: THREE.QuadraticBezierCurve3;
  line: THREE.Line;
  dot: THREE.Mesh;
  duration: number;
}

export function SceneMap({ model }: { model: SceneModel }) {
  const [baiduConfig, setBaiduConfig] = useState<{ provider: string; baiduWebAk: string | null } | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetch('/api/map/config')
      .then((response) => (response.ok ? response.json() : null))
      .then((config) => {
        if (!cancelled && config) setBaiduConfig(config);
      })
      .catch(() => {
        if (!cancelled) setBaiduConfig(null);
      });
    return () => { cancelled = true; };
  }, []);

  if (baiduConfig?.provider === 'baidu' && baiduConfig.baiduWebAk) {
    return <BaiduSceneMap ak={baiduConfig.baiduWebAk} model={model} />;
  }
  return <ThreeSceneMap model={model} />;
}

function ThreeSceneMap({ model }: { model: SceneModel }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [webgl] = useState(detectWebGL);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const nodeRefs = useRef<Map<string, NodeMeshes>>(new Map());
  const flyRefs = useRef<FlyLine[]>([]);
  const radarRef = useRef<{ group: THREE.Group; sweep: THREE.Mesh; rings: THREE.Mesh[] } | null>(null);
  const rafRef = useRef<number | null>(null);
  const modelRef = useRef<SceneModel>(model);
  modelRef.current = model;

  // auto-frame: fit camera to the bounding box of all points (including move targets)
  const frameCamera = (nodes: SceneNode[]) => {
    const camera = cameraRef.current;
    const container = containerRef.current;
    if (!camera || !container || nodes.length === 0) {
      return;
    }
    let minX = Infinity;
    let maxX = -Infinity;
    let minY = Infinity;
    let maxY = -Infinity;
    for (const node of nodes) {
      const candidates: Array<[number, number]> = [[node.x, node.y]];
      if (node.moveTarget) {
        candidates.push([node.moveTarget.x, node.moveTarget.y]);
      }
      for (const [x, y] of candidates) {
        if (x < minX) minX = x;
        if (x > maxX) maxX = x;
        if (y < minY) minY = y;
        if (y > maxY) maxY = y;
      }
    }
    const cx = (minX + maxX) / 2;
    const cy = (minY + maxY) / 2;
    const halfW = Math.max(1, (maxX - minX) / 2);
    const halfD = Math.max(1, (maxY - minY) / 2);
    const margin = 26;
    const aspect = container.clientWidth / Math.max(1, container.clientHeight);
    const vfov = (camera.fov * Math.PI) / 180;
    const tanV = Math.tan(vfov / 2);
    const tanH = tanV * aspect;
    // fixed viewing angle (same as the initial camera at (0,150,230)); ground-depth foreshortening ~0.547
    const depthFactor = 0.547;
    const distH = (halfW + margin) / tanH;
    const distD = ((halfD + margin) * depthFactor) / tanV;
    const dist = Math.max(distH, distD, 60);
    const direction = new THREE.Vector3(0, 0.5474, 0.8393).normalize();
    const center = new THREE.Vector3(cx, 0, -cy);
    camera.position.copy(center.clone().addScaledVector(direction, dist));
    camera.lookAt(center);
  };

  // 初始化渲染器 / 场景 / 摄像机 / 常驻元素
  useEffect(() => {
    const container = containerRef.current;
    if (!container || !webgl) {
      return;
    }

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setClearColor(0x020a14, 0);
    container.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x020a14, 0.0018);
    sceneRef.current = scene;

    const camera = new THREE.PerspectiveCamera(42, container.clientWidth / container.clientHeight, 1, 1200);
    camera.position.set(0, 150, 230);
    camera.lookAt(0, 0, 0);
    cameraRef.current = camera;

    // 地图地面
    const mapTexture = makeMapTexture();
    const ground = new THREE.Mesh(
      new THREE.PlaneGeometry(380, 380),
      new THREE.MeshBasicMaterial({ map: mapTexture, transparent: false, depthWrite: false }),
    );
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = -1;
    scene.add(ground);

    // 雷达
    const radarGroup = new THREE.Group();
    radarGroup.visible = false;
    const radarTexture = makeRadarTexture();
    const sweep = new THREE.Mesh(
      new THREE.PlaneGeometry(150, 150),
      new THREE.MeshBasicMaterial({
        map: radarTexture,
        transparent: true,
        blending: THREE.AdditiveBlending,
        depthWrite: false,
        side: THREE.DoubleSide,
      }),
    );
    sweep.rotation.x = -Math.PI / 2;
    sweep.position.y = 0.6;
    radarGroup.add(sweep);
    const rings: THREE.Mesh[] = [];
    for (let i = 0; i < 3; i += 1) {
      const ring = new THREE.Mesh(
        new THREE.RingGeometry(8, 9.5, 64),
        new THREE.MeshBasicMaterial({
          color: 0x17e5c3,
          transparent: true,
          opacity: 0.5,
          side: THREE.DoubleSide,
          blending: THREE.AdditiveBlending,
          depthWrite: false,
        }),
      );
      ring.rotation.x = -Math.PI / 2;
      ring.position.y = 0.5;
      ring.visible = false;
      radarGroup.add(ring);
      rings.push(ring);
    }
    scene.add(radarGroup);
    radarRef.current = { group: radarGroup, sweep, rings };

    // 动画循环
    const clock = new THREE.Clock();
    const animate = () => {
      const elapsed = clock.getElapsedTime();
      const current = modelRef.current;

      // 节点脉冲与聚焦
      for (const [id, meshes] of nodeRefs.current) {
        const node = current.nodes.find((item) => item.id === id);
        const targetFocus = node?.focused ? 1 : 0;
        meshes.focus += (targetFocus - meshes.focus) * 0.08;
        const focusScale = 1 + meshes.focus * 0.45;
        meshes.group.scale.setScalar(focusScale);
        const coreMat = meshes.core.material as THREE.MeshBasicMaterial;
        const baseOpacity = 0.85 + meshes.focus * 0.15;
        coreMat.opacity = baseOpacity;
        (meshes.halo.material as THREE.SpriteMaterial).opacity = 0.65 + meshes.focus * 0.35;
        (meshes.ring.material as THREE.MeshBasicMaterial).opacity = 0.35 + meshes.focus * 0.45;
        // 平滑移动到目标位置
        meshes.group.position.x += (meshes.targetX - meshes.group.position.x) * 0.03;
        meshes.group.position.z += (meshes.targetZ - meshes.group.position.z) * 0.03;
      }

      // 飞线
      for (const fly of flyRefs.current) {
        const t = (elapsed % fly.duration) / fly.duration;
        const point = fly.curve.getPoint(t);
        fly.dot.position.copy(point);
        const mat = fly.dot.material as THREE.MeshBasicMaterial;
        mat.opacity = Math.sin(Math.PI * t) * 0.9 + 0.1;
      }



      renderer.render(scene, camera);
      rafRef.current = window.requestAnimationFrame(animate);
    };
    rafRef.current = window.requestAnimationFrame(animate);

    const resizeCanvas = () => {
      const width = container.clientWidth;
      const height = container.clientHeight;
      if (!width || !height) {
        return;
      }
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height);
      frameCamera(modelRef.current.nodes);
    };
    window.addEventListener('resize', resizeCanvas);
    const resizeObserver = new ResizeObserver(() => resizeCanvas());
    resizeObserver.observe(container);

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      resizeObserver.disconnect();
      if (rafRef.current !== null) {
        window.cancelAnimationFrame(rafRef.current);
      }
      nodeRefs.current.clear();
      flyRefs.current = [];
      scene.traverse((object) => {
        const mesh = object as THREE.Mesh;
        if (mesh.geometry) {
          mesh.geometry.dispose();
        }
        const material = (mesh as THREE.Mesh).material as THREE.Material | THREE.Material[] | undefined;
        if (Array.isArray(material)) {
          material.forEach((item) => item.dispose());
        } else if (material) {
          material.dispose();
        }
      });
      radarTexture.dispose();
      mapTexture.dispose();
      renderer.dispose();
      renderer.domElement.remove();
      rendererRef.current = null;
      sceneRef.current = null;
      cameraRef.current = null;
      radarRef.current = null;
    };
  }, [webgl]);

  // 节点 / 飞线随模型更新
  useEffect(() => {
    const scene = sceneRef.current;
    const camera = cameraRef.current;
    if (!scene || !camera || !webgl) {
      return;
    }

    // 清理已消失的节点（保留存在的节点，实现平滑移动）
    const aliveIds = new Set(model.nodes.map((node) => node.id));
    for (const [id, meshes] of nodeRefs.current) {
      if (!aliveIds.has(id)) {
        scene.remove(meshes.group);
        nodeRefs.current.delete(id);
      }
    }
    for (const fly of flyRefs.current) {
      scene.remove(fly.line);
      scene.remove(fly.dot);
    }
    flyRefs.current = [];

    const position = (node: SceneNode): THREE.Vector3 =>
      new THREE.Vector3(node.x, 0, -node.y);

    for (const node of model.nodes) {
      const targetX = node.moveTarget?.x ?? node.x;
      const targetZ = -(node.moveTarget?.y ?? node.y);
      const existing = nodeRefs.current.get(node.id);
      if (existing) {
        // 更新移动目标与标签（位置由动画循环平滑插值）
        existing.targetX = targetX;
        existing.targetZ = targetZ;
        const oldMat = existing.label.material as THREE.SpriteMaterial;
        existing.label.material = makeLabelSprite(node.label, node.color, node.sublabel).material;
        oldMat.map?.dispose();
        oldMat.dispose();
        continue;
      }
      const group = new THREE.Group();
      const pos = position(node);
      group.position.copy(pos);

      const glowTexture = makeGlowTexture(node.color);
      const halo = new THREE.Sprite(
        new THREE.SpriteMaterial({
          map: glowTexture,
          transparent: true,
          opacity: 0.65,
          blending: THREE.AdditiveBlending,
          depthWrite: false,
        }),
      );
      halo.scale.setScalar(node.kind === 'patient' || node.kind === 'ambulance' ? 30 : 22);
      group.add(halo);

      const core = new THREE.Mesh(
        new THREE.SphereGeometry(node.kind === 'patient' ? 2.6 : node.kind === 'ambulance' ? 3.4 : 2, 24, 24),
      );
      core.material = new THREE.MeshBasicMaterial({
        color: node.color,
        transparent: true,
        opacity: 0.9,
        blending: THREE.AdditiveBlending,
        depthWrite: false,
      });
      core.position.y = 2.4;
      group.add(core);

      const ring = new THREE.Mesh(
        new THREE.TorusGeometry(4.6, 0.22, 12, 48),
        new THREE.MeshBasicMaterial({
          color: node.color,
          transparent: true,
          opacity: 0.4,
          blending: THREE.AdditiveBlending,
          depthWrite: false,
        }),
      );
      ring.position.y = 2.4;
      group.add(ring);

      const label = makeLabelSprite(node.label, node.color, node.sublabel);
      label.position.set(0, 11, 0);
      group.add(label);

      scene.add(group);
      nodeRefs.current.set(node.id, {
        id: node.id,
        group,
        core,
        halo,
        ring,
        label,
        baseScale: 1 + Math.random(),
        focus: node.focused ? 1 : 0,
        targetX,
        targetZ,
      });
    }

    // 飞线
    for (const link of model.links.filter((item) => item.kind === 'fly')) {
      const from = model.nodes.find((node) => node.id === link.from);
      const to = model.nodes.find((node) => node.id === link.to);
      if (!from || !to) {
        continue;
      }
      const start = position(from);
      const end = position(to);
      const mid = start.clone().lerp(end, 0.5);
      mid.y += Math.max(26, start.distanceTo(end) * 0.35);
      const curve = new THREE.QuadraticBezierCurve3(start, mid, end);
      const points = curve.getPoints(64);
      const lineGeo = new THREE.BufferGeometry().setFromPoints(points);
      const line = new THREE.Line(
        lineGeo,
        new THREE.LineBasicMaterial({
          color: link.active ? 0x4be3ff : 0x1392df,
          transparent: true,
          opacity: 0.75,
          blending: THREE.AdditiveBlending,
          depthWrite: false,
        }),
      );
      scene.add(line);
      const dot = new THREE.Mesh(
        new THREE.SphereGeometry(1.1, 12, 12),
        new THREE.MeshBasicMaterial({
          color: 0xffffff,
          transparent: true,
          opacity: 0.9,
          blending: THREE.AdditiveBlending,
        }),
      );
      scene.add(dot);
      flyRefs.current.push({ id: link.id, curve, line, dot, duration: 1.8 + Math.random() * 0.6 });
    }
    frameCamera(model.nodes);
  }, [model, webgl]);

  if (!webgl) {
    return <Scene2D model={model} />;
  }

  return <div ref={containerRef} className="lra-scene-canvas" style={{ width: '100%', height: '100%' }} />;
}

function Scene2D({ model }: { model: SceneModel }) {
  const viewBox = useMemo(() => {
    let minX = Infinity;
    let maxX = -Infinity;
    let minY = Infinity;
    let maxY = -Infinity;
    for (const node of model.nodes) {
      if (node.x < minX) minX = node.x;
      if (node.x > maxX) maxX = node.x;
      if (node.y < minY) minY = node.y;
      if (node.y > maxY) maxY = node.y;
    }
    if (!Number.isFinite(minX)) {
      return '-170 -150 340 300';
    }
    const pad = 40;
    return `${minX - pad} ${minY - pad} ${maxX - minX + pad * 2} ${maxY - minY + pad * 2}`;
  }, [model.nodes]);
  return (
    <svg viewBox={viewBox} style={{ width: '100%', height: '100%' }} preserveAspectRatio="xMidYMid slice">
      <defs>
        <radialGradient id="lra-radar-grad" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="rgba(23,229,195,0.35)" />
          <stop offset="60%" stopColor="rgba(23,229,195,0.08)" />
          <stop offset="100%" stopColor="rgba(23,229,195,0)" />
        </radialGradient>
      </defs>
      <rect x="-170" y="-150" width="340" height="300" fill="#050d18" />
      {/* 楼宇 */}
      {[
        [-150, -120, 60, 45], [-60, -125, 65, 50], [35, -130, 60, 45], [105, -120, 40, 52],
        [-145, -35, 55, 55], [-45, -30, 70, 58], [55, -35, 62, 55], [130, -30, 30, 55],
        [-150, 55, 62, 52], [-45, 60, 78, 58], [55, 55, 62, 58], [125, 60, 35, 52],
        [-105, 125, 70, 28], [25, 128, 70, 25], [95, 125, 58, 28],
      ].map(([x, y, w, h], i) => (
        <g key={i}>
          <rect x={x} y={y} width={w} height={h} rx="4" fill="rgba(17,42,68,0.9)" stroke="rgba(78,190,255,0.18)" strokeWidth="1" />
          {Array.from({ length: Math.max(1, Math.floor(h / 8)) }).map((_, j) => (
            <line key={j} x1={x + 3} y1={y + 6 + j * 8} x2={x + w - 3} y2={y + 6 + j * 8} stroke="rgba(78,190,255,0.08)" strokeWidth="1" />
          ))}
        </g>
      ))}
      {/* 道路 */}
      <line x1="-170" y1="-50" x2="170" y2="-50" stroke="#0e2238" strokeWidth="8" />
      <line x1="-170" y1="52" x2="170" y2="52" stroke="#0e2238" strokeWidth="9" />
      <line x1="-60" y1="-150" x2="-60" y2="150" stroke="#0e2238" strokeWidth="8" />
      <line x1="62" y1="-150" x2="62" y2="150" stroke="#0e2238" strokeWidth="8" />
      <line x1="-170" y1="-50" x2="170" y2="-50" stroke="rgba(46,122,178,0.5)" strokeWidth="0.8" strokeDasharray="6 5" />
      <line x1="-170" y1="52" x2="170" y2="52" stroke="rgba(46,122,178,0.5)" strokeWidth="0.8" strokeDasharray="6 5" />
      <line x1="-60" y1="-150" x2="-60" y2="150" stroke="rgba(46,122,178,0.5)" strokeWidth="0.8" strokeDasharray="6 5" />
      <line x1="62" y1="-150" x2="62" y2="150" stroke="rgba(46,122,178,0.5)" strokeWidth="0.8" strokeDasharray="6 5" />
      {/* 中央广场 */}
      <ellipse cx="0" cy="-10" rx="58" ry="36" fill="rgba(23,229,195,0.04)" stroke="rgba(23,229,195,0.3)" strokeWidth="1.2" />
      <ellipse cx="0" cy="-10" rx="42" ry="26" fill="none" stroke="rgba(23,229,195,0.14)" strokeWidth="1" />
      {/* 水系 */}
      <ellipse cx="120" cy="110" rx="32" ry="19" fill="rgba(16,74,110,0.55)" stroke="rgba(78,190,255,0.25)" strokeWidth="1" />
      <ellipse cx="0" cy="0" rx="150" ry="150" fill="url(#lra-radar-grad)" opacity="0.5" />



      {model.links
        .filter((link) => link.kind === 'fly')
        .map((link) => {
          const from = model.nodes.find((node) => node.id === link.from);
          const to = model.nodes.find((node) => node.id === link.to);
          if (!from || !to) {
            return null;
          }
          const midX = (from.x + to.x) / 2;
          const midY = (from.y + to.y) / 2 - 42;
          return (
            <path
              key={link.id}
              d={`M ${from.x} ${from.y} Q ${midX} ${midY} ${to.x} ${to.y}`}
              fill="none"
              stroke="rgba(75,227,255,0.7)"
              strokeWidth="1.6"
              strokeDasharray="8 10"
            >
              <animate attributeName="stroke-dashoffset" values="0;-72" dur="1.6s" repeatCount="indefinite" />
            </path>
          );
        })}

      {model.nodes.map((node) => {
        const r = node.kind === 'patient' || node.kind === 'ambulance' ? 7 : 5.5;
        return (
          <g key={node.id} transform={`translate(${node.x}, ${node.y})`}>
            <circle r={r + 4} fill={node.color} opacity="0.25" />
            <circle r={r} fill={node.color} stroke="#eafaff" strokeWidth="1.2" />
            <rect
              x={-46}
              y={node.kind === 'patient' ? 18 : 14}
              width="92"
              height={node.sublabel ? 34 : 24}
              rx="5"
              fill="rgba(3,12,24,0.85)"
              stroke={node.color}
              strokeWidth="1"
            />
            <text x="0" y={node.sublabel ? 33 : 30} textAnchor="middle" fill="#eafaff" fontSize="12" fontWeight="700">
              {node.label.length > 10 ? `${node.label.slice(0, 10)}…` : node.label}
            </text>
            {node.sublabel && (
              <text x="0" y="46" textAnchor="middle" fill={node.color} fontSize="10">
                {node.sublabel.length > 14 ? `${node.sublabel.slice(0, 14)}…` : node.sublabel}
              </text>
            )}
          </g>
        );
      })}
    </svg>
  );
}


