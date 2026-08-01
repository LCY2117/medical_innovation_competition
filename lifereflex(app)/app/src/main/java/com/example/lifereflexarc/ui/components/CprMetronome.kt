package com.example.lifereflexarc.ui.components

import android.media.AudioManager
import android.media.ToneGenerator
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.delay

const val DEFAULT_CPR_BPM = 110
const val MIN_CPR_BPM = 100
const val MAX_CPR_BPM = 120

fun cprBeatIntervalMs(beatsPerMinute: Int): Long {
    val clamped = beatsPerMinute.coerceIn(MIN_CPR_BPM, MAX_CPR_BPM)
    return (60_000L / clamped).coerceAtLeast(400L)
}

@Composable
fun rememberCprToneGenerator(): ToneGenerator? {
    val context = LocalContext.current
    return remember(context) {
        try {
            ToneGenerator(AudioManager.STREAM_MUSIC, 60)
        } catch (_: Exception) {
            null
        }
    }
}

@Composable
fun CprBeatAnimation(
    active: Boolean,
    modifier: Modifier = Modifier,
    color: Color = Color(0xFF34D399),
) {
    val transition = rememberInfiniteTransition(label = "cprBeat")
    val beatFraction by transition.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(durationMillis = 600),
            repeatMode = RepeatMode.Restart,
        ),
        label = "cprBeatScale",
    )
    Box(modifier = modifier, contentAlignment = Alignment.Center) {
        Canvas(modifier = Modifier.fillMaxSize()) {
            val ringSize = size.minDimension * (0.72f + beatFraction * 0.28f)
            val alpha = if (active) (1f - beatFraction).coerceIn(0f, 1f) else 0f
            drawCircle(
                color = color.copy(alpha = 0.45f * alpha),
                radius = ringSize / 2f,
                style = Stroke(width = 10f),
            )
        }
        Canvas(
            modifier = Modifier
                .fillMaxSize(0.62f)
                .graphicsLayer {
                    scaleX = if (active) 1f - beatFraction * 0.12f else 1f
                    scaleY = if (active) 1f - beatFraction * 0.12f else 1f
                }
        ) {
            drawCircle(
                color = if (active) color.copy(alpha = 0.9f) else color.copy(alpha = 0.25f),
                style = Stroke(width = 16f),
            )
        }
    }
}

@Composable
fun CprMetronomeTicker(
    active: Boolean,
    beatsPerMinute: Int = DEFAULT_CPR_BPM,
) {
    val toneGenerator = rememberCprToneGenerator()
    DisposableEffect(toneGenerator) {
        onDispose {
            try {
                toneGenerator?.stopTone()
            } catch (_: Exception) {
                // ignore
            }
            toneGenerator?.release()
        }
    }
    LaunchedEffect(active, beatsPerMinute) {
        if (!active) {
            try {
                toneGenerator?.stopTone()
            } catch (_: Exception) {
                // ignore
            }
            return@LaunchedEffect
        }
        val intervalMs = cprBeatIntervalMs(beatsPerMinute)
        while (true) {
            try {
                toneGenerator?.startTone(ToneGenerator.TONE_PROP_BEEP, 80)
            } catch (_: Exception) {
                // ignore
            }
            delay(intervalMs)
        }
    }
}
