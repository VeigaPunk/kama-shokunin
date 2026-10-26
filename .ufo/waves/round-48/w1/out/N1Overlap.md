# N1Overlap — round-48 sibling-overlap scan

**Verdict:** No sibling lane holds any of round-48 kama's four capabilities (region-graded append-only audit, live-receipt provenance verified at record time, HF revision pinning, receipt `--compare`); overlaps found are name/method-adjacent, reported below (never absorbed).

## Evidence

Scan method: read-only `glob`/`grep` over `/home/vgpnk/Projects/shokunin/*-shokunin/{SKILL.md,tools,registry,verifiers,c2-controls,corpus/SOURCES.md}` (`gitignore=false`) for `append-only-contract`, `x-repo-commit`, `resolve/`, `server-archive`, `provenance`, `stable projection`, `--compare`, `append-only|appendonly`, `re-derived`, `exempt`, `record time`, `receipt`, `huggingface.co`, `40-hex`. All grep runs completed (exit 0); full hits in `w1/out/N1Overlap/overlap.md`. No lane modified; no tool installs; no binaries run.

1. **Append-only audit with regions** — the v3 `## `-section region grammar (`exempt=<## T>|…@p:n` / `only=<## P>@p:n`, window-eligibility, declared_at binding) is unique to kama (`tools/append-only-audit.py:4-15,118,138-154,222-228,350-359`; `tools/round48-append-audit-v3-check.py:28-42,143-146`). Sibling append-only audits: kaidoku `tools/round-38/registry-immutable.sh:2-19,90-93,109-114` (row-level, deletion/reorder); mori `tools/mori-sources-appendonly.py:8-11,34-44,69-79` (P-C12 supersession); tsukuroi `tools/check-appended-notices.py:1-5`; chousa `tools/research-gate.sh:6665-6669` (append-only JSON manifest, fail-closed) — none has regions or declaration binding. kasegi's “append-only hunter-contract” is an out-of-repo ledger state machine (`SKILL.md:224-231`). Only kama has an in-repo `registry/`.
2. **Live-receipt provenance verified at record time** — no sibling hashes artifact bytes before starting a server. Closest: kaidoku `run_provenance_ok` (`tools/round-39/c1-counter.py:219-224`, run-attribution) and `tools/round-40/fetch-vendor.py` (URL→image sha256→tar member→carve→pin, `SKILL.md:1470`); chousa witness receipts pin gate sha256 at record time (`tools/argv-witness.py:310-373`); mado “receipt-time is provenance” (`tools/mado-verify.sh:1758-1760,2413-2415`).
3. **Hugging Face revision pinning** — only kama pins an HF `resolve/<40-hex>` model URL (`tools/kama-llamacpp-live.py:70-71,1299-1304`; SOURCES S492/S493). kengaku's only HF use is `huggingface.co/api/models` catalog probing, unpinned (`SKILL.md:776-777`).
4. **Receipt `--compare`** — souji's census family uses `--compare PREV.tsv` with the same fail-closed malformed-baseline rule (`tools/souji-census.impl-33.sh:52-70`; `tools/impl-40.sh:42-51`; `tools/impl-41.sh:31-37`; `tools/impl-44.sh:46-58`; `tools/impl-47.sh:24-39`; `tools/cand-census-07.sh:4-8`), kotoba has a `--compare` derived-row mode (`verifiers/verify_harness_independent.py:95-99`), mado has `--snapshot-diff` — none compares JSON receipts against a stable projection of captured surfaces.

Deliverables written:
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/N1Overlap/overlap.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/N1Overlap.md`
