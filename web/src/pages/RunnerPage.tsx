import ResponderFlowPage from "./ResponderFlowPage";

const RUNNER_CFG = {
  role: "RUNNER" as const,
  roleName: "AED保障",
  standbyTitle: "等待任务分派",
  standbySub: "您将被匹配为 AED 保障（RUNNER）",
  variant: {
    RESPONSE_CONFIRMED: "primary" as const,
    AED_PICKED: "primary" as const,
    AED_DELIVERED: "amber" as const,
  },
  waiting: (status: string) => {
    if (status === "AED_DELIVERED" || status === "AED_ANALYZING")
      return { title: "AED 已送达", sub: "已交给核心施救，现场待命" };
    if (status === "HANDOVER" || status === "ARCHIVED")
      return { title: status === "HANDOVER" ? "交接中" : "事件已归档", sub: "本次保障任务完成" };
    return { title: "等待分派", sub: "系统将按距离与 AED 点位匹配" };
  },
};

/** AED 保障端（RUNNER）：确认响应 → 取 AED → 送 AED。 */
export default function RunnerPage() {
  return <ResponderFlowPage cfg={RUNNER_CFG} />;
}
