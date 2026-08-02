import { useNow } from "../lib/hooks";

interface Props {
  /** 起点时间（ISO 字符串或毫秒时间戳）。 */
  startedAt: string | number | null;
  /** 黄金时间窗口（秒）。 */
  windowSec?: number;
}

function pad(n: number): string {
  return String(n).padStart(2, "0");
}

/** 后端返回 naive UTC 时间（无时区后缀），统一按 UTC 解析，避免本地时区偏移。 */
export function parseServerTime(iso: string): number {
  const normalized = /(Z|[+-]\d{2}:?\d{2})$/i.test(iso) ? iso : `${iso}Z`;
  const t = Date.parse(normalized);
  return Number.isNaN(t) ? 0 : t;
}

/** 黄金时间倒计时：从 started_at 起倒计时 windowSec 秒。 */
export default function Countdown({ startedAt, windowSec = 240 }: Props) {
  const now = useNow(Boolean(startedAt));

  let base = 0;
  if (startedAt !== null && startedAt !== undefined) {
    base = typeof startedAt === "string" ? parseServerTime(startedAt) : startedAt;
  }
  const elapsed = Math.max(0, (now - base) / 1000);
  const remain = Math.max(0, windowSec - elapsed);
  const expired = base > 0 && elapsed >= windowSec;

  const mm = pad(Math.floor(remain / 60));
  const ss = pad(Math.floor(remain % 60));

  return (
    <div className="countdown card">
      <div className={`countdown-value ${expired ? "red" : ""}`}>
        {expired ? "00:00" : `${mm}:${ss}`}
      </div>
      <div className="countdown-label">
        {expired ? "黄金 4 分钟已过" : "黄金时间剩余"}
      </div>
      <div className="kv" style={{ marginTop: 8 }}>
        <span className="k">已耗时</span>
        <span className="v glow-num">
          {pad(Math.floor(elapsed / 60))}:{pad(Math.floor(elapsed % 60))}
        </span>
      </div>
    </div>
  );
}
