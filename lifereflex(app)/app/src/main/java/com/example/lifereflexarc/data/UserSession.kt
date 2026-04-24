package com.example.lifereflexarc.data

enum class UserRole(
    val label: String,
    val subtitle: String,
    val backendRole: String? = null,
) {
    PATIENT(
        label = "患者侧",
        subtitle = "处于重点监测或被触发为患者终端",
        backendRole = null,
    ),
    PRIME(
        label = "核心施救",
        subtitle = "负责 CPR 与首轮现场处置",
        backendRole = "PRIME",
    ),
    RUNNER(
        label = "AED 保障",
        subtitle = "负责取送 AED 与设备链路",
        backendRole = "RUNNER",
    ),
    GUIDE(
        label = "环境清障",
        subtitle = "负责通道协调与救护车接驳",
        backendRole = "GUIDE",
    ),
}

enum class HealthCondition(
    val label: String,
    val subtitle: String,
    val isPatientCandidate: Boolean,
) {
    GENERAL(
        label = "身体状态一般",
        subtitle = "日常活动正常，无明显急症风险",
        isPatientCandidate = false,
    ),
    ATHLETIC(
        label = "身体素质良好",
        subtitle = "行动能力较强，可快速奔跑和搬运",
        isPatientCandidate = false,
    ),
    CARDIAC_RISK(
        label = "存在心脏骤停风险",
        subtitle = "既往心血管病史，需要重点监测",
        isPatientCandidate = true,
    ),
    LIMITED_MOBILITY(
        label = "体能受限",
        subtitle = "不适合高强度奔跑，但可参与信息协同",
        isPatientCandidate = false,
    ),
}

enum class ProfessionIdentity(
    val label: String,
    val subtitle: String,
    val credentialStatus: String,
) {
    EMERGENCY_DOCTOR(
        label = "医生 / 专业急救人员",
        subtitle = "具备规范急救技能，可承担核心施救",
        credentialStatus = "高可信急救资质",
    ),
    TRAINED_RESPONDER(
        label = "系统培训过的急救者",
        subtitle = "接受过 CPR / AED 培训，可辅助施救",
        credentialStatus = "具备基础急救能力",
    ),
    BASIC_KNOWLEDGE(
        label = "有一定急救常识",
        subtitle = "理解急救流程，可执行明确指令",
        credentialStatus = "具备执行型协助能力",
    ),
    LIMITED_EXPERIENCE(
        label = "对急救不太熟悉",
        subtitle = "适合执行简单、低门槛的协助任务",
        credentialStatus = "适合低门槛支援任务",
    ),
    SECURITY_COORDINATOR(
        label = "安保 / 物业 / 场地协调人员",
        subtitle = "熟悉现场通道与人员调度，可承担引导清障",
        credentialStatus = "适合环境协调与接驳",
    ),
}

data class UserPreset(
    val key: String,
    val title: String,
    val description: String,
    val healthCondition: HealthCondition,
    val professionIdentity: ProfessionIdentity,
    val organization: String,
    val bio: String,
)

val DefaultUserPresets = listOf(
    UserPreset(
        key = "athlete",
        title = "体育生",
        description = "身体素质好，跑得快，适合快速取送设备",
        healthCondition = HealthCondition.ATHLETIC,
        professionIdentity = ProfessionIdentity.BASIC_KNOWLEDGE,
        organization = "高校运动场 / 校园",
        bio = "体育生，身体素质良好，跑得快，熟悉校园路线，能快速往返取送 AED。",
    ),
    UserPreset(
        key = "cardiac-risk",
        title = "冠心病患者",
        description = "存在一定心脏骤停风险，需要重点监测",
        healthCondition = HealthCondition.CARDIAC_RISK,
        professionIdentity = ProfessionIdentity.LIMITED_EXPERIENCE,
        organization = "社区 / 家庭场景",
        bio = "多年冠心病病史，有一定心脏骤停风险，需要重点监测，突发时更适合作为患者侧终端。",
    ),
    UserPreset(
        key = "doctor",
        title = "急救科医生",
        description = "具备专业急救资质，可承担核心施救",
        healthCondition = HealthCondition.GENERAL,
        professionIdentity = ProfessionIdentity.EMERGENCY_DOCTOR,
        organization = "市医院急救科",
        bio = "市医院急救科医生，熟悉心脏骤停处置流程，可执行高质量 CPR 与现场判断。",
    ),
    UserPreset(
        key = "security",
        title = "社区安保",
        description = "熟悉场地与交通组织，适合清障接驳",
        healthCondition = HealthCondition.GENERAL,
        professionIdentity = ProfessionIdentity.SECURITY_COORDINATOR,
        organization = "小区 / 社区物业",
        bio = "小区或社区安保人员，熟悉楼栋与出入口，能协调人员流线、电梯和救护车接驳。",
    ),
)

data class UserSession(
    val isLoggedIn: Boolean = false,
    val userId: String = "",
    val authToken: String = "",
    val displayName: String = "",
    val phone: String = "",
    val organization: String = "",
    val healthCondition: HealthCondition = HealthCondition.GENERAL,
    val professionIdentity: ProfessionIdentity = ProfessionIdentity.BASIC_KNOWLEDGE,
    val bio: String = "",
    val credentialStatus: String = "未认证",
) {
    val isPatientCandidate: Boolean
        get() = healthCondition.isPatientCandidate

    val profileLabel: String
        get() = if (isPatientCandidate) "重点监护对象" else "可调度协同成员"

    val profileSummary: String
        get() = "${healthCondition.label} · ${professionIdentity.label}"

    val dispatchNarrative: String
        get() = buildString {
            append("身体状态：")
            append(healthCondition.label)
            append("；职业身份：")
            append(professionIdentity.label)
            append("；组织场景：")
            append(if (organization.isBlank()) "未填写" else organization)
            append("；个人介绍：")
            append(if (bio.isBlank()) "未填写" else bio)
        }
}

data class IncidentArchiveEntry(
    val incidentId: String,
    val userId: String,
    val title: String,
    val summary: String,
    val roleLabel: String,
    val phaseLabel: String,
    val dispatchSource: String,
    val isPatient: Boolean,
    val startedAt: Long,
    val endedAt: Long,
    val durationSec: Long,
)
