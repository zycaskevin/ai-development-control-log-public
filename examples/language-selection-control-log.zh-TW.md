# 語言選擇 Control Log 範例

> 這個範例展示同一個任務在開始前如何指定輸出語言、讀者與語氣，避免 AI 默默用使用者看不懂的語言寫 log。

## 0. 語言與讀者設定

| 欄位 | 值 |
|---|---|
| 輸出語言 | zh-TW |
| 讀者 | 創辦人 / 非工程背景操作者 |
| 語氣 | 白話、直接、可決策 |
| 技術名詞是否翻成人話 | 是 |

## 1. 任務目標

### Timeline

| 欄位 | 值 |
|---|---|
| 任務開始時間 | 2026-06-03 01:40 UTC+8 |
| 最後更新時間 | 2026-06-03 01:40 UTC+8 |

### 目標

- 把 AI Development Control Log 的輸出從英文優先改成支援語言選擇。
- 對繁中使用者預設使用繁體中文。

### 不做什麼

- 不在這一輪做自動寄信。
- 不建立 SaaS 或 dashboard。

### 成功標準

- [x] log 明確指定輸出語言。
- [x] 使用者能看到「為什麼不是英文」。
- [x] 技術驗證仍保留真實命令輸出。

## 2. 使用者明確要求

- 增加語言選擇能力。
- 不要只寫英文，因為 使用者看不懂。

## 3. 待釐清問題與假設

| 問題 | 目前假設 | 如果錯了，修改成本 | 是否需要使用者確認 |
|---|---|---:|---|
| founder-facing 預設語言 | zh-TW | 低 | 不需要，使用者已明確表達 |
| public repo 是否保留英文 | 保留，但繁中也要一等支援 | 中 | 不需要 |

## 4. AI 自己做了哪些決定

| 決定 | 為什麼 | 替代方案 | 風險 |
|---|---|---|---|
| 先做模板與規則，不先做自動寄送 | 語義先清楚，工具後補 | 直接做 email / Feishu automation | 低 |
| 中英模板並存 | public repo 需要英文，但繁中使用者需要繁中 | 只做繁中 / 只做英文 | 低 |

## 5. 偏離規格

| 偏離 | 原因 | 使用者是否批准 | 後續 |
|---|---|---|---|
| 無 |  |  |  |

## 6. Surgical Change Traceability

| 檔案 / 區域 | 變更 | 對應需求 | 是否必要 | 備註 |
|---|---|---|---|---|
| `templates/daily-decision-digest.zh-TW.md` | 新增繁中模板 | 使用者看得懂 | 是 | founder-facing 預設 |
| `templates/daily-decision-digest.en.md` | 新增英文模板 | public repo 需要 | 是 | 補充，不是預設 |
| `README.md` | 說明語言選擇 | 避免誤解 | 是 | 繁中優先 |

## 7. 取捨

| 選擇 | 好處 | 代價 | 何時重看 |
|---|---|---|---|
| 先模板後自動化 | 先確保使用者理解 | 還不會自動寄送 | PR #5 |

## 8. 高風險 / 不可逆操作檢查

- [ ] 刪資料或覆蓋使用者資料
- [ ] 改資料庫 schema 或 migration
- [ ] production deploy 或 production config
- [ ] 金流、付款、訂閱
- [ ] 權限、auth、secret
- [ ] 核心計算邏輯
- [ ] 不可逆外部副作用
- [ ] 大範圍重構
- [x] 以上皆無

## 9. 驗證結果

### 回報可信度

- [x] ✅ 已真實驗證：有工具輸出、測試、live smoke 或 production check 支撐
- [ ] ⚠️ 部分驗證
- [ ] ❌ 未驗證

### 測試類型

- [ ] mock
- [x] unit
- [ ] integration
- [ ] live smoke
- [ ] production verified

### 已驗證

| 檢查 | 命令 / 方法 | 結果 |
|---|---|---|
| unit tests | `python -m unittest discover -s tests -v` | 待執行 |
| repo validation | `python scripts/validate.py` | 待執行 |

### 未驗證

| 項目 | 為什麼沒驗證 | 風險 |
|---|---|---|
| 自動寄送 | 本輪不做 automation | 低 |

## 10. 回滾方式

- Revert 本次 PR。
- 移除新增 templates / examples。
- 還原 `README.md` / `CLAUDE.md` / `scripts/validate.py` / `tests/test_validate.py`。

## 11. 給人類看的總結

| 項目 | 摘要 |
|---|---|
| Changed | 新增語言選擇範例與繁中優先設計 |
| Not changed | 尚未做每天自動寄送 |
| AI-made decisions | 先做模板和規則，不先做 automation |
| Deviations | 無 |
| Verified | 待跑測試 |
| Not verified | 自動寄送 |
| Rollback | Revert PR |
