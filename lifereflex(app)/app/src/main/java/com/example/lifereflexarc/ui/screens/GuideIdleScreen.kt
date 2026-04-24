package com.example.lifereflexarc.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
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
fun GuideIdleScreen(onJoin: () -> Unit) {
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
                    .background(PhoneColors.Yellow, RoundedCornerShape(18.dp))
                    .padding(horizontal = 16.dp, vertical = 12.dp)
            ) {
                Text("🛡  环境清障响应", color = PhoneColors.Black, fontSize = 14.sp, fontWeight = FontWeight.Bold)
                Text("疏通通道，迎接急救车", color = Color(0xFF7C2D12), fontSize = PhoneTokens.Body)
            }
            Spacer(modifier = Modifier.height(22.dp))
            Text("环境清障任务", color = PhoneColors.White, fontSize = PhoneTokens.Title, fontWeight = FontWeight.Bold)
            Spacer(modifier = Modifier.height(6.dp))
            Text("当前状态：待命", color = PhoneColors.GrayText, fontSize = PhoneTokens.Body)
        }

        PressableButton(
            text = "立即响应（环境清障）",
            onClick = onJoin,
            colors = androidx.compose.material3.ButtonDefaults.buttonColors(containerColor = PhoneColors.Yellow)
        )
    }
}

@androidx.compose.ui.tooling.preview.Preview(showBackground = true)
@Composable
private fun GuideIdlePreview() {
    GuideIdleScreen(onJoin = {})
}
