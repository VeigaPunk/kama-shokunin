## Criteria added — round 51 (each cites `corpus/lessons/round-51.md`)

No earlier row is superseded. KQ85 narrows KQ80's exe-digest leg (KQ76's outside
observation and KQ81's mapped model stand unchanged). KQ86 qualifies KQ84's
accounting equation by adding the `permitted` bucket that KQ87 defines, and
narrows KQ67's audit invocation to the default threshold; KQ84 and KQ67
otherwise stand. KQ88 turns KQ67's "explained in the lesson" for a lost line
into a mechanical disclosure binding. Line pointers name build
`138af25b963450b6520794995605fa7dbbcd87e0`; read them as
`git show 138af25b:<path>`.

| ID | Admit only when | Reject or limit when | Motivating lesson |
|---|---|---|---|
| KQ85 (narrows KQ80) | A replay's server is **its own** only when an observer opens the running child's image through `/proc/<pid>/exe` and `fstat()`s that open descriptor (proc_pid_exe(5): "attempting to open it will open the executable") — never the `readlink(2)` text and never a path re-stat — and the opened image's `(dev, inode)` equals the replay's own extracted `<work>/server/<member>` while its bytes hash to the receipt's server sha256; the rerun receipt records that opened image as `server_exe` with the same dev, inode and digest, the replay's result records the member as `own_server`, and every round-50 bind and teardown leg still holds. `Check:` `python3 tools/round51-replay-exe-audit.py --repo <clone> --tip <tip> --scratch <dir>` prints `bind=1 own=1 teardown=1 newrow=1 bound=3/3 owned=3/3 met=True`, exit 0 (build `138af25b`, three b11909 receipts; the counter's `own` leg opens that link itself; live tool `tools/kama-llamacpp-live.py:730-766` opens the link and fstats the fd, records at `:2041`; replay compares at `tools/kama-live-replay.py:359-365`). The committed base control `controls/base.c1.out` prints `bind=1 own=0 teardown=1 newrow=0 bound=3/3 owned=0/3 met=False`, exit 1. | An exe **sha256 alone** — a byte-identical install exec'd from another file (round-50 seat J4Decoy's host b11909 exec) — the `readlink` path, argv, or a later stat of that path is offered as the running file; a rerun receipt without `server_exe`, or with another dev or inode, is admitted. Limit: this identifies the whole executable file and cannot tell bytes rewritten in place after it was mapped/executed (carried limit). | `corpus/lessons/round-51.md` Claims C1, Gate reject 1, Mistakes #4; round-50 closure `corpus/lessons/round-50-verifier-spotcheck.md` R6 C1 (J4Decoy). |
| KQ86 (qualifies KQ84's equation; narrows KQ67's invocation) | An append-only audit's evidence run grades **every deletion** in the contract's declared population with no size threshold: invoked without `--threshold` (default 1, `tools/append-only-audit.py:544`), every `(commit, file)` with at least one deleted line is an event (`:629`), deleted equals `git diff --numstat --no-renames` on that first-parent pair, and per event `graded + ungraded + permitted == deleted` with `permitted` only as KQ87 defines (`:706`); the run reports `"definition": "v6"` and exits 0 only when `unrestored=partial=regressed=bad_disclosures=bad_declarations=0` (`:757`). `Check:` `python3 tools/round51-append-audit-v6-check.py --repo <clone> --tip <tip> --scratch <dir>` prints `fixture=1 lane=1 scenarios=9/9 lost=142 disclosed=166 met=True`, exit 0 at `138af25b`; the tip's own tool (`python3 tools/append-only-audit.py --repo <clone> --to <tip> --json`) prints `threshold 1`, `events 106`, `deleted 6164 = graded 5901 + ungraded 205 + permitted 58`, `disclosed_lines 166` across 51 events, exit 0. At base `57a2e25b` the counter prints `fixture=0 lane=0 scenarios=0/9 met=False` and exits 1. | A v5/threshold-20 run is offered as append-only evidence (the committed base control's tool reports `threshold 20`, `events 5` for the same history, hiding 97 events including the real `LOG.md` loss at `ed135b3c`); shape-only totals; the tool's self-reported `ungraded` is taken as the whole story (KQ84's counter-side recomputation still applies). | `corpus/lessons/round-51.md` Claims C2, Gate reject 3; round-50 closure R6 C2 (X13Threshold); `considerthese/2026-10-26.md` proposal 1. |
| KQ87 | The **only** in-place change left ungraded is the cell set the contract's A-row rule names: a deleted registry row in an A-row file is `permitted` (counted, never graded) only when the deleting commit's blob holds a row with the same `S` id whose other cells are byte-equal — i.e. only status (8th), recheck (10th) and used-by (11th) changed (`tools/append-only-audit.py:487-524` splits cells outside backtick spans and `:508-523` compares the immutable cells; applied at `:647-648`); a change to `teaches`, `anchor`, `source` or any other cell, a deleted non-row line, or a row whose cells were split by a pipe character inside a backtick span is graded. `Check:` the C2 counter's `arow-mutable` scenario exits 0 with `permitted=1 graded=0`, and `arow-immutable`, `code-span-pipe` and `row-dropped` each exit 1; the lane at `138af25b` reports `permitted_lines 58` with no A-row deletion counted ungraded. | A whole-file in-place edit, or a row whose id is re-used with changed immutable cells, is called permitted; `permitted` is folded into `ungraded` to make `unrestored=0`; an append-only claim rests on the count alone without the failing immutable-cell, code-span and dropped-row scenarios. | `corpus/lessons/round-51.md` Claims C2; round-50 closure R6 C2; KQ22's A-row cell rule. |
| KQ88 (makes KQ67's disclosure mechanical) | Every graded line not held at the tip is either restored or disclosed by a ledger row that binds mechanically: deleting `commit` (40 lower-case hex), `file`, `line_sha256` of the CR-stripped line, `count` no greater than the event's unheld graded lines with that key, and `class` equal to the mechanical class — `revert` when the deleting commit's subject starts `Revert "`, else `in-place-edit` when the line's `-U0` hunk adds lines, else `removal` — and each row is consumed by exactly those lines (`tools/append-only-audit.py:525-541` parses, `:669-696` binds and subtracts). A row naming no event, no unheld line, more lines than unheld, or another class is itself a bad disclosure and exits 1. `Check:` the C2 counter's `junk-hash`, `over-count`, `wrong-class` and `no-event` scenarios each exit 1, `disclosed` exits 0, and at `138af25b` the lane's `166` disclosed lines are accepted with `bad_disclosures 0` and exit 0. | Prose-only, count-only, or "the ledger exists" disclosure; a row whose commit is not a deleting event for that file; a stale ledger — a line restored later in the same round makes the row an over-count and the audit must exit 1, so the ledger is regenerated after any build that touches a declared file (round-51 Mistakes #3). Limit: the `note` column is **not** graded — the parser checks six tab-separated fields and the shapes above but accepts an empty note (probe `empty-note-probe.out`: a correct key/count/class row with an empty note exits 0 `disclosed=1`), so "names nothing" binds by event, key, count and class, not by note text. | `corpus/lessons/round-51.md` Claims C2, Gate reject 3, Mistakes #3; round-50 closure R6 C2. |

Drafted by wave seat T4Quality (`.ufo/waves/round-51/a2w1/out/T4Quality/`) for
integration by the kama L1.

---

## Drafting evidence (not part of the QUALITY.md section)

Commands were run at the lane build `138af25b963450b6520794995605fa7dbbcd87e0`
against a `git clone --shared` of the lane; receipts are in this directory.

```
$ python3 tools/round51-replay-exe-audit.py --repo "$S/lane" --tip 138af25b... --scratch "$S/runc1"
bind=1 own=1 teardown=1 newrow=1 bound=3/3 owned=3/3 met=True
detail: own b1: running image 103:05:144695725 is the extracted member, recorded in server_exe and own_server
detail: own b2: running image 103:05:1218749509 is the extracted member, recorded in server_exe and own_server
detail: own b3: running image 103:05:76519591 is the extracted member, recorded in server_exe and own_server
detail: teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok
detail: newrow: 1 rows new since base; 1 name proc_pid_exe(5): ['| S499 |']
exit=0                                                        (c1-build-t4.out, 18.7 s)
```

```
$ python3 tools/round51-append-audit-v6-check.py --repo "$S/lane" --tip 138af25b... --scratch "$S/runc2"
fixture=1 lane=1 scenarios=9/9 lost=142 disclosed=166 met=True
exit=0                                                        (c2-build-t4.out)
$ python3 tools/round51-append-audit-v6-check.py --repo "$S/lane" --tip 57a2e25b... --scratch "$S/runc2base"
fixture=0 lane=0 scenarios=0/9 lost=0 disclosed=0 met=False
exit=1                                                        (c2-base-t4.out)
```

```
$ python3 tools/append-only-audit.py --repo "$S/lane" --to 138af25b... --json
definition v6 threshold 1
events 106  commits 341  deleted 6164
graded 5901  ungraded 205  permitted 58
disclosed_lines 166  bad_disclosures 0  bad_declarations 0  unrestored 0  partial 0
exit=0                                    (aoa-v6-json-138af25b.json, aoa-summary.txt)
```

Limit probe (KQ88): `empty-note-probe.out` — a synthetic repository with a
contract-declared `LOG.md`, one deleted line and a disclosure row carrying the
right commit, key, count and class but an empty `note` exits 0 with
`disclosed=1`; `cat -A` shows the trailing tab and no note text. The ledger's
own 166 rows all carry a non-empty note (`bad_note_rows=0`; classes
160 `in-place-edit`, 5 `revert`, 1 `removal`), so this is a parser boundary,
not a lane defect.
