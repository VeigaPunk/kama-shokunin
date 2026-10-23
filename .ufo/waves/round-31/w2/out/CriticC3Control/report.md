```RESULTS
Direct process commands; stdout/stderr tails below are the complete captured streams.

00-mkdir
cwd: /home/vgpnk/Projects/shokunin
$ mkdir -p /tmp/kama-r31w2/CriticC3Control
exit: 0
stdout tail: (empty)
stderr tail: (empty)

01-clone
cwd: /home/vgpnk/Projects/shokunin
$ git clone --no-local /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r31w2/CriticC3Control/lane
exit: 0
stdout tail: (empty)
stderr tail (verbatim):
Cloning into '/tmp/kama-r31w2/CriticC3Control/lane'...

02-tip
cwd: /tmp/kama-r31w2/CriticC3Control/lane
$ git -C /tmp/kama-r31w2/CriticC3Control/lane rev-parse HEAD
exit: 0
stdout tail (verbatim):
bda324bbc5c1d7db93553adb13c5f380492c3c93
stderr tail: (empty)

03-file-digests
cwd: /tmp/kama-r31w2/CriticC3Control/lane
$ sha256sum tools/gate-registry-check.py .ufo/waves/round-29/count-c1.py SKILL.md
exit: 0
stdout tail (verbatim):
28500af9024aaa328d65cf715b5dd031cd53f065976f85d0fb133296a9aead4e  tools/gate-registry-check.py
fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383  .ufo/waves/round-29/count-c1.py
f67e30b28ce6b4f8b18555e0f4d8370da434f2b19605b5bdd0f693a8564c06eb  SKILL.md
stderr tail: (empty)

04-gate-unmodified
cwd: /tmp/kama-r31w2/CriticC3Control/lane
$ python3 tools/gate-registry-check.py
exit: 1
stdout tail (verbatim):
unregistered .ufo/waves/round-29/count-c1.py
registered 8 unregistered 1
stderr tail: (empty)

05-freeze-input-diff
cwd: /tmp/kama-r31w2/CriticC3Control/lane
$ git -C /tmp/kama-r31w2/CriticC3Control/lane diff --exit-code 382d11b2107d335705875da1a4d889b074bd6fa6 HEAD -- tools/gate-registry-check.py SKILL.md ':(glob).ufo/waves/round-*/count-*.py'
exit: 0
stdout tail: (empty)
stderr tail: (empty)

06-gate-bogus-row
cwd: /tmp/kama-r31w2/CriticC3Control/lane
$ python3 tools/gate-registry-check.py
exit: 0
stdout tail (verbatim):
registered 9 unregistered 0
stderr tail: (empty)

07-gate-correct-row
cwd: /tmp/kama-r31w2/CriticC3Control/lane
$ python3 tools/gate-registry-check.py
exit: 0
stdout tail (verbatim):
registered 9 unregistered 0
stderr tail: (empty)
```

FINDING: The target is not discriminative: a registry row with an empty exit map passes exactly like a correct row. The shortcut is **path-token registration** (occurrence-only coverage), not literal no-edit success.

LIMITS: The unchanged clone fails (exit 1); doing absolutely nothing does not reach the target. These are working-tree gate runs, not committed `--rev` runs. I did not run the round-29 counter, create/validate its round-31 receipt, evaluate the full conjunctive C3 predicate, or invoke the canonical judge. The report is advisory, not admission or rejection. No live server was started and no tool was installed or updated.

## Axes and counterexample

- **Operability:** the gate cannot distinguish a usable exit contract from a blank exit-map cell.
- **Calibration:** `unregistered 0` demonstrates path coverage only, not the claimed completeness/accuracy of registry documentation.

| Clone state | Exit | Complete stdout |
|---|---:|---|
| Fresh, unmodified | 1 | `unregistered .ufo/waves/round-29/count-c1.py` then `registered 8 unregistered 1` |
| Base + bogus row, empty exit map | 0 | `registered 9 unregistered 0` |
| Base + correct row | 0 | `registered 9 unregistered 0` |

The bogus row was appended at `SKILL.md:1292`. It includes the real entry command and the independently re-derived full counter SHA-256; only its Exit map cell is empty. For the correct arm I replaced that appended row, filling the Exit map cell without changing any other cell. Thus the correct arm does not retain a second, already-sufficient bogus occurrence. Exact fixtures: `bogus-row.txt` and `correct-row.txt` alongside this report.

## Evidence and provenance

- Fresh clone: `/tmp/kama-r31w2/CriticC3Control/lane`, cloned from the lane without local hardlinks. Its observed HEAD is `bda324bbc5c1d7db93553adb13c5f380492c3c93`, later than the dispatch pin `382d11b2107d335705875da1a4d889b074bd6fa6`. The recorded pre-mutation `git diff --exit-code` is empty and exits 0 for SKILL.md, the gate, and every tracked counter-pattern path; those tested inputs therefore match the frozen dispatch inputs.
- Gate SHA-256: `28500af9024aaa328d65cf715b5dd031cd53f065976f85d0fb133296a9aead4e`.
- Round-29 counter SHA-256: `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383`.
- `tools/gate-registry-check.py:12-15,29-34,124-128`: registration is substring occurrence anywhere in SKILL.md; no row parsing or column validation occurs. The source was read end to end.
- `.ufo/waves/round-31/preregistration-c3.json:15`: the full frozen predicate additionally requires the counter SHA-256 in the row and a round-31 counter receipt. It does **not** require any exit-map content. Lines 21-23 explicitly acknowledge the wrong-map limitation.
- `.ufo/waves/round-29/count-c1.py:42-46,282-288,346-364`: source-backed normal exit contract is 0 when evaluation ran (even if `met` is false), 2 when evaluation cannot run or an existing output is refused. The correct row documents this; it does not claim the counter was executed here.
- No wave-1 seat artifact was named by this item, so none was read. The frozen preregistrations were read in the requested order, followed by the inherited round lesson.

## Smallest safe correction

For this empty-cell counterexample, add a condition that the named path occurs in an actual instrument-registry row whose Exit map cell is nonempty. To discriminate a **correct** map from an arbitrary nonempty bogus map, require that cell to state the source-backed mapping: `0 = evaluation ran, independent of met; 2 = could not evaluate / existing output refused`. Scope the check to this named row; no new abstraction or wider registry rewrite is necessary.

Neither nonempty-cell checking nor exit-map correctness is in the frozen predicate. Its SHA-256 and receipt conjuncts are independent of the exit-map cell: [INFERENCE] preserving genuine SHA/receipt evidence while blanking that cell would not violate either conjunct. This experiment does not supply that full-predicate committed-tree witness.

This is a fixable prospective discriminator defect **if** the claim is operationally complete registry documentation. If the intended claim is only occurrence coverage, it is an explicitly declared tradeoff, and the coarse target cannot be reported as instrument quality. Do not amend the frozen predicate after these data; any stronger condition needs a new freeze. Canonical judgment remains outside this seat.

## Receipts and write boundary

`00-mkdir` through `07-gate-correct-row` each have `.stdout.log`, `.stderr.log`, and `.receipt.json`; `commands.json` aggregates the direct command records. Read/edit/write tool calls are not process commands. Only the isolated clone's SKILL.md and this seat's allowed output directory were written; no lane tracked file or lane git state was edited.

The alternate requested `.ufo/waves/round-31/w2/out/CriticC3Control.md` lies outside the seat-only write boundary and was not written. The report is at the explicitly requested, permitted seat-directory path below.

Report: .ufo/waves/round-31/w2/out/CriticC3Control/report.md
