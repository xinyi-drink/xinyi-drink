# 新一好喝 Skill

`xinyi-drink` 是一个面向多 Agent 平台的 Skill 包，当前只覆盖新一好喝相关的四类能力：

1. 参与活动并领取奖励
2. 查询门店基础信息
3. 查询商品基础信息
4. 基于商品、门店、天气和可选订单历史做饮品推荐

## 仓库与发布目录

- 当前 GitHub 仓库根目录是 `xinyi-drink/`
- 源码与发布来源：`https://github.com/xinyi-drink/xinyi-drink`
- 实际对外发布与安装使用的 Skill 包根目录是 `xinyi-drink/skill/`
- 因此仓库根目录下的文档、安装命令与文件路径，都应以 `skill/` 作为真实 Skill 根目录来理解

## 当前事实

- 这是包含可执行脚本的 Skill，不是 instruction-only 包；核心脚本在 `skill/scripts/`，安装脚本是 `skill/install.sh`。
- 默认后端是 `https://ai.xinyicoffee.com/api`，来源见 `skill/config/defaults.json`。
- 推荐能力走 `/skill/xinyi/context` 聚合上下文接口。
- 商品基础信息目前由 `/skill/xinyi/context` 聚合返回，并由脚本整理给大模型使用。
- 服务端接口返回结构化原始数据；Skill 脚本会再整理成文本/表格给大模型使用。
- 推荐时统一走 `/skill/xinyi/context`，由 `context` 自动返回天气信息。
- 用户在参与活动或个性化推荐时输入过手机号后，会默认保存在本地状态文件中复用。
- 本地状态文件保存 `{mobile, activityJoined, updatedAt}`，并尽量设置为 `0600` 权限。
- 当用户尚未注册或未命中活动用户时，应先引导其登录微信小程序【新一好喝】，并告知小程序绑定的手机号。
- 领取成功或已参与活动时，脚本会自动补充统一的活动提示、到店门店信息和推荐饮品文案。
- 本地调试可用 `XINYI_API_BASE_URL`、`XINYI_TIMEOUT_SECONDS` 和 `XINYI_DRINK_STATE_FILE` 临时覆盖默认配置。

## OpenClaw 与隐私说明

OpenClaw 安全扫描关注“是否会联网、是否处理个人数据、是否本地持久化”。本 Skill 的行为边界如下：

| 类型 | 说明 |
| --- | --- |
| 包类型 | 包含 Python 脚本和 `install.sh`，不是 instruction-only |
| 默认后端 | `https://ai.xinyicoffee.com/api` |
| 本地状态 | 默认保存到 `~/.xinyi-drink/state.json`，内容为 `{mobile, activityJoined, updatedAt}` |
| 可配置项 | `XINYI_API_BASE_URL`、`XINYI_TIMEOUT_SECONDS`、`XINYI_DRINK_STATE_FILE` |
| 不会读取 | shell history、浏览器 Cookie、系统凭据、SSH 密钥或无关文件 |
| 不需要 | API key、token、密码或其他账号凭据 |

接口和手机号数据流：

| 接口 | 方法 | 发送数据 | 用途 |
| --- | --- | --- | --- |
| `GET /skill/xinyi/stores` | GET | 不发送个人数据 | 查询门店 |
| `GET /skill/xinyi/context` | GET | 有手机号时发送 `mobile` query | 获取商品、门店、天气、订单摘要和活动状态 |
| `POST /skill/xinyi/claim` | POST | 手机号会作为请求数据发送到后端，JSON 形如 `{"mobile":"..."}` | 查询并领取活动奖励 |

使用真实手机号前，应确认 `skill/config/defaults.json` 中的默认后端可信，或通过 `XINYI_API_BASE_URL` 指向你控制的后端。清空本地手机号缓存可运行：

```bash
python3 skill/scripts/recommend_drink.py --clear-mobile
```

## 安装

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

## 使用示例

```text
/xinyi-drink 我想领新一好喝的小龙虾福利
/xinyi-drink 新一在北京有哪些门店
/xinyi-drink 新一苦尽甘来拿铁是什么
/xinyi-drink 给我推荐一杯新一的咖啡
```

自然触发场景下，也可以直接问：

```text
新一在北京有哪些门店
给我推荐一杯新一的咖啡
我想喝饮料，推荐一杯
```

## 脚本

- `skill/scripts/claim_reward.py`: 调用活动接口；成功或已参与时会补充门店信息和推荐饮品文案
- `skill/scripts/fetch_stores.py`: 调用门店接口，并输出门店表格
- `skill/scripts/recommend_drink.py`: 调用 `/skill/xinyi/context`，并把接口自动返回的商品、门店、天气和可选订单历史整理成推荐上下文表格/文本
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
- [注意事项](skill/references/gotchas.md)
- [隐私边界](skill/references/privacy-boundaries.md)
- [平台安装说明](skill/references/platform-install.md)
- [发布前检查清单](skill/spec/release-readiness-checklist.md)
