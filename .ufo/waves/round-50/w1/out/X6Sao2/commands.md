# X6Sao2 command log (round 50, census + append-only at the build)

Scratch: `S=/fast/scratch/hyaku/kama-r50/X6Sao2` (TMPDIR=$S), system date 2026-10-27T00:55Z.
Clone: `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane` (read-only use).
Build-tip tree export (read-only): `git -C lane archive 97c864b | tar -x -C $S/tree97`
Freeze-tip tree export: `git -C lane archive 601c8889 | tar -x -C $S/treef`

## 1. Census, whole-fleet invocation

```
$ bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama
... 97 lines, see census-root-kama.out
exit=1
```
(97 = 93 W04 + 1 W01 + 3 E11. Lane worktree at integration HEAD 3b79eadd; SOURCES.md there
differs from the 97c864b blob only in the S498 teaches cell, see §4.)

## 2. Census `--file` on a scratch copy at the build

```
$ bash scripts/sources-census.sh validate --file $S/tree97/corpus/SOURCES.md
... 97 lines, see census-file-build.out
exit=1
$ bash scripts/sources-census.sh census --file $S/tree97/corpus/SOURCES.md
rows 239 | tier.A 228 | tier.B 7 | tier.C 4 | status.mined 220 | status.queued 8 | status.rejected 11
exit=0
```

## 3. Census `--file` at the freeze (reproducing census/start.out)

```
$ bash scripts/sources-census.sh census --file $S/treef/corpus/SOURCES.md
rows 236 | tier.A 225 | tier.B 7 | tier.C 4 | status.mined 217 | status.queued 8 | status.rejected 11
exit=0
$ bash scripts/sources-census.sh validate --file $S/treef/corpus/SOURCES.md
... 95 lines + ok, see census-file-freeze.out ; exit=0
$ diff <(grep -v '^exit=' <lane>/.ufo/waves/round-50/census/start.out | sed 's/^kama\t/file\t/') census-file-freeze.out
95c95 < file ok /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
      > file ok /fast/scratch/hyaku/kama-r50/X6Sao2/treef/corpus/SOURCES.md     (path label only)
$ diff <(cat start.out) census-root-kama.out
95,96c95,97  (3 E11 rows added; exit line dropped because exit was echoed separately)
```

W04 set identity between start.out and the build census: `comm -3` produced 0 lines.
W01 line identity: md5 `c193b779771caccf1d83b6433cc41fcf` on both.

## 4. SOURCES append-only guard at the build

```
$ python3 tools/sources-append-only.py --from 26ecba64ad6fb571d09074b07202d1618a46ecd1 --to 26ecba64ad6fb571d09074b07202d1618a46ecd1 --repo $S/lane
no append-only violations                                    exit=0
$ python3 tools/sources-append-only.py --from 26ecba64ad6fb571d09074b07202d1618a46ecd1 --to 601c8889 --repo $S/lane
no append-only violations                                    exit=0
$ python3 tools/sources-append-only.py --from 26ecba64ad6fb571d09074b07202d1618a46ecd1 --to 97c864bead3ee4a2f629574e77263d33834ec98a --repo $S/lane --json
{"error": "97c864bead3ee4a2f629574e77263d33834ec98a:corpus/SOURCES.md:251: unterminated table row (no closing pipe)", "violations": null}
exit=2
$ python3 tools/sources-append-only.py --from 26ecba64ad6fb571d09074b07202d1618a46ecd1 --to 3d42897b --repo $S/lane --json
{"violations": [], "added": ["S496","S497","S498"], "ok": true}   exit=0
$ python3 tools/sources-append-only.py --from 26ecba64ad6fb571d09074b07202d1618a46ecd1 --to 3b79eadd --repo $S/lane --json
{"violations": [], "added": ["S496","S497","S498"], "ok": true}   exit=0
```
Tool blob is `f269ef0d5dfa…` at 26ecba6, 601c8889, 97c864b, 3d42897b, 3b79eadd (unchanged).

## 5. Independent append-only property check (tolerant parse, scratch script)

```
base rows 236  build rows 239
removed: []   added: ['S496','S497','S498']
(no IMMUTABLE CHANGE lines; no mutable-cell change lines)
odd backtick counts at build: S498 line 251 ticks 7
odd backtick counts at base: (none)
```

## 6. Proposed parser fix (scratch copy only; lane file untouched)

```
$ cp <97c864b tools/sources-append-only.py> $S/prop/sources-append-only-patched.py   # then edited
$ python3 $S/prop/sources-append-only-patched.py --selftest
45/45 selftest cases passed                                   exit=0
$ python3 $S/prop/sources-append-only-patched.py --from 26ecba64ad6fb571d09074b07202d1618a46ecd1 \
    --to 97c864bead3ee4a2f629574e77263d33834ec98a --repo $S/lane --json
{"violations": [], "added": ["S496","S497","S498"], "ok": true}   exit=0
$ ... --to 3d42897b --repo $S/lane      -> exit=0, no violations
$ ... --from base --to base             -> exit=0, no violations
```
Diff: `proposed-sources-append-only-code-span.diff`.

## 7. Build battery cross-check

```
$ git -C lane show 3b79eadd:.ufo/waves/round-50/measured/sao-build.out
$ python3 tools/sources-append-only.py --from 26ecba64ad6fb571d09074b07202d1618a46ecd1 --to 97c864bead3ee4a2f629574e77263d33834ec98a (tip=97c864be…)
error: 97c864bead3ee4a2f629574e77263d33834ec98a:corpus/SOURCES.md:251: unterminated table row (no closing pipe)
exit=2
```
No post-fix `sao` receipt exists: `measured/` at 3b79eadd holds only `*-build.out`.
No tool installs or upgrades were needed.
