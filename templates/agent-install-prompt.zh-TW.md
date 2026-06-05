# Agent 安裝 Prompt（繁中）

把這段貼給你的 coding agent。

```text
請幫我安裝 AI Development Control Log 的每日 AI Decision Digest。

我要的結果：
- 裝一次就忘。
- 每天自動產出一份 1 分鐘看得懂的報告。
- 報告要能寄到我選的頻道：Slack / 飛書 / Telegram / Email / 不外寄。
- 如果我還沒有憑證，請你引導我建立，不要叫我自己研究文件。
- 第一次不確定時，先設成不外寄，只驗證 GitHub Actions artifact。

請照 docs/install/agent-assisted-install.zh-TW.md 做：
1. 確認 gh auth / repo / workflow。
2. 問我要寄去哪裡。
3. 幫我安全設定 GitHub Actions variable/secrets。
4. 本機跑 build / validate / tests。
5. 觸發 GitHub Actions 真跑一次。
6. 下載 artifact 並確認內容不是空模板。
7. 如果我選外寄，確認真的送到目標頻道。
8. 最後用白話回報 run URL、artifact、外寄狀態、怎麼關閉。

安全規則：
- 不要印出任何 token、webhook、API key。
- 不要把 secret 寫進 git、issue、PR、README、commit message 或 chat log。
- 如果 secret 不小心曝光，先停下，叫我 revoke / rotate。
```
