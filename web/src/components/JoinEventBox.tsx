import { useState } from "react";
import { readLastEventId, useStore } from "../lib/store";

/** 加入事件：输入事件编号（演示：同一浏览器患者端触发后自动填入）。 */
export default function JoinEventBox() {
  const attachEvent = useStore((s) => s.attachEvent);
  const error = useStore((s) => s.error);
  const [value, setValue] = useState(() => {
    const last = readLastEventId();
    return last ? String(last) : "";
  });
  const [busy, setBusy] = useState(false);

  const join = async () => {
    const id = Number(value);
    if (!Number.isInteger(id) || id <= 0) return;
    setBusy(true);
    try {
      await attachEvent(id);
    } catch {
      /* 错误已写入 store */
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="card" style={{ width: "100%" }}>
      <h4 className="card-title">加入救援事件</h4>
      <div className="join-box">
        <input
          inputMode="numeric"
          placeholder="事件编号 #"
          value={value}
          onChange={(e) => setValue(e.target.value)}
        />
        <button
          className="action-btn primary small"
          onClick={() => void join()}
          disabled={busy || value.trim() === ""}
        >
          {busy ? <span className="spin" /> : "加入"}
        </button>
      </div>
      {error && <div className="text-faint" style={{ fontSize: 12, marginTop: 8 }}>{error}</div>}
    </div>
  );
}
