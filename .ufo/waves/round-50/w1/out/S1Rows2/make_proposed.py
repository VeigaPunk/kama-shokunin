#!/usr/bin/env python3
"""Build the proposed S496/S497/S498 rows and check parse-level properties.

Writes $S/proposed-A.md (S498 entity form) and $S/proposed-B.md (S498 tick-free
sentences) from the clone's registry at HEAD, then reports per-row cell counts,
raw backtick parity (the sources-append-only split_cells toggle) and quote checks.
"""
import html
import pathlib
import re
import sys

S = pathlib.Path("/fast/scratch/hyaku/kama-r50/S1Rows2")
SRC = S / "lane/corpus/SOURCES.md"
COPY = pathlib.Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50")
PDE = re.sub(r"\s+", " ", (COPY / "c1/PR_SET_PDEATHSIG.2const.txt").read_text()).strip()
MAPS = re.sub(r"\s+", " ", (COPY / "c1/proc_pid_maps.5.txt").read_text()).strip()
CM = re.sub(r"\s+", " ", (COPY / "c2/commonmark-0.31.2-s4.5.txt").read_text()).strip()

SHA_MAPS = "e7cdf0ff1c8d8d87e5c92e529a09270945ca3b7cafb8e823a7ca3d294f3c16a2"
SHA_PDE = "906bbe5cc7e38c02a82bb60ff3b7e0d1cfb21089a1a24f00f045fb1b86edb1e4"
SHA_CM = "c85f56cc2101f761cc94215c677cd2c7c1ecca9c47be016479fdfe718af60f0d"

ROW496 = (
    "| S496 | Linux proc_pid_maps(5) — https://man7.org/linux/man-pages/man5/proc_pid_maps.5.html "
    "| docs | A | what `/proc/<pid>/maps` lines report: per-mapping `dev` (major:minor), `inode` and "
    "`pathname` of the backing file, and that an inode of 0 means a memory region has no file; Linux "
    "only; not other platforms, not a permission model | §DESCRIPTION, paragraphs on "
    "offset/dev/inode/pathname; man-pages 6.19, page dated 2026-02-08 (text copy "
    "`.ufo/waves/round-50/c1/proc_pid_maps.5.txt`, sha256 `" + SHA_MAPS + "`) | "
    "\"dev is the device (major:minor); inode is the inode on that device\" and \"The pathname field "
    "will usually be the file that is backing the mapping.\" — so the live tool can read which file a "
    "running server maps, then hash that same file through its pathname | mined | 2026-10-27 | "
    "on-release | corpus/knowledge/llamacpp-loading-lifecycle.md, tools/kama-llamacpp-live.py, "
    "corpus/lessons/round-50.md |"
)

ROW497 = (
    "| S497 | Linux PR_SET_PDEATHSIG(2const) — https://man7.org/linux/man-pages/man2/PR_SET_PDEATHSIG.2const.html "
    "| docs | A | what a parent-death signal is and when it fires: on termination of the parent thread, "
    "on each subreaper reparenting after it, and when the parent is already gone at prctl time; it is "
    "cleared for a fork(2) child and is process-directed | §DESCRIPTION; man-pages 6.19, page dated "
    "2026-02-08 (text copy `.ufo/waves/round-50/c1/PR_SET_PDEATHSIG.2const.txt`, sha256 `" + SHA_PDE + "`) | "
    "\"The parent-death signal is sent upon subsequent termination of the parent thread and also upon "
    "termination of each subreaper process\" and \"The parent-death signal setting is cleared for the "
    "child of a fork(2).\" — so a replay and its live child can make the whole tree die when the process "
    "that started them dies, but only because each link sets its own signal: the kernel clears the "
    "setting across fork(2) | mined | 2026-10-27 | on-release | "
    "corpus/knowledge/llamacpp-loading-lifecycle.md, tools/kama-live-replay.py, "
    "tools/kama-llamacpp-live.py, corpus/lessons/round-50.md |"
)

SCOPE498 = (
    "what opens and closes a fenced code block: at least three backticks or tildes (not mixed), up to "
    "three spaces of indentation, a backtick fence whose info string holds no backtick, a closing fence "
    "of the same character with at least as many of them; an unclosed fence runs to the end of the "
    "containing block; the content is literal text"
)
ANCHOR498 = (
    "§4.5 Fenced code blocks (text copy `.ufo/waves/round-50/c2/commonmark-0.31.2-s4.5.txt`; full page "
    "sha256 `" + SHA_CM + "`)"
)

ROW498_A = (
    "| S498 | CommonMark spec 0.31.2 §4.5, Fenced code blocks — https://spec.commonmark.org/0.31.2/#fenced-code-blocks "
    "| spec | A | " + SCOPE498 + " | " + ANCHOR498 + " | "
    "\"A code fence is a sequence of at least three consecutive backtick characters (&#96;) or tildes (~).\" "
    "and \"The content of a code fence is treated as literal text, not parsed as inlines.\" — so a section "
    "scanner must not treat a `## ` line inside a fence as a heading | mined | 2026-10-27 | 360d | "
    "corpus/lessons/round-50.md, tools/append-only-audit.py |"
)

ROW498_B = (
    "| S498 | CommonMark spec 0.31.2 §4.5, Fenced code blocks — https://spec.commonmark.org/0.31.2/#fenced-code-blocks "
    "| spec | A | " + SCOPE498 + " | " + ANCHOR498 + " | "
    "\"A fenced code block begins with a code fence, preceded by up to three spaces of indentation.\" and "
    "\"The closing code fence must use the same character as the opening fence:\" and \"The content of a "
    "code fence is treated as literal text, not parsed as inlines.\" — so a section scanner must not treat "
    "a `## ` line inside a fence as a heading | mined | 2026-10-27 | 360d | "
    "corpus/lessons/round-50.md, tools/append-only-audit.py |"
)

REPL = {"S496": ROW496, "S497": ROW497}
QUOTES = {
    "S496": [
        "dev is the device (major:minor); inode is the inode on that device",
        "The pathname field will usually be the file that is backing the mapping.",
    ],
    "S497": [
        "The parent-death signal is sent upon subsequent termination of the parent thread and also upon termination of each subreaper process",
        "The parent-death signal setting is cleared for the child of a fork(2).",
    ],
}


def split_cells(line):
    """Mirror of tools/sources-append-only.py split_cells, minus the escape subtlety."""
    s = line.strip()
    cells, buf, in_code, i = [], [], False, 1
    while i < len(s):
        ch = s[i]
        if ch == "\\" and i + 1 < len(s) and s[i + 1] == "|" and not in_code:
            buf.append("\\|")
            i += 2
            continue
        if ch == "`":
            in_code = not in_code
            buf.append(ch)
            i += 1
            continue
        if ch == "|" and not in_code:
            cells.append("".join(buf).strip())
            buf = []
            i += 1
            continue
        buf.append(ch)
        i += 1
    return cells, "".join(buf).strip()


def main():
    text = SRC.read_text(encoding="utf-8").splitlines(keepends=True)
    for variant, row498 in (("A", ROW498_A), ("B", ROW498_B)):
        out = []
        for line in text:
            if re.match(r"\| S496 \|", line):
                out.append(ROW496 + "\n")
            elif re.match(r"\| S497 \|", line):
                out.append(ROW497 + "\n")
            elif re.match(r"\| S498 \|", line):
                out.append(row498 + "\n")
            else:
                out.append(line)
        dst = S / f"proposed-{variant}.md"
        dst.write_text("".join(out), encoding="utf-8")
        print(f"wrote {dst}")

    # properties of each proposed row
    for label, row in (("S496", ROW496), ("S497", ROW497), ("S498-A", ROW498_A), ("S498-B", ROW498_B)):
        cells, trailing = split_cells(row)
        ticks = row.count("`")
        print(f"{label}: cells={len(cells)} (want 11) trailing={trailing!r} backticks={ticks} parity={'even' if ticks % 2 == 0 else 'ODD'}")

    # quote checks
    hay = {"S496": MAPS, "S497": PDE}
    for row, qs in QUOTES.items():
        for q in qs:
            print(f"{row} quote words={len(q.split()):>2} verbatim={q in hay[row]} :: {q[:60]}...")
    for row, qs in (
        ("S498-A", [
            html.unescape("A code fence is a sequence of at least three consecutive backtick characters (&#96;) or tildes (~)."),
            "The content of a code fence is treated as literal text, not parsed as inlines.",
        ]),
        ("S498-B", [
            "A fenced code block begins with a code fence, preceded by up to three spaces of indentation.",
            "The closing code fence must use the same character as the opening fence:",
            "The content of a code fence is treated as literal text, not parsed as inlines.",
        ]),
    ):
        for q in qs:
            print(f"{row} quote words={len(q.split()):>2} verbatim={q in CM} :: {q[:60]}...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
