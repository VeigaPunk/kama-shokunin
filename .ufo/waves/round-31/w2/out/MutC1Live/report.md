```RESULTS
# Every shell command below ran on 2026-10-23. Tool-backed reads/edits (read, grep, edit) have no
# shell exit code; mutations applied through the edit tool are shown by their committed diffs in
# mutation-diffs.txt. Scratch clone: /tmp/kama-r31w2/MutC1Live/repo. Frozen counter used everywhere:
# .ufo/waves/round-31/count-c1.py sha256 d86c4a94b9a464a9aa6212b2958c72229b7134eb440f64edab70de090d924216
# (matches preregistration.json C1.counter_sha256).

$ cd /home/vgpnk/Projects/shokunin/kama-shokunin && sha256sum .ufo/waves/round-31/count-c1.py && git rev-parse HEAD && git cat-file -t 382d11b2107d335705875da1a4d889b074bd6fa6 && git ls-tree -r --name-only 382d11b2107d335705875da1a4d889b074bd6fa6 -- .ufo/waves/round-31/sources | sed -n '1,8p' && git ls-tree -r --name-only 382d11b2107d335705875da1a4d889b074bd6fa6 -- .ufo/waves/round-31/count-c1.py registry/chat-param-outcomes-r31.json SKILL.md corpus/SOURCES.md && ls -l /home/vgpnk/.local/opt/llama-b11755/llama-server /home/vgpnk/.local/opt/llama-b11755/libllama-server-impl.so /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf && git check-ignore -v .ufo/waves/round-31/count-c1.py; echo "ignore-exit:$?"
d86c4a94b9a464a9aa6212b2958c72229b7134eb440f64edab70de090d924216  .ufo/waves/round-31/count-c1.py
bda324bbc5c1d7db93553adb13c5f380492c3c93
commit
.ufo/waves/round-31/sources/SNAPSHOT.json
.ufo/waves/round-31/sources/llama.cpp-704366d/server-chat.cpp
.ufo/waves/round-31/sources/llama.cpp-704366d/server-common.cpp
.ufo/waves/round-31/sources/llama.cpp-704366d/server-http.cpp
.ufo/waves/round-31/sources/llama.cpp-704366d/server-models.cpp
.ufo/waves/round-31/sources/llama.cpp-704366d/server-schema.cpp
.ufo/waves/round-31/sources/llama.cpp-704366d/server-task.cpp
.ufo/waves/round-31/sources/llama.cpp-704366d/utils.hpp
.ufo/waves/round-31/count-c1.py
SKILL.md
corpus/SOURCES.md
registry/chat-param-outcomes-r31.json
-rw-r--r-- 1 vgpnk vgpnk 1185376 Oct 20 10:17 /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf
-rwxr-xr-x 1 vgpnk vgpnk 7671544 Oct 20 08:10 /home/vgpnk/.local/opt/llama-b11755/libllama-server-impl.so
-rwxr-xr-x 1 vgpnk vgpnk 17864 Oct 20 08:10 /home/vgpnk/.local/opt/llama-b11755/llama-server
ignore-exit:1
exit:0   # (last command is echo; ignore-exit:1 means the counter is tracked, not ignored)

$ mkdir -p /tmp/kama-r31w2/MutC1Live /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/MutC1Live && df -h /tmp | tail -1 && du -sh /home/vgpnk/Projects/shokunin/kama-shokunin/.git && ... (prerequisite listing)
/dev/nvme1n1p1  128G   44G   85G  35% /tmp
38M	/home/vgpnk/Projects/shokunin/kama-shokunin/.git
...
-rwxr-xr-x 1 vgpnk vgpnk 17864 Oct 20 08:10 /home/vgpnk/.local/opt/llama-b11755/llama-server
exit:0

$ cd /tmp/kama-r31w2/MutC1Live; rm -rf repo; git clone --no-hardlinks --quiet /home/vgpnk/Projects/shokunin/kama-shokunin repo; cd repo; git checkout --detach --quiet 382d11b2107d335705875da1a4d889b074bd6fa6; echo "HEAD:$(git rev-parse HEAD)"; git status --porcelain | wc -l; sha256sum .ufo/waves/round-31/count-c1.py registry/chat-param-outcomes-r31.json SKILL.md corpus/SOURCES.md
HEAD:382d11b2107d335705875da1a4d889b074bd6fa6
0
d86c4a94b9a464a9aa6212b2958c72229b7134eb440f64edab70de090d924216  .ufo/waves/round-31/count-c1.py
c79d193605997d21d7f4fa7f621b6f8b56ab1442963daf12ef31a3f4476447f5  registry/chat-param-outcomes-r31.json
f67e30b28ce6b4f8b18555e0f4d8370da434f2b19605b5bdd0f693a8564c06eb  SKILL.md
5441d8135f672546d999c5ec03d28f06c7eddfaf5af8cf74a2f5edfc53936520  corpus/SOURCES.md
exit:0

$ OUT=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/MutC1Live; cd /tmp/kama-r31w2/MutC1Live/repo; /usr/bin/python3 .ufo/waves/round-31/count-c1.py --lane "$PWD" --repo "$PWD" --tip 382d11b2107d335705875da1a4d889b074bd6fa6 --out "$OUT/baseline-382d11b2.json"
registered 18 counted 17 target 12 met True not-counted ['K31-10']
exit:0

# M1a: edit registry K31-05 outcome.status 400 -> 422 (edit tool; only this file changed), then commit and run.
$ OUT=...; cd /tmp/kama-r31w2/MutC1Live/repo; git diff --stat; git -c user.name=KamaR31.MutC1Live -c user.email=mutc1live@local commit -qam "mutant M1a: K31-05 expected status 422 (registry only)"; M1=$(git rev-parse HEAD); echo "M1:$M1"; git show --stat --oneline --format='%h %s' HEAD; sha256sum registry/chat-param-outcomes-r31.json; /usr/bin/python3 .ufo/waves/round-31/count-c1.py --lane "$PWD" --repo "$PWD" --tip "$M1" --out "$OUT/m1-registry-only.json" > "$OUT/m1-registry-only.out" 2>&1; rc=$?; cat "$OUT/m1-registry-only.out"; echo "exit:$rc"
 registry/chat-param-outcomes-r31.json | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
M1:e60fe105554877869d60e66ee3dccc93a02c72e8
e60fe10 mutant M1a: K31-05 expected status 422 (registry only)

 registry/chat-param-outcomes-r31.json | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
8afae12fad568c57bdfcd57fc3ff9a1cef26c46132b777ac235891816de8bb59  registry/chat-param-outcomes-r31.json
registered 18 counted 16 target 12 met True not-counted ['K31-05', 'K31-10']
exit:0

# Receipt reasons for M1a (jq extraction, later collection command):
{"summary":"registered 18 counted 16 target 12 met True not-counted ['K31-05', 'K31-10']","rows":[{"id":"K31-05","counted":false,"reasons":["skill-outcome:'reject 400 invalid_request_error: top_logprobs requires logprobs to be set to true'"],"live":{}},{"id":"K31-10","counted":false,"reasons":["reject-message-not-adapter"],"live":{}}]}

# M1b: edit SKILL.md K31-05 outcome cell to the matching 422 rendering (edit tool), so all static
# checks pass and only the live comparison can fail. Commit and run.
$ OUT=...; cd /tmp/kama-r31w2/MutC1Live/repo; git diff --stat; git -c user.name=KamaR31.MutC1Live -c user.email=mutc1live@local commit -qam "mutant M1b: SKILL K31-05 outcome cell matches 422 mutant"; M1B=$(git rev-parse HEAD); echo "M1B:$M1B"; /usr/bin/python3 .ufo/waves/round-31/count-c1.py --lane "$PWD" --repo "$PWD" --tip "$M1B" --out "$OUT/m1-live-consistent.json" > "$OUT/m1-live-consistent.out" 2>&1; rc=$?; cat "$OUT/m1-live-consistent.out"; echo "exit:$rc"
 SKILL.md | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
M1B:921caab51f10cbad5733f4229fe3a9ce313d9010
registered 18 counted 16 target 12 met True not-counted ['K31-05', 'K31-10']
exit:0

# Receipt reasons for M1b:
{"summary":"registered 18 counted 16 target 12 met True not-counted ['K31-05', 'K31-10']","rows":[{"id":"K31-05","counted":false,"reasons":["reject-status:400","reject-code:400"],"live":{"status":400,"error_keys":["code","message","type"],"message":"top_logprobs requires logprobs to be set to true","type":"invalid_request_error","code":400}},{"id":"K31-10","counted":false,"reasons":["reject-message-not-adapter"],"live":{}}]}

# Restore after M1: check out both files from 382d11b2, commit, prove the tree is identical, run.
$ OUT=...; cd /tmp/kama-r31w2/MutC1Live/repo; git checkout 382d11b2107d335705875da1a4d889b074bd6fa6 -- registry/chat-param-outcomes-r31.json SKILL.md; git -c user.name=KamaR31.MutC1Live -c user.email=mutc1live@local commit -qam "restore exact 382d11b2 bytes after M1"; R=$(git rev-parse HEAD); echo "RESTORE:$R"; if git diff --quiet 382d11b2107d335705875da1a4d889b074bd6fa6 HEAD; then echo "TREE_IDENTICAL:yes"; else echo "TREE_IDENTICAL:no"; fi; git status --porcelain | wc -l; sha256sum registry/chat-param-outcomes-r31.json SKILL.md; /usr/bin/python3 .ufo/waves/round-31/count-c1.py --lane "$PWD" --repo "$PWD" --tip "$R" --out "$OUT/restore-after-m1.json" > "$OUT/restore-after-m1.out" 2>&1; rc=$?; cat "$OUT/restore-after-m1.out"; echo "exit:$rc"
RESTORE:d4533cc272c03cada4061f231062def6e007f51b
TREE_IDENTICAL:yes
0
c79d193605997d21d7f4fa7f621b6f8b56ab1442963daf12ef31a3f4476447f5  registry/chat-param-outcomes-r31.json
f67e30b28ce6b4f8b18555e0f4d8370da434f2b19605b5bdd0f693a8564c06eb  SKILL.md
registered 18 counted 17 target 12 met True not-counted ['K31-10']
exit:0

# M2: edit SKILL.md K31-01 meaning cell to the three-word "Set max tokens." (edit tool), commit, run.
$ OUT=...; cd /tmp/kama-r31w2/MutC1Live/repo; git diff --stat; git -c user.name=KamaR31.MutC1Live -c user.email=mutc1live@local commit -qam "mutant M2: K31-01 SKILL meaning cell three words"; M2=$(git rev-parse HEAD); echo "M2:$M2"; /usr/bin/python3 .ufo/waves/round-31/count-c1.py --lane "$PWD" --repo "$PWD" --tip "$M2" --out "$OUT/m2-meaning-3words.json" > "$OUT/m2-meaning-3words.out" 2>&1; rc=$?; cat "$OUT/m2-meaning-3words.out"; echo "exit:$rc"
 SKILL.md | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
M2:0d566a3875f7451a8956ee2823476bbe37907095
registered 18 counted 16 target 12 met True not-counted ['K31-01', 'K31-10']
exit:0

# Receipt reasons for M2:
{"summary":"registered 18 counted 16 target 12 met True not-counted ['K31-01', 'K31-10']","rows":[{"id":"K31-01","counted":false,"reasons":["skill-meaning-words:3"],"live":{}},{"id":"K31-10","counted":false,"reasons":["reject-message-not-adapter"],"live":{}}]}

# Restore after M2: check out SKILL.md from 382d11b2, commit, prove the tree is identical, run.
$ OUT=...; cd /tmp/kama-r31w2/MutC1Live/repo; git checkout 382d11b2107d335705875da1a4d889b074bd6fa6 -- SKILL.md; git -c user.name=KamaR31.MutC1Live -c user.email=mutc1live@local commit -qam "restore exact 382d11b2 bytes after M2"; R2=$(git rev-parse HEAD); echo "RESTORE2:$R2"; if git diff --quiet 382d11b2107d335705875da1a4d889b074bd6fa6 HEAD; then echo "TREE_IDENTICAL:yes"; else echo "TREE_IDENTICAL:no"; fi; git status --porcelain | wc -l; sha256sum SKILL.md registry/chat-param-outcomes-r31.json corpus/SOURCES.md .ufo/waves/round-31/count-c1.py; /usr/bin/python3 .ufo/waves/round-31/count-c1.py --lane "$PWD" --repo "$PWD" --tip "$R2" --out "$OUT/restore-after-m2.json" > "$OUT/restore-after-m2.out" 2>&1; rc=$?; cat "$OUT/restore-after-m2.out"; echo "exit:$rc"; cat "$OUT/commits.txt"
RESTORE2:309cf738e42ba19a46f765736fc82988fbef312a
TREE_IDENTICAL:yes
0
f67e30b28ce6b4f8b18555e0f4d8370da434f2b19605b5bdd0f693a8564c06eb  SKILL.md
c79d193605997d21d7f4fa7f621b6f8b56ab1442963daf12ef31a3f4476447f5  registry/chat-param-outcomes-r31.json
5441d8135f672546d999c5ec03d28f06c7eddfaf5af8cf74a2f5edfc53936520  corpus/SOURCES.md
d86c4a94b9a464a9aa6212b2958c72229b7134eb440f64edab70de090d924216  .ufo/waves/round-31/count-c1.py
registered 18 counted 17 target 12 met True not-counted ['K31-10']
exit:0
M1=e60fe105554877869d60e66ee3dccc93a02c72e8
M1B=921caab51f10cbad5733f4229fe3a9ce313d9010
RESTORE=d4533cc272c03cada4061f231062def6e007f51b
M2=0d566a3875f7451a8956ee2823476bbe37907095
RESTORE2=309cf738e42ba19a46f765736fc82988fbef312a

# Evidence collection: mutation diffs, per-receipt reasons, receipt hashes, lane tracked-file diff.
$ OUT=...; cd /tmp/kama-r31w2/MutC1Live/repo; { echo '# mutation commit chain (base 382d11b2)'; git log --oneline 382d11b2..HEAD; ... git show --format=... --stat --patch each commit ...; } > "$OUT/mutation-diffs.txt"; { for f in baseline-382d11b2 m1-registry-only m1-live-consistent restore-after-m1 m2-meaning-3words restore-after-m2; do echo "== $f"; jq -c '{summary,rows:[.rows[]|select((.counted|not))|{id,counted,reasons,live}]}' "$OUT/$f.json"; done; } > "$OUT/not-counted-evidence.txt"; sha256sum "$OUT"/*.json "$OUT"/*.out > "$OUT/receipt-sha256.txt"; git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff --stat > "$OUT/lane-tracked-diff.txt" 2>&1 || true; git -C /home/vgpnk/Projects/shokunin/kama-shokunin status --porcelain=v1 -- SKILL.md registry corpus/SOURCES.md .ufo/waves/round-31/count-c1.py >> "$OUT/lane-tracked-diff.txt" 2>&1 || true; echo "== not-counted-evidence.txt"; cat "$OUT/not-counted-evidence.txt"; echo "== lane-tracked-diff.txt"; cat "$OUT/lane-tracked-diff.txt"; echo "== receipts"; ls -l "$OUT"
== not-counted-evidence.txt
== baseline-382d11b2
{"summary":"registered 18 counted 17 target 12 met True not-counted ['K31-10']","rows":[{"id":"K31-10","counted":false,"reasons":["reject-message-not-adapter"],"live":{}}]}
== m1-registry-only
{"summary":"registered 18 counted 16 target 12 met True not-counted ['K31-05', 'K31-10']","rows":[{"id":"K31-05","counted":false,"reasons":["skill-outcome:'reject 400 invalid_request_error: top_logprobs requires logprobs to be set to true'"],"live":{}},{"id":"K31-10","counted":false,"reasons":["reject-message-not-adapter"],"live":{}}]}
== m1-live-consistent
{"summary":"registered 18 counted 16 target 12 met True not-counted ['K31-05', 'K31-10']","rows":[{"id":"K31-05","counted":false,"reasons":["reject-status:400","reject-code:400"],"live":{"status":400,"error_keys":["code","message","type"],"message":"top_logprobs requires logprobs to be set to true","type":"invalid_request_error","code":400}},{"id":"K31-10","counted":false,"reasons":["reject-message-not-adapter"],"live":{}}]}
== restore-after-m1
{"summary":"registered 18 counted 17 target 12 met True not-counted ['K31-10']","rows":[{"id":"K31-10","counted":false,"reasons":["reject-message-not-adapter"],"live":{}}]}
== m2-meaning-3words
{"summary":"registered 18 counted 16 target 12 met True not-counted ['K31-01', 'K31-10']","rows":[{"id":"K31-01","counted":false,"reasons":["skill-meaning-words:3"],"live":{}},{"id":"K31-10","counted":false,"reasons":["reject-message-not-adapter"],"live":{}}]}
== restore-after-m2
{"summary":"registered 18 counted 17 target 12 met True not-counted ['K31-10']","rows":[{"id":"K31-10","counted":false,"reasons":["reject-message-not-adapter"],"live":{}}]}
== lane-tracked-diff.txt
== receipts
total 96
-rw-r--r-- 1 vgpnk vgpnk 5094 ... baseline-382d11b2.json
-rw-r--r-- 1 vgpnk vgpnk   67 ... baseline-382d11b2.out
-rw-r--r-- 1 vgpnk vgpnk  232 ... commits.txt
-rw-r--r-- 1 vgpnk vgpnk    0 ... lane-tracked-diff.txt
-rw-r--r-- 1 vgpnk vgpnk 5168 ... m1-live-consistent.json
-rw-r--r-- 1 vgpnk vgpnk   77 ... m1-live-consistent.out
-rw-r--r-- 1 vgpnk vgpnk 5015 ... m1-registry-only.json
-rw-r--r-- 1 vgpnk vgpnk   77 ... m1-registry-only.out
-rw-r--r-- 1 vgpnk vgpnk 5106 ... m2-meaning-3words.json
-rw-r--r-- 1 vgpnk vgpnk   77 ... m2-meaning-3words.out
-rw-r--r-- 1 vgpnk vgpnk 8320 ... mutation-diffs.txt
-rw-r--r-- 1 vgpnk vgpnk 1671 ... not-counted-evidence.txt
-rw-r--r-- 1 vgpnk vgpnk 2030 ... receipt-sha256.txt
-rw-r--r-- 1 vgpnk vgpnk 5094 ... restore-after-m1.json
-rw-r--r-- 1 vgpnk vgpnk   67 ... restore-after-m1.out
-rw-r--r-- 1 vgpnk vgpnk 5094 ... restore-after-m2.json
-rw-r--r-- 1 vgpnk vgpnk   67 ... restore-after-m2.out
exit:0

$ cat /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/MutC1Live/receipt-sha256.txt
6b58b4340886f602fd5e2a2f2795d4e7abf50dad9252d033c41050beba80331e  .../baseline-382d11b2.json
5fca079281962ea60a5ea1027caf24036e6fb01686559a6eb8a86a4b3bbc4112  .../m1-live-consistent.json
8cebbe4e5c8bd2bbcb6362f570bfc11e69a085956488242eadff31d3a9a8381c  .../m1-registry-only.json
379967b5b0fef514a2c8ace8236f3ec4d7c17d974914b88722a28855bf755454  .../m2-meaning-3words.json
0fd7382b26a74888ebf05ca244b46fd5b1afe9c7a3f04e8b3217dd474c763778  .../restore-after-m1.json
6b8a3ceb37978efa9bf64c5cb40fc621c33c37a8a9d28aa64cdc782e87feba28  .../restore-after-m2.json
8996bae5630a225edb66d1189c996e73a996d0d823ee29df510fe6894b7b694f  .../baseline-382d11b2.out
213a62137853ba3379c03d4664fa3847c1b7552ac6a2d13781523f8185a8e5bc  .../m1-live-consistent.out
213a62137853ba3379c03d4664fa3847c1b7552ac6a2d13781523f8185a8e5bc  .../m1-registry-only.out
a8fd22e2509bf45a07a3340c1cb411886f8b33577a177b1f05f5b869e0213fc7  .../m2-meaning-3words.out
8996bae5630a225edb66d1189c996e73a996d0d823ee29df510fe6894b7b694f  .../restore-after-m1.out
8996bae5630a225edb66d1189c996e73a996d0d823ee29df510fe6894b7b694f  .../restore-after-m2.out
exit:0

# Mutation diffs (verbatim cores; full patch set: mutation-diffs.txt)
M1a e60fe10  registry/chat-param-outcomes-r31.json: -    "status": 400, / +    "status": 422,
M1b 921caab  SKILL.md K31-05: -| ... | reject 400 invalid_request_error: top_logprobs requires logprobs to be set to true | ... | S188 |
                                    +| ... | reject 422 invalid_request_error: top_logprobs requires logprobs to be set to true | ... | S188 |
M2  0d566a3  SKILL.md K31-01: -| ... | Set max_tokens to bound output; do not assume this stored alias proves sampler use. | S190 |
                             +| ... | Set max tokens. | S190 |
restores d4533cc, 309cf73 revert those exact lines; `git diff --quiet 382d11b2 HEAD` exits 0 at 309cf73.

$ set -e; OUT=...; cp "$OUT/MutC1Live/report.md" "$OUT/MutC1Live.md"; sha256sum "$OUT/MutC1Live/report.md" "$OUT/MutC1Live.md"; ls -l "$OUT/MutC1Live.md"; git -C lane diff --stat -- SKILL.md registry corpus/SOURCES.md .ufo/waves/round-31/count-c1.py; git -C lane status --porcelain=v1 -- SKILL.md registry corpus/SOURCES.md .ufo/waves/round-31/count-c1.py; echo "lane-tracked-check-exit:$?"
cd942f146ff8348037e78799b4149b68393d8d7b55617724cc8157d19502cdf9  .../MutC1Live/report.md
cd942f146ff8348037e78799b4149b68393d8d7b55617724cc8157d19502cdf9  .../MutC1Live.md
-rw-r--r-- 1 vgpnk vgpnk 19350 Oct 23 20:10 .../MutC1Live.md
 SKILL.md | 21 +++++++++++++++++++++
 1 file changed, 21 insertions(+)
 M SKILL.md
lane-tracked-check-exit:0

# External lane change observed immediately after the copy above (not this seat); captured verbatim:
$ { git -C lane diff --stat; ...; git -C lane rev-parse HEAD; stat ...; git -C lane diff -- SKILL.md | sed -n '1,12p'; } > lane-concurrent-change.txt; cat lane-concurrent-change.txt
# lane state at 20:11 after my probe (external change, not this seat)
$ git -C lane diff --stat
 PROVINCE.md |  6 ++++++
 SKILL.md    | 21 +++++++++++++++++++++
 2 files changed, 27 insertions(+)

$ git -C lane status --porcelain=v1 -- SKILL.md registry corpus/SOURCES.md .ufo/waves/round-31/count-c1.py
 M SKILL.md

$ git -C lane rev-parse HEAD
addeb57c5d717785a94105a2e36cc8a76940fb6c

$ stat -c '%y %s %n' lane/SKILL.md
2026-10-23 20:09:42.535121388 -0300 138927 SKILL.md

$ git -C lane diff -- SKILL.md | sed -n '1,12p'
diff --git i/SKILL.md w/SKILL.md
index d23ba2c..9e3306c 100644
--- i/SKILL.md
+++ w/SKILL.md
@@ -1277,6 +1277,27 @@ A `reject` row establishes the measured API error contract for that request, not
+### Round-31 attempt-2 meaning-cell corrections (appended 2026-10-23; frozen rows unchanged)
exit:0
```

FINDING: Both mutants are KILLED — the frozen counter fails closed on each: (M1a) the registry-only K31-05 `outcome.status` 400→422 mutation makes row K31-05 uncounted with `reasons ["skill-outcome:'reject 400 invalid_request_error: top_logprobs requires logprobs to be set to true'"]` and `live {}`, i.e. caught by the SKILL/registry text comparison before any live request; (M1b) aligning the SKILL outcome cell to the mutated 422 rendering so all static checks pass makes the same row uncounted with `reasons ["reject-status:400","reject-code:400"]` and a live observation of HTTP 400 with `{code,message,type}` and the exact adapter message — so the counter does re-query the pinned live endpoint and compares the claimed status against the observed one, not just the row text; (M2) changing K31-01's SKILL `meaning` cell to three words makes row K31-01 uncounted with `reasons ["skill-meaning-words:3"]` and `live {}`. Summaries: pristine 382d11b2 `registered 18 counted 17 target 12 met True not-counted ['K31-10']`; M1a and M1b `counted 16 ... ['K31-05','K31-10']`; M2 `counted 16 ... ['K31-01','K31-10']`; both restored tips reproduce `counted 17 ... ['K31-10']`. Restoration: both restore commits have trees byte-identical to 382d11b2 (`git diff --quiet` exit 0, `TREE_IDENTICAL:yes`, clean `git status`), with registry `c79d1936…`, SKILL `f67e30b2…`, SOURCES `5441d813…`, counter `d86c4a94…`; the lane's tracked-file diff was empty at the 20:08 collection step (external lane appends appeared afterward; see CONCURRENT LANE CHANGE below); no lane file was written by this seat. LIMITS: this probe tests only the K31-05 `reject` live path; the slot/ignored/response live comparators (e.g. K31-16 `n_choices` 2→3 or a K31-13 `ignored` delta) were not mutated, so their fail-closed behavior is not established here. A registry-only live-expectation change is caught statically and never reaches the live request (`live {}`), so live-path evidence requires the SKILL cell to agree, as in M1b. Each mutant drops the count 17→16 while `counted >= 12` still reads `met True`; these single-row mutants therefore cannot overturn C1's aggregate predicate and say nothing about the known no-op/duplicate-row shortcut or the K31-10 non-count — a surviving aggregate `met True` under row-level mutation is slack in the claim, not evidence for it. One build/model/argv (llama-server b11755, `stories260K.gguf`, default argv, n_slots 4), one request per row, one run per state; no repeatability, concurrency, or flake study, and the counter deletes its ephemeral server log with its TemporaryDirectory (the receipt's `live` block is the retained observation). The counter's `reject-code` check compares `error.code` to the registry `status` field rather than directly to HTTP status, so the two M1b reasons share one mutated field; the independent measurement is `live.status: 400`. Nothing here judges C1's admission, C2, C3, the round, or whether the adapter's real behavior is correct beyond the single observed 422-vs-400 contradiction. No tools were installed or upgraded.

CONCURRENT LANE CHANGE (not this seat): at 20:11, after the probe's counter runs (20:06–20:08), the lane working tree carried external uncommitted edits — `git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff --stat` read `PROVINCE.md | 6 ++++++` and `SKILL.md | 21 +++++++++++++++++++++`, `git status --porcelain -- SKILL.md` read ` M SKILL.md`, lane HEAD had moved from `bda324bb` (probe start) to `addeb57c`, and lane `SKILL.md` had mtime `2026-10-23 20:09:42 -0300`; the appended heading is `### Round-31 attempt-2 meaning-cell corrections (appended 2026-10-23; frozen rows unchanged)`. Verbatim capture: `lane-concurrent-change.txt`. This seat wrote only `/tmp/kama-r31w2/MutC1Live` and the `w2/out/MutC1Live*` report files; it did not create, edit, stage, or revert those lane changes. All counter receipts above came from the /tmp clone at 382d11b2 before the lane change appeared, and are unaffected by it. Final-state check: the external edits were committed by the L1 as lane HEAD `a9181096` ("round-31 attempt 2: meaning-cell corrections (6 rows), PROVINCE/README count corrections, dead snapshot weight removed…"); the lane's tracked tree is clean again (`git status --porcelain -- SKILL.md PROVINCE.md` empty), and none of the probe's inputs changed.
