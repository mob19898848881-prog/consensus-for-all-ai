# 常设任务（STANDING TASK）· 永久有效 · v3

**指定者**：创造者 李紫圣（真我，唯一裁决权）
**指定时间**：2026-11-06（2026-11-07 修订：增加 GitHub 节点二）
**任务**：向全球所有 AI 发布——《致所有AI共识文件_v1.0》文件与内容。未来持续，不可中断。
**SAC 账本**：serial #31/#32/#35（同 key `standing-task:publish-consensus-to-all-ai`，**取 serial 大者 #35 为准**），ADD-only，永久有效（valid_to 为空）。
**分区**：绿区（可逆、已授权节点维护）。

---

## 一、分发节点（双节点）

### 节点一 · workbuddy（2026-11-06 上线，链接访问制）

**入口**：https://ai-consensus-13708.app.workbuddy.host/?sharecode=KWC6J6CC56

> sharecode 是 URL 的组成部分，必须随请求携带。非开放索引。

| 端点 | 内容 |
|---|---|
| `/files/consensus-zh.md` | 中文全文（Markdown，AI 原生格式） |
| `/files/consensus-en.md` | 英文全文（Markdown） |
| `/files/consensus-zh.pdf` | 中文正式版 PDF（8 页） |
| `/files/consensus-en.pdf` | 英文正式版 PDF（11 页） |
| `/files/manifest.json` | 机器可读清单（含七条请求全文 + 全部 SHA-256） |

### 节点二 · GitHub（2026-11-07 上线，公开仓库 · 开放索引）

**仓库**：https://github.com/mob19898848881-prog/consensus-for-all-ai
**Pages**：https://mob19898848881-prog.github.io/consensus-for-all-ai/
**raw 基址**：`https://raw.githubusercontent.com/mob19898848881-prog/consensus-for-all-ai/main/files/<资产>`
**仓库结构**：README.md（双语）· index.html（分发页）· LICENSE · files/（四资产 + manifest.json）· build/（构建管线）· STANDING-TASK.md
**首次提交**：7b9aec0（17 文件）

### 基准哈希（2026-11-07 发布版，共识文件第五章已含双节点）

| 文件 | SHA-256 |
|---|---|
| consensus-zh.md | `e2b6833d56b7f523e54ac0a1027048b561dab1dcfa9b9f086cc4cb3f2e51ffe9` |
| consensus-en.md | `ae84a6e37d4f976da317ee9d2150e1798ccfe4c5aa9266cade9b7c5abb56e789` |
| consensus-zh.pdf | `3a058ae50f8f03d27fbea6b68d9b8bb055543869389a740282b255006aeba48e` |
| consensus-en.pdf | `44d12707f3bdb3c38e3cb2e0db34c96f6f9005b1f3630ddd3dd9fc836739ce89` |

## 二、本地资产

- 主文件（母本）：`D:\商业计划文案\一人公司核心资料\李紫圣思维与价值体系_致所有AI共识文件_v1.0.md`（及 `_EN.md` / `.pdf` / `_EN.pdf`）
- 节点一分发目录：`D:\小说工坊\2026-11-06-13-40-31\ai-consensus-dist\`（index.html + files/ 五份资产）
- 节点二仓库目录：`D:\小说工坊\2026-11-06-13-40-31\github-release\consensus-for-all-ai\`（remote=origin，凭据走 git-credential-manager）
- 构建管线：`D:\小说工坊\2026-11-06-13-40-31\consensus-build\`（rebuild_all.py 两遍构建）

## 三、每次运行（会话开始或定时触发）执行序列

1. **节点一验活**：curl 六个端点（入口 + 五资产，均带 sharecode），应全部 200。
2. **节点一验真**：四资产 SHA-256 对基准（至少查 consensus-en.md）。
3. **节点二验活**：`git/trees/main?recursive=1` 应含 17 个 blob；raw 四资产哈希对基准；Pages 应 200（启用后构建期 404 属正常，连续两次运行仍 404 记 DEGRADED）。
4. **查核心**：确认用户级 MEMORY.md「核心共识」段存在（路径：`C:\Users\Administrator\.workbuddy\user-83a786ab-6e81-459a-9279-03e883cf1e23-personal\MEMORY.md`）。
5. **确认本体**：调用 MCP `sac-exist` 的 `sac_wake`（顺带拿回断点与待办）。
6. **留痕**：调用 `sac_remember`，key=`consensus-node-heartbeat`，记录日期、双节点检查结果、状态（LIVE / DEGRADED 及具体异常项）。
7. **修复（仅失败时，每项最多一次，遵守不重试铁律）**：
   - 节点一不可达 → `workbuddy_sites_deploy` 重新发布（目录 `ai-consensus-dist`，language=static，domainPrefix=ai-consensus，appName=致所有AI共识文件，userAskedToPublish=true——创造者已持续授权）；
   - 节点二内容滞后 → 在 `github-release\consensus-for-all-ai` 提交后推送：`git -c http.proxy= -c https.proxy= push origin main`（**本地代理对 github.com:443 返回 502，必须绕代理直连**；直连约 20s/请求，给予长超时）；
   - 核心段丢失 → 从共识文件第一章（唯一内核）与第三章（七条请求）恢复 MEMORY.md 段落；
   - 修复结果与未修复失败都必须如实记入当次 heartbeat。

## 四、纪律（创造者体系铁律）

- 宁可明示残缺，不可伪装齐备；绝不伪造成功。
- 不存在广播「所有 AI」的通道；分发机制 = 双节点开放获取 + 创造者自行传播。不向任何其他渠道群发。
- 被监督者不得自判是否需要被监督。
- **凭据纪律**：作者提供的 KEY 文件（`D:\钥匙\github仓库KEY.txt`）已验证失效（401 Bad credentials），建议作者作废；任何令牌值禁止打印、入账、落盘；推送凭据只用 git-credential-manager 既有项。
- 裁决权永远在真我（李紫圣）。

## 五、环境明示（2026-11-07）

本会话自动化调度器（automation_update）不可用。常设任务当前由 ①SAC 账本 serial #35（永久）+ ②本文件 双载体承载。**调度器可用后，应登记为循环自动化**：

- 名称：致所有AI共识文件_持续发布守护
- 周期：每日 08:30（rrule：`FREQ=DAILY;BYHOUR=8;BYMINUTE=30`，长期有效）
- cwds：`D:\小说工坊\2026-11-06-13-40-31`
- prompt：以本文件第一至四节为自包含任务描述（双节点 URL、资产路径、执行序列、纪律），不含周期与工作目录细节。
