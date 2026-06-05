# Example: Database Migration Control Log

## 1. Task Goal

### Goal
- Add an optional `nickname` field to customer profiles.

### Non-goals / Out of Scope
- Do not rename existing customer fields.
- Do not backfill nicknames automatically.
- Do not delete or rewrite existing customer data.

### Success Criteria
- [x] Migration adds nullable `nickname` column.
- [x] Existing customer rows remain valid.
- [x] Rollback migration exists.

## 2. Explicit User Requirements

- Add a nickname field.
- Keep existing customer data safe.

## 3. Open Questions and Assumptions

| Question / ambiguity | Current assumption | If wrong, cost | Needs confirmation? |
|---|---|---:|---|
| Should nickname be required? | No, nullable | Medium | No, safer default |
| Should old records be backfilled? | No | Medium | Yes, if requested later |

## 4. AI-Made Decisions

| Decision | Why this choice | Alternatives | Risk |
|---|---|---|---|
| Make column nullable | Avoid breaking existing rows | Required column with default | Low |
| No automatic backfill | Avoid guessing customer names | Generate from full name | Low |

## 5. Spec Deviations

| Deviation | Reason | User approved? | Follow-up needed? |
|---|---|---|---|
| None |  |  |  |

## 6. Surgical Change Traceability

| File / area | Change | Requirement it traces to | Necessary? | Notes |
|---|---|---|---|---|
| `migrations/20260519_add_customer_nickname.sql` | Add nullable column | Add nickname field | Yes | No data rewrite |
| `src/customer/profile.ts` | Read/write nickname | Add nickname field | Yes | Optional field |
| `src/customer/nameFormatter.ts` | No change | Avoid changing existing name logic | Yes | Explicitly preserved |

## 7. Tradeoffs

| Choice | Benefit | Cost / downside | Revisit when |
|---|---|---|---|
| Nullable column | Safe for existing data | App must handle empty nickname | If product requires nickname later |

## 8. High-Risk / Irreversible Operation Check

- [ ] Deletes or overwrites user data
- [x] Changes database schema or migrations
- [ ] Deploys to production or changes production config
- [ ] Modifies payments, billing, subscriptions, or financial logic
- [ ] Changes authentication, authorization, permissions, or secrets
- [ ] Changes core calculation or business logic
- [ ] Performs irreversible external side effects
- [ ] Broad refactor outside requested scope

Because schema changes are involved, production migration requires explicit user confirmation.

## 9. Verification Results

### Verified

| Check | Command / method | Result |
|---|---|---|
| Fresh migration | `npm run db:migrate:test` | Passed |
| Existing customer fixtures | `npm test -- customer` | Passed |
| Rollback | `npm run db:rollback:test` | Passed |

### Not Verified

| Area | Why not verified | Risk |
|---|---|---|
| Production migration | Not approved | High |
| Large dataset timing | No production-sized dump | Medium |

## 10. Rollback Plan

- Run rollback migration to drop nullable `nickname` column.
- Revert app changes that read/write nickname.
- No existing data should need restoration because no old fields were modified.
