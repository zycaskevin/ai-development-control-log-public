# Example: Multi-Round Control Log

This example shows how the same task log evolves across multiple agent updates. The key point is that the log is updated during the task, not reconstructed after the fact.

## Round 1 — Initial implementation

### 1. Task Goal

#### Timeline

| Field | Value |
|---|---|
| Task started at | 2026-06-02 09:00 UTC |
| Last updated at | 2026-06-02 09:22 UTC |

#### Goal

- Add an export button to download the current report as CSV.

#### Non-goals / Out of Scope

- Do not change report calculations.
- Do not add PDF export.
- Do not deploy to production.

#### Success Criteria

- [x] Button appears on the report page.
- [ ] CSV output is verified with a real sample report.
- [ ] Existing report calculations remain unchanged.

### 2. Explicit User Requirements

- Add CSV export.
- Keep the current report numbers unchanged.

### 3. Open Questions and Assumptions

| Question / ambiguity | Current assumption | If wrong, cost to change | Needs user confirmation? |
|---|---|---:|---|
| Should CSV include hidden columns? | No, export only visible report columns | Medium | Yes if hidden data is requested |

### 4. AI-Made Decisions

| Decision | Why this choice | Alternatives considered | Risk |
|---|---|---|---|
| Add export logic in the report UI layer | Avoid touching calculation code | Move export into report engine | Low |

### 5. Spec Deviations

| Deviation | Reason | User approved? | Follow-up needed? |
|---|---|---|---|
| None currently |  |  |  |

### 6. Surgical Change Traceability

| File / area | Change | Requirement it traces to | Necessary? | Notes |
|---|---|---|---|---|
| `src/pages/report.tsx` | Add CSV export button | Add CSV export | Yes | UI only |
| `src/report/exportCsv.ts` | Convert visible rows to CSV | Add CSV export | Yes | New isolated helper |
| `src/report/calculateTotals.ts` | No change | Keep numbers unchanged | Yes | Explicitly preserved |

### 9. Verification Results

#### Verified

| Check | Command / method | Result |
|---|---|---|
| Type check | `npm run typecheck` | Passed |

#### Not Verified

| Area | Why not verified | Risk |
|---|---|---|
| Real sample CSV | Waiting for sample report fixture | Medium |
| Existing totals | Tests not run yet | High |

## Round 2 — After verification and one correction

### Updated Timeline

| Field | Value |
|---|---|
| Task started at | 2026-06-02 09:00 UTC |
| Last updated at | 2026-06-02 10:05 UTC |

### What changed since Round 1

- Added a sample report fixture.
- Fixed CSV escaping for commas and quotes.
- Ran report calculation regression tests.

### Updated Surgical Change Traceability

| File / area | Change | Requirement it traces to | Necessary? | Notes |
|---|---|---|---|---|
| `src/report/exportCsv.ts` | Escape quotes and commas correctly | CSV export must be usable | Yes | Correction found during sample verification |
| `tests/fixtures/sampleReport.json` | Add sample report fixture | Verify real sample CSV | Yes | Test fixture only |
| `src/report/calculateTotals.ts` | No change | Keep numbers unchanged | Yes | Still explicitly preserved |

### Updated Verification Results

#### Report Credibility

- [x] ✅ Verified: backed by real tool output, tests, live smoke, or production checks
- [ ] ⚠️ Partially verified: only part of the claim was checked, or live / production evidence is missing
- [ ] ❌ Unverified: based on reasoning, reading, or assumptions without real execution

#### Test Type Labels

- [ ] mock: simulated behavior only
- [x] unit: unit tests passed
- [x] integration: integration tests passed
- [ ] live smoke: a real CLI / API / service was exercised at minimum depth
- [ ] production verified: production was checked directly

#### Verified

| Check | Command / method | Result |
|---|---|---|
| CSV fixture export | `npm test -- exportCsv` | Passed — see output below |
| Existing totals regression | `npm test -- calculateTotals` | Passed — totals unchanged |

Tool output:

```text
$ npm test -- exportCsv calculateTotals

✓ src/report/exportCsv.test.ts (5 tests) 31ms
✓ src/report/calculateTotals.test.ts (8 tests) 44ms

Test Files  2 passed (2)
Tests       13 passed (13)
Duration    0.71s
```

#### Not Verified

| Area | Why not verified | Risk |
|---|---|---|
| Production export | Production deploy not requested | Low |

### Final Summary for Human Review

| Item | Summary |
|---|---|
| Changed | Added CSV export button and isolated CSV helper |
| Not changed | Report calculation logic and production config |
| AI-made decisions | Kept export outside calculation engine |
| Deviations | None |
| Verified | Type check, CSV fixture export, totals regression |
| Not verified | Production export |
| Rollback | Revert `report.tsx`, `exportCsv.ts`, and fixture/test commit |
