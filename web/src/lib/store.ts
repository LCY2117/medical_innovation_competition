/** 全局状态：鉴权 + 事件 + WS 版本合并（防旧消息回退）。 */
import { create } from "zustand";
import { persist } from "zustand/middleware";

import {
  createSOS,
  demoLogin,
  getActiveEvent,
  getEvent,
  getHealth,
  getTimeline,
  login,
  storeToken,
  submitAction as apiSubmitAction,
} from "./api";
import { EventSocket, type WsStatus } from "./ws";
import type {
  EventData,
  HealthReading,
  Role,
  Transition,
  WsAssignmentUpdateData,
  WsHealthReadingData,
  WsMessage,
  WsTimerSyncData,
  WsTransitionAddedData,
} from "./types";

export const LAST_EVENT_KEY = "lifereflex.lastEventId";

interface AuthSlice {
  token: string | null;
  role: Role | null;
  username: string | null;
  userId: number | null;
}

interface AppState extends AuthSlice {
  event: EventData | null;
  timeline: Transition[];
  health: HealthReading[];
  lastVersion: number;
  wsStatus: WsStatus;
  currentEventId: number | null;
  submitting: boolean;
  error: string | null;
  initialized: boolean;
  /** 活跃事件自动发现状态：idle=未查询 / found=已发现并订阅 / none=暂无进行中事件。 */
  discovery: "idle" | "found" | "none";

  // actions
  init: () => void;
  loginDemo: (role: Role) => Promise<void>;
  loginForm: (username: string, password: string) => Promise<void>;
  logout: () => void;
  attachEvent: (eventId: number) => Promise<void>;
  refreshEvent: () => Promise<void>;
  triggerSOS: () => Promise<EventData | null>;
  autoDiscoverEvent: () => Promise<void>;
  detachEvent: () => void;
  submitAction: (action: string, metadata?: Record<string, unknown>) => Promise<void>;
  handleWsMessage: (msg: WsMessage) => void;
  clearError: () => void;
}

/** WS 单例：登录后建立、登出关闭。 */
let socket: EventSocket | null = null;

function ensureSocket(): EventSocket {
  const token = useStore.getState().token;
  if (socket) return socket;
  socket = new EventSocket({
    token: token ?? "",
    onMessage: (msg) => useStore.getState().handleWsMessage(msg),
    onStatus: (s) => useStore.setState({ wsStatus: s }),
  });
  socket.connect();
  return socket;
}

function socketOrNull(): EventSocket | null {
  return socket;
}

/** 字段级合并：EVENT_UPDATE/SNAPSHOT 不含 assignments，需保留旧值。 */
function mergeEvent(prev: EventData | null, incoming: Partial<EventData>): EventData {
  if (!prev) return incoming as EventData;
  return {
    ...prev,
    ...incoming,
    assignments: incoming.assignments ?? prev.assignments,
  };
}

/** 时间线合并：按 id 去重 + seq 升序（幂等追加）。 */
function mergeTimeline(prev: Transition[], incoming: Transition[]): Transition[] {
  const map = new Map<number, Transition>();
  for (const t of [...prev, ...incoming]) map.set(t.id, t);
  return [...map.values()].sort((a, b) => a.seq - b.seq || a.id - b.id);
}

function errText(e: unknown): string {
  return e instanceof Error ? e.message : String(e);
}

export const useStore = create<AppState>()(
  persist(
    (set, get) => ({
      token: null,
      role: null,
      username: null,
      userId: null,
      event: null,
      timeline: [],
      health: [],
      lastVersion: 0,
      wsStatus: "closed",
      currentEventId: null,
      submitting: false,
      error: null,
      initialized: false,
      discovery: "idle",

      init: () => {
        const { token, currentEventId } = get();
        if (!token) {
          set({ initialized: true });
          return;
        }
        // 恢复会话：连 WS + 若有事件则订阅并拉快照
        if (currentEventId !== null) {
          const s = ensureSocket();
          s.subscribe(currentEventId);
          void get().refreshEvent();
        } else {
          ensureSocket();
        }
        set({ initialized: true });
      },

      loginDemo: async (role) => {
        try {
          const res = await demoLogin(role);
          storeToken(res.access_token);
          set({
            token: res.access_token,
            role: res.role,
            username: res.username,
            userId: res.user_id,
            error: null,
          });
          ensureSocket();
        } catch (e) {
          set({ error: `登录失败：${errText(e)}` });
          throw e;
        }
      },

      loginForm: async (username, password) => {
        try {
          const res = await login(username, password);
          storeToken(res.access_token);
          set({
            token: res.access_token,
            role: res.role,
            username: res.username,
            userId: res.user_id,
            error: null,
          });
          ensureSocket();
        } catch (e) {
          set({ error: `登录失败：${errText(e)}` });
          throw e;
        }
      },

      logout: () => {
        socketOrNull()?.close();
        socket = null;
        storeToken("");
        localStorage.removeItem(LAST_EVENT_KEY);
        set({
          token: null,
          role: null,
          username: null,
          userId: null,
          event: null,
          timeline: [],
          health: [],
          lastVersion: 0,
          wsStatus: "closed",
          currentEventId: null,
          error: null,
          discovery: "idle",
        });
      },

      attachEvent: async (eventId) => {
        set({ currentEventId: eventId, discovery: "found", error: null });
        try {
          localStorage.setItem(LAST_EVENT_KEY, String(eventId));
        } catch {
          /* ignore */
        }
        const s = ensureSocket();
        s.subscribe(eventId);
        await get().refreshEvent();
      },

      refreshEvent: async () => {
        const eventId = get().currentEventId;
        if (eventId === null) return;
        try {
          const [event, timeline, health] = await Promise.all([
            getEvent(eventId),
            getTimeline(eventId),
            getHealth(eventId),
          ]);
          set((s) => ({
            event: mergeEvent(s.event, event),
            timeline: mergeTimeline(s.timeline, timeline),
            health,
            lastVersion: Math.max(s.lastVersion, event.seq),
            error: null,
          }));
        } catch (e) {
          set({ error: `刷新事件失败：${errText(e)}` });
        }
      },

      triggerSOS: async () => {
        try {
          const event = await createSOS();
          set({
            event,
            timeline: [],
            health: [],
            lastVersion: event.seq,
            error: null,
            discovery: "found",
          });
          await get().attachEvent(event.id);
          return event;
        } catch (e) {
          set({ error: `发起 SOS 失败：${errText(e)}` });
          return null;
        }
      },

      /** 自动发现当前活跃事件：存在则订阅，不存在则置 discovery=none。 */
      autoDiscoverEvent: async () => {
        if (get().currentEventId !== null) return; // 已订阅事件，无需再发现
        try {
          const res = await getActiveEvent();
          if (res.event) {
            await get().attachEvent(res.event.id);
          } else {
            set({ discovery: "none", error: null });
          }
        } catch (e) {
          set({ error: `自动发现事件失败：${errText(e)}` });
        }
      },

      /** 脱离当前事件（演示重置后）：清空事件数据并让 WS 忘记订阅。 */
      detachEvent: () => {
        socketOrNull()?.unsubscribe();
        set({
          event: null,
          timeline: [],
          health: [],
          lastVersion: 0,
          currentEventId: null,
          discovery: "idle",
          error: null,
        });
      },

      submitAction: async (action, metadata = {}) => {
        const eventId = get().currentEventId;
        if (eventId === null) return;
        set({ submitting: true, error: null });
        try {
          const res = await apiSubmitAction(eventId, action, metadata);
          if (res.applied && res.event) {
            // 服务端权威结果直接替换（含可用动作/分配）
            set((s) => ({
              event: res.event!,
              lastVersion: Math.max(s.lastVersion, res.event!.seq),
            }));
          } else if (res.duplicate) {
            set({ error: "该操作已提交过（幂等），无需重复操作" });
          } else {
            set({ error: res.reason || "操作被拒绝" });
          }
        } catch (e) {
          set({ error: `提交失败：${errText(e)}` });
        } finally {
          set({ submitting: false });
        }
      },

      handleWsMessage: (msg) => {
        const state = get();
        switch (msg.type) {
          case "PONG":
            return;
          case "ERROR": {
            const d = msg.data as { message?: string };
            set({ error: d.message || "WebSocket 服务端错误" });
            return;
          }
          case "PING":
            // 服务端心跳，无需回包（回包会被当作未知类型）
            return;
          case "TIMER_SYNC": {
            const d = msg.data as unknown as WsTimerSyncData;
            if (d.started_at && state.event) {
              set({
                event: { ...state.event, started_at: d.started_at },
              });
            }
            return;
          }
          case "EVENT_SNAPSHOT":
          case "EVENT_UPDATE": {
            const version = msg.version ?? 0;
            if (version < state.lastVersion) return; // 旧消息 → 丢弃，防回退
            const data = msg.data as Partial<EventData>;
            set((s) => ({
              lastVersion: Math.max(s.lastVersion, version),
              event: mergeEvent(s.event, data),
            }));
            return;
          }
          case "TRANSITION_ADDED": {
            const d = msg.data as WsTransitionAddedData;
            const version = msg.version ?? 0;
            if (version < state.lastVersion) return;
            const incoming: Transition[] = d.transitions ?? (d.transition ? [d.transition] : []);
            if (d.available_actions && state.event) {
              set({ event: { ...state.event, available_actions: d.available_actions! } });
            }
            set((s) => ({
              lastVersion: Math.max(s.lastVersion, version),
              timeline: mergeTimeline(s.timeline, incoming),
            }));
            return;
          }
          case "ASSIGNMENT_UPDATE": {
            const d = msg.data as unknown as WsAssignmentUpdateData;
            set((s) => ({
              event: s.event ? { ...s.event, assignments: d.assignments } : s.event,
            }));
            return;
          }
          case "HEALTH_READING": {
            const d = msg.data as unknown as WsHealthReadingData;
            set((s) => ({
              health: [...s.health.filter((h) => h.id !== d.reading.id), d.reading],
            }));
            return;
          }
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: "lifereflex-store",
      partialize: (s) => ({
        token: s.token,
        role: s.role,
        username: s.username,
        userId: s.userId,
        currentEventId: s.currentEventId,
      }),
    },
  ),
);

/** 供组件读取本地共享的事件编号（演示：同一浏览器多标签联动）。 */
export function readLastEventId(): number | null {
  try {
    const v = localStorage.getItem(LAST_EVENT_KEY);
    return v ? Number(v) : null;
  } catch {
    return null;
  }
}
