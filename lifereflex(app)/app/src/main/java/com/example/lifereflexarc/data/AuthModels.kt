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

data class AuthResponse(
    val ok: Boolean,
    val token: String,
    val user: AuthUser,
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
