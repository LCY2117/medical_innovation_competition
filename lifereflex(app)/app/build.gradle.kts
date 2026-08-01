plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.compose)
}

import java.util.Properties

val localProperties = Properties().apply {
    val localFile = rootProject.file("local.properties")
    if (localFile.isFile) {
        localFile.inputStream().use(::load)
    }
}

fun projectLocalOrEnv(name: String): String? =
    providers.gradleProperty(name).orNull
        ?: localProperties.getProperty(name)
        ?: providers.environmentVariable(name).orNull

val apiBase = projectLocalOrEnv("LRA_API_BASE") ?: "https://www.yclsm.top/"
val wsBase = projectLocalOrEnv("LRA_WS_BASE") ?: "wss://www.yclsm.top/ws"
val releaseStoreFilePath = projectLocalOrEnv("LRA_RELEASE_STORE_FILE")
val releaseStorePassword = projectLocalOrEnv("LRA_RELEASE_STORE_PASSWORD")
val releaseKeyAlias = projectLocalOrEnv("LRA_RELEASE_KEY_ALIAS")
val releaseKeyPassword = projectLocalOrEnv("LRA_RELEASE_KEY_PASSWORD")
val hasReleaseSigning = listOf(
    releaseStoreFilePath,
    releaseStorePassword,
    releaseKeyAlias,
    releaseKeyPassword,
).all { !it.isNullOrBlank() }

fun isReleaseBuildTask(taskName: String): Boolean {
    val lowerName = taskName.lowercase()
    return "release" in lowerName && listOf("assemble", "bundle", "package", "install", "process").any { it in lowerName }
}

fun requireReleaseUrlScheme(name: String, value: String, scheme: String) {
    if (!value.trim().startsWith(scheme)) {
        throw GradleException(
            "$name must start with $scheme for release builds. " +
                "Use local HTTP/WS only for debug builds."
        )
    }
}

gradle.taskGraph.whenReady {
    if (allTasks.any { isReleaseBuildTask(it.name) }) {
        requireReleaseUrlScheme("LRA_API_BASE", apiBase, "https://")
        requireReleaseUrlScheme("LRA_WS_BASE", wsBase, "wss://")
    }
}

android {
    namespace = "com.example.lifereflexarc"
    compileSdk {
        version = release(36)
    }

    defaultConfig {
        applicationId = "com.example.lifereflexarc"
        minSdk = 26
        targetSdk = 36
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        buildConfigField("String", "LRA_API_BASE", "\"$apiBase\"")
        buildConfigField("String", "LRA_WS_BASE", "\"$wsBase\"")
    }

    signingConfigs {
        if (hasReleaseSigning) {
            create("release") {
                storeFile = file(releaseStoreFilePath!!)
                storePassword = releaseStorePassword
                keyAlias = releaseKeyAlias
                keyPassword = releaseKeyPassword
            }
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            if (hasReleaseSigning) {
                signingConfig = signingConfigs.getByName("release")
            }
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
    buildFeatures {
        compose = true
        buildConfig = true
    }
}

dependencies {
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.runtime.ktx)
    implementation(libs.androidx.activity.compose)
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.compose.ui)
    implementation(libs.androidx.compose.ui.graphics)
    implementation(libs.androidx.compose.animation)
    implementation(libs.androidx.compose.ui.tooling.preview)
    implementation(libs.androidx.compose.material3)
    implementation(libs.androidx.lifecycle.viewmodel.compose)
    implementation(libs.coroutines.android)
    implementation(libs.retrofit)
    implementation(libs.retrofit.gson)
    implementation(libs.okhttp)
    implementation(libs.okhttp.logging)
    implementation(libs.gson)
    implementation(libs.androidx.security.crypto)
    implementation(libs.androidx.health.connect)
    testImplementation(libs.junit)
    androidTestImplementation(libs.androidx.junit)
    androidTestImplementation(libs.androidx.espresso.core)
    androidTestImplementation(platform(libs.androidx.compose.bom))
    androidTestImplementation(libs.androidx.compose.ui.test.junit4)
    debugImplementation(libs.androidx.compose.ui.tooling)
    debugImplementation(libs.androidx.compose.ui.test.manifest)
}
