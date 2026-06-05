# AI Development Control Log

[![validate](https://github.com/zycaskevin/ai-development-control-log-public/actions/workflows/validate.yml/badge.svg)](https://github.com/zycaskevin/ai-development-control-log-public/actions/workflows/validate.yml) [![License: MIT + CC BY 4.0](https://img.shields.io/badge/License-MIT%20%2B%20CC--BY--4.0-blue.svg)](LICENSE)

> 我不一定看得懂 AI 写的每一行 code。
> 但我一定要看得懂，它什么时候偷偷替我做主。

[繁体中文](README.md) | [English](README.en.md)

## 这份东西是什么？

这是一份给非工程背景创业者、产品负责人、独立开发者用的 **AI 开发控制日志**。

它不是教你写程式。
它是教你怎么管理一个很会写程式、但偶尔会自作主张的 AI 助理。

AI coding agents 很厉害。Claude Code、Cursor、Codex、OpenCode 这类工具，已经可以把一个产品从 0 慢慢堆起来。

但真正吓人的地方不是 AI 写错。
写错还能修。

真正吓人的是：它没问你，就替你做了产品决策。

你只是叫它改一个小功能，它顺手改了核心计算逻辑。
你只是叫它调整画面，它顺手重构一整个模组。
你只是叫它补一个栏位，它顺手改了资料库 schema。
它可能不是故意的。它甚至觉得自己在帮你。

问题是，它没有告诉你。

这份 repo 要解决的就是这件事。

## 一句话

> Karpathy guidelines 管 AI 怎么写 code。
> AI Development Control Log 管 AI 有没有越权。

## 你不需要看懂 code

你需要看懂这些：

- AI 做了什么？
- 哪些是你明确要求的？
- 哪些是 AI 自己决定的？
- 哪些地方偏离原本规格？
- 有没有碰到资料、金流、production、权限、核心计算？
- 验证了什么？没验证什么？
- 出事怎么退？

这些是人话。不是 code。

只要 AI 老实写出来，非工程背景的人也能管理它。

## 这份规范怎么来的？

它结合了两件事。

第一个是 Karpathy-style coding guidelines：

- Think before coding：不要乱猜，先讲假设
- Simplicity first：不要过度设计
- Surgical changes：只改该改的，不要顺手乱改
- Goal-driven execution：要有验证标准，不要只说「完成」

第二个是 Control Log：

- 把 AI 的假设写出来
- 把 AI 自己做的决定写出来
- 把偏离规格的地方写出来
- 把取舍写出来
- 把不可逆操作挡下来
- 把验证和回滚写清楚

Karpathy 让 AI 少写烂 code。
Control Log 让 AI 不要偷偷当老板。

## 什么时候一定要用？

只要做错会痛，就用。

特别是：

- 金流、付款、订阅、佣金
- 使用者资料、CRM、隐私资料
- 资料库 schema、migration、批次更新
- production deploy、cutover、webhook、gateway
- 权限、登入、auth、secret
- 核心计算逻辑
- 多 agent 协作
- 任何你看不懂，但出事很麻烦的任务

小 typo、单行文案、没有副作用的小修改，可以不用。

## 最重要的规则

### 1. 每个改动都要能追溯到需求

> Every changed line should trace directly to the user's request.

如果你叫 AI 改按钮文案，它却动到付款逻辑，这不是「顺手优化」。
这是越权。

### 2. AI 自己决定的事情要分开列

AI 可以建议。
AI 可以提出更好的做法。
但它不能默默替你决定。

### 3. 不可逆操作必须停下问

碰到这些事，AI 必须停：

- 删资料
- 改资料库结构
- 推上 production
- 改金流、付款、订阅
- 改权限、auth、secret
- 改核心计算逻辑
- 大规模重构

不是写在最后报告。
是做之前就停下来问。

### 4. 「已完成」不是证据

AI 说完成，不代表完成。
AI 说测过，不代表真的测过。

它要写清楚：

- 跑了哪些测试
- 哪些通过
- 哪些没跑
- 哪些只是推测
- 如果出事怎么回滚

每份回报也应该先标可信度：

```text
✅ 已真实验证：有工具输出、测试、live smoke 或 production check 可支撑
⚠️ 部分验证：只验证其中一部分，或缺少 live / production 证据
❌ 未验证：只是推论、阅读文件、或尚未执行真实检查
```

测试类型也要分清楚，不要把 mock test 说成真实可用：

```text
mock：只代表模拟通过
unit：单元测试通过
integration：整合测试通过
live smoke：真实 CLI / API / 服务最小可用检查通过
production verified：production 环境已确认
```

## 会每天记、每天寄吗？

**从 v0.4 起：可以，而且不需要你自己手改 workflow。v0.5 起：如果 agent 写了 task log，daily digest 会优先用任务级证据，不再只靠 git 猜。**

具体行为：

- 每天 02:00 UTC（= 10:00 台北时间）GitHub Actions 自动跑一次
- 自动从最近 24 小时 git 活动产出一份可读的 `logs/daily/YYYY-MM-DD-digest.zh-TW.md`
- 如果存在 `logs/tasks/*.md` task control logs，报告会优先读取它们，列出「用户明确要求」和「AI 自己决定」
- 如果没有 task logs，仍保留 v0.4 git-based fallback，诚实标示哪些事无法可靠判断
- 报告会回答 7 个问题：AI 做了什么、哪些是 AI 自己决定、有没有高风险、怎么退
- 报告会上传成 workflow artifact
- 如果你让 agent 设置了配送频道，会自动寄到 Slack / 飞书 / Telegram / Email
- 如果没设置配送频道，默认不外寄，只保留 artifact
- 默认不调用 LLM，所以 daily digest 的模型 token 成本是 0

如果你想 5 分钟内接好，请看：[**5 分钟接上指南：交给 agent 安装**](#5-分钟接上指南交给-agent-安装)。

更早版本（v0.3.1 之前）的设计哲学是「手动 SOP，不自动跑」。v0.4 把它升级成「**每天自动产出可读报告，配送交给 agent 安装**」。v0.4 的 daily digest 回答的问题也跟 v0.3.1 不一样——见下表。

### v0.3.1 vs v0.4 daily digest 差在哪？

| 问题 | v0.3.1 digest | v0.4 digest |
|---|---|---|
| AI 今天做了什么？ | commit / PR 标题 | 每个动作标 ✅/⚠️/❌ 是 user 叫的还是 AI 自决 |
| 哪些是 AI 自决？ | 自由文字段落 | 表格 + 「该不该先问你」栏 |
| 偏离规格了吗？ | 自由文字 | 表格 + 「是否需要你确认」 |
| 高风险 gate 触发了吗？ | 自由文字 | 8 个风险项逐项 ✅/❌ |
| 验证了什么 / 没验证什么？ | 自由文字 | 表格，「没验证」也要写 |
| 出事怎么退？ | 自由文字 | 表格 + 「已验证可退」 |
| 这份你看懂吗？ | **没有** | §8 明确问你 ✅/⚠️/❌ |
| 1 分钟看完摘要 | **没有** | §0 1 分钟版（老板专用）|

v0.4 的 digest 是**老板抓 AI 越权用的**，不是「AI 员工自我感觉良好日报」。如果你要的是工作进度（PR、issue、commit），请看 GitHub 自己的 daily digest。

### v0.5 补上什么？

v0.4 的限制是：只看 git 时，它能知道「改了什么」，但不能可靠知道「这是你要求的，还是 AI 自己决定的」。

v0.5 新增 task-level control log：

- 模板：`templates/task-control-log.zh-TW.md` / `templates/task-control-log.en.md`
- 建议路径：`logs/tasks/YYYY-MM-DD-<slug>.md`
- Parser：`scripts/collect_task_logs.py`
- Daily digest：有 task logs 时优先使用；没有时回到 v0.4 的保守 fallback

也就是说，agent 每次任务结束后多写一份小记录，隔天的 daily digest 就能更准确回答：哪些是你明确要求、哪些是 AI 自己决定。

## 5 分钟接上指南：交给 agent 安装

**目标**：fork 完这个 repo，5 分钟内开始每天收到一份「你看得懂的 AI 做了什么」报告。

你不用自己改 workflow。请直接把这段给你的 coding agent：

```text
请帮我安装 AI Development Control Log 的每日报告。
我要每天收到 1 分钟看得懂的 digest。
请照 docs/install/agent-assisted-install.zh-CN.md 做，帮我选配送频道、设置 GitHub Actions secrets、触发 workflow、下载 artifact、确认外寄结果。
不要把任何 token / webhook / secret 写进 git。
```

agent 会问你一个问题：

> 你要每天报告寄到哪里？Slack / 飞书 / Telegram / Email / 不外寄

然后 agent 会帮你做：

1. 设置 `DELIVERY_PROVIDER`
2. 把 webhook / token 放进 GitHub Actions secrets
3. 本地产生一次 digest 并验证
4. 触发 GitHub Actions workflow 跑一次
5. 确认 artifact 有产出
6. 如果你选了外寄，确认消息真的有送到频道

完整 agent 任务卡：[`docs/install/agent-assisted-install.zh-CN.md`](docs/install/agent-assisted-install.zh-CN.md)。
可复制 prompt：[`templates/agent-install-prompt.zh-CN.md`](templates/agent-install-prompt.zh-CN.md)。

### 之后不想收怎么关？

请 agent 帮你跑：

```bash
gh variable set DELIVERY_PROVIDER --body none
```

或者删掉对应的 webhook secret。

## 语言选择

Control Log 与 Daily Digest 不能硬写英文。每份 log 都应该先指定：

```text
输出语言：zh-TW / zh-CN / en / ja / custom
读者：创办人 / operator / 工程师 / 客户 / 内部团队
语气：白话 / 技术 / 高层摘要 / 客户可读
技术名词是否翻成人话：是 / 否
```

对 创办人 / operator 内部使用，预设是：

```text
语言：繁体中文 zh-TW
语气：白话、CEO 可读、少技术黑话
```

公开 repo 可以保留英文文件，但不能只有英文模板。繁中使用者应该能直接看懂 AI 今天做了什么决定。

## 快速使用

### 方法 A：只拿日志模板

繁中使用者建议直接复制繁中模板：

```bash
cp templates/implementation-control-log.zh-TW.md ./implementation-control-log.md
```

如果你的团队偏英文，则可使用英文 / 双语模板：

```bash
cp templates/implementation-control-log.md ./implementation-control-log.md
```

然后要求 AI：

> 这次任务请边做边更新 `implementation-control-log.md`。不要做完才补。凡是你自行决定、偏离规格、碰到不可逆操作，都要写进去。

### 方法 B：Claude Code

把 [`CLAUDE.md`](CLAUDE.md) 合并进你的专案 `CLAUDE.md`。

### 方法 C：Cursor

把 Cursor rule 复制到你的专案：

```bash
mkdir -p .cursor/rules
cp .cursor/rules/ai-development-control-log.mdc your-project/.cursor/rules/
```

### 方法 D：Hermes / Agent skill

使用：

```text
skills/ai-development-control-log/SKILL.md
```

## 日志模板

任务级 Control Log 模板：

- [`templates/implementation-control-log.zh-TW.md`](templates/implementation-control-log.zh-TW.md)：繁体中文，给中文使用者直接套用
- [`templates/implementation-control-log.md`](templates/implementation-control-log.md)：英文 / 双语栏位，适合英文团队或跨语言团队
- [`templates/task-control-log.zh-TW.md`](templates/task-control-log.zh-TW.md)：v0.5 任务级 evidence log，让每日报告知道 user asked / AI self-decided
- [`templates/task-control-log.en.md`](templates/task-control-log.en.md)：v0.5 English task-level evidence log

Daily Decision Digest 模板：

- [`templates/daily-decision-digest.zh-TW.md`](templates/daily-decision-digest.zh-TW.md)：繁体中文，每日 AI 决策摘要
- [`templates/daily-decision-digest.en.md`](templates/daily-decision-digest.en.md)：英文，每日 AI 决策摘要

Delivery automation 模板与范例：

- [`docs/automation/optional-delivery-automation.md`](docs/automation/optional-delivery-automation.md)：选配自动寄送规则
- [`templates/daily-digest-delivery-config.zh-TW.md`](templates/daily-digest-delivery-config.zh-TW.md)：繁中寄送设定模板
- [`templates/daily-digest-delivery-config.en.md`](templates/daily-digest-delivery-config.en.md)：英文寄送设定模板

核心栏位：

0. 语言与读者设定
1. 任务目标
2. 使用者明确要求
3. 待厘清问题 / 假设
4. AI 自行决定
5. 偏离规格
6. Surgical Change 检查
7. 取舍
8. 高风险 / 不可逆操作
9. 验证结果
10. 回滚方式

回报时请额外标出：可信度、测试类型，以及能支撑结论的真实工具输出。


## 验证脚本

这个 repo 附了一个轻量验证脚本：[`scripts/validate.py`](scripts/validate.py)。

它不是测你的产品功能，而是检查 protocol kit / repo 是否仍然完整：

- 必要文件是否存在且不是空档
- `SKILL.md` 是否有基本 frontmatter
- `templates/implementation-control-log.md` 与 `templates/implementation-control-log.zh-TW.md` 是否保留核心 section
- Daily Digest / delivery automation 模板是否保留安全 section
- 范例与文章是否仍在预期路径

### 验证模式

```bash
python scripts/validate.py --mode repo
python scripts/validate.py --mode kit
python scripts/validate.py --mode strict
```

| mode | 用途 | 是否要求 private live log |
|---|---|---|
| `repo` | 维护这个 protocol repo 本身，预设模式 | ❌ 不要求；使用 public-safe example |
| `kit` | 给 fork / 使用者套用 | ❌ 不要求；使用 public-safe example |
| `strict` | CI / maintainer 严格检查，目前等同 `repo` | ❌ 不要求；使用 public-safe example |

预设执行：

```bash
python scripts/validate.py
```

等同：

```bash
python scripts/validate.py --mode repo
```

成功时输出：

```text
VALIDATION PASSED (repo mode)
```

失败时会列出缺失项，例如：

```text
VALIDATION FAILED (repo mode)
- missing: templates/implementation-control-log.md
- template missing section: Verification Results
```

GitHub Actions 也会在 push / pull request 时执行 repo mode 验证与测试。

## 范例

- [`examples/calc-feature-control-log.md`](examples/calc-feature-control-log.md)：接近核心计算逻辑的功能
- [`examples/billing-change-control-log.md`](examples/billing-change-control-log.md)：金流 / 订阅变更
- [`examples/database-migration-control-log.md`](examples/database-migration-control-log.md)：资料库 migration 与 rollback
- [`examples/multi-round-control-log.md`](examples/multi-round-control-log.md)：同一任务多轮更新
- [`examples/daily-decision-digest.zh-TW.md`](examples/daily-decision-digest.zh-TW.md)：繁中每日 AI 决策摘要范例
- [`examples/daily-decision-digest.en.md`](examples/daily-decision-digest.en.md)：英文每日 AI 决策摘要范例
- [`examples/language-selection-control-log.zh-TW.md`](examples/language-selection-control-log.zh-TW.md)：繁中语言选择 control log 范例
- [`examples/github-actions-daily-digest.yml`](examples/github-actions-daily-digest.yml)：GitHub Actions local-only digest artifact 范例
- [`examples/hermes-cron-daily-digest.zh-TW.md`](examples/hermes-cron-daily-digest.zh-TW.md)：Hermes cron 每日摘要范例

## 可以分享的文章

如果你想把这套观念分享给其他人，可以从这篇开始改：

- [`articles/manage-ai-engineer-with-control-log.md`](articles/manage-ai-engineer-with-control-log.md)

## Repo 结构

```text
.
├── README.md
├── README.zh-CN.md
├── README.en.md
├── CLAUDE.md
├── .cursor/rules/ai-development-control-log.mdc
├── skills/ai-development-control-log/SKILL.md
├── templates/
│   ├── implementation-control-log.zh-TW.md
│   ├── implementation-control-log.md
│   ├── daily-decision-digest.zh-TW.md
│   ├── daily-decision-digest.en.md
│   ├── agent-install-prompt.zh-TW.md
│   ├── agent-install-prompt.en.md
│   ├── agent-install-prompt.zh-CN.md
│   └── irreversible-operations-checklist.md
├── docs/
│   ├── automation/
│   │   └── daily-digest-v0.4.md
│   ├── install/
│   │   ├── agent-assisted-install.zh-TW.md
│   │   ├── agent-assisted-install.en.md
│   │   └── agent-assisted-install.zh-CN.md
│   └── plans/
├── examples/
├── logs/
├── articles/
├── scripts/
│   ├── build_daily_digest.py
│   ├── send_daily_digest.py
│   ├── validate_daily_digest.py
│   └── validate.py
└── tests/
```

## License

双授权：

- 程式码与自动化脚本：MIT
- 文档、模板、范例、文章：CC BY 4.0

建议署名：`AI Development Control Log` by Arthur Liao, licensed under CC BY 4.0.
