VERDICT: confirm - install_tree() applies no member cap and skips every symlink (regular files only); the cost is that the soname symlinks the bundled libraries NEED are unpinned, so retargeting one leaves install_tree_sha256 unchanged.

# TreeCap probe: does install_tree() cap members or skip symlinks?

Scope: `tools/kama-llamacpp-live.py:178-202` in the round-19 copy `/tmp/kama-r19-TreeCap` (unmodified; the lane was not edited). Receipts: `/tmp/kama-r19-TreeCap/out/` (`run.log`, `probe-results.json`, `ls-*.txt`, `readelf-d-*.txt`). Driver: `bash /tmp/kama-r19-TreeCap/out/run.sh` → exit 0; `all_ok=true`.

## Code (read + grep)
- No cap: no slice, no `break`, no max/limit parameter. Tool grep of `:178-202` for break, slice, max, limit, cap, islink, follow → No matches.
- Symlinks are skipped by `os.lstat` + `stat.S_ISREG` (`:191`, `:194`). Directories and FIFOs are skipped by the same test.
- Silent drops: an unreadable regular file hits `except OSError: continue` (`:198-199`); an unlistable directory hits `return tree, None` (`:186-187`), giving `{}` with a null digest.
- The caller stores the dict verbatim (`kama-llamacpp-live.py:1268`, `:1280-1281`). No empty-tree guard exists.

## Counts vs ls (`out/snapshot.sh` exit 0; oracle in `probe_install_tree.py`, `probe-results.json`)

| fixture | `ls -A1` | regular | symlink | dir | fifo | install_tree | note |
|---|---|---|---|---|---|---|---|
| fixture-main | 70 | 60 | 8 | 1 | 1 | **60** | includes dotfile and `sp ace.bin`; all 8 symlinks excluded (file, chained, dangling, to-dir, to-parent, abs-outside, to-dotfile, to-server) |
| fixture-scale | 5002 | 5000 | 2 | 0 | 0 | **5000** | no cap below 5000 |
| fixture-unreadable | 5 | 5 | 0 | 0 | 0 | **4** | `locked-01` (mode 000) silently dropped; oracle reports PermissionError |
| fixture-nolist | exit 2 | 0 | 0 | 0 | 0 | **0**, `({}, None)` | listing failure returns empty with no error |
| fixture-repoint | 4 | 3 | 1 | 0 | 0 | **3** | see blind spot below |
| real install tree | 61 | 51 | 10 | 0 | 0 | **51** | keys equal receipt `server.install_tree`; digest `6c216313…5a2c` equals receipt |

- Plain `ls` shows 69 for fixture-main (hides `.hidden-reg`); install_tree includes it.
- Relative `llama-server` (dirname `''`) → `({}, None)`; `./llama-server` → 60 members.

## Blind spot: soname symlinks are unpinned
- `readelf -d` on llama-server and six libraries: `libllama-server-impl.so` NEEDs `libllama-common.so.0`, `libmtmd.so.0`, `libllama.so.0`, `libggml.so.0`, `libggml-base.so.0` (RUNPATH `$ORIGIN`). In the real tree each is a symlink to a versioned regular file, which is the pinned member (`ls-la-real-install-tree.txt`).
- `fixture-repoint`: retarget `libllama.so.0` from `libllama.so.0.7.0` to `libllama-common.so.0.7.0`. Tree digest `82456fa4…c1ad` is identical before and after. Bytes behind the name change from `3ed1ecdc…c179` to `a21445d9…8ad8d`.
- [INFERENCE] glibc opens NEEDED names through symlinks. Not executed. Retargeting requires write access to the install directory.
- `install-tree-grid.py:28-29` `DEFAULT_MEMBERS` are the three versioned regular files. The grid never touches a symlink, so it cannot see a retarget.

## Other findings
- Grid coverage cap, not install_tree: `install-tree-grid.py:73` `sorted(tree)[:3]` runs only when no default member is present. The receipts do not hit it.
- [INFERENCE] An end-to-end producer run against an unlistable install dir would write `install_tree: {}` and `install_tree_sha256: null`. The function-level result is executed; the producer run is not. The gate then skips its basename check (`check-receipt.py:369`, `if tree and …`).

## Advice (the lane owns the fix)
1. Fold symlink topology into the identity: record `name -> os.readlink()` per symlink, or hash the resolved bytes per soname, so a retarget changes the digest.
2. Fail closed: raise `SetupError` on listdir or sha256 failure instead of `return tree, None` / `continue`. Refuse to write a receipt with an empty tree.
3. Add `fixture-repoint` as a grid negative control once item 1 lands.

## Commands and exits
- `cp -a /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r19-TreeCap` → 0
- `mkdir -p …/out`; `command -v readelf` → 0; `readelf -d` on llama-server and six libraries → 0 each
- `id -u` → 1000; `python3 --version` → 3.14.8
- Real-tree `ls -A1` / `find` counts → 0
- `bash /tmp/kama-r19-TreeCap/out/run.sh` → 0 (build 0, probe 0 with all_ok=true, snapshot 0)

No installs or updates. The only lane write is this file.
