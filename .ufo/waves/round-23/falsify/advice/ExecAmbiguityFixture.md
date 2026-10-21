# ExecAmbiguityFixture: RevLookup F1 falsify grid (round 23, CloseKama22.ExecAmbiguityFixture-2)

## Verdict

**HOLDS.** RevLookup F1 (peel/cross-repo ambiguity overwrite) is live on the current
arm at 245a37f6: all 6 graded fault rows unmet, all 6 controls met, exit 1. The frozen
arm (4fe9339f) shows the identical cells on every row — the fault is inherited
unchanged by round 23, not introduced by it. Both arms keep every control (B2c, B4,
B5c), proving the `landed-ambiguous` detector itself works when the masking object is
absent; only the overwrite erases it. No crash, no traceback, no hang, no program
execution on any row (slowest arm run 0.07 s, timeout 30 s).

Mechanism, at 245a37f `tools/report-landing-audit.py`:
- `lookup()` 139-142 asks the bare name first "to keep ambiguity visible" (docstring
  130-134), but 152-154 (`if status[token] != "found"`) and 164
  (`status[token] = "found"`) let any per-repo resolution overwrite the bare
  ambiguity.
- `audit_round()` 323-325 checks every Landed citation through that `lookup` with peel
  `^{commit}`; git resolves `<prefix>^{commit}` by type, so a commit+blob ambiguity
  peels to the commit (premise observed: `68c726c^{commit}` →
  `68c726ca67aa781fc78594ef3be66a81e751800a commit 164`). A lane-internal commit+commit
  ambiguity is overwritten by the fleet resolving the same prefix to one commit.
- `apply_errata()` 389-392 validates corrections through the same peel lookup, so an
  ambiguous correction is accepted as `found`.

## Evidence (command + observed output)

Command: `python3 .ufo/waves/round-23/falsify/out/ExecAmbiguityFixture/ambiguity-grid.py`
(fresh scratch repos in /tmp, `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`,
example.invalid only; fixture premises verified with plain git before grading;
full log: `grid-run.txt`, exit 1).

Fixture collisions (byte-identical fast-import stream to the build wave's
`build/out/RevLookup/fixtures.py`, oids reproduce exactly): commit+blob share `68c726c`
in the lane; commits `8877aeef7b32` (first) + second share `8877aee`, lane holds both.

Grid rows (expect = normative, grounded in the tool's own contract: `landed-ambiguous`
= "such a token that is an ambiguous abbreviation", line 20; lookup docstring 134;
identical token reported when fleet lacks the mask — control B2c):

| Row | Kind | Scenario (lookup / audit) | expect(current) | frozen | current | met |
|---|---|---|---|---|---|---|
| A1a | control | bare `68c726c` in lane | ambiguous | ambiguous | ambiguous | yes |
| A1b | fault | peel `68c726c` in lane | ambiguous | found | found | no |
| A2a | fault | bare `8877aee`, lane+fleet(first) | ambiguous | found | found | no |
| A2b | fault | peel `8877aee`, lane+fleet(first) | ambiguous | found | found | no |
| A2c | control | bare `8877aee`, fleet lacks both | ambiguous | ambiguous | ambiguous | yes |
| A3 | control | unique prefix `9be247d` | found | found | found | yes |
| A4 | control | absent `d3adb33` | missing | missing | missing | yes |
| B1 | fault | Landed cites `68c726c` | rc1 `landed-ambiguous:68c726c` | rc0 [] | rc0 [] | no |
| B2 | fault | Landed cites `8877aee` | rc1 `landed-ambiguous:8877aee` | rc0 [] | rc0 [] | no |
| B2c | control | same, fleet lacks both | rc1 `landed-ambiguous:8877aee` | rc1 ✓ | rc1 ✓ | yes |
| B3 | control | Landed cites `9be247d` | rc0 [] | rc0 [] | rc0 [] | yes |
| B4 | control | Landed cites `d3adb33` | rc1 `landed-unresolved:d3adb33` | rc1 ✓ | rc1 ✓ | yes |
| B5 | fault | errata correction `68c726c` | rc1 `errata-invalid:68c726c` | rc0, correction accepted | rc0, correction accepted | no |
| B5c | control | errata correction `d3adb34` | rc1 `errata-invalid:d3adb34` | rc1 ✓ | rc1 ✓ | yes |

Cross-check with the build wave's independent review
(`.ufo/waves/round-23/build/advice/RevLookup.md:24`): "Commit + blob share 7-hex
`68c726c`, same repo: bare `ambiguous`; `^{commit}` → `found`." — reproduced here at
audit level with exit codes, plus the errata path and the frozen arm.

Additional finding (informational): the `lookup()` docstring (131-134) claims "With a
peel, git answers `missing` for an ambiguous short name" — false on git 2.56.0: the
peel resolves by type to the commit (A1b frozen cell is `found`, not `missing`). The
bare pre-pass (139-142) is therefore defeated by design of 152-154/164, not by git.

## Not verified

- Only the two declared arms at exactly 245a37f6 / 4fe9339f; no branch or working-tree
  drift beyond them.
- Host git 2.56.0 only; no <2.45 behavior (T01 floor) exercised.
- Hang/exec channels are structurally absent from these fixtures (no promisor, no
  sshCommand); their coverage lives in the C1 grid and was not retested here.
- Alternates (O01), gitfile redirect (O02), second Landed section, sibling tools —
  other seats.
- The batch-check output-shape premise was corrected once (batch-check echoes the
  resolved 40-hex oid on found lines, not the query); the corrected premises are
  re-verified with plain git on every run.

## Files written

- `.ufo/waves/round-23/falsify/out/ExecAmbiguityFixture/ambiguity-grid.py` (builder +
  harness; exit 0 falsified / 1 holds / 2 could-not-evaluate; `--repo`, `--scratch`)
- `.ufo/waves/round-23/falsify/out/ExecAmbiguityFixture/grid-run.txt` (the logged run)
- `.ufo/waves/round-23/falsify/advice/ExecAmbiguityFixture.md` (this report)

Scratch (not deliverables): `/tmp/kama-r23w2/ExecAmbiguityFixture` (clone, HEAD verified
245a37f6), `/tmp/kama-r23w2/arms/`, `/tmp/kama-r23w2/ExecAmbiguityFixture-grid/`.
Installs: none (git 2.56.0, python 3.14.8 already sufficient).
