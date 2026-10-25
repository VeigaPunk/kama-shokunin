kimi version 2.3.1
• Let me parse the task:

  - Seat directory: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-36/w3/out/MutRowPipe/
  - Target: census parser's handling of a pipe inside a cell.
  - Task: In seat directory only, copy the lane registry (corpus/SOURCES.md), insert a literal pipe inside one cell of a copied data row, run /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file against the copy. Paste exit code and finding. Say whether census catches broken column count. Do not modify lane registry.
  - Report: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-36/w3/out/MutRowPipe.md

  Steps:
  1. Look at the script sources-census.sh to understand validate mode and what a "column count" check looks like.
  2. Copy SOURCES.md to seat scratch dir.
  3. Insert a literal pipe inside one cell of a copied data row (e.g. take the S328 row, insert `|` in the middle of a cell — making it appear as an extra column, or inside a cell making column count wrong).
  4. Run validate --file on the copy, capture exit code and output.
  5. Run validate on pristine copy as baseline control too (to confirm baseline passes).
  6. Write report at the given path, with mutant, expected detector, output, verdict, restoration evidence (though scratch copy is disposable per tasking? The tasking says scratch files go in seat dir; the copy is in the seat dir, so it's fine to keep it — record before/after hashes of the lane registry to prove untouched).

  Also the Godspeed framing: name axes, iterate cheap in parallel, record actual outputs, killed/survived/inconclusive.

  Let me start by reading the script and the registry tail in parallel.

  Bounds: don't modify lane registry; use copy. Read-only git permitted. Don't touch other things.

  Let me do parallel calls:
  - Read /home/vgpnk/Projects/shokunin/scripts/sources-census.sh
  - Bash: tail of SOURCES.md to see data rows and column structure
  - Bash: mkdir seat dir

  Actually Read for script; Bash for tail -n 30 of SOURCES.md; mkdir -p seat dir. All independent.

  Let me also hash the lane registry before and after for restoration evidence (well, we don't modify it, but evidence of untouched: sha256 before and after).

  Plan the mutation: find a data row (e.g. `| S328 | ... |`), pick a cell and insert a literal `|` inside it, e.g. change `| 2026-10-24 |` to `| 2026-10-|24 |` — that creates an extra column break, changing column count from N to N+1. Alternatively insert pipe inside a URL cell. The point: the parser should catch column count mismatch if it validates columns.

  Let me execute.1e44b4f314f2eb7f671feb537d03030af145713d484cbd326017fcbb5a83e8fe  /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
`scripts/sources-census.sh validate` read them as E12 `row outside Registry section` (12 findings,$
exit 1). They now sit in the `## Registry` table above with ids and cells unchanged; this pointer$
records the move (append-only: no cell was rewritten). Defect and fix recorded in$
`corpus/lessons/round-31.md` M-BM-'Mistakes row 4.$
$
## Round-33 search log supplement$
$
**2026-10-24 M-bM-^@M-^T gate definition and reject-side re-open.** Question: where exactly does the r32 gate define registration, and does the standing S104 reject about fsck/promisor still hold? Where: `tools/gate-registry-check.py` at c4c46ad5 (docstring "Contract", lines 15M-bM-^@M-^S16); `https://raw.githubusercontent.com/git/git/v2.56.0/builtin/fsck.c` (S104, lines 143M-bM-^@M-^S149); and the r32 C2 gate receipts. Identified 2 source candidates; screened 2; included 1 new row (S194) and reopened standing rejected S104 without changing its row; excluded 0. Stop: both source decisions are bounded to the exact routed evidence; no vendor/API or endpoint claim was sought.$
I should read the AGENTS.md file that applies. Also I need to see the actual registry data rows (the last two data rows, S328/S329) to copy a row. Let me read AGENTS.md and grep the SOURCES.md for S328/S329 rows in parallel.214:| S328 | SGLang Native APIs at tag v0.5.22 — https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/docs/docs/basic_usage/native_api.mdx | docs | A | the published SGLang native-API route list at tag v0.5.22; a documentation surface, not a live server | line 6 and route-list line 9 — Apart from the OpenAI compatible APIs, the SGLang Runtime also provides its native server APIs. | the published page still lists only /get_model_info and never names /model_info, so a client that reads the page as the contract probes the route the engine is retiring | mined | 2026-10-24 | 90d | corpus/knowledge/sglang-native-route-deprecation.md |
215:| S329 | SGLang http_server.py at tag v0.5.22 — https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/python/sglang/srt/entrypoints/http_server.py | code | A | the engine-side deprecation of /get_model_info at tag v0.5.22 | lines 790-791 — Endpoint '/get_model_info' is deprecated and will be removed in a future version. Please use '/model_info' instead. | the engine itself warns that the documented route is deprecated and names /model_info as the replacement, so the published route list is not the engine's current contract | mined | 2026-10-24 | 90d | corpus/knowledge/sglang-native-route-deprecation.md |
462
I have everything I need:

  - Registry has S328/S329 rows at lines 214-215 of /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md (462 lines total).
  - The census parser: `gawk -F'|'`, expects NF==13 for valid rows (11 columns => NF=13). E01 fires when NF!=13, with `fields=%d` (NF-2). Baseline clean => exit 0.

  Mutation: copy SOURCES.md into seat dir, insert a literal pipe inside one cell of a copied data row. E.g., inside the S328 "teaches" cell, insert `|` — that splits one cell into two, making NF=14, so E01 with fields=12. Wait: normal row NF=13 (leading empty field before first pipe + 11 cells + trailing empty). Inserting a pipe inside a cell makes NF=14, fields=12. Also possibly id parse still fine.

  Important subtlety: with NF=14, the parser prints E01 and E02 possibly (if id doesn't match). The id would be at $2 which is unchanged, so E01 with fields=12.

  Also note: url_of uses `https?://[^[:space:]|]+` — inserting a pipe inside a URL would truncate URL parsing, but I'll insert the pipe in a non-URL cell to be clean, e.g. the teaches cell or the scope cell. Actually the task says "insert a literal pipe inside one cell of a copied data row". Any cell. To specifically test the column-count detector, put it in a non-URL cell so the only effect is NF. Let me put it in the scope cell of S328: `| A |` ... hmm, the scope cell for S328 is "the published SGLang native-API route list at tag v0.5.22; ...". Insert `|` mid-cell.

  Plan:
  1. Baseline control: run validate --file on a pristine copy in the seat dir → expect exit 0, "ok".
  2. Mutated copy: insert pipe in one cell of S328 row (sed or python) → run validate --file → capture exit code + output.
  3. Restored copy: apply reverse edit (or re-copy pristine) → run validate → exit 0. Hashes before/after.

  Actually per the UFO mutation protocol: run the detector on pristine, mutated, and restored bytes; record before/after hashes. The lane registry itself must not be modified — my restoration evidence is that the lane file hash is unchanged before/after (1e44b4f3...).

  Let me do it with cp and python for exact single-cell pipe insertion. Steps in one bash script, capturing outputs to files in the seat dir.

  Seat dir: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-36/w3/out/MutRowPipe/

  Commands:
  ```
  SEAT=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-36/w3/out/MutRowPipe
  LANE=/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
  CENSUS=/home/vgpnk/Projects/shokunin/scripts/sources-census.sh

  cp "$LANE" "$SEAT/SOURCES.pristine.md"
  sha256sum "$LANE" > "$SEAT/lane-hash.before"

  # baseline
  bash "$CENSUS" validate --file "$SEAT/SOURCES.pristine.md"; echo "pristine exit=$?"

  # mutate: insert literal pipe inside S328 teaches cell (after "route-list line 9" maybe)
  ```

  For the mutation, use python to replace a unique substring in the S328 line, inserting ` | `? Wait — "insert a literal pipe inside one cell" — the pipe character itself. E.g. change "Apart from the OpenAI compatible APIs," to "Apart |from..." Actually let me insert the pipe into the scope cell: "the published SGLang native-API route list at tag v0.5.22;" → "the published SGLang |native-API route list at tag v0.5.22;". Simple replacement of unique string "the published SGLang native-API route list" → "the published SGLang |native-API route list". That string appears only in the S328 row (line 214). Verify uniqueness first.

  Then run mutated validate, capture exit code (expect 1) and output (expect E01 ... fields=12).

  Then restore: copy pristine back over the mutated file, run validate again (exit 0), and hash-compare mutated-after-restore vs pristine.

  Also re-hash the lane registry at the end to prove untouched.

  One more check: does `--file` mode treat the dir correctly? `dir_abs=$(realpath "$(dirname file)/..")` — my seat dir's parent is .../w3/out, fine; used-by paths are resolved relative to $dir — usedby_findings only runs for mined rows. S328/S329 are mined with used-by corpus/knowledge/sglang-native-route-deprecation.md. dir would be .../w3/out, so E11 could fire for the pristine copy! Careful — the pristine baseline may not be clean. The used-by path exists relative to the lane: /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/knowledge/sglang-native-route-deprecation.md. In my seat copy, dir = .../out/MutRowPipe/.. = .../out, so $dir/corpus/knowledge/... won't exist → E11 findings on both pristine and mutated. Hmm.

  Per the protocol: "A baseline failure is inconclusive, not a killed mutant." I want the baseline clean. Options:
  1. Structure the seat dir so that dir/.. resolves to the lane root: place the copy at $SEAT/corpus/SOURCES.md — then dir = $SEAT, and $SEAT/corpus/knowledge/sglang-native-route-deprecation.md must exist. I can copy the knowledge file into $SEAT/corpus/knowledge/ too. Then baseline is clean and E11 won't fire. That keeps everything in my seat dir.

  Wait, dir_abs = realpath(dirname(file)/..). If file = $SEAT/corpus/SOURCES.md, dirname = $SEAT/corpus, /.. = $SEAT. dir=$SEAT. Then used-by "corpus/knowledge/sglang-native-route-deprecation.md" checked at $SEAT/corpus/knowledge/sglang-native-route-deprecation.md. Copy that file in. Also W04/W01...: S328/S329 tier A mined used-by set → no W01 (W01 is tier C). W03 only if used-by == —. So pristine copy should validate clean (exit 0, "ok") as long as used-by resolves. There may be other rows in the full registry... wait, the registry is 462 lines with many rows S001..S329 presumably, all with used-by paths relative to the lane. E11 fires for any mined row whose used-by doesn't exist under $SEAT. That would flood the baseline with E11s. Hmm.

  So copying the whole registry gives many mined rows with various used-by paths. That's a problem for a clean baseline in an arbitrary seat dir.

  Alternative: create the seat scratch as a minimal registry? The task says "copy the lane registry". So copy the full registry. Then baseline: run validate --file on pristine copy at $SEAT/corpus/SOURCES.md with used-by files copied. How many distinct used-by paths are there? Could be many. Simpler: check how many E11 findings the pristine copy produces. If it's many, baseline is noisy.

  Alternative approach: make $SEAT mirror the lane layout: $SEAT/probe/corpus/SOURCES.md plus symlink? Can't symlink outside... Actually symlinks inside seat dir pointing to lane corpus files — that's read-only usage of the lane, fine. But E11 checks `[ ! -e "$dir/$path" ]` — with $dir=$SEAT/probe, path=corpus/knowledge/sglang-native-route-deprecation.md → $SEAT/probe/corpus/knowledge/... So I'd need all used-by paths under $SEAT/probe. A symlink $SEAT/probe/corpus/knowledge → lane corpus/knowledge would resolve all of them at once! Symlink creation is inside my seat dir, doesn't mutate the lane. -e follows symlinks, so it works.

  But wait — is it even necessary for the *finding*? The core question: does the census catch the broken column count (E01)? Even with E11 noise, E01 for the mutated row would be the signal. But a clean baseline is much stronger evidence. Let me do the symlink mirror:

  - $SEAT/probe/corpus/SOURCES.md (copy)
  - $SEAT/probe/corpus/knowledge -> symlink to lane corpus/knowledge
  - Any other used-by dirs? Check what directories used-by paths use. Let me grep used-by cells: 11th column of mined rows. They're probably all corpus/knowledge/*.md. Check quickly.

  Also note: the separator/header rows use `separator_row()` — fine.

  Also there may be a wrinkle: rows before "## Registry"? The full lane registry has other sections maybe. E12 fires for row-shaped lines outside Registry that look like S-rows. Since I copy the whole file, content is identical to lane, which presumably validates clean. Fine.

  Also `--file` mode: lane name is "file" in output. Baseline expect: `file	ok	<path>` exit 0.

  Mutation: insert pipe in S328 scope cell. Expected: E01 S328 fields=12, exit 1. Note the parser also prints E02 if id !~ — id fine. Note: with NF=14, subsequent cells shift: tier=$5 still A (pipe inserted in scope cell ($6) → $6 and $7 split, shifting anchor... opened=trim($10) becomes part of scope, so E08 might fire too (opened="2026-10-24" moved to $11... let me count.

  Columns (after -F'|'): $1="" $2=id $3=source $4=kind $5=tier $6=scope $7=anchor $8=teaches $9=status $10=opened $11=recheck $12=used-by $13="".

  If I insert pipe in the scope cell: scope splits into two fields: $6="the published SGLang " $7="native-API route list...". Then anchor=$7, teaches=$8, status=$9, opened=$10, recheck=$11, usedby=$12 — all shifted by one: status now = anchor value "§..."? S328's anchor cell: "line 6 and route-list line 9 — ..." So shifted: $9 (parsed as status) = anchor text, $10 (opened) = teaches text, etc. The parser prints E01 and `next`s immediately for NF!=13 — no further checks for that row (E05/E06/etc. skipped). Only E01 (and E02 if id malformed). Good: clean single finding.

  But also: the shifted row could affect dedup maps? No — it `next`s before seen[id] etc. Wait: E01 branch: prints E01, maybe E02, then `next`. So seen[id] not set — no side effects.

  Also url_of uses source $3 unchanged. W04 unaffected.

  Also census row count: rows++ happens before mode check, so census would still count it; but we run validate only. Fine — could optionally also run census to note rows unchanged (a coverage note). The task only asks validate. Keep focused, but a quick census row count on pristine vs mutated is a cheap extra axis: mutated row still counted in census → census does NOT catch it. That's a genuine secondary finding worth one command. Actually the task says "Say whether the census catches the broken column count" — "the census" here means the census script (sources-census.sh), i.e., does `validate` catch it. But running `census` mode too clarifies both readings cheaply. Do both: validate (primary) and census rows count (pristine vs mutated).

  used-by dirs: let me check distinct used-by path prefixes to know what to mirror. Quick grep of 11th field... simpler: after running pristine baseline, if E11s appear, mirror more. But better to check first. Used-by values are corpus/knowledge/... almost surely (usedby_findings splits on comma too). Let me check unique prefixes.

  Plan commands (parallel batch 1):
  1. Extract used-by prefixes: awk to list distinct used-by values from mined rows.
  2. Nothing else needed.

  Then batch 2: build probe tree, run pristine, mutate, run mutated, restore, rerun, hashes.

  Let me also record the exact mutant line diff for the report.

  Let me write the whole thing as one bash script with outputs tee'd into seat files. Careful with `set -e` — I want exit codes captured; use `; rc=$?` pattern.

  Script:

  ```bash
  set -u
  SEAT=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-36/w3/out/MutRowPipe
  LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
  CENSUS=/home/vgpnk/Projects/shokunin/scripts/sources-census.sh

  # probe tree mirrors lane layout so used-by paths resolve
  mkdir -p "$SEAT/probe/corpus"
  ln -sfn "$LANE/corpus/knowledge" "$SEAT/probe/corpus/knowledge"
  cp "$LANE/corpus/SOURCES.md" "$SEAT/probe/corpus/SOURCES.md"
  sha256sum "$LANE/corpus/SOURCES.md" | tee "$SEAT/lane.before.sha256"

  # 1. pristine baseline
  bash "$CENSUS" validate --file "$SEAT/probe/corpus/SOURCES.md" > "$SEAT/pristine.validate.out" 2>&1
  echo "pristine validate exit=$?" | tee -a "$SEAT/pristine.validate.out"
  cat "$SEAT/pristine.validate.out"

  # 2. mutate: literal pipe inside one cell (S328 scope cell)
  python3 - "$SEAT/probe/corpus/SOURCES.md" <<'EOF'
  import sys
  p = sys.argv[1]
  s = open(p, encoding='utf-8').read()
  old = "the published SGLang native-API route list"
  assert s.count(old) == 1, s.count(old)
  s = s.replace(old, "the published SGLang |native-API route list")
  open(p, 'w', encoding='utf-8').write(s)
  EOF
  sha256sum "$SEAT/probe/corpus/SOURCES.md" | tee "$SEAT/mutated.sha256"

  # 3. mutated run
  bash "$CENSUS" validate --file "$SEAT/probe/corpus/SOURCES.md" > "$SEAT/mutated.validate.out" 2>&1
  echo "mutated validate exit=$?" | tee -a "$SEAT/mutated.validate.out"
  cat "$SEAT/mutated.validate.out"

  # also census row count on mutated
  bash "$CENSUS" census --file "$SEAT/probe/corpus/SOURCES.md" > "$SEAT/mutated.census.out" 2>&1
  echo "mutated census exit=$?" | tee -a "$SEAT/mutated.census.out"

  # 4. restore exact bytes
  cp "$LANE/corpus/SOURCES.md" "$SEAT/probe/corpus/SOURCES.md"
  sha256sum "$SEAT/probe/corpus/SOURCES.md" "$LANE/corpus/SOURCES.md" | tee "$SEAT/restored.sha256"

  # 5. restored run
  bash "$CENSUS" validate --file "$SEAT/probe/corpus/SOURCES.md" > "$SEAT/restored.validate.out" 2>&1
  echo "restored validate exit=$?" | tee -a "$SEAT/restored.validate.out"

  # 6. pristine census rows for comparison
  bash "$CENSUS" census --file "$SEAT/probe/corpus/SOURCES.md" > "$SEAT/restored.census.out" 2>&1
  echo "restored census exit=$?" >> "$SEAT/restored.census.out"

  # lane untouched evidence
  sha256sum "$LANE/corpus/SOURCES.md" | tee "$SEAT/lane.after.sha256"
  diff "$SEAT/lane.before.sha256" "$SEAT/lane.after.sha256" && echo "LANE UNTOUCHED"
  ```

  One issue: ln -sfn knowledge symlink — if used-by paths include other dirs (corpus/lessons?), E11 will fire. Check used-by prefixes first. Let me first run the used-by scan, then the main script. Two sequential batches (dependency).

  Actually let me combine: run used-by scan first in its own quick call, then the main script. Batch 1: the awk scan. Also grep distinct used-by values:

  awk -F'|' '$9 ~ /mined/ ...' hmm simpler: grep for rows and print last-but-one field. Use gawk: -F'|' NF==13 && trim($9)=="mined" print $12. Let me just run:

  gawk -F'|' '/^\s*\| S[0-9]/ {gsub(/^[ \t]+|[ \t]+$/,"",$12); print $12}' SOURCES.md | sort -u | head

  Wait field indexes: $2=id ... $12=used-by. Yes.

  Then cut prefix: cut -d/ -f1-2.

• AGENTS.md read — noted: census via `scripts/sources-census.sh`, evidence = re-executed commands, exit codes are contract. The parser contract is clear: rows parsed with `gawk -F'|'`, a valid row must have `NF==13` (11 cells), else **E01 malformed row**. Now I'll check what used-by paths exist (so my seat copy gets a clean baseline), then build the probe.     30 corpus/knowledge
     27 corpus/lessons
      1 used-by
      1 SKILL.md, registry/request-field-outcomes-r28.json, corpus
      1 SKILL.md, registry/error-signatures-r26.json
      1 SKILL.md
      1 —
      1 ---


• Used-by paths reference corpus/knowledge, corpus/lessons, SKILL.md, and registry/*.json (relative to lane root). My probe dir must mirror: probe/corpus/knowledge, probe/corpus/lessons, probe/SKILL.md, probe/registry. Symlinks to the lane (read-only usage) solve all of them:

  - ln -sfn $LANE/corpus/knowledge $SEAT/probe/corpus/knowledge
  - ln -sfn $LANE/corpus/lessons $SEAT/probe/corpus/lessons
  - ln -sfn $LANE/SKILL.md $SEAT/probe/SKILL.md
  - ln -sfn $LANE/registry $SEAT/probe/registry

  Then pristine baseline should be clean (exit 0, "file ok ...").

  Run the full probe script now.

• All used-by targets resolve to `corpus/knowledge`, `corpus/lessons`, `SKILL.md`, `registry/` — I'll mirror those with read-only symlinks into my seat probe tree so the pristine baseline is clean. Now the full probe: baseline → mutate → detect → restore → re-verify.
=== PRISTINE ===
file	W04	S031 duplicate url docs.ollama.com/api/tags across scopes
file	W04	S043 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp across scopes
file	W04	S056 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/arg.cpp across scopes
file	W04	S060 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S064 duplicate url docs.python.org/3.14/library/subprocess.html across scopes
file	W04	S065 duplicate url docs.python.org/3.14/library/sys.html across scopes
file	W04	S067 duplicate url man7.org/linux/man-pages/man8/ld.so.8.html across scopes
file	W04	S071 duplicate url git-scm.com/docs/git-cat-file across scopes
file	W04	S077 duplicate url docs.python.org/3.14/library/os.html across scopes
file	W04	S078 duplicate url man7.org/linux/man-pages/man8/ldconfig.8.html across scopes
file	W04	S079 duplicate url man7.org/linux/man-pages/man8/ld.so.8.html across scopes
file	W04	S080 duplicate url nix.dev/manual/nix/2.34/protocols/nix-archive across scopes
file	W04	S081 duplicate url go.googlesource.com/mod/+/refs/tags/v0.42.0/sumdb/dirhash/hash.go across scopes
file	W04	S082 duplicate url git-scm.com/docs/gitrevisions across scopes
file	W04	S083 duplicate url git-scm.com/docs/git-cat-file across scopes
file	W04	S084 duplicate url docs.jj-vcs.dev/latest/cli-reference across scopes
file	W04	S085 duplicate url git-scm.com/docs/git-log across scopes
file	W04	S086 duplicate url tldp.org/HOWTO/Program-Library-HOWTO/shared-libraries.html across scopes
file	W04	S087 duplicate url docs.python.org/3.14/builtins/functions.html across scopes
file	W04	S088 duplicate url docs.python.org/3.14/library/os.html across scopes
file	W04	S093 duplicate url git-scm.com/docs/git-log across scopes
file	W04	S097 duplicate url docs.python.org/3.14/library/subprocess.html across scopes
file	W04	S100 duplicate url git-scm.com/docs/git-config across scopes
file	W04	S103 duplicate url git-scm.com/docs/partial-clone across scopes
file	W04	S105 duplicate url docs.python.org/3.14/builtins/stdtypes.html across scopes
file	W04	S108 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp across scopes
file	W04	S109 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S110 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/arg.cpp across scopes
file	W04	S112 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md across scopes
file	W04	S114 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S115 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S116 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S117 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S118 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S119 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S120 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S121 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S122 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S123 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S124 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S125 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S127 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S129 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/ggml/src/gguf.cpp across scopes
file	W04	S130 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-context.cpp across scopes
file	W04	S131 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/fit.cpp across scopes
file	W04	S132 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-context.cpp across scopes
file	W04	S133 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S134 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md across scopes
file	W04	S135 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-kv-cache.cpp across scopes
file	W04	S137 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S141 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S142 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S143 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S144 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S145 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S146 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S147 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S148 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S149 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S150 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S151 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S152 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S153 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S154 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S155 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S156 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S157 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S158 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S159 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S160 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S161 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S162 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S163 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S164 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S165 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S166 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S167 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S168 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S169 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S170 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S171 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S172 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S173 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S181 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S182 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S183 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S184 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S185 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S186 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S187 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S188 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S189 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S191 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	E11	S057 missing used-by SCORECARD.md
file	E11	S089 missing used-by tools/report-landing-audit.py
file	E11	S091 missing used-by tools/report-landing-audit.py
file	E11	S096 missing used-by tools/report-landing-audit.py
file	E11	S100 missing used-by tools/report-landing-audit.py
file	E11	S100 missing used-by tests/report-audit/repo-state-grid.py
file	E11	S101 missing used-by tools/report-landing-audit.py
file	E11	S102 missing used-by tools/report-landing-audit.py
file	E11	S102 missing used-by tests/report-audit/promisor-grid.py
file	E11	S103 missing used-by tests/report-audit/promisor-grid.py
file	E11	S174 missing used-by .ufo/waves/round-29/count-c1.py
file	E11	S175 missing used-by .ufo/waves/round-29/count-c1.py
file	E11	S176 missing used-by .ufo/waves/round-29/count-c1.py
file	E11	S177 missing used-by .ufo/waves/round-29/count-c1.py
pristine_validate_exit=1

=== MUTATED validate ===
file	W04	S031 duplicate url docs.ollama.com/api/tags across scopes
file	W04	S043 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp across scopes
file	W04	S056 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/arg.cpp across scopes
file	W04	S060 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S064 duplicate url docs.python.org/3.14/library/subprocess.html across scopes
file	W04	S065 duplicate url docs.python.org/3.14/library/sys.html across scopes
file	W04	S067 duplicate url man7.org/linux/man-pages/man8/ld.so.8.html across scopes
file	W04	S071 duplicate url git-scm.com/docs/git-cat-file across scopes
file	W04	S077 duplicate url docs.python.org/3.14/library/os.html across scopes
file	W04	S078 duplicate url man7.org/linux/man-pages/man8/ldconfig.8.html across scopes
file	W04	S079 duplicate url man7.org/linux/man-pages/man8/ld.so.8.html across scopes
file	W04	S080 duplicate url nix.dev/manual/nix/2.34/protocols/nix-archive across scopes
file	W04	S081 duplicate url go.googlesource.com/mod/+/refs/tags/v0.42.0/sumdb/dirhash/hash.go across scopes
file	W04	S082 duplicate url git-scm.com/docs/gitrevisions across scopes
file	W04	S083 duplicate url git-scm.com/docs/git-cat-file across scopes
file	W04	S084 duplicate url docs.jj-vcs.dev/latest/cli-reference across scopes
file	W04	S085 duplicate url git-scm.com/docs/git-log across scopes
file	W04	S086 duplicate url tldp.org/HOWTO/Program-Library-HOWTO/shared-libraries.html across scopes
file	W04	S087 duplicate url docs.python.org/3.14/builtins/functions.html across scopes
file	W04	S088 duplicate url docs.python.org/3.14/library/os.html across scopes
file	W04	S093 duplicate url git-scm.com/docs/git-log across scopes
file	W04	S097 duplicate url docs.python.org/3.14/library/subprocess.html across scopes
file	W04	S100 duplicate url git-scm.com/docs/git-config across scopes
file	W04	S103 duplicate url git-scm.com/docs/partial-clone across scopes
file	W04	S105 duplicate url docs.python.org/3.14/builtins/stdtypes.html across scopes
file	W04	S108 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp across scopes
file	W04	S109 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S110 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/arg.cpp across scopes
file	W04	S112 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md across scopes
file	W04	S114 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S115 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S116 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S117 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S118 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S119 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S120 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S121 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S122 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S123 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S124 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S125 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S127 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S129 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/ggml/src/gguf.cpp across scopes
file	W04	S130 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-context.cpp across scopes
file	W04	S131 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/fit.cpp across scopes
file	W04	S132 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-context.cpp across scopes
file	W04	S133 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S134 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md across scopes
file	W04	S135 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-kv-cache.cpp across scopes
file	W04	S137 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S141 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S142 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S143 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S144 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S145 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S146 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S147 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S148 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S149 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S150 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S151 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S152 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S153 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S154 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S155 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S156 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S157 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S158 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S159 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S160 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S161 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S162 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S163 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S164 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S165 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S166 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S167 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S168 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S169 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S170 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S171 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S172 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S173 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S181 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S182 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S183 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S184 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S185 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S186 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S187 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S188 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S189 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S191 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	E01	S328 fields=12
file	E11	S057 missing used-by SCORECARD.md
file	E11	S089 missing used-by tools/report-landing-audit.py
file	E11	S091 missing used-by tools/report-landing-audit.py
file	E11	S096 missing used-by tools/report-landing-audit.py
file	E11	S100 missing used-by tools/report-landing-audit.py
file	E11	S100 missing used-by tests/report-audit/repo-state-grid.py
file	E11	S101 missing used-by tools/report-landing-audit.py
file	E11	S102 missing used-by tools/report-landing-audit.py
file	E11	S102 missing used-by tests/report-audit/promisor-grid.py
file	E11	S103 missing used-by tests/report-audit/promisor-grid.py
file	E11	S174 missing used-by .ufo/waves/round-29/count-c1.py
file	E11	S175 missing used-by .ufo/waves/round-29/count-c1.py
file	E11	S176 missing used-by .ufo/waves/round-29/count-c1.py
file	E11	S177 missing used-by .ufo/waves/round-29/count-c1.py
mutated_validate_exit=1

=== MUTATED census ===
file	rows	203
file	tier.A	194
file	tier.B	6
file	tier.C	3
file	status.mined	183
file	status.invalid	1
file	status.queued	8
file	status.rejected	11
FLEET	rows	203
FLEET	tier.A	194
FLEET	tier.B	6
FLEET	tier.C	3
FLEET	tier.invalid	0
FLEET	status.queued	8
FLEET	status.mined	183
FLEET	status.rejected	11
FLEET	status.invalid	1
FLEET	missing	0
mutated_census_exit=0

=== RESTORED validate ===
file	W04	S031 duplicate url docs.ollama.com/api/tags across scopes
file	W04	S043 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp across scopes
file	W04	S056 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/arg.cpp across scopes
file	W04	S060 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S064 duplicate url docs.python.org/3.14/library/subprocess.html across scopes
file	W04	S065 duplicate url docs.python.org/3.14/library/sys.html across scopes
file	W04	S067 duplicate url man7.org/linux/man-pages/man8/ld.so.8.html across scopes
file	W04	S071 duplicate url git-scm.com/docs/git-cat-file across scopes
file	W04	S077 duplicate url docs.python.org/3.14/library/os.html across scopes
file	W04	S078 duplicate url man7.org/linux/man-pages/man8/ldconfig.8.html across scopes
file	W04	S079 duplicate url man7.org/linux/man-pages/man8/ld.so.8.html across scopes
file	W04	S080 duplicate url nix.dev/manual/nix/2.34/protocols/nix-archive across scopes
file	W04	S081 duplicate url go.googlesource.com/mod/+/refs/tags/v0.42.0/sumdb/dirhash/hash.go across scopes
file	W04	S082 duplicate url git-scm.com/docs/gitrevisions across scopes
file	W04	S083 duplicate url git-scm.com/docs/git-cat-file across scopes
file	W04	S084 duplicate url docs.jj-vcs.dev/latest/cli-reference across scopes
file	W04	S085 duplicate url git-scm.com/docs/git-log across scopes
file	W04	S086 duplicate url tldp.org/HOWTO/Program-Library-HOWTO/shared-libraries.html across scopes
file	W04	S087 duplicate url docs.python.org/3.14/builtins/functions.html across scopes
file	W04	S088 duplicate url docs.python.org/3.14/library/os.html across scopes
file	W04	S093 duplicate url git-scm.com/docs/git-log across scopes
file	W04	S097 duplicate url docs.python.org/3.14/library/subprocess.html across scopes
file	W04	S100 duplicate url git-scm.com/docs/git-config across scopes
file	W04	S103 duplicate url git-scm.com/docs/partial-clone across scopes
file	W04	S105 duplicate url docs.python.org/3.14/builtins/stdtypes.html across scopes
file	W04	S108 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp across scopes
file	W04	S109 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S110 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/arg.cpp across scopes
file	W04	S112 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md across scopes
file	W04	S114 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S115 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S116 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S117 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S118 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S119 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S120 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S121 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S122 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S123 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S124 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S125 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S127 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S129 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/ggml/src/gguf.cpp across scopes
file	W04	S130 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-context.cpp across scopes
file	W04	S131 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/fit.cpp across scopes
file	W04	S132 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-context.cpp across scopes
file	W04	S133 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
file	W04	S134 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md across scopes
file	W04	S135 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-kv-cache.cpp across scopes
file	W04	S137 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S141 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S142 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S143 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S144 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S145 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S146 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S147 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S148 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S149 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S150 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S151 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S152 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S153 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S154 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S155 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S156 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S157 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S158 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S159 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S160 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S161 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S162 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S163 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S164 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S165 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S166 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S167 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S168 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S169 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S170 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S171 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S172 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S173 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	W04	S181 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S182 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S183 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S184 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S185 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S186 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S187 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S188 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S189 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
file	W04	S191 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	E11	S057 missing used-by SCORECARD.md
file	E11	S089 missing used-by tools/report-landing-audit.py
file	E11	S091 missing used-by tools/report-landing-audit.py
file	E11	S096 missing used-by tools/report-landing-audit.py
file	E11	S100 missing used-by tools/report-landing-audit.py
file	E11	S100 missing used-by tests/report-audit/repo-state-grid.py
file	E11	S101 missing used-by tools/report-landing-audit.py
file	E11	S102 missing used-by tools/report-landing-audit.py
file	E11	S102 missing used-by tests/report-audit/promisor-grid.py
file	E11	S103 missing used-by tests/report-audit/promisor-grid.py
file	E11	S174 missing used-by .ufo/waves/round-29/count-c1.py
file	E11	S175 missing used-by .ufo/waves/round-29/count-c1.py
file	E11	S176 missing used-by .ufo/waves/round-29/count-c1.py
file	E11	S177 missing used-by .ufo/waves/round-29/count-c1.py
restored_validate_exit=1

=== RESTORED census ===
file	rows	203
file	tier.A	194
file	tier.B	6
file	tier.C	3
file	status.mined	184
file	status.queued	8
file	status.rejected	11
FLEET	rows	203
FLEET	tier.A	194
FLEET	tier.B	6
FLEET	tier.C	3
FLEET	tier.invalid	0
FLEET	status.queued	8
FLEET	status.mined	184
FLEET	status.rejected	11
FLEET	status.invalid	0
FLEET	missing	0
restored_census_exit=0

=== HASHES ===
1e44b4f314f2eb7f671feb537d03030af145713d484cbd326017fcbb5a83e8fe  /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
6b21d9f46c2141e4c55846ca04faf6e36a191979ff016fb51e62b1c4f8da190b  /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-36/w3/out/MutRowPipe/probe/corpus/SOURCES.md
1e44b4f314f2eb7f671feb537d03030af145713d484cbd326017fcbb5a83e8fe  /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-36/w3/out/MutRowPipe/probe/corpus/SOURCES.md
1e44b4f314f2eb7f671feb537d03030af145713d484cbd326017fcbb5a83e8fe  /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
1e44b4f314f2eb7f671feb537d03030af145713d484cbd326017fcbb5a83e8fe  /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
LANE_REGISTRY_UNTOUCHED


• Results analysis:

  **Pristine baseline:** exit 1, but only W04 warnings + 14 E11 findings. The E11s are baseline noise caused by my probe location: used-by paths like `tools/report-landing-audit.py`, `SCORECARD.md`, `.ufo/waves/round-29/count-c1.py` resolve relative to `$dir` = probe root, and those live at the lane root, not under my seat probe. I symlinked corpus/knowledge, corpus/lessons, SKILL.md, registry — but not tools/, tests/, SCORECARD.md, .ufo/. So the pristine baseline is NOT clean — it has 14 E11 errors.

  Per protocol: "A baseline failure is inconclusive, not a killed mutant." However, the finding here is precise: the E01 finding for S328 appears ONLY in the mutated run, and disappears in restored. The E01 detector did fire. But to be rigorous, I should fix the baseline to be clean by mirroring the remaining used-by roots: tools/, tests/, SCORECARD.md, .ufo/waves/round-29/count-c1.py (i.e., .ufo/). Symlink the whole lane tree? Simplest: symlink the missing roots: tools, tests, SCORECARD.md, .ufo. Then the pristine baseline should be truly clean (exit 0, "file ok ...").

  Wait, also mutated census showed `status.invalid 1` — that's because the S328 row with the extra pipe shifted cells: status parsed from wrong column → invalid, tier parsed from $5 which is still tier... tier.A count 194 same; status.invalid 1 in mutated census vs 0 in restored. And rows still 203 in both — census mode does NOT flag the broken row; it just misclassifies it (status.invalid 1). That's a genuine secondary finding: `census` mode has no E01 equivalent; the row is still counted (rows 203), and only distorts the status histogram (status.mined 183 vs 184, status.invalid 1 vs 0).

  Note interesting: in mutated census, tier.A still 194 — because tier=$5 unchanged (pipe inserted in scope cell $6). Good.

  Now improve: make baseline clean. Add symlinks: tools → lane/tools, tests → lane/tests, SCORECARD.md → lane/SCORECARD.md, .ufo → lane/.ufo. Then re-run the three-phase probe (pristine/mutate/restore). This is cheap and gives the definitive "killed" verdict with a clean baseline.

  Wait — caution: `.ufo` symlink to lane's .ufo — read-only use, fine. E11 check is `[ ! -e "$dir/$path" ]` — just existence check.

  Also verify there are no other used-by roots I missed: the uniq -c list showed: corpus/knowledge, corpus/lessons, SKILL.md (3 variants incl. combined lists), registry/*.json (in combined "SKILL.md, registry/..., corpus" — wait one entry was "SKILL.md, registry/request-field-outcomes-r28.json, corpus" — cut -d/ -f1-2 of "SKILL.md, registry" gives "SKILL.md," hmm the comma-lists complicate. The full used-by list for that row includes "corpus/..." something as third item. My prefix scan on comma-split items would catch corpus/knowledge or corpus/lessons anyway. But let me be thorough: comma-split used-by values and get first path component of each. Quick check, then rebuild symlinks and re-run.

  Also one subtlety: E11 for S057 "SCORECARD.md" → need $SEAT/probe/SCORECARD.md. And "tools/report-landing-audit.py" → $SEAT/probe/tools. "tests/report-audit/..." → $SEAT/probe/tests. ".ufo/waves/round-29/count-c1.py" → $SEAT/probe/.ufo.

  After symlinks, pristine should be exit 0 with `file	ok	<path>`.

  Then the definitive result:
  - pristine: exit 0, ok
  - mutated: exit 1, `file	E01	S328	fields=12` (plus baseline W04 warnings which are warnings, exit 0-worthy; the E11s should vanish)
  - restored: exit 0, ok
  - hashes: mutated 6b21d9f4..., restored == lane 1e44b4f3...

  Let me also capture the mutated row for the report — diff pristine vs mutated copy (one line change). And save diff output.

  Then write the report. Axes (Godspeed): detection power (E01 fired = killed), baseline cleanliness (fixed), no collateral damage (lane untouched, only seat writes).

  Run now: symlink completion + full re-probe. Also produce `mutant.diff` and check comma-split used-by roots in the same script (before the probe, assert coverage).

• E01 fired on the mutant (`file E01 S328 fields=12`), but my pristine baseline is **not clean** — 14 E11s because used-by roots `tools/`, `tests/`, `SCORECARD.md`, `.ufo/` resolve against the probe dir. Baseline failure = inconclusive, so I'm completing the mirror and re-running the three-phase probe to get a conclusive verdict. Also noted: `census` mode still counted the broken row (rows 203 both ways, but `status.invalid 1` vs `0`).used-by roots:
---
corpus
registry
SCORECARD.md
SKILL.md
tests
tools
.ufo
=== PRISTINE (tail) ===
file	W04	S191 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	ok	/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-36/w3/out/MutRowPipe/probe/corpus/SOURCES.md
pristine_validate_exit=0
95
=== MUTATED (E-findings + tail) ===
file	E01	S328 fields=12
file	E01	S328 fields=12
mutated_validate_exit=1
95
=== RESTORED (tail) ===
file	W04	S191 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
file	ok	/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-36/w3/out/MutRowPipe/probe/corpus/SOURCES.md
restored_validate_exit=0
95
=== HASHES ===
1e44b4f314f2eb7f671feb537d03030af145713d484cbd326017fcbb5a83e8fe  /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
1e44b4f314f2eb7f671feb537d03030af145713d484cbd326017fcbb5a83e8fe  /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-36/w3/out/MutRowPipe/pristine.copy.for-diff.md
6b21d9f46c2141e4c55846ca04faf6e36a191979ff016fb51e62b1c4f8da190b  /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-36/w3/out/MutRowPipe/probe/corpus/SOURCES.md
1e44b4f314f2eb7f671feb537d03030af145713d484cbd326017fcbb5a83e8fe  /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-36/w3/out/MutRowPipe/probe/corpus/SOURCES.md
1e44b4f314f2eb7f671feb537d03030af145713d484cbd326017fcbb5a83e8fe  /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
1e44b4f314f2eb7f671feb537d03030af145713d484cbd326017fcbb5a83e8fe  /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
LANE_REGISTRY_UNTOUCHED


• Clean and conclusive now:

  - **Pristine**: exit 0, `file ok <path>` (95 lines: 94 W04 warnings + ok line). Baseline clean (E-findings: none).
  - **Mutated**: exit 1, exactly one E-finding: `file E01 S328 fields=12` (appears twice in output because validate emits the E-line twice — once in the grep pass, once... actually looking at the script: in validate mode, `out` is printed once via `grep -E '\t[EW][0-9]+\t' | out_sink`. Hmm why twice? The grep in my shell command `grep -P '\tE[0-9]+\t'` printed two lines... Both lines are from the output file, and wc says 95 lines — same as pristine (94 W04 + ok). Wait pristine = 95 lines: 94 W04 + 1 ok. Mutated = 95 lines: 94 W04 + 1 E01 = 95. But grep printed the E01 line twice? That's odd.

