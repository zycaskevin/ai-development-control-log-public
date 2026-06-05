# Task Control Log — <task name>

> Purpose: feed the Daily AI Decision Digest with task-level evidence. This is not a bragging report. It records what the user explicitly asked for, what AI decided on its own, where risk exists, and how to roll back.
>
> Suggested path: `logs/tasks/YYYY-MM-DD-<slug>.md`

## Metadata

- Date: YYYY-MM-DD
- Actor: <agent / human name>
- Repo: <repo name>
- Branch: <branch name>
- Commit / PR: <commit sha / PR URL / pending>

## User explicitly asked

> Only write what the user actually said or clearly requested. AI inference does not count.

- <direct quote or faithful paraphrase of the user request>

## AI self-decided

> List decisions AI made without explicit user instruction, especially decisions affecting product, architecture, data, permissions, payments, workflows, releases, or external effects.

- Decision: <what AI decided>
  Rationale: <why>
  Should have asked user first: yes/no/gray

## Spec deviations

> If there was no deviation, write `- none`. If there was a deviation, record the original spec, actual implementation, reason, and whether user confirmation is needed.

- Deviation: <deviation>
  Original spec: <original requirement / spec>
  Actual implementation: <what actually happened>
  Reason: <why it deviated>
  Needs user confirmation: yes/no/gray

## High-risk touchpoints

> List any DB, auth, secret, payment, production, workflow, webhook, core calculation, external publishing, or broad refactor touchpoint.

- Path / operation: <file path or operation>
  Risk type: <db/auth/secret/payment/production/workflow/webhook/core-calc/publish/refactor/other>
  User confirmed: yes/no/partial
  Rollback path: <how to roll back>

## Verification evidence

> Paste real evidence. Do not write "should work". If not verified, say `not verified`.
> ⚠️ Do not paste raw tokens, webhook URLs, API keys, Authorization headers,
> cookies, passwords, or full `.env` output. If evidence contains a secret,
> replace it with `[REDACTED]` first.

- Claim: <what conclusion did you verify?>
  Verification type: unit / integration / workflow / sandbox / manual / not verified
  Raw evidence: <command output / CI URL / artifact path / pending; secrets must be [REDACTED]>

## Rollback evidence

> "Can revert" is not evidence. Write the concrete procedure; if not verified, say partial/no.
> ⚠️ Rollback instructions must not include raw tokens, webhook URLs, API
> keys, or passwords. Refer to secret names or `[REDACTED]` values instead.

- Failure scenario: <what failure should trigger rollback?>
  Rollback command / toggle / procedure: <exact rollback procedure; secrets must be [REDACTED]>
  Verified rollback: yes / partial / no

## Human-readable final summary

> Three lines or fewer for the boss.

- <what changed, where the risk is, and what remains>
