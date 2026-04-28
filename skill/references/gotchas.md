# 注意事项

- 推荐由 Agent 自行完成。
- 推荐能力统一走 `/skill/xinyi/context`；这个接口会自动返回商品、门店、天气和可选订单历史。
- 接口返回的是结构化原始数据；提供给大模型前，应使用脚本层整理成文本/表格，不要把 JSON 原样塞给模型。
- 用户输入过手机号后，默认复用本地保存的手机号，除非用户明确要求更换或清空。
- 手机号活动状态是三态：`true` 表示已参加，`false` 表示接口确认未参加，`null` 表示未确认。
- 推荐前会尝试调用 `/skill/xinyi/claim` 同步活动状态；如果该接口失败，推荐不会中断，会继续使用 `/skill/xinyi/context` 并把活动状态保留为未确认。
- 活动领取细则见 `activity-flow.md`；推荐回答细则见 `response-guidelines.md`；意图判断细则见 `intent-routing.md`。
- 天气是推荐时的增强输入，不是单独对外暴露的能力；如果 `context` 没返回天气，推荐文案会自动降级成普通句式。
- 门店状态缓存只有 5 分钟，不保证秒级实时。
- 生产默认 API 来自 `config/defaults.json`，本地调试可用 `XINYI_API_BASE_URL` 和 `XINYI_TIMEOUT_SECONDS` 临时覆盖。
- 本 Skill 包含 Python 脚本和 `install.sh`，发布元数据不能标记为 instruction-only。
- 使用真实手机号前，先确认默认后端 `https://ai.xinyicoffee.com/api` 或 `XINYI_API_BASE_URL` 指向可信服务。
- 回答用户时不要暴露内部脚本路径、缓存结构、OpenClaw 审查细节，除非用户明确询问 Skill 实现或安全边界。
- 用户问功能介绍时，只讲可见能力和使用方式；用户问活动时，先讲 Skill 用户大礼包，不要只列商品活动。
- 接口没有返回的数据就是盲区：宁可说明没拿到，也不要补全门店、商品、券名、订单或活动状态。
