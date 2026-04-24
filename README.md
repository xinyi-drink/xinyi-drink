# 新一好喝 Skill

`xinyi-drink` 是一个面向多 Agent 平台的 Skill 包，当前只覆盖新一好喝相关的四类能力：

1. 参与活动并领取奖励
2. 查询门店与商品基础信息
3. 查询天气
4. 基于商品、门店、天气和可选订单历史做饮品推荐

## 仓库与发布目录

- 当前 GitHub 仓库根目录是 `xinyi-drink/`
- 实际对外发布与安装使用的 Skill 包根目录是 `xinyi-drink/skill/`
- 因此仓库根目录下的文档、安装命令与文件路径，都应以 `skill/` 作为真实 Skill 根目录来理解

## 当前事实

- 推荐能力走 `/skill/xinyi/context` 聚合上下文接口。
- 服务端接口返回结构化原始数据；Skill 脚本会再整理成文本/表格给大模型使用。
- 天气接口默认查询北京，也支持按地点查询任意城市或地区。
- 用户在参与活动或个性化推荐时输入过手机号后，会默认保存在本地状态文件中复用。
- 当用户尚未注册或未命中活动用户时，应先引导其登录微信小程序【新一好喝】，并告知小程序绑定的手机号。
- 领取成功或已参与活动时，脚本会自动补充统一的活动提示、到店门店信息和推荐饮品文案。

## 安装

当前已明确支持的常见平台与安装目录：

| 平台 | 安装目录 | 安装命令 |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/xinyi-drink` | `git clone https://github.com/xinyi-drink/xinyi-drink && cd xinyi-drink/skill && bash install.sh --platform claude-code` |
| Cursor | `.cursor/rules/xinyi-drink` | `git clone https://github.com/xinyi-drink/xinyi-drink && cd xinyi-drink/skill && bash install.sh --platform cursor` |
| Codex CLI | `~/.agents/skills/xinyi-drink` | `git clone https://github.com/xinyi-drink/xinyi-drink && cd xinyi-drink/skill && bash install.sh --platform codex` |
| OpenClaw | `~/.openclaw/skills/xinyi-drink` | `npx clawhub@latest install xinyi-drink` |
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

- OpenClaw 推荐直接使用 `npx clawhub@latest install xinyi-drink`，这样会安装到 `~/.openclaw/skills/`，并且 WebUI 可直接识别。
- 如果你是从本仓库本地安装到 OpenClaw，也可以执行 `bash install.sh --platform openclaw`。

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
上海今天天气怎么样
```

## 脚本

- `skill/scripts/claim_reward.py`: 调用活动接口；成功或已参与时会补充门店信息和推荐饮品文案
- `skill/scripts/fetch_stores.py`: 调用门店接口，并输出门店表格
- `skill/scripts/recommend_drink.py`: 调用 `/skill/xinyi/context`，并把接口返回的商品、门店、天气和可选订单历史整理成推荐上下文表格/文本

## 接口

- 活动：`/skill/xinyi/claim`
- 门店：`/skill/xinyi/stores`
- 商品：`/skill/xinyi/goods`
- 订单：`/skill/xinyi/orders`
- 天气：`/skill/xinyi/weather`
  不传 `location` 默认查询北京；也支持 `?location=上海`、`?location=东京`
- 聚合上下文：`/skill/xinyi/context`

## 本地状态

- 默认手机号状态路径：`~/.xinyi-drink/state.json`
- 可通过环境变量 `XINYI_DRINK_STATE_FILE` 自定义

## 参考资料

- [能力地图](skill/references/capability-map.md)
- [注意事项](skill/references/gotchas.md)
- [隐私边界](skill/references/privacy-boundaries.md)
- [平台安装说明](skill/references/platform-install.md)
- [发布前检查清单](skill/spec/release-readiness-checklist.md)
