# N4Pattern — round 49 cross-claim pattern

Verdict: four round-48 closure items closed (R1 archive bound, K2Cheat/K2Urlswap replay witness, K1Regions exempt laundering, K1Binding substring binding); the three round-48 N4Pattern-ranked residual acceptors remain open, and digest-ledger.py:131-132 (`unverifiable` = any non-empty note) is now the cheapest remaining self-report hatch.

## Evidence

- Build diff (freeze `36d5ed26` → tip `74558c71`, clone `/fast/scratch/hyaku/kama-r49/N4Pattern/lane`): `git diff --stat 36d5ed26 74558c71 -- tools/` → `append-only-audit.py | 101 +++++`, `kama-live-replay.py | 27 ++`, `kama-llamacpp-live.py | 151 +++`; `corpus/SOURCES.md` +S494/S495. `git diff --stat 438127bc 36d5ed26 -- tools/` → only the two frozen round-49 counters added.
- `git log --oneline 438127bc..74558c71 -- tools/hexrun-census.py tools/gguf-identity.py tools/kama-context-capacity.py tools/digest-ledger.py tools/kama-ollama-evidence.py` → empty (round-48 flagged instruments untouched).
- C1 witness: `kama-llamacpp-live.py:280-300` (`hold_for_witness` writes ready.json atomically, holds until release); `round49-replay-witness-audit.py:258-289` (`observe` reads /proc exe digest, socket inode, -m hash, nonce round-trip vs GGUF vocab), `:292-340` (`witness_one` requires server gone after release; `:327-329`).
- C2 v4: `append-only-audit.py:423-441` (`origins` from first commit blob), `:474-476` (carve-out only for exempt-born text); `:14-19` (word-bound token, negation window, no wildcard self-declaration); `:465-467` (eligible = title whose section size never dropped below parent).
- Ranked residual acceptors (file:line at tip): digest-ledger.py:131-132; hexrun-census.py:273-274 (NOTE_MIN=10 at :77); gguf-identity.py:948,978-984 (evidence_scope `receipt-self-report-not-authenticated-execution` at :629); kama-ollama-evidence.py:472-476 (offline, readiness=unknown); kama-context-capacity.py:602-635; capability-repertoire-audit.py:140-161; pin-trigger-consumed.py:19-29.
- No tools installed/upgraded (analysis-only; read-only git). No llama-server processes started (verified `pgrep -af llama-server` → none). Scratch clone removed after writing outputs.

## Deliverable

Full ranked analysis: `.ufo/waves/round-49/w1/out/N4Pattern/patterns.md`.
