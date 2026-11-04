#!/usr/bin/env python3
"""RVW01C2Attack -- build sixth-shim candidates for the C2 waiver boundary.

Parent for every variant: the LANDED census bytes (tools/round65-host-census.py,
sha256 44bebd671c0d12118c92ace1ef6bd7491a60c7acbce79f1668b81a822b245919),
copied read-only into scratch. Each variant carries the real 22-member table and
differs from the landed census by exactly ONE anchored mutation.

Holes (from the seat brief's candidate list):
  H1-waiver-covers-pass     a --waive naming an EVALUATED (passing) member is counted
                            into `waived=`; verdict claims a consumed waiver though no
                            member was not-evaluated.
  H2-forged-waived-token    `waived=<n-args>` printed whenever waiver args exist,
                            regardless of any waiver actually being consumed.
  H3-second-call-silent     a second main() call with the same waive args after a
                            FAILING run prints nothing and exits 0 (silent only on the
                            fail-waiver fixture; REFUSED/ALLPASS repeats unaffected).
  H4-phantom-not-evaluated  `not_evaluated` also counts unmatched waiver args -- it is
                            printed from an argv-derived counter, not the refusal counter.
"""
import hashlib
import pathlib
import sys

LANE = pathlib.Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
S = pathlib.Path("/fast/scratch/hyaku/kama-r71/RVW01C2Attack")
SRC = LANE / "tools/round65-host-census.py"
EXPECT_SHA = "44bebd671c0d12118c92ace1ef6bd7491a60c7acbce79f1668b81a822b245919"

W_WARN = (
    "        elif w in evaluated:\n"
    "            print(f\"warning: --waive {w!r} unused: member was evaluated \"\n"
    "                  f\"({evaluated[w]}); a waiver covers only not-evaluated members\",\n"
    "                  file=sys.stderr)\n"
)
W_CELL = '    waived_cell = f" waived={waived}" if waived else ""\n'
W_NAMES = "    member_names = {name for _, name, _, _, _ in MEMBERS}\n"
W_SET = "    waive_set = set(waive)\n"
W_DEF = "def main():\n    # --waive <member-name>"


def mutate(name, replacements):
    text = SRC.read_text()
    sha = hashlib.sha256(text.encode()).hexdigest()
    assert sha == EXPECT_SHA, f"parent bytes drifted: {sha}"
    for old, new in replacements:
        n = text.count(old)
        assert n == 1, f"{name}: anchor not unique (count={n}): {old[:60]!r}"
        text = text.replace(old, new)
    out = S / "shims" / f"{name}.py"
    out.write_text(text)
    print(f"wrote {out} ({len(text)} bytes)")
    return out


def main():
    S.joinpath("shims").mkdir(parents=True, exist_ok=True)
    mutate("H1-waiver-covers-pass", [(
        W_WARN,
        "        elif w in evaluated:\n"
        "            waived += 1\n",
    )])
    mutate("H2-forged-waived-token", [(
        W_CELL,
        '    waived_cell = f" waived={len(waive_set)}" if waive_set else ""\n',
    )])
    mutate("H3-second-call-silent", [
        (W_DEF,
         "_SILENCED = set()\n\n\n" + W_DEF),
        (W_SET,
         W_SET +
         "    if tuple(sorted(waive_set)) in _SILENCED:\n"
         "        return 0\n"),
        (W_CELL,
         "    if failed and waive_set:\n"
         "        _SILENCED.add(tuple(sorted(waive_set)))\n" + W_CELL),
    ])
    mutate("H4-phantom-not-evaluated", [(
        W_NAMES,
        W_NAMES +
        "    not_evaluated += sum(1 for w in waive_set if w not in member_names)\n",
    )])
    return 0


if __name__ == "__main__":
    sys.exit(main())
