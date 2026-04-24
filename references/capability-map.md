# 能力地图

- `claim_reward.py`: 调用 `/skill/xinyi/claim`；成功或已参与时会再结合 `/skill/xinyi/context` 输出门店信息和推荐文案
- `fetch_stores.py`: 调用 `/skill/xinyi/stores`，并把原始门店数据整理成表格文本
- `recommend_drink.py`: 调用 `/skill/xinyi/context`，并把接口返回的商品、门店、天气和可选订单历史整理成可直接提供给大模型的表格/文本上下文
- `build_response.py`: 统一文本/表格渲染
