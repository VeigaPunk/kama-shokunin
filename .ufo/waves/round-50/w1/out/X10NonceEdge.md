# X10NonceEdge — nonce robustness of C1 against a real held server

**Verdict: the C1 nonce rule is solid on the counter's own form (60/60 fresh nonces, two witnessed replays of `receipt-3.json` at the round-50 build) and every one of the 20 edge forms round-trips faithfully through the held server (80/80 by byte concatenation and 80/80 by `/detokenize`), but the rule as written is string-and-literals-only: 10/20 edge forms fail it *closed* on byte-fallback tokens, control tokens and a literal U+2581, so a future edit to the nonce literal could silently turn C1 into an always-fail — one fragility, no live defect, one order-free residual.**

Round-50 lane C1 (`tools/round50-replay-bind-audit.py`, sha256 `ff6ac2ac…c5e89` = the preregistration's `counter_sha256`) answered fresh nonces on a server the *build under test* held for me, not on a scratch server of my own. Everything below was measured on the wire; inference is marked.

## What ran

Lane clone (read-only use), tool blobs identical at lane HEAD and at the build commit:

```
$ git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane
$ git -C $S/lane rev-parse HEAD
3b79eaddf38246c637cc7ba1a94ab363422876b6
$ for f in tools/kama-live-replay.py tools/kama-llamacpp-live.py tools/round50-replay-bind-audit.py; do
    git -C $S/lane rev-parse HEAD:$f; git -C $S/lane rev-parse 97c864bead3ee4a2f629574e77263d33834ec98a:$f; done
4d675380… 4d675380…   (kama-live-replay.py, identical)
f47f4f70… f47f4f70…   (kama-llamacpp-live.py, identical)
d918d601… d918d601…   (round50-replay-bind-audit.py, identical)
```

Two runs of `python3 $S/probe.py $S` (harness: `out/X10NonceEdge/probe.py`), each one a witnessed replay:

| run | command | exit | wall | held pid/port | replay verdict |
|---|---|---|---|---|---|
| 1 | `python3 $S/probe.py $S` | 0 | 6.1 s | 2225430 / 38191 | `match=true refused=None mismatches=0` |
| 2 | `python3 $S/probe.py $S` (adds the frozen `observe()` verbatim) | 0 | 4.2 s | 3361367 / 37215 | `match=true refused=None mismatches=0`, replay rc 0 |

Each replay was started the way the counter starts one (`python3 -I tools/kama-live-replay.py --receipt .ufo/waves/round-48/c2/live/receipt-3.json --witness-dir …`), with an allow-list env (`PATH HOME LANG LC_ALL TMPDIR`) plus, in run 2, `KAMA_R50_CANARY` planted in *the harness's own* environment so the counter's env leg was exercised for real.

**The server was real and held** (both runs; run 2 shown, `nonce-probe.json:held`):

```
exe_sha256 35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0  == frozen server
LISTEN inode 703491710 owned by pid 3361367 (one socket, 127.0.0.1:37215)
mapped      dev 103:05 inode 414254164 → hashes to 270cba1b…256d (the frozen model)
ready.json pid 3361367 == rerun receipt child_pid; rerun model_mapping dev/inode identical
counter.observe(pid, port, vocab, "KAMA_R50_CANARY", probs) → problems []
```

`counter.observe` is the frozen function itself (`tools/round50-replay-bind-audit.py:343`), called against the held server: it ran its own nonce round-trip plus exe, listen, tree, env and mapped legs and appended no problem. Release and teardown after the battery, both runs:

```
release file written → replay exit 0; after: {pid_alive: false, port_refuses: true, ready_gone: true}
pgrep -af X10NonceEdge  → 0
```

## Result: 60 counter-form nonces, 20 edge forms

Rules applied are the counter's own, verbatim: `piece` is `str`, `0 <= id < len(vocab)`, `vocab[id].replace("\u2581"," ") == piece` (`tools/round50-replay-bind-audit.py:364-365`), then `/detokenize` content `in (nonce, " " + nonce)` (`:368-369`); the vocabulary is decoded from the model by the counter's own `gguf_tokens` (`:149`), 512 tokens.

| form | n | current rule | detok rule | byte-concat (= nonce or ' '+nonce) |
|---|---|---|---|---|
| counter form `kama witness <hex16>` | 60 | **60/60** | 60/60 | 60/60 |
| edge forms | 20 | 10/20 | 20/20 | 20/20 |

Edge forms (each of ten classes twice, fresh random tail each run): **pass** — uppercase hex (`kama witness 7BB833844909FDDC`), digits only (`827764359111945735456609396150`, no letters or spaces), leading space (` kama witness …`), 200 chars (`kama witness ` + 188 hex → 197 tokens), double space (`kama  witness …`). **fail the piece rule** — non-ASCII mixed (`kama witness é中文≥🙂 …`), embedded newline, trailing newline, tab, CJK only (`かま 目撃 …`).

Failure classes, exact, from `vocab-analysis.json:failure_classes`:

```
piece-is-byte-array      id 231 piece [228]   packed vocab "<0xE4>"   (中 = E4 B8 AD)
                         id 233 [230] "<0xE6>"   id 230 [227] "<0xE3>"
                         id 187 [184] "<0xB8>"   id 176 [173] "<0xAD>" …
piece-is-control-char    id 12  piece "\t"     packed vocab "<0x09>"
                         id 13  piece "\n"     packed vocab "<0x0A>"
```

Mechanism. The model's vocab has 256 byte tokens at ids 3–258, packed as the literal strings `<0xNN>`; b11909's `/tokenize` with `with_pieces` sends a byte-fallback token as a **JSON int array** (`[228]`), and a control token as the **unpacked character** (`"\n"`), not as the packed `<0x0A>`. The counter's predicate requires `isinstance(piece, str)` and compares against the packed string with only U+2581 replaced, so those tokens can never satisfy it. Meanwhile the server is *right*: `/detokenize` of those ids returned the nonce in 80/80 cases, and the wire bytes of the pieces concatenate to the nonce (modulo the leading space) in 80/80 cases — including the two non-ASCII classes once the int arrays are joined as bytes (exact UTF-8 reconstruction of `é中 文≥🙂` and `かま 目撃`).

Two load-bearing facts about the counter's own form:
- The `"\u2581"`→`" "` mapping is genuinely exercised: 120 of 1196 pieces carry `▁` in the packed vocab (`▁k`→` k`, `▁w`→` w`, `▁f`→` f`, …). Without it, all 60 would fail.
- `/detokenize` on b11909 always prepends exactly one space: **0/80** exact matches, **80/80** via `" " + nonce`. The rule's first alternative (`dt == nonce`) is dead on this server; the second is the only one that fires. Token counts of the counter form are 22–25 (merges vary with the hex value, all vocab-consistent), far below `-c 256`, and even the 200-char form is 197 tokens — no truncation risk in either rule.

## Findings

**F1 (fragility, not a live defect).** `tools/round50-replay-bind-audit.py:364-365` is defined only over text tokens that the GGUF stores as plain strings. Reproduced with: `python3 $S/probe.py $S` → `edge-05…09 pieces_ok=False` while `detok_ok=True` for all of them. Trigger: any edit to the nonce literal at `:360` that introduces a control character, a non-ASCII code point, or a literal `▁`. Consequence: `probs` gains a line, `bind=0`, `met=False` on all three receipts, with a message that reads like server misbehaviour. Three code points are involved, all provable from the packed vocab: byte tokens (3–258), control tokens (12, 13, and siblings), and U+2581 itself (id 410: the rule maps its packed `▁` to `" "`, while the server's piece for that token is `▁` — *[INFERENCE: from the rule text + vocab; not sent on the wire]*). Proposed fix (out of scope to apply; counter frozen): add `piece_bytes`/`piece_ok` and compare the byte concatenation of the pieces with the nonce, full text in `out/X10NonceEdge/proposed_nonce_rule.py`. Evaluated offline against all 80 stored rows: **80/80 accepted** (current rule 70/80), and it still rejects a reversed piece list, an id-shifted list and a foreign-piece list (`vocab-analysis.json:proposed_rule_adversarial`). Sketch:

```diff
--- a/tools/round50-replay-bind-audit.py
+++ b/tools/round50-replay-bind-audit.py
@@ observe(), before the nonce block
+BYTE_TOKEN = re.compile(r"^<0x([0-9A-Fa-f]{2})>$")
+def piece_bytes(piece):            # JSON str, or byte-fallback int array
+    if isinstance(piece, list) and all(isinstance(b, int) and 0 <= b < 256 for b in piece):
+        return bytes(piece)
+    return piece.encode("utf-8")
+def piece_ok(t, vocab):
+    tid, piece = t.get("id"), t.get("piece")
+    if not isinstance(tid, int) or not 0 <= tid < len(vocab):
+        return False
+    wire, packed = piece_bytes(piece), vocab[tid]
+    m = BYTE_TOKEN.match(packed)
+    if m:
+        return wire == bytes([int(m.group(1), 16)])
+    return wire in (packed.replace("\u2581", " ").encode("utf-8"), packed.encode("utf-8"))
@@ inside observe()
-        bad = [t for t in tk if not (isinstance(t.get("piece"), str) and 0 <= t["id"] < len(vocab)
-                                     and vocab[t["id"]].replace("\u2581", " ") == t["piece"])]
+        bad = [t for t in tk if not piece_ok(t, vocab)]
         if not ids or bad:
             probs.append(f"tokenize pieces disagree with the model vocabulary: {bad[:3]}")
+        elif b"".join(piece_bytes(t["piece"]) for t in tk) not in (
+                nonce.encode(), b" " + nonce.encode()):
+            probs.append("tokenize pieces concatenate to something other than the nonce")
```

**R1 (residual bound, not a defect).** The predicate at `:364-365` is membership-only and order-free: on the stored wire data, reversing a passing token list leaves `bad == []` (`vocab-analysis.json:proposed_rule_adversarial.current_rule_on_reversed_tokens.bad_pieces = 0`), so a server that answers `/tokenize` with a permutation of the model's own tokens and `/detokenize` with the inverse would pass both rules. The claim is "answering a fresh nonce against the model's own vocabulary", which membership satisfies, so this is inside the claim as written; the concat check above makes the rule order-sensitive at zero cost (it holds 80/80 today).

## Limits of this seat

- One model, one server build (`b11909`, frozen sha), one receipt (`receipt-3.json`), two holds; the counter checks three receipts, but the encoding behaviour is a property of the binary and the 512-token vocab, not of the receipt.
- The hold window is short (~1 s of probing per run, 40 requests); holds by design start only after `ready.json`, so loading-state behaviour is untested here (out of scope).
- `mapped_model` behaviour on btrfs-subvolume dev/inode mismatch was not exercised (scratch is xfs); the counter's own limit list covers it.
- No tool installs, no pacman, no writes outside my scratch and `out/X10NonceEdge/`; lane, fleet repo and shokuknow untouched (all lane access through the shared clone; read-only). Scratch `/fast/scratch/hyaku/kama-r50/X10NonceEdge` removed after the copies; `pgrep -af llama-server` shows no process of mine (the four others belong to X11ModelSwap/J4Decoy/R1Rerun2/Sen1Env and were left alone).

## Artifacts

| file | what |
|---|---|
| `out/X10NonceEdge/nonce-probe.json` | run 2, all 40 rows (ids, pieces, detok, verdicts), held-server facts, frozen `observe()` problems, replay outcome, post-release state |
| `out/X10NonceEdge/nonce-probe-run1.json` | run 1, same battery without `observe()` (independent 30 counter-form samples) |
| `out/X10NonceEdge/vocab-analysis.json` | pooled 80-row verdicts, vocab facts, failure classes, proposed-rule evaluation and adversarial checks |
| `out/X10NonceEdge/probe.py` | the harness (imports the frozen counter for `post`, `gguf_tokens`, `mapped_model`, `observe`) |
| `out/X10NonceEdge/replay.json`, `rerun-receipt.json` | the witnessed replay's own output and the rerun receipt (`match=true`, `witness.released=true`, `model_mapping` mapped) |
| `out/X10NonceEdge/proposed_nonce_rule.py` | proposed hardened rule, offline-validated 80/80 accept / rejects permutation, id shift, foreign pieces |
| `out/X10NonceEdge/environment.json`, `replay.log` | host/kernel/python, lane HEAD and tool digests, model digest; replay's one-line verdict |
