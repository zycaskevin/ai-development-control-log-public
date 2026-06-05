# Implementation Control Log (v0.3.1 — with Actor metadata)

> v0.3.1 changes from v0.3:
> - Section 0.5 (Actor & Provenance) is now **hard required**. The
>   `scripts/validate.py` gate refuses to pass a v0.3.1 log whose
>   0.5 section is missing the Agent model / session / approver /
>   approval evidence / wall clock fields.
> - **Self-approval is forbidden when 9.5.6 has high-risk rows.**
>   The gate refuses to pass a v0.3.1 log whose 9.5.6 table lists
>   one or more high-risk touchpoints AND whose 0.5 lists
>   `Human approver: self-approved`. The v0.3.0 behaviour (just
>   informational) is removed.
> - A new script `scripts/collect_actor_metadata.py` autofills
>   Agent model, Agent session, and Wall clock fields from the
>   `HERMES_AGENT_MODEL` / `HERMES_AGENT_SESSION` / `HERMES_TASK_ID`
>   environment variables, so the agent can produce a complete
>   0.5 block in one command.

## 0. 語言與讀者設定

| 欄位 | 值 |
|---|---|
| 輸出語言 | zh-TW / zh-CN / en / ja / custom |
| 讀者 | founder / operator / engineer / customer / internal team |
| 語氣 | 白話 / 技術 / 高層摘要 / 客戶可讀 |
| 技術名詞是否翻成人話 | Yes / No |

## 0.5 Actor & Provenance (v0.3.1 — required)

> **v0.3.1:** All six rows are required. Validation refuses to
> pass this log if any are empty.
>
> **Self-approval is forbidden when 9.5.6 has high-risk rows.**
> If 9.5.6 contains a row of category `payment`, `db-schema`,
> `auth`, `secret`, `production-config`, `core-calculation`, or
> `external-side-effect`, then `Human approver` MUST be a GitHub
> handle (e.g. `@maintainer`), NOT `self-approved`.
>
> **Approval evidence** must be a URL — a PR review URL, an
> issues link, a documented decision in a meeting note, or
> `no human in loop` (which forces a high-risk check).
>
> **Wall clock** fields must be ISO-8601 timestamps. The agent
> autofills them via `scripts/collect_actor_metadata.py`; a human
> reviewer can correct the values if they are wrong.

| Field | Value | Required? | Validation rule |
|---|---|---|---|
| Agent model       |  | yes | non-empty |
| Agent session     |  | yes | non-empty |
| Human approver    |  | yes | non-empty; not `self-approved` when 9.5.6 has high-risk rows |
| Approval evidence |  | yes | non-empty; URL or `no human in loop` |
| Wall clock start  |  | yes | ISO-8601 |
| Wall clock end    |  | yes | ISO-8601; must be ≥ start |

How to autofill (agent side):

```bash
$ python scripts/collect_actor_metadata.py

## 0.5 Actor & Provenance (autofilled)

| Field | Value |
|---|---|
| Agent model       | minimax-m3 |
| Agent session     | 2026-06-04T22:00:00Z-7a3b1c |
| Human approver    |  |
| Approval evidence |  |
| Wall clock start  | 2026-06-04T22:00:00Z |
| Wall clock end    | 2026-06-04T22:05:30Z |
```

A human fills `Human approver` and `Approval evidence` after review.

## 1. Task Goal

### Timeline

| Field | Value |
|---|---|
| Task started at |  |
| Last updated at |  |

### Goal
-

### Non-goals / Out of Scope
-

### Success Criteria
- [ ]

## 2. Explicit User Requirements

These are requirements the user explicitly stated.

-

## 3. Open Questions and Assumptions

| Question / ambiguity | Current assumption | If wrong, cost to change (Low/Medium/High) | Needs user confirmation? |
|---|---|---:|---|
|  |  |  |  |
| Example: Should this touch production config? | No, local / staging only | High | Yes before production |

## 4. AI-Made Decisions

These are choices the AI made because the user did not specify them.

| Decision | Why this choice | Alternatives considered | Risk |
|---|---|---|---|
|  |  |  |  |

## 5. Spec Deviations

Cases where the user asked for A, but the implementation did B.

| Deviation | Reason | User approved? | Follow-up needed? |
|---|---|---|---|
| None currently |  |  |  |

## 6. Surgical Change Traceability

Every changed file should trace directly to the user's request.

| File / area | Change | Requirement it traces to | Necessary? | Notes |
|---|---|---|---|---|
|  |  |  |  |  |

## 7. Tradeoffs

| Choice | Benefit | Cost / downside | Revisit when |
|---|---|---|---|
|  |  |  |  |

## 8. High-Risk / Irreversible Operation Check

Mark every relevant item.

- [ ] Deletes or overwrites user data
- [ ] Changes database schema or migrations
- [ ] Deploys to production or changes production config
- [ ] Modifies payments, billing, subscriptions, or financial logic
- [ ] Changes authentication, authorization, permissions, or secrets
- [ ] Changes core calculation or business logic
- [ ] Performs irreversible external side effects
- [ ] Broad refactor outside requested scope
- [ ] None of the above

If any high-risk item is checked, stop and get explicit user confirmation before proceeding.

## 9. Verification Results

### 9.1 Report Credibility
- [ ] ✅ Verified: backed by real tool output, tests, live smoke, or production checks
- [ ] ⚠️ Partially verified: only part of the claim was checked, or live / production evidence is missing
- [ ] ❌ Unverified: based on reasoning, reading, or assumptions without real execution

### 9.2 Test Type Labels
- [ ] mock: simulated behavior only
- [ ] unit: unit tests passed
- [ ] integration: integration tests passed
- [ ] live smoke: a real CLI / API / service was exercised at minimum depth
- [ ] production verified: production was checked directly

### 9.3 Verified
| Check | Command / method | Result |
|---|---|---|
|  |  |  |

### 9.4 Not Verified
| Area | Why not verified | Risk |
|---|---|---|---|
|  |  |  |

## 9.5 Evidence Layer (v0.3)

> Goal: the "watched" (AI) and the "reporter" (Log) are no longer the same party.
> Each claim is anchored to an objective artifact a human can re-run.

### 9.5.1 Changed Files (objective)
| Path | Status | Lines +/- | Hash (optional) |
|---|---|---:|---|
|  | added / modified / deleted |  |  |

How to fill:
```bash
git diff --name-status <BASE_REF>..<HEAD_SHA>
git diff --numstat <BASE_REF>..<HEAD_SHA>
```

### 9.5.2 Diff Summary (per file)
| Path | What changed (plain language) | Public API? | Schema? |
|---|---|---|---|
|  |  | Yes / No | Yes / No |

### 9.5.3 Test Result (raw output, not a summary)
| Suite | Command | Result | Pass / Fail / Skip |
|---|---|---|---|
|  |  | (paste actual output) |  |

How to fill:
```bash
pytest -q 2>&1 | tail -40 > evidence/test-result.txt
```

### 9.5.4 Verification Type
Mark every claim with the strongest type that actually applies:

- [ ] mock: simulated behavior only — NOT acceptable for prod gates
- [ ] unit: unit tests passed
- [ ] integration: integration tests passed
- [ ] live smoke: a real CLI / API / service was exercised
- [ ] production verified: production was checked directly

> Do not collapse these. "Passed" without a type is an unverified claim.

### 9.5.5 Commit Hash / PR Link
- Commit hash: `<HEAD_SHA>`
- Branch: `<BRANCH>`
- PR link: `<URL>`
- Re-run command: `git checkout <BRANCH> && git rev-parse HEAD`

### 9.5.6 High-Risk Touchpoints (v0.3 — auto-detected, do not delete rows)

> v0.3 changes: this table is now produced by
> `scripts/detect_high_risk_touchpoints.py` from the working tree
> + staged changes, against `config/high_risk_patterns.yml`.
>
> **v0.3.1 addition**: if this table is non-empty, Section 0.5
> MUST list a non-self human approver. Validation refuses to
> pass otherwise.

| Path | Touchpoint type | Why this is high-risk | Notes (optional) |
|---|---|---|---|
|  |  |  |  |

### 9.5.7 Rollback Evidence (v0.3 — actually exercised)

> v0.3 changes: "revertible" is no longer evidence. The table below is
> produced by `scripts/collect_rollback_evidence.py`, which runs
> `git revert --no-commit --no-edit <HEAD>` on a throwaway worktree
> at `<HEAD>~1` and records the real exit code and conflict markers.
>
> Validation refuses to pass a v0.3 log where:
> 1. the section is missing,
> 2. `Exit code` is not 0 OR `Conflict markers` is non-empty,
> 3. the only entry is `n/a` for a non-trivial task.

| Rollback step | Command | Exit code | Conflict markers | Verified by |
|---|---|---:|---|---|
| Revert commit | `git revert --no-commit --no-edit <HEAD_SHA>` | 0 | 0 unmerged, 0 .rej | throwaway worktree at HEAD~1, then reverted |

How to fill:
```bash
python scripts/collect_rollback_evidence.py --sha <HEAD_SHA>
```

## 10. Rollback Plan

If this change causes problems, revert by:

- Commit / branch:
- Files to revert:
- Data recovery steps:
- Config rollback steps:

## 11. Final Summary for Human Review

| Item | Summary |
|---|---|
| Changed |  |
| Not changed |  |
| AI-made decisions |  |
| Deviations |  |
| Verified |  |
| Not verified |  |
| Rollback |  |
| Approver | <github handle> |
| Approval evidence | <URL or "no human in loop"> |
