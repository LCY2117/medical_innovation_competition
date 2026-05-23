package com.example.lifereflexarc.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.lifereflexarc.data.IncidentState
import com.example.lifereflexarc.data.IncidentArchiveEntry
import com.example.lifereflexarc.data.LogEntry
import com.example.lifereflexarc.data.UserRole
import com.example.lifereflexarc.data.UserSession
import com.example.lifereflexarc.data.AedSite
import com.example.lifereflexarc.data.DispatchRoleDecision
import com.example.lifereflexarc.data.GeoPoint
import com.example.lifereflexarc.data.HealthIntegrationReadiness
import com.example.lifereflexarc.data.HealthSignalSummary
import com.example.lifereflexarc.data.AppSettings
import com.example.lifereflexarc.ui.accentForRole
import com.example.lifereflexarc.ui.dispatchSourceLabel
import com.example.lifereflexarc.ui.components.EmptyStateCard
import com.example.lifereflexarc.ui.components.MetricCard
import com.example.lifereflexarc.ui.components.PressableButton
import com.example.lifereflexarc.ui.components.SectionTitle
import com.example.lifereflexarc.ui.components.SummaryRow
import com.example.lifereflexarc.ui.formatAedStatusLabel
import com.example.lifereflexarc.ui.formatFloorLabel
import com.example.lifereflexarc.ui.formatLocationSourceLabel
import com.example.lifereflexarc.ui.roleStatusLabel
import com.example.lifereflexarc.ui.theme.PhoneColors
import com.example.lifereflexarc.viewmodel.IncidentViewModel
import com.example.lifereflexarc.BuildConfig
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

@Composable
fun CommandHomeScreen(
    session: UserSession,
    incidentState: IncidentState?,
    connected: Boolean,
    assignedRole: UserRole?,
    healthSignals: HealthSignalSummary?,
    healthReadiness: HealthIntegrationReadiness,
    onCreateIncident: () -> Unit,
    onOpenCurrent: () -> Unit,
    onAutoJoinCurrent: (() -> Unit)?,
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState()),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        Card(
            colors = CardDefaults.cardColors(containerColor = Color(0xFF111C34)),
            shape = androidx.compose.foundation.shape.RoundedCornerShape(28.dp),
            border = BorderStroke(1.dp, Color(0xFF22304A)),
        ) {
            Column(modifier = Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
                Text(
                    text = "欢迎回来，${session.displayName}",
                    color = Color.White,
                    fontSize = 22.sp,
                    fontWeight = FontWeight.Bold,
                )
                Text(
                    text = "${session.organization} · ${session.profileSummary}",
                    color = PhoneColors.GrayText,
                    fontSize = 13.sp,
                )
                Text(
                    text = if (incidentState == null) {
                        "优先进入网页指挥台创建的当前事件；公共演示环境下不建议在 App 端随意新建事件。"
                    } else {
                        "当前存在活动事件，建议直接查看任务或自动接单。"
                    },
                    color = Color(0xFFE2E8F0),
                    fontSize = 14.sp,
                    lineHeight = 22.sp,
                )
            }
        }

        Row(horizontalArrangement = Arrangement.spacedBy(12.dp), modifier = Modifier.fillMaxWidth()) {
            MetricCard(
                label = "网络状态",
                value = if (connected) "已连接" else "待同步",
                accent = if (connected) PhoneColors.Green else PhoneColors.Yellow,
                modifier = Modifier.weight(1f),
            )
            MetricCard(
                label = "当前状态",
                value = assignedRole?.label ?: session.profileLabel,
                accent = assignedRole?.let(::accentForRole) ?: Color(0xFF2563EB),
                modifier = Modifier.weight(1f),
            )
        }

        HealthSignalSummaryCard(healthSignals = healthSignals, readiness = healthReadiness)

        SectionTitle("快速入口")
        IncidentQuickActionsCard(
            canAutoJoin = onAutoJoinCurrent != null,
            onCreateIncident = onCreateIncident,
            onOpenCurrent = onOpenCurrent,
            onAutoJoinCurrent = onAutoJoinCurrent,
        )
    }
}

@Composable
fun TasksScreen(
    session: UserSession,
    incidentState: IncidentState?,
    assignedRole: UserRole?,
    deviceUserId: String,
    incidentViewModel: IncidentViewModel,
    pendingAction: String?,
    onOpenIncident: () -> Unit,
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState()),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        SectionTitle("我的任务")
        if (incidentState == null) {
            EmptyStateCard(
                title = "当前没有任务",
                body = "连接一个活动事件，或等待云端分配后再回来查看。",
            )
            return
        }

        MissionPanel(
            session = session,
            incidentState = incidentState,
            assignedRole = assignedRole,
            deviceUserId = deviceUserId,
            incidentViewModel = incidentViewModel,
            pendingAction = pendingAction,
        )
        RecentTimelineCard(logs = incidentState.logs)

        if (incidentState.phase != "ARCHIVED") {
            PressableButton(
                text = "查看现场总览",
                onClick = onOpenIncident,
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF1D4ED8), contentColor = Color.White),
                modifier = Modifier.fillMaxWidth(),
            )
        }
    }
}

@Composable
fun IncidentScreen(
    session: UserSession,
    incidentState: IncidentState?,
    assignedRole: UserRole?,
    healthSignals: HealthSignalSummary?,
    healthReadiness: HealthIntegrationReadiness,
    deviceUserId: String,
    incidentViewModel: IncidentViewModel,
    pendingAction: String?,
    onCreateIncident: () -> Unit,
    onOpenCurrent: () -> Unit,
    onAutoJoinCurrent: (() -> Unit)?,
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState()),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        SectionTitle("现场总览")

        if (incidentState == null) {
            EmptyStateCard(
                title = "尚未接入事件",
                body = "先从首页进入当前事件，或由指挥端触发急救协同后，再回来查看实时状态和任务。",
            )
            IncidentQuickActionsCard(
                canAutoJoin = onAutoJoinCurrent != null,
                onCreateIncident = onCreateIncident,
                onOpenCurrent = onOpenCurrent,
                onAutoJoinCurrent = onAutoJoinCurrent,
            )
            return
        }

        IncidentHeaderCard(incidentState = incidentState, assignedRole = assignedRole ?: UserRole.PATIENT)
        HealthSignalSummaryCard(healthSignals = healthSignals, readiness = healthReadiness)
        MissionPanel(
            session = session,
            incidentState = incidentState,
            assignedRole = assignedRole,
            deviceUserId = deviceUserId,
            incidentViewModel = incidentViewModel,
            pendingAction = pendingAction,
        )
        if (incidentState.phase != "ARCHIVED") {
            Card(
                colors = CardDefaults.cardColors(containerColor = Color(0xFF0F172A)),
                shape = androidx.compose.foundation.shape.RoundedCornerShape(24.dp),
                border = BorderStroke(1.dp, Color(0xFF1E293B)),
            ) {
                Column(modifier = Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Text("现场协同", color = Color.White, fontSize = 18.sp, fontWeight = FontWeight.SemiBold)
                    SummaryRow("核心施救", roleStatusLabel(incidentState.roles.PRIME.status), dark = true)
                    SummaryRow("AED保障", roleStatusLabel(incidentState.roles.RUNNER.status), dark = true)
                    SummaryRow("环境清障", roleStatusLabel(incidentState.roles.GUIDE.status), dark = true)
                }
            }
        }
        RecentTimelineCard(logs = incidentState.logs)
        AedSitesCard(aedSites = incidentState.aedSites)
        DispatchRationaleCard(incidentState = incidentState)
    }
}

@Composable
private fun RecentTimelineCard(
    logs: List<LogEntry>,
) {
    val formatter = remember { SimpleDateFormat("HH:mm:ss", Locale.getDefault()) }
    val recentLogs = logs.takeLast(6).asReversed()

    Card(
        colors = CardDefaults.cardColors(containerColor = Color(0xFF0F172A)),
        shape = androidx.compose.foundation.shape.RoundedCornerShape(24.dp),
        border = BorderStroke(1.dp, Color(0xFF1E293B)),
    ) {
        Column(modifier = Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text("最近现场时间线", color = Color.White, fontSize = 18.sp, fontWeight = FontWeight.SemiBold)
            if (recentLogs.isEmpty()) {
                Text(
                    text = "暂无现场日志。患者触发、角色接单和 AED 进展会同步到这里。",
                    color = PhoneColors.GrayText,
                    fontSize = 13.sp,
                    lineHeight = 20.sp,
                )
            } else {
                recentLogs.forEach { log ->
                    TimelineLogRow(
                        timeLabel = formatter.format(Date(log.ts)),
                        message = translateTimelineMessage(log.msg),
                    )
                }
            }
        }
    }
}

@Composable
private fun TimelineLogRow(
    timeLabel: String,
    message: String,
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Text(
            text = timeLabel,
            color = Color(0xFF93C5FD),
            fontSize = 12.sp,
            fontWeight = FontWeight.SemiBold,
        )
        Text(
            text = message,
            color = Color(0xFFE2E8F0),
            fontSize = 13.sp,
            lineHeight = 19.sp,
            modifier = Modifier.weight(1f),
        )
    }
}

@Composable
private fun AedSitesCard(
    aedSites: List<AedSite>,
) {
    Card(
        colors = CardDefaults.cardColors(containerColor = Color(0xFF0F172A)),
        shape = androidx.compose.foundation.shape.RoundedCornerShape(24.dp),
        border = BorderStroke(1.dp, Color(0xFF1E293B)),
    ) {
        Column(modifier = Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text("AED 点位", color = Color.White, fontSize = 18.sp, fontWeight = FontWeight.SemiBold)
            if (aedSites.isEmpty()) {
                Text(
                    text = "当前事件还没有同步 AED 点位。请先在网页调度台初始化协同演示场景。",
                    color = PhoneColors.GrayText,
                    fontSize = 13.sp,
                    lineHeight = 20.sp,
                )
            } else {
                aedSites.forEach { site ->
                    SummaryRow(
                        label = site.name,
                        value = listOfNotNull(
                            site.location.label,
                            formatFloorLabel(site.location.floor),
                            formatAedStatusLabel(site.status),
                        )
                            .joinToString(" · "),
                        dark = true,
                    )
                    if (site.accessNotes.isNotBlank()) {
                        Text(site.accessNotes, color = PhoneColors.GrayText, fontSize = 12.sp, lineHeight = 18.sp)
                    }
                }
            }
        }
    }
}

@Composable
private fun DispatchRationaleCard(
    incidentState: IncidentState,
) {
    Card(
        colors = CardDefaults.cardColors(containerColor = Color(0xFF0F172A)),
        shape = androidx.compose.foundation.shape.RoundedCornerShape(24.dp),
        border = BorderStroke(1.dp, Color(0xFF1E293B)),
    ) {
        Column(modifier = Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text("调度依据", color = Color.White, fontSize = 18.sp, fontWeight = FontWeight.SemiBold)
            Text(
                text = "来源：${dispatchSourceLabel(incidentState.dispatchSource)}",
                color = PhoneColors.GrayText,
                fontSize = 13.sp,
            )
            if (incidentState.dispatchRationale.isEmpty()) {
                Text(
                    text = "触发患者后，云端会把角色评分、距离和选择理由同步到这里。",
                    color = PhoneColors.GrayText,
                    fontSize = 13.sp,
                    lineHeight = 20.sp,
                )
            } else {
                DispatchDecisionRow("核心施救", incidentState.dispatchRationale["PRIME"], PhoneColors.Red)
                DispatchDecisionRow("AED 保障", incidentState.dispatchRationale["RUNNER"], PhoneColors.Blue)
                DispatchDecisionRow("环境清障", incidentState.dispatchRationale["GUIDE"], PhoneColors.Yellow)
            }
        }
    }
}

@Composable
private fun DispatchDecisionRow(
    roleLabel: String,
    decision: DispatchRoleDecision?,
    accent: Color,
) {
    if (decision == null) {
        SummaryRow(roleLabel, "待分派", dark = true)
        return
    }
    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
        Text(roleLabel, color = accent, fontSize = 13.sp, fontWeight = FontWeight.Bold)
        SummaryRow("候选终端", decision.userId ?: "未分配", dark = true)
        SummaryRow("综合评分", decision.score.toInt().toString(), dark = true)
        SummaryRow("到患者", formatMeters(decision.distanceToPatientMeters), dark = true)
        if (decision.distanceToAedMeters != null) {
            SummaryRow("到 AED", formatMeters(decision.distanceToAedMeters), dark = true)
        }
        decision.reasons.take(3).forEach { reason ->
            Text("· $reason", color = Color(0xFFE2E8F0), fontSize = 12.sp, lineHeight = 18.sp)
        }
        decision.warnings.take(2).forEach { warning ->
            Text("风险：$warning", color = PhoneColors.RedSoft, fontSize = 12.sp, lineHeight = 18.sp)
        }
    }
}

private fun formatMeters(value: Double?): String {
    if (value == null) {
        return "--"
    }
    return if (value >= 1000.0) {
        "%.2f km".format(value / 1000.0)
    } else {
        "${value.toInt()} m"
    }
}

@Composable
private fun HealthSignalSummaryCard(
    healthSignals: HealthSignalSummary?,
    readiness: HealthIntegrationReadiness,
) {
    Card(
        colors = CardDefaults.cardColors(containerColor = Color(0xFF0F172A)),
        shape = androidx.compose.foundation.shape.RoundedCornerShape(24.dp),
        border = BorderStroke(1.dp, Color(0xFF1E293B)),
    ) {
        Column(modifier = Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text("健康数据增强", color = Color.White, fontSize = 18.sp, fontWeight = FontWeight.SemiBold)
            Text(
                text = if (healthSignals == null) {
                    "真实健康授权完成前，系统使用健康摘要样例维持协同流程闭环。"
                } else {
                    "当前健康摘要用于展示调度如何参考健康风险。"
                },
                color = PhoneColors.GrayText,
                fontSize = 13.sp,
                lineHeight = 20.sp,
            )
            SummaryRow("数据来源", translateHealthSource(healthSignals?.source), dark = true)
            SummaryRow("授权状态", translateHealthAuthorization(healthSignals?.authorizationStatus), dark = true)
            SummaryRow("接入准备", readiness.statusText, dark = true)
            SummaryRow("心率", healthSignals?.heartRateBpm?.let { "$it bpm" } ?: "--", dark = true)
            SummaryRow("血氧", healthSignals?.bloodOxygenPercent?.let { "${it.toInt()}%" } ?: "--", dark = true)
            SummaryRow("压力", healthSignals?.pressureScore?.toString() ?: "--", dark = true)
            val riskTags = healthSignals?.riskTags.orEmpty()
            if (riskTags.isNotEmpty()) {
                Text(
                    text = "风险标记：${riskTags.joinToString("、") { translateHealthRiskTag(it) }}",
                    color = PhoneColors.RedSoft,
                    fontSize = 12.sp,
                    lineHeight = 18.sp,
                )
            }
            Text(
                text = readiness.detailText,
                color = PhoneColors.GrayText,
                fontSize = 12.sp,
                lineHeight = 18.sp,
            )
        }
    }
}

private fun translateHealthSource(source: String?): String = when (source) {
    "oppo", "oppo_health" -> "OPPO 健康"
    "mock" -> "健康摘要样例"
    "manual" -> "手动录入"
    else -> "健康数据未接入"
}

private fun translateHealthAuthorization(status: String?): String = when (status) {
    "authorized" -> "已授权"
    "sample" -> "样例接入"
    "not_connected", null -> "未接入"
    "denied" -> "未授权"
    else -> status
}

private fun translateHealthRiskTag(tag: String): String = when (tag) {
    "tachycardia" -> "心率偏快"
    "bradycardia" -> "心率偏慢"
    "low_spo2" -> "血氧偏低"
    "high_pressure" -> "压力偏高"
    "limited_mobility" -> "行动能力受限"
    else -> tag
}

private fun translateTimelineMessage(message: String): String {
    val normalized = message.lowercase(Locale.ROOT)
    return when {
        normalized.contains("patient designated") -> "患者端已被标记，现场协同链路开始启动"
        normalized.contains("ai dispatching") -> "智能协同正在生成核心施救、AED 保障与清障分派"
        normalized.contains("dispatch") || normalized.contains("assigned") -> "云端已完成角色分派，任务同步到各终端"
        normalized.contains("sos") && normalized.contains("cancel") -> "患者已取消 SOS 告警"
        normalized.contains("sos") || normalized.contains("alert") -> "患者端触发 SOS 告警"
        normalized.contains("cpr started") -> "核心施救者已启动 CPR"
        normalized.contains("aed picked") -> "AED 保障者已取到设备，正在回送现场"
        normalized.contains("aed delivered") -> "AED 已送达患者位置"
        normalized.contains("aed analysis") || normalized.contains("aed analyzing") -> "AED 正在分析心律"
        normalized.contains("aed shock delivered") || normalized.contains("shock delivered") -> "AED 已完成一次除颤"
        normalized.contains("ambulance arrived") -> "救护车已到达，环境清障进入接驳"
        normalized.contains("handover") -> "现场任务进入医疗交接"
        normalized.contains("archive") -> "事件记录已归档"
        normalized.contains("join") -> "协同成员已响应任务"
        else -> message
    }
}

@Composable
fun ArchiveScreen(
    incidentState: IncidentState?,
    archives: List<IncidentArchiveEntry>,
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState()),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        SectionTitle("事件归档")
        if (archives.isEmpty()) {
            EmptyStateCard(
                title = "暂无已归档事件",
                body = "完成救护车交接并归档后，记录会保存在本机档案中。",
            )
            return
        }
        archives.forEachIndexed { index, entry ->
            Card(
                colors = CardDefaults.cardColors(containerColor = if (entry.isPatient) Color(0xFF2A0B11) else Color.White),
                shape = androidx.compose.foundation.shape.RoundedCornerShape(28.dp),
            ) {
                Column(modifier = Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text(
                        entry.title,
                        color = if (entry.isPatient) Color.White else Color(0xFF0F172A),
                        fontSize = 22.sp,
                        fontWeight = FontWeight.Bold,
                    )
                    Text(
                        entry.summary,
                        color = if (entry.isPatient) Color(0xFFE2E8F0) else Color(0xFF475569),
                        fontSize = 14.sp,
                    )
                    SummaryRow("终端身份", entry.roleLabel, dark = entry.isPatient)
                    SummaryRow("归档状态", entry.phaseLabel, dark = entry.isPatient)
                    SummaryRow("任务来源", dispatchSourceLabel(entry.dispatchSource), dark = entry.isPatient)
                    SummaryRow("处置时长", "${entry.durationSec / 60} 分 ${entry.durationSec % 60} 秒", dark = entry.isPatient)
                    if (entry.taskSummary.isNotEmpty()) {
                        Text(
                            "参与者视角复盘",
                            color = if (entry.isPatient) Color.White else Color(0xFF0F172A),
                            fontSize = 14.sp,
                            fontWeight = FontWeight.SemiBold,
                        )
                        entry.taskSummary.forEachIndexed { itemIndex, item ->
                            Text(
                                text = "${itemIndex + 1}. $item",
                                color = if (entry.isPatient) Color(0xFFE2E8F0) else Color(0xFF475569),
                                fontSize = 13.sp,
                                lineHeight = 19.sp,
                            )
                        }
                    }
                    if (index == 0 && incidentState?.incidentId == entry.incidentId) {
                        SummaryRow("当前状态", "本轮事件刚完成归档", dark = entry.isPatient)
                    }
                }
            }
        }
    }
}

@Composable
fun ProfileScreen(
    session: UserSession,
    healthSignals: HealthSignalSummary?,
    healthReadiness: HealthIntegrationReadiness,
    location: GeoPoint?,
    locationStatus: String,
    onSyncSystemLocation: () -> Unit,
    onDemoLocationSelected: (label: String, latitude: Double, longitude: Double) -> Unit,
    onLogout: () -> Unit,
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState()),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        SectionTitle("个人中心")
        Card(
            colors = CardDefaults.cardColors(containerColor = Color(0xFF111C34)),
            shape = androidx.compose.foundation.shape.RoundedCornerShape(28.dp),
            border = BorderStroke(1.dp, Color(0xFF22304A)),
        ) {
            Column(modifier = Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Text(session.displayName, color = Color.White, fontSize = 24.sp, fontWeight = FontWeight.Bold)
                Text(session.phone, color = PhoneColors.GrayText, fontSize = 13.sp)
                SummaryRow("所属组织", session.organization, dark = true)
                SummaryRow("身体状况", session.healthCondition.label, dark = true)
                SummaryRow("职业身份", session.professionIdentity.label, dark = true)
                SummaryRow("认证状态", session.credentialStatus, dark = true)
                SummaryRow("个人画像", session.profileSummary, dark = true)
            }
        }

        HealthSignalSummaryCard(healthSignals = healthSignals, readiness = healthReadiness)

        DemoLocationCard(
            location = location,
            locationStatus = locationStatus,
            onSyncSystemLocation = onSyncSystemLocation,
            onDemoLocationSelected = onDemoLocationSelected,
        )

        Card(
            colors = CardDefaults.cardColors(containerColor = Color(0xFF0F172A)),
            shape = androidx.compose.foundation.shape.RoundedCornerShape(24.dp),
            border = BorderStroke(1.dp, Color(0xFF1E293B)),
        ) {
            Column(modifier = Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                Text("我的能力标签", color = Color.White, fontSize = 18.sp, fontWeight = FontWeight.SemiBold)
                Text(
                    text = session.bio,
                    color = PhoneColors.GrayText,
                    fontSize = 13.sp,
                    lineHeight = 20.sp,
                )
                Text(
                    text = "系统会基于你的身体状况、职业身份和个人画像，为你分配最合适的现场任务。",
                    color = PhoneColors.GrayText,
                    fontSize = 13.sp,
                    lineHeight = 20.sp,
                )
            }
        }

        PressableButton(
            text = "退出登录",
            onClick = onLogout,
            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF7F1D1D), contentColor = Color.White),
            modifier = Modifier.fillMaxWidth(),
        )
    }
}

@Composable
fun SettingsScreen(
    session: UserSession,
    incidentState: IncidentState?,
    connected: Boolean,
    connecting: Boolean,
    healthReadiness: HealthIntegrationReadiness,
    appSettings: AppSettings,
    location: GeoPoint?,
    locationStatus: String,
    archiveCount: Int,
    onOpenCurrent: () -> Unit,
    onSyncSystemLocation: () -> Unit,
    onVoiceGuidanceChanged: (Boolean) -> Unit,
    onVibrationAlertChanged: (Boolean) -> Unit,
    onDemoSafetyChanged: (Boolean) -> Unit,
    onLogout: () -> Unit,
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState()),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        SectionTitle("设置")
        Card(
            colors = CardDefaults.cardColors(containerColor = Color(0xFF111C34)),
            shape = androidx.compose.foundation.shape.RoundedCornerShape(28.dp),
            border = BorderStroke(1.dp, Color(0xFF22304A)),
        ) {
            Column(modifier = Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Text("应用状态", color = Color.White, fontSize = 22.sp, fontWeight = FontWeight.Bold)
                Text(
                    text = "这里集中查看连接、事件、定位和演示边界，便于赛前检查。",
                    color = PhoneColors.GrayText,
                    fontSize = 13.sp,
                    lineHeight = 20.sp,
                )
                SummaryRow("登录用户", session.displayName, dark = true)
                SummaryRow("服务连接", connectionStatusLabel(connected, connecting), dark = true)
                SummaryRow("当前事件", incidentState?.incidentId?.take(8) ?: "未接入", dark = true)
                SummaryRow("事件阶段", incidentState?.phase?.let { com.example.lifereflexarc.ui.phaseTitle(it) } ?: "待同步", dark = true)
                SummaryRow("本机归档", "${archiveCount} 条", dark = true)
            }
        }

        Card(
            colors = CardDefaults.cardColors(containerColor = Color(0xFF0F172A)),
            shape = androidx.compose.foundation.shape.RoundedCornerShape(24.dp),
            border = BorderStroke(1.dp, Color(0xFF1E293B)),
        ) {
            Column(modifier = Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                Text("服务端点", color = Color.White, fontSize = 18.sp, fontWeight = FontWeight.SemiBold)
                SummaryRow("REST", BuildConfig.LRA_API_BASE, dark = true)
                SummaryRow("WebSocket", BuildConfig.LRA_WS_BASE, dark = true)
                Text(
                    text = "发布版构建会阻止 HTTP/WS 本地端点，避免比赛或专家演示时误连测试服务。",
                    color = PhoneColors.GrayText,
                    fontSize = 12.sp,
                    lineHeight = 18.sp,
                )
                PressableButton(
                    text = "重新同步当前事件",
                    onClick = onOpenCurrent,
                    colors = ButtonDefaults.buttonColors(containerColor = PhoneColors.Blue, contentColor = Color.White),
                    modifier = Modifier.fillMaxWidth(),
                )
            }
        }

        Card(
            colors = CardDefaults.cardColors(containerColor = Color(0xFF0F172A)),
            shape = androidx.compose.foundation.shape.RoundedCornerShape(24.dp),
            border = BorderStroke(1.dp, Color(0xFF1E293B)),
        ) {
            Column(modifier = Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Text("本机偏好", color = Color.White, fontSize = 18.sp, fontWeight = FontWeight.SemiBold)
                SettingsSwitchRow(
                    title = "语音指引",
                    body = "核心施救任务中播放简短语音提示。",
                    checked = appSettings.voiceGuidanceEnabled,
                    onCheckedChange = onVoiceGuidanceChanged,
                )
                SettingsSwitchRow(
                    title = "震动提醒",
                    body = "为后续真机告警预留震动提醒开关。",
                    checked = appSettings.vibrationAlertEnabled,
                    onCheckedChange = onVibrationAlertChanged,
                )
                SettingsSwitchRow(
                    title = "演示安全确认",
                    body = "在比赛与预实验中明确当前流程仅用于模拟展示。",
                    checked = appSettings.demoSafetyAcknowledged,
                    onCheckedChange = onDemoSafetyChanged,
                )
            }
        }

        Card(
            colors = CardDefaults.cardColors(containerColor = Color(0xFF0F172A)),
            shape = androidx.compose.foundation.shape.RoundedCornerShape(24.dp),
            border = BorderStroke(1.dp, Color(0xFF1E293B)),
        ) {
            Column(modifier = Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                Text("设备能力", color = Color.White, fontSize = 18.sp, fontWeight = FontWeight.SemiBold)
                SummaryRow("健康接入", healthReadiness.statusText, dark = true)
                SummaryRow("真实 SDK", if (healthReadiness.realSdkAvailable) "可用" else "未启用", dark = true)
                SummaryRow("定位状态", locationStatus, dark = true)
                SummaryRow("当前位置", location?.label ?: "未同步", dark = true)
                Text(
                    text = healthReadiness.detailText,
                    color = PhoneColors.GrayText,
                    fontSize = 12.sp,
                    lineHeight = 18.sp,
                )
                PressableButton(
                    text = "同步系统定位",
                    onClick = onSyncSystemLocation,
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF047857), contentColor = Color.White),
                    modifier = Modifier.fillMaxWidth(),
                )
            }
        }

        Card(
            colors = CardDefaults.cardColors(containerColor = Color(0xFF0F172A)),
            shape = androidx.compose.foundation.shape.RoundedCornerShape(24.dp),
            border = BorderStroke(1.dp, Color(0xFF1E293B)),
        ) {
            Column(modifier = Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                Text("演示边界", color = Color.White, fontSize = 18.sp, fontWeight = FontWeight.SemiBold)
                Text(
                    text = "当前版本用于医创赛演示和低成本预实验模拟。健康摘要、AED 点位和调度解释应作为系统能力展示，不作为真实医疗诊断依据。",
                    color = PhoneColors.GrayText,
                    fontSize = 13.sp,
                    lineHeight = 20.sp,
                )
                SummaryRow("应用版本", BuildConfig.VERSION_NAME, dark = true)
                SummaryRow("构建号", BuildConfig.VERSION_CODE.toString(), dark = true)
            }
        }

        PressableButton(
            text = "退出登录",
            onClick = onLogout,
            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF7F1D1D), contentColor = Color.White),
            modifier = Modifier.fillMaxWidth(),
        )
    }
}

private fun connectionStatusLabel(connected: Boolean, connecting: Boolean): String = when {
    connecting -> "同步中"
    connected -> "实时同步"
    else -> "离线"
}

@Composable
private fun SettingsSwitchRow(
    title: String,
    body: String,
    checked: Boolean,
    onCheckedChange: (Boolean) -> Unit,
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        Column(modifier = Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(4.dp)) {
            Text(title, color = Color.White, fontSize = 14.sp, fontWeight = FontWeight.SemiBold)
            Text(body, color = PhoneColors.GrayText, fontSize = 12.sp, lineHeight = 18.sp)
        }
        Switch(
            checked = checked,
            onCheckedChange = onCheckedChange,
        )
    }
}

@Composable
private fun DemoLocationCard(
    location: GeoPoint?,
    locationStatus: String,
    onSyncSystemLocation: () -> Unit,
    onDemoLocationSelected: (label: String, latitude: Double, longitude: Double) -> Unit,
) {
    val points = listOf(
        DemoLocationPoint("患者走廊", "教学楼 A 座 2 层走廊", 39.904120, 116.407210),
        DemoLocationPoint("一层大厅", "教学楼 A 座 1 层大厅", 39.904210, 116.407260),
        DemoLocationPoint("校门岗亭", "校门岗亭", 39.904500, 116.407620),
        DemoLocationPoint("操场入口", "操场入口", 39.903920, 116.407020),
    )
    Card(
        colors = CardDefaults.cardColors(containerColor = Color(0xFF0F172A)),
        shape = androidx.compose.foundation.shape.RoundedCornerShape(24.dp),
        border = BorderStroke(1.dp, Color(0xFF1E293B)),
    ) {
        Column(modifier = Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text("位置同步", color = Color.White, fontSize = 18.sp, fontWeight = FontWeight.SemiBold)
            Text(
                text = locationStatus,
                color = PhoneColors.GrayText,
                fontSize = 13.sp,
                lineHeight = 20.sp,
            )
            SummaryRow("当前位置", location?.label ?: "未同步", dark = true)
            SummaryRow("坐标来源", formatLocationSourceLabel(location?.source), dark = true)
            SummaryRow("经纬度", location?.let { formatCoordinate(it) } ?: "--", dark = true)
            SummaryRow("精度", location?.accuracyMeters?.let { "${it.toInt()} m" } ?: "--", dark = true)
            PressableButton(
                text = "同步系统定位",
                onClick = onSyncSystemLocation,
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF047857), contentColor = Color.White),
                modifier = Modifier.fillMaxWidth(),
            )
            Text(
                text = "演示备用位置",
                color = Color.White,
                fontSize = 14.sp,
                fontWeight = FontWeight.SemiBold,
            )
            points.forEach { point ->
                PressableButton(
                    text = point.title,
                    onClick = { onDemoLocationSelected(point.label, point.latitude, point.longitude) },
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF1D4ED8), contentColor = Color.White),
                    modifier = Modifier.fillMaxWidth(),
                )
            }
        }
    }
}

private data class DemoLocationPoint(
    val title: String,
    val label: String,
    val latitude: Double,
    val longitude: Double,
)

private fun formatCoordinate(location: GeoPoint): String {
    return "%.6f, %.6f".format(Locale.US, location.latitude, location.longitude)
}

@Composable
private fun IncidentQuickActionsCard(
    canAutoJoin: Boolean,
    onCreateIncident: () -> Unit,
    onOpenCurrent: () -> Unit,
    onAutoJoinCurrent: (() -> Unit)?,
) {
    Card(
        colors = CardDefaults.cardColors(containerColor = Color(0xFF0F172A)),
        shape = androidx.compose.foundation.shape.RoundedCornerShape(24.dp),
        border = BorderStroke(1.dp, Color(0xFF1E293B)),
    ) {
        Column(modifier = Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Text("事件入口", color = Color.White, fontSize = 18.sp, fontWeight = FontWeight.SemiBold)
            Text(
                text = "比赛演示优先进入当前事件或自动接单。新建事件仅作为本地备用入口，正式演示由网页指挥台初始化。",
                color = PhoneColors.GrayText,
                fontSize = 13.sp,
                lineHeight = 20.sp,
            )

            PressableButton(
                text = "进入当前事件",
                onClick = onOpenCurrent,
                colors = ButtonDefaults.buttonColors(containerColor = PhoneColors.Blue, contentColor = Color.White),
                modifier = Modifier.fillMaxWidth(),
            )
            if (canAutoJoin && onAutoJoinCurrent != null) {
                PressableButton(
                    text = "自动接单",
                    onClick = onAutoJoinCurrent,
                    colors = ButtonDefaults.buttonColors(containerColor = PhoneColors.Red, contentColor = Color.White),
                    modifier = Modifier.fillMaxWidth(),
                )
            }
            PressableButton(
                text = "演示备用：新建事件",
                onClick = onCreateIncident,
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF334155), contentColor = Color.White),
                modifier = Modifier.fillMaxWidth(),
            )
        }
    }
}
