#!/usr/bin/env python3
"""Generate append-only-audit.py mutants for seat M1Tool (round 48).

Each mutant is a single minimal textual mutation of the pristine tool.
Every `old` string must occur exactly once in the pristine source; the
generator aborts otherwise (no silent mis-anchoring).
"""
import difflib
import pathlib
import sys

S = pathlib.Path("/fast/scratch/hyaku/kama-r48/M1Tool")
src = (S / "pristine-append-only-audit.py").read_text()

MUTANTS = [
    # --- parse_region
    ("M01", "parse-region-fullmatch", "m = REGION.fullmatch(cell)", "m = REGION.match(cell)"),
    ("M02", "parse-region-exempt-prefix-drop",
     "if not titles or not all(t.startswith(\"## \") for t in titles):", "if not titles:"),
    ("M03", "parse-region-only-prefix-drop", "if not body.startswith(\"## \"):", "if False:"),
    # --- sections()
    ("M04", "sections-prefix-nospace", "if line.startswith(b\"## \"):", "if line.startswith(b\"##\"):"),
    ("M05", "sections-no-trailing-strip",
     "title = line.rstrip(b\"\\r\").decode(\"utf-8\", \"replace\").rstrip()",
     "title = line.rstrip(b\"\\r\").decode(\"utf-8\", \"replace\")"),
    ("M06", "sections-no-crlf-strip",
     "title = line.rstrip(b\"\\r\").decode(\"utf-8\", \"replace\").rstrip()",
     "title = line.decode(\"utf-8\", \"replace\").rstrip()"),
    ("M54", "sections-strict-decode",
     "title = line.rstrip(b\"\\r\").decode(\"utf-8\", \"replace\").rstrip()",
     "title = line.rstrip(b\"\\r\").decode(\"utf-8\").rstrip()"),
    # --- eligibility (comparison and window)
    ("M07", "eligibility-strict-gt", ">= pcount[t]}", "> pcount[t]}"),
    ("M08", "window-exclude-event", "window = commits[i:]", "window = commits[i + 1:]"),
    ("M09", "window-all-commits", "window = commits[i:]", "window = commits"),
    ("M52", "eligible-guard-drop",
     "if max(r.section_counts(wb[f\"{x}:{f}\"])[t] if wb[f\"{x}:{f}\"] else 0 for x in window)",
     "if max(r.section_counts(wb[f\"{x}:{f}\"])[t] for x in window)"),
    # --- only-prefix filter
    ("M10", "only-prefix-equality",
     "if prefixes and not any(s is not None and s.startswith(q) for q in prefixes):",
     "if prefixes and not any(s is not None and s == q for q in prefixes):"),
    ("M11", "only-prefix-none-crash",
     "if prefixes and not any(s is not None and s.startswith(q) for q in prefixes):",
     "if prefixes and not any(s.startswith(q) for q in prefixes):"),
    # --- exempt membership
    ("M12", "exempt-always", "if s in eligible:", "if s in titles:"),
    ("M13", "exempt-inverted", "if s in eligible:", "if s not in eligible:"),
    # --- G counting
    ("M14", "g-double", "G[text] += 1", "G[text] += 2"),
    ("M15", "ng-distinct", "ng = sum(G.values())", "ng = len(G)"),
    # --- held / clamp / K
    ("M16", "held-no-clamp", "max(0, M[l] - K[l])", "M[l] - K[l]"),
    ("M17", "held-ignore-k", "min(n, max(0, M[l] - K[l]))", "min(n, M[l])"),
    ("M18", "k-no-subtract", "K = r.lines(pb) - D", "K = r.lines(pb)"),
    # --- by condition / best
    ("M19", "by-drop-ng", "if by is None and ng and h == ng:", "if by is None and h == ng:"),
    ("M20", "best-last", "if h > best:", "if h >= best:"),
    ("M21", "by-geq-equivalent", "if by is None and ng and h == ng:", "if by is None and ng and h >= ng:"),
    # --- status
    ("M22", "status-ungraded-invert", "if ng == 0:", "if ng != 0:"),
    ("M23", "status-swap",
     "status = \"restored\" if best == ng else (\"unrestored\" if best == 0 else \"partial\")",
     "status = \"restored\" if best == ng else (\"partial\" if best == 0 else \"unrestored\")"),
    # --- regressed formula
    ("M24", "regressed-leq", "e[\"held_at_to\"] < e[\"restored_max\"]", "e[\"held_at_to\"] <= e[\"restored_max\"]"),
    ("M25", "regressed-restored-only",
     "e[\"status\"] in (\"restored\", \"partial\") and e[\"held_at_to\"] < e[\"restored_max\"]",
     "e[\"status\"] == \"restored\" and e[\"held_at_to\"] < e[\"restored_max\"]"),
    # --- exit_code terms
    ("M26", "exit-drop-regressed",
     "return 1 if (s[\"partial\"] or s[\"unrestored\"] or s[\"regressed\"] or s[\"vanished\"]",
     "return 1 if (s[\"partial\"] or s[\"unrestored\"] or s[\"vanished\"]"),
    ("M27", "exit-drop-vanished", "s[\"regressed\"] or s[\"vanished\"]", "s[\"regressed\"]"),
    ("M28", "exit-drop-baddecl", "or s[\"bad_declarations\"]) else 0", ") else 0"),
    ("M48", "main-return-zero", "return exit_code(res)", "return 0"),
    # --- binds()
    ("M29", "binds-drop-negations", " or any(n in low for n in NEGATIONS)", ""),
    ("M30", "binds-or-to-and",
     "return fnmatch.fnmatchcase(decl_path, pattern) or (bool(tok) and tok in low)",
     "return fnmatch.fnmatchcase(decl_path, pattern) and (bool(tok) and tok in low)"),
    ("M31", "binds-drop-self",
     "return fnmatch.fnmatchcase(decl_path, pattern) or (bool(tok) and tok in low)",
     "return bool(tok) and tok in low"),
    # --- row_token
    ("M32", "row-token-wildcard-base", "return parts[-2] if len(parts) > 1 else \"\"", "return parts[-1]"),
    ("M33", "row-token-keep-ext", "return base.rsplit(\".\", 1)[0] if \".\" in base else base", "return base"),
    # --- line_at / declaration region checks
    ("M34", "line-at-off-by-one", "return ls[n - 1] if 1 <= n <= len(ls) else None",
     "return ls[n] if 1 <= n <= len(ls) else None"),
    ("M35", "decl-exempt-drop-rederived",
     "if text is None or \"re-derived\" not in low or not all(t[3:].strip().lower() in low for t in region[1]):",
     "if text is None or not all(t[3:].strip().lower() in low for t in region[1]):"),
    ("M36", "decl-exempt-all-to-any",
     "not all(t[3:].strip().lower() in low for t in region[1])",
     "not any(t[3:].strip().lower() in low for t in region[1])"),
    ("M37", "decl-only-drop-prefix",
     "elif not binds(text, pat, pp) or region[1][3:].strip().lower() not in low:",
     "elif not binds(text, pat, pp):"),
    ("M55", "decl-region-star-drop", "if region[0] == \"*\":\n        return out",
     "if region[0] == \"never*\":\n        return out"),
    # --- parse_contract
    ("M38", "contract-cells-4", "if len(cells) != 5:", "if len(cells) != 4:"),
    ("M39", "contract-drop-rule",
     "if not pat or rule not in RULES or not re.fullmatch(r\"[^:]+:\\d+\", decl):",
     "if not pat or not re.fullmatch(r\"[^:]+:\\d+\", decl):"),
    # --- threshold / numstat / deleted_lines positions
    ("M40", "threshold-leq", "if ns[f] < threshold:", "if ns[f] <= threshold:"),
    ("M41", "numstat-additions", "res[path] = int(parts[1]) if parts[1].isdigit() else None",
     "res[path] = int(parts[0]) if parts[1].isdigit() else None"),
    ("M42", "deleted-pos-plus-one", "out.append((start + gd, ln[1:]))", "out.append((start + gd + 1, ln[1:]))"),
    ("M43", "psec-off-by-one", "s = psec[pos - 1]", "s = psec[pos]"),
    ("M44", "hunk-new-start", "start = int(m.group(1))", "start = int(m.group(3))"),
    # --- vanished / expand
    ("M45", "vanished-keep-present", "if t not in present and any(fnmatch", "if any(fnmatch"),
    ("M46", "expand-any-to-all",
     "return sorted({t for t in tree if any(fnmatch.fnmatchcase(t, p) for p in patterns)})",
     "return sorted({t for t in tree if all(fnmatch.fnmatchcase(t, p) for p in patterns)})"),
    # --- file_regions union
    ("M53", "titles-overwrite", "titles |= set(region[1])", "titles = set(region[1])"),
    # --- render (text output)
    ("M47", "render-deleted", "deleted={e['deleted']}", "deleted={e['graded']}"),
    # --- selftest verdict integrity
    ("M49", "selftest-fail-hardcode",
     "print(f\"AOA_SELFTEST pass={len(cases) - fails} fail={fails}\")",
     "print(f\"AOA_SELFTEST pass={len(cases) - fails} fail=0\")"),
    ("M50", "selftest-fails-zero", "fails = sum(1 for _, ok, _ in cases if not ok)", "fails = 0"),
    ("M51", "case-vacuous", "ok, why = fn()", "ok, why = True, \"\""),
]

generated = []
for mid, tag, old, new in MUTANTS:
    n = src.count(old)
    if n != 1:
        print(f"ABORT {mid}-{tag}: {n} occurrences of old string", file=sys.stderr)
        sys.exit(1)
    mut = src.replace(old, new, 1)
    p = S / "mutants" / f"{mid}-{tag}.py"
    p.write_text(mut)
    diff = "\n".join(difflib.unified_diff(src.splitlines(), mut.splitlines(),
                                          "pristine", f"{mid}-{tag}", lineterm=""))
    (S / "diffs" / f"{mid}-{tag}.diff").write_text(diff + "\n")
    generated.append(f"{mid}-{tag}")

print(f"generated {len(generated)} mutants")
