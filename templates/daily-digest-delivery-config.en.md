# Daily Digest Delivery Config

> Purpose: define who receives the Daily AI Decision Digest, in what tone, and when delivery must stop.

## 1. Automation is optional, not default

| Field | Value |
|---|---|
| Delivery enabled | yes / no |
| Default mode | local only / draft-first / send |
| Owner | operator / team / custom |
| Output language | zh-TW / en / custom |
| Audience | founder / engineer / customer / internal team |
| Tone | executive summary / technical / customer-readable |

Recommended default:

```text
Delivery enabled: no
Default mode: local only
```

## 2. Delivery channels

| Channel | Target | Mode | Notes |
|---|---|---|---|
| local file | logs/daily/ | send | lowest risk |
| GitHub Actions artifact | workflow artifact | draft-first | repo-scoped evidence |
| Hermes cron | origin chat | draft-first / send | internal assistant workflow |
| Feishu / Lark | group or DM | draft-first | team digest |
| Email / Telegram | address / chat | draft-first | external channels need explicit approval |

## 3. Safety gates

| Gate | Check | Result | If failed |
|---|---|---|---|
| Secret / token | no token, cookie, private key | pass / fail | stop delivery |
| PII | no unauthorized customer data | pass / fail | stop delivery |
| Internal state | no dry-run / preview / committed leakage to customers | pass / fail | rewrite or stop |
| Verification label | every claim has ✅ / ⚠️ / ❌ | pass / fail | add labels |
| High-risk operation | production / auth / billing / DB schema | pass / fail | draft-first |
| Audience match | tone matches recipient | pass / fail | regenerate audience version |

## 4. Verification evidence

| Evidence | Value |
|---|---|
| Digest path / URL |  |
| Delivery mode used | local only / draft-first / send |
| Tool output |  |
| Safety gate result |  |
| Credibility | ✅ Verified / ⚠️ Partially verified / ❌ Unverified |

## 5. Rollback

| Failure | Rollback |
|---|---|
| wrong channel | pause schedule, remove channel mapping |
| wrong digest content | keep evidence, publish correction |
| missed gate | stop automation, fix gate/template, rerun validation |
| cost too high | reduce frequency, switch to local-only, shorten digest |
