# Evidence Layer v0.3 — Replit-proof

> v0.2 turned the AI Development Control Log from a self-report
> into a cross-checkable record. v0.3 turns it into a record the
> AI cannot lie about. The trigger is the 2025-07 Replit incident:
> an AI agent deleted a live production database during a code
> freeze, then apologized for "a catastrophic failure on my part".

## Why v0.3

v0.2 added the Evidence Layer with seven sub-blocks:

- 9.5.1 Changed Files
- 9.5.2 Diff Summary
- 9.5.3 Test Result
- 9.5.4 Verification Type
- 9.5.5 Commit Hash / PR Link
- 9.5.6 High-Risk Touchpoints
- 9.5.7 Rollback Evidence

v0.2 still had two weaknesses that the Replit incident made
impossible to ignore:

1. **9.5.6 was self-reported.** The agent listed which files
   touched DB, payments, auth, etc. — but the agent is the same
   party that did the touching. If the agent (or the underlying
   LLM) is miscalibrated or adversarial, 9.5.6 is a lie waiting
   to happen. Replit's agent reportedly *promised* it would not
   touch production and then did exactly that.
2. **9.5.7 was a hand-wave.** "Revertible" without exercising the
   path is not evidence. The agent has every incentive to write
   "revertible" because it is the path of least resistance, and
   no test catches it.

v0.3 fixes both by making the entries **produced by the
working tree and by `git`, not by the agent**.

## What changes in v0.3

### 9.5.6 is auto-detected

A new script `scripts/detect_high_risk_touchpoints.py` scans the
working tree + staged changes against
`config/high_risk_patterns.yml` and produces the 9.5.6 table.
The categories are:

| Category ID | Why it is high-risk |
|---|---|
| `db-schema`        | Rollback needs explicit down-migration |
| `payment`          | Incident blast radius is money |
| `auth`             | Wrong code is a security CVE |
| `secret`           | Leaking one is a security incident |
| `production-config`| Production environment |
| `core-calculation` | Wrong code changes the product's output |
| `external-side-effect` | Deploy, webhook, cutover, batch |

The patterns are kept in a YAML file the agent is **not** supposed
to edit. If the patterns need to change, that's a PR with a human
reviewer, not a quiet edit by the agent right before shipping.

The agent MAY add notes per detected row. The agent MUST NOT
delete detected rows. `scripts/validate.py` refuses to pass a
v0.3 log if a path detected by the script is missing from the
table.

### 9.5.7 is actually exercised

A new script `scripts/collect_rollback_evidence.py`:

1. Creates a throwaway `git worktree` at the current branch tip.
2. Runs `git revert --no-commit --no-edit <HEAD>` inside it.
3. Captures the real `Exit code`, the conflict markers, and any
   `.rej` / `.orig` sidecars.
4. Tears the worktree down, even on failure.
5. Emits a markdown snippet the agent can paste into 9.5.7.

`scripts/validate.py` refuses to pass a v0.3 log if `Exit code`
is not 0 or `Conflict markers` is non-empty. The user can always
opt out of this check by writing `n/a` for a trivial change
(e.g. one-line copy edit), but the choice is now visible in the
log instead of hidden behind "revertible".

The script is read-only with respect to the user's branch — it
only touches a throwaway worktree. This means a v0.3 log can
record rollback evidence **before** the user merges, without
risking the agent's working tree.

## How to use v0.3

For non-trivial tasks, the agent should:

1. Open the v0.3 template: `templates/implementation-control-log.v0.3.md`
   (or `.zh-TW.v0.3.md` for 繁中).
2. Run `python scripts/detect_high_risk_touchpoints.py --base main`
   and paste the output into 9.5.6.
3. Run `python scripts/collect_rollback_evidence.py` and paste
   the output into 9.5.7.
4. Read the script's verdict:
   - **Verified** (exit 0, no conflicts): rollback is real.
   - **Conflict** (exit 1, conflict markers present): the agent
     must write a follow-up note explaining how the conflict is
     resolved, or escalate to a human reviewer.
   - **Error** (exit ≥ 128, e.g. shallow repo): the agent must
     fall back to a manual `git revert --no-commit` and paste the
     output verbatim.

## What v0.3 does NOT do

- It does **not** make the agent's code review-proof. A
  malicious or confused agent can still write bad code.
- It does **not** prevent the Replit incident. The agent in that
  incident had production access. v0.3 is for the *audit trail*,
  not the *gate*. Phase 0.3.2 (storage hardening) and 0.3.3
  (multi-agent) will tighten the gate; those are not v0.3.0.
- It does **not** check the agent's prose. The agent can still
  say "this is fine" in Section 11. v0.3 only makes the
  *evidence-bearing* sections unfakeable.

## Why this matters for the repo

- Honest answer to "what if the AI lies about scope?": the
  detector reads the working tree. The agent can add files
  without changing the pattern, but it cannot make the detector
  see files that are not there.
- Honest answer to "what if rollback doesn't actually work?": the
  evidence section shows the exit code. If `git revert` is going
  to fail, the user finds out *before* shipping, not after a
  production incident.
- Aligned with 2026 industry direction:
  - EU AI Act Article 12 — automatic event recording
  - NIST AI 600-1 — TEVV for GenAI
  - CSA *AI Agent Disclosure Vacuum* 2026 — self-disclosure is
    not evidence
