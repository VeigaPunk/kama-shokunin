VERDICT: confirm — Routed defect 5's premises hold on 2026-10-20: the retained tarball exists, its digest equals upstream, and no /usr/bin/llama-server exists, so the PATH link shadows nothing.

# ScribeInstallDisclosure — round-17 build, routed defect 5

Scope: owned draft `.ufo/waves/round-17/build/drafts/install-disclosure.md` (written). No lane doc, lesson, L0 file, install, link or cache was edited, removed or executed. No tool installed or updated (none needed). No subagent dispatched. No port bound; `ss -ltnp` filtered for llama-server returned no listener.

## Behavior
Draft paragraph names `~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz` under L0 question (b), states that no `/usr/bin/llama-server` exists, and says the PATH link shadows nothing on this host. It also contains one L0 follow-up line in the `kama | round-17 | <question>` format, because the round-16 question (b) does not name the archive. Removal is left to the operator.

## Read-only outputs (run 2026-10-20)

```
$ ls -l ~/.local/opt/ | grep llama
drwxr-xr-x 1 vgpnk vgpnk   2182 Oct 20 08:10 llama-b11755
-rw-r--r-- 1 vgpnk vgpnk 22240468 Oct 20 10:17 llama-b11755-bin-ubuntu-x64.tar.gz
$ ls -l ~/.local/bin/llama-server
lrwxrwxrwx 1 vgpnk vgpnk 48 Oct 20 10:17 /home/vgpnk/.local/bin/llama-server -> /home/vgpnk/.local/opt/llama-b11755/llama-server
$ ls -l /usr/bin/llama-server
ls: cannot access '/usr/bin/llama-server': No such file or directory
$ command -v -a llama-server
/home/vgpnk/.local/bin/llama-server
$ sha256sum ~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz
753bfa7327a75b477d4d14cde71e0e46a40acc3a1408c5504530b78c33a6e226  /home/vgpnk/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz
$ tar -xzOf ~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz llama-b11755/llama-server | sha256sum
b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804  -
$ sha256sum ~/.local/opt/llama-b11755/llama-server
b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804  llama-b11755/llama-server
$ tar -tzf ~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz | wc -l
62
$ ss -ltnp | grep -c llama-server
0   (exit 1: no matching listener)
```

PATH observed in this shell: `~/.local/bin` is entry 4; `/usr/bin` is entry 13. The link precedes `/usr/bin`, but `/usr/bin` holds no llama-server, so nothing is shadowed. The lane runtime PATH was not observed [unknown].

## Sources (accessed 2026-10-20)
- `corpus/lessons/round-16-verifier-spotcheck.md:186` (routed defect 5): "name the retained tarball `~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz` under L0 question (b)".
- `corpus/lessons/round-16-verifier-spotcheck.md:116`: "`/usr/bin/llama-server` is absent and no package owns it."
- `/home/vgpnk/Projects/shokunin/.ufo/l0-questions.md:58`: "Decide: (a) ratify the fixture exception, or reject it; (b) keep, or remove, the persistent install, the PATH link and the model cache."
- https://github.com/ggml-org/llama.cpp/releases/expanded_assets/b11755: "llama-b11755-bin-ubuntu-x64.tar.gz … sha256:753bfa7327a75b477d4d14cde71e0e46a40acc3a1408c5504530b78c33a6e226 … 21.2 MB 2026-10-20T11:21:10Z".
- https://github.com/ggml-org/llama.cpp/releases/tag/b11755: "Pre-release" and "released this 20 Oct 11:18", tag commit "`704366d`".

Upstream API (`api.github.com/.../releases/tags/b11755`) returned HTTP 403; the expanded-assets HTML was used for the digest instead.

## Findings
1. The routed-defect premise holds: the archive exists and is not named in `.ufo/l0-questions.md:58`. The lesson's install paragraph (line 118) says removal is "through L0 question (b)", which covers the install, link and cache but not the archive.
2. Digest: local archive equals upstream asset digest (753bfa73…e226). The archive's `llama-server` member equals the extracted binary (b6a31a8e…d804).
3. Shadowing: none on this host; `/usr/bin/llama-server` absent.

## Limitations
- Only this shell's PATH was checked; the lane's runtime PATH is unobserved [unknown].
- Locations outside PATH were not searched.
- Pre-release status comes from the release page fetched 2026-10-20; not re-checked.
- The removal decision is operator-owned; none recorded.

## Installs
None. No tool was installed or updated; all checks used existing `ls`, `sha256sum`, `tar`, `command`, `ss`.

## Integration note for L1
Append the draft paragraph to the next report, and append the one `kama | round-17 | …` line to `.ufo/l0-questions.md` (L1 only; I did not touch it).
