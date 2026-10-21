VERDICT: confirm - a soname retarget changes the object glibc maps while every loader line keeps the symlink path; install_tree_sha256 never moves, install_links_sha256 does; a glibc-hwcaps copy shadows the tree with both digests unchanged (gap)

Scope: round-21 kama LinksLoaderProof, premise of C2. Advisory only; lane untouched (scratch clone at a29bb84; tool sha256 c05cd8bf...). llama-server was never started or exec'd; it appears only as an argument.

Method (out/LinksLoaderProof/run.sh reproduces; commands.log has every command with its exit)
- S0 = cp -a of ~/.local/opt/llama-b11755 (source only read). llama-server sha256 and S0 lane digests equal the source's (summary.txt 27-31).
- Probes are trace-only: `ld.so --list` (LD_DEBUG=libs,files), `ldd`, `ldd -r`. Here ldd runs the loader from RTLDLIST with LD_TRACE_LOADED_OBJECTS=1 on the file (/usr/bin/ldd:104,116-120,158-176); it does not exec the binary, so no substitute was needed. readelf -d gives NEEDED/RUNPATH.
- Identity: stat -L and sha256 of what open(2) reaches. Digests: lane install_tree/install_links imported unchanged from a29bb84 (digests.py).

Graph (commands.log 114-164): llama-server NEEDs libllama-server-impl.so (RUNPATH $ORIGIN, FLAGS BIND_NOW); impl NEEDs libllama.so.0, libggml.so.0, libggml-base.so.0, libmtmd.so.0, libllama-common.so.0, libssl.so.3, libcrypto.so.3; libggml.so.0 -> libggml.so.0.27.0 (SONAME libggml.so.0).

Results (digests as 8-char prefixes; full values in summary.txt)
| state | object opened (size, sha256 prefix) | LD size | ldd -r undefined | install_tree | install_links |
|---|---|---|---|---|---|
| S0 pristine | .27.0 (51040, 8643a58b) | 0xb2b0 | 0 | 6c216313 | b58f1b4d |
| S1 staged | .27.0 | 0xb2b0 | 0 | ef19e31a | b58f1b4d |
| S2 stub retarget | libggml.so.0.0.0-decoy (15168, b0cb014a) | 0x4010 | 18 (10 unique) | ef19e31a | 33e95251 |
| S3 same-ABI retarget | .27.0-sameabi (51040, 137ad56b) | 0xb2b0 | 0 | ef19e31a | 95b93721 |
| S4 dangling | none: ld.so --list exit 127 | - | 18 (10 unique) | ef19e31a | 442cf614 |
| S5 hwcaps copy | glibc-hwcaps/x86-64-v3/libggml.so.0 (51040, 8643a58b); impl sha 3059abeb | 0xb2b0 | 0 | ef19e31a | b58f1b4d |

In S0-S3 `ld.so --list` and `ldd` print `libggml.so.0 => .../tree/libggml.so.0`; in S4 they print `not found`; in S5 the same lines name the glibc-hwcaps path.
Resolution lines, S0-baseline.txt 107-113: needed by impl -> find library -> search path=tree (RUNPATH of llama-server) -> trying tree/libggml.so.0 -> generating link map, size 0x000000000000b2b0. S2 lines 107-113 are identical except size 0x0000000000004010.

Findings
1. [observed] The mapped object changes while loader output keeps the symlink path. A check reading only `ld.so --list` or `ldd` output misses a retarget.
2. [observed] install_tree_sha256 is blind to every retarget (S1=S2=S3=S4=S5); it moves only when a regular file is added (S0->S1). This confirms the R19 TreeCap debt.
3. [observed] install_links_sha256 moves at each retarget (S1->S2->S3->S4). The C2 premise holds on this tree.
4. [observed] The same-ABI retarget (S3) passes ldd -r with zero errors and maps the same size; only sha256 and inode differ.
5. [observed] Dangling (S4): ld.so --list exits 127, "libggml.so.0: cannot open shared object file" (S4 lines 112-124); the search falls back to /etc/ld.so.cache and /usr/lib first. ldd exits 0 while printing "not found", so its exit is not a load check. [INFERENCE] A libggml.so.0 in /usr/lib would load silently; none exists here.
6. [observed, beyond C2] glibc-hwcaps shadow (S5): impl and closure load from tree/glibc-hwcaps/x86-64-v3/ (search order v4,v3,v2 on this host: S5 line 24; impl opened lines 27-29). install_tree, install_links and impl_sha (a29bb84:1295-1298, top-level path only; top-level impl sha e404b91a, unchanged) all stay as before, because both scans are non-recursive (a29bb84:183-195, 212-223). Only a complete copy was tested.
7. [observed] S2 stub: ldd -r reports 18 undefined-symbol lines (10 unique ggml_backend_*). [INFERENCE] A real start would fail when those bindings resolve; not run.
8. [observed] Safety control: a constructor-bearing DT_NEEDED lib leaves its marker absent under ld.so --list, ldd -r and ldd (commands.log 286, 297, 308) and present when the control program runs (315). Trace-mode loads ran no constructors here.
9. [observed in source] The live tool gives the child only PATH, HOME, LANG, LC_ALL, TMPDIR (a29bb84:84, 1335-1336, 1366) and argv[0]=realpath (1320-1321). LD_* never reaches the server, so live resolution follows RUNPATH/$ORIGIN and /etc/ld.so.cache, as here.

Recommendations (L1 decides; nothing implemented)
- Keep install_links: it caught S2, S3 and S4.
- Close the hwcaps gap: reject subdirectories of the install dir or walk it recursively before pinning; add a grid cell with a glibc-hwcaps copy.
- Pin what is mapped: realpath + sha256 of each object from the ld.so --list trace, not only the top-level impl_sha.
- Use ld.so --list's exit status, not ldd's, as the load check.

Tools and provenance
- Nothing installed or upgraded; pacman untouched. Used pre-installed: glibc ldd and ld.so 2.44, gcc 16.2.1, GNU readelf 2.47, git 2.56.0, Python 3.14.8, coreutils.
- No labrat spawned; no background process started. Non-zero exits in commands.log: only S4 ld.so --list (127) and S4 ident (1), both expected.
- Deliverables: .ufo/waves/round-21/build/out/LinksLoaderProof/ (run.sh, commands.log, summary.txt, S0-S5-*.txt, decoy.c, mk_variant.py, digests.py, summarize.py, ctor-control.c). Scratch /tmp/kama-r21-LinksLoaderProof removed after this report.
