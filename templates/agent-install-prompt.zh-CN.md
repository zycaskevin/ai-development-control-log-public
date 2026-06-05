# Agent 安装 Prompt（简中）

把这段贴给你的 coding agent。

```text
请帮我安装 AI Development Control Log 的每日 AI Decision Digest。

我要的结果：
- 装一次就忘。
- 每天自动产出一份 1 分钟看得懂的报告。
- 报告要能寄到我选择的频道：Slack / 飞书 / Telegram / Email / 不外寄。
- 如果我还没有凭证，请你引导我建立，不要叫我自己研究文件。
- 第一次不确定时，先设成不外寄，只验证 GitHub Actions artifact。

请照 docs/install/agent-assisted-install.zh-CN.md 做：
1. 确认 gh auth / repo / workflow。
2. 问我要寄到哪里。
3. 帮我安全设置 GitHub Actions variable/secrets。
4. 本机跑 build / validate / tests。
5. 触发 GitHub Actions 真的跑一次。
6. 下载 artifact 并确认内容不是空模板。
7. 如果我选外寄，确认真的送到目标频道。
8. 最后用白话回报 run URL、artifact、外寄状态、怎么关闭。

安全规则：
- 不要印出任何 token、webhook、API key。
- 不要把 secret 写进 git、issue、PR、README、commit message 或 chat log。
- 如果 secret 不小心曝光，先停下，叫我 revoke / rotate。
```
