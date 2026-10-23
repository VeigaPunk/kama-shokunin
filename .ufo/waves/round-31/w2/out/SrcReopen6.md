# SrcReopen6 — scoped findings (S190, S191 re-opened)

Falsifier seat, leaf. Measured at HEAD `bda324b` (one past dispatch tip `382d11b`; SOURCES.md
itself last changed in `382d11b`, worktree clean). Full command log:
`.ufo/waves/round-31/w2/out/SrcReopen6/report.md`; raw receipts: `…/SrcReopen6/receipts.txt`.

## Verdict lines (required format)

- `S190: quote-verbatim yes; words 1; line match yes; used-by corpus/knowledge/chat-adapter-outcomes.md,registry/chat-param-outcomes-r31.json exists yes`
- `S191: quote-verbatim yes; words 9; line match yes; used-by corpus/knowledge/chat-adapter-outcomes.md,registry/chat-param-outcomes-r31.json exists yes`

## What was checked

1. Both rows sit inside `## Registry` (SOURCES.md lines 202–203; section spans 9–204).
   Relocation note at line 440 confirms append-only move with cells unchanged.
2. URLs pin `tools/server/server-schema.cpp` @ `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad`,
   `#L47` and `#L64`. The local snapshot's `SNAPSHOT.json` pins that file sha256
   `1f9d7b73b4…05`; `sha256sum` on the snapshot file matches.
3. `sed -n '47p'` → `->add_alias("max_tokens")` — quote is a verbatim substring, 1 word.
   `sed -n '64p'` → `->add_alias("n") // alias "n" as fallback (OpenAI completions API)` —
   verbatim substring, 9 words. Both ≤ 25 words.
4. Context (lines 38–70) shows L47 chains off `field_num("n_predict")` and L64 chains off
   `field_num("n_cmpl")` with hard limits `1..params_base.n_parallel`, consistent with the
   rows' scope cells (max_tokens as n_predict alias; n as OpenAI fallback for n_cmpl).
5. Both used-by paths exist; bonus back-citation grep shows the knowledge file header cites
   S180–S191 and the registry JSON carries `"row": "S190"` (line 30) and `"row": "S191"` (line 325).

## Disagreements

None. Both rows survive this falsification pass on every required axis.

## What this does not establish

- Only S190/S191 were opened; S180–S189 unchecked by this seat.
- The semantic claim in S190's scope cell that `max_tokens` "lands in both stored keys" was
  not verified against request-parsing code (only the schema alias declaration).
- No upstream re-fetch; verification is against the lane's pinned snapshot, matching the
  counter's reference tree.
- used-by files exist and cite the rows; semantic correctness of the citations was not judged.
- This is advisory evidence, not a verdict; it neither admits nor rejects C1.
- No tools installed; system coreutils/git sufficed.
