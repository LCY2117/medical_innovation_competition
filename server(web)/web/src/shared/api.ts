import type {
  AuthMeResponse,
  AuthResponse,
  AuthUser,
  AedSite,
  ClientInfo,
  GeoPoint,
  HealthSignalSummary,
  IncidentState,
  RoleName,
} from './types';

const ENV_API_BASE = import.meta.env.VITE_API_BASE?.trim();
const ENV_WS_BASE = import.meta.env.VITE_WS_BASE?.trim();

export function normalizeBaseUrl(value: string): string {
  return value.endsWith('/') ? value.slice(0, -1) : value;
}

export function getApiBase(): string {
  if (ENV_API_BASE) {
    return normalizeBaseUrl(ENV_API_BASE);
  }
  if (typeof window === 'undefined') {
    return '/api';
  }
  return `${window.location.origin}/api`;
}

export function getWsBase(): string {
  if (ENV_WS_BASE) {
    return normalizeBaseUrl(ENV_WS_BASE);
  }
  if (typeof window === 'undefined') {
    return '/ws';
  }
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${protocol}//${window.location.host}/ws`;
}

export function getStoreddemoAdminToken(): string {
  if (typeof window === 'undefined') {
    return '';
  }
  return window.localStorage.getItem('lra_demo_admin_token') ?? '';
}

export function builddemoAdminHeaders(token: string, extra?: HeadersInit): HeadersInit {
  const headers = new Headers(extra);
  const trimmed = token.trim();
  if (trimmed) {
    headers.set('X-demo-Admin-Token', trimmed);
  }
  return headers;
}

export function buildAuthHeaders(token: string | null | undefined, extra?: HeadersInit): HeadersInit {
  const headers = new Headers(extra);
  const trimmed = token?.trim();
  if (trimmed) {
    headers.set('Authorization', `Bearer ${trimmed}`);
  }
  return headers;
}

export function explainStatusError(status: number, fallback: string): string {
  if (status === 401) {
    return `${fallback}：请先登录`;
  }
  if (status === 403) {
    return `${fallback}：权限不足或需要演示管理员口令`;
  }
  return `${fallback}（${status}）`;
}

export async function explainResponseError(response: Response, fallback: string): Promise<string> {
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

async function requestJson<T>(path: string, init?: RequestInit, fallback = '请求失败'): Promise<T> {
  const res = await fetch(`${getApiBase()}${path}`, init);
  if (!res.ok) {
    throw new Error(await explainResponseError(res, fallback));
  }
  return (await res.json()) as T;
}

export interface RegisterForm {
  displayName: string;
  phone: string;
  password: string;
  organization: string;
  healthCondition: string;
  professionIdentity: string;
  profileBio: string;
}

export async function registerAccount(form: RegisterForm): Promise<AuthResponse> {
  return requestJson<AuthResponse>(
    '/auth/register',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form),
    },
    '注册失败',
  );
}

export async function loginAccount(phone: string, password: string): Promise<AuthResponse> {
  return requestJson<AuthResponse>(
    '/auth/login',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone, password }),
    },
    '登录失败',
  );
}

export async function logindemoPersona(persona: string): Promise<AuthResponse> {
  return requestJson<AuthResponse>(
    '/auth/demo',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ persona }),
    },
    '进入演示模式失败',
  );
}

export async function fetchMe(token: string): Promise<AuthMeResponse> {
  return requestJson<AuthMeResponse>('/auth/me', { headers: buildAuthHeaders(token) }, '校验登录态失败');
}

export async function logoutAccount(token: string): Promise<void> {
  await requestJson('/auth/logout', { method: 'POST', headers: buildAuthHeaders(token) }, '退出登录失败');
}

export async function registerClient(user: AuthUser, token: string, location?: GeoPoint | null): Promise<void> {
  await requestJson(
    '/clients/register',
    {
      method: 'POST',
      headers: buildAuthHeaders(token, { 'Content-Type': 'application/json' }),
      body: JSON.stringify({
        userId: user.userId,
        displayName: user.displayName,
        organization: user.organization,
        healthCondition: user.healthCondition,
        professionIdentity: user.professionIdentity,
        profileBio: user.profileBio,
        deviceType: 'MOBILE_WEB',
        location,
      }),
    },
    '注册浏览器终端失败',
  );
}

export async function updateClientHealth(userId: string, token: string, healthSignals: HealthSignalSummary): Promise<void> {
  await requestJson(
    '/clients/health',
    {
      method: 'POST',
      headers: buildAuthHeaders(token, { 'Content-Type': 'application/json' }),
      body: JSON.stringify({ userId, healthSignals }),
    },
    '同步健康摘要失败',
  );
}

export async function updateClientLocation(userId: string, token: string, location: GeoPoint): Promise<void> {
  await requestJson(
    '/clients/location',
    {
      method: 'POST',
      headers: buildAuthHeaders(token, { 'Content-Type': 'application/json' }),
      body: JSON.stringify({ userId, location }),
    },
    '更新位置失败',
  );
}

export async function fetchCurrentIncident(): Promise<IncidentState> {
  return requestJson<IncidentState>('/incidents/current', undefined, '加载当前事件失败');
}

export async function fetchIncident(incidentId: string): Promise<IncidentState> {
  return requestJson<IncidentState>(`/incidents/${encodeURIComponent(incidentId)}`, undefined, '加载事件失败');
}

export async function fetchClients(): Promise<ClientInfo[]> {
  const data = await requestJson<{ clients: ClientInfo[] }>('/clients', undefined, '加载在线终端失败');
  return Array.isArray(data.clients) ? data.clients : [];
}

export async function fetchAedSites(): Promise<AedSite[]> {
  const data = await requestJson<{ aedSites: AedSite[] }>('/aed-sites', undefined, '加载 AED 点位失败');
  return Array.isArray(data.aedSites) ? data.aedSites : [];
}

export async function autoJoinCurrent(userId: string, token: string): Promise<{ incidentId: string; role: RoleName }> {
  return requestJson(
    '/incidents/current/join_auto',
    {
      method: 'POST',
      headers: buildAuthHeaders(token, { 'Content-Type': 'application/json' }),
      body: JSON.stringify({ userId }),
    },
    '自动接入任务失败',
  );
}

export async function joinIncident(incidentId: string, role: RoleName, userId: string, token: string): Promise<void> {
  await requestJson(
    `/incidents/${encodeURIComponent(incidentId)}/join`,
    {
      method: 'POST',
      headers: buildAuthHeaders(token, { 'Content-Type': 'application/json' }),
      body: JSON.stringify({ role, userId }),
    },
    '响应任务失败',
  );
}

export async function postIncidentAction(incidentId: string, action: string, userId: string, token: string): Promise<void> {
  await requestJson(
    `/incidents/${encodeURIComponent(incidentId)}/actions`,
    {
      method: 'POST',
      headers: buildAuthHeaders(token, { 'Content-Type': 'application/json' }),
      body: JSON.stringify({ action, userId }),
    },
    '提交动作失败',
  );
}

export async function patientSosStart(incidentId: string, token: string): Promise<void> {
  await requestJson(
    `/incidents/${encodeURIComponent(incidentId)}/patient_sos_start`,
    {
      method: 'POST',
      headers: buildAuthHeaders(token),
    },
    '启动患者 SOS 失败',
  );
}

export async function patientSosCancel(incidentId: string, token: string): Promise<void> {
  await requestJson(
    `/incidents/${encodeURIComponent(incidentId)}/patient_sos_cancel`,
    {
      method: 'POST',
      headers: buildAuthHeaders(token),
    },
    '取消患者 SOS 失败',
  );
}

export function openIncidentSocket(incidentId: string): WebSocket {
  return new WebSocket(`${getWsBase()}?incidentId=${encodeURIComponent(incidentId)}`);
}

export interface DownloadedPackageInfo {
  filename: string;
  packageSha256: string | null;
}

export async function downloadExperimentPackage(
  token?: string | null,
  demoAdminToken = getStoreddemoAdminToken(),
  incidentId?: string | null,
): Promise<DownloadedPackageInfo> {
  if (typeof window === 'undefined') {
    throw new Error('下载事件证据包失败：当前环境不支持浏览器下载');
  }
  const headers = builddemoAdminHeaders(demoAdminToken, buildAuthHeaders(token));
  const trimmedIncidentId = incidentId?.trim();
  const packagePath = trimmedIncidentId
    ? `/experiments/${encodeURIComponent(trimmedIncidentId)}/package`
    : '/experiments/current/package';
  const response = await fetch(`${getApiBase()}${packagePath}`, { headers });
  if (!response.ok) {
    throw new Error(await explainResponseError(response, '下载事件证据包失败'));
  }
  const blob = await response.blob();
  const disposition = response.headers.get('Content-Disposition') ?? '';
  const encoded = disposition.match(/filename\*=UTF-8''([^;]+)/)?.[1];
  const plain = disposition.match(/filename="?([^";]+)"?/)?.[1];
  const filename = encoded ? decodeURIComponent(encoded) : plain || 'lifereflex-experiment-current.zip';
  const packageSha256 = response.headers.get('X-LifeReflexArc-Package-Sha256');
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
  return { filename, packageSha256 };
}
