package com.example.lifereflexarc.ui.screens

import androidx.compose.foundation.Canvas
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
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.lifereflexarc.ui.components.PressableButton
import com.example.lifereflexarc.ui.theme.PhoneColors
import com.example.lifereflexarc.ui.theme.PhoneTokens

@Composable
fun CprMetronomeScreen(onCprStarted: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(PhoneColors.Black)
            .padding(PhoneTokens.ScreenPadding),
        verticalArrangement = Arrangement.SpaceBetween,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Text("CPR METRONOME", color = PhoneColors.GrayText, fontSize = PhoneTokens.Caption)
            Spacer(modifier = Modifier.height(12.dp))
            Box(contentAlignment = Alignment.Center) {
                Canvas(modifier = Modifier.size(220.dp)) {
                    drawCircle(
                        color = PhoneColors.Navy,
                        style = Stroke(width = 12f, cap = StrokeCap.Round)
                    )
                }
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text("100", color = PhoneColors.Green, fontSize = 60.sp, fontWeight = FontWeight.Bold)
                    Text("BPM", color = PhoneColors.Green, fontSize = 12.sp)
                }
            }
            Spacer(modifier = Modifier.height(10.dp))
            Text("保持按压频率", color = PhoneColors.GrayText, fontSize = PhoneTokens.Body)
            Text("深度 5-6cm", color = PhoneColors.Green, fontSize = PhoneTokens.Body)
        }

        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Text("AI VOICE ASSISTANT ACTIVE", color = PhoneColors.GrayText, fontSize = PhoneTokens.Caption)
            Spacer(modifier = Modifier.height(10.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                PressableButton(
                    text = "开始CPR",
                    onClick = onCprStarted,
                    colors = androidx.compose.material3.ButtonDefaults.buttonColors(containerColor = PhoneColors.Slate),
                    modifier = Modifier
                        .fillMaxWidth(0.48f)
                        .height(54.dp)
                )
                PressableButton(
                    text = "呼叫替补",
                    onClick = {},
                    colors = androidx.compose.material3.ButtonDefaults.buttonColors(containerColor = PhoneColors.Slate),
                    modifier = Modifier
                        .fillMaxWidth(0.48f)
                        .height(54.dp)
                )
            }
        }
    }
}

@androidx.compose.ui.tooling.preview.Preview(showBackground = true)
@Composable
private fun CprMetronomePreview() {
    CprMetronomeScreen(onCprStarted = {})
}
