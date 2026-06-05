# Evidence Layer v0.3.1 — Actor & Provenance

> v0.3 turned the AI Development Control Log into a Replit-proof
> record. v0.3.1 turns it into a record where the **agent and
> the approver cannot be the same party** — without that, the
> v0.3 evidence is only as trustworthy as the agent's self-report,
> which the Replit incident showed is not enough.

## Why v0.3.1

The v0.3 Evidence Layer is solid: 9.5.6 is auto-detected, 9.5.7
is actually exercised, and a human can re-run every claim. But
none of that answers the question "who signed off on this?"
If the agent both decided to touch high-risk systems AND
approved its own decision, the v0.3 evidence is a careful
record of an unaccountable act. v0.3.1 closes that gap by
requiring a named, non-self human approver whenever 9.5.6
shows high-risk touchpoints.

## What changes in v0.3.1

Section 0.5 (Actor & Provenance) goes from "placeholder, please
fill when convenient" in v0.3 to **hard required** in v0.3.1.
The `scripts/validate.py` gate refuses to pass a v0.3.1 log
whose 0.5 block is missing any of:

- Agent model
- Agent session
- Human approver
- Approval evidence
- Wall clock start
- Wall clock end

A new script `scripts/collect_actor_metadata.py` autofills the
agent-side rows from environment variables, so an agent can
produce a complete 0.5 block in one command:

```bash
$ HERMES_AGENT_MODEL=claude-sonnet-4-6 \
  HERMES_TASK_ID=feat-v0.3.1-actor \
  python scripts/collect_actor_metadata.py
```

The two **human-side** rows — `Human approver` and `Approval
evidence` — are intentionally left empty. The agent must NOT
fill them; the human does.

### Self-approval is forbidden for high-risk tasks

If Section 9.5.6 (High-Risk Touchpoints) contains any row whose
`Touchpoint type` is one of the seven high-risk categories
(`db-schema`, `payment`, `auth`, `secret`, `production-config`,
`core-calculation`, `external-side-effect`), then
`Human approver` MUST be a GitHub handle, not `self-approved`.

The Replit incident is exactly the case this guards against.
The agent in that incident both decided to touch production and
approved its own decision. v0.3.1 makes that structurally
impossible: the agent cannot mark its own log as approved when
9.5.6 says it touched high-risk systems.

The gate's error message tells the human reviewer exactly what
to do:

> v0.3.1 self-approval is forbidden when 9.5.6 has high-risk
> touchpoints. Set Human approver to a GitHub handle
> (e.g. @user).

### Wall clock ordering is checked

`Wall clock end` must be ≥ `Wall clock start`, when both parse
as ISO-8601. The gate's error message names the offending
timestamps, so a reviewer can spot the bug at a glance.

## How to use v0.3.1

For non-trivial tasks, the agent should:

1. Open the v0.3.1 template:
   `templates/implementation-control-log.v0.3.1.md`
   (or `.zh-TW.v0.3.1.md` for 繁中).
2. Run `python scripts/collect_actor_metadata.py` to autofill
   the agent-side rows of Section 0.5.
3. Continue with the v0.3 workflow: detect high-risk
   touchpoints, exercise rollback, fill 9.5.1–9.5.7.
4. Stop and ask a human reviewer. The human reviews 9.5.6, sees
   it has a high-risk row, and fills `Human approver` and
   `Approval evidence` in 0.5.
5. The reviewer opens a PR. The PR description includes the
   completed v0.3.1 log.
6. CI runs `python scripts/validate.py`, which enforces the
   0.5 completeness rule and the self-approval rule.

## What v0.3.1 does NOT do

- It does **not** verify the human approver is actually a human.
  The `Human approver` field is a string; nothing in v0.3.1
  checks that the named GitHub handle actually approved the PR.
  v0.3.4 (Cross-validator) will tighten this.
- It does **not** verify the agent model string. The gate only
  checks that the field is non-empty. v0.3.4 will compare the
  string against an authoritative agent-model registry.
- It does **not** prevent the agent from filling the
  `Approval evidence` field with a fake URL. The gate only
  requires that the field is non-empty and looks URL-ish.
  v0.3.4 will require the URL to resolve.
- It does **not** preserve old logs. v0.3.1 is a hard rule on
  new logs; the v0.3 log a project shipped last week is still
  valid under v0.3. v0.3.2 (storage hardening) will require
  periodic re-issuance of old logs under the v0.3.1 schema.

## Why this matters for the repo

- Honest answer to "what if the agent self-approves?": the
  gate refuses to validate the log. CI fails. The PR cannot
  merge.
- Honest answer to "what if the agent fakes the approver?":
  v0.3.1 does not catch this. v0.3.4 will.
- Aligned with 2026 industry direction:
  - EU AI Act Article 12 — automatic event recording, with a
    non-agent party responsible for the audit trail
  - NIST AI 600-1 — TEVV for GenAI: human reviewers must
    appear in the trace
  - CSA *AI Agent Disclosure Vacuum* 2026 — agents must
    disclose their identity, and a human must attest to
    accepting the output

## v0.3.1 vs v0.3 in one line

> v0.3: "the agent must show the diff and the exit code."
> v0.3.1: "and a real human must sign off on it."
