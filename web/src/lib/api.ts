/** REST 封装：所有请求带 Bearer Token，统一错误抛出。 */
import type {
  ActionResult,
  AedDevice,
  AuthResponse,
  EventData,
  HealthReading,
  Role,
  Transition,
} from "./types";

/** 开发走 Vite 代理 /api/v1；生产同源 /api/v1（Nginx 反代）。 */
const API_BASE = (import.meta.env.VITE_API_BASE as string | undefined) || "/api/v1";

const TOKEN_KEY = "lifereflex.token";

export function getStoredToken(): string {
  try {
    return localStorage.getItem(TOKEN_KEY) || "";
  } catch {
    return "";
  }
}

export function storeToken(token: string): void {
  try {
    if (token) localStorage.setItem(TOKEN_KEY, token);
    else localStorage.removeItem(TOKEN_KEY);
  } catch {
    /* ignore */
  }
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  token?: string,
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  const auth = token ?? getStoredToken();
  if (auth) headers.Authorization = `Bearer ${auth}`;

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      /* 非 JSON 响应 */
    }
    throw new ApiError(res.status, detail);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

// ---------- 认证 ----------

export function demoLogin(role: Role): Promise<AuthResponse> {
  return request<AuthResponse>("/auth/demo", {
    method: "POST",
    body: JSON.stringify({ role }),
  });
}

export function login(username: string, password: string): Promise<AuthResponse> {
  return request<AuthResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
}

// ---------- 事件 ----------

export function createSOS(location = "中心广场"):
  Promise<EventData> {
  return request<EventData>("/events/sos", {
    method: "POST",
    body: JSON.stringify({ location }),
  });
}

export function getEvent(eventId: number): Promise<EventData> {
  return request<EventData>(`/events/${eventId}`);
}

/** 自动发现当前活跃事件（响应端登录后调用，无需手输编号）。 */
export function getActiveEvent(): Promise<{ event: EventData | null }> {
  return request<{ event: EventData | null }>("/events/active");
}

export function getTimeline(eventId: number): Promise<Transition[]> {
  return request<Transition[]>(`/events/${eventId}/timeline`);
}

export function getHealth(eventId: number): Promise<HealthReading[]> {
  return request<HealthReading[]>(`/events/${eventId}/health`);
}

export function submitAction(
  eventId: number,
  action: string,
  metadata: Record<string, unknown> = {},
): Promise<ActionResult> {
  return request<ActionResult>(`/events/${eventId}/actions`, {
    method: "POST",
    body: JSON.stringify({ action, metadata }),
  });
}

/** 一键触发演示事件（SYSTEM/ADMIN）：创建事件 + SOS + 立即分派。 */
export function demoTrigger(): Promise<EventData> {
  return request<EventData>("/demo/trigger", { method: "POST", body: "{}" });
}

/** 重置全部演示业务数据（SYSTEM/ADMIN）。 */
export function demoReset(): Promise<{ ok: boolean; message: string }> {
  return request("/demo/reset", { method: "POST", body: "{}" });
}

/** 初始化/补齐种子数据（SYSTEM/ADMIN，幂等）。 */
export function demoInit(): Promise<{ ok: boolean; seeded: boolean }> {
  return request("/demo/init", { method: "POST", body: "{}" });
}

/** AED 设备列表（大屏 AED 点位面板）。 */
export function getAedDevices(): Promise<AedDevice[]> {
  return request<AedDevice[]>("/aed");
}

/** 上报健康读数（大屏"模拟体征"用，SYSTEM 允许）。 */
export function postHealthReading(
  eventId: number,
  body: {
    reading_type: string;
    value: number;
    unit: string;
    source: string;
  },
): Promise<HealthReading> {
  return request<HealthReading>(`/events/${eventId}/health`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/** 证据包（JSON 结构）。 */
export function getEvidence(
  eventId: number,
): Promise<Record<string, unknown>> {
  return request<Record<string, unknown>>(`/events/${eventId}/evidence`);
}

/** 下载证据 ZIP（带 Bearer 的二进制下载）。 */
export async function downloadEvidenceZip(eventId: number): Promise<void> {
  const res = await fetch(`${API_BASE}/events/${eventId}/evidence.zip`, {
    headers: { Authorization: `Bearer ${getStoredToken()}` },
  });
  if (!res.ok) throw new ApiError(res.status, `导出失败 HTTP ${res.status}`);
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `event-${eventId}-evidence.zip`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 4000);
}

/** 下载 JSON 文本文件（触发浏览器保存）。 */
export function downloadJson(filename: string, data: unknown): void {
  const blob = new Blob([JSON.stringify(data, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 4000);
}
