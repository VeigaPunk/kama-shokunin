VERDICT: partial - names, flags, S066-S068 quotes, grid numbers and loader order match; the "never smaller" rule, the empty-block digest rule, the relative-target boundary and the ldconfig attribution do not, and a symlinked glibc-hwcaps passes the producer.
Attacked: corpus/knowledge/llamacpp-loading-lifecycle.md:324-362 (round-21 supplement) and corpus/SOURCES.md:78-80 (S066-S068), against code at a6617149 (tools/, tests/, knowledge, SOURCES identical to measured b76727f3: `git diff --quiet` exit 0).
Method: read-only; no server; real install tree read only; gcc loader stubs in scratch. Probe: out/KnowledgeAccuracy/probe.py -> probe-output.txt (exit 0, sections §1-§6). Commands and exits: out/KnowledgeAccuracy/commands.txt. [INFERENCE] marks unexecuted reasoning.

## Findings (supplement line -> code line)

F1 Medium. "Fail closed, never smaller" (L343-348) is not enforced for read failures. install_tree drops any regular member whose sha256_file raises OSError (tools/kama-llamacpp-live.py:196-199). install_links checks only os.access(R_OK) (L241-242) and records no problem. Injected EIO on 1 of 3 members: install_tree returns 2 members, the tree digest changes, install_links problems [] (§3). The gate recomputes over the receipt's own map (check-receipt.py:412-415), so it cannot see the drop. Selftest docstring (L1102-1105) claims "never a silently smaller identity" and tests only chmod. Reachability: [INFERENCE] open()/read can fail where access() succeeds (I/O error, LSM open denial).
  Fix: raise OSError out of install_tree (or open-test each regular member in install_links) and refuse; add a read-failure cell to the grid.

F2 Medium. Gate accepts an emptied block with a null digest. check-receipt.py:454-455 `allow_none=not links`: {"install_links": {}, "install_links_sha256": null} is VALID by default and under --require-install-links (CLI exit 0, §2). Supplement L351 ("its digest must recompute") and L355-356 ("a stripped block only by --require-install-links or that pin") are wrong for this variant: only the pin catches it. No pass-path emits it; the setup-error skeleton fails "server.install_tree is empty" (gate:390-392, §1 S11).
  Fix: `allow_none=False` at check-receipt.py:455; the setup-error skeleton already fails on "install_tree is empty". [INFERENCE] no selftest fixture needs the leniency (not checked).

F3 Medium. A symlink named glibc-hwcaps passes the producer. install_links records any symlink (producer:237-238). With glibc-hwcaps -> ../outside: problems [], and the loader loads outside/x86-64-v3/libprobe.so.0 (exit 1 vs base 2, §4-B). Only the gate's "/" rule rejects it (check-receipt.py:192-193). The grid has no such cell (install-links-grid.py:139-168). L346-348 presents glibc-hwcaps as refused by the producer. Threat model: needs write access to the install directory [INFERENCE].
  Fix: refuse any entry named `glibc-hwcaps` whatever its type; add a symlink-hwcaps grid cell.

F4 Low-Med. Boundary narrower than the rule. L359-360 says relative targets that "leave the directory (../lib/...)" are rejected. Code rejects any target containing "/" (gate:192-193), including same-directory ./libllama.so, with the false message "leaves the pinned directory" (§1 S5; grid cell link-same-resolution-text). L352-353 ("same-directory basenames") matches the code. The producer does not refuse ../ targets (grid link-dotdot: changed, not refused); the gate does.
  Fix: reword to "any target containing `/` (absolute, `../` or `./`) is rejected"; correct the gate message.

F5 Low-Med. Scope overclaim: L335 "the chain ldconfig maintains". S066 documents the layout ldconfig creates for directories it processes (ldconfig(8) DESCRIPTION para 1: command-line dirs, /etc/ld.so.conf, /lib, /usr/lib). ~/.local/opt is in none: no ld.so.conf entry, `ldconfig -p` lists 0 llama entries, and no lane tool runs ldconfig. The links are release-layout links. Lesson gate row (corpus/lessons/round-21.md:42) repeats "maintained chain".
  Fix: reword to "the soname layout ldconfig(8) documents (S066); nothing runs ldconfig on this directory (not in ld.so.conf; `ldconfig -p` lists no llama entry)"; correct the lesson gate row too.

F6 Low. S067 anchor. The install-dir search is RUNPATH step (3) with $ORIGIN (readelf: llama-server and libllama-server-impl.so carry RUNPATH [$ORIGIN]). S067 cites steps (4)-(5) (cache, default dirs); the RUNPATH text belongs to S057. "at every exec" (L336) is not in S067 [INFERENCE from search order]. Fix: cite S057 step (3); mark the inference.
  The S067 row's own "teaches" column (corpus/SOURCES.md:79) repeats "at every exec" without a mark.

F7 Low. L345-346 "a name with a control character": code is ord(ch) < 0x20 (producer:231). Names with DEL or U+0085 are accepted (§3). Say "C0 control character".

F8 Low. L346-348 hwcaps order is sourced to seat LinksLoaderProof, not S066-S068. ld.so(8) NOTES "glibc Hardware capabilities (from glibc 2.33)" gives the search path "glibc-hwcaps/x86-64-v3:glibc-hwcaps/x86-64-v2:"; §4-A confirms (exit 1 with subdir, 2 without). Add that anchor.

F9 Low. S068 "not the bytes it resolves to" is not in the cited index.md line 29. nix file-system-object.md L15-19 says it ("An arbitrary string, known as the target ... Nix does not assign any semantics to symbolic links"). Cite it or mark [INFERENCE].

F10 Low. L331-332 "both selftests": three --selftest entry points exist (tools/kama-llamacpp-live.py, check-receipt.py, install-links-grid.py). Name them.

## Verified matches
- Names and flags exist exactly: install_tree (producer:178), links_digest (:205), install_links (:213), receipt key install_links_sha256 (:1394), install_links_sha (check-receipt:173), link_chain_problem (:181), --expect-install-links-sha256 and --require-install-links (argparse :2321, :2324), install-tree-unpinnable (producer:1378), install-links-grid.py.
- Digest: producer and gate encode identically; real-tree digest 5cb9f486... equals the live receipt (§5).
- Retarget changes the mapped object while the regular digest is unchanged (grid frozen link 0/13).
- Consistent retarget detected only by the pin (§1 S6); dropped block by require or pin (§1 S1, §2); dangling, loop, name-collision and ../ rejected (§1 S7-S10).
- glibc-hwcaps directory refused (grid subdir 1/1 refused); unreadable member refused (chmod, §3).
- install_tree encoding unchanged (diff from 7a6bc911 starts at producer:202); six round-18 v3 receipts VALID by default, exit 1 with --require-install-links (§6).
- verified-at: check-receipt --selftest exit 0 (11 VALID + 1 NOT-EVALUATED, 91 mutations); install-links-grid --selftest exit 0 (13/13); producer --selftest exit 0; grid current exit 0 (link 13/13, null 0/1); grid --arm both exit 1 (frozen link 0/13, back-compat equal).
- S066: ldconfig(8) DESCRIPTION para 3 quote verbatim (man-pages 6.19, footer 2026-08-03). S067: quote verbatim; page has no "symlink". S068: index.md line 29 verbatim at 26842787...; tag 2.34.1 peels to that commit (git ls-remote).

## Other observations (outside the supplement)
- O1: LinksLoaderProof summary (.ufo/waves/round-21/build/out/LinksLoaderProof/summary.txt) records install_links_sha256 b58f1b4d...; that value reproduces only from line-joined "name -> target" lines (§5), a pre-canonical encoding. Final producer value 5cb9f486... matches the receipt. Its loader traces stand; its digests are stale evidence.
- O2: Lesson Limits section omits F1-F3; grid has no cells for symlinked hwcaps, read failure or emptied block.

## Gaps
- F1 reachability and F3 threat model are [INFERENCE]; not shown with real I/O or LSM faults.
- Not re-run: official run.py measurement; round-18 receipts were gated, not regenerated.
- Installs: none. Used host gcc 16.2.1, GNU readelf 2.47, Python 3.14.8; pacman -Q queries only. Scratch /tmp/kama-r21-KnowledgeAccuracy removed at finish.
