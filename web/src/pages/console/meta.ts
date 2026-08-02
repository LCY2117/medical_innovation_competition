/** 大屏共享元信息：动作标签 / 阶段严重度 / 格式化工具。 */

export const ACTION_LABELS: Record<string, string> = {
  SOS_TRIGGERED: "发起SOS",
  RESPONSE_CONFIRMED: "确认响应",
  DISPATCH: "系统分派",
  CPR_STARTED: "开始CPR",
  AED_PICKED: "已取AED",
  AED_DELIVERED: "AED已送达",
  AED_ANALYSIS_STARTED: "开始AED分析",
  AED_SHOCK_DELIVERED: "实施除颤",
  AMBULANCE_ARRIVED: "救护车到场",
  HANDOVER_COMPLETED: "完成交接",
  ARCHIVE: "归档事件",
};

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

/** 阶段严重度：warn=危急 / amber=待办 / ok=正常。 */
export function stageSeverity(status: string): "warn" | "amber" | "ok" {
  switch (status) {
    case "SOS":
    case "CPR":
    case "AED_ANALYZING":
    case "SHOCK_DELIVERED":
      return "warn";
    case "DISPATCHED":
    case "AED_PICKED":
    case "AED_DELIVERED":
    case "HANDOVER":
      return "amber";
    default:
      return "ok";
  }
}

export function pad(n: number): string {
  return String(n).padStart(2, "0");
}

export function fmtClock(iso: string | null): string {
  if (!iso) return "--:--:--";
  const d = new Date(iso.endsWith("Z") || /[+-]\d{2}:?\d{2}$/.test(iso) ? iso : `${iso}Z`);
  if (Number.isNaN(d.getTime())) return "--:--:--";
  return `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
}
