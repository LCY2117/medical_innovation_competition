package com.example.lifereflexarc.data

data class AuthRegisterRequest(
    val displayName: String,
    val phone: String,
    val password: String,
    val organization: String,
    val healthCondition: String,
    val professionIdentity: String,
    val profileBio: String,
)

data class AuthLoginRequest(
    val phone: String,
    val password: String,
)

data class AuthCodeRequest(
    val phone: String,
)

data class AuthCodeLoginRequest(
    val phone: String,
    val code: String,
)

data class AuthCodeRegisterRequest(
    val phone: String,
    val code: String,
    val displayName: String,
    val organization: String,
    val healthCondition: String,
    val professionIdentity: String,
    val profileBio: String,
)

data class AuthCodeRequestResponse(
    val ok: Boolean,
    val channel: String,
    val expiresInSec: Int,
    val betaCode: String? = null,
)

data class AuthCodeLoginResponse(
    val ok: Boolean,
    val needsProfileSetup: Boolean,
    val token: String? = null,
    val user: AuthUser? = null,
    val tokenExpiresAt: Long? = null,
    val phone: String? = null,
)

data class AuthProfileUpdateRequest(
    val displayName: String,
    val organization: String,
    val healthCondition: String,
    val professionIdentity: String,
    val profileBio: String,
)

data class AuthResponse(
    val ok: Boolean,
    val token: String,
    val user: AuthUser,
    val tokenExpiresAt: Long? = null,
)

data class AuthMeResponse(
    val ok: Boolean,
    val user: AuthUser,
    val tokenExpiresAt: Long? = null,
)

data class SimpleOkResponse(
    val ok: Boolean,
)

data class AuthUser(
    val userId: String,
    val displayName: String,
    val phone: String,
    val organization: String,
    val healthCondition: String,
    val professionIdentity: String,
    val profileBio: String,
    val credentialStatus: String,
)
