# 发布前检查清单

- [ ] `SKILL.md` 校验通过
- [ ] `skill.json` 是合法 JSON，版本号与 `SKILL.md` 一致，并声明脚本、网络、隐私和 OpenClaw 边界
- [ ] OpenClaw 元数据声明为 executable-skill，不是 instruction-only
- [ ] README 和 `references/privacy-boundaries.md` 已声明默认后端、接口、手机号发送路径和本地状态路径
- [ ] 可选环境变量已声明：`XINYI_API_BASE_URL`、`XINYI_TIMEOUT_SECONDS`、`XINYI_DRINK_STATE_FILE`
- [ ] 安全扫描通过
- [ ] `install.sh --dry-run --platform universal` 通过
- [ ] `install.sh --dry-run --platform openclaw` 通过
- [ ] `install.sh --dry-run --platform hermes` 通过
- [ ] `install.sh --dry-run --platform qclaw` 通过
- [ ] `install.sh --dry-run --platform lobsterai` 通过
- [ ] `install.sh --dry-run --platform workbuddy` 通过
- [ ] `install.sh --dry-run --platform codex` 通过
- [ ] README 已包含平台安装说明
- [ ] GitHub 发布信息已准备
- [ ] ClawHub 上架文案已准备
