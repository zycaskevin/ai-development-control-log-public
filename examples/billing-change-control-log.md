# Example: Billing Change Control Log

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

### Verified

| Check | Command / method | Result |
|---|---|---|
| Pricing UI loads | Local browser check | Passed — page rendered `Starter`, `Pro`, and `Enterprise` cards |
| Sandbox checkout | Stripe test mode checkout | Passed — returned sandbox subscription ID `sub_test_123` |
| Existing invoice tests | `npm test -- billing` | Passed — see tool output below |

Example tool output:

```text
$ npm test -- billing

> app@0.1.0 test
> vitest run billing

✓ src/billing/calculateInvoice.test.ts (12 tests) 48ms

Test Files  1 passed (1)
Tests       12 passed (12)
Duration    0.62s
```

### Not Verified

| Area | Why not verified | Risk |
|---|---|---|
| Production checkout | Not approved | High |
| Existing user migration | Out of scope | Medium |

## 10. Rollback Plan

- Revert plan config and pricing page commit.
- No database rollback needed.
- No live Stripe changes were made.
