# 隐私边界

## 个人数据

- 活动领取、活动总览、订单摘要和口味偏好分析可接受手机号作为身份输入。
- 普通推荐、门店查询和菜单查询默认不读取本地缓存手机号，也不自动发送手机号。
- 手机号会在以下场景发送到后端：
  - `POST /skill/xinyi/claim`: JSON body 中发送 `mobile`，用于查询或领取活动奖励。
  - `GET /skill/xinyi/context`: 用户本轮提供手机号，或 Agent 在活动总览、订单/偏好分析场景使用内部 `--use-saved-mobile` 时，以 query 发送 `mobile`，用于获取活动状态和精简订单摘要。
- 普通门店查询 `GET /skill/xinyi/stores` 不发送手机号。

## 后端与配置

- 默认后端来自 `config/defaults.json`：`https://ai.xinyicoffee.com/api`。
- 可通过 `XINYI_API_BASE_URL` 覆盖默认后端；使用真实手机号前应确认该后端可信。
- 可通过 `XINYI_TIMEOUT_SECONDS` 覆盖请求超时时间。
- 可通过 `XINYI_DRINK_STATE_FILE` 自定义本地状态文件路径。

## 本地状态

- 活动领取和活动状态确认会把当前手机号和活动状态默认保存到本地状态文件：`~/.xinyi-drink/state.json`。
- 状态文件写入后会尽量设置为 `0600` 权限，只允许当前用户读写。
- 状态结构为 `{mobile, activityJoined, updatedAt}`；`activityJoined=null` 表示接口尚未确认。
- 用户可运行 `python3 scripts/recommend_drink.py --clear-mobile` 清空当前缓存手机号和活动状态。

## 不做的事

- 不读取 shell history、浏览器 Cookie、系统凭据、SSH 密钥或无关文件。
- 不请求 API key、token、密码或其他账号凭据。
- 不提供原始订单全量透出，只返回推荐所需的精简订单字段。
- 不返回财务或更敏感的个人消费信息。
