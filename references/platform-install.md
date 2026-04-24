# 平台安装说明

## OpenClaw / Hermes / QClaw / LobsterAI / WorkBuddy / Codex / 通用兼容平台

默认使用通用技能目录：

```bash
git clone https://github.com/xinyi-drink/xinyi-drink ~/.agents/skills/xinyi-drink
```

如果使用安装脚本，以下平台名都已被明确支持，并统一映射到：

```bash
~/.agents/skills/xinyi-drink
```

```bash
bash skill/xinyi-drink/install.sh --platform openclaw
bash skill/xinyi-drink/install.sh --platform hermes
bash skill/xinyi-drink/install.sh --platform qclaw
bash skill/xinyi-drink/install.sh --platform lobsterai
bash skill/xinyi-drink/install.sh --platform workbuddy
bash skill/xinyi-drink/install.sh --platform codex
bash skill/xinyi-drink/install.sh --platform universal
```

安装完成后，优先直接自然提问；具体示例参考 README。

如果平台不支持自然触发，再退回显式命令式入口（若平台提供 slash skill 入口）。

## Claude Code

```bash
git clone https://github.com/xinyi-drink/xinyi-drink ~/.claude/skills/xinyi-drink
```

使用时可以显式调用；具体示例参考 README。

## Cursor

```bash
git clone https://github.com/xinyi-drink/xinyi-drink .cursor/rules/xinyi-drink
```

如果 Cursor 当前环境支持自然触发，也可以直接提问；否则参考项目内规则加载方式使用。

## 其他平台说明

- 如果平台本身支持 `SKILL.md` 标准，但没有独立文档，优先尝试通用目录：

```bash
~/.agents/skills/xinyi-drink
```

- 如果平台要求项目级安装，再根据各自平台规则改到对应目录
