## RESULTS

Exact shell text for every command (including the python heredocs that edited the JSON pins) is
preserved in `commands.log`; the block below is the same transcript with long hash/path arguments
shortened for reading. No output line below is paraphrased.

```
$ git clone --no-hardlinks <lane> clone && git reset --hard 382d11b2... && sha256sum <pins>
exit 0
382d11b2107d335705875da1a4d889b074bd6fa6
685b93876ed40cdf1f40a38e093ab179f23ad9f1000591cd7c7414bd8343b021  .ufo/waves/round-31/sources/SNAPSHOT.json
c79d193605997d21d7f4fa7f621b6f8b56ab1442963daf12ef31a3f4476447f5  registry/chat-param-outcomes-r31.json
f67e30b28ce6b4f8b18555e0f4d8370da434f2b19605b5bdd0f693a8564c06eb  SKILL.md
d86c4a94b9a464a9aa6212b2958c72229b7134eb440f64edab70de090d924216  /tmp/kama-r31w2/MutC1Pin/count-c1.py

$ sha256sum ~/.local/opt/llama-b11755/llama-server .../libllama-server-impl.so ~/.cache/kama-shokunin/models/stories260K.gguf
exit 0
b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804  llama-server
e404b91a81c9ab65756b6a57b97b42115a5f429c5060c4b7f0d717ca595b59ed  libllama-server-impl.so
270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d  stories260K.gguf

# M0 baseline, pristine clone
$ python3 count-c1.py --repo clone --lane clone --out baseline-receipt.json
exit 0
registered 18 counted 17 target 12 met True not-counted ['K31-10']
receipt: baseline-receipt.json (5094 bytes); stderr empty except `time` (real 0m0.282s)

# M1a working-tree-only tamper: SNAPSHOT.json server-common.cpp sha256 b4f4... -> a4f4... (NOT committed)
$ python3 count-c1.py --repo clone --lane clone --out m1a-receipt.json
exit 0
registered 18 counted 17 target 12 met True not-counted ['K31-10']
stderr: (empty); receipt written: m1a-receipt.json (5094 bytes)

# M1b same tamper committed in clone (af2752df75f7fd515493c0827a6a2ca5108ba913)
$ python3 count-c1.py --repo clone --lane clone --out m1b-receipt.json
exit 2
stdout: (empty)
stderr: cannot evaluate: snapshot server-common.cpp sha256 b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442 != a4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442
receipt: NOT created (ls: cannot access 'm1b-receipt.json': No such file or directory)

# restore clone to 382d11b2, verify bytes
$ git reset --hard 382d11b2... && diff <(sha256sum SNAPSHOT registry SKILL) pristine-hashes.txt
exit 0
RESTORED-IDENTICAL

# M0' restored baseline
$ python3 count-c1.py --repo clone --lane clone --out restored-receipt.json
exit 0
registered 18 counted 17 target 12 met True not-counted ['K31-10']
stderr: (empty); receipt written (5094 bytes)

# M2 registry build.model_sha256 270c...d -> 270c...e committed (a4747cf70afa929344ed91aec3a4d3dd1db45242)
$ python3 count-c1.py --repo clone --lane clone --out m2-receipt.json
exit 2
stdout: (empty)
stderr: cannot evaluate: model pin mismatch: 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d != 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256e
receipt: NOT created (ls: cannot access 'm2-receipt.json': No such file or directory)

# restore, verify
$ git reset --hard 382d11b2... && diff <(sha256sum ...) pristine-hashes.txt
exit 0
RESTORED-IDENTICAL-M2

# M3 (supplementary) on-disk snapshot bytes tampered: server-common.cpp += "\n// mutant byte\n"
$ python3 count-c1.py --repo clone --lane clone --out m3-receipt.json
exit 2
stdout: (empty)
stderr: cannot evaluate: snapshot server-common.cpp sha256 f7047421b0465c90b3732c0f1013a23ea9cbfd736c12d49aaa6e42e0e4d2d9f7 != b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442
receipt: NOT created (ls: cannot access 'm3-receipt.json': No such file or directory)

# restore disk snapshot from saved pristine copy, verify all
$ cp server-common.cpp.pristine .../server-common.cpp && sha256sum ... && diff ... pristine-hashes.txt
exit 0
b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442  server-common.cpp
685b93876ed40cdf1f40a38e093ab179f23ad9f1000591cd7c7414bd8343b021  SNAPSHOT.json
c79d193605997d21d7f4fa7f621b6f8b56ab1442963daf12ef31a3f4476447f5  registry/chat-param-outcomes-r31.json
RESTORED-ALL-IDENTICAL

# final restored baseline
$ python3 count-c1.py --repo clone --lane clone --out final-receipt.json
exit 0
registered 18 counted 17 target 12 met True not-counted ['K31-10']
receipt: final-receipt.json (5094 bytes); `diff baseline-receipt.json final-receipt.json` -> RECEIPTS-IDENTICAL

# M2a working-tree-only tamper: registry build.model_sha256 -> "0"*64 (NOT committed)
$ python3 count-c1.py --repo clone --lane clone --out m2a-receipt.json
exit 0
registered 18 counted 17 target 12 met True not-counted ['K31-10']
stderr: (empty); receipt written (5094 bytes); `git status --porcelain` showed ` M registry/...`, then `git checkout --` restored it (status lines after: 0)

# M4 committed tamper of the declared `bytes` pin only: SNAPSHOT.json server-common.cpp bytes 75061 -> 1
#    commit 94ffe8f1841a5bea6566bdb0f88edf344ecd63a7
$ python3 count-c1.py --repo clone --lane clone --out m4-receipt.json
exit 0
registered 18 counted 17 target 12 met True not-counted ['K31-10']
stderr: (empty); receipt written: m4-receipt.json (5094 bytes)
then `git reset --hard 382d11b2...` + hash diff -> RESTORED-IDENTICAL-M4

# cleanup checks
$ pgrep -af llama-server ; ls -d /tmp/kama-r31c1-* ; ss -ltn | grep 479
exit 0 (no output: no server process, no leftover server temp dirs, no listener)
$ cd clone && git rev-parse HEAD && git status --porcelain | wc -l
382d11b2107d335705875da1a4d889b074bd6fa6
0
```

## FINDING

FINDING: committed pin breaks are refused (exit 2, named reason, no receipt); working-tree-only pin edits and the declared `bytes` field are not.

Detail: the counter's pin preflight fails closed for tip-committed `SNAPSHOT.json` sha256 digests,
registry `build.model_sha256`, and on-disk snapshot bytes — each gives exit 2 with a named reason
and no receipt. The claim is nonetheless narrower than stated: pins are read from the tip **blob**
(`git cat-file blob <tip>:...`), so a SNAPSHOT.json or registry edited only in the working tree is
ignored and the counter measures normally (exit 0, receipt written); and the snapshot schema's
declared `bytes` field is never verified, so a committed `bytes` pin set to 1 also exits 0.
Neither survivor shows a wrong file being measured undetected (sha256 still binds content; `bytes`
is implied by sha256) — they show the refusal is keyed to committed digests, not to "the pin file"
as an operator sees it, and that not every declared pin field is enforced.

## Verdicts

| Mutant | Expected detector | Actual | Verdict |
|---|---|---|---|
| M1a SNAPSHOT sha256 edited in working tree only | exit 2, named pin reason, no receipt | exit 0, full measurement, receipt written | **SURVIVED** |
| M1b same edit committed at tip | exit 2, named pin reason, no receipt | exit 2, `snapshot server-common.cpp sha256 ... != ...`, no receipt | KILLED |
| M2 registry `build.model_sha256` committed wrong | exit 2, named pin reason, no receipt | exit 2, `model pin mismatch: ... != ...`, no receipt | KILLED |
| M2a registry pin edited in working tree only | exit 2 | exit 0, full measurement, receipt written | **SURVIVED** |
| M3 on-disk snapshot source bytes tampered | exit 2, named pin reason, no receipt | exit 2, `snapshot server-common.cpp sha256 ... != ...`, no receipt | KILLED |
| M4 committed `bytes` pin 75061 -> 1 | exit 2 (a "pin" is broken) | exit 0, full measurement, receipt written | **SURVIVED** (sha256-only enforcement) |

## LIMITS

- Clone is at dispatch tip `382d11b2`; the lane's current `master` is `bda324bb` (one commit
  ahead: round-31 attempt 2 C3 freeze). I did not run the counter at `bda324bb`, so I cannot say
  whether the later commit changes anything in the pin path (files inspected at `382d11b2`).
- I did not mutate `build.server_sha256`/`build.library_sha256`; they share the same loop and
  message shape as the killed model pin, so that path is inferred, not exercised.
- `--lane` and `--repo` both pointed at the same clone. A split invocation (pins from one repo,
  snapshot bytes from a different lane dir) was not probed.
- M4's `bytes` survival is a metadata-consistency gap only, since sha256 is checked; it is not
  evidence that content substitution can pass. M1a/M2a survival is consistent with a commit-keyed
  instrument and does not by itself falsify a claim read as "committed pins"; I do not adjudicate
  which reading is intended.
- This probes only pin refusal, not C1's 18-row/17-counted depth claim, not the registry's row
  semantics, and not the live request outcomes beyond the summary line.
- Single host/fixture. Baseline and restored receipts were byte-identical here; that determinism
  is observed once, not generalized.
- Exit codes and stderr are verbatim above; raw stdout/stderr, receipts, commit patches and
  before/after hashes are saved in this directory (`*.stderr`, `*.stdout`, `*-receipt.json`,
  `m1-commit.patch`, `m2-commit.patch`, `m4-commit.patch`, `pristine-hashes.txt`,
  `final-hashes.txt`, `final-tip.txt`, `commands.log`). No check was fabricated or left unrun.

## Context

Seat `KamaR31.MutC1Pin` (leaf; no subagents, no installs, no lane edits). Claim served: C1 (depth)
— "the counter refuses to measure when its pins are broken." Scratch clone
`/tmp/kama-r31w2/MutC1Pin/clone` (plain `git clone` of the lane, hard-reset to dispatch tip
`382d11b2107d335705875da1a4d889b074bd6fa6`). Counter copy
`/tmp/kama-r31w2/MutC1Pin/count-c1.py`, sha256
`d86c4a94b9a464a9aa6212b2958c72229b7134eb440f64edab70de090d924216` (matches the frozen pin).
All runs: `python3 count-c1.py --repo clone --lane clone --out <receipt>` from
`/tmp/kama-r31w2/MutC1Pin`, so git-read pins and on-disk snapshot files both come from the clone.
Output written only under `.ufo/waves/round-31/w2/out/MutC1Pin/` and the scratch dir. This seat
wrote no tracked lane file. The lane `git status` taken at the end of this run showed
` M SKILL.md` (+21 lines, an attempt-2 meaning-cell correction block naming
`w2/out/RevRow*` reports) — a concurrent wave-2 peer's edit that appeared during this seat's
run and was left untouched. All my measurements came from the clone pinned at `382d11b2`, so
that workspace edit is outside every result above.
