VERDICT: holds — every README.json claim in d3-r26-shortcut-pins re-verified: both pinned files hash-match the stated sha256, equal the r26w2 scratch originals byte-for-byte, equal what the pinned llama-server binary prints today, and the counter/gen_shortcut SHA statements check out at eb09e742; the declared gap is honestly scoped.

# Repair review — defect 3 (d3-r26-shortcut-pins)

Routed defect: `corpus/lessons/round-26-verifier-spotcheck.md:235` — "`gen_shortcut.py` sets `COUNTER_SHA` (line 24) but never asserts it, and it reads `info-help.txt` and `info-version.txt`, which were never committed. Pin and commit them, or note the gap."

The repair chose both: it pinned the two files under `.ufo/waves/round-27/repairs/d3-r26-shortcut-pins/` AND noted the residual gap explicitly in the `gap` field.

## Hash table

| file | README sha256 | re-hashed (repair copy) | scratch original (r26w2) | live binary output | match |
|---|---|---|---|---|---|
| `info-help.txt` | `bcb795d4...2f6b` (60469 B) | `bcb795d4736d9bf3209492e0a10058adc6015ac5f8eeadb9abe9182bb9722f6b` | identical | identical | yes |
| `info-version.txt` | `741785a8...07b2` (90 B) | `741785a8bef8e1d72733be64f62ee12584d39779039812d8685e9abe872c07b2` | identical | identical | yes |

Commands run (all exit 0):

```
$ sha256sum <repair>/info-help.txt <repair>/info-version.txt \
    /fast/scratch/hyaku/kama-r26w2/CriticShortcutRows/info-{help,version}.txt
bcb795d4736d9bf3209492e0a10058adc6015ac5f8eeadb9abe9182bb9722f6b  (all four lines: help pair)
741785a8bef8e1d72733be64f62ee12584d39779039812d8685e9abe872c07b2  (version pair)

$ cmp -s <repair>/info-help.txt  <scratch>/info-help.txt  -> identical
$ cmp -s <repair>/info-version.txt <scratch>/info-version.txt -> identical

$ timeout 30 ~/.local/opt/llama-b11755/llama-server --help    2>&1 | sha256sum
bcb795d4736d9bf3209492e0a10058adc6015ac5f8eeadb9abe9182bb9722f6b  -   (exit 0)

$ timeout 30 ~/.local/opt/llama-b11755/llama-server --version 2>&1 | sha256sum
741785a8bef8e1d72733be64f62ee12584d39779039812d8685e9abe872c07b2  -   (exit 0)
version text: "version: 0.7.0-dev (build 11755, commit 704366d76)"
```

So the pinned copies are (a) byte-identical to the r26w2 scratch originals the L1 copied from, and (b) byte-identical to what the b11755 binary emits today — the README's `regenerated_check` claim reproduced exactly.

## mtime / provenance claims

```
$ stat -c '%y %s %n' <scratch>/{info-help.txt,info-version.txt,gen_shortcut.py}
2026-10-23 00:59:58.246 -0300  60469  info-help.txt
2026-10-23 00:59:58.251 -0300     90  info-version.txt
2026-10-23 01:01:06.154 -0300   7485  gen_shortcut.py
```

Matches README's "mtime 2026-10-23 00:59:58 -0300, before gen_shortcut.py mtime 01:01". The info files were written ~68 s before the generator ran, consistent with being its captured inputs.

## counter_sha claim

```
$ git -C <lane> show eb09e742:.ufo/waves/round-26/count-c1.py | sha256sum
6501737c749926be9d6b37761175d76f89876976c46bd5951fc1a3520c796588   (equals README + gen_shortcut.py:24 value)

$ git ls-tree -r eb09e742 -- .ufo/waves/round-26 | grep gen_shortcut
100755 blob 764da3ff...  .ufo/waves/round-26/w2-falsify/out/CriticShortcutRows/gen_shortcut.py
$ git show eb09e742:...gen_shortcut.py | sha256sum
1a236f801d509db4f0e49742d33f804a9d449a54597c27a1a894893eaee2f178
$ sha256sum <scratch>/gen_shortcut.py
1a236f801d509db4f0e49742d33f804a9d449a54597c27a1a894893eaee2f178   (equal)
```

`grep -n 'COUNTER_SHA\|assert' <scratch>/gen_shortcut.py`: `COUNTER_SHA` occurs only at line 24 (assignment); the 9 `assert` statements (lines 85-93) reference literals/base-hits, never `COUNTER_SHA`. README's "never asserted by the script" is accurate — it is never even read.

## Declared gap — accurate

README `gap`: scratch copies are not proven to be the exact bytes the seat read at 01:01 beyond mtime + regenerated-sha equality. Correct and non-exitable: a file could have been rewritten between capture and copy with identical content (undetectable), or the binary's output could have changed after 01:01 (sha equality to today's output makes this moot for the pin's purpose — the pin documents current bytes, which is what a verifier can reproduce). The honest framing stands; no stronger evidence is obtainable [INFERENCE: short of a contemporaneous hash receipt, which defect 3's repair pattern now institutionalizes].

## Residual risk / notes

- The files live under `repairs/` in the working tree, not a retroactive round-26 commit — appropriate: lane rules forbid rewriting round-26 history; the repair gives any future verifier a committed, hash-stated reference copy.
- No edit to the committed round-26 script was made (README states this); the unasserted `COUNTER_SHA` remains as-is at eb09e742 — acceptable since the gap is documented rather than silently patched.
- No tools installed; no server started (hashing the binary's `--help`/`--version` output only, no port use); no processes left running.
