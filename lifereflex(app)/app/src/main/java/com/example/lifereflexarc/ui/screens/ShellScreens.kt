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
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.lifereflexarc.data.IncidentState
import com.example.lifereflexarc.data.IncidentArchiveEntry
import com.example.lifereflexarc.data.UserRole
import com.example.lifereflexarc.data.UserSession
import com.example.lifereflexarc.ui.accentForRole
import com.example.lifereflexarc.ui.components.EmptyStateCard
import com.example.lifereflexarc.ui.components.MetricCard
import com.example.lifereflexarc.ui.components.PressableButton
import com.example.lifereflexarc.ui.components.SectionTitle
import com.example.lifereflexarc.ui.components.SummaryRow
import com.example.lifereflexarc.ui.theme.PhoneColors
import com.example.lifereflexarc.viewmodel.IncidentViewModel

@Composable
fun CommandHomeScreen(
    session: UserSession,
    incidentState: IncidentState?,
    connected: Boolean,
    assignedRole: UserRole?,
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
                        "当前无活动急救事件，可以发起监测、创建事件或接入现场。"
                    } else {
                        "当前存在活动事件，建议直接进入事件页处理实时任务。"
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
        )

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
    deviceUserId: String,
    incidentViewModel: IncidentViewModel,
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
        MissionPanel(
            session = session,
            incidentState = incidentState,
            assignedRole = assignedRole,
            deviceUserId = deviceUserId,
            incidentViewModel = incidentViewModel,
        )
        if (incidentState.phase != "ARCHIVED") {
            Card(
                colors = CardDefaults.cardColors(containerColor = Color(0xFF0F172A)),
                shape = androidx.compose.foundation.shape.RoundedCornerShape(24.dp),
                border = BorderStroke(1.dp, Color(0xFF1E293B)),
            ) {
                Column(modifier = Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Text("现场协同", color = Color.White, fontSize = 18.sp, fontWeight = FontWeight.SemiBold)
                    SummaryRow("核心施救", incidentState.roles.PRIME.status ?: "待命", dark = true)
                    SummaryRow("AED保障", incidentState.roles.RUNNER.status ?: "待命", dark = true)
                    SummaryRow("环境清障", incidentState.roles.GUIDE.status ?: "待命", dark = true)
                }
            }
        }
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
                    SummaryRow("任务来源", entry.dispatchSource, dark = entry.isPatient)
                    SummaryRow("处置时长", "${entry.durationSec / 60} 分 ${entry.durationSec % 60} 秒", dark = entry.isPatient)
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
                text = "支持新建事件和进入当前事件。患者触发、角色分派和整体调度都由网页指挥台完成。",
                color = PhoneColors.GrayText,
                fontSize = 13.sp,
                lineHeight = 20.sp,
            )

            PressableButton(
                text = "新建事件",
                onClick = onCreateIncident,
                colors = ButtonDefaults.buttonColors(containerColor = PhoneColors.Green, contentColor = Color.White),
                modifier = Modifier.fillMaxWidth(),
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
        }
    }
}
