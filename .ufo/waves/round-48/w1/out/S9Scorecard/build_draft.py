#!/usr/bin/env python3
"""build_draft.py - assemble the S9Scorecard round-48 SCORECARD.md draft.

Reads the lane clone's SCORECARD.md (content of build commit 380bcdff), applies
the round-48 head re-anchors and appends the round-48 section, writing the
result over the clone's SCORECARD.md for the verification commit.  Every
replacement asserts its exact match count, so a drifted base fails loudly.

Usage: build_draft.py <lane-clone-dir> <section-file> <r47-banner-file>
"""
import sys

clone, section_file, banner_file = sys.argv[1], sys.argv[2], sys.argv[3]
path = f"{clone}/SCORECARD.md"
text = open(path, encoding="utf-8").read()
section = open(section_file, encoding="utf-8").read()
r47_banner = open(banner_file, encoding="utf-8").read().rstrip("\n")

# ---- authored texts -------------------------------------------------------
NEW_BANNER = (
    "**Current authority (round 48):** the assigned axes are operability + calibration "
    "(`shokunin.conf` kama row; `MISSION.md:29` still says operability + freshness, an open L0 "
    "question since round 35). Latest measured round: 48. Calibration 7 is the lowest assigned "
    "axis, below operability 8, and below the saturation line, so the stagnation nudge is "
    "inactive. The `## Axes` table, §Planned, §Retired, §Saturation and §Capabilities below are "
    "re-derived from the tree by `tools/round42-selfdesc-reconcile.py` (round-42 claim C1) and "
    "kept current in rounds 43, 44, 45, 46, 47 and 48; the round-5 banner and the head sections "
    "they replace are kept verbatim under §Historical head sections, and the authority banner "
    "this line replaces is appended byte-exact under §Superseded head banners. Completed rounds "
    "are counted by the fleet's `MANIFEST.json`, not by this file."
)

ROW_APPEND_ONLY = (
    "| append-only-audit | Set the lane's contract-declared append-only self-description against "
    "its git history - the paths and patterns `registry/append-only-contract.tsv` names, each row "
    "pointing at the lane line that declares the rule and carrying a `region` cell that says which "
    "lines it grades (`exempt=<## title>`: ungraded while that section is not gutted; "
    "`only=<## prefix>`: only that section graded): list every commit that deletes >= 20 lines "
    "from one of those files with a deleted count equal to `git diff --numstat` (byte-exact, so "
    "no `--`-prefixed line is lost), report the largest share of those graded lines any commit in "
    "the event's own window holds again (a multiset maximum, so a later head re-anchor cannot "
    "lower it) and which later commit first holds all of them, and exit 1 on a partial or "
    "unrestored mass deletion, on a graded line set the tip holds less of than the event's best "
    "window commit (`regressed`), or on a declaration that does not bind (the line says "
    "append-only for that path and is not a negation) | `tools/append-only-audit.py`; "
    "`registry/append-only-contract.tsv`; `tools/round48-append-audit-v3-check.py` | 46 |"
)

ROW_LIVE_REPLAY = (
    "| live-receipt-replay | Re-acquire a `kama-llamacpp-live/v4` or `kama-llamacpp-live/v5` "
    "receipt's server release archive and model from the URLs its provenance block records (v5: "
    "the model URL pinned to a `/resolve/<40-hex>/` Hugging Face revision, and the archive and "
    "archive member hashed against the asset digest and the server binary before the server "
    "starts, `provenance.verified`), verify both sha256 values before anything is extracted or "
    "executed, re-run the lifecycle from an empty home and compare every check the original "
    "evaluated plus a stable projection of the captured surfaces (props fields, slots count and "
    "body digest, health status and body digest, models ids/owned_by, metrics status, loading "
    "envelope, teardown outcome, listener ownership), exposed as `--compare`, and refuse a "
    "receipt whose provenance is missing or unverified at record time, whose recorded digest "
    "does not match what it downloads, whose URL revision differs from the recorded commit, or "
    "whose server-archive member is unsafe | `tools/kama-live-replay.py`; "
    "`.ufo/waves/round-48/c2/live/receipt-1.json` | 47 |"
)


def replace_once(old, new, n=1):
    global text
    c = text.count(old)
    assert c == n, f"expected {n} match(es) for {old[:70]!r}, found {c}"
    text = text.replace(old, new)


# ---- head re-anchors ------------------------------------------------------
lines = text.split("\n")
assert lines[5].startswith("**Current authority (round 47):**"), "line 6 is not the round-47 banner"
lines[5] = NEW_BANNER
text = "\n".join(lines)

replace_once(
    "→ `33` (outside closures on record)",
    "→ `34` (outside closures on record)",
)
replace_once(
    "latest outside closure `corpus/lessons/round-46-verifier-spotcheck.md` (admitted; re-anchored round 47)",
    "latest outside closure `corpus/lessons/round-47-verifier-spotcheck.md` (admitted; re-anchored round 48)",
)
replace_once(
    "The live plan is `### Planned (round 48)` at the end of this file",
    "The live plan is `### Planned (round 49)` at the end of this file",
)
replace_once(
    "Mirror of the round-47 canonical capability list that §Round 47 carries",
    "Mirror of the round-48 canonical capability list that §Round 48 carries",
)
replace_once(
    "(kept current in round 47)",
    "(kept current in rounds 47 and 48)",
)
replace_once(
    "A capability entered in round 47, so the window is not exhausted either.",
    "Round 48 entered no capability (the 11 canonical rows are the round-47 set, re-worded for "
    "v3 and v5), so one round of the four that would exhaust the window has passed.",
)

# the two capability rows appear twice: the head mirror and the round-47 canonical list.
# Only the head mirror is re-derived in place; the round-47 canonical table is a dated
# record and stays byte-intact, so replace inside the `## Capabilities` section only.
cap_start = text.index("\n## Capabilities")
cap_end = text.index("\n## ", cap_start + 1)
head, rest = text[:cap_end], text[cap_end:]
for old_row, new_row in (
    ("| append-only-audit | Set the lane's contract-declared append-only self-description", ROW_APPEND_ONLY),
    ("| live-receipt-replay | Re-acquire a `kama-llamacpp-live/v4` receipt's", ROW_LIVE_REPLAY),
):
    rows = [l for l in head.split("\n") if l.startswith(old_row)]
    assert len(rows) == 1, f"head mirror row not unique/found: {old_row[:50]!r} -> {len(rows)}"
    old = rows[0]
    if old_row.startswith("| live-receipt"):
        head = head.replace(old, new_row, 1)
    else:
        # keep the head row's own first-working cell text if it differs; assert it is `| 46 |`
        assert old.rstrip().endswith("| 46 |"), old[-30:]
        head = head.replace(old, new_row, 1)
text = head + rest

# ---- round-48 canonical list (highest-numbered canon heading wins) --------
canon_old = text.index("**Capabilities — canonical list as of round 47**")
tbl_start = text.index("| Capability | What it can now do | Evidence pointer | First-working round |", canon_old)
tbl_end = text.index("\n\n", tbl_start)
old_rows = text[tbl_start:tbl_end].split("\n")
header, sep, rows = old_rows[0], old_rows[1], old_rows[2:]
assert len(rows) == 11, f"round-47 canonical table has {len(rows)} rows, expected 11"
new_rows = []
for r in rows:
    if r.startswith("| append-only-audit |"):
        new_rows.append(ROW_APPEND_ONLY)
    elif r.startswith("| live-receipt-replay |"):
        new_rows.append(ROW_LIVE_REPLAY)
    else:
        new_rows.append(r)
named = ", ".join(x.split("|")[1].strip() for x in new_rows)
canon = "\n".join([
    "**Capabilities — canonical list as of round 48**",
    "",
    f"Same four columns as the round-47 canonical list, which stays byte-intact; no row is "
    f"added or removed: `append-only-audit` is re-worded for v3 (bound regions, the binding "
    f"rule, `regressed` in the exit) and `live-receipt-replay` for v5 (record-time verified "
    f"provenance, the pinned model revision, the stable projection and `--compare`).",
    "",
    header,
    sep,
    *new_rows,
])
assert named.count(",") == 10

# ---- splice the section ---------------------------------------------------
appendix = "### Superseded head banners (kept verbatim; round 48)"
assert text.count(appendix) == 1
body = section.replace("{{CANON}}", canon).rstrip("\n")
text = text.replace(appendix, body + "\n\n" + appendix, 1)

# ---- append the superseded round-47 banner byte-exact ---------------------
text = text.rstrip("\n") + "\n\n" + r47_banner + "\n"

open(path, "w", encoding="utf-8").write(text)
print(f"wrote {path}: {len(text.splitlines())} lines")
print(f"canon names: {named}")
