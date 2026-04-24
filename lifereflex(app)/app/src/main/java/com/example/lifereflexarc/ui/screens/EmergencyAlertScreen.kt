package com.example.lifereflexarc.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.lifereflexarc.ui.components.PressableButton
import com.example.lifereflexarc.ui.theme.PhoneColors
import com.example.lifereflexarc.ui.theme.PhoneTokens

@Composable
fun EmergencyAlertScreen(
    incidentId: String,
    onJoin: () -> Unit,
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(PhoneColors.Black)
            .padding(PhoneTokens.ScreenPadding),
        verticalArrangement = Arrangement.SpaceBetween,
    ) {
        Column(modifier = Modifier.fillMaxWidth()) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(PhoneColors.Red, RoundedCornerShape(PhoneTokens.CardRadiusLg))
                    .padding(horizontal = 18.dp, vertical = 18.dp)
            ) {
                Text("一级危急（SCA）", color = PhoneColors.RedSoft, fontSize = PhoneTokens.Body, fontWeight = FontWeight.SemiBold)
                Text("ID: $incidentId", color = PhoneColors.RedSoft, fontSize = 10.sp)
                Spacer(modifier = Modifier.height(12.dp))
                Text("附近有人\n心脏骤停", color = Color.White, fontSize = PhoneTokens.TitleXL, fontWeight = FontWeight.Bold)
                Spacer(modifier = Modifier.height(8.dp))
                Text("距离您 150 米 • 购物中心中庭", color = PhoneColors.RedSoft, fontSize = PhoneTokens.Body)
            }

            Spacer(modifier = Modifier.height(20.dp))

            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 6.dp)
                    .background(PhoneColors.Navy, RoundedCornerShape(PhoneTokens.CardRadiusMd))
                    .padding(horizontal = 20.dp, vertical = 18.dp)
            ) {
                Text("黄金救援时间", color = PhoneColors.GrayText, fontSize = 11.sp)
                Spacer(modifier = Modifier.height(6.dp))
                Text("3:30", color = Color(0xFFFACC15), fontSize = 52.sp, fontWeight = FontWeight.Bold)
                Spacer(modifier = Modifier.height(4.dp))
                Text("刻不容缓，请立即前往！", color = PhoneColors.RedSoft, fontSize = 12.sp)
            }
        }

        Column {
            Spacer(modifier = Modifier.height(14.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                PressableButton(
                    text = "无法前往",
                    onClick = {},
                    colors = ButtonDefaults.buttonColors(containerColor = PhoneColors.Slate),
                    modifier = Modifier.fillMaxWidth(0.48f)
                )
                PressableButton(
                    text = "立即响应",
                    onClick = onJoin,
                    colors = ButtonDefaults.buttonColors(containerColor = PhoneColors.Red),
                    modifier = Modifier.fillMaxWidth(0.48f)
                )
            }
        }
    }
}

@androidx.compose.ui.tooling.preview.Preview(showBackground = true)
@Composable
private fun EmergencyAlertPreview() {
    EmergencyAlertScreen(incidentId = "demo-id", onJoin = {})
}
