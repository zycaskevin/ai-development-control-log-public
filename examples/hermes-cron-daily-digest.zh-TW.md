# Hermes Cron Daily Digest 範例

> 這是示範卡，不會自動建立 cron。建立排程前，先確認 delivery target 與安全 gate。

## 1. 自動寄送是選配，不是預設

建議第一輪只用 local output：

```text
deliver: local
repeat: 5
```

確認摘要品質穩定後，再改成：

```text
deliver: origin
```

## 2. 寄送通道

Hermes cron 建議分三階段：

| 階段 | deliver | 用途 |
|---|---|---|
| Trial | local | 只保存，不打擾操作者 |
| Internal | origin | 回到目前對話 / 內部 DM |
| Team | platform:chat_id | 送到明確指定群組 |

範例 prompt：

```text
每天產出一份 Daily AI Decision Digest。請讀取 repo 內最近的 control logs / PR summaries / agent-decision-digest，輸出繁體中文、高層可讀版本。每個結論必須標 ✅/⚠️/❌，並列出真實驗證證據。若發現 secret、個資、高風險 gate 或不確定外部通道，請只輸出 draft，不要宣稱已送出。
```

## 3. 安全 gate

建立 cron 前檢查：

| Gate | 狀態 |
|---|---|
| 是否只讀 repo / logs | pass / fail |
| 是否不會自動 merge / deploy | pass / fail |
| 是否不含 secret / token / customer PII | pass / fail |
| 是否 founder-facing 使用 zh-TW | pass / fail |
| 是否高風險內容 draft-first | pass / fail |

## 4. 驗證證據

cron 建立後，第一次請手動 run 一次並保留：

```text
- job_id
- deliver mode
- latest output path or message URL
- safety gate result
- whether founder-facing digest is readable
```

可信度標籤：

```text
⚠️ 部分驗證：只有 local output，不代表外部通道已成功送達。
✅ 已真實驗證：有 job run output + 目標訊息 URL / artifact URL。
```

## 5. 回滾方式

```text
cronjob(action='pause', job_id='...')
cronjob(action='remove', job_id='...')
```

如果已經送到錯誤通道：

1. 停止 cron。
2. 保留輸出與送達證據。
3. 發更正訊息。
4. 修正 delivery config / safety gate。
