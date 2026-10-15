# MCP 集成说明

本项目对接 **麦当劳中国 MCP Server**（`https://mcp.mcd.cn`，Streamable HTTP）。

## 实际使用的 Tools

| Tool | 用途（本 Skill 场景） |
|---|---|
| `now-time-info` | 判断当前时段，匹配早餐/午餐燃油文案 |
| `query-nearby-stores` / `query-meals` | 查附近门店与可售菜单 |
| `query-meal-detail` | 看套餐组成、可替换项 |
| `query-store-coupons` / `query-my-coupons` | 挑可用券 |
| `calculate-price` | 核价，生成确认摘要里的应付金额 |
| `create-order` | **仅在** `grind unlock` 通过 **且** 用户确认哈希后调用 |
| `query-order` / `order-list` | 下单后查取餐进度 |
| `available-coupons` / `auto-bind-coupons` | 可选：领券（需用户确认） |
| `cancel-order` | 可选：取消（需用户确认） |

**刻意不默认调用**：任何会改账户状态的 Tool，都必须先出预览摘要，再带确认令牌执行。`create-order` 被本地闸门 `scripts/grind_gate.py` 二次约束——刷题进度未达标时，Skill 禁止进入下单流程。

## 调用流程（业务价值）

```text
用户：刷完 3 道华为 OD 了，想吃巨无霸套餐，最省。
  │
  ├─① grind status / unlock     （本地：进度是否 ≥ 门槛）
  ├─② query-nearby-stores + query-meals + calculate-price
  ├─③ 输出确认摘要 + confirm 哈希（门店/餐品/券/应付）
  └─④ 用户说「确认」后 → create-order → 返回支付链接
       （哈希或金额对不上则拒绝下单）
```

**业务价值**：把「冲动点餐」变成「完成专注任务后的奖励」，适合备考/赶工开发者；MCP 负责真实菜单与下单，本仓库负责闸门与确认协议，避免 Agent 直接裸调 `create-order`。

## 配置方式

1. 在 [open.mcd.cn/mcp](https://open.mcd.cn/mcp) 申请 Token。
2. 复制 `.env.example` → `.env`，填入 `MCD_MCP_TOKEN`（勿提交）。
3. 复制 `mcp.example.json` 到 Cursor / WorkBuddy MCP 配置，将 `YOUR_MCP_TOKEN` 换成环境变量或本地密钥，**不要**把真实 Token 写进仓库。

## 安全

- 仓库内只有占位符，无真实凭证。
- Token 不得放入 GitHub Actions / 第三方托管 CI。
- 支付与取餐仍由用户在官方链路完成。
