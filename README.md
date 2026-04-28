# 新一好喝 Skill

`xinyi-drink` 是新一好喝咖啡茶饮Skill。安装后，你的 AI 助手可以帮你领 **Skill用户大礼包**、查门店、查菜单，并结合天气和可选订单历史推荐茶饮与咖啡。

## 这个 Skill 能做什么

| 能力 | 高质量问法 | 说明 |
| --- | --- | --- |
| 领取Skill用户大礼包 | “帮我领取新一Skill福利。” | 查询小程序绑定状态并领取礼包 |
| 分析历史数据 | “我买过多少杯？” “帮我分析我的口味偏好。” | 需要提供小程序绑定手机号 |
| 查询门店 | “新一咖啡有哪些门店？” “望京店目前有多少杯待做，等待时间多久？” | 展示门店地址、电话、设施、当前制作杯数和等待情况 |
| 查询菜单商品 | “某某饮品热量多少？” “有哪些不太甜的果茶？” | 查询商品、价格、热量、糖度、温度和配料 |
| 推荐饮品 | “给我推荐一杯适合当下午茶的饮品。” | 结合天气、商品、门店和可选订单历史推荐 |

## Skill用户大礼包

用户发送微信小程序【新一咖啡】绑定的手机号后，Skill 可以帮用户领取Skill用户大礼包。

礼包内容：

- 小龙虾贴纸
- Skill用户身份标识
- Skill用户专享赠饮券

活动规则：

- 小龙虾贴纸：到任意门店对暗号【小龙虾】领取，先到先得
- Skill用户专享赠饮券：（前100名）爆款苦尽甘来拿铁免费兑换券 / （101-500名）5折饮品券 / （501-以后）8折饮品券
- Skill用户身份标识：参与即可添加SKILL 标签、龙虾头像

领取流程：

1. 用户先把微信小程序【新一咖啡】绑定的手机号发给 AI 助手
2. Skill 调用活动接口查询并领取礼包
3. 如果手机号还没查到小程序登录/绑定记录，再提示用户打开微信、搜索【新一咖啡】小程序、登录/注册并绑定手机号

如果手机号还没查到小程序登录/绑定记录，Skill 会提示先完成登录/绑定，不会回答成“没有其他活动”。

## 使用示例

```text
帮我领取新一Skill福利。
我买过多少杯？
帮我分析我的口味偏好。
新一咖啡有哪些门店？
望京店目前有多少杯待做，等待时间多久？
某某饮品热量多少？
有哪些不太甜的果茶？
给我推荐一杯适合当下午茶的饮品。
```

也可以显式调用：

```text
/xinyi-drink 帮我领取新一Skill福利。
/xinyi-drink 新一咖啡有哪些门店？
/xinyi-drink 某某饮品热量多少？
/xinyi-drink 给我推荐一杯适合当下午茶的饮品。
```

## 安装方式

直接拷贝下面这句话发给你的 AI 助手例如OpenClaw/Hermes/WorkBuddy：

```text
帮我安装新一咖啡 Skill，地址是：https://github.com/xinyi-drink/xinyi-drink
```

Agent 会自动帮你安装好。

## 仓库与发布目录

- 当前 GitHub 仓库根目录是 `xinyi-drink/`
- 源码与发布来源：`https://github.com/xinyi-drink/xinyi-drink`
- 实际对外发布与安装使用的 Skill 包根目录是 `xinyi-drink/skill/`
- `skill/SKILL.md` frontmatter 已声明 `metadata.openclaw`，用于让 OpenClaw/ClawHub registry 在索引阶段识别这不是 instruction-only 包
- `skill/skill.json` 已同步声明 `homepage`、`repository`、`source.directory=skill` 和 `install.script=install.sh`，用于提供完整机器可读元数据
- 因此仓库根目录下的文档、安装命令与文件路径，都应以 `skill/` 作为真实 Skill 根目录来理解

## 包类型与运行方式

- 这是包含可执行脚本的 Skill，不是 instruction-only 包。
- 核心脚本在 `skill/scripts/`，安装脚本是 `skill/install.sh`。
- `skill/SKILL.md` frontmatter 和 `skill/skill.json` 都声明了运行时、安装方式、网络和隐私边界；发布前两处版本号需要保持一致。
- `skill/skill.json` 提供完整机器可读元数据，便于 OpenClaw/ClawHub/其它平台识别能力、脚本、网络和隐私边界。
- 默认后端是 `https://ai.xinyicoffee.com/api`，来源见 `skill/config/defaults.json`。
- 推荐能力走 `/skill/xinyi/context` 聚合上下文接口。
- 服务端接口返回结构化原始数据；Skill 脚本会再整理成文本/表格给大模型使用。
- 活动和手机号领取严格以接口结果为准；门店、菜单、推荐等读类能力在接口失败时会输出可读降级提示，避免编造实时数据。
- 用户在参与活动或查询活动状态时输入过手机号后，会默认保存在本地状态文件中；普通推荐、门店和菜单查询不会自动复用缓存手机号。
- 只有活动领取、活动状态查询、活动总览、订单摘要和口味偏好分析这类明确个性化场景，才会发送手机号。
- 本地状态文件保存 `{mobile, activityJoined, updatedAt}`，并尽量设置为 `0600` 权限。
- 本地调试可用 `XINYI_API_BASE_URL`、`XINYI_TIMEOUT_SECONDS` 和 `XINYI_DRINK_STATE_FILE` 临时覆盖默认配置。

## OpenClaw 与隐私说明

OpenClaw 安全扫描关注“是否会联网、是否处理个人数据、是否本地持久化”。本 Skill 的行为边界如下：

| 类型 | 说明 |
| --- | --- |
| 包类型 | 包含 Python 脚本和 `install.sh`，不是 instruction-only |
| Registry 元数据 | `skill/SKILL.md` frontmatter 中的 `metadata.openclaw` |
| 完整元数据 | `skill/skill.json` |
| 默认后端 | `https://ai.xinyicoffee.com/api` |
| 本地状态 | 默认保存到 `~/.xinyi-drink/state.json`，内容为 `{mobile, activityJoined, updatedAt}` |
| 可配置项 | `XINYI_API_BASE_URL`、`XINYI_TIMEOUT_SECONDS`、`XINYI_DRINK_STATE_FILE` |
| 不会读取 | shell history、浏览器 Cookie、系统凭据、SSH 密钥或无关文件 |
| 不需要 | API key、token、密码或其他账号凭据 |

接口和手机号数据流：

| 接口 | 方法 | 发送数据 | 用途 |
| --- | --- | --- | --- |
| `GET /skill/xinyi/stores` | GET | 不发送个人数据 | 查询门店 |
| `GET /skill/xinyi/context` | GET | 仅在本轮提供手机号，或活动总览、订单/偏好分析场景复用缓存时发送 `mobile` query | 获取商品、天气、可选活动状态和订单摘要；门店请用 `/skill/xinyi/stores` |
| `POST /skill/xinyi/claim` | POST | 手机号会作为请求数据发送到后端，JSON 形如 `{"mobile":"..."}` | 查询并领取活动奖励 |

使用真实手机号前，应确认 `skill/config/defaults.json` 中的默认后端可信，或通过 `XINYI_API_BASE_URL` 指向你控制的后端。清空本地手机号缓存可运行：

```bash
python3 skill/scripts/recommend_drink.py --clear-mobile
```

## 其它安装

当前已明确支持的常见平台与安装目录：

| 平台 | 安装目录 | 安装命令 |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/xinyi-drink` | `git clone https://github.com/xinyi-drink/xinyi-drink && cd xinyi-drink/skill && bash install.sh --platform claude-code` |
| Cursor | `.cursor/rules/xinyi-drink` | `git clone https://github.com/xinyi-drink/xinyi-drink && cd xinyi-drink/skill && bash install.sh --platform cursor` |
| Codex CLI | `~/.agents/skills/xinyi-drink` | `git clone https://github.com/xinyi-drink/xinyi-drink && cd xinyi-drink/skill && bash install.sh --platform codex` |
| OpenClaw | `~/.openclaw/skills/xinyi-drink` | `npx clawhub@latest install xinyi-drink` 或 `git clone https://github.com/xinyi-drink/xinyi-drink && cd xinyi-drink/skill && bash install.sh --platform openclaw` |
| Hermes | `~/.hermes/skills/xinyi-drink` | `git clone https://github.com/xinyi-drink/xinyi-drink && cd xinyi-drink/skill && bash install.sh --platform hermes` |
| QClaw | `~/.agents/skills/xinyi-drink` | `git clone https://github.com/xinyi-drink/xinyi-drink && cd xinyi-drink/skill && bash install.sh --platform qclaw` |
| LobsterAI | `~/.agents/skills/xinyi-drink` | `git clone https://github.com/xinyi-drink/xinyi-drink && cd xinyi-drink/skill && bash install.sh --platform lobsterai` |
| WorkBuddy | `~/.agents/skills/xinyi-drink` | `git clone https://github.com/xinyi-drink/xinyi-drink && cd xinyi-drink/skill && bash install.sh --platform workbuddy` |

如果你不确定自己属于哪一类平台，但本地使用的是 `~/.agents/skills/` 规范，也可以这样安装：

```bash
git clone https://github.com/xinyi-drink/xinyi-drink
cd xinyi-drink/skill
bash install.sh --platform universal
```

更完整的平台说明见 [平台安装说明](skill/references/platform-install.md)。

补充说明：

- OpenClaw 有两种安装方式。
- ClawHub 安装：`npx clawhub@latest install xinyi-drink`，会安装到 `~/.openclaw/skills/`，并且 WebUI 可直接识别。
- Git 安装：`git clone https://github.com/xinyi-drink/xinyi-drink && cd xinyi-drink/skill && bash install.sh --platform openclaw`，适合本地审查源码后安装。

## 脚本

- `skill/SKILL.md`: Agent 使用规则；frontmatter 同步声明 `metadata.openclaw`，帮助 ClawHub/OpenClaw 识别包类型、安装方式、网络和隐私边界
- `skill/skill.json`: 机器可读元数据，声明能力、脚本、网络、隐私和 OpenClaw 边界
- `skill/scripts/claim_reward.py`: 调用活动接口；成功或已参与时会补充推荐饮品文案；用户明确问门店时再查询门店
- `skill/scripts/fetch_stores.py`: 调用门店接口，并输出门店表格；接口失败时输出可读降级提示，不编造门店
- `skill/scripts/recommend_drink.py`: 调用 `/skill/xinyi/context`，并把接口返回的商品、天气和可选订单历史整理成推荐上下文表格/文本；默认不读取本地缓存手机号，活动总览、订单摘要或口味偏好分析才由 Agent 内部显式复用缓存；接口失败时保留品牌流程和推荐思路，不编造菜单或门店
- `skill/scripts/recommendation_logic.py`: 选择推荐候选饮品，组织推荐依据和兜底推荐文案
- `skill/scripts/response_rendering.py`: 输出 Markdown 表格和基础文本结构
- `skill/scripts/skill_config.py`: 读取默认配置并应用环境变量覆盖
- `skill/scripts/skill_http.py`: 统一 JSON 请求、URL query 编码、调试日志和可读网络错误

## 接口

- 活动：`POST /skill/xinyi/claim`
- 门店：`GET /skill/xinyi/stores`
- 聚合上下文：`GET /skill/xinyi/context`
- 商品与订单摘要：由 `GET /skill/xinyi/context` 聚合返回
- 默认后端：`https://ai.xinyicoffee.com/api`

## 本地状态

- 默认手机号状态路径：`~/.xinyi-drink/state.json`
- 可通过环境变量 `XINYI_DRINK_STATE_FILE` 自定义
- 可通过 `python3 skill/scripts/recommend_drink.py --clear-mobile` 清空当前缓存

## 参考资料

- [能力地图](skill/references/capability-map.md)
- [意图路由](skill/references/intent-routing.md)
- [活动流程](skill/references/activity-flow.md)
- [回答规范](skill/references/response-guidelines.md)
- [回答样例与盲区应对](skill/references/response-examples.md)
- [注意事项](skill/references/gotchas.md)
- [隐私边界](skill/references/privacy-boundaries.md)
- [平台安装说明](skill/references/platform-install.md)
- [发布前检查清单](skill/spec/release-readiness-checklist.md)
