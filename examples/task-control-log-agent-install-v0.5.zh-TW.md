# Task Control Log — v0.5 task-level control log

## Metadata

- Date: 2026-06-05
- Actor: Example Agent
- Repo: ai-development-control-log
- Branch: feat/v0.5-task-control-log
- Commit / PR: pending

## User explicitly asked

- 使用者問「需要重開對話嗎？再繼續0.5？」
- 使用者回「繼續」，要求接著做 v0.5。
- 使用者要 daily digest 能看出哪些是使用者要求、哪些是 AI 自己決定。

## AI self-decided

- Decision: v0.5 先做 task-level control log，不先加 LLM 美化。
  Rationale: 沒有可靠任務紀錄時，LLM 只會把 git 猜測寫得更漂亮，不能讓報告更準。
  Should have asked user first: no
- Decision: 保留 v0.4 git fallback。
  Rationale: 沒有 task logs 的 fork 不能被 v0.5 破壞；無 task logs 時報告要誠實說不知道。
  Should have asked user first: no
- Decision: task log headings 使用英文穩定欄位，內容可繁中。
  Rationale: parser 規則更穩，跨語言文件也能共用同一套結構。
  Should have asked user first: no

## Spec deviations

- Deviation: v0.4 design note 原本把 v0.5 候選寫成 multi-agent digest。
  Original spec: v0.5 multi-agent digests.
  Actual implementation: v0.5 task-level control logs.
  Reason: 使用者現在更需要 daily digest 能分辨 user asked / AI self-decided；multi-agent 可延後。
  Needs user confirmation: no

## High-risk touchpoints

- Path / operation: scripts/build_daily_digest.py
  Risk type: daily report source-of-truth logic
  User confirmed: yes
  Rollback path: revert v0.5 commit and keep v0.4.1 release
- Path / operation: scripts/collect_task_logs.py
  Risk type: parser controls what evidence becomes boss-facing report
  User confirmed: yes
  Rollback path: disable --task-log-dir or remove task logs and use git fallback

## Verification evidence

- Claim: task-log parser extracts user requests, AI decisions, deviations, risk touchpoints, verification, and rollback evidence.
  Verification type: unit
  Raw evidence: python -m pytest tests/test_collect_task_logs.py -q
- Claim: daily digest uses task logs when present and keeps v0.4 fallback when absent.
  Verification type: unit
  Raw evidence: python -m pytest tests/test_build_daily_digest_with_task_logs.py tests/test_build_daily_digest.py -q
- Claim: GitHub workflow still produces artifact after v0.5.
  Verification type: not verified
  Raw evidence: pending after merge

## Rollback evidence

- Failure scenario: v0.5 digest becomes confusing or overclaims from task logs.
  Rollback command / toggle / procedure: remove task logs from `logs/tasks` or pass an empty `--task-log-dir`; digest returns to v0.4 git fallback language.
  Verified rollback: partial
- Failure scenario: parser breaks workflow.
  Rollback command / toggle / procedure: revert the v0.5 commit and use v0.4.1 release tag.
  Verified rollback: partial

## Human-readable final summary

- v0.5 adds task-level evidence so the daily report stops guessing from git only.
- The report can now show the user's explicit asks and the agent's self-decisions when task logs exist.
- No LLM is added; token cost remains zero by default.
