---
name: ai-development-control-log
description: Use when running non-trivial AI-assisted coding tasks, especially for non-engineering founders or product owners who need to manage agent assumptions, AI-made decisions, spec deviations, high-risk operations, verification, and rollback.
version: 1.0.0
author: Arthur Liao and contributors
license: MIT
metadata:
  hermes:
    tags: [ai-development, agent-governance, worklog, coding-agent, karpathy]
    related_skills: [karpathy-guidelines, subagent-driven-development, test-driven-development]
---

# AI Development Control Log

## Overview

This skill turns an AI coding agent from a black box into a managed assistant.

It is for users who may not read code fluently but can manage product intent, risk, tradeoffs, and verification. The agent must keep a human-readable control log that distinguishes explicit user requirements from AI-made decisions and spec deviations.

## When to Use

Use for non-trivial tasks, especially:

- payments, billing, subscriptions, or financial logic
- user data, CRM, privacy, or production records
- database schema, migrations, or destructive data operations
- production deploys, cutovers, gateways, or external integrations
- permissions, authentication, authorization, or secrets
- core calculation or business logic
- multi-agent or long-running implementation tasks

Do not require the full protocol for typos, one-line copy edits, or obviously reversible low-risk changes.

## Control Log Requirement

Create or update `implementation-control-log.md` during the task, not only after the task.

Required sections:

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

## Procedure

1. Before coding, write the task goal, non-goals, assumptions, and success criteria.
2. During coding, append AI-made decisions as they happen.
3. For every file touched, record why the change is necessary and which requirement it traces to.
4. If a change touches high-risk areas, stop and ask for explicit confirmation.
5. Before final response, run verification and record exact commands or checks.
6. Report any unverified areas plainly.

## High-Risk Stop Rule

Stop and ask before:

- deleting, overwriting, or bulk-modifying data
- changing database schema or migrations
- deploying to production
- modifying payments, billing, subscriptions, or financial logic
- changing auth, permissions, secrets, or security boundaries
- changing core calculation logic
- performing irreversible external side effects
- broad refactors outside the request

## Final Response Checklist

The final answer must include:

- what changed
- what was intentionally not changed
- what was verified
- what was not verified
- AI-made decisions or deviations
- rollback path when risk is non-trivial

## Common Pitfalls

1. **Backfilling the log at the end.** The point is to catch decisions while they happen.
2. **Writing a progress log instead of a decision log.** “Edited file X” is not enough; explain why and which requirement it traces to.
3. **Letting tests replace governance.** Tests can pass while the AI still made unauthorized product decisions.
4. **Treating reversible and irreversible work the same.** Destructive data changes and production deploys need explicit confirmation.
5. **Hiding unverified work.** “Should work” is not verification.

## Verification Checklist

- [ ] `implementation-control-log.md` exists or was updated.
- [ ] Explicit user requirements are separated from AI-made decisions.
- [ ] Spec deviations are listed, or explicitly marked none.
- [ ] Every touched file has a requirement trace.
- [ ] High-risk operations were checked.
- [ ] Verification commands/checks are recorded.
- [ ] Unverified areas are marked.
- [ ] Rollback path is documented when relevant.
