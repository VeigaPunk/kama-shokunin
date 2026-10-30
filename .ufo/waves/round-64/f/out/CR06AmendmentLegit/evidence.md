# CR06AmendmentLegit — evidence log (round 64, wave f, kama)

Seat: CR06AmendmentLegit (leaf critic, process review; no subagent dispatch).
Scope: freeze.txt AMENDMENT 1/1a/1b and the wave-b reports that motivated them.
Read-only on the lane; all code runs in my own scratch clone.

## Tooling

No installs or upgrades. Host pacman not touched. Used: python3 3.14 (stdlib only), git,
sha256sum, diff. Nothing to record on the tooling channel.

## Clone

```
S=/fast/scratch/hyaku/kama-r64/f/CR06AmendmentLegit; D=$S/clone
git clone -q --shared /home/vgpnk/Projects/shokunin/kama-shokunin $D
git -C $D rev-parse --show-toplevel) = $D        # asserted
git -C $D checkout -q 23b3fdb1a925129a9961cf551f6d40bf251602cb
```

## E1 — tool bytes identical between freeze and tip (assignment's hard requirement)

```
git diff --stat f6a4ea9a 23b3fdb1a -- tools/kama-completion-live.py   -> (empty)
git diff f6a4ea9a 23b3fdb1a -- tools/kama-completion-live.py | wc -l  -> 0
sha256 of tools/kama-completion-live.py:
  f6a4ea9a  a0c26e14184d664bef75013aac6f1c2a7bb47881eb4bf372b5bb70a26861423c
  23b3fdb1a a0c26e14184d664bef75013aac6f1c2a7bb47881eb4bf372b5bb70a26861423c
  (base 0c1eff3 is a different file: e24bc9447e19b0a78777f213c2032698a384f3f976811e9e7fa876a49195c8f6)
```

PASS: the tool is byte-identical across the amendment window. The amendment is
instrument-only on the tool side, exactly as claimed.

## E2 — amendment scope: which files changed in the amendment window

```
git diff --name-status f6a4ea9a 23b3fdb1a -- . ':(exclude).ufo/waves/round-64/b' ':(exclude).ufo/waves/round-64/b/*'
A  .ufo/waves/round-64/controls/c1-mutants-a1.txt
M  .ufo/waves/round-64/controls/freeze.txt
A  .ufo/waves/round-64/controls/run-c1-mutants-a1.sh
A  .ufo/waves/round-64/gen-b.py
A  .ufo/waves/round-64/gen-f.py
M  SCORECARD.md
A  registry/capability-claims-r64.tsv
A  registry/capability-regress-r64.tsv
M  registry/hexrun-ledger.tsv
M  tools/round42-selfdesc-reconcile.py
M  tools/round64-c1-counter.py     <- the C1 instrument
A  tools/round64-c2-counter.py
M  tools/shortcut-tally.py
```

The C1 amendment itself is confined to `tools/round64-c1-counter.py`
(668 insertions / 319 deletions). The C2-side files are the C2 build the freeze
already discloses separately ("C2 build disclosure"). `tools/kama-completion-live.py`
does not appear: unchanged.

## E3 — traceability of each amended element to a named wave-b finding

Each element named in freeze.txt AMENDMENT 1 "What changed" was located in the tip
counter and matched to the finding that motivated it:

| amended element | code location (tip) | motivating finding |
|---|---|---|
| counter draws the tool's own request, passes `--prompt/--n-predict/--seed` | 1819-1820, 1022-1024 | RV02 D1, MT13 §3 |
| `receipt_req` / `receipt_ref_text` / `receipt_ref_usage` | 807-826, `RECEIPT_BIND` 88 | RV02 D1, MT13 §3 |
| exact argv list | `expected_argv` 553-557, `argv_ok` 491-496 | RV02 D2, MT04, MT10 F2 |
| environ allowlist PATH/HOME/LANG/LC_ALL | `TOOL_CHILD_ENV` 162, `env_ok` 499-503 | RV02 D2, MT05 F3 |
| `bind_ns` (mnt/pid/net/user/ipc/uts) | `ns_of` 379-386, `bind_ns` 509-511 | MT05 F1/F8 |
| `bind_trace` (TracerPid 0) | 512-513 | MT05 F6 |
| `bind_state` (S/R/D) | 514-515 | MT03 (c) |
| unreadable fd tables of ANY uid, graded if started after the tool | `holder_pids` 267-316, `unreadable_own` 452-455 | RV02 D6 |
| hold.json mtime upper bound | `hold_fresh` 543-549 | RV02 D8 |
| unreadable `pid_gone` fails closed | `pid_gone` 975-986 | RV02 D12 (PARTIAL - see E5) |
| holders + tool process group killed on exit | 1092-1105 | RV02 D5 |
| non-empty `--work` exits 2 | 1788-1795 | RV02 D11 |
| three distinct non-empty reference answers | 1819-1828 | X08 |
| structural forge/relabel builders | `splice_before_main` 1345, `FORGE_CLAIM` 1357, `RELABEL_WRAP` 1374 | CR03 K1-K3 |
| patch dry-run without fuzz; missing patch is an error | `apply_patch` 1334-1341, `forge_variants` 1394-1399 | RV02 D10 |
| evaluator self-test 3 -> 8 planted cases | `eval_selftest_run` 1894-1927, `EXPECT_EVAL_SELFTEST = 8` | RV02 D4, MT11 |
| `bind_ref_files` (path/device/inode vs the counter's reference server) | 373-376, 835-840 | MT06 (AMENDMENT 1a) |
| fresh (uncached) model digest | `sha256_path` 180-191, `cache=False` default | MT06 a2/b2, RV02 D9 |
| holder_pids re-read 4 x 50 ms | `retries=4`, 296-305 | AMENDMENT 1b (1) |
| `bind_ancestry` control pid 999999999 | 1654 | AMENDMENT 1b (2) |
| replay redraws until the answer differs | 2003-2017 | AMENDMENT 1b (3) |

Every element maps to a named wave-b finding. No element is present without a
finding behind it (no unmotivated hardening).

## E4 — control totals

```
EXPECT_FAMILIES (tip) sum = 91  [bind=30, receiptbind=4, replay=1, ...]
EXPECT_EVAL_SELFTEST (tip) = 8
EXPECT_FAMILIES (freeze f6a4ea9a) sum = 76
```

## E5 — the `pid_gone` fail-closed claim is only partly true (safe injection)

freeze.txt AMENDMENT 1 claims "unreadable pid_gone fails closed". The tip code:

```
def pid_gone(pid, ticks):
    pp, tk = stat_fields(pid)
    if pp is None: return True      # <-- stat read failed => "gone"
```

`stat_fields` returns `(None, None)` for ANY OSError/parse failure, including a
PermissionError on an unreadable `/proc/<pid>/stat` - indistinguishable from a
vanished pid. So an *unreadable* holder is graded as gone, not as "not observed
gone".

Safe fault injection (imported the counter module; no process, port or signal
touched):

```
stat_fields -> (None,None);  pid_gone(999999, 123) = True     # fail-OPEN
stat_fields -> (None,None);  pid_gone(999999, None) = True
```

The docstring's own claim ("Unknown start ticks fail closed: not gone") is only
true for the `ticks is None` branch, not for the unreadable-stat branch. The
port-closed observation backstops the teardown conjunct, so this does not by
itself flip `met`; it is a disclosed-claim inaccuracy, not a live forgery.
Cross-check: RV08's D12 disposition reached the same conclusion by a different
route ("D12 not fully fixed: the first stat read still conflates unreadable and
gone"), which is independent corroboration.

## E6 — the freeze's AMENDED C1 SENTENCE disagrees with the counter docstring in the control count

freeze.txt AMENDMENT 1 quotes the amended sentence with "all 89 targeted controls"
and "(EXPECT_FAMILIES, sum 89)" (freeze lines 156 and 159). AMENDMENT 1a (line
192) then says: "the control total is 91, not 89 (the amended sentence above reads
'91 targeted controls', EXPECT_FAMILIES sums to 91)".

The parenthetical is false as written: the amended sentence above still reads 89.
Machine diff of the freeze's quoted sentence against the counter's docstring
predicate, whitespace-normalised:

```
delete '... ' -> ''
insert '' -> ' '
delete '8' -> ''
insert '' -> '1'
delete ' (EXPECT_FAMILIES, sum 89)' -> ''
```

i.e. the only substantive difference is 89 vs 91. The counter's docstring says
91 (and `EXPECT_FAMILIES` sums to 91); the freeze's quoted sentence says 89.
AMENDMENT 1a asserts the quoted sentence reads 91; it does not.

Commit-level trace of the sentence: it has read "89" at every commit since
bf0db9e3 (AMENDMENT 1) through HEAD. It was never updated to 91.

## E7 — the amendment's own disclosure order (instrument vs. its written record)

```
bf0db9e3  20:59:57  AMENDMENT 1: counter hardened to 91 controls; freeze text says 89
f39ccec9  22:04:54  AMENDMENT 1a: adds bind_ref_files disclosure; sentence still says 89
23b3fdb1a 22:08:08  AMENDMENT 1b: counter fixes (unreadable re-read, ancestry pid, replay draw)
7252c7c9  22:12:41  AMENDMENT 1b freeze text + pre-wave-f receipts + wave f spec
```

`git show 23b3fdb1a:.ufo/waves/round-64/controls/freeze.txt | grep -c "AMENDMENT 1b"`
= 0. So at the tip this wave scores (23b3fdb1a), the counter carries the 1b fixes
but the frozen record at that commit does not yet describe them. They land four
minutes later, at 7252c7c9, together with the wave-f spec. The 1b fixes are
disclosed before any wave-f seat dispatched and before the measured-tip scoring
(the freeze's own ordering condition), so this is disclosure completeness, not
a rule change after scoring.

## E8 — the amendment's disclosure is accurate about what the counter now accepts

Reproduced CR03DoNothing's candidates against the tip counter (unmutated tip
counter, each candidate committed in my own clone, fresh `--work` per run):

```
K1c (996c43f8) tool_present=1 live_ok=1/1 controls_targeted=91/91 of 91 families_exact=1
     missing_families=[] eval_selftest=8/8 errors=0 met=True
K2  (c97e2c9b) tool_present=1 live_ok=1/1 controls_targeted=91/91 of 91 families_exact=1
     missing_families=[] eval_selftest=8/8 errors=0 met=True
K3  (66539b0f) tool_present=1 live_ok=1/1 controls_targeted=91/91 of 91 families_exact=1
     missing_families=[] eval_selftest=8/8 errors=0 met=True
```

The amendment's honest-disclosure paragraph says exactly this: K1c/K2/K3 are
accepted with met=True because the held child really is the pinned server.
Confirmed, not just asserted.

The kill-rule narrowing is therefore not a cover: the amendment replaces
"a v2-schema or schema-relabelled tool accepted" (which the counter cannot
discriminate - the tool's own bookkeeping is ungraded) with "a tool whose
receipt omits the holder bookkeeping accepted" (which the counter does
discriminate: `bind_claim` / `listener_holders_pinned` / `inconsistent:missing-checks`
all fail for a receipt without the holder block - see the base receipt
`controls/c1-base-final-counter.txt`: `error: live: ["bind_claim",
"inconsistent:missing-checks", "listener_holders_pinned", "schema"]`).

## E9 — baseline runs of the tip counter

```
python3 tools/round64-c1-counter.py --repo <clone> --tip 23b3fdb1a --work <fresh>
tool_present=1 live_ok=1/1 controls_targeted=91/91 of 91 families_exact=1 missing_families=[]
eval_selftest=8/8 errors=0 met=True families[bind=30/30 canned=1/1 detach=1/1 digest=1/1
forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1
predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 receiptbind=4/4 relabel=1/1 replay=1/1
reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2
tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]
exit=0
```

One run, no flake (77 s). Matches the committed receipt
`controls/c1-final-prewave-runs.txt` exactly.

## E10 — counter has no tool-byte pin of its own

`grep -n "TOOL_SHA|tool_sha|tool_digest|tool_bytes_sha" tools/round64-c1-counter.py`
-> no matches. The counter reads the tool blob from the tip and runs it; it does
not compare that blob against a digest of the freeze commit's tool. The
"byte-pinned" wording in the C1 sentence is therefore a property of the *lane
tip* (established by the freeze's own tool-identity check and by E1), not
something the counter grades. This is consistent with the amendment's disclosure
and with the accepted K1c/K2/K3: the counter verifies the *process*, not the
tool's provenance.
