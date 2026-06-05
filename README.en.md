# AI Development Control Log

[![validate](https://github.com/zycaskevin/ai-development-control-log/actions/workflows/validate.yml/badge.svg)](https://github.com/zycaskevin/ai-development-control-log/actions/workflows/validate.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> I may not understand every line of code an AI agent writes.
> But I need to know when it quietly made a decision for me.

[繁體中文](README.md) | [简体中文](README.zh-CN.md)

## What is this?

This is a control-log protocol for founders, product owners, indie builders, and AI operators who use coding agents.

It does not teach you how to code.

It teaches you how to manage an AI assistant that is very good at coding, but sometimes makes product, architecture, or risk decisions without telling you.

The scary part is not that AI writes bad code. Bad code can be fixed.

The scary part is when the agent thinks it is helping:

- You ask for a small feature, and it changes core calculation logic.
- You ask for a UI tweak, and it refactors a whole module.
- You ask for a new field, and it changes the database schema.
- You ask for a safer flow, and it changes auth or billing.

It may not be malicious. It may even be trying to be helpful.

But it did not tell you.

This repo is meant to fix that.

## One sentence

> Karpathy-style guidelines control how the AI writes code.
> AI Development Control Log controls whether the AI overstepped.

## You do not need to read code

You need to read the decision record:

- What did the AI change?
- Which changes were explicitly requested?
- Which decisions did the AI make on its own?
- Did it deviate from the spec?
- Did it touch data, payments, production, permissions, or core calculations?
- What was verified?
- What was not verified?
- How do we roll back if this goes wrong?

These are human-readable questions.

## Where this comes from

This combines two ideas.

First, Karpathy-style coding guidelines:

- Think before coding: surface assumptions before implementation.
- Simplicity first: do not overbuild.
- Surgical changes: only touch what the task requires.
- Goal-driven execution: define success criteria and verify them.

Second, the Control Log:

- Write down assumptions.
- Separate explicit user requirements from AI-made decisions.
- Record deviations from the spec.
- Record tradeoffs.
- Stop before irreversible operations.
- Record verification and rollback.

Karpathy guidelines help the AI write less bad code.

The Control Log stops the AI from quietly acting like the boss.

## When should you use it?

Use it when a mistake would hurt.

Especially for:

- payments, billing, subscriptions, commissions
- user data, CRM, privacy data
- database schema, migrations, bulk updates
- production deploys, cutovers, webhooks, gateways
- auth, permissions, secrets
- core calculation logic
- multi-agent development work
- anything you do not fully understand but cannot afford to break

Skip it for typos, one-line copy edits, and low-risk reversible changes.

## The most important rules

### 1. Every changed line must trace to the request

> Every changed line should trace directly to the user's request.

If you asked the AI to change button copy and it modified billing logic, that is not "cleanup".

That is overreach.

### 2. AI-made decisions must be listed separately

The AI may suggest. It may propose a better path.

It must not silently choose for you.

### 3. Irreversible operations require confirmation

The AI must stop before:

- deleting data
- changing database schema
- deploying to production
- changing payments, billing, or subscriptions
- changing auth, permissions, or secrets
- changing core calculation logic
- doing broad refactors outside the request

It should stop before the action, not explain afterward.

### 4. "Done" is not evidence

The agent must write:

- which tests it ran
- which checks passed
- what was not tested
- what is only an assumption
- how to roll back

Every report should also label its credibility first:

```text
✅ Verified: backed by tool output, tests, live smoke, or production checks
⚠️ Partially verified: only part of the claim was checked, or live / production evidence is missing
❌ Unverified: based on reasoning, reading, or assumptions without real execution
```

Test types should be explicit. Do not present a mock test as proof that the real system works:

```text
mock: simulated behavior only
unit: unit tests passed
integration: integration tests passed
live smoke: a real CLI / API / service was exercised at minimum depth
production verified: production was checked directly
```

## Does it write or send daily logs automatically?

**As of v0.4: yes — and the user does not need to hand-edit the workflow. As of v0.5: if the agent writes task logs, the daily digest uses task-level evidence before falling back to git.**

What happens by default:

- The workflow runs daily at 02:00 UTC (= 10:00 Asia/Taipei)
- It builds a readable `logs/daily/YYYY-MM-DD-digest.zh-TW.md` from the last 24 hours of git activity
- If `logs/tasks/*.md` task control logs exist, it uses them to list explicit user requests and AI self-decisions
- If no task logs exist, it keeps the v0.4 git-based fallback and says what it cannot reliably know
- It answers the 7 control questions: what AI did, what AI decided, high-risk touches, verification, rollback
- It uploads the digest as a workflow artifact
- If an agent configures delivery, it can send to Slack / Feishu / Telegram / Email
- If no delivery provider is configured, it does not send externally
- It does not call an LLM by default, so daily model-token cost is 0

Want it working in 5 minutes? See: [**5-minute setup guide: let an agent install it**](#5-minute-setup-guide-let-an-agent-install-it).

Earlier versions (pre-v0.4) followed the "manual SOP, no auto-run" philosophy.
v0.4 upgrades this to "**daily readable report, with delivery installed by an agent**".
The v0.4 digest also answers different questions than v0.3.1 — see the
comparison below.

### v0.3.1 vs v0.4 daily digest — what changed?

| Question | v0.3.1 digest | v0.4 digest |
|---|---|---|
| What did AI do today? | commit / PR titles | each action tagged ✅/⚠️/❌ for who asked |
| What did AI decide on its own? | free-text paragraph | table + "should it have asked first?" column |
| Did it deviate from spec? | free-text | table + "needs user confirmation?" column |
| Were any high-risk gates triggered? | free-text | 8 risk items, each ✅/❌ |
| What was verified / not verified? | free-text | table, "not verified" is mandatory |
| If it breaks, how to roll back? | free-text | table + "rollback actually verified?" |
| Can the user read this? | **no** | §8 explicitly asks ✅/⚠️/❌ |
| 1-minute skim summary | **no** | §0 1-minute block (for the boss) |

v0.4's digest exists so the boss can catch AI overstepping. It is not
an "AI employee bragging report". If you want progress tracking (PRs,
issues, commits), use GitHub's own daily digest.

### What does v0.5 add?

v0.4's limit is evidence: git can show **what changed**, but not reliably **whether the user asked for it or AI decided it alone**.

v0.5 adds task-level control logs:

- Templates: `templates/task-control-log.zh-TW.md` / `templates/task-control-log.en.md`
- Suggested path: `logs/tasks/YYYY-MM-DD-<slug>.md`
- Parser: `scripts/collect_task_logs.py`
- Daily digest: uses task logs first; falls back to the conservative v0.4 git language when absent

In practice: if the agent writes one small task log at the end of each task, tomorrow's digest can distinguish explicit user requests from AI self-decisions.

## 5-minute setup guide: let an agent install it

**Goal**: after forking this repo, start receiving a daily readable report within 5 minutes.

Do not edit the workflow yourself. Give this to your coding agent:

```text
Please install the AI Development Control Log daily report for me.
I want a daily 1-minute readable digest.
Follow docs/install/agent-assisted-install.en.md: choose a delivery channel with me, configure GitHub Actions secrets, trigger the workflow, download the artifact, and verify delivery.
Do not commit any token / webhook / secret.
```

The agent should ask you only one setup question:

> Where should the daily report be delivered? Slack / Feishu / Telegram / Email / no external delivery

Then the agent does the work:

1. Set `DELIVERY_PROVIDER`
2. Save webhook / token values into GitHub Actions secrets
3. Build and validate one local digest
4. Trigger the GitHub Actions workflow once
5. Confirm the artifact was created
6. If delivery is enabled, confirm the message was actually sent

Full agent task card: [`docs/install/agent-assisted-install.en.md`](docs/install/agent-assisted-install.en.md).
Copyable prompt: [`templates/agent-install-prompt.en.md`](templates/agent-install-prompt.en.md).

### How do I turn it off later?

Ask the agent to run:

```bash
gh variable set DELIVERY_PROVIDER --body none
```

Or delete the relevant webhook secret.

## Language selection

Control logs and daily digests should not be hardcoded to English. Each log should declare:

```text
Output language: zh-TW / zh-CN / en / ja / custom
Audience: founder / operator / engineer / customer / internal team
Tone: plain / technical / executive summary / customer-readable
Translate technical terms into plain language: yes / no
```

For founder / operator internal use, the default is:

```text
Language: Traditional Chinese zh-TW
Tone: plain, CEO-readable, minimal technical jargon
```

Public repositories can still include English docs, but non-English users should have first-class readable templates.

## Quick start

### Option A: Use only the template

For Traditional Chinese users, copy the zh-TW template first:

```bash
cp templates/implementation-control-log.zh-TW.md ./implementation-control-log.md
```

For English or mixed-language teams, use the English / bilingual template:

```bash
cp templates/implementation-control-log.md ./implementation-control-log.md
```

Then tell your agent:

> For this task, update `implementation-control-log.md` as you work. Do not backfill it at the end. Record AI-made decisions, spec deviations, high-risk operations, verification, and rollback.

### Option B: Claude Code

Merge [`CLAUDE.md`](CLAUDE.md) into your project `CLAUDE.md`.

### Option C: Cursor

Copy the Cursor rule:

```bash
mkdir -p .cursor/rules
cp .cursor/rules/ai-development-control-log.mdc your-project/.cursor/rules/
```

### Option D: Hermes / agent skill

Use:

```text
skills/ai-development-control-log/SKILL.md
```

## Template

Task-level control-log templates:

- [`templates/implementation-control-log.zh-TW.md`](templates/implementation-control-log.zh-TW.md): Traditional Chinese template for Chinese-speaking users
- [`templates/implementation-control-log.md`](templates/implementation-control-log.md): English / bilingual-field template for English or mixed-language teams
- [`templates/task-control-log.zh-TW.md`](templates/task-control-log.zh-TW.md): v0.5 task-level evidence log for user-request vs AI-self-decision evidence
- [`templates/task-control-log.en.md`](templates/task-control-log.en.md): v0.5 English task-level evidence log

Daily Decision Digest templates:

- [`templates/daily-decision-digest.zh-TW.md`](templates/daily-decision-digest.zh-TW.md): Traditional Chinese daily AI decision digest
- [`templates/daily-decision-digest.en.md`](templates/daily-decision-digest.en.md): English daily AI decision digest

Delivery automation docs and templates:

- [`docs/automation/optional-delivery-automation.md`](docs/automation/optional-delivery-automation.md): optional delivery safety rules
- [`templates/daily-digest-delivery-config.zh-TW.md`](templates/daily-digest-delivery-config.zh-TW.md): Traditional Chinese delivery config template
- [`templates/daily-digest-delivery-config.en.md`](templates/daily-digest-delivery-config.en.md): English delivery config template

Core sections:

0. Language and audience settings
1. Task goal
2. Explicit user requirements
3. Open questions / assumptions
4. AI-made decisions
5. Spec deviations
6. Surgical-change traceability
7. Tradeoffs
8. High-risk / irreversible operation check
9. Verification results
10. Rollback plan

When reporting back, also include the credibility label, test type labels, and the real tool output that supports the conclusion.


## Validation script

This repo includes a lightweight validation script: [`scripts/validate.py`](scripts/validate.py).

It does not test your product. It checks that the protocol kit / repo is still structurally complete:

- required files exist and are not empty
- `SKILL.md` has basic frontmatter
- `templates/implementation-control-log.md` and `templates/implementation-control-log.zh-TW.md` still contain the required core sections
- Daily Digest / delivery automation templates still contain their safety sections
- examples and articles remain in the expected paths

### Validation modes

```bash
python scripts/validate.py --mode repo
python scripts/validate.py --mode kit
python scripts/validate.py --mode strict
```

| mode | Use case | Requires a private live log |
|---|---|---|
| `repo` | Maintains this protocol repo itself; default mode | ❌ no; uses public-safe examples |
| `kit` | For fork / starter-kit users | ❌ no; uses public-safe examples |
| `strict` | CI / maintainer strict check; currently equivalent to `repo` | ❌ no; uses public-safe examples |

Default run:

```bash
python scripts/validate.py
```

Equivalent to:

```bash
python scripts/validate.py --mode repo
```

Successful output:

```text
VALIDATION PASSED (repo mode)
```

Failure output lists the exact missing item, for example:

```text
VALIDATION FAILED (repo mode)
- missing: templates/implementation-control-log.md
- template missing section: Verification Results
```

GitHub Actions runs repo-mode validation and the unit tests on push and pull request.

## Examples

- [`examples/calc-feature-control-log.md`](examples/calc-feature-control-log.md): feature near core calculation logic
- [`examples/billing-change-control-log.md`](examples/billing-change-control-log.md): billing / subscription change
- [`examples/database-migration-control-log.md`](examples/database-migration-control-log.md): database migration and rollback
- [`examples/multi-round-control-log.md`](examples/multi-round-control-log.md): one task with multiple log updates
- [`examples/daily-decision-digest.zh-TW.md`](examples/daily-decision-digest.zh-TW.md): Traditional Chinese daily decision digest example
- [`examples/daily-decision-digest.en.md`](examples/daily-decision-digest.en.md): English daily decision digest example
- [`examples/language-selection-control-log.zh-TW.md`](examples/language-selection-control-log.zh-TW.md): Traditional Chinese language-selection control log example
- [`examples/github-actions-daily-digest.yml`](examples/github-actions-daily-digest.yml): GitHub Actions local-only digest artifact example
- [`examples/hermes-cron-daily-digest.zh-TW.md`](examples/hermes-cron-daily-digest.zh-TW.md): Hermes cron daily digest example

## Shareable article

- [`articles/manage-ai-engineer-with-control-log.md`](articles/manage-ai-engineer-with-control-log.md)

## License

MIT
