# 能力地图

- `claim_reward.py`: 调用 `/skill/xinyi/claim`；成功或已参与时会再结合 `/skill/xinyi/context` 输出门店信息和推荐文案
- `fetch_stores.py`: 调用 `/skill/xinyi/stores`，并把原始门店数据整理成表格文本
- `recommend_drink.py`: 调用 `/skill/xinyi/context`，并把接口自动返回的商品、门店、天气和可选订单历史整理成可直接提供给大模型的表格/文本上下文
- `skill_config.py`: 读取默认配置，并支持 `XINYI_API_BASE_URL`、`XINYI_TIMEOUT_SECONDS` 环境变量覆盖
- `skill_http.py`: 统一 JSON 请求、URL query 编码、调试日志和可读网络错误
- `user_state.py`: 读写本地手机号与活动状态缓存，状态文件默认设置为仅当前用户可读写
- `recommendation_logic.py`: 选择推荐候选饮品、组织推荐依据和兜底推荐文案
- `response_rendering.py`: Markdown 表格和基础文本渲染
- `build_response.py`: 组合用户上下文、天气、订单、商品、门店、推荐素材和活动结果输出
