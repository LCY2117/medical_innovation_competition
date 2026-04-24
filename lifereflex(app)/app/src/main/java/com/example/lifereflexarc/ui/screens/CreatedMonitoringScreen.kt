package com.example.lifereflexarc.ui.screens

import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
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
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
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
fun CreatedMonitoringScreen(onConfirm: () -> Unit) {
    val transition = rememberInfiniteTransition(label = "bars")
    val pulse by transition.animateFloat(
        initialValue = 0.8f,
        targetValue = 1.0f,
        animationSpec = infiniteRepeatable(tween(900), RepeatMode.Reverse),
        label = "pulse",
    )
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(PhoneColors.Black)
            .padding(PhoneTokens.ScreenPadding),
        verticalArrangement = Arrangement.SpaceBetween,
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text("14:00", color = PhoneColors.GrayText, fontSize = PhoneTokens.Caption)
            Text("5G 100%", color = PhoneColors.GrayText, fontSize = PhoneTokens.Caption)
        }

        Spacer(modifier = Modifier.height(8.dp))

        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween,
            modifier = Modifier.fillMaxWidth()
        ) {
            Text(
                "健康守护",
                color = PhoneColors.GrayText,
                fontSize = PhoneTokens.Caption,
                fontWeight = FontWeight.Bold
            )
            Text("❤", color = PhoneColors.GreenSoft, fontSize = 14.sp)
        }

        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Row(
                verticalAlignment = Alignment.Bottom,
                horizontalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                val heights = listOf(8, 12, 10, 14, 12, 18, 26, 34, 18, 12, 10, 8)
                heights.forEachIndexed { index, h ->
                    val alpha = if (index >= heights.size - 3) 0.4f else 1f
                    Column(
                        modifier = Modifier
                            .width(6.dp)
                            .height((h * pulse).dp)
                            .background(Color(0xFFDC2626).copy(alpha = alpha))
                            .padding(0.dp)
                    ) {}
                }
            }
            Spacer(modifier = Modifier.height(18.dp))
            Row(verticalAlignment = Alignment.Bottom) {
                Text("86", color = Color.White, fontSize = 48.sp, fontWeight = FontWeight.Bold)
                Spacer(modifier = Modifier.width(6.dp))
                Text("BPM", color = PhoneColors.GrayText, fontSize = PhoneTokens.Body)
            }
            Text("监测中...", color = PhoneColors.GrayText, fontSize = PhoneTokens.Body, modifier = Modifier.padding(top = 6.dp))
        }

        PressableButton(
            text = "异常确认",
            onClick = onConfirm,
            colors = androidx.compose.material3.ButtonDefaults.buttonColors(containerColor = PhoneColors.Slate),
            modifier = Modifier.padding(bottom = 8.dp)
        )
    }
}

@androidx.compose.ui.tooling.preview.Preview(showBackground = true)
@Composable
private fun CreatedMonitoringPreview() {
    CreatedMonitoringScreen(onConfirm = {})
}
