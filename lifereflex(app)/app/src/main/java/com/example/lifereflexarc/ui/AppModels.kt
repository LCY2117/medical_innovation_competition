package com.example.lifereflexarc.ui

import androidx.compose.runtime.Composable
import androidx.compose.runtime.produceState
import androidx.compose.ui.graphics.Color
import com.example.lifereflexarc.data.IncidentState
import com.example.lifereflexarc.data.UserRole
import com.example.lifereflexarc.ui.theme.PhoneColors
import kotlinx.coroutines.delay

enum class MainTab(val label: String) {
    Home("首页"),
    Tasks("任务"),
    Incident("事件"),
    Archive("归档"),
    Profile("我的"),
}

fun userRoleFromBackendRole(role: String): UserRole = when (role) {
    "PRIME" -> UserRole.PRIME
    "RUNNER" -> UserRole.RUNNER
    "GUIDE" -> UserRole.GUIDE
    else -> UserRole.PATIENT
}

fun accentForRole(role: UserRole): Color = when (role) {
    UserRole.PATIENT -> Color(0xFF0F766E)
    UserRole.PRIME -> PhoneColors.Red
    UserRole.RUNNER -> PhoneColors.Blue
    UserRole.GUIDE -> PhoneColors.Yellow
}

fun phaseTitle(phase: String?): String = when (phase) {
    "CREATED" -> "监测中"
    "DISPATCHING" -> "智能分派中"
    "DISPATCHED" -> "已派发"
    "CPR" -> "基础复苏中"
    "AED_PICKED" -> "AED 已取"
    "AED_DELIVERED" -> "AED 已达"
    "AED_ANALYZING" -> "AED 分析中"
    "SHOCK_DELIVERED" -> "已完成除颤"
    "HANDOVER" -> "已交接"
    "ARCHIVED" -> "已归档"
    else -> "未知阶段"
}

fun phaseHeadline(phase: String): String = when (phase) {
    "CREATED" -> "监测与告警准备"
    "DISPATCHING" -> "云端正在生成任务编排"
    "DISPATCHED" -> "多角色协同已启动"
    "CPR" -> "基础复苏循环正在进行"
    "AED_PICKED" -> "AED 正在回送现场"
    "AED_DELIVERED" -> "AED 已送达现场"
    "AED_ANALYZING" -> "AED 正在分析心律"
    "SHOCK_DELIVERED" -> "已完成一次电击除颤"
    "HANDOVER" -> "救护车交接完成"
    "ARCHIVED" -> "救援记录已归档"
    else -> "现场状态更新"
}

fun phaseBody(phase: String): String = when (phase) {
    "CREATED" -> "系统正在等待异常确认或自动告警。"
    "DISPATCHING" -> "患者已被网页指挥台触发，硅基流动正在根据画像和能力标签生成核心施救、AED保障、环境清障分派。"
    "DISPATCHED" -> "云端已向核心施救、AED保障、环境清障三类角色派发并行任务。"
    "CPR" -> "核心施救者已开始基础复苏循环，正在按 30:2 节律持续执行胸外按压与人工呼吸。"
    "AED_PICKED" -> "设备链路已经打通，AED 正向患者位置回送。"
    "AED_DELIVERED" -> "设备已抵达现场，核心施救者应立即贴附电极片并按 AED 语音提示分析。"
    "AED_ANALYZING" -> "AED 正在分析患者心律，请停止接触患者并等待是否建议电击。"
    "SHOCK_DELIVERED" -> "已完成一次 AED 除颤，应立刻恢复 30:2 基础复苏循环，并在 2 分钟后再次等待 AED 分析。"
    "HANDOVER" -> "院前社会力量已完成阶段任务，进入急救车接管与归档。"
    "ARCHIVED" -> "本次救援任务已完成归档，终端可退出应急模式并在档案页查看记录。"
    else -> "等待更多事件同步。"
}

fun roleStatusLabel(status: String?): String = when (status) {
    null, "", "IDLE" -> "待命"
    "ASSIGNED" -> "已分派"
    "JOINED" -> "已响应"
    "CPR_STARTED" -> "基础复苏中"
    "AED_PICKED" -> "已取到 AED"
    "AED_DELIVERED" -> "已送达 AED"
    "AED_ANALYZING" -> "AED 分析中"
    "AED_SHOCK_DELIVERED" -> "已完成除颤"
    "AMBULANCE_ARRIVED" -> "救护车已到场"
    "HANDOVER_COMPLETED" -> "交接已完成"
    else -> "未识别状态"
}

fun primeVoiceCue(incidentState: IncidentState): String? = when {
    incidentState.phase == "DISPATCHED" -> "你已被分配为核心施救者，请立即前往患者位置，开始基础复苏。"
    incidentState.roles.PRIME.status == "CPR_STARTED" || incidentState.phase == "CPR" ->
        "保持三十比二基础复苏循环，持续高质量胸外按压。"
    incidentState.phase == "AED_PICKED" -> "AED 已取到，继续胸外按压并等待设备送达。"
    incidentState.phase == "AED_DELIVERED" -> "AED 已送达，请贴附电极片并准备启动分析。"
    incidentState.phase == "AED_ANALYZING" -> "AED 正在分析，请停止接触患者。"
    incidentState.phase == "SHOCK_DELIVERED" -> "除颤完成，立即恢复三十比二基础复苏循环。"
    incidentState.phase == "HANDOVER" -> "救护车已到场，请准备完成医疗交接。"
    else -> null
}

fun formatDuration(totalSeconds: Long): String {
    val minutes = totalSeconds / 60
    val seconds = totalSeconds % 60
    return "%02d:%02d".format(minutes, seconds)
}

@Composable
fun rememberElapsedLabel(startTs: Long?): String {
    val elapsed = produceState(initialValue = "--:--", startTs) {
        if (startTs == null) {
            value = "--:--"
            return@produceState
        }
        while (true) {
            val elapsedSeconds = ((System.currentTimeMillis() - startTs) / 1000L).coerceAtLeast(0L)
            value = formatDuration(elapsedSeconds)
            delay(1000)
        }
    }
    return elapsed.value
}

@Composable
fun rememberCountdownValue(startTs: Long?, durationSec: Int?): Int {
    val countdown = produceState(initialValue = durationSec ?: 10, startTs, durationSec) {
        if (startTs == null || durationSec == null) {
            value = durationSec ?: 10
            return@produceState
        }
        while (true) {
            val elapsed = ((System.currentTimeMillis() - startTs) / 1000L).toInt().coerceAtLeast(0)
            value = (durationSec - elapsed).coerceAtLeast(0)
            delay(500)
        }
    }
    return countdown.value
}
