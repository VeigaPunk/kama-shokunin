#!/usr/bin/env python3
"""Create the named source mutants from the pristine copies and record hashes."""
import hashlib
import json
import sys
from pathlib import Path

S = Path(sys.argv[1])
PRISTINE = S / "pristine"
MUT = S / "mutants"
MUT.mkdir(exist_ok=True)

C1 = "round80-selfrecord-round79.py"
C2 = "round80-engine-pin-relations.py"
C3 = "round80-ollama-census.py"

C1_LOOP = '''        for b in fact_blocks:
            if b["old"] != declared:
                reasons.append("old-mismatch")
                unbacked += 1
                continue
            if not re.fullmatch(r"[0-9a-f]{40}", b["at"]):
                reasons.append("at-malformed")
                unbacked += 1
                continue
            resolved = resolve(repo, b["at"])
            if resolved is None:
                reasons.append("at-unresolvable")
                unbacked += 1
                continue
            if resolved != sealed:
                reasons.append("at-not-sealed")
                unbacked += 1
                continue
            if b["new"] != seen_tip:
                reasons.append("new-not-rederived")
                unbacked += 1
                continue
            ok = b
'''

SPECS = [
    dict(tag="c1-m1-new-not-rederived", module=C1,
         old='''            if b["new"] != seen_tip:
                reasons.append("new-not-rederived")
                unbacked += 1
                continue
''', new="",
         note="a correction is accepted although `new` does not re-derive at the tip"),
    dict(tag="c1-m2-at-any-resolvable", module=C1,
         old='''            if resolved != sealed:
                reasons.append("at-not-sealed")
                unbacked += 1
                continue
''', new="",
         note="`at` may name any resolvable commit, not the sealed revision"),
    dict(tag="c1-m3-corrected-from-prose", module=C1,
         old=C1_LOOP,
         new='''        for b in fact_blocks:
            ok = b
            break
''',
         note="a fact counts corrected when any block is present; old/at/new are not re-derived"),
    dict(tag="c1-m4-unbacked-ignored", module=C1,
         old='    return int(bool(s["mismatches"] or s["unbacked"]))',
         new='    return int(bool(s["mismatches"]))',
         note="unbacked corrections no longer fail the verdict"),
    dict(tag="c2-m1-newer-as-strings", module=C2,
         old='        out[name] = (tuple(int(g) for g in groups), info.get("peeled") or info.get("oid", ""))',
         new='        out[name] = (".".join(groups), info.get("peeled") or info.get("oid", ""))',
         note="version keys compared lexicographically instead of numerically"),
    dict(tag="c2-m2-missing-ref-engine-only", module=C2,
         old='''    required = [(p["engine"], p["pin"]) for p in pins] + list(cross_refs)
    for engine, ref in required:
        if (engine, ref) not in seen:
            findings.append(f"PIN_RELATIONS_FINDING missing-ref engine={engine} ref={ref}")
''',
         new='''    required = [(p["engine"], p["pin"]) for p in pins] + list(cross_refs)
    have_engines = {engine for engine, _ in seen}
    for engine, ref in required:
        if engine not in have_engines:
            findings.append(f"PIN_RELATIONS_FINDING missing-ref engine={engine} ref={ref}")
''',
         note="a missing ref counts as covered when any other ref of the same engine has a row"),
    dict(tag="c2-m3-receipt-always-present", module=C2,
         old='''def receipt_committed(repo: Path, path: str, tip: str) -> bool:
    proc = subprocess.run(["git", "-C", str(repo), "cat-file", "-e", f"{tip}:{path}"],
                          capture_output=True, text=True)
    if proc.returncode == 0:
        return True
    return (repo / path).is_file()
''',
         new='''def receipt_committed(repo: Path, path: str, tip: str) -> bool:
    return True
''',
         note="every receipt counts as present and committed"),
    dict(tag="c3-m1-legs-share-registry", module=C3,
         old='        write_registry(no_reg, None)',
         new='        write_registry(no_reg, port)',
         note="the unregistered leg runs against a registry that declares the port"),
    dict(tag="c3-m2-governed-without-class", module=C3,
         old='''            if summary.get("governed") != (1 if name == "yes" else 0):
                findings.append(f"OLLAMA_CENSUS_FINDING governed-count leg={name} "
                                f"governed={summary.get('governed')}")
''', new="",
         note="the summary governed count is not tied to the registered class"),
    dict(tag="c3-m3-audit-no-engine-name", module=C3,
         old='''        if engine not in text:
            findings.append(f"CLASS_ENGINES_FINDING receipt-names-other-engine {engine} {receipt}")
            continue
''', new="",
         note="a register row verifies on a receipt that names a different engine"),
    dict(tag="c3-m4-audit-one-engine", module=C3,
         old='''    if len(engines) < 2:
        findings.append(f"CLASS_ENGINES_FINDING one-engine engines={len(engines)}")
''', new="",
         note="a one-engine register audits green; the two-engine requirement is dropped"),
]

out = []
for spec in SPECS:
    src = (PRISTINE / spec["module"]).read_text()
    count = src.count(spec["old"])
    if count != 1:
        raise SystemExit(f"{spec['tag']}: anchor count {count} != 1")
    mutant = src.replace(spec["old"], spec["new"], 1)
    if mutant == src:
        raise SystemExit(f"{spec['tag']}: replacement changed nothing")
    target = MUT / spec["tag"]
    target.mkdir(exist_ok=True)
    path = target / spec["module"]
    path.write_text(mutant)
    out.append(dict(spec, path=str(path),
                    pristine_sha256=hashlib.sha256(src.encode()).hexdigest(),
                    mutant_sha256=hashlib.sha256(mutant.encode()).hexdigest(),
                    kept_bytes=len(mutant)))
(MUT / "index.json").write_text(json.dumps(out, indent=2) + "\n")
print("\n".join(f"{s['tag']}: {s['pristine_sha256'][:12]} -> {s['mutant_sha256'][:12]}" for s in out))
