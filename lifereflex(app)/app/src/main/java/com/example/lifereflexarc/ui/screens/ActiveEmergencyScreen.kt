package com.example.lifereflexarc.ui.screens

import android.speech.tts.TextToSpeech
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.produceState
import androidx.compose.runtime.remember
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.lifereflexarc.data.IncidentState
import com.example.lifereflexarc.data.UserRole
import com.example.lifereflexarc.data.UserSession
import com.example.lifereflexarc.ui.accentForRole
import com.example.lifereflexarc.ui.primeVoiceCue
import com.example.lifereflexarc.ui.components.PressableButton
import com.example.lifereflexarc.ui.phaseTitle
import com.example.lifereflexarc.ui.roleStatusLabel
import com.example.lifereflexarc.ui.rememberCountdownValue
import com.example.lifereflexarc.ui.rememberElapsedLabel
import com.example.lifereflexarc.ui.theme.PhoneColors
import com.example.lifereflexarc.viewmodel.IncidentViewModel
import kotlinx.coroutines.delay
import java.util.Locale

@Composable
fun ActiveEmergencyScreen(
    session: UserSession,
    incidentState: IncidentState,
    assignedRole: UserRole?,
    deviceUserId: String,
    incidentViewModel: IncidentViewModel,
    onExitEmergency: () -> Unit,
) {
    PrimeVoicePrompt(
        incidentState = incidentState,
        assignedRole = assignedRole,
        isPatient = incidentState.patientUserId == deviceUserId,
    )
    when {
        incidentState.phase == "ARCHIVED" -> ArchivedFullScreen(
            session = session,
            incidentState = incidentState,
            assignedRole = assignedRole,
            onExitEmergency = onExitEmergency,
        )
        incidentState.phase == "HANDOVER" -> HandoverFullScreen(
            incidentState = incidentState,
            userId = deviceUserId,
            incidentViewModel = incidentViewModel,
        )
        incidentState.phase == "DISPATCHING" -> DispatchingFullScreen(incidentState = incidentState)
        incidentState.patientUserId == deviceUserId -> PatientFullScreen(incidentState = incidentState)
        assignedRole == UserRole.PRIME -> PrimeFullScreen(
            incidentState = incidentState,
            userId = deviceUserId,
            incidentViewModel = incidentViewModel,
        )
        assignedRole == UserRole.RUNNER -> RunnerFullScreen(
            incidentState = incidentState,
            userId = deviceUserId,
            incidentViewModel = incidentViewModel,
        )
        assignedRole == UserRole.GUIDE -> GuideFullScreen(
            incidentState = incidentState,
            userId = deviceUserId,
            incidentViewModel = incidentViewModel,
        )
        else -> UnassignedFullScreen(session = session, incidentState = incidentState)
    }
}

@Composable
private fun PrimeVoicePrompt(
    incidentState: IncidentState,
    assignedRole: UserRole?,
    isPatient: Boolean,
) {
    if (assignedRole != UserRole.PRIME || isPatient) {
        return
    }
    val context = LocalContext.current
    var tts by remember { mutableStateOf<TextToSpeech?>(null) }
    var lastPromptKey by remember { mutableStateOf<String?>(null) }
    val prompt = primeVoiceCue(incidentState)?.let { cue ->
        val promptId = when (incidentState.phase) {
            "DISPATCHED" -> "dispatch"
            "AED_PICKED" -> "aed-picked"
            "AED_DELIVERED" -> "aed"
            "AED_ANALYZING" -> "analysis"
            "SHOCK_DELIVERED" -> "shock"
            "HANDOVER" -> "handover"
            else -> "cpr"
        }
        "$promptId|$cue"
    }

    DisposableEffect(context) {
        var engine: TextToSpeech? = null
        engine = TextToSpeech(context) { status ->
            if (status == TextToSpeech.SUCCESS) {
                engine?.language = Locale.CHINA
            }
        }
        tts = engine
        onDispose {
            engine?.stop()
            engine?.shutdown()
            tts = null
        }
    }

    LaunchedEffect(prompt, tts) {
        val engine = tts ?: return@LaunchedEffect
        val cue = prompt ?: return@LaunchedEffect
        if (cue == lastPromptKey) {
            return@LaunchedEffect
        }
        lastPromptKey = cue
        engine.speak(cue.substringAfter('|'), TextToSpeech.QUEUE_FLUSH, null, cue.substringBefore('|'))
    }
}

@Composable
private fun DispatchingFullScreen(
    incidentState: IncidentState,
) {
    val countdown = rememberCountdownValue(dispatchStartTs(incidentState), 3)
    CriticalScaffold(
        eyebrow = "心脏骤停警报",
        title = "心脏骤停告警已触发",
        body = "所有在线终端已收到覆盖全屏的红色告警。云端正在结合用户画像调用 AI 进行 PRIME、RUNNER、GUIDE 三类任务分配。",
        accent = PhoneColors.Red,
    ) {
        MetricTile(label = "AI 分配倒计时", value = "${countdown.coerceAtLeast(0)} 秒")
        MetricTile(label = "事件阶段", value = phaseTitle(incidentState.phase))
    }
}

@Composable
private fun PatientFullScreen(
    incidentState: IncidentState,
) {
    CriticalScaffold(
        eyebrow = "患者端",
        title = "已进入患者应急态",
        body = "系统已向周边协同成员发出求助，并同步生成急救任务。患者端保持当前位置，等待周边力量到场和救护车接管。",
        accent = PhoneColors.Red,
    ) {
        MetricTile(label = "当前阶段", value = phaseTitle(incidentState.phase))
        MetricTile(label = "已通知分配", value = incidentState.dispatchSource ?: "规则/AI 处理中")
        MetricTile(label = "事件耗时", value = rememberElapsedLabel(incidentState.logs.firstOrNull()?.ts))
    }
}

@Composable
private fun PrimeFullScreen(
    incidentState: IncidentState,
    userId: String,
    incidentViewModel: IncidentViewModel,
) {
    val status = incidentState.roles.PRIME.status
    val cprStarted = status == "CPR_STARTED"
    val aedDelivered = incidentState.roles.RUNNER.status == "AED_DELIVERED"
    val analyzing = status == "AED_ANALYZING"
    val shockDelivered = status == "AED_SHOCK_DELIVERED"
    val voiceCue = primeVoiceCue(incidentState)
    val cprStartTs = incidentState.logs.lastOrNull { it.msg.contains("CPR started", ignoreCase = true) }?.ts
    val shockStartTs = incidentState.logs.lastOrNull { it.msg.contains("AED shock delivered", ignoreCase = true) }?.ts
    val guidanceStartTs = when {
        shockDelivered -> shockStartTs
        cprStarted -> cprStartTs
        else -> null
    }
    CriticalScaffold(
        eyebrow = "核心施救任务",
        title = when {
            shockDelivered -> "已完成一次 AED 除颤"
            analyzing -> "AED 正在分析心律"
            aedDelivered -> "AED 已送达，立即执行贴片分析"
            cprStarted -> "保持基础复苏循环"
            else -> "你被分配为核心施救者"
        },
        body = when {
            shockDelivered -> "除颤完成后不要停顿，立刻恢复 30:2 基础复苏循环，并等待 2 分钟后再次由 AED 分析。"
            analyzing -> "按 AED 语音提示停止接触患者，确认周围安全后准备执行一次电击。"
            aedDelivered -> "请迅速贴附电极片，连接 AED，并按设备提示开始心律分析。"
            cprStarted -> "从胸外按压开始，按 30 次按压 + 2 次人工呼吸的节律持续复苏，AED 到场后仅在分析和除颤时短暂停止接触。"
            else -> "请第一时间触达患者，确认无意识且无正常呼吸后立即开始胸外按压。"
        },
        accent = accentForRole(UserRole.PRIME),
    ) {
        MetricTile(label = "任务状态", value = roleStatusLabel(status))
        MetricTile(label = "事件阶段", value = phaseTitle(incidentState.phase))
        MetricTile(label = "调度来源", value = incidentState.dispatchSource ?: "规则调度")
        if (voiceCue != null) {
            VoiceCueCard(message = voiceCue)
        }
        when {
            shockDelivered -> ResuscitationGuidancePanel(
                startTs = guidanceStartTs,
                aedReady = true,
                onRequestAnalysis = { incidentViewModel.actionAedAnalysisStarted(userId) },
            )
            analyzing -> PressableButton(
                text = "确认已完成一次电击除颤",
                onClick = { incidentViewModel.actionAedShockDelivered(userId) },
                colors = ButtonDefaults.buttonColors(containerColor = PhoneColors.Red, contentColor = Color.White),
                modifier = Modifier.fillMaxWidth(),
            )
            aedDelivered -> PressableButton(
                text = "开始 AED 心律分析",
                onClick = { incidentViewModel.actionAedAnalysisStarted(userId) },
                colors = ButtonDefaults.buttonColors(containerColor = PhoneColors.Red, contentColor = Color.White),
                modifier = Modifier.fillMaxWidth(),
            )
            !cprStarted -> {
            PressableButton(
                text = "确认到场并开始基础复苏",
                onClick = { incidentViewModel.actionCprStarted(userId) },
                colors = ButtonDefaults.buttonColors(containerColor = PhoneColors.Red, contentColor = Color.White),
                modifier = Modifier.fillMaxWidth(),
            )
            }
            else -> Unit
        }
        if (cprStarted && !analyzing) {
            ResuscitationGuidancePanel(
                startTs = guidanceStartTs,
                aedReady = aedDelivered || shockDelivered,
                onRequestAnalysis = if (shockDelivered) {
                    { incidentViewModel.actionAedAnalysisStarted(userId) }
                } else {
                    null
                },
            )
        }
    }
}

@Composable
private fun ResuscitationGuidancePanel(
    startTs: Long?,
    aedReady: Boolean,
    onRequestAnalysis: (() -> Unit)? = null,
) {
    val cycleElapsedSec by produceState(initialValue = 0, startTs) {
        if (startTs == null) {
            value = 0
            return@produceState
        }
        while (true) {
            value = ((System.currentTimeMillis() - startTs) / 1000L).toInt().coerceAtLeast(0)
            delay(500)
        }
    }
    val cycleTotalSec = 120
    val cycleRemaining = (cycleTotalSec - (cycleElapsedSec % cycleTotalSec)).coerceAtLeast(0)
    val blockElapsed = cycleElapsedSec % 20
    val isBreathing = blockElapsed >= 16
    val blockRemaining = if (isBreathing) 20 - blockElapsed else 16 - blockElapsed
    val guidanceTitle = if (isBreathing) "人工呼吸阶段" else "胸外按压阶段"
    val guidanceBody = if (isBreathing) {
        "保持气道开放，完成 2 次人工呼吸后立刻回到胸外按压。"
    } else {
        "保持 100-120 次/分钟按压频率，深度 5-6 厘米，尽量减少中断。"
    }

    MetricTile(label = "复苏循环剩余", value = "${cycleRemaining} 秒")
    MetricTile(label = "当前阶段", value = guidanceTitle)
    MetricTile(label = "阶段切换倒计时", value = "${blockRemaining.coerceAtLeast(0)} 秒")
    Card(
        colors = CardDefaults.cardColors(containerColor = Color(0xFF111827)),
        shape = RoundedCornerShape(20.dp),
        border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFF1F2937)),
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(18.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            Text(
                text = if (isBreathing) "2 次人工呼吸" else "30 次胸外按压",
                color = if (isBreathing) PhoneColors.Yellow else PhoneColors.Green,
                fontWeight = FontWeight.Bold,
                fontSize = 18.sp,
            )
            Text(
                text = guidanceBody,
                color = Color(0xFFCBD5E1),
                fontSize = 13.sp,
                lineHeight = 20.sp,
            )
            Text(
                text = if (aedReady) {
                    "AED 已在现场。仅在设备分析或除颤提示时暂停接触患者，其余时间持续复苏。"
                } else {
                    "AED 尚未到场。请持续执行 30:2 基础复苏循环，等待设备送达。"
                },
                color = PhoneColors.GrayText,
                fontSize = 12.sp,
                lineHeight = 18.sp,
            )
            if (aedReady && onRequestAnalysis != null) {
                if (cycleRemaining > 10) {
                    Text(
                        text = "本轮复苏结束后，AED 将再次进入心律分析。",
                        color = PhoneColors.GreenSoft,
                        fontSize = 12.sp,
                        lineHeight = 18.sp,
                    )
                } else {
                    PressableButton(
                        text = "开始第二轮 AED 心律分析",
                        onClick = onRequestAnalysis,
                        colors = ButtonDefaults.buttonColors(
                            containerColor = PhoneColors.Red,
                            contentColor = Color.White,
                        ),
                        modifier = Modifier.fillMaxWidth(),
                    )
                }
            }
        }
    }
}

@Composable
private fun VoiceCueCard(
    message: String,
) {
    Card(
        colors = CardDefaults.cardColors(containerColor = Color(0xFF132238)),
        shape = RoundedCornerShape(20.dp),
        border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFF1E40AF)),
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Text(
                text = "语音指引已开启",
                color = Color(0xFF93C5FD),
                fontWeight = FontWeight.Bold,
                fontSize = 14.sp,
            )
            Text(
                text = message,
                color = Color.White,
                fontSize = 13.sp,
                lineHeight = 20.sp,
            )
        }
    }
}

@Composable
private fun RunnerFullScreen(
    incidentState: IncidentState,
    userId: String,
    incidentViewModel: IncidentViewModel,
) {
    val status = incidentState.roles.RUNNER.status
    CriticalScaffold(
        eyebrow = "AED 保障任务",
        title = when (status) {
            "AED_PICKED" -> "AED 已取到，立即回送"
            "AED_DELIVERED" -> "AED 已完成送达"
            else -> "你被分配为 AED 保障者"
        },
        body = when (status) {
            "AED_PICKED" -> "沿最短路径回返患者位置，与 PRIME 汇合。"
            "AED_DELIVERED" -> "设备已送达现场，提醒 PRIME 贴附电极片并按 AED 语音提示分析与除颤。"
            else -> "立即前往最近 AED 点位，取到设备后第一时间返回现场。"
        },
        accent = accentForRole(UserRole.RUNNER),
    ) {
        MetricTile(label = "任务状态", value = roleStatusLabel(status))
        MetricTile(label = "事件阶段", value = phaseTitle(incidentState.phase))
        when (status) {
            "AED_PICKED" -> PressableButton(
                text = "确认 AED 已送达",
                onClick = { incidentViewModel.actionAedDelivered(userId) },
                colors = ButtonDefaults.buttonColors(containerColor = PhoneColors.Blue, contentColor = Color.White),
                modifier = Modifier.fillMaxWidth(),
            )
            "AED_DELIVERED" -> Unit
            else -> PressableButton(
                text = "确认已取到 AED",
                onClick = { incidentViewModel.actionAedPicked(userId) },
                colors = ButtonDefaults.buttonColors(containerColor = PhoneColors.Blue, contentColor = Color.White),
                modifier = Modifier.fillMaxWidth(),
            )
        }
    }
}

@Composable
private fun GuideFullScreen(
    incidentState: IncidentState,
    userId: String,
    incidentViewModel: IncidentViewModel,
) {
    val status = incidentState.roles.GUIDE.status
    val handoverReady = status == "AMBULANCE_ARRIVED" || incidentState.phase == "HANDOVER"
    CriticalScaffold(
        eyebrow = "环境清障任务",
        title = if (handoverReady) "救护车已到场，交接进行中" else "你被分配为环境清障者",
        body = if (handoverReady) {
            "继续协助疏通通道和现场秩序，并配合完成医疗交接。"
        } else {
            "立即疏通生命通道、协调电梯和路口，并引导救护车快速抵达患者位置。"
        },
        accent = accentForRole(UserRole.GUIDE),
    ) {
        MetricTile(label = "任务状态", value = roleStatusLabel(status))
        MetricTile(label = "事件阶段", value = phaseTitle(incidentState.phase))
        MetricTile(label = "调度来源", value = incidentState.dispatchSource ?: "规则调度")
        if (!handoverReady) {
            PressableButton(
                text = "确认救护车已到达",
                onClick = { incidentViewModel.actionAmbulanceArrived(userId) },
                colors = ButtonDefaults.buttonColors(containerColor = PhoneColors.Yellow, contentColor = Color.Black),
                modifier = Modifier.fillMaxWidth(),
            )
        }
    }
}

@Composable
private fun UnassignedFullScreen(
    session: UserSession,
    incidentState: IncidentState,
) {
    CriticalScaffold(
        eyebrow = "待命终端",
        title = "当前未被分配具体任务",
        body = "本轮调度优先保障核心施救、AED 与通道清障。未被分配的终端保持待命，等待进一步指令。",
        accent = Color(0xFF94A3B8),
    ) {
        MetricTile(label = "你的画像", value = session.profileSummary)
        MetricTile(label = "身体状态", value = session.healthCondition.label)
        MetricTile(label = "当前阶段", value = phaseTitle(incidentState.phase))
    }
}

@Composable
private fun HandoverFullScreen(
    incidentState: IncidentState,
    userId: String,
    incidentViewModel: IncidentViewModel,
) {
    CriticalScaffold(
        eyebrow = "医疗交接",
        title = "急救车已接管患者",
        body = "本轮社会化协同任务已经完成，现场进入医疗交接与日志归档阶段。",
        accent = PhoneColors.Green,
    ) {
        MetricTile(label = "总耗时", value = rememberElapsedLabel(incidentState.logs.firstOrNull()?.ts))
        MetricTile(label = "分配来源", value = incidentState.dispatchSource ?: "规则调度")
        PressableButton(
            text = "确认完成救护车交接并归档",
            onClick = { incidentViewModel.actionHandoverCompleted(userId) },
            colors = ButtonDefaults.buttonColors(containerColor = PhoneColors.Green, contentColor = Color.White),
            modifier = Modifier.fillMaxWidth(),
        )
    }
}

@Composable
private fun ArchivedFullScreen(
    session: UserSession,
    incidentState: IncidentState,
    assignedRole: UserRole?,
    onExitEmergency: () -> Unit,
) {
    val isPatient = incidentState.patientUserId == session.userId
    CriticalScaffold(
        eyebrow = "已归档",
        title = if (isPatient) "患者端记录已保存" else "本轮救援记录已保存",
        body = if (isPatient) {
            "救护车已完成接管，本次被救援记录已经写入手机档案。你现在可以退出应急模式。"
        } else {
            "你的现场任务和处置日志已经归档到本机，可在档案页复盘本次协同救援。"
        },
        accent = PhoneColors.Green,
    ) {
        MetricTile(label = "终端身份", value = if (isPatient) "患者端" else assignedRole?.label ?: "协同终端")
        MetricTile(label = "归档状态", value = phaseTitle(incidentState.phase))
        PressableButton(
            text = "退出应急模式",
            onClick = onExitEmergency,
            colors = ButtonDefaults.buttonColors(containerColor = PhoneColors.Green, contentColor = Color.White),
            modifier = Modifier.fillMaxWidth(),
        )
    }
}

@Composable
private fun CriticalScaffold(
    eyebrow: String,
    title: String,
    body: String,
    accent: Color,
    content: @Composable ColumnScope.() -> Unit,
) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                Brush.verticalGradient(
                    colors = listOf(
                        Color(0xFF2A0208),
                        Color(0xFF4C0519),
                        Color(0xFF020617),
                    )
                )
            )
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            Spacer(modifier = Modifier.height(24.dp))
            Text(eyebrow, color = accent, fontSize = 12.sp, fontWeight = FontWeight.Black)
            Text(title, color = Color.White, fontSize = 30.sp, fontWeight = FontWeight.Black, lineHeight = 36.sp)
            Text(body, color = Color(0xFFE2E8F0), fontSize = 15.sp, lineHeight = 24.sp)

            Card(
                colors = CardDefaults.cardColors(containerColor = Color(0xFF130A18)),
                shape = RoundedCornerShape(28.dp),
                border = androidx.compose.foundation.BorderStroke(1.dp, accent.copy(alpha = 0.35f)),
            ) {
                Column(
                    modifier = Modifier.padding(20.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp),
                    content = content,
                )
            }
        }
    }
}

@Composable
private fun MetricTile(
    label: String,
    value: String,
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(Color(0xCC0F172A), RoundedCornerShape(20.dp))
            .padding(horizontal = 16.dp, vertical = 14.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
    ) {
        Text(label, color = PhoneColors.GrayText, fontSize = 12.sp)
        Text(value, color = Color.White, fontSize = 13.sp, fontWeight = FontWeight.Bold)
    }
}

private fun dispatchStartTs(incidentState: IncidentState): Long? {
    return incidentState.logs.lastOrNull { entry ->
        entry.msg.contains("Patient designated", ignoreCase = true) ||
            entry.msg.contains("AI dispatching", ignoreCase = true)
    }?.ts ?: incidentState.logs.lastOrNull()?.ts
}
