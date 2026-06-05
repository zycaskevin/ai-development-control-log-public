#!/usr/bin/env python3
"""Collect Actor & Provenance metadata for Section 0.5 of a v0.3.1
Control Log.

This script autofills the agent-side rows of the 0.5 table:

    | Agent model       | <from HERMES_AGENT_MODEL or "unknown">       |
    | Agent session     | <from HERMES_AGENT_SESSION or wall-clock>     |
    | Human approver    |   (left blank for the human reviewer)         |
    | Approval evidence |   (left blank for the human reviewer)         |
    | Wall clock start  | <ISO-8601>                                    |
    | Wall clock end    | <ISO-8601>                                    |

The human-side rows (`Human approver`, `Approval evidence`) are
intentionally NOT filled: those must come from a human, not the
agent. The script's output marks them with `<FILL BY HAND>` so
a reader can find them quickly.

Why this lives in a script and not in the template alone:
the wall-clock end has to be `now()` at the moment the agent
finishes the task, not when the human opens the file. Letting
the template example show a static time would create a habit
of copy-pasting a stale value. The script makes the wall
clock authoritative.

The script also produces a JSON variant (`--json`) for use
by other automation (notably scripts/validate.py will need
the same source-of-truth for its gate).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

DEFAULT_LANG = "en"  # one of "en", "zh-TW"

# ---------------------------------------------------------------------------
# Field labels in both languages. Keeping them in one place lets us
# avoid drift between the rendered markdown and the validate.py gate.
# ---------------------------------------------------------------------------

LABELS = {
    "en": {
        "section_title": "## 0.5 Actor & Provenance (v0.3.1 — autofilled)",
        "agent_model": "Agent model",
        "agent_session": "Agent session",
        "human_approver": "Human approver",
        "approval_evidence": "Approval evidence",
        "wall_clock_start": "Wall clock start",
        "wall_clock_end": "Wall clock end",
        "fill_by_hand": "<FILL BY HAND>",
    },
    "zh-TW": {
        "section_title": "## 0.5 Actor & Provenance（v0.3.1 — 自動填）",
        "agent_model": "Agent model",
        "agent_session": "Agent session",
        "human_approver": "Human approver",
        "approval_evidence": "Approval evidence",
        "wall_clock_start": "Wall clock start",
        "wall_clock_end": "Wall clock end",
        "fill_by_hand": "<由人類填寫>",
    },
}


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def derive_session_id() -> str:
    """A short, sortable session identifier.

    Combines wall-clock second + a small tag from HERMES_TASK_ID
    if set. This is intentionally not crypto-strong — it is a
    pointer that helps a human reviewer correlate the log with
    the agent's transcript / CI run.
    """
    task_id = os.environ.get("HERMES_TASK_ID", "").strip()
    suffix = f"-{task_id[:8]}" if task_id else ""
    return now_iso() + suffix


def collect() -> dict:
    return {
        "agent_model": os.environ.get("HERMES_AGENT_MODEL", "").strip() or "unknown",
        "agent_session": os.environ.get("HERMES_AGENT_SESSION", "").strip() or derive_session_id(),
        "human_approver": "",  # intentionally blank
        "approval_evidence": "",  # intentionally blank
        "wall_clock_start": now_iso(),
        "wall_clock_end": now_iso(),
    }


def render_markdown(data: dict, lang: str = DEFAULT_LANG) -> str:
    L = LABELS[lang]
    fill = L["fill_by_hand"]
    lines = [
        L["section_title"],
        "",
        f"| {L['agent_model']}       | {data['agent_model']} |",
        f"| {L['agent_session']}     | {data['agent_session']} |",
        f"| {L['human_approver']}    | {fill} |",
        f"| {L['approval_evidence']} | {fill} |",
        f"| {L['wall_clock_start']}  | {data['wall_clock_start']} |",
        f"| {L['wall_clock_end']}    | {data['wall_clock_end']} |",
    ]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lang", choices=["en", "zh-TW"], default=DEFAULT_LANG,
                        help="Render language (default: en)")
    parser.add_argument("--json", action="store_true",
                        help="Emit JSON instead of markdown.")
    parser.add_argument("--out", type=Path, default=None,
                        help="Write to file instead of stdout.")
    args = parser.parse_args(argv)

    data = collect()
    if args.json:
        out = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    else:
        out = render_markdown(data, args.lang)

    if args.out:
        args.out.write_text(out, encoding="utf-8")
    else:
        sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
