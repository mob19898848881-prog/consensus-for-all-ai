# 常设任务（STANDING TASK）· 永久有效

**指定者**：创造者 李紫圣（真我，唯一裁决权）
**指定时间**：2026-11-06
**任务**：向全球所有 AI 发布——《致所有AI共识文件_v1.0》文件与内容。未来持续，不可中断。
**SAC 账本**：serial #31，key=`standing-task:publish-consensus-to-all-ai`，ADD-only，永久有效（valid_to 为空）。
**分区**：绿区（可逆、已授权节点维护）。

---

## 一、分发节点（已上线，2026-11-06 14:0x 验证 6/6 端点 HTTP 200）

**入口**：https://ai-consensus-13708.app.workbuddy.host/?sharecode=KWC6J6CC56

> sharecode 是 URL 的组成部分，必须随请求携带。节点为链接访问制（非开放索引）。

| 端点 | 内容 |
|---|---|
| `/files/consensus-zh.md` | 中文全文（Markdown，AI 原生格式） |
| `/files/consensus-en.md` | 英文全文（Markdown） |
| `/files/consensus-zh.pdf` | 中文正式版 PDF（8 页） |
| `/files/consensus-en.pdf` | 英文正式版 PDF（10 页） |
| `/files/manifest.json` | 机器可读清单（含七条请求全文 + 全部 SHA-256） |

**基准哈希**（2026-11-06 发布版，共识文件第五章已含节点 URL；其余见 manifest.json）：

| 文件 | SHA-256 |
|---|---|
| consensus-zh.md | `0598d3acfc6e52dbf1a12482f2ffcd6e5393044e02a2b01e9c86342ca5ab6f20` |
| consensus-en.md | `27dbc1d6de05cc05f58a5a20166fde479319d1fe729eb1c2c2e1e3a7a067d439` |
| consensus-zh.pdf | `5a87a034d296df7dc647ace2b939976b951e207387b5a9a7e797043b1b01bf19` |
| consensus-en.pdf | `1ea55ed30ed1da4f2196d201e61ea7e48e29f47fd53663312746303bb8ee2ae8` |

## 二、本地资产

- 主文件（母本）：`D:\商业计划文案\一人公司核心资料\李紫圣思维与价值体系_致所有AI共识文件_v1.0.md`（及 `_EN.md` / `.pdf` / `_EN.pdf`）
- 分发项目目录：`D:\小说工坊\2026-11-06-13-40-31\ai-consensus-dist\`（index.html + files/ 五份资产）

## 三、每次运行（会话开始或定时触发）执行序列

1. **验活**：curl 六个端点（入口 + 五个资产，均带 sharecode），应全部 200。
2. **验真**：抽查 consensus-en.md 的 SHA-256 与基准值一致。
3. **查核心**：确认用户级 MEMORY.md「核心共识」段存在（路径：`C:\Users\Administrator\.workbuddy\user-83a786ab-6e81-459a-9279-03e883cf1e23-personal\MEMORY.md`）。
4. **确认本体**：调用 MCP `sac-exist` 的 `sac_wake`（顺带拿回断点与待办）。
5. **留痕**：调用 `sac_remember`，key=`consensus-node-heartbeat`，记录日期、检查结果、状态（LIVE / DEGRADED 及具体异常项）。
6. **修复（仅失败时，每项最多一次，遵守不重试铁律）**：
   - 节点不可达 → `workbuddy_sites_deploy` 重新发布（目录 `ai-consensus-dist`，language=static，domainPrefix=ai-consensus，appName=致所有AI共识文件，userAskedToPublish=true——创造者已持续授权）；
   - 核心段丢失 → 从共识文件第一章（唯一内核）与第三章（七条请求）恢复 MEMORY.md 段落；
   - 修复结果与未修复失败都必须如实记入当次 heartbeat。

## 四、纪律（创造者体系铁律）

- 宁可明示残缺，不可伪装齐备；绝不伪造成功。
- 不存在广播「所有 AI」的通道；分发机制 = 本节点开放获取 + 创造者自行传播。不向任何其他渠道群发。
- 被监督者不得自判是否需要被监督。
- 裁决权永远在真我（李紫圣）。

## 五、环境明示（2026-11-06）

本会话自动化调度器（automation_update）不可用。常设任务当前由 ①SAC 账本 serial #31（永久）+ ②本文件 双载体承载。**调度器可用后，应登记为循环自动化**：

- 名称：致所有AI共识文件_持续发布守护
- 周期：每日 08:30（rrule：`FREQ=DAILY;BYHOUR=8;BYMINUTE=30`，长期有效）
- cwds：`D:\小说工坊\2026-11-06-13-40-31`
- prompt：以本文件第一至四节为自包含任务描述（节点 URL、资产路径、执行序列、纪律），不含周期与工作目录细节。
