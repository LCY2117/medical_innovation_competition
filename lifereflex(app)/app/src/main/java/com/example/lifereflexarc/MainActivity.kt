package com.example.lifereflexarc

import android.content.Context
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.platform.LocalContext
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.lifereflexarc.ui.AppRoot
import com.example.lifereflexarc.ui.theme.LifeReflexArcTheme
import com.example.lifereflexarc.viewmodel.IncidentViewModel
import com.example.lifereflexarc.viewmodel.SessionViewModel
import java.util.UUID

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            LifeReflexArcTheme {
                Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
                    DemoApp(modifier = Modifier.padding(innerPadding))
                }
            }
        }
    }
}

@Composable
fun DemoApp(modifier: Modifier = Modifier, vm: IncidentViewModel = viewModel()) {
    val context = LocalContext.current
    val userId = remember {
        getOrCreateTerminalId(context)
    }
    androidx.compose.foundation.layout.Box(modifier = modifier.fillMaxSize()) {
        AppRoot(
            incidentViewModel = vm,
            sessionViewModel = viewModel<SessionViewModel>(),
            deviceUserId = userId,
        )
    }
}

@Preview(showBackground = true)
@Composable
fun AppPreview() {
    LifeReflexArcTheme {
        DemoApp()
    }
}

private fun getOrCreateTerminalId(context: Context): String {
    val prefs = context.getSharedPreferences("lra_terminal_identity", Context.MODE_PRIVATE)
    val existing = prefs.getString(KEY_TERMINAL_ID, null)
    if (!existing.isNullOrBlank()) {
        return existing
    }

    val generated = "terminal-${UUID.randomUUID()}"
    prefs.edit().putString(KEY_TERMINAL_ID, generated).apply()
    return generated
}

private const val KEY_TERMINAL_ID = "terminal_id"
