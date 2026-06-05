# Implementation Control Log (v0.2 with Evidence Layer)

> This file is for managing AI-assisted development. Update it during the task, not only after completion.
> v0.2 adds the Evidence Layer (Section 9.5 + Section 10.5) so the log is no longer
> a self-report. Each claim is now backed by cross-checkable evidence:
> changed files, diff, test result, commit hash, high-risk touchpoints, and rollback.

## 0. 語言與讀者設定

| 欄位 | 值 |
|---|---|
| 輸出語言 | zh-TW / zh-CN / en / ja / custom |
| 讀者 | founder / operator / engineer / customer / internal team |
| 語氣 | 白話 / 技術 / 高層摘要 / 客戶可讀 |
| 技術名詞是否翻成人話 | Yes / No |

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

## 9.5 Evidence Layer (v0.2 — cross-checkable, not self-reported)

> Goal: the "watched" (AI) and the "reporter" (Log) are no longer the same party.
> Each claim is anchored to an objective artifact a human can re-run.

### 9.5.1 Changed Files (objective)
| Path | Status | Lines +/- | Hash (optional) |
|---|---|---:|---|
|  | added / modified / deleted |  |  |

How to fill:
```bash
# Real diff vs base ref (HEAD~1, main, or a tag)
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
# Example: paste the real tail of the test run, not "it passed"
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

### 9.5.6 High-Risk Touchpoints
List every file/area that crossed a sensitive boundary. If none, write `None`.

| Path | Touchpoint type | Why this is high-risk |
|---|---|---|
|  | DB schema / payment / auth / permission / secret / production config / core calculation / external side effect |  |

### 9.5.7 Rollback Evidence
> "可回滾" is not evidence. Show the rollback path was actually exercised.

| Rollback step | Command | Verified by |
|---|---|---|
| Revert commit | `git revert <HEAD_SHA>` | Dry-run output: (paste) |
| Restore DB |  | Backup file path: (paste) |
| Disable feature flag |  |  |
| Redeploy previous version |  | Tag / commit:  |

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
