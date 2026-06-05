# 給 Facebook 社群的正式回覆（v0.2 已 merge 進 main）

> 使用對象：之前在 GitHub 與 FB 社群針對「AI 寫 code 的 repo 不實際 /
> AI 是放大器 / 不會寫程式的人不該靠 AI」發言的朋友。
>
> 發文前提：v0.2 已經 merge 進
> `zycaskevin/ai-development-control-log` 的 main branch
> （PR #8 + PR #9，49 個 pytest 測試 + pytest CI 全綠）。
>
> 字數控制：~500 字以內，可在 FB 一次貼完。語氣穩重、不嗆、不卑不亢。
> 結尾留一個真的可以下載 / 看 / 反饋的入口（PR 連結），不要叫賣。

---

## 發文版本 A — 長版（推薦主貼）

最近 repo 收到不少質疑：

> 「AI 是放大器，不會寫程式的人硬用 AI 是問題」
> 「AI 自己產的 log 不算 log，被監督者也是報告者」
> 「寫 repo 不如把時間拿去學寫程式」

這些質疑是對的。我沒有反駁的立場。

這個 repo 本來就不是「讓不會寫程式的人假裝自己會寫」。
它要做的是一件比較小、也比較具體的事：

**讓 AI Coding Agent 的行為留下可追蹤、可驗證、可回滾的紀錄。**

v0.1 我們做了「驗過 / 部分驗過 / 沒驗過」跟測試類型標籤。
但寫 Log 的人和被記錄的還是同一個 AI —— 這點楊士弘講得對。

所以 v0.2（剛 merge 進 main）我加了一層 **Evidence Layer**：
每個宣稱都綁到一個客觀、人類可重新執行的證據，
不只是 AI 自己說。

具體多了什麼：

- **真實 `git diff`**：哪些檔案被改、加了多少行、減了多少行 —— 不是 AI 口述
- **真實測試輸出**：pytest / vitest / go test 的 raw output，貼進 Log，不是「通過」兩個字
- **驗證類型強制標出**：mock / unit / integration / live smoke / production —— 沒有標類型的「通過」不算驗證
- **Commit Hash + PR 連結**：你 `git rev-parse HEAD` 就能還原
- **高風險接觸點**：AI 有沒有越過 DB / 金流 / 權限 / production 邊界
- **回滾證據**：「可回滾」不算證據，要真的把 `git revert` / 還原 / 重新部署跑過

隨 PR #9 一起進了 49 個 pytest 測試 + 修掉 3 個真 bug
（包含 CI 之前其實沒在跑測試這件事）—— 有興趣看 code 的人，
PR 在這裡：
https://github.com/zycaskevin/ai-development-control-log/pull/8
https://github.com/zycaskevin/ai-development-control-log/pull/9

repo 不會讓不會寫程式的人變會寫。
但如果有人在用 AI Coding，這層 Evidence Layer 至少讓你不用
只信 AI 自己的嘴。

歡迎繼續罵、繼續指問題。罵完有具體建議更好。

---

## 發文版本 B — 短版（備用，給只想看 3 行的朋友）

謝謝指教。「AI 是放大器」「被監督者也是報告者」這兩點都成立，
這個 repo 本來就不是給不會寫程式的人用的。

v0.2（已 merge）做的事很具體：把 Control Log 從「AI 自報」
升級成「可交叉驗證」—— 改動檔案、測試輸出、commit hash、
驗證類型、回滾證據，全部綁到真實工具輸出。

PR #8 / #9、49 個 pytest、3 個真 bug（包含 CI 之前沒在跑測試）。
歡迎繼續看 code：
https://github.com/zycaskevin/ai-development-control-log

---

## 發文守則（給作者自己複查用）

- ✅ 不回嗆「垃圾 / 屎山」等攻擊詞
- ✅ 不膨脹「AI 不會取代工程師」「未來是人機協作」這類空話
- ✅ 把攻擊點轉成具體改進：Evidence Layer 真實物件
- ✅ 給真的可驗證的入口：PR 連結
- ✅ 保留「歡迎繼續罵」的姿態，不關對話
- ❌ 不要講到 v0.3 / roadmap（避免被說「又在畫大餅」）
- ❌ 不要放 AI 工具品牌（避免被說「業配」）
- ❌ 不要「如果你喜歡請給 star」這類叫人氣的 CTA
