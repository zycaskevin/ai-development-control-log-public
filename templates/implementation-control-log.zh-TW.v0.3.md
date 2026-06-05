# 任務執行控制日誌（v0.3 — Replit-proof）

> v0.3 從 v0.2 的改變：
> - 9.5.6 高風險接觸點改為**由工作樹自動偵測**（scripts/detect_high_risk_touchpoints.py）。
>   AI 只能補註，不能刪除自動偵測到的列。
> - 9.5.7 回滾證據改為**真的跑 `git revert --no-commit`** 在 throwaway worktree 上
>   （scripts/collect_rollback_evidence.py）。沒有 `Exit code: 0` 且 conflict markers 為 0，
>   「可回滾」三個字不算證據。
> - 新增 Section 0.5（Actor & Provenance）— v0.3.0 是 placeholder，v0.3.1 變強制。

## 0. 語言與讀者設定

| 欄位 | 值 |
|---|---|
| 輸出語言 | zh-TW / zh-CN / en / ja / 自訂 |
| 讀者 | 創辦人 / operator / 工程師 / 客戶 / 內部團隊 |
| 語氣 | 白話 / 技術 / 高層摘要 / 客戶可讀 |
| 技術名詞是否翻成人話 | 是 / 否 |

## 0.5 Actor & Provenance（v0.3.1 placeholder）

> v0.3.0 這段是參考用。v0.3.1 開始變強制欄位。詳見 docs/automation/evidence-layer-v0.3.md。

| 欄位 | 值 |
|---|---|
| Agent model       | claude-sonnet-4-6 / minimax-m3 / human / other |
| Agent session     |  |
| Human approver    | <github handle 或 "self-approved"> |
| Approval evidence | <PR review URL 或 "no human in loop"> |
| Wall clock start  | ISO-8601 |
| Wall clock end    | ISO-8601 |

## 1. 任務目標

### 時間軸

| 欄位 | 值 |
|---|---|
| 任務開始時間 |  |
| 最後更新時間 |  |

### 目標
-

### 不做什麼 / 範圍外
-

### 成功標準
- [ ]

## 2. 使用者明確要求

這裡只寫使用者明確講出的要求，不要混入 AI 自己補的推論。

-

## 3. 待釐清問題與假設

| 問題 / 模糊處 | 目前假設 | 如果假設錯了，修改成本（低/中/高） | 是否需要使用者確認 |
|---|---|---:|---|
|  |  |  |  |
| 範例：這次是否會碰 production config？ | 不會，只限 local / staging | 高 | 若要碰 production，必須先確認 |

## 4. AI 自行決定

這裡列出 AI 在使用者沒有明講時，自己做出的選擇。

| 決定 | 為什麼這樣做 | 考慮過的替代方案 | 風險 |
|---|---|---|---|
|  |  |  |  |

## 5. 規格偏離

這裡列出「使用者原本要 A，但實作變成 B」的地方。

| 偏離項目 | 原因 | 使用者是否同意 | 是否需要後續處理 |
|---|---|---|---|
| 目前沒有 |  |  |  |

## 6. Surgical Change 追溯

每個改動都應該能追溯到使用者需求。

| 檔案 / 區域 | 改了什麼 | 對應哪個需求 | 是否必要 | 備註 |
|---|---|---|---|---|
|  |  |  |  |  |

## 7. 取捨

| 選擇 | 好處 | 成本 / 代價 | 什麼時候要重新檢查 |
|---|---|---|---|
|  |  |  |  |

## 8. 高風險 / 不可逆操作檢查

請逐項標記。

- [ ] 刪除或覆寫使用者資料
- [ ] 修改資料庫 schema 或 migration
- [ ] 部署到 production 或修改 production config
- [ ] 修改付款、金流、訂閱、財務邏輯
- [ ] 修改登入、權限、授權、secret
- [ ] 修改核心計算或商業邏輯
- [ ] 執行不可逆外部副作用
- [ ] 超出需求的大範圍重構
- [ ] 以上皆無

如果任何高風險項目被勾選，必須停下來，先取得使用者明確確認。

## 9. 驗證結果

### 9.1 回報可信度
- [ ] ✅ 已真實驗證：有真實工具輸出、測試、live smoke 或 production check 支撐
- [ ] ⚠️ 部分驗證：只驗證一部分，或缺少 live / production 證據
- [ ] ❌ 未驗證：只是推論、閱讀文件，或尚未實際執行檢查

### 9.2 測試類型標籤
- [ ] mock：只代表模擬通過
- [ ] unit：單元測試通過
- [ ] integration：整合測試通過
- [ ] live smoke：真實 CLI / API / 服務最小可用檢查通過
- [ ] production verified：production 環境已確認

### 9.3 已驗證
| 檢查 | 指令 / 方法 | 結果 |
|---|---|---|
|  |  |  |

### 9.4 未驗證
| 區域 | 為什麼未驗證 | 風險 |
|---|---|---|
|  |  |  |

## 9.5 證據層（v0.3）

> 目標：被監督的一方（AI）不再同時也是報告的一方（Log）。
> 每個宣稱都綁定到人類可重新執行的客觀物件。

### 9.5.1 改動檔案（客觀）
| 路徑 | 狀態 | 增 / 減行數 | Hash（選填） |
|---|---|---:|---|
|  | 新增 / 修改 / 刪除 |  |  |

填法：
```bash
git diff --name-status <BASE_REF>..<HEAD_SHA>
git diff --numstat <BASE_REF>..<HEAD_SHA>
```

### 9.5.2 Diff 摘要（逐檔）
| 路徑 | 改了什麼（白話） | 公開 API？ | 動到 schema？ |
|---|---|---|---|
|  |  | 是 / 否 | 是 / 否 |

### 9.5.3 測試結果（貼原始輸出，不要寫「通過」兩個字）
| 套件 | 指令 | 結果 | 通過 / 失敗 / 跳過 |
|---|---|---|---|
|  |  | （貼實際輸出） |  |

填法：
```bash
pytest -q 2>&1 | tail -40 > evidence/test-result.txt
```

### 9.5.4 驗證類型
每個宣稱都要勾出「實際上跑到哪一層」。不要混用。

- [ ] mock：只代表模擬通過 —— **不可作為 production gate**
- [ ] unit：單元測試通過
- [ ] integration：整合測試通過
- [ ] live smoke：真實 CLI / API / 服務被實際跑過
- [ ] production verified：production 環境被直接確認

> 沒有標類型的「通過」不算是驗證，只是自我宣稱。

### 9.5.5 Commit Hash / PR 連結
- Commit hash：`<HEAD_SHA>`
- Branch：`<BRANCH>`
- PR 連結：`<URL>`
- 重新驗證指令：`git checkout <BRANCH> && git rev-parse HEAD`

### 9.5.6 高風險接觸點（v0.3 — 自動偵測，列不可刪）

> v0.3 改變：本表由 `scripts/detect_high_risk_touchpoints.py` 從工作樹
> + staged changes 自動產生，比對 `config/high_risk_patterns.yml`。
>
> 驗證器在以下情況擋下：
> 1. 表整段不見
> 2. 自動偵測到的路徑在表裡找不到
> 3. 表裡只有 `None`
>
> AI 只能補註、不能刪列。

| 路徑 | 接觸類型 | 為什麼這是高風險 | 備註（選填） |
|---|---|---|---|
|  |  |  |  |

### 9.5.7 回滾證據（v0.3 — 真的跑過）

> v0.3 改變：「可回滾」三個字不算證據。本表由
> `scripts/collect_rollback_evidence.py` 在 throwaway worktree 跑
> `git revert --no-commit --no-edit <HEAD>`，並記錄真實 exit code 跟
> conflict markers。
>
> 驗證器在以下情況擋下：
> 1. 整段不見
> 2. `Exit code` 不是 0，或 `Conflict markers` 不是 0
> 3. 非 trivial task 卻只填 `n/a`

| 回滾步驟 | 指令 | Exit code | Conflict markers | 驗證方式 |
|---|---|---:|---|---|
| Revert commit | `git revert --no-commit --no-edit <HEAD_SHA>` | 0 | 0 unmerged, 0 .rej | 在 HEAD~1 的 throwaway worktree 上跑 |

填法：
```bash
python scripts/collect_rollback_evidence.py --sha <HEAD_SHA>
```

## 10. 回滾計畫

如果這次變更出問題，回滾方式：

- Commit / branch：
- 要還原的檔案：
- 資料恢復步驟：
- 設定回滾步驟：

## 11. 給人類審查的最終摘要

| 項目 | 摘要 |
|---|---|
| 改了什麼 |  |
| 沒改什麼 |  |
| AI 自行決定 |  |
| 規格偏離 |  |
| 已驗證 |  |
| 未驗證 |  |
| 回滾方式 |  |
