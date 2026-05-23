package com.example.lifereflexarc.data

import retrofit2.http.Header
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.PATCH
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

    @GET("/auth/me")
    suspend fun me(
        @Header("Authorization") authorization: String?,
    ): AuthMeResponse

    @PATCH("/auth/me")
    suspend fun updateMe(
        @Header("Authorization") authorization: String?,
        @Body body: AuthProfileUpdateRequest,
    ): AuthMeResponse

    @POST("/auth/logout")
    suspend fun logout(
        @Header("Authorization") authorization: String?,
    ): SimpleOkResponse

    @POST("/incidents")
    suspend fun createIncident(): CreateIncidentResponse

    @POST("/clients/register")
    suspend fun registerClient(
        @Header("Authorization") authorization: String?,
        @Body body: ClientRegisterRequest,
    )

    @POST("/clients/location")
    suspend fun updateClientLocation(
        @Header("Authorization") authorization: String?,
        @Body body: ClientLocationUpdateRequest,
    )

    @POST("/clients/health")
    suspend fun updateClientHealth(
        @Header("Authorization") authorization: String?,
        @Body body: ClientHealthUpdateRequest,
    )

    @GET("/incidents/current")
    suspend fun getCurrentIncident(): IncidentState

    @GET("/incidents/{id}")
    suspend fun getIncident(
        @Path("id") incidentId: String,
    ): IncidentState

    @POST("/incidents/current/join_auto")
    suspend fun joinCurrentAuto(
        @Header("Authorization") authorization: String?,
        @Body body: AutoJoinRequest,
    ): AutoJoinResponse

    @POST("/incidents/{id}/join")
    suspend fun joinIncident(
        @Header("Authorization") authorization: String?,
        @Path("id") incidentId: String,
        @Body body: JoinRequest,
    )

    @POST("/incidents/{id}/actions")
    suspend fun postAction(
        @Header("Authorization") authorization: String?,
        @Path("id") incidentId: String,
        @Body body: ActionRequest,
    )

    @POST("/incidents/{id}/sos_start")
    suspend fun sosStart(
        @Path("id") incidentId: String,
    ): MutationResponse

    @POST("/incidents/{id}/sos_cancel")
    suspend fun sosCancel(
        @Path("id") incidentId: String,
    ): MutationResponse

    @POST("/incidents/{id}/patient_sos_start")
    suspend fun patientSosStart(
        @Header("Authorization") authorization: String?,
        @Path("id") incidentId: String,
    ): MutationResponse

    @POST("/incidents/{id}/patient_sos_cancel")
    suspend fun patientSosCancel(
        @Header("Authorization") authorization: String?,
        @Path("id") incidentId: String,
    ): MutationResponse

    @POST("/incidents/{id}/trigger")
    suspend fun triggerIncident(
        @Path("id") incidentId: String,
    ): MutationResponse
}
