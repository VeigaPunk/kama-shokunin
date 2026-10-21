#!/usr/bin/env python3
"""ReopenS066 (KamaR21 FALSIFY): stdlib re-check of registry row S066 and its round-21 Gate quote.

Usage: check-s066.py MAN7_HTML TARBALL_TROFF HOST_TROFF SOURCES_MD LESSON_MD LANE_ROOT
  MAN7_HTML      https://man7.org/linux/man-pages/man8/ldconfig.8.html, fetched 2026-10-21
  TARBALL_TROFF  man-pages-6.19.tar.xz member man/man8/ldconfig.8 (kernel.org mirror)
  HOST_TROFF     /usr/share/man/man8/ldconfig.8.gz decompressed (pacman man-pages 6.19-1)
  SOURCES_MD     corpus/SOURCES.md blob at a6617149 (git show)
  LESSON_MD      corpus/lessons/round-21.md blob at a6617149 (git show)
  LANE_ROOT      scratch clone checked out at a6617149 (used-by path existence)
Exit 0 iff every PASS/FAIL check holds. INFO lines are observations, not verdicts.
"""
import hashlib
import html
import pathlib
import re
import sys

EXPECT_HTML_SHA = "6a81540a534692ed7cb6d5434275e08b3ade388311bdb88f1e4e506be2bfde38"
KINDS = {"spec", "docs", "paper", "code", "tool", "dataset", "talk", "book", "community", "own-work"}
RESULTS = []


def rec(tag, ok, detail=""):
    RESULTS.append(bool(ok))
    print(("PASS " if ok else "FAIL ") + tag + (f" :: {detail}" if detail else ""))


def info(tag, detail=""):
    print("INFO " + tag + (f" :: {detail}" if detail else ""))


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def toks(s):
    return re.findall(r"[A-Za-z0-9]+", s)


def man7_paragraphs(text):
    seg = text[text.index('id="DESCRIPTION"'):text.index('id="OPTIONS"')]
    pre = re.search(r"<pre>(.*?)</pre>", seg, re.S).group(1)
    body = html.unescape(re.sub(r"<[^>]+>", "", pre))
    return [norm(p) for p in re.split(r"\n\s*\n", body) if p.strip()]


def troff_paragraphs(path):
    """DESCRIPTION chunks split at .P/.PP macros; macro names dropped, arguments kept."""
    lines = path.read_text(encoding="utf-8").splitlines()
    i = lines.index(".SH DESCRIPTION")
    j = lines.index(".SH OPTIONS")
    chunks, cur = [], []
    for raw in lines[i + 1:j]:
        s = raw.strip()
        if s in (".P", ".PP"):
            chunks.append(" ".join(cur))
            cur = []
            continue
        if not s or s.startswith('.\\"'):
            continue
        if s.startswith("."):
            head, _, rest = s[1:].partition(" ")
            if head in ("in", "EX", "EE", "nf", "fi", "PD", "TP", "RS", "RE", "sp", "br"):
                continue
            s = rest
        cur.append(s)
    chunks.append(" ".join(cur))
    out = []
    for c in chunks:
        c = re.sub(r"\\f[BIRP]", "", c)
        c = c.replace("\\->", "->").replace("\\-", "-").replace("\\%", "").replace("\\&", "")
        c = c.replace("\\c", "").replace("\\~", " ").replace("( ", "(")
        out.append(norm(c))
    return out


def th_line(path):
    return next(l for l in path.read_text(encoding="utf-8").splitlines() if l.startswith(".TH "))


def main(argv):
    man7, tar, host, sources_p, lesson_p, lane = (pathlib.Path(a) for a in argv[1:7])

    # --- source bytes and paragraph structure -------------------------------------------
    raw = man7.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    rec("man7 HTML sha256 equals the pinned 2026-10-21 fetch", digest == EXPECT_HTML_SHA, digest)
    text = raw.decode("utf-8")
    paras = man7_paragraphs(text)
    info("man7 DESCRIPTION paragraphs (blank-line split)", str(len(paras)))
    for n, p in enumerate(paras, 1):
        info(f"  para {n}", p[:120] + ("..." if len(p) > 120 else ""))
    t_chunks = troff_paragraphs(tar)
    h_chunks = troff_paragraphs(host)
    rec("man7 DESCRIPTION paragraph count == upstream 6.19 troff chunk count",
        len(paras) == len(t_chunks), f"{len(paras)} vs {len(t_chunks)}")
    same = len(paras) == len(t_chunks) and all(toks(a) == toks(b) for a, b in zip(paras, t_chunks))
    rec("man7 DESCRIPTION word tokens == upstream 6.19 troff, paragraph by paragraph", same)
    rec("host 6.19-1 DESCRIPTION chunks == upstream 6.19 chunks", h_chunks == t_chunks)
    th_t, th_h = th_line(tar), th_line(host)
    info("upstream 6.19 tarball .TH", th_t)
    info("host man-pages 6.19-1 .TH", th_h)
    rec("man7 footer reads 'Linux man-pages 6.19' and date 2026-08-03",
        "Linux man-pages 6.19" in text and "2026-08-03" in text)
    rec("upstream .TH date 2026-08-03", "2026-08-03" in th_t)
    info("upstream .TH names the version as '(unreleased)'", str("(unreleased)" in th_t))

    # --- Gate quote in round-21.md (committed blob) -----------------------------------
    lesson = lesson_p.read_text(encoding="utf-8")
    gate = next((l for l in lesson.splitlines()
                 if l.startswith("| The soname is a link in a maintained chain |")), None)
    rec("round-21.md §Gate row for S066 present", gate is not None)
    m = re.search(r'§DESCRIPTION ¶(\d): "([^"]+)"', gate or "")
    rec("Gate row has '§DESCRIPTION ¶N: \"...\"' form", m is not None)
    loc, quote = m.group(1), m.group(2)
    nwords = len(quote.split())
    rec("Gate quote <= 25 words", nwords <= 25, f"{nwords} words: {quote!r}")
    hits = [n for n, p in enumerate(paras, 1) if quote in p]
    rec("Gate quote verbatim in man7 DESCRIPTION (whitespace-normalised)", bool(hits), f"paragraph(s) {hits}")
    rec("Gate ¶ number equals the paragraph holding the quote", hits == [int(loc)], f"Gate ¶{loc}, found ¶{hits}")
    troff_hits = [n for n, c in enumerate(t_chunks, 1) if quote in c]
    rec("Gate quote verbatim in upstream 6.19 troff", bool(troff_hits), f"chunk(s) {troff_hits}")
    rec("Gate URL equals the row URL",
        "https://man7.org/linux/man-pages/man8/ldconfig.8.html" in (gate or ""))

    # --- Row S066 in committed corpus/SOURCES.md ---------------------------------------
    rows = [l for l in sources_p.read_text(encoding="utf-8").splitlines() if re.match(r"^\|\s*S066\s*\|", l)]
    rec("exactly one S066 row", len(rows) == 1, str(len(rows)))
    cells = [c.strip() for c in rows[0].split("|")[1:-1]]
    names = ["id", "source", "kind", "tier", "scope", "anchor", "teaches", "status", "opened", "recheck", "used_by"]
    rec("S066 row has 11 cells (awk NF 13)", len(cells) == 11, str(len(cells)))
    d = dict(zip(names, cells))
    for k in names:
        info(f"row.{k}", d.get(k, ""))
    rec("kind in contract enum", d["kind"] in KINDS, d["kind"])
    rec("tier is A", d["tier"] == "A", d["tier"])
    rec("status is mined", d["status"] == "mined", d["status"])
    rec("opened is ISO 2026-10-21", d["opened"] == "2026-10-21", d["opened"])
    rec("recheck is a valid cadence or date",
        d["recheck"] == "on-release" or re.fullmatch(r"\d+d|\d{4}-\d{2}-\d{2}", d["recheck"]) is not None,
        d["recheck"])
    used = [p.strip() for p in d["used_by"].split(",") if p.strip() not in ("", "—")]
    rec("mined row has >= 1 used-by path", len(used) >= 1, str(len(used)))
    for p in used:
        fp = lane / p
        exists = fp.exists()
        cites = exists and "S066" in fp.read_text(encoding="utf-8")
        rec(f"used-by path exists and cites S066: {p}", exists and cites)
    rec("anchor cites §DESCRIPTION ¶1 and the first ¶ holds 'creates the necessary links'",
        "ldconfig creates the necessary links" in paras[0] and "¶1" in d["anchor"])
    chain_hits = [n for n, p in enumerate(paras, 1) if "libfoo.so -> libfoo.so.1 -> libfoo.so.1.12" in p]
    rec("anchor '¶3' holds the chain example (example is its own indented block)",
        chain_hits == [3], f"example found in ¶{chain_hits}")
    rec("teaches cell contains no pipe (census rule)", "|" not in d["teaches"])

    # --- scope / teaches observations on the whole page --------------------------------
    for term in ("DT_", "ELF", "DT_SONAME", "symlink", "symbolic link", "linker name", "real name",
                 "digest", "install", "glibc", "expects", "creates"):
        info(f"man7 page occurrences of {term!r}", str(text.count(term)))
    rec("man7 page never names DT_SONAME (scope exclusion is consistent)", "DT_" not in text)
    rec("man7 page gives glibc version notes (scope 'glibc systems')", "Since glibc" in text)
    rec("¶1 says ldconfig creates 'the necessary links'", "ldconfig creates the necessary links" in paras[0])
    rec("¶3 says ldconfig 'expects a certain pattern' for symbolic links",
        "ldconfig expects a certain pattern to how the symbolic links are set up" in paras[2])
    rec("'Failure to follow this pattern...' sentence present (paragraph 5)", "Failure to follow this pattern may result in compatibility issues after an upgrade." in paras[4])

    failed = [i for i, ok in enumerate(RESULTS) if not ok]
    print(f"SUMMARY checks={len(RESULTS)} pass={len(RESULTS) - len(failed)} fail={len(failed)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
