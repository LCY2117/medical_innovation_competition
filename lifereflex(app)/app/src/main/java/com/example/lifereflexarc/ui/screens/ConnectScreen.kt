package com.example.lifereflexarc.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.example.lifereflexarc.ui.components.PressableButton
import com.example.lifereflexarc.ui.theme.PhoneColors
import com.example.lifereflexarc.ui.theme.PhoneTokens

@Composable
fun ConnectScreen(
    onConnect: (String) -> Unit,
    onOpenCurrent: (() -> Unit)? = null,
    onAutoJoinCurrent: (() -> Unit)? = null,
    onCreateIncident: (() -> Unit)? = null,
    title: String = "连接事件",
    message: String? = null,
) {
    var incidentId by remember { mutableStateOf("") }

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(PhoneTokens.ScreenPadding),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text(title, color = PhoneColors.GrayText)
        if (!message.isNullOrBlank()) {
            Spacer(modifier = Modifier.height(8.dp))
            Text(message, color = PhoneColors.Red)
        }
        Spacer(modifier = Modifier.height(8.dp))
        onOpenCurrent?.let {
            PressableButton(
                text = "进入当前事件",
                onClick = it,
                colors = ButtonDefaults.buttonColors(containerColor = PhoneColors.Blue),
                modifier = Modifier.fillMaxWidth(),
            )
            Spacer(modifier = Modifier.height(12.dp))
        }
        onAutoJoinCurrent?.let {
            PressableButton(
                text = "自动接单",
                onClick = it,
                colors = ButtonDefaults.buttonColors(containerColor = PhoneColors.Red),
                modifier = Modifier.fillMaxWidth(),
            )
            Spacer(modifier = Modifier.height(12.dp))
        }
        onCreateIncident?.let {
            PressableButton(
                text = "新建事件",
                onClick = it,
                colors = ButtonDefaults.buttonColors(containerColor = PhoneColors.Green),
                modifier = Modifier.fillMaxWidth(),
            )
            Spacer(modifier = Modifier.height(16.dp))
        }
        Text("或输入事件编号", color = PhoneColors.GrayText)
        Spacer(modifier = Modifier.height(8.dp))
        OutlinedTextField(
            value = incidentId,
            onValueChange = { incidentId = it },
            label = { Text("incidentId") },
            modifier = Modifier.fillMaxWidth(),
        )
        Spacer(modifier = Modifier.height(12.dp))
        PressableButton(
            text = "连接",
            onClick = { if (incidentId.isNotBlank()) onConnect(incidentId) },
            colors = ButtonDefaults.buttonColors(containerColor = PhoneColors.Blue),
            modifier = Modifier.fillMaxWidth(),
        )
    }
}

@androidx.compose.ui.tooling.preview.Preview(showBackground = true)
@Composable
private fun ConnectScreenPreview() {
    ConnectScreen(onConnect = {})
}
