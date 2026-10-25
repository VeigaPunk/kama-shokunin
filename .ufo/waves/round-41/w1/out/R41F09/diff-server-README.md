diff --git a/tools/server/README.md b/tools/server/README.md
index e1c5804da..8e27e37b8 100644
--- a/tools/server/README.md
+++ b/tools/server/README.md
@@ -563,7 +563,7 @@ These words will not be included in the completion, so make sure to add them to
 
 `dry_penalty_last_n`: How many tokens to scan for repetitions. Default: `64`, where `0` is disabled.
 
-`dry_sequence_breakers`: Specify an array of sequence breakers for DRY sampling. Only a JSON array of strings is accepted. Default: `['\n', ':', '"', '*']`
+`dry_sequence_breakers`: Specify an array of sequence breakers for DRY sampling. Only a JSON array of strings is accepted. At most 64 distinct breakers, duplicates are ignored. Default: `['\n', ':', '"', '*']`
 
 `xtc_probability`: Set the chance for token removal via XTC sampler. Default: `0.0`, which is disabled.
 
@@ -771,37 +771,125 @@ This endpoint also supports multimodal embeddings. See the documentation for the
 
 ### POST `/reranking`: Rerank documents according to a given query
 
+> [!IMPORTANT]
+>
+> This endpoint is **not** OAI-compatible.
 Similar to https://jina.ai/reranker/ but might change in the future.
-Requires a reranker model (such as [bge-reranker-v2-m3](https://huggingface.co/BAAI/bge-reranker-v2-m3)) and the `--embedding --pooling rank` options.
+Requires a reranker model (such as [bge-reranker-v2-m3](https://huggingface.co/BAAI/bge-reranker-v2-m3)) and the `--embedding --pooling rank` or `--reranking` options.
 
-*Options:*
+`query` and each `documents`/`texts` element accept a plain string, or
+(for multimodal rerankers such as Qwen3-VL-Reranker) an object of the form
+`{"text": string | [strings], "image": url | data-uri | raw-base64 | [urls]}`.
+All keys are optional; a plain string is treated as `{"text": "..."}`.
 
-`query`: The query against which the documents will be ranked.
-
-`documents`: An array strings representing the documents to be ranked.
+Options: `top_n` (default: all), `model` (echoed in the Jina response), `return_text` (TEI only).
 
 *Aliases:*
   - `/rerank`
   - `/v1/rerank`
   - `/v1/reranking`
 
-*Examples:*
+The format is selected by which key carries the documents: `texts` (TEI, same input shape as Jina,
+set `return_text: true` to echo document text) or `documents` (Jina, multimodal supported).
+
+**Text only (TEI format)** - `query` + `texts`; set `return_text: true` to echo document text:
 
 ```shell
 curl http://127.0.0.1:8012/v1/rerank \
     -H "Content-Type: application/json" \
     -d '{
-        "model": "some-model",
-            "query": "What is panda?",
-            "top_n": 3,
-            "documents": [
-                "hi",
-            "it is a bear",
-            "The giant panda (Ailuropoda melanoleuca), sometimes called a panda bear or simply panda, is a bear species endemic to China."
-            ]
+        "query": "What is machine learning?",
+        "texts": [
+            "Machine learning is a subset of artificial intelligence.",
+            "A python is a large snake."
+        ],
+        "return_text": true
     }' | jq
 ```
 
+**Multimodal (Jina Format)** - mix text and images in `query` and/or `documents`:
+
+```shell
+curl http://127.0.0.1:8012/v1/rerank \
+    -H "Content-Type: application/json" \
+    -d '{
+        "model": "Qwen/Qwen3-VL-Reranker-2B",
+        "query": {
+            "text": "A city skyline with tall buildings and a river",
+            "image": "data:image/jpeg;base64,<base64>"
+        },
+        "documents": [
+            "a plain string document is also valid",
+            {
+                "text": "A photograph of the Boston skyline at dusk",
+                "image": "https://example.com/skyline.jpg"
+            },
+            {
+                "text": "caption for the two-figure spread",
+                "image": ["https://example.com/fig1.png", "data:image/jpeg;base64,<base64>"]
+            }
+        ],
+        "top_n": 2
+    }' | jq
+```
+
+Jina format returns a wrapped object with `model`, `object`, `usage` (`prompt_tokens` is the sum
+of `tokens_evaluated` across all scored pairs), and a `results` array of `{index, relevance_score}`.
+TEI format returns a bare array of `{index, score}` (+ `text` when `return_text: true`).
+Both are sorted descending by score and truncated to `top_n`; the score is the match probability in `[0, 1]`.
+
+Images never appear in any response shape.
+
+> **NOTE:** **Input size limit:** A bidirectional-encoder reranker (e.g. `bge-reranker-v2-m3`) must fit the whole prompt within
+`--ubatch-size`; if the input is too large to process, increase `--ubatch-size`.
+Causal decoder rerankers (e.g. `Qwen3-VL-Reranker`) have no such limitation.
+
+
+
+### POST `/tts`: Generate speech audio from text
+
+Returns raw audio bytes (`audio/wav` by default) rather than JSON. For more info, see [tts/README.md](../tts/README.md)
+
+*Options:*
+
+`input`: The text to speak (alias: `prompt`).
+
+`lang`: Language code for the utterance (model-dependent, e.g. `en`, `zh`). Optional.
+
+`speaker_ref_b64`: Base64-encoded reference audio to clone the speaker's voice. Optional. Alternatively, upload the reference audio as a `speaker_ref` file field via `multipart/form-data` (see example below) - if both are provided, the uploaded file takes precedence.
+
+`top_k`, `top_p`: Sampling params for the acoustic code predictor. Optional, model-dependent defaults apply.
+
+`repeat_penalty`: Repetition penalty applied to the backbone sampler over the whole generation (default `1.05`). Without this, the backbone can loop and re-generate the same utterance.
+
+`seed`: RNG seed for both the backbone sampler and the codec/vocoder (`-1` = random, the default). Set to a fixed value for reproducible output.
+
+`n_predict`: Max number of audio frames to generate. Defaults to `512`; generation normally stops earlier once the model emits an end-of-speech token.
+
+`response_format`: `wav` (default) or `pcm` (raw `float32` little-endian mono samples, no header; the response `Content-Type` carries the sample rate, e.g. `audio/pcm;rate=24000;encoding=float;bits=32`).
+
+`stream`: If `true`, the response is streamed as audio becomes available instead of waiting for the full generation to finish. WAV streaming writes an RFC-noncompliant header with an unknown (`0xFFFFFFFF`) size field, since the final length isn't known up front; most players and decoders (ffmpeg, VLC, ...) handle this by reading until EOF.
+
+Note: it's highly recommended to always provide a speaker reference voice; otherwise, the model's performance may be degraded.
+
+*Examples:*
+
+```shell
+curl -X POST http://127.0.0.1:9931/tts \
+    -H "Content-Type: application/json" \
+    -d '{"input": "Hello, this is a test."}' \
+    -o output.wav
+```
+
+With a speaker reference uploaded as a file (`multipart/form-data`), instead of base64-encoding it into the JSON body:
+
+```shell
+curl -X POST http://127.0.0.1:9931/tts \
+    -F "input=Hello, this is a test." \
+    -F "speaker_ref=@/path/to/speaker-reference.wav;type=audio/wav" \
+    -o output.wav
+```
+
 ### POST `/infill`: For code infilling.
 
 Takes a prefix and a suffix and returns the predicted completion as stream.
@@ -1262,11 +1350,12 @@ Each object in `data` has an `architecture` object. It has two string arrays:
 - `input_modalities` lists what the model can read. It always has `text`, plus each media type that the model supports.
 - `output_modalities` lists what the model can produce.
 
-One output value is special:
+Some output values are special:
 
 | Value | Meaning |
 |---|---|
 | `decisions` | The model is a native decision model. Serve it with [`/v1/systemone`](#post-v1systemone-typesafe-compatible-system-one-api). |
+| `audio` | The model can generate speech. Serve it with [`/tts`](#post-tts-generate-speech-audio-from-text). A TTS-only model has `["audio"]` without `text`. |
 
 A language model that classifies with prompts does not get `decisions`. Only native decision models do.
 
@@ -1491,6 +1580,31 @@ Acts on an in-flight completion identified by its `id` (the `id` field streamed
 
 Returns a JSON object with a boolean `success` field, and an optional `message` field describing the reason when `success` is `false`.
 
+### WebSocket `/v1/realtime`: Realtime transcription
+
+Transcribes streamed audio, for models with a streaming audio encoder. Compatible with OAI `/v1/realtime` schema.
+
+Audio must be PCM16, mono, at the model sample rate. The sample rate is returned in `session.created` as `audio.input.format.rate`. Each `input_audio_buffer.append` carries a base64-encoded chunk of PCM16 samples.
+
+*Client events:*
+
+- `session.update`: accepted for compatibility, the server replies with `session.updated`
+- `input_audio_buffer.append`: `audio` holds base64 PCM16 samples
+- `input_audio_buffer.commit`: flushes the audio received so far, so the words still held back by the model's delay are produced. The server replies with `input_audio_buffer.committed` and starts a new item. With `"final": true`, the input ends instead and the last item is completed once the stream drains.
+- `input_audio_buffer.clear`: accepted for compatibility, audio already sent cannot be discarded
+
+Closing the websocket also ends the input.
+
+*Server events:*
+
+- `session.created` and `session.updated`: carry the `session` object
+- `conversation.item.input_audio_transcription.delta`: `delta` holds the new text for `item_id`
+- `conversation.item.input_audio_transcription.completed`: `transcript` holds the full text of `item_id`
+- `input_audio_buffer.committed`: `item_id` of the committed item, `previous_item_id` of the item committed before it (`null` for the first one)
+- `error`: `error.message` describes the problem
+
+Note that words held back by the model's delay at the time of a commit are attributed to the next item.
+
 ### POST `/v1/responses`: OpenAI-compatible Responses API
 
 *Options:*
@@ -1649,6 +1763,8 @@ See [Anthropic Messages API documentation](https://docs.anthropic.com/en/api/mes
 
 `top_k`: Top-k sampling
 
+`extra_params`: llama.cpp parameters that the Anthropic API has no field for, such as `seed`, `min_p` or `repeat_penalty`, as an object (e.g. `{"seed": 42, "min_p": 0.05}`). Its keys are merged into the converted request and behave as on `/v1/chat/completions`.
+
 `stop_sequences`: Array of stop sequences
 
 `stream`: Enable streaming (default: false)
@@ -1669,7 +1785,8 @@ curl http://localhost:9931/v1/messages \
     "system": "You are a helpful assistant.",
     "messages": [
       {"role": "user", "content": "Hello!"}
-    ]
+    ],
+    "extra_params": {"seed": 42, "min_p": 0.05}
   }'
 ```
 
@@ -1725,13 +1842,13 @@ Follows the [TypeSafe API](https://docs.typesafe.ai/api), streaming is not suppo
 
 The questions of a request are answered independently, an answer does not depend on the other questions. The exception is clef: it reads all the questions in one prompt and decides them jointly.
 
-The number of options of a `choice` question is limited by the model, for example: 52 for openjev, 255 for granite-switch, laya, clef, pplx-decider, vllm-decision2, vllm-d3, lfm2-d1 and lfm2-d1-omni. For laya, long questions and options are truncated to the token budget the model was trained with.
+The number of options of a `choice` question is limited by the model, for example: 52 for openjev, 255 for granite-switch, laya, clef, pplx-decider, vllm-decision2, vllm-d3, lfm2-d1, lfm2-d1-omni and h2o-lightning. For laya, long questions and options are truncated to the token budget the model was trained with.
 
-For laya, clef, vllm-d3 and lfm2-d1-omni, the whole prompt is evaluated in one batch: it must fit in `--ubatch-size`. An lfm2-d1-omni prompt is cut to 16384 tokens. For vllm-decision2, the options of a question and the end of the prompt must fit in one batch. A server that runs clef only serves this endpoint, text generation is not available. A decision model that is also a text model, such as granite-switch, serves both and reports `["text", "decisions"]`.
+For laya, clef, vllm-d3 and lfm2-d1-omni, the whole prompt is evaluated in one batch: it must fit in `--ubatch-size`. An lfm2-d1-omni prompt is cut to 16384 tokens. For vllm-decision2, the options of a question and the end of the prompt must fit in one batch. An h2o-lightning state longer than 32000 tokens keeps its first and last 16000 tokens. A server that runs clef only serves this endpoint, text generation is not available. A decision model that is also a text model, such as granite-switch, serves both and reports `["text", "decisions"]`.
 
 *Image input:*
 
-Image input needs a model that supports it (for example: openjev, clef, pplx-decider, vllm-d3, lfm2-d1, lfm2-d1-omni) and its multimodal projector, see `--mmproj`.
+Image input needs a model that supports it (for example: openjev, clef, pplx-decider, vllm-d3, lfm2-d1, lfm2-d1-omni, h2o-lightning) and its multimodal projector, see `--mmproj`.
 
 Images can be given in two ways, and both can be used in the same request:
 
@@ -1760,6 +1877,8 @@ All the images are placed before the state in the prompt, the ones from `files`
 
 The probabilities are scaled with the temperatures stored in the model file. They are not guaranteed to be calibrated for your data.
 
+For h2o-lightning, `score` questions can have 1 to 255 levels, and the `instructions` and `type` of a question can be left out (`choice` by default; `"instructions": null` is written as `null`).
+
 *Examples:*
 
 ```shell
@@ -1990,6 +2109,8 @@ For **GET** endpoints (`/props`, `/metrics`, etc.) The router uses the `model` q
 GET /props?model=ggml-org%2Fgemma-3-4b-it-GGUF%3AQ4_K_M
 ```
 
+For the **WebSocket** endpoint (`/v1/realtime`) The router also uses the `model` query parameter.
+
 By default, the model will be loaded automatically if it's not loaded. To disable this, add `--no-models-autoload` when starting the server. Additionally, you can include `?autoload=true|false` in the query param to control this behavior per-request.
 
 ### GET `/models`: List available models
@@ -2025,7 +2146,7 @@ Note:
     - If a model is not running, it will be added or updated according to the source
 2. When the model is loaded, the info from `/v1/models` is forwarded to router's `/v1/models`. This includes metadata about the model and the runtime instance.
 
-Each object in `data` has the same `architecture` object as [`GET /v1/models`](#get-v1models-openai-compatible-model-info-api) of a direct server. The server computes both arrays offline. It does not load the model, download files, or run inference. `output_modalities` comes from the GGUF metadata. `input_modalities` comes from the projector file. A native decision model shows `decisions` before its first load, after unload, and while it sleeps:
+Each object in `data` has the same `architecture` object as [`GET /v1/models`](#get-v1models-openai-compatible-model-info-api) of a direct server. The server computes both arrays offline. It does not load the model, download files, or run inference. `output_modalities` comes from the GGUF metadata, plus `audio` when the projector file can generate speech. `input_modalities` comes from the projector file. A native decision model shows `decisions` before its first load, after unload, and while it sleeps:
 
 ```json
 {
