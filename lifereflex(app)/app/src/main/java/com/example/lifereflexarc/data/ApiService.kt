package com.example.lifereflexarc.data

import retrofit2.http.Header
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path

interface ApiService {
    @POST("/auth/register")
    suspend fun register(
        @Body body: AuthRegisterRequest,
    ): AuthResponse

    @POST("/auth/login")
    suspend fun login(
        @Body body: AuthLoginRequest,
    ): AuthResponse

    @POST("/incidents")
    suspend fun createIncident(): CreateIncidentResponse

    @POST("/clients/register")
    suspend fun registerClient(
        @Header("Authorization") authorization: String?,
        @Body body: ClientRegisterRequest,
    )

    @GET("/incidents/current")
    suspend fun getCurrentIncident(): IncidentState

    @GET("/incidents/{id}")
    suspend fun getIncident(
        @Path("id") incidentId: String,
    ): IncidentState

    @POST("/incidents/current/join_auto")
    suspend fun joinCurrentAuto(
        @Body body: AutoJoinRequest,
    ): AutoJoinResponse

    @POST("/incidents/{id}/join")
    suspend fun joinIncident(
        @Path("id") incidentId: String,
        @Body body: JoinRequest,
    )

    @POST("/incidents/{id}/actions")
    suspend fun postAction(
        @Path("id") incidentId: String,
        @Body body: ActionRequest,
    )

    @POST("/incidents/{id}/sos_start")
    suspend fun sosStart(
        @Path("id") incidentId: String,
    )

    @POST("/incidents/{id}/sos_cancel")
    suspend fun sosCancel(
        @Path("id") incidentId: String,
    )

    @POST("/incidents/{id}/trigger")
    suspend fun triggerIncident(
        @Path("id") incidentId: String,
    )
}
