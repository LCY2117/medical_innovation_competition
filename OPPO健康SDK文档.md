# 健康服务介绍

OPPO健康服务是为开发者提供查询用户穿戴设备数据的能力，在接入服务且获得用户授权后，开发者能够快速获取运动健康相关数据，为用户提供丰富的运动健康相关服务。

## 服务优势

1、开放丰富的运动健康相关数据，包括运动记录、睡眠数据、心率数据、压力数据、心电记录、血氧数据等
2、OPPO健康服务为开发者和用户提供完善的授权流程，保证用户数据使用的合法合规，在提供高效便捷服务的同时保障用户隐私安全。
3、提供客户端SDK和云端API两种接入方式，开发者可以按需选择更合适的方式。
4、OPPO健康服务覆盖亿级用户，能够为开发者提供全面、丰富的用户资源。

# 健康服务接入流程

## 申请合作

如需申请接入OPPO健康服务，请发邮件至商务邮箱liujinxin1@oppo.com，说明应用名称、合作目的、合作计划、健康数据权限需求。申请健康数据权限请遵循权限最小化原则。
注意：双方确认合作意向后，需要签署保密协议和数据使用协议。

## 提供材料

开发者与OPPO方完成协议签署后，请准备以下申请材料并发邮件至sporthealth@oppo.com，预计 3 个工作日内审核并回复。若选择云云对接方式，审核通过后将发放clientId和clientSecret 。

| 材料                          | 是否必填 | 说明                                                         |
| ----------------------------- | -------- | ------------------------------------------------------------ |
| logo                          | 是       | 图标，授权时显示，尺寸520*520px，大小不超过3M                |
| host                          | 是       | 跳转地址 redirect_uri 的 host 部分，用于校验认证时的 redirect_uri 参数，域名不同会导致授权失败 |
| appName                       | 是       | 应用名称                                                     |
| applicationUniqueId           | 是       | 应用唯一标识。 例如： C3:3A:64:FB:08:58:36:F0:3d:B0:68:FB:14:76:B7:6D:DC:CA:CF:E3 |
| appPackageName                | 是       | 应用包名。 例如 com.oppo.sporthealth                         |
| heartRateExceptionRedirectUri | 否       | 心率异常消息推送，三方订阅该消息后需要提供                   |
| tumbleRedirectUri             | 否       | 跌倒消息推送，三方订阅该消息后需要提供                       |

## 流程图

![image1.png](./assets/0f64dec8e42b8fe74030f1dccda4d5b2.png)

# 健康服务SDK个人信息保护政策

最新更新时间：2023 年 9 月 18日

 

健康服务SDK是广东欢太科技有限公司（注册地址：

广东省东莞市长安镇乌沙兴一路112号202室，邮编：523859）（以下简称“我们”）开发/运营并提供的软件开发工具包。

OPPO健康服务是为开发者提供查询用户穿戴设备数据的能力，在接入服务且获得用户授权后，开发者能够快速获取运动健康相关数据，为用户提供丰富的运动健康相关服务。

当您在使用集成健康服务 SDK的产品和服务过程中，我们可能会收集、存储、使用、加工、传输、提供、公开、删除（统称“处理”）您的个人信息。其中，个人信息指以电子或者其他方式记录的能够单独或者与其他信息结合识别自然人个人身份的各种信息。

我们非常注重保护您的个人信息及隐私，我们深知个人信息对您的重要性，我们根据适用法律法规及国家标准制订了《健康服务SDK个人信息保护政策》（以下简称“本政策”）。我们将通过本政策向您说明我们处理您的个人信息的目的、方式、范围，以及您拥有管理个人信息的权利和实现方式，并向您阐述我们为保护信息安全所采取的安全保护措施。

仔细阅读本政策，以了解我们处理您个人信息的做法，特别是重点阅读我们以粗体标识的条款。请您知悉，您同意本政策仅代表您已了解我们的产品/服务所提供的功能，以及同意我们处理功能运行所需的个人信息。对于本政策涉及的**敏感个人信息的处理以及可能对您的权益有重大关系的条款**，**我们将采用加粗形式进行提示**，请您留意阅读。同时，**对敏感个人信息，我们用“加粗”的书写方式进行特别提醒，希望您在阅读时特别关注。**

 

## **【特别提示】**

**如果您是开发者****：**

**您集成、使用健康服务 SDK相关产品和功能****，****涉及的数据和个人信息处理应符合有关国家或地区涉及国家安全、网络安全、数据安全、个人信息保护的相关法律法规、标准规范，并采取适当充分的技术型和组织性安全保护措施。不得从事任何违反国家安全、网络安全、数据安全，侵犯最终用户隐私和个人信息权益的违法行为。**

**在接入、使用****健康服务** **SDK和****相关****服务****/功能****前，请按照本****政策的****要求在您应用的****个人信息保护****政策中****以显著方式、通俗易懂的语言，****向您的用户告知SDK相关信息，并获取用户的同意或取得其他合法性基础****，确保用户是在理解和同意后使用接入健康服务 SDK相关产品和功能的****。**

**基于不同的设备类型和设备型号，应****用****和系统版本****，****以及开发者****在****集成、****使用****健康服务 SDK时决定的权限，健康服务 SDK收****集****、使用的信息会有所不同，因此开发者应按照实际收集的个人信息向用户进行说明。**

**健康服务 SDK作为数据的委托处理者，不是数据的处理者，数据的使用方式、目的和方式由手机和第三方****应用****与服务开发者自行决定。如有任何涉及数据处理、个人信息保护方面的监管问询、争议纠纷，用户有任何涉及个人信息权利行使方面的诉求****，****手机和手表的应用与服****务****开发者应自行解决，健康服务 SDK可自主决策提供相应协助，如发生数据泄露，****相关应用的****数据处理者应****及****时通知我们。**

**为了向用户提供最新的、****安全****的服务****，****我们会不时更新SDK版本。我们强烈建议****开****发者集成****使用****最新版本的SDK****。**

 

**本政策将帮助您了解以下内容：**

一、我们如何收集和使用您的个人信息

二、我们如何存储和保留您的个人信息

三、我们如何委托处理、共享、转让或公开披露您的个人信息

四、我们如何保护您的个人信息

五、您对您的个人信息的权利

六、我们如何处理儿童的个人信息

七、本政策如何更新

八、联系我们

 

## 一、我们如何收集和使用您的个人信息

我们会遵循按国家法律法规要求，恪守正当、合法、必要的原则保护您的个人信息，仅出于本政策所述的业务功能需要以及目的，并在征得您的同意下，您在使用第三方应用授权运动健康数据使用健康服务SDK过程中提供的相关信息。

**本平台提供基本业务功能和扩展业务功能。我们不会因您不同意收集扩展业务功能中的个人信息，而拒绝您使用健康服务的基本业务功能服务。如果我们拟将您的个人信息用于本政策未载明的其它用途或其他特定目的，我们将以合理的方式告知您，并再次征得您的同意。**

 

### 1.1 基本功能

为了向应用开发者和其用户提供本SDK和服务，我们会收集、使用、传输、存储服务所必需的如下个人信息。

#### 1.1.1 收集个人信息

| **个人信息类型** | **个人信息字段**                                             | **使用目的**                                      | **存储期限说明**               | **必要/可选个人信息**         |
| ---------------- | ------------------------------------------------------------ | ------------------------------------------------- | ------------------------------ | ----------------------------- |
| 应用基本信息     | 健康APP包名信息                                              | 用于判断应用安装状态，以支持APP端与第三方数据传输 | 本地不存储，不上云             | 必要个人信息：健康APP包名信息 |
| 应用商店包名信息 | 当API在OPPO手机上使用时，若未安装健康，将引导跳转至软件商店下载 | 本地不存储，不上云                                | 可选个人信息：应用商店包名信息 |                               |

#### 1.1.2 仅作为通道传输个人信息

| 传输路径            | **个人信息类型**                                             | **个人信息字段**                                   | **使用目的**                                 | **存储期限说明**                 | **必要/可选个人信息**            |
| ------------------- | ------------------------------------------------------------ | -------------------------------------------------- | -------------------------------------------- | -------------------------------- | -------------------------------- |
| 健康APP传输给第三方 | 个人身份类                                                   | **ssoid映射后形成的虚拟用户ID**                    | 用于用户账号绑定                             | 本地不存储，不上云               | 必要个人信息                     |
| **运动健康数据**    | **压力、心率、心电记录、睡眠、血氧**、步数、消耗、锻炼时长、活动次数、运动记录 | 提供数据共享服务，助力开发者给用户提供运动健康服务 | 本地不存储，不上云                           | 可选个人信息（开发者和用户可选） |                                  |
| 第三方传输给健康APP | 运动数据                                                     | 运动记录                                           | 提供数据同步写入服务，给用户提供运动记录功能 | 本地不存储，不上云               | 可选个人信息（开发者和用户可选） |
| 设备信息            | 穿戴设备MAC地址                                              | 标识设备信息，提供数据同步写入服务                 | 本地不存储，不上云                           | 必要个人信息                     |                                  |

 

### 1.2 权限声明

健康服务SDK不会调用任何权限。

 

## 二、我们如何存储和保留您的个人信息

### 2.1 存储地点

我们依照法律法规的规定，将在中华人民共和国境内（简称“境内”）运营过程中收集、产生的您的个人信息存储于境内的服务器。

 

### 2.2 存储时间

我们将按照法律法规规定的为提供产品/服务之目的所必需且最短的期间内保留您的个人信息。在任何存储期限结束或符合删除的其他条件时，我们会对您的个人信息将进行删除或匿名化处理，但法律法规另有规定的除外。

在我们因特殊原因停止运营我们的部分或全部产品或服务时，我们会及时向您告知并停止相关产品或服务的个人信息收集和处理活动，同时将我们所持有的与该述产品或服务相关的个人信息进行删除或匿名化处理，除非法律法规另有规定。

健康服务 SDK涉及处理的个人信息不做存储，也不涉及上传服务器。

 

## 三、我们如何委托处理、共享、转让、披露您的个人信息

### 3.1 委托处理

为了向您提供更完善、更优质的服务，我们可能会委托关联公司或其他专业服务提供商代表我们来处理信息，例如我们会聘请服务提供商为我们提供基础设施技术支持和服务、客户支持服务等。对于委托处理个人信息的场景，我们会根据法律法规规定通过书面协议、现场审计等方式要求受托合作方（公司、组织和个人）遵守严格的保密义务并采取有效的保密措施，要求其只能在委托范围内处理您的信息，而不得出于其自身利益使用您的信息。书面协议中会严格约定委托处理的目的、期限、处理方式、个人信息的种类、保护措施以及双方的权利和义务等，并对受托人的个人信息处理活动进行监督。

 

### 3.2 我们如何共享、转让您的个人信息

我们可能不时会与其关联公司和与我们合作提供产品和服务的战略合作伙伴共享部分个人信息或在其他情形中共享、转让您的个人信息，以便提供您要求的产品或服务。

（1）关联公司：为便于我们基于手机上的生态应用与服务给穿戴设备发消息、发通知、传输数据，并获取穿戴设备状态、读取传感器数据等，也可以实现穿戴设备上的生态应用与服务给手机发消息、传输数据等服务，您的个人信息可能会与我们的关联公司共享，例如手机和穿戴设备终端涉及的关联公司。我们只会共享必要的个人信息，如果我们或关联公司改变个人信息的使用及处理目的，将再次征求您的授权同意。

（2）与授权合作伙伴共享：仅为实现本政策中声明的目的，我们的某些服务将由授权合作伙伴提供。我们可能会与合作伙伴共享您的某些个人信息，以提供合作向您提供服务并提升用户体验。

（3）在涉及合并、收购或破产清算时，如涉及到个人信息转让，我们会在要求新的持有您个人信息的公司、组织继续受本政策的约束，否则我们将要求该公司、组织重新向您征求授权同意。如果不涉及个人信息转让，我们会对您进行充分告知，并将我们控制的所有个人信息删除或做匿名化处理。

我们仅会出于合法、正当、必要、特定、明确的目的共享或转让您的个人信息，并且只会共享服务所必需的个人信息。同时，我们会通过协议或其他适当措施，要求上述第三方采取相当的保密和安全措施来处理个人信息。

 

### 3.3 我们如何公开披露您的个人信息

我们仅会在以下情况下，公开披露您的个人信息：

（1）获得您明确同意后；或

（2）基于法律的披露：在法律强制要求遵守传票或其他法律程序、诉讼或政府主管部门强制性要求的情况下，若我们真诚地相信披露对保护我们的权利、保护您的安全或他人的安全、调查欺诈或响应政府要求是必要的，我们可能会披露您的个人信息。

 

### 3.4 委托处理、共享、转让或公开披露个人信息的授权同意例外

您已充分知晓，依据可适用的法律，在以下情形中，我们共享、转让或公开披露您的个人信息无需事先征得您的授权同意：

（1）与我们履行法律法规规定的义务相关的；

（2）与国家安全、国防安全直接相关的；

（3）与公共安全、公共卫生、重大公共利益直接相关的；

（4）与刑事侦查、起诉、审判和判决执行等直接相关的；

（5）出于维护您或其他个人的生命、财产等重大合法权益但又很难得到您本人授权同意的；

（6）所涉及的个人信息是您已自行向社会公众公开的；

（7）从合法公开披露的信息，如合法的新闻报道、政府信息公开等渠道，收集的您的个人信息的。

 

## 四、我们如何保护您的个人信息

### 4.1 我们如何保护您的个人信息

我们采取了合理可行的技术安全和组织措施，以保护所收集的与服务有关的信息。我们已使用符合业界标准的安全防护措施保护您提供的个人信息，防止数据遭到未经授权的访问、公开披露、使用、修改、损坏或丢失。我们会采取一切合理可行的措施，保护您的个人信息，包括：

（1）我们使用 SSL 等主流安全技术手段对许多服务进行加密。我们会定期审查信息收集、存储和处理方面的做法（包括物理性安全措施），以避免各种系统遭到未经授权的访问或篡改。

（2）根据有关法规要求，我们任命了个人信息保护负责人并成立了个人信息保护工作机构。我们还建立了相关的内控管理流程，以最小授权为原则，我们对个人信息的访问进行严格的权限管控，只允许那些为了帮我们处理个人信息而需要知晓这些信息的我们的员工，授权代为处理的服务公司的人员访问个人信息，而且他们需要履行严格的合同保密义务，如果其未能履行这些义务，就可能会被追究法律责任或被终止其与我们的关系。个人数据的访问日志将被记录，并定期审计。针对需要访问***敏感个人信息\***的员工，其访问权限由相关管理人员审批，记录访问情况，并采取技术措施，避免违法访问、修改、复制、下载个人信息。

（3）对我们来说，您的信息的安全非常重要。因此，我们将不断努力保障您的个人信息安全，并实施存储和传输全程安全加密等保障手段，以免您的信息在未经授权的情况下被访问、使用或披露。同时，某些加密数据的具体内容，除了用户自己，其他人都无权访问。

（4）我们在传输和存储您的特殊类型个人信息时，会采用加密等安全措施；存储个人生物识别信息时，将采用技术措施处理后再进行存储，例如仅存储个人生物识别信息的摘要。

（5）我们会严格筛选业务合作伙伴和服务提供商，将在个人信息保护方面的要求落实到双方的商务合同或审计、考核等活动中。

（6）公司内部颁布实施数据安全管理规范，明确对用户数据（包括用户个人信息）的保护标准和要求。

（7）我们会举办安全和隐私保护培训课程、测试与宣传活动，加强员工对于保护个人信息重要性的认识。

（8）我们采用国际及业内认可的标准来保护您的个人信息，并积极通过相关安全与隐私保护认证，并与监管方、第三方安全服务提供商、测评认证机构建立良好的协调沟通机制，及时抵御并处置信息安全威胁，保护您的个人信息及隐私安全。

 

### 4.2 个人信息安全事件的通知与应对

但是请注意，虽然我们采取了合理的措施保护您的信息，但没有任何网站、Internet 传输、计算机系统或无线连接是绝对安全的。

在发生个人信息安全事件后，我们将按照相关法律法规的要求，及时向您告知：安全事件的基本情况和可能的影响、我们已采取或将要采取的处置措施、您可自主防范和降低风险的建议、对您的补救措施等。我们将及时将事件相关情况以邮件、信函、电话、推送通知等方式告知您。难以逐一告知个人信息主体时，我们会采取合理、有效的方式发布公告。同时，我们还将按照监管部门要求，主动上报个人信息安全事件的处置情况。

 

## 五、您如何实现您作为个人信息主体的权利

我们尊重您对您个人信息的权利，并全力保护您对您个人信息的控制权。为此，我们为您提供多种方式方便您更安心、更便捷地进行隐私设置及个人信息管理，保障您的个人信息安全。**请注意，不同操作系统、产品软件的不同版本之间，操作设置可能存在差异；**此外，为了优化您的使用体验，我们可能对操作设置进行调整。故如下管理路径仅供参考，若您对行使相关权利的方式及途径有任何疑问的，您可以通过本政策「第八章“联系我们”」披露的方式与我们联系。在符合相关法律规定且技术可行的前提下，我们会响应您的权利请求。

以下列出您依法享有的权利，以及我们将如何保护您的这些权利：

（1）您可以通过OPPO开放平台访问本政策，并查阅OPPO健康服务SDK处理您个人信息的情况。

（2）您可以在健康App，点击个人头像进入个人中心，点击“数据共享与授权”选择对应的第三方应用进行授权、查看和取消。

 

## 六、我们如何保护未成年人的个人信息

我们非常重视儿童个人信息的保护。**OPPO 健康服务SDK并不以儿童（不满14周岁的未成年人）为服务对象**。请您留意，由于技术条件等客观限制，可能无法主动识别用户的年龄。

如果您是儿童，**在使用第三方应用以及OPPO 健康服务 SDK前，应事先征得您父母或其他监护人的同意**，并务必和您的父母或其他监护人一起仔细阅读并充分理解本政策、我们专门制定的《[欢太儿童个人信息保护政策](https://muc.heytap.com/document/heytap/childrenPrivacyPolicy/privacyPolicy_zh-CN.html)》、以及其他服务条款，并在征得您的父母或其他监护人的同意后，使用我们的产品和/或服务。未经儿童父母及其他监护人的同意，儿童不得使用我们的产品/服务。

如果您是儿童的家长或其他监护人，或您通过其他方式发现我们处理的信息中可能包括儿童的个人信息，请按照本政策中提供的联系方式与我们联系，我们会设法尽快删除相关数据。

 

## 七、本隐私政策的查阅和更新

### 7.1 查阅个人信息保护政策

您可以通过OPPO开放平台访问本政策，并查阅OPPO 健康服务SDK处理您个人信息的情况。

### 7.1 更新个人信息保护政策

我们保留不时更新或修改本政策的权利。我们会通过不同渠道向您发送变更通知。对于本政策的重大变更，若您向我们提供了电子邮箱，我们会在变更生效前通过您的电子邮件通知您，否则我们会在我们的网站上发布告示或通过我们的设备向您推送通知。

本政策容许调整，但未经您明示同意，我们不会削弱您按照本政策所享有的权利。

如您不同意以上本政策我们将无法收集和使用提供服务所必需的信息，从而无法为您正常提供服务。

 

## 八、联系方式

如果您对本政策或个人信息保护相关事宜有任何问题，或您有任何建议、投诉，您可以通过以下方式与我们联系：

个人信息主体权利行使平台：为了更好的保护您的个人权益，我们专门设立了个人信息主体权利行使平台https://brand.heytap.com/privacy-feedback.html。

广东欢太科技有限公司

广东省东莞市长安镇乌沙兴一路112号202室，邮编：523859

邮编：523902

# 健康服务SDK合规使用说明

请开发者在接入和使用OPPO健康服务SDK前，按照本说明要求在您的隐私政策中向最终用户告知SDK相关信息，并获取用户的同意或取得其他合法性基础。同时，您也可以根据您应用实际情况按需做隐私合规配置。

 

## 一、SDK处理的个人信息

为了向开发者和其最终用户提供本SDK和服务，我们会处理（包括但不限于收集、使用、传输、存储）服务所需要的个人信息，以及为最终用户提供行使权利的途径，详情请见[OPPO健康服务SDK个人信息保护政策](https://open.oppomobile.com/documentation/page/info?id=12478)。

开发者在接入和使用OPPO健康服务SDK前，请在集成SDK的应用隐私政策中向最终用户告知我们SDK的名称、公司名称、收集个人信息种类、使用目的、隐私政策链接，并获取用户的同意或取得其他合法性基础。您可以参照以下方式将OPPO健康服务SDK相关信息加入到您应用的隐私政策：

第三方SDK名称：OPPO健康服务SDK

第三方公司名称：广东欢太科技有限公司

收集个人信息种类：应用基本信息（健康APP包名、应用商店包名）

使用目的：用于判断应用安装状态，以支持APP端与第三方数据传输

隐私政策链接：https://sport.health.heytapmobi.com/h5/statement/index.html#/?langCode=zh-CN&appPackName=com.heytap.health:sdk&contentType=16&osType=1&appVersion=

 

## 二、SDK权限说明

SDK未调用任何权限

 

## 三、SDK合规配置说明

SDK各项可选个人信息使用目的、场景及对应关闭的配置方式、示例

| **基础业务功能下可选个人信息类型**                           | **使用目的、场景**                                 | **对应关闭的配置方式**                                       | **示例**                                                     |
| ------------------------------------------------------------ | -------------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| 运动健康数据（从健康APP读取）[数据类型](https://open.oppomobile.com/documentation/page/info?id=11530) | 提供数据共享服务，助力开发者给用户提供运动健康服务 | 开发者：不调用对应API，即不调用dataApi().read(DataReadRequest readRequest, HResponse<List<DataSet>> rsp)接口。 用户：取消授权，用户可以通过点击右上角头像进入到“个人中心”页面->"数据共享与授权“选择已授权的应用，进行取消授权 | 调用接口：dataApi().read(DataReadRequest readRequest, HResponse<List<DataSet>> rsp); |
| 运动数据（将数据写入至健康APP）[数据类型](https://open.oppomobile.com/documentation/page/info?id=11530) | 提供数据同步写入服务，给用户提供运动记录功能       | 开发者：不调用对应API，即不调用dataApi().insert(DataInsertRequest insertRequest, HResponse<Integer> rsp)接口。 用户：取消授权，用户可以通过点击右上角头像进入到“个人中心”页面->"数据共享与授权“选择已授权的应用，进行取消授权 | 调用接口：dataApi().insert(DataInsertRequest insertRequest, HResponse<Integer> rsp); |

 

## 四、SDK初始化

请开发者在集成SDK的应用获取最终用户同意后才能调用OPPO健康服务SDK接口初始化SDK，以避免SDK提前收集使用个人信息。SDK初始化完成，调用接口申请用户授权，授权成功后才能正常使用对应的业务api。参考：[开发接入](https://open.oppomobile.com/documentation/page/info?id=11520)

 

## 五、SDK需要取得最终用户单独同意的场景以及建议方式/示例

| **取得最终用户单独同意的场景**                 | **建议方式/示例**                                          |
| ---------------------------------------------- | ---------------------------------------------------------- |
| 用户授权OPPO健康服务SDK共享数据至第三方App     | 在第三方App中提供授权入口，点击跳转至健康App并拉起授权页面 |
| 用户授权OPPO健康服务SDK第三方App共享数据至健康 | 在第三方App中提供授权入口，点击跳转至健康App并拉起授权页面 |

 

## 六、主要API

1.IAuthorityApi

| 接口                                                         | 功能                                                         |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| void request(Activity activity, HResponse<AuthResult> callback); | 请求授权，三方应用向开发者平台申请权限由OPPO后台配置，该接口为拉起健康用户授权页面，请求用户进行授权 |
| void request(Activity activity, String redirectUrl, HResponse<AuthResult> callback); | 请求授权，三方应用向开发者平台申请权限由OPPO后台配置，该接口为拉起健康用户授权页面，请求用户进行授权 |
| void revoke(HResponse<List<Object>> callback);               | 取消授权，取消三方应用所有权限                               |
| void valid(HResponse<List<String>> callback);                | 查询权限列表，返回用户已授权的权限列表                       |

 

2.ISportHealthApi

| 接口                                                         | 功能                                                         |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| <T> void query(HeytapHealthParams params, HResponse<List<T>> hResponse); | 旧的查询每日活动、心率数据接口，权限校验在健康APP中，用户可以通过点击右上角头像进入到“个人中心”页面->"数据共享与授权“选择已授权的应用，进行取消授权。 |

 

3.IUserInfoApi

| 接口                                                  | 功能                                                       |
| ----------------------------------------------------- | ---------------------------------------------------------- |
| void query(HResponse<List<UserInfoProxy>> hResponse); | 旧接口，查询健康当前用户信息。                             |
| void readInfo(HResponse<List<DataSet>> hResponse);    | 新接口，查询健康当前用户信息，返回云端分配的虚拟的openId。 |

 

4.IHealthDataApi

| 接口                                                         | 功能                                                         |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| void read(DataReadRequest params, HResponse<List<DataSet>> hResponse); | 将三方应用申请且用户授权的健康APP的运动健康数据共享给三方应用 |
| void insert(DataInsertRequest params, HResponse<Integer> hResponse); | 将三方应用申请且用户授权的运动健康数据共享至健康APP          |

 

5.InstallUtils

| 方法名                                                       | 方法介绍                            |
| ------------------------------------------------------------ | ----------------------------------- |
| public static boolean isAppInstalled(Context context, String packageName) | 查询设备中是否存在指定APP（已安装） |
| public static void DownloadApp(Activity activity)            | 通过浏览器页面下载健康APP           |

 

# 能力说明

SDK信息

| **名称**         | **内容**                                                     |
| ---------------- | ------------------------------------------------------------ |
| SDK名称          | OPPO健康服务SDK                                              |
| 开发者           | 广东欢太科技有限公司                                         |
| 版本号           | 2.1.7                                                        |
| 主要功能         | 运动数据、健康数据共享                                       |
| 个人信息处理规则 | [OPPO健康服务SDK个人信息保护政策](https://open.oppomobile.com/documentation/page/info?id=12478) |
| 合规使用说明     | [OPPO健康服务SDK合规使用说明](https://open.oppomobile.com/documentation/page/info?id=12482) |

 

API总入口为HeyTapHealthApi，在安装好HeyTap Health App且API初始化后，便可使用其各项接口，实现数据的相关授权和读取操作。



API总大小约为350 kB（aar格式），各接口常规响应时间除首次访问需启动相关进程外，一般为30 ms以内。以下将介绍各接口功能。

## **dataApi(2.0.4之后）**

HealthDataApi负责运动健康类数据的读取。



读取数据前需先设置数据的类型（如每日活动，心率）和模式（详情或统计），详情见[数据类型](https://open.oppomobile.com/documentation/page/info?id=11530)。

## **AuthorityApi**

AuthorityApi负责权限的请求，校验与删除。



请求权限将会拉起HeyTap Health App的授权页面。权限列表与三方事先申请好的权限一致，用户只有至少勾选一项权限，才能授权成功。



校验权限提供三方权限检查，可返回三方已授权权限范围



解除权限将会撤销用户对三方App的全部授权。

## **SportHealthApi（2.0.4之后不推荐使用）**

SportHealthApi负责运动健康类数据的读取。



读取数据前需先设置数据的类型（如每日活动，心率）和模式（详情或统计），详情见[数据类型](https://open.oppomobile.com/documentation/page/info?id=11530)。

## **UserInfoApi**

UserInfoApi负责用户信息类数据的读取。

# SDK下载

## **下载环境配置**

1.在顶级gradle文件中添加maven仓库：

maven {  url '[https://maven.columbus.heytapmobi.com/repository/heytap-health-releases/](https://maven.columbus.heytapmobi.com/repository/heytap-health-releases/') ['](http://maven.columbus.oppoer.me/repository/heytap-health-releases/')  allowInsecureProtocol = **true**  credentials {    username "healthUser"    password "8174a9eac1264495b593a9d5ab221491"  }}maven {  url '[https://maven.columbus.heytapmobi.com/repository/heytap-health-snapshots/](https://maven.columbus.heytapmobi.com/repository/heytap-health-snapshots/') ['](http://maven.columbus.oppoer.me/#browse/browse:heytap-health-snapshots/')  allowInsecureProtocol = **true**  credentials {    username "healthUser"    password "8174a9eac1264495b593a9d5ab221491"  }}

 

2.在模块gradle文件中添加依赖：

implementation 'com.heytap.health:sdk:{$latestVersion}'

latestVersion填写sdk版本号。

点击sync，如果报错：problem occurred evaluating root project 'My Application'.

\> Build was configured to prefer settings repositories over project repositories but repository 'Google' was added by build file 'build.gradle'

请将顶级gradle刚加的内容剪切到settings.gradle文件中dependencyResolutionManagement下的repositories中。

```java
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
        maven {
            url 'https://maven.columbus.heytapmobi.com/repository/heytap-health-releases/'
            allowInsecureProtocol = true
            credentials {
                username "healthUser"
                password "8174a9eac1264495b593a9d5ab221491"
            }
        }
        maven {
            url 'https://maven.columbus.heytapmobi.com/repository/heytap-health-snapshots/'
            allowInsecureProtocol = true
            credentials {
                username "healthUser"
                password "8174a9eac1264495b593a9d5ab221491"
            }
        }
    }
}
```

# 开发接入

## 环境准备

### HeyTap Health App安装

由于App-Api是本地调用，因此使用时必须安装HeyTap Health App, 建议开发者使用前向用户申明此点。Api提供引导下载的接口供开发者使用，当Api在OPPO手机上使用时，接口将引导至软件商店HeyTap Health商店页；当其在三方手机上使用时，将打开浏览器跳转至HeyTap Health的H5页面。具体使用方法见下例：

```scss
  InstallUtils.downloadApp(activity);  
```

自Android 11开始，无法直接通过packageMaganer拉起app，因此，如果要在OPPO手机上拉起软件商店，请开发者在app模块的Manifest里添加以下语句：

```xml
<queries>
    <package android:name= "com.heytap.market"/>
    <package android:name= "com.oppo.market"/>
</queries>
```

### API初始化

开始调用api前需进行初始化，首先进行init，之后开始调用接口，申请授权或读取数据。

```csharp
  HeytapHealthApi.init(context);  
```

自Android 11开始，无法直接通过packageMaganer拉起app，因此，使用OPPO健康服务时，请开发者在app模块的Manifest里添加以下语句：

```xml
<queries>
    <package android:name= "com.heytap.health"/>
</queries>
```

### 设置API的log打印

api默认log关闭，如需使用log，需手动设置，getter与setter方法如下：

```java
HeytapHealthApi.setLoggable(loggable); //setter
HeytapHealthApi.isLoggable(); //getter
```




# 数据类型

| DataType                   | 数据含义         |
| -------------------------- | ---------------- |
| TYPE_HEART_RATE            | 心率详情         |
| TYPE_HEART_RATE_COUNT      | 心率统计         |
| TYPE_DAILY_ACTIVITY        | 每日活动详情     |
| TYPE_DAILY_ACTIVITY_COUNT  | 每日活动统计     |
| TYPE_PRESSURE              | 压力详情         |
| TYPE_PRESSURE_COUNT        | 压力统计         |
| TYPE_BLOOD_OXYGEN          | 血氧详情         |
| TYPE_BLOOD_OXYGEN_COUNT    | 血氧统计         |
| TYPE_SLEEP                 | 睡眠详情         |
| TYPE_SLEEP_COUNT           | 睡眠统计         |
| TYPE_ECG                   | 心电             |
| TYPE_HEARING_HEALTH        | 听力详情         |
| TYPE_HEARING_HEALTH_COUNT  | 听力统计         |
| TYPE_RELAX                 | 放松详情         |
| TYPE_RELAX_COUNT           | 放松统计         |
| TYPE_BLOOD_PRESSURE        | 血压详情         |
| TYPE_BLOOD_PRESSURE_COUNT  | 血压统计         |
| TYPE_BODY_WEIGHT           | 体重             |
| TYPE_SPORT_METADATA        | 运动记录概要数据 |
| TYPE_GYM_STRENGTH_TRAINING | 健身力量训练     |
| TYPE_TRAINING_ACTION       | 训练动作         |

## 1. 用户授权

健康app数据共享前原则上需获得用户授权，同时健康平台也提供取消授权的接口，方便用户管理自己的数据。

### 1.1 用户授权

健康app提供用户授权页面，三方应用跳转到该页面请求用户授权。授权结果写入数据平台。

1）在后台配置时不配置三方应用的host，即三方应用host一栏配置为默认的地址：[https://sport.health.heytapmobi.com/open/callback ](https://sport.health.heytapmobi.com/open/callback)时，APP请求授权接口：

```java
HeytapHealthApi.getInstance().authorityApi().request(this, new HResponse<AuthResult>() {
   @Override
   public void onSuccess(AuthResult authResult) {

    }

    @Override
    public void onFailure(int i) {
         
    }
});
```

2）在后台配置时配置三方应用的host，即三方应用host一栏配置为三方应用给的地址：如： https://xxxx 时， APP请求授权接口：

```java
HeytapHealthApi.getInstance().authorityApi().request(this, https://xxxx, new HResponse<AuthResult>() {
   @Override
   public void onSuccess(AuthResult authResult) {

    }

    @Override
    public void onFailure(int i) {
         
    }
});
```

### 1.2 校验授权

健康APP提供校验授权接口，可通过此接口查看已授权权限范围，白名单用户显示已通过白名单设置的权限范围，权限类型可见1.4。使用示例：

```java
HeytapHealthApi.getInstance()
    .authorityApi()
    .valid(new HResponse<List<String>>() {
        @Override
        public void onSuccess(List<String> scopeList) {
            HLog.i(TAG, "Auth scope is " + scopeList);
        }

       @Override
       public void onFailure(int errorCode) {
            HLog.e(TAG, "Auth valid failed! Error code: " + errorCode);
       }
  });
```

### 1.3 取消授权

健康APP提供取消授权接口，可取消共享数据授权。使用示例：

```java
HeytapHealthApi.getInstance()
    .authorityApi()
    .revoke(new HResponse<List<Object>>() {
        @Override
        public void onSuccess(List<Object> objectList) {
            HLog.i(TAG, "revoke access successfully");
        }

       @Override
       public void onFailure(int errorCode) {
            HLog.e(TAG, "revoke access failed! Error code: " + errorCode);
       }
  });
```

### 1.4 权限类型

| 权限                      | 描述                 | 是否可用 |
| ------------------------- | -------------------- | -------- |
| READ_PRESSURE             | 读取压力数据         | 是       |
| WRITE_PRESSURE            | 写入压力数据         | 否       |
| READ_HEART_RATE           | 读取心率数据         | 是       |
| WRITE_HEART_RATE          | 写入心率数据         | 否       |
| READ_DAILY_ACTIVITY       | 读取日常活动数据     | 是       |
| WRITE_DAILY_ACTIVITY      | 写入日常活动数据     | 否       |
| READ_PROFILE              | 读取个人资料数据     | 是       |
| WRITE_PROFILE             | 写入个人资料数据     | 否       |
| READ_DEVICE_DATA          | 读取设备数据         | 否       |
| WRITE_DEVICE_DATA         | 写入设备数据         | 否       |
| READ_SLEEP_DATA           | 读取睡眠数据         | 是       |
| WRITE_SLEEP_DATA          | 写入睡眠数据         | 否       |
| READ_BLOOD_OXYGEN_DATA    | 读取血氧数据         | 是       |
| WRITE_BLOOD_OXYGEN_DATA   | 写入血氧数据         | 否       |
| READ_LOCATION_DATA        | 读取位置数据         | 否       |
| WRITE_LOCATION_DATA       | 写入位置数据         | 否       |
| READ_AUDITION_DATA        | 读取听力数据         | 是       |
| WRITE_AUDITION_DATA       | 写入听力数据         | 否       |
| READ_RELAX_DATA           | 读取放松数据         | 是       |
| WRITE_RELAX_DATA          | 写入放松数据         | 否       |
| READ_BLOOD_PRESSURE_DATA  | 读取血压数据         | 是       |
| WRITE_BLOOD_PRESSURE_DATA | 写入血压数据         | 否       |
| READ_BODY_WEIGHT_DATA     | 读取体重数据         | 是       |
| WRITE_BODY_WEIGHT_DATA    | 写入体重数据         | 否       |
| READ_SPORT_METADATA_DATA  | 读取运动记录概要数据 | 是       |
| WRITE_SPORT_METADATA_DATA | 写入运动记录数据     | 是       |

 

## 2.个人信息

**数据描述**

类名：com.heytap.databaseengine.apiv3.data.DataPoint

字段：

| DataType | 数据类型 | Object | DataType.TYPE_USER_INFO |
| -------- | -------- | ------ | ----------------------- |
| values   | 开放id   | string | Element.ELEMENT_OPENID  |

**获取数据**

```java
//获取个人信息
HeytapHealthApi.getInstance().userInfoApi().readInfo(new HResponse<List<DataSet>>() {
    @Override
    public void onSuccess(List<DataSet> dataSets) {
        for (DataSet dataSet : dataSets) {
             showDataSet(dataSet);
        }
   }

   @Override
    public void onFailure(int i) {
         
    }
});
```

 

## 3. 设备信息

```java
HeytapHealthApi.getInstance()
    .deviceApi().deviceInfoApi()
    .queryBoundDevice(new HResponse<List<UserDeviceInfoProxy>>() {
        @Override
        public void onSuccess(List<UserDeviceInfoProxy> userDeviceInfoList) {}

       @Override
        public void onFailure(int i) {}
})
```

返回列表数据List<UserDeviceInfoProxy>，UserDeviceInfoProxy内容如下：

| 属性            | 描述                                                         |
| --------------- | ------------------------------------------------------------ |
| devicename      | 设备名称                                                     |
| deviceType      | 设备类型，1：手表，2:手环，3：RX手表，100:体脂称             |
| subDeviceType   | 设备子类型, 1：ECG版本                                       |
| model           | 设备型号                                                     |
| manufacturer    | 厂商                                                         |
| connectionState | 连接状态：100：设备未连接101：设备连接中102：设备已连接，大核模式/二代表性能模式103：设备已断开104：设备已连接，小核模式105：设备已连接，大核模式/二代表均衡模式 |

 

## 4. 健康单元

构建SportHealthApi接口参数时需传入运动健康数据类型，具体类型见本文开头的表格，每次查询数据最大范围为**30**天。

### 4.1 压力

**详情数据**

类名：com.heytap.databaseengine.apiv3.data.DataPoint

压力详情设置时间范围时，会将时间戳精确至ms，区间为**完全闭区间**

字段：

| DataType       | 数据类型   | Object                                 | DataType.TYPE_PRESSURE              |
| -------------- | ---------- | -------------------------------------- | ----------------------------------- |
| startTimeStamp | 开始时间戳 | long                                   | 数据产生时间戳；                    |
| values         | 压力值     | int                                    | Element.ELEMENT_PRESSURE，范围0-100 |
| 类型           | int        | Element.ELEMENT_TYPE（0-自动，1-手动） |                                     |

 

**获取每分钟详情**

```java
//获取过去29天压力详情数据
private void pressure() {
    long time = System.currentTimeMillis();
    DataReadRequest readRequest = new DataReadRequest.Builder()
            .read(DataType.TYPE_PRESSURE)
            .setTimeRange(time - 29 * 24 * 60 * 60 * 1000L, time)
            .build();
    request(readRequest);
}

private void request(DataReadRequest readRequest) {
    HeytapHealthApi.getInstance()
    .dataApi()
    .read(readRequest, new HResponse<List<DataSet>>() {
        @Override
        public void onSuccess(List<DataSet> dataSets) {
             for (DataSet dataSet : dataSets) {
                 showDataSet(dataSet);
             }
         }

       @Override
        public void onFailure(int i) {
            Log.e(TAG, "i: " + i);
        }
    });
}
```

 

**统计数据**

类名：com.heytap.databaseengine.apiv3.data.DataPoint

压力统计设置时间范围时，会将时间戳精确至对应所在日期，区间为**完全闭区间。**

字段：

| dataType     | 数据类型     | Object                    | DataType.TYPE_PRESSURE   |
| ------------ | ------------ | ------------------------- | ------------------------ |
| timeStamp    | 日期         | long                      | 数据产生日期(20220501)； |
| values       | 当日最大压力 | float                     | Element.ELEMENT_MAX；    |
| 当日最小压力 | float        | Element.ELEMENT_MIN；     |                          |
| 当日平均压力 | float        | Element.ELEMENT_AVERAGE； |                          |

**获取每天统计数据**

```java
//获取过去29天压力统计数据
private void pressureCount() {
    long time = System.currentTimeMillis();
    DataReadRequest readRequest = new DataReadRequest.Builder()
            .read(DataType.TYPE_PRESSURE_COUNT)
            .setTimeRange(time - 29 * 24 * 60 * 60 * 1000L, time)
            .build();
    request(readRequest);
}

private void request(DataReadRequest readRequest) {
    HeytapHealthApi.getInstance()
    .dataApi()
    .read(readRequest, new HResponse<List<DataSet>>() {
        @Override
        public void onSuccess(List<DataSet> dataSets) {
            for (DataSet dataSet : dataSets) {
                showDataSet(dataSet);
            }
        }

        @Override
        public void onFailure(int i) {
            Log.e(TAG, "i: " + i);
        }
     });
}
```

 

### 4.2 心率

**说明**

心脏收缩跳动的频率和每分钟跳动的次数。

**详情数据**

类名：com.heytap.databaseengine.apiv3.data.DataPoint

心率类详情模式设置时间范围时，会将时间戳精确至ms，区间为**完全闭区间**

字段：

| DataType       | 数据类型   | Object | DataType.TYPE_HEART_RATE                        |
| -------------- | ---------- | ------ | ----------------------------------------------- |
| startTimeStamp | 开始时间戳 | long   | 数据产生时间戳；                                |
| values         | 心率值     | int    | Element.ELEMENT_HEART_RATE，范围40-220，单位BPM |

**获取每分钟详情**

```java
//获取过去29天心率详情数据
private void heartRate() {
    long time = System.currentTimeMillis();
    DataReadRequest readRequest = new DataReadRequest.Builder()
            .read(DataType.TYPE_HEART_RATE)
            .setTimeRange(time - 29 * 24 * 60 * 60 * 1000L, time)
            .build();
    request(readRequest);
}

private void request(DataReadRequest readRequest) {
    HeytapHealthApi.getInstance()
    .dataApi()
    .read(readRequest, new HResponse<List<DataSet>>() {
        @Override
        public void onSuccess(List<DataSet> dataSets) {
            for (DataSet dataSet : dataSets) {
                showDataSet(dataSet);
           }
        }

        @Override
        public void onFailure(int i) {
            Log.e(TAG, "i: " + i);
        }
    });
}
```

 

**统计数据**

类名：com.heytap.databaseengine.apiv3.data.DataPoint

心率类统计模式设置时间范围时，会将时间戳精确至对应所在日期，区间为**完全闭区间。**

字段：

| dataType         | 数据类型     | Object                          | DataType.TYPE_HEART_RATE_COUNT |
| ---------------- | ------------ | ------------------------------- | ------------------------------ |
| timeStamp        | 日期         | long                            | 数据产生日期(20220501)；       |
| values           | 当日最大心率 | float                           | Element.ELEMENT_MAX；          |
| 当日最小心率     | float        | Element.ELEMENT_MIN；           |                                |
| 当日平均心率     | float        | Element.ELEMENT_AVERAGE；       |                                |
| 当日静息心率     | int          | Element.ELEMENT_REST_HR；       |                                |
| 当日睡眠基准心率 | int          | Element.ELEMENT_SLEEP_BASE_HR； |                                |
| 当日步行平均心率 | int          | Element.ELEMENT_WALK_AVG_HR；   |                                |

**获取每天统计数据**

```java
//获取过去29天心率统计数据
private void heartRate() {
    long time = System.currentTimeMillis();
    DataReadRequest readRequest = new DataReadRequest.Builder()
            .read(DataType.TYPE_HEART_RATE_COUNT)
            .setTimeRange(time - 29 * 24 * 60 * 60 * 1000L, time)
            .build();
    request(readRequest);
}

private void request(DataReadRequest readRequest) {
    HeytapHealthApi.getInstance()
    .dataApi()
    .read(readRequest, new HResponse<List<DataSet>>() {
        @Override
        public void onSuccess(List<DataSet> dataSets) {
            for (DataSet dataSet : dataSets) {
                showDataSet(dataSet);
            }
        }

        @Override
            public void onFailure(int i) {
                 Log.e(TAG, "i: " + i);
            }
        });
}
```

 

### 4.3 心电记录

**详情数据**

类名：com.heytap.databaseengine.apiv3.data.DataPoint

心电记录设置时间范围时，会将时间戳精确至ms，区间为**完全闭区间**

字段：

| DataType       | 数据类型   | Object                                                       | DataType.TYPE_PRESSURE                 |
| -------------- | ---------- | ------------------------------------------------------------ | -------------------------------------- |
| startTimeStamp | 开始时间戳 | long                                                         | 数据开始时间戳；                       |
| timeStamp      | 结束时间戳 | long                                                         | 数据结束时间戳；                       |
| values         | 平均心率   | int                                                          | Element.ELEMENT_HEART_RATE，范围40-220 |
| 专家解读       | string     | ELEMENT_ECG_EXPERT_INTERPRETATION，json解析格式为： { "auditDate": "1629703021000", "core": "您本次心电监测未见明显异常", "doctorAcademicTitle": "主治医师", "doctorHospital": "国家远程医疗与互联网医学中心", "doctorName": "王肖艳2", "hospitalGrade": "国家远程医", "imageUrl": "3e8529f7.png", "interpretationResults": "窦性心律", "pdfUrlAfter": "https://api-test.995120.cn/ecgdatatest/pdf/2021-08-23/4031720210823161320.pdf", "suggestions": "如无症状，不需处理。如有不适，及时随诊。" } |                                        |

**获取记录详情**

```java
//获取一天心电记录数据
private void ecgRecord() {
    long time = System.currentTimeMillis();
    DataReadRequest readRequest = new DataReadRequest.Builder()
            .read(DataType.TYPE_ECG)
            .setTimeRange(time - 24 * 60 * 60 * 1000L, time)
            .build();
    request(readRequest);
}

private void request(DataReadRequest readRequest) {
    HeytapHealthApi.getInstance()
    .dataApi()
    .read(readRequest, new HResponse<List<DataSet>>() {
        @Override
        public void onSuccess(List<DataSet> dataSets) {
            for (DataSet dataSet : dataSets) {
                showDataSet(dataSet);
            }
        }

        @Override
         public void onFailure(int i) {
             Log.e(TAG, "i: " + i);
        }
    });
}
```

 

### 4.4 睡眠

**详情数据**

类名：com.heytap.databaseengine.apiv3.data.DataPoint

睡眠详情设置时间范围时，会将时间戳精确至ms，区间为**完全闭区间**

字段：

| DataType       | 数据类型   | Object                                                 | DataType.TYPE_SLEEP                                          |
| -------------- | ---------- | ------------------------------------------------------ | ------------------------------------------------------------ |
| startTimeStamp | 开始时间戳 | long                                                   | 数据开始时间戳；                                             |
| timeStamp      | 结束时间戳 | long                                                   | 数据结束时间戳；                                             |
| values         | 睡眠状态   | int                                                    | Element.ELEMENT_SLEEP（1-入睡，2-深睡，3-快速眼动，4-浅睡，5-短暂清醒，6-出睡） |
| 设备类型       | Integer    | Element.ELEMENT_DEVICE_TYPE（0-手机，其它-手表或手环） |                                                              |

**获取每分钟详情**

```java
//获取过去29天睡眠详情数据
private void sleep() {
    long time = System.currentTimeMillis();
    DataReadRequest readRequest = new DataReadRequest.Builder()
            .read(DataType.TYPE_SLEEP)
            .setTimeRange(time - 29 * 24 * 60 * 60 * 1000L, time)
            .build();
    request(readRequest);
}

private void request(DataReadRequest readRequest) {
    HeytapHealthApi.getInstance()
    .dataApi()
    .read(readRequest, new HResponse<List<DataSet>>() {
        @Override
        public void onSuccess(List<DataSet> dataSets) {
            for (DataSet dataSet : dataSets) {
                showDataSet(dataSet);
            }
        }

        @Override
         public void onFailure(int i) {
              Log.e(TAG, "i: " + i);
         }
     });
}
```

 

**统计数据**

类名：com.heytap.databaseengine.apiv3.data.DataPoint

睡眠统计设置时间范围时，会将时间戳精确至对应所在日期，区间为**完全闭区间。**

字段：

| dataType                           | 数据类型    | Object                                               | DataType.TYPE_SLEEP_COUNT         |
| ---------------------------------- | ----------- | ---------------------------------------------------- | --------------------------------- |
| timeStamp                          | 日期        | long                                                 | 数据产生日期(20220501)；          |
| values                             | 睡眠总时长  | float                                                | Element.ELEMENT_TOTAL，单位分钟； |
| 睡眠总深睡时长                     | int         | Element.ELEMENT_TOTAL_DEEP_SLEEP_TIME，单位分钟；    |                                   |
| 睡眠总浅睡时长                     | int         | Element.ELEMENT_TOTAL_LIGHTLY_SLEEP_TIME，单位分钟； |                                   |
| 睡眠总清醒时长                     | int         | Element.ELEMENT_TOTAL_WAKE_UP_TIME，单位分钟；       |                                   |
| 睡眠总快速眼动时长                 | int         | Element.ELEMENT_TOTAL_REM_TIME，单位分钟；           |                                   |
| 最早入睡                           | int         | Element.ELEMENT_FALL_ASLEEP，单位分钟；              |                                   |
| 最晚出睡                           | int         | Element.ELEMENT_SLEEP_OUT，单位分钟；                |                                   |
| 睡眠评分                           | Integer     | Element.ELEMENT_SLEEP_SCORE；                        |                                   |
| 睡眠片段数据（包含每段的统计数据） | Json String | Element.ELEMENT_SLEEP_DAY_FRAGS                      |                                   |

睡眠片段数据示例：

[{"date":20230513,"deviceUniqueId":"","sleepInTime":1683909240000,"sleepOutTime":1683937800000,"sleepUnitDataList":[{"deviceUniqueId":"","endTimestamp":1683910560000,"sleepType":4,"ssoid":"xxxxxxx","stageSleepEnd":false,"startTimestamp":1683909240000},{"deviceUniqueId":"","endTimestamp":1683911280000,"sleepType":2,"ssoid":"xxxxxxx","stageSleepEnd":false,"startTimestamp":1683910560000},{"deviceUniqueId":"","endTimestamp":1683911460000,"sleepType":4,"ssoid":"xxxxxxx","stageSleepEnd":false,"startTimestamp":1683911280000},{"deviceUniqueId":"","endTimestamp":1683911640000,"sleepType":2,"ssoid":"xxxxxxx","stageSleepEnd":false,"startTimestamp":1683911460000},{"deviceUniqueId":"","endTimestamp":1683912600000,"sleepType":4,"ssoid":"xxxxxxx","stageSleepEnd":false,"startTimestamp":1683911640000},{"deviceUniqueId":"","endTimestamp":1683913260000,"sleepType":2,"ssoid":"xxxxxxx","stageSleepEnd":false,"startTimestamp":1683912600000},{"deviceUniqueId":"","endTimestamp":1683913620000,"sleepType":4,"ssoid":"xxxxxxx","stageSleepEnd":false,"startTimestamp":1683913260000},{"deviceUniqueId":"","endTimestamp":1683913980000,"sleepType":3,"ssoid":"xxxxxxx","stageSleepEnd":false,"startTimestamp":1683913620000},{"deviceUniqueId":"","endTimestamp":1683914280000,"sleepType":4,"ssoid":"xxxxxxx","stageSleepEnd":false,"startTimestamp":1683913980000},{"deviceUniqueId":"","endTimestamp":1683915300000,"sleepType":3,"ssoid":"xxxxxxx","stageSleepEnd":false,"startTimestamp":1683914280000},{"deviceUniqueId":"","endTimestamp":1683917520000,"sleepType":4,"ssoid":"xxxxxxx","stageSleepEnd":false,"startTimestamp":1683915300000},{"deviceUniqueId":"","endTimestamp":1683918000000,"sleepType":3,"ssoid":"xxxxxxx","stageSleepEnd":false,"startTimestamp":1683917520000},{"deviceUniqueId":"","endTimestamp":1683918540000,"sleepType":4,"ssoid":"xxxxxxx","stageSleepEnd":false,"startTimestamp":1683918000000},{"deviceUniqueId":"","endTimestamp":1683918900000,"sleepType":3,"ssoid":"xxxxxxx","stageSleepEnd":false,"startTimestamp":1683918540000},{"deviceUniqueId":"","endTimestamp":1683919260000,"sleepType":4,"ssoid":"xxxxxxx","stageSleepEnd":false,"startTimestamp":1683918900000},{"deviceUniqueId":"","endTimestamp":1683919680000,"sleepType":2,"ssoid":"xxxxxxx","stageSleepEnd":false,"startTimestamp":1683919260000},{"deviceUniqueId":"","endTimestamp":1683920280000,"sleepType":4,"ssoid":"xxxxxxx","stageSleepEnd":false,"startTimestamp":1683919680000},{"deviceUniqueId":"","endTimestamp":1683920460000,"sleepType":3,"ssoid":"xxxxxxx","stageSleepEnd":false,"startTimestamp":1683920280000},{"deviceUniqueId":"","endTimestamp":1683920700000,"sleepType":4,"ssoid":"xxxxxxx","stageSleepEnd":false,"startTimestamp":1683920460000},{"deviceUniqueId":"","endTimestamp":1683921600000,"sleepType":3,"ssoid":"xxxxxxx","stageSleepEnd":false,"startTimestamp":1683920700000},{"deviceUniqueId":"","endTimestamp":1683923100000,"sleepType":4,"ssoid":"xxxxxxx","stageSleepEnd":false,"startTimestamp":1683921600000},{"deviceUniqueId":"","endTimestamp":1683924180000,"sleepType":3,"ssoid":"xxxxxxx","stageSleepEnd":false,"startTimestamp":1683923100000},{"deviceUniqueId":"","endTimestamp":1683924660000,"sleepType":4,"ssoid":"xxxxxxx","stageSleepEnd":false,"startTimestamp":1683924180000},{"deviceUniqueId":"","endTimestamp":1683924960000,"sleepType":3,"ssoid":"xxxxxxx","stageSleepEnd":false,"startTimestamp":1683924660000},{"deviceUniqueId":"","endTimestamp":1683926460000,"sleepType":4,"ssoid":"xxxxxxx","stageSleepEnd":false,"startTimestamp":1683924960000},{"deviceUniqueId":"","endTimestamp":1683927660000,"sleepType":2,"ssoid":"xxxxxxx","stageSleepEnd":false,"startTimestamp":1683926460000},{"deviceUniqueId":"","endTimestamp":1683927900000,"sleepType":4,"ssoid":"xxxxxxx","stageSleepEnd":false,"startTimestamp":1683927660000},{"deviceUniqueId":"","endTimestamp":1683928680000,"sleepType":2,"ssoid":"xxxxxxx","stageSleepEnd":false,"startTimestamp":1683927900000},{"deviceUniqueId":"","endTimestamp":1683928860000,"sleepType":0,"ssoid":"xxxxxxx","stageSleepEnd":false,"startTimestamp":1683928680000},{"deviceUniqueId":"","endTimestamp":1683929880000,"sleepType":4,"ssoid":"xxxxxxx","stageSleepEnd":false,"startTimestamp":1683928860000},{"deviceUniqueId":"","endTimestamp":1683929940000,"sleepType":0,"ssoid":"xxxxxxx","stageSleepEnd":false,"startTimestamp":1683929880000},{"deviceUniqueId":"","endTimestamp":1683930780000,"sleepType":4,"ssoid":"xxxxxxx","stageSleepEnd":false,"startTimestamp":1683929940000},{"deviceUniqueId":"","endTimestamp":1683931020000,"sleepType":3,"ssoid":"xxxxxxx","stageSleepEnd":false,"startTimestamp":1683930780000},{"deviceUniqueId":"","endTimestamp":1683931740000,"sleepType":4,"ssoid":"xxxxxxx","stageSleepEnd":false,"startTimestamp":1683931020000},{"deviceUniqueId":"","endTimestamp":1683934200000,"sleepType":2,"ssoid":"xxxxxxx","stageSleepEnd":false,"startTimestamp":1683931740000},{"deviceUniqueId":"","endTimestamp":1683935040000,"sleepType":4,"ssoid":"xxxxxxx","stageSleepEnd":false,"startTimestamp":1683934200000},{"deviceUniqueId":"","endTimestamp":1683936540000,"sleepType":3,"ssoid":"xxxxxxx","stageSleepEnd":false,"startTimestamp":1683935040000},{"deviceUniqueId":"","endTimestamp":1683936960000,"sleepType":4,"ssoid":"xxxxxxx","stageSleepEnd":false,"startTimestamp":1683936540000},{"deviceUniqueId":"","endTimestamp":1683937620000,"sleepType":3,"ssoid":"xxxxxxx","stageSleepEnd":false,"startTimestamp":1683936960000},{"deviceUniqueId":"","endTimestamp":1683937800000,"sleepType":4,"ssoid":"xxxxxxx","stageSleepEnd":true,"startTimestamp":1683937620000}],"source":1,"ssoid":"xxxxxxx","totalDeepSleepTime":107,"totalLightlySleepTime":247,"totalREMSleepTime":118,"totalSleepTime":472,"totalWakeTime":4,"wakeCount":2}]

**获取每天统计数据**

```java
//获取过去29天睡眠统计数据
private void sleepCount() {
    long time = System.currentTimeMillis();
    DataReadRequest readRequest = new DataReadRequest.Builder()
            .read(DataType.TYPE_SLEEP_COUNT)
            .setTimeRange(time - 29 * 24 * 60 * 60 * 1000L, time)
            .build();
    request(readRequest);
}

private void request(DataReadRequest readRequest) {
    HeytapHealthApi.getInstance()
    .dataApi()
    .read(readRequest, new HResponse<List<DataSet>>() {
        @Override
        public void onSuccess(List<DataSet> dataSets) {
            for (DataSet dataSet : dataSets) {
                showDataSet(dataSet);
            }
        }

        @Override
         public void onFailure(int i) {
             Log.e(TAG, "i: " + i);
         }
    });
}
```

 

### 4.5 血氧

**详情数据**

类名：com.heytap.databaseengine.apiv3.data.DataPoint

血氧详情设置时间范围时，会将时间戳精确至ms，区间为**完全闭区间**

字段：

| DataType       | 数据类型   | Object                                 | DataType.TYPE_BLOOD_OXYGEN              |
| -------------- | ---------- | -------------------------------------- | --------------------------------------- |
| startTimeStamp | 开始时间戳 | long                                   | 数据产生时间戳；                        |
| values         | 血氧值     | int                                    | Element.ELEMENT_BLOOD_OXYGEN，范围0-100 |
| 血氧类型       | int        | Element.ELEMENT_TYPE（0-日常，1-睡眠） |                                         |

**获取每分钟详情**

```java
//获取过去29天血氧详情数据
private void bloodOxygen() {
    long time = System.currentTimeMillis();
    DataReadRequest readRequest = new DataReadRequest.Builder()
            .read(DataType.TYPE_BLOOD_OXYGEN)
            .setTimeRange(time - 29 * 24 * 60 * 60 * 1000L, time)
            .build();
    request(readRequest);
}

private void request(DataReadRequest readRequest) {
    HeytapHealthApi.getInstance()
    .dataApi()
    .read(readRequest, new HResponse<List<DataSet>>() {
        @Override
        public void onSuccess(List<DataSet> dataSets) {
            for (DataSet dataSet : dataSets) {
                showDataSet(dataSet);
            }
        }

        @Override
        public void onFailure(int i) {
             Log.e(TAG, "i: " + i);
         }
    });
}
```

 

**统计数据**

类名：com.heytap.databaseengine.apiv3.data.DataPoint

血氧统计设置时间范围时，会将时间戳精确至对应所在日期，区间为**完全闭区间。**

字段：

| dataType     | 数据类型     | Object                    | DataType.TYPE_BLOOD_OXYGEN_COUNT |
| ------------ | ------------ | ------------------------- | -------------------------------- |
| timeStamp    | 日期         | long                      | 数据产生日期(20220501)；         |
| values       | 当日最大血氧 | float                     | Element.ELEMENT_MAX；            |
| 当日最小血氧 | float        | Element.ELEMENT_MIN；     |                                  |
| 当日平均血氧 | float        | Element.ELEMENT_AVERAGE； |                                  |

**获取每天统计数据**

```java
//获取过去29天血氧统计数据
private void bloodOxygenCount() {
    long time = System.currentTimeMillis();
    DataReadRequest readRequest = new DataReadRequest.Builder()
            .read(DataType.TYPE_BLOOD_OXYGEN_COUNT)
            .setTimeRange(time - 29 * 24 * 60 * 60 * 1000L, time)
            .build();
    request(readRequest);
}

private void request(DataReadRequest readRequest) {
    HeytapHealthApi.getInstance()
    .dataApi()
    .read(readRequest, new HResponse<List<DataSet>>() {
        @Override
        public void onSuccess(List<DataSet> dataSets) {
            for (DataSet dataSet : dataSets) {
                showDataSet(dataSet);
            }
        }

        @Override
         public void onFailure(int i) {
             Log.e(TAG, "i: " + i);
         }
    });
}
```

 

### 4.6 听力

**详情数据**

类名：com.heytap.databaseengine.apiv3.data.DataPoint 

压力详情设置时间范围时，会将时间戳精确至ms，区间为**完全闭区间**

字段：

| DataType       | 数据类型   | Object                               | DataType.TYPE_HEARING_HEALTH   |
| -------------- | ---------- | ------------------------------------ | ------------------------------ |
| startTimeStamp | 开始时间戳 | long                                 | 数据产生时间戳；               |
| values         | 听力值     | float                                | Element.ELEMENT_HEARING_HEALTH |
| 持续时长       | long       | Element.ELEMENT_DURATION（单位：秒） |                                |

**获取每分钟详情**

```java
//获取过去29天听力详情数据
private void hearingHealth() {
    long time = System.currentTimeMillis();
    DataReadRequest readRequest = new DataReadRequest.Builder()
            .read(DataType.TYPE_HEARING_HEALTH)
            .setTimeRange(time - 29 * 24 * 60 * 60 * 1000L, time)
            .build();
    request(readRequest);
}
 
private void request(DataReadRequest readRequest) {
    HeytapHealthApi.getInstance()
            .dataApi()
            .read(readRequest, new HResponse<List<DataSet>>() {
                @Override
                public void onSuccess(List<DataSet> dataSets) {
                    for (DataSet dataSet : dataSets) {
                        showDataSet(dataSet);
                    }
                }
 
                @Override
                public void onFailure(int i) {
                    Log.e(TAG, "i: " + i);
                }
            });
}
```

**统计数据**

类名：com.heytap.databaseengine.apiv3.data.DataPoint

听力统计设置时间范围时，会将时间戳精确至对应所在日期，区间为**完全闭区间。**

字段：

| dataType     | 数据类型     | Object                                | DataType.TYPE_HEARING_HEALTH_COUNT |
| ------------ | ------------ | ------------------------------------- | ---------------------------------- |
| timeStamp    | 日期         | long                                  | 数据产生日期(20220501)；           |
| values       | 当日最大听力 | float                                 | Element.ELEMENT_MAX；              |
| 当日最小听力 | float        | Element.ELEMENT_MIN；                 |                                    |
| 当日平均听力 | float        | Element.ELEMENT_AVERAGE；             |                                    |
| 当日听力时长 | long         | Element.ELEMENT_DURATION（单位：秒）; |                                    |

#### **获取每天统计数据**

```java
//获取过去29天听力统计数据
private void hearingHealthCount() {
    long time = System.currentTimeMillis();
    DataReadRequest readRequest = new DataReadRequest.Builder()
            .read(DataType.TYPE_HEARING_HEALTH_COUNT)
            .setTimeRange(time - 29 * 24 * 60 * 60 * 1000L, time)
            .build();
    request(readRequest);
}
 
private void request(DataReadRequest readRequest) {
    HeytapHealthApi.getInstance()
            .dataApi()
            .read(readRequest, new HResponse<List<DataSet>>() {
                @Override
                public void onSuccess(List<DataSet> dataSets) {
                    for (DataSet dataSet : dataSets) {
                        showDataSet(dataSet);
                    }
                }
 
                @Override
                public void onFailure(int i) {
                    Log.e(TAG, "i: " + i);
                }
            });
}
```

##

### 4.7 放松

**详情数据**

类名：com.heytap.databaseengine.apiv3.data.DataPoint 

放松详情设置时间范围时，会将时间戳精确至ms，区间为**完全闭区间**

字段：

| DataType       | 数据类型   | Object                                                       | DataType.TYPE_RELAX                                          |
| -------------- | ---------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| startTimeStamp | 开始时间戳 | long                                                         | 数据产生时间戳；                                             |
| values         | 类型       | int                                                          | Element.ELEMENT_TYPE; （全部类型：-2,呼吸：1,冥想: 2,游戏：3) |
| 子类型         | int        | Element.ELEMENT_SUB_TYPE（呼吸：自然呼吸：1，蜂鸣式呼吸：2， 助眠式呼吸：3；冥想：情绪觉知：1，躯体扫描：2，工作小憩：3，正念行走：4，助眠冥想：5；游戏：捏泡泡：1，打地鼠：2。） |                                                              |
| 压力值         | int        | Element.ELEMENT_PRESSURE;                                    |                                                              |
| 持续时长       | long       | Element.ELEMENT_DURATION（单位：秒）;                        |                                                              |

#### **获取每分钟详情**

```java
//获取过去29天放松详情数据
private void relax() {
    long time = System.currentTimeMillis();
    DataReadRequest readRequest = new DataReadRequest.Builder()
            .read(DataType.TYPE_RELAX)
            .setTimeRange(time - 29 * 24 * 60 * 60 * 1000L, time)
            .build();
    request(readRequest);
}
 
private void request(DataReadRequest readRequest) {
    HeytapHealthApi.getInstance()
            .dataApi()
            .read(readRequest, new HResponse<List<DataSet>>() {
                @Override
                public void onSuccess(List<DataSet> dataSets) {
                    for (DataSet dataSet : dataSets) {
                        showDataSet(dataSet);
                    }
                }
 
                @Override
                public void onFailure(int i) {
                    Log.e(TAG, "i: " + i);
                }
            });
}
```

**统计数据**

类名：com.heytap.databaseengine.apiv3.data.DataPoint

放松统计设置时间范围时，会将时间戳精确至对应所在日期，区间为**完全闭区间。**

字段：

| DataType  | 数据类型     | Object | DataType.TYPE_RELAX_COUNT                                    |
| --------- | ------------ | ------ | ------------------------------------------------------------ |
| timeStamp | 日期         | long   | 数据产生日期(20220501)；                                     |
| values    | 当日放松时长 | long   | Element.ELEMENT_DURATION（返回全部放松类型的时长，单位：秒）； |

**获取每天统计数据**

```java
//获取过去29天放松统计数据
private void relaxCount() {
    long time = System.currentTimeMillis();
    DataReadRequest readRequest = new DataReadRequest.Builder()
            .read(DataType.TYPE_RELAX_COUNT)
            .setTimeRange(time - 29 * 24 * 60 * 60 * 1000L, time)
            .build();
    request(readRequest);
}
 
private void request(DataReadRequest readRequest) {
    HeytapHealthApi.getInstance()
            .dataApi()
            .read(readRequest, new HResponse<List<DataSet>>() {
                @Override
                public void onSuccess(List<DataSet> dataSets) {
                    for (DataSet dataSet : dataSets) {
                        showDataSet(dataSet);
                    }
                }
 
                @Override
                public void onFailure(int i) {
                    Log.e(TAG, "i: " + i);
                }
            });
}
```

 

## 5.运动单元

构建SportHealthApi接口参数时需传入运动健康数据类型，具体类型见本文开头的表格，每次查询数据最大范围为**30**天。

### 5.1 每日活动

包含步数/消耗/锻炼时长/活动次数四类数据

**详情数据**

类名：com.heytap.databaseengine.apiv3.data.DataPoint

每日活动类详情模式设置时间范围时，会将时间戳精确至ms，区间为**完全闭区间**

字段：

| dataType       | 数据类型   | Object                   | DataType.TYPE_DAILY_ACTIVITY |
| -------------- | ---------- | ------------------------ | ---------------------------- |
| startTimeStamp | 开始时间戳 | long                     | 数据开始产生时间戳；         |
| timeStamp      | 结束时间戳 | long                     | 数据截止时间戳；             |
| values         | 步数       | int                      | Element.ELEMENT_STEP         |
| 距离           | int        | Element.ELEMENT_DISTANCE |                              |
| 消耗           | int        | Element.ELEMENT_CALORIE  |                              |

**获取数据**

```java
//获取当天每日活动详情数据
private void dailyActivity() {
    long time = System.currentTimeMillis();
    DataReadRequest readRequest = new DataReadRequest.Builder()
            .read(DataType.TYPE_DAILY_ACTIVITY)
            .setTimeRange(time - 1, time)
            .build();
    request(readRequest);
}

private void request(DataReadRequest readRequest) {
    HeytapHealthApi.getInstance()
    .dataApi()
    .read(readRequest, new HResponse<List<DataSet>>() {
        @Override
        public void onSuccess(List<DataSet> dataSets) {
            for (DataSet dataSet : dataSets) {
                showDataSet(dataSet);
            }
        }

        @Override
         public void onFailure(int i) {
             Log.e(TAG, "i: " + i);
         }
    });
}
```

**统计数据**

类名：com.heytap.databaseengine.apiv3.data.DataPoint

每日活动统计类设置时间范围时，会将时间戳精确至对应所在日期，区间为**完全闭区间**

字段：

| dataType       | 数据类型   | Object                                           | DataType.TYPE_DAILY_ACTIVITY_COUNT |
| -------------- | ---------- | ------------------------------------------------ | ---------------------------------- |
| startTimeStamp | 开始时间戳 | long                                             | 数据开始产生时间戳；               |
| timeStamp      | 结束时间戳 | long                                             | 数据截止时间戳；                   |
| values         | 步数       | int                                              | Element.ELEMENT_STEP，一步一计     |
| 步数目标       | int        | Element.ELEMENT_STEP_GOAL，默认8000              |                                    |
| 距离           | int        | Element.ELEMENT_DISTANCE，单位m                  |                                    |
| 消耗           | int        | Element.ELEMENT_CALORIE，单位cal                 |                                    |
| 消耗目标       | int        | Element.ELEMENT_CALORIE_GOAL，默认300000，单位卡 |                                    |
| 锻炼时长       | int        | Element.ELEMENT_WORK_MINUTE，单位min             |                                    |
| 活动次数       | int        | Element.ELEMENT_MOVE_TIME，单位次                |                                    |

**获取数据**

```java
//获取当天每日活动统计数据
private void dailyActivityCount() {
    long time = System.currentTimeMillis();
    DataReadRequest readRequest = new DataReadRequest.Builder()
            .read(DataType.TYPE_DAILY_ACTIVITY_COUNT)
            .setTimeRange(time - 1, time)
            .build();
    request(readRequest);
}

private void request(DataReadRequest readRequest) {
    HeytapHealthApi.getInstance()
    .dataApi()
    .read(readRequest, new HResponse<List<DataSet>>() {
        @Override
        public void onSuccess(List<DataSet> dataSets) {
            for (DataSet dataSet : dataSets) {
                showDataSet(dataSet);
            }
         }

        @Override
        public void onFailure(int i) {
            Log.e(TAG, "i: " + i);
        }
    });
}
```

 

### 5.2 运动记录概要数据

#### **说明**

查询返回运动记录概要数据:

开放的数据字段包括运动类和健身类

①运动类：

| **运动名称**    | **运动类型（SportMode）** | **运动名称** | **运动类型（SportMode）** | **运动名称**     | **运动类型（SportMode）** |
| --------------- | ------------------------- | ------------ | ------------------------- | ---------------- | ------------------------- |
| 室外健走        | 1                         | 室外减脂跑   | 17                        | 跑步课程（室内） | 43                        |
| 室外跑步        | 2                         | 室内减脂跑   | 18                        | 跑步课程（室外） | 44                        |
| 室外骑行        | 3                         | 室内健走     | 19                        | 体能测试         | 127                       |
| 泳池游泳        | 7                         | 跑步机       | 21                        | 跑酷             | 505                       |
| 室内跑          | 10                        | 马拉松       | 22                        | 徒步             | 506                       |
| 室外体能跑      | 13                        | 登山         | 36                        | 遛狗             | 905                       |
| 室内体能跑      | 14                        | 越野         | 37                        | 自定义室外运动   | 1001                      |
| 室外5公里轻松跑 | 15                        | 自动识别跑步 | 40                        | 自定义室内运动   | 1002                      |
| 室内5公里轻松跑 | 16                        | 自动识别健走 | 41                        | 自定义水上运动   | 1003                      |

返回数据为：开始时间（秒）、结束时间（秒）、运动类型、平均心率（count/min)、平均配速（s/km）、最佳配速（s/km）、平均步频（step/min）、最佳步频（step/min）、总消耗（卡）、总距离（米）、总步数、总时长（秒）、设备类型（Watch/Band/WATCH2/BAND2/WATCH3/WATHC3PRO/BANDHSB/等设备型号)。

 

②健身类：除运动类以外的其它运动

返回数据为：开始时间（秒）、结束时间（秒）、运动类型、平均心率（count/min)、课程名称、课程完成次数、训练消耗卡路里（卡）、训练时长（秒）、设备类型（Watch/Band/WATCH2/BAND2/WATCH3/WATHC3PRO/BANDHSB/等设备型号)。

 

### **概要数据**

- 类名：com.heytap.databaseengine.apiv3.data.DataPoint
- 运动记录数据设置时间范围时，会将时间戳精确至ms，区间为**完全闭区间**
- 运动类返回字段：

| dataType              | 数据类型           | Object                             | DataType.TYPE_SPORT_METADATA    |
| --------------------- | ------------------ | ---------------------------------- | ------------------------------- |
| startTimeStamp        | 开始时间戳         | long                               | 数据开始产生时间戳；            |
| values                | 运动开始时间（秒） | Integer                            | Element.ELEMENT_START_TIMESTAMP |
| 运动结束时间（秒）    | Integer            | Element.ELEMENT_END_TIMESTAMP      |                                 |
| 运动类型              | Integer            | Element.ELEMENT_SPORT_MODE         |                                 |
| 平均心率（count/min） | Integer            | Element.ELEMENT_AVG_HEART_RATE     |                                 |
| 平均配速（s/km）      | Integer            | Element.ELEMENT_AVG_PACE           |                                 |
| 最佳配速（s/km）      | Integer            | Element.ELEMENT_BEST_PACE          |                                 |
| 平均步频（step/min）  | Integer            | Element.ELEMENT_AVG_STEP_FREQUENCY |                                 |
| 最佳步频（step/min）  | Integer            | Element.ELEMENT_BEST_STEP_REQUENCY |                                 |
| 总消耗（卡）          | Integer            | Element.ELEMENT_CALORIE            |                                 |
| 总距离（米）          | Integer            | Element.ELEMENT_DISTANCE           |                                 |
| 总步数                | Integer            | Element.ELEMENT_STEP               |                                 |
| 总时长（秒）          | Integer            | Element.ELEMENT_DURATION           |                                 |
| 设备类型              | String             | Element.ELEMENT_DEVICE_CATEGORY    |                                 |

- 健身类返回字段：

| dataType             | 数据类型           | Object                                | DataType.TYPE_SPORT_METADATA    |
| -------------------- | ------------------ | ------------------------------------- | ------------------------------- |
| startTimeStamp       | 开始时间戳         | long                                  | 数据开始产生时间戳；            |
| values               | 运动开始时间（秒） | Integer                               | Element.ELEMENT_STRAT_TIMESTAMP |
| 运动结束时间（秒）   | Integer            | Element.ELEMENT_END_TIMESTAMP         |                                 |
| 运动类型             | Integer            | Element.ELEMENT_SPORT_MODE            |                                 |
| 平均心率（count/min) | Integer            | Element.ELEMENT_AVG_HEART_RATE        |                                 |
| 课程名称             | String             | Element.ELEMENT_COURSE_NAME           |                                 |
| 课程完成次数         | Integer            | Element.ELEMENT_COURSE_COMPLETE_COUNT |                                 |
| 训练消耗卡路里（卡） | Integer            | Element.ELEMENT_CALORIE               |                                 |
| 训练时长（秒）       | Integer            | Element.ELEMENT_DURATION              |                                 |
| 设备类型             | String             | Element.ELEMENT_DEVICE_CATEGORY       |                                 |

###  

### **获取概要数据：**

```java
//获取当天运动记录概要数据
private void sportMetadata() {
	long startTime= LocalDate.now().atStartOfDay().atZone(ZoneId.systemDefault()).toInstant().toEpochMilli();
	long endTime = LocalDate.now().plusDays(1).atStartOfDay().atZone(ZoneId.systemDefault()).toInstant().toEpochMilli() - 1;
	DataReadRequest readRequest = new DataReadRequest.Builder()
			.read(DataType.TYPE_SPORT_METADATA)
			.setTimeRange(startTime, endTime)
			.build();
	request(readRequest);
}

private void request(DataReadRequest readRequest) {
    HeytapHealthApi.getInstance()
    .dataApi()
    .read(readRequest, new HResponse<List<DataSet>>() {
        @Override
        public void onSuccess(List<DataSet> dataSets) {
            for (DataSet dataSet : dataSets) {
                showDataSet(dataSet);
            }
        }

        @Override
        public void onFailure(int i) {
            Log.e(TAG, "i: " + i);
	}
   });
}
```

 

### 5.3 写入健身力量训练运动记录:

- 需要展示的数据：

| 数据                   | 数据名称       | 数据类型                                                     | 单位或说明                                   | 是否必须 |
| ---------------------- | -------------- | ------------------------------------------------------------ | -------------------------------------------- | -------- |
| 训练标题               | 胸·三头·腹肌·2 | String                                                       | 尽量非空，如为空，则显示默认标题“力量训练”   | Must     |
| 基础数据               | 总容量         | int                                                          | 单位：kg                                     | Must     |
| 运动时长               | int            | 单位：s                                                      | Must                                         |          |
| 消耗                   | int            | 单位：cal                                                    | Must                                         |          |
| 最高心率               | int            | 单位：次/分钟                                                | Must                                         |          |
| 平均心率               | int            | 单位：次/分钟                                                | Must                                         |          |
| 运动开始时间           | int/long       | 运动开始的utc时间戳，作为element时单位：s， 作为DataPoint的startTimeStamp字段时单位为ms。 | Must                                         |          |
| 运动结束时间           | int/long       | 运动结束的utc时间戳，作为element时单位：s， 作为DataPoint的timeStamp字段时单位为ms。 | Must                                         |          |
| 运动模式               | int            | SportMode.GYM_STRENGTH_TRAINING                              | Must                                         |          |
| 数据客户端【唯一标识】 | String         | 必须有，能唯一标识的数据客户端                               | Must                                         |          |
| 心率                   | int            | 全程心率数据，用于绘制实时心率图表                           | Option                                       |          |
| 训练计划               | 动作名称       | String                                                       | 由字母，符号，字符串组成，如：V-Bar 绳索下压 | Must     |
| 轮数                   | String         | 如：热, 4, d1                                                | Must                                         |          |
| 配重1                  | int            | 如：12  单位：kg                                             | Option                                       |          |
| 配重2                  | int            | 如：12  单位：kg                                             | Option                                       |          |
| 次数                   | int            | 该组动作运动次数                                             | Option                                       |          |
| 完成状态               | int            | 是否完成：完成时正常显示，未完成时灰色 完成：1 未完成：0 【不传，默认为完成】 | Must                                         |          |

 

### **数据写入**：

   接口：HeytapHealthApi.getInstance().dataApi().insert(insertRequest, new HResponse<Integer>)

```java
HeytapHealthApi.getInstance().dataApi().insert(DataInsertRequest insertRequest, new HResponse<Integer>() {
	@Override
	public void onSuccess(Integer integer) {
		//integer为 ErrorCode.SUCCESS
		//TODO: insert success
	}

	@Override
	public void onFailure(int i) {
		//i为对应的ErrorCode错误码
		//TODO: insert fail
	}
}
```

insertRequest由 DataInsertRequest insertRequest = new DataInsertRequest.Builder() .setData(dataSetList) .build(); 创建。

数据由dataSetList传入。

要写入健身训练记录：需要使用DataSet，其中dataType为DataType.TYPE_GYM_STRENGTH_TRAINING。

每个DataSet包含一次运动，即由一个训练基础数据DataPoint和若干个训练动作数据DataPoint及若干个训练心率数据DataPoint构成。

- 类名：com.heytap.databaseengine.apiv3.data.DataSet
- dataPoints为List，可以包含多个DataPoint。
- dataType为DataType，表示该数据的类型，见DataType。使用 DataType.TYPE_GYM_STRENGTH_TRAINING

 

- 类名：com.heytap.databaseengine.apiv3.data.DataPoint
- dataType为数据类型
- startTimestamp填入该条运动记录的开始时间戳（utc），单位ms
- timestamp为心率时填入心率数据的时间戳，单位ms

 

**1.训练基础数据DataPoint:**

| dataType              | 数据类型             | Object                            | DataType.TYPE_GYM_STRENGTH_TRAINING |
| --------------------- | -------------------- | --------------------------------- | ----------------------------------- |
| startTimeStamp        | 开始时间戳           | long                              | 运动开始时间戳（utc），单位：ms     |
| values（Elements）    | 运动开始时间戳（秒） | Integer                           | Element.ELEMENT_START_TIMESTAMP     |
| 运动结束时间戳（秒）  | Integer              | Element.ELEMENT_END_TIMESTAMP     |                                     |
| 运动类型              | Integer              | Element.ELEMENT_SPORT_MODE        |                                     |
| 平均心率（count/min） | Integer              | Element.ELEMENT_AVG_HEART_RATE    |                                     |
| 最高心率（count/min） | Integer              | Element.ELEMENT_MAX_HEART_RATE    |                                     |
| 数据客户端            | String               | Element.ELEMENT_DATA_CLIENT       |                                     |
| 训练标题              | String               | Element.ELEMENT_TRAINING_TITLE    |                                     |
| 总容量（kg）          | Integer              | Element.ELEMENT_TRAINING_CAPACITY |                                     |
| 运动时长 （秒）       | Integer              | Element.ELEMENT_DURATION          |                                     |
| 消耗 (卡）            | Integer              | Element.ELEMENT_CALORIE           |                                     |

 

**2.训练动作数据DataPoint: 【按组连着添加，如递减组必须连着在一起如：3，d1,d2,d3的这样添加】**

| dataType          | 数据类型   | Object                                   | DataType.TYPE_TRAINING_ACTION   |
| ----------------- | ---------- | ---------------------------------------- | ------------------------------- |
| startTimeStamp    | 开始时间戳 | long                                     | 运动开始时间戳（utc），单位：ms |
| value（Elements） | 动作名称   | String                                   | Element.ELEMENT_TRAINING_ACTION |
| 轮                | String     | Element.ELEMENT_ACTION_ROUNDS            |                                 |
| 配重1             | Integer    | Element.ELEMENT_ACTION_COUNTWEIGHT_1     |                                 |
| 配重2             | Integer    | Element.ELEMENT_ACTION_COUNTWEIGHT_2     |                                 |
| 次数              | Integer    | Element.ELEMENT_TIMES                    |                                 |
| 完成状态          | Integer    | Element.ELEMENT_ACTION_COMPLETION_STATUS |                                 |

 

**3.训练心率数据DataPoint:** 

| dataType           | 数据类型         | Object  | DataType.                       |
| ------------------ | ---------------- | ------- | ------------------------------- |
| startTimeStamp     | 开始时间戳       | long    | 运动开始时间戳（utc），单位：ms |
| timeStamp          | 心率的数据时间戳 | long    | 心率数据时间戳，单位：ms        |
| values（Elements） | 心率（count/min) | Integer | Element.HEART_RATE              |

#### **写入一条健身训练记录数据**

```java
//写入一条健身训练记录
private void saveRecorddata() {
	DataSet.Builder dataSetBuilder = getBuilder();
	insertData(Collections.singletonList(dataSetBuilder.build()));
}

@NonNull
private DataSet.Builder getBuilder() {
	DataSet.Builder dataSetBuilder = DataSet.builder(DataType.TYPE_GYM_STRENGTH_TRAINING);
	//添加训练基础数据
	DataPoint base = DataPoint.builder(DataType.TYPE_GYM_STRENGTH_TRAINING)
			.setStartTimeStamp(DateUtil.getStartTime(System.currentTimeMillis()))//ms，应该设置为实际运动的开始时间戳，这里设置的为今天的0点时间戳
			.setElement(Element.ELEMENT_TRAINING_TITLE, "胸.三头.腹肌.2")
			.setElement(Element.ELEMENT_TRAINING_CAPACITY, 2200)//kg
			.setElement(Element.ELEMENT_DURATION, 1200)//s
			.setElement(Element.ELEMENT_CALORIE, 1100000)//cal
			.setElement(Element.ELEMENT_MAX_HEART_RATE, 170)
			.setElement(Element.ELEMENT_AVG_HEART_RATE, 130)
			.setElement(Element.ELEMENT_START_TIMESTAMP, (int)(DateUtil.getStartTime(System.currentTimeMillis()) / 1000))//s，应该设置为实际运动的开始时间秒，这里设置的为今天的0点的时间秒
			.setElement(Element.ELEMENT_END_TIMESTAMP, (int)(DateUtil.getStartTime(System.currentTimeMillis()) / 1000 + 1200))//s，应该设置为实际运动的结束时间秒，这里设置的为今天的0点的时间秒 + 1200秒
			.setElement(Element.ELEMENT_SPORT_MODE, SportMode.GYM_STRENGTH_TRAINING)
			.setElement(Element.ELEMENT_DATA_CLIENT, "test_client")
			.build();
	dataSetBuilder.add(base);
	//添加训练心率数据
	DataPoint hr = DataPoint.builder(DataType.TYPE_HEART_RATE)
			.setStartTimeStamp(DateUtil.getStartTime(System.currentTimeMillis()))//ms，应该设置为实际运动的开始时间戳，这里设置的为今天的0点时间戳
			.setTimeStamp(DateUtil.getStartTime(System.currentTimeMillis()))//ms，心率实时数据对应时间戳，这里设置的为今天的0点时间戳
			.setElement(Element.ELEMENT_HEART_RATE, 160)
			.build();
	dataSetBuilder.add(hr);
	DataPoint hr1 = DataPoint.builder(DataType.TYPE_HEART_RATE)
			.setStartTimeStamp(DateUtil.getStartTime(System.currentTimeMillis()))//ms，应该设置为实际运动的开始时间戳，这里设置的为今天的0点时间戳
			.setTimeStamp(DateUtil.getStartTime(System.currentTimeMillis()) + 60000)//ms，心率实时数据对应时间戳，这里设置的为今天的0点时间戳
			.setElement(Element.ELEMENT_HEART_RATE, 160)
			.build();
	dataSetBuilder.add(hr1);
	...
	//添加训练动作数据
	DataPoint action = DataPoint.builder(DataType.TYPE_TRAINING_ACTION)
			.setStartTimeStamp(DateUtil.getStartTime(System.currentTimeMillis()))//ms，应该设置为实际运动的开始时间戳，这里设置的为今天的0点时间戳
			.setElement(Element.ELEMENT_TRAINING_ACTION, "哑铃卧推")
			.setElement(Element.ELEMENT_ACTION_ROUNDS, "2")
			.setElement(Element.ELEMENT_ACTION_COUNTERWEIGHT_1, 15)//kg
			.setElement(Element.ELEMENT_ACTION_COUNTERWEIGHT_2, 15)//kg
			.setElement(Element.ELEMENT_TIMES, 10)
			.setElement(Element.ELEMENT_ACTION_COMPLETION_STATUS, 1)
			.build();
	dataSetBuilder.add(action);
	DataPoint action2 = DataPoint.builder(DataType.TYPE_TRAINING_ACTION)
			.setStartTimeStamp(DateUtil.getStartTime(System.currentTimeMillis()))//ms，应该设置为实际运动的开始时间戳，这里设置的为今天的0点时间戳
			.setElement(Element.ELEMENT_TRAINING_ACTION, "哑铃卧推")
			.setElement(Element.ELEMENT_ACTION_ROUNDS, "3")
			.setElement(Element.ELEMENT_ACTION_COUNTERWEIGHT_1, 18)//kg
			.setElement(Element.ELEMENT_ACTION_COUNTERWEIGHT_2, 18)//kg
			.setElement(Element.ELEMENT_TIMES, 8)
			.setElement(Element.ELEMENT_ACTION_COMPLETION_STATUS, 1)
			.build();
	dataSetBuilder.add(action2);
	DataPoint action3 = DataPoint.builder(DataType.TYPE_TRAINING_ACTION)
			.setStartTimeStamp(DateUtil.getStartTime(System.currentTimeMillis()))//ms，应该设置为实际运动的开始时间戳，这里设置的为今天的0点时间戳
			.setElement(Element.ELEMENT_TRAINING_ACTION, "哑铃卧推")
			.setElement(Element.ELEMENT_ACTION_ROUNDS, "d1")
			.setElement(Element.ELEMENT_ACTION_COUNTERWEIGHT_1, 18)//kg
			.setElement(Element.ELEMENT_ACTION_COUNTERWEIGHT_2, 15)//kg
			.setElement(Element.ELEMENT_TIMES, 8)
			.setElement(Element.ELEMENT_ACTION_COMPLETION_STATUS, 1)
			.build();
	dataSetBuilder.add(action3);
	DataPoint action4 = DataPoint.builder(DataType.TYPE_TRAINING_ACTION)
			.setStartTimeStamp(DateUtil.getStartTime(System.currentTimeMillis()))//ms，应该设置为实际运动的开始时间戳，这里设置的为今天的0点时间戳
			.setElement(Element.ELEMENT_TRAINING_ACTION, "哑铃卧推")
			.setElement(Element.ELEMENT_ACTION_ROUNDS, "d2")
			.setElement(Element.ELEMENT_ACTION_COUNTERWEIGHT_1, 15)//kg
			.setElement(Element.ELEMENT_ACTION_COUNTERWEIGHT_2, 15)//kg
			.setElement(Element.ELEMENT_TIMES, 8)
			.setElement(Element.ELEMENT_ACTION_COMPLETION_STATUS, 1)
			.build();
	dataSetBuilder.add(action4);

	DataPoint action5 = DataPoint.builder(DataType.TYPE_TRAINING_ACTION)
			.setStartTimeStamp(DateUtil.getStartTime(System.currentTimeMillis()))//ms，应该设置为实际运动的开始时间戳，这里设置的为今天的0点时间戳
			.setElement(Element.ELEMENT_TRAINING_ACTION, "飞鸟卧推")
			.setElement(Element.ELEMENT_ACTION_ROUNDS, "2")
			.setElement(Element.ELEMENT_ACTION_COUNTERWEIGHT_1, 16)//kg
			.setElement(Element.ELEMENT_ACTION_COUNTERWEIGHT_2, 16)//kg
			.setElement(Element.ELEMENT_TIMES, 12)
			.setElement(Element.ELEMENT_ACTION_COMPLETION_STATUS, 1)
			.build();
	dataSetBuilder.add(action5);
	...
	return dataSetBuilder;
}

private void insertData(List<DataSet> dataSetList) {
	DataInsertRequest insertRequest = new DataInsertRequest.Builder()
			.setData(dataSetList)
			.build();
	HeytapHealthApi.getInstance().dataApi().insert(insertRequest, new HResponse<Integer>() {
		@Override
		public void onSuccess(Integer integer) {
			//integer为 ErrorCode.SUCCESS
			//TODO: insert success
		}
	 
		@Override
		public void onFailure(int i) {
			//i为对应的ErrorCode错误码
			//TODO: insert fail
		}
	});
}
```

 

## 6.单位元素

### 6.1 数据元素

| name     | type   |
| -------- | ------ |
| 心率     | int    |
| 睡眠     | int    |
| 血氧     | int    |
| 血压     | float  |
| 压力     | int    |
| 步频     | int    |
| 速度     | float  |
| 步数     | int    |
| 消耗     | long   |
| 活动次数 | int    |
| 锻炼时长 | long   |
| 经度     | double |
| 纬度     | double |
| 海拔     | float  |

###  

### 6.2 统计

| type      | 数据类型   | 补充说明                                        |
| --------- | ---------- | ----------------------------------------------- |
| startTime | 开始时间戳 | 无                                              |
| endTime   | 结束时间戳 | 无                                              |
| Value     | 值对象     | 返回List<Value>列表，表示范围，数值从小到大排列 |

###  

### 6.3 记录

| type        | 运动记录类型      | 补充说明                     |
| ----------- | ----------------- | ---------------------------- |
| startTime   | 开始时间戳        | 无                           |
| endTime     | 结束时间戳        | 无                           |
| List<Value> | 各项详情/统计数据 | 运动记录数据由各体征数据构成 |

###  

### 6.4 详情

详情数据的统一格式。

| type      | 数据类型   | 补充说明                                         |
| --------- | ---------- | ------------------------------------------------ |
| startTime | 开始时间戳 | 单点数据表示产生时间戳；持续数据表示开始时间戳； |
| endTime   | 结束时间戳 | 单点数据为0；持续数据表示结束时间戳；            |
| Value     | 值对象     | 值类型不同，获取数据接口不同                     |

## 7.数据处理

```java
private void showDataSet(DataSet dataSet) {
    Log.i(TAG, "time end: " + System.currentTimeMillis());
    for (DataPoint dataPoint : dataSet.getDataPoints()) {
        Log.i(TAG, "data type name: " + dataPoint.getDataType().getName());
        Log.i(TAG, "data type start time: " + dataPoint.getStartTimeStamp());
        for (Element element : dataPoint.getDataType().getElements()) {
            Log.i(TAG, "field name: " + element.getName());
            Log.i(TAG, "field format: " + element.getFormat());
            Log.i(TAG, "value: " + dataPoint.getValue(element));
        }
    }
}
```

# 版本日志

| 更新时间   | 版本号 | 更新说明                                                     |
| ---------- | ------ | ------------------------------------------------------------ |
| 2024/12/25 | 2.1.7  | 2.1.7 修复HLog.e(TAG, e.getMessage())报NPE的bug              |
| 2024/11/04 | 2.1.6  | 2.1.6 修复SDK请求授权在授权页授权后没有返回成功的bug         |
| 2024/03/27 | 2.1.5  | 2.1.5 不再依赖RxJava，gson依赖版本更新为2.10.1               |
| 2023/10/21 | 2.1.2  | 2.1.2 将SDK的最小API由26降至23；优化请求授权时内存泄露；优化未安装健康APP时下载健康APP流程 |
| 2023/08/03 | 2.1.1  | 2.1.1 查询新增数据返回：心率统计查询新增静息心率、睡眠基准心率、步行平均心率；睡眠详情查询新增设备类型；睡眠统计查询新增入睡、出睡、睡眠评分、深睡时长、浅睡时长、清醒时长、快速眼动时长、睡眠片段数据。 |
| 2023/07/18 | 2.1.0  | 修复升级到2.0.8或2.0.9后，编译失败报InstallUtils.DownloadApp()方法找不到的问题。 |
| 2023/07/17 | 2.0.9  | 修复授权时内存泄漏，更新接入环境配置。minSdk版本由23升至26。 |
| 2023/06/01 | 2.0.8  | 运动单元新增支持写入健身运动记录数据至健康                   |
| 2023/03/08 | 2.0.7  | 运动单元新增运动记录的概要数据                               |
| 2022/9/29  | 2.0.4  | 新增同步授权云端API的能力，支持在一次授权中完成两种接入方式的鉴权流程；健康服务SDK新增（包含详情值与统计值）：个人信息（OpenID）、压力、血氧、睡眠、心电、每日活动、心率； 数据授权流程及页面优化。 |
| --         | 1.1.5  | 健康平台新增用户授权逻辑，支持三方拉起授权页向用户请求健康数据权限；用户可在健康内部的数据授权页管理三方授权范围。 |

 

# 错误码

| ErrorCode                         | 值     | 描述                         |
| --------------------------------- | ------ | ---------------------------- |
| SUCCESS                           | 100000 | 成功                         |
| ERR_PARAMETER_ERROR               | 100001 | 参数错误                     |
| ERR_SQLITE_EXCEPTION              | 100002 | 数据库数据处理异常           |
| ERR_BINDER_EXCEPTION              | 100003 | Binder错误                   |
| ERR_LOGIN_STATUS                  | 100004 | 帐号登录状态错误             |
| ERR_REMOTE_EXCEPTION              | 100005 | 远程服务器错误               |
| ERR_PERMISSION_DENY               | 100006 | 没有权限                     |
| ERR_HEALTH_APP_IS_NOT_INSTALLED   | 100007 | 健康app未安装                |
| ERR_HEALTH_APP_VERSION_IS_TOO_LOW | 100008 | 健康app版本过低              |
| ERR_DATA_TYPE_IS_NOT_SUPPORT      | 100009 | 当前版本不支持该类型数据     |
| ERR_FUN_NOT_IMPL                  | 100011 | 方法未实现                   |
| ERR_AUTH_FAILURE                  | 100012 | 授权失败                     |
| ERR_STORAGE_SPACE_LOW             | 100013 | 手机存储过低                 |
| ERR_AUTH_CANCEL                   | 100014 | 授权取消                     |
| ERR_BIND_SERVICE_FAIL             | 100015 | 绑定服务失败                 |
| ERR_DATA_INSERT                   | 101001 | 数据插入失败                 |
| ERR_DATA_READ                     | 101002 | 数据读取失败                 |
| ERR_DATA_DELTE                    | 101003 | 数据删除失败                 |
| ERR_DATA_SYNCING                  | 101004 | 正在同步数据                 |
| ERR_QUERY_EMPTY                   | 101005 | 读取数据为空                 |
| ERR_CHECK_SCOPE_EXCEPTION         | 101006 | 检测权限时发生异常           |
| ERR_DATA_INVALID                  | 101007 | 数据不可信，超过正常边界范围 |

 

# 公用部分说明

## 1.访问域名

测试环境：[**https://sporthealth-api-cn.wanyol.com/uat/open/**](https://sporthealth.wanyol.com/pre_prod/open/)

生产环境：https://sport.health.heytapmobi.com/open

 

## 2.接入时序图

![img]()![img](./assets/e63a2ef63ee6daa2be165cb846de66aa.png)

 

## 3.返回说明

| 参数      | 类型   | 是否必须 | 描述                          |
| --------- | ------ | -------- | ----------------------------- |
| errorCode | int    | 是       | 状态码 0标识成功 其他标识失败 |
| message   | String | 是       | 状态码描述                    |
| body      | Object | 否       | 返回数据 根据具体接口定义返回 |

示例：

![img](./assets/1e8234e55c5a4a8df3b292d43e9e38b9.png)

 

# 授权认证

## 1.接入流程

（1）[申请接入OPPO健康服务](https://open.oppomobile.com/documentation/page/info?id=11453)，提交必要资料(接入名称，RedirectUri，logo等)，审核通过后发放clientId和clientSecret。 

（2）配置OPPO运动健康登录授权页（目前OPPO提供H5的登录和授权页面）。

（3）登录成功并确认授权后将向您的应用程序返回一个授权码（Authorization Code），**授权码五分钟后失效，请尽快完成授权**。

（4）应用程序调用接口用授权码（Authorization Code）获得 accessToken，同时获得一个用于刷新 accessToken 的 refreshToken。**accessToken有效期24小时（非自然天）。**

（5）请求头中携带Access Token ，通过API上传或者获取用户个人或者运动健康等信息。

（6）在 accessToken 过期后，使用 refreshToken 获得新的 access_token（可选）。**refreshToken有效期30天，刷新accessToken同时会刷新refreshToken的有效期。若refreshToken失效，需要重新授权。**

 

## 2.配置OPPO健康服务登录授权页

申请拿到client_id和client_secret后，在应用app内合适位置放置一个按钮，点击按钮打开指定的oppo健康服务授权页面。备注：如果是H5接入，则跳转到对应授权的H5页面，H5负责第三步授权。三方只需要提供redirect_uri和client_id即可。具体步骤如下：

 

## 3.H5授权

欢太健康授权页H5测试环境跳转链接：

**[https://sporthealth-api-cn.wanyol.com](https://sporthealth.wanyol.com/pre_prod/open/)/u**at[**/h4/HeyTap/index.html#/?page=ThirdPartyAuthRedirect&**](https://sporthealth.wanyol.com/pre_prod/h5/HeyTap/index.html#/?page=ThirdPartyAuthRedirect&clientId=&redirectUri=)[**clientId=**](https://sporthealth.wanyol.com/pre_prod/h5/HeyTap/index.html#/?page=ThirdPartyAuthRedirect&clientId=&redirectUri=)[**&**](https://sporthealth.wanyol.com/pre_prod/h5/HeyTap/index.html#/?page=ThirdPartyAuthRedirect&clientId=&redirectUri=)[**redirectUri=**](https://sporthealth.wanyol.com/pre_prod/h5/HeyTap/index.html#/?page=ThirdPartyAuthRedirect&clientId=&redirectUri=)

生产环境跳转链接：

[**https://sport.health.heytapmobi.com/h4/HeyTap/index.html#/?page=ThirdPartyAuthRedirect&**](https://sport.health.heytapmobi.com/h5/HeyTap/index.html#/?page=ThirdPartyAuthRedirect&clientId=&redirectUri=)[**clientId=**](https://sport.health.heytapmobi.com/h5/HeyTap/index.html#/?page=ThirdPartyAuthRedirect&clientId=&redirectUri=)[**&**](https://sport.health.heytapmobi.com/h5/HeyTap/index.html#/?page=ThirdPartyAuthRedirect&clientId=&redirectUri=)[**redirectUri=**](https://sport.health.heytapmobi.com/h5/HeyTap/index.html#/?page=ThirdPartyAuthRedirect&clientId=&redirectUri=)

 

上述链接中的clientId、redirectUri需要开发者补充完整。例如：**[https://sporthealth-api-cn.wanyol.com](https://sporthealth.wanyol.com/pre_prod/open/)/u**at[**/h4/HeyTap/index.html#/?page=ThirdPartyAuthRedirect&**](https://sporthealth.wanyol.com/pre_prod/h5/HeyTap/index.html#/?page=ThirdPartyAuthRedirect&clientId=&redirectUri=)[**clientId=123**](https://sporthealth.wanyol.com/pre_prod/h5/HeyTap/index.html#/?page=ThirdPartyAuthRedirect&clientId=&redirectUri=)[**&**](https://sporthealth.wanyol.com/pre_prod/h5/HeyTap/index.html#/?page=ThirdPartyAuthRedirect&clientId=&redirectUri=)[**redirectUri=**](https://sporthealth.wanyol.com/pre_prod/h5/HeyTap/index.html#/?page=ThirdPartyAuthRedirect&clientId=&redirectUri=)[https://www.baidu.com?](http://www.baidu.com/)otherInfo=xxx&otherInfo2=xxx。redirectUri中可以携带三方额外信息，跳转时会原封不动的返回。***注意：redirectUri请严格按照规范填写，比如第一个参数是？后续是&，否则会造成无法识别\***

​                                                              

在欢太健康授权页授权完成之后会跳转到redirectUri对应的链接，并将authorizeCode和openId作为参数放在链接中。如：

[**https://www.baidu.com/callback?authorizeCode=CC7721**](https://www.baidu.com/callback?authorizeCode=CC7721)&openId=5313009198

三方app从该链接中取出authorizeCode和openId并进行下一步操作。  

 

## 4.根据授权码换取access token和refresh token

URL: v1/oauth/token

Method: POST

参数：

HEADER:

| 参数         | 是否必填 | 说明             |
| ------------ | -------- | ---------------- |
| Content-Type | 是       | application/json |
| Accept       | 是       | application/json |

 

BODY

| 参数              | 是否必填 | 说明                                                         |
| ----------------- | -------- | ------------------------------------------------------------ |
| clientId          | 是       | 应用唯一标识                                                 |
| clientSecret      | 是       | 秘钥                                                         |
| grantType         | 是       | 当grantType=authorizationCode时，表示用授权码换取accessToken。当grantType=refreshToken时,表示刷新accessToken |
| authorizationCode | 否       | 授权码 grantType=authorizationCode时必填                     |
| refreshToken      | 否       | grantType=refreshToken时必填                                 |
| redirectUri       | 否       | 应用回调地址，当 grant_type=authorization_code 时， redirect_uri 为必传参数，仅支持 http 和 https，不支持指定端口号，且传入的地址需要与获取 authorization_code 时，传入的回调地址保持一致 |

响应结果：

```markup
{
  "errorCode": 0,
  "message": "string",
  "body": {
            "accessToken": "954e744a1f4c6fc20f498e366b9aabd2c4b971fd",
	//grantType=authorizationCode时才会返回refreshToken
            "refreshToken": "954e744a1f4c6fc20f498e366b9aabd2c4b971fd",                          "expireAt": 1610457720,
            "scope": [
                       "READ_PROFILE",
                       "READ_HEART_RATE"
                      ]
           }
}
```

 

## 5.解除授权

URL: v1/oauth/revoke

Method: POST

参数：

HEADER:

| 参数         | 是否必填 | 说明             |
| ------------ | -------- | ---------------- |
| Content-Type | 是       | application/json |
| Accept       | 是       | application/json |

BODY

| 参数         | 是否必填 | 说明      |
| ------------ | -------- | --------- |
| accessToken  | 是       | 访问token |
| clientSecret | 是       | 秘钥      |

响应结果：

```markup
{
              "errorCode": 0,
              "message": "string",xxu
              "body": null
}
```

 

 

# 读取数据

读取数据接口统一需要如下请求头HEADER

| 参数         | 是否必填 | 说明              |
| ------------ | -------- | ----------------- |
| Content-Type | 是       | application/json  |
| Accept       | 是       | application/json  |
| access-token | 是       | 授权后返回的token |

 

## 1.查询用户信息

URL: /v1/data/user/profile

Method: GET

参数：

响应结果：

```markup
{
 "userName": "string"
}
```

 

## 2.查询用户定位信息

URL: /v1/data/user/location

Method: GET

参数：

响应结果：

```markup
{
       "city": "深圳市",//用户所在城市
       "county": "南山区",//用户所在区、县
       "modifyTime": 1629277703210//用户上报位置时间
}
```

 

## 3.查询心率

### 3.1 查询心率详情

URL: /v1/data/heartRate/detail

Method: GET

参数：

注意：查询范围不能超过一个月

| 参数            | 类型 | 是否必填 | 说明              |
| --------------- | ---- | -------- | ----------------- |
| startTimeMillis | Long | 是       | 开始时间 单位毫秒 |
| endTimeMillis   | Long | 是       | 结束时间 单位毫秒 |

 

响应结果：

```markup
 {
   "dataCreateTime": 0,//数据生成时间单位毫秒
   "heartRateValue": 0,//心率值
   "heartRateType": 0//心率类型 0=日常心率 1=静息心率 2=运动心率 3=日常过高心率 4=健走平均心率
5=睡眠心率 6=过低预警心率 7=手机测量心率
  }
```

 

### 3.2 查询心率统计

URL: /v1/data/heartRate/static

Method: GET

参数：

注意：查询范围不能超过一个月

| 参数            | 类型 | 是否必填 | 说明              |
| --------------- | ---- | -------- | ----------------- |
| startTimeMillis | Long | 是       | 开始时间 单位毫秒 |
| endTimeMillis   | Long | 是       | 结束时间 单位毫秒 |

 

响应结果：

```markup
 {
	"averageHeartRate":87 //平均心率 int
	"maxHeartRate": 130,//最大心率 int
    "minHeartRate": 77,//最小心率 int
    "statisticsDay": 20190830,//统计日期 int
    "createTime": 0,//创建时间单位毫秒
    "updateTime": 0 //更新时间单位毫秒
  }
```

 

## 4.查询步数

### 4.1 查询步数详情

URL: /v1/data/steps/detail

Method: GET

参数：

注意：查询范围不能超过一个月

| 参数            | 类型    | 是否必填 | 说明                                                         |
| --------------- | ------- | -------- | ------------------------------------------------------------ |
| startTimeMillis | Long    | 是       | 开始时间 单位毫秒                                            |
| endTimeMillis   | Long    | 是       | 结束时间 单位毫秒                                            |
| sportMode       | Integer | 否       | 运动模式 0=默认 1=户外健走 2=户外跑步 3=户外骑行 5=爬楼/爬山 6=久坐 7=泳池游泳 8=高尔夫 9=健身 10=室内跑 12=瑜伽 19=室内健走 31=羽毛球 32=椭圆机 33=划船机 34=室内骑车 35=自由训练 36=登山 37=越野 |

 

响应结果：

```markup
  {
   "calories": 0,//运动卡路里 Integer 单位卡
	"distance": 0,//运动距离 Integer 单位米
	"altitudeOffset": 0,//爬升高度 Integer 单位厘米
   "endTime": 0,//结束时间 Long 单位毫秒
   "sportMode": 0,//运动模式 Integer
   "startTime": 0,//开始时间 Long 单位毫秒
   "steps": 0//运动步数 Integer
	 "sportMode": 0 //运动模式 Integer
  }
```

 

### 4.2 查询步数统计

URL: /v1/data/steps/static

Method: GET

参数：

注意：查询范围不能超过一个月

| 参数            | 类型    | 是否必填 | 说明                                                         |
| --------------- | ------- | -------- | ------------------------------------------------------------ |
| startTimeMillis | Long    | 是       | 开始时间 单位毫秒                                            |
| endTimeMillis   | Long    | 是       | 结束时间 单位毫秒                                            |
| sportMode       | Integer | 否       | 运动模式-4：手机端消耗卡路里，-3：手表手环统计数据，-2：全部1=户外健走 2=户外跑步 3=户外骑行 5=爬楼/爬山 6=久坐 7=泳池游泳 8=高尔夫 9=健身" +"10=室内跑 12=瑜伽 19=室内健走 31=羽毛球 32=椭圆机 33=划船机 34=室内骑车 35=自由训练 36=登山 37=越野 |

 

响应结果：

```markup
 {
	"statisticsDay": 20190830,//统计日期 int
   "totalCalories": 0,//运动卡路里 Integer 单位卡
   "totalDistance": 0,//运动总距离 Integer 单位米
   "endTime": 0,//结束时间 Long 单位毫秒
   "startTime": 0,//开始时间 Long 单位毫秒
	"totalSteps": 0,//运动步数 Integer
	"totalDuration": 0,//运动总时长 Long 单位毫秒
	"totalAltitudeOffset": 0//累计爬升高度 Long 单位厘米
	 
  }
```

 

### 4.3 查询用户日常活动数据

URL: /v1/data/steps/dailyActivity

Method: GET

参数：

注意：查询范围不能超过一个月

| 参数            | 类型 | 是否必填 | 说明              |
| --------------- | ---- | -------- | ----------------- |
| startTimeMillis | Long | 是       | 开始时间 单位毫秒 |
| endTimeMillis   | Long | 是       | 结束时间 单位毫秒 |

 

响应结果：

```markup
[
	{
		"currentDayCaloriesGoal": 300000,//Integer 当天消耗目标 单位:卡
		"currentDayStepsGoal": 8000, //Integer 当天步数目标
		"statisticsDay": 20221019,//Integer 统计日期
		"totalCalories": 9000, //Long 运动卡路里 单位:卡
		"totalDistance": 157, //Integer 运动距离 单位：米
		"totalMoveAboutTimes": 1, //Integer 总活动次数
		"totalSteps": 424,//Integer 运动步数
		"totalWorkoutMinutes": 1 //Integer 锻炼总时长 单位:分钟
	}
]
```

 

## 5.查询用户绑定设备信息

URL: /v1/data/user/device

Method: GET

参数：

响应结果：

```markup
 //如果用户绑定多个设备 会返回多条记录
 {
              "deviceName": "OW20W1",//设备名称
              "deviceSn": "d5ba8585", //设备SN码 可以唯一标识一个设备
              "deviceType": 1,//设备类型 1=手表 2=手环
              "manufacturer": "OPPO" //设备制造厂商
       } 
```

 

## 6.查询血氧

### 6.1 查询血氧详情

URL: /v2/data/bloodOxygen/detail

Method: GET

参数：

注意：查询范围不能超过一个月。同时该接口是加密的，需要根据加解密算法和秘钥解密

| 参数            | 类型 | 是否必填 | 说明              |
| --------------- | ---- | -------- | ----------------- |
| startTimeMillis | Long | 是       | 开始时间 单位毫秒 |
| endTimeMillis   | Long | 是       | 结束时间 单位毫秒 |

 

响应结果：

解密前：

```
VkntQneppV6Qco+gAxJm7rN0WtrXNKNbmAeG1hepvQmjrj3M125aYSZiqKpVAKUZlRbrkXTFsMXcqJENXx6R8JIHP1sahhQPSdlhc+3B2xDqY8THsR899dv0Qkdi+KpyjlqfoeYbLt+U2ndgWw581y+y0s5KPUn9j+EmLU6DWFkNGQ8/RCap7CxBzypue/TNfOJpGayIb6Ti0A==
```

解密后：

```markup
   {
              "bloodOxygenSaturationType": 1,//血氧饱和度类型 0=日常血氧，1=睡眠血氧 2=自动间隔测试血氧 3=手动测试血氧 4=鼾症 秒级血氧 Integer
              "bloodOxygenSaturationValue": 99,//血氧饱和度值 Integer
              "dataCreatedTimestamp": 1629156789000 //数据生成时间 单位毫秒 Long
       },
       {
              "bloodOxygenSaturationType": 1,
              "bloodOxygenSaturationValue": 99,
              "dataCreatedTimestamp": 1629157094000
       },
       {
              "bloodOxygenSaturationType": 1,
              "bloodOxygenSaturationValue": 99,
              "dataCreatedTimestamp": 1629156911000
       } 
```

 

### 6.2 查询血氧统计

URL: /v2/data/bloodOxygen/static

Method: GET

参数：

注意：查询范围不能超过一个月。同时该接口是加密的，需要根据加解密算法和秘钥解密

| 参数            | 类型 | 是否必填 | 说明              |
| --------------- | ---- | -------- | ----------------- |
| startTimeMillis | Long | 是       | 开始时间 单位毫秒 |
| endTimeMillis   | Long | 是       | 结束时间 单位毫秒 |

 

响应结果：

解密前：

```
VkntQneppV6Qco+gAxJm7rN0WtrXNKNbmAeG1hepvQmjrj3M125aYSZiqKpVAKUZlRbrkXTFsMXcqJENXx6R8JIHP1sahhQPSdlhc+3B2xDqY8THsR899dv0Qkdi+KpyjlqfoeYbLt+U2ndgWw581y+y0s5KPUn9j+EmLU6DWFkNGQ8/RCap7CxBzypue/TNfOJpGayIb6Ti0A==
```

解密后：

```markup
  {
       "averageBloodOxygenSaturation": 97,//平均血氧饱和度 Integer
       "maxBloodOxygenSaturation": 99,//最大血氧饱和度 Integer
       "minBloodOxygenSaturation": 86,//最小血氧饱和度 Integer
       "statisticsDay": 20210817//统计日期 Integer
    } 
```

 

## 7.查询运动记录

### 7.1 运动记录查询（不包含轨迹GPS点等额外信息）

URL: /v1/data/sport/record

Method: GET

参数：

注意：查询范围不能超过一个月。

| 参数            | 类型 | 是否必填 | 说明              |
| --------------- | ---- | -------- | ----------------- |
| startTimeMillis | Long | 是       | 开始时间 单位毫秒 |
| endTimeMillis   | Long | 是       | 结束时间 单位毫秒 |

 

响应结果：

```markup
  {
       "dataType": 2,//运动数类型 1=健身类 2=其他运动类
       "startTime": 1630323565000, //开始时间 单位毫秒
       "endTime": 1630337130000,//结束时间 单位毫秒
       "sportMode": 10,//运动模式 室内跑 详情见文档附录
       "deviceType":"手表"，//设备类型 手表 手环
       "model":"OWW201",//设备型号
       "deviceName":"OPPO Watch 2 ECG版",//设备名称
       "otherSportData": {
           "avgHeartRate": 153,//平均心率 单位：count/min
           "avgPace": 585,//平均配速 单位s/km
           "avgStepRate": 115,//平均步频 单位step/min
           "bestStepRate": 135,//最佳步频 单位step/min
           "bestPace": 572,//最佳配速 单位s/km
           "totalCalories": 2176000,//总消耗 单位卡
           "totalDistance": 23175,//总距离 单位米
           "totalSteps": 26062,//总步数
           "totalClimb":348,//累计爬升 单位米
           "totalTime": 13562000//总时长，单位:毫秒
       }
    },
    {
       "dataType": 1,//运动数类型 1=健身类 2=其他运动类
       "startTime": 1630293981497 //开始时间 单位毫秒
       "endTime": 1630294218127,//结束时间 单位毫秒
       "sportMode": 9,//运动模式 健身 详情见文档附录
       "deviceType":"手表"，//设备类型 手表 手环
       "model":"OWW201",//设备型号
       "deviceName":"OPPO Watch 2 ECG版",//设备名称
       "fitnessData": {
           "avgHeartRate": 90,//平均心率 单位：count/min
           "courseName": "零基础减脂碎片练习",//课程名称
           "finishNumber": 1,//课程完成次数
           "trainedCalorie": 13554,//训练消耗的卡路里，单位:卡
           "trainedDuration": 176000//实际训练时间，单位:ms
       }
    } 
```

 

### 7.2 运动记录查询（包含轨迹GPS点等额外信息）

URL: /v2/data/sport/record

Method: GET

参数：

注意：该接口返回的数据量比较大，所以查询时间间隔范围不能超过一个天。

| 参数            | 类型 | 是否必填 | 说明              |
| --------------- | ---- | -------- | ----------------- |
| startTimeMillis | Long | 是       | 开始时间 单位毫秒 |
| endTimeMillis   | Long | 是       | 结束时间 单位毫秒 |

 

响应结果：

```markup
  {
       "dataType": 2,//运动数类型 1=健身类 2=其他运动类
       "startTime": 1630323565000, //开始时间 单位毫秒
       "endTime": 1630337130000,//结束时间 单位毫秒
       "sportMode": 10,//运动模式 室内跑 详情见文档附录
       "deviceType":"手表"，//设备类型 手表 手环
       "model":"OWW201",//设备型号
       "deviceName":"OPPO Watch 2 ECG版",//设备名称
       "otherSportData": {
	   "avgHeartRate": 153,//平均心率 单位：count/min
	   "avgPace": 585,//平均配速 单位s/km
	   "avgStepRate": 115,//平均步频 单位step/min
	   "bestStepRate": 135,//最佳步频 单位step/min
	   "bestPace": 572,//最佳配速 单位s/km
	   "totalCalories": 2176000,//总消耗 单位卡
	   "totalDistance": 23175,//总距离 单位米
	   "totalSteps": 26062,//总步数
           "totalClimb":348,//累计爬升 单位米
	   "totalTime": 13562000，//总时长，单位:毫秒
	   "kmPace":[519,454,466,455],//每公里耗时，单位秒 可能为空。第一公里耗时519秒，第二公里454秒
	   "gpsPoint":[{
			"latitude": 30.559628,//double  纬度
			"longitude": 104.03321100000001,//double 经度
			"timestamp": 1668517884000,//long 记录时间戳 毫秒
			"type": 0 //点类型 0=正常点 1=暂停点
		}],//GPS点信息 可能为空
	   "elevation":[{
			"timestamp": 1668517875000,//long 记录时间戳 毫秒
			"value": 4304//海拔 单位分米
		}],//海拔打点
	   "heartRate":[{
			"timestamp": 1668517875000,//long 记录时间戳 毫秒
			"value": 107//心率值
		}],//心率打点
	   "distance":[{
			"timestamp": 1668517875000,//long 记录时间戳 毫秒
			"value": 3//截止到记录时间累积距离 单位米
		}],//距离打点
           "pace":[{
			"timestamp": 1668517875000,//long 记录时间戳 毫秒
			"value": 310 //配速 秒/公里
		}],//配速打点
           "state":[{
			"timestamp": 1668517875000,//long 记录时间戳 毫秒
			"value": 0 //state=0表示运动 state=1表示暂停。暂停时间段相关的数据统计会被过滤，比如计算最高海拔和最高心率等
		}],//状态打点
	   "frequency":[{
			"timestamp": 1668517875000,//long 记录时间戳 毫秒
			"value": 172//步频
		}],//步频打点
    },
    {
       "dataType": 1,//运动数类型 1=健身类 2=其他运动类
       "startTime": 1630293981497 //开始时间 单位毫秒
       "endTime": 1630294218127,//结束时间 单位毫秒
       "sportMode": 9,//运动模式 健身 详情见文档附录
       "deviceType":"手表"，//设备类型 手表 手环
       "model":"OWW201",//设备型号
       "deviceName":"OPPO Watch 2 ECG版",//设备名称
       "fitnessData": {
           "avgHeartRate": 90,//平均心率 单位：count/min
           "courseName": "零基础减脂碎片练习",//课程名称
           "finishNumber": 1,//课程完成次数
           "trainedCalorie": 13554,//训练消耗的卡路里，单位:卡
           "trainedDuration": 176000//实际训练时间，单位:ms
       }
    } 
```

 

## 8.查询压力

### 8.1 查询压力详情

URL: /v1/data/stress/detail

Method: GET

参数：

注意：查询范围不能超过一个月。同时该接口是加密的，需要根据加解密算法和秘钥解密

| 参数            | 类型 | 是否必填 | 说明              |
| --------------- | ---- | -------- | ----------------- |
| startTimeMillis | Long | 是       | 开始时间 单位毫秒 |
| endTimeMillis   | Long | 是       | 结束时间 单位毫秒 |

 

响应结果：

解密后：

```markup
{
    "stressType": 0, // 压力类型，目前只有 0
    "stressValue": 0, // 压力值，取值区间 [0, 100]
    "dataCreatedTimestamp": 1629156911000 // 压力数据时间戳
  }
```

 

### 8.2 查询压力统计

URL: /v1/data/stress /statistic

Method: GET

参数：

注意：查询范围不能超过一个月。同时该接口是加密的，需要根据加解密算法和秘钥解密

| 参数            | 类型 | 是否必填 | 说明              |
| --------------- | ---- | -------- | ----------------- |
| startTimeMillis | Long | 是       | 开始时间 单位毫秒 |
| endTimeMillis   | Long | 是       | 结束时间 单位毫秒 |

 

响应结果：

解密后：

```markup
   {
    "maxStressValue": 0, // 当日最大压力值，取值区间 [0, 100]
    "relaxStressTotalTime": 0, // 放松时长，分钟，取值区间 [0, 1440]
    "normalStressTotalTime": 0, // 正常压力时长，分钟，取值区间 [0, 1440]
    "middleStressTotalTime": 0, // 中等压力时长，分钟，取值区间 [0, 1440]
    "highStressTotalTime": 0, // 高压力时长，分钟，取值区间 [0, 1440]
    "date": 20210817 // 统计日期
  } 
```

 

## 9.查询睡眠详情

### 9.1 查询睡眠详情

URL: /v1/data/sleep/detail

Method: GET

参数：

注意：查询范围不能超过一个月。同时该接口是加密的，需要根据加解密算法和秘钥解密

| 参数            | 类型 | 是否必填 | 说明              |
| --------------- | ---- | -------- | ----------------- |
| startTimeMillis | Long | 是       | 开始时间 单位毫秒 |
| endTimeMillis   | Long | 是       | 结束时间 单位毫秒 |

 

响应结果：

解密后：

```markup
   {
    "sleepType": 0, // 0 夜间睡眠
    "sleepState": 0, // 睡眠状态 1 入睡, 2 沉睡, 3 快速眼动, 4 浅睡, 5 清醒, 6 出睡
    "bedTimeState": 0, // 睡前状态 用三位bit标识 从左到右分别标识卧床、想睡、体动（1表示有，0表示没有）,比如110 表示卧床想睡没有体动
    "startTimestamp": 0, // 开始睡眠时间戳
    "endTimestamp": 0 // 结束睡眠时间戳
  } 
```

 

### 9.2 查询睡眠统计

URL: /v1/data/sleep/statistic

Method: GET

参数：

注意：查询范围不能超过一个月。同时该接口是加密的，需要根据加解密算法和秘钥解密

| 参数            | 类型 | 是否必填 | 说明              |
| --------------- | ---- | -------- | ----------------- |
| startTimeMillis | Long | 是       | 开始时间 单位毫秒 |
| endTimeMillis   | Long | 是       | 结束时间 单位毫秒 |

 

响应结果：

解密后：

```markup
   {
    "fallAsleep": 0, // 入睡时间戳
    "sleepOut": 0, // 出睡时间戳
    "totalSleepTime": 0, // 总睡眠时长，分钟
    "totalWakeUpTime": 0, // 清醒时长，分钟
    "totalDeepSleepTime": 0, // 深睡时长，分钟
    "totalLightlySleepTime": 0, // 浅睡时长，分钟
    "totalRemTime": 0, // 快速眼动期时长，分钟
    "date": 20211201, // 统计日期
    "sleepScore": 87 // Integer  睡眠评分
  } 
```

 

### 9.3 查询睡眠指标

URL: /v1/data/sleep/indexStat

Method: GET

参数：

注意：查询范围不能超过一个月。同时该接口是加密的，需要根据加解密算法和秘钥解密

| 参数            | 类型 | 是否必填 | 说明              |
| --------------- | ---- | -------- | ----------------- |
| startTimeMillis | Long | 是       | 开始时间 单位毫秒 |
| endTimeMillis   | Long | 是       | 结束时间 单位毫秒 |

 

响应结果：

解密后：

```markup
   {
    "deviceType": 0, // int 设备类型 0=手机1=手表 2=手环 3=RS表
    "avgSleepSpo2": 0, //int 平均睡眠血氧
    "basalSleepHeartRate": 70, // int 睡眠基准心率
    "sleepHeartRateRangeLow": 60, // int 睡眠心率范围（低）
    "sleepHeartRateRangeHigh": 80, //int 睡眠心率范围（高）
    "sleepBreatheRangeLow": 0, // int 睡眠呼吸率范围（低）
    "sleepBreatheRangeHigh": 0, // int 睡眠呼吸率范围（低）
    "outputRate": 0, // int 出值率 0-100
    "bedTimeData":[{"type":1,"bedTimestamp":1702740600},{"type":2,"bedTimestamp":1702771200}] //睡前活动 type int 1上床 2下床 bedTimestamp int 上下床时间戳戳，单位是秒
    "date": 20231201 // 统计日期
  } 
```

### 9.4 查询分段睡眠日统计

URL: /v1/data/sleep/fragmentStat

Method: GET

参数：

注意：查询范围不能超过一个月。同时该接口是加密的，需要根据加解密算法和秘钥解密

| 参数            | 类型 | 是否必填 | 说明              |
| --------------- | ---- | -------- | ----------------- |
| startTimeMillis | Long | 是       | 开始时间 单位毫秒 |
| endTimeMillis   | Long | 是       | 结束时间 单位毫秒 |

 

响应结果：

解密后：

```java
[
	{
		"calibration": false, //是否校准
		"date": 20230720,//日期
		"deviceUniqueId": "",//设备id 可空
		"modifiedTimestamp": 1689902974951,
		"restInTime": 1689854400000,//作息入睡时间戳
		"restOutTime": 1689854400000,//作息出睡时间戳
		"score": 0,//睡眠评分
		"sleepDayFrgDataList": [ //分段睡眠列表
			{
				"sleepInTime": 1689786600000,
				"sleepOutTime": 1689811500000,
				"totalDeepSleepTime": 91,
				"totalLightlySleepTime": 237,
				"totalREMSleepTime": 84,
				"totalSleepTime": 412,
				"totalWakeTime": 3,
				"wakeCount": 3
			},
			{
				"sleepInTime": 1689832320000,
				"sleepOutTime": 1689833220000,
				"totalDeepSleepTime": 0,
				"totalLightlySleepTime": 15,
				"totalREMSleepTime": 0,
				"totalSleepTime": 15,
				"totalWakeTime": 0,
				"wakeCount": 0
			}
		],
		"sleepMainData": { //主睡
			"sleep3HoursBeforeTime": 1689775800000,//入睡前3小时  不早于20:00
			"sleepInTime": 1689786600000,
			"sleepInTimeMinutesOffset": 1510,//入睡时间分钟数，相对昨天0点
			"sleepOutTime": 1689811500000,
			"sleepOutTimeMinutesOffset": 1925,//出睡时间分钟数，相对昨天0点
			"totalDeepSleepTime": 91,
			"totalLightlySleepTime": 237,
			"totalREMSleepTime": 84,
			"totalSleepTime": 412,
			"totalWakeTime": 3,
			"wakeCount": 3
		},
		"sleepInTime": 1689786600000,//入睡时间戳
		"sleepOutTime": 1689833220000,//出睡时间戳
		"standardTime": 480,//达标时长  单位分钟
		"totalDeepSleepTime": 91,//深睡总时长  单位分钟
		"totalLightlySleepTime": 252,//浅睡总时长  单位分钟
		"totalREMSleepTime": 84,//REM总时长  单位分钟
		"totalSleepTime": 427,// 睡眠总时长  单位分钟
		"totalWakeTime": 3,//清醒总时长 单位分钟
		"wakeCount": 3//清醒次数
	}
]
```

 

# 写入数据

写入数据接口统一需要如下请求头HEADER

| 参数         | 是否必填 | 说明              |
| ------------ | -------- | ----------------- |
| Content-Type | 是       | application/json  |
| Accept       | 是       | application/json  |
| access-token | 是       | 授权后返回的token |

 

## 1.运动记录写入

URL: /v2/data/sport/record

Method: POST

参数：

| 参数名            | 类型          | 是否必填 | 备注                                                         |
| ----------------- | ------------- | -------- | ------------------------------------------------------------ |
| startTimestamp    | Long          | 是       | 开始时间戳 单位毫秒                                          |
| endTimestamp      | Long          | 是       | 结束时间戳 单位毫秒                                          |
| sportMode         | Integer       | 是       | 运动类型  2=户外跑步 3=户外骑行 36=登山 37=越野跑 506=徒步   |
| deviceType        | String        | 否       | 设备类型 枚举，当前设备类型有 Watch,Band,WATCH_GT,WATCH2,BAND2,REALME_GT, WATCH3,BANDHSB,WATCH3SE,WATCH3PRO,WATCH4PRO,WATCH4,WATCH_STAR |
| deviceUniqueId    | String        | 否       | 设备唯一ID 即设备蓝牙mac 30:1A:BA:19:1E:16                   |
| avgPace           | Integer       | 否       | 平均配速 s/km                                                |
| bestPace          | Integer       | 否       | 最佳配速 s/km                                                |
| avgHeartRate      | Integer       | 否       | 平均心率 count/min                                           |
| maxHeartRate      | Integer       | 否       | 最大心率 count/min                                           |
| minHeartRate      | Integer       | 否       | 最小心率 count/min                                           |
| avgStepRate       | Integer       | 否       | 平均步频 step/min                                            |
| bestStepRate      | Integer       | 否       | 最佳步频 step/min                                            |
| totalDistance     | Integer       | 是       | 总距离 米                                                    |
| totalCalories     | Long          | 是       | 动态消耗 卡                                                  |
| totalCal          | Long          | 是       | 总消耗 卡                                                    |
| totalSteps        | Integer       | 是       | 总步数                                                       |
| totalTime         | Long          | 是       | 总耗时 毫秒                                                  |
| totalClimb        | Integer       | 否       | 累计爬升 米                                                  |
| cumulativeDecline | Integer       | 否       | 累计下降 米                                                  |
| maxElevation      | Integer       | 否       | 最高海拔 米                                                  |
| kmPace            | List<Integer> | 否       | 每公里配速 单位秒/公里 按顺序第一个元素表示第一公里耗时多少秒 |
| elevation         | List<String>  | 否       | 实时海拔 单位分米。 结构如下所示timestamp,elevation 例如:["1705047085000,-288","1705047086000,-288","1705047087000,-282"]。注意中间是英文逗号。每个点间隔1s并且时间升序排列。 |
| distance          | List<String>  | 否       | 实时距离 单位米。结构如下所示timestamp,distance 例如:["1705047085000,0","1705047086000,7","1705047087000,10"] 注意中间是英文逗号。 每个点间隔1s并且 时间升序排列。距离从0累加。 |
| pace              | List<String>  | 否       | 实时配速 s/km 结构如下所示timestamp,pace 例如:["1705047085000,303","1705047086000,304","1705047087000,304"] 注意中间是英文逗号。 每个点间隔1s并且 时间升序排列。 |
| heartRate         | List<String>  | 否       | 实时心率 count/min 结构如下所示timestamp,heartRate 例如:["1705047085000,151","1705047086000,141","1705047087000,148"] 。每个点间隔1s并且时间升序排列 。 |
| frequency         | List<String>  | 否       | 实时步频 step/min 结构如下所示timestamp,frequency 例如:["1705047085000,144","1705047086000,156","1705047087000,160"]。每个点间隔1s并且时间升序排列。 |
| stride            | List<String>  | 否       | 实时步幅 厘米 结构如下所示timestamp,stride 例如:["1705047085000,64","1705047086000,64","1705047087000,64"] 。每个点间隔1s并且时间升序排列。 |
| state             | List<String>  | 是       | 实时状态。结构如下所示timestamp,state 例如:["1705047085000,0","1705047086000,0","1705047087000,1"] 。每个点间隔1s并且时间升序排列。state=0表示运动 state=1表示暂停。暂停时间段相关的数据统计会被过滤，比如计算最高海拔和最高心率等 |
| gps               | List<String>  | 否       | 实时轨迹 结构如下所示timestamp,latitude,longitude,state,speed 时间戳 维度 经度 状态（0=正常 1=暂停）速度。例如:["1705047085000,22.561582664661067,113.87669082713569,0,0.0","1705047086000,22.561602710540647,113.87668365710148,0,1.438849"。每个点间隔1s并且时间升序排列 |

响应结果：

```markup
{
    "errorCode": 0,
    "message": "成功",
    "body": true
}
```

# 推送数据

这部分数据由开发平台主动推送给三方服务器，目前只推送如下几类信息。推送的前提是用户当前授权中并且已提供相应的接口的回调地址（post方式，content-type=application/json 并且不同的数据类型不同的回调地址）。例如：https://www.oppo.com/heart/callback

入参：

| 参数 | 类型   | 是否必填 | 说明         |
| ---- | ------ | -------- | ------------ |
| data | String | 是       | 加密后的数据 |

data的数据是加密后的，需要根据加解密算法解析出相应的数据，加解密算法具体详见6.2。具体的数据结构如下：

## 1.心率异常推送

| 字段               | 类型    | 含义                                                         |
| ------------------ | ------- | ------------------------------------------------------------ |
| openId             | String  | 用户唯一标识 授权的时候返回                                  |
| ssoid              | String  | oppo内部系统对接时使用账号ID                                 |
| heartRateAlarmType | Integer | 心率告警类型，1:心率过低 2:心率过高                          |
| heartRateType      | Integer | 心率类型，0=日常心率 1=静息心率 2=运动心率 3=日常过高心率 4=健走平均心率5=睡眠心率 6=过低预警心率 7=手机测量心率 |
| heartRateValueMin  | Integer | 心率值最低值                                                 |
| heartRateValueMax  | Integer | 心率值最高值                                                 |
| startTimestamp     | Long    | 心率数据开始时间                                             |
| endTimestamp       | Long    | 心率数据结束时间                                             |
| heartRateLowest    | Integer | 心率过低阀值                                                 |
| heartRateHighest   | Integer | 心率过高阀值                                                 |

 

## 2.跌倒信息推送

| 字段      | 类型   | 含义                         |
| --------- | ------ | ---------------------------- |
| openId    | String | 用户唯一标识 授权的时候返回  |
| ssoid     | String | oppo内部系统对接时使用账号ID |
| timestamp | Long   | 跌倒发生时间                 |

 

## 3.入睡事件

```markup
{
  "type": 1, // int, 入睡:1
  "timestamp": 1656582640000, // long
  "ssoid": "571603459" // string, OPPO 用户账号, 仅限内部使用
}
```

 

## 4.运动记录更新推送

| 字段      | 类型   | 含义                                                         |
| --------- | ------ | ------------------------------------------------------------ |
| openId    | String | 用户唯一标识 授权的时候返回                                  |
| dataType  | String | 数据类型 目前只有一种 SPORT_RECORD                           |
| timestamp | Long   | 运动记录开始时间(查询的开始时间 ，结束时间用该时间加一天即可) |

 

# 下载数据

为了应对医疗或科研等相关场景的大批数据获取的需求，该部分提供异步批量下载的功能。要使用该功能，有如下前提。1.接入方需提供用户授权接入方查询用户相关数据的书面证明。2.用户需要使用健康APP并且登录。

基本流程：

- [申请接入OPPO健康服务](https://open.oppomobile.com/documentation/page/info?id=11453)，提交必要资料(接入名称，redirectURL，logo)，审核通过后发放clientId和clientSecret。
- 提供需要批量查询用户名单（用户手机号码），平台会返回相应的openIds
- 获取应用级access-token
- 提交下载任务
- 查询下载任务

 

下载数据接口统一需要如下请求头HEADER

| 参数         | 是否必填 | 说明             |
| ------------ | -------- | ---------------- |
| Content-Type | 是       | application/json |
| Accept       | 是       | application/json |

 

## 1.生成应用级AccessToken

URL: /v2/download/token

Method: POST

参数：

| 参数         | 类型   | 是否必填 | 说明                          |
| ------------ | ------ | -------- | ----------------------------- |
| clientId     | String | 是       | 三方应用ID 接入时平台会提供   |
| clientSecret | String | 是       | 三方应用秘钥 接入时平台会提供 |

 

响应结果：

```java
 {
   "token": "cMe3PLyJckBTKNoUaLJUdZf+huhvv1ljzvpXl6Tqvq3GrE65tr5GOTx+kDC+RjXPK0hQueE=",//应用级token 有效期7天
   "expireAt": 1677600000000,//token过期时间
  }
```

###  

## 2.提交下载任务

URL: /v2/download/task

Method: POST 

 

请求头

| 参数         | 是否必填 | 说明             |
| ------------ | -------- | ---------------- |
| Content-Type | 是       | application/json |
| Accept       | 是       | application/json |
| client-id    | 是       | 三方应用ID       |
| access-token | 是       | 应用级token      |

 

参数：

注意：查询范围不能超过一个月。该任务必须等已提交的任务完成后方可再次提交

| 参数           | 类型         | 是否必填 | 说明                                                         |
| -------------- | ------------ | -------- | ------------------------------------------------------------ |
| openIds        | List<String> | 是       | 用户openId 接入时平台会提供 目前一次最多支持100个用户同时下载 |
| dataCodes      | List<String> | 是       | 下载数据类型 PRESSURE=压力 DAILY_ACTIVITY=步数和日常活动数据 HEART_RATE=心率 SPORT_DATA=运动记录 DEVICE_DATA=设备数据 BLOOD_OXYGEN_DATA=血氧 SLEEP_DATA=睡眠 |
| startTimestamp | Long         | 是       | 查询开始时间戳                                               |
| endTimestamp   | Long         | 是       | 查询结束时间戳                                               |

 

响应结果：

```java
 {
   "taskId": 1000,//Long 下载任务Id 可用于查询下载任务进度
  }
```

 

## 3.查询下载任务进度

URL: /v2/download/record

Method: GET

 

请求头

| 参数         | 是否必填 | 说明             |
| ------------ | -------- | ---------------- |
| Content-Type | 是       | application/json |
| Accept       | 是       | application/json |
| client-id    | 是       | 三方应用ID       |
| access-token | 是       | 应用级token      |

 

参数：

| 参数   | 类型 | 是否必填 | 说明       |
| ------ | ---- | -------- | ---------- |
| taskId | Long | 是       | 任务下载Id |

 

响应结果：

```java
{
  "taskId": 1000,//Long 下载任务ID
  "downloadUrl": "string",  //任务处理成功后 数据的下载链接
  "status": 0, //任务状态 0=待处理 1=处理中 2=处理成功 3=处理失败
  "createTime": "2023-03-09T09:22:29.000Z" //任务创建时间
}
```

# 附录

## 1.错误码

| **错误码** | **描述**                       | **解决方法**                                                 |
| ---------- | ------------------------------ | ------------------------------------------------------------ |
| 100001     | 服务异常                       | 联系OPPO运动健康反馈异常。                                   |
| 100002     | 权限无效                       | 授予OPPO运动健康限定的权限。                                 |
| 100003     | clientId 格式无效              | 使用OPPO运动健康分发的 clientId。                            |
| 100004     | client 无效                    | 使用OPPO运动健康分发的 clientId。                            |
| 100005     | client 认证失败                | 使用正确的 clientSecret。                                    |
|            |                                |                                                              |
| 101001     | authorizationCode 格式无效     | 使用OPPO运动健康分发的 authorizationCode。                   |
| 101002     | authorizationCode 无效         | 引导用户重新授权。                                           |
| 101003     | authorizationCode 过期         | 引导用户重新授权。                                           |
| 101004     | authorizationCode 重复使用     | 引导用户重新授权。妥善保管授权码，慎防攻击。                 |
| 101005     | authorizationCode 重复生成     | 在授权码有效期内置换 accessToken 进行后续流程。否则等待授权码有效期结束后，引导用户重新授权。 |
| 101006     | redirectURI 格式无效           | 使用接入OPPO运动健康时设置的协议、域名。                     |
| 101007     | redirectURI 不匹配             | 使用接入OPPO运动健康时设置的协议、域名。                     |
| 101008     | 至少授权一项                   | 引导用户至少授予一项权限                                     |
| 101009     | 授权关系无效                   | 联系OPPO运动健康反馈异常。                                   |
|            |                                |                                                              |
| 102001     | accessToken 格式无效           | 使用OPPO运动健康分发的accessToken。                          |
| 102002     | accessToken 无效               | 更新 accessToken。                                           |
| 102003     | accessToken 访问过频           | 降低访问频率。                                               |
| 102004     | accessToken 访问配额不足       | 降低访问频率。                                               |
|            |                                |                                                              |
| 103001     | refreshToken 格式无效          | 使用OPPO运动健康分发的refreshToken。                         |
| 103002     | refreshToken 无效              | 引导用户重新授权。                                           |
| 103003     | grantType 无效                 | 使用有效授权类型。                                           |
|            |                                |                                                              |
| 120101     | 数据接口权限范围未定义         | 访问正确的资源。                                             |
| 120101     | 数据接口未授权                 | 访问已经授权的资源。                                         |
| 120101     | 数据查询时间间隔不能超过一个月 | 缩短查询时间间隔。                                           |

 

## 2.加密算法

```markup
//加解密算法，每次申请接入OPPO健康服务时，并且需要获取血氧等需要加密的数据时，健康服务都会分配一个秘钥，即下文的passWord。得到的字符串采用 aesDecryptByGCkdfhM方法解密接口即可，解密出来的字符串为JSONString。
public static String aesEncryptByGCM(String passWord, String content) throws Exception {
        byte[] iv = generateSecureBytes(16);
        byte[] input = content.getBytes(StandardCharsets.UTF_8);
        byte[] digest = passWord.getBytes(StandardCharsets.UTF_8);
        SecretKeySpec skc = new SecretKeySpec(digest, "AES");
        // 报 java.security.NoSuchProviderException: no such provider: BC，需要加上这一段，同时需要bcprov-jdk15on.jar
        // Security.addProvider(new BouncyCastleProvider());
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding", "BC");
        cipher.init(1, skc, new GCMParameterSpec(128, iv));
        byte[] encrypted = cipher.doFinal(input);
        byte[] data = new byte[16 + encrypted.length];
        System.arraycopy(iv, 0, data, 0, 16);
        System.arraycopy(encrypted, 0, data, 16, encrypted.length);
        return java.util.Base64.getEncoder().encodeToString(data);
}
private static byte[] generateSecureBytes(int num) {
        byte[] bytes = new byte[num];
        new SecureRandom().nextBytes(bytes);
        return bytes;
}
public static String aesDecryptByGCM(String passWord, String content) throws Exception {
        byte[] input = java.util.Base64.getDecoder().decode(content);
        byte[] keys = passWord.getBytes(StandardCharsets.UTF_8);
        byte[] iv = new byte[16];
        System.arraycopy(input, 0, iv, 0, 16);
        SecretKeySpec secretKeySpec = new SecretKeySpec(keys, "AES");
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding", "BC");
        cipher.init(2, secretKeySpec, new GCMParameterSpec(128, iv));
        byte[] encrypted = new byte[input.length - 16];
        System.arraycopy(input, 16, encrypted, 0, encrypted.length);
        byte[] clearByte = cipher.doFinal(encrypted);
        return new String(clearByte, StandardCharsets.UTF_8);
}
public static void main(String[] args) throws Exception {
        String a = aesEncryptByGCM("Npz24jVWtKSCEThhMTlaF83Zj7dnbgqM", "456549120");
        System.out.println(a);
        System.out.println(aesDecryptByGCM("Npz24jVWtKSCEThhMTlaF83Zj7dnbgqM", a));
}

```

## 3.运动记录实例数据

```java
//骑行运动记录示例
{
	"errorCode": 0,
	"message": "成功",
	"body": [
		{
			"startTime": 1732607519000,
			"endTime": 1732607792000,
			"sportMode": 3,
			"deviceType": "手表",
			"model": "OWW231",
			"deviceName": "OPPO Watch X",
			"dataType": 2,
			"otherSportData": {
				"avgPace": 260,
				"bestPace": 130,
				"avgHeartRate": 127,
				"avgStepRate": 0,
				"bestStepRate": 0,
				"totalDistance": 1030,
				"totalCalories": 26000,
				"totalSteps": 0,
				"totalTime": 268000,
				"totalClimb": 6,
				"kmPace": [],
				"gpsPoint": [
					{
						"longitude": 117.13532500000001,
						"latitude": 34.214658,
						"type": 0,
						"timestamp": 1732607529000
					},
					{
						"longitude": 117.13529833333333,
						"latitude": 34.21459311111111,
						"type": 0,
						"timestamp": 1732607530000
					}
				],
				"heartRate": [
					{
						"value": 0,
						"timestamp": 1732607520000
					},
					{
						"value": 0,
						"timestamp": 1732607521000
					}
				],
				"elevation": [
					{
						"value": 609,
						"timestamp": 1732607520000
					},
					{
						"value": 609,
						"timestamp": 1732607521000
					}
				],
				"frequency": [],
				"state": [
					{
						"value": 0,
						"timestamp": 1732607520000
					},
					{
						"value": 0,
						"timestamp": 1732607521000
					}
				],
				"distance": [
					{
						"value": 0,
						"timestamp": 1732607520000
					},
					{
						"value": 0,
						"timestamp": 1732607521000
					}
				],
				"pace": [
					{
						"value": 0,
						"timestamp": 1732607520000
					},
					{
						"value": 0,
						"timestamp": 1732607521000
					}
				]
			}
		}
	]
}
//游泳运动记录示例
{
	"errorCode": 0,
	"message": "成功",
	"body": [
		{
			"startTime": 1732789443000,
			"endTime": 1732793637000,
			"sportMode": 7,
			"deviceType": "手表",
			"model": "OWW221",
			"deviceName": "WATCH3PRO",
			"dataType": 2,
			"otherSportData": {
				"avgPace": 2477,
				"bestPace": 0,
				"avgHeartRate": 143,
				"avgStepRate": 0,
				"bestStepRate": 0,
				"totalDistance": 1600,
				"totalCalories": 614000,
				"totalSteps": 0,
				"totalTime": 3964000,
				"totalClimb": 0,
				"kmPace": [],
				"gpsPoint": [],
				"heartRate": [
					{
						"value": 0,
						"timestamp": 1732607520000
					},
					{
						"value": 0,
						"timestamp": 1732607521000
					}
				],
				"elevation": [],
				"frequency": [],
				"state": [
					{
						"value": 0,
						"timestamp": 1732607520000
					},
					{
						"value": 0,
						"timestamp": 1732607521000
					}
				],
				"distance": [
					{
						"value": 0,
						"timestamp": 1732607520000
					},
					{
						"value": 0,
						"timestamp": 1732607521000
					}
				],
				"pace": [
					{
						"value": 0,
						"timestamp": 1732607520000
					},
					{
						"value": 0,
						"timestamp": 1732607521000
					}
				]
			}
		}
	]
}

```

## 4.运动类型枚举

```markup
/**
  * walk also include outdoor fitness walk 走路（户外健走）   
 */
    public static final int WALK = 1;
 
    /**
     * common out door run 跑步（户外跑步）
     */
    public static final int RUN = 2;
 
    /**
     * ride by bike 骑行（户外骑行） 
     */
    public static final int RIDE = 3;
 
    /**
     * drive or take bus 乘车
     */
    public static final int BY_BUS = 4;
 
    /**
     * climb mountains or steps 爬楼
     */
    public static final int CLIMB = 5;
 
    /**
     * stand or sitting for hours 久坐
     */
    public static final int STANDING = 6;
 
    /**
     * pool swim 游泳池游泳
     */
    public static final int SWIM = 7;
 
    /**
     * play golf 高尔夫
     */
    public static final int GOLF = 8;
 
    /**
     * gym, health build 健身
     */
    public static final int FITNESS = 9;
 
    /**
     * common indoor run 普通室内跑
     */
    public static final int INDOOR_RUN = 10;
 
    /**
     * yoga 瑜伽
     */
    public static final int YOGA = 12;
 
    /**
     * outdoor physical run 户外跑步
     */
    public static final int OUTDOOR_PHYSICAL_RUN = 13;
 
    /**
     * indoor physical run 室内体能跑
     */
    public static final int INDOOR_PHYSICAL_RUN = 14;
 
    /**
     * outdoor 5km relaxing run 室外5KM轻松跑
     */
    public static final int OUTDOOR_5KM_RELAX_RUN = 15;
 
    /**
     * indoor 5km relaxing run 室内5KM轻松跑
     */
    public static final int INDOOR_5KM_RELAX_RUN = 16;
 
    /**
     * outdoor fat reduce run 室外减脂跑
     */
    public static final int OUTDOOR_FAT_REDUCE_RUN = 17;
 
    /**
     * indoor fat reduce run 室内减脂跑
     */
    public static final int INDOOR_FAT_REDUCE_RUN = 18;
 
    /**
     * indoor fitness walk 室内健走
     */
    public static final int INDOOR_FITNESS_WALK = 19;
 
    /**
     * treadmill run 跑步机
     */
    public static final int TREADMILL_RUN = 21;
 
    /**
     * marathon 马拉松
     */
    public static final int MARATHON = 22;
 
    /**
     * badminton 羽毛球
     */
    public static final int BADMINTON = 31;
 
    /**
     * elliptical machine 椭圆机
     */
    public static final int ELLIPTICAL_MACHINE = 32;
 
    /**
     * rowing machine 划船机
     */
    public static final int ROWING_MACHINE = 33;
 
    /**
     * indoor motion bike 室内骑车，动感单车
     */
    public static final int INDOOR_MOTION_BIKE = 34;
 
    /**
     * free training 自由训练
     */
    public static final int FREE_TRAINING = 35;
 
    /**
     * mountain climbing 登山
     */
    public static final int MOUNTAIN_CLIMBING = 36;
 
    /**
     * cross country 越野
     */
    public static final int CROSS_COUNTRY = 37;
 
    /**
     * cross country 游戏
     */
    public static final int GAME = 38;
 
    /**
     *  自动识别跑步
     */
    public static final int AUTO_MODE_RUN= 40;
    /**
     * 自动识别健走
     */
    public static final int AUTO_MODE_WALK = 41

    /**
     * all run state data for searching
     */
    public static final int RUN_ALL = 100;
    /**
     * all walk state data for searching
     */
    public static final int WALK_ALL = 101;
    /**
     * all ride state data for searching
     */
    public static final int RIDE_ALL = 102;
    /**
     * all fitness state data for searching
     */
    public static final int FITNESS_ALL = 103;
    /**
     * all swim state data for searching
     */
    public static final int SWIM_ALL = 104;
    /**
     * all ball game state data for searching 球类运动
     */
    public static final int BALL_ALL = 105;
    /**
     * all outdoor sports state data for searching 户外运动
     */
    public static final int OUTDOOR_ALL = 106;
    /**
     * all yoga state data for searching 瑜伽
     */
    public static final int YOGA_ALL = 107;
    /**
     * all dance state data for searching 舞蹈
     */
    public static final int DANCE_ALL = 108;
    /**
     * all snow sports state data for searching 冰雪运动
     */
    public static final int SNOW_ALL = 109;
    /**
     * all water sports state data for searching 水上运动
     */
    public static final int WATER_ALL = 110;
    /**
     * all leisure sports state data for searching 休闲运动
     */
    public static final int LEISURE_ALL = 111;
 
    /**
     * all game sports state data for searching 游戏记录
     */
    public static final int GAME_ALL = 112;
 
    /**
     * all custom sports state data for searching 自定义运动
     */
    public static final int CUSTOM_ALL = 113;
 
    /**
     * 体能测试类型
     */
    public static final int STAMINAL_TEST = 127;
//--------------------------------------------------------------健身---------------------------------------------------------------------------
    /**
     * 爆发力训练
     */
    public static final int EXPLOSIVE_TRAINING = 201;
    /**
     * 背部训练
     */
    public static final int BACK_TRAINING = 202;
    /**
     * 单杠
     */
    public static final int HORIZONTAL_BAR = 203;
    /**
     * 登山机
     */
    public static final int CLIMBER = 204;
    /**
     * 腹部训练
     */
    public static final int ABDOMINAL_TRAINING = 205;
    /**
     * 核心训练
     */
    public static final int CORE_TRAINING = 206;
    /**
     * 击剑
     */
    public static final int FENCING = 207;
    /**
     * 肩部训练
     */
    public static final int SHOULDER_TRAINING = 208;
    /**
     * 健身操
     */
    public static final int AEROBICS = 209;
    /**
     * 颈部训练
     */
    public static final int NECK_TRAINING = 210;
    /**
     * 力量训练
     */
    public static final int STRENGTH_TRAINING = 211;
    /**
     * 脸部训练
     */
    public static final int FACE_TRAINING = 212;
    /**
     * 灵敏性训练
     */
    public static final int AGILITY_TRAINING = 213;
    /**
     * 平衡性训练
     */
    public static final int BALANCE_TRAINING = 214;
    /**
     * 拳击
     */
    public static final int BOXING = 215;
    /**
     * 柔道
     */
    public static final int JUDO = 216;
    /**
     * 柔韧性训练
     */
    public static final int FLEXIBILITY_TRAINING = 217;
    /**
     * 上肢训练
     */
    public static final int UPPER_LIMB_TRAINING = 218;
    /**
     * 射击
     */
    public static final int SHOOTING = 219;
    /**
     * 射箭
     */
    public static final int ARCHERY = 220;
    /**
     * 双杠
     */
    public static final int PARALLEL_BARS = 221;
    /**
     * 踏步机
     */
    public static final int STEPPER = 222;
    /**
     * 跆拳道
     */
    public static final int TAEKWONDO = 223;
    /**
     * 太极
     */
    public static final int TAI_CHI = 224;
    /**
     * 体操
     */
    public static final int GYMNASTICS = 225;
    /**
     * 臀部训练
     */
    public static final int HIP_TRAINING = 226;
    /**
     * 武术
     */
    public static final int MARTIAL_ARTS = 227;
    /**
     * 下肢训练
     */
    public static final int LOWER_LIMB_TRAINING = 228;
    /**
     * 胸部训练
     */
    public static final int CHEST_TRAINING = 229;
    /**
     * 腰部训练
     */
    public static final int WAIST_TRAINING = 230;
  //--------------------------------------------------------------瑜伽---------------------------------------------------------------------------
    /**
     * 阿奴萨拉
     */
    public static final int ANUSARA = 301;
    /**
     * 阿斯汤加瑜伽
     */
    public static final int ASHTANGA_YOGA = 302;
    /**
     * 艾扬格瑜伽
     */
    public static final int IYENGAR_YOGA = 303;
    /**
     * 飞行瑜伽
     */
    public static final int FLY_YOGA = 304;
    /**
     * 哈他瑜伽
     */
    public static final int HATHA_YOGA = 305;
    /**
     * 空中瑜伽
     */
    public static final int AERIAL_YOGA = 306;
    /**
     * 理疗瑜伽
     */
    public static final int PHYSIOTHERAPY_YOGA = 307;
    /**
     * 流瑜伽
     */
    public static final int FLOW_YOGA = 308;
    /**
     * 冥想
     */
    public static final int MEDITATION = 309;
    /**
     * 内观流瑜伽
     */
    public static final int VIPASSANA_FLOW_YOGA = 310;
    /**
     * 普拉提
     */
    public static final int PILATES = 311;
    /**
     * 阴瑜伽
     */
    public static final int YIN_YOGA = 312;
    /**
     * 孕瑜伽
     */
    public static final int PREGNANCY_YOGA = 313;
 //--------------------------------------------------------------舞蹈---------------------------------------------------------------------------
    /**
     * 芭蕾舞
     */
    public static final int BALLET = 401;
    /**
     * 迪斯科
     */
    public static final int DISCO = 402;
    /**
     * 肚皮舞
     */
    public static final int BELLY_DANCE = 403;
    /**
     * 广场舞
     */
    public static final int SQUARE_DANCE = 404;
    /**
     * 华尔兹
     */
    public static final int WALTZ = 405;
    /**
     * 街舞
     */
    public static final int STREET_DANCE = 406;
    /**
     * 爵士舞
     */
    public static final int JAZZ = 407;
    /**
     * 拉丁舞
     */
    public static final int LATIN_DANCE = 408;
    /**
     * 探戈
     */
    public static final int TANGO = 409;
    /**
     * 踢踏舞
     */
    public static final int TAP_DANCE = 410;
//--------------------------------------------------------------球类运动---------------------------------------------------------------------------
    /**
     * 板球
     */
    public static final int CRICKET = 601;
    /**
     * 棒球
     */
    public static final int BASEBALL = 602;
    /**
     * 橄榄球
     */
    public static final int AMERICAN_FOOTBALL = 603;
    /**
     * 篮球
     */
    public static final int BASKETBALL = 604;
    /**
     * 垒球
     */
    public static final int SOFTBALL = 605;
    /**
     * 门球
     */
    public static final int CROQUET = 606;
    /**
     * 排球
     */
    public static final int VOLLEYBALL = 607;
    /**
     * 乒乓球
     */
    public static final int PINGPONG = 608;
    /**
     * 曲棍球
     */
    public static final int HOCKEY = 609;
    /**
     * 网球
     */
    public static final int TENNIS = 610;
    /**
     * 足球
     */
    public static final int FOOTBALL = 611;
//--------------------------------------------------------------冰雪运动---------------------------------------------------------------------------
    /**
     * 冰壶
     */
    public static final int CURLING = 701;
    /**
     * 冰球
     */
    public static final int PUCK = 702;
    /**
     * 冬季两项
     */
    public static final int BIATHLON = 703;
    /**
     * 滑冰
     */
    public static final int SKATE = 704;
    /**
     * 滑雪
     */
    public static final int SKI = 705;
    /**
     * 雪车
     */
    public static final int SNOW_CAR = 706;
    /**
     * 雪橇
     */
    public static final int SLED = 707;
 //--------------------------------------------------------------休闲运动---------------------------------------------------------------------------
    /**
     * 拔河
     */
    public static final int TUG_OF_WAR = 901;
    /**
     * 放风筝
     */
    public static final int FLY_A_KITE = 902;
    /**
     * 飞镖
     */
    public static final int DARTS = 903;
    /**
     * 飞盘
     */
    public static final int FRISBEE = 904;
    /**
     * 遛狗
     */
    public static final int WALK_THE_DOG = 905;
    /**
     * 骑马
     */
    public static final int HORSE_RIDING = 906;
    /**
     * 踢毽子
     */
    public static final int KICK_THE_SHUTTLECOCK = 907;
    /**
     * 跳绳
     */
    public static final int ROPE_SKIPPING = 908;

    /**
     * 操场跑
     */
    public static final int PLAYGROUND_RUN = 909;
//--------------------------------------------------------------定制专属运动---------------------------------------------------------------------------
    /**
     * 自定义户外运动
     */
    public static final int CUSTOM_OUTDOOR_SPORTS = 1001;
    /**
     * 自定义室内运动
     */
    public static final int CUSTOM_INDOOR_SPORTS = 1002;
    /**
     * 自定义水上运动
     */
    public static final int CUSTOM_WATER_SPORTS = 1003;
```

  