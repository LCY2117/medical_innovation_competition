package com.example.lifereflexarc.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.example.lifereflexarc.viewmodel.IncidentViewModel
import com.example.lifereflexarc.viewmodel.SessionViewModel
import com.example.lifereflexarc.ui.components.ActiveIncidentBanner
import com.example.lifereflexarc.ui.components.AppTopBar
import com.example.lifereflexarc.ui.components.InlineErrorCard
import com.example.lifereflexarc.ui.screens.ActiveEmergencyScreen
import com.example.lifereflexarc.ui.screens.ArchiveScreen
import com.example.lifereflexarc.ui.screens.CommandHomeScreen
import com.example.lifereflexarc.ui.screens.IncidentScreen
import com.example.lifereflexarc.ui.screens.LoginScreen
import com.example.lifereflexarc.ui.screens.ProfileScreen
import com.example.lifereflexarc.ui.screens.TasksScreen
import com.example.lifereflexarc.data.isArchived

@Composable
fun AppRoot(
    incidentViewModel: IncidentViewModel,
    sessionViewModel: SessionViewModel,
    deviceUserId: String,
) {
    val session by sessionViewModel.session.collectAsState()
    val sessionError by sessionViewModel.error.collectAsState()
    val sessionLoading by sessionViewModel.loading.collectAsState()
    val archives by sessionViewModel.archives.collectAsState()
    val incidentState by incidentViewModel.state.collectAsState(null)
    val connected by incidentViewModel.connected.collectAsState(false)
    val connecting by incidentViewModel.connecting.collectAsState(false)
    val incidentError by incidentViewModel.error.collectAsState(null)
    val assignedRoleRaw by incidentViewModel.assignedRole.collectAsState(null)
    val activeUserId = session.userId.ifBlank { deviceUserId }

    if (!session.isLoggedIn) {
        LoginScreen(
            error = sessionError,
            loading = sessionLoading,
            onRegister = { name, phone, password, organization, healthCondition, professionIdentity, bio ->
                sessionViewModel.register(
                    displayName = name,
                    phone = phone,
                    password = password,
                    organization = organization,
                    healthCondition = healthCondition,
                    professionIdentity = professionIdentity,
                    bio = bio,
                )
            },
            onLogin = { phone, password ->
                sessionViewModel.login(phone = phone, password = password)
            },
            onInputChanged = sessionViewModel::clearError,
        )
        return
    }

    LaunchedEffect(
        session.displayName,
        session.organization,
        session.healthCondition,
        session.professionIdentity,
        session.bio,
        activeUserId,
    ) {
        incidentViewModel.registerTerminal(userId = activeUserId, session = session)
    }

    LaunchedEffect(session.isLoggedIn) {
        if (session.isLoggedIn) {
            incidentViewModel.connectCurrent(activeUserId, autoJoin = false)
        }
    }

    val assignedRole = assignedRoleRaw?.let(::userRoleFromBackendRole)
        ?: incidentState?.let { deriveAssignedRole(it, activeUserId) }
    var activeTab by rememberSaveable { mutableStateOf(MainTab.Home) }
    var dismissedArchivedIncidentId by rememberSaveable { mutableStateOf<String?>(null) }
    val currentIncident = incidentState
    val currentIncidentError = incidentError
    val navigationAccent = assignedRole?.let(::accentForRole) ?: Color(0xFF2563EB)

    LaunchedEffect(currentIncident?.incidentId, currentIncident?.phase, assignedRole) {
        if (currentIncident?.phase == "ARCHIVED") {
            sessionViewModel.recordIncidentArchive(currentIncident, assignedRole)
        } else if (currentIncident?.incidentId != dismissedArchivedIncidentId) {
            dismissedArchivedIncidentId = null
        }
    }

    val currentIncidentId = currentIncident?.incidentId
    val isActiveParticipant = currentIncident?.patientUserId == activeUserId || assignedRole != null
    val shouldShowEmergency = currentIncident != null && isActiveParticipant &&
        !(currentIncident.isArchived() && dismissedArchivedIncidentId == currentIncidentId)

    if (shouldShowEmergency) {
        ActiveEmergencyScreen(
            session = session,
            incidentState = currentIncident,
            assignedRole = assignedRole,
            deviceUserId = activeUserId,
            incidentViewModel = incidentViewModel,
            onExitEmergency = {
                dismissedArchivedIncidentId = currentIncidentId
                activeTab = MainTab.Archive
            },
        )
        return
    }

    Scaffold(
        modifier = Modifier.fillMaxSize(),
        containerColor = Color(0xFF020617),
        bottomBar = {
            NavigationBar(
                containerColor = Color(0xFF0F172A),
                tonalElevation = 0.dp,
            ) {
                MainTab.entries.forEach { tab ->
                    NavigationBarItem(
                        selected = activeTab == tab,
                        onClick = { activeTab = tab },
                        icon = {
                            Box(
                                modifier = Modifier
                                    .clip(CircleShape)
                                    .background(if (activeTab == tab) navigationAccent else Color(0xFF475569))
                                    .size(10.dp)
                            )
                        },
                        label = { Text(tab.label) },
                    )
                }
            }
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(horizontal = 16.dp, vertical = 12.dp),
        ) {
            if (activeTab == MainTab.Home) {
                AppTopBar(
                    session = session,
                    incidentState = incidentState,
                    connected = connected,
                    connecting = connecting,
                    assignedRole = assignedRole,
                )

                if (currentIncident != null) {
                    Spacer(modifier = Modifier.height(12.dp))
                    ActiveIncidentBanner(
                        incidentState = currentIncident,
                        assignedRole = assignedRole,
                        onOpenIncident = { activeTab = MainTab.Incident },
                    )
                }

                Spacer(modifier = Modifier.height(12.dp))
            }

            if (!currentIncidentError.isNullOrBlank()) {
                InlineErrorCard(message = currentIncidentError)
                Spacer(modifier = Modifier.height(12.dp))
            }

            when (activeTab) {
                MainTab.Home -> CommandHomeScreen(
                    session = session,
                    incidentState = incidentState,
                    connected = connected,
                    assignedRole = assignedRole,
                    onCreateIncident = {
                        incidentViewModel.clearError()
                        incidentViewModel.createIncident()
                        activeTab = MainTab.Incident
                    },
                    onOpenCurrent = {
                        incidentViewModel.clearError()
                        incidentViewModel.connectCurrent(activeUserId, autoJoin = false)
                        activeTab = MainTab.Incident
                    },
                    onAutoJoinCurrent = null,
                )
                MainTab.Tasks -> TasksScreen(
                    session = session,
                    incidentState = incidentState,
                    assignedRole = assignedRole,
                    deviceUserId = activeUserId,
                    incidentViewModel = incidentViewModel,
                    onOpenIncident = { activeTab = MainTab.Incident },
                )
                MainTab.Incident -> IncidentScreen(
                    session = session,
                    incidentState = incidentState,
                    assignedRole = assignedRole,
                    deviceUserId = activeUserId,
                    incidentViewModel = incidentViewModel,
                    onCreateIncident = {
                        incidentViewModel.clearError()
                        incidentViewModel.createIncident()
                    },
                    onOpenCurrent = {
                        incidentViewModel.clearError()
                        incidentViewModel.connectCurrent(activeUserId, autoJoin = false)
                    },
                    onAutoJoinCurrent = null,
                )
                MainTab.Archive -> ArchiveScreen(
                    incidentState = incidentState,
                    archives = archives,
                )
                MainTab.Profile -> ProfileScreen(
                    session = session,
                    onLogout = {
                        incidentViewModel.disconnect()
                        sessionViewModel.signOut()
                        activeTab = MainTab.Home
                    },
                )
            }
        }
    }
}

private fun deriveAssignedRole(
    incidentState: com.example.lifereflexarc.data.IncidentState,
    deviceUserId: String,
): com.example.lifereflexarc.data.UserRole? = when (deviceUserId) {
    incidentState.roles.PRIME.userId -> com.example.lifereflexarc.data.UserRole.PRIME
    incidentState.roles.RUNNER.userId -> com.example.lifereflexarc.data.UserRole.RUNNER
    incidentState.roles.GUIDE.userId -> com.example.lifereflexarc.data.UserRole.GUIDE
    else -> null
}
