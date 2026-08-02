import type { AuthUser, GeoPoint } from './types';

export interface StoredSession {
  token: string;
  user: AuthUser;
  tokenExpiresAt?: number | null;
  demoPersona?: 'patient' | 'prime' | 'runner' | 'guide';
}

const SESSION_KEY = 'lra_mobile_session';
const TAB_SESSION_KEY = 'lra_mobile_tab_session';
const LOCATION_KEY = 'lra_mobile_location';
const THEME_KEY = 'lra_mobile_theme';

function demoSlotFromUrl(): string | null {
  if (typeof window === 'undefined') return null;
  const raw = new URLSearchParams(window.location.search).get('slot');
  return raw && /^[a-z0-9_-]{0,24}$/.test(raw) ? raw : null;
}

function tabSessionKey(): string {
  const slot = demoSlotFromUrl();
  return slot ? `${TAB_SESSION_KEY}_${slot}` : TAB_SESSION_KEY;
}

function tabLocationKey(): string {
  const slot = demoSlotFromUrl();
  return slot ? `${LOCATION_KEY}_${slot}` : LOCATION_KEY;
}

export function readStoredSession(): StoredSession | null {
  if (typeof window === 'undefined') return null;
  const raw = window.sessionStorage.getItem(tabSessionKey())
    || window.sessionStorage.getItem(TAB_SESSION_KEY)
    || window.localStorage.getItem(SESSION_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as StoredSession;
  } catch {
    return null;
  }
}

export function saveSession(session: StoredSession): void {
  if (typeof window === 'undefined') return;
  const json = JSON.stringify(session);
  if (session.demoPersona) {
    window.sessionStorage.setItem(tabSessionKey(), json);
  } else {
    window.localStorage.setItem(SESSION_KEY, json);
  }
}

export function clearSession(): void {
  if (typeof window === 'undefined') return;
  window.sessionStorage.removeItem(tabSessionKey());
  window.localStorage.removeItem(SESSION_KEY);
}

export function readStoredLocation(): GeoPoint | null {
  if (typeof window === 'undefined') return null;
  const raw = window.sessionStorage.getItem(tabLocationKey())
    || window.localStorage.getItem(LOCATION_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as GeoPoint;
  } catch {
    return null;
  }
}

export function saveLocation(location: GeoPoint): void {
  if (typeof window === 'undefined') return;
  const json = JSON.stringify(location);
  window.sessionStorage.setItem(tabLocationKey(), json);
  window.localStorage.setItem(LOCATION_KEY, json);
}

export type MobileTheme = 'light' | 'dark';

export function readStoredTheme(): MobileTheme {
  if (typeof window === 'undefined') return 'dark';
  const stored = window.localStorage.getItem(THEME_KEY) as MobileTheme | null;
  if (stored === 'light' || stored === 'dark') return stored;
  return window.matchMedia?.('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
}

export function saveTheme(theme: MobileTheme): void {
  if (typeof window === 'undefined') return;
  window.localStorage.setItem(THEME_KEY, theme);
}

export function getStoreddemoAdminToken(): string {
  if (typeof window === 'undefined') return '';
  return window.localStorage.getItem('lra_demo_admin_token') ?? '';
}
