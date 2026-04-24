package com.example.lifereflexarc.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.Box
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
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.PathEffect
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.lifereflexarc.ui.components.PressableButton
import com.example.lifereflexarc.ui.theme.PhoneColors
import com.example.lifereflexarc.ui.theme.PhoneTokens

@Composable
fun AedDeliveryScreen(
    phase: String,
    onAedPicked: () -> Unit,
    onAedDelivered: () -> Unit,
) {
    val isReturning = phase == "AED_PICKED"
    val isDelivered = phase == "AED_DELIVERED"
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(PhoneColors.White)
            .padding(PhoneTokens.ScreenPadding),
        verticalArrangement = Arrangement.SpaceBetween,
    ) {
        Column {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(PhoneColors.Blue, RoundedCornerShape(PhoneTokens.CardRadiusMd))
                    .padding(horizontal = 16.dp, vertical = 14.dp)
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text("⚡", color = PhoneColors.White, fontSize = 14.sp)
                    Spacer(modifier = Modifier.width(6.dp))
                    Text("AED 紧急配送", color = PhoneColors.White, fontSize = 14.sp, fontWeight = FontWeight.Bold)
                }
                Text("目标：二楼服务台 AED箱", color = PhoneColors.BlueSoft, fontSize = PhoneTokens.Body)
            }

            Spacer(modifier = Modifier.height(12.dp))

            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(PhoneColors.White, RoundedCornerShape(PhoneTokens.CardRadiusMd))
                    .padding(10.dp)
            ) {
                Box(
                    modifier = Modifier
                        .background(Color(0xFFE2E8F0), RoundedCornerShape(PhoneTokens.CardRadiusMd))
                        .height(200.dp)
                        .fillMaxWidth()
                ) {
                    Canvas(modifier = Modifier.fillMaxSize()) {
                        val path = Path().apply {
                            moveTo(size.width * 0.3f, size.height * 0.75f)
                            quadraticTo(
                                size.width * 0.45f,
                                size.height * 0.5f,
                                size.width * 0.75f,
                                size.height * 0.2f
                            )
                        }
                        drawPath(
                            path = path,
                            color = PhoneColors.Blue,
                            style = Stroke(
                                width = 6f,
                                cap = StrokeCap.Round,
                                pathEffect = PathEffect.dashPathEffect(floatArrayOf(10f, 10f))
                            )
                        )
                        drawCircle(color = PhoneColors.Blue, radius = 10f, center = Offset(size.width * 0.32f, size.height * 0.72f))
                        drawCircle(color = Color.White, radius = 6f, center = Offset(size.width * 0.32f, size.height * 0.72f))
                        drawCircle(color = PhoneColors.Blue, radius = 12f, center = Offset(size.width * 0.78f, size.height * 0.22f))
                        drawCircle(color = Color.White, radius = 6f, center = Offset(size.width * 0.78f, size.height * 0.22f))
                    }
                    Text(
                        "现场地图",
                        color = PhoneColors.GrayText.copy(alpha = 0.4f),
                        fontSize = 24.sp,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.align(Alignment.Center)
                    )
                    Box(
                        modifier = Modifier
                            .align(Alignment.TopEnd)
                            .padding(10.dp)
                            .background(PhoneColors.Blue, RoundedCornerShape(PhoneTokens.ButtonRadius))
                            .padding(horizontal = 8.dp, vertical = 4.dp)
                    ) {
                        Text("AED (二楼)", color = PhoneColors.White, fontSize = 11.sp)
                    }
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            Column(
                modifier = Modifier
                    .background(PhoneColors.White, RoundedCornerShape(PhoneTokens.CardRadiusMd))
                    .padding(16.dp)
            ) {
                Row(horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
                    Column {
                        Text("状态", color = PhoneColors.GrayText, fontSize = PhoneTokens.Caption)
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            text = when {
                                isDelivered -> "AED 已送达患者"
                                isReturning -> "正在赶回患者位置"
                                else -> "正在前往取件"
                            },
                            color = PhoneColors.Navy,
                            fontSize = 16.sp,
                            fontWeight = FontWeight.Bold
                        )
                    }
                    Column(horizontalAlignment = Alignment.End) {
                        Text("30s", color = PhoneColors.Blue, fontSize = 16.sp, fontWeight = FontWeight.Bold)
                        Text("预计到达", color = PhoneColors.GrayText, fontSize = PhoneTokens.Caption)
                    }
                }
                Spacer(modifier = Modifier.height(12.dp))
                PressableButton(
                    text = when {
                        isDelivered -> "已送达"
                        isReturning -> "到达患者位置"
                        else -> "到达 AED 位置"
                    },
                    onClick = {
                        if (!isDelivered) {
                            if (isReturning) {
                                onAedDelivered()
                            } else {
                                onAedPicked()
                            }
                        }
                    },
                    enabled = !isDelivered,
                    colors = androidx.compose.material3.ButtonDefaults.buttonColors(containerColor = PhoneColors.Blue),
                    modifier = Modifier.fillMaxWidth()
                )
            }
        }

        Spacer(modifier = Modifier.height(12.dp))
    }
}

@androidx.compose.ui.tooling.preview.Preview(showBackground = true, name = "AED Picked")
@Composable
private fun AedPickedPreview() {
    AedDeliveryScreen(phase = "AED_PICKED", onAedPicked = {}, onAedDelivered = {})
}

@androidx.compose.ui.tooling.preview.Preview(showBackground = true, name = "AED Delivering")
@Composable
private fun AedDeliveringPreview() {
    AedDeliveryScreen(phase = "AED_DELIVERED", onAedPicked = {}, onAedDelivered = {})
}
