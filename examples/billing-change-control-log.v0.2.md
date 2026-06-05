# Example: Billing Change Control Log (v0.2 — Evidence Layer)

> Companion to `billing-change-control-log.md` (v0.1).
> v0.2 adds Section 9.5 / 10.5: every claim is anchored to a real artifact
> a human can re-run, not to AI's own self-report.

## 1. Task Goal

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

## 9.5 Evidence Layer (v0.2)

### 9.5.1 Changed Files (objective)

| Path | Status | Lines +/- | Hash (optional) |
|---|---|---:|---|
| `src/config/plans.ts` | modified | +18 / -2 |  |
| `src/pages/pricing.tsx` | modified | +42 / -1 |  |
| `tests/billing/calculateInvoice.test.ts` | unchanged | 0 / 0 |  |

How this was filled:

```bash
$ git diff --name-status main..HEAD
M       src/config/plans.ts
M       src/pages/pricing.tsx

$ git diff --numstat main..HEAD
18      2       src/config/plans.ts
42      1       src/pages/pricing.tsx
```

### 9.5.2 Diff Summary (per file)

| Path | What changed (plain language) | Public API? | Schema? |
|---|---|---|---|
| `src/config/plans.ts` | Added `Pro` plan entry; kept existing 3 plans untouched | No | No |
| `src/pages/pricing.tsx` | Added a `Pro` card and a click-through to the sandbox checkout | No | No |

### 9.5.3 Test Result (raw output, not a summary)

| Suite | Command | Result | Pass / Fail / Skip |
|---|---|---|---|
| `billing` unit tests | `npm test -- billing` | see below | Pass |

Raw output (not paraphrased):

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

> Note: Stripe live checkout is intentionally NOT verified. That is a separate,
> human-approved production cutover, and belongs in a different log.

### 9.5.5 Commit Hash / PR Link

- Commit hash: `40425cb...` (placeholder, replace with real HEAD)
- Branch: `feat/billing-pro-plan`
- PR link: https://github.com/zycaskevin/ai-development-control-log/pull/<N>
- Re-run command:

```bash
git checkout feat/billing-pro-plan
git rev-parse HEAD
git diff --name-status main..HEAD
```

### 9.5.6 High-Risk Touchpoints

| Path | Touchpoint type | Why this is high-risk |
|---|---|---|
| `src/config/plans.ts` | financial logic | Defines plan IDs the billing engine reads |
| `src/pages/pricing.tsx` | financial logic | Surfaces prices to users |

> DB schema, auth, secrets, and production config: **None touched in this task.**

### 9.5.7 Rollback Evidence

| Rollback step | Command | Verified by |
|---|---|---|
| Revert commit | `git revert <HEAD_SHA>` | `git revert --no-commit <HEAD_SHA>` dry-run output: clean (no conflicts) |
| Restore DB | n/a | No DB migration in this task |
| Disable feature flag | n/a | No flag system in use yet |
| Redeploy previous version | redeploy last green tag | Last green tag: `v0.1.3-billing` |

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
| Verified | `npm test -- billing` 12/12 passed; sandbox checkout `sub_test_123`; local UI renders 3 cards |
| Not verified | Production checkout (not approved); existing user migration (out of scope) |
| Rollback | `git revert` clean, no DB restore needed, redeploy `v0.1.3-billing` |
