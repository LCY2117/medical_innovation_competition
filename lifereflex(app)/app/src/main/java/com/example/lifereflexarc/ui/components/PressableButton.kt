package com.example.lifereflexarc.ui.components

import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsPressedAsState
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonColors
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.scale
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.shape.RoundedCornerShape
import com.example.lifereflexarc.ui.theme.PhoneTokens

@Composable
fun PressableButton(
    text: String,
    onClick: () -> Unit,
    colors: ButtonColors = ButtonDefaults.buttonColors(),
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
) {
    val interaction = remember { MutableInteractionSource() }
    val pressed by interaction.collectIsPressedAsState()
    val scale by animateFloatAsState(if (pressed) 0.96f else 1f, label = "press")

    Button(
        onClick = onClick,
        colors = colors,
        enabled = enabled,
        interactionSource = interaction,
        shape = RoundedCornerShape(PhoneTokens.ButtonRadius),
        modifier = Modifier
            .height(PhoneTokens.ButtonHeight)
            .scale(scale)
            .then(modifier)
    ) {
        Text(text)
    }
}
