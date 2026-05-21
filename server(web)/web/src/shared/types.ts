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
