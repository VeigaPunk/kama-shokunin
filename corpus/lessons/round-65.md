# Round 65 lesson — kama (2026-10-31)

Fresh-start round on a new host: Windows 10.0.26200, Git Bash (MinGW64, git
2.55.0.windows.3), CPython 3.13.15 (`python`; `python3` is the Microsoft Store
alias stub that exits 49 with "Python was not found"). The former host's
llama-server/OMP endpoints are absent; the round's evidence is an honest
negative localhost census plus lane-local instruments run and repaired on this
host. Claims: C1 operability (host self-test census: the declared set runs
green at the landed tip after three portability repairs and the registration of
twenty unregistered counters), C2 calibration (PROVINCE.md made to match the
observed host, before `stale=9` → after `stale=0`). Sourced claim: C1 rests on
S537 (opened this round). Assimilation: none — shokuknow unreachable;
considerthese `2026-10-26.md` re-opened this round, no still-unimplemented
proposal adopted.

## Gate

| Row / candidate | Located quote (≤25 words) | Verdict |
|---|---|---|
| S537 `https://git-scm.com/docs/git-maintenance` | "This boolean config option controls whether some commands run git maintenance run --auto after doing their normal work. Defaults to true." (§CONFIGURATION, `maintenance.auto`) | **admit** — grounds C1's fixture repair: the new host's git ran background maintenance mid-selftest and packed fresh fixture objects; the fixture now pins `gc.auto=0` and `maintenance.auto=false` on every fixture repo. Fetched bytes sha256 `b1e301c1df74bb254b6c80a96935d84686cdc177c11c2e841ec5055872196cd4` retained at `.ufo/waves/round-65/source/git-maintenance.html`, accessed 2026-10-31 by `curl -s https://git-scm.com/docs/git-maintenance` |
| endpoint census (no row; host observation) | curl exit 7 (connection refused) on `127.0.0.1:8080/health`, `/v1/models`, `[::1]:8080/health`, `127.0.0.1:34113/health`, `127.0.0.1:11434/api/tags`; full `netstat -ano -p tcp` listen set holds no `8080`/`34113`/`11434` | **observed negative** — receipts `.ufo/waves/round-65/measured/endpoint-census.out`; `ollama` and `llama-server` absent from PATH; the three registered consumer rows keep `DEAD` |
| consumer surfaces (no row; host observation) | `~/.config/opencode/opencode.jsonc` parses to a single `$schema` key; `~/.omp/agent/settings.json` parses to a single `shellPath` key | **observed negative** — no provider block, no baseURL pin on this host; credential-like keys would have been redacted, none were present. Receipts `.ufo/waves/round-65/measured/consumer-surfaces.out`, `consumer-shape.out`, `omp-settings-shape.out` |

Registry rows 276 → 277 (`grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'
corpus/SOURCES.md`); one tier-A row added, none rejected, none flipped.

## Mistakes

Class · evidence pointer · captured-by · fix.

1. **fixture/loose-objects** · `tools/report-landing-audit.py --selftest` assumed a freshly committed blob stays a loose object; on this host the hole fixture's fresh blob was gone from loose storage at unlink time — a `multi-pack-index` and a cruft pack (`.mtimes`) sat in the fixture repo's objects directory and the blob existed only inside a pack (WinError 3, instrumented rerun `.ufo/waves/round-65/measured/rla-trace.txt`; mechanism grounded in S537) · captured-by the tool's own `could-not-evaluate` on the first host run · fix: the fixture's `hermetic()` helper pins `gc.auto=0`, `gc.autoDetach=false`, `maintenance.auto=false` on every fixture repo it creates; the audited audit logic is untouched and the selftest is green again (`selftest cases=79 failed=0`, exit 0).
2. **fixture/permissions** · the same fixture unlinks git-written loose objects; git writes them read-only and Windows refuses to unlink a read-only file (WinError 5, `Access is denied`) where POSIX unlinks it · captured-by the second host run of the same selftest after mistake 1's fix · fix: a `drop_loose()` helper clears the mode (`os.chmod 0o644`) before unlinking; a no-op-on-POSIX change.
3. **portability/os-sep** · two instruments compared forward-slash constants against paths built with the platform separator: `tools/digest-ledger.py`'s `is_doc()`/ledger match (so `.ufo\` documents leaked into the token set and the ledger file itself was scanned as a document: `selftest pass=3 fail=8`) and `tools/citation-provenance.py`'s `doc_bind` `endswith` (so the real lane run reported `missing=17` with `found=0`) · captured-by both tools' own selftests/runs on the new host · fix: normalize separators at the comparison boundary (`rel.replace(os.sep, "/")`, `str(t[0]).replace(os.sep, "/")`); POSIX behaviour unchanged.
4. **portability/platform-API** · `tools/digest-ledger.py` `hash_external()` built its `os.open` flags from `os.O_NOFOLLOW` and `os.O_NONBLOCK` unconditionally; neither exists on Windows Python, and `AttributeError` is not caught by the function's `except OSError` — a latent crash on any non-POSIX host, first triggered here · captured-by the repaired selftest reaching the external-hash arms · fix: `getattr(os, ...)` flags plus `os.O_BINARY` where present, with the docstring naming which refusal paths remain.
5. **environment/child-spawn** · `tools/citation-provenance.py`'s selftest spawned its CLI child with a minimal Linux env (`PATH=/usr/bin:/bin`, no `SystemRoot`); on Windows CreateProcess failed for every arm (`[WinError 2]`), so the CLI contract was untestable · captured-by the selftest's cli-* failures on the first host run · fix: `nt`-conditional loader keys and a resolvable PATH in the child env (the unusable-git arm still overrides PATH), plus `OSError` from the lane probe re-raised as a named `ValueError` so a missing git executable exits 2 with "git" in the message instead of a raw spawn error.
6. **process/registry-drift** · rounds 56-64 added twenty `tools/round*-*.py` counters without registering them in SKILL.md's instrument registry; `tools/gate-registry-check.py`'s own selftest (lane-tip arm) was not in any of those rounds' gate re-run sets, so the drift lived nine rounds (`registered 54 unregistered 20 defective 0` at base `3325e8ed86a5`) · captured-by the gate's own selftest run on this host · fix: all twenty counters registered in `SKILL.md` §"Round-56–64 instrument registry" with source-derived entry/exit facts and sha256 prefixes; the worktree gate prints `registered 74 unregistered 0 defective 0`; routed: the gate selftest belongs in every round whose instrument set changes.
7. **host-shape/NTFS** · the lane tracks a wave-artifact path containing `|` (`.ufo/waves/round-52/w1/out/c -l...`), which NTFS cannot check out; every instrument that clones the lane (`tools/round42-selfdesc-reconcile.py --selftest`) refuses with `error: invalid path` on this host · captured-by the reconciler selftest's could-not-evaluate · fix: none in this round — renaming rewrites the path of committed round-52 evidence, a history decision the lane does not make unilaterally; filed at `.ufo/l0-questions.md` (kama round-65) and pinned as a refusal marker in the host census.
8. **fixture/newline** · the citation-provenance fixture wrote the cited blob with text-mode `write_text("payload\n")`, which translates `\n` on Windows, so the stored blob's digest could never match the cited one (`mismatch=1` in the direct-function arms) · captured-by the selftest's `doc-binding-ok` failures on the first host run · fix: `write_bytes(b"payload\n")` — exact bytes on every host.
