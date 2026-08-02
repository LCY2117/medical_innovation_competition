/** 角色展示元信息（无 emoji，纯文字/字母，深色科技风）。 */
import type { Role } from "./types";

export interface RoleMeta {
  label: string;
  short: string;
  desc: string;
  mark: string;
}

export const ROLE_META: Record<Role, RoleMeta> = {
  PATIENT: { label: "患者端", short: "患者", desc: "一键 SOS · 救援进度", mark: "SOS" },
  PRIME: { label: "核心施救端", short: "核心施救", desc: "CPR · AED · 除颤", mark: "CPR" },
  RUNNER: { label: "AED 保障端", short: "AED保障", desc: "取送 AED", mark: "AED" },
  GUIDE: { label: "环境清障端", short: "环境清障", desc: "清障 · 引导救护车", mark: "引" },
  SYSTEM: { label: "调度系统", short: "调度", desc: "自动分派 · 归档", mark: "SY" },
  ADMIN: { label: "管理员", short: "管理", desc: "系统控制台", mark: "AD" },
};

/** 动作 → 补充说明（渲染在主按钮下）。 */
export const ACTION_HINTS: Record<string, string> = {
  SOS_TRIGGERED: "向全体响应单元发出求救",
  RESPONSE_CONFIRMED: "确认响应，即刻赶赴现场",
  CPR_STARTED: "110 BPM 节拍器引导按压",
  AED_PICKED: "已取得 AED，携带赶赴现场",
  AED_DELIVERED: "AED 已交到核心施救手中",
  AED_ANALYSIS_STARTED: "远离患者，AED 自动分析心律",
  AED_SHOCK_DELIVERED: "确认无人接触，按下放电",
  AMBULANCE_ARRIVED: "引导救护车到位",
  HANDOVER_COMPLETED: "将患者交接给急救人员",
  ARCHIVE: "归档事件并生成证据包",
};
