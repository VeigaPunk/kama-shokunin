# SCR01Frontier command and observation ledger

Axes: calibration + operability. Author-side source and draft work only.

All bash commands below completed with tool-reported exit 0. Historical receipt EXIT=1 is a read value, not this seat's execution. No installs or updates.

1. `git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse HEAD && git -C /home/vgpnk/Projects/shokunin/kama-shokunin status --porcelain | wc -l && sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-85/count.py`
   - HEAD: 7d3c987c0e3a6ee62673c18c26ecdd22f39e5cdd; dirty-line count at that instant: 11. Counter sha256 e550a24786d7c3e073c549a8dcb03d456579696ba92a7f2a15ea2e7c04bedca9. Freeze token is the revision, not this sha256.
2. `git -C /home/vgpnk/Projects/shokunin/kama-shokunin log -3 --format='%H %ad %s' --date=iso && git -C /home/vgpnk/Projects/shokunin/kama-shokunin status --porcelain`
   - Freeze commit subject: `round-85: freeze authority-cell and delivered-mutant claims`; prior commit 4401b72f64a2202fd30f26479c463e9b9d9cabad. Concurrent user/integrator changes observed; none changed by this seat.
3. `mkdir -p /fast/scratch/hyaku/kama-r85/SCR01Frontier /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-85/w1/out/SCR01Frontier`
4. `env TMPDIR=/fast/scratch/hyaku/kama-r85/SCR01Frontier curl --silent --show-error --location --dump-header /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-85/w1/out/SCR01Frontier/commonmark.headers --output /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-85/w1/out/SCR01Frontier/commonmark.html --write-out 'HTTP_STATUS=%{http_code}\nBYTES=%{size_download}\nURL=%{url_effective}\n' https://spec.commonmark.org/0.31.2/#atx-headings`
   - HTTP_STATUS=200; BYTES=514698; effective URL unchanged.
5. `env TMPDIR=/fast/scratch/hyaku/kama-r85/SCR01Frontier curl --silent --show-error --location --dump-header /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-85/w1/out/SCR01Frontier/rejected-readme.headers --output /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-85/w1/out/SCR01Frontier/rejected-readme.txt --write-out 'HTTP_STATUS=%{http_code}\nBYTES=%{size_download}\nURL=%{url_effective}\n' https://raw.githubusercontent.com/ggml-org/llama.cpp/b7200/examples/server/README.md`
   - HTTP_STATUS=404; BYTES=14; effective URL unchanged. Actual body `404: Not Found`.
6. `git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 7d3c987c0e3a6ee62673c18c26ecdd22f39e5cdd:corpus/SOURCES.md | wc -l`
   - 679 lines. This line count is not an ID-absence test.
7. Read-only eval subprocess: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 7d3c987c0e3a6ee62673c18c26ecdd22f39e5cdd:corpus/SOURCES.md`, returncode 0; `re.findall(r'^\| '+id+r' \|', stdout, re.M)` returned 0 for each of S576 and S577. Current working-file grep separately found both occupied at lines331–332; KQ137 occupied at QUALITY.md line662.
8. `sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-85/w1/out/SCR01Frontier/commonmark.html /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-85/w1/out/SCR01Frontier/rejected-readme.txt`
   - CommonMark c85f56cc2101f761cc94215c677cd2c7c1ecca9c47be016479fdfe718af60f0d; rejected body d5558cd419c8d46bdc958064cb97f963d1ea793866414c025906ec15033512ed.

Specialized reads: complete round85 plan including raw line21 to recover truncation; frozen count.py; tooling RULES; Godspeed and self-evaluation skills; source registry schema; source validation interface; source bodies; CommonMark §4.2/ex68/ex69; round84 red receipt; before directory listing; round84 closure and plan citations. No counter execution, build, lint, selftest, fleet validation, or source mirror. Existing before/census/validation receipts were read only.
