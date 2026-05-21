# 第三方资源准备清单

本文档用于集中申请 LifeReflexArc / 生命反射弧在医创赛演示和预实验中需要的第三方资源。原则是：先保证系统无 Key 也能用演示模式跑通，再用地图、AI、推送等服务增强真实感。

## 0. 推荐申请顺序

1. 固定 Android 包名和签名证书。
2. 生成 release keystore，并记录 SHA1。
3. 申请地图 Android Key、Web JS Key、WebService Key。
4. 申请或确认 AI 模型 API Key。
5. 固定云端域名和 HTTPS/WSS。
6. 后续再考虑厂商推送、短信/电话通知。

## 1. 项目固定信息

| 项目 | 建议值 | 说明 |
| --- | --- | --- |
| 产品名称 | 生命反射弧 LifeReflexArc | 医创赛展示名称 |
| Android 包名 | `com.example.lifereflexarc` | 当前代码使用值；若要更正式可后续改为 `top.mddcommunity.lifereflex`，但会影响地图 Key |
| 云端主域名 | `mddcommunity.top` | 已有 |
| 推荐演示子域名 | `lifereflex.mddcommunity.top` | Web 调度台 + API + WebSocket |
| Android API 地址 | `https://lifereflex.mddcommunity.top/` | 必须以 `/` 结尾 |
| Android WS 地址 | `wss://lifereflex.mddcommunity.top/ws` | HTTPS 环境下使用 WSS |
| 后端部署目录 | `/opt/lifereflex` | 统一管理 |

## 2. Android 签名证书

地图 Android Key 通常需要包名和签名证书 SHA1。建议先生成比赛专用 release keystore，再用该证书打 APK。

本地生成示例：

```powershell
keytool -genkeypair -v -keystore lifereflex-release.jks -alias lifereflex -keyalg RSA -keysize 2048 -validity 10000
```

查看 SHA1：

```powershell
keytool -list -v -keystore lifereflex-release.jks -alias lifereflex
```

注意：

- keystore、密码、alias 密码不要提交到 Git。
- 申请地图 Key 时使用 release keystore 的 SHA1。
- 如果用 debug 签名安装，地图 Android Key 需要另建 debug Key 或改为 release 安装包测试。

## 3. 地图与定位服务

### 3.1 推荐主选：高德开放平台

官网入口：

- 开放平台官网：[https://lbs.amap.com/](https://lbs.amap.com/)
- 控制台/应用管理：[https://console.amap.com/dev/key/app](https://console.amap.com/dev/key/app)
- Android 定位 SDK：[https://lbs.amap.com/api/android-location-sdk/summary/](https://lbs.amap.com/api/android-location-sdk/summary/)
- Android 地图 SDK：[https://lbs.amap.com/api/android-sdk/summary/](https://lbs.amap.com/api/android-sdk/summary/)
- JavaScript API 2.0：[https://lbs.amap.com/api/javascript-api-v2/summary/](https://lbs.amap.com/api/javascript-api-v2/summary/)
- Web 服务 API：[https://lbs.amap.com/api/webservice/summary/](https://lbs.amap.com/api/webservice/summary/)

需要申请的 Key：

| Key 类型 | 用途 | 绑定建议 |
| --- | --- | --- |
| Android Key | App 定位、地图展示 | 绑定包名 + SHA1 |
| Web JS Key | Web 调度台地图展示 | 限制域名 `lifereflex.mddcommunity.top` |
| WebService Key | 后端路线规划、逆地理编码 | 仅放服务器环境变量，可配置 IP 白名单 |

申请步骤：

1. 登录高德开放平台。
2. 进入控制台，创建应用：`LifeReflexArc-医创赛`。
3. 添加 Android Key：填写包名和 SHA1。
4. 添加 Web 端 Key：填写域名白名单。
5. 添加 WebService Key：用于后端服务。
6. 把 Key 填入服务器 `.env`，不要写进 Git。

代码环境变量建议：

```bash
LRA_MAP_PROVIDER=amap
LRA_AMAP_WEB_KEY=
LRA_AMAP_WEB_SECURITY_JS_CODE=
LRA_AMAP_SERVICE_KEY=
```

搜索教程关键词：

- 高德开放平台 Android 获取 Key SHA1 包名
- 高德地图 JS API 2.0 安全密钥
- 高德地图 WebService API 路径规划

### 3.2 备选：腾讯位置服务

官网入口：

- 官网：[https://lbs.qq.com/](https://lbs.qq.com/)
- 控制台 Key 管理：[https://lbs.qq.com/dev/console/key/manage](https://lbs.qq.com/dev/console/key/manage)
- Android 地图 SDK 获取密钥文档：[https://lbs.qq.com/mobile/androidMapSDK/developerGuide/getKey](https://lbs.qq.com/mobile/androidMapSDK/developerGuide/getKey)
- JavaScript API GL：[https://lbs.qq.com/webApi/javascriptGL/glGuide/glOverview](https://lbs.qq.com/webApi/javascriptGL/glGuide/glOverview)
- WebService API：[https://lbs.qq.com/service/webService/webServiceGuide/webServiceOverview](https://lbs.qq.com/service/webService/webServiceGuide/webServiceOverview)

适用情况：

- 如果高德账号或配额申请不顺，可以切换腾讯。
- 腾讯生态常见登录方式是微信/QQ，半夜自动申请可能卡在扫码。

需要准备：

- Android 包名
- SHA1
- Web 域名
- 后端服务 IP 或域名限制

### 3.3 备选：百度地图开放平台

官网入口：

- 官网：[https://lbsyun.baidu.com/](https://lbsyun.baidu.com/)
- 控制台：[https://lbsyun.baidu.com/apiconsole/key](https://lbsyun.baidu.com/apiconsole/key)
- Android 地图 SDK：[https://lbsyun.baidu.com/index.php?title=androidsdk](https://lbsyun.baidu.com/index.php?title=androidsdk)
- JavaScript API GL：[https://lbsyun.baidu.com/index.php?title=jspopularGL](https://lbsyun.baidu.com/index.php?title=jspopularGL)
- Web 服务 API：[https://lbsyun.baidu.com/index.php?title=webapi](https://lbsyun.baidu.com/index.php?title=webapi)

适用情况：

- 百度地图对 Web 和国内地址解析支持成熟。
- Android Key 同样通常需要 SHA1 和包名。

## 4. AI 模型服务

### 4.1 SiliconFlow / 硅基流动

官网入口：

- 官网：[https://siliconflow.cn/](https://siliconflow.cn/)
- 控制台：[https://cloud.siliconflow.cn/](https://cloud.siliconflow.cn/)
- API 文档：[https://docs.siliconflow.cn/](https://docs.siliconflow.cn/)

用途：

- AI 调度角色分派。
- 生成调度解释。
- 比赛展示“AI 参与急救协同决策”的核心证据之一。

后端环境变量：

```bash
LRA_SILICONFLOW_API_KEY=
LRA_SILICONFLOW_MODEL=Qwen/Qwen2-7B-Instruct
LRA_SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
LRA_SILICONFLOW_TIMEOUT_SEC=8
```

安全要求：

- API Key 只放服务器 `.env`。
- App 和 Web 前端不直接持有 AI Key。
- AI 不可用时自动降级本地规则调度。

## 5. 域名、证书、反向代理

已有条件：

- 服务器 IP：`104.248.151.6`
- 主域名：`mddcommunity.top`
- 1Panel + OpenResty

推荐：

- 子域名：`lifereflex.mddcommunity.top`
- 后端端口：`18080` 或类似空闲端口
- 对外路径：
  - Web：`https://lifereflex.mddcommunity.top/`
  - API：`https://lifereflex.mddcommunity.top/api/*`
  - WebSocket：`wss://lifereflex.mddcommunity.top/ws`

证书：

- 优先用 1Panel 申请和自动续签。
- 命令行配置时必须写入 1Panel 数据库记录，方便面板管理。

## 6. 后续可选：推送、短信、电话

比赛版先不强依赖。

可选路线：

| 能力 | 推荐时机 | 说明 |
| --- | --- | --- |
| 厂商推送 | 真实落地后 | 华为/小米/OPPO/VIVO 配置复杂，账号审核多 |
| 短信通知 | 真实落地后 | 阿里云/腾讯云短信需要签名和模板审核 |
| 电话外呼 | 真实落地后 | 合规成本更高，不适合第一版 |

比赛演示建议：

- App 前台 WebSocket 实时推送。
- 后台/锁屏推送用“后续计划”描述。

## 7. 半夜自动申请策略

可以自动推进：

- 打开官网和控制台入口。
- 查找申请页面。
- 填写非敏感基础项目名称。
- 截图或记录所需字段。

需要早上人工处理：

- 微信/QQ扫码登录。
- 邮箱/SMS验证码。
- 实名认证。
- 付费或开通计费。
- 创建最终 Key 前的法律协议确认。
- 复制真实 Key 给服务器环境变量。

## 8. 申请完成后交给开发的内容

请集中提供：

```text
地图服务商：高德 / 腾讯 / 百度
Android Key：
Android Key 绑定包名：
Android Key 绑定 SHA1：
Web JS Key：
Web 安全密钥/安全码（如高德 jscode）：
WebService Key：
AI Provider：
AI API Key：
正式域名：
```

不要把这些 Key 发到公开仓库；可以让我直接写入服务器 `.env` 或本机未提交的 `.env`。

## 9. Provider 接入契约

第三方能力全部按“真实 provider + demo fallback”接入，避免 Key、审核、配额或网络波动阻塞医创赛演示。

| 能力 | provider 环境变量 | 真实 provider | fallback | 前端/APP 暴露内容 |
| --- | --- | --- | --- | --- |
| 地图/距离 | `LRA_MAP_PROVIDER` | `amap`、后续可扩展 `tencent`、`baidu` | `demo` 内置坐标和后端 Haversine 距离 | 仅展示点位、距离、路线提示，不暴露服务端 Key |
| AI 调度 | `LRA_PREFER_LOCAL_MODEL` + `LRA_SILICONFLOW_*` | 本地 OpenAI-compatible 或 SiliconFlow | 规则调度 | 展示调度来源、评分、理由、风险提示 |
| 健康数据 | `LRA_HEALTH_PROVIDER` | OPPO Health SDK/API | mock/manual health summary | 展示“演示健康数据/OPPO 健康模拟接入”，不作临床诊断 |
| 推送 | 未来 `LRA_PUSH_PROVIDER` | 厂商推送/极光 | 前台 WebSocket + 移动 Web 轮询 | 展示实时同步状态，不承诺锁屏必达 |
| 短信/验证码 | 未来 `LRA_SMS_PROVIDER` | 阿里云/腾讯云短信 | 密码账号 + demo persona | 比赛版不把短信作为登录阻塞项 |

后续编码原则：

- 服务端 Key 只进入服务器 `.env` 或 secret storage，前端和 Android 不直接持有服务端 Key。
- provider 不可用时返回结构化状态，例如 `provider=demo`、`source=fallback`、`warning=quota_or_key_missing`，不要让用户看到堆栈错误。
- 调度解释必须记录 provider 来源，预实验证据包中保留 `dispatchSource` 和健康摘要 `source`。
- 对外材料只说“可接入某 provider / 已完成接口预埋 / 当前演示使用 fallback”，不把 fallback 说成真实第三方数据。
- 申请到 Key 后优先只改 `.env` 和 provider adapter，避免重写业务流程。
