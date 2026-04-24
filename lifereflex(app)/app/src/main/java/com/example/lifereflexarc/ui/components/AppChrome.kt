@file:OptIn(androidx.compose.foundation.layout.ExperimentalLayoutApi::class)

package com.example.lifereflexarc.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.lifereflexarc.data.IncidentState
import com.example.lifereflexarc.data.UserRole
import com.example.lifereflexarc.data.UserSession
import com.example.lifereflexarc.ui.accentForRole
import com.example.lifereflexarc.ui.phaseTitle
import com.example.lifereflexarc.ui.rememberElapsedLabel
import com.example.lifereflexarc.ui.theme.PhoneColors

@Composable
fun AppTopBar(
    session: UserSession,
    incidentState: IncidentState?,
    connected: Boolean,
    connecting: Boolean,
    assignedRole: UserRole?,
) {
    val elapsedLabel = rememberElapsedLabel(incidentState?.logs?.firstOrNull()?.ts)

    Card(
        colors = CardDefaults.cardColors(containerColor = Color(0xFF0F172A)),
        shape = RoundedCornerShape(24.dp),
        border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFF1E293B)),
        modifier = Modifier.fillMaxWidth(),
    ) {
        Column(modifier = Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    Text(
                        text = "生命反射弧",
                        color = Color.White,
                        fontSize = 24.sp,
                        fontWeight = FontWeight.Bold,
                    )
                    Text(
                        text = "院前急救分布式协同终端",
                        color = PhoneColors.GrayText,
                        fontSize = 12.sp,
                    )
                }
                StatusTag(
                    text = when {
                        connecting -> "同步中"
                        connected -> "实时同步"
                        else -> "离线"
                    },
                    background = if (connected) Color(0xFF052E16) else Color(0xFF3F1D1D),
                    foreground = if (connected) PhoneColors.GreenSoft else PhoneColors.RedSoft,
                )
            }

            FlowRow(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                if (assignedRole != null) {
                    StatChip("任务角色", assignedRole.label, accentForRole(assignedRole))
                } else {
                    StatChip("职业画像", session.professionIdentity.label, Color(0xFF3B82F6))
                }
                StatChip("阶段", phaseTitle(incidentState?.phase), Color(0xFF1D4ED8))
                StatChip("耗时", elapsedLabel, Color(0xFF0F766E))
            }
        }
    }
}

@Composable
fun ActiveIncidentBanner(
    incidentState: IncidentState,
    assignedRole: UserRole?,
    onOpenIncident: () -> Unit,
) {
    Card(
        colors = CardDefaults.cardColors(containerColor = Color(0xFF111827)),
        shape = RoundedCornerShape(22.dp),
        border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFF1F2937)),
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onOpenIncident() },
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text("活动事件", color = PhoneColors.GrayText, fontSize = 11.sp)
                Text(
                    text = "正在协同处置 · ${phaseTitle(incidentState.phase)}",
                    color = Color.White,
                    fontWeight = FontWeight.Bold,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                )
            }
            StatusTag(
                text = assignedRole?.label ?: "待智能分派",
                background = (assignedRole?.let(::accentForRole) ?: Color(0xFF1E3A8A)).copy(alpha = 0.12f),
                foreground = assignedRole?.let(::accentForRole) ?: Color(0xFF93C5FD),
            )
        }
    }
}

@Composable
fun SectionTitle(title: String) {
    Text(title, color = Color.White, fontSize = 20.sp, fontWeight = FontWeight.Bold)
}

@Composable
fun StatusTag(
    text: String,
    background: Color,
    foreground: Color,
) {
    Text(
        text = text,
        color = foreground,
        fontSize = 11.sp,
        fontWeight = FontWeight.Bold,
        modifier = Modifier
            .clip(RoundedCornerShape(999.dp))
            .background(background)
            .padding(horizontal = 10.dp, vertical = 6.dp),
    )
}

@Composable
fun StatChip(
    label: String,
    value: String,
    accent: Color,
) {
    Row(
        verticalAlignment = Alignment.CenterVertically,
        modifier = Modifier
            .clip(RoundedCornerShape(999.dp))
            .background(Color(0xFF0B1223))
            .border(1.dp, accent.copy(alpha = 0.25f), RoundedCornerShape(999.dp))
            .padding(horizontal = 10.dp, vertical = 8.dp),
    ) {
        Text("$label ", color = PhoneColors.GrayText, fontSize = 11.sp)
        Text(value, color = Color.White, fontWeight = FontWeight.Bold, fontSize = 11.sp)
    }
}

@Composable
fun MetricCard(
    label: String,
    value: String,
    accent: Color,
    modifier: Modifier = Modifier,
) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(containerColor = Color(0xFF0F172A)),
        shape = RoundedCornerShape(22.dp),
        border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFF1E293B)),
    ) {
        Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text(label, color = PhoneColors.GrayText, fontSize = 11.sp)
            Text(value, color = Color.White, fontWeight = FontWeight.Bold, maxLines = 1, overflow = TextOverflow.Ellipsis)
            Box(
                modifier = Modifier
                    .height(4.dp)
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(999.dp))
                    .background(accent)
            )
        }
    }
}

@Composable
fun RoleModuleCard(
    title: String,
    body: String,
    accent: Color,
    modifier: Modifier = Modifier,
) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(containerColor = Color(0xFF0F172A)),
        shape = RoundedCornerShape(22.dp),
        border = androidx.compose.foundation.BorderStroke(1.dp, accent.copy(alpha = 0.35f)),
    ) {
        Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Box(
                modifier = Modifier
                    .size(12.dp)
                    .clip(CircleShape)
                    .background(accent)
            )
            Text(title, color = Color.White, fontWeight = FontWeight.Bold)
            Text(body, color = PhoneColors.GrayText, fontSize = 12.sp, lineHeight = 18.sp)
        }
    }
}

@Composable
fun EmptyStateCard(
    title: String,
    body: String,
) {
    Card(
        colors = CardDefaults.cardColors(containerColor = Color(0xFF0F172A)),
        shape = RoundedCornerShape(28.dp),
        border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFF1E293B)),
    ) {
        Column(modifier = Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text(title, color = Color.White, fontSize = 20.sp, fontWeight = FontWeight.Bold)
            Text(body, color = PhoneColors.GrayText, fontSize = 14.sp, lineHeight = 22.sp)
        }
    }
}

@Composable
fun InlineErrorCard(message: String) {
    Card(
        colors = CardDefaults.cardColors(containerColor = Color(0xFF3F1D1D)),
        shape = RoundedCornerShape(18.dp),
        border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFF7F1D1D)),
        modifier = Modifier.fillMaxWidth(),
    ) {
        Text(
            text = message,
            color = PhoneColors.RedSoft,
            modifier = Modifier.padding(14.dp),
            fontSize = 13.sp,
            lineHeight = 20.sp,
        )
    }
}

@Composable
fun SummaryRow(label: String, value: String, dark: Boolean = false) {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text(label, color = if (dark) PhoneColors.GrayText else Color(0xFF64748B), fontSize = 13.sp)
            Text(
                value,
                color = if (dark) Color.White else Color(0xFF0F172A),
                fontWeight = FontWeight.Bold,
                fontSize = 14.sp,
            )
        }
        HorizontalDivider(color = if (dark) Color(0xFF1E293B) else Color(0xFFE2E8F0))
    }
}
