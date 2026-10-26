# S9Quality — round 49 criteria draft (KQ76–KQ79): met, with three stated limits

**Verdict: KQ76–KQ79 drafted from the round-49 build `74558c71` and every `Check:` in them was run by this seat at that commit (C1 `met=True` exit 0, C2 `met=True` exit 0, filed-once check `met=True` on six rounds / `met=False` on round 48, census-sentence check both ways). No defect in the frozen counters, preregistration or controls; the three limits below are the build's own and are written into the criteria rather than left as room for a later shortcut.**

## What I ran (all at `/home/vgpnk/Projects/shokunin/kama-shokunin` tools against my own clone)

Scratch `S=/fast/scratch/hyaku/kama-r49/S9Quality`; clone `git clone -q --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane` (HEAD `122c4ee9`, 334 MB; the build `74558c71` is its parent chain). Nothing in the lane, the fleet repo or jj was written.

1. C1 execution-witness counter, tip `74558c71c38ceaeace15fd4cf8aa9d84977584b1`:
   `python3 tools/round49-replay-witness-audit.py --repo $S/lane --tip 74558c71… --scratch $S/c1 --out …/S9Quality/c1-build.out` → exit 0, 12.2 s wall:
   ```
   witness=1 cap=1 newrow=1 witnessed=3/3 met=True
   detail: witness w1: pid 367081 port 39457 exe+listen+model ok, nonce 'kama witness 03693b02de845a8e' round-tripped
   detail: witness w2: pid 374915 port 40017 exe+listen+model ok, nonce 'kama witness 6f1a9c44d5577e90' round-tripped
   detail: witness w3: pid 381357 port 44641 exe+listen+model ok, nonce 'kama witness 3c83f7352f9355e6' round-tripped
   detail: cap sparse-1e15: exit 2 setup_error 'provenance-member-sparse' executed=False seconds=0.1 ok
   detail: cap member-is-server-control: exit 2 setup_error 'server-exited-early-rc3' executed=True seconds=0.1 ok
   detail: newrow: 2 rows new since base; 1 name the README at caa8191df159 and /tokenize: ['| S494 |']
   ```
   Pids and nonces differ from L1's measured receipt (`.ufo/waves/round-49/measured/c1-build.out`, same three legs); the counter spawned three `llama-server` children on loopback and `pgrep -af llama-server` after the run shows none of mine (only peer `X1Offline`'s two, scratch `/fast/scratch/hyaku/kama-r49/X1Offline`).
2. C2 append-audit-v4 counter, same tip: `python3 tools/round49-append-audit-v4-check.py --repo $S/lane --tip 74558c71… --scratch $S/c2 --out …/S9Quality/c2-build.out` → exit 0, 4.3 s:
   ```
   fixture=1 lane=1 scenarios=8/8 met=True
   detail: lane: tool exit 0 events 5 bad_declarations 0 regressed 0 ungraded_lines 82
   detail: lane: event 0718b6abbda6 SCORECARD.md ungraded 65 <= natively exempt 65
   ```
   Reproduces L1's measured output verbatim.
3. Filed-once + census checks for KQ79 (my own, `.ufo/waves/round-49/w1/out/S9Quality/report-filed-once.out`, `census-sentence.out`):
   - `report-filed-once.py` over `.ufo/reports/round-<N>/kama.md` in the fleet repo with each round's last lane commit as tip: rounds 42–47 `adds=1 rewrites=0 … met=True` exit 0; round 48 `adds=1 rewrites=1 met=False` exit 1 (`add=15710a2a`, rewrite `dcc079e7`, 58 s later — the exact round-48 closure R2 defect).
   - `census-summary-check.py` (frozen from round 44) against round 49's own start census `.ufo/waves/round-49/census/start.out` (`receipt=W01=1 W04=93`): sentence `93 W04, 0 E` → `missing class W01: receipt has 1`, `met=False` exit 1; sentence `93 W04, 1 W01, 0 E` → `met=True` exit 0.
4. Binding-rule probe (KQ78 limits), importing `tools/append-only-audit.py` from its blob **at the build** into scratch and calling `binds()` directly (`negation-window.out`):
   ```
   'LOG.md is append-only' binds_LOG= True
   'the catalog is append-only' binds_LOG= False
   'LOG.md is not strictly append-only' binds_LOG= False
   'LOG.md is not, in any meaningful sense, append-only' binds_LOG= True
   'log-rotation is append-only' binds_LOG= True
   'logrotation is append only' binds_LOG= False
   'LOG.md is appended-only' binds_LOG= False
   ```

## Deliverable

`.ufo/waves/round-49/w1/out/S9Quality/criteria.md` — four rows, same columns as KQ69–KQ75, section header `## Criteria added — round 49 (each cites corpus/lessons/round-49.md)`, footer naming what each supplements. Line pointers name build `74558c71` only (`git show 74558c71:<path>`), as the round-48 block does.

- **KQ76 execution evidence** — a replay counts as having run a server only when an outside observer sees the recorded binary as the listener, the recorded model as `-m`, and a fresh nonce answered by `/tokenize`/`/detokenize` against its own vocab decoding, then sees the pid gone; the replay records only what it knows (`ready.json`, `released`, `waited_ms`); archive-member verification is bounded before hashing. Pointers `tools/kama-llamacpp-live.py:277`, `:280-300`, `:208-212`, `:232`–`:263`; `tools/kama-live-replay.py:275-281`, `:450-453`; rows S494/S495.
- **KQ77 origin-aware carve-outs** — exemption covers text born in the exempt region; `origin(l)` and the v4 ungraded rule at `tools/append-only-audit.py:423-441`, `:465-475`, `:384-394`.
- **KQ78 declarations** — whole-word token (`:202-207`), three-word negation window (`:212-214`), wildcard rows bind only through a naming line (`:216-231`).
- **KQ79 report precision** — filed once after the cited final lane commit, corrections through `registry/report-landing-errata.tsv`, census tally quoted whole. Names my `report-filed-once.py` and the frozen `census-summary-check.py`, both demonstrated able to fail and to pass.

## Findings (limits written into the criteria)

1. **Negation window is exactly three words** (`tools/append-only-audit.py:212-214`, `NEG_WINDOW` `{0,3}?`): `LOG.md is not, in any meaningful sense, append-only` **binds** at the v4 build — the hedge hatch is narrower than v3 but not closed. Not a defect against the frozen predicate (the preregistration's C2 statement says "negations within three words of append-only unbind"), a limit of the rule. Command: the probe in §4.
2. **Token whole-word boundary is `[a-z0-9_]`** (`:229`): a token inside a hyphen-joined compound counts as present (`log-rotation is append-only` binds `LOG.md`), and only `append-only` / `append only` are accepted spellings (`:227`), so `appended-only` binds nothing. Written into KQ78.
3. **"Final lane tip" needs the tip the report cites, not the last round-prefixed commit**: round 47's report passes the after-tip leg against `383f1fc7` and fails against `6b7e6cf8` ("round-47: late seat report revisions"), which postdates the report by design. KQ79's limit says so, so the criterion cannot be gamed by filing before a late seat-report commit.
4. C1's disclosed limits are restated in KQ76 rather than treated as closed: the witness does not bind the executing binary to the downloaded archive at replay time, `/proc/<pid>/exe` is Linux-only and fails closed, and a different model of the same architecture would fail on the `-m` digest leg, not on the pieces.

## Out of scope / not done

- No edit to `corpus/QUALITY.md`, the counters, the preregistration, the controls, the lessons or any lane file: the criteria text is a proposed append in my out dir for the L1 to integrate (KQ67 makes QUALITY.md append-only; the block is a pure append).
- Not re-reported: the two round-49 counters missing from the SKILL instrument registry; SCORECARD/LOG/lesson/QUALITY/README round-49 entries; `used-by` of S494/S495 naming `corpus/lessons/round-49.md`.
- No tool installed or upgraded (nothing was needed; no pacman run). No `gh` request. No service started beyond the counter's own loopback servers, all torn down by the counter.

## Artifacts (all under `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Quality/`)

| file | content |
|---|---|
| `criteria.md` | the KQ76–KQ79 block |
| `c1-build.out`, `c1-run.log` | my C1 run at `74558c71` (`met=True`, exit 0) |
| `c2-build.out`, `c2-run.log` | my C2 run at `74558c71` (`met=True`, exit 0) |
| `report-filed-once.py`, `report-filed-once.out` | the KQ79 filed-once check and its run over rounds 42–48 |
| `census-sentence.out`, `sentence-dropped.txt`, `sentence-whole.txt` | the census whole-quote check both ways on round 49's start census |
| `negation-window.out` | the binding-rule probe (§4) |
