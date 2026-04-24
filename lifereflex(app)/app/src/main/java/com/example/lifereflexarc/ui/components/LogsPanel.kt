package com.example.lifereflexarc.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.lifereflexarc.data.LogEntry
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

@Composable
fun LogsPanel(logs: List<LogEntry>) {
    val formatter = SimpleDateFormat("HH:mm:ss", Locale.getDefault())
    val listState = rememberLazyListState()
    val visibleLogs = logs.takeLast(40)

    LaunchedEffect(visibleLogs.size) {
        if (visibleLogs.isNotEmpty()) {
            listState.scrollToItem(visibleLogs.lastIndex)
        }
    }

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .heightIn(min = 80.dp)
            .background(Color(0xFF0B1220))
            .padding(12.dp),
        verticalArrangement = Arrangement.spacedBy(6.dp)
    ) {
        Text("SYSTEM LOGS", color = Color(0xFF94A3B8), fontSize = 10.sp)
        LazyColumn(modifier = Modifier.heightIn(max = 160.dp), state = listState) {
            items(visibleLogs) { log ->
                val time = formatter.format(Date(log.ts))
                Text("$time  ${log.msg}", color = Color(0xFFE2E8F0), fontSize = 11.sp)
            }
            if (visibleLogs.isEmpty()) {
                item { Text("Waiting for event...", color = Color(0xFF64748B), fontSize = 11.sp) }
            }
        }
    }
}
