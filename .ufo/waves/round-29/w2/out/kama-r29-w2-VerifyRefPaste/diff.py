#!/usr/bin/env python3
"""VerifyRefPaste: mechanically diff SCORECARD.md correction rows (tip 513eba3b)
against the frozen counter's per-statement observed values (receipt.json)."""
import json

T = "/tmp/kama-r29-w2-VerifyRefPaste"
HEADING = "## Round 29 — self-assessment corrections"

def parse_rows(path):
    """Independent parse: rows under HEADING whose first cell starts with SA29:.
    Returns (sid_after_prefix, last_cell_stripped_of_backticks, n_cols, raw_line)."""
    out, on = [], False
    for raw in open(path, encoding="utf-8").read().split("\n"):
        if raw.startswith("## "):
            on = raw.strip() == HEADING
            continue
        if on and raw.startswith("|"):
            cols = [c.strip() for c in raw.strip().strip("|").split("|")]
            first = cols[0].strip("`")
            if first.startswith("SA29:"):
                out.append((first[5:], cols[-1].strip("`"), len(cols), raw))
    return out

receipt = json.load(open(f"{T}/receipt.json"))
obs = {s["sid"]: s["observed"] for s in receipt["all_statements"]}
holds = {s["sid"]: s["holds"] for s in receipt["all_statements"]}
mism = {m["sid"]: m["observed"] for m in receipt["mismatches"]}

tip = open(f"{T}/SCORECARD-tip.md", "rb").read()
base = open(f"{T}/SCORECARD-base.md", "rb").read()
append_only = tip.startswith(base)
appended = tip[len(base):].decode("utf-8", "replace")

rows = parse_rows(f"{T}/SCORECARD-tip.md")
row_sids = [r[0] for r in rows]
dupes = sorted({s for s in row_sids if row_sids.count(s) > 1})

results, n_match = [], 0
for sid, cell, ncols, raw in rows:
    o = obs.get(sid)
    ok = (o is not None) and (cell == o)
    in_mism = sid in mism
    n_match += ok
    results.append({"sid": sid, "row_cell": cell, "counter_observed": o,
                    "exact_match": ok, "in_mismatch_set": in_mism,
                    "cell_eq_mismatch_obs": in_mism and cell == mism[sid],
                    "n_cols": ncols, "raw": raw})

verdict = {
    "tip": receipt.get("tip"),
    "counter_sha256": receipt.get("counter_sha256"),
    "base": receipt.get("base"),
    "summary_stdout_expected": (
        f"statements {receipt['statements']} mismatched_at_base {receipt['mismatched_at_base']} "
        f"append_only {receipt['append_only']} valid_corrections {receipt['valid_corrections']} "
        f"false_corrections {len(receipt['false_corrections'])} unresolved {receipt['unresolved']} "
        f"met {receipt['met']}"),
    "statements": receipt["statements"],
    "by_class": receipt.get("by_class"),
    "mismatched_at_base": receipt["mismatched_at_base"],
    "correction_rows_found": len(rows),
    "duplicate_sids": dupes,
    "rows_exactly_match_counter": n_match,
    "rows_not_matching": [r["sid"] for r in results if not r["exact_match"]],
    "row_sids_seteq_mismatch_set": sorted(row_sids) == sorted(mism),
    "row_sids_not_in_mismatches": sorted(set(row_sids) - set(mism)),
    "mismatch_sids_without_row": sorted(set(mism) - set(row_sids)),
    "append_only_independent": append_only,
    "appended_bytes_preview": appended[:2000],
    "receipt_summary_fields": {k: receipt[k] for k in
        ("statements", "mismatched_at_base", "append_only", "correction_rows",
         "valid_corrections", "false_corrections", "unresolved", "met")},
}
print(json.dumps(verdict, indent=1, ensure_ascii=False))
print("\n--- per-row ---")
for r in results:
    print(json.dumps(r, indent=1, ensure_ascii=False))
