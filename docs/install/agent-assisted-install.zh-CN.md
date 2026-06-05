# Agent-assisted install：让 AI agent 帮你装每日报告

> 使用者不用研究 GitHub Actions。使用者只选择「报告寄到哪里」；agent 负责设置、测试、启用、回报。

## 先说清楚

**5 分钟可完成的前提：你已经有该频道的 webhook / token。**

如果还没有，agent 要先帮你建立或引导你建立。不要叫非工程使用者自己翻文件。

推荐路径：

1. 第一次先选 **不外寄**，确认 artifact 会产生。
2. 确认报告内容可以接受后，再开 Slack / 飞书 / Telegram / Email。
3. 外寄频道请选择内部私人频道，不要选客户群或公开频道；digest 会包含 commit 标题、作者、文件路径和风险提示。

## 支持频道

| 频道 | DELIVERY_PROVIDER | 需要的设置 |
|---|---|---|
| 不外寄 | `none` | 不需要 |
| Slack | `slack` | secret: `SLACK_WEBHOOK_URL` |
| 飞书 / Lark | `feishu` | secret: `FEISHU_WEBHOOK_URL` |
| Telegram | `telegram` | secrets: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` |
| Email / Resend | `email_resend` | secret: `RESEND_API_KEY`; variables: `EMAIL_FROM`, `EMAIL_TO` |

## 凭证怎么拿？

agent 要照使用者选择的频道做，不要一次要求所有凭证。

### Slack

建立一个 Slack Incoming Webhook URL，频道请选择内部私人频道。URL 通常长得像 `https://hooks.slack.com/services/...`。

### 飞书 / Lark

在飞书群组新增自定义机器人，取得 webhook URL，通常长得像 `https://open.feishu.cn/open-apis/bot/v2/hook/...`。这版只支持普通 webhook；如果 bot 开了签名校验，先关闭签名，或等后续版本支持 signed webhook。

### Telegram

使用 `@BotFather` 建 bot，取得 `TELEGRAM_BOT_TOKEN`。把 bot 加到目标聊天，再取得 `TELEGRAM_CHAT_ID`。不确定时不要猜 chat id。

### Email / Resend

使用 Resend API key。`EMAIL_FROM` 必须是 Resend 已允许的 sender / domain。`EMAIL_TO` 可以是单一 email 或逗号分隔多个 email。

## 给 agent 的任务

把这段贴给 coding agent：

````text
请帮我安装 AI Development Control Log 的每日 AI Decision Digest。

目标：
- 装一次就忘。
- 每天自动产出一份 1 分钟看得懂的报告。
- 报告可以寄到 Slack / 飞书 / Telegram / Email，或先不外寄。
- 不要把任何 token、webhook、secret 写进 git、issue、PR、README 或 chat log。

请照以下 SOP 做：

1. 确认 repo 与 GitHub CLI：
   - gh auth status
   - gh repo view --json nameWithOwner
   - gh workflow list

2. 问我一个问题：
   「你要每日报告寄到哪里？Slack / 飞书 / Telegram / Email / 不外寄」

3. 如果我还没有该频道凭证，请先引导我取得。不要叫我自己研究文件。

4. 设置 GitHub Actions variable：
   - 不外寄：gh variable set DELIVERY_PROVIDER --body none
   - Slack：gh variable set DELIVERY_PROVIDER --body slack
   - 飞书：gh variable set DELIVERY_PROVIDER --body feishu
   - Telegram：gh variable set DELIVERY_PROVIDER --body telegram
   - Email：gh variable set DELIVERY_PROVIDER --body email_resend

5. 设置 secrets / variables。请用 stdin，不要把 secret 印出来。

   Slack：
   ```bash
   read -rsp "Paste SLACK_WEBHOOK_URL: " SLACK_WEBHOOK_URL; echo
   printf '%s' "$SLACK_WEBHOOK_URL" | gh secret set SLACK_WEBHOOK_URL --body-file -
   unset SLACK_WEBHOOK_URL
   ```

   飞书 / Lark：
   ```bash
   read -rsp "Paste FEISHU_WEBHOOK_URL: " FEISHU_WEBHOOK_URL; echo
   printf '%s' "$FEISHU_WEBHOOK_URL" | gh secret set FEISHU_WEBHOOK_URL --body-file -
   unset FEISHU_WEBHOOK_URL
   ```

   Telegram：
   ```bash
   read -rsp "Paste TELEGRAM_BOT_TOKEN: " TELEGRAM_BOT_TOKEN; echo
   printf '%s' "$TELEGRAM_BOT_TOKEN" | gh secret set TELEGRAM_BOT_TOKEN --body-file -
   unset TELEGRAM_BOT_TOKEN

   read -rsp "Paste TELEGRAM_CHAT_ID: " TELEGRAM_CHAT_ID; echo
   printf '%s' "$TELEGRAM_CHAT_ID" | gh secret set TELEGRAM_CHAT_ID --body-file -
   unset TELEGRAM_CHAT_ID
   ```

   Email / Resend：
   ```bash
   read -rsp "Paste RESEND_API_KEY: " RESEND_API_KEY; echo
   printf '%s' "$RESEND_API_KEY" | gh secret set RESEND_API_KEY --body-file -
   unset RESEND_API_KEY

   gh variable set EMAIL_FROM --body "digest@example.com"
   gh variable set EMAIL_TO --body "boss@example.com"
   ```

6. 本机先跑一次，不外寄：
   ```bash
   python -m pip install pytest pyyaml
   python scripts/build_daily_digest.py --output /tmp/digest.md --date $(date -u +%F)
   python scripts/validate_daily_digest.py /tmp/digest.md
   python scripts/send_daily_digest.py /tmp/digest.md --provider none
   python scripts/validate.py --mode repo
   python -m pytest tests/ -q
   ```

7. 触发 GitHub Actions 真的跑一次：
   ```bash
   gh workflow run daily-digest.yml --ref main
   sleep 3
   gh run list --workflow daily-digest.yml --limit 1 --json databaseId,status,conclusion,url
   gh run watch <RUN_ID> --interval 10 --exit-status
   ```

8. 验证 artifact 真的产出：
   ```bash
   rm -rf /tmp/aidcl-artifact
   mkdir -p /tmp/aidcl-artifact
   gh run download <RUN_ID> --name daily-ai-decision-digest --dir /tmp/aidcl-artifact
   find /tmp/aidcl-artifact -type f -maxdepth 3 -print
   sed -n '1,40p' /tmp/aidcl-artifact/*
   ```

9. 如果我选择外寄，确认目标频道或 workflow log 真的显示发送成功。

10. 用白话回报我：频道、run URL、artifact 文件名、外寄结果、失败原因、怎么关掉。
````

## 关闭 / rollback

只是不想外寄：

```bash
gh variable set DELIVERY_PROVIDER --body none
```

如果 workflow 成功但外寄失败，先把 provider 设成 `none`，保留 artifact 生成，修好凭证后再开。

如果想完全停止每日 workflow，到 GitHub Actions：Actions → Daily AI Decision Digest → Disable workflow。

如果 secret 不小心曝光，立刻到原服务 revoke / rotate，重新设置 GitHub secret，清理曝光位置，再重跑 smoke test。
