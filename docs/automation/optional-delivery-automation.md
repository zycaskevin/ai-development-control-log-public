# Optional Daily Digest Delivery Automation

> 目標：把 Daily AI Decision Digest 從「手動產出」延伸成「可選擇自動寄送」，但不讓 repo 預設替使用者發送外部訊息。

---

## 1. 自動寄送是選配，不是預設

這個 repo 的預設狀態仍然是：

```text
不自動每天記。
不自動每天寄。
不自動連接任何外部平台。
```

自動寄送只有在使用者明確配置 delivery channel 後才啟用。原因是 Daily Digest 可能包含：

- AI 自主決策
- 任務成本與驗證狀態
- 專案名稱、PR、內部路線圖
- 高風險 gate 或未驗證結論

所以 delivery automation 是一層 **optional wrapper**，不是 protocol 本體。

---

## 2. 寄送通道

建議從低風險到高風險分層啟用：

| 通道 | 適合情境 | 風險 | 建議預設 |
|---|---|---:|---|
| local file only | 初次試跑、私人專案 | 低 | ✅ 開 |
| GitHub Actions artifact / issue comment | repo 內部追蹤 | 中 | ⚠️ 需確認 |
| Hermes cron → origin chat | operator / internal agent system | 中 | ⚠️ 需確認 |
| Feishu / Lark bot | 團隊每日摘要 | 中高 | ⚠️ draft-first |
| Email / Telegram / public channel | 外部或跨團隊 | 高 | ❌ 不預設 |

最小安全原則：

```text
先 local 保存，再人工確認；
再內部通道；
最後才外部通道。
```

---

## 3. 安全 gate

啟用自動寄送前，必須逐項檢查：

| Gate | 規則 | 預設動作 |
|---|---|---|
| Secret / token | 摘要不得含 secret、token、cookie、private key | 停下，不寄 |
| Internal state | customer-facing 通道不得出現 dry-run / committed / preview / internal reasoning | 改寫或停下 |
| PII / customer data | 不寄個資、客戶資料、未授權 CRM 細節 | 停下 |
| Unverified claim | 未驗證結論必須標 ❌ 或 ⚠️ | 加標籤後才可寄 |
| High-risk operation | production、付款、auth、DB schema、外部副作用 | draft-first，等人確認 |
| Wrong audience | 給創辦人/操作者的語氣不能直接寄給 customer | 重新生成對應版本 |

如果任一 gate 不確定，delivery 狀態必須降級為：

```text
draft only / local only
```

---

## 4. 驗證證據

每次 delivery run 的報告至少要保留：

```text
- digest 檔案路徑或 artifact URL
- 使用的 delivery config
- 實際寄送目標或 local-only 狀態
- safety gate 結果
- 工具輸出或 job URL
- 可信度標籤：✅ / ⚠️ / ❌
```

不要只寫：

```text
已寄出
```

要寫成：

```text
✅ 已真實驗證
- 產物：logs/daily/2026-06-03.zh-TW.md
- 通道：local file only
- gate：secret / PII / high-risk 均未觸發
- 工具輸出：GitHub Actions run URL 或 Hermes cron output
```

---

## 5. 回滾方式

delivery automation 的 rollback 應該分成三層：

| 層級 | 回滾方式 |
|---|---|
| Template / docs | revert PR 或恢復模板 |
| Schedule | disable GitHub Actions schedule / pause Hermes cron |
| External channel | 移除 webhook、bot token、email recipient 或 channel mapping |

高風險情境下，不要刪除歷史 digest；改成：

```text
保留證據 → 停止新 delivery → 標記錯誤 → 再修正模板 / gate
```
