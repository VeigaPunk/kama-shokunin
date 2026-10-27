# T2Skill — round-50 SKILL.md instrument rows and the isolated-replay how-to

**Verdict: rows drafted and demonstrated — with the five round-50 rows applied to a scratch clone at the build commit, `python3 tools/gate-registry-check.py` reports `registered 46 unregistered 0 defective 0` (exit 0), and the gate's own selftest is 6/6 including its lane-tip arm. No defect found in the five instruments' docstring-to-behavior mapping that the rows assert.**

Seat: T2Skill (leaf). Build commit measured: `97c864bead3ee4a2f629574e77263d33834ec98a`. Clone: `git clone --shared` of the lane, checked out at that commit, scratch `/fast/scratch/hyaku/kama-r50/T2Skill` (removed before finishing). Nothing in the lane, the fleet repo or shokuknow was written; the lane's jj state and index were never touched.

## Deliverable

- `.ufo/waves/round-50/w1/out/T2Skill/skill.md` — the `## Round-50 instrument registry` section (five rows: the two counters, `tools/append-only-audit.py` v5 definitions, `tools/kama-llamacpp-live.py` model mapping, `tools/kama-live-replay.py` isolation) plus `### Re-running live evidence (isolated replay, round 50)`. It is written as text to append to `SKILL.md`; it is not applied to the lane (integration item, L1).
- `.ufo/waves/round-50/w1/out/T2Skill/c1.out`, `c2.out` — the two counters' receipt files from this seat's runs at `97c864be`.

## Evidence

### 1. Baseline: the two round-50 counters are unregistered at the build commit

```
$ cd /fast/scratch/hyaku/kama-r50/T2Skill/lane            # git clone --shared, HEAD = 97c864be…
$ python3 tools/gate-registry-check.py --repo $PWD --rev 97c864bead3ee4a2f629574e77263d33834ec98a
unregistered tools/round50-append-audit-v5-check.py
unregistered tools/round50-replay-bind-audit.py
registered 44 unregistered 2 defective 0
EXIT=1
```

Population at that tree: 46 tracked counters (`tools/round[0-9]+-*.py` plus `.ufo/waves/round-*/count-*.py`), `tools/gate-registry-check.py:60-63`.

### 2. With the five rows applied

Working-tree mode (rows in the filesystem `SKILL.md`, counters from `git ls-files`):

```
$ cat .ufo/waves/round-50/w1/out/T2Skill/skill.md >> $CLONE/SKILL.md
$ python3 tools/gate-registry-check.py --repo $CLONE
registered 46 unregistered 0 defective 0
EXIT=0
```

Committed mode on the clone (commit `aee9ba9c02d3bc5ea910937ef4040de491a26877`, `SKILL.md | 21 +++++++++++++++++++++`, one file changed):

```
$ python3 tools/gate-registry-check.py --repo $CLONE --rev aee9ba9c02d3bc5ea910937ef4040de491a26877
registered 46 unregistered 0 defective 0
EXIT=0
```

Gate selftest (includes arm 6, this clone's `master` now at `aee9ba9c02d3`):

```
$ python3 tools/gate-registry-check.py --selftest
PASS valid-row: exit=0 (want 0) line='registered 1 unregistered 0 defective 0' …
PASS thin-row: exit=1 (want 1) line='registered 1 unregistered 0 defective 3' want-line='defective .ufo/waves/round-98/count-selftest.py: thin-row'
PASS empty-exit-map: exit=1 (want 1) …
PASS missing-path: exit=1 (want 1) line='… defective .ufo/waves/round-98/count-selftest.py: missing-path:.ufo/waves/round-999/count-c999.py'
PASS prose-only: exit=1 (want 1) line='unregistered .ufo/waves/round-98/count-selftest.py'
PASS lane-tip aee9ba9c02d3: exit=0 line='registered 46 unregistered 0 defective 0'
GATE_SELFTEST pass=6 fail=0
SELFTEST_EXIT=0
```

### 3. Negative control: the zero is carried by the rows

```
$ grep -v '^| Round-50 C1 replay-bind audit ' SKILL.md > SKILL.noC1 && cp SKILL.noC1 SKILL.md
$ python3 tools/gate-registry-check.py --repo $CLONE
unregistered tools/round50-replay-bind-audit.py
registered 45 unregistered 1 defective 0
EXIT=1
$ cp SKILL.full SKILL.md && python3 tools/gate-registry-check.py --repo $CLONE
registered 46 unregistered 0 defective 0
RESTORED_EXIT=0
```

So the pass line is fail-capable per row, not a property of the tree state.

### 4. What each row must carry, and where it comes from

The gate grades five things per row (`tools/gate-registry-check.py:246-284`): at least two non-empty cells, a non-empty entry cell, a non-empty exit-map cell, and that every repo-relative path token in the entry / self-test / write-scope cells exists at the evaluated revision. Every row in `skill.md` satisfies these at `97c864be`; tokens cited and confirmed present there: `tools/kama-live-replay.py`, `tools/kama-llamacpp-live.py`, `tools/append-only-audit.py`, `registry/append-only-contract.tsv`, `corpus/SOURCES.md`, `.ufo/waves/round-48/c2/live/receipt-1.json`, `.ufo/waves/round-50/preregistration.json`, `.ufo/waves/round-50/controls/base.c1.out`, `.ufo/waves/round-50/controls/base.c2.out`. `corpus/lessons/round-50.md` is deliberately **not** cited: it does not exist at `97c864be` (it lands at integration) and would be a `missing-path` defect.

Entry commands were checked against each tool's `--help`:

- `tools/round50-replay-bind-audit.py --help` → `[--repo REPO] [--tip TIP] [--scratch SCRATCH] [--out OUT]`, `--repo`/`--tip` required.
- `tools/round50-append-audit-v5-check.py --help` → same four.
- `tools/kama-llamacpp-live.py --help` → includes `--server-asset-url/--server-asset-sha256/--server-member/--model-url/--server-archive/--witness-dir/--witness-timeout/--selftest`.
- `tools/kama-live-replay.py --help` → includes `--receipt/--work/--out/--live/--timeout/--compare A B/--selftest/--scratch/--witness-dir/--witness-timeout`.
- `tools/append-only-audit.py --help` → `[--repo REPO] [--to TO] [--threshold N] [--contract CONTRACT] [--files FILES] [--json] [--selftest] [--scratch SCRATCH]`.

### 5. Measurements behind the "Self-test / pinned values" cells

**C1** — `python3 tools/round50-replay-bind-audit.py --repo $CLONE --tip 97c864be… --scratch $S/c1scratch --out $S/c1.out`, exit 0, 17.5 s wall (user 53.8 s):

```
tip=97c864bead3ee4a2f629574e77263d33834ec98a
bind=1 teardown=1 newrow=1 bound=3/3 met=True
detail: counter vocabulary: 512 tokens from its own download
detail: bind b1: pid 2329743 port 46875 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 1353318236 recorded, nonce 'kama witness d04c07dad714c01d' round-tripped
detail: bind b2: pid 2347008 port 41403 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 1754039853 recorded, nonce 'kama witness c568f69e71ea1c21' round-tripped
detail: bind b3: pid 2366915 port 38533 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 1418593040 recorded, nonce 'kama witness d6d94f463c3116da' round-tripped
detail: teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok
detail: newrow: 3 rows new since base; 1 name proc_pid_maps(5): ['| S496 |']
```

**C2** — `python3 tools/round50-append-audit-v5-check.py --repo $CLONE --tip 97c864be… --scratch $S/c2scratch --out $S/c2.out`, exit 0, 15.0 s wall:

```
tip=97c864bead3ee4a2f629574e77263d33834ec98a
fixture=1 lane=1 scenarios=12/12 met=True
detail: scenario launder: ok exit 1 … {'deleted': 25, 'graded': 25, 'ungraded': 0, 'status': 'unrestored'}
detail: scenario native-head: ok exit 0 … {'deleted': 25, 'graded': 0, 'ungraded': 25, 'status': 'ungraded'}
detail: scenario dated-loss: ok exit 1 … {'deleted': 25, 'graded': 25, 'status': 'unrestored'}
detail: scenario substring: ok exit 1 … bad_declarations 1
detail: scenario word-token: ok exit 0 … bad_declarations 0
detail: scenario negated: ok exit 1 … bad_declarations 1
detail: scenario wildcard-self: ok exit 1 … bad_declarations 1
detail: scenario wildcard-named: ok exit 0 … bad_declarations 0
detail: scenario order-a: ok exit 0 … {'deleted': 25, 'graded': 0, 'ungraded': 25, 'status': 'ungraded'}
detail: scenario order-b: ok exit 0 … {'deleted': 25, 'graded': 0, 'ungraded': 25, 'status': 'ungraded'}
detail: scenario fence: ok exit 1 … {'deleted': 25, 'graded': 25, 'ungraded': 0, 'status': 'unrestored'}
detail: scenario crlf-launder: ok exit 1 … {'deleted': 25, 'graded': 25, 'ungraded': 0, 'status': 'unrestored'}
detail: lane: tool exit 0 events 5 bad_declarations 0 regressed 0 ungraded_lines 89
detail: lane: event dd9f5dc6c0e6 SCORECARD.md ungraded 17 <= v5 natively exempt 23
detail: lane: event 0718b6abbda6 SCORECARD.md ungraded 72 <= v5 natively exempt 72
```

The two counters therefore meet at `97c864be` on this host, independently of the L1 dry run.

**Tool selftests** (all in the same clone):

```
$ python3 tools/append-only-audit.py --selftest --scratch $S/st1
… 36 `pass` lines …
AOA_SELFTEST pass=36 fail=0                                # exit 0
$ python3 tools/kama-llamacpp-live.py --selftest
selftest: ok; closed tcp6 listeners ::1:42567, ::ffff:127.0.0.1:46001   # exit 0
$ python3 tools/kama-live-replay.py --selftest --scratch $S/st2
… 23 `pass` lines (match … witness-passthrough, compare-instance-only, compare-stable-differs) …
KLR_SELFTEST pass=23 fail=0                               # exit 0
```

### 6. Row content traced to the code it describes

- `tools/kama-live-replay.py:46-53` states the round-50 isolation, env allow-list and `model_mapping` rule; `:88` `LIVE_ENV_KEYS = ("PATH", "HOME", "LANG", "LC_ALL")`; `:113-116` `live_env()` adds `TMPDIR` under `--work`; `:100-109` `set_own_pdeathsig()`; `:314-332` the child's `PR_SET_PDEATHSIG` SIGTERM + post-prctl `getppid()` re-check and argv `[sys.executable, "-I", live, …]`; `:343-348` `model-mapping:<reason>` / `model-mapping:sha256:<want>-><got>` mismatches; `:587` the replay sets the signal on itself at start.
- `tools/kama-llamacpp-live.py:123-125` `CHILD_ENV_KEYS`; `:661-672` `_preexec_pdeathsig` (SIGKILL); `:678-727` `model_mapping(pid, model_path)` — maps read, `O_NOFOLLOW` re-open, `fstat` dev/inode equality, regular-file and size bound, sha256; receipt written at `:2000-2005` (`server-not-running` when the child is gone), and the field is recorded, not added to `checks` (so v1-v5 check ids are unchanged).
- `tools/append-only-audit.py:1-28` v5 definition block; `:276-280` origin key drops one trailing CR; `:282-306` CommonMark 0.31.2 §4.5 open/close; `:308-320` fence-aware sections; `:472-509` origins over births; `:573` `"schema": "append-only-audit/v3", "definition": "v5"`.
- Source rows verified at `97c864be:corpus/SOURCES.md:249-251` (S496 maps, S497 pdeathsig, S498 CommonMark §4.5) — the C1 row's parenthetical "(S496; S497 is the mechanism row)" holds; the counter's own `newrow` detail names only S496, which is the maps URL row it pins.

## Findings

1. **No gate-relevant defect in the five instruments.** Every claim the rows assert (flags, exit maps, receipt field names, refusal tokens, selftest pass lines) matched the tools' `--help`, docstrings and observed output at `97c864be`. Nothing to patch.
2. **Timing differs from the L1 dry run — recorded, not a defect.** C1: 17.5 s here vs 46 s in the dry run; C2: 15.0 s here vs 5 s. Both rows state this seat's own values and name the L1's beside them, so a reader is not misled about either. The how-to section's "17.5 s on this host" should be treated as a host-local figure.
3. **The zero is per-row fail-capable** (control in §3): removing the C1 row alone flips the gate to `unregistered 1`, exit 1.
4. **Integration note measured, not a re-report** (known item): at the current lane tip `3b79eaddf38246c637cc7ba1a94ab363422876b6`, `python3 tools/gate-registry-check.py --repo $CLONE --rev 3b79eadd…` still prints `unregistered tools/round50-append-audit-v5-check.py`, `unregistered tools/round50-replay-bind-audit.py`, `registered 44 unregistered 2 defective 0`, exit 1 — appending `skill.md` verbatim to `SKILL.md` is what clears it (demonstrated above at `aee9ba9c`). The section is self-contained and appends after the round-49 section without touching frozen rows.

## Out of scope / not done

- `SKILL.md` was not edited in the lane (leaf seat; the rows ship as text). The L1 lands them.
- The gate's `--rev` mode was exercised only on the clone commits (`97c864be`, `aee9ba9c`, `3b79eadd`); no lane ref was created or moved.
- C2's lane-leg binder limitation (the counter's own binder is still the v4 rule) and C1's scratch filesystem assumption are preregistration limits, not restated here.

## Artifact paths

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/T2Skill/skill.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/T2Skill/c1.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/T2Skill/c2.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/T2Skill.md`

Scratch `/fast/scratch/hyaku/kama-r50/T2Skill` (clone, selftest dirs, sanity copies) was removed after these receipts were copied out. No llama-server this seat started survived: `pgrep -fa llama-server` shows only peers' processes (paths under `J2NoPdeathsig/`, `Sen3Teardown/`), none under `T2Skill/`. No tools were installed or upgraded.
