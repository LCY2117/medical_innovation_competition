package com.example.lifereflexarc.data

import com.google.gson.JsonElement
import com.google.gson.JsonParser
import retrofit2.HttpException
import java.io.IOException
import java.net.ConnectException
import java.net.SocketTimeoutException
import java.net.UnknownHostException
import java.net.UnknownServiceException
import javax.net.ssl.SSLException

object ErrorMessages {
    fun forHttpOrNetwork(error: Throwable, fallback: String = "操作失败，请稍后重试"): String {
        return when (error) {
            is HttpException -> formatHttpException(error)
            is UnknownHostException -> "网络不可达或服务器地址不可用，请检查域名、网络或 API Base 配置。"
            is SocketTimeoutException -> "连接超时，请检查网络状态后重试。"
            is ConnectException -> "无法连接服务器，请确认云端服务正在运行。"
            is SSLException -> "HTTPS 证书或安全连接异常，请检查域名证书配置。"
            is UnknownServiceException -> formatUnknownService(error)
            is IOException -> "网络连接中断，请检查网络后重试。"
            else -> error.message?.takeIf { it.isNotBlank() }?.let(::normalizeKnownServerText) ?: fallback
        }
    }

    fun forWebSocketFailure(error: Throwable?): String {
        val hint = error?.let { forHttpOrNetwork(it, fallback = "") }.orEmpty()
        return if (hint.isBlank()) {
            "实时连接中断，正在重连。"
        } else {
            "实时连接中断，正在重连。$hint"
        }
    }

    fun forWebSocketPayload(payload: String?): String {
        val normalized = payload?.trim().orEmpty()
        if (normalized.isBlank()) {
            return "实时连接收到异常消息，请稍后重试。"
        }
        return normalizeKnownServerText(normalized)
    }

    fun isUnauthorized(error: Throwable): Boolean = error is HttpException && error.code() == 401

    private fun formatHttpException(error: HttpException): String {
        val detail = extractServerDetail(error)?.let(::normalizeKnownServerText)
        return when (error.code()) {
            400 -> detail?.let { "请求未通过：$it" } ?: "请求参数有误，请检查填写内容。"
            401 -> detail?.takeIf { it.contains("手机号") || it.contains("密码") }
                ?: "登录态已失效，请重新登录。"
            403 -> detail?.let { "权限不足：$it" } ?: "权限不足，可能需要演示口令或管理员授权。"
            404 -> detail?.let { "事件或资源不存在：$it" } ?: "事件或资源不存在，请重新获取事件链接。"
            409 -> detail?.let { "当前状态暂不能执行：$it" } ?: "当前事件状态暂不能执行这个操作。"
            422 -> "输入不符合服务器边界，请检查位置、健康摘要或 AED 状态。"
            429 -> detail ?: "请求过于频繁，请稍后再试。"
            in 500..599 -> "云端服务暂时异常，请稍后重试或检查服务器健康状态。"
            else -> detail ?: "服务端返回异常状态：${error.code()}"
        }
    }

    private fun formatUnknownService(error: UnknownServiceException): String {
        val message = error.message.orEmpty()
        return if (message.contains("CLEARTEXT", ignoreCase = true)) {
            "当前服务器地址使用 HTTP，但应用未允许明文访问。请改用 HTTPS，或仅在调试环境放开本地 HTTP。"
        } else {
            "网络协议配置不兼容，请检查服务器地址。"
        }
    }

    private fun extractServerDetail(error: HttpException): String? {
        val raw = error.response()?.errorBody()?.string()?.trim()
            ?: return null
        if (raw.isBlank()) {
            return null
        }
        return runCatching {
            val root = JsonParser.parseString(raw)
            describeJsonDetail(root)
        }.getOrElse {
            raw.take(120)
        }?.takeIf { it.isNotBlank() }
    }

    private fun describeJsonDetail(element: JsonElement?): String? {
        if (element == null || element.isJsonNull) {
            return null
        }
        if (element.isJsonPrimitive) {
            return element.asString
        }
        if (element.isJsonArray) {
            return element.asJsonArray
                .mapNotNull { describeJsonDetail(it) }
                .take(2)
                .joinToString("；")
                .takeIf { it.isNotBlank() }
        }
        if (element.isJsonObject) {
            val obj = element.asJsonObject
            val detail = obj.get("detail") ?: obj.get("msg") ?: obj.get("message") ?: obj.get("error")
            if (detail != null) {
                return describeJsonDetail(detail)
            }
            val location = obj.get("loc")?.let(::describeJsonDetail)
            val message = obj.get("msg")?.let(::describeJsonDetail)
            return listOfNotNull(location, message).joinToString("：").takeIf { it.isNotBlank() }
        }
        return null
    }

    private fun normalizeKnownServerText(value: String): String {
        val text = value.trim()
        return when {
            text == "Client not registered" -> "终端尚未注册，请先登录并进入协同终端。"
            text == "Patient client not registered" -> "患者端尚未注册，请先让患者端进入事件。"
            text.startsWith("Incident already has an active patient") -> "当前事件已有患者端，请重置或新建事件后再选择。"
            text == "Incident already dispatched" -> "当前事件已经完成分派。"
            text == "Invalid role" -> "角色不符合服务器要求。"
            text == "No available roles" -> "当前没有可加入的空闲角色。"
            text == "Handover not ready" -> "交接条件尚未满足。"
            text == "Only active participants can complete handover" -> "只有当前参与者可以完成交接。"
            text == "Only the active patient can cancel SOS" -> "只有当前患者端可以取消 SOS。"
            text == "Incident not found" -> "事件不存在或已被重置，请返回总控台重新获取事件链接。"
            text.startsWith("User is not assigned to") -> "当前账号未被分配到该角色。"
            text.contains("cannot perform this action from status") -> "当前任务状态还不能执行这个动作。"
            text.startsWith("HTTP ") -> "服务端响应异常，请稍后重试。"
            else -> text
        }
    }
}
