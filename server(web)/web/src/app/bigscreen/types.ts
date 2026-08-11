import type { DispatchMeta, HealthDetail, IncidentState } from '@/shared/types';

export interface AdminSessionUser {
  userId: string;
  displayName: string;
  phone: string;
  privileges?: string[];
}

export interface AdminSession {
  token: string;
  user: AdminSessionUser;
  tokenExpiresAt?: number | null;
}

export interface AuditEvent {
  eventId: string;
  eventType: string;
  actorId?: string | null;
  actorType?: string | null;
  targetId?: string | null;
  targetType?: string | null;
  outcome: string;
  requestHash?: string | null;
  ts: number;
}

export interface PackageDownloadInfo {
  filename: string;
  packageSha256: string | null;
}

export type LogEntryType = 'alert' | 'success' | 'info';

export interface LogEntry {
  id: string;
  time: string;
  source: string;
  message: string;
  type: LogEntryType;
}

export interface DispatchStreamStep {
  key: string;
  title: string;
  detail: string;
  visible: boolean;
  done: boolean;
  active: boolean;
}

export interface DemoFlowStep {
  title: string;
  detail: string;
  complete: boolean;
  active: boolean;
}

export interface DemoShareLink {
  key: string;
  label: string;
  caption: string;
  url: string;
}

export interface ReadinessItem {
  label: string;
  value: string;
  ready: boolean;
}

export interface DashboardData {
  incidentId: string | null;
  incidentState: IncidentState | null;
  clients: import('@/shared/types').ClientInfo[];
  aedSites: import('@/shared/types').AedSite[];
  dispatchMeta: DispatchMeta | null;
  healthDetail: HealthDetail | null;
}
