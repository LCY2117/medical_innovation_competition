import type { AedSite, ClientInfo, IncidentState } from '@/shared/types';
import type { SpotlightTarget } from '@/shared/spotlight';
import { hasGuideCompleted, hasRunnerDelivered, hasRunnerPicked, hasPrimeStarted } from '@/shared/domain';

export type SceneNodeKind = 'patient' | 'prime' | 'runner' | 'guide' | 'aed' | 'ambulance';

export interface SceneNode {
  id: string;
  kind: SceneNodeKind;
  label: string;
  sublabel?: string;
  x: number;
  y: number;
  color: string;
  focused: boolean;
  active: boolean;
  latitude?: number | null;
  longitude?: number | null;
  realLatitude?: number | null;
  realLongitude?: number | null;
  moveTarget?: { x: number; y: number; latitude: number | null; longitude: number | null } | null;
}

export interface SceneLink {
  id: string;
  from: string;
  to: string;
  kind: 'fly' | 'signal';
  active: boolean;
}

export interface SceneModel {
  nodes: SceneNode[];
  links: SceneLink[];
  radarTarget: string | null;
  phase: string | null;
}

const COLORS: Record<SceneNodeKind, string> = {
  patient: '#ff4d6d',
  prime: '#34f5a8',
  runner: '#4be3ff',
  guide: '#ffc857',
  aed: '#17e5c3',
  ambulance: '#eef6ff',
};

const DEFAULT_LAYOUT: Array<Pick<SceneNode, 'id' | 'kind' | 'x' | 'y'>> = [
  { id: 'patient', kind: 'patient', x: 0, y: 0 },
  { id: 'prime', kind: 'prime', x: -72, y: 44 },
  { id: 'runner', kind: 'runner', x: 88, y: -38 },
  { id: 'guide', kind: 'guide', x: 34, y: -92 },
  { id: 'aed-1', kind: 'aed', x: -118, y: -76 },
  { id: 'aed-2', kind: 'aed', x: 122, y: 62 },
];

function latLngToMeters(lat: number, lng: number, centerLat: number, centerLng: number): [number, number] {
  const metersPerDegreeLat = 111320;
  const metersPerDegreeLng = 111320 * Math.cos((centerLat * Math.PI) / 180);
  return [(lng - centerLng) * metersPerDegreeLng, (lat - centerLat) * metersPerDegreeLat];
}

interface PointInput {
  id: string;
  lat?: number | null;
  lng?: number | null;
  label?: string | null;
}

function computePositions(
  points: Array<PointInput & { fallback?: [number, number] }>,
  centerLat: number,
  centerLng: number,
): {
  positions: Map<string, { x: number; y: number }>;
  latLng: Map<string, [number, number]>;
  metersPerUnit: number;
} {
  const result = new Map<string, { x: number; y: number }>();
  const latLng = new Map<string, [number, number]>();
  let maxExtent = 0;
  const raw = new Map<string, { x: number; y: number; used: boolean }>();

  for (const point of points) {
    if (typeof point.lat === 'number' && typeof point.lng === 'number') {
      const [x, y] = latLngToMeters(point.lat, point.lng, centerLat, centerLng);
      raw.set(point.id, { x, y, used: true });
      maxExtent = Math.max(maxExtent, Math.abs(x), Math.abs(y));
    }
  }

  // 真实坐标过于聚集时退化为演示布局，保证大屏可读性
  let metersPerUnit = maxExtent > 0 ? maxExtent / 95 : 2;
  if (maxExtent < 25) {
    metersPerUnit = 2;
    for (const point of points) {
      if (point.fallback) {
        result.set(point.id, { x: point.fallback[0], y: point.fallback[1] });
      }
    }
  } else {
    for (const [id, value] of raw) {
      result.set(id, { x: value.x / metersPerUnit, y: value.y / metersPerUnit });
    }
  }

  // 鏈€灏忛棿璺濓細鎶婅繃浜庨潬杩戠殑鐐规帹寮€锛屼繚璇佸ぇ灞忎笂鏍囪涓庢爣绛句笉閲嶅彔
  // real positions only: label collision is handled by the renderer,
  // so points keep their true physical coordinates

  // convert final unit positions back to (virtual) lat/lng for real basemaps
  const metersPerDegreeLat = 111320;
  const metersPerDegreeLng = 111320 * Math.cos((centerLat * Math.PI) / 180);
  for (const [id, value] of result) {
    latLng.set(id, [
      centerLat + (value.y * metersPerUnit) / metersPerDegreeLat,
      centerLng + (value.x * metersPerUnit) / metersPerDegreeLng,
    ]);
  }

  return { positions: result, latLng, metersPerUnit };
}

export function buildSceneModel(
  incidentState: IncidentState | null,
  clients: ClientInfo[],
  aedSites: AedSite[],
  spotlightTarget: SpotlightTarget | null,
): SceneModel {
  const patientClient = clients.find((client) => client.isPatient || client.patientCandidate) ?? null;
  const centerLat = patientClient?.location?.latitude ?? 39.915976;
  const centerLng = patientClient?.location?.longitude ?? 116.465922;

  const primeClient = clients.find((client) => client.userId === incidentState?.roles?.PRIME?.userId) ?? null;
  const runnerClient = clients.find((client) => client.userId === incidentState?.roles?.RUNNER?.userId) ?? null;
  const guideClient = clients.find((client) => client.userId === incidentState?.roles?.GUIDE?.userId) ?? null;

  const fallbackById: Record<string, [number, number]> = Object.fromEntries(
    DEFAULT_LAYOUT.map((entry) => [entry.id, [entry.x, entry.y]]),
  );

  const points: Array<PointInput & { fallback?: [number, number] }> = [
    {
      id: 'patient',
      lat: patientClient?.location?.latitude ?? 39.916156,
      lng: patientClient?.location?.longitude ?? 116.465571,
      label: patientClient?.location?.label ?? '交通和苑 8 号楼前广场',
      fallback: fallbackById.patient,
    },
    {
      id: 'prime',
      lat: primeClient?.location?.latitude ?? 39.916030,
      lng: primeClient?.location?.longitude ?? 116.466039,
      label: primeClient?.location?.label ?? '交通和苑中心花园',
      fallback: fallbackById.prime,
    },
    {
      id: 'runner',
      lat: runnerClient?.location?.latitude ?? 39.915868,
      lng: runnerClient?.location?.longitude ?? 116.466566,
      label: runnerClient?.location?.label ?? '交通和苑物业用房',
      fallback: fallbackById.runner,
    },
    {
      id: 'guide',
      lat: guideClient?.location?.latitude ?? 39.915509,
      lng: guideClient?.location?.longitude ?? 116.464892,
      label: guideClient?.location?.label ?? '交通和苑北门出入口',
      fallback: fallbackById.guide,
    },
    ...aedSites.map((site, index) => ({
      id: site.siteId,
      lat: site.location.latitude,
      lng: site.location.longitude,
      label: site.location.label ?? site.name,
      fallback: fallbackById[`aed-${index + 1}`] ?? [index % 2 === 0 ? -100 : 100, -60 - index * 40],
    })),
  ];

  const { positions, latLng, metersPerUnit } = computePositions(points, centerLat, centerLng);
  const phase = incidentState?.phase ?? null;

  const nodes: SceneNode[] = [];
  const pointById = new Map(points.map((point) => [point.id, point]));
  const pushNode = (
    id: string,
    kind: SceneNodeKind,
    label: string,
    sublabel: string | undefined,
    active: boolean,
  ) => {
    const position = positions.get(id);
    if (!position) {
      return;
    }
    nodes.push({
      id,
      kind,
      label,
      sublabel,
      x: position.x,
      y: position.y,
      color: COLORS[kind],
      focused: spotlightTarget === kind.toUpperCase().replace('AED', 'AED'),
      active,
      latitude: latLng.get(id)?.[0] ?? pointById.get(id)?.lat ?? null,
      longitude: latLng.get(id)?.[1] ?? pointById.get(id)?.lng ?? null,
      realLatitude: pointById.get(id)?.lat ?? null,
      realLongitude: pointById.get(id)?.lng ?? null,
    });
  };

  const patientStatus =
    incidentState?.sos?.status === 'ALERTING'
      ? 'SOS 告警中'
      : incidentState
        ? phase === 'CREATED'
          ? '监测中'
          : '协同处置中'
        : '未接入';
  pushNode('patient', 'patient', '患者端', patientStatus, Boolean(incidentState));
  pushNode(
    'prime',
    'prime',
    primeClient?.displayName ?? '核心施救',
    primeClient ? incidentState?.roles?.PRIME?.status ?? '待命' : '未接入',
    Boolean(incidentState?.roles?.PRIME?.userId),
  );
  pushNode(
    'runner',
    'runner',
    runnerClient?.displayName ?? 'AED 保障',
    runnerClient ? incidentState?.roles?.RUNNER?.status ?? '待命' : '未接入',
    Boolean(incidentState?.roles?.RUNNER?.userId),
  );
  pushNode(
    'guide',
    'guide',
    guideClient?.displayName ?? '环境清障',
    guideClient ? incidentState?.roles?.GUIDE?.status ?? '待命' : '未接入',
    Boolean(incidentState?.roles?.GUIDE?.userId),
  );
  aedSites.forEach((site, index) => {
    pushNode(
      site.siteId,
      'aed',
      site.name,
      `AED-${index + 1}`,
      site.status === 'AVAILABLE',
    );
  });

  // 救护车：仅在事件推进到救护阶段出现
  if (hasGuideCompleted(incidentState) || phase === 'HANDOVER' || phase === 'ARCHIVED') {
    nodes.push({
      id: 'ambulance',
      kind: 'ambulance',
      label: '120 急救',
      sublabel: '已到场',
      x: 0,
      y: 140,
      color: COLORS.ambulance,
      focused: spotlightTarget === 'GUIDE',
      active: true,
      latitude: centerLat,
      longitude: centerLng,
    });
  }

  // 事件驱动的角色移动目标：点位随事件阶段设置目标，渲染层做平滑插值动画
  const patientNodeForMove = nodes.find((node) => node.kind === 'patient');
  const aedNodesForMove = nodes.filter((node) => node.kind === 'aed');
  // 到达患者旁时停在侧旁错开的位置，避免标签重叠（RUNNER 站患者右下，PRIME 站左上）
  const approachTarget = (
    target: SceneNode,
    slot: 'runner' | 'prime',
  ): { x: number; y: number; latitude: number | null; longitude: number | null } => {
    const dx = slot === 'runner' ? 24 : -24;
    const dy = slot === 'runner' ? -18 : 18;
    const metersPerDegreeLat = 111320;
    const metersPerDegreeLng = 111320 * Math.cos((centerLat * Math.PI) / 180);
    return {
      x: target.x + dx,
      y: target.y + dy,
      latitude:
        typeof target.latitude === 'number'
          ? target.latitude + (dy * metersPerUnit) / metersPerDegreeLat
          : null,
      longitude:
        typeof target.longitude === 'number'
          ? target.longitude + (dx * metersPerUnit) / metersPerDegreeLng
          : null,
    };
  };
  const setMoveTarget = (
    nodeId: string,
    target: SceneNode | { x: number; y: number; latitude: number | null; longitude: number | null } | null,
  ) => {
    const node = nodes.find((item) => item.id === nodeId);
    if (!node) {
      return;
    }
    if (!target) {
      node.moveTarget = null;
      return;
    }
    node.moveTarget = {
      x: target.x,
      y: target.y,
      latitude: typeof target.latitude === 'number' ? target.latitude : null,
      longitude: typeof target.longitude === 'number' ? target.longitude : null,
    };
  };
  const runnerNodeForMove = nodes.find((node) => node.kind === 'runner');
  if (runnerNodeForMove) {
    let nearestAed: SceneNode | null = null;
    let nearestAedDist = Infinity;
    for (const aed of aedNodesForMove) {
      const dist = (aed.x - runnerNodeForMove.x) ** 2 + (aed.y - runnerNodeForMove.y) ** 2;
      if (dist < nearestAedDist) {
        nearestAedDist = dist;
        nearestAed = aed;
      }
    }
    if (hasRunnerDelivered(incidentState) || hasRunnerPicked(incidentState)) {
      // 已取到 / 已送达：前往患者身边（站侧旁，避免与患者标签重叠）
      if (patientNodeForMove) setMoveTarget('runner', approachTarget(patientNodeForMove, 'runner'));
    } else if (incidentState?.roles?.RUNNER?.status === 'JOINED' && phase === 'DISPATCHED') {
      // 已响应：前往最近 AED
      setMoveTarget('runner', nearestAed);
    }
  }
  const primeNodeForMove = nodes.find((node) => node.kind === 'prime');
  if (primeNodeForMove && patientNodeForMove && hasPrimeStarted(incidentState)) {
    // 核心施救已开始：前往患者身边（站侧旁，避免与患者标签重叠）
    setMoveTarget('prime', approachTarget(patientNodeForMove, 'prime'));
  }

  const links: SceneLink[] = [];
  const patientNode = nodes.find((node) => node.kind === 'patient');
  if (patientNode) {
    if (incidentState?.phase === 'DISPATCHING') {
      for (const role of ['PRIME', 'RUNNER', 'GUIDE']) {
        const node = nodes.find((item) => item.id === role.toLowerCase());
        if (node) {
          links.push({ id: `signal-${role}`, from: 'patient', to: node.id, kind: 'signal', active: true });
        }
      }
    }
    const runnerNode = nodes.find((node) => node.kind === 'runner');
    const aedNode = nodes.find((node) => node.kind === 'aed');
    if (runnerNode && aedNode) {
      if (hasRunnerPicked(incidentState) && !hasRunnerDelivered(incidentState)) {
        links.push({ id: 'fly-runner-aed', from: runnerNode.id, to: 'patient', kind: 'fly', active: true });
      }
      if (incidentState?.roles?.RUNNER?.status === 'JOINED' && phase === 'DISPATCHED') {
        links.push({ id: 'fly-runner-to-aed', from: 'runner', to: aedNode.id, kind: 'fly', active: true });
      }
    }
    const primeNode = nodes.find((node) => node.kind === 'prime');
    if (primeNode && hasPrimeStarted(incidentState)) {
      links.push({ id: 'fly-prime', from: 'prime', to: 'patient', kind: 'fly', active: true });
    }
  }

  const radarTarget =
    incidentState?.sos?.status === 'ALERTING'
      ? 'patient'
      : spotlightTarget === 'PATIENT'
        ? 'patient'
        : spotlightTarget === 'RUNNER'
          ? 'runner'
          : spotlightTarget === 'PRIME'
            ? 'prime'
            : spotlightTarget === 'GUIDE'
              ? 'guide'
              : null;

  return { nodes, links, radarTarget, phase };
}

export function spotlightToSceneId(target: SpotlightTarget | null): string | null {
  if (!target) {
    return null;
  }
  switch (target) {
    case 'PATIENT':
      return 'patient';
    case 'PRIME':
      return 'prime';
    case 'RUNNER':
      return 'runner';
    case 'GUIDE':
      return 'guide';
    case 'AED':
      return null;
    default:
      return null;
  }
}
