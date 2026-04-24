@file:OptIn(androidx.compose.foundation.layout.ExperimentalLayoutApi::class)

package com.example.lifereflexarc.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.lifereflexarc.data.IncidentState
import com.example.lifereflexarc.data.UserRole
import com.example.lifereflexarc.data.UserSession
import com.example.lifereflexarc.ui.accentForRole
import com.example.lifereflexarc.ui.primeVoiceCue
import com.example.lifereflexarc.ui.phaseBody
import com.example.lifereflexarc.ui.phaseHeadline
import com.example.lifereflexarc.ui.phaseTitle
import com.example.lifereflexarc.ui.roleStatusLabel
import com.example.lifereflexarc.ui.rememberCountdownValue
import com.example.lifereflexarc.ui.components.EmptyStateCard
import com.example.lifereflexarc.ui.components.PressableButton
import com.example.lifereflexarc.ui.components.StatChip
import com.example.lifereflexarc.ui.components.StatusTag
import com.example.lifereflexarc.ui.theme.PhoneColors
import com.example.lifereflexarc.viewmodel.IncidentViewModel

@Composable
fun IncidentHeaderCard(
    incidentState: IncidentState,
    assignedRole: UserRole,
) {
    Card(
        colors = CardDefaults.cardColors(containerColor = accentForRole(assignedRole).copy(alpha = 0.12f)),
        shape = RoundedCornerShape(28.dp),
        border = BorderStroke(1.dp, accentForRole(assignedRole).copy(alpha = 0.45f)),
    ) {
        Column(modifier = Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
            StatusTag(
                text = phaseTitle(incidentState.phase),
                background = accentForRole(assignedRole).copy(alpha = 0.18f),
                foreground = accentForRole(assignedRole),
            )
            Text(
                text = phaseHeadline(incidentState.phase),
                color = Color.White,
                fontSize = 22.sp,
                fontWeight = FontWeight.Bold,
            )
            Text(
                text = phaseBody(incidentState.phase),
                color = PhoneColors.GrayText,
                fontSize = 14.sp,
                lineHeight = 22.sp,
            )
            FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                StatChip("核心施救", roleStatusLabel(incidentState.roles.PRIME.status), PhoneColors.Red)
                StatChip("AED保障", roleStatusLabel(incidentState.roles.RUNNER.status), PhoneColors.Blue)
                StatChip("环境清障", roleStatusLabel(incidentState.roles.GUIDE.status), PhoneColors.Yellow)
            }
        }
    }
}

@Composable
fun ResponderStatusCard(incidentState: IncidentState) {
    Card(
        colors = CardDefaults.cardColors(containerColor = Color(0xFF0F172A)),
        shape = RoundedCornerShape(24.dp),
        border = BorderStroke(1.dp, Color(0xFF1E293B)),
    ) {
        Column(modifier = Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Text("协同角色", color = Color.White, fontSize = 18.sp, fontWeight = FontWeight.SemiBold)
            RoleStatusStrip("核心施救", incidentState.roles.PRIME.status ?: "待命", PhoneColors.Red)
            RoleStatusStrip("AED保障", incidentState.roles.RUNNER.status ?: "待命", PhoneColors.Blue)
            RoleStatusStrip("环境清障", incidentState.roles.GUIDE.status ?: "待命", PhoneColors.Yellow)
        }
    }
}

@Composable
private fun RoleStatusStrip(
    role: String,
    status: String,
    accent: Color,
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Box(
                modifier = Modifier
                    .size(10.dp)
                    .clip(CircleShape)
                    .background(accent)
            )
            androidx.compose.foundation.layout.Spacer(modifier = Modifier.size(8.dp))
            Text(role, color = Color.White, fontWeight = FontWeight.Medium)
        }
        StatusTag(
            text = roleStatusLabel(status),
            background = accent.copy(alpha = 0.12f),
            foreground = accent,
        )
    }
}

@Composable
fun MissionPanel(
    session: UserSession,
    incidentState: IncidentState,
    assignedRole: UserRole?,
    deviceUserId: String,
    incidentViewModel: IncidentViewModel,
) {
    val activeRole = assignedRole

    when {
        incidentState.phase == "HANDOVER" -> HandoverMissionCard()
        incidentState.phase == "CREATED" -> CreatedMissionCard(
            incidentState = incidentState,
            onStartSos = incidentViewModel::sosStart,
            onCancelSos = incidentViewModel::sosCancel,
        )
        incidentState.phase == "DISPATCHING" -> DispatchingMissionCard()
        activeRole == UserRole.PRIME -> PrimeMissionCard(
            incidentState = incidentState,
            deviceUserId = deviceUserId,
            onJoin = { incidentViewModel.joinPrime(deviceUserId) },
            onStartCpr = { incidentViewModel.actionCprStarted(deviceUserId) },
        )
        activeRole == UserRole.RUNNER -> RunnerMissionCard(
            incidentState = incidentState,
            deviceUserId = deviceUserId,
            onJoin = { incidentViewModel.joinRunner(deviceUserId) },
            onPicked = { incidentViewModel.actionAedPicked(deviceUserId) },
            onDelivered = { incidentViewModel.actionAedDelivered(deviceUserId) },
        )
        activeRole == UserRole.GUIDE -> GuideMissionCard(
            incidentState = incidentState,
            deviceUserId = deviceUserId,
            onJoin = { incidentViewModel.joinGuide(deviceUserId) },
            onAmbulanceArrived = { incidentViewModel.actionAmbulanceArrived(deviceUserId) },
        )
        else -> ObserverMissionCard()
    }
}

@Composable
private fun CreatedMissionCard(
    incidentState: IncidentState,
    onStartSos: () -> Unit,
    onCancelSos: () -> Unit,
) {
    val countdown = rememberCountdownValue(incidentState.sos?.startTs, incidentState.sos?.durationSec)
    val isAlerting = incidentState.sos?.status == "ALERTING"
    Card(
        colors = CardDefaults.cardColors(containerColor = Color(0xFF0F172A)),
        shape = RoundedCornerShape(28.dp),
        border = BorderStroke(1.dp, Color(0xFF1E293B)),
    ) {
        Column(modifier = Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Text("监测与告警", color = Color.White, fontSize = 20.sp, fontWeight = FontWeight.Bold)
            Text(
                text = if (isAlerting) {
                    "检测到异常倒地，系统正在执行 SOS 倒计时。"
                } else {
                    "当前处于监测态，可手动确认异常并发起急救接力。"
                },
                color = PhoneColors.GrayText,
                fontSize = 14.sp,
                lineHeight = 22.sp,
            )
            Card(
                colors = CardDefaults.cardColors(containerColor = if (isAlerting) Color(0xFF3F1D1D) else Color(0xFF111C34)),
                shape = RoundedCornerShape(22.dp),
            ) {
                Column(modifier = Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text(if (isAlerting) "SOS 告警" else "健康守护", color = if (isAlerting) PhoneColors.RedSoft else PhoneColors.GreenSoft)
                    Text(
                        text = if (isAlerting) countdown.toString().padStart(2, '0') else "86 BPM",
                        color = Color.White,
                        fontSize = 30.sp,
                        fontWeight = FontWeight.Black,
                    )
                }
            }
            PressableButton(
                text = if (isAlerting) "我没事，取消告警" else "确认异常，开始倒计时",
                onClick = if (isAlerting) onCancelSos else onStartSos,
                colors = ButtonDefaults.buttonColors(
                    containerColor = if (isAlerting) Color(0xFF334155) else PhoneColors.Red,
                    contentColor = Color.White,
                ),
                modifier = Modifier.fillMaxWidth(),
            )
        }
    }
}

@Composable
private fun PrimeMissionCard(
    incidentState: IncidentState,
    deviceUserId: String,
    onJoin: () -> Unit,
    onStartCpr: () -> Unit,
) {
    val status = incidentState.roles.PRIME.status
    val title: String
    val body: String
    val cta: String?
    val action: (() -> Unit)?
    val voiceCue = primeVoiceCue(incidentState)

    when {
        status.isNullOrBlank() || status == "IDLE" -> {
            title = "等待 AI 分配"
            body = "当前终端尚未被分配到核心施救任务。"
            cta = null
            action = null
        }
        status == "ASSIGNED" || status == "JOINED" -> {
            title = "核心施救任务已派发"
            body = "你是现场核心施救者，立即前往患者位置并开始胸外按压。"
            cta = if (status == "ASSIGNED") "确认到场并启动 CPR" else "启动 CPR"
            action = onStartCpr
        }
        else -> {
            title = "CPR 执行中"
            body = "保持 100-120 次/分钟节律，等待 AED 与急救车汇合。"
            cta = null
            action = null
        }
    }

    MissionActionCard(
        title = title,
        body = body,
        accent = PhoneColors.Red,
        status = "核心施救 · ${roleStatusLabel(status)} · ${deviceUserId.takeLast(4)}",
        cta = cta,
        onAction = action,
    ) {
        if (voiceCue != null) {
            VoiceCueCard(message = voiceCue)
        }
    }
}

@Composable
private fun RunnerMissionCard(
    incidentState: IncidentState,
    deviceUserId: String,
    onJoin: () -> Unit,
    onPicked: () -> Unit,
    onDelivered: () -> Unit,
) {
    val status = incidentState.roles.RUNNER.status
    val title: String
    val body: String
    val cta: String?
    val action: (() -> Unit)?

    when (status) {
        null, "", "IDLE" -> {
            title = "等待 AI 分配"
            body = "当前终端尚未被分配到 AED 保障任务。"
            cta = null
            action = null
        }
        "ASSIGNED", "JOINED" -> {
            title = "前往 AED 点位"
            body = "系统已锁定最近 AED，拿到设备后立即回返患者位置。"
            cta = "确认已取到 AED"
            action = onPicked
        }
        "AED_PICKED" -> {
            title = "回送患者位置"
            body = "继续赶往现场，与核心施救者汇合。"
            cta = "确认 AED 已送达"
            action = onDelivered
        }
        else -> {
            title = "AED 已完成交付"
            body = "设备已到场，保持通信畅通，等待进一步调度。"
            cta = null
            action = null
        }
    }

    MissionActionCard(
        title = title,
        body = body,
        accent = PhoneColors.Blue,
        status = "AED保障 · ${roleStatusLabel(status)} · ${deviceUserId.takeLast(4)}",
        cta = cta,
        onAction = action,
    )
}

@Composable
private fun GuideMissionCard(
    incidentState: IncidentState,
    deviceUserId: String,
    onJoin: () -> Unit,
    onAmbulanceArrived: () -> Unit,
) {
    val status = incidentState.roles.GUIDE.status
    val title: String
    val body: String
    val cta: String?
    val action: (() -> Unit)?

    when (status) {
        null, "", "IDLE" -> {
            title = "等待 AI 分配"
            body = "当前终端尚未被分配到环境清障任务。"
            cta = null
            action = null
        }
        "ASSIGNED", "JOINED" -> {
            title = "生命通道处理中"
            body = "请疏通消防通道、引导电梯与路口，等待急救车靠近。"
            cta = "确认救护车已到达"
            action = onAmbulanceArrived
        }
        else -> {
            title = "接驳完成"
            body = "救护车已抵达现场，后续进入交接归档阶段。"
            cta = null
            action = null
        }
    }

    MissionActionCard(
        title = title,
        body = body,
        accent = PhoneColors.Yellow,
        status = "环境清障 · ${roleStatusLabel(status)} · ${deviceUserId.takeLast(4)}",
        cta = cta,
        onAction = action,
    )
}

@Composable
private fun DispatchingMissionCard() {
    EmptyStateCard(
        title = "AI 正在生成任务分配",
        body = "患者终端已经被网页指挥台触发。所有在线终端会先收到全屏红色告警，约 3 秒后进入各自专属任务页。",
    )
}

@Composable
private fun ObserverMissionCard() {
    EmptyStateCard(
        title = "当前为观察视角",
        body = "你现在没有可执行的角色动作，但仍可以查看实时日志与阶段推进。",
    )
}

@Composable
private fun HandoverMissionCard() {
    EmptyStateCard(
        title = "进入交接阶段",
        body = "现场任务已转入 HANDOVER，可前往归档页查看汇总与后续交接。",
    )
}

@Composable
private fun MissionActionCard(
    title: String,
    body: String,
    accent: Color,
    status: String,
    cta: String?,
    onAction: (() -> Unit)?,
    extraContent: @Composable () -> Unit = {},
) {
    Card(
        colors = CardDefaults.cardColors(containerColor = Color(0xFF0F172A)),
        shape = RoundedCornerShape(28.dp),
        border = BorderStroke(1.dp, accent.copy(alpha = 0.35f)),
    ) {
        Column(modifier = Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
            StatusTag(
                text = status,
                background = accent.copy(alpha = 0.12f),
                foreground = accent,
            )
            Text(title, color = Color.White, fontSize = 20.sp, fontWeight = FontWeight.Bold)
            Text(body, color = PhoneColors.GrayText, fontSize = 14.sp, lineHeight = 22.sp)
            if (cta != null && onAction != null) {
                PressableButton(
                    text = cta,
                    onClick = onAction,
                    colors = ButtonDefaults.buttonColors(containerColor = accent, contentColor = Color.White),
                    modifier = Modifier.fillMaxWidth(),
                )
            }
            extraContent()
        }
    }
}

@Composable
private fun VoiceCueCard(message: String) {
    Card(
        colors = CardDefaults.cardColors(containerColor = Color(0xFF111827)),
        shape = RoundedCornerShape(20.dp),
        border = BorderStroke(1.dp, PhoneColors.Red.copy(alpha = 0.35f)),
    ) {
        Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Text("语音提示", color = PhoneColors.RedSoft, fontSize = 12.sp, fontWeight = FontWeight.SemiBold)
            Text(message, color = Color.White, fontSize = 14.sp, lineHeight = 21.sp)
        }
    }
}
