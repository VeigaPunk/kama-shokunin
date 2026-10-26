# X1R04 — C1 rows S114, S115 (llama.cpp b11755 pin → b11906)

Upstream refs: pin `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` (b11755);
b11889 `d854d98bae598388ecea1ed84396587e5edc326d`; b11906 `4d71b42fd87db24b8b7c808c151b713aa4459cfd`.
Repo: `/fast/scratch/hyaku/kama-r46/L1/llama.git` (read-only).
Path: `tools/server/server-context.cpp`.

## Identity / blobs

```
$ git -C $R rev-parse --verify -q 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad:tools/server/server-context.cpp
b2116b1740a39be2412a33caf52adb9e322e95ee
$ git -C $R rev-parse --verify -q 4d71b42fd87db24b8b7c808c151b713aa4459cfd:tools/server/server-context.cpp
9043fa2c02905495f55045d8d0fc978b1f94e027
$ git -C $R show <pin>:tools/server/server-context.cpp | sha256sum
dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329  -
   # == the anchor sha256 in SOURCES.md columns for S114 and S115
$ git -C $R show 4d71b42fd...:tools/server/server-context.cpp | sha256sum
61c1afcfd6869aef8ca0f83369b1f94140e0e893d366c3375036fcb9dce61114  -
```

Line counts: pin 6320; b11889 7070; b11906 7073 (+3).

## Pin text (with line numbers)

```
$ git -C $R show 704366d76f...:tools/server/server-context.cpp | awk 'NR>=5360&&NR<=5412{printf "%d\t%s\n",NR,$0}'
5363	    this->get_slots = [this](const server_http_req & req) {
5364	        auto res = create_response();
5365	        if (!params.endpoint_slots) {
5366	            res->error(format_error_response("This server does not support slots endpoint. Start it with `--slots`", ERROR_TYPE_NOT_SUPPORTED));
5367	            return res;
5368	        }
...
5370	        // request slots data using task queue
5371	        {
5372	            server_task task(SERVER_TASK_TYPE_SLOT_GET);
5373	            task.id = res->rd.get_new_id();
5374	            res->rd.post_task(std::move(task), true); // high-priority task
5375	        }
...
5405	    this->post_slots = [this](const server_http_req & req) {
5406	        auto res = create_response();
5407	        if (params.slot_save_path.empty()) {
5408	            res->error(format_error_response("This server does not support slots action. Start it with `--slot-save-path`", ERROR_TYPE_NOT_SUPPORTED));
5409	            return res;
5410	        }
5411	
5412	        std::string id_slot_str = req.get_param("id_slot");
5413	
5414	        int id_slot;
5415	        try {
5416	            id_slot = std::stoi(id_slot_str);
...
5422	        std::string action = req.get_param("action");
5424	        if (action == "save") {
5425	            return handle_slots_save(req, id_slot);
5426	        }
5427	        if (action == "restore") {
5428	            return handle_slots_restore(req, id_slot);
5429	        }
5430	        if (action == "erase") {
5431	            return handle_slots_erase(req, id_slot);
5432	        }
5433	
5434	        res->error(format_error_response("Invalid action", ERROR_TYPE_INVALID_REQUEST));
5435	        return res;
5436	    };
```

## Release text at b11906

```
$ git -C $R show 4d71b42fd...:tools/server/server-context.cpp | grep -n "does not support slots"
5687:            res->error(format_error_response("This server does not support slots endpoint. Start it with `--slots`", ERROR_TYPE_NOT_SUPPORTED));
5729:            res->error(format_error_response("This server does not support slots action. Start it with `--slot-save-path`", ERROR_TYPE_NOT_SUPPORTED));

$ git -C $R show 4d71b42fd...:tools/server/server-context.cpp | awk 'NR>=5680&&NR<=5735{printf "%d\t%s\n",NR,$0}'
5684	    this->get_slots = [this](const server_http_req & req) {
5685	        auto res = create_response();
5686	        if (!params.endpoint_slots) {
5687	            res->error(format_error_response("This server does not support slots endpoint. Start it with `--slots`", ERROR_TYPE_NOT_SUPPORTED));
5688	            return res;
5689	        }
...
5726	    this->post_slots = [this](const server_http_req & req) {
5727	        auto res = create_response();
5728	        if (params.slot_save_path.empty()) {
5729	            res->error(format_error_response("This server does not support slots action. Start it with `--slot-save-path`", ERROR_TYPE_NOT_SUPPORTED));
5730	            return res;
5731	        }
5732	
5733	        std::string id_slot_str = req.get_param("id_slot");
5735	        int id_slot;
5736	        try {
5737	            id_slot = std::stoi(id_slot_str);
...
```

## Pair equality (counter semantics: strip each line, drop blanks, join)

```
$ python3  # excerpt() from tools/round46-release-recheck-audit.py:211-212
(5365, 5367) (5686, 5688) equal
(5407, 5409) (5728, 5730) equal
(5366, 5366) (5687, 5687) equal
(5408, 5408) (5729, 5729) equal
pin nonws chars A 158
pin nonws chars B 172
```

Raw-byte check of the two guard blocks (`cat -A`, no trailing whitespace difference):

```
$ sed -n '5365,5367p' $S/pin.cpp | cat -A
        if (!params.endpoint_slots) {$
            res->error(format_error_response("This server does not support slots endpoint. Start it with `--slots`", ERR
            return res;$
$ sed -n '5686,5688p' $S/rel.cpp | cat -A
        if (!params.endpoint_slots) {$
            res->error(format_error_response("This server does not support slots endpoint. Start it with `--slots`", ERR
            return res;$
```

Whole `get_slots` body identical pin 5363-5403 ↔ b11906 5684-5724:

```
$ diff <(sed -n '5363,5403p' pin.cpp | sed 's/^[ \t]*//') <(sed -n '5684,5724p' rel.cpp | sed 's/^[ \t]*//')
BODY_A_EQUAL
```

## b11889..b11906 diff for the path

```
$ git -C $R diff --stat d854d98ba... 4d71b42fd... -- tools/server/server-context.cpp
 tools/server/server-context.cpp | 15 +++++++++------
 1 file changed, 9 insertions(+), 6 deletions(-)

$ git -C $R show c6fb3b5be -- tools/server/server-context.cpp | grep "^@@"
@@ -1012,16 +1012,17 @@ public:
@@ -1397,6 +1398,8 @@ private:
@@ -1705,9 +1708,9 @@
@@ -5127,7 +5130,7 @@ server_context_meta server_context::get_meta() const:
```

Only commit in the range touching this file is `c6fb3b5be mtmd: add mtmd_helper_get_capabilities (#31183)`;
it replaces `mtmd_gen_audio_get_info`/`mtmd_helper_model_can_chat`/`mtmd_support_*` calls with a cached
`mtmd_cap` struct (hunks at 1012, 1398, 1708, 5130) and adds 3 net lines above the slots handlers. It does
not touch `get_slots`/`post_slots`, `endpoint_slots`, or `slot_save_path`. Every hunk is above line 5363,
so the +3 shift is uniform for both guards.

## Callers / surrounding behaviour at b11906

```
$ git -C $R show 4d71b42fd...:tools/server/server.cpp | grep -n "get_slots\|post_slots"
213:    ctx_http.get ("/slots",                    ex_wrapper(routes.get_slots));
214:    ctx_http.post("/slots/:id_slot",           ex_wrapper(routes.post_slots));
483:        routes.get_slots                   = models_routes->proxy_get;
484:        routes.post_slots                  = models_routes->proxy_post;

$ diff <(git -C $R show 704366d76f...:tools/server/server.cpp | sed -n '318,319p') \
       <(git -C $R show 4d71b42fd...:tools/server/server.cpp | sed -n '213,214p')
ROUTES_EQUAL

$ git -C $R show 4d71b42fd...:tools/server/server-context.cpp | grep -n "endpoint_slots"
5575:        { "endpoint_slots",              params.endpoint_slots },
5686:        if (!params.endpoint_slots) {

$ git -C $R show 4d71b42fd...:common/arg.cpp | grep -n "slot-save-path\|--slots"
3655:        {"--slots"},
3663:        {"--slot-save-path"}, "PATH",
```

`common/arg.cpp`, `tools/server/server-common.{cpp,h}` (where `format_error_response` lives) and
`tools/server/server.cpp` are not in the b11889..b11906 diffstat;

```
$ git -C $R show 4d71b42fd...:tools/server/server-context.cpp | grep -n "handle_slots_save\|handle_slots_restore\|handle_slots_erase"
5746:            return handle_slots_save(req, id_slot);
5749:            return handle_slots_restore(req, id_slot);
5752:            return handle_slots_erase(req, id_slot);
6633:std::unique_ptr<server_res_generator> server_routes::handle_slots_save(const server_http_req & req, int id_slot) {
6669:std::unique_ptr<server_res_generator> server_routes::handle_slots_restore(const server_http_req & req, int id_slot) {
6706:std::unique_ptr<server_res_generator> server_routes::handle_slots_erase(const server_http_req & req, int id_slot) {
```

(dispatch block `action` parse + save/restore/erase at b11906:5743-5756, pin 5424-5435)
 `tools/server/server-models.cpp`
changes one comment only:

```
$ git -C $R diff d854d98ba... 4d71b42fd... -- tools/server/server-models.cpp
-        // same rule as mtmd_helper_model_can_chat()
+        // same rule as mtmd_helper_get_capabilities()
```

Full diffstat of the range: 65 files, `9 insertions(+), 6 deletions(-)` in server-context.cpp plus
ggml/sycl/vulkan/metal/ui/deepseek4.1 work; nothing else under `tools/server` except
`tests/utils.py` (2 lines) and the comment above.

## Fragment scored

```
$ python3 .../tools/check-fragment.py .../out/X1R04/rows.tsv /fast/scratch/hyaku/kama-r46/X1R04/chk
VALID S114 holds
VALID S115 holds
EXIT=0
```
