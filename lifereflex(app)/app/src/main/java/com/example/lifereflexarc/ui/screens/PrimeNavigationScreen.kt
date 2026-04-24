package com.example.lifereflexarc.ui.screens

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
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
fun PrimeNavigationScreen(onArrived: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(PhoneColors.Navy)
            .padding(PhoneTokens.ScreenPadding),
        verticalArrangement = Arrangement.SpaceBetween,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Box(contentAlignment = Alignment.Center) {
                Canvas(modifier = Modifier.size(220.dp)) {
                    drawCircle(
                        color = Color(0xFF1E293B),
                        style = Stroke(width = 10f, cap = StrokeCap.Round)
                    )
                    drawCircle(color = Color(0xFF0F172A), radius = size.minDimension * 0.45f)
                }
                Text("↑", color = PhoneColors.GreenSoft, fontSize = 56.sp, fontWeight = FontWeight.Bold)
                Box(
                    modifier = Modifier
                        .size(56.dp)
                        .offset(x = 80.dp, y = (-80).dp)
                        .background(Color(0x3322C55E), RoundedCornerShape(12.dp)),
                    contentAlignment = Alignment.Center
                ) {
                    Box(
                        modifier = Modifier
                            .size(10.dp)
                            .background(PhoneColors.GreenSoft, RoundedCornerShape(6.dp))
                    )
                }
            }
            Spacer(modifier = Modifier.height(18.dp))
            Row(verticalAlignment = Alignment.Bottom) {
                Text("15", color = PhoneColors.White, fontSize = 52.sp, fontWeight = FontWeight.Bold)
                Spacer(modifier = Modifier.width(4.dp))
                Text("m", color = PhoneColors.GrayText, fontSize = PhoneTokens.Body)
            }
            Spacer(modifier = Modifier.height(6.dp))
            Text("AHEAD", color = PhoneColors.GreenSoft, fontWeight = FontWeight.Bold)
        }

        PressableButton(
            text = "我已到达 (Start CPR)",
            onClick = onArrived,
            colors = androidx.compose.material3.ButtonDefaults.buttonColors(containerColor = PhoneColors.Green)
        )
    }
}

@androidx.compose.ui.tooling.preview.Preview(showBackground = true)
@Composable
private fun PrimeNavigationPreview() {
    PrimeNavigationScreen(onArrived = {})
}
