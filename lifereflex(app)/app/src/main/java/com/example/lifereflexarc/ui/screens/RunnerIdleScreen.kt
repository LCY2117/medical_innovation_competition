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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.lifereflexarc.ui.components.PressableButton
import com.example.lifereflexarc.ui.theme.PhoneColors
import com.example.lifereflexarc.ui.theme.PhoneTokens

@Composable
fun RunnerIdleScreen(onJoin: () -> Unit) {
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
                    .background(PhoneColors.Blue, RoundedCornerShape(18.dp))
                    .padding(horizontal = 16.dp, vertical = 12.dp)
            ) {
                Text("⚡  AED 保障响应", color = PhoneColors.White, fontSize = 14.sp, fontWeight = FontWeight.Bold)
                Text("就近取用 AED，赶赴现场", color = PhoneColors.BlueSoft, fontSize = PhoneTokens.Body)
            }
            Spacer(modifier = Modifier.height(22.dp))
            Text("资源保障任务", color = PhoneColors.White, fontSize = PhoneTokens.Title, fontWeight = FontWeight.Bold)
            Spacer(modifier = Modifier.height(6.dp))
            Text("当前状态：待命", color = PhoneColors.GrayText, fontSize = PhoneTokens.Body)
        }

        PressableButton(
            text = "立即响应（AED保障）",
            onClick = onJoin,
            colors = androidx.compose.material3.ButtonDefaults.buttonColors(containerColor = PhoneColors.Blue)
        )
    }
}

@androidx.compose.ui.tooling.preview.Preview(showBackground = true)
@Composable
private fun RunnerIdlePreview() {
    RunnerIdleScreen(onJoin = {})
}
