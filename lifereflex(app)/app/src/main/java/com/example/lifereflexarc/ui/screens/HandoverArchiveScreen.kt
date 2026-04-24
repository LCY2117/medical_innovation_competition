package com.example.lifereflexarc.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.graphics.PathEffect
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.lifereflexarc.ui.theme.PhoneColors
import com.example.lifereflexarc.ui.theme.PhoneTokens

@Composable
fun HandoverArchiveScreen() {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(PhoneColors.White)
            .padding(PhoneTokens.ScreenPadding),
        verticalArrangement = Arrangement.Top,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Spacer(modifier = Modifier.height(18.dp))
        Box(
            modifier = Modifier
                .size(72.dp)
                .background(Color(0xFFD1FAE5), CircleShape),
            contentAlignment = Alignment.Center
        ) {
            Text("✓", color = PhoneColors.Green, fontSize = 28.sp, fontWeight = FontWeight.Bold)
        }
        Spacer(modifier = Modifier.height(16.dp))
        Text("任务归档", color = PhoneColors.Navy, fontSize = PhoneTokens.Title, fontWeight = FontWeight.Bold)
        Spacer(modifier = Modifier.height(6.dp))
        Text("救护车已接管患者", color = PhoneColors.GrayText, fontSize = PhoneTokens.Body)
        Spacer(modifier = Modifier.height(18.dp))

        Box(
            modifier = Modifier
                .background(PhoneColors.White, RoundedCornerShape(PhoneTokens.CardRadiusMd))
                .drawBehind {
                    val stroke = 2f
                    val radius = 16f
                    val dash = PathEffect.dashPathEffect(floatArrayOf(12f, 10f), 0f)
                    drawRoundRect(
                        color = Color(0xFF93C5FD),
                        size = size,
                        cornerRadius = CornerRadius(radius, radius),
                        style = androidx.compose.ui.graphics.drawscope.Stroke(width = stroke, pathEffect = dash)
                    )
                }
                .padding(20.dp),
            contentAlignment = Alignment.Center
        ) {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Box(
                    modifier = Modifier
                        .size(56.dp)
                        .background(Color(0xFFE0E7FF), CircleShape),
                    contentAlignment = Alignment.Center
                ) {
                    Text("📄", fontSize = 20.sp)
                }
                Spacer(modifier = Modifier.height(8.dp))
                Text("NFC 触碰传输", color = PhoneColors.Navy, fontSize = 16.sp, fontWeight = FontWeight.Bold)
                Text("靠近急救员终端传输日志", color = PhoneColors.GrayText, fontSize = PhoneTokens.Body)
            }
        }

        Spacer(modifier = Modifier.height(18.dp))
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .background(Color(0xFFF8FAFC), RoundedCornerShape(PhoneTokens.CardRadiusMd))
                .padding(12.dp)
        ) {
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text("总耗时", color = PhoneColors.GrayText, fontSize = PhoneTokens.Body)
                Text("04:35", color = PhoneColors.Navy, fontSize = PhoneTokens.Body, fontWeight = FontWeight.Bold)
            }
            Spacer(modifier = Modifier.height(8.dp))
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text("协同人数", color = PhoneColors.GrayText, fontSize = PhoneTokens.Body)
                Text("3人", color = PhoneColors.Navy, fontSize = PhoneTokens.Body, fontWeight = FontWeight.Bold)
            }
            Spacer(modifier = Modifier.height(8.dp))
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text("AED使用", color = PhoneColors.GrayText, fontSize = PhoneTokens.Body)
                Text("成功（1 次）", color = PhoneColors.Green, fontSize = PhoneTokens.Body, fontWeight = FontWeight.Bold)
            }
        }
    }
}

@androidx.compose.ui.tooling.preview.Preview(showBackground = true)
@Composable
private fun HandoverArchivePreview() {
    HandoverArchiveScreen()
}
