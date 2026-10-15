#!/usr/bin/env python3
"""本地刷题燃油闸门：进度门槛 + 下单确认哈希。不接触 MCP Token。"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def state_dir(demo: bool) -> Path:
    d = ROOT / ".grind" / ("demo" if demo else "live")
    d.mkdir(parents=True, exist_ok=True)
    return d


def load_state(demo: bool) -> dict:
    p = state_dir(demo) / "state.json"
    if not p.exists():
        return {"threshold": int(os.environ.get("GRIND_THRESHOLD", "3")), "logs": []}
    return json.loads(p.read_text(encoding="utf-8"))


def save_state(demo: bool, state: dict) -> None:
    p = state_dir(demo) / "state.json"
    p.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def done_count(state: dict) -> int:
    return len(state.get("logs", []))


def is_unlocked(state: dict) -> bool:
    return done_count(state) >= int(state.get("threshold", 3))


def cmd_status(demo: bool) -> int:
    st = load_state(demo)
    n, th = done_count(st), int(st.get("threshold", 3))
    flag = "UNLOCKED" if n >= th else "LOCKED"
    print(f"{flag}  progress={n}/{th}  demo={demo}")
    for i, row in enumerate(st.get("logs", []), 1):
        print(f"  {i}. {row.get('ts','')}  {row.get('title','')}")
    return 0


def cmd_log(demo: bool, title: str) -> int:
    st = load_state(demo)
    st.setdefault("logs", []).append(
        {"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "title": title or "untitled"}
    )
    save_state(demo, st)
    return cmd_status(demo)


def cmd_reset(demo: bool) -> int:
    th = int(os.environ.get("GRIND_THRESHOLD", "3"))
    save_state(demo, {"threshold": th, "logs": []})
    print(f"RESET  progress=0/{th}  demo={demo}")
    return 0


def cmd_set_threshold(demo: bool, n: int) -> int:
    st = load_state(demo)
    st["threshold"] = max(1, n)
    save_state(demo, st)
    return cmd_status(demo)


def canonical_payload(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def confirm_hash(payload: dict) -> str:
    raw = canonical_payload(payload).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:12]


def cmd_preview(demo: bool, payload_raw: str) -> int:
    st = load_state(demo)
    if not is_unlocked(st):
        print("DENIED  reason=grind-locked  run: log more solves first", file=sys.stderr)
        return 2
    payload = json.loads(payload_raw)
    h = confirm_hash(payload)
    preview_path = state_dir(demo) / "last_preview.json"
    preview_path.write_text(
        json.dumps({"confirm": h, "payload": payload}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print("PREVIEW_OK")
    print(f"confirm={h}")
    print("summary=")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print("告诉用户以上摘要；仅当用户明确确认后，用同一 payload + confirm 调用 confirm 子命令，再 create-order。")
    return 0


def cmd_confirm(demo: bool, payload_raw: str, confirm: str) -> int:
    st = load_state(demo)
    if not is_unlocked(st):
        print("DENIED  reason=grind-locked", file=sys.stderr)
        return 2
    payload = json.loads(payload_raw)
    expect = confirm_hash(payload)
    if confirm != expect:
        print(f"DENIED  reason=confirm-mismatch  expect={expect}  got={confirm}", file=sys.stderr)
        return 3
    preview_path = state_dir(demo) / "last_preview.json"
    if preview_path.exists():
        prev = json.loads(preview_path.read_text(encoding="utf-8"))
        if prev.get("confirm") != confirm or canonical_payload(prev.get("payload", {})) != canonical_payload(payload):
            print("DENIED  reason=preview-stale-or-tampered", file=sys.stderr)
            return 4
    print("CONFIRM_OK  allowed_to_call_create_order=1")
    print(f"confirm={confirm}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="mcd-grind-reward local gate")
    ap.add_argument("--demo", action="store_true", help="use demo state dir")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status")
    p_log = sub.add_parser("log")
    p_log.add_argument("--title", default="solve")
    sub.add_parser("reset")
    p_th = sub.add_parser("threshold")
    p_th.add_argument("n", type=int)
    p_prev = sub.add_parser("preview")
    p_prev.add_argument("--payload", required=True)
    p_conf = sub.add_parser("confirm")
    p_conf.add_argument("--payload", required=True)
    p_conf.add_argument("--confirm", required=True)

    args = ap.parse_args()
    demo = bool(args.demo)

    if args.cmd == "status":
        return cmd_status(demo)
    if args.cmd == "log":
        return cmd_log(demo, args.title)
    if args.cmd == "reset":
        return cmd_reset(demo)
    if args.cmd == "threshold":
        return cmd_set_threshold(demo, args.n)
    if args.cmd == "preview":
        return cmd_preview(demo, args.payload)
    if args.cmd == "confirm":
        return cmd_confirm(demo, args.payload, args.confirm)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
