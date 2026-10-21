#!/usr/bin/env python3
"""On the REAL release tree, enumerate every link map with the pinned install_links
digest (same serialization), gate-validate each, and report:
  - whether each accepted decoy drops a DT_NEEDED soname (names read with readelf -d);
  - whether any accepted decoy RETARGETS a standalone name (must be 0 for the R19 aim);
The identity parse (the legitimate map) is counted separately."""
import importlib.util
import sys
from pathlib import Path

SCRATCH = Path("/tmp/kama-r21-LinksDigestEncoding")
REAL = Path("/home/vgpnk/.local/opt/llama-b11755")
NEEDED_BY_IMPL = {"libllama-common.so.0", "libmtmd.so.0", "libllama.so.0",
                  "libggml.so.0", "libggml-base.so.0"}


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


prod = load("kama_prod", SCRATCH / "lane/tools/kama-llamacpp-live.py")
gate = load("kama_gate", SCRATCH / "lane/tests/llamacpp-live/check-receipt.py")

rt, rt_sha = prod.install_tree(str(REAL / "llama-server"))
rl, rl_sha = prod.install_links(str(REAL / "llama-server"))


def occurrences(s, pat):
    out, i = [], s.find(pat)
    while i != -1:
        out.append(i)
        i = s.find(pat, i + 1)
    return out


def ser(m):
    return "".join(f"{n} -> {m[n]}\n" for n in sorted(m))


S = ser(rl)
events = sorted([(p, "A") for p in occurrences(S, " -> ")] +
                [(p, "B") for p in occurrences(S, "\n")])
last = len(S) - 1
seqs = []


def rec(start, want, acc):
    for j in range(start, len(events)):
        p, kind = events[j]
        if kind != want:
            continue
        nxt = acc + [(p, kind)]
        if kind == "B":
            if p == last:
                seqs.append(nxt)
            else:
                rec(j + 1, "A", nxt)
        else:
            rec(j + 1, "B", nxt)


rec(0, "A", [])
accepted = []
for seq in seqs:
    m, prev, ok = {}, 0, True
    for i in range(0, len(seq), 2):
        a, b = seq[i][0], seq[i + 1][0]
        key = S[prev:a]
        if key in m:
            ok = False
            break
        m[key] = S[a + 4:b]
        prev = b + 1
    if not ok or ser(m) != S:
        continue
    r = gate._selftest_receipt_v3()
    r["server"]["install_tree"] = dict(rt)
    r["server"]["install_tree_sha256"] = rt_sha
    r["server"]["install_links"] = m
    r["server"]["install_links_sha256"] = gate.install_links_sha(m)
    r["server"]["sha256"] = rt["llama-server"]
    r["server"]["server_impl_sha256"] = rt["libllama-server-impl.so"]
    if gate.validate(r, expect_tree=rt_sha, expect_links=rl_sha) == []:
        accepted.append(m)

identity = [m for m in accepted if m == rl]
decoys = [m for m in accepted if m != rl]
removed_sets = [set(rl) - set(m) for m in decoys]
drop_needed = [bool(NEEDED_BY_IMPL & s) for s in removed_sets]
drop_only_non_needed = [bool(s) and not (NEEDED_BY_IMPL & s) for s in removed_sets]
retarget_violations = sum(1 for m in decoys for k in m if k in rl and m[k] != rl[k])
standalone_kept = sum(1 for m in decoys for k in m if k in rl)
print(f"parses_enumerated={len(seqs)} same_digest_parses_gate_accepted={len(accepted)}")
print(f"identity_parse_accepted={len(identity)} decoys_accepted={len(decoys)}")
print(f"decoys_dropping_at_least_one_NEEDED_soname={sum(drop_needed)} of {len(decoys)}")
print(f"decoys_dropping_only_non_NEEDED_names={sum(drop_only_non_needed)}")
print(f"standalone_names_kept_across_decoys={standalone_kept} retarget_violations={retarget_violations}")
minimal = sorted({tuple(sorted(s)) for s in removed_sets if NEEDED_BY_IMPL & s}, key=len)[:3]
for d in minimal:
    print("  smallest-removal example:", list(d))
ok = (len(identity) == 1 and len(decoys) > 0
      and sum(drop_needed) == len(decoys) and sum(drop_only_non_needed) == 0
      and retarget_violations == 0)
print("PASS: decoys drop a NEEDED soname, never only other names, never retarget"
      if ok else "FAIL")
sys.exit(0 if ok else 1)
