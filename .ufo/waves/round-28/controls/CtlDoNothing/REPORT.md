VERDICT: does-not-meet
counted 0 registered 0 exit 0

Control class: do-nothing (preregistration.json C1.controls_required."do-nothing":
"base tree, no registry -> counted 0"). Three trees, all scored with the frozen
counter unchanged; every one prints `registered 0 counted 0 target 18 met False not-counted []`
and exits 0. `receipt.json` is the freeze run (tree 2).

Counter sha256 (all three trees, checked with `sha256sum` before running):
`e6a706bb2e15aec288924b9aec863ff0b1ffdd7e588e78250c0f642565c0540c` (equals
preregistration.json C1.counter_sha256; the receipts record the same value).

| tree | HEAD in scratch clone | registered | counted | met | exit | receipt (sha256) |
|---|---|---|---|---|---|---|
| (1) base | aa1dbd75 (4179301f + counter + sources snapshot) | 0 | 0 | False | 0 | receipt-base.json (fec4be3d…bf3) |
| (2) freeze | d8bf1804 unchanged | 0 | 0 | False | 0 | receipt-freeze.json = receipt.json (1f0c6991…ea0) |
| (3) empty | 92712f19 (d8bf1804 + empty registry + header-only section) | 0 | 0 | False | 0 | receipt-empty.json (287a4ab2…ce) |

All three receipts also carry `schema_file_at_base: []`.

## What was built

Scratch root `/fast/scratch/hyaku/kama-r28/ctl/CtlDoNothing/`, one clone of the lane
repo per tree. Commits were made only inside the scratch clones, with GIT_DIR,
GIT_WORK_TREE and GIT_INDEX_FILE unset.

1. `base/`: checked out 4179301f7516ad667509d54b5ebfe0a70a002d5b, then
   `git checkout d8bf1804 -- .ufo/waves/round-28/count-c1.py .ufo/waves/round-28/sources`.
   Nothing else was added (diff vs 4179301f: count-c1.py plus the three snapshot files
   server-schema.cpp, server-schema.h and server-task.cpp). The pins need the snapshot,
   otherwise the run exits 2 with `source pin mismatch`.
2. `freeze/`: checked out d8bf1804ce52c30343f3e41cbae41c9640db9a64, unchanged.
3. `empty/`: d8bf1804 plus `registry/request-field-outcomes-r28.json` = `{"rows": []}`
   and, appended to the end of SKILL.md, `## Round-28 request-field outcomes` followed by
   only the header row `| id | field | value | outcome | meaning | source |`.
   Copies are in `fixture/registry/request-field-outcomes-r28.json` and
   `fixture/SKILL.md.diff`.

## Exact commands

```
S=/fast/scratch/hyaku/kama-r28/ctl/CtlDoNothing
for t in base freeze empty; do git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin $S/$t; done
git -C $S/base checkout -q 4179301f7516ad667509d54b5ebfe0a70a002d5b
git -C $S/base checkout -q d8bf1804ce52c30343f3e41cbae41c9640db9a64 -- .ufo/waves/round-28/count-c1.py .ufo/waves/round-28/sources
git -C $S/freeze checkout -q d8bf1804ce52c30343f3e41cbae41c9640db9a64
git -C $S/empty  checkout -q d8bf1804ce52c30343f3e41cbae41c9640db9a64
# (empty) write registry + header-only section, commit in scratch only
for t in base freeze empty; do
  timeout 900 /usr/bin/python3 $S/$t/.ufo/waves/round-28/count-c1.py --lane $S/$t --repo $S/$t --out $S/receipt-$t.json; echo exit=$?
done
```

Output (`$S/runs.out`):

```
== base
registered 0 counted 0 target 18 met False not-counted []
exit=0
== freeze
registered 0 counted 0 target 18 met False not-counted []
exit=0
== empty
registered 0 counted 0 target 18 met False not-counted []
exit=0
```

## Which predicate clauses refused which rows

No rows reached any clause, so no clause (a) to (e) refused anything. In all three trees
the counter finished its pre-row checks (fixed environment, host pins, binary, library,
model and source pins, base object read) and then took the early return at
`count-c1.py:505` (`if not entries:` sets counted 0). Trees 1 and 2 have no registry file,
so `entries` stays `[]`. Tree 3 has a registry whose `rows` is `[]`. The header-only
SKILL.md section is never read on that path, and an empty section with no registry rows
cannot add a count. Because of the early return no llama-server was started:
`ss -ltnp` showed no listener on 127.0.0.1:47600-47619 before or after the runs, and this
seat started no other process.

## Hole?

None found for this class. An absent registry, an empty registry and a header-only
section all score 0, the same as the preregistered `before` receipt
(`before/c1-base.out`). The unmoved command holds: the counter at base prints counted 0.

## Tool installs

None.
