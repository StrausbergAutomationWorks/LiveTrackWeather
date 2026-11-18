# Live Track Weather

[English](README.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Nederlands](README.nl.md) · **简体中文** · [Español](README.es.md) · [Italiano](README.it.md) · [Dansk](README.da.md) · [Kalaallisut](README.kl.md) · [所有语言](#语言)

**为 Home Assistant 提供天气警报、风暴、地震、洪水、野火、雷达和实时天气，
全部在一张地图上。** Live Track Weather 把美国国家气象局（National Weather
Service）的警报、飓风和台风、强风暴展望、地震、火山、河流洪水、风暴和降雪
报告、野火和烟雾数据、挪威气象局（MET Norway）的警报以及斯瓦尔巴的气象站
放到你的 Home Assistant 地图上，并为你的家、家人的手机和你的房车监视危险。

> **Live Track Weather 是 Live Track 的一个模块**。Live Track 是一组 Home
> Assistant 集成，把所有移动的东西以及它们穿越的天气画在同一张共享地图上：
> 飞机、船舶、火车，现在还有天气。可以单独安装，也可以和其他模块一起安装
> （[见下方列表](#live-track-的组成部分其他模块)）。

**状态：开发中，尚未发布。** 在首次发布之前，代码仓库保持私有。

StrausbergAutomationWorks 的原创作品。与美国国家气象局、NOAA、国家飓风中心
（National Hurricane Center）、风暴预测中心（Storm Prediction Center）、联合
台风警报中心（Joint Typhoon Warning Center）、NASA、美国地质调查局（US
Geological Survey）、EPA、MET Norway、KNMI 或 GeoNames 均无关联，也未获其
认可。

> ⚠ **这不是紧急警报系统。** 它显示的是公开数据，最快也会晚几分钟。对于
> 保护生命的警报，请使用手机的紧急警报、气象广播（在美国为 NOAA Weather
> Radio）和当地政府的信息，并服从疏散命令。

---

## 目录

1. [全部功能](#全部功能)
2. [Live Track 的组成部分：其他模块](#live-track-的组成部分其他模块)
3. [开始之前](#开始之前)
4. [安装步骤](#安装步骤)
5. [设置步骤](#设置步骤)
6. [解锁更多功能的免费密钥](#解锁更多功能的免费密钥)
7. [把地图放到仪表盘上](#把地图放到仪表盘上)
8. [在自动化中使用](#在自动化中使用)
9. [地图上的全部内容详解](#地图上的全部内容详解)
10. [你所在地点的全部内容详解](#你所在地点的全部内容详解)
11. [它创建的全部实体](#它创建的全部实体)
12. [它发送和下载的内容](#它发送和下载的内容)
13. [语言](#语言)
14. [致谢与许可](#致谢与许可)
15. [关键词](#关键词)

---

## 全部功能

### 地图上的内容，无需任何设置

| 内容 | 范围 | 来源 |
|---|---|---|
| **天气警报**：警告、监视、提示和声明，按气象局自己的颜色半透明填充 | 美国全境及其海岸和水域 | National Weather Service |
| **龙卷风、强雷暴、山洪等基于风暴的警告**，按其自身的多边形绘制 | 美国 | National Weather Service |
| **飓风、热带风暴、台风和气旋**：每个风暴一个标记，预报锥、预报路径、风场和过去路径 | 全世界 | 国家飓风中心；联合台风警报中心（经由 NASA EONET） |
| **今天的强天气展望**：强雷暴风险从 Marginal 到 High | 美国 | NOAA 风暴预测中心 |
| 过去 24 小时的**地震**：大地震和有感地震显示为标记，其余显示为小点，最强的显示震动等值线 | 全世界 | 美国地质调查局 |
| **警戒级别升高的火山**，按航空颜色代码显示 | 美国火山 | USGS 火山灾害计划 |
| **正在泛滥或预报将泛滥的河流**，轻度、中度或严重 | 美国河流和潮位站 | NOAA 国家水文预报服务 |
| **风暴报告**：龙卷风、漏斗云、冰雹、破坏性大风、洪水 | 美国 | NWS Local Storm Reports |
| **冬季报告**：降雪量、暴风雪、冰粒、冻雨和冰暴、极寒、雪崩、冰塞 | 美国 | NWS Local Storm Reports |
| **MET Norway 的天气警报**，与美国警报并列 | 挪威、其海域、斯瓦尔巴 | MET Norway |
| 56 个海区和 39 个沿海区域的**海洋预报**，点击阅读 | 从北海到北极 | MET Norway |
| 斯瓦尔巴**朗伊尔城的预报点**，点击查看预报 | 斯瓦尔巴 | MET Norway |
| **天气雷达**和**闪电**：为屏幕上的范围选择最清晰的雷达 | 全世界 | 由 Live Track 地图卡片绘制 |

### 你所在地点的内容，无需任何设置

"你的地点"是你的家，以及你选择监视的任何人员、手机、设备追踪器或区域。
每个地点都会获得（实体名称为英文）：

* **Alert at …**：当地点处于天气警报范围内、靠近强烈地震或处于正在喷发的
  火山的危险区内时打开。可直接用于自动化：开灯、给手机发送通知、关上
  车库门。
* **Forecast at …**：完整的天气预报，随地点移动而跟随，可用于仪表盘上的
  每张天气卡片。美国陆地上使用美国国家气象局的预报；其他所有地方以及所有
  水面上使用 MET Norway 的预报。
* **Wind at …**、**Wind gust at …**、**Wind direction at …** 和
  **Temperature at …**：最近的气象站测得的数据。起阵风时收起遮阳篷。
* **Elevation at …** 和 **Depth at …**：地面的海拔，以及船下的水深。

### 用你自己的免费密钥或账户启用

| 免费密钥或账户 | 增加的功能 |
|---|---|
| **NASA FIRMS** 地图密钥 | 你所在地点附近的野火警报；地图上的每个卫星火点探测 |
| **AirNow** API 密钥 | 你在美国的地点的野火烟雾和空气质量（PM2.5 AQI）警报；地图上的每个空气质量监测站 |
| **KNMI** API 密钥 | 荷兰上空更清晰的雷达 |
| **GeoNames** 用户名 | 美国以外的实测风和温度，来自最近的机场；水深的海域名称以及水面或陆地判断 |
| **MET Norway Frost** 客户端 ID | 地图上斯瓦尔巴和扬马延岛的每个气象站；你在挪威和斯瓦尔巴的地点的实测风和温度 |

每一项都只需几分钟即可获得：[见下方步骤](#解锁更多功能的免费密钥)。

---

## Live Track 的组成部分：其他模块

Live Track 是一组 Home Assistant 集成，每种移动的东西对应一个，全部画在同
一张地图卡片上。每个集成都能单独使用；合在一起就构成一幅实时画面。它们共用
地图卡片和一个 Python 库
（[saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)），
因此多安装一个集成，不会对另一个集成已在读取的数据源增加任何请求。

| 模块 | 它在地图上显示什么 | 状态 |
|---|---|---|
| [Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft) | 通过 ADS-B 显示头顶上的飞机，含航线和机型图标 | 已发布 |
| [Live Track Ships](https://github.com/StrausbergAutomationWorks/LiveTrackShips) | 通过 AIS 显示附近或任何地方的船舶 | 已发布 |
| [Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail) | 北美、欧洲和澳大利亚的通勤列车 | 已发布 |
| [Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail) | 北美、欧洲和澳大利亚的城际和长途列车 | 已发布 |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | 移民和联邦执法机构的飞机和船只，来自公开名单 | 已发布 |
| **Live Track Weather** | 天气、风暴和自然灾害（本模块） | 开发中 |
| Live Track Stations | 每个车站的发车时刻表和"该出发了"提醒 | 计划中 |
| Live Track Satellites | 从头顶经过的卫星 | 计划中 |
| Live Track Freight Trains | 铁路公司公布的货运和工程列车 | 计划中 |
| Live Track Transit | 城市公交、有轨电车、渡轮和地铁 | 计划中 |
| Live Track Intercity Buses | 城际和区域长途客车 | 计划中 |
| Live Track Commuter Buses | 通勤巴士 | 计划中 |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | 每个模块都在其上绘制的共享地图卡片 | 已发布，随每个模块安装 |

全部免费且开源。没有任何功能只留给赞助者。

---

## 开始之前

* **Home Assistant** 2025.1 或更高版本（在 2026.11 上开发和测试）。
* 你的 Home Assistant 中装有 **Marketplace**（HACS），便于安装和更新。没有
  它也可以手动复制文件。
* Home Assistant 能**访问互联网**：所有数据都来自公共气象服务。
* **可选：Marketplace 中的 auto-entities**，用于把风暴、地震和气象站的标记
  放到地图上（见[把地图放到仪表盘上](#把地图放到仪表盘上)）。警报和区域
  形状不需要它也会显示。
* 基本功能无需付费，也无需账户。上面的免费密钥是可选的。

---

## 安装步骤

### 通过 Marketplace（推荐）

Live Track Weather 还不在 Marketplace 的目录中。通过链接添加：

1. 在 Home Assistant 中打开 **设置 → Marketplace**（HACS）。
2. 选择 **从链接添加**（或三点菜单 → **自定义存储库**）。
3. 输入 `StrausbergAutomationWorks/LiveTrackWeather`。如果询问类型，选择
   **集成**。
4. 在列表中找到 **Live Track Weather**，选择 **下载** 或 **安装**。
5. **重启 Home Assistant**：**设置 → 系统 → 修复** 会提供重启，或者使用
   **设置 → 系统 → 重新启动**。

### 手动安装

1. 下载[最新版本](https://github.com/StrausbergAutomationWorks/LiveTrackWeather/releases/latest)
   的源代码。
2. 把其中的 `custom_components/live_track_weather` 文件夹复制到 Home
   Assistant 配置文件夹中的 `custom_components` 文件夹（如果没有
   `custom_components`，请创建）。
3. 重启 Home Assistant。

---

## 设置步骤

1. 打开 **设置 → 设备与服务**。
2. 选择 **添加集成**（右下角），搜索 **Live Track Weather**。
3. 选择 **提交**。无需输入任何内容：一个 Live Track Weather 覆盖全世界。

就这样。警报、风暴、地震、火山、洪水、风暴报告和 MET Norway 的警报会在几分
钟内开始出现，你的家也开始被监视：**Alert at Home**、**Forecast at Home**、
**Wind at Home**、**Temperature at Home**、**Elevation at Home** 和
**Depth at Home**。

### 更改监视内容：选项

打开 **设置 → 设备与服务 → Live Track Weather → 配置**（齿轮图标）。每个
选项的通俗说明：

| 选项 | 作用 | 默认值 |
|---|---|---|
| **轮询间隔秒数** | 获取美国警报列表的频率，60 至 900 秒 | 180 |
| **监视家** | 你的家获得"… at Home"传感器和天气预报；关闭即移除 | 开 |
| **同时监视这些人员、设备追踪器或区域** | 每一项都获得自己的"Alert at …"、"Forecast at …"、风、温度、海拔和水深，并随其移动而跟随。可选择家人的手机、房车的追踪器、度假屋的区域 | 无 |
| **使地点打开的警报** | 任何警报（包括提示和声明），或只有中等、严重或极端的警报。所有警报仍会列在传感器中 | 任何警报 |
| **实测风和温度仅取自机场气象站** | 关：最近的任何类型的气象站（常常离露营地更近）；开：仅机场 | 关 |
| **NASA FIRMS MAP_KEY** | 火灾警报和火点探测（见[免费密钥](#解锁更多功能的免费密钥)） | 空 |
| **火灾计入的距离范围** | 火灾距离多近才使地点打开，5 至 150 公里 | 50 公里 |
| **AirNow API 密钥** | 烟雾警报和空气质量站点 | 空 |
| **烟雾计入的 PM2.5 AQI 下限** | 使地点打开的空气质量指数 | 90 |
| **地图上的火点探测和空气质量站点** | 绘制哪些区域：本土 48 州和夏威夷、阿拉斯加、加拿大、全世界（仅火点） | 无 |
| **地图点图层上的最小地震** | 略去低于某个震级的小地震点；标记保留 | 空：所有地震 |
| **KNMI API 密钥** | 荷兰上空更清晰的雷达 | 空 |
| **GeoNames 用户名** | 美国以外的天气、海域名称 | 空 |
| **MET Norway Frost 客户端 ID** | 斯瓦尔巴和扬马延岛的气象站；挪威的实测天气 | 空 |

每个密钥在输入时检查一次，如果不能用会提示你。某个字段留空即关闭对应的
功能。

---

## 解锁更多功能的免费密钥

这些都是免费且个人的：每个安装 Live Track Weather 的人都要申请自己的。把每个
密钥粘贴到 **设置 → 设备与服务 → Live Track Weather → 配置** 中。

### NASA FIRMS（野火）

1. 打开 <https://firms.modaps.eosdis.nasa.gov/api/map_key/>。
2. 输入你的电子邮件地址并申请 **MAP_KEY**。它会通过电子邮件发来。
3. 把它粘贴到 **NASA FIRMS MAP_KEY**，如果 50 公里不合适，设置
   **火灾计入的距离范围**。
4. 要在地图上看到火点，还要在 **地图上的火点探测和空气质量站点** 下勾选一个
   区域。

### AirNow（烟雾和空气质量，美国）

1. 打开 <https://docs.airnowapi.org/>，选择 **Request an AirNow API
   Account**。
2. 确认电子邮件，登录，并从账户页面复制你的 **API key**。
3. 把它粘贴到 **AirNow API 密钥**。

### KNMI（荷兰上空的雷达）

1. 在 KNMI 数据平台注册，<https://developer.dataplatform.knmi.nl/>。
2. 申请 **WMS** API 的密钥。（Open Data API 的密钥在这里不可用。）
3. 把它粘贴到 **KNMI API 密钥**。之后地图在荷兰上空使用 KNMI 的雷达；没有它
   则使用 RainViewer 的。

### GeoNames（美国以外的天气）

1. 在 <https://www.geonames.org/login> 创建一个免费账户。
2. 打开 GeoNames 发来的确认邮件并确认。
3. 登录，打开账户页面，**启用免费网络服务**。
4. 在 **GeoNames 用户名** 中输入你的**用户名**（不是密码）。

### MET Norway Frost（斯瓦尔巴气象站、挪威的天气）

1. 打开 <https://frost.met.no/auth/requestCredentials.html>。
2. 输入你的电子邮件地址。你会得到一个**客户端 ID** 和一个客户端密钥。
3. 把**客户端 ID** 粘贴到 **MET Norway Frost 客户端 ID**。不需要客户端
   密钥。

---

## 把地图放到仪表盘上

地图是 [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard)，
每个 Live Track 模块都在这张卡片上绘制。**它随 Live Track Weather 一起安装**：
无需下载，无需复制到 `www`，无需添加资源。

1. 打开一个仪表盘，选择铅笔图标（**编辑仪表盘**），然后选择 **添加卡片**。
2. 滚动到底部，选择 **手动**。
3. 粘贴以下内容，然后选择 **保存**：

```yaml
type: custom:auto-entities
card:
  type: custom:live-track-map-card
filter:
  include:
    - domain: geo_location
      attributes:
        source: live_track_weather
```

天气警报、强天气展望、MET Norway 的区域、风暴的预报锥和路径、地震的震动
等值线以及各个点图层会自动出现。标记（风暴、地震、火山、河流水位站、朗伊尔
城的预报和斯瓦尔巴的气象站）通过上面的过滤器显示，这需要 Marketplace 中的
[auto-entities](https://github.com/thomasloven/lovelace-auto-entities)。如果
还安装了其他 Live Track 模块，为它们的每个来源再添加一个
`- domain: geo_location` 过滤器（`live_track_aircraft`、`live_track_ships`
等等）。

**地图上：**

* 右上角的**图层控件**为每个图层提供一个复选框：美国警报、强天气展望、热带
  气旋、MET Norway 的警报和海洋预报、地震、地震震动、风暴报告、冬季报告、
  火点探测、空气质量站点、天气雷达、雷达动画、闪电和云。每位查看者的选择
  保存在各自的浏览器中。
* **点击**标记、区域、线条或点即可查看详情。
* **过滤卡片**（`custom:live-track-map-filter-card`）可以隐藏斯瓦尔巴的
  气象站，名称为 **Observed weather (MET Norway)**。
* 每个数据源的署名会在显示其数据时出现在地图的署名行中。

如果你的仪表盘资源是在 YAML 中设置的（`lovelace: resource_mode: yaml`），
就无法为你自动注册：此时 **修复** 中会有一条问题，给出需要添加的确切行。任何
其他显示 `geo_location` 实体的地图卡片都会显示这些标记，但不会显示警报、
区域或点。

---

## 在自动化中使用

一切都是普通的 Home Assistant 实体，因此自动化编辑器可以直接使用，无需
编写代码。

**家处于警报范围内时给手机发送通知：**

1. **设置 → 自动化与场景 → 创建自动化 → 创建新的自动化**。
2. **当**：*实体 → 状态*，实体 **Alert at Home**，变为 **不安全**（开）。
3. **则执行**：*通知 → 通过 mobile_app_… 发送通知*，消息例如
   `家中天气警报：{{ state_attr('binary_sensor.live_track_weather_alert_at_home', 'highest') }}`。
4. 保存。

**起阵风时收起遮阳篷：** *当* **Wind gust at Home** 超过 50 公里/小时（或
30 英里/小时）时，*则*关闭遮阳篷的卷帘。

**其他想法：** 当 **Severe weather outlook** 达到 3（Enhanced）时让一盏灯
闪烁；当 **Alert at Camper** 因 50 公里内的野火而打开时提醒房车的主人；当
**Temperature at Cabin** 降到冰点以下时发送通知；船在海上时在天气卡片上显示
**Forecast at Boat**。

---

## 地图上的全部内容详解

### 美国天气警报

美国国家气象局的每一条生效警报：县、陆地区域、海洋、近海和火险天气区域的
警告、监视、提示和声明，按气象局为每种事件规定的颜色半透明填充（警报重叠
处取优先级最高的）。龙卷风、强雷暴和山洪等基于风暴的警告按其自身的多边形
绘制，而不是整个县。无需设置位置：地图显示屏幕上的范围。区域轮廓（11,651
个，简化到约 500 米，约 3.6 MB）随每个版本一起发布，每个浏览器每个版本下载
一次。

**传感器 `US alerts`**：生效警报的数量；其属性包含地图绘制的列表
（`zones`、`polygons`、`styles`、`updated`、`shapes_url`），这些属性几乎每次
轮询都会变化，不会记录在历史中。

### 热带气旋：飓风、台风、气旋

全世界每一个活跃的热带气旋，每个风暴一个标记，标注其名称，按等级着色：热带
低压蓝色，热带风暴青色，1 至 5 级依次为金色、橙色、深橙色、红色和品红色，
后热带气旋灰色。鼠标悬停可查看其类别、风速、气压和移动情况。

* **国家飓风中心**的风暴（大西洋、东太平洋和中太平洋）：预报锥（蓝色）、
  预报路径（红色）、当前 34、50 和 64 节的风圈（黄色、橙色、红色）和过去
  路径（黑色）。
* **所有其他海域**，来自联合台风警报中心，经由 NASA 的 EONET：标记和过去
  路径。最后一次定位超过 24 小时的风暴不会显示。

标记为 `geo_location.storm_<id>`（`geo_location.storm_ep222026`），属性有
`storm_class`、`storm_category`（TD、TS、H1-H5、PT）、`max_wind_kmh`、
`pressure_hpa`、`course_deg`、`speed_kmh`、`last_seen`、`advisory_number`
和 `storm_source`。它们随风暴出现和消失，没有唯一 ID，因此无法在界面中重命名。
**传感器 `Tropical cyclones`**：风暴的数量。

### 强天气展望

风暴预测中心第 1 天的分类展望：今天可能出现强雷暴的地方，从 1 Marginal、
2 Slight、3 Enhanced、4 Moderate 到 5 High，使用该中心自己的颜色，绘制在
警报下方。**传感器 `Severe weather outlook`**：今天美国任何地方的最高风险，
0 至 5，会被记录，以便驱动自动化；属性 `risk`、`issued`、`valid_from`、
`valid_to`。一般雷暴区域不绘制。

### 地震

美国地质调查局列出的过去 24 小时内全世界的每次地震（每天约 240 次）：

* 4.5 级及以上的地震以及有人报告有感的地震显示为**标记**，标注震级
  （`geo_location.quake_<USGS id>`）。点击可查看时间、深度、有感报告、最强
  震动、PAGER 警报级别和 USGS 的事件页面。"海啸标志"不是警报；海啸警报
  来自 NOAA（tsunami.gov）。
* 其他每次地震显示为**小点**（采石爆破和爆炸为灰色），位于单独的图层：
  **传感器 `Earthquakes`**。选项 **地图点图层上的最小地震** 可略去小地震。
* 当天最大地震（6 级及以上或强烈震动，最多五个）的**震动等值线**（USGS
  ShakeMap）：**传感器 `Earthquake shaking`**。

### 警戒级别升高的火山

美国每座警戒级别为 Advisory 或航空颜色代码为 Yellow 及以上的火山，以其颜色
代码显示为标记，标注其名称（`geo_location.volcano_<number>`）。点击可查看警戒
级别、颜色代码、开始时间、观测站的概要以及通告和火山页面的链接。

### 正在泛滥或预报将泛滥的河流

美国每个**当前处于轻度洪水或更严重**、或预报将达到该程度的河流或潮位站，
按气象局的洪水颜色标注 Minor、Moderate 或 Major
（`geo_location.river_<gauge id>`）。**深色圆环表示当前正在泛滥**；没有圆环
则是预报。点击可查看当前水位、预报水位、洪水水位、流量和水位站页面。⚠ 少数
水位站的洪水水位看起来像占位值，因此显示为 Major（北达科他州的 Devils Lake）。

### 风暴报告

过去 24 小时内关于龙卷风或水龙卷、漏斗云、冰雹、雷暴大风或损坏、山洪或洪水
的每一份 NWS Local Storm Report：龙卷风红色，大风蓝色，冰雹绿色，洪水青色。
重要报告（任何龙卷风、2 英寸或更大的冰雹、65 节或更强的风）更大，并带深色
圆环。报告随时间变淡：一小时以内、1 至 6 小时、6 至 24 小时。点击可查看
类型、大小或速度、地点、时间、NWS 办公室和备注。**传感器 `Storm reports`**：
点的数量。⚠ 这些是人们提交的原始报告，尚未经过气象局核实，可能需要 30 分钟
才会出现。

### 冬季报告

来自同一批报告，位于风暴报告下方的单独图层：降雪、大雪和雪飑（石板蓝）、
暴风雪（橙红）、冰粒（兰花紫）、冻雨、冻毛毛雨和冰暴（深品红）、冰雪损坏
（灰色）、极寒和风寒（蓝色）、雪崩（棕色）和冰塞（深青色），每个都有一个细的
深色圆环。重要报告（12 英寸降雪、半英寸冰粒、四分之一英寸积冰、任何冰暴）
更大。点击可查看以英寸和厘米或毫米表示的数量，或以 °F 和 °C 表示的温度。
**传感器 `Winter reports`**。⚠ 一场大风暴会带来数千份报告；两份报告会重叠的
地方只绘制一份，所以请放大查看。

### MET Norway：警报、海洋预报、朗伊尔城预报

* 挪威陆地、海岸和海域以及直到北极的海域的**警报**，使用 MET 的黄色、橙色
  或红色，与美国警报并列。点击可查看预计情况、后果、建议和时间（英文）。
  **传感器 `MET Norway warnings`**。
* 56 个海区和 39 个沿海区域（包括斯瓦尔巴的）的**海洋预报**，绘制在警报
  下方。点击可查看其预报以及任何大风、海冰或极地低压警报。
  **传感器 `MET Norway marine forecasts`**。
* **朗伊尔城的预报点**，标注温度；点击可查看一天内每六小时的预报
  （`geo_location.met_forecast_longyearbyen`）。

### 斯瓦尔巴和扬马延岛的实测天气（Frost 客户端 ID）

斯瓦尔巴、熊岛、霍彭岛和扬马延岛上温度和风的数据都不超过两小时的每个气象站
（约 30 个）显示为一个青绿色圆点，标注温度（斯瓦尔巴机场为
`geo_location.frost_sn99840`，依此类推）。点击可查看温度、风速和风向、过去
一小时的最大阵风、湿度、气压、积雪深度和时间。只报告温度的气象站不绘制；
相距不到 1 公里的两个气象站只绘制一个。Frost 标记为非常不确定或错误的值不会
使用；目前只经过自动检查的值（通常是 MET 最新一小时的数据）会显示，弹出框
会注明"Automatic check only"。

### 野火和空气质量（FIRMS 和 AirNow 密钥）

在 **地图上的火点探测和空气质量站点** 下选择区域：

* **火点探测**（需要 FIRMS 密钥）：过去 24 小时的每个卫星火点探测（NOAA-20
  和 NOAA-21 VIIRS），显示为红色小点。NASA 已分类的工厂、炼油厂、火炬和其他
  固定热源会被排除。点击可查看时间、哪颗卫星、火辐射功率和 NASA 的置信度。
  **传感器 `Fire detections`**。
* **空气质量站点**（需要 AirNow 密钥；美国和加拿大）：每个细颗粒物
  （PM2.5）监测站，按 EPA 的颜色根据其 AQI 着色，每小时更新。
  **传感器 `Air quality sites`**。

### 天气雷达、闪电和云

由地图卡片本身绘制，无需设置：一个雷达图层，为屏幕上的范围选择最清晰的来源
（北美为 RainViewer、NOAA nowCOAST 和加拿大的 GeoMet；欧洲为芬兰的 FMI 和
德国的 DWD；日本的 JMA；荷兰上空用你的密钥使用 KNMI），以及雷达动画、来自
nowCOAST 的闪电和来自 GOES 与 EUMETSAT 卫星的云图。

---

## 你所在地点的全部内容详解

### Alert at …

**`Alert at Home`**（`binary_sensor.live_track_weather_alert_at_home`，设备
类别 *safety*：开表示不安全），以及你监视的每个人员、追踪器或区域各一个。
当地点满足以下条件时打开：

* 处于**美国天气警报**或 **MET Norway 警报**范围内（按气象局自己的规则：
  龙卷风或洪水警告只在其多边形内计入，而不是整个县；区域来自气象局本身，
  因此海岸上或县界上的地点也能得到正确的结果）；
* 过去 24 小时内靠近强烈**地震**：4 级在 50 公里内，5 级在 150 公里内，6 级
  在 300 公里内，7 级在 600 公里内；
* 处于警戒级别为 Watch 或 Orange 及以上的**火山**的危险区内（USGS 的国家
  火山威胁图层，随集成一起提供）；
* 有 FIRMS 密钥时，靠近**野火**（在你设置的距离内，默认 50 公里；探测结果
  在卫星过境后 2 至 4 小时到达 Home Assistant）；
* 有 AirNow 密钥时，处于**野火烟雾**中：50 英里内最近的 PM2.5 监测站达到或
  超过你设置的 AQI，默认 90（美国的地点）。

属性：`alerts`（该地点的每条警报，最严重的在前，含 `event`、`severity`、
`headline`、`onset`、`ends`、`source` 和一个链接）、`highest`、`zones`；有
密钥时还有 `fires_near`、`nearest_fire_km`、`pm25_aqi`、`pm25_site` 等。移动
的追踪器移动超过 1 公里后会重新查询其区域。NASA 建议不要仅凭火点探测在现场
做出决定：请服从疏散命令。

### Forecast at …

**`Forecast at Home`**（`weather.live_track_weather_forecast_at_home`），以及
每个被监视地点各一个，可用于每张天气卡片和 `weather.get_forecasts`：每日、
白天和夜间、以及逐小时预报。

* **在美国陆地上**：美国国家气象局为该地点 2.5 公里网格提供的预报，七天的
  白天和夜间预报及文字说明，以及六天半的逐小时预报。
* **其他所有地方以及所有水面上**：MET Norway 的预报，约两天半逐小时，之后
  每六小时一次，直到约十天。

地点移动时会切换来源（船驶离港口，房车驶入加拿大）。

### Wind at …、Wind gust at …、Wind direction at …、Temperature at …

最近的气象站为每个被监视地点测得的数据
（`sensor.live_track_weather_wind_at_home` 等）。

* **在美国**：任何网络中最近的美国国家气象局气象站（机场、火险天气站和
  公路气象站、志愿者气象站），或按选项仅用机场；某个站没有近期数据时，使用
  下一个，最多三个。
* **在挪威和斯瓦尔巴**，有 Frost 客户端 ID 时：MET Norway 自己的气象站中
  最近的一个（在挪威各地 22 个地点测得：距离 0.4 至 11 公里）。阵风为过去
  一小时的最大值。
* **其他地方**，有 GeoNames 用户名时：最近机场约 100 公里内的天气报告
  （METAR）。
* 当没有不超过两小时的报告包含其数值时，传感器为**不可用**。没有报告阵风时，
  阵风为未知。属性：`station`、`station_name`、`provider`、`distance_km`、
  `observed`、`age_min`。

### Elevation at … 和 Depth at …

**`Elevation at Home`** 和 **`Depth at Home`**，以及每个被监视地点各一个，
在启动时和移动超过 500 米后检查。

* **海拔**取自第一个有数值的来源：USGS 3DEP（美国及边境地区，精确到 1 米）、
  加拿大自然资源部（Natural Resources Canada）、Kartverket（挪威本土），然后
  是 Mapzen 的 Terrain Tiles（世界其他地方）。
* **在水面上**时，海拔是水面高度，**Depth** 是该地点下方的水深，在挪威取自
  Kartverket，其他地方取自 NOAA NCEI（包括五大湖）；在陆地上为未知。有
  GeoNames 用户名时，`sea` 给出海域名称。
* ⚠ 已知限制：斯瓦尔巴的海拔约高 35 米（没有找到更好的来源）；河流、港口和
  水库没有水深；在没有 GeoNames 的浅海中，海拔是海底；只能通过 terrain tiles
  获取的低于海平面的湖泊显示为 0。

---

## 它创建的全部实体

| 实体 | 是什么 |
|---|---|
| `sensor.live_track_weather_us_alerts` | 美国生效警报的数量；地图绘制的列表 |
| `sensor.live_track_weather_tropical_cyclones` | 热带气旋的数量 |
| `sensor.live_track_weather_severe_weather_outlook` | 今天最高的强风暴风险，0 至 5 |
| `sensor.live_track_weather_met_norway_warnings` | 已绘制的 MET Norway 警报 |
| `sensor.live_track_weather_met_norway_marine_forecasts` | MET Norway 海洋预报区域 |
| `sensor.live_track_weather_earthquakes` | 地图上的地震点 |
| `sensor.live_track_weather_earthquake_shaking` | 已绘制的 ShakeMap |
| `sensor.live_track_weather_storm_reports` | 已绘制的风暴报告 |
| `sensor.live_track_weather_winter_reports` | 已绘制的冬季报告 |
| `sensor.live_track_weather_fire_detections` | 火点探测（需 FIRMS 密钥和一个区域） |
| `sensor.live_track_weather_air_quality_sites` | 空气质量站点（需 AirNow 密钥和一个区域） |
| `sensor.live_track_weather_knmi_radar` | 最新的 KNMI 雷达帧（需 KNMI 密钥） |
| `geo_location.storm_…`、`quake_…`、`volcano_…`、`river_…`、`met_forecast_…`、`frost_…` | 各种标记；随事件出现和消失，没有唯一 ID |
| `binary_sensor.live_track_weather_alert_at_home` | Alert at Home（每个被监视地点各一个） |
| `weather.live_track_weather_forecast_at_home` | Forecast at Home（每个被监视地点各一个） |
| `sensor.live_track_weather_wind_at_home`、`…_wind_gust_at_home`、`…_wind_direction_at_home`、`…_temperature_at_home` | 家中的实测天气（以及每个地点的） |
| `sensor.live_track_weather_elevation_at_home`、`…_depth_at_home` | 家中的海拔和水深（以及每个地点的） |

每次轮询都会变化的属性（列表、形状、弹出框）不会写入 Home Assistant 的历史
记录，因此你的数据库不会因它们而增长。

---

## 它发送和下载的内容

**关于你的位置。** 你的家和每个被监视地点的位置会四舍五入到约 11 米，只发送
给需要它的服务：发送给美国国家气象局以获取该地点的区域、预报网格和气象站；
在美国预报范围以外，发送给 MET Norway 获取其预报；发送给 USGS（以及在 USGS
没有数据的地方，发送给加拿大自然资源部、Kartverket 和 NOAA NCEI）获取海拔和
水深，在启动时和移动超过 500 米后各一次；有你的密钥时，发送给 NASA FIRMS
（地点周围的一个矩形）、AirNow、GeoNames 和 MET Norway 的 Frost。关闭
**监视家** 并且不监视其他任何东西，就不会发送任何位置。不会向任何地方发送
关于你的其他信息。

**数据量。** 美国警报列表每 3 分钟约 100 KB（可调）；其他服务在允许的情况下
只请求有变化的文件：飓风公报每 5 分钟，EONET 每 30 分钟，强天气展望每 5 分钟，
MET Norway 的警报每 5 分钟，海洋预报每 15-30 分钟，点预报每 30 分钟（每次都
按 MET 的要求随机延后一分钟，被拒绝后 30 分钟内不再请求）；USGS 地震每 5 分钟
（约 170 KB），火山每 10 分钟，河流每 30 分钟，风暴报告每 10 分钟；Frost 每 10
分钟（约 80 KB）；GeoNames 控制在其每天 10,000 免费点数的一半以内；KNMI 每小时
最多约 24 次请求，而且只在有地图显示它时。出错后，每个服务都会被搁置一段时间
再重新请求。

---

## 语言

本 README：[English](README.md)、[Deutsch](README.de.md)、
[Français](README.fr.md)、[Nederlands](README.nl.md)、**简体中文**、
[Español](README.es.md)、[Italiano](README.it.md)、[Dansk](README.da.md) 和
[Kalaallisut](README.kl.md)（一份简短的草稿；在母语者审阅之前，以丹麦语页面
为准）。每份翻译的 README 都是完整的。

当你的 Home Assistant 语言是以下之一时，设置对话框和选项会以该语言显示：
English、Dansk、Deutsch、Español、Français、Gaeilge、Íslenska、Italiano、
Nederlands、Norsk Bokmål、Polski、Português、Português (BR)、Suomi、Svenska
和简体中文。其他语言显示英文。实体名称（**Alert at Home** 等）和地图卡片的
标签在所有语言中都是英文。

发现翻译有误，或需要其他语言？请在
<https://github.com/StrausbergAutomationWorks/LiveTrackWeather/issues> 告诉我们。

---

## 致谢与许可

* 美国国家气象局、国家飓风中心、风暴预测中心、国家水文预报服务（National
  Water Prediction Service）、联合台风警报中心、NASA 和美国地质调查局都是美国
  政府机构；它们的数据是美国政府作品。AirNow 数据为初步数据，未经核实（美国
  EPA 及合作伙伴）。
* **MET Norway**：数据采用 Norwegian Licence for Open Government Data (NLOD)
  2.0 和 Creative Commons Attribution 4.0 许可；Frost 的观测数据采用 Creative
  Commons Attribution 3.0 Norway 许可。本集成对区域做了取整，对警报重新着色，
  并换算了单位。
* **KNMI**：雷达采用 Creative Commons Attribution 4.0 许可，裁剪并缩放为地图
  瓦片。
* **GeoNames**：METAR 报告和海域名称采用 Creative Commons Attribution 4.0
  许可。
* **海拔**：加拿大自然资源部的 CDEM，Open Government Licence - Canada；
  Kartverket，Creative Commons Attribution 4.0；NOAA NCEI，美国政府。
  **Terrain Tiles**：Mapzen，以及 Mapzen 的 Joerd 署名（`tilezen/joerd`、
  `docs/attribution.md`）中列出的来源，原文照录如下：ArcticDEM terrain data
  DEM(s) were created from DigitalGlobe, Inc., imagery and funded under
  National Science Foundation awards 1043681, 1559691, and 1542736; Australia
  terrain data © Commonwealth of Australia (Geoscience Australia) 2017; Austria
  terrain data © offene Daten Österreichs – Digitales Geländemodell (DGM)
  Österreich; Canada terrain data contains information licensed under the Open
  Government Licence – Canada; Europe terrain data produced using Copernicus
  data and information funded by the European Union - EU-DEM layers; Global
  ETOPO1 terrain data U.S. National Oceanic and Atmospheric Administration;
  Mexico terrain data source: INEGI, Continental relief, 2016; New Zealand
  terrain data Copyright 2011 Crown copyright (c) Land Information New Zealand
  and the New Zealand Government (All rights reserved); Norway terrain data ©
  Kartverket; United Kingdom terrain data © Environment Agency copyright and/or
  database right 2015. All rights reserved; United States 3DEP (formerly NED)
  and global GMTED2010 and SRTM terrain data courtesy of the U.S. Geological
  Survey.
* **火山危险区**：USGS National Volcanic Threat Layer（2024，CC0）。

上述机构均未制作或认可本集成。

**代码**：MIT，见 [LICENSE](LICENSE)。

**开发者：** `tools/build_shapes.py` 根据 NWS 的 shapefile
（<https://www.weather.gov/gis/>）重建警报区域文件，`tools/build_colours.py`
根据 NWS 的灾害地图页面重建颜色表；测试用
`python -m unittest discover -s tests` 运行。

---

## 关键词

Home Assistant 天气 · Home Assistant 天气警报 · NWS 警报 · 美国国家气象局 ·
天气警报地图 · 龙卷风警告 · 强雷暴警告 · 山洪警告 · 冬季风暴警告 · 飓风追踪 ·
热带风暴 · 台风追踪 · 气旋 · 飓风预报锥 · NHC · JTWC · SPC 展望 · 强天气展望 ·
地震地图 · 地震警报 · USGS 地震 · ShakeMap · 火山警报 · 河流洪水地图 · 水位站 ·
NWPS · 风暴报告 · 冰雹 · 降雪量 · 暴风雪 · 冰暴 · 野火地图 · 野火警报 · 火点
探测 · NASA FIRMS · VIIRS · 烟雾警报 · 空气质量 · AQI · PM2.5 · AirNow · 天气
雷达 · 降雨雷达 · 闪电地图 · MET Norway · yr · 斯瓦尔巴天气 · 朗伊尔城 ·
扬马延岛 · Frost API · 海洋预报 · KNMI 雷达 · GeoNames · METAR · 气象站 · 阵风
传感器 · 温度传感器 · 设备追踪器天气预报 · 房车天气 · 船舶天气 · 海拔传感器 ·
水深 · geo_location · binary_sensor · weather 实体 · 地图卡片 · Lovelace ·
HACS · Marketplace · Live Track · LiveTrack · StrausbergAutomationWorks
