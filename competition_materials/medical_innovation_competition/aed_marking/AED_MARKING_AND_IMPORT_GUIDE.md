# 云南大学 AED 人工标记与导入说明

更新时间：2026-05-25

## 1. 你应该在哪里标记

短期推荐：

直接填写本文件夹里的：

`YNU_AED_MARKING_TEMPLATE.csv`

每一行代表一个 AED 点位。填完后我可以把 CSV 转成后端接口请求，导入到生命反射弧系统。

长期优化：

后续可以在 Web 总控台新增“添加 AED 点位”表单，直接从网页录入。但当前国赛时间紧，CSV 是最快、最稳、最好审阅的方式。

## 2. 字段说明

| 字段 | 是否必填 | 示例 | 说明 |
| --- | --- | --- | --- |
| siteId | 推荐填 | `ynu-aed-library-1f` | 点位唯一 ID，只用英文、数字、短横线 |
| name | 必填 | `云南大学图书馆一楼 AED` | 展示名称 |
| latitude | 必填 | `24.826xxx` | 纬度 |
| longitude | 必填 | `102.85xxxx` | 经度 |
| accuracyMeters | 可选 | `20` | 坐标精度估计 |
| label | 必填 | `呈贡校区图书馆一楼大厅` | 位置描述 |
| floor | 可选 | `1F` / `2F` / `B1` | 楼层 |
| source | 默认 | `manual` | 人工标记 |
| status | 必填 | `AVAILABLE` | 可选：`AVAILABLE`、`MAINTENANCE`、`UNAVAILABLE` |
| accessNotes | 推荐填 | `大厅服务台旁 AED 箱，取用时联系值班人员` | 取用说明 |

## 3. 如何获取经纬度

推荐方法：

1. 打开高德地图或百度地图网页版。
2. 搜索云南大学具体建筑。
3. 右键或使用“坐标拾取器”复制经纬度。
4. 如果 AED 在室内，坐标标建筑入口或最近可识别点，具体室内位置写到 `label` 和 `accessNotes`。

注意：

- 室内 AED 很难靠 GPS 精确定位，所以 `floor`、`label`、`accessNotes` 比经纬度更重要。
- 如果不确定真实位置，不要写成真实 AED。可以写“模拟 AED 点位”或“待核验 AED 点位”。
- 对外 PPT 使用时，建议标注“人工标记/待实地复核”。

## 4. 后端接口格式

生命反射弧后端已经支持 AED 点位写入：

```http
POST /api/aed-sites
Header: X-beta-Admin-Token: <演示管理员口令>
Content-Type: application/json
```

JSON 示例：

```json
{
  "siteId": "ynu-aed-library-1f",
  "name": "云南大学图书馆一楼 AED",
  "location": {
    "latitude": 24.826,
    "longitude": 102.85,
    "accuracyMeters": 20,
    "label": "呈贡校区图书馆一楼大厅",
    "floor": "1F",
    "source": "manual"
  },
  "status": "AVAILABLE",
  "accessNotes": "大厅服务台旁 AED 箱，按现场标识取用。"
}
```

## 5. 导入后的用途

导入后，AED 点位会用于：

- Web 总控台 AED 点位库展示。
- mobile 端“位置与 AED”展示。
- 角色调度中 AED 保障者距离评分。
- 事件证据包中的 `aed_sites.csv`。
- PPT 中“人工标记 AED 点位参与调度”的证据。

## 6. 推荐国赛口径

安全说法：

本项目当前使用人工标记的校园 AED 点位进行系统级模拟和预实验展示。由于 AED 设备位置可能存在维护、迁移或开放时间差异，真实部署前需要与学校后勤、安保或急救培训部门共同核验点位状态和取用流程。

不要说：

- 已接入全国真实 AED 数据库。
- AED 点位完全准确。
- 系统可保证找到最近可用 AED。

