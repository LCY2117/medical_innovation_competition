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
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.lifereflexarc.data.DefaultUserPresets
import com.example.lifereflexarc.data.HealthCondition
import com.example.lifereflexarc.data.ProfessionIdentity
import com.example.lifereflexarc.data.UserPreset
import com.example.lifereflexarc.ui.components.InlineErrorCard
import com.example.lifereflexarc.ui.components.LraOutlinedTextField
import com.example.lifereflexarc.ui.components.PressableButton
import com.example.lifereflexarc.ui.theme.PhoneColors

private enum class AuthMode(val label: String) {
    Register("注册"),
    Login("登录"),
}

@Composable
fun LoginScreen(
    error: String?,
    loading: Boolean,
    onRegister: (String, String, String, String, HealthCondition, ProfessionIdentity, String) -> Unit,
    onLogin: (String, String) -> Unit,
    onInputChanged: () -> Unit,
) {
    var authMode by rememberSaveable { mutableStateOf(AuthMode.Register) }
    var displayName by rememberSaveable { mutableStateOf("") }
    var phone by rememberSaveable { mutableStateOf("") }
    var password by rememberSaveable { mutableStateOf("") }
    var organization by rememberSaveable { mutableStateOf("") }
    var selectedHealth by rememberSaveable { mutableStateOf(HealthCondition.GENERAL) }
    var selectedIdentity by rememberSaveable { mutableStateOf(ProfessionIdentity.BASIC_KNOWLEDGE) }
    var bio by rememberSaveable { mutableStateOf("") }

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
            Spacer(modifier = Modifier.height(24.dp))
            Text("生命反射弧", color = Color.White, fontSize = 32.sp, fontWeight = FontWeight.Black)
            Text(
                text = "先完成真实账号登录，再把用户画像送入调度云端。",
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
                    Text("账号入口", color = Color.White, fontSize = 20.sp, fontWeight = FontWeight.Bold)
                    Text(
                        text = if (authMode == AuthMode.Register) {
                            "注册时提交真实账号信息和急救画像，后续 Web 触发后由 AI 自动分配任务。"
                        } else {
                            "登录使用服务端真实账号，不再只是本地假会话。"
                        },
                        color = PhoneColors.GrayText,
                        fontSize = 12.sp,
                        lineHeight = 18.sp,
                    )

                    Row(horizontalArrangement = Arrangement.spacedBy(10.dp), modifier = Modifier.fillMaxWidth()) {
                        AuthMode.entries.forEach { mode ->
                            val selected = mode == authMode
                            Box(
                                modifier = Modifier
                                    .weight(1f)
                                    .clip(RoundedCornerShape(16.dp))
                                    .background(if (selected) Color(0xFF1D4ED8) else Color(0xFF0F172A))
                                    .border(
                                        width = 1.dp,
                                        color = if (selected) Color(0xFF60A5FA) else Color(0xFF1E293B),
                                        shape = RoundedCornerShape(16.dp),
                                    )
                                    .clickable {
                                        authMode = mode
                                        onInputChanged()
                                    }
                                    .padding(vertical = 12.dp),
                            ) {
                                Text(
                                    text = mode.label,
                                    color = Color.White,
                                    fontWeight = FontWeight.Bold,
                                    modifier = Modifier.align(Alignment.Center),
                                )
                            }
                        }
                    }

                    if (authMode == AuthMode.Register) {
                        Text("默认画像", color = Color.White, fontWeight = FontWeight.SemiBold)
                        Text(
                            text = "这里只填写画像，不直接决定 AED / CPR / 清障角色。具体任务会在患者触发后由 AI 再分配。",
                            color = PhoneColors.GrayText,
                            fontSize = 12.sp,
                            lineHeight = 18.sp,
                        )
                        DefaultUserPresets.forEach { preset ->
                            PresetCard(
                                preset = preset,
                                onApply = {
                                    if (displayName.isBlank()) {
                                        displayName = preset.title
                                    }
                                    selectedHealth = preset.healthCondition
                                    selectedIdentity = preset.professionIdentity
                                    organization = preset.organization
                                    bio = preset.bio
                                    onInputChanged()
                                },
                            )
                        }
                    }

                    if (authMode == AuthMode.Register) {
                        LraOutlinedTextField(
                            value = displayName,
                            onValueChange = {
                                displayName = it
                                onInputChanged()
                            },
                            label = "姓名",
                            modifier = Modifier.fillMaxWidth(),
                        )
                    }

                    LraOutlinedTextField(
                        value = phone,
                        onValueChange = {
                            phone = it
                            onInputChanged()
                        },
                        label = "手机号",
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Phone),
                        modifier = Modifier.fillMaxWidth(),
                    )
                    LraOutlinedTextField(
                        value = password,
                        onValueChange = {
                            password = it
                            onInputChanged()
                        },
                        label = "密码",
                        modifier = Modifier.fillMaxWidth(),
                    )

                    if (authMode == AuthMode.Register) {
                        LraOutlinedTextField(
                            value = organization,
                            onValueChange = {
                                organization = it
                                onInputChanged()
                            },
                            label = "组织 / 场景",
                            modifier = Modifier.fillMaxWidth(),
                        )

                        SelectorSection(
                            title = "身体状况",
                            options = HealthCondition.entries.map { item ->
                                Triple(item.label, item.subtitle, item == selectedHealth)
                            },
                            onSelected = { index ->
                                selectedHealth = HealthCondition.entries[index]
                                onInputChanged()
                            },
                        )

                        SelectorSection(
                            title = "职业身份",
                            options = ProfessionIdentity.entries.map { item ->
                                Triple(item.label, item.subtitle, item == selectedIdentity)
                            },
                            onSelected = { index ->
                                selectedIdentity = ProfessionIdentity.entries[index]
                                onInputChanged()
                            },
                        )

                        LraOutlinedTextField(
                            value = bio,
                            onValueChange = {
                                bio = it
                                onInputChanged()
                            },
                            label = "个人介绍",
                            modifier = Modifier.fillMaxWidth(),
                        )
                    }

                    if (!error.isNullOrBlank()) {
                        InlineErrorCard(message = error)
                    }

                    PressableButton(
                        text = when {
                            loading -> "提交中..."
                            authMode == AuthMode.Register -> "注册并进入协同终端"
                            else -> "登录进入协同终端"
                        },
                        onClick = {
                            if (loading) {
                                return@PressableButton
                            }
                            if (authMode == AuthMode.Register) {
                                onRegister(
                                    displayName,
                                    phone,
                                    password,
                                    organization,
                                    selectedHealth,
                                    selectedIdentity,
                                    bio,
                                )
                            } else {
                                onLogin(phone, password)
                            }
                        },
                        colors = ButtonDefaults.buttonColors(
                            containerColor = if (authMode == AuthMode.Register && selectedHealth.isPatientCandidate) {
                                PhoneColors.Red
                            } else {
                                PhoneColors.Blue
                            },
                            contentColor = Color.White,
                        ),
                        modifier = Modifier.fillMaxWidth(),
                    )
                }
            }
        }
    }
}

@Composable
private fun PresetCard(
    preset: UserPreset,
    onApply: () -> Unit,
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(18.dp))
            .background(Color(0xFF0B1223))
            .border(1.dp, Color(0xFF1E293B), RoundedCornerShape(18.dp))
            .clickable { onApply() }
            .padding(14.dp),
        horizontalArrangement = Arrangement.spacedBy(12.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Box(
            modifier = Modifier
                .size(12.dp)
                .clip(CircleShape)
                .background(if (preset.healthCondition.isPatientCandidate) PhoneColors.Red else PhoneColors.Blue)
        )
        Column(verticalArrangement = Arrangement.spacedBy(4.dp), modifier = Modifier.weight(1f)) {
            Text(preset.title, color = Color.White, fontWeight = FontWeight.Bold)
            Text(preset.description, color = PhoneColors.GrayText, fontSize = 12.sp, lineHeight = 18.sp)
            Text(
                text = "${preset.healthCondition.label} · ${preset.professionIdentity.label}",
                color = Color(0xFF93C5FD),
                fontSize = 11.sp,
            )
        }
        Text("填充", color = Color.White, fontSize = 12.sp, fontWeight = FontWeight.Bold)
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
