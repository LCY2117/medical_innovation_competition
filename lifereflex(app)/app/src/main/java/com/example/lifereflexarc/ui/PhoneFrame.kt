package com.example.lifereflexarc.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.lifereflexarc.ui.components.StatusLight
import com.example.lifereflexarc.ui.theme.PhoneColors
import com.example.lifereflexarc.ui.theme.PhoneTokens

@Composable
fun PhoneFrame(
    connected: Boolean,
    incidentId: String?,
    content: @Composable () -> Unit,
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        modifier = Modifier.fillMaxSize().padding(16.dp)
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            StatusLight(isConnected = connected)
            Text(
                text = if (connected) "实时同步" else "离线",
                color = PhoneColors.GrayText,
                fontSize = 12.sp
            )
        }

        Spacer(modifier = Modifier.width(8.dp))

        Text(
            text = if (incidentId != null) "事件：${incidentId.take(8)}" else "事件：--",
            color = if (incidentId != null) PhoneColors.White else PhoneColors.GrayText,
            fontSize = 12.sp,
            fontWeight = FontWeight.Bold,
            modifier = Modifier.padding(top = 6.dp)
        )

        Box(
            modifier = Modifier
                .width(PhoneTokens.PhoneWidth)
                .height(PhoneTokens.PhoneHeight)
                .clip(RoundedCornerShape(PhoneTokens.PhoneRadius))
                .background(PhoneColors.Black)
                .border(6.dp, Color(0xFF1F2937), RoundedCornerShape(PhoneTokens.PhoneRadius))
                .padding(10.dp)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .clip(RoundedCornerShape(PhoneTokens.InnerRadius))
                    .background(PhoneColors.Black)
            ) {
                // Status bar
                Row(
                    modifier = Modifier
                        .fillMaxSize()
                        .weight(0.08f)
                        .padding(horizontal = 12.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Text("14:00", color = PhoneColors.White, fontSize = 10.sp)
                    Text("5G 100%", color = PhoneColors.White, fontSize = 10.sp)
                }

                Column(
                    modifier = Modifier
                        .weight(0.92f)
                        .fillMaxSize()
                        .clip(RoundedCornerShape(PhoneTokens.InnerRadius))
                        .background(Color(0xFF0B1220))
                        .padding(8.dp)
                ) {
                    content()
                }
            }
        }
    }
}
