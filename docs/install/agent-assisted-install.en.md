# Agent-assisted install: let an AI agent install the daily report

> The user should not need to learn GitHub Actions. The user chooses where the report should go; the agent configures, tests, enables, and reports back.

## First: set expectations

**The 5-minute path assumes the delivery credential already exists.**

If it does not exist, the agent must guide the user to create it safely. Do not tell a non-engineering founder to go read a pile of docs.

Recommended path:

1. Start with **no external delivery** and verify the artifact first.
2. After the report content looks safe, enable Slack / Feishu / Telegram / Email.
3. Use a private internal channel. The digest can include commit subjects, author names, touched paths, and risk labels.

## Supported channels

| Channel | DELIVERY_PROVIDER | Required setup |
|---|---|---|
| No external delivery | `none` | none |
| Slack | `slack` | secret: `SLACK_WEBHOOK_URL` |
| Feishu / Lark | `feishu` | secret: `FEISHU_WEBHOOK_URL` |
| Telegram | `telegram` | secrets: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` |
| Email / Resend | `email_resend` | secret: `RESEND_API_KEY`; variables: `EMAIL_FROM`, `EMAIL_TO` |

## How to get credentials

The agent should only guide the channel the user selected.

### Slack

Create a Slack Incoming Webhook URL for a private internal channel. The URL should look like `https://hooks.slack.com/services/...`.

### Feishu / Lark

Create a custom bot webhook in a private internal group. This version supports ordinary webhook URLs such as `https://open.feishu.cn/open-apis/bot/v2/hook/...`. If the bot requires signature verification, disable signing for now or wait for signed-webhook support.

### Telegram

Use `@BotFather` to create a bot and get `TELEGRAM_BOT_TOKEN`. Add the bot to the target chat, then get `TELEGRAM_CHAT_ID`. Do not guess chat ids.

### Email / Resend

Use a Resend API key. `EMAIL_FROM` must be an approved sender/domain. `EMAIL_TO` can be one email or comma-separated emails.

## Agent task

Give this to the coding agent:

````text
Please install the AI Development Control Log daily AI Decision Digest.

Goal:
- Install once, then forget it.
- Generate a daily 1-minute readable report.
- Deliver to Slack / Feishu / Telegram / Email, or keep artifact-only.
- Do not commit, print, or paste any token/webhook/secret into git, issues, PRs, README, or chat logs.

SOP:

1. Confirm repo and GitHub CLI:
   - gh auth status
   - gh repo view --json nameWithOwner
   - gh workflow list

2. Ask me one question:
   "Where should the daily report go? Slack / Feishu / Telegram / Email / no external delivery"

3. If I do not have credentials yet, guide me to create them safely.

4. Set the GitHub Actions variable:
   - no external delivery: gh variable set DELIVERY_PROVIDER --body none
   - Slack: gh variable set DELIVERY_PROVIDER --body slack
   - Feishu: gh variable set DELIVERY_PROVIDER --body feishu
   - Telegram: gh variable set DELIVERY_PROVIDER --body telegram
   - Email: gh variable set DELIVERY_PROVIDER --body email_resend

5. Set secrets / variables using stdin. Do not print secrets.

   Slack:
   ```bash
   read -rsp "Paste SLACK_WEBHOOK_URL: " SLACK_WEBHOOK_URL; echo
   printf '%s' "$SLACK_WEBHOOK_URL" | gh secret set SLACK_WEBHOOK_URL --body-file -
   unset SLACK_WEBHOOK_URL
   ```

   Feishu / Lark:
   ```bash
   read -rsp "Paste FEISHU_WEBHOOK_URL: " FEISHU_WEBHOOK_URL; echo
   printf '%s' "$FEISHU_WEBHOOK_URL" | gh secret set FEISHU_WEBHOOK_URL --body-file -
   unset FEISHU_WEBHOOK_URL
   ```

   Telegram:
   ```bash
   read -rsp "Paste TELEGRAM_BOT_TOKEN: " TELEGRAM_BOT_TOKEN; echo
   printf '%s' "$TELEGRAM_BOT_TOKEN" | gh secret set TELEGRAM_BOT_TOKEN --body-file -
   unset TELEGRAM_BOT_TOKEN

   read -rsp "Paste TELEGRAM_CHAT_ID: " TELEGRAM_CHAT_ID; echo
   printf '%s' "$TELEGRAM_CHAT_ID" | gh secret set TELEGRAM_CHAT_ID --body-file -
   unset TELEGRAM_CHAT_ID
   ```

   Email / Resend:
   ```bash
   read -rsp "Paste RESEND_API_KEY: " RESEND_API_KEY; echo
   printf '%s' "$RESEND_API_KEY" | gh secret set RESEND_API_KEY --body-file -
   unset RESEND_API_KEY

   gh variable set EMAIL_FROM --body "digest@example.com"
   gh variable set EMAIL_TO --body "boss@example.com"
   ```

6. Run local smoke without external delivery:
   ```bash
   python -m pip install pytest pyyaml
   python scripts/build_daily_digest.py --output /tmp/digest.md --date $(date -u +%F)
   python scripts/validate_daily_digest.py /tmp/digest.md
   python scripts/send_daily_digest.py /tmp/digest.md --provider none
   python scripts/validate.py --mode repo
   python -m pytest tests/ -q
   ```

7. Trigger the real GitHub workflow:
   ```bash
   gh workflow run daily-digest.yml --ref main
   sleep 3
   gh run list --workflow daily-digest.yml --limit 1 --json databaseId,status,conclusion,url
   gh run watch <RUN_ID> --interval 10 --exit-status
   ```

8. Verify the artifact:
   ```bash
   rm -rf /tmp/aidcl-artifact
   mkdir -p /tmp/aidcl-artifact
   gh run download <RUN_ID> --name daily-ai-decision-digest --dir /tmp/aidcl-artifact
   find /tmp/aidcl-artifact -type f -maxdepth 3 -print
   sed -n '1,40p' /tmp/aidcl-artifact/*
   ```

9. If external delivery is enabled, confirm the target channel or workflow log says delivery succeeded.

10. Report back in plain language: provider, run URL, artifact filename, delivery result, failure if any, and how to turn it off.
````

## Turn off / rollback

Only stop external delivery:

```bash
gh variable set DELIVERY_PROVIDER --body none
```

If workflow succeeds but delivery fails, set provider to `none`, keep artifact generation, fix the credential, then re-enable delivery.

To fully stop daily runs, disable the workflow in GitHub Actions: Actions → Daily AI Decision Digest → Disable workflow.

If a secret is exposed, revoke/rotate it at the original service, reset the GitHub secret, clean the exposed location if needed, and rerun a smoke test.
