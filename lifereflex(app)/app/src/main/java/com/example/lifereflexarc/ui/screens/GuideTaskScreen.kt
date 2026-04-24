package com.example.lifereflexarc.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.lifereflexarc.ui.components.PressableButton
import com.example.lifereflexarc.ui.theme.PhoneColors
import com.example.lifereflexarc.ui.theme.PhoneTokens

@Composable
fun GuideTaskScreen(onAmbulanceArrived: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(PhoneColors.Navy)
            .padding(PhoneTokens.ScreenPadding),
        verticalArrangement = Arrangement.SpaceBetween,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(PhoneColors.Yellow, RoundedCornerShape(PhoneTokens.CardRadiusMd))
                    .padding(horizontal = 16.dp, vertical = 12.dp)
            ) {
                Text("🛡  环境清障任务", color = PhoneColors.Black, fontSize = 14.sp, fontWeight = FontWeight.Bold)
                Text("任务 ID: #CLR-8823", color = Color(0xFF7C2D12), fontSize = PhoneTokens.Body)
            }
            Spacer(modifier = Modifier.height(26.dp))
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Box(
                    modifier = Modifier
                        .size(72.dp)
                        .background(Color(0x33251A00), RoundedCornerShape(36.dp)),
                    contentAlignment = Alignment.Center
                ) {
                    Text("⚠", color = PhoneColors.Yellow, fontSize = 36.sp)
                }
                Spacer(modifier = Modifier.height(10.dp))
                Text("疏散入口车辆", color = PhoneColors.White, fontSize = PhoneTokens.Title, fontWeight = FontWeight.Bold)
                Spacer(modifier = Modifier.height(6.dp))
                Text("请保持消防通道畅通", color = PhoneColors.GrayText, fontSize = PhoneTokens.Body)
            }
            Spacer(modifier = Modifier.height(18.dp))
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(PhoneColors.Slate, RoundedCornerShape(PhoneTokens.CardRadiusMd))
                    .padding(14.dp)
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text("\uD83D\uDD14", color = PhoneColors.Yellow)
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("120 急救车接近中", color = PhoneColors.White, fontSize = 12.sp)
                    }
                    Box(
                        modifier = Modifier
                            .background(Color(0xFF2A1F04), RoundedCornerShape(10.dp))
                            .padding(horizontal = 8.dp, vertical = 4.dp)
                    ) {
                        Text("B-120Q", color = PhoneColors.YellowSoft, fontSize = 11.sp)
                    }
                }
                Spacer(modifier = Modifier.height(8.dp))
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(Color(0xFF1E293B), RoundedCornerShape(10.dp))
                        .height(8.dp)
                ) {
                    Spacer(
                        modifier = Modifier
                            .fillMaxWidth(0.3f)
                            .background(Color(0xFFEF4444), RoundedCornerShape(10.dp))
                            .height(8.dp)
                    )
                }
                Spacer(modifier = Modifier.height(10.dp))
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("3 公里", color = PhoneColors.GrayText, fontSize = 11.sp)
                    Text("到达中", color = PhoneColors.GrayText, fontSize = 11.sp)
                }
            }
        }

        PressableButton(
            text = "救护车已到达",
            onClick = onAmbulanceArrived,
            colors = androidx.compose.material3.ButtonDefaults.buttonColors(containerColor = PhoneColors.Yellow)
        )
    }
}

@androidx.compose.ui.tooling.preview.Preview(showBackground = true)
@Composable
private fun GuideTaskPreview() {
    GuideTaskScreen(onAmbulanceArrived = {})
}
