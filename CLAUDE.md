# AI Development Control Log Instructions

Use these instructions for non-trivial coding tasks. They are designed to reduce silent assumptions, drive-by refactors, scope creep, and irreversible AI actions.

## Core principles

1. **Think before coding** — state assumptions, ambiguity, and tradeoffs before implementation. Maps to log sections 3 and 7.
2. **Simplicity first** — implement the minimum code that solves the current problem; no speculative features. Maps to sections 1 and 7.
3. **Surgical changes** — touch only what the task requires. Every changed line should trace directly to the user's request. Maps to section 6.
4. **Goal-driven execution** — define success criteria and verify them before claiming completion. Maps to sections 1 and 9.
5. **Control-log discipline** — maintain an implementation control log during the task, not only after the task. Maps to sections 1-11.

## When this is required

Use the control log for non-trivial tasks. A task is non-trivial if any of these are true:

- it changes more than one file or more than one functional area
- it touches payments, billing, subscriptions, user data, production config, auth, permissions, secrets, database schema, migrations, or core calculations
- it has external side effects such as deploys, API writes, webhooks, data imports, or batch updates
- it requires assumptions, tradeoffs, or AI-made decisions that a human reviewer should see
- failure would be costly, hard to detect, or hard to roll back

You may skip the log for low-risk reversible changes such as typo fixes, one-line copy edits, formatting-only changes, or documentation wording tweaks that do not alter behavior.

## Required control log

Before writing a control log or decision digest, identify the expected output language and audience.

If the user is Chinese-speaking or the project uses Chinese documentation, default to Traditional Chinese (`zh-TW`) unless the user requests otherwise. Do not silently output English-only logs for non-English users.

Each control log should include:

- output language
- target audience
- tone
- whether technical terms should be translated into plain language

For every non-trivial task, create or update:

```text
implementation-control-log.md
```

Use the template in `templates/implementation-control-log.md` if available. For Chinese-speaking users or founder-facing reports, prefer `templates/implementation-control-log.zh-TW.md` when available.

The log must include:

1. Task goal and non-goals
2. Explicit user requirements
3. Open questions and assumptions
4. AI-made decisions
5. Spec deviations
6. Surgical-change traceability table
7. Tradeoffs
8. High-risk / irreversible operation check
9. Verification results
10. Rollback plan

## Daily decision digest

For long-running work, multi-agent work, or any day with multiple non-trivial AI-made decisions, produce or update a daily decision digest.

Recommended files:

```text
templates/daily-decision-digest.zh-TW.md
templates/daily-decision-digest.en.md
```

The digest must focus on decisions, not activity noise:

- AI-made decisions
- assumptions and fallback choices
- deviations from the original expectation
- verification credibility
- high-risk gates
- decisions the user needs to make

Do not bury this digest in internal notes. Put it somewhere the user can see.

## Optional delivery automation

Daily digest delivery is optional, not default. Do not assume this repo sends messages automatically.

Before sending a digest to any external or team channel, check the delivery config and safety gates:

- secret / token leakage
- PII or customer data
- internal state leakage such as dry-run, preview, committed, or private reasoning
- verification labels for every claim
- high-risk operations such as production, auth, billing, DB schema, or external side effects
- audience and tone match

If any gate is uncertain, downgrade to local-only or draft-first. Do not send customer-facing or external messages that expose internal state.

## Stop-and-confirm rule

Stop and ask for explicit confirmation before:

- deleting or overwriting user data
- changing database schema or migrations
- deploying to production
- modifying payments, billing, subscriptions, or financial logic
- changing permissions, authentication, authorization, or secrets
- modifying core calculation logic
- performing irreversible external side effects
- doing broad refactors outside the requested scope

## Completion rule

Do not claim “done” unless the final response includes:

- what changed
- what was intentionally not changed
- what was verified
- what was not verified
- any AI-made decisions or deviations
- rollback path if relevant
