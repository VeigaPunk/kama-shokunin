# W3Frontier — round-53 frontier draft (append-ready)

Two blocks, ready to paste. **A** appends to `corpus/README.md` after line 1580 (end of
file, after the round-52 disposition and its integration line). **B** goes into the
round-53 SCORECARD chapter, immediately before `### Round-53 measured results` — the place
`### Planned (round 53)` occupies for round 52 today (`SCORECARD.md:3018` =
`### Planned (round 53)`, `:3020` = `### Round-52 measured results`).

Nothing here restates the integration items the L1 owns (§Round-53 section, measured
results, LOG entry, QUALITY rows, README coverage map, SKILL registry, lesson
Mistakes/Errata, the round-52 closure Errata). Numbers come from the committed receipts
(`c1-build.out`, `c2-build.out`, `base.c1.out`, `base.c2.out`, copied into this directory)
and from the wave reports named per row. This seat ran no counter, edited no lane file and
rewrote no seat report. Line numbers are the frozen counters' at the build
(`tools/round53-*.py` are byte-identical at `d01b2b6d` and `c22602bd`; `X1Rerun.md`
§Provenance).

---

## A. `corpus/README.md` — append after line 1580

`````text
## Frontier disposition — round 53 (appended)

**Moved from frontier to held ground:**

- *Per-mapping identity for the code the launcher loads* (round-52 "Not shown by round 52",
  second bullet; `SCORECARD.md` §Planned (round 53) item 1; the round-52 outside closure's
  routed R2, "libraries and model load by path"). The live tool records every executable
  file mapping of its server — path, dev, inode, owner, and the digest of the file at that
  path only while `fstat()` shows the mapped inode; a `(deleted)` name is never opened —
  into the receipt's `code_mappings` (`tools/kama-llamacpp-live.py:774`), the replay hashes
  the archive members those mappings name from the archive's own tar stream and reports the
  verified ones as `own_code` (`tools/kama-live-replay.py:305`), and the C1 counter believes
  neither: it opens `/proc/<pid>/mem` (S506), reads each executable range of the server and
  compares it with its own download of the release archive
  (`tools/round53-replay-code-audit.py:405-433`), requires `libllama-server-impl.so`,
  `libggml-base.so*`, `libggml.so*` and a `libggml-cpu-*.so` among the mapped members
  (`:103`), and cross-checks the rerun receipt's recorded digest and `own_code`
  (`:615-630`). A library swapped after the replay's member check is thereby a byte
  difference, not an unobserved path, and the memory leg is the one that carries it: with
  the checks intact the replay itself refuses (`bind=0`, `code-mapping:digest`) and the
  counter reports `code=0 met=False` (control J1SwapChecked); with the replay's
  `verify_code()` made to lie it still reports `code=0 met=False` (J2SwapUnchecked); and
  with the live tool's digests forged as well, only the `/proc/<pid>/mem` comparison fails
  (J3ForgedReceipt — `bind=1 sealed=1 code=0 ... met=False`, all three receipts, in
  `.ufo/waves/round-53/w1/out/`). The build receipt: 8 archive files over 8 executable
  ranges byte-equal in memory, 13 root-owned host files, `coderuns=3/3`
  (`.ufo/waves/round-53/measured/c1-build.out`). Held for the executable ranges of the
  replay's own server only — not for host libraries, data segments or the model.

- *A mechanical cited-path instrument for the self-assessment* (round-52 lesson Mistakes #4;
  seat W3Mistakes' prototype counted 51 misses and called 50 "pre-existing" without
  examining them). `tools/round53-cited-path-check.py` reads every backtick citation of a
  lane-root path — and of the fleet's `scripts/` and `templates/` — in `SCORECARD.md`,
  `SHONEN.md` and `SKILL.md` outside ``` fences, expands `{a,b}`, cuts `:N` / `:N-M` /
  `:N,M` anchors, resolves against the lane tree then the fleet tree, and requires each miss
  to be disclosed by a `registry/cited-path-corrections.tsv` row whose class (`deleted`,
  `never`, `moved`, `eof`, `untracked`, `upstream`, `fixed`) it re-derives from git history,
  with no bad row and no SCORECARD citation dropped since the base. At the build:
  `cited=682 unresolved=14 disclosed=14 bad=0 stale=0 dropped=0`, eight fixture scenarios
  (`.ufo/waves/round-53/measured/c2-build.out`), against `unresolved=16, undisclosed=16` at
  the base. What is held is that a pointer resolves or says why not; that the cited file
  says what the citing sentence claims is not graded.

**Not shown by round 53:**

- *Where the compared bytes came from.* The counter compares memory with its own download;
  a replay whose memfd and unpacked libraries were filled from this host's byte-identical
  `/home/vgpnk/.local/opt/llama-b11909/` still matches — round-52 J5HostMemfd, preregistration
  limit 1, and round-53 probe J6HostMemfd measured it: `met=True`, with the replay's
  opens of the host install visible in a trace
  (`.ufo/waves/round-53/w1/out/J6HostMemfd/c1-probe.out`, `trace-summary.txt`). Bytes, not
  provenance.
- *The non-executable segments.* Only rows with `x` in the permission column are compared
  (`tools/round53-replay-code-audit.py:413`); the libraries' `r--` and `rw-` `PT_LOAD`
  segments, relocated at load, are not read.
- *The model behind its path.* The model leg is the round-50 one: a file-backed mapping
  whose pathname, stat()ed now, hashes to the frozen model (`:307`). A model the server
  maps from a sealed memfd (round-52 seat N2Pattern's route) has no pathable mapping, so the
  bind leg fails rather than describing it.
- *Host libraries, and anything root-owned.* The 13 root-owned files the build maps are only
  classified — uid 0, the mapped inode, not writable by the counter (`:447`) — and their
  bytes are compared with no reference; `dev` is not compared for them at all (this host's
  btrfs/overlay root reports a st_dev different from the one `/proc/<pid>/maps` shows,
  disclosed before the freeze). No reference means no class: seat J5Preload loaded a
  root-owned copy of `libggml-rpc.so` from outside the tree and the counter reports
  `code=1 met=True` with 14 host files — the same load, user-owned, is caught as `foreign`
  (`:363`) — and probe K3Host tests how far the rule bends.
- *When it was read.* One observation, while the server is held: a library rewritten after
  the counter's read is not observed, and the live tool's digest is of the file at the path,
  not of memory. Probe J7Late asks whether an in-place rewrite of an already-mapped `r-x`
  range is even reachable without the loader refusing.
- *A second executable memfd.* The counter's own leg skips every `/memfd:` row (`:413`), so
  it cannot see code the server executes from an anonymous memfd other than its sealed
  image; from the wave the replay refuses one that is not its own sealed image (by dev and
  inode, `code-mapping:foreign-memfd`), which is a check the same wave showed the counter
  cannot audit — a lying replay passes (J2SwapUnchecked, finding 2). Found by seat V3Review.
- *Hosts at `ptrace_scope` 2 or 3.* The leg opens `/proc/<pid>/mem` of a descendant (`:405`),
  grounded on S507 (ptrace(2), Yama scope 1) for this host only; at scope 2 or 3 the open
  fails and `code` goes 0 — the instrument fails closed, it does not degrade to another
  observation. S508 (`map_files`) was rejected as the alternative: the reading process needs
  `CAP_SYS_ADMIN` or `CAP_CHECKPOINT_RESTORE`, and this host's `CapEff` is 0 (EPERM on
  `open`).
- *What C2 counts as satisfied.* A citation can be removed instead of disclosed: the
  `dropped` leg reads `SCORECARD.md` only and compares token sets, so deleting a `SKILL.md`
  citation, deleting one of several occurrences of a `SCORECARD.md` token, or fencing it
  leaves `met=True` (seat J10Drop; the build's own `SKILL.md:113` replacement,
  `scripts/local-helper.mjs` → an absolute path, is disclosed only in a ledger comment the
  counter does not read). Hiding a dead `SKILL.md` citation behind quotes, a fence or a
  `./` prefix with its ledger row removed also meets, and the only trace is `cited` falling
  682 → 678 (seat J12Hide). An `upstream` row is satisfied by any
  `raw.githubusercontent.com` URL that answers 200 — the mutable `master`, or a b11909 file
  whose sha256 is not the one `SKILL.md` pins — and a `fixed` row by a replacement that
  resolves but names an unrelated file (seat J11BadFixed; seat V5Review on the live-GET
  dependence). No citation exercises the fleet's `templates/` root, so a mutant restricting
  `FLEET_ROOTS` to `scripts/` survives (seat M5Ctr, M04).
- *C2's parsing and resolution strength.* Three surfaces only: `LOG.md`, the lessons, this
  file and the knowledge entries are not read, and a path written in prose or as a link is
  not a backtick citation. An anchor is checked by the file's line count, not by what the
  line says, and a `#fragment` is cut without being resolved
  (`tools/round53-cited-path-check.py:160`). A glob resolves on one match and a directory on
  one path beneath it; a lane path that is gone resolves if the fleet tree holds a path of
  the same name (`resolve()`, `:203-212`, lane then fleet for every root). The eight
  fixtures never exercise the `moved`, `eof`, `untracked`, `upstream` or `fixed` classes
  (`:435`).

**Still frontier:** a verifier-owned reference for the bytes the replay runs (a witness of
the replay's own download or extraction stream, so the host-install fill fails); identity
for the non-executable segments and for the model object; a host-library rule with a
reference behind it (a package-owned allowlist of system libraries, by digest) instead of
uid 0 and not-writable, so a root-owned library from outside the tree cannot be host code;
an observation that survives a post-read rewrite; a counter leg for anonymous executable
memfds that does not rest on the replay's own claim; a stated host requirement
(`ptrace_scope` 1) or a non-ptrace route; the round-50 carried items (probe PATH execution,
kills during download or readiness, pid start-time binding of `child_pid` — the counter
holds start times in `reap()` and `teardown_leg()`,
`tools/round53-replay-code-audit.py:242,679`, but compares `child_pid == pid` bare at
`:599`); hosts with `vm.memfd_noexec=2` (S502: no memfd server can run there; the replay
refuses at creation); the prerelease cliff (b11909 is still a GitHub prerelease, three
releases behind b11913; seat Sc2Watch re-checked both pinned digests on 2026-10-27); for C2,
a `dropped` leg that covers every surface and every occurrence and sees a citation replaced
by a non-citation, content-pinned `upstream` and `fixed` rows, content-aware anchors, the
uncovered surfaces, a resolution that does not fall back from the lane to the fleet, and
fixture scenarios for the five unexercised ledger classes and for a `templates/`-only
citation.

Integration (round 53, L1): written from the wave's reports (`.ufo/waves/round-53/w1/out/`);
measured values are in SCORECARD under the round-53 measured-results heading.
`````

---

## B. `SCORECARD.md` — `### Planned (round 54)`, immediately before `### Round-53 measured results`

`````text
### Planned (round 54)

1. Operability: give the code comparison provenance, not only bytes — a witness of the replay's own download or extraction stream (a counter-owned extraction the replay must use, or a held descriptor on the archive member), so a tree or memfd filled from the host's byte-identical install fails (probes J6HostMemfd and round-52 J5HostMemfd, both `met=True` when run); put a reference behind the host-file class, since `uid 0` plus not-writable admits a root-owned library from outside the tree as host code (seat J5Preload: `code=1 met=True`, 13 → 14 host files, `tools/round53-replay-code-audit.py:447`) — a package-owned allowlist of system libraries with digests, or an admission rule that no extra root-owned mapping is allowed at all (probe K3Host asks how far the current rule bends); compare what is not executable today: the libraries' read-only and writable `PT_LOAD` segments and the model object (a sealed-memfd model has no path for the round-50 leg, `:307`); classify the anonymous executable memfd in the counter's own leg instead of only in the replay (`:413`, seat V3Review), so `code=1` does not rest on a claim the same wave showed forgeable (J2SwapUnchecked finding 2, J3ForgedReceipt); read a second time, or hold the compared ranges against a rewrite, if the post-read window can be closed at all (seat J7Late); state the host requirement the leg carries — `/proc/<pid>/mem` of a descendant, `ptrace_scope` 1 (S507), `map_files` refused without `CAP_SYS_ADMIN`/`CAP_CHECKPOINT_RESTORE` (S508) — in the instrument registry, and bind the observed pid by start time (`child_pid == pid` at `:599` is compared without the start time `stat_fields()` already returns); carry the round-50 items (probe PATH execution, kills during download or readiness) and the `vm.memfd_noexec=2` host (S502).
2. Calibration: make the `dropped` leg what it claims — every surface and every occurrence, and enough content awareness to see a citation replaced by a non-citation, since today a `SKILL.md` citation deleted, hidden (a fence, quotes, a `./` prefix) or replaced by an absolute path leaves `met=True`, with only `cited` falling (seats J10Drop, J12Hide; the build's own `SKILL.md:113` correction is disclosed in a ledger comment the counter never reads, `tools/round53-cited-path-check.py:363-377`); pin `upstream` evidence to a digest of the fetched bytes at a fixed revision instead of any URL that answers 200 — the mutable `master` and a wrong-revision file pass today — and check that a `fixed` replacement is the file the sentence means, not merely one that resolves (seats V5Review, J11BadFixed); give an anchor its content (`:N` naming the right line, a resolved `#fragment`, `:160`) and either extend the surfaces past `SCORECARD.md`/`SHONEN.md`/`SKILL.md` (LOG.md, the lessons, corpus/README.md, the knowledge entries, inline prose and link paths) or write the three-surface boundary into the instrument's contract, and stop a lane citation from resolving on a same-named fleet path (`resolve()`, `:203-212`); add fixture scenarios for `moved`, `eof`, `untracked`, `upstream`, `fixed` — five of the seven classes the eight scenarios at `:435` never exercise — for the ledger's one-row-per-(surface, token) granularity, and for a `templates/`-only citation (seat M5Ctr's surviving M04).
`````

---

## Evidence key (why each line above is there)

| Claim in the draft | Evidence |
|---|---|
| `code_mappings` records path/dev/inode/uid/digest of the file at the mapped inode; `(deleted)` never opened | `tools/kama-llamacpp-live.py:774-830`; selftest `:1783-1818`; `c1-build.out` |
| replay hashes members from the archive stream, reports `own_code`, refuses digest/not-a-member/foreign/unopened/no-archive-library | `tools/kama-live-replay.py:290-337` |
| counter reads `/proc/<pid>/mem` ranges against its own download; required member names; receipt cross-check | `tools/round53-replay-code-audit.py:393-459`, `:103`, `:614-631` |
| swap after the check, checks intact | `J1SwapChecked.md` (`bind=0 sealed=1 code=0 ... met=False`; replay `code-mapping:digest`) |
| swap after the check, replay lying | `J2SwapUnchecked.md` + `c1-j2.out` (`bind=1 sealed=1 code=0 ...`, exit 1), copied here |
| swap after the check, receipt forged too | `J3ForgedReceipt.md` (`bind=1 sealed=1 code=0 ... met=False`, memory leg alone) |
| build receipt numbers | `c1-build.out` (`code b1..b3: 8 archive files (8 executable ranges) ... 13 root-owned host files`, `coderuns=3/3`, exit 0) |
| base control | `base.c1.out` (`code=0 coderuns=0/3 newrow=0 met=False`) |
| host-install fill still meets | `J6HostMemfd/c1-probe.out` (`met=True`), `J6HostMemfd/trace-summary.txt`; round-52 `J5HostMemfd` |
| root-owned library from outside the tree is host code | `J5Preload.md` v2/v3 (`code=1 met=True`, `14 root-owned host files`) vs v1 (`foreign`, uid 1000) |
| `/memfd:` rows skipped by the counter's own leg | `round53-replay-code-audit.py:413`; seat `V3Review.md` (medium) |
| replay now refuses a foreign executable memfd (post-build integration) | `git diff c22602bd -- tools/kama-live-replay.py tools/kama-llamacpp-live.py` (`code-mapping:foreign-memfd`, `reason: anonymous-memfd`) |
| host-file rule (uid 0, inode, not writable, no dev) | `round53-replay-code-audit.py:438-452`; preregistration `limits[1]` |
| model leg is path-bound | `round53-replay-code-audit.py:307-337`; preregistration `limits[2]` |
| single read, post-read rewrite | preregistration `limits[3]`; probe `J7Late` (report not landed when this draft was written) |
| ptrace_scope 1 / `map_files` CAP | SOURCES S507, S508; counter `:405` |
| C2 parser, resolution, ledger classes | `round53-cited-path-check.py:99-212`, `:234-311`; ledger `registry/cited-path-corrections.tsv` |
| C2 build and base numbers | `c2-build.out` (`cited=682 unresolved=14 disclosed=14 ... met=True`), `base.c2.out` (`cited=679 unresolved=16 disclosed=0 undisclosed=16 met=False`) |
| `dropped` leg scope | `round53-cited-path-check.py:363-377`; seats `J10Drop.md` (SKILL.md deletion invisible; build's own line 113), `J12Hide.md` (fence/quote/`./` hide, `cited` 682 → 678) |
| `upstream` any-200, `fixed` unrelated replacement | `round53-cited-path-check.py:298-311`, `:239-253`; seats `J11BadFixed.md`, `V5Review.md` |
| `templates/` root unexercised | `M5Ctr.md` M04 survives; `FLEET_ROOTS` at `:102` |
| five of seven classes have no fixture | `round53-cited-path-check.py:435-447` (unresolved, fenced, brace, forged `deleted`, true `deleted`, forged `never`, anchor past EOF, stale row) |
| b11909 still a prerelease, three behind b11913; both pinned digests still serve | `Sc2Watch.md` |
| `vm.memfd_noexec=2` host cannot run the replay | round-52 disposition (S502); untouched by round 53 |

## Deliberately left out

- Anything the L1 already integrates (SCORECARD §Round 53 narrative, measured results,
  LOG entry, QUALITY rows, README coverage map, SKILL §Round-53 instrument registry, lesson
  Mistakes/Errata, the round-52 closure Errata draft, Planned (round 53) closure wording).
- Probes whose reports had not landed when this draft was written (`J7Late`, `K3Host`,
  `S5Limits`, `X4Fresh`, `X8Regen`, `M6Ledger`): they are named as probes, never as
  outcomes. If a landed probe contradicts a "not shown" bullet, the L1 should edit that
  bullet, not this evidence key.
- No counter was run and no lane file was touched by this seat; a defect already filed by a
  wave seat is attributed to that seat rather than restated as new.
