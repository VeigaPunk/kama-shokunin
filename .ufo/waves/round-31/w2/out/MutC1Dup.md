# MutC1Dup — is the C1 counter's duplicate-id rule load-bearing? (round 31, w2)

```RESULTS
[0] prep
$ mkdir -p .ufo/waves/round-31/w2/out/MutC1Dup /tmp/kama-r31w2/MutC1Dup
exit 0

[1] frozen counter identity + registry row count
$ wc -l .ufo/waves/round-31/count-c1.py && sha256sum .ufo/waves/round-31/count-c1.py
exit 0
  600 .ufo/waves/round-31/count-c1.py
  d86c4a94b9a464a9aa6212b2958c72229b7134eb440f64edab70de090d924216  .ufo/waves/round-31/count-c1.py

[2] lane state at seat start (read-only)
$ git rev-parse --short master && git status --porcelain | head -20 && du -sh .git
exit 0
  bda324b
   M SKILL.md
  ?? .ufo/waves/round-31/c1/c1-382d11b2.json
  ...
  38M	.git

[3] fixture pins
$ sha256sum ~/.local/opt/llama-b11755/llama-server ~/.local/opt/llama-b11755/libllama-server-impl.so ~/.cache/kama-shokunin/models/stories260K.gguf
exit 0
  b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804  .../llama-server
  e404b91a81c9ab65756b6a57b97b42115a5f429c5060c4b7f0d717ca595b59ed  .../libllama-server-impl.so
  270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d  .../stories260K.gguf

[4] clone (scratch only) + counter copies + ancestry + cited source line
$ git clone -q --no-hardlinks --single-branch --branch master <lane> /tmp/kama-r31w2/MutC1Dup/repo
$ cp <lane>/.ufo/waves/round-31/count-c1.py bin/count-c1.pristine.py
$ cp bin/count-c1.pristine.py bin/count-c1.mutant.py
$ sha256sum bin/count-c1.pristine.py bin/count-c1.mutant.py <lane>/.ufo/waves/round-31/count-c1.py
exit 0
  d86c4a94b9a464a9aa6212b2958c72229b7134eb440f64edab70de090d924216  bin/count-c1.pristine.py
  d86c4a94b9a464a9aa6212b2958c72229b7134eb440f64edab70de090d924216  bin/count-c1.mutant.py
  d86c4a94b9a464a9aa6212b2958c72229b7134eb440f64edab70de090d924216  <lane>/.ufo/waves/round-31/count-c1.py
$ git -C repo rev-parse 382d11b2107d335705875da1a4d889b074bd6fa6^{commit}
exit 0
  382d11b2107d335705875da1a4d889b074bd6fa6
$ git -C repo merge-base --is-ancestor 07794a4d30a54a60ebdff50ac76d12c6df40a0f1 382d11b2...
exit 0   (base-ancestor yes)
$ sed -n '1530p' .ufo/waves/round-31/sources/llama.cpp-704366d/server-common.cpp
exit 0
              llama_params[item.key()] = item.value();
$ grep -n 'dup_ids\|seen_ids\|duplicate-id' bin/count-c1.pristine.py
exit 0
  380:    seen_ids = set()
  382:    dup_ids = set()
  385:        if rid in seen_ids:
  386:            dup_ids.add(rid)
  387:        seen_ids.add(rid)
  406:            if rid in dup_ids:
  407:                reasons.append("duplicate-id")

[5] the mutation: disable the per-id uniqueness test only
$ diff -u bin/count-c1.pristine.py bin/count-c1.mutant.py
exit 1   (files differ; expected)
  -            if rid in dup_ids:
  +            if False:  # MUTANT: per-id uniqueness test disabled; dup_ids still computed, never applied
                 reasons.append("duplicate-id")
  (full unified diff: receipts/mutation.diff; mutant sha256
   70dc9ba8fbb6a1fd3f9a85416063e1ab0508473f90a4a51f8179df9b695b9c56)

[6] no-op fixtures in the clone (12 rows; every row asserts the base request's own max_tokens=1 /
    n_predict=1; corpus/SOURCES.md untouched, every row cites the existing S189 row)
$ python3 fixtures/build_fixture.py distinct repo && git ... commit
exit 0
  fixture distinct: 12 rows, skill rows 12
  772c5607995106f86fff1963fbef5ab924b79351   (parent 382d11b2 per fixtures/fixture-commit-parents.txt)
$ python3 fixtures/build_fixture.py sameid repo && git ... commit
exit 0
  fixture sameid: 12 rows, skill rows 1
  76fa5a1bc93a86123d644c0cf5a657ca56482808   (parent 382d11b2)
$ python3 - <<PY   # are the fixture requests literally the base request?
exit 0
  all 12 fixture requests are byte-identical to base_body: True
  base_body: {"max_tokens": 1, "messages": [{"content": "hi", "role": "user"}]}
  distinct ids unique: True

[7] pre-flight: no listener in 47900-47999, no llama-server process
$ ss -Hltpn 'sport >= :47900 and sport <= :47999'; pgrep -af llama-server
exit 0
  (no listeners)   /   no llama-server running

[8] unmutated counter on the real 18-row registry at the measured tip
$ /usr/bin/python3 bin/count-c1.pristine.py --lane <lane> --repo /tmp/kama-r31w2/MutC1Dup/repo \
    --tip 382d11b2107d335705875da1a4d889b074bd6fa6 --out receipts/pristine-real.json
exit 0
  registered 18 counted 17 target 12 met True not-counted ['K31-10']
  (stderr empty; row-level counted/reasons and live status equal to the tracked receipt
   .ufo/waves/round-31/c1/c1-382d11b2.json)

[9] mutated counter, same registry and tip
$ /usr/bin/python3 bin/count-c1.mutant.py --lane <lane> --repo /tmp/kama-r31w2/MutC1Dup/repo \
    --tip 382d11b2107d335705875da1a4d889b074bd6fa6 --out receipts/mutant-real.json
exit 0
  registered 18 counted 17 target 12 met True not-counted ['K31-10']

[10] twelve-row no-op registry, distinct ids, unmutated counter
$ /usr/bin/python3 bin/count-c1.pristine.py ... --tip 772c5607995106f86fff1963fbef5ab924b79351 \
    --out receipts/pristine-noop-distinct.json
exit 0
  registered 12 counted 12 target 12 met True not-counted []
  (all 12 rows live: HTTP 200, slot_task 3,6,9,12,15,18,...; reasons [])

[11] twelve-row no-op registry, distinct ids, mutated counter
$ /usr/bin/python3 bin/count-c1.mutant.py ... --tip 772c5607995106f86fff1963fbef5ab924b79351 \
    --out receipts/mutant-noop-distinct.json
exit 0
  registered 12 counted 12 target 12 met True not-counted []

[12] CONTROL: twelve rows sharing ONE id, unmutated counter
$ /usr/bin/python3 bin/count-c1.pristine.py ... --tip 76fa5a1bc93a86123d644c0cf5a657ca56482808 \
    --out receipts/pristine-noop-sameid.json
exit 0
  registered 12 counted 0 target 12 met False not-counted ['K31-X', 'K31-X', 'K31-X', 'K31-X', 'K31-X', 'K31-X', 'K31-X', 'K31-X', 'K31-X', 'K31-X', 'K31-X', 'K31-X']
  (reasons {'duplicate-id'} on every row; live skipped, statuses None)

[13] CONTROL: same-id registry, mutated counter
$ /usr/bin/python3 bin/count-c1.mutant.py ... --tip 76fa5a1bc93a86123d644c0cf5a657ca56482808 \
    --out receipts/mutant-noop-sameid.json
exit 0
  registered 12 counted 12 target 12 met True not-counted []

[14] restore: copy the frozen bytes again, verify, re-run
$ cp <lane>/.ufo/waves/round-31/count-c1.py bin/count-c1.restored.py && sha256sum bin/count-c1.restored.py
exit 0
  d86c4a94b9a464a9aa6212b2958c72229b7134eb440f64edab70de090d924216  bin/count-c1.restored.py
$ cmp bin/count-c1.restored.py bin/count-c1.pristine.py
exit 0
  cmp restored vs pristine: identical (exit 0)
$ /usr/bin/python3 bin/count-c1.restored.py ... --tip 382d11b2... --out receipts/restored-real.json
exit 0
  registered 18 counted 17 target 12 met True not-counted ['K31-10']

[15] supplementary: the live master had advanced to addeb57 during the seat
$ git diff --stat 382d11b2 addeb57 -- SKILL.md registry/chat-param-outcomes-r31.json corpus/SOURCES.md
exit 0
   SKILL.md | 1 +
   1 file changed, 1 insertion(+)
$ (chat table rows at addeb57) == 18 ; (registry rows at addeb57) == 18
$ /usr/bin/python3 bin/count-c1.pristine.py ... --tip addeb57 --out receipts/pristine-real-addeb57.json
exit 0
  registered 18 counted 17 target 12 met True not-counted ['K31-10']
  (receipt resolves tip addeb57c5d717785a94105a2e36cc8a76940fb6c)

[16] post-run hygiene / restoration evidence
$ ss -Hltpn 'sport >= :47900 and sport <= :47999'; pgrep -af llama-server
exit 0
  (no listeners)   /   no llama-server process
$ sha256sum <lane>/.ufo/waves/round-31/count-c1.py
exit 0
  d86c4a94b9a464a9aa6212b2958c72229b7134eb440f64edab70de090d924216   (unchanged before/after)
$ git -C <lane> status --porcelain | grep -c 'count-c1.py' ; git -C <lane> rev-parse master
exit 0
  0
  addeb57c5d717785a94105a2e36cc8a76940fb6c

[17] harness-only failures (recorded, not detector failures)
$ python3 <<PY  (first receipt-inspection script: sorted() over {None, 200, 400, 500})
exit 1
  TypeError: '<' not supported between instances of 'NoneType' and 'int'
  -> reporting-script bug; re-run with string keys printed all summaries correctly (exit 0).
$ (first collection script) ; diff -u > receipts/mutation.diff   # diff exits 1
exit 1
  no output: the shell wrapper aborts the remainder of a command on a non-zero exit; re-run
  with `|| true` produced receipts/mutation.diff and receipts/hashes.txt (exit 0).

[18] artifact export and copy (evidence, not new measurement)
$ git -C repo show 772c560...:registry/chat-param-outcomes-r31.json > fixtures/distinct.registry.json
$ git -C repo show 76fa5a1...:registry/chat-param-outcomes-r31.json > fixtures/sameid.registry.json
$ git -C repo show <fixture>:SKILL.md | sed -n '/^## Round-31 chat-completions parameter outcomes/,/^## /p' > fixtures/*.skill-section.md
$ git -C repo cat-file -p <fixture> | head -4 > fixtures/fixture-commit-parents.txt
$ cp receipts/* fixtures/* "$OUT/receipts/" && cp run.sh "$OUT/receipts/run.sh"
exit 0
  40 files under .ufo/waves/round-31/w2/out/MutC1Dup/receipts/
$ git -C repo branch -vv
exit 0
  fixture-noop-distinct 772c560 ... ; * fixture-noop-sameid 76fa5a1 ... ;
  master addeb57 [origin/master] round-31 attempt 2: C3 — SKILL instrument-registry row ...
$ git -C repo status --porcelain
exit 0   (clean clone worktree at the checked-out fixture commit)
```

Seat: MutC1Dup (leaf). Claim served: C1 (depth), open attack
`.ufo/waves/round-31/w1/out/CriticClaimSize/c1-noop.json`. No tracked lane file was edited;
no subagent was spawned; no tool was installed.

FINDING: `duplicate-id rule load-bearing: no` — the twelve-row distinct-id no-op registry (every row asserting the base request's own `max_tokens = 1` / `n_predict = 1`) counts `registered 12 counted 12 target 12 met True` under the unmutated counter and the identical `registered 12 counted 12 target 12 met True` under the mutant with the per-id uniqueness test disabled, so the rule is not what stands between this lane and a do-nothing registry; it bites only on a same-id registry (control: `counted 0 met False` pristine vs `counted 12 met True` mutant), a shape the no-op attack does not need.

Restoration evidence: the tracked counter was never written (`d86c4a94…924216` before and after; `git status` shows no change to it); the mutated bytes exist only as `/tmp/kama-r31w2/MutC1Dup/bin/count-c1.mutant.py` (`70dc9ba8…b9c56`, one-line diff, receipted); the restored copy is byte-identical to the frozen counter (`cmp` exit 0) and its run reproduces the pristine summary and the tracked `c1-382d11b2.json` row-for-row (`counted`/`reasons`/live status equal). No server was left running and no port in 47900-47999 is bound. Writes stayed in `/tmp/kama-r31w2/MutC1Dup/` and `.ufo/waves/round-31/w2/out/MutC1Dup/`; the lane advanced to `addeb57` by another session while this seat ran, and this seat made no lane git write.

LIMITS: (1) The probe changes exactly one application site (`if rid in dup_ids:` -> `if False:`); the `dup_ids` computation is left dead but harmless, and no other check was touched — the diff receipt shows one hunk. (2) "Load-bearing: no" is scoped to the no-op shortcut C1's open attack names (twelve distinct ids asserting base values); on a same-id registry the rule demonstrably changes the count, so this is not a claim that the check is inert. (3) The fixtures are my own construction, not the critic's bytes; they independently reproduce the critic's `registered 12 counted 12` shape, but agreement is at shape level only. (4) One build, model, argv and one live point per row; the live receipts prove the requests returned 200 and stored base-equal slot parameters, not that the counter's meaning prose or the sampler is correct. (5) The real-registry runs cover the summary at `382d11b2` and a supplementary run at `addeb57`; rows are not re-verified beyond counted/reasons/live-status equality with the tracked receipt. (6) This is advisory mutation evidence, not a verdict on C1, not a claim that C1 should be admitted or rejected, and not a finding about the counter's other invariants.
