package com.example.lifereflexarc.data

import com.google.gson.Gson
import com.google.gson.JsonParser
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.launch
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import okhttp3.WebSocket
import okhttp3.WebSocketListener
import java.util.concurrent.TimeUnit
import kotlin.math.min

class WsClient(
    private val gson: Gson,
    private val baseWsUrl: String,
) {
    val connected = MutableStateFlow(false)
    val latestState = MutableStateFlow<IncidentState?>(null)
    val latestError = MutableStateFlow<String?>(null)

    private val client = OkHttpClient.Builder()
        .readTimeout(0, TimeUnit.MILLISECONDS)
        .build()

    private var webSocket: WebSocket? = null
    private var incidentId: String? = null
    private var reconnectAttempt = 0
    private var manualClose = false
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    fun connect(id: String) {
        manualClose = true
        webSocket?.close(1000, "switching incident")
        webSocket = null
        incidentId = id
        reconnectAttempt = 0
        latestError.value = null
        manualClose = false
        openSocket()
    }

    fun close() {
        manualClose = true
        incidentId = null
        webSocket?.close(1000, "closed")
        webSocket = null
        connected.value = false
    }

    private fun openSocket() {
        val id = incidentId ?: return
        val request = Request.Builder()
            .url("$baseWsUrl?incidentId=$id")
            .build()

        webSocket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                connected.value = true
                reconnectAttempt = 0
                latestError.value = null
            }

            override fun onMessage(webSocket: WebSocket, text: String) {
                try {
                    val envelope = JsonParser.parseString(text).asJsonObject
                    val type = envelope.get("type")?.asString.orEmpty()
                    if (type == "STATE" && envelope.has("payload")) {
                        latestState.value = gson.fromJson(envelope.get("payload"), IncidentState::class.java)
                        latestError.value = null
                    } else if (type == "ERROR") {
                        latestError.value = envelope.get("payload")?.asString ?: "Server error"
                    }
                } catch (e: Exception) {
                    latestError.value = e.message ?: "Invalid websocket payload"
                }
            }

            override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                connected.value = false
                if (!manualClose) {
                    scheduleReconnect()
                }
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                connected.value = false
                latestError.value = t.message ?: "WebSocket connection failed"
                if (!manualClose) {
                    scheduleReconnect()
                }
            }
        })
    }

    private fun scheduleReconnect() {
        val id = incidentId ?: return
        val delayMs = min(10_000L, 1_000L * (1 shl reconnectAttempt))
        reconnectAttempt = min(reconnectAttempt + 1, 4)
        scope.launch {
            delay(delayMs)
            if (incidentId == id) {
                openSocket()
            }
        }
    }
}
