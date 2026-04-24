package com.example.lifereflexarc.ui.screens

import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.lifereflexarc.ui.components.PressableButton
import com.example.lifereflexarc.ui.theme.PhoneColors
import com.example.lifereflexarc.ui.theme.PhoneTokens

@Composable
fun SosCountdownScreen(seconds: Int, totalSeconds: Int, onCancel: () -> Unit) {
    val progress by animateFloatAsState(
        targetValue = (seconds.coerceAtLeast(0) / totalSeconds.coerceAtLeast(1).toFloat()).coerceIn(0f, 1f),
        label = "progress"
    )

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(PhoneColors.Black)
            .padding(horizontal = PhoneTokens.ScreenPadding),
        verticalArrangement = Arrangement.SpaceBetween,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text("14:00", color = PhoneColors.GrayText, fontSize = PhoneTokens.Caption)
            Text("5G 100%", color = PhoneColors.GrayText, fontSize = PhoneTokens.Caption)
        }
        Spacer(modifier = Modifier.height(12.dp))
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Canvas(modifier = Modifier.size(220.dp)) {
                drawArc(
                    color = Color(0xFF334155),
                    startAngle = -90f,
                    sweepAngle = 360f,
                    useCenter = false,
                    style = Stroke(width = 18f, cap = StrokeCap.Round)
                )
                drawArc(
                    color = Color(0xFFEF4444),
                    startAngle = -90f,
                    sweepAngle = 360f * progress,
                    useCenter = false,
                    style = Stroke(width = 18f, cap = StrokeCap.Round)
                )
            }
            Text("${seconds.coerceAtLeast(0)}", color = Color.White, fontSize = 64.sp, fontWeight = FontWeight.Bold)
            Text("SOS 告警", color = Color(0xFFEF4444), fontSize = PhoneTokens.Body)
            Spacer(modifier = Modifier.height(8.dp))
            Text("检测到异常倒地\n即将自动呼叫急救", color = PhoneColors.GrayText, fontSize = PhoneTokens.Body)
        }

        PressableButton(
            text = "我没事 (取消)",
            onClick = onCancel,
            colors = androidx.compose.material3.ButtonDefaults.buttonColors(containerColor = PhoneColors.Slate),
            modifier = Modifier.padding(bottom = 12.dp)
        )
    }
}

@androidx.compose.ui.tooling.preview.Preview(showBackground = true)
@Composable
private fun SosCountdownPreview() {
    SosCountdownScreen(seconds = 7, totalSeconds = 10, onCancel = {})
}
