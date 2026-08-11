export type RoleName = 'PRIME' | 'RUNNER' | 'GUIDE';

export type ThemeMode = 'dark' | 'light';

export interface GeoPoint {
  latitude: number;
  longitude: number;
  accuracyMeters?: number | null;
  label?: string | null;
  floor?: string | null;
  source?: string;
  updatedTs?: number | null;
}

export interface HealthSignalSummary {
  source: string;
  authorizationStatus: string;
  provider?: string;
  heartRateBpm?: number | null;
  bloodOxygenPercent?: number | null;
  pressureScore?: number | null;
  activityLevel?: string | null;
  sleepQuality?: string | null;
  riskTags?: string[];
  updatedTs?: number | null;
  note?: string | null;
}

export interface AedSite {
  siteId: string;
  name: string;
  location: GeoPoint;
  status: string;
  accessNotes?: string;
  lastCheckedTs?: number | null;
}

export interface DispatchRoleDecision {
  userId?: string | null;
  score: number;
  reasons: string[];
  warnings: string[];
  distanceToPatientMeters?: number | null;
  nearestAedSiteId?: string | null;
  distanceToAedMeters?: number | null;
  aedToPatientMeters?: number | null;
}

export interface RoleState {
  status?: string | null;
  userId?: string | null;
}

export interface AiTaskState {
  taskId: string;
  title: string;
  description: string;
  requiredSkill: string;
  priority: number;
  locationLabel: string | null;
  createdBy: string;
  createdRole: string;
  status: 'PENDING' | 'ACTIVE' | 'COMPLETED' | 'CANCELLED';
  assignableUserIds: string[];
  runnerUserId: string | null;
  supportUserIds: string[];
  capScores: Record<string, number>;
  matchScores: Record<string, number>;
  matchReasons: Record<string, string[]>;
  scoreRev: number;
  requires: string[];
  createdAt: number;
  updatedAt: number;
  acceptedAt: number | null;
  releasedAt: number | null;
  completedAt: number | null;
  statusLogs: { ts: number; type: string; userId: string; note?: string }[];
}

export interface IncidentState {
  incidentId: string;
  phase: string;
  sos?: { status: string; startTs: number | null; durationSec: number };
  patientUserId?: string | null;
  dispatchSource?: string | null;
  roles: Record<RoleName, RoleState>;
  logs: { ts: number; msg: string }[];
  aedSites?: AedSite[];
  dispatchRationale?: Record<string, DispatchRoleDecision>;
  aiTasks?: Record<string, AiTaskState>;
}

export interface ClientInfo {
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

export interface DispatchMeta {
  configured: boolean;
  provider: string;
  dispatchDelaySec: number;
  model: string;
  baseUrl: string;
  timeoutSec: number;
  llmBudgetSec?: number;
  configFile: string;
  envKeys: string[];
  candidateFields: string[];
  selectionRules: Record<string, string>;
  responseFormat: Record<string, string>;
  systemPrompt: string;
}

export interface HealthDetail {
  demoAdminAuthEnabled?: boolean;
  frontend?: { ok?: boolean };
}

export interface AuthUser {
  userId: string;
  displayName: string;
  phone: string;
  organization: string;
  healthCondition: string;
  professionIdentity: string;
  profileBio: string;
  credentialStatus: string;
  privileges?: string[];
}

export interface AuthResponse {
  ok: boolean;
  token: string;
  user: AuthUser;
  tokenExpiresAt?: number | null;
}

export interface AuthMeResponse {
  ok: boolean;
  user: AuthUser;
  tokenExpiresAt?: number | null;
}
