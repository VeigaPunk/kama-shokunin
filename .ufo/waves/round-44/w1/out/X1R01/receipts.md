# X1R01 receipts — C1 rows S140-S145 (pin 704366d76 b11755 -> release d854d98b b11889)

## blobs
$ git -C llama.cpp rev-parse 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad:tools/server/server-schema.cpp
54e126aa0c3572895042cd0a8c4faf4a0eb0b9f7
$ git -C llama.cpp rev-parse d854d98bae598388ecea1ed84396587e5edc326d:tools/server/server-schema.cpp
0a14a9620961ff627348952112b4a9a6a0513c43

## commits touching the file pin..release
63412d873 llama: fix exhausting CPU and MEM caused by dry sequence breaker (#31035)
5c0b49a23 server : add POST /tts endpoint for TTS models (#26603)

## diffstat
 tools/server/server-schema.cpp | 71 ++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 71 insertions(+)

## anchored lines, pin (40-63)
40	    add((new field_num("sse_ping_interval", params.sse_ping_interval))
41	        ->set_hard_limits(-1, INT32_MAX)
42	        ->set_desc("Interval in seconds between SSE comment pings emitted while the stream stays silent, -1 disables pings"));
43	
44	    add((new field_num("n_predict", params.n_predict))
45	        ->set_hard_limits(-1, INT32_MAX)
46	        ->add_alias("max_completion_tokens")
47	        ->add_alias("max_tokens")
48	        ->set_desc("Set the maximum number of tokens to predict. When 0, no tokens will be generated but the prompt is evaluated into the cache"));
49	
50	    add((new field_num("n_indent", params.n_indent))
51	        ->set_hard_limits(0, INT32_MAX)
52	        ->set_desc("Specify the minimum line indentation for the generated text in number of whitespace characters. Useful for code completion tasks"));
53	
54	    add((new field_num("n_keep", params.n_keep))
55	        ->set_hard_limits(-1, INT32_MAX)
56	        ->set_desc("Specify the number of tokens from the initial prompt to retain when context size is exceeded. Use -1 to retain all tokens from the prompt"));
57	
58	    add((new field_num("n_discard", params.n_discard))
59	        ->set_hard_limits(0, INT32_MAX)
60	        ->set_desc("Number of tokens after n_keep that may be discarded when shifting context (0 = half context)"));
61	
62	    add((new field_num("n_cmpl", params.n_cmpl))
63	        ->set_hard_limits(1, params_base.n_parallel)

## anchored lines, release (42-65)
42	    add((new field_num("sse_ping_interval", params.sse_ping_interval))
43	        ->set_hard_limits(-1, INT32_MAX)
44	        ->set_desc("Interval in seconds between SSE comment pings emitted while the stream stays silent, -1 disables pings"));
45	
46	    add((new field_num("n_predict", params.n_predict))
47	        ->set_hard_limits(-1, INT32_MAX)
48	        ->add_alias("max_completion_tokens")
49	        ->add_alias("max_tokens")
50	        ->set_desc("Set the maximum number of tokens to predict. When 0, no tokens will be generated but the prompt is evaluated into the cache"));
51	
52	    add((new field_num("n_indent", params.n_indent))
53	        ->set_hard_limits(0, INT32_MAX)
54	        ->set_desc("Specify the minimum line indentation for the generated text in number of whitespace characters. Useful for code completion tasks"));
55	
56	    add((new field_num("n_keep", params.n_keep))
57	        ->set_hard_limits(-1, INT32_MAX)
58	        ->set_desc("Specify the number of tokens from the initial prompt to retain when context size is exceeded. Use -1 to retain all tokens from the prompt"));
59	
60	    add((new field_num("n_discard", params.n_discard))
61	        ->set_hard_limits(0, INT32_MAX)
62	        ->set_desc("Number of tokens after n_keep that may be discarded when shifting context (0 = half context)"));
63	
64	    add((new field_num("n_cmpl", params.n_cmpl))
65	        ->set_hard_limits(1, params_base.n_parallel)

## 400 path: hard-limit throw, release server-schema.cpp 602-622
602	template <typename T>
603	void field_num<T>::eval(field_eval_context & ctx, const json & data) {
604	    for (const auto & n : name) {
605	        if (has_value(data, n)) {
606	            handle_with_catch(n, [&]() {
607	                if (custom_handler) {
608	                custom_handler(ctx, data);
609	                } else if (!is_hard_limit) {
610	                    val = std::max(min, std::min(max, data.at(n).template get<T>()));
611	                } else {
612	                    T tmp = data.at(n).template get<T>();
613	                    if (tmp < min || tmp > max) {
614	                        throw std::invalid_argument(std::string("Value must be between ") + std::to_string(min) + " <= value <= " + std::to_string(max) + ", but got " + std::to_string(tmp));
615	                    }
616	                    val = tmp;
617	                }
618	            });
619	            return;
620	        }
621	    }
622	}

## error mapping, release server-common.cpp 93-100
93	json format_error_response(const std::string & message, const enum error_type type) {
94	    std::string type_str;
95	    int code = 500;
96	    switch (type) {
97	        case ERROR_TYPE_INVALID_REQUEST:
98	            type_str = "invalid_request_error";
99	            code = 400;
100	            break;

## handler catch, release server-context.cpp 5275-5279
5275	        rd.post_tasks(std::move(tasks), chat_session);
5276	    } catch (const std::exception & e) {
5277	        res->error(format_error_response(e.what(), ERROR_TYPE_INVALID_REQUEST));
5278	        return res;
5279	    }

## route, release server.cpp 178-179
178	    ctx_http.post("/completion",               ex_wrapper(routes.post_completions)); // legacy
179	    ctx_http.post("/completions",              ex_wrapper(routes.post_completions));

## field backing types at release
d854d98bae598388ecea1ed84396587e5edc326d:common/common.h:458:    int32_t n_predict             =    -1; // max. number of new tokens to predict, -1 == no limit
d854d98bae598388ecea1ed84396587e5edc326d:common/common.h:462:    int32_t n_keep                =     0; // number of tokens to keep from initial prompt
d854d98bae598388ecea1ed84396587e5edc326d:common/common.h:464:    int32_t n_parallel            =     1; // number of parallel sequences to decode
d854d98bae598388ecea1ed84396587e5edc326d:common/common.h:636:    int32_t sse_ping_interval   = 30;            // SSE ping interval in seconds
d854d98bae598388ecea1ed84396587e5edc326d:tools/server/server-task.h:72:    int32_t n_discard =  0; // number of tokens after n_keep that may be discarded when shifting context, 0 defaults to half
d854d98bae598388ecea1ed84396587e5edc326d:tools/server/server-task.h:74:    int32_t n_indent  =  0; // minimum line indentation for the generated text in number of whitespace characters
d854d98bae598388ecea1ed84396587e5edc326d:tools/server/server-task.h:75:    int32_t n_cmpl    =  1; // number of completions to generate from this prompt

## duplicate-name check (release) — n_predict also in TTS schema only
42:    add((new field_num("sse_ping_interval", params.sse_ping_interval))
46:    add((new field_num("n_predict", params.n_predict))
52:    add((new field_num("n_indent", params.n_indent))
56:    add((new field_num("n_keep", params.n_keep))
60:    add((new field_num("n_discard", params.n_discard))
64:    add((new field_num("n_cmpl", params.n_cmpl))
554:    add((new field_num("n_predict", task.params.n_predict))

## checker run (exact command + output)
$ python3 .ufo/waves/round-44/tools/check-fragment.py c1 .ufo/waves/round-44/w1/out/X1R01/fragment.tsv /fast/scratch/hyaku/kama-r44/X1R01/chk
pop=91 rows=91 valid=85 unverified=6 unchanged=4 holds=81 reworded=0 drifted=0 removed=0 flags_missing=0 section=0 met=False
VALID S140
VALID S141
VALID S142
VALID S143
VALID S144
VALID S145
