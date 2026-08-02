/** WebSocket 封装：断线指数退避重连 + 心跳保活 + 订阅事件。 */

export type WsStatus = "connecting" | "connected" | "reconnecting" | "closed";

interface Options {
  token: string;
  /** 收到任意服务端消息（已 JSON 解析）。 */
  onMessage: (msg: import("./types").WsMessage) => void;
  onStatus: (status: WsStatus) => void;
  /** 心跳间隔（毫秒），默认 20s（服务端每 30s 也主动 PING）。 */
  heartbeatInterval?: number;
}

/** 指数退避：1s → 2s → 4s → ... → 封顶 30s。 */
const BACKOFF_BASE = 1000;
const BACKOFF_MAX = 30000;

export class EventSocket {
  private ws: WebSocket | null = null;
  private token: string;
  private onMessage: Options["onMessage"];
  private onStatus: Options["onStatus"];
  private heartbeatMs: number;
  private eventId: number | null = null;

  private reconnectAttempt = 0;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private heartbeatTimer: ReturnType<typeof setInterval> | null = null;
  private alive = false;
  private closedByUser = false;

  constructor(opts: Options) {
    this.token = opts.token;
    this.onMessage = opts.onMessage;
    this.onStatus = opts.onStatus;
    this.heartbeatMs = opts.heartbeatInterval ?? 20_000;
  }

  /** 生成 WS 地址（开发经 Vite /ws 代理；生产同源反代）。 */
  private url(): string {
    const proto = window.location.protocol === "https:" ? "wss" : "ws";
    const query = new URLSearchParams({ token: this.token });
    return `${proto}://${window.location.host}/ws/events?${query.toString()}`;
  }

  connect(): void {
    this.closedByUser = false;
    this.status("connecting");
    try {
      this.ws = new WebSocket(this.url());
    } catch {
      this.scheduleReconnect();
      return;
    }

    this.ws.onopen = () => {
      this.reconnectAttempt = 0;
      this.alive = true;
      this.status("connected");
      // 若已有关注的事件，重连成功后重新订阅（服务端会回发快照）。
      if (this.eventId !== null) {
        this.send({ type: "SUBSCRIBE_EVENT", data: { event_id: this.eventId } });
      }
      this.startHeartbeat();
    };

    this.ws.onmessage = (ev) => {
      this.alive = true;
      let msg: import("./types").WsMessage;
      try {
        msg = JSON.parse(String(ev.data)) as import("./types").WsMessage;
      } catch {
        return;
      }
      this.onMessage(msg);
    };

    this.ws.onclose = () => {
      this.stopHeartbeat();
      if (!this.closedByUser) {
        this.status("reconnecting");
        this.scheduleReconnect();
      } else {
        this.status("closed");
      }
    };

    this.ws.onerror = () => {
      // onclose 随后触发并处理重连
    };
  }

  /** 订阅事件：服务端回发 EVENT_SNAPSHOT + 时间线 + TIMER_SYNC。 */
  subscribe(eventId: number): void {
    this.eventId = eventId;
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.send({ type: "SUBSCRIBE_EVENT", data: { event_id: eventId } });
    }
  }

  /** 忘记当前订阅（事件被重置/删除后调用，避免重连时订阅已失效事件）。 */
  unsubscribe(): void {
    this.eventId = null;
  }

  send(payload: Record<string, unknown>): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(payload));
    }
  }

  close(): void {
    this.closedByUser = true;
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.reconnectTimer = null;
    this.stopHeartbeat();
    if (this.ws) {
      this.ws.onclose = null;
      this.ws.onmessage = null;
      this.ws.close();
      this.ws = null;
    }
    this.status("closed");
  }

  // ---------- 内部 ----------

  private scheduleReconnect(): void {
    if (this.closedByUser) return;
    const delay = Math.min(
      BACKOFF_BASE * 2 ** this.reconnectAttempt,
      BACKOFF_MAX,
    );
    this.reconnectAttempt += 1;
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.reconnectTimer = setTimeout(() => this.connect(), delay);
  }

  private startHeartbeat(): void {
    this.stopHeartbeat();
    this.heartbeatTimer = setInterval(() => {
      // 服务端心跳循环（PING）期间若本地未确认过存续，则认为连接可能失效
      if (!this.alive) {
        // 直接断开以触发 onclose → 指数退避重连
        try {
          this.ws?.close();
        } catch {
          /* ignore */
        }
        return;
      }
      this.alive = false;
      this.send({ type: "PING" });
    }, this.heartbeatMs);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatTimer) clearInterval(this.heartbeatTimer);
    this.heartbeatTimer = null;
  }

  private status(s: WsStatus): void {
    this.onStatus(s);
  }
}
