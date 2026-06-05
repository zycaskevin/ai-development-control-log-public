# Implementation Control Log

> This file is for managing AI-assisted development. Update it during the task, not only after completion.

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

### Report Credibility

- [ ] ✅ Verified: backed by real tool output, tests, live smoke, or production checks
- [ ] ⚠️ Partially verified: only part of the claim was checked, or live / production evidence is missing
- [ ] ❌ Unverified: based on reasoning, reading, or assumptions without real execution

### Test Type Labels

- [ ] mock: simulated behavior only
- [ ] unit: unit tests passed
- [ ] integration: integration tests passed
- [ ] live smoke: a real CLI / API / service was exercised at minimum depth
- [ ] production verified: production was checked directly

### Verified

| Check | Command / method | Result |
|---|---|---|
|  |  |  |

### Not Verified

| Area | Why not verified | Risk |
|---|---|---|
|  |  |  |

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
