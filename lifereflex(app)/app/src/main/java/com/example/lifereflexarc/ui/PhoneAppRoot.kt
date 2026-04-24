package com.example.lifereflexarc.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.example.lifereflexarc.ui.components.LogsPanel
import com.example.lifereflexarc.ui.components.StatusLight
import com.example.lifereflexarc.ui.screens.AedDeliveryScreen
import com.example.lifereflexarc.ui.screens.ConnectScreen
import com.example.lifereflexarc.ui.screens.CreatedMonitoringScreen
import com.example.lifereflexarc.ui.screens.CprMetronomeScreen
import com.example.lifereflexarc.ui.screens.EmergencyAlertScreen
import com.example.lifereflexarc.ui.screens.GuideIdleScreen
import com.example.lifereflexarc.ui.screens.GuideTaskScreen
import com.example.lifereflexarc.ui.screens.HandoverArchiveScreen
import com.example.lifereflexarc.ui.screens.PrimeNavigationScreen
import com.example.lifereflexarc.ui.screens.RunnerIdleScreen
import com.example.lifereflexarc.ui.screens.SosCountdownScreen
import com.example.lifereflexarc.ui.theme.PhoneColors
import com.example.lifereflexarc.ui.theme.PhoneTokens
import com.example.lifereflexarc.viewmodel.IncidentViewModel
import kotlinx.coroutines.delay

@Composable
fun PhoneAppRoot(viewModel: IncidentViewModel, userId: String, role: Role = Role.PRIME) {
    val incidentState by viewModel.state.collectAsState(null)
    val connected by viewModel.connected.collectAsState(false)
    val connecting by viewModel.connecting.collectAsState(false)
    val error by viewModel.error.collectAsState(null)
    val assignedRole by viewModel.assignedRole.collectAsState(null)
    val incidentId = incidentState?.incidentId
    val phase = incidentState?.phase
    val sos = incidentState?.sos

    val countdown = remember(incidentId) { mutableStateOf(7) }
    val cancelRequested = remember(incidentId) { mutableStateOf(false) }
    val victimView = rememberSaveable(incidentId) { mutableStateOf("monitoring") }
    val nowTick = remember { mutableStateOf(System.currentTimeMillis()) }

    LaunchedEffect(phase, incidentId, sos?.status, sos?.startTs, sos?.durationSec) {
        if (phase != "CREATED") {
            victimView.value = "monitoring"
            cancelRequested.value = false
            countdown.value = 7
            return@LaunchedEffect
        }
        if (sos?.status == "ALERTING" && sos.startTs != null) {
            victimView.value = "alerting"
            cancelRequested.value = false
        } else {
            victimView.value = "monitoring"
            cancelRequested.value = false
            countdown.value = 7
        }
    }

    LaunchedEffect(phase, sos?.status, sos?.startTs, sos?.durationSec) {
        if (phase == "CREATED" && sos?.status == "ALERTING" && sos.startTs != null) {
            while (true) {
                nowTick.value = System.currentTimeMillis()
                delay(500)
                if (phase != "CREATED" || sos?.status != "ALERTING") {
                    return@LaunchedEffect
                }
            }
        }
    }

    if (phase == "CREATED" && sos?.status == "ALERTING" && sos.startTs != null) {
        val duration = sos.durationSec.coerceAtLeast(1)
        val elapsedSec = ((nowTick.value - sos.startTs) / 1000).toInt().coerceAtLeast(0)
        countdown.value = (duration - elapsedSec).coerceAtLeast(0)
    }

    val resolvedRole = when (assignedRole) {
        "PRIME" -> Role.PRIME
        "RUNNER" -> Role.RUNNER
        "GUIDE" -> Role.GUIDE
        else -> role
    }
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(PhoneTokens.ScreenPadding),
        verticalArrangement = Arrangement.SpaceBetween,
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            StatusLight(isConnected = connected)
            Spacer(modifier = Modifier.width(0.dp))
            Text(
                text = if (connected) "已连接" else "重新连接中",
                color = PhoneColors.GrayText,
                modifier = Modifier.padding(start = 8.dp)
            )
        }

        Spacer(modifier = Modifier.height(8.dp))

        Box(
            modifier = Modifier.weight(1f),
            contentAlignment = Alignment.Center
        ) {
            if (incidentState == null) {
                if (connecting) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text(
                                text = "正在连接...",
                            color = PhoneColors.GrayText
                        )
                        if (error != null) {
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(text = error ?: "", color = PhoneColors.Red)
                        }
                    }
                } else {
                    ConnectScreen(
                        onConnect = {
                            viewModel.clearError()
                            viewModel.connect(it)
                        },
                        onOpenCurrent = {
                            viewModel.clearError()
                            viewModel.connectCurrent(userId, autoJoin = false)
                        },
                        onAutoJoinCurrent = {
                            viewModel.clearError()
                            viewModel.connectCurrent(userId, autoJoin = true)
                        },
                        onCreateIncident = {
                            viewModel.clearError()
                            viewModel.createIncident()
                        },
                        title = "选择进入方式",
                        message = error
                    )
                }
            } else {
                when (screenFor(incidentState!!, resolvedRole)) {
                    PhoneScreen.SosCountdown -> {
                        if (victimView.value == "monitoring") {
                            CreatedMonitoringScreen(
                                onConfirm = {
                                    victimView.value = "alerting"
                                    cancelRequested.value = false
                                    viewModel.sosStart()
                                }
                            )
                        } else {
                            SosCountdownScreen(
                                seconds = countdown.value,
                                totalSeconds = sos?.durationSec ?: 10,
                                onCancel = {
                                    cancelRequested.value = true
                                    victimView.value = "monitoring"
                                    viewModel.sosCancel()
                                }
                            )
                        }
                    }
                    PhoneScreen.EmergencyAlert -> EmergencyAlertScreen(
                        incidentId = incidentState!!.incidentId,
                        onJoin = { viewModel.joinPrime(userId) }
                    )
                    PhoneScreen.PrimeNavigation -> PrimeNavigationScreen(
                        onArrived = { viewModel.actionCprStarted(userId) }
                    )
                    PhoneScreen.CprMetronome -> CprMetronomeScreen(
                        onCprStarted = { viewModel.actionCprStarted(userId) }
                    )
                    PhoneScreen.RunnerIdle -> RunnerIdleScreen(
                        onJoin = { viewModel.joinRunner(userId) }
                    )
                    PhoneScreen.AedDelivery -> AedDeliveryScreen(
                        phase = incidentState!!.phase,
                        onAedPicked = { viewModel.actionAedPicked(userId) },
                        onAedDelivered = { viewModel.actionAedDelivered(userId) }
                    )
                    PhoneScreen.GuideIdle -> GuideIdleScreen(
                        onJoin = { viewModel.joinGuide(userId) }
                    )
                    PhoneScreen.GuideTask -> GuideTaskScreen(
                        onAmbulanceArrived = { viewModel.actionAmbulanceArrived(userId) }
                    )
                    PhoneScreen.HandoverArchive -> HandoverArchiveScreen()
                }
            }
        }

        Spacer(modifier = Modifier.height(8.dp))
        LogsPanel(logs = incidentState?.logs ?: emptyList())
    }
}
