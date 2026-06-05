# AI Development Control Log

[![validate](https://github.com/zycaskevin/ai-development-control-log/actions/workflows/validate.yml/badge.svg)](https://github.com/zycaskevin/ai-development-control-log/actions/workflows/validate.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> 我不一定看得懂 AI 寫的每一行 code。
> 但我一定要看得懂，它什麼時候偷偷替我做主。

[简体中文](README.zh-CN.md) | [English](README.en.md)

## 這份東西是什麼？

這是一份給非工程背景創業者、產品負責人、獨立開發者用的 **AI 開發控制日誌**。

它不是教你寫程式。
它是教你怎麼管理一個很會寫程式、但偶爾會自作主張的 AI 助理。

AI coding agents 很厲害。Claude Code、Cursor、Codex、OpenCode 這類工具，已經可以把一個產品從 0 慢慢堆起來。

但真正嚇人的地方不是 AI 寫錯。
寫錯還能修。

真正嚇人的是：它沒問你，就替你做了產品決策。

你只是叫它改一個小功能，它順手改了核心計算邏輯。
你只是叫它調整畫面，它順手重構一整個模組。
你只是叫它補一個欄位，它順手改了資料庫 schema。
它可能不是故意的。它甚至覺得自己在幫你。

問題是，它沒有告訴你。

這份 repo 要解決的就是這件事。

## 一句話

> Karpathy guidelines 管 AI 怎麼寫 code。
> AI Development Control Log 管 AI 有沒有越權。

## 你不需要看懂 code

你需要看懂這些：

- AI 做了什麼？
- 哪些是你明確要求的？
- 哪些是 AI 自己決定的？
- 哪些地方偏離原本規格？
- 有沒有碰到資料、金流、production、權限、核心計算？
- 驗證了什麼？沒驗證什麼？
- 出事怎麼退？

這些是人話。不是 code。

只要 AI 老實寫出來，非工程背景的人也能管理它。

## 這份規範怎麼來的？

它結合了兩件事。

第一個是 Karpathy-style coding guidelines：

- Think before coding：不要亂猜，先講假設
- Simplicity first：不要過度設計
- Surgical changes：只改該改的，不要順手亂改
- Goal-driven execution：要有驗證標準，不要只說「完成」

第二個是 Control Log：

- 把 AI 的假設寫出來
- 把 AI 自己做的決定寫出來
- 把偏離規格的地方寫出來
- 把取捨寫出來
- 把不可逆操作擋下來
- 把驗證和回滾寫清楚

Karpathy 讓 AI 少寫爛 code。
Control Log 讓 AI 不要偷偷當老闆。

## 什麼時候一定要用？

只要做錯會痛，就用。

特別是：

- 金流、付款、訂閱、佣金
- 使用者資料、CRM、隱私資料
- 資料庫 schema、migration、批次更新
- production deploy、cutover、webhook、gateway
- 權限、登入、auth、secret
- 核心計算邏輯
- 多 agent 協作
- 任何你看不懂，但出事很麻煩的任務

小 typo、單行文案、沒有副作用的小修改，可以不用。

## 最重要的規則

### 1. 每個改動都要能追溯到需求

> Every changed line should trace directly to the user's request.

如果你叫 AI 改按鈕文案，它卻動到付款邏輯，這不是「順手優化」。
這是越權。

### 2. AI 自己決定的事情要分開列

AI 可以建議。
AI 可以提出更好的做法。
但它不能默默替你決定。

### 3. 不可逆操作必須停下問

碰到這些事，AI 必須停：

- 刪資料
- 改資料庫結構
- 推上 production
- 改金流、付款、訂閱
- 改權限、auth、secret
- 改核心計算邏輯
- 大規模重構

不是寫在最後報告。
是做之前就停下來問。

### 4. 「已完成」不是證據

AI 說完成，不代表完成。
AI 說測過，不代表真的測過。

它要寫清楚：

- 跑了哪些測試
- 哪些通過
- 哪些沒跑
- 哪些只是推測
- 如果出事怎麼回滾

每份回報也應該先標可信度：

```text
✅ 已真實驗證：有工具輸出、測試、live smoke 或 production check 可支撐
⚠️ 部分驗證：只驗證其中一部分，或缺少 live / production 證據
❌ 未驗證：只是推論、閱讀文件、或尚未執行真實檢查
```

測試類型也要分清楚，不要把 mock test 說成真實可用：

```text
mock：只代表模擬通過
unit：單元測試通過
integration：整合測試通過
live smoke：真實 CLI / API / 服務最小可用檢查通過
production verified：production 環境已確認
```

### 5. v0.2 Evidence Layer — 從「AI 自報」升級成「可交叉驗證」

v0.1 把「驗過 / 部分驗過 / 沒驗過」和測試類型標籤分開，已經是一步。
但寫 Log 的人和被記錄的還是同一個 AI —— 這就是楊士弘說的
「被監督者也是報告者」問題。

v0.2 把每個宣稱都綁到一個 **客觀、可被重新執行** 的證據上，
不再只是 AI 自己說：

| 子區塊 | 綁定的客觀物件 |
|---|---|
| 9.5.1 改動檔案 | `git diff --name-status <BASE>...HEAD` |
| 9.5.2 Diff 摘要（逐檔） | `git diff` + 人工白話 |
| 9.5.3 測試結果 | 原始 pytest / vitest / go test 輸出，**不是「通過」兩個字** |
| 9.5.4 驗證類型 | mock / unit / integration / live smoke / production — 強制標出 |
| 9.5.5 Commit Hash / PR 連結 | `git rev-parse HEAD` + PR URL |
| 9.5.6 高風險接觸點 | DB / 金流 / 權限 / secret / production / 核心計算 / 外部副作用 |
| 9.5.7 回滾證據 | 「可回滾」不算 —— 要真的把 revert / 還原 / 重新部署跑過一次 |

實作工具：

```bash
python scripts/collect_evidence.py --base main
# or
bash scripts/collect_evidence.sh main
```

會直接吐出 9.5.1 改動檔案與 9.5.3 測試結果，AI 只要貼進去就好，
不用手打。

詳細設計：見 [`docs/automation/evidence-layer-v0.2.md`](docs/automation/evidence-layer-v0.2.md)。
v0.2 模板：

- [`templates/implementation-control-log.v0.2.md`](templates/implementation-control-log.v0.2.md)
- [`templates/implementation-control-log.zh-TW.v0.2.md`](templates/implementation-control-log.zh-TW.v0.2.md)
- [`examples/billing-change-control-log.v0.2.md`](examples/billing-change-control-log.v0.2.md)（金流範例，附 v0.2 證據）

## 會每天記、每天寄嗎？

**v0.4 起：可以，而且不需要你自己手改 workflow。v0.5 起：如果 agent 寫了 task log，daily digest 會優先用任務級證據，不再只靠 git 猜。**

具體行為：

- 每天 02:00 UTC（= 10:00 台北時間）GitHub Actions 自動跑一次
- 自動從最近 24 小時 git 活動產出一份可讀的 `logs/daily/YYYY-MM-DD-digest.zh-TW.md`
- 如果存在 `logs/tasks/*.md` task control logs，報告會優先讀它們，列出「使用者明確要求」與「AI 自己決定」
- 如果沒有 task logs，仍保留 v0.4 git-based fallback，誠實標示哪些事無法可靠判斷
- 報告會回答 7 個問題：AI 做了什麼、哪些是 AI 自己決定、有沒有高風險、怎麼退
- 報告會上傳成 workflow artifact
- 如果你讓 agent 設定了配送頻道，會自動寄到 Slack / 飛書 / Telegram / Email
- 如果沒設定配送頻道，預設不外寄，只保留 artifact
- 預設不呼叫 LLM，所以 daily digest 的模型 token 成本是 0

如果你想 5 分鐘內接好，請看：[**5 分鐘接上指南：交給 agent 安裝**](#5-分鐘接上指南交給-agent-安裝)。

更早版本（v0.3.1 之前）的設計哲學是「手動 SOP，不自動跑」。v0.4 把它升級成「**每天自動產出可讀報告，配送交給 agent 安裝**」。v0.4 的 daily digest 回答的問題也跟 v0.3.1 不一樣——見下表。

### v0.3.1 vs v0.4 daily digest 差在哪？

| 問題 | v0.3.1 digest | v0.4 digest |
|---|---|---|
| AI 今天做了什麼？ | commit / PR 標題 | 每個動作標 ✅/⚠️/❌ 是 user 叫的還是 AI 自決 |
| 哪些是 AI 自決？ | 自由文字段落 | 表格 + 「該不該先問你」欄 |
| 偏離規格了嗎？ | 自由文字 | 表格 + 「是否需要你確認」 |
| 高風險 gate 觸發了嗎？ | 自由文字 | 8 個風險項逐項 ✅/❌ |
| 驗證了什麼 / 沒驗證什麼？ | 自由文字 | 表格，「沒驗證」也要寫 |
| 出事怎麼退？ | 自由文字 | 表格 + 「已驗證可退」 |
| 這份你看懂嗎？ | **沒有** | §8 明確問你 ✅/⚠️/❌ |
| 1 分鐘看完摘要 | **沒有** | §0 1 分鐘版（老闆專用）|

v0.4 的 digest 是**老闆抓 AI 越權用的**，不是「AI 員工自我感覺良好日報」。如果你要的是工作進度（PR、issue、commit），請看 GitHub 自己的 daily digest。

### v0.5 補上什麼？

v0.4 的限制是：只看 git 時，它能知道「改了什麼」，但不能可靠知道「這是你要求的，還是 AI 自己決定的」。

v0.5 新增 task-level control log：

- 模板：`templates/task-control-log.zh-TW.md` / `templates/task-control-log.en.md`
- 建議路徑：`logs/tasks/YYYY-MM-DD-<slug>.md`
- Parser：`scripts/collect_task_logs.py`
- Daily digest：有 task logs 時優先使用；沒有時回到 v0.4 的保守 fallback

也就是說，agent 每次任務結束後多寫一份小紀錄，隔天的 daily digest 就能更準確回答：哪些是你明確要求、哪些是 AI 自己決定。

## 5 分鐘接上指南：交給 agent 安裝

**目標**：fork 完這個 repo，5 分鐘內開始每天收到一份「你看得懂的 AI 做了什麼」報告。

你不用自己改 workflow。請直接把這段給你的 coding agent：

```text
請幫我安裝 AI Development Control Log 的每日報告。
我要每天收到 1 分鐘看得懂的 digest。
請照 docs/install/agent-assisted-install.zh-TW.md 做，幫我選配送頻道、設定 GitHub Actions secrets、觸發 workflow、確認 artifact 和外寄結果。
不要把任何 token / webhook / secret 寫進 git。
```

agent 會問你一個問題：

> 你要每天報告寄去哪裡？Slack / 飛書 / Telegram / Email / 不外寄

然後 agent 會幫你做：

1. 設定 `DELIVERY_PROVIDER`
2. 把 webhook / token 放進 GitHub Actions secrets
3. 本機產生一次 digest 並驗證
4. 觸發 GitHub Actions workflow 跑一次
5. 確認 artifact 有產出
6. 如果你選了外寄，確認訊息真的有送到頻道

完整 agent 任務卡：[`docs/install/agent-assisted-install.zh-TW.md`](docs/install/agent-assisted-install.zh-TW.md)。
可複製 prompt：[`templates/agent-install-prompt.zh-TW.md`](templates/agent-install-prompt.zh-TW.md)。

### 之後不想收怎麼關？

請 agent 幫你跑：

```bash
gh variable set DELIVERY_PROVIDER --body none
```

或者刪掉對應的 webhook secret。

### 為什麼交給 agent？

因為這個 repo 的目標不是教使用者學 GitHub Actions。

目標是：**裝一次，以後每天收到看得懂的報告。**

## 語言選擇

Control Log 與 Daily Digest 不能硬寫英文。每份 log 都應該先指定：

```text
輸出語言：zh-TW / zh-CN / en / ja / custom
讀者：創辦人 / operator / 工程師 / 客戶 / 內部團隊
語氣：白話 / 技術 / 高層摘要 / 客戶可讀
技術名詞是否翻成人話：是 / 否
```

對 創辦人 / operator 內部使用，預設是：

```text
語言：繁體中文 zh-TW
語氣：白話、CEO 可讀、少技術黑話
```

公開 repo 可以保留英文文件，但不能只有英文模板。繁中使用者應該能直接看懂 AI 今天做了什麼決定。

## 快速使用

### 方法 A：只拿日誌模板

繁中使用者建議直接複製繁中模板：

```bash
cp templates/implementation-control-log.zh-TW.md ./implementation-control-log.md
```

如果你的團隊偏英文，則可使用英文 / 雙語模板：

```bash
cp templates/implementation-control-log.md ./implementation-control-log.md
```

然後要求 AI：

> 這次任務請邊做邊更新 `implementation-control-log.md`。不要做完才補。凡是你自行決定、偏離規格、碰到不可逆操作，都要寫進去。

### 方法 B：Claude Code

把 [`CLAUDE.md`](CLAUDE.md) 合併進你的專案 `CLAUDE.md`。

### 方法 C：Cursor

把 Cursor rule 複製到你的專案：

```bash
mkdir -p .cursor/rules
cp .cursor/rules/ai-development-control-log.mdc your-project/.cursor/rules/
```

### 方法 D：Hermes / Agent skill

使用：

```text
skills/ai-development-control-log/SKILL.md
```

## 日誌模板

任務級 Control Log 模板：

- [`templates/implementation-control-log.zh-TW.md`](templates/implementation-control-log.zh-TW.md)：繁體中文，給中文使用者直接套用
- [`templates/implementation-control-log.md`](templates/implementation-control-log.md)：英文 / 雙語欄位，適合英文團隊或跨語言團隊
- [`templates/task-control-log.zh-TW.md`](templates/task-control-log.zh-TW.md)：v0.5 任務級 evidence log，讓每日報告知道 user asked / AI self-decided
- [`templates/task-control-log.en.md`](templates/task-control-log.en.md)：v0.5 English task-level evidence log
- [`templates/implementation-control-log.zh-TW.v0.2.md`](templates/implementation-control-log.zh-TW.v0.2.md)：v0.2 證據層，繁中
- [`templates/implementation-control-log.v0.2.md`](templates/implementation-control-log.v0.2.md)：v0.2 證據層，英文

Daily Decision Digest 模板：

- [`templates/daily-decision-digest.zh-TW.md`](templates/daily-decision-digest.zh-TW.md)：繁體中文，每日 AI 決策摘要
- [`templates/daily-decision-digest.en.md`](templates/daily-decision-digest.en.md)：英文，每日 AI 決策摘要

Delivery automation 模板與範例：

- [`docs/automation/optional-delivery-automation.md`](docs/automation/optional-delivery-automation.md)：選配自動寄送規則
- [`templates/daily-digest-delivery-config.zh-TW.md`](templates/daily-digest-delivery-config.zh-TW.md)：繁中寄送設定模板
- [`templates/daily-digest-delivery-config.en.md`](templates/daily-digest-delivery-config.en.md)：英文寄送設定模板

核心欄位：

0. 語言與讀者設定
1. 任務目標
2. 使用者明確要求
3. 待釐清問題 / 假設
4. AI 自行決定
5. 偏離規格
6. Surgical Change 檢查
7. 取捨
8. 高風險 / 不可逆操作
9. 驗證結果
10. 回滾方式

回報時請額外標出：可信度、測試類型，以及能支撐結論的真實工具輸出。


## 驗證腳本

這個 repo 附了一個輕量驗證腳本：[`scripts/validate.py`](scripts/validate.py)。

它不是測你的產品功能，而是檢查 protocol kit / repo 是否仍然完整：

- 必要文件是否存在且不是空檔
- `SKILL.md` 是否有基本 frontmatter
- `templates/implementation-control-log.md` 與 `templates/implementation-control-log.zh-TW.md` 是否保留核心 section
- Daily Digest / delivery automation 模板是否保留安全 section
- 範例與文章是否仍在預期路徑

### 驗證模式

```bash
python scripts/validate.py --mode repo
python scripts/validate.py --mode kit
python scripts/validate.py --mode strict
```

| mode | 用途 | 是否要求 private live log |
|---|---|---|
| `repo` | 維護這個 protocol repo 本身，預設模式 | ❌ 不要求；使用 public-safe example |
| `kit` | 給 fork / 使用者套用 | ❌ 不要求；使用 public-safe example |
| `strict` | CI / maintainer 嚴格檢查，目前等同 `repo` | ❌ 不要求；使用 public-safe example |

預設執行：

```bash
python scripts/validate.py
```

等同：

```bash
python scripts/validate.py --mode repo
```

成功時輸出：

```text
VALIDATION PASSED (repo mode)
```

失敗時會列出缺失項，例如：

```text
VALIDATION FAILED (repo mode)
- missing: templates/implementation-control-log.md
- template missing section: Verification Results
```

GitHub Actions 也會在 push / pull request 時執行 repo mode 驗證與測試。

## 範例

- [`examples/calc-feature-control-log.md`](examples/calc-feature-control-log.md)：接近核心計算邏輯的功能
- [`examples/billing-change-control-log.md`](examples/billing-change-control-log.md)：金流 / 訂閱變更
- [`examples/billing-change-control-log.v0.2.md`](examples/billing-change-control-log.v0.2.md)：同範例的 v0.2 證據層版本
- [`examples/database-migration-control-log.md`](examples/database-migration-control-log.md)：資料庫 migration 與 rollback
- [`examples/multi-round-control-log.md`](examples/multi-round-control-log.md)：同一任務多輪更新
- [`examples/daily-decision-digest.zh-TW.md`](examples/daily-decision-digest.zh-TW.md)：繁中每日 AI 決策摘要範例
- [`examples/daily-decision-digest.en.md`](examples/daily-decision-digest.en.md)：英文每日 AI 決策摘要範例
- [`examples/language-selection-control-log.zh-TW.md`](examples/language-selection-control-log.zh-TW.md)：繁中語言選擇 control log 範例
- [`examples/github-actions-daily-digest.yml`](examples/github-actions-daily-digest.yml)：GitHub Actions local-only digest artifact 範例
- [`examples/hermes-cron-daily-digest.zh-TW.md`](examples/hermes-cron-daily-digest.zh-TW.md)：Hermes cron 每日摘要範例

## 可以分享的文章

如果你想把這套觀念分享給其他人，可以從這篇開始改：

- [`articles/manage-ai-engineer-with-control-log.md`](articles/manage-ai-engineer-with-control-log.md)

## Repo 結構

```text
.
├── README.md
├── README.zh-CN.md
├── README.en.md
├── CLAUDE.md
├── .cursor/rules/ai-development-control-log.mdc
├── skills/ai-development-control-log/SKILL.md
├── templates/
│   ├── implementation-control-log.zh-TW.md
│   ├── implementation-control-log.md
│   ├── implementation-control-log.zh-TW.v0.2.md
│   ├── implementation-control-log.v0.2.md
│   ├── daily-decision-digest.zh-TW.md
│   ├── daily-decision-digest.en.md
│   ├── agent-install-prompt.zh-TW.md
│   ├── agent-install-prompt.en.md
│   ├── agent-install-prompt.zh-CN.md
│   └── irreversible-operations-checklist.md
├── docs/
│   ├── automation/
│   │   ├── daily-digest-v0.4.md
│   │   ├── optional-delivery-automation.md
│   │   └── evidence-layer-v0.2.md
│   ├── install/
│   │   ├── agent-assisted-install.zh-TW.md
│   │   ├── agent-assisted-install.en.md
│   │   └── agent-assisted-install.zh-CN.md
│   └── plans/
├── examples/
├── logs/
├── articles/
├── scripts/
│   ├── build_daily_digest.py
│   ├── send_daily_digest.py
│   ├── validate_daily_digest.py
│   ├── validate.py
│   ├── collect_evidence.py
│   └── collect_evidence.sh
└── tests/
```

## License

MIT
