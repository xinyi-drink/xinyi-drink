# 隐私边界

- 活动领取和个性化推荐可接受手机号作为身份输入
- 个性化推荐会把当前手机号和活动状态默认保存到本地状态文件：`~/.xinyi-drink/state.json`
- 可通过环境变量 `XINYI_DRINK_STATE_FILE` 自定义保存位置
- 状态文件写入后会尽量设置为 `0600` 权限，只允许当前用户读写
- 状态结构为 `{mobile, activityJoined, updatedAt}`；`activityJoined=null` 表示接口尚未确认
- 用户可运行推荐脚本的 `--clear-mobile` 清空当前缓存手机号和活动状态
- 不提供原始订单全量透出，只返回推荐所需的精简订单字段
- 不返回财务或更敏感的个人消费信息
