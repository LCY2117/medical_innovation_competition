/** 与后端 M1 契约对齐的全部类型定义。 */

export type Role = "PATIENT" | "PRIME" | "RUNNER" | "GUIDE" | "SYSTEM" | "ADMIN";

export interface AvailableAction {
  action: string;
  label: string;
  to_status: string | null;
}

export interface Assignment {
  id: number;
  responder_id: number;
  responder_name: string;
  role: string;
  status: string; // PENDING / CONFIRMED / DECLINED / BACKUP
  priority: number;
  score: number;
  assigned_at: string | null;
  responded_at: string | null;
}

export interface EventData {
  id: number;
  status: string;
  seq: number;
  patient_id: number;
  prime_confirmed: boolean;
  runner_confirmed: boolean;
  guide_confirmed: boolean;
  ambulance_arrived: boolean;
  shock_count: number;
  started_at: string | null;
  created_at: string | null;
  updated_at: string | null;
  location: string;
  latitude: number;
  longitude: number;
  assignments?: Assignment[];
  available_actions: AvailableAction[];
}

export interface Transition {
  id: number;
  seq: number;
  action: string;
  from_status: string;
  to_status: string;
  actor_id: number | null;
  actor_role: string;
  duplicate: boolean;
  payload: Record<string, unknown>;
  created_at: string | null;
}

export interface HealthReading {
  id: number;
  reading_type: string;
  value: number;
  unit: string;
  source: string;
  recorded_at: string | null;
}

export interface AedDevice {
  id: number;
  name: string;
  location: string;
  latitude: number;
  longitude: number;
  available: boolean;
  created_at: string | null;
  updated_at: string | null;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user_id: number;
  role: Role;
  username: string;
  expires_in: number;
}

export interface ActionResult {
  applied: boolean;
  duplicate: boolean;
  from_status: string;
  to_status: string;
  reason: string;
  new_seq: number;
  event: EventData | null;
}

/** 事件状态机中文可读标签（前端兜底，后端 available_actions.label 为权威）。 */
export const STATUS_LABELS: Record<string, string> = {
  CREATED: "已创建",
  SOS: "SOS 已触发",
  DISPATCHED: "已分派",
  CPR: "心肺复苏中",
  AED_PICKED: "AED 已取出",
  AED_DELIVERED: "AED 已送达",
  AED_ANALYZING: "AED 分析中",
  SHOCK_DELIVERED: "已实施除颤",
  HANDOVER: "交接中",
  ARCHIVED: "已归档",
};

/** WS 消息类型。 */
export type WsMessageType =
  | "EVENT_SNAPSHOT"
  | "EVENT_UPDATE"
  | "TRANSITION_ADDED"
  | "ASSIGNMENT_UPDATE"
  | "HEALTH_READING"
  | "TIMER_SYNC"
  | "PONG"
  | "PING"
  | "ERROR";

export interface WsMessage<T = Record<string, unknown>> {
  type: WsMessageType;
  ts: number;
  /** 版本 = event.seq，单调递增；无 version 的消息（PONG/ERROR/PING）不做合并。 */
  version?: number;
  data: T;
}

export interface WsSnapshotData extends EventData {}
export interface WsTransitionAddedData {
  transition?: Transition;
  transitions?: Transition[];
  available_actions?: AvailableAction[];
}
export interface WsAssignmentUpdateData {
  assignments: Assignment[];
}
export interface WsHealthReadingData {
  reading: HealthReading;
}
export interface WsTimerSyncData {
  elapsed: number;
  started_at: string | null;
}
