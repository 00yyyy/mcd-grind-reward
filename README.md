# mcd-grind-reward · 刷题燃油闸门

> 麦当劳程序员创意开发大赛参赛作品（非官方产品）。过完题，才配点巨无霸。

把「冲动点餐」变成「完成刷题/专注后的奖励」：本地闸门管进度与确认哈希，麦当劳 MCP 管菜单、券、核价、下单。

[![Contest](https://img.shields.io/badge/MCD-1024%20Challenge-ffc72c)](https://github.com/M-China/mcd-developer-innovation-challenge)

## 为什么不是又一个凑套餐助手？

| 常见 Skill | 本项目 |
|---|---|
| 一开口就查券下单 | **先** `grind` 达标，否则锁死 `create-order` |
| 提示词约定「先确认」 | **代码**校验 confirm 哈希；payload/金额被改就拒绝 |
| 纯推荐文案 | 可接真实 MCP；无 Token 也能 `--demo` 走完闸门 |

## 30 秒 Demo（无需 Token）

```bash
python3 scripts/grind_gate.py --demo reset
python3 scripts/grind_gate.py --demo log --title "OD-双指针"
python3 scripts/grind_gate.py --demo log --title "OD-单调栈"
python3 scripts/grind_gate.py --demo log --title "OD-并查集"
python3 scripts/grind_gate.py --demo status
# → UNLOCKED  progress=3/3

PAYLOAD=$(cat demo/sample_payload.json | python3 -c 'import sys,json; print(json.dumps(json.load(sys.stdin),ensure_ascii=False))')
python3 scripts/grind_gate.py --demo preview --payload "$PAYLOAD"
# → confirm=........
python3 scripts/grind_gate.py --demo confirm --payload "$PAYLOAD" --confirm <上一步的confirm>
# → CONFIRM_OK  allowed_to_call_create_order=1
```

未达标时 `preview` 直接 `DENIED`。

## 安装 Skill

1. 克隆本仓库。
2. 将 [`SKILL.md`](./SKILL.md) 装到 Cursor / WorkBuddy / Claude Code 的 skills 目录（或在对话里 `@` 引用）。
3. 按 [`mcp.example.json`](./mcp.example.json) 配置麦当劳 MCP（Token 用环境变量，**不要**提交真实密钥）。
4. 复制 `.env.example` → `.env`，填入 `MCD_MCP_TOKEN`（已被 `.gitignore`）。

申请 Token：[麦当劳 MCP 开放平台](https://open.mcd.cn/mcp)

## 目标用户

- 备考华为 OD / 算法面试，想用「过题才吃」抗住外卖冲动
- 需要 **可审计下单确认** 的 Agent 用户（不信任纯提示词）

## 仓库结构

```text
CONTEST_DECLARATION.md   # 官方参赛声明（内容不可改）
MCP_INTEGRATION.md       # 用到的 MCP Tool 与流程
SKILL.md                 # Agent Skill
scripts/grind_gate.py    # 本地闸门
demo/                    # 示例 payload
mcp.example.json         # MCP 配置模板
```

## 安全

- 仓库 **不含** 真实 MCP Token。
- 禁止把 Token 放进 GitHub Actions。
- 支付仍在官方链接由用户完成。

## 许可与声明

参赛作品，规则与声明见 `CONTEST_DECLARATION.md`。麦当劳及相关商标归权利人所有。
