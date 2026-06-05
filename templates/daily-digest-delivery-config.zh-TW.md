# Daily Digest Delivery Config（繁中模板）

> 用途：在啟用 Daily AI Decision Digest 自動寄送前，先定義「寄給誰、用什麼語氣、哪些情況停下」。

## 1. 自動寄送是選配，不是預設

| 欄位 | 值 |
|---|---|
| Delivery enabled | yes / no |
| Default mode | local only / draft-first / send |
| Owner | operator / team / custom |
| Output language | zh-TW |
| Audience | founder / operator / engineer / customer / internal team |
| Tone | 白話高層摘要 / 技術摘要 / customer-readable |

預設建議：

```text
Delivery enabled: no
Default mode: local only
```

## 2. 寄送通道

| Channel | Target | Mode | Notes |
|---|---|---|---|
| local file | logs/daily/ | send | 永遠可用，最低風險 |
| GitHub Actions artifact | workflow artifact | draft-first | 不直接通知外部人 |
| Hermes cron | origin chat | draft-first / send | 只限內部確認後開啟 |
| Feishu / Lark | group or DM | draft-first | 團隊摘要，不放 secret |
| Email / Telegram | address / chat | draft-first | 外部通道需額外確認 |

## 3. 安全 gate

| Gate | 檢查 | 結果 | 若失敗 |
|---|---|---|---|
| Secret / token | 無 token、cookie、private key | pass / fail | 停止寄送 |
| PII | 無客戶個資或未授權資料 | pass / fail | 停止寄送 |
| Internal state | 不洩漏 dry-run、preview、committed 等內部狀態 | pass / fail | 改寫或停止 |
| Verification label | 每項結論有 ✅ / ⚠️ / ❌ | pass / fail | 補標籤 |
| High-risk operation | production / auth / billing / DB schema 有無觸發 | pass / fail | draft-first |
| Audience match | 語氣與讀者匹配 | pass / fail | 重寫版本 |

## 4. 驗證證據

| Evidence | Value |
|---|---|
| Digest path / URL |  |
| Delivery mode used | local only / draft-first / send |
| Tool output |  |
| Safety gate result |  |
| Credibility | ✅ 已真實驗證 / ⚠️ 部分驗證 / ❌ 未驗證 |

## 5. 回滾方式

| Failure | Rollback |
|---|---|
| 寄錯通道 | pause schedule，移除 channel mapping |
| 摘要內容錯誤 | 保留證據，補更正摘要 |
| gate 漏檢 | 停止自動寄送，修 gate/template，再重跑驗證 |
| 成本過高 | 降頻、改 local-only、縮短摘要 |
