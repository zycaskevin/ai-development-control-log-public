# Task Control Log — <task name>

> 用途：給 daily AI decision digest 當資料來源。這不是給 AI 自吹自擂的日報；這是讓老闆知道哪些是使用者要求、哪些是 AI 自己決定、哪裡有風險、出事怎麼退。
>
> 建議路徑：`logs/tasks/YYYY-MM-DD-<slug>.md`

## Metadata

- Date: YYYY-MM-DD
- Actor: <agent / human name>
- Repo: <repo name>
- Branch: <branch name>
- Commit / PR: <commit sha / PR URL / pending>

## User explicitly asked

> 只能寫使用者明確說過的事。AI 自己推論的不算。

- <直接引用或白話轉述使用者要求>

## AI self-decided

> AI 自己決定的事要分開列。小決定也可以列，尤其是會影響產品、架構、資料、權限、金流、workflow、release 的決定。

- Decision: <AI 自己決定了什麼>
  Rationale: <為什麼這樣做>
  Should have asked user first: yes/no/gray

## Spec deviations

> 沒偏離就寫 `- 無`。有偏離要寫原規格、實際做法、原因、需不需要使用者確認。

- Deviation: <偏離點>
  Original spec: <原本要求 / 規格>
  Actual implementation: <實際做法>
  Reason: <為什麼偏離>
  Needs user confirmation: yes/no/gray

## High-risk touchpoints

> 只要碰到 DB、auth、secret、金流、production、workflow、webhook、核心計算、對外發布，就要列。

- Path / operation: <file path or operation>
  Risk type: <db/auth/secret/payment/production/workflow/webhook/core-calc/publish/refactor/other>
  User confirmed: yes/no/partial
  Rollback path: <怎麼退>

## Verification evidence

> 貼真實驗證證據，不要寫「應該可以」。沒有驗證就標 `not verified`。
> ⚠️ 不要貼 raw token、webhook URL、API key、Authorization header、cookie、密碼或完整 `.env`。若輸出含 secret，請先改成 `[REDACTED]`。

- Claim: <你驗證了什麼結論>
  Verification type: unit / integration / workflow / sandbox / manual / not verified
  Raw evidence: <command output / CI URL / artifact path / pending，secret 一律 [REDACTED]>

## Rollback evidence

> 「可以 revert」不是證據。寫具體退路；如果尚未驗證，要誠實標 partial/no。
> ⚠️ 回滾指令也不要包含 raw token/webhook/API key。只寫 secret name 或 `[REDACTED]`。

- Failure scenario: <什麼情況下要退>
  Rollback command / toggle / procedure: <具體怎麼退，secret 一律 [REDACTED]>
  Verified rollback: yes / partial / no

## Human-readable final summary

> 給老闆看的 3 行以內摘要。

- <這次任務真正完成什麼、風險在哪、還缺什麼>
