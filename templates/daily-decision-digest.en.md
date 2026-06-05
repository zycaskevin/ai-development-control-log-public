# Daily AI Decision Digest

> Purpose: let the user see every day what AI decided for them, what was actually verified, and what still needs human judgment.
> This is not a work-log. It is an authority log.

## 📋 Section 0. 1-Minute Version (for the boss)

> Rule: this section **must come first**. The generator pulls counts and bullets from the 7 sections below by rule, not by LLM.
> Leave a field empty if there is nothing to report. The validator will fail on empty required fields.

| Field | Value |
|---|---|
| How many things AI did yesterday | (auto-counted from §1) |
| How many user-requested / how many AI-self-decided | (auto-counted from §2 §3) |
| How many spec deviations | (auto-counted from §4) |
| How many high-risk gates triggered | (auto-counted from §5) |
| How many decisions still need you | (auto-counted from §7) |
| Full digest link | `logs/daily/YYYY-MM-DD-digest.md` |
| Can you read this? | ✅ / ⚠️ / ❌ (see §8) |

## 0. Language and Audience

| Field | Value |
|---|---|
| Output language | en / zh-TW / zh-CN / ja / custom |
| Audience | founder / operator / engineer / customer / internal team |
| Tone | plain / technical / executive / customer-readable |
| Translate technical jargon | Yes / No |

## 1. What did AI do?

| Action | User-requested? | AI-self-decided? | Evidence |
|---|---|---|---|
|  | ✅ / ⚠️ partial / ❌ no | ✅ / ⚠️ partial / ❌ no | link or file path |

> Rule: every action **must** carry a ✅/⚠️/❌ label on who asked for it. Listing commit titles alone is not enough.

## 2. What did the user explicitly require?

> Rule: only list things the user actually said, wrote in chat, or wrote in issue. AI inference does not count.

- (direct quote or message reference)

## 3. What did AI decide on its own?

| AI-made decision | Why this choice | Alternatives considered | Should AI have asked first? |
|---|---|---|---|
|  |  |  | ✅ yes / ❌ no / ⚠️ grey |

## 4. Did it deviate from the spec?

| Deviation | Original spec | Actual implementation | Reason | Needs user confirmation? |
|---|---|---|---|---|
|  |  |  |  | ✅ / ❌ / ⚠️ |

> Rule: if there were no deviations, write "None" + ✅. Do not skip the section.

## 5. Did it touch any high-risk operation?

| Risk item | Triggered? | How handled | User confirmation obtained? |
|---|---|---|---|
| Delete or overwrite data | ✅ / ❌ |  |  |
| Change DB schema / migration | ✅ / ❌ |  |  |
| Production deploy / cutover | ✅ / ❌ |  |  |
| Payments / billing / subscription | ✅ / ❌ |  |  |
| Auth / permission / secrets | ✅ / ❌ |  |  |
| External publish / customer message | ✅ / ❌ |  |  |
| Core calculation logic | ✅ / ❌ |  |  |
| Broad refactor outside request | ✅ / ❌ |  |  |

> Rule: every ✅ trigger must have either a "user confirmation" row or a "revert path" row.

## 6. What was verified? What was not?

| Conclusion | Credibility | Evidence (raw output, not "should work") |
|---|---|---|
|  | ✅ verified / ⚠️ partial / ❌ unverified | (paste raw output) |

> Rule: list unverified items too. "Should work" is not verification.

## 7. If it breaks, how do you roll back?

| Failure scenario | Rollback path | Rollback actually verified? |
|---|---|---|
|  |  | ✅ / ⚠️ / ❌ |

## 8. Can you read this digest?

> Rule: a simple feedback affordance. We do not actually wire up feedback collection (to keep the product simple), but we do ask.

Please reply with one of ✅ / ⚠️ / ❌:

- ✅ Got it: I know what AI did and what needs my decision
- ⚠️ Partly: some parts were unclear (suggest filing a GitHub issue with the digest file name + unclear parts)
- ❌ Lost: this was not useful to me (strongly suggest filing an issue, with the digest file name + the format you would prefer)

---

## Notes for the author (do not include in the digest itself)

- Do **not** write this as "AI employee reporting how great it did" — this exists so the boss can catch AI overstepping
- Do **not** let an LLM free-write the body — use this template field by field, the 1-minute version is rule-generated
- Do **not** leave required fields blank to skip them — leave them empty, the validator will fail
- Do **not** list commit titles only — label who asked for it, why, and how to revert
