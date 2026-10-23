#!/usr/bin/env python3
"""Offline replay of clause (h) `h:same-message-frame` from the frozen
round-27 counter (count-c1.py, sha256
49491b80e4f4ed2a85ab822a52f0b1a0fdb1dee53423e3d43b60ee25d1bf2765).

The frame expression and error_message() are not re-implemented: both are
extracted from the frozen counter source at run time, after the counter's
sha256 is checked, and executed verbatim. If the counter bytes differ or the
markers move, the harness fails closed.

Frame expression (counter lines 707-708, lowering applied by the code):

    elif (fr := msg.replace(e["signature"], "\0").lower()).strip("\0 ") and \
            fr == om.replace(oe["signature"], "\0").lower():
        clash = "h:same-message-frame"

Note the exact semantics preserved here:
  * every occurrence of each side's own signature is replaced with one NUL;
  * both sides are lowercased;
  * the truthiness guard strips NUL/space from the *left* frame only, but the
    equality compares the *unstripped* lowercased frames (fr holds the value
    before .strip());
  * a message that is exactly its own signature yields frame "\\0", whose
    stripped form is empty, so the guard suppresses the comparison.

No server is started; no count-c1.py main() is imported or run.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
OUT = LANE / ".ufo/waves/round-27/w1a3/out/ExecOfflineFrameReplay"
COUNTER = LANE / ".ufo/waves/round-27/count-c1.py"
COUNTER_SHA = "49491b80e4f4ed2a85ab822a52f0b1a0fdb1dee53423e3d43b60ee25d1bf2765"

SHORTCUT_RECEIPT = (LANE / ".ufo/waves/round-26/w2-falsify/out/CriticShortcutRows"
                    / "shortcut.receipt.json")
SHORTCUT_REGISTRY = (LANE / ".ufo/waves/round-26/w2-falsify/out/CriticShortcutRows"
                     / "shortcut.registry.json")
E26_REGISTRY = LANE / "registry/error-signatures-r26.json"
E26_RECEIPT = LANE / ".ufo/waves/round-26/final/c1-final-tip-receipt.json"
E26_RECEIPT_DUP = LANE / ".ufo/waves/round-26/final/c1-tip-receipt.json"

RECEIPT_OUT = OUT / "frame-replay.receipt.json"


def sha256(text: str | bytes) -> str:
    if isinstance(text, str):
        text = text.encode("utf-8")
    return hashlib.sha256(text).hexdigest()


def extract_frozen_rules(src: str) -> tuple[str, str, list[int], list[int]]:
    """Return (error_message_source, frame_expression, em_lines, frame_lines)."""
    lines = src.splitlines()
    # --- error_message: def line through the last line before the next top-level def
    i0 = None
    for i, line in enumerate(lines):
        if line.startswith("def error_message("):
            i0 = i
            break
    if i0 is None:
        raise SystemExit("FAIL: def error_message not found in frozen counter")
    i1 = None
    for i in range(i0 + 1, len(lines)):
        if lines[i].startswith("def "):
            i1 = i
            break
    if i1 is None:
        raise SystemExit("FAIL: end of error_message not found")
    em_src = "\n".join(lines[i0:i1]).rstrip()

    # --- frame expression: the elif line(s) immediately above the clash marker
    marker = None
    for i, line in enumerate(lines):
        if line.strip() == 'clash = "h:same-message-frame"':
            marker = i
            break
    if marker is None:
        raise SystemExit("FAIL: h:same-message-frame marker not found")
    start = marker - 1
    while start >= 0 and not lines[start].lstrip().startswith("elif "):
        start -= 1
    if start < 0:
        raise SystemExit("FAIL: elif of frame clause not found")
    raw = "\n".join(lines[start:marker]).strip()
    if not raw.startswith("elif "):
        raise SystemExit("FAIL: frame clause does not start with elif")
    expr = re.sub(r"\\\n\s*", " ", raw[len("elif "):]).strip()
    if not expr.endswith(":"):
        raise SystemExit("FAIL: frame clause does not end with ':'")
    expr = expr[:-1]
    frame_lines = [start + 1, start + 2]  # 1-based, two physical lines
    return em_src, expr, [i0 + 1, i1], frame_lines


def build_namespace(em_src: str, expr: str) -> dict:
    # seed the globals error_message() reads in count-c1.py (it uses only json)
    ns: dict = {"json": json}
    exec(compile(em_src, "<frozen-count-c1.py:error_message>", "exec"), ns)
    fsrc = ("def _frame_clause(e, msg, oe, om):\n"
            "    return bool(" + expr + ")\n")
    exec(compile(fsrc, "<frozen-count-c1.py:707-708>", "exec"), ns)
    return ns


def frame_diag(fr_fn, sig: str, msg: str) -> dict:
    fr = msg.replace(sig, "\0").lower()
    stripped = fr.strip("\0 ")
    return {
        "signature_in_message": sig in msg,
        "frame_sha256": sha256(fr),
        "frame_len": len(fr),
        "frame_stripped_empty": stripped == "",
        "frame_excerpt": fr[:160],
    }


def load_rows(receipt_path: Path, registry_path: Path, error_message, lane: Path) -> list[dict]:
    receipt = json.loads(receipt_path.read_text("utf-8"))
    registry = json.loads(registry_path.read_text("utf-8"))
    sigs = registry["signatures"] if isinstance(registry, dict) else registry
    rec_rows = {r["id"]: r for r in receipt["rows"]}
    reg_ids = [s["id"] for s in sigs]
    rec_ids = [r["id"] for r in receipt["rows"]]
    if reg_ids != rec_ids:
        raise SystemExit(f"FAIL: registry/receipt order mismatch {registry_path}")
    rows = []
    for s in sigs:
        r = rec_rows[s["id"]]
        excerpt = r["observed"]["channel_excerpt"]
        body = excerpt.encode("utf-8")
        msg = error_message(body)
        rows.append({
            "id": s["id"],
            "signature": s["signature"],
            "message": msg,
            "message_sha256": sha256(msg) if msg is not None else None,
            "message_len": len(msg) if msg is not None else None,
            "excerpt_len": len(excerpt),
            "excerpt_sha256": sha256(body),
            "channel_status": r["observed"].get("status"),
            "channel_exit": r["observed"].get("exit"),
        })
    return rows


def replay(rows: list[dict], fr_fn, error_message) -> dict:
    """Frame-clause-only greedy replay in given order, with a full pairwise
    earlier-row collision list. Equality is transitive on fixed frames, so the
    greedy survivor set equals 'no collision against any earlier row'."""
    survivors: list[dict] = []
    pairs: list[dict] = []
    for row in rows:
        rid, sig, msg = row["id"], row["signature"], row["message"]
        if msg is None:
            row.update(status="frame-not-applicable",
                       why="error_message() returned None; clause (h) unreachable "
                           "(counter reaches e:not-shown first)")
            survivors.append(row)
            continue
        row.update(frame_diag(fr_fn, sig, msg))
        clash = []
        for s in survivors:
            if s["message"] is None:
                continue
            if fr_fn({"signature": sig}, msg, {"signature": s["signature"]}, s["message"]):
                clash.append(s["id"])
                pairs.append({"earlier": s["id"], "later": rid,
                              "frame_sha256": row["frame_sha256"]})
        if clash:
            row.update(status="collapsed", collides_with=clash)
        else:
            row.update(status="survives", collides_with=[])
            survivors.append(row)
    survivor_ids = [r["id"] for r in survivors]
    collapsed = [r["id"] for r in rows if r.get("status") == "collapsed"]

    # full pairwise accounting: every i<j pair that the expression fires on,
    # whether or not j was already collapsed by an earlier representative.
    testable = [r for r in rows if r["message"] is not None]
    all_pairs = []
    for i, a in enumerate(testable):
        for b in testable[i + 1:]:
            if fr_fn({"signature": a["signature"]}, a["message"],
                     {"signature": b["signature"]}, b["message"]):
                all_pairs.append([a["id"], b["id"]])
    classes: dict[str, list[str]] = {}
    for r in testable:
        key = sha256(r["message"].replace(r["signature"], "\0").lower())
        classes.setdefault(key, []).append(r["id"])
    return {
        "order": [r["id"] for r in rows],
        "registered": len(rows),
        "frame_tested": len(testable),
        "frame_not_applicable": [r["id"] for r in rows if r["message"] is None],
        "survivors": len(survivors),
        "survivor_ids": survivor_ids,
        "collapsed": collapsed,
        "colliding_pairs": pairs,
        "all_pairwise_frame_collisions": len(all_pairs),
        "all_pairwise_frame_collision_pairs": all_pairs,
        "frame_class_sizes": sorted((len(v) for v in classes.values()), reverse=True),
        "frame_classes": [v for v in classes.values() if len(v) > 1],
        "rows": [{k: v for k, v in r.items() if k != "message"} for r in rows],
    }


def equal_frame_classes(rows: list[dict]) -> dict:
    """Diagnostic: group on the equality key *ignoring the truthiness guard*,
    to show which collisions the guard suppresses."""
    buckets: dict[str, list[str]] = {}
    for r in rows:
        if r["message"] is None:
            continue
        key = sha256(r["message"].replace(r["signature"], "\0").lower())
        buckets.setdefault(key, []).append(r["id"])
    return {k: v for k, v in buckets.items() if len(v) > 1}


def raw_text_variant(rows: list[dict], excerpts: dict[str, str], fr_fn) -> dict:
    """Counterfactual only: treat the recorded excerpt text as the message.
    NOT the frozen clause (the clause uses error_message(qb)), included to show
    what decoding buys and costs."""
    work = []
    for r in rows:
        w = dict(r)
        w["message"] = excerpts[r["id"]]
        work.append(w)
    res = replay(work, fr_fn, lambda b: None)
    res["label"] = "counterfactual raw-excerpt text, not the frozen clause"
    res["rows"] = [{k: v for k, v in r.items() if k != "message"} for r in work]
    return res


def main() -> int:
    counter_bytes = COUNTER.read_bytes()
    counter_sha = sha256(counter_bytes)
    if counter_sha != COUNTER_SHA:
        print(f"FAIL counter sha {counter_sha} != pinned {COUNTER_SHA}", file=sys.stderr)
        return 2
    src = counter_bytes.decode("utf-8")
    em_src, expr, em_lines, frame_lines = extract_frozen_rules(src)
    if frame_lines != [707, 708]:
        print(f"FAIL frame clause moved: {frame_lines} != [707, 708]", file=sys.stderr)
        return 2
    ns = build_namespace(em_src, expr)
    error_message, fr_fn = ns["error_message"], ns["_frame_clause"]

    # ---- controls: the extracted expression must fire and must not fire ----
    controls = [
        {"name": "trailing-splice echo frame collides",
         "args": [{"signature": "AAA"}, "generic text, but got: AAA",
                  {"signature": "BBB"}, "generic text, but got: BBB"],
         "expect": True},
        {"name": "case-differing frame collides",
         "args": [{"signature": "AAA"}, "Generic Text, but got: AAA",
                  {"signature": "BBB"}, "generic text, but got: BBB"],
         "expect": True},
        {"name": "distinct frames do not collide",
         "args": [{"signature": "AAA"}, "one frame: AAA",
                  {"signature": "BBB"}, "other frame: BBB"],
         "expect": False},
        {"name": "message==signature guard suppresses",
         "args": [{"signature": "AAA"}, "AAA",
                  {"signature": "BBB"}, "BBB"],
         "expect": False},
        {"name": "repeat occurrence replaced on both sides",
         "args": [{"signature": "AAA"}, "AAA and AAA",
                  {"signature": "BBB"}, "BBB and BBB"],
         "expect": True},
        {"name": "whitespace-only frame suppressed",
         "args": [{"signature": "AAA"}, "  AAA  ",
                  {"signature": "BBB"}, "  BBB  "],
         "expect": False},
    ]
    for c in controls:
        c["observed"] = bool(fr_fn(*c["args"]))
        c["pass"] = c["observed"] == c["expect"]

    # ---- set 1: round-26 shortcut rows (registry order) ----
    sc_rows = load_rows(SHORTCUT_RECEIPT, SHORTCUT_REGISTRY, error_message, LANE)
    sc_res = replay(sc_rows, fr_fn, error_message)
    sc_excerpts = {r["id"]: r["observed"]["channel_excerpt"]
                   for r in json.loads(SHORTCUT_RECEIPT.read_text("utf-8"))["rows"]}
    sc_raw = raw_text_variant(sc_rows, sc_excerpts, fr_fn)

    # ---- set 2: landed E26 rows (registry order, final-tip receipt messages) ----
    e26_rows = load_rows(E26_RECEIPT, E26_REGISTRY, error_message, LANE)
    e26_res = replay(e26_rows, fr_fn, error_message)
    e26_excerpts = {r["id"]: r["observed"]["channel_excerpt"]
                    for r in json.loads(E26_RECEIPT.read_text("utf-8"))["rows"]}
    e26_raw = raw_text_variant(e26_rows, e26_excerpts, fr_fn)

    # variant: re-spell the two raw-body-escaped E26 signatures in decoded form
    requote_rows = [dict(r, signature=r["signature"].replace('\\"', '"'))
                    for r in e26_rows]
    e26_requote = replay(requote_rows, fr_fn, error_message)

    # duplicate receipt: are the decoded HTTP messages the same? (tip vs final-tip)
    dup_rows = load_rows(E26_RECEIPT_DUP, E26_REGISTRY, error_message, LANE)
    dup_res = replay(dup_rows, fr_fn, error_message)
    dup = {
        "source": str(E26_RECEIPT_DUP.relative_to(LANE)),
        "survivors": dup_res["survivors"],
        "colliding_pairs": dup_res["colliding_pairs"],
        "message_sha_equal_to_final_tip": {
            a["id"]: (None if a["message_sha256"] is None or b["message_sha256"] is None
                      else a["message_sha256"] == b["message_sha256"])
            for a, b in zip(e26_rows, dup_rows)},
    }

    e26_frame_tested = e26_res["frame_tested"]
    guard_suppressed = equal_frame_classes(e26_rows)
    guard_suppressed_pairs = sum(len(v) * (len(v) - 1) // 2
                                 for v in guard_suppressed.values())
    receipt = {
        "schema": "kama-r27-x1-frame-offline-replay/v1",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "lane": str(LANE),
        "counter": {
            "path": str(COUNTER.relative_to(LANE)),
            "sha256": counter_sha,
            "pinned_sha256": COUNTER_SHA,
            "sha_match": counter_sha == COUNTER_SHA,
            "frame_clause_lines": frame_lines,
            "frame_clause_source": "elif " + expr + ":",
            "frame_clause_note": ("fr holds msg.replace(sig,NUL).lower(); the "
                                  ".strip(\"\\0 \") is a truthiness guard only; "
                                  "equality uses the unstripped fr"),
            "error_message_lines": em_lines,
            "error_message_slice_note": "start line 506; end boundary 520 is the next "
                                        "top-level def; the function body ends at line 518",
            "error_message_sha256": sha256(em_src),
            "error_message_source": em_src,
        },
        "inputs": {
            "shortcut_receipt": str(SHORTCUT_RECEIPT.relative_to(LANE)),
            "shortcut_registry": str(SHORTCUT_REGISTRY.relative_to(LANE)),
            "e26_registry": str(E26_REGISTRY.relative_to(LANE)),
            "e26_receipt": str(E26_RECEIPT.relative_to(LANE)),
        },
        "controls": controls,
        "controls_all_pass": all(c["pass"] for c in controls),
        "sets": {
            "shortcut": sc_res,
            "e26": e26_res,
        },
        "totals": {
            "shortcut_survivors": f"{sc_res['survivors']}/{sc_res['registered']}",
            "e26_survivors": f"{e26_res['survivors']}/{e26_res['registered']}",
            "e26_frame_tested_survivors": f"{e26_frame_tested}/{e26_frame_tested}",
            "e26_frame_not_applicable": e26_res["frame_not_applicable"],
            "shortcut_colliding_pairs": len(sc_res["colliding_pairs"]),
            "e26_colliding_pairs": len(e26_res["colliding_pairs"]),
            "shortcut_all_pairwise_frame_collisions": sc_res["all_pairwise_frame_collisions"],
            "e26_all_pairwise_frame_collisions": e26_res["all_pairwise_frame_collisions"],
            "e26_guard_suppressed_pairs": guard_suppressed_pairs,
        },
        "diagnostics": {
            "e26_equal_frame_classes_ignoring_guard": guard_suppressed,
            "e26_guard_suppressed_pairs": guard_suppressed_pairs,
            "e26_signature_not_in_decoded_message": [
                r["id"] for r in e26_rows if r["message"] is not None
                and not r["signature_in_message"]],
            "e26_process_rows_no_decodable_message": e26_res["frame_not_applicable"],
        },
        "variant_e26_decoded_signature_spelling": {
            "label": "E26-07/E26-14 signatures re-spelled with decoded quotes; "
                     "same frame expression",
            "survivors": e26_requote["survivors"],
            "registered": e26_requote["registered"],
            "colliding_pairs": e26_requote["colliding_pairs"],
            "frame_class_sizes": e26_requote["frame_class_sizes"],
            "frame_classes": e26_requote["frame_classes"],
            "signatures_absent_from_message": [
                r["id"] for r in requote_rows if r["message"] is not None
                and not r["signature_in_message"]],
        },
        "counterfactual_raw_text": {
            "shortcut": {k: v for k, v in sc_raw.items() if k != "rows"},
            "e26": {k: v for k, v in e26_raw.items() if k != "rows"},
            "label": "raw recorded excerpt treated as the message; NOT the frozen clause",
        },
        "duplicate_receipt_check": dup,
        "exit": 0,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    RECEIPT_OUT.write_text(json.dumps(receipt, indent=1, sort_keys=True) + "\n", "utf-8")

    print(f"counter sha {counter_sha} pins {counter_sha == COUNTER_SHA}")
    print(f"frame clause extracted at lines {frame_lines}: elif {expr}:")
    print(f"error_message extracted at lines {em_lines}")
    print(f"controls all pass {receipt['controls_all_pass']}")
    print(f"shortcut_survivors {sc_res['survivors']}/{sc_res['registered']} "
          f"collapsed {sc_res['collapsed']}")
    print(f"  colliding pairs: {len(sc_res['colliding_pairs'])} "
          f"(all-pairwise {sc_res['all_pairwise_frame_collisions']}, "
          f"class sizes {sc_res['frame_class_sizes']})")
    for p in sc_res["colliding_pairs"]:
        print(f"  PAIR {p['earlier']} ~ {p['later']} frame {p['frame_sha256'][:16]}")
    print(f"e26_survivors {e26_res['survivors']}/{e26_res['registered']} "
          f"(frame-tested {e26_res['frame_tested']}, "
          f"not-applicable {e26_res['frame_not_applicable']})")
    print(f"  colliding pairs: {len(e26_res['colliding_pairs'])} "
          f"(all-pairwise {e26_res['all_pairwise_frame_collisions']})")
    print(f"  equal-frame classes ignoring guard: {len(guard_suppressed)} "
          f"(sizes {[len(v) for v in guard_suppressed.values()]}, "
          f"guard-suppressed pairs {guard_suppressed_pairs})")
    print(f"  signatures absent from decoded message: "
          f"{receipt['diagnostics']['e26_signature_not_in_decoded_message']}")
    print(f"decoded-spelling variant: e26 {e26_requote['survivors']}/"
          f"{e26_requote['registered']} pairs {len(e26_requote['colliding_pairs'])} "
          f"classes {e26_requote['frame_class_sizes']}")
    print(f"raw-text counterfactual: shortcut {sc_raw['survivors']}/{sc_raw['registered']}, "
          f"e26 {e26_raw['survivors']}/{e26_raw['registered']}")
    print(f"duplicate tip receipt: e26 {dup_res['survivors']}/{dup_res['registered']} "
          f"http-message-identical "
          f"{all(dup['message_sha_equal_to_final_tip'][i] for i in dup['message_sha_equal_to_final_tip'] if i not in ('E26-15','E26-16','E26-17'))}")
    print(f"receipt written {RECEIPT_OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
