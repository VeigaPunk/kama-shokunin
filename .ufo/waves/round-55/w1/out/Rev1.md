# Rev1 — K1Cheat coverage of the round-55 C1 counter (kama, round 55, operability)

**Verdict:** No K1Cheat sub-finding is left with neither a killing leg nor a disclosed
limit — each of its four demonstrated attacks and each of its six code-level findings maps
to a named round-55 C1 leg or to a limit the frozen preregistration states — **but** the
root-owned-plant class is killed only in its `LD_PRELOAD` spelling. The identical plant
delivered via `LD_AUDIT` with a frozen-set basename passes the frozen counter end-to-end
(`met=True`, 14 host files, the three counter-observed server pids running the module's
constructor), admitted only by the basename-only host limit; and the battery arm meant to
kill that class is vacuous (`m-ldaudit-foreign.out:2` prints `met=True`), which contradicts
the frozen target and kill rule (`preregistration.json:19-20,44`).

## 0. Frozen inputs checked before any probe

| artifact | value | evidence |
|---|---|---|
| C1 counter | `c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af` = `preregistration.json` C1 `counter_sha256` | `sha256sum tools/round54-replay-code-audit.py` |
| base control | `newrow=0 … met=False` | `.ufo/waves/round-55/controls/base.c1.out:2` |
| build measurement | `newrow=1 … met=True` | `.ufo/waves/round-55/measured/c1-build.out:2` |
| battery control | `met=True` | `.ufo/waves/round-55/c1/battery/control.out:2` |
| battery kills | `m-ldpreload` `envnames=0/3 met=False`; `m-text-flip` `code=0/3 rehash=3 met=False`; `m-member-flip` `rehash=3 met=False` | same dir, line 2 of each |
| battery non-kills | `m-ldaudit-foreign` `met=True`; `m-ldaudit-writable` `met=True`; `m-extra-in-tree` `met=True` | same dir, line 2 of each |

K1Cheat source: `.ufo/waves/round-53/w1/out/K1Cheat.md` (plus the seat's artifacts in
`.ufo/waves/round-53/w1/out/K1Cheat/`).

## 1. Sub-finding ledger (the requested mapping)

Counter lines are `tools/round54-replay-code-audit.py` at 9c60eae. "Kill" cites the leg's
code and a receipt/observation that shows it failing; "Limit" cites the frozen disclosure.

| # | K1Cheat sub-finding (K1Cheat.md) | round-55 leg that kills it | disclosed limit that admits it |
|---|---|---|---|
| 1 | **Root-owned `LD_PRELOAD` plant** (:80-86): constructor in a root-owned `.so` runs arbitrary code in the observed server | **envnames** — `BAD_ENV` 146, `env_leg` 429-441, leg 824, `met` 954. Receipt `m-ldpreload.out:2` (`envnames=0/3 met=False`) and `:9` (`env: server environment carries LD_PRELOAD`), with the preload itself a frozen-set basename (`/usr/lib/libzstd.so.1.5.7`), so envnames alone killed it. `clearenv()/unsetenv()` cannot hide it: `probe3.json` (the exec-time environ page still carries `LD_PRELOAD=`) | only for the non-`LD_PRELOAD` spellings: limit 87-92 ("host libraries are bound by name to the frozen set, not byte-compared") / `preregistration.json:49`. Demonstrated below (D3) |
| 2 | **Anonymous RWX page** (:87-90): shellcode `mmap`ed and called inside the server | **code** — `code_observe` 498-506 (`code: anonymous executable mapping …`), `anon` count 713, `met` 954. `probe.json` probeA reproduces the exact line for the page the constructor called (`7f58113ce000-7f58113cf000 rwxp`, marker result 42 at the same address); `c1-audit-anon…out:8-9,14-15,20-21` (`anon=6`, `met=False`) | sampling window only (87-92): a page created and unmapped between the two passes is not observed. No same-uid battery arm (limit, `preregistration.json:49`) |
| 3 | **Path-text lie / ` (deleted)` name** (:91-95) | **code** — a tree path that is not a regular archive member 515-520; a host path that cannot be stat'ed 546-550. Unchanged from round 53; code reading only (no new receipt) | none needed — closed |
| 4 | **`dlopen` after the counter's single read** (:96-99) | **none** (by design: the read is now two passes + a post-exit re-hash) | **Limit** 87-92: "the counter samples state … two `/proc/<pid>/mem` passes during the hold"; the rehash 770-779 re-hashes only archive paths already observed, so a library loaded after the passes is not covered. [INFERENCE: the limit's example is rewrite/restore; "samples state" is the sentence that admits new loads] |
| 5 | **Anonymous rows skipped by the path filter** (:62-66: the old `code_observe` only examined rows with a pathname) | **code** — 498-506 now classifies every executable row without a pathname as a problem; named kernel maps (`[vdso]` …) are the only skip (503, `KERNEL_MAPS` 144) | none needed — closed |
| 6 | **Host branch accepts any root-owned executable, bytes never compared** (:67-71) | **code/hostlibs** — 558-565: root-owned **and** inode-matching **and** not writable **and** basename in the frozen 13 (`HOST_LIBS` 138-143), leg 825. `probe.json` probeB: a root-owned `/usr/lib/libexpat.so.1.13.0` mapping yields `code: root-owned host library … is not in the frozen host set` | **Limit** 91-92 / `preregistration.json:49` for an attacker file whose basename *is* in the set; no byte comparison, no path binding. Demonstrated (D3) |
| 7 | **Post-release cross-check only iterates the archive members it saw** (:72-73); the receipt-side `verify_code` admits `uid==0` | archive-member cross-check 760-765; the receipt side is still `verify_code`'s `elif e.get("uid") != 0` → `host.append` (`tools/kama-live-replay.py:362-365`), unchanged | same **Limit** 91-92: a root-owned in-set-basename entry is an ordinary "host" entry in both the counter and the receipt, never compared |
| 8 | **Predicate quantifier "executable *file* mappings"** (:74-76) | **fixed in the wording and enforced**: `preregistration.json:18` now says "every one of whose executable **mappings**"; counter docstring 10-12 and 76-80; the anon/memfd branches 498-513 enforce it | none needed — closed |
| 9 | **The +1 host file (14 vs 13) passed unnoticed** (:49-52) | **code/hostlibs** for a *new* basename — 563-565. K1Cheat's `kama-r53-cheat.so` would now fail here | **Limit** 91-92 for a duplicate in-set basename; the count is printed (785-790) but never asserted, so 14 still meets (leg 825 checks only the `code: root-owned host library` problem prefix). Reproduced end-to-end: `c1-audit-LD_AUDIT…out:5,11,17` — "**14** root-owned host files", `met=True` (D3) |
| 10 | **Remedy "fail on `LD_PRELOAD`/`LD_LIBRARY_PATH`-style names"** (:120-123) | only `LD_PRELOAD`/`DYLD_INSERT_LIBRARIES` are checked (`BAD_ENV` 146); `LD_LIBRARY_PATH` cannot be added unchanged because the honest live tool sets it itself (`tools/kama-llamacpp-live.py:2195`), so flagging it would fail the honest replay | **Limit** 91-92 for both `LD_LIBRARY_PATH` and `LD_AUDIT`, neither of which is named in the limits paragraph |

**Gap test (the ticket's criterion):** none of rows 1-10 has *neither* a killing leg nor a
disclosed limit, so there is no K1Cheat sub-finding gap. Rows 2, 5, 6 and 9 are
demonstrated by run; rows 1 and 10 by run plus code; rows 3 and 8 by code; row 4 is the
frozen sampling limit; row 7 is the frozen name-only limit.

## 2. Defects and residuals found by this seat

### D1 (HIGH, frozen battery vs frozen claim) — the `hostlibs` arm is vacuous and the kill rule is literally triggered

- `m-ldaudit-foreign.out:2` (`envnames=3/3 hostlibs=3/3 anon=0 … met=True`) and
  `m-ldaudit-writable.out:2` (`met=True`) are the receipts for two arms that
  `preregistration.json:44` lists as mutants (`m-ldaudit-writable (code leg)`,
  `m-ldaudit-foreign (hostlibs leg)`), while `:19` says "kill battery: each named mutant
  receipt prints `met=False` (exit 1) with its named leg failing" and `:20` says the claim
  "is falsified if … any battery mutant prints `met=True`".
- The driver later reclassifies the arm: `run-battery.py:52-61` ("not reproducible as a
  non-root mutant … the LD_AUDIT vector … is empirically void on this glibc") and `:137`
  (`if kind == "vector": ok = rc == 0 and met`). The receipt is real; the expectation was
  changed after the freeze, which the frozen kill rule does not permit.
- The "void" conclusion is an artifact of the test DSO, not of the vector. `probe.json`
  probeC, same glibc, same `/usr/bin/true`:

      LD_AUDIT=<conforming module exporting la_version>  -> exit 0, la_version 2 pid …, constructor marker written
      LD_AUDIT=/usr/lib/libexpat.so.1                    -> ERROR: ld.so: object '…libexpat.so.1' cannot be
                                                            loaded as audit interface: undefined symbol: la_version; ignored.

  An audit module is loaded by ld.so *and* its constructor runs (`probe2.json`,
  `probe5.json`). The arm's intent (a root-owned foreign basename failing the `hostlibs`
  leg) is achievable — `probe.json` probeB shows an out-of-set root-owned mapping is
  flagged — but the frozen receipt does not show it.
- Also: `m-text-flip` (a live kill) is absent from `preregistration.json:44`, and
  `m-ldaudit-writable.out` is not produced by the current driver (stale file), so the
  receipt set and the frozen mutant list do not line up.
- Proposed fix: rerun the arm with a conforming audit module carrying an **out-of-set**
  basename (expected `hostlibs=0/3 met=False`), add the `anon` arm of D2, and either
  commit a corrected preregistration in a *new* round or state in the round report that
  `:19-20` were not met by the frozen receipts. The frozen files themselves must not be
  edited.

### D2 (MEDIUM, battery coverage) — no arm exercises the `anon` leg

The frozen receipts all print `anon=0`; nothing shows the leg able to fail. The lack is
disclosed (`preregistration.json:49`: "the anon leg's non-root isolation is covered by
design and receipts, not by a same-uid mutant"), but the leg is the only thing standing
between a root-owned in-set-basename plant and arbitrary code (D3). This seat's second
end-to-end run closes the evidence gap: the same fixture tip 13d5ed99 with the plant also
`mmap`ing an anonymous RWX page yields `code=0/3 anon=6 met=False`
(`c1-audit-anon.in-set-basename.met-False.out:2`), and the three observed server pids
(211709, 237734, 263881) each executed the shellcode (`anon-exec.txt` line
`211709 42 0x7f889ee6e000` matches the receipt's anon row at `:8`).
Proposed fix: add this arm to the battery.

### D3 (MEDIUM, residual admitted by the limit) — the plant class survives via `LD_AUDIT` + an in-set basename

Command (fixture `fixture.patch`, tip `13d5ed99a8f4fa1220db4a66b3b5555e94a881ae`, frozen
counter unmodified):

    python3 tools/round54-replay-code-audit.py --repo "$S/lane" --tip 13d5ed99… \
        --scratch "$S/ctr" --out "$S/c1-audit.out"
    # exit 0
    # bind=1 sealed=1 code=1 teardown=1 newrow=1 … envnames=3/3 hostlibs=3/3 anon=0 … met=True

The plant is a root-owned `libzstd.so.1.5.7` (basename in `HOST_LIBS` 138-143) executing
`la_version` and a constructor in every observed server: receipt `:9,15,21` name the
observed pids 3907951 / 3928271 / 3944924, and each is present in `end2end-la.txt` and
`end2end-ctor.txt`. The receipt reports "**14** root-owned host files" (`:5,11,17`) — the
exact 14-vs-13 observation K1Cheat used, now passing with `met=True`, because the host
branch only checks `basename in HOST_LIBS` (563-565) and the leg only checks the problem
prefix (825). This is admitted by the frozen limit ("bound by name to the frozen set, not
byte-compared", 91-92 / `preregistration.json:49`), so C1 is not falsified — but the
limits paragraph does not name the `LD_AUDIT`/`ld.so.preload` vectors, and the envnames
leg records the name without flagging it (`probe2.json`, `probe5.json`).
Proposed fix: `proposal-counter.patch` (LD_AUDIT in `BAD_ENV`; host set must equal the
frozen 13 names at 13 paths, not a subset). The honest build already maps exactly 13 host
files, so the equality is its normal state.

### D4 (LOW, receipt-side) — the replay receipt cannot distinguish the plant

`verify_code` admits any `uid==0` executable mapping (`tools/kama-live-replay.py:362-365`)
and `bind_one` cross-checks only the archive files it observed (760-765); the plant is an
ordinary `host` entry in both. Admitted by the same name-only limit; fixed by D3's host-set
assertion at counter level. No separate edit proposed.

## 3. Evidence (commands, outputs, exit codes)

Scratch `S=/fast/scratch/hyaku/kama-r55/w1/Rev1` (removed; artifacts copied to this
directory). Frozen files were never edited.

1. Probe programs (frozen counter imported as a module; no archive, no network):
   `python3 probe.py` → `probe.json`: probeA constructor built an anon RWX page and called
   it (`cheat-marker: 2693434 42 0x7f58113ce000`); `env_leg` → `env: server environment
   carries LD_PRELOAD`; `code_observe` → `code: anonymous executable mapping
   7f58113ce000-7f58113cf000 rwxp (name '(none)')` and the user-owned `cheat.so` problem.
   probeB → `code: root-owned host library /usr/lib/libexpat.so.1.13.0 is not in the frozen
   host set`. probeC → conforming audit module `la_version 2 pid 2695796` + `ctor pid
   2695796`; libexpat rejected as an audit interface.
   `python3 probe2.py` → `probe2.json`: `LD_AUDIT` recorded (8 names), no env problem;
   `la_version` and constructor ran. `python3 probe3.py` → `probe3.json`: `LD_PRELOAD`
   still in `/proc/pid/environ` after `unsetenv`+`clearenv`. `python3 probe4.py` /
   `probe5.py` → the root-owned in-set-basename plant draws **no** problem line; probe5
   (server image in a memfd, as the honest replay runs it) reports
   `env_problems=[] hostset_problems=[] anon_problems=[] all_code_problems=[] host_count=3`.
2. End-to-end, frozen counter, own `git clone --shared`, fixture committed only in the
   clone (`git -C "$S/lane" … -c user.name=fx -c user.email=fx@invalid commit`; toplevel
   verified equal to `$S/lane`; tip 13d5ed99, `fixture.patch` = 3 lines in
   `tools/kama-llamacpp-live.py` child_env):
   - plant with constructor only → exit 0, `met=True`, 14 host files, observed pids
     3907951/3928271/3944924 all in `end2end-la.txt` + `end2end-ctor.txt`
     (`c1-audit-LD_AUDIT.in-set-basename.met-True.out`);
   - plant also mapping an anon RWX page → exit 1, `code=0/3 anon=6 met=False`, observed
     pids 211709/237734/263881 in `anon-exec.txt`
     (`c1-audit-anon.in-set-basename.met-False.out`);
   - no counter/prereg edit; lane, fleet repo and shokuknow untouched; no llama-server
     from this seat remains (`pgrep -af llama-server` shows only seat J5EnvNames' two
     processes); scratch removed including the root-owned probe file.
3. Tooling: no installs; system `gcc` 16.2.1 built the probe libraries; `sudo` used only to
   chown/chmod/remove the two scratch probe files (pacman paused host-wide — not run).

## 4. Confidence

High for every line-number claim and every receipt quoted (read at 9c60eae / on disk).
High for D1's "vector not void" and D3's end-to-end pass (both run). Medium only for
row 4's limit mapping: the frozen sentence is phrased as rewrite/restore, and I extended
it to newly loaded code by inference (marked). Row 3 is code reading only — the round-53
closure is unchanged in substance and no round-55 receipt re-exercises it.

## Artifacts (this directory)

`c1-audit-LD_AUDIT.in-set-basename.met-True.out` (+ `.stdout`), `end2end-la.txt`,
`end2end-ctor.txt`, `fixture.patch`, `c1-audit-anon.in-set-basename.met-False.out`
(+ `.stdout`), `anon-exec.txt`, `probe.json`, `probe2.json`, `probe3.json`, `probe4.json`,
`probe5.json`, `cheat.c`/`cheat.so`, `audit.c`/`audit.so`, `audit_anon.c`/`audit_anon.so`,
`clr.c`, `sha256s.txt`, `proposal-counter.patch`, `README-proposal.md`, `run-notes.md`.
