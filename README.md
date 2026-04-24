# 新一好喝 Skill

`xinyi-drink` 是一个面向多 Agent 平台的 Skill 包，当前只覆盖新一好喝相关的四类能力：

1. 参与活动并领取奖励
2. 查询门店与商品基础信息
3. 查询天气
4. 基于商品、门店、天气和可选订单历史做饮品推荐

## 当前事实

- 推荐能力走 `/skill/xinyi/context` 聚合上下文接口。
- 服务端接口返回结构化原始数据；Skill 脚本会再整理成文本/表格给大模型使用。
- 天气接口默认查询北京，也支持按地点查询任意城市或地区。
- 用户在参与活动或个性化推荐时输入过手机号后，会默认保存在本地状态文件中复用。
- 当用户尚未注册或未命中活动用户时，应先引导其登录微信小程序【新一好喝】，并告知小程序绑定的手机号。
- 领取成功或已参与活动时，脚本会自动补充统一的活动提示、到店门店信息和推荐饮品文案。

## 安装

常见平台安装方式：

```bash
git clone <repo-url> ~/.agents/skills/xinyi-drink
```

Claude Code：

```bash
git clone <repo-url> ~/.claude/skills/xinyi-drink
```

Cursor：

```bash
git clone <repo-url> .cursor/rules/xinyi-drink
```

更完整的平台说明见 [平台安装说明](references/platform-install.md)。

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

- `scripts/claim_reward.py`: 调用活动接口；成功或已参与时会补充门店信息和推荐饮品文案
- `scripts/fetch_stores.py`: 调用门店接口，并输出门店表格
- `scripts/recommend_drink.py`: 调用 `/skill/xinyi/context`，并把接口返回的商品、门店、天气和可选订单历史整理成推荐上下文表格/文本

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

- [能力地图](references/capability-map.md)
- [注意事项](references/gotchas.md)
- [隐私边界](references/privacy-boundaries.md)
- [平台安装说明](references/platform-install.md)
- [发布前检查清单](spec/release-readiness-checklist.md)
