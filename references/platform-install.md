# 平台安装说明

## 使用 `~/.agents/skills/` 的平台

以下平台都明确安装到同一个目录：

- Codex CLI
- OpenClaw
- Hermes
- QClaw
- LobsterAI
- WorkBuddy

统一安装目录：

```bash
~/.agents/skills/xinyi-drink
```

直接安装命令：

```bash
git clone https://github.com/xinyi-drink/xinyi-drink ~/.agents/skills/xinyi-drink
```

如果使用安装脚本，以下平台参数都已明确支持，并且都会安装到上面的同一目录：

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

- 如果平台本身兼容 `SKILL.md`，但不在上面的明确支持列表中，优先尝试这个目录：

```bash
~/.agents/skills/xinyi-drink
```

- 如果平台要求项目级安装，再按该平台自己的技能目录规则调整
