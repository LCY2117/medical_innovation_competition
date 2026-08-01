package com.example.lifereflexarc.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.lifereflexarc.data.HealthCondition
import com.example.lifereflexarc.data.ProfessionIdentity
import com.example.lifereflexarc.ui.components.InlineErrorCard
import com.example.lifereflexarc.ui.components.LraOutlinedTextField
import com.example.lifereflexarc.ui.components.PressableButton
import com.example.lifereflexarc.ui.theme.PhoneColors

private enum class LoginMethod(val label: String) {
    Code("验证码登录"),
    Password("密码登录"),
}

private enum class ProfileStep(
    val title: String,
    val subtitle: String,
) {
    Identity(
        title = "展示身份",
        subtitle = "这里只设置协同展示信息，不要求真实姓名。",
    ),
    Ability(
        title = "协同能力",
        subtitle = "选择平时具备的能力，事件角色仍由系统按场景分派。",
    ),
    Health(
        title = "身体状态",
        subtitle = "用于风险评估与任务避让，不作为医疗诊断。",
    ),
}

@Composable
fun LoginScreen(
    error: String?,
    loading: Boolean,
    codeHint: String?,
    pendingProfilePhone: String?,
    onPasswordLogin: (String, String) -> Unit,
    onRequestCode: (String) -> Unit,
    onCodeLogin: (String, String) -> Unit,
    onCompleteProfileSetup: (String, String, HealthCondition, ProfessionIdentity, String) -> Unit,
    onCancelProfileSetup: () -> Unit,
    onInputChanged: () -> Unit,
) {
    var loginMethod by rememberSaveable { mutableStateOf(LoginMethod.Code) }
    var phone by rememberSaveable { mutableStateOf("") }
    var password by rememberSaveable { mutableStateOf("") }
    var code by rememberSaveable { mutableStateOf("") }
    var profileStepIndex by rememberSaveable { mutableStateOf(0) }
    var displayName by rememberSaveable { mutableStateOf("") }
    var organization by rememberSaveable { mutableStateOf("") }
    var selectedHealth by rememberSaveable { mutableStateOf(HealthCondition.GENERAL) }
    var selectedIdentity by rememberSaveable { mutableStateOf(ProfessionIdentity.BASIC_KNOWLEDGE) }
    var bio by rememberSaveable { mutableStateOf("") }
    var localError by rememberSaveable { mutableStateOf<String?>(null) }
    val profileSteps = ProfileStep.entries
    val profileStep = profileSteps[profileStepIndex.coerceIn(0, profileSteps.lastIndex)]

    fun clearErrors() {
        localError = null
        onInputChanged()
    }

    fun validatePhone(): Boolean {
        localError = if (phone.filter(Char::isDigit).length < 11) "请输入有效手机号" else null
        return localError == null
    }

    fun validateProfileIdentity(): Boolean {
        localError = if (displayName.isBlank()) "请输入昵称或展示名" else null
        return localError == null
    }

    Surface(
        modifier = Modifier.fillMaxSize(),
        color = Color(0xFF020617),
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            Spacer(modifier = Modifier.height(20.dp))
            Text("生命反射弧", color = Color.White, fontSize = 32.sp, fontWeight = FontWeight.Black)
            Text(
                text = if (pendingProfilePhone.isNullOrBlank()) {
                    "用手机号快速进入协同终端。新用户验证后再设置昵称、能力和身体状态。"
                } else {
                    "手机号 ${maskPhone(pendingProfilePhone)} 已验证，现在补齐用于调度的协同画像。"
                },
                color = PhoneColors.GrayText,
                fontSize = 14.sp,
                lineHeight = 22.sp,
            )

            Card(
                colors = CardDefaults.cardColors(containerColor = Color(0xFF111C34)),
                shape = RoundedCornerShape(28.dp),
                border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFF22304A)),
            ) {
                Column(modifier = Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
                    if (pendingProfilePhone.isNullOrBlank()) {
                        LoginMethodPanel(
                            method = loginMethod,
                            phone = phone,
                            password = password,
                            code = code,
                            loading = loading,
                            codeHint = codeHint,
                            onMethodChange = {
                                loginMethod = it
                                clearErrors()
                            },
                            onPhoneChange = {
                                phone = it
                                clearErrors()
                            },
                            onPasswordChange = {
                                password = it
                                clearErrors()
                            },
                            onCodeChange = {
                                code = it
                                clearErrors()
                            },
                            onRequestCode = {
                                if (validatePhone()) {
                                    onRequestCode(phone)
                                }
                            },
                            onSubmit = {
                                if (loading || !validatePhone()) {
                                    return@LoginMethodPanel
                                }
                                if (loginMethod == LoginMethod.Password) {
                                    onPasswordLogin(phone, password)
                                } else {
                                    onCodeLogin(phone, code)
                                }
                            },
                        )
                    } else {
                        ProfileSetupPanel(
                            step = profileStep,
                            stepIndex = profileStepIndex,
                            totalSteps = profileSteps.size,
                            displayName = displayName,
                            organization = organization,
                            selectedHealth = selectedHealth,
                            selectedIdentity = selectedIdentity,
                            bio = bio,
                            loading = loading,
                            onDisplayNameChange = {
                                displayName = it
                                clearErrors()
                            },
                            onOrganizationChange = {
                                organization = it
                                clearErrors()
                            },
                            onIdentitySelected = {
                                selectedIdentity = it
                                clearErrors()
                            },
                            onHealthSelected = {
                                selectedHealth = it
                                clearErrors()
                            },
                            onBioChange = {
                                bio = it
                                clearErrors()
                            },
                            onBack = {
                                if (profileStepIndex > 0) {
                                    profileStepIndex -= 1
                                    clearErrors()
                                } else {
                                    onCancelProfileSetup()
                                }
                            },
                            onNext = {
                                if (loading) {
                                    return@ProfileSetupPanel
                                }
                                if (profileStep == ProfileStep.Identity && !validateProfileIdentity()) {
                                    return@ProfileSetupPanel
                                }
                                if (profileStepIndex < profileSteps.lastIndex) {
                                    profileStepIndex += 1
                                    clearErrors()
                                } else {
                                    onCompleteProfileSetup(
                                        displayName,
                                        organization,
                                        selectedHealth,
                                        selectedIdentity,
                                        bio,
                                    )
                                }
                            },
                        )
                    }

                    val visibleError = localError ?: error
                    if (!visibleError.isNullOrBlank()) {
                        InlineErrorCard(message = visibleError)
                    }
                }
            }
        }
    }
}

@Composable
private fun LoginMethodPanel(
    method: LoginMethod,
    phone: String,
    password: String,
    code: String,
    loading: Boolean,
    codeHint: String?,
    onMethodChange: (LoginMethod) -> Unit,
    onPhoneChange: (String) -> Unit,
    onPasswordChange: (String) -> Unit,
    onCodeChange: (String) -> Unit,
    onRequestCode: () -> Unit,
    onSubmit: () -> Unit,
) {
    Column(verticalArrangement = Arrangement.spacedBy(14.dp)) {
        Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
            Text("账号登录", color = Color.White, fontSize = 20.sp, fontWeight = FontWeight.Bold)
            Text(
                text = "验证码用于快速登录；密码用于已有账号和管理场景。",
                color = PhoneColors.GrayText,
                fontSize = 12.sp,
                lineHeight = 18.sp,
            )
        }

        Row(horizontalArrangement = Arrangement.spacedBy(10.dp), modifier = Modifier.fillMaxWidth()) {
            LoginMethod.entries.forEach { item ->
                SegmentedChoice(
                    text = item.label,
                    selected = item == method,
                    modifier = Modifier.weight(1f),
                    onClick = { onMethodChange(item) },
                )
            }
        }

        LraOutlinedTextField(
            value = phone,
            onValueChange = onPhoneChange,
            label = "手机号",
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Phone),
            modifier = Modifier.fillMaxWidth(),
        )

        if (method == LoginMethod.Password) {
            LraOutlinedTextField(
                value = password,
                onValueChange = onPasswordChange,
                label = "密码",
                visualTransformation = PasswordVisualTransformation(),
                modifier = Modifier.fillMaxWidth(),
            )
        } else {
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp), modifier = Modifier.fillMaxWidth()) {
                LraOutlinedTextField(
                    value = code,
                    onValueChange = onCodeChange,
                    label = "验证码",
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Text),
                    modifier = Modifier.weight(1f),
                )
                PressableButton(
                    text = if (loading) "发送中" else "获取验证码",
                    onClick = onRequestCode,
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF334155), contentColor = Color.White),
                    modifier = Modifier.weight(0.9f),
                    enabled = !loading,
                )
            }
            if (!codeHint.isNullOrBlank()) {
                SmallInfoCard(title = "验证码状态", body = codeHint)
            }
        }

        PressableButton(
            text = if (loading) "登录中..." else if (method == LoginMethod.Password) "密码登录" else "验证码登录",
            onClick = onSubmit,
            colors = ButtonDefaults.buttonColors(containerColor = PhoneColors.Blue, contentColor = Color.White),
            modifier = Modifier.fillMaxWidth(),
            enabled = !loading,
        )
    }
}

@Composable
private fun ProfileSetupPanel(
    step: ProfileStep,
    stepIndex: Int,
    totalSteps: Int,
    displayName: String,
    organization: String,
    selectedHealth: HealthCondition,
    selectedIdentity: ProfessionIdentity,
    bio: String,
    loading: Boolean,
    onDisplayNameChange: (String) -> Unit,
    onOrganizationChange: (String) -> Unit,
    onIdentitySelected: (ProfessionIdentity) -> Unit,
    onHealthSelected: (HealthCondition) -> Unit,
    onBioChange: (String) -> Unit,
    onBack: () -> Unit,
    onNext: () -> Unit,
) {
    Column(verticalArrangement = Arrangement.spacedBy(14.dp)) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Column(verticalArrangement = Arrangement.spacedBy(4.dp), modifier = Modifier.weight(1f)) {
                Text("新用户资料设置", color = Color.White, fontSize = 20.sp, fontWeight = FontWeight.Bold)
                Text("用于调度画像，不等于实名信息", color = PhoneColors.GrayText, fontSize = 12.sp)
            }
            Text(
                text = "${stepIndex + 1}/$totalSteps",
                color = Color(0xFF93C5FD),
                fontSize = 12.sp,
                fontWeight = FontWeight.Bold,
            )
        }

        StepHeader(step = step, stepIndex = stepIndex, totalSteps = totalSteps)

        when (step) {
            ProfileStep.Identity -> {
                LraOutlinedTextField(
                    value = displayName,
                    onValueChange = onDisplayNameChange,
                    label = "昵称 / 展示名",
                    supportingText = "例如：小李、AED 志愿者 01、图书馆值班员",
                    modifier = Modifier.fillMaxWidth(),
                )
                LraOutlinedTextField(
                    value = organization,
                    onValueChange = onOrganizationChange,
                    label = "组织 / 场景（可选）",
                    supportingText = "例如：云南大学、图书馆、社区演示",
                    modifier = Modifier.fillMaxWidth(),
                )
                SmallInfoCard(
                    title = "为什么不是姓名？",
                    body = "普通协同账号只需要展示身份。真实姓名、单位证明和急救资质应放在后续认证流程中单独提交。",
                )
            }

            ProfileStep.Ability -> {
                SelectorSection(
                    title = "你的协同能力",
                    options = ProfessionIdentity.entries.map { item ->
                        Triple(item.label, item.subtitle, item == selectedIdentity)
                    },
                    onSelected = { index -> onIdentitySelected(ProfessionIdentity.entries[index]) },
                )
                SmallInfoCard(
                    title = "事件角色动态分派",
                    body = "患者、核心施救、AED 取送和现场引导，会在每次事件中根据位置、健康状态和任务适配度重新分派。",
                )
            }

            ProfileStep.Health -> {
                SelectorSection(
                    title = "身体状态",
                    options = HealthCondition.entries.map { item ->
                        Triple(item.label, item.subtitle, item == selectedHealth)
                    },
                    onSelected = { index -> onHealthSelected(HealthCondition.entries[index]) },
                )
                LraOutlinedTextField(
                    value = bio,
                    onValueChange = onBioChange,
                    label = "个人补充（可选）",
                    supportingText = "可写培训经历、熟悉路线、值班位置等；不填也能完成设置。",
                    modifier = Modifier.fillMaxWidth(),
                )
            }
        }

        Row(horizontalArrangement = Arrangement.spacedBy(10.dp), modifier = Modifier.fillMaxWidth()) {
            PressableButton(
                text = if (stepIndex > 0) "上一步" else "返回登录",
                onClick = onBack,
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF334155), contentColor = Color.White),
                modifier = Modifier.weight(1f),
                enabled = !loading,
            )
            PressableButton(
                text = when {
                    loading -> "提交中..."
                    stepIndex < totalSteps - 1 -> "下一步"
                    else -> "完成设置"
                },
                onClick = onNext,
                colors = ButtonDefaults.buttonColors(containerColor = PhoneColors.Blue, contentColor = Color.White),
                modifier = Modifier.weight(1f),
                enabled = !loading,
            )
        }
    }
}

@Composable
private fun StepHeader(
    step: ProfileStep,
    stepIndex: Int,
    totalSteps: Int,
) {
    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
            repeat(totalSteps) { index ->
                Box(
                    modifier = Modifier
                        .weight(1f)
                        .height(4.dp)
                        .clip(CircleShape)
                        .background(if (index <= stepIndex) Color(0xFF3B82F6) else Color(0xFF1E293B))
                )
            }
        }
        Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
            Text(step.title, color = Color.White, fontSize = 18.sp, fontWeight = FontWeight.Bold)
            Text(step.subtitle, color = PhoneColors.GrayText, fontSize = 12.sp, lineHeight = 18.sp)
        }
    }
}

@Composable
private fun SegmentedChoice(
    text: String,
    selected: Boolean,
    modifier: Modifier = Modifier,
    onClick: () -> Unit,
) {
    Box(
        modifier = modifier
            .clip(RoundedCornerShape(16.dp))
            .background(if (selected) Color(0xFF1D4ED8) else Color(0xFF0F172A))
            .border(
                width = 1.dp,
                color = if (selected) Color(0xFF60A5FA) else Color(0xFF1E293B),
                shape = RoundedCornerShape(16.dp),
            )
            .clickable(onClick = onClick)
            .padding(vertical = 12.dp),
    ) {
        Text(
            text = text,
            color = Color.White,
            fontWeight = FontWeight.Bold,
            modifier = Modifier.align(Alignment.Center),
        )
    }
}

@Composable
private fun SmallInfoCard(
    title: String,
    body: String,
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(18.dp))
            .background(Color(0xFF0B1223))
            .border(1.dp, Color(0xFF1E293B), RoundedCornerShape(18.dp))
            .padding(14.dp),
        verticalArrangement = Arrangement.spacedBy(6.dp),
    ) {
        Text(title, color = Color.White, fontSize = 14.sp, fontWeight = FontWeight.SemiBold)
        Text(body, color = PhoneColors.GrayText, fontSize = 12.sp, lineHeight = 18.sp)
    }
}

@Composable
private fun SelectorSection(
    title: String,
    options: List<Triple<String, String, Boolean>>,
    onSelected: (Int) -> Unit,
) {
    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Text(title, color = Color.White, fontWeight = FontWeight.SemiBold)
        options.forEachIndexed { index, option ->
            val selected = option.third
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(18.dp))
                    .background(if (selected) Color(0xFF172554) else Color(0xFF0F172A))
                    .border(
                        width = 1.dp,
                        color = if (selected) Color(0xFF3B82F6) else Color(0xFF1E293B),
                        shape = RoundedCornerShape(18.dp),
                    )
                    .clickable { onSelected(index) }
                    .padding(14.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Box(
                    modifier = Modifier
                        .size(12.dp)
                        .clip(CircleShape)
                        .background(if (selected) Color(0xFF60A5FA) else Color(0xFF334155))
                )
                Spacer(modifier = Modifier.size(12.dp))
                Column {
                    Text(option.first, color = Color.White, fontWeight = FontWeight.Bold)
                    Text(option.second, color = PhoneColors.GrayText, fontSize = 12.sp, lineHeight = 18.sp)
                }
            }
        }
    }
}

private fun maskPhone(phone: String): String {
    val digits = phone.filter(Char::isDigit)
    return if (digits.length >= 7) {
        "${digits.take(3)}****${digits.takeLast(4)}"
    } else {
        phone
    }
}
