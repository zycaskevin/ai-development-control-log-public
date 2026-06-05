# Daily AI Decision Digest v0.4

> Status: shipped in v0.4. This document is the design note.
> Companion to: `templates/daily-decision-digest.zh-TW.md`,
> `scripts/build_daily_digest.py`, `scripts/send_daily_digest.py`,
> `scripts/validate_daily_digest.py`, `.github/workflows/daily-digest.yml`,
> `docs/install/agent-assisted-install.zh-TW.md`,
> `docs/install/agent-assisted-install.en.md`,
> `docs/install/agent-assisted-install.zh-CN.md`.

## Why v0.4

Through v0.3.1, the repo provided daily digest **templates** but not
the plumbing to make a digest actually arrive in the user's inbox.
The shipped examples were annotated `# Example only: enable intentionally`,
which forced every fork author to re-implement the same glue.

The deeper problem was worse than plumbing: even when digests did get
written, they failed the "can the user read this?" test. They were
LLM-generated, full of jargon, missing the user-facing structure, and
silently skipped the high-risk / rollback / "what was NOT verified"
questions that the user actually needs to make decisions.

v0.4 closes both gaps:

1. A real, runnable GitHub Actions workflow (`.github/workflows/daily-digest.yml`)
   that builds a readable digest on schedule from recent git activity.
   Fork authors do not write glue code.
2. A small delivery sender (`scripts/send_daily_digest.py`) that supports
   Slack, Feishu / Lark, Telegram, and Resend email behind an explicit
   `DELIVERY_PROVIDER` variable.
3. An agent-assisted install task card so the user can ask a coding
   agent to set secrets, run the workflow, and verify delivery instead
   of learning GitHub Actions.
4. A rule-based validator (`scripts/validate_daily_digest.py`) that
   enforces a fixed 7-question structure and refuses to mark a digest
   "complete" if any question is unanswered or contains only the
   template placeholder.

## What changes in v0.4

- `templates/daily-decision-digest.zh-TW.md` — rewritten. Adds:
  - **`## 📋 0. 1 分鐘版（給老闆看）`** as the first section. This is
    the summary a non-engineering founder or product owner can read
    in under a minute.
  - **7 mandatory question sections** (Q1–Q7) explicitly mapped to the
    user's original 7 questions.
  - **§8 Feedback** at the end, asking the reader to reply with
    ✅ / ⚠️ / ❌. We do not auto-collect feedback; the affordance is
    there so the reader knows the channel exists.
  - **Per-row credibility labels** on every claim (✅ / ⚠️ / ❌).
  - **Empty-is-empty rule**: required sections must have real content.
    The validator will fail any digest that is still in template
    placeholder state.
- `templates/daily-decision-digest.en.md` — English version of the
  same structure, with the corresponding English aliases.
- `examples/daily-decision-digest.zh-TW.md` — rewritten as a fully
  filled example showing what a real day's digest looks like. This
  is the file you can copy and adapt to your own day.
- `scripts/validate_daily_digest.py` (new) — rule-based validator:
  - 1-minute block must be at the top of the file (within first 500 chars)
  - All 7 question headings must be present (zh-TW or en aliases)
  - Each Q1, Q3, Q4, Q5, Q6, Q7 must have real content (not placeholder)
  - Q2 (user requirements) and Q8 (feedback) are not gated for content
- `scripts/validate.py` — extended to also require the 9 daily-digest
  headings (per language) and the new validator / builder / sender /
  agent-install files.
- `scripts/build_daily_digest.py` (new) — builds a readable zh-TW digest
  from the last 24 hours of git activity. This replaces the old empty
  scaffold behavior.
- `scripts/send_daily_digest.py` (new) — sends a completed digest to an
  opt-in channel (`none`, `slack`, `feishu`, `telegram`, `email_resend`).
- `docs/install/agent-assisted-install.zh-TW.md` /
  `docs/install/agent-assisted-install.en.md` /
  `docs/install/agent-assisted-install.zh-CN.md` + matching
  `templates/agent-install-prompt.*.md` files (new) — lets the user hand
  setup to an AI agent.
- `.github/workflows/daily-digest.yml` (new) — first workflow that
  actually builds a readable digest end-to-end:
  - Schedule: 02:00 UTC daily (= 10:00 Asia/Taipei)
  - Builds `logs/daily/YYYY-MM-DD-digest.zh-TW.md` from git activity
  - Runs `validate_daily_digest.py` as a hard gate
  - Runs repo validation and pytest
  - Uploads the file as a workflow artifact
  - Sends externally only when `DELIVERY_PROVIDER` is configured
- `tests/test_validate_daily_digest.py` (new) — unit tests pinning
  the validator's contract.

## How to use v0.4

### As a fork author

1. Fork the repo and enable GitHub Actions.
2. Give the matching agent install task card to your coding agent:
   `docs/install/agent-assisted-install.zh-TW.md`,
   `docs/install/agent-assisted-install.en.md`, or
   `docs/install/agent-assisted-install.zh-CN.md`.
3. The agent asks where to deliver the report: Slack / Feishu /
   Telegram / Email / no external delivery.
4. The agent sets `DELIVERY_PROVIDER` plus the matching secrets, triggers
   the workflow once, checks the artifact, and verifies delivery.
5. After that, the workflow runs daily. If you want to stop delivery,
   set `DELIVERY_PROVIDER=none`.

### As a daily reader

Open the artifact from yesterday's run (or the latest file in
`logs/daily/`). Read the **1-minute block first**. If you need detail,
the 7 question sections are right below.

When you have read it, reply with ✅ / ⚠️ / ❌ in your team chat or
GitHub issue. That is the feedback loop — without it, the digest
cannot improve.

## What v0.4 does NOT do

- **It does not call out to an LLM.** The validator and default digest
  generator are rule-based on purpose. The digest may be conservative
  when git evidence cannot prove whether a change was user-requested
  or AI-decided.
- **It does not send externally unless configured.** Every external
  channel is a potential leak. The user opts in by asking an agent to
  set `DELIVERY_PROVIDER` and the matching secrets.
- **It does not sign the digest or store it append-only.** That is
  v0.3.1 territory. v0.4 is about *user readability*, not
  *non-repudiation*. If you need both, run v0.4 + v0.3.1 together.
- **It does not collect feedback automatically.** The §8 section
  asks for a reply, but the user must file an issue or send a chat
  message. We will not auto-build a feedback channel in v0.4.
- **It does not enforce a single language.** The validator accepts
  both zh-TW and English headings so non-English users can use the
  same workflow.

## Migration from v0.3.1 → v0.4

If your fork already runs the v0.3.1 daily digest (the LLM-generated
one), here is what to do:

1. **Stop using the v0.3.1 digest output as a user-facing report.**
   It answers different questions than v0.4. The v0.3.1 digest
   answers "what did the agent do today?"; v0.4 answers "did the
   agent overstep today, and if so, where?".
2. **Switch the workflow template reference** from
   `examples/github-actions-daily-digest.yml` to
   `.github/workflows/daily-digest.yml`.
3. **Re-train your readers.** v0.3.1 readers expected a work-log
   (commits, PRs, sample images). v0.4 readers should expect a
   7-question authority report. If your team is reading the digest
   to "see what shipped today", they should read the daily GitHub
   digest (PRs, issues) instead. v0.4 is for "is the AI making
   decisions I should know about?".

## What we learned building v0.4

- **LLM-generated digests fail the "did the user understand it?"
  test**, because the LLM optimizes for "looks complete" rather
  than "answers the user's questions". Rule-based validation of the
  *structure* is the only way to make the digest answerable.
- **The 1-minute block is the load-bearing feature.** Without it,
  the user has to scan the whole digest to find out whether anything
  needs their decision. With it, the digest is skim-readable.
- **Empty placeholders are not a UX problem; they are a contract
  problem.** The validator must fail on placeholder-only sections,
  not warn. This is the difference between "you should fill this in"
  and "this is not yet a digest".

## What comes after v0.4

Candidates, in order of likely value:

1. **v0.4.1** — Add a "yesterday's completed digests" link in the
   1-minute block, so the user can browse history without leaving the
   digest.
2. **v0.4.2** — Auto-collect feedback by reading replies to the issue
   the digest creates. Only if a real user asks for it.
3. **v0.5** — Task-level control logs: agents write one small
   `logs/tasks/YYYY-MM-DD-<slug>.md` file per meaningful task so the
   digest can distinguish explicit user requests from AI self-decisions
   instead of guessing from git alone.
4. **v0.6** — Optional LLM boss-summary layer that rewrites evidence
   into shorter human language without adding unsupported claims.
