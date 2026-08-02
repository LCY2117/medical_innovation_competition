import JoinEventBox from "./JoinEventBox";
import { useStore } from "../lib/store";

interface Props {
  title?: string;
  sub?: string;
}

/** 响应端待命：无事件时显示等待分派 + 加入事件入口。
 *
 * 活跃事件自动发现（M2 体验修复）：登录后自动查询 /events/active；
 * 发现活跃事件则自动订阅并进入流程；无则提示"暂无进行中事件"
 * （保留手动加入作为兜底）。
 */
export default function ResponderStandby({
  title = "等待任务分派",
  sub = "系统分派引擎将在 SOS 后自动匹配",
}: Props) {
  const discovery = useStore((s) => s.discovery);
  const showNone = discovery === "none";

  return (
    <div className="standby">
      <div className="standby-ic">
        <span style={{ fontFamily: "var(--font-num)", fontWeight: 800, color: "var(--cyan)" }}>/ / /</span>
      </div>
      <div className="standby-title">{showNone ? "暂无进行中事件" : title}</div>
      <div className="standby-sub">
        {showNone ? "正在监听新事件，患者触发 SOS 后将自动接入…" : sub}
      </div>
      <JoinEventBox />
    </div>
  );
}
