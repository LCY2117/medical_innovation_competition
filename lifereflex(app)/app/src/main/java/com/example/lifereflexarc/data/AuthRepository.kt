package com.example.lifereflexarc.data

import com.google.gson.Gson
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

class AuthRepository(
    apiBase: String,
) {
    private val apiService: ApiService

    init {
        val logger = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.NONE
        }
        val okHttp = OkHttpClient.Builder()
            .addInterceptor(logger)
            .build()

        apiService = Retrofit.Builder()
            .baseUrl(apiBase)
            .client(okHttp)
            .addConverterFactory(GsonConverterFactory.create(Gson()))
            .build()
            .create(ApiService::class.java)
    }

    suspend fun register(
        displayName: String,
        phone: String,
        password: String,
        organization: String,
        healthCondition: String,
        professionIdentity: String,
        profileBio: String,
    ): AuthResponse {
        return apiService.register(
            AuthRegisterRequest(
                displayName = displayName,
                phone = phone,
                password = password,
                organization = organization,
                healthCondition = healthCondition,
                professionIdentity = professionIdentity,
                profileBio = profileBio,
            )
        )
    }

    suspend fun login(
        phone: String,
        password: String,
    ): AuthResponse {
        return apiService.login(AuthLoginRequest(phone = phone, password = password))
    }

    suspend fun requestLoginCode(phone: String): AuthCodeRequestResponse {
        return apiService.requestLoginCode(AuthCodeRequest(phone = phone))
    }

    suspend fun loginWithCode(
        phone: String,
        code: String,
    ): AuthCodeLoginResponse {
        return apiService.loginWithCode(AuthCodeLoginRequest(phone = phone, code = code))
    }

    suspend fun completeCodeRegistration(
        phone: String,
        code: String,
        displayName: String,
        organization: String,
        healthCondition: String,
        professionIdentity: String,
        profileBio: String,
    ): AuthResponse {
        return apiService.completeCodeRegistration(
            AuthCodeRegisterRequest(
                phone = phone,
                code = code,
                displayName = displayName,
                organization = organization,
                healthCondition = healthCondition,
                professionIdentity = professionIdentity,
                profileBio = profileBio,
            )
        )
    }

    suspend fun me(authToken: String): AuthMeResponse {
        return apiService.me("Bearer $authToken")
    }

    suspend fun updateProfile(
        authToken: String,
        displayName: String,
        organization: String,
        healthCondition: String,
        professionIdentity: String,
        profileBio: String,
    ): AuthMeResponse {
        return apiService.updateMe(
            authorization = "Bearer $authToken",
            body = AuthProfileUpdateRequest(
                displayName = displayName,
                organization = organization,
                healthCondition = healthCondition,
                professionIdentity = professionIdentity,
                profileBio = profileBio,
            ),
        )
    }

    suspend fun logout(authToken: String) {
        apiService.logout("Bearer $authToken")
    }
}
