# F25C2ReceiptProvenance — C2 receipt provenance (w2 falsify)
Attack: synthetic receipt, never emitted by tools/kama-ollama-live.py (nonce f00dface0001, binary_sha256 64 zeros, version 0.0.0-never-shipped, argv /usr/bin/true, all 11 capture bodies hand-authored, sha256 recomputed per body).
Expected if clause holds: C2 met=False / receipt_ok=0 for the forgery.
Output: in a scratch fixture whose registry+amendment are green on the REAL committed receipt (phase 1: met=True exit 0, controls_rejected=35/35), swapping in the forgery gives byte-identical stdout — met=True exit 0, receipt_ok=1, controls_rejected=35/35; receipt sha256 49d06600…90c2a6 → 76a75436…29e935, verdict unchanged. Real receipt with attacker bodies (root, show) + recomputed hashes also met=True exit 0; the tamper control only rejects non-rehashed edits.
Verdict: MUTANT KILLED — tools/round60-c2-counter.py receipt_caps() reads only schema + sha256(body); nonce/binary_sha256/pin/checks/port/argv_child/receipt-verdict are never read, so C2 cannot prove any receipt came from the real tool or any server at all.
Coverage finding, no repair: predicates/registry/receipt/counters untouched; note registry/ollama-live-claims-r60.tsv + amendment exist in no commit, so the hole arms when they land.
Restoration: lane untouched (status clean of my writes; receipt.json 49d06600… and counter d2e9a722… hashes unchanged pre/post); scratch /fast/scratch/hyaku/kama-r60/F25C2ReceiptProvenance removed, TMPDIR scratch-local.
Details: .ufo/waves/round-60/w2/out/F25C2ReceiptProvenance/findings.md
