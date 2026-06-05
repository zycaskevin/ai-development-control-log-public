# Example: Billing Change Control Log (v0.3.1 — with Actor metadata)

> Companion to the v0.3 billing example. v0.3.1 adds Section 0.5
> (Actor & Provenance) as a hard-required block.
>
> This example demonstrates a **non-trivial** change: 9.5.6 has a
> `payment` touchpoint row, so the v0.3.1 self-approval rule kicks
> in. `Human approver` is `@maintainer`, not `self-approved`. The
> `Approval evidence` is a real PR review URL.

The 0.5 fields below were autofilled by
`scripts/collect_actor_metadata.py` (agent-side rows) and then
completed by a human reviewer (approver + evidence rows). The
exact autofill command was:

```bash
$ HERMES_AGENT_MODEL=claude-sonnet-4-6 \
  HERMES_TASK_ID=feat-v0.3.1-actor \
  python scripts/collect_actor_metadata.py --json
{
  "agent_model": "claude-sonnet-4-6",
  "agent_session": "2026-06-04T23:01:46Z-feat-v0.",
  "human_approver": "",
  "approval_evidence": "",
  "wall_clock_start": "2026-06-04T23:01:46Z",
  "wall_clock_end": "2026-06-04T23:01:46Z"
}
```

After autofill, the human reviewer filled in the two empty
fields, turning the JSON into the markdown table below.

## 0. 語言與讀者設定

| 欄位 | 值 |
|---|---|
| 輸出語言 | zh-TW |
| 讀者 | 創辦人 / 工程師 |
| 語氣 | 技術 |
| 技術名詞是否翻成人話 | 是 |

## 0.5 Actor & Provenance (v0.3.1 — required)

> **v0.3.1 self-approval rule**: 9.5.6 has a `payment` touchpoint
> row, so `Human approver` MUST be a GitHub handle. `@maintainer`
> below is correct; `self-approved` would fail validation.

| Field | Value |
|---|---|
| Agent model       | claude-sonnet-4-6 |
| Agent session     | 2026-06-04T23:01:46Z-feat-v0.3.1-actor |
| Human approver    | @maintainer |
| Approval evidence | https://github.com/zycaskevin/ai-development-control-log/pull/<N>#pullrequestreview-<id> |
| Wall clock start  | 2026-06-04T23:01:46Z |
| Wall clock end    | 2026-06-04T23:18:30Z |

## 1. Task Goal

### Timeline

| Field | Value |
|---|---|
| Task started at | 2026-06-04T23:01:46Z |
| Last updated at | 2026-06-04T23:18:30Z |

### Goal
- Add a new monthly subscription plan named `Pro`.
- Show the new plan on the pricing page.

### Non-goals / Out of Scope
- Do not change existing customer subscriptions.
- Do not change invoice calculation for existing plans.
- Do not deploy to production until explicitly approved.

### Success Criteria
- [x] Pricing page lists the new plan.
- [x] Checkout creates a `Pro` subscription in sandbox mode.
- [ ] Production Stripe price ID is not changed in this task.

## 2. Explicit User Requirements

- Add a new plan called `Pro`.
- Keep existing plans untouched.
- Test in sandbox first.

## 3. Open Questions and Assumptions

| Question / ambiguity | Current assumption | If wrong, cost | Needs confirmation? |
|---|---|---:|---|
| Should existing users be migrated? | No migration | High | Yes, if migration is requested later |
| Should this use live Stripe price ID? | No, sandbox only | High | Yes before production |

## 4. AI-Made Decisions

| Decision | Why this choice | Alternatives | Risk |
|---|---|---|---|
| Add plan config but do not alter billing engine | Lowest risk | Refactor billing logic | Low |
| Use sandbox price ID placeholder | Prevent accidental live billing | Use live price ID now | Medium |

## 5. Spec Deviations

| Deviation | Reason | User approved? | Follow-up needed? |
|---|---|---|---|
| None |  |  |  |

## 6. Surgical Change Traceability

| File / area | Change | Requirement it traces to | Necessary? | Notes |
|---|---|---|---|---|
| `src/config/plans.ts` | Add `Pro` plan config | Add new plan | Yes | Config only |
| `src/pages/pricing.tsx` | Show `Pro` card | Add plan to pricing page | Yes | UI only |
| `src/billing/calculateInvoice.ts` | No change | Keep invoice calculation untouched | Yes | Explicitly preserved |

## 7. Tradeoffs

| Choice | Benefit | Cost / downside | Revisit when |
|---|---|---|---|
| Sandbox-only setup | Avoid accidental charges | Requires production cutover later | Before launch |

## 8. High-Risk / Irreversible Operation Check

- [ ] Deletes or overwrites user data
- [ ] Changes database schema or migrations
- [ ] Deploys to production or changes production config
- [x] Modifies payments, billing, subscriptions, or financial logic
- [ ] Changes authentication, authorization, permissions, or secrets
- [ ] Changes core calculation or business logic
- [ ] Performs irreversible external side effects
- [ ] Broad refactor outside requested scope

Because billing is involved, production changes require explicit user confirmation.

## 9. Verification Results

### 9.1 Report Credibility
- [x] ✅ Verified: backed by real tool output, tests, live smoke, or production checks
- [ ] ⚠️ Partially verified
- [ ] ❌ Unverified

### 9.2 Test Type Labels
- [ ] mock
- [x] unit
- [ ] integration
- [x] live smoke
- [ ] production verified

### 9.3 Verified
| Check | Command / method | Result |
|---|---|---|
| Pricing UI loads | Local browser check | Passed — page rendered `Starter`, `Pro`, and `Enterprise` cards |
| Sandbox checkout | Stripe test mode checkout | Passed — returned sandbox subscription ID `sub_test_123` |
| Existing invoice tests | `npm test -- billing` | Passed — see 9.5.3 raw output |

### 9.4 Not Verified
| Area | Why not verified | Risk |
|---|---|---|
| Production checkout | Not approved | High |
| Existing user migration | Out of scope | Medium |

## 9.5 Evidence Layer (v0.3)

### 9.5.1 Changed Files (objective)

| Path | Status | Lines +/- | Hash (optional) |
|---|---|---:|---|
| `src/config/plans.ts` | modified | +3 / -1 |  |
| `src/pages/pricing.tsx` | modified | +42 / -1 |  |
| `src/billing/calculateInvoice.ts` | unchanged | 0 / 0 |  |

### 9.5.2 Diff Summary (per file)

| Path | What changed (plain language) | Public API? | Schema? |
|---|---|---|---|
| `src/config/plans.ts` | Added `Pro` plan entry at price 30; kept existing 3 plans untouched | No | No |
| `src/pages/pricing.tsx` | Added a `Pro` card and a click-through to the sandbox checkout | No | No |

### 9.5.3 Test Result (raw output, not a summary)

| Suite | Command | Result | Pass / Fail / Skip |
|---|---|---|---|
| `billing` unit tests | `npm test -- billing` | see below | Pass |

Raw output:

```text
$ npm test -- billing

> app@0.1.0 test
> vitest run billing

✓ src/billing/calculateInvoice.test.ts (12 tests) 48ms

Test Files  1 passed (1)
Tests       12 passed (12)
Duration    0.62s
```

### 9.5.4 Verification Type

- [ ] mock
- [x] unit
- [ ] integration
- [x] live smoke
- [ ] production verified

### 9.5.5 Commit Hash / PR Link

- Commit hash: `e980d608ed48ec23085153131d92383c34b4e218` (fixture HEAD)
- Branch: `feat/billing-pro-plan`
- PR link: https://github.com/zycaskevin/ai-development-control-log/pull/<N>
- Re-run command:

```bash
git checkout feat/billing-pro-plan
git rev-parse HEAD
git diff --name-status main..HEAD
```

### 9.5.6 High-Risk Touchpoints (v0.3 — auto-detected)

| Path | Touchpoint type | Why this is high-risk | Notes (optional) |
|---|---|---|---|
| `src/billing/calculateInvoice.ts` | payment | Payment, billing, or financial logic — incident blast radius is money | Listed because the file matches the `**/billing*/**` pattern. Unchanged in this commit, but a future commit could re-introduce it. |

### 9.5.7 Rollback Evidence (v0.3 — actually exercised)

| Rollback step | Command | Exit code | Conflict markers | Verified by |
|---|---|---:|---|---|
| Revert commit | `git revert --no-commit --no-edit e980d60` | 0 | 0 unmerged, 0 .rej | throwaway worktree at current tip, then reverted |
| Restore DB | n/a | n/a | n/a | No DB migration in this task |
| Disable feature flag | n/a | n/a | n/a | No flag system in use yet |
| Redeploy previous version | redeploy last green tag | n/a | n/a | Last green tag: `v0.1.3-billing` |

## 10. Rollback Plan

- Revert plan config and pricing page commit.
- No database rollback needed.
- No live Stripe changes were made.

## 11. Final Summary for Human Review

| Item | Summary |
|---|---|
| Changed | `plans.ts` (added `Pro`), `pricing.tsx` (added `Pro` card) |
| Not changed | `calculateInvoice.ts`, all existing plans, Stripe live price IDs |
| AI-made decisions | Use sandbox price ID; do not refactor billing engine |
| Deviations | None |
| Verified | `npm test -- billing` 12/12 passed; sandbox checkout `sub_test_123`; local UI renders 3 cards; `git revert` clean (exit 0, 0 unmerged) |
| Not verified | Production checkout (not approved); existing user migration (out of scope) |
| Rollback | `git revert` dry-run on throwaway worktree succeeded with exit 0; redeploy `v0.1.3-billing` if needed |
| Approver | @maintainer |
| Approval evidence | https://github.com/zycaskevin/ai-development-control-log/pull/<N>#pullrequestreview-<id> |
