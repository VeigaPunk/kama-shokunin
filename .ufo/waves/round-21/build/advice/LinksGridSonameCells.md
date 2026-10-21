VERDICT: confirm - current identity detects each of five loader-needed soname retargets

Axes: operability 8 (symlink identity); calibration 7 was not exercised by this scoped move.

Deliverable: `.ufo/waves/round-21/build/out/LinksGridSonameCells/install-links-grid-needed.patch`, a patch against `a29bb84abbb8b4d328f5970a89e448330a3a42ac`. It adds explicit retarget cells for each in-tree `DT_NEEDED` symlink and retains null, regular, type, and link-integrity controls. The `libllama.so.0` cell retargets to `libllama-common.so.0.7.0`.

Evidence (commands and exits):
- `readelf -d /home/vgpnk/.local/opt/llama-b11755/llama-server` — exit 0. `DT_NEEDED`: `libllama-server-impl.so`, `libstdc++.so.6`, `libgcc_s.so.1`, `libc.so.6`.
- `readelf -d /home/vgpnk/.local/opt/llama-b11755/libllama-server-impl.so` — exit 0. In-tree sonames: `libllama-common.so.0`, `libmtmd.so.0`, `libllama.so.0`, `libggml.so.0`, `libggml-base.so.0`; remaining entries were `libssl.so.3`, `libcrypto.so.3`, `libstdc++.so.6`, `libm.so.6`, `libgcc_s.so.1`, `libc.so.6`, `ld-linux-x86-64.so.2`.
- `readlink` loop over the five in-tree names — exit 0; targets were respectively `libllama-common.so.0.7.0`, `libmtmd.so.0.7.0`, `libllama.so.0.7.0`, `libggml.so.0.27.0`, `libggml-base.so.0.27.0`.
- In the scratch clone checked out at the assigned draft commit: `python3 tests/llamacpp-live/install-links-grid.py --tree /home/vgpnk/.local/opt/llama-b11755 --arm both` — exit 1 (the frozen arm is expected to miss link-only cells). All five new retarget rows were frozen=same/current=changed; none printed a current gate-chain problem.

Observed summary lines:
```
summary arm=frozen link=0/12 regular=2/2 type=1/1 null=0/1 wrong=12 status=fail
summary arm=current link=12/12 regular=2/2 type=1/1 null=0/1 wrong=0 status=pass
back_compat install_tree_sha256 equal=True
```

Risk: the retained `link-same-resolution-shortcut` control uses `./<member>` and the current receipt gate flags that target as leaving the pinned directory. The targeted library-to-library retargets remained chain-clean. No tools were installed or updated. No lane files were modified.