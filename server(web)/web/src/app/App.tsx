import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  Heart, 
  Activity, 
  MapPin, 
  Shield, 
  Zap, 
  Ambulance, 
  Smartphone, 
  Clock, 
  CheckCircle2, 
  AlertTriangle,
  Users,
  Radio,
  FileText,
  Copy,
  ChevronDown,
  ChevronRight,
  RotateCcw,
  Download,
  ExternalLink,
  Navigation,
  X,
  ArrowUp,
  KeyRound,
  Siren,
  Moon,
  Sun,
  Lock,
  Unlock,
  ShieldCheck,
  HeartPulse,
  LogIn,
  LogOut
} from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { formatHealthRiskTags, formatHealthSignalSummary, mergeIncidentState, roleNames, translateHealthSource } from '@/shared/domain';
import type { HealthSignalSummary, IncidentState as SharedIncidentState } from '@/shared/types';

// Utility for Tailwind classes
function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

function formatElapsed(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

function formatArchiveDurationLabel(state: IncidentState | null, nowMs: number): string {
  const startedAt = state?.logs?.[0]?.ts;
  if (!state || !startedAt) {
    return '待生成';
  }
  const lastLogTs = state.logs[state.logs.length - 1]?.ts ?? startedAt;
  const endedAt = state.phase === 'HANDOVER' || state.phase === 'ARCHIVED' ? lastLogTs : nowMs;
  return formatElapsed(Math.max(0, Math.floor((endedAt - startedAt) / 1000)));
}

function formatArchiveRoleCount(state: IncidentState | null): string {
  if (!state) {
    return '待生成';
  }
  const count = roleNames.filter((role) => Boolean(state.roles[role]?.userId)).length;
  return count > 0 ? `${count}类任务` : '待生成';
}

function formatArchiveAedSummary(state: IncidentState | null): string {
  if (!state) {
    return '待生成';
  }
  const primeStatus = state.roles.PRIME?.status;
  const runnerStatus = state.roles.RUNNER?.status;
  if (primeStatus === 'AED_SHOCK_DELIVERED' || state.phase === 'SHOCK_DELIVERED') {
    return '电击记录 1 次';
  }
  if (primeStatus === 'AED_ANALYZING' || state.phase === 'AED_ANALYZING') {
    return 'AED 分析已记录';
  }
  if (runnerStatus === 'AED_DELIVERED' || state.phase === 'AED_DELIVERED' || state.phase === 'HANDOVER' || state.phase === 'ARCHIVED') {
    return 'AED 已送达';
  }
  if (runnerStatus === 'AED_PICKED' || state.phase === 'AED_PICKED') {
    return 'AED 已取用';
  }
  return '未记录';
}

function getResuscitationGuidance(elapsedSec: number) {
  const cycleTotal = 120;
  const cycleRemaining = cycleTotal - (elapsedSec % cycleTotal);
  const blockElapsed = elapsedSec % 20;
  const breathing = blockElapsed >= 16;
  const blockRemaining = breathing ? 20 - blockElapsed : 16 - blockElapsed;
  return {
    cycleRemaining: Math.max(0, cycleRemaining),
    stageRemaining: Math.max(0, blockRemaining),
    stageTitle: breathing ? '人工呼吸阶段' : '胸外按压阶段',
    stageAction: breathing ? '2 次人工呼吸' : '30 次胸外按压',
    stageBody: breathing
      ? '保持气道开放，完成 2 次人工呼吸后立刻恢复胸外按压。'
      : '保持 100-120 次/分钟按压节律，深度 5-6 厘米，尽量减少中断。',
  };
}

function getLatestLogTs(state: IncidentState | null, keyword: string): number | null {
  if (!state?.logs?.length) {
    return null;
  }
  for (let index = state.logs.length - 1; index >= 0; index -= 1) {
    const entry = state.logs[index];
    if (entry.msg.toLowerCase().includes(keyword.toLowerCase())) {
      return entry.ts;
    }
  }
  return null;
}

function isRoleJoined(status?: string | null): boolean {
  if (!status) {
    return false;
  }
  const joinedStatuses = new Set([
    'ASSIGNED',
    'JOINED',
    'AED_PICKED',
    'AED_DELIVERED',
    'CPR_STARTED',
    'AMBULANCE_ARRIVED',
    'CPR',
  ]);
  return joinedStatuses.has(status);
}

function hasPrimeStarted(state?: IncidentState | null): boolean {
  return state?.roles?.PRIME?.status === 'CPR_STARTED';
}

function hasRunnerPicked(state?: IncidentState | null): boolean {
  const status = state?.roles?.RUNNER?.status;
  return status === 'AED_PICKED' || status === 'AED_DELIVERED';
}

function hasRunnerDelivered(state?: IncidentState | null): boolean {
  return state?.roles?.RUNNER?.status === 'AED_DELIVERED';
}

function hasGuideCompleted(state?: IncidentState | null): boolean {
  return state?.roles?.GUIDE?.status === 'AMBULANCE_ARRIVED' || state?.roles?.GUIDE?.status === 'HANDOVER_COMPLETED' || state?.phase === 'HANDOVER' || state?.phase === 'ARCHIVED';
}

function isAedAnalyzing(state?: IncidentState | null): boolean {
  return state?.roles?.PRIME?.status === 'AED_ANALYZING' || state?.phase === 'AED_ANALYZING';
}

function isShockDelivered(state?: IncidentState | null): boolean {
  return state?.roles?.PRIME?.status === 'AED_SHOCK_DELIVERED' || state?.phase === 'SHOCK_DELIVERED';
}

function mapServerPhaseToScenarioPhase(state?: IncidentState | null): ScenarioPhase {
  if (!state) {
    return 'intro';
  }
  const { phase: serverPhase, roles } = state;
  const primeActive = isRoleJoined(roles?.PRIME?.status);
  const runnerActive = isRoleJoined(roles?.RUNNER?.status);
  const guideActive = isRoleJoined(roles?.GUIDE?.status);
  switch (serverPhase) {
    case 'CREATED':
      if (primeActive || runnerActive || guideActive) {
        return 'dispatch';
      }
      return 'trigger';
    case 'DISPATCHING':
      return 'dispatch';
    case 'DISPATCH':
    case 'DISPATCHED':
      if (primeActive) {
        return 'action';
      }
      return 'dispatch';
    case 'CPR':
    case 'AED_PICKED':
      return 'action';
    case 'AED_DELIVERED':
    case 'AED_ANALYZING':
    case 'SHOCK_DELIVERED':
      return 'convergence';
    case 'HANDOVER':
      return 'handover';
    case 'ARCHIVED':
      return 'summary';
    default:
      return serverPhase ? 'action' : 'intro';
  }
}

// --- Data & Types ---

type RoleType = 'doctor' | 'student' | 'security' | 'victim';

type ScenarioPhase = 
  | 'intro'
  | 'trigger'
  | 'dispatch'
  | 'action'
  | 'convergence'
  | 'handover'
  | 'summary';

interface LogEntry {
  id: string;
  time: string;
  source: string;
  message: string;
  type: 'info' | 'alert' | 'success';
}

function classifyLogType(message: string): LogEntry['type'] {
  const normalized = message.toLowerCase();
  if (/unknown|error|fail|failed|exception|not found|forbidden|unauthorized|invalid|timeout/.test(normalized)) {
    return 'alert';
  }
  if (/assigned|joined|delivered|completed|started|created|arrived|triggered/.test(normalized)) {
    return 'success';
  }
  return 'info';
}

type ServerPhase =
  | 'CREATED'
  | 'DISPATCHING'
  | 'DISPATCHED'
  | 'AED_PICKED'
  | 'AED_DELIVERED'
  | 'CPR'
  | 'HANDOVER'
  | 'ARCHIVED'
  | string;

interface IncidentState {
  incidentId: string;
  phase: ServerPhase;
  sos?: { status: string; startTs: number | null; durationSec: number };
  patientUserId?: string | null;
  dispatchSource?: string | null;
  roles: {
    PRIME: { status: string; userId: string | null };
    RUNNER: { status: string; userId: string | null };
    GUIDE: { status: string; userId: string | null };
  };
  logs: { ts: number; msg: string }[];
  aedSites?: AedSite[];
  dispatchRationale?: Record<string, DispatchRoleDecision>;
}

interface GeoPoint {
  latitude: number;
  longitude: number;
  accuracyMeters?: number | null;
  label?: string | null;
  floor?: string | null;
  source?: string;
  updatedTs?: number | null;
}

interface AedSite {
  siteId: string;
  name: string;
  location: GeoPoint;
  status: string;
  accessNotes?: string;
  lastCheckedTs?: number | null;
}

interface DispatchRoleDecision {
  userId?: string | null;
  score: number;
  reasons: string[];
  warnings: string[];
  distanceToPatientMeters?: number | null;
  nearestAedSiteId?: string | null;
  distanceToAedMeters?: number | null;
  aedToPatientMeters?: number | null;
}

interface ClientInfo {
  userId: string;
  displayName: string;
  organization: string;
  healthCondition: string;
  professionIdentity: string;
  profileBio: string;
  deviceType: string;
  online: boolean;
  lastSeenTs: number;
  assignedRole?: string | null;
  patientCandidate?: boolean;
  isPatient?: boolean;
  location?: GeoPoint | null;
  healthSignals?: HealthSignalSummary | null;
}

interface DispatchMeta {
  configured: boolean;
  provider: string;
  dispatchDelaySec: number;
  model: string;
  baseUrl: string;
  timeoutSec: number;
  configFile: string;
  envKeys: string[];
  candidateFields: string[];
  selectionRules: Record<string, string>;
  responseFormat: Record<string, string>;
  systemPrompt: string;
  mapProvider?: Record<string, unknown>;
}

interface HealthDetail {
  demoAdminAuthEnabled?: boolean;
  auth?: {
    adminAccountAuthEnabled?: boolean;
    adminPhoneCount?: number;
  };
  frontend?: { ok?: boolean };
  mapProvider?: Record<string, unknown>;
  pushProvider?: Record<string, unknown>;
  demoReadiness?: DemoReadiness;
}

interface DemoReadiness {
  ready?: boolean;
  patientSelected?: boolean;
  clientCount?: number;
  assignedRoleCount?: number;
  availableAedSiteCount?: number;
  locationCoveragePercent?: number;
  healthCoveragePercent?: number;
  exportReady?: boolean;
  warnings?: string[];
}

interface AdminSessionUser {
  userId: string;
  displayName: string;
  phone: string;
  privileges?: string[];
}

interface AdminSession {
  token: string;
  user: AdminSessionUser;
  tokenExpiresAt?: number | null;
}

interface AuditEvent {
  eventId: string;
  ts: number;
  eventType: string;
  actorType: string;
  actorId?: string | null;
  targetType?: string | null;
  targetId?: string | null;
  outcome: string;
  requestHash?: string | null;
  metadata?: Record<string, string | number | boolean | null>;
}

type ThemeMode = 'dark' | 'light';

const ENV_API_BASE = import.meta.env.VITE_API_BASE?.trim();
const ENV_WS_BASE = import.meta.env.VITE_WS_BASE?.trim();

function normalizeBaseUrl(value: string): string {
  return value.endsWith('/') ? value.slice(0, -1) : value;
}

function getApiBase(): string {
  if (ENV_API_BASE) {
    return normalizeBaseUrl(ENV_API_BASE);
  }
  if (typeof window === 'undefined') {
    return '/api';
  }
  return `${window.location.origin}/api`;
}

function getWsBase(): string {
  if (ENV_WS_BASE) {
    return normalizeBaseUrl(ENV_WS_BASE);
  }
  if (typeof window === 'undefined') {
    return '/ws';
  }
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${protocol}//${window.location.host}/ws`;
}

function translatePhaseLabel(phase?: string | null): string {
  switch (phase) {
    case 'CREATED':
      return '监测中';
    case 'DISPATCHING':
      return '智能分派中';
    case 'DISPATCHED':
      return '任务已下发';
    case 'CPR':
      return 'CPR 进行中';
    case 'AED_PICKED':
      return 'AED 已取到';
    case 'AED_DELIVERED':
      return 'AED 已送达';
    case 'AED_ANALYZING':
      return 'AED 分析中';
    case 'SHOCK_DELIVERED':
      return '已完成除颤';
    case 'HANDOVER':
      return '完成交接';
    case 'ARCHIVED':
      return '已归档';
    default:
      return phase ?? '未开始';
  }
}

function translateDispatchSourceLabel(source?: string | null): string {
  switch (source?.trim()) {
    case 'fallback':
      return '规则兜底';
    case 'ai':
    case 'local_model':
      return '本地智能分派';
    case 'siliconflow':
      return '云端智能分派';
    case '':
    case undefined:
    case null:
      return '智能分派处理中';
    default:
      return /[A-Za-z_]/.test(source) ? '智能分派' : source;
  }
}

function translateRoleLabel(role?: string | null): string {
  switch (role) {
    case 'PRIME':
      return '核心施救';
    case 'RUNNER':
      return 'AED 保障';
    case 'GUIDE':
      return '环境清障';
    default:
      return '未分配';
  }
}

function translateRoleStatus(status?: string | null): string {
  switch (status) {
    case '':
      return '待命';
    case 'ASSIGNED':
      return '已分配';
    case 'JOINED':
      return '已响应';
    case 'CPR_STARTED':
      return '已开始 CPR';
    case 'AED_PICKED':
      return '已取到 AED';
    case 'AED_DELIVERED':
      return '已送达 AED';
    case 'AED_ANALYZING':
      return 'AED 分析中';
    case 'AED_SHOCK_DELIVERED':
      return '已完成一次除颤';
    case 'AMBULANCE_ARRIVED':
      return '救护车已到场';
    case 'HANDOVER_COMPLETED':
      return '交接已完成';
    case 'CPR':
      return 'CPR 进行中';
    default:
      return status ?? '待命';
  }
}

function translateScenarioPhaseLabel(phase?: ScenarioPhase | null): string {
  switch (phase) {
    case 'intro':
      return '未开始';
    case 'trigger':
      return '患者告警';
    case 'dispatch':
      return '智能分派';
    case 'action':
      return '现场处置';
    case 'convergence':
      return 'AED 汇合';
    case 'handover':
      return '救护交接';
    case 'summary':
      return '记录归档';
    default:
      return '未开始';
  }
}

function translateAedStatus(status?: string | null): string {
  switch (status) {
    case 'AVAILABLE':
      return '可用';
    case 'MAINTENANCE':
      return '维护中';
    case 'UNAVAILABLE':
      return '不可用';
    default:
      return status || '未知';
  }
}

function translateAuditEventType(type: string): string {
  const labels: Record<string, string> = {
    auth_register: '账号注册',
    auth_login: '账号登录',
    auth_logout: '退出登录',
    auth_demo_login: '演示身份登录',
    demo_admin_denied: '管理口令拒绝',
    admin_denied: '管理权限拒绝',
    admin_user_denied: '管理员账号拒绝',
    incident_created: '创建事件',
    incident_reset: '重置事件',
    demo_bootstrapped: '初始化演示',
    patient_designated: '指定患者',
    role_joined: '角色响应',
    role_auto_joined: '自动接单',
    incident_action_posted: '现场动作',
    sos_started: '启动 SOS',
    sos_cancelled: '取消 SOS',
    patient_sos_started: '患者 SOS',
    patient_sos_cancelled: '患者取消 SOS',
    incident_triggered: '触发事件',
    experiment_exported: '导出 JSON',
    experiment_package_exported: '导出证据包',
    audit_events_viewed: '查看审计',
    aed_site_upserted: '更新 AED',
    client_registered: '终端接入',
    client_location_updated: '位置更新',
    client_health_updated: '健康摘要更新',
    actor_user_mismatch: '终端身份不符',
  };
  return labels[type] ?? type;
}

function translateAuditOutcome(outcome: string): string {
  switch (outcome) {
    case 'success':
      return '成功';
    case 'denied':
      return '拒绝';
    default:
      return outcome || '--';
  }
}

function summarizeActor(value?: string | null): string {
  if (!value) {
    return '--';
  }
  if (value === 'demo_admin') {
    return '演示口令';
  }
  if (value === 'open_demo_admin') {
    return '本地演示';
  }
  return value;
}

function translateLogMessage(message: string, displayUser: (userId?: string | null) => string): string {
  let match = message.match(/^Patient designated by (.+) \((.+)\)$/);
  if (match) {
    const source = match[1].startsWith('patient SOS') ? '患者端 SOS' : match[1] === 'dashboard' ? '调度台' : match[1];
    return `${source}确认患者：${displayUser(match[2])}`;
  }
  match = message.match(/^Patient SOS alerting started \((.+)\)$/);
  if (match) {
    return `患者端启动 SOS：${displayUser(match[1])}`;
  }
  match = message.match(/^Patient SOS confirmed \((.+)\)$/);
  if (match) {
    return `患者端 SOS 已确认：${displayUser(match[1])}`;
  }
  match = message.match(/^Patient SOS alerting canceled \((.+)\)$/);
  if (match) {
    return `患者端取消 SOS：${displayUser(match[1])}`;
  }
  match = message.match(/^(PRIME|RUNNER|GUIDE) assigned \((.+)\) via (.+)$/);
  if (match) {
    const source = translateDispatchSourceLabel(match[3]);
    return `${translateRoleLabel(match[1])} 已分派给 ${displayUser(match[2])}（${source}）`;
  }
  match = message.match(/^(PRIME|RUNNER|GUIDE) joined \((.+)\)$/);
  if (match) {
    return `${translateRoleLabel(match[1])} 已响应：${displayUser(match[2])}`;
  }
  match = message.match(/^CPR started \((.+)\)$/);
  if (match) {
    return `核心施救开始 CPR：${displayUser(match[1])}`;
  }
  match = message.match(/^AED picked \((.+)\)$/);
  if (match) {
    return `AED 保障已取到设备：${displayUser(match[1])}`;
  }
  match = message.match(/^AED delivered \((.+)\)$/);
  if (match) {
    return `AED 已送达患者旁：${displayUser(match[1])}`;
  }
  match = message.match(/^AED analysis started \((.+)\)$/);
  if (match) {
    return `AED 分析已开始：${displayUser(match[1])}`;
  }
  match = message.match(/^AED shock delivered \((.+)\)$/);
  if (match) {
    return `已完成一次 AED 除颤：${displayUser(match[1])}`;
  }
  match = message.match(/^Ambulance arrived \((.+)\)$/);
  if (match) {
    return `救护车已到场：${displayUser(match[1])}`;
  }
  match = message.match(/^Handover completed \((.+)\)$/);
  if (match) {
    return `现场交接已完成：${displayUser(match[1])}`;
  }
  if (message === 'Incident created') {
    return '事件已创建';
  }
  if (message === 'Incident reset') {
    return '事件已重置';
  }
  if (message === 'AI dispatching started') {
    return '智能分派已启动';
  }
  if (message === 'Demo scenario bootstrapped') {
    return '协同演示场景已初始化';
  }
  if (message === 'Incident auto-triggered') {
    return '事件已自动触发';
  }
  if (message.startsWith('AED site updated')) {
    return message.replace('AED site updated', 'AED 点位已更新');
  }
  return message;
}

function formatTimeLabel(ts?: number | null): string {
  if (!ts) {
    return '--:--:--';
  }
  return new Date(ts).toLocaleTimeString('zh-CN', { hour12: false });
}

function getStoredDemoAdminToken(): string {
  if (typeof window === 'undefined') {
    return '';
  }
  return window.localStorage.getItem('lra_demo_admin_token') ?? '';
}

const ADMIN_SESSION_KEY = 'lra_admin_session';

const mobileDemoEntries = [
  { key: 'patient', label: '患者端', caption: '触发 SOS' },
  { key: 'prime', label: '核心施救', caption: 'CPR 与 AED 分析' },
  { key: 'runner', label: 'AED 保障', caption: '取送设备' },
  { key: 'guide', label: '清障接驳', caption: '通道与救护车接应' },
] as const;

function getStoredAdminSession(): AdminSession | null {
  if (typeof window === 'undefined') {
    return null;
  }
  try {
    const raw = window.localStorage.getItem(ADMIN_SESSION_KEY);
    return raw ? (JSON.parse(raw) as AdminSession) : null;
  } catch {
    return null;
  }
}

function getStoredThemeMode(): ThemeMode {
  if (typeof window === 'undefined') {
    return 'dark';
  }
  const stored = window.localStorage.getItem('lra_theme_mode');
  if (stored === 'dark' || stored === 'light') {
    return stored;
  }
  if (window.matchMedia?.('(prefers-color-scheme: light)').matches) {
    return 'light';
  }
  return 'dark';
}

function buildAdminHeaders(demoToken: string, adminToken: string | null | undefined, extra?: HeadersInit): HeadersInit {
  const headers = new Headers(extra);
  const trimmedAdminToken = adminToken?.trim();
  if (trimmedAdminToken) {
    headers.set('Authorization', `Bearer ${trimmedAdminToken}`);
  }
  const trimmedDemoToken = demoToken.trim();
  if (trimmedDemoToken) {
    headers.set('X-Demo-Admin-Token', trimmedDemoToken);
  }
  return headers;
}

function explainStatusError(status: number, fallback: string): string {
  if (status === 401) {
    return `${fallback}：请先登录管理员账号`;
  }
  if (status === 403) {
    return `${fallback}：需要管理员账号或演示口令`;
  }
  return `${fallback}（${status}）`;
}

async function explainResponseError(response: Response, fallback: string): Promise<string> {
  try {
    const payload = await response.clone().json();
    const detail = typeof payload?.detail === 'string' ? payload.detail : '';
    if (detail) {
      return `${fallback}：${detail}`;
    }
  } catch {
    // Fall back to status-only text below.
  }
  return explainStatusError(response.status, fallback);
}

function formatDistanceLabel(value?: number | null): string {
  if (value === undefined || value === null || Number.isNaN(value)) {
    return '--';
  }
  if (value >= 1000) {
    return `${(value / 1000).toFixed(2)} km`;
  }
  return `${Math.round(value)} m`;
}

function formatLocationLabel(location?: GeoPoint | null): string {
  if (!location) {
    return '未上报位置';
  }
  const floor = location.floor ? ` · ${location.floor}` : '';
  const accuracy = location.accuracyMeters ? ` · 精度 ${formatDistanceLabel(location.accuracyMeters)}` : '';
  return `${location.label ?? '模拟点位'}${floor}${accuracy}`;
}

function formatTechnicalValue(value: unknown): string {
  if (value === undefined || value === null || value === '') {
    return '--';
  }
  if (typeof value === 'string') {
    const labels: Record<string, string> = {
      demo: '演示距离模型',
      amap: '高德地图服务',
      tencent: '腾讯地图服务',
      baidu: '百度地图服务',
      haversine_demo: '演示直线距离',
      amap_web_service: '高德 WebService 距离',
      amap_service_key_missing: '高德服务 Key 未配置，已使用演示距离',
      amap_timeout: '高德服务超时，已使用演示距离',
      amap_distance_failed: '高德距离接口异常，已使用演示距离',
      unsupported_provider: '地图服务暂不支持，已使用演示距离',
      tencent_adapter_pending: '腾讯地图适配待接入，已使用演示距离',
      baidu_adapter_pending: '百度地图适配待接入，已使用演示距离',
    };
    return labels[value] ?? value;
  }
  if (typeof value === 'boolean') {
    return value ? '是' : '否';
  }
  if (Array.isArray(value)) {
    return value.length ? value.map((item) => formatTechnicalValue(item)).join('、') : '--';
  }
  if (typeof value === 'object') {
    return JSON.stringify(value);
  }
  return String(value);
}

function readinessPercent(value?: number | null): string {
  return typeof value === 'number' && Number.isFinite(value) ? `${Math.round(value)}%` : '--';
}

function downloadJson(filename: string, data: unknown): void {
  if (typeof window === 'undefined') {
    return;
  }
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json;charset=utf-8' });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

async function copyTextToClipboard(text: string): Promise<boolean> {
  if (typeof window === 'undefined' || typeof document === 'undefined') {
    return false;
  }
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text);
      return true;
    }
  } catch {
    // Fall back to a temporary textarea below.
  }
  const textarea = document.createElement('textarea');
  textarea.value = text;
  textarea.setAttribute('readonly', 'true');
  textarea.style.position = 'fixed';
  textarea.style.left = '-9999px';
  textarea.style.top = '0';
  document.body.appendChild(textarea);
  textarea.select();
  let copied = false;
  try {
    copied = document.execCommand('copy');
  } finally {
    textarea.remove();
  }
  return copied;
}

async function downloadResponseBlob(response: Response, fallbackFilename: string): Promise<void> {
  if (typeof window === 'undefined') {
    return;
  }
  const blob = await response.blob();
  const disposition = response.headers.get('Content-Disposition') ?? '';
  const encoded = disposition.match(/filename\*=UTF-8''([^;]+)/)?.[1];
  const plain = disposition.match(/filename="?([^";]+)"?/)?.[1];
  const filename = encoded ? decodeURIComponent(encoded) : plain || fallbackFilename;
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

function getDispatchStartTs(state?: IncidentState | null): number | null {
  if (!state) {
    return null;
  }
  const log = [...(state.logs ?? [])].reverse().find((entry) =>
    entry.msg.includes('AI dispatching started') || entry.msg.includes('Patient designated')
  );
  return log?.ts ?? state.logs?.[0]?.ts ?? null;
}

function buildDispatchStream(
  state: IncidentState | null,
  clients: ClientInfo[],
  dispatchMeta: DispatchMeta | null,
  nowMs: number,
) {
  if (!state?.patientUserId) {
    return [];
  }
  const patient = clients.find((client) => client.userId === state.patientUserId);
  const candidates = clients.filter((client) => client.userId !== state.patientUserId);
  const primeName = clients.find((client) => client.userId === state.roles.PRIME.userId)?.displayName ?? '未分配';
  const runnerName = clients.find((client) => client.userId === state.roles.RUNNER.userId)?.displayName ?? '未分配';
  const guideName = clients.find((client) => client.userId === state.roles.GUIDE.userId)?.displayName ?? '未分配';
  const startTs = getDispatchStartTs(state);
  const delayMs = Math.max(1, (dispatchMeta?.dispatchDelaySec ?? 3) * 1000);
  const elapsedMs = startTs ? Math.max(0, nowMs - startTs) : delayMs;
  const stepCount = 6;
  const visibleCount = state.phase === 'DISPATCHING'
    ? Math.min(stepCount, Math.max(1, Math.ceil((elapsedMs / delayMs) * stepCount)))
    : stepCount;

  const steps = [
    {
      key: 'patient',
      title: '锁定患者画像',
      detail: patient
        ? `患者端：${patient.displayName}，画像为 ${patient.healthCondition} / ${patient.professionIdentity}`
        : '根据当前事件中的患者端信息构建画像',
    },
    {
      key: 'pool',
      title: '汇总在线终端',
      detail: `当前在线 ${clients.length} 台终端，可参与协同 ${candidates.length} 台`,
    },
    {
      key: 'prime',
      title: '筛选核心施救',
      detail: dispatchMeta?.selectionRules.PRIME ?? '优先医生和系统培训急救者',
    },
    {
      key: 'runner',
      title: '筛选 AED 保障',
      detail: dispatchMeta?.selectionRules.RUNNER ?? '优先体能好、跑得快、熟悉路线的人',
    },
    {
      key: 'guide',
      title: '筛选环境清障',
      detail: dispatchMeta?.selectionRules.GUIDE ?? '优先安保、物业和现场协调人员',
    },
    {
      key: 'result',
      title: '生成任务单',
      detail:
        state.phase === 'DISPATCHED'
          ? `已完成分配：核心施救 → ${primeName}；AED 保障 → ${runnerName}；环境清障 → ${guideName}`
          : '正在生成可执行任务单，并推送到各终端',
    },
  ];

  return steps.map((step, index) => ({
    ...step,
    visible: index < visibleCount,
    done: state.phase !== 'DISPATCHING' || index + 1 < visibleCount,
    active: state.phase === 'DISPATCHING' && index + 1 === visibleCount,
  }));
}

function buildDemoFlowSteps(state: IncidentState | null) {
  const phase = state?.phase;
  const hasIncident = Boolean(state);
  const dispatchStarted = Boolean(
    state?.patientUserId ||
    phase === 'DISPATCHING' ||
    phase === 'DISPATCHED' ||
    phase === 'CPR' ||
    phase === 'AED_PICKED' ||
    phase === 'AED_DELIVERED' ||
    phase === 'AED_ANALYZING' ||
    phase === 'SHOCK_DELIVERED' ||
    phase === 'HANDOVER' ||
    phase === 'ARCHIVED',
  );
  const rolesAssigned = Boolean(
    state?.roles?.PRIME?.userId ||
    state?.roles?.RUNNER?.userId ||
    state?.roles?.GUIDE?.userId,
  );
  const rescueStarted = Boolean(hasPrimeStarted(state) || hasRunnerPicked(state) || hasGuideCompleted(state));
  const archived = phase === 'ARCHIVED';
  const handover = archived || phase === 'HANDOVER' || hasGuideCompleted(state);
  const definitions = [
    { title: '初始化场景', detail: '准备患者、救援者、AED 点位', complete: hasIncident, active: !hasIncident },
    { title: '患者 SOS', detail: '患者端触发告警并锁定位置', complete: dispatchStarted, active: hasIncident && !dispatchStarted },
    { title: '智能分派', detail: '生成核心施救、AED 保障、环境清障任务', complete: rolesAssigned, active: dispatchStarted && !rolesAssigned },
    { title: '现场处置', detail: 'CPR、AED 取送、清障接车', complete: rescueStarted || handover, active: rolesAssigned && !handover },
    { title: '交接归档', detail: '导出预实验证据包', complete: archived, active: handover && !archived },
  ];
  return definitions;
}

function describeClientMission(client: ClientInfo, state: IncidentState | null): string {
  if (!state?.patientUserId) {
    return client.patientCandidate ? '重点监测中，尚未触发事件' : '在线待命，等待事件触发';
  }
  if (client.isPatient) {
    if (state.phase === 'DISPATCHING') {
      return '已触发心脏骤停，系统正在广播红色告警并进行智能分派';
    }
    if (state.phase === 'HANDOVER') {
      return '救护车已完成现场接管，进入交接阶段';
    }
    return '保持当前位置，等待周边协同成员与救护车到场';
  }
  switch (client.assignedRole) {
    case 'PRIME':
      if (isShockDelivered(state)) {
        return '已完成一次 AED 除颤，当前应继续 CPR 并观察患者反应';
      }
      if (isAedAnalyzing(state)) {
        return 'AED 正在分析心律，等待设备给出是否建议电击';
      }
      if (hasRunnerDelivered(state)) {
        return 'AED 已送达，核心施救者正在贴附电极片并准备分析';
      }
      return hasPrimeStarted(state) ? '已在患者旁持续执行 CPR' : '立即前往患者位置，确认后开始 CPR';
    case 'RUNNER':
      if (hasRunnerDelivered(state)) {
        return 'AED 已送达现场，保持通信畅通';
      }
      if (hasRunnerPicked(state)) {
        return '已取到 AED，正在回送患者位置';
      }
      return '前往最近 AED 点位并尽快回送';
    case 'GUIDE':
      return hasGuideCompleted(state) ? '已引导救护车到场并完成交接' : '正在疏通通道并引导救护车';
    default:
      return state.phase === 'DISPATCHING' ? '正在等待智能分派结果' : '本轮未分配任务，保持待命';
  }
}

function HealthSignalBadge({ summary }: { summary?: HealthSignalSummary | null }) {
  const riskCount = summary?.riskTags?.length ?? 0;
  return (
    <div
      className={cn(
        "mt-2 inline-flex max-w-full items-center gap-2 rounded-lg border px-2.5 py-1.5 text-[10px]",
        summary
          ? riskCount > 0
            ? "border-amber-500/50 bg-amber-500/10 text-amber-200"
            : "border-emerald-500/40 bg-emerald-500/10 text-emerald-200"
          : "border-slate-700 bg-slate-900/70 text-slate-500",
      )}
    >
      <HeartPulse size={13} className="shrink-0" />
      <span className="truncate">{formatHealthSignalSummary(summary)}</span>
    </div>
  );
}

// --- Components ---

// 1. Intro Screen
const IntroScreen = ({ onStart }: { onStart: () => void }) => {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-slate-950 text-white p-8 overflow-y-auto">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-4xl w-full space-y-8 py-12"
      >
        <div className="text-center space-y-4">
          <div className="inline-flex items-center justify-center p-4 bg-red-600 rounded-full mb-4 shadow-[0_0_30px_rgba(220,38,38,0.5)]">
            <Activity size={48} className="text-white" />
          </div>
          <h1 className="text-5xl font-bold tracking-tight text-white">生命反射弧</h1>
          <p className="text-xl text-slate-400">基于端侧AI的分布式急救任务协同系统</p>
          <div className="flex items-center justify-center space-x-2 text-sm text-slate-500 uppercase tracking-widest mt-2">
            <span>方案验证</span>
            <span>•</span>
            <span>场景演练</span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
          <div className="bg-slate-900/50 p-6 rounded-xl border border-slate-800 backdrop-blur-sm">
            <div className="text-red-500 font-bold text-lg mb-2 flex items-center"><Clock size={18} className="mr-2"/> 痛点: 时间错配</div>
            <p className="text-slate-400 text-sm leading-relaxed">
              急救车平均到达 12-15 分钟 <br/>
              心脏骤停黄金抢救 4 分钟 <br/>
              <span className="text-red-400 font-bold block mt-2">结果：8分钟死亡真空</span>
            </p>
          </div>
          <div className="bg-slate-900/50 p-6 rounded-xl border border-slate-800 backdrop-blur-sm">
            <div className="text-blue-500 font-bold text-lg mb-2 flex items-center"><Navigation size={18} className="mr-2"/> 方案: 任务拆解</div>
            <ul className="text-slate-400 text-sm space-y-3">
              <li className="flex items-center"><Heart size={14} className="mr-2 text-green-400"/> 核心施救单（心肺复苏）</li>
              <li className="flex items-center"><Zap size={14} className="mr-2 text-yellow-400"/> 资源保障单（AED 转运）</li>
              <li className="flex items-center"><Shield size={14} className="mr-2 text-blue-400"/> 环境清障单（通道疏通）</li>
            </ul>
          </div>
          <div className="bg-slate-900/50 p-6 rounded-xl border border-slate-800 backdrop-blur-sm">
            <div className="text-purple-500 font-bold text-lg mb-2 flex items-center"><Smartphone size={18} className="mr-2"/> 核心: 端侧协同</div>
            <p className="text-slate-400 text-sm leading-relaxed">
              多源感知触发<br/>
              毫秒级任务分发<br/>
              物理与数字握手
            </p>
          </div>
        </div>

        <div className="flex justify-center mt-12">
          <button 
            onClick={onStart}
            className="group flex items-center bg-red-600 hover:bg-red-700 text-white px-8 py-4 rounded-full font-bold text-lg transition-all shadow-lg hover:shadow-red-900/50"
          >
            开始全流程演练
            <ChevronRight className="ml-2 group-hover:translate-x-1 transition-transform" />
          </button>
        </div>
      </motion.div>
    </div>
  );
};

// 2. Mobile Device Simulator
const DeviceSimulator = ({ role, children }: { role: RoleType, children: React.ReactNode }) => {
  const getRoleColor = () => {
    switch(role) {
      case 'doctor': return 'border-green-500 shadow-green-900/20';
      case 'student': return 'border-blue-500 shadow-blue-900/20';
      case 'security': return 'border-yellow-500 shadow-yellow-900/20';
      case 'victim': return 'border-red-500 shadow-red-900/20';
      default: return 'border-slate-600';
    }
  };

  const getRoleName = () => {
    switch(role) {
      case 'doctor': return '张医生 (核心施救)';
      case 'student': return '大学生小李 (资源保障)';
      case 'security': return '保安老王 (环境清障)';
      case 'victim': return '患者 (监测中)';
      default: return '生命反射弧';
    }
  };

  return (
    <div className="flex flex-col items-center justify-center h-full">
      <motion.div 
        key={role}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-sm font-medium text-slate-400 mb-4"
      >
        {getRoleName()}
      </motion.div>
      <div className={cn("w-[320px] h-[640px] max-h-[80vh] bg-black rounded-[3rem] border-8 overflow-hidden relative shadow-2xl transition-all duration-500 flex flex-col", getRoleColor())}>
        {/* Notch */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-1/3 h-7 bg-black rounded-b-xl z-30 flex justify-center items-end pb-1">
           <div className="w-12 h-1 bg-slate-800 rounded-full"></div>
        </div>
        {/* Status Bar */}
        <div className="h-8 bg-transparent w-full absolute top-0 left-0 z-20 flex justify-between px-6 items-center pt-1">
           <div className="text-[10px] text-white font-mono">14:00</div>
           <div className="text-[10px] text-white font-mono flex space-x-1">
             <span>5G</span>
             <span>100%</span>
           </div>
        </div>
        
        {/* Content */}
        <div className="flex-1 w-full bg-slate-50 relative overflow-y-auto scrollbar-hide">
          {children}
        </div>

        {/* Home Bar */}
        <div className="absolute bottom-2 left-1/2 -translate-x-1/2 w-1/3 h-1 bg-white/20 rounded-full z-30"></div>
      </div>
    </div>
  );
};

// 3. Cloud Brain Map Visualization
const CloudMap = ({ phase }: { phase: ScenarioPhase }) => {
  return (
    <div className="w-full h-full bg-slate-950 relative overflow-hidden rounded-xl border border-slate-800 shadow-inner">
      {/* Grid Background */}
      <div className="absolute inset-0 opacity-20 pointer-events-none" 
           style={{ backgroundImage: 'linear-gradient(#334155 1px, transparent 1px), linear-gradient(90deg, #334155 1px, transparent 1px)', backgroundSize: '40px 40px' }}></div>
      
      {/* Central Hub - Mall */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[60%] h-[60%] border border-slate-800 rounded-lg flex items-center justify-center bg-slate-900/50">
        <span className="text-slate-700 text-xs font-mono font-bold tracking-[0.2em] absolute top-4 left-4">商场场景</span>
        
        {/* Corridors */}
        <div className="absolute inset-0 border-[20px] border-slate-900/30 rounded-lg clip-path-polygon"></div>
      </div>

      {/* Victim Node */}
      <motion.div 
        className="absolute top-1/2 left-1/2 z-10"
        animate={{ scale: phase === 'trigger' ? [1, 2, 1] : 1 }}
        transition={{ repeat: Infinity, duration: 2 }}
      >
         <div className="w-4 h-4 bg-red-500 rounded-full shadow-[0_0_20px_rgba(239,68,68,1)] flex items-center justify-center">
            <div className="w-2 h-2 bg-white rounded-full"></div>
         </div>
         {phase !== 'intro' && (
           <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-red-950/90 text-red-200 text-[10px] px-2 py-1 rounded border border-red-800 whitespace-nowrap shadow-lg">
             <span className="font-bold">心脏骤停事件</span>
             <span className="block text-[8px] opacity-70">一级危急</span>
           </div>
         )}
      </motion.div>

      {/* Doctor Node */}
      {phase !== 'intro' && (
        <motion.div 
          className="absolute z-10"
          initial={{ top: '35%', left: '35%' }}
          animate={
            phase === 'action' || phase === 'convergence' || phase === 'handover' 
            ? { top: '48%', left: '48%' } 
            : { top: '35%', left: '35%' }
          }
          transition={{ duration: 4, ease: "easeInOut" }}
        >
          <div className="w-3 h-3 bg-green-500 rounded-full ring-4 ring-green-900/50"></div>
          <div className="text-[10px] text-green-400 mt-2 font-mono bg-slate-900/80 px-1 rounded absolute whitespace-nowrap -translate-x-1/3">
            张医生（核心施救）
          </div>
        </motion.div>
      )}

      {/* Student Node */}
      {phase !== 'intro' && (
        <motion.div 
          className="absolute z-10"
          initial={{ top: '25%', left: '75%' }}
          animate={
            phase === 'action' ? { top: '30%', left: '65%' } : 
            phase === 'convergence' || phase === 'handover' ? { top: '48%', left: '52%' } : 
            { top: '25%', left: '75%' }
          }
          transition={{ duration: phase === 'action' ? 2 : 4, ease: "easeInOut" }}
        >
          <div className="w-3 h-3 bg-blue-500 rounded-full ring-4 ring-blue-900/50"></div>
          <div className="text-[10px] text-blue-400 mt-2 font-mono bg-slate-900/80 px-1 rounded absolute whitespace-nowrap -translate-x-1/2">
            小李（AED 保障）
          </div>
        </motion.div>
      )}

      {/* Security Node */}
      {phase !== 'intro' && (
        <motion.div 
          className="absolute top-[85%] left-[50%] -translate-x-1/2 z-10"
        >
          <div className="w-3 h-3 bg-yellow-500 rounded-full ring-4 ring-yellow-900/50"></div>
          <div className="text-[10px] text-yellow-400 mt-2 font-mono bg-slate-900/80 px-1 rounded absolute whitespace-nowrap -translate-x-1/2">
            保安老王（环境清障）
          </div>
        </motion.div>
      )}

       {/* Ambulance Node */}
       {(phase === 'convergence' || phase === 'handover') && (
        <motion.div 
          className="absolute z-10"
          initial={{ top: '100%', left: '50%' }}
          animate={{ top: '85%', left: '50%' }}
          transition={{ duration: 3, ease: "easeOut" }}
        >
          <div className="w-6 h-6 bg-slate-100 rounded-md flex items-center justify-center text-red-600 font-bold text-[8px] shadow-lg -translate-x-1/2 -translate-y-1/2">
            <Ambulance size={12} />
          </div>
          <div className="text-[10px] text-white mt-1 font-mono bg-slate-900/80 px-1 rounded absolute whitespace-nowrap -translate-x-1/2">
            120急救
          </div>
        </motion.div>
      )}

      {/* Radar Scan Effect */}
      {phase === 'trigger' && (
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] rounded-full border border-red-500/20 bg-red-500/5 animate-ping pointer-events-none"></div>
      )}
    </div>
  );
};

// --- Main App Component ---

export default function App() {
  const [incidentId, setIncidentId] = useState<string | null>(() => {
    if (typeof window === 'undefined') {
      return null;
    }
    return new URLSearchParams(window.location.search).get('incidentId');
  });
  const [incidentState, setIncidentState] = useState<IncidentState | null>(null);
  const [clients, setClients] = useState<ClientInfo[]>([]);
  const [aedSites, setAedSites] = useState<AedSite[]>([]);
  const [dispatchMeta, setDispatchMeta] = useState<DispatchMeta | null>(null);
  const [healthDetail, setHealthDetail] = useState<HealthDetail | null>(null);
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([]);
  const [showAuditPanel, setShowAuditPanel] = useState(false);
  const [showTechnicalDetails, setShowTechnicalDetails] = useState(false);
  const [demoAdminToken, setDemoAdminToken] = useState(getStoredDemoAdminToken);
  const [adminSession, setAdminSession] = useState<AdminSession | null>(getStoredAdminSession);
  const [adminPhone, setAdminPhone] = useState('');
  const [adminPassword, setAdminPassword] = useState('');
  const [adminLoginBusy, setAdminLoginBusy] = useState(false);
  const [themeMode, setThemeMode] = useState<ThemeMode>(getStoredThemeMode);
  const [copiedLinkKey, setCopiedLinkKey] = useState<string | null>(null);
  const [lastClientRefreshTs, setLastClientRefreshTs] = useState<number | null>(null);
  const [wsConnected, setWsConnected] = useState(false);
  const [liveNowMs, setLiveNowMs] = useState(Date.now());
  const [wsError, setWsError] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptRef = useRef(0);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const copyLinkTimeoutRef = useRef<number | null>(null);
  const manualCloseRef = useRef(false);

  const [activeRole, setActiveRole] = useState<RoleType>('doctor');
  const logContainerRef = useRef<HTMLDivElement>(null);
  const logEndRef = useRef<HTMLDivElement>(null);
  const [stickLogsToBottom, setStickLogsToBottom] = useState(true);
  const [dispatchNowMs, setDispatchNowMs] = useState(Date.now());
  const [clientId] = useState(() => `dashboard-${Math.random().toString(36).slice(2, 8)}`);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [victimView, setVictimView] = useState<'monitoring' | 'alerting'>('monitoring');
  const [victimCountdown, setVictimCountdown] = useState(10);
  const triggerRequestedRef = useRef(false);
  const sos = incidentState?.sos;

  const phase: ScenarioPhase = mapServerPhaseToScenarioPhase(incidentState);
  const getClientDisplayName = (userId?: string | null) =>
    clients.find((client) => client.userId === userId)?.displayName ?? userId ?? '未分配';
  const logs: LogEntry[] = (incidentState?.logs ?? []).map((log, index) => ({
    id: `${log.ts}-${index}`,
    time: new Date(log.ts).toLocaleTimeString('zh-CN', { hour12: false }),
    source: '服务端',
    message: translateLogMessage(log.msg, getClientDisplayName),
    type: classifyLogType(log.msg),
  }));
  const activeServerRole =
    activeRole === 'doctor' ? 'PRIME' : activeRole === 'student' ? 'RUNNER' : activeRole === 'security' ? 'GUIDE' : null;
  const isCprActive = hasPrimeStarted(incidentState);
  const isPrimeAnalyzing = isAedAnalyzing(incidentState);
  const isPrimeShockDelivered = isShockDelivered(incidentState);
  const isAedOnsite = hasRunnerDelivered(incidentState);
  const responderCount = incidentState
    ? Object.values(incidentState.roles).filter((role) => isRoleJoined(role.status)).length
    : 0;
  const serverPhase = incidentState?.phase;
  const isPrimeActive = isRoleJoined(incidentState?.roles?.PRIME?.status);
  const isRunnerActive = isRoleJoined(incidentState?.roles?.RUNNER?.status);
  const isGuideActive = isRoleJoined(incidentState?.roles?.GUIDE?.status);
  const primeJoined = isRoleJoined(incidentState?.roles?.PRIME?.status);
  const runnerJoined = isRoleJoined(incidentState?.roles?.RUNNER?.status);
  const guideJoined = isRoleJoined(incidentState?.roles?.GUIDE?.status);
  const actionsDisabled = !incidentState;
  const actionDisabledTitle = actionsDisabled ? '等待服务端状态同步' : undefined;
  const incidentStartTs = incidentState?.logs?.[0]?.ts ?? null;
  const archiveDurationLabel = formatArchiveDurationLabel(incidentState, liveNowMs);
  const archiveRoleCountLabel = formatArchiveRoleCount(incidentState);
  const archiveAedSummaryLabel = formatArchiveAedSummary(incidentState);
  const dispatchStream = buildDispatchStream(incidentState, clients, dispatchMeta, dispatchNowMs);
  const demoFlowSteps = buildDemoFlowSteps(incidentState);
  const rationale = incidentState?.dispatchRationale ?? {};
  const rationaleEntries = Object.entries(rationale);
  const assignedRoleEntries = incidentState
    ? roleNames.map((role) => [role, incidentState.roles[role]] as const).filter(([, roleState]) => Boolean(roleState.userId))
    : [];
  const hasDispatchRationale = rationaleEntries.length > 0;
  const hasRoleAssignments = assignedRoleEntries.length > 0;
  const dispatchExplanationPending = incidentState?.phase === 'DISPATCHING';
  const dispatchProgressLabel = incidentState
    ? incidentState.phase === 'DISPATCHING'
      ? '流式输出中'
      : hasDispatchRationale || hasRoleAssignments
        ? '分派已完成'
        : '等待触发'
    : '等待事件';
  const dispatchSummaryLabel = incidentState?.phase === 'DISPATCHING'
    ? '正在根据画像、距离、AED 可达性和健康风险生成任务。'
    : hasRoleAssignments
      ? assignedRoleEntries
        .map(([role, roleState]) => `${translateRoleLabel(role)}：${getClientDisplayName(roleState.userId)}`)
        .join('；')
      : '等待患者端 SOS 后自动生成三类协同任务。';
  const mapProviderDetail = dispatchMeta?.mapProvider ?? healthDetail?.mapProvider ?? {};
  const visibleAedSites = incidentState?.aedSites?.length ? incidentState.aedSites : aedSites;
  const demoReadiness = healthDetail?.demoReadiness;
  const readinessWarnings = demoReadiness?.warnings ?? [];
  const readinessItems = [
    { label: '终端', value: `${demoReadiness?.clientCount ?? clients.length}/4`, ready: (demoReadiness?.clientCount ?? clients.length) >= 4 },
    { label: 'AED', value: `${demoReadiness?.availableAedSiteCount ?? visibleAedSites.length}`, ready: (demoReadiness?.availableAedSiteCount ?? visibleAedSites.length) >= 1 },
    { label: '定位', value: readinessPercent(demoReadiness?.locationCoveragePercent), ready: (demoReadiness?.locationCoveragePercent ?? 0) >= 100 },
    { label: '健康摘要', value: readinessPercent(demoReadiness?.healthCoveragePercent), ready: (demoReadiness?.healthCoveragePercent ?? 0) >= 100 },
    { label: '证据导出', value: demoReadiness?.exportReady ? '可用' : '待事件日志', ready: Boolean(demoReadiness?.exportReady) },
  ];
  const cprLogTs = getLatestLogTs(incidentState, 'CPR started');
  const shockLogTs = getLatestLogTs(incidentState, 'AED shock delivered');
  const guidanceStartTs = isPrimeShockDelivered ? shockLogTs : cprLogTs;
  const guidanceElapsedSec = guidanceStartTs ? Math.max(0, Math.floor((liveNowMs - guidanceStartTs) / 1000)) : 0;
  const resuscitationGuidance = getResuscitationGuidance(guidanceElapsedSec);
  const adminAccountEnabled = Boolean(healthDetail?.auth?.adminAccountAuthEnabled);
  const adminSessionReady = Boolean(adminSession?.token && adminSession.user.privileges?.includes('admin'));
  const demoAdminRequired = Boolean(healthDetail?.demoAdminAuthEnabled || adminAccountEnabled);
  const demoAdminReady = !demoAdminRequired || adminSessionReady || demoAdminToken.trim().length > 0;
  const demoAdminStatusLabel = adminSessionReady
    ? '账号已登录'
    : demoAdminToken.trim()
      ? '口令已填'
      : demoAdminRequired
      ? '需要权限'
      : '本地免口令';
  const buildDemoUrl = (path: '/mobile' | '/mobile-demo', params?: Record<string, string>): string => {
    if (typeof window === 'undefined') {
      return path;
    }
    const url = new URL(path, window.location.origin);
    if (incidentId) {
      url.searchParams.set('incidentId', incidentId);
    }
    Object.entries(params ?? {}).forEach(([key, value]) => {
      if (value) {
        url.searchParams.set(key, value);
      }
    });
    return url.toString();
  };
  const demoShareLinks = [
    {
      key: 'stage',
      label: '4端导播台',
      caption: '一屏预览患者与三类任务端',
      url: buildDemoUrl('/mobile-demo'),
    },
    ...mobileDemoEntries.map((entry) => ({
      ...entry,
      url: buildDemoUrl('/mobile', { demo: entry.key, slot: entry.key }),
    })),
  ];
  const mobileTerminalLinks = demoShareLinks.filter((link) => link.key !== 'stage');
  const mobileTerminalShareText = mobileTerminalLinks.map((link) => `${link.label}：${link.url}`).join('\n');
  const demoShareText = demoShareLinks.map((link) => `${link.label}：${link.url}`).join('\n');

  const getActorId = (role: 'PRIME' | 'RUNNER' | 'GUIDE'): string => {
    const serverUserId = incidentState?.roles?.[role]?.userId;
    return serverUserId || `${clientId}-${role.toLowerCase()}`;
  };

  const getActionActorId = (action: 'CPR_STARTED' | 'AED_ANALYSIS_STARTED' | 'AED_SHOCK_DELIVERED' | 'AED_PICKED' | 'AED_DELIVERED' | 'AMBULANCE_ARRIVED' | 'HANDOVER_COMPLETED'): string => {
    if (action === 'AED_PICKED' || action === 'AED_DELIVERED') {
      return getActorId('RUNNER');
    }
    if (action === 'AMBULANCE_ARRIVED' || action === 'HANDOVER_COMPLETED') {
      return getActorId('GUIDE');
    }
    return getActorId('PRIME');
  };

  useEffect(() => {
    if (typeof document === 'undefined' || typeof window === 'undefined') {
      return;
    }
    document.documentElement.classList.toggle('dark', themeMode === 'dark');
    document.documentElement.dataset.theme = themeMode;
    window.localStorage.setItem('lra_theme_mode', themeMode);
  }, [themeMode]);

  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }
    const trimmed = demoAdminToken.trim();
    if (trimmed) {
      window.localStorage.setItem('lra_demo_admin_token', trimmed);
    } else {
      window.localStorage.removeItem('lra_demo_admin_token');
    }
  }, [demoAdminToken]);

  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }
    if (adminSession?.token) {
      window.localStorage.setItem(ADMIN_SESSION_KEY, JSON.stringify(adminSession));
    } else {
      window.localStorage.removeItem(ADMIN_SESSION_KEY);
    }
  }, [adminSession]);

  const loadHealthDetail = async () => {
    try {
      const res = await fetch(`${getApiBase()}/health/detail`);
      if (!res.ok) {
        return;
      }
      const data = await res.json();
      setHealthDetail(data as HealthDetail);
    } catch {
      setHealthDetail(null);
    }
  };

  const verifyStoredAdminSession = async () => {
    if (!adminSession?.token) {
      return;
    }
    try {
      const res = await fetch(`${getApiBase()}/auth/me`, {
        headers: { Authorization: `Bearer ${adminSession.token}` },
      });
      if (!res.ok) {
        setAdminSession(null);
        return;
      }
      const data = await res.json();
      const nextSession = {
        token: adminSession.token,
        user: data.user as AdminSessionUser,
        tokenExpiresAt: data.tokenExpiresAt ?? null,
      };
      setAdminSession(nextSession);
    } catch {
      setAdminSession(null);
    }
  };

  useEffect(() => {
    verifyStoredAdminSession();
  }, []);

  useEffect(() => {
    if (!stickLogsToBottom) {
      return;
    }
    const container = logContainerRef.current;
    if (!container) {
      return;
    }
    container.scrollTop = container.scrollHeight;
  }, [logs, stickLogsToBottom]);

  useEffect(() => {
    if (serverPhase !== 'DISPATCHING') {
      setDispatchNowMs(Date.now());
      return;
    }
    const intervalId = window.setInterval(() => setDispatchNowMs(Date.now()), 200);
    return () => window.clearInterval(intervalId);
  }, [serverPhase, incidentId]);

  useEffect(() => {
    if (!incidentStartTs) {
      setElapsedSeconds(0);
      return;
    }
    const updateElapsed = () => {
      const diffMs = Date.now() - incidentStartTs;
      setElapsedSeconds(Math.max(0, Math.floor(diffMs / 1000)));
    };
    updateElapsed();
    const intervalId = window.setInterval(updateElapsed, 1000);
    return () => window.clearInterval(intervalId);
  }, [incidentStartTs]);

  useEffect(() => {
    if (phase !== 'trigger') {
      setVictimView('monitoring');
      setVictimCountdown(10);
      return;
    }
    if (sos?.status === 'ALERTING' && sos.startTs) {
      setVictimView('alerting');
    } else {
      setVictimView('monitoring');
      setVictimCountdown(10);
    }
  }, [phase, sos?.status, sos?.startTs]);

  useEffect(() => {
    const intervalId = window.setInterval(() => setLiveNowMs(Date.now()), 500);
    return () => window.clearInterval(intervalId);
  }, []);

  useEffect(() => {
    if (phase !== 'trigger' || sos?.status !== 'ALERTING' || !sos.startTs) {
      return;
    }
    const duration = sos?.durationSec ?? 10;
    const updateCountdown = () => {
      const elapsed = Math.floor((Date.now() - sos.startTs) / 1000);
      setVictimCountdown(Math.max(0, duration - elapsed));
    };
    updateCountdown();
    const intervalId = window.setInterval(updateCountdown, 500);
    return () => window.clearInterval(intervalId);
  }, [phase, sos?.status, sos?.startTs, sos?.durationSec]);

  const connectWs = (id: string) => {
    if (!id) {
      return;
    }
    manualCloseRef.current = false;
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    if (reconnectTimeoutRef.current) {
      window.clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    setWsError(null);
    const ws = new WebSocket(`${getWsBase()}?incidentId=${id}`);
    wsRef.current = ws;

    ws.onopen = () => {
      reconnectAttemptRef.current = 0;
      setWsConnected(true);
      setWsError(null);
    };
    ws.onclose = () => {
      setWsConnected(false);
      if (!manualCloseRef.current && incidentId) {
        const attempt = reconnectAttemptRef.current;
        const delay = Math.min(10000, 1000 * Math.pow(2, attempt));
        reconnectAttemptRef.current += 1;
        reconnectTimeoutRef.current = window.setTimeout(() => connectWs(incidentId), delay);
      }
    };
    ws.onerror = () => setWsError('WebSocket 连接异常');
    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg?.type === 'STATE') {
          const nextState = msg.payload as IncidentState;
          if (nextState?.incidentId === id) {
            setIncidentState((current) =>
              mergeIncidentState(current as SharedIncidentState | null, nextState as SharedIncidentState) as IncidentState,
            );
          }
        } else if (msg?.type === 'ERROR') {
          setWsError(String(msg.payload ?? 'WebSocket error'));
        }
      } catch {
        setWsError('Invalid WebSocket message');
      }
    };
  };

  useEffect(() => {
    if (!incidentId) {
      return;
    }
    manualCloseRef.current = false;
    connectWs(incidentId);
    return () => {
      manualCloseRef.current = true;
      if (reconnectTimeoutRef.current) {
        window.clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
      wsRef.current?.close();
      wsRef.current = null;
    };
  }, [incidentId]);

  const loginAdminAccount = async () => {
    const phone = adminPhone.trim();
    const password = adminPassword;
    if (!phone || !password) {
      setErrorMessage('请输入管理员手机号和密码');
      return;
    }
    try {
      setAdminLoginBusy(true);
      setErrorMessage(null);
      const res = await fetch(`${getApiBase()}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone, password }),
      });
      if (!res.ok) {
        throw new Error(await explainResponseError(res, '管理员登录失败'));
      }
      const data = await res.json();
      const user = data.user as AdminSessionUser;
      if (!user.privileges?.includes('admin')) {
        throw new Error('管理员登录失败：该账号不在管理员白名单');
      }
      setAdminSession({ token: data.token, user, tokenExpiresAt: data.tokenExpiresAt ?? null });
      setAdminPassword('');
    } catch (error) {
      setAdminSession(null);
      setErrorMessage(error instanceof Error ? error.message : '管理员登录失败');
    } finally {
      setAdminLoginBusy(false);
    }
  };

  const logoutAdminAccount = async () => {
    const token = adminSession?.token;
    setAdminSession(null);
    if (!token) {
      return;
    }
    try {
      await fetch(`${getApiBase()}/auth/logout`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
    } catch {
      // Local logout still succeeds even if the server token was already expired.
    }
  };

  const createIncident = async () => {
    try {
      setErrorMessage(null);
      const res = await fetch(`${getApiBase()}/incidents`, {
        method: 'POST',
        headers: buildAdminHeaders(demoAdminToken, adminSession?.token),
      });
      if (!res.ok) {
        throw new Error(await explainResponseError(res, '创建事件失败'));
      }
      const data = await res.json();
    if (data?.incidentId) {
      setIncidentId(data.incidentId);
      setActiveRole('doctor');
      triggerRequestedRef.current = false;
      if (typeof window !== 'undefined') {
        const url = new URL(window.location.href);
        url.searchParams.set('incidentId', data.incidentId);
        window.history.replaceState(null, '', url.toString());
        }
      }
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Create incident failed');
    }
  };

  const loadCurrentIncident = async () => {
    try {
      setErrorMessage(null);
      const res = await fetch(`${getApiBase()}/incidents/current`);
      if (!res.ok) {
        throw new Error(await explainResponseError(res, '加载当前事件失败'));
      }
      const data = await res.json();
      if (data?.incidentId) {
        setIncidentId(data.incidentId);
        setIncidentState((current) =>
          mergeIncidentState(current as SharedIncidentState | null, data as SharedIncidentState) as IncidentState,
        );
        if (typeof window !== 'undefined') {
          const url = new URL(window.location.href);
          url.searchParams.set('incidentId', data.incidentId);
          window.history.replaceState(null, '', url.toString());
        }
      }
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : '加载当前事件失败');
    }
  };

  const loadClients = async () => {
    try {
      const res = await fetch(`${getApiBase()}/clients`);
      if (!res.ok) {
        throw new Error(await explainResponseError(res, '加载终端列表失败'));
      }
      const data = await res.json();
      setClients(Array.isArray(data?.clients) ? (data.clients as ClientInfo[]) : []);
      setLastClientRefreshTs(Date.now());
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : '加载终端列表失败');
    }
  };

  const loadDispatchMeta = async () => {
    try {
      const res = await fetch(`${getApiBase()}/dispatch/meta`);
      if (!res.ok) {
        throw new Error(await explainResponseError(res, '加载 AI 调度说明失败'));
      }
      const data = await res.json();
      setDispatchMeta(data as DispatchMeta);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : '加载 AI 调度说明失败');
    }
  };

  const loadAedSites = async () => {
    try {
      const res = await fetch(`${getApiBase()}/aed-sites`);
      if (!res.ok) {
        throw new Error(await explainResponseError(res, '加载 AED 点位失败'));
      }
      const data = await res.json();
      setAedSites(Array.isArray(data?.aedSites) ? (data.aedSites as AedSite[]) : []);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : '加载 AED 点位失败');
    }
  };

  const loadAuditEvents = async () => {
    try {
      setErrorMessage(null);
      const res = await fetch(`${getApiBase()}/audit/events?limit=30`, {
        headers: buildAdminHeaders(demoAdminToken, adminSession?.token),
      });
      if (!res.ok) {
        throw new Error(await explainResponseError(res, '加载审计日志失败'));
      }
      const data = await res.json();
      setAuditEvents(Array.isArray(data?.events) ? (data.events as AuditEvent[]) : []);
      setShowAuditPanel(true);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : '加载审计日志失败');
    }
  };

  const bootstrapDemo = async () => {
    try {
      setErrorMessage(null);
      const res = await fetch(`${getApiBase()}/demo/bootstrap`, {
        method: 'POST',
        headers: buildAdminHeaders(demoAdminToken, adminSession?.token),
      });
      if (!res.ok) {
        throw new Error(await explainResponseError(res, '初始化演示场景失败'));
      }
      const data = await res.json();
      if (data?.incidentId) {
        setIncidentId(data.incidentId);
        triggerRequestedRef.current = false;
        if (typeof window !== 'undefined') {
          const url = new URL(window.location.href);
          url.searchParams.set('incidentId', data.incidentId);
          window.history.replaceState(null, '', url.toString());
        }
      }
      setClients(Array.isArray(data?.clients) ? (data.clients as ClientInfo[]) : []);
      setAedSites(Array.isArray(data?.aedSites) ? (data.aedSites as AedSite[]) : []);
      await loadCurrentIncident();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : '初始化演示场景失败');
    }
  };

  const openMobileDemoStage = () => {
    if (typeof window === 'undefined') {
      return;
    }
    const url = new URL('/mobile-demo', window.location.origin);
    if (incidentId) {
      url.searchParams.set('incidentId', incidentId);
    }
    const opened = window.open(url.toString(), 'lifereflex-mobile-demo-stage');
    if (!opened) {
      setErrorMessage('浏览器拦截了 4端演示台，请允许本站弹出窗口后重试。');
      return;
    }
    setErrorMessage(null);
  };

  const exportExperiment = async () => {
    try {
      setErrorMessage(null);
      const res = await fetch(`${getApiBase()}/experiments/current/export`, {
        headers: buildAdminHeaders(demoAdminToken, adminSession?.token),
      });
      if (!res.ok) {
        throw new Error(await explainResponseError(res, '导出实验数据失败'));
      }
      const data = await res.json();
      downloadJson(`lifereflex-experiment-${data?.incidentId ?? 'current'}.json`, data);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : '导出实验数据失败');
    }
  };

  const exportExperimentPackage = async () => {
    try {
      setErrorMessage(null);
      const res = await fetch(`${getApiBase()}/experiments/current/package`, {
        headers: buildAdminHeaders(demoAdminToken, adminSession?.token),
      });
      if (!res.ok) {
        throw new Error(await explainResponseError(res, '导出预实验证据包失败'));
      }
      await downloadResponseBlob(res, `lifereflex-experiment-${incidentId ?? 'current'}.zip`);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : '导出预实验证据包失败');
    }
  };

  const handleLogScroll = () => {
    const container = logContainerRef.current;
    if (!container) {
      return;
    }
    const distanceToBottom = container.scrollHeight - container.scrollTop - container.clientHeight;
    setStickLogsToBottom(distanceToBottom < 48);
  };

  const resetCurrentIncident = async () => {
    try {
      setErrorMessage(null);
      const res = await fetch(`${getApiBase()}/incidents/current/reset`, {
        method: 'POST',
        headers: buildAdminHeaders(demoAdminToken, adminSession?.token),
      });
      if (!res.ok) {
        throw new Error(await explainResponseError(res, '重置事件失败'));
      }
      const data = await res.json();
      if (data?.incidentId) {
        setIncidentId(data.incidentId);
        triggerRequestedRef.current = false;
      }
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : '重置事件失败');
    }
  };

  const designatePatient = async (patientUserId: string) => {
    try {
      setErrorMessage(null);
      const res = await fetch(`${getApiBase()}/incidents/current/designate_patient`, {
        method: 'POST',
        headers: buildAdminHeaders(demoAdminToken, adminSession?.token, { 'Content-Type': 'application/json' }),
        body: JSON.stringify({ patientUserId }),
      });
      if (!res.ok) {
        throw new Error(await explainResponseError(res, '触发患者端失败'));
      }
      const data = await res.json();
      if (data?.incidentId) {
        setIncidentId(data.incidentId);
        if (typeof window !== 'undefined') {
          const url = new URL(window.location.href);
          url.searchParams.set('incidentId', data.incidentId);
          window.history.replaceState(null, '', url.toString());
        }
      }
      await loadClients();
      await loadCurrentIncident();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : '触发患者端失败');
    }
  };

  const joinIncident = async (role: 'PRIME' | 'RUNNER' | 'GUIDE') => {
    if (!incidentId) {
      return;
    }
    try {
      setErrorMessage(null);
      const res = await fetch(`${getApiBase()}/incidents/${incidentId}/join`, {
        method: 'POST',
        headers: buildAdminHeaders(demoAdminToken, adminSession?.token, { 'Content-Type': 'application/json' }),
        body: JSON.stringify({ role, userId: getActorId(role) }),
      });
      if (!res.ok) {
        throw new Error(await explainResponseError(res, `${translateRoleLabel(role)}响应失败`));
      }
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Join failed');
    }
  };

  const postAction = async (action: 'CPR_STARTED' | 'AED_ANALYSIS_STARTED' | 'AED_SHOCK_DELIVERED' | 'AED_PICKED' | 'AED_DELIVERED' | 'AMBULANCE_ARRIVED' | 'HANDOVER_COMPLETED') => {
    if (!incidentId) {
      return;
    }
    try {
      setErrorMessage(null);
      const res = await fetch(`${getApiBase()}/incidents/${incidentId}/actions`, {
        method: 'POST',
        headers: buildAdminHeaders(demoAdminToken, adminSession?.token, { 'Content-Type': 'application/json' }),
        body: JSON.stringify({ action, userId: getActionActorId(action) }),
      });
      if (!res.ok) {
        throw new Error(await explainResponseError(res, `动作 ${action} 失败`));
      }
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Action failed');
    }
  };

  const triggerIncident = async () => {
    if (!incidentId) {
      return;
    }
    try {
      setErrorMessage(null);
      const res = await fetch(`${getApiBase()}/incidents/${incidentId}/trigger`, {
        method: 'POST',
        headers: buildAdminHeaders(demoAdminToken, adminSession?.token),
      });
      if (!res.ok) {
        throw new Error(await explainResponseError(res, '触发事件失败'));
      }
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Trigger incident failed');
    }
  };

  const startSos = async () => {
    if (!incidentId) {
      return;
    }
    try {
      setErrorMessage(null);
      const res = await fetch(`${getApiBase()}/incidents/${incidentId}/sos_start`, {
        method: 'POST',
        headers: buildAdminHeaders(demoAdminToken, adminSession?.token),
      });
      if (!res.ok) {
        throw new Error(await explainResponseError(res, '启动 SOS 失败'));
      }
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'SOS start failed');
    }
  };

  const cancelSos = async () => {
    if (!incidentId) {
      return;
    }
    try {
      setErrorMessage(null);
      const res = await fetch(`${getApiBase()}/incidents/${incidentId}/sos_cancel`, {
        method: 'POST',
        headers: buildAdminHeaders(demoAdminToken, adminSession?.token),
      });
      if (!res.ok) {
        throw new Error(await explainResponseError(res, '取消 SOS 失败'));
      }
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'SOS cancel failed');
    }
  };

  useEffect(() => {
    if (incidentId) {
      return;
    }
    loadCurrentIncident();
  }, [incidentId]);

  useEffect(() => {
    loadClients();
    const intervalId = window.setInterval(loadClients, 3000);
    return () => window.clearInterval(intervalId);
  }, []);

  useEffect(() => {
    loadDispatchMeta();
    loadAedSites();
    loadHealthDetail();
  }, []);

  useEffect(() => {
    setStickLogsToBottom(true);
  }, [incidentId]);

  useEffect(() => {
    return () => {
      if (copyLinkTimeoutRef.current) {
        window.clearTimeout(copyLinkTimeoutRef.current);
        copyLinkTimeoutRef.current = null;
      }
    };
  }, []);

  const openDemoLink = (url: string, key: string) => {
    if (typeof window === 'undefined') {
      return;
    }
    const opened = window.open(url, key === 'stage' ? 'lifereflex-mobile-demo-stage' : '_blank');
    if (!opened) {
      setErrorMessage('浏览器拦截了演示入口，请允许本站弹出窗口后重试。');
      return;
    }
    setErrorMessage(null);
  };

  const openAllMobileTerminals = async () => {
    if (typeof window === 'undefined') {
      return;
    }
    const preopened = mobileTerminalLinks.map((link) => ({
      link,
      windowRef: window.open('about:blank', `lifereflex-${link.key}-${incidentId ?? 'current'}`),
    }));
    const opened = preopened.filter((entry) => Boolean(entry.windowRef));
    opened.forEach(({ link, windowRef }) => {
      if (!windowRef) {
        return;
      }
      try {
        windowRef.location.href = link.url;
        windowRef.focus();
      } catch {
        // A browser extension or popup policy may still block navigation after the window was created.
      }
    });
    if (opened.length !== mobileTerminalLinks.length) {
      const copied = await copyDemoLink('mobile-all', mobileTerminalShareText);
      setErrorMessage(
        copied
          ? `浏览器只允许打开 ${opened.length}/${mobileTerminalLinks.length} 个手机端，已复制四端链接，请手动粘贴到新标签页。`
          : `浏览器只允许打开 ${opened.length}/${mobileTerminalLinks.length} 个手机端，且剪贴板复制失败，请使用下方单个复制按钮。`,
      );
      return;
    }
    setErrorMessage(null);
    setCopiedLinkKey('mobile-all');
    if (copyLinkTimeoutRef.current) {
      window.clearTimeout(copyLinkTimeoutRef.current);
    }
    copyLinkTimeoutRef.current = window.setTimeout(() => {
      setCopiedLinkKey(null);
      copyLinkTimeoutRef.current = null;
    }, 1600);
  };

  const copyDemoLink = async (key: string, text: string): Promise<boolean> => {
    const ok = await copyTextToClipboard(text);
    if (!ok) {
      setErrorMessage('复制失败，请手动复制演示入口链接。');
      return false;
    }
    setErrorMessage(null);
    setCopiedLinkKey(key);
    if (copyLinkTimeoutRef.current) {
      window.clearTimeout(copyLinkTimeoutRef.current);
    }
    copyLinkTimeoutRef.current = window.setTimeout(() => {
      setCopiedLinkKey(null);
      copyLinkTimeoutRef.current = null;
    }, 1600);
    return true;
  };

  // --- Sub-View Renderers ---

  const renderPhoneContent = () => {
    // 1. Trigger Phase (Victim)
    if (phase === 'trigger') {
      if (victimView === 'monitoring') {
        return (
          <div className="flex flex-col h-full bg-black text-white p-6 relative">
            <div className="flex items-center justify-between mb-8">
              <span className="text-slate-400 font-bold uppercase text-xs tracking-widest">Health Guard</span>
              <Activity size={16} className="text-green-500 animate-pulse" />
            </div>

            <div className="flex-1 flex flex-col items-center justify-center">
              <div className="w-64 h-32 flex items-end justify-center space-x-1 mb-8">
                {[40, 60, 45, 70, 50, 80, 60, 90, 40, 30, 20, 10, 5, 0].map((h, i) => (
                  <motion.div 
                    key={i}
                    initial={{ height: 10 }}
                    animate={{ height: `${h}%` }}
                    transition={{ duration: 0.5, repeat: Infinity, repeatType: 'mirror', delay: i * 0.1 }}
                    className={cn("w-3 bg-red-600 rounded-t", i > 10 ? "opacity-30" : "")}
                  />
                ))}
              </div>
              <div className="text-center">
                <div className="text-6xl font-bold font-mono">86 <span className="text-xl text-slate-500">BPM</span></div>
                <div className="text-slate-400 text-sm mt-2">监测中...</div>
              </div>
            </div>

            <button 
              onClick={startSos}
              className="w-full py-4 bg-slate-800 rounded-xl text-sm font-bold border border-slate-700 hover:bg-slate-700 transition-colors"
            >
              异常确认
            </button>
          </div>
        );
      }

      const sosDuration = sos?.durationSec ?? 10;
      const circumference = 2 * Math.PI * 120;
      const strokeDashoffset = circumference - (victimCountdown / sosDuration) * circumference;

      return (
        <div className="flex flex-col h-full bg-black text-white items-center justify-center relative p-6">
          <div className="relative w-64 h-64 flex items-center justify-center mb-12">
            <svg className="absolute inset-0 w-full h-full -rotate-90">
              <circle cx="128" cy="128" r="120" stroke="#334155" strokeWidth="12" fill="none" />
              <motion.circle 
                cx="128" cy="128" r="120" 
                stroke="#dc2626" 
                strokeWidth="12" 
                fill="none" 
                strokeDasharray={circumference}
                animate={{ strokeDashoffset }}
                transition={{ duration: 1, ease: "linear" }}
                strokeLinecap="round"
              />
            </svg>
            <div className="text-center z-10">
              <div className="text-8xl font-bold font-mono">{victimCountdown}</div>
              <div className="text-red-500 font-bold uppercase mt-2 animate-pulse">SOS Alert</div>
            </div>
          </div>

          <div className="space-y-4 w-full z-10">
            <div className="text-center text-slate-300 mb-4">
              检测到异常倒地<br/>即将自动呼叫急救
            </div>
            <button 
              onClick={cancelSos}
              className="w-full bg-slate-800 hover:bg-slate-700 py-4 rounded-full font-bold text-lg"
            >
              我没事 (取消)
            </button>
          </div>
        </div>
      );
    }

    // 2. Dispatch/Action Phase (Doctor)
    if ((phase === 'dispatch' && activeRole === 'doctor') || (phase === 'action' && activeRole === 'doctor')) {
      return (
        <div className="flex flex-col h-full bg-black text-white relative">
          
          {phase === 'dispatch' ? (
             // --- Doctor: Dispatch Screen ---
             <div className="flex flex-col h-full">
                {/* Header Alert */}
                <div className="bg-red-600 p-6 pb-12 rounded-b-[3rem] shadow-xl z-10 relative overflow-hidden">
                   <div className="absolute top-0 right-0 w-32 h-32 bg-red-500/30 rounded-full blur-2xl -mr-10 -mt-10"></div>
                   <div className="flex justify-between items-start mb-4">
                      <div className="flex items-center space-x-2 bg-red-800/60 px-2 py-1 rounded text-xs font-bold border border-red-400/30">
                         <AlertTriangle size={12} className="text-white" />
                         <span>一级危急 (SCA)</span>
                      </div>
                      <div className="text-[10px] opacity-70">ID: {incidentId ?? '--'}</div>
                   </div>
                   <h2 className="text-3xl font-bold leading-tight">附近有人<br/>心脏骤停</h2>
                   <p className="text-red-100 text-sm mt-2 opacity-90">距离您 150 米 • 购物中心中庭</p>
                </div>

                {/* Golden Timer */}
                <div className="flex-1 flex flex-col items-center justify-center p-6 -mt-8 z-20">
                    <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-2xl w-full text-center mb-8">
                       <div className="text-xs text-slate-500 uppercase tracking-widest mb-2 font-bold">Golden Rescue Time</div>
                       <div className="text-6xl font-bold font-mono text-yellow-500 flex items-center justify-center">
                          3:30
                       </div>
                       <div className="text-xs text-red-400 mt-2 font-medium">刻不容缓，请立即前往！</div>
                    </div>

                   {/* Action Buttons */}
                   <div className="flex gap-4 w-full">
                      <button 
                        className="flex-1 py-4 rounded-2xl border border-slate-600 text-slate-400 font-bold hover:bg-slate-900 transition-colors"
                        onClick={() => {}}
                      >
                        无法前往
                      </button>
                      <button 
                        onClick={() => joinIncident('PRIME')}
                        className="flex-[2] py-4 bg-red-600 hover:bg-red-500 text-white rounded-2xl font-bold text-lg shadow-lg shadow-red-900/50 active:scale-95 transition-transform"
                      >
                        立即响应
                      </button>
                   </div>
                </div>
             </div>
          ) : (
            // --- Doctor: Action Mode ---
            !isCprActive ? (
              // 2a. Navigation (AirTag Style)
              <div className="flex flex-col h-full bg-slate-900 relative overflow-hidden">
                 {/* Mini Map PIP */}
                 <div className="absolute top-4 right-4 w-24 h-24 bg-slate-800 rounded-xl border border-slate-700 z-20 overflow-hidden shadow-lg opacity-90">
                    <div className="w-full h-full bg-slate-700 relative">
                       <div className="absolute top-1/2 left-1/2 w-2 h-2 bg-green-500 rounded-full shadow-[0_0_10px_rgba(34,197,94,1)]"></div>
                    </div>
                 </div>

                 <div className="flex-1 flex flex-col items-center justify-center relative">
                    {/* Direction Arrow */}
                    <motion.div 
                       animate={{ rotate: [-5, 5, -5] }}
                       transition={{ repeat: Infinity, duration: 4, ease: "easeInOut" }}
                       className="relative w-64 h-64 flex items-center justify-center"
                    >
                       <div className="absolute inset-0 bg-emerald-500/10 rounded-full blur-3xl animate-pulse"></div>
                       <div className="w-56 h-56 bg-slate-950 rounded-full border-4 border-slate-800 flex items-center justify-center shadow-2xl relative z-10">
                          <ArrowUp size={120} className="text-emerald-500 drop-shadow-[0_0_15px_rgba(16,185,129,0.8)]" strokeWidth={2.5} />
                       </div>
                    </motion.div>

                    <div className="mt-12 text-center z-10">
                       <div className="text-5xl font-bold text-white font-mono">15<span className="text-2xl text-slate-500">m</span></div>
                       <div className="text-emerald-500 font-bold uppercase tracking-widest mt-2 flex items-center justify-center">
                          <Navigation size={14} className="mr-2" />
                          即将到达
                       </div>
                    </div>
                 </div>

                 {/* Bottom Action */}
                 <div className="p-6 bg-slate-950 border-t border-slate-900 z-20">
                   <button 
                      onClick={() => postAction('CPR_STARTED')}
                      disabled={actionsDisabled}
                      title={actionDisabledTitle}
                      className="w-full bg-emerald-600 hover:bg-emerald-500 text-white py-4 rounded-xl font-bold shadow-lg shadow-emerald-900/50"
                      >
                       我已到达，开始基础复苏
                    </button>
                 </div>
              </div>
            ) : isPrimeShockDelivered ? (
              <div className="flex-1 flex flex-col bg-black text-white">
                <div className="bg-emerald-600 p-6 pt-8 rounded-b-3xl shadow-lg z-10">
                  <h2 className="font-bold text-lg flex items-center"><CheckCircle2 className="mr-2"/> 已完成一次 AED 除颤</h2>
                  <p className="text-xs text-emerald-100 mt-1">请立即恢复胸外按压，并按 30:2 节律持续复苏</p>
                </div>
                <div className="flex-1 flex flex-col items-center justify-center px-8 text-center space-y-6">
                  <motion.div
                    animate={{ scale: [1, 1.18, 1], opacity: [0.82, 1, 0.82] }}
                    transition={{ repeat: Infinity, duration: 0.6 }}
                    className="w-36 h-36 rounded-full bg-emerald-500/15 border border-emerald-500/40 flex items-center justify-center shadow-[0_0_50px_rgba(16,185,129,0.16)]"
                  >
                    <div>
                      <div className="text-5xl font-bold font-mono text-emerald-300">100</div>
                      <div className="text-[10px] tracking-[0.3em] uppercase text-emerald-500 mt-2">BPM</div>
                    </div>
                  </motion.div>
                  <div className="grid grid-cols-3 gap-3 w-full">
                    <div className="rounded-2xl border border-slate-800 bg-slate-950/80 px-4 py-3">
                      <div className="text-[10px] text-slate-500 uppercase tracking-wider">复苏循环</div>
                      <div className="mt-2 text-2xl font-mono font-bold text-white">{resuscitationGuidance.cycleRemaining}s</div>
                    </div>
                    <div className="rounded-2xl border border-slate-800 bg-slate-950/80 px-4 py-3">
                      <div className="text-[10px] text-slate-500 uppercase tracking-wider">当前阶段</div>
                      <div className="mt-2 text-sm font-bold text-emerald-300">{resuscitationGuidance.stageTitle}</div>
                    </div>
                    <div className="rounded-2xl border border-slate-800 bg-slate-950/80 px-4 py-3">
                      <div className="text-[10px] text-slate-500 uppercase tracking-wider">阶段切换</div>
                      <div className="mt-2 text-2xl font-mono font-bold text-white">{resuscitationGuidance.stageRemaining}s</div>
                    </div>
                  </div>
                  <div>
                    <div className="text-3xl font-bold">{resuscitationGuidance.stageAction}</div>
                    <div className="text-slate-400 mt-3 text-sm leading-7">
                      {resuscitationGuidance.stageBody}
                      <br />
                      持续完成 2 分钟复苏循环后，再次交由 AED 分析心律。
                    </div>
                  </div>
                </div>
              </div>
            ) : isPrimeAnalyzing ? (
              <div className="flex-1 flex flex-col bg-black text-white">
                <div className="bg-amber-500 p-6 pt-8 text-black rounded-b-3xl shadow-lg z-10">
                  <h2 className="font-bold text-lg flex items-center"><Zap className="mr-2"/> AED 正在分析心律</h2>
                  <p className="text-xs text-amber-900/80 mt-1">请停止接触患者，确认周围安全后执行除颤</p>
                </div>
                <div className="flex-1 flex flex-col items-center justify-center px-8 text-center space-y-6">
                  <div className="w-36 h-36 rounded-full border-[10px] border-amber-400/60 flex items-center justify-center animate-pulse">
                    <div className="text-center">
                      <div className="text-4xl font-bold font-mono text-amber-300">AED</div>
                      <div className="text-xs uppercase tracking-[0.3em] text-amber-500 mt-2">Analyze</div>
                    </div>
                  </div>
                  <div className="text-slate-400 text-sm leading-7">
                    设备提示“建议电击”。请清空患者周围接触者，
                    确认无人接触后执行一次电击除颤。
                  </div>
                  <button
                      onClick={() => postAction('AED_SHOCK_DELIVERED')}
                    disabled={actionsDisabled}
                    title={actionDisabledTitle}
                    className="w-full bg-amber-500 hover:bg-amber-400 text-black py-4 rounded-xl font-bold shadow-lg shadow-amber-900/40"
                  >
                    已完成一次电击除颤
                  </button>
                </div>
              </div>
            ) : isAedOnsite ? (
              <div className="flex-1 flex flex-col bg-black text-white">
                <div className="bg-blue-600 p-6 pt-8 rounded-b-3xl shadow-lg z-10">
                  <h2 className="font-bold text-lg flex items-center"><Zap className="mr-2"/> AED 已送达现场</h2>
                  <p className="text-xs text-blue-100 mt-1">请贴附电极片并按 AED 语音提示开始心律分析</p>
                </div>
                <div className="flex-1 flex flex-col items-center justify-center px-8 text-center space-y-6">
                  <div className="w-28 h-28 rounded-full bg-blue-500/15 border border-blue-500/40 flex items-center justify-center">
                    <Zap size={44} className="text-blue-400" />
                  </div>
                  <div className="text-slate-400 text-sm leading-7">
                    AED 保障者已将 AED 送达。现在由核心施救者贴附电极片，
                    停止接触患者并启动 AED 心律分析。
                  </div>
                  <button
                    onClick={() => postAction('AED_ANALYSIS_STARTED')}
                    disabled={actionsDisabled}
                    title={actionDisabledTitle}
                    className="w-full bg-blue-600 hover:bg-blue-500 text-white py-4 rounded-xl font-bold shadow-lg shadow-blue-900/40"
                  >
                    开始 AED 心律分析
                  </button>
                </div>
              </div>
            ) : (
              // 2b. CPR Tunnel Vision (Existing)
               <div className="flex-1 flex flex-col relative overflow-hidden bg-black">
                <div className="absolute top-4 left-4 text-[10px] text-green-500 font-mono border border-green-500/30 px-2 py-1 rounded bg-green-900/10">
                   HR: -- (Detecting)
                </div>
                
                <div className="flex-1 flex flex-col items-center justify-center space-y-8 z-10">
                   <div className="text-slate-500 text-xs uppercase tracking-[0.3em]">心肺复苏节拍器</div>
                   
                   <motion.div 
                    animate={{ scale: [1, 1.2, 1], opacity: [0.8, 1, 0.8] }}
                    transition={{ repeat: Infinity, duration: 0.6 }} // 100bpm
                    className="w-56 h-56 rounded-full bg-slate-900 border-8 border-slate-800 flex items-center justify-center relative shadow-[0_0_60px_rgba(34,197,94,0.1)]"
                   >
                     <div className="absolute inset-0 rounded-full border border-green-500/20 animate-ping"></div>
                     <div className="text-center">
                       <div className="text-7xl font-bold font-mono text-green-500">100</div>
                       <div className="text-xs text-green-700 font-bold uppercase mt-1">BPM</div>
                     </div>
                   </motion.div>

                   <div className="grid grid-cols-3 gap-3 w-full px-6">
                     <div className="rounded-2xl border border-slate-800 bg-slate-950/80 px-4 py-3 text-center">
                       <div className="text-[10px] text-slate-500 uppercase tracking-wider">复苏循环</div>
                       <div className="mt-2 text-2xl font-mono font-bold text-white">{resuscitationGuidance.cycleRemaining}s</div>
                     </div>
                     <div className="rounded-2xl border border-slate-800 bg-slate-950/80 px-4 py-3 text-center">
                       <div className="text-[10px] text-slate-500 uppercase tracking-wider">当前阶段</div>
                       <div className="mt-2 text-sm font-bold text-green-300">{resuscitationGuidance.stageTitle}</div>
                     </div>
                     <div className="rounded-2xl border border-slate-800 bg-slate-950/80 px-4 py-3 text-center">
                       <div className="text-[10px] text-slate-500 uppercase tracking-wider">阶段切换</div>
                       <div className="mt-2 text-2xl font-mono font-bold text-white">{resuscitationGuidance.stageRemaining}s</div>
                     </div>
                   </div>

                   <div className="text-slate-400 text-sm text-center px-8 leading-7">
                     <span className="text-green-300 font-semibold">{resuscitationGuidance.stageAction}</span>
                     <br/>
                     {resuscitationGuidance.stageBody}
                     <br/>
                     <span className="text-green-500 text-xs">深度 5-6cm，尽量减少中断</span>
                   </div>
                 </div>
                 
                 <div className="p-6 bg-slate-900 border-t border-slate-800 z-20">
                   <div className="text-[10px] text-center text-slate-600 mb-3 uppercase tracking-wider">语音指引已开启</div>
                   <div className="grid grid-cols-2 gap-3">
                      <button
                        onClick={() => postAction('CPR_STARTED')}
                       disabled={actionsDisabled}
                       title={actionDisabledTitle}
                       className="bg-slate-800 hover:bg-slate-700 py-3 rounded-lg text-xs font-medium border border-slate-700 flex flex-col items-center justify-center gap-1"
                      >
                         <span className="w-2 h-2 rounded-full bg-red-500 mb-1"></span>
                         当前复苏阶段
                      </button>
                      <button onClick={() => {}} className="bg-slate-800 hover:bg-slate-700 py-3 rounded-lg text-xs font-medium border border-slate-700 flex flex-col items-center justify-center gap-1">
                         <Users size={12} className="mb-1 text-blue-400"/>
                         提醒轮换按压
                      </button>
                   </div>
                 </div>
              </div>
            )
          )}
        </div>
      );
    }

    if ((phase === 'dispatch' || (phase === 'action' && !runnerJoined)) && activeRole === 'student') {
      return (
        <div className="flex flex-col h-full bg-slate-900 text-white">
          <div className="bg-blue-600 p-6 pt-8 text-white rounded-b-3xl shadow-lg z-10">
            <h2 className="font-bold text-lg flex items-center mb-1"><Zap className="mr-2"/> AED 保障响应</h2>
            <p className="text-xs text-blue-100 mt-1">就近取用 AED，赶赴现场</p>
          </div>
          <div className="flex-1 flex flex-col items-center justify-center p-6 space-y-6">
            <div className="text-center space-y-2">
              <div className="text-3xl font-bold text-white">资源保障任务</div>
              <div className="text-slate-400 text-sm">当前状态: {translateRoleStatus(incidentState?.roles?.RUNNER?.status)}</div>
            </div>
            <button
              onClick={() => joinIncident('RUNNER')}
              className="w-full bg-blue-600 hover:bg-blue-500 text-white py-4 rounded-xl font-bold shadow-lg shadow-blue-900/40"
            >
              立即响应（AED保障）
            </button>
          </div>
        </div>
      );
    }

    if ((phase === 'dispatch' || (phase === 'action' && !guideJoined)) && activeRole === 'security') {
      return (
        <div className="flex flex-col h-full bg-slate-900 text-white">
          <div className="bg-yellow-500 p-6 pt-8 text-black rounded-b-3xl shadow-lg z-10">
            <h2 className="font-bold text-lg flex items-center mb-1"><Shield className="mr-2"/> 环境清障响应</h2>
            <p className="text-xs text-yellow-900/70 mt-1">疏通通道，迎接急救车</p>
          </div>
          <div className="flex-1 flex flex-col items-center justify-center p-6 space-y-6">
            <div className="text-center space-y-2">
              <div className="text-3xl font-bold text-white">环境清障任务</div>
              <div className="text-slate-400 text-sm">当前状态: {translateRoleStatus(incidentState?.roles?.GUIDE?.status)}</div>
            </div>
            <button
              onClick={() => joinIncident('GUIDE')}
              className="w-full bg-yellow-500 hover:bg-yellow-400 text-black py-4 rounded-xl font-bold shadow-lg shadow-yellow-900/30"
            >
              立即响应（环境清障）
            </button>
          </div>
        </div>
      );
    }

    // 3. Action Phase (Student - Runner)
    if (phase === 'action' && activeRole === 'student' && runnerJoined) {
      return (
        <div className="flex flex-col h-full bg-slate-50 text-slate-900">
           <div className="bg-blue-600 p-6 pt-8 text-white rounded-b-3xl shadow-lg z-10">
            <h2 className="font-bold text-lg flex items-center mb-1"><Zap className="mr-2"/> AED 紧急配送</h2>
            <div className="flex items-center text-xs text-blue-100 bg-blue-700/50 self-start px-2 py-1 rounded inline-block">
               <MapPin size={10} className="mr-1"/> 目标：二楼服务台 AED箱
            </div>
           </div>
           
           <div className="flex-1 relative p-4 flex flex-col">
              <div className="w-full flex-1 bg-slate-200 rounded-2xl mb-4 relative overflow-hidden shadow-inner border border-slate-300">
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-slate-400 font-bold text-4xl opacity-20 rotate-12">现场地图</div>
                <svg className="absolute inset-0 w-full h-full pointer-events-none">
                  <path d="M 160 500 Q 100 300 250 100" stroke="#3b82f6" strokeWidth="6" fill="none" strokeDasharray="10 6" strokeLinecap="round" />
                  <circle cx="160" cy="500" r="8" fill="#2563eb" />
                </svg>
                <motion.div 
                  initial={{ y: 0 }}
                  animate={{ y: -10 }}
                  transition={{ repeat: Infinity, repeatType: "reverse", duration: 0.8 }}
                  className="absolute top-[80px] right-[50px] transform translate-x-1/2"
                >
                   <div className="bg-blue-600 text-white text-[10px] px-2 py-1 rounded-md mb-1 shadow-md whitespace-nowrap">AED (二楼)</div>
                   <MapPin size={32} className="text-blue-600 drop-shadow-lg mx-auto" fill="white" />
                </motion.div>
                <motion.div 
                  className="absolute bottom-[120px] left-[150px] w-4 h-4 bg-white border-4 border-blue-600 rounded-full shadow-lg z-10"
                  animate={{ scale: [1, 1.3, 1] }}
                  transition={{ repeat: Infinity, duration: 2 }}
                ></motion.div>
              </div>

              <div className="bg-white p-5 rounded-2xl shadow-sm border border-slate-100 space-y-4">
                <div className="flex justify-between items-center">
                  <div>
                    <div className="text-xs text-slate-500 uppercase font-bold tracking-wider">状态</div>
                    <div className="font-bold text-lg text-slate-800">
                      {hasRunnerPicked(incidentState) ? '正在赶回患者位置' : '正在前往取件'}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-mono font-bold text-blue-600">30<span className="text-sm">s</span></div>
                    <div className="text-[10px] text-slate-400">预计到达</div>
                  </div>
                </div>

                <button 
                  onClick={() => postAction(hasRunnerPicked(incidentState) ? 'AED_DELIVERED' : 'AED_PICKED')}
                  disabled={actionsDisabled}
                  title={actionDisabledTitle}
                  className="w-full bg-blue-600 text-white py-4 rounded-xl font-bold shadow-lg shadow-blue-200 active:scale-95 transition-transform flex items-center justify-center"
                >
                  {hasRunnerPicked(incidentState) ? '到达患者位置' : '到达 AED 位置'}
                </button>
              </div>
           </div>
        </div>
      );
    }

    // 4. Action Phase (Security - Guide)
    if ((phase === 'action' || phase === 'convergence' || phase === 'handover') && activeRole === 'security' && guideJoined) {
       return (
         <div className="flex flex-col h-full bg-slate-900 text-white">
            <div className="bg-yellow-500 p-6 pt-8 text-black rounded-b-3xl shadow-lg z-10">
              <h2 className="font-bold text-lg flex items-center"><Shield className="mr-2"/> 环境清障任务</h2>
              <p className="text-xs text-yellow-900/70 mt-1">任务 ID: #CLR-8823</p>
            </div>
            
            <div className="flex-1 flex flex-col p-6 space-y-8">
               <div className="flex-1 flex flex-col items-center justify-center text-center">
                 <div className="relative mb-6">
                   <div className="absolute inset-0 bg-yellow-500/20 blur-xl rounded-full animate-pulse"></div>
                   <div className="relative w-24 h-24 bg-slate-800 border-2 border-yellow-500 rounded-full flex items-center justify-center z-10">
                      <AlertTriangle size={48} className="text-yellow-500" />
                   </div>
                 </div>
                 <h3 className="text-2xl font-bold text-white">疏散入口车辆</h3>
                 <p className="text-slate-400 mt-2 text-sm">请保持消防通道畅通</p>
               </div>
               
               {/* Ambulance Status */}
               <div className="w-full bg-slate-800 border border-slate-700 p-5 rounded-2xl">
                 <div className="flex justify-between items-center mb-4">
                    <div className="flex items-center space-x-2">
                       <Siren size={16} className="text-red-500 animate-pulse" />
                       <span className="text-sm font-bold text-white">120 急救车接近中</span>
                    </div>
                    <span className="text-xs font-mono text-yellow-500 bg-yellow-900/30 px-2 py-1 rounded border border-yellow-700/50">
                       粤B·120QA
                    </span>
                 </div>
                 
                 {/* Progress Bar */}
                 <div className="relative h-2 bg-slate-700 rounded-full mb-2 overflow-hidden">
                    <motion.div 
                      className="absolute top-0 left-0 h-full bg-gradient-to-r from-red-600 to-red-400 rounded-full"
                      initial={{ width: "0%" }}
                      animate={{ width: "80%" }}
                      transition={{ duration: 10, ease: "linear" }}
                    ></motion.div>
                 </div>
                 <div className="flex justify-between text-[10px] text-slate-400 uppercase tracking-wider">
                    <span>3km</span>
                    <span>即将到达</span>
                 </div>
               </div>

               <button
                 onClick={() => postAction('AMBULANCE_ARRIVED')}
                 disabled={actionsDisabled}
                 title={actionDisabledTitle}
                 className="w-full bg-yellow-500 text-black py-4 rounded-xl font-bold shadow-lg shadow-yellow-900/30 hover:bg-yellow-400 transition-colors"
               >
                 救护车已到达
               </button>
               {incidentState?.phase === 'HANDOVER' && (
                 <button
                   onClick={() => postAction('HANDOVER_COMPLETED')}
                   disabled={actionsDisabled}
                   title={actionDisabledTitle}
                   className="mt-3 w-full bg-emerald-500 text-white py-4 rounded-xl font-bold shadow-lg shadow-emerald-900/30 hover:bg-emerald-400 transition-colors"
                 >
                   完成救护车交接并归档
                 </button>
               )}
            </div>
         </div>
       )
    }

    // 5. Convergence
    if (phase === 'convergence') {
      return (
        <div className="flex flex-col h-full bg-slate-900 text-white relative overflow-hidden">
           {/* Background Map Effect */}
           <div className="absolute inset-0 opacity-10" style={{ backgroundImage: 'radial-gradient(circle at 50% 50%, #22c55e 0%, transparent 60%)' }}></div>
           
           <div className="relative z-10 flex flex-col h-full p-6">
              <div className="flex-1 flex flex-col items-center justify-center">
                 <div className="w-48 h-48 border-[12px] border-green-600 rounded-full flex items-center justify-center mb-8 relative">
                    <div className="text-center">
                       <div className="text-6xl font-bold font-mono text-white">50<span className="text-2xl text-slate-400">m</span></div>
                       <div className="text-xs text-green-500 uppercase tracking-widest mt-2">接近现场</div>
                    </div>
                    {/* Tick marks */}
                    <div className="absolute inset-0 border-4 border-slate-800 rounded-full scale-110 border-dashed"></div>
                 </div>

                 <div className="text-center">
                   <h3 className="text-2xl font-bold text-white mb-2">AED 即将到达</h3>
                   <p className="text-slate-400 text-sm">持有人: 小李 (学生)</p>
                 </div>
              </div>
              
              <button 
                onClick={() => postAction('AED_DELIVERED')}
                disabled={actionsDisabled}
                title={actionDisabledTitle}
                className="w-full bg-green-600 hover:bg-green-500 py-4 rounded-xl font-bold mb-4 shadow-lg shadow-green-900/50 transition-colors"
              >
                AED 已送达
              </button>
           </div>
        </div>
      )
    }

    // 6. Handover
    if (phase === 'handover' || phase === 'summary') {
       return (
         <div className="flex flex-col h-full bg-white text-slate-900">
            <div className="bg-slate-50 p-8 pt-12 text-center border-b border-slate-100">
               <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                 <CheckCircle2 size={40} className="text-green-600" />
               </div>
               <h2 className="text-2xl font-bold text-slate-800">{phase === 'summary' ? '本轮记录已归档' : '任务归档'}</h2>
               <p className="text-slate-500 mt-2">{phase === 'summary' ? '手机端现在可以退出应急模式' : '救护车已接管患者'}</p>
            </div>
            
            <div className="flex-1 p-6 flex flex-col items-center justify-center">
                <div className="w-full bg-white border-2 border-dashed border-indigo-300 rounded-2xl p-8 flex flex-col items-center justify-center mb-8">
                   <div className="w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                      <FileText size={32} className="text-indigo-600" />
                   </div>
                   <div className="text-slate-900 font-bold text-lg">现场交接摘要已生成</div>
                   <div className="text-xs text-slate-500 mt-1">关键处置日志已进入事件记录，可在证据包中复核</div>
                </div>

                <div className="w-full space-y-3 px-2">
                  <div className="flex justify-between text-sm py-2 border-b border-slate-100">
                    <span className="text-slate-500">总耗时</span>
                    <span className="font-mono font-bold text-slate-900">{archiveDurationLabel}</span>
                  </div>
                  <div className="flex justify-between text-sm py-2 border-b border-slate-100">
                    <span className="text-slate-500">协同任务</span>
                    <span className="font-mono font-bold text-slate-900">{archiveRoleCountLabel}</span>
                  </div>
                  <div className="flex justify-between text-sm py-2 border-b border-slate-100">
                    <span className="text-slate-500">AED记录</span>
                    <span className="font-mono font-bold text-green-600 bg-green-50 px-2 rounded">{archiveAedSummaryLabel}</span>
                  </div>
                 {phase === 'summary' && (
                   <div className="flex justify-between text-sm py-2 border-b border-slate-100">
                     <span className="text-slate-500">手机端状态</span>
                     <span className="font-mono font-bold text-emerald-600 bg-emerald-50 px-2 rounded">可退出应急模式</span>
                   </div>
                 )}
               </div>
            </div>
         </div>
       )
    }

    // Default Fallback
    return (
      <div className="flex flex-col items-center justify-center h-full text-slate-400 p-8 text-center bg-slate-900">
         <Smartphone size={48} className="mb-4 opacity-50"/>
         <p>请先创建或连接事件</p>
      </div>
    );
  };

  // --- Main Render ---

  if (phase === 'intro' && !incidentId) {
    return (
      <div className="flex items-center justify-center h-screen bg-slate-950 text-slate-200">
        <div className="text-sm text-slate-400">正在连接服务端...</div>
      </div>
    );
  }

  if (phase === 'intro') {
    return <IntroScreen onStart={createIncident} />;
  }

  return (
    <div className="lra-dashboard flex flex-col h-screen bg-slate-950 text-slate-200 overflow-hidden font-sans">
      
      {/*Top Bar*/}
      <header className="min-h-16 border-b border-slate-800 bg-slate-900 flex flex-wrap items-center justify-between gap-3 px-6 py-3 z-50 shadow-md flex-shrink-0">
        <div className="flex items-center space-x-4">
            <div className="font-bold text-xl tracking-tight text-white flex items-center">
            <Activity className="mr-2 text-red-500"/> 生命反射弧
          </div>
          <div className="hidden md:flex items-center space-x-2 text-[10px] bg-slate-800 px-3 py-1 rounded-full text-slate-400 uppercase tracking-wider font-bold">
             <div className={cn("w-2 h-2 rounded-full", wsConnected ? "bg-green-500 animate-pulse" : "bg-yellow-500")}></div>
             <span>{wsConnected ? "实时同步" : "离线"}</span>
          </div>
        </div>

          <div className="flex flex-wrap items-center justify-end gap-3">
            {adminAccountEnabled && (
              <div className="h-9 flex items-center gap-2 rounded-lg border border-slate-700 bg-black/30 px-3">
                <ShieldCheck size={14} className={adminSessionReady ? "text-emerald-300" : "text-slate-400"} />
                {adminSessionReady ? (
                  <>
                    <span className="max-w-28 truncate text-xs font-semibold text-emerald-200" title={adminSession?.user.displayName}>
                      {adminSession?.user.displayName}
                    </span>
                    <button
                      onClick={logoutAdminAccount}
                      className="text-slate-400 hover:text-slate-100"
                      title="退出管理员账号"
                    >
                      <LogOut size={14} />
                    </button>
                  </>
                ) : (
                  <>
                    <input
                      value={adminPhone}
                      onChange={(event) => setAdminPhone(event.target.value)}
                      inputMode="tel"
                      autoComplete="username"
                      placeholder="管理员手机号"
                      className="w-28 bg-transparent text-xs text-slate-200 outline-none placeholder:text-slate-500"
                      title="服务器配置 LRA_ADMIN_PHONES 后，可用白名单手机号登录管理"
                    />
                    <input
                      value={adminPassword}
                      onChange={(event) => setAdminPassword(event.target.value)}
                      onKeyDown={(event) => {
                        if (event.key === 'Enter') {
                          loginAdminAccount();
                        }
                      }}
                      type="password"
                      autoComplete="current-password"
                      placeholder="密码"
                      className="w-20 bg-transparent text-xs text-slate-200 outline-none placeholder:text-slate-500"
                    />
                    <button
                      onClick={loginAdminAccount}
                      disabled={adminLoginBusy}
                      className="text-slate-300 hover:text-white disabled:opacity-50"
                      title="登录正式管理员账号"
                    >
                      <LogIn size={14} />
                    </button>
                  </>
                )}
              </div>
            )}
            <button
              onClick={() => setThemeMode((current) => current === 'dark' ? 'light' : 'dark')}
              className="h-9 w-9 flex items-center justify-center rounded-lg border border-slate-700 bg-black/30 text-slate-200 hover:bg-slate-800 transition-colors"
              title={themeMode === 'dark' ? '切换到浅色模式' : '切换到深色模式'}
            >
              {themeMode === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
            </button>
            <div className="h-9 flex items-center gap-2 rounded-lg border border-slate-700 bg-black/30 px-3">
              <KeyRound size={14} className="text-slate-400" />
              <input
                value={demoAdminToken}
                onChange={(event) => setDemoAdminToken(event.target.value)}
                type="password"
                autoComplete="off"
                placeholder="演示口令"
                className="w-28 bg-transparent text-xs text-slate-200 outline-none placeholder:text-slate-500"
                title="服务器启用演示管理员口令后，用于初始化、触发、重置和导出；正式管理员账号也可替代口令"
              />
            </div>
            <div
              className={cn(
                "h-9 flex items-center gap-2 rounded-lg border px-3 text-[10px] font-bold uppercase tracking-wider",
                demoAdminReady
                  ? "border-emerald-700/60 bg-emerald-950/40 text-emerald-300"
                  : "border-amber-700/60 bg-amber-950/40 text-amber-300"
              )}
              title="读取 /api/health/detail 后判断是否需要正式管理员账号或演示口令"
            >
              {demoAdminReady ? <Unlock size={14} /> : <Lock size={14} />}
              {demoAdminStatusLabel}
            </div>
            <div className="font-mono text-xs font-bold text-slate-200 px-3 py-2 text-center bg-black/30 rounded border border-white/10">
              {incidentId ? `事件: ${incidentId.slice(0, 8)}` : '事件: --'}
            </div>
            <div className="font-mono text-xs font-bold text-slate-200 px-3 py-2 text-center bg-black/30 rounded border border-white/10">
              {incidentStartTs ? `耗时: ${formatElapsed(elapsedSeconds)}` : '耗时: --:--'}
            </div>
            
          <div className="flex items-center gap-2">
             <button
               onClick={bootstrapDemo}
               className="h-9 px-3 rounded-lg bg-red-600 text-white hover:bg-red-500 transition-colors text-[10px] font-bold uppercase tracking-wider flex items-center gap-2"
               title="初始化可演示的患者、救援者和 AED 场景"
             >
               <Siren size={16} /> 演示场景
             </button>
             <button
               onClick={openMobileDemoStage}
               className="h-9 px-3 rounded-lg bg-blue-600 text-white hover:bg-blue-500 transition-colors text-[10px] font-bold uppercase tracking-wider flex items-center gap-2"
               title="新开单个 4 端分屏演示台，兼容 Edge 弹窗限制"
             >
               <Smartphone size={16} /> 4端演示
             </button>
             <button
               onClick={exportExperiment}
               className="h-9 px-3 rounded-lg bg-slate-800 text-slate-200 hover:bg-slate-700 transition-colors text-[10px] font-bold uppercase tracking-wider flex items-center gap-2"
               title="导出当前事件的实验数据 JSON"
             >
               <Download size={16} /> 导出数据
             </button>
             <button
               onClick={exportExperimentPackage}
               className="h-9 px-3 rounded-lg bg-indigo-700 text-white hover:bg-indigo-600 transition-colors text-[10px] font-bold uppercase tracking-wider flex items-center gap-2"
               title="下载包含 JSON、CSV 和说明文档的预实验证据包"
             >
               <FileText size={16} /> 证据包
             </button>
             <button
               onClick={loadAuditEvents}
               className="h-9 px-3 rounded-lg bg-emerald-800 text-emerald-50 hover:bg-emerald-700 transition-colors text-[10px] font-bold uppercase tracking-wider flex items-center gap-2"
               title="查看最近的登录、演示、导出和角色动作审计记录"
             >
               <ShieldCheck size={16} /> 审计
             </button>
             <button
               onClick={resetCurrentIncident}
               className="h-9 w-9 flex items-center justify-center hover:bg-slate-800 rounded-full transition-colors text-yellow-300 hover:text-yellow-200"
               title="重置当前事件"
             >
               <RotateCcw size={20} />
             </button>
          </div>
        </div>
      </header>

      {showAuditPanel && (
        <div className="border-b border-emerald-900/60 bg-emerald-950/40 px-6 py-4">
          <div className="mx-auto flex max-w-[1800px] flex-col gap-3">
            <div className="flex items-center justify-between gap-3">
              <div>
                <div className="text-[10px] font-bold tracking-wider text-emerald-300">安全审计留痕</div>
                <div className="text-sm text-slate-100">最近管理、登录、导出和现场动作留痕</div>
              </div>
              <button
                onClick={() => setShowAuditPanel(false)}
                className="h-8 px-3 rounded-lg border border-emerald-800 text-[10px] font-bold uppercase tracking-wider text-emerald-100 hover:bg-emerald-900/70"
              >
                收起
              </button>
            </div>
            <div className="grid gap-2 md:grid-cols-2 xl:grid-cols-3">
              {auditEvents.length === 0 ? (
                <div className="rounded-lg border border-emerald-900/70 bg-slate-950/40 p-3 text-xs text-slate-300">
                  暂无审计事件，或当前口令无权读取。
                </div>
              ) : (
                auditEvents.slice(0, 9).map((event) => (
                  <div key={event.eventId} className="rounded-lg border border-emerald-900/70 bg-slate-950/40 p-3">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-xs font-bold text-emerald-200">{translateAuditEventType(event.eventType)}</span>
                      <span className="text-[10px] text-slate-500">{formatTimeLabel(event.ts)}</span>
                    </div>
                    <div className="mt-2 grid grid-cols-2 gap-2 text-[11px] text-slate-300">
                      <span>操作者：{summarizeActor(event.actorId || event.actorType)}</span>
                      <span>结果：{translateAuditOutcome(event.outcome)}</span>
                      <span>对象：{event.targetId || event.targetType || '--'}</span>
                      <span>请求指纹：{event.requestHash || '--'}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {/* Main Content Grid */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 overflow-hidden">
        
        {/* Left: Cloud Brain / Control Center */}
        <div className="lg:col-span-7 flex flex-col border-r border-slate-800 bg-slate-900/50 p-6 space-y-6 overflow-y-auto">
          
          {/* Status Cards */}
          <div className="grid grid-cols-3 gap-4">
             <div className="bg-slate-800/80 p-4 rounded-lg border border-slate-700/50">
                <div className="text-[10px] text-slate-500 uppercase mb-2 font-bold tracking-wider">当前事件</div>
                <div className="text-red-400 font-bold flex items-center">
                  <AlertTriangle size={16} className="mr-2" /> {translatePhaseLabel(incidentState?.phase)}
                </div>
             </div>
             <div className="bg-slate-800/80 p-4 rounded-lg border border-slate-700/50">
                <div className="text-[10px] text-slate-500 uppercase mb-2 font-bold tracking-wider">已响应终端</div>
                <div className="text-blue-400 font-bold flex items-center">
                  <Users size={16} className="mr-2" /> {responderCount} 台
                </div>
             </div>
             <div className="bg-slate-800/80 p-4 rounded-lg border border-slate-700/50">
                <div className="text-[10px] text-slate-500 uppercase mb-2 font-bold tracking-wider">救护接管</div>
                <div className="text-white font-bold flex items-center font-mono">
                  <Ambulance size={16} className="mr-2" /> {hasGuideCompleted(incidentState) ? '已到场' : incidentState ? '进行中' : '--'}
                </div>
             </div>
          </div>
          <div className="rounded-lg border border-amber-700/40 bg-amber-950/30 px-3 py-2 text-xs text-amber-100">
            安全边界：当前系统用于急救协同演示、训练复盘与研究验证，不替代 120、AED 语音提示、现场专业医护判断或真实医疗诊断。
          </div>
          <div className={cn(
            "rounded-xl border p-4",
            demoReadiness?.ready
              ? "border-emerald-700/60 bg-emerald-950/20"
              : "border-amber-700/60 bg-amber-950/20",
          )}>
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <div className="text-[10px] text-slate-500 uppercase tracking-wider font-bold">运行准备度</div>
                <div className="text-sm text-white font-semibold mt-1">
                  {demoReadiness?.ready ? '已满足本轮协同演示前置条件' : '仍有演示前检查项需要确认'}
                </div>
              </div>
              <div className={cn(
                "rounded-lg border px-3 py-2 text-[10px] font-bold uppercase tracking-wider",
                demoReadiness?.ready
                  ? "border-emerald-700/60 bg-emerald-900/50 text-emerald-100"
                  : "border-amber-700/60 bg-amber-900/40 text-amber-100",
              )}>
                {demoReadiness?.ready ? '准备就绪' : `${readinessWarnings.length || 1} 项待确认`}
              </div>
            </div>
            <div className="mt-3 grid grid-cols-2 md:grid-cols-5 gap-2">
              {readinessItems.map((item) => (
                <div key={item.label} className={cn(
                  "rounded-lg border px-3 py-3",
                  item.ready ? "border-emerald-800/50 bg-slate-950/30" : "border-amber-800/50 bg-slate-950/30",
                )}>
                  <div className="text-[10px] text-slate-500 uppercase tracking-wider">{item.label}</div>
                  <div className={cn("mt-1 text-sm font-semibold", item.ready ? "text-emerald-200" : "text-amber-200")}>{item.value}</div>
                </div>
              ))}
            </div>
            {readinessWarnings.length > 0 && (
              <div className="mt-3 text-xs leading-5 text-amber-100">
                {readinessWarnings.slice(0, 3).join('；')}
              </div>
            )}
          </div>
          <div className="rounded-xl border border-blue-800/50 bg-blue-950/20 p-4">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <div className="text-[10px] text-blue-300 uppercase tracking-wider font-bold">演示入口</div>
                <div className="text-sm text-white font-semibold mt-1">把这些链接发给手机或观察端即可进入指定终端</div>
                <div className="mt-1 text-xs text-slate-400">
                  {incidentId ? `已绑定当前事件 ${incidentId.slice(0, 8)}，刷新或新开标签页不会丢失事件。` : '等待事件编号，同步后会自动带上 incidentId。'}
                </div>
              </div>
              <div className="flex flex-wrap items-center gap-2">
                <button
                  onClick={openAllMobileTerminals}
                  className="h-9 rounded-lg border border-blue-600/80 bg-blue-600/20 px-3 text-[10px] font-bold uppercase tracking-wider text-blue-50 hover:bg-blue-600/35 transition-colors flex items-center gap-2"
                  title="同步打开患者端、核心施救端、AED 保障端和清障接驳端"
                >
                  <Smartphone size={14} /> {copiedLinkKey === 'mobile-all' ? '已打开' : '打开4个手机端'}
                </button>
                <button
                  onClick={() => copyDemoLink('all', demoShareText)}
                  className="h-9 rounded-lg border border-blue-700/70 bg-blue-900/40 px-3 text-[10px] font-bold uppercase tracking-wider text-blue-100 hover:bg-blue-900/70 transition-colors flex items-center gap-2"
                  title="复制四端导播台和各移动端入口"
                >
                  <Copy size={14} /> {copiedLinkKey === 'all' ? '已复制' : '复制全部'}
                </button>
              </div>
            </div>
            <div className="mt-3 grid grid-cols-1 md:grid-cols-5 gap-2">
              {demoShareLinks.map((link) => (
                <div key={link.key} className="rounded-lg border border-blue-900/60 bg-slate-950/35 px-3 py-3">
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0">
                      <div className="text-xs font-semibold text-white truncate">{link.label}</div>
                      <div className="mt-1 text-[10px] leading-4 text-slate-400">{link.caption}</div>
                    </div>
                    <div className="flex shrink-0 items-center gap-1">
                      <button
                        onClick={() => copyDemoLink(link.key, link.url)}
                        className="flex h-7 w-7 items-center justify-center rounded-md border border-slate-700 bg-slate-900/70 text-slate-300 hover:text-white"
                        title={`复制${link.label}链接`}
                      >
                        {copiedLinkKey === link.key ? <CheckCircle2 size={14} /> : <Copy size={14} />}
                      </button>
                      <button
                        onClick={() => openDemoLink(link.url, link.key)}
                        className="flex h-7 w-7 items-center justify-center rounded-md border border-slate-700 bg-slate-900/70 text-slate-300 hover:text-white"
                        title={`打开${link.label}`}
                      >
                        <ExternalLink size={14} />
                      </button>
                    </div>
                  </div>
                  <div className="mt-2 truncate rounded bg-black/20 px-2 py-1.5 font-mono text-[10px] text-slate-500" title={link.url}>
                    {link.url}
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-2">
            {demoFlowSteps.map((step, index) => (
              <div
                key={step.title}
                className={cn(
                  "min-h-24 rounded-lg border px-3 py-3 transition-colors",
                  step.complete
                    ? "border-emerald-700/60 bg-emerald-950/30"
                    : step.active
                      ? "border-red-500/70 bg-red-950/40"
                      : "border-slate-700 bg-slate-900/60",
                )}
              >
                <div className="flex items-center gap-2">
                  <span
                    className={cn(
                      "flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-[10px] font-bold",
                      step.complete
                        ? "bg-emerald-500 text-slate-950"
                        : step.active
                          ? "bg-red-500 text-white"
                          : "bg-slate-700 text-slate-300",
                    )}
                  >
                    {step.complete ? <CheckCircle2 size={14} /> : index + 1}
                  </span>
                  <div className="min-w-0 text-xs font-semibold text-white">{step.title}</div>
                </div>
                <div className="mt-2 text-[11px] leading-4 text-slate-400">{step.detail}</div>
              </div>
            ))}
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <button
              onClick={bootstrapDemo}
              className="min-h-12 rounded-lg border border-red-500/60 bg-red-950/40 px-4 py-3 text-left hover:bg-red-950/70 transition-colors"
            >
              <div className="flex items-center gap-2 text-sm font-semibold text-white">
                <Siren size={16} className="text-red-300" /> 初始化协同演示场景
              </div>
              <div className="text-xs text-slate-400 mt-1">自动生成患者、医生、AED 保障、环境清障和 AED 点位。</div>
            </button>
            <button
              onClick={exportExperimentPackage}
              className="min-h-12 rounded-lg border border-slate-700 bg-slate-800/70 px-4 py-3 text-left hover:bg-slate-800 transition-colors"
            >
              <div className="flex items-center gap-2 text-sm font-semibold text-white">
                <Download size={16} className="text-blue-300" /> 导出事件证据包
              </div>
              <div className="text-xs text-slate-400 mt-1">下载 JSON、CSV 表格和说明文件，便于复盘统计与交接留存。</div>
            </button>
          </div>
          {wsError && (
            <div className="text-xs text-red-400 border border-red-900/60 bg-red-950/40 rounded-lg px-3 py-2">
              实时连接：{wsError}
            </div>
          )}
          {errorMessage && (
            <div className="text-xs text-red-400 border border-red-900/60 bg-red-950/40 rounded-lg px-3 py-2">
              请求异常：{errorMessage}
            </div>
          )}

          <div className="rounded-xl border border-emerald-800/50 bg-emerald-950/20 p-4">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <div className="text-[10px] text-emerald-300 uppercase tracking-wider font-bold">智能分派摘要</div>
                <div className="text-sm text-white font-semibold mt-1">{dispatchSummaryLabel}</div>
              </div>
              <div className={cn(
                "px-3 py-2 rounded-lg text-[10px] font-bold uppercase tracking-wider",
                incidentState?.phase === 'DISPATCHING'
                  ? "bg-red-950/60 text-red-200 border border-red-700/60"
                  : hasRoleAssignments
                    ? "bg-emerald-900/60 text-emerald-100 border border-emerald-600/60"
                    : "bg-slate-900/60 text-slate-300 border border-slate-700/60",
              )}>
                {dispatchProgressLabel}
              </div>
            </div>
            {hasRoleAssignments && (
              <div className="mt-3 grid grid-cols-1 md:grid-cols-3 gap-2">
                {assignedRoleEntries.map(([role, roleState]) => (
                  <div key={role} className="rounded-lg border border-emerald-800/50 bg-slate-950/40 px-3 py-3">
                    <div className="text-[10px] text-slate-500 uppercase tracking-wider">{translateRoleLabel(role)}</div>
                    <div className="mt-1 text-sm font-semibold text-white truncate">{getClientDisplayName(roleState.userId)}</div>
                    <div className="mt-1 text-xs text-emerald-300">{translateRoleStatus(roleState.status)}</div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <button
            type="button"
            onClick={() => setShowTechnicalDetails((visible) => !visible)}
            className="flex min-h-11 items-center justify-between gap-3 rounded-lg border border-slate-700/60 bg-slate-800/60 px-4 py-3 text-left text-sm text-slate-100 hover:bg-slate-800 transition-colors"
          >
            <span>
              <span className="font-semibold">{showTechnicalDetails ? '收起技术详情' : '展开技术详情'}</span>
              <span className="ml-2 text-xs text-slate-400">算法配置、调度评分与审计留痕</span>
            </span>
            <ChevronDown className={cn("h-4 w-4 shrink-0 transition-transform", showTechnicalDetails && "rotate-180")} />
          </button>

          {showTechnicalDetails && (
            <>
          <div className="bg-slate-800/70 border border-slate-700/60 rounded-xl p-4">
            <div className="flex items-center justify-between gap-3 mb-3">
              <div>
                <div className="text-[10px] text-slate-500 uppercase tracking-wider font-bold">AI 调度引擎</div>
                <div className="text-sm text-white font-semibold mt-1">
                  {dispatchMeta?.configured ? '云端智能分派已启用，按画像和距离生成任务单' : '当前以本地规则调度生成任务单'}
                </div>
              </div>
              <div className={cn(
                "px-3 py-2 rounded-lg text-[10px] font-bold uppercase tracking-wider",
                dispatchMeta?.configured ? "bg-emerald-950/60 text-emerald-300 border border-emerald-700/60" : "bg-amber-950/60 text-amber-300 border border-amber-700/60"
              )}>
                {dispatchMeta?.configured ? '智能分派' : '规则兜底'}
              </div>
            </div>
            <div className="grid grid-cols-2 xl:grid-cols-4 gap-3 mb-4">
              <div className="rounded-lg border border-slate-700 bg-slate-900/60 px-3 py-3">
                <div className="text-[10px] text-slate-500 uppercase tracking-wider">运行配置</div>
                <div className="text-xs text-slate-200 mt-1 break-all">{dispatchMeta?.configFile ? '服务端运行配置' : '未返回配置状态'}</div>
              </div>
              <div className="rounded-lg border border-slate-700 bg-slate-900/60 px-3 py-3">
                <div className="text-[10px] text-slate-500 uppercase tracking-wider">分派耗时</div>
                <div className="text-xs text-slate-200 mt-1">{dispatchMeta?.dispatchDelaySec !== undefined ? `${dispatchMeta.dispatchDelaySec} 秒` : '--'}</div>
              </div>
              <div className="rounded-lg border border-slate-700 bg-slate-900/60 px-3 py-3">
                <div className="text-[10px] text-slate-500 uppercase tracking-wider">模型</div>
                <div className="text-xs text-slate-200 mt-1 break-all">{dispatchMeta?.model ?? '--'}</div>
              </div>
              <div className="rounded-lg border border-slate-700 bg-slate-900/60 px-3 py-3">
                <div className="text-[10px] text-slate-500 uppercase tracking-wider">超时</div>
                <div className="text-xs text-slate-200 mt-1">{dispatchMeta?.timeoutSec ?? '--'} 秒</div>
              </div>
            </div>
            <div className="text-xs text-slate-400 leading-6">
              <span className="text-slate-200 font-semibold">传入画像字段：</span>
              {dispatchMeta?.candidateFields?.join('、') ?? '加载中...'}
            </div>
            <div className="text-xs text-slate-400 leading-6 mt-2">
              <span className="text-slate-200 font-semibold">角色选择依据：</span>
              {dispatchMeta ? Object.entries(dispatchMeta.selectionRules).map(([role, rule]) => `${translateRoleLabel(role)}: ${rule}`).join('；') : '加载中...'}
            </div>
            <div className="mt-3 grid grid-cols-1 md:grid-cols-3 gap-3 text-xs text-slate-400">
              <div className="rounded-lg border border-slate-700 bg-slate-900/60 px-3 py-3">
                <div className="text-[10px] text-slate-500 uppercase tracking-wider">地图距离</div>
                <div className="mt-1 break-all text-slate-200">
                  {formatTechnicalValue(mapProviderDetail.activeProvider ?? mapProviderDetail.mode ?? mapProviderDetail.requestedProvider)}
                </div>
              </div>
              <div className="rounded-lg border border-slate-700 bg-slate-900/60 px-3 py-3">
                <div className="text-[10px] text-slate-500 uppercase tracking-wider">距离来源</div>
                <div className="mt-1 break-all text-slate-200">{formatTechnicalValue(mapProviderDetail.distanceSource)}</div>
              </div>
              <div className="rounded-lg border border-slate-700 bg-slate-900/60 px-3 py-3">
                <div className="text-[10px] text-slate-500 uppercase tracking-wider">距离计算状态</div>
                <div className="mt-1 break-all text-slate-200">{formatTechnicalValue(mapProviderDetail.fallbackReason)}</div>
              </div>
            </div>
          </div>

          <div className="bg-slate-800/70 border border-slate-700/60 rounded-xl p-4">
            <div className="flex items-center justify-between gap-3 mb-3">
              <div>
                <div className="text-[10px] text-slate-500 uppercase tracking-wider font-bold">AI 流式分派过程</div>
                <div className="text-sm text-white font-semibold mt-1">
                  {incidentState?.phase === 'DISPATCHING'
                    ? '正在分步分析患者与候选终端'
                    : hasDispatchRationale || hasRoleAssignments
                      ? '展示最近一次分派决策链路'
                      : '等待患者端触发事件'}
                </div>
              </div>
              <div className="text-xs text-slate-400">
                {dispatchProgressLabel}
              </div>
            </div>
            <div className="space-y-3">
              {dispatchStream.length === 0 && (
                <div className="rounded-lg border border-slate-700 bg-slate-900/60 px-4 py-4 text-sm text-slate-400">
                  尚未触发患者端心脏骤停，暂无分派过程。
                </div>
              )}
              {dispatchStream.filter((step) => step.visible).map((step, index) => (
                <div
                  key={step.key}
                  className={cn(
                    "rounded-lg border px-4 py-3 transition-colors",
                    step.active ? "border-red-500 bg-red-950/30" : step.done ? "border-emerald-700/60 bg-emerald-950/20" : "border-slate-700 bg-slate-900/60"
                  )}
                >
                  <div className="flex items-center justify-between gap-3">
                    <div className="text-sm font-semibold text-white">{index + 1}. {step.title}</div>
                    <div className={cn(
                      "text-[10px] font-bold uppercase tracking-wider",
                      step.active ? "text-red-300" : step.done ? "text-emerald-300" : "text-slate-500"
                    )}>
                      {step.active ? '执行中' : step.done ? '已完成' : '等待中'}
                    </div>
                  </div>
                  <div className="text-xs text-slate-400 mt-2 leading-5">{step.detail}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
            <div className="bg-slate-800/70 border border-slate-700/60 rounded-xl p-4">
              <div className="flex items-center justify-between gap-3 mb-3">
                <div>
                  <div className="text-[10px] text-slate-500 uppercase tracking-wider font-bold">AED 点位库</div>
                  <div className="text-sm text-white font-semibold mt-1">可用于调度评分与预实验记录</div>
                </div>
                <button
                  onClick={loadAedSites}
                  className="text-[10px] text-slate-400 hover:text-white transition-colors"
                >
                  刷新
                </button>
              </div>
              <div className="space-y-2">
                {visibleAedSites.length === 0 && (
                  <div className="rounded-lg border border-slate-700 bg-slate-900/60 px-4 py-4 text-xs text-slate-400">
                    暂无 AED 点位，点击“初始化协同演示场景”可生成演示点位。
                  </div>
                )}
                {visibleAedSites.map((site) => (
                  <div key={site.siteId} className="rounded-lg border border-slate-700 bg-slate-900/60 px-4 py-3">
                    <div className="flex items-center justify-between gap-3">
                      <div className="text-sm font-semibold text-white">{site.name}</div>
                      <span className={cn(
                        "px-2 py-1 rounded-full text-[10px] font-bold",
                        site.status === 'AVAILABLE' ? "bg-emerald-500/15 text-emerald-300 border border-emerald-700/50" : "bg-amber-500/15 text-amber-300 border border-amber-700/50"
                      )}>
                        {translateAedStatus(site.status)}
                      </span>
                    </div>
                    <div className="text-xs text-slate-400 mt-2">{formatLocationLabel(site.location)}</div>
                    {site.accessNotes && (
                      <div className="text-xs text-slate-500 mt-2 leading-5">{site.accessNotes}</div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-slate-800/70 border border-slate-700/60 rounded-xl p-4">
              <div className="mb-3">
                <div className="text-[10px] text-slate-500 uppercase tracking-wider font-bold">调度解释</div>
                <div className="text-sm text-white font-semibold mt-1">角色选择理由与风险提示</div>
              </div>
              <div className="space-y-2">
                {rationaleEntries.length === 0 && !hasRoleAssignments && (
                  <div className="rounded-lg border border-slate-700 bg-slate-900/60 px-4 py-4 text-xs text-slate-400">
                    {dispatchExplanationPending ? 'AI 正在生成角色选择理由，请稍候。' : '尚未触发患者端事件，选择患者端后会生成可解释结果。'}
                  </div>
                )}
                {rationaleEntries.length === 0 && hasRoleAssignments && (
                  <div className="space-y-2">
                    <div className="rounded-lg border border-emerald-700/50 bg-emerald-950/20 px-4 py-3 text-xs text-emerald-200">
                      已完成任务分派，解释详情正在同步；下方先显示服务端确认的角色任务单。
                    </div>
                    {assignedRoleEntries.map(([role, roleState]) => (
                      <div key={role} className="rounded-lg border border-slate-700 bg-slate-900/60 px-4 py-3">
                        <div className="flex items-center justify-between gap-3">
                          <div>
                            <div className="text-sm font-semibold text-white">{translateRoleLabel(role)}</div>
                            <div className="text-xs text-slate-400 mt-1">{getClientDisplayName(roleState.userId)}</div>
                          </div>
                          <div className="text-right">
                            <div className="text-[10px] text-slate-500 uppercase tracking-wider">状态</div>
                            <div className="text-sm text-emerald-300">{translateRoleStatus(roleState.status)}</div>
                          </div>
                        </div>
                        <div className="text-xs text-slate-400 mt-3 leading-5">
                          服务端已确认该终端承担 {translateRoleLabel(role)} 任务，可继续在手机端响应协同流程。
                        </div>
                      </div>
                    ))}
                  </div>
                )}
                {rationaleEntries.map(([role, decision]) => (
                  <div key={role} className="rounded-lg border border-slate-700 bg-slate-900/60 px-4 py-3">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <div className="text-sm font-semibold text-white">{translateRoleLabel(role)}</div>
                        <div className="text-xs text-slate-400 mt-1">{getClientDisplayName(decision.userId)}</div>
                      </div>
                      <div className="text-right">
                        <div className="text-[10px] text-slate-500 uppercase tracking-wider">评分</div>
                        <div className="text-sm font-mono text-emerald-300">{decision.score.toFixed(1)}</div>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-2 mt-3 text-[10px] text-slate-400">
                      <div className="rounded bg-black/20 px-2 py-2">距患者 {formatDistanceLabel(decision.distanceToPatientMeters)}</div>
                      <div className="rounded bg-black/20 px-2 py-2">距 AED {formatDistanceLabel(decision.distanceToAedMeters)}</div>
                    </div>
                    {decision.reasons.length > 0 && (
                      <div className="text-xs text-slate-300 mt-3 leading-5">{decision.reasons.join('；')}</div>
                    )}
                    {decision.warnings.length > 0 && (
                      <div className="text-xs text-amber-300 mt-2 leading-5">{decision.warnings.join('；')}</div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="bg-slate-800/70 border border-slate-700/60 rounded-xl p-4">
            <div className="flex items-center justify-between mb-3">
              <div>
                <div className="text-[10px] text-slate-500 uppercase tracking-wider font-bold">在线安卓终端 ({clients.length})</div>
                <div className="text-[10px] text-slate-500 mt-1">
                  每 3 秒自动刷新
                  {lastClientRefreshTs ? ` · 最近更新 ${new Date(lastClientRefreshTs).toLocaleTimeString('zh-CN', { hour12: false })}` : ''}
                </div>
              </div>
              <button
                onClick={loadClients}
                className="text-[10px] text-slate-400 hover:text-white transition-colors"
              >
                刷新
              </button>
            </div>
            <div className="space-y-2">
              {clients.length === 0 && (
                <div className="text-xs text-slate-500">暂无在线安卓终端</div>
              )}
              {clients.map((client) => (
                <div
                  key={client.userId}
                  className={cn(
                    "rounded-lg border px-3 py-3 flex items-center justify-between gap-3",
                    client.isPatient
                      ? "border-red-500/70 bg-red-950/40"
                      : client.patientCandidate
                        ? "border-amber-500/60 bg-amber-950/20"
                        : "border-slate-700 bg-slate-900/60"
                  )}
                >
                  <div className="min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <div className="text-sm font-semibold text-white truncate">{client.displayName}</div>
                      {client.isPatient && (
                        <span className="px-2 py-1 rounded-full bg-red-600 text-white text-[10px] font-bold uppercase tracking-wider">患者</span>
                      )}
                      {!client.isPatient && client.patientCandidate && (
                        <span className="px-2 py-1 rounded-full bg-amber-500/20 text-amber-300 text-[10px] font-bold uppercase tracking-wider border border-amber-700/60">患者候选</span>
                      )}
                    </div>
                    <div className="text-[10px] text-slate-400 uppercase tracking-wider">
                      {client.healthCondition} · {client.professionIdentity} · {translateRoleLabel(client.assignedRole)}
                    </div>
                    <div className="text-[10px] text-slate-500 mt-1 truncate">
                      {client.organization} · {client.profileBio}
                    </div>
                    <div className="text-[10px] text-slate-500 mt-1 truncate">
                      位置：{formatLocationLabel(client.location)}
                    </div>
                    <HealthSignalBadge summary={client.healthSignals} />
                  </div>
                  <button
                    onClick={() => designatePatient(client.userId)}
                    className={cn(
                      "px-3 py-2 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-colors",
                      client.isPatient
                        ? "bg-red-600 text-white"
                        : "bg-slate-700 text-slate-200 hover:bg-red-600 hover:text-white"
                    )}
                  >
                    {client.isPatient ? '心脏骤停患者' : '触发心脏骤停'}
                  </button>
                </div>
              ))}
            </div>
          </div>
            </>
          )}

          {/* Task Orders */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className={cn(
              "p-4 rounded-lg border transition-colors",
              isPrimeActive ? "bg-red-900/40 border-red-500" : "bg-slate-800/60 border-slate-700/60",
              primeJoined ? "shadow-[0_0_14px_rgba(239,68,68,0.55)]" : "animate-pulse"
            )}>
              <div className="text-[10px] text-slate-400 uppercase tracking-wider font-bold">核心施救单</div>
              <div className="mt-2 text-sm text-slate-200">状态: {translateRoleStatus(incidentState?.roles?.PRIME?.status)}</div>
              <div className="text-[10px] text-slate-500 mt-1">CPR: {hasPrimeStarted(incidentState) ? '已启动' : '待启动'}</div>
            </div>

            <div className={cn(
              "p-4 rounded-lg border transition-colors",
              isRunnerActive ? "bg-blue-900/40 border-blue-500" : "bg-slate-800/60 border-slate-700/60",
              runnerJoined ? "shadow-[0_0_14px_rgba(59,130,246,0.55)]" : "animate-pulse"
            )}>
              <div className="text-[10px] text-slate-400 uppercase tracking-wider font-bold">AED保障单</div>
              <div className="mt-2 text-sm text-slate-200">状态: {translateRoleStatus(incidentState?.roles?.RUNNER?.status)}</div>
              <div className="text-[10px] text-slate-500 mt-1">AED: {hasRunnerDelivered(incidentState) ? '已送达' : hasRunnerPicked(incidentState) ? '已取到' : '待执行'}</div>
            </div>

            <div className={cn(
              "p-4 rounded-lg border transition-colors",
              isGuideActive ? "bg-yellow-900/40 border-yellow-500" : "bg-slate-800/60 border-slate-700/60",
              guideJoined ? "shadow-[0_0_14px_rgba(234,179,8,0.55)]" : "animate-pulse"
            )}>
              <div className="text-[10px] text-slate-400 uppercase tracking-wider font-bold">环境清障单</div>
              <div className="mt-2 text-sm text-slate-200">状态: {translateRoleStatus(incidentState?.roles?.GUIDE?.status)}</div>
              <div className="text-[10px] text-slate-500 mt-1">急救接管: {hasGuideCompleted(incidentState) ? '已完成' : '待到场'}</div>
            </div>
          </div>

          {/* Map Visualization */}
          <div className="flex-1 min-h-[300px] flex flex-col">
            <div className="text-[10px] text-slate-500 uppercase mb-2 font-bold tracking-wider">现场协同拓扑</div>
            <CloudMap phase={phase} />
          </div>

          {/* Live Logs */}
          {showTechnicalDetails && (
            <div className="h-64 bg-black rounded-lg border border-slate-800 p-4 overflow-hidden flex flex-col shadow-2xl">
              <div className="text-[10px] font-mono text-slate-500 mb-3 flex justify-between border-b border-slate-900 pb-2">
                <span>系统日志</span>
                <span className="text-green-500">● 实时</span>
              </div>
              <div
                ref={logContainerRef}
                onScroll={handleLogScroll}
                className="flex-1 overflow-y-auto space-y-3 font-mono text-xs pr-2 scrollbar-thin scrollbar-thumb-slate-800 scrollbar-track-transparent"
              >
                <AnimatePresence initial={false}>
                  {logs.map((log) => (
                    <motion.div
                      key={log.id}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      className="flex w-full min-w-0 items-start space-x-3 border-l-2 border-transparent pl-2 hover:bg-slate-900/50 py-1 rounded"
                      style={{ borderLeftColor: log.type === 'alert' ? '#ef4444' : log.type === 'success' ? '#22c55e' : 'transparent' }}
                    >
                      <span className="text-slate-600 min-w-[50px]">{log.time}</span>
                      <span className={cn(
                        "font-bold min-w-[80px]",
                        log.type === 'alert' ? 'text-red-500' :
                        log.type === 'success' ? 'text-green-500' : 'text-blue-400'
                      )}>{log.source}:</span>
                      <span className="min-w-0 flex-1 whitespace-pre-wrap break-words text-slate-300">{log.message}</span>
                    </motion.div>
                  ))}
                  <div ref={logEndRef} />
                </AnimatePresence>
                {logs.length === 0 && <div className="text-slate-700 italic text-center mt-10">等待事件触发...</div>}
              </div>
            </div>
          )}

        </div>

        <div className="lg:col-span-5 bg-slate-950 p-4 border-l border-slate-900 overflow-y-auto">
          <div className="sticky top-0 z-10 bg-slate-950 pb-4">
            <div className="text-[10px] text-slate-500 uppercase tracking-wider font-bold">终端状态总览</div>
            <div className="text-lg font-bold text-white mt-2">四端协同状态面板</div>
            <div className="text-xs text-slate-400 mt-1">不再展示虚拟手机壳，直接展示每个真实终端的画像、任务、阶段和最近状态。</div>
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 mt-4">
            {clients.length === 0 && (
              <div className="col-span-full rounded-2xl border border-slate-800 bg-slate-900/60 p-6 text-sm text-slate-400">
                暂无在线终端，请先让安卓端登录并接入当前事件。
              </div>
            )}
            {clients.map((client) => (
              <div
                key={client.userId}
                className={cn(
                  "rounded-2xl border p-5 shadow-xl",
                  client.isPatient
                    ? "border-red-500/70 bg-red-950/30"
                    : client.assignedRole === 'PRIME'
                      ? "border-green-500/50 bg-emerald-950/20"
                      : client.assignedRole === 'RUNNER'
                        ? "border-blue-500/50 bg-blue-950/20"
                        : client.assignedRole === 'GUIDE'
                          ? "border-yellow-500/50 bg-yellow-950/20"
                          : client.patientCandidate
                            ? "border-amber-500/60 bg-amber-950/20"
                            : "border-slate-700 bg-slate-900/60"
                )}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="text-lg font-bold text-white truncate">{client.displayName}</div>
                    <div className="text-xs text-slate-400 mt-1">{translateRoleLabel(client.assignedRole)}</div>
                  </div>
                  <div className="flex flex-wrap justify-end gap-2">
                    {client.isPatient && <span className="px-2 py-1 rounded-full bg-red-600 text-white text-[10px] font-bold">患者端</span>}
                    {!client.isPatient && client.patientCandidate && <span className="px-2 py-1 rounded-full bg-amber-500/20 border border-amber-700/60 text-amber-300 text-[10px] font-bold">患者候选</span>}
                    <span className={cn(
                      "px-2 py-1 rounded-full text-[10px] font-bold",
                      client.online ? "bg-emerald-500/15 text-emerald-300 border border-emerald-700/50" : "bg-slate-700 text-slate-300"
                    )}>
                      {client.online ? '在线' : '离线'}
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3 mt-4 text-xs">
                  <div className="rounded-xl bg-black/20 px-3 py-3">
                    <div className="text-slate-500">身体状况</div>
                    <div className="text-slate-100 mt-1">{client.healthCondition}</div>
                  </div>
                  <div className="rounded-xl bg-black/20 px-3 py-3">
                    <div className="text-slate-500">职业身份</div>
                    <div className="text-slate-100 mt-1">{client.professionIdentity}</div>
                  </div>
                  <div className="rounded-xl bg-black/20 px-3 py-3">
                    <div className="text-slate-500">事件阶段</div>
                    <div className="text-slate-100 mt-1">{translatePhaseLabel(incidentState?.phase)}</div>
                  </div>
                  <div className="rounded-xl bg-black/20 px-3 py-3">
                    <div className="text-slate-500">最近上线</div>
                    <div className="text-slate-100 mt-1">{formatTimeLabel(client.lastSeenTs)}</div>
                  </div>
                  <div className="rounded-xl bg-black/20 px-3 py-3 col-span-2">
                    <div className="flex items-center justify-between gap-2">
                      <div className="text-slate-500">OPPO 健康摘要</div>
                      <span className={cn(
                        "rounded-full px-2 py-0.5 text-[10px] font-bold",
                        client.healthSignals?.source === 'mock'
                          ? "bg-amber-500/15 text-amber-300"
                          : client.healthSignals
                            ? "bg-emerald-500/15 text-emerald-300"
                            : "bg-slate-700 text-slate-400"
                      )}>
                        {translateHealthSource(client.healthSignals?.source)}
                      </span>
                    </div>
                    <div className="mt-2 flex flex-wrap gap-2 text-slate-100">
                      <span>{client.healthSignals?.heartRateBpm ? `${client.healthSignals.heartRateBpm} bpm` : '心率 --'}</span>
                      <span>{client.healthSignals?.bloodOxygenPercent ? `${client.healthSignals.bloodOxygenPercent}% SpO2` : '血氧 --'}</span>
                      <span>{client.healthSignals?.pressureScore !== undefined && client.healthSignals?.pressureScore !== null ? `压力 ${client.healthSignals.pressureScore}` : '压力 --'}</span>
                    </div>
                    {Boolean(client.healthSignals?.riskTags?.length) && (
                      <div className="mt-2 text-amber-300">
                        风险标记：{formatHealthRiskTags(client.healthSignals?.riskTags)}
                      </div>
                    )}
                  </div>
                </div>

                <div className="mt-4 rounded-xl bg-black/20 px-4 py-4">
                  <div className="text-xs text-slate-500">当前任务</div>
                  <div className="text-sm text-white font-semibold mt-2">{describeClientMission(client, incidentState)}</div>
                  <div className="text-xs text-slate-400 mt-3">
                    组织场景：{client.organization}
                  </div>
                  <div className="text-xs text-slate-500 mt-2 leading-5">
                    个人介绍：{client.profileBio}
                  </div>
                  <div className="text-xs text-slate-300 mt-3">
                    任务状态：{translateRoleStatus(
                      client.assignedRole === 'PRIME'
                        ? incidentState?.roles?.PRIME?.status
                        : client.assignedRole === 'RUNNER'
                          ? incidentState?.roles?.RUNNER?.status
                          : client.assignedRole === 'GUIDE'
                            ? incidentState?.roles?.GUIDE?.status
                            : null
                    )}
                  </div>
                  <div className="text-xs text-slate-400 mt-2">
                    位置：{formatLocationLabel(client.location)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
