#!/usr/bin/env python3
"""Proposed unambiguous digest encodings for the llama.cpp install pins
(KamaR21, round 21, LinksDigestEncoding). Standalone: nothing here edits the lane.

install_tree_sha256 (back-compatible):
  Keep the current bytes sha256(''.join(f'{name} {sha}\\n' for sorted names)).
  Admit a map only if every name is non-empty strict UTF-8 without a newline byte
  and every digest is 64 lowercase hex. On the admitted domain the serialization is
  injective: split on '\\n' (names cannot contain it), take the last 64 bytes as the
  digest and require ' ' before them. Every currently admissible tree keeps its
  exact digest.

install_links_sha256 (new in round 21, not in any landed receipt; free to change):
  sha256 over canonical JSON: sort_keys, compact separators, ensure_ascii, no NaN.
  JSON string escaping is a bijection, so json.loads(bytes) recovers the map.

Checks exit 0 iff all pass. Reads the real release tree only.
"""
import hashlib
import importlib.util
import json
import random
import re
import sys
from pathlib import Path

SCRATCH = Path("/tmp/kama-r21-LinksDigestEncoding")
PRODUCER = SCRATCH / "lane/tools/kama-llamacpp-live.py"
REAL = Path("/home/vgpnk/.local/opt/llama-b11755")
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else SCRATCH / "proposal-out"
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
FAILS = []


def check(tag, ok, detail):
    print(f"CHECK {tag}: {'PASS' if ok else 'FAIL'} :: {detail}", flush=True)
    if not ok:
        FAILS.append(tag)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


prod = load("kama_prod", PRODUCER)


def sha(data):
    return hashlib.sha256(data).hexdigest()


# ------------------------------------------------------------ proposed encodings
def legacy_tree_bytes(tree):
    """Current bytes, verbatim: sorted 'name sha\\n' lines, strict UTF-8."""
    return "".join(f"{n} {tree[n]}\n" for n in sorted(tree)).encode("utf-8")


def admit_tree(tree):
    """Fail closed: raise for any map whose legacy serialization is not injective."""
    for name, digest in tree.items():
        if not isinstance(name, str) or not name:
            raise ValueError(f"member name must be a non-empty string: {name!r}")
        if "\n" in name:
            raise ValueError(f"member name contains a newline: {name!r}")
        try:
            name.encode("utf-8")
        except UnicodeEncodeError as exc:
            raise ValueError(f"member name is not strict UTF-8: {name!r}") from exc
        if not isinstance(digest, str) or not HEX64.match(digest):
            raise ValueError(f"member digest is not 64 lowercase hex: {name!r}")
    return tree


def install_tree_sha256(tree):
    return sha(legacy_tree_bytes(admit_tree(tree)))


def decode_admitted_tree(data):
    """Left inverse of legacy_tree_bytes on the admitted domain."""
    text = data.decode("utf-8")
    if text == "":
        return {}
    if not text.endswith("\n"):
        raise ValueError("record stream does not end with a newline")
    out = {}
    for line in text[:-1].split("\n"):
        if len(line) < 66 or line[-65] != " " or not HEX64.match(line[-64:]):
            raise ValueError(f"malformed record: {line!r}")
        name = line[:-65]
        if name in out:
            raise ValueError(f"duplicate name: {name!r}")
        out[name] = line[-64:]
    return out


def canonical_links_bytes(links):
    for k, v in links.items():
        if not isinstance(k, str) or not isinstance(v, str):
            raise ValueError("links must map str to str")
    return json.dumps(links, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def install_links_sha256(links):
    return sha(canonical_links_bytes(links))


def legacy_links_bytes(links):
    """Current draft bytes, verbatim: sorted 'name -> text\\n' lines."""
    return "".join(f"{n} -> {links[n]}\n" for n in sorted(links)).encode("utf-8")


# ----------------------------------------------- collision-class enumeration helpers
def occurrences(s, pat):
    out, i = [], s.find(pat)
    while i != -1:
        out.append(i)
        i = s.find(pat, i + 1)
    return out


def alternating_parses(S):
    events = sorted([(p, "A") for p in occurrences(S, " -> ")] +
                    [(p, "B") for p in occurrences(S, "\n")])
    last = len(S) - 1
    out = []

    def rec(start, want, acc):
        for j in range(start, len(events)):
            p, kind = events[j]
            if kind != want:
                continue
            nxt = acc + [(p, kind)]
            if kind == "B":
                if p == last:
                    out.append(nxt)
                else:
                    rec(j + 1, "A", nxt)
            else:
                rec(j + 1, "B", nxt)

    rec(0, "A", [])
    return out


def decode_links(S, seq):
    m, prev = {}, 0
    for i in range(0, len(seq), 2):
        a, b = seq[i][0], seq[i + 1][0]
        key = S[prev:a]
        if key in m:
            return None
        m[key] = S[a + 4:b]
        prev = b + 1
    return m


def absorb(tree, names_set):
    """Fold each member in names_set into the key of the next kept member."""
    m, prefix = {}, ""
    for n in sorted(tree):
        if n in names_set:
            prefix += f"{n} {tree[n]}\n"
        else:
            m[prefix + n] = tree[n]
            prefix = ""
    return m


# ------------------------------------------------------------------ checks
rt, rt_legacy = prod.install_tree(str(REAL / "llama-server"))
rl, rl_legacy = prod.install_links(str(REAL / "llama-server"))

# C1: back-compat of the tree digest on the real release tree.
new_rt = install_tree_sha256(rt)
check("C1-real-tree-install_tree_sha256-unchanged", new_rt == rt_legacy,
      f"producer_legacy={rt_legacy} proposed={new_rt} members={len(rt)}")

# C2: admission refuses every newline-bearing collision map built from the real tree.
cpu = {n for n in rt if n.startswith("libggml-cpu-")}
refusals = {
    "synthetic-E1-notes": {"notes-1.txt " + sha(b"one") + "\nnotes-2.txt": sha(b"two")},
    "real-cpu-backends-absorbed": absorb(rt, cpu),
    "real-LICENSE-absorbed": absorb(rt, {"LICENSE"}),
}
refused = {}
for label, m in refusals.items():
    same_legacy = legacy_tree_bytes(m) == legacy_tree_bytes(rt) if label.startswith("real") else None
    try:
        admit_tree(m)
        refused[label] = "ADMITTED"
    except ValueError as exc:
        refused[label] = f"refused: {str(exc)[:60]}"
    if same_legacy is not None:
        refused[label] += f" | same_legacy_bytes_as_real_tree={same_legacy}"
check("C2-admission-refuses-collision-decoys",
      all(v.startswith("refused") for v in refused.values()),
      json.dumps(refused, sort_keys=True))

# C3: injectivity on the admitted domain (random maps, round-trip through decode).
ALPH = list("abcdefghijklmnopqrstuvwxyz0123456789-._ >\t\"\\") + ["é", "ü", "\r"]
rng = random.Random(21)
failures = 0
for _ in range(3000):
    m = {}
    for _ in range(rng.randint(1, 8)):
        name = "".join(rng.choice(ALPH) for _ in range(rng.randint(1, 12)))
        m[name] = "%064x" % rng.getrandbits(256)
    admit_tree(m)
    if decode_admitted_tree(legacy_tree_bytes(m)) != m:
        failures += 1
check("C3-admitted-tree-serialization-injective", failures == 0,
      f"random_admitted_maps=3000 round_trip_failures={failures}")

# C4: canonical links digest separates the entire collision class of the real link map.
S = legacy_links_bytes(rl).decode("utf-8")
valid, distinct_dicts, canon_digests, legacy_digests = 0, set(), set(), set()
for seq in alternating_parses(S):
    m = decode_links(S, seq)
    if m is None or legacy_links_bytes(m).decode("utf-8") != S:
        continue
    valid += 1
    distinct_dicts.add(tuple(sorted(m.items())))
    canon_digests.add(install_links_sha256(m))
    legacy_digests.add(sha(legacy_links_bytes(m)))
    assert json.loads(canonical_links_bytes(m)) == m
check("C4-canonical-links-separates-collision-class",
      valid == len(distinct_dicts) == len(canon_digests) and len(legacy_digests) == 1,
      f"same_legacy_digest_parses={valid} distinct_maps={len(distinct_dicts)} "
      f"distinct_canonical_digests={len(canon_digests)} distinct_legacy_digests={len(legacy_digests)}")

# C5: the two small link collisions (E2, E3) and the synthetic soname pair.
pairs = {
    "E2-arrow": ({"x -> y": "z"}, {"x": "y -> z"}),
    "E3-soname-newline": ({"libllama-alias.so": "libllama.so.0", "libllama.so.0": "libllama.so"},
                          {"libllama-alias.so -> libllama.so.0\nlibllama.so.0": "libllama.so"}),
}
pair_rows = {}
all_sep = True
for label, (a, b) in pairs.items():
    legacy_eq = sha(legacy_links_bytes(a)) == sha(legacy_links_bytes(b))
    canon_ne = install_links_sha256(a) != install_links_sha256(b)
    all_sep = all_sep and legacy_eq and canon_ne
    pair_rows[label] = {"legacy_equal": legacy_eq, "canonical_distinct": canon_ne,
                        "canonical_a": install_links_sha256(a),
                        "canonical_b": install_links_sha256(b)}
check("C5-small-link-collisions-separated", all_sep, json.dumps(pair_rows, sort_keys=True))

# C6: golden values for the real release tree (for pinning in both producer and gate).
golden = {
    "real_install_tree_sha256_unchanged": new_rt,
    "real_install_links_sha256_legacy_draft": rl_legacy,
    "real_install_links_sha256_canonical": install_links_sha256(rl),
    "real_regular_members": len(rt),
    "real_links": len(rl),
}
check("C6-golden-real-tree-values-recorded", all(golden.values()),
      json.dumps(golden, sort_keys=True))

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "golden-and-pairs.json").write_text(
    json.dumps({"golden": golden, "pairs": pair_rows, "refusals": refused},
               indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
print(f"WROTE {OUT / 'golden-and-pairs.json'}")
print("FAILED:" if FAILS else "ALL CHECKS PASS", FAILS if FAILS else "")
sys.exit(1 if FAILS else 0)
