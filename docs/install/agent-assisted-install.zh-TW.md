# Agent-assisted install：讓 AI agent 幫你裝每日報告

> 使用者不用研究 GitHub Actions。使用者只選「報告寄去哪裡」；agent 負責設定、測試、啟用、回報。

## 先講清楚

**5 分鐘可完成的前提：你已經有該頻道的 webhook / token。**

如果你還沒有，agent 要先幫你建立或引導你建立。不要叫非工程使用者自己翻文件。

推薦路徑：

1. 第一次先選 **不外寄**，確認 artifact 會產生。
2. 確認報告內容可以接受後，再開 Slack / 飛書 / Telegram / Email。
3. 外寄頻道請選內部私人頻道，不要選客戶群或公開頻道；digest 會包含 commit 標題、作者、檔案路徑和風險提示。

## 支援頻道

| 頻道 | DELIVERY_PROVIDER | 需要的設定 |
|---|---|---|
| 不外寄 | `none` | 不需要 |
| Slack | `slack` | secret: `SLACK_WEBHOOK_URL` |
| 飛書 / Lark | `feishu` | secret: `FEISHU_WEBHOOK_URL` |
| Telegram | `telegram` | secrets: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` |
| Email / Resend | `email_resend` | secret: `RESEND_API_KEY`; variables: `EMAIL_FROM`, `EMAIL_TO` |

## 憑證怎麼拿？

agent 要照使用者選的頻道做，不要一次要求所有憑證。

### Slack

使用者需要一個 Slack Incoming Webhook URL。

給 agent 的指引：

1. 引導使用者到 Slack app 管理頁建立 Incoming Webhook。
2. 讓使用者選一個內部私人 channel。
3. 拿到長得像 `https://hooks.slack.com/services/...` 的 URL。
4. 不要把 URL 貼到 issue、PR、README 或 commit message。

### 飛書 / Lark

使用者需要一個自訂機器人的 webhook URL。

給 agent 的指引：

1. 請使用者在飛書群組新增「自訂機器人」。
2. 取得 webhook URL，通常長得像 `https://open.feishu.cn/open-apis/bot/v2/hook/...`。
3. 這版只支援一般 webhook；如果該 bot 開了簽名校驗，先關閉簽名，或等後續版本支援 signed webhook。
4. 請使用內部私人群組，不要用客戶群。

### Telegram

使用者需要 bot token 和 chat id。

給 agent 的指引：

1. 請使用者找 `@BotFather` 建 bot，取得 `TELEGRAM_BOT_TOKEN`。
2. 把 bot 加到目標群組或 DM。
3. 取得 `TELEGRAM_CHAT_ID`。
   - agent 可以用 Telegram API 或既有工具查。
   - 不確定時，不要猜 chat id。
4. 請使用內部私人群組，不要用公開群。

### Email / Resend

使用者需要 Resend API key、寄件地址、收件地址。

給 agent 的指引：

1. 使用者要先有 Resend 帳號。
2. 寄件地址 `EMAIL_FROM` 必須是 Resend 已允許的 sender / domain。
3. `EMAIL_TO` 可以是單一 email 或逗號分隔多個 email。
4. 如果 domain / sender 尚未驗證，先選 `none`，不要硬開外寄。

## 給 agent 的任務

把這段貼給 coding agent：

````text
請幫我安裝 AI Development Control Log 的每日 AI Decision Digest。

目標：
- 裝一次就忘。
- 每天自動產出一份 1 分鐘看得懂的報告。
- 報告可以寄到 Slack / 飛書 / Telegram / Email，或先不外寄。
- 不要把任何 token、webhook、secret 寫進 git、issue、PR、README 或 chat log。

請照以下 SOP 做：

1. 確認 repo 與 GitHub CLI：
   - gh auth status
   - gh repo view --json nameWithOwner
   - gh workflow list

2. 問我一個問題：
   「你要每天報告寄去哪裡？Slack / 飛書 / Telegram / Email / 不外寄」

3. 如果我還沒有該頻道憑證，請先引導我取得。不要叫我自己研究文件。

4. 設定 GitHub Actions variable：
   - 不外寄：gh variable set DELIVERY_PROVIDER --body none
   - Slack：gh variable set DELIVERY_PROVIDER --body slack
   - 飛書：gh variable set DELIVERY_PROVIDER --body feishu
   - Telegram：gh variable set DELIVERY_PROVIDER --body telegram
   - Email：gh variable set DELIVERY_PROVIDER --body email_resend

5. 設定 secrets / variables。請用 stdin，不要把 secret 印出來。

   Slack：
   ```bash
   read -rsp "Paste SLACK_WEBHOOK_URL: " SLACK_WEBHOOK_URL; echo
   printf '%s' "$SLACK_WEBHOOK_URL" | gh secret set SLACK_WEBHOOK_URL --body-file -
   unset SLACK_WEBHOOK_URL
   ```

   飛書 / Lark：
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

6. 本機先跑一次，不外寄：
   ```bash
   python -m pip install pytest pyyaml
   python scripts/build_daily_digest.py --output /tmp/digest.md --date $(date -u +%F)
   python scripts/validate_daily_digest.py /tmp/digest.md
   python scripts/send_daily_digest.py /tmp/digest.md --provider none
   python scripts/validate.py --mode repo
   python -m pytest tests/ -q
   ```

7. 觸發 GitHub Actions 真跑一次：
   ```bash
   gh workflow run daily-digest.yml --ref main
   sleep 3
   gh run list --workflow daily-digest.yml --limit 1 --json databaseId,status,conclusion,url
   gh run watch <RUN_ID> --interval 10 --exit-status
   ```

8. 驗證 artifact 真的產出：
   ```bash
   rm -rf /tmp/aidcl-artifact
   mkdir -p /tmp/aidcl-artifact
   gh run download <RUN_ID> --name daily-ai-decision-digest --dir /tmp/aidcl-artifact
   find /tmp/aidcl-artifact -type f -maxdepth 3 -print
   sed -n '1,40p' /tmp/aidcl-artifact/*
   ```

9. 如果我選了外寄，確認 workflow log 或目標頻道真的收到：
   - Delivery sent via slack
   - Delivery sent via feishu
   - Delivery sent via telegram
   - Delivery sent via email_resend

10. 用白話回報我：
   - 已設定哪個頻道
   - workflow run URL
   - artifact 檔名
   - 外寄是否成功
   - 若失敗，錯在哪一步
   - 之後怎麼關閉

安全規則：
- 不要印出 secret。
- 不要 commit secret。
- 不要把 webhook/token 貼到 issue、PR、README、commit message。
- 如果 secret 被貼出來，立刻請使用者 revoke / rotate，然後重設 GitHub secret。
- 如果不確定頻道是否安全，先設 DELIVERY_PROVIDER=none。
````

## 關閉 / rollback

### 只是不想外寄

```bash
gh variable set DELIVERY_PROVIDER --body none
```

### 外寄失敗，但 artifact 正常

1. 先關外寄：
   ```bash
   gh variable set DELIVERY_PROVIDER --body none
   ```
2. 保留 workflow；每天仍會產 artifact。
3. 修好 webhook/token 後再開。

### 想完全停掉每日 workflow

到 GitHub repo：Actions → Daily AI Decision Digest → Disable workflow。

或請 agent 用 GitHub API / UI 操作；不要刪 workflow 檔，避免未來不好恢復。

### secret 不小心曝光

1. 立刻到原服務 revoke / rotate 該 token/webhook/API key。
2. 重新設定 GitHub secret。
3. 檢查 issue、PR、commit、chat log 是否需要清理。
4. 再跑一次 workflow smoke。

## 成功回報範例

```text
已完成每日報告安裝。

- 頻道：不外寄 / Slack / 飛書 / Telegram / Email
- GitHub Actions：成功
- Run URL：https://github.com/.../actions/runs/...
- Artifact：daily-ai-decision-digest / 2026-06-05-digest.zh-TW.md
- 外寄：成功 / 未開啟 / 失敗但已關閉外寄

之後不想收：gh variable set DELIVERY_PROVIDER --body none
```
