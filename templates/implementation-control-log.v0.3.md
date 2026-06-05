# Implementation Control Log (v0.3 — Replit-proof)

> v0.3 changes from v0.2:
> - 9.5.6 High-Risk Touchpoints is now **auto-detected from the working
>   tree** (scripts/detect_high_risk_touchpoints.py). Agents may add
>   notes but MUST NOT delete detected rows.
> - 9.5.7 Rollback Evidence is now **actually exercised** by
>   `git revert --no-commit` against a throwaway worktree
>   (scripts/collect_rollback_evidence.py). "Revertible" without
>   exit code 0 and zero conflict markers is not evidence.
> - Adds Section 0.5 (Actor & Provenance) — placeholder in v0.3,
>   hard-required in v0.3.1.

## 0. 語言與讀者設定

| 欄位 | 值 |
|---|---|
| 輸出語言 | zh-TW / zh-CN / en / ja / custom |
| 讀者 | founder / operator / engineer / customer / internal team |
| 語氣 | 白話 / 技術 / 高層摘要 / 客戶可讀 |
| 技術名詞是否翻成人話 | Yes / No |

## 0.5 Actor & Provenance (v0.3.1 placeholder)

> In v0.3.0 this section is informational. In v0.3.1 it becomes hard
> required. See docs/automation/evidence-layer-v0.3.md for details.

| Field | Value |
|---|---|
| Agent model       | claude-sonnet-4-6 / minimax-m3 / human / other |
| Agent session     |  |
| Human approver    | <github handle or "self-approved"> |
| Approval evidence | <PR review URL or "no human in loop"> |
| Wall clock start  | ISO-8601 |
| Wall clock end    | ISO-8601 |

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
|---|---|---|
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
> Validation refuses to pass a v0.3 log where:
> 1. the table is missing,
> 2. a path detected by the script is missing from the table,
> 3. the table contains only `None`.
>
> The agent MAY add notes per row but MUST NOT delete rows.

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
