# Agent Install Prompt (English)

Paste this into your coding agent.

```text
Please install the AI Development Control Log daily AI Decision Digest for me.

Desired result:
- Install once, then forget it.
- Generate a daily 1-minute readable report.
- Deliver to my selected channel: Slack / Feishu / Telegram / Email / no external delivery.
- If I do not have credentials yet, guide me to create them safely instead of sending me to read docs.
- If unsure, start with no external delivery and verify the GitHub Actions artifact first.

Follow docs/install/agent-assisted-install.en.md:
1. Check gh auth / repo / workflow.
2. Ask where the report should go.
3. Configure GitHub Actions variable/secrets safely.
4. Run local build / validation / tests.
5. Trigger the real GitHub Actions workflow once.
6. Download the artifact and confirm it is not an empty template.
7. If delivery is enabled, confirm the target channel really received it.
8. Report back in plain language: run URL, artifact, delivery status, and how to turn it off.

Safety rules:
- Do not print any token, webhook, or API key.
- Do not put secrets in git, issues, PRs, README, commit messages, or chat logs.
- If a secret is exposed, stop and ask me to revoke / rotate it.
```
