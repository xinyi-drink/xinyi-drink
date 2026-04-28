# 能力地图

## 脚本与能力

- `skill.json`: 机器可读能力地图，供 OpenClaw、ClawHub 和其它平台识别脚本、接口、隐私边界和关键词
- `claim_reward.py`: 调用 `/skill/xinyi/claim`；成功或已参与时会再结合 `/skill/xinyi/context` 输出门店信息和推荐文案
- `fetch_stores.py`: 调用 `/skill/xinyi/stores`，并把原始门店数据整理成表格文本
- `recommend_drink.py`: 调用 `/skill/xinyi/context`，并把接口返回的商品、门店、天气和可选订单历史整理成可直接提供给大模型的表格/文本上下文；默认不读取本地缓存手机号，只有内部 `--use-saved-mobile` 或本轮 `--mobile` 才发送手机号
- `skill_config.py`: 读取默认配置，并支持 `XINYI_API_BASE_URL`、`XINYI_TIMEOUT_SECONDS` 环境变量覆盖
- `skill_http.py`: 统一 JSON 请求、URL query 编码、调试日志和可读网络错误
- `user_state.py`: 读写本地手机号与活动状态缓存，状态文件默认设置为仅当前用户可读写
- `recommendation_logic.py`: 选择推荐候选饮品、组织推荐依据和兜底推荐文案
- `response_rendering.py`: Markdown 表格和基础文本渲染
- `build_response.py`: 组合用户上下文、天气、订单、商品、门店、推荐素材和活动结果输出

## 网络边界

- 默认后端：`https://ai.xinyicoffee.com/api`
- `GET /skill/xinyi/stores`: 不发送个人数据
- `GET /skill/xinyi/context`: 仅在本轮提供手机号或内部 `--use-saved-mobile` 个性化场景发送 `mobile` query
- `POST /skill/xinyi/claim`: 发送 `{"mobile":"..."}` JSON body

## 本地边界

- 默认状态文件：`~/.xinyi-drink/state.json`
- 状态内容：`{mobile, activityJoined, updatedAt}`
- 可配置项：`XINYI_API_BASE_URL`、`XINYI_TIMEOUT_SECONDS`、`XINYI_DRINK_STATE_FILE`
- 本 Skill 包含可执行脚本，不是 instruction-only
