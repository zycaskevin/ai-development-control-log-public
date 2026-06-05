# Task-Level Control Log v0.5

> Status: planned and implemented in v0.5.
> Companion to: `templates/task-control-log.zh-TW.md`,
> `templates/task-control-log.en.md`, `scripts/collect_task_logs.py`,
> and `scripts/build_daily_digest.py`.

## Why v0.5

v0.4 made the Daily AI Decision Digest real: it runs daily, builds a readable artifact, validates the 7-question structure, and optionally sends the report out.

But v0.4 still has a hard evidence limit: git activity can show **what changed**, but it cannot reliably show **why** it changed or **who authorized** it.

That is the exact gap a founder or product owner cares about:

- Which changes were explicitly requested by the user?
- Which decisions did AI make on its own?
- Did AI deviate from the spec?
- What evidence proves the work was verified?
- What rollback path exists if the AI overstepped?

v0.5 adds a small task-level log so agents record those answers while the task is still fresh. The daily digest then aggregates task logs first and uses git only as fallback.

## What changes in v0.5

- `templates/task-control-log.zh-TW.md` — zh-TW task log template with stable extractable headings.
- `templates/task-control-log.en.md` — English task log template using the same heading contract.
- `examples/task-control-log-agent-install-v0.5.zh-TW.md` — realistic example based on the v0.5 implementation task.
- `scripts/collect_task_logs.py` — rule-based Markdown parser for same-day task logs; it filters by Metadata `Date` or filename date and defensively redacts obvious raw secrets before rendering.
- `scripts/build_daily_digest.py` — now accepts `--task-log-dir` and uses same-day task logs to fill:
  - §2 user explicit requirements;
  - §3 AI self-decisions;
  - §4 spec deviations;
  - §5 high-risk touchpoints;
  - §6 verification evidence;
  - §7 rollback evidence.
- Tests prove that no-task-log repos keep the v0.4 conservative fallback.

## How agents should use v0.5

At the end of every meaningful AI coding task, write one file:

```text
logs/tasks/YYYY-MM-DD-<slug>.md
```

Use `templates/task-control-log.zh-TW.md` or `templates/task-control-log.en.md`.
The digest only reads logs whose Metadata `Date` or filename date matches the digest day, so old task logs do not repeat forever.

Minimum task prompt addition:

```text
任務完成後，請在 logs/tasks/YYYY-MM-DD-<slug>.md 寫一份 task-control-log，填入：使用者明確要求、AI 自決、偏離、驗證證據、rollback。不要寫入 secret/token/API key。
```

The log should be committed with the task when appropriate. If your repo cannot store task logs publicly, keep them private and run the digest in the private environment that can read them.

## What v0.5 does NOT do

- It does not call an LLM.
- It does not read chat history automatically.
- It does not guarantee the agent is honest; it creates a structured place to compare claims against evidence.
- It does not sign logs or make them append-only.
- It does not replace code review.
- It does not force task logs to exist. If no task logs exist, the digest falls back to v0.4 git-based conservative language.

## Evidence rules

Task logs are not allowed to contain raw secrets. Use env var names or placeholders:

- ✅ `SLACK_WEBHOOK_URL`
- ✅ `[REDACTED]`
- ❌ actual webhook URL
- ❌ actual API key

Verification must be concrete:

- ✅ `python -m pytest tests/test_collect_task_logs.py -q -> 8 passed`
- ✅ GitHub Actions run URL
- ✅ artifact path inspected
- ❌ `should work`
- ❌ `AI says it passed`

## Migration from v0.4.1 → v0.5

Existing users do not need to change anything immediately.

- If no `logs/tasks/*.md` files exist, the daily digest behaves like v0.4.1.
- If task logs exist, the digest uses them first.
- Delivery configuration is unchanged.
- Token cost remains zero by default.

## Recommended next versions

1. **v0.5.1** — Add stricter redaction checks for task logs if users start committing them to public repos.
2. **v0.6** — Optional LLM boss-summary layer that rewrites evidence into shorter human language without adding unsupported claims.
3. **v0.7** — Multi-agent / multi-repo digest split.
