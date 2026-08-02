import ResponderFlowPage from "./ResponderFlowPage";

const GUIDE_CFG = {
  role: "GUIDE" as const,
  roleName: "环境清障",
  standbyTitle: "等待任务分派",
  standbySub: "您将被匹配为环境清障（GUIDE）",
  variant: {
    RESPONSE_CONFIRMED: "primary" as const,
    AMBULANCE_ARRIVED: "amber" as const,
    HANDOVER_COMPLETED: "primary" as const,
  },
  waiting: (status: string) => {
    if (status === "HANDOVER")
      return { title: "交接中", sub: "等待调度系统归档事件" };
    if (status === "ARCHIVED")
      return { title: "事件已归档", sub: "本次清障任务完成" };
    return { title: "清障完毕", sub: "已为救护车打通通道" };
  },
};

/** 环境清障端（GUIDE）：确认响应 → 救护车到场 → 完成交接。 */
export default function GuidePage() {
  return <ResponderFlowPage cfg={GUIDE_CFG} />;
}
