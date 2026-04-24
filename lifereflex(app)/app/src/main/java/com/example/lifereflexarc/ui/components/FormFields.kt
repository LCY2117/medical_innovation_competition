package com.example.lifereflexarc.ui.components

import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import com.example.lifereflexarc.ui.theme.PhoneColors

@Composable
fun LraOutlinedTextField(
    value: String,
    onValueChange: (String) -> Unit,
    label: String,
    modifier: Modifier = Modifier,
    supportingText: String? = null,
    keyboardOptions: androidx.compose.foundation.text.KeyboardOptions = androidx.compose.foundation.text.KeyboardOptions.Default,
) {
    OutlinedTextField(
        value = value,
        onValueChange = onValueChange,
        label = { Text(label, color = PhoneColors.GrayText) },
        supportingText = supportingText?.let { { Text(it, color = PhoneColors.GrayText) } },
        keyboardOptions = keyboardOptions,
        modifier = modifier,
        singleLine = true,
        colors = OutlinedTextFieldDefaults.colors(
            focusedTextColor = Color.White,
            unfocusedTextColor = Color.White,
            focusedContainerColor = Color(0xFF0B1223),
            unfocusedContainerColor = Color(0xFF0B1223),
            focusedBorderColor = Color(0xFF3B82F6),
            unfocusedBorderColor = Color(0xFF334155),
            cursorColor = Color.White,
            focusedLabelColor = Color(0xFF93C5FD),
            unfocusedLabelColor = PhoneColors.GrayText,
        ),
    )
}
