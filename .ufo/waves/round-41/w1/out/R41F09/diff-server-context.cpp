diff --git a/tools/server/server-context.cpp b/tools/server/server-context.cpp
index b2116b174..a5cba1d71 100644
--- a/tools/server/server-context.cpp
+++ b/tools/server/server-context.cpp
@@ -1,4 +1,7 @@
 #include "server-context.h"
+#include <atomic>
+#include <thread>
+#include "base64.hpp"
 #include "server-chat.h"
 #include "server-common.h"
 #include "server-decision.h"
@@ -17,10 +20,12 @@
 #include "speculative.h"
 #include "mtmd.h"
 #include "mtmd-helper.h"
+#include "base64.hpp"
 
 #include <algorithm>
 #include <cstddef>
 #include <cinttypes>
+#include <deque>
 #include <exception>
 #include <memory>
 #include <filesystem>
@@ -40,6 +45,14 @@
 constexpr int HTTP_POLLING_SECONDS = 1;
 
 static common_speculative_output_limits server_output_limits(const common_params & params) {
+    if (!params.mmproj.path.empty()) {
+        const auto mcaps = mtmd_get_cap_from_file(params.mmproj.path.c_str());
+        if (mcaps.gen_audio) {
+            // some TTS models decode with embeddings output for the whole batch
+            return { params.n_batch, params.n_batch };
+        }
+    }
+
     if (params.embedding ||
             (params.pooling_type != LLAMA_POOLING_TYPE_UNSPECIFIED && params.pooling_type != LLAMA_POOLING_TYPE_NONE)) {
         return { params.n_batch, 1 };
@@ -254,6 +267,27 @@ struct server_slot {
     mtmd_context * mctx = nullptr;
     mtmd::batch_ptr mbatch = nullptr;
 
+    struct tts_ctx {
+        mtmd_helper::gen_audio ctx;
+        std::vector<float> h_state_prompt; // the first h_state after step_prompt done
+        const float * h_state;
+        llama_token   sampled;
+        int32_t       n_decoded;
+        bool          stop;
+        bool is_supported() const {
+            return ctx.valid();
+        }
+        void reset() {
+            ctx.reset();
+            h_state_prompt.clear();
+            h_state   = nullptr;
+            sampled   = LLAMA_TOKEN_NULL;
+            n_decoded = 0;
+            stop      = false;
+        }
+    };
+    tts_ctx tts;
+
     // speculative decoding
     common_speculative * spec;
 
@@ -360,8 +394,14 @@ struct server_slot {
 
     // for TTS models, this is the embd generated from prev step, decode this to generate next hidden state
     // corresponding to one token position (size = n_embd)
+    // for realtime transcription, these are the rows from the last audio stream step (size = n_rows * n_embd)
     std::vector<float> inp_embd;
 
+    // realtime transcription, see SERVER_TASK_TYPE_TRANSCRIBE_RT
+    mtmd::audio_stream_ptr audio_stream;
+    bool audio_wait = false; // the stream needs more audio before it can produce rows
+    std::deque<int64_t> audio_commit_rows; // end row of each non-final commit not yet completed
+
     server_slot_stats stats;
 
     // accepted tokens per draft position
@@ -413,6 +453,13 @@ struct server_slot {
 
         // clear multimodal state
         mbatch.reset();
+
+        tts.reset();
+
+        audio_stream.reset();
+        audio_wait = false;
+        audio_commit_rows.clear();
+        inp_embd.clear();
     }
 
     void init_sampler() const {
@@ -542,16 +589,28 @@ struct server_slot {
     // add sampled token of this slot to the batch, optionally add the speculative draft tokens if any
     void handle_last_sampled_token(server_batch & batch) {
         bool add_ok = true;
+        // the audio stream has no token before the first step, track the position with a dummy token
+        const llama_token tok_track = sampled == LLAMA_TOKEN_NULL ? 0 : sampled;
         if (spec_draft.empty()) {
             // no speculative decoding
             i_batch = batch.size();
 
             if (!inp_embd.empty()) {
-                // text embeddings broadcast the same position across the M-RoPE sections
-                const llama_pos p = prompt.tokens.pos_next();
-                const llama_pos pos[GGML_MROPE_SECTIONS] = { p, p, p, 0 };
-                GGML_ASSERT((int32_t) inp_embd.size() == batch.n_embd);
-                add_ok &= batch.add_embd(id, inp_embd.data(), pos, true, false);
+                const int32_t n_rows = (int32_t) inp_embd.size() / batch.n_embd;
+                GGML_ASSERT((int32_t) inp_embd.size() == n_rows * batch.n_embd);
+                i_batch = batch.size() + n_rows - 1;
+                for (int32_t i = 0; i < n_rows; i++) {
+                    // text embeddings broadcast the same position across the M-RoPE sections
+                    const llama_pos p = prompt.tokens.pos_next();
+                    const llama_pos pos[GGML_MROPE_SECTIONS] = { p, p, p, 0 };
+                    add_ok &= batch.add_embd(id, inp_embd.data() + (size_t) i * batch.n_embd, pos, i == n_rows - 1, false);
+                    if (i < n_rows - 1) {
+                        prompt.tokens.push_back(tok_track);
+                    }
+                }
+                if (audio_stream) {
+                    inp_embd.clear(); // rows are consumed, the next step produces new ones
+                }
             } else {
                 add_ok &= batch.add(id, sampled, prompt.tokens.pos_next(), true, false);
             }
@@ -579,7 +638,7 @@ struct server_slot {
 
         GGML_ASSERT(add_ok && "batch must be large enough to hold the sampled and draft tokens");
 
-        prompt.tokens.push_back(sampled);
+        prompt.tokens.push_back(tok_track);
         prompt.tokens.insert(spec_draft);
     }
 
@@ -595,7 +654,12 @@ struct server_slot {
 
             // do not keep context of the child slots - the parent's context is enough
             // nor of the stateless slots - no task ever reuses it
-            if (task->is_child() || task->is_stateless()) {
+            if (task->is_child() || task->is_stateless() || audio_stream) {
+                prompt_clear();
+            }
+
+            // mtmd_helper always re-eval the whole prompt
+            if (task->type == SERVER_TASK_TYPE_TTS) {
                 prompt_clear();
             }
 
@@ -952,6 +1016,14 @@ public:
     mtmd_helper_init_opt init_opt = mtmd_helper_init_opt_default();
     const llama_vocab * vocab = nullptr;
 
+    bool has_cap_tts() const {
+        return mctx != nullptr && mtmd_gen_audio_get_info(mctx).type != MTMD_GEN_AUDIO_TYPE_NONE;
+    }
+
+    bool has_cap_chat() const {
+        return mctx == nullptr || mtmd_helper_model_can_chat(ctx_tgt, mctx);
+    }
+
     server_decision_context decision;
 
     server_queue    queue_tasks;
@@ -1180,7 +1252,8 @@ private:
         }
 
         // optionally fit mmproj memory usage
-        if (has_mmproj && params_base.fit_params) {
+        // on resume params_base already holds the margin from the first load
+        if (has_mmproj && params_base.fit_params && !is_resume) {
             const auto & mmproj_mem = mmproj_usage.backend_mem_usage;
             const int64_t t_elapsed = mmproj_usage_t_us;
             if (!mmproj_mem.empty()) {
@@ -1439,6 +1512,10 @@ private:
             slot.mctx                   = mctx;
             slot.prompt.tokens.has_mtmd = mctx != nullptr;
 
+            if (has_cap_tts()) {
+                slot.tts.ctx.init(ctx_tgt, mctx);
+            }
+
             SLT_TRC(slot, "new slot, n_ctx = %d\n", slot.n_ctx);
 
             slot.callback_on_release = [this](int id_slot) {
@@ -1920,6 +1997,20 @@ private:
 
         SLT_DBG(slot, "launching slot : %s\n", safe_json_to_str(slot.to_json()).c_str());
 
+        if (task.type == SERVER_TASK_TYPE_TTS) {
+            GGML_ASSERT(has_cap_tts()); // should already checked in route handler
+            if (!slot.tts.is_supported()) {
+                slot.tts.ctx.init(ctx_tgt, slot.mctx);
+            }
+            // mtmd_helper always re-eval the whole prompt
+            slot.prompt_clear();
+            task.tts_inp.data.seq_id = slot.id;
+            if (slot.tts.ctx.set_input(task.tts_inp.get()) != 0) {
+                send_error(task, "failed to process TTS prompt", ERROR_TYPE_SERVER);
+                return false;
+            }
+        }
+
         // initialize samplers
         if (task.need_sampling()) {
             try {
@@ -1937,6 +2028,9 @@ private:
             // TODO: getting pre sampling logits is not yet supported with backend sampling
             use_backend_sampling &= !need_pre_sample_logits;
 
+            // TODO: check verify if this actually works with TTS
+            use_backend_sampling &= task.type != SERVER_TASK_TYPE_TTS;
+
             // TODO: tmp until backend sampling is fully implemented
             if (use_backend_sampling) {
                 llama_set_sampler(ctx_tgt, slot.id, common_sampler_get(slot.smpl.get()));
@@ -1962,9 +2056,30 @@ private:
 
         slot.task = std::make_unique<const server_task>(std::move(task));
 
-        slot.state = slot.task->is_child()
-            ? SLOT_STATE_WAIT_OTHER // wait for the parent to process prompt
-            : SLOT_STATE_STARTED;
+        if (slot.task->type == SERVER_TASK_TYPE_TTS) {
+            slot.state = SLOT_STATE_PROCESSING_PROMPT;
+        } else {
+            slot.state = slot.task->is_child()
+                ? SLOT_STATE_WAIT_OTHER // wait for the parent to process prompt
+                : SLOT_STATE_STARTED;
+        }
+
+        // no prompt, the rows come from the audio stream, which audio controls reach from now on
+        if (slot.task->type == SERVER_TASK_TYPE_TRANSCRIBE_RT) {
+            slot.audio_stream.reset(mtmd_audio_stream_init(mctx, mtmd_audio_stream_params_default()));
+            if (!slot.audio_stream) {
+                send_error(slot, "failed to initialize the audio stream", ERROR_TYPE_SERVER);
+                slot.release();
+                return false;
+            }
+            slot.prompt_clear();
+            slot.init_sampler();
+            slot.sampled = LLAMA_TOKEN_NULL;
+            slot.i_batch = -1;
+            slot.stats.update_prompt_start();
+            slot.state = SLOT_STATE_GENERATING;
+            send_partial_response(slot, {}, false, true);
+        }
 
         // reset server kill-switch counter
         n_empty_consecutive = 0;
@@ -2227,6 +2342,18 @@ private:
         queue_results.send(std::move(res));
     }
 
+    void send_tts_result(server_slot & slot, int32_t sample_rate, const char * data, size_t data_len, bool final) {
+        auto res = std::make_unique<server_task_result_tts>();
+
+        res->id          = slot.task->id;
+        res->index       = slot.task->index;
+        res->sample_rate = sample_rate;
+        res->audio.assign(data, data_len);
+        res->final       = final;
+
+        queue_results.send(std::move(res));
+    }
+
     void send_final_response(server_slot & slot) {
         auto res = std::make_unique<server_task_result_cmpl_final>();
 
@@ -2828,8 +2955,10 @@ private:
         switch (task.type) {
             case SERVER_TASK_TYPE_COMPLETION:
             case SERVER_TASK_TYPE_INFILL:
+            case SERVER_TASK_TYPE_TRANSCRIBE_RT:
             case SERVER_TASK_TYPE_EMBEDDING:
             case SERVER_TASK_TYPE_RERANK:
+            case SERVER_TASK_TYPE_TTS:
             case SERVER_TASK_TYPE_DECISION:
                 {
                     // special case: if input is provided via CLI, tokenize it first
@@ -2915,15 +3044,15 @@ private:
 
                     server_slot * slot = get_slot_by_cmpl_id(task.params.control_cmpl_id);
                     if (slot == nullptr) {
-                        SRV_WRN("control %s on unknown completion id=%s, no live slot\n",
-                                task.params.control_action.c_str(), task.params.control_cmpl_id.c_str());
+                        SRV_WRN("control %d on unknown completion id=%s, no live slot\n",
+                                (int) task.params.control_action, task.params.control_cmpl_id.c_str());
                         res->success = false;
                         res->message = "no active completion for this id";
                         queue_results.send(std::move(res));
                         break;
                     }
 
-                    if (task.params.control_action == "reasoning_end") {
+                    if (task.params.control_action == SERVER_CONTROL_ACTION_REASONING_END) {
                         // the budget sampler only exists when reasoning control was armed
                         if (!slot->task->params.sampling.reasoning_control) {
                             res->success = false;
@@ -2934,6 +3063,26 @@ private:
                         // act on the live slot mid generation, never defer
                         common_sampler_reasoning_budget_force(slot->smpl.get());
                         res->success = true;
+                    } else if (task.params.control_action == SERVER_CONTROL_ACTION_AUDIO_APPEND
+                            || task.params.control_action == SERVER_CONTROL_ACTION_AUDIO_COMMIT
+                            || task.params.control_action == SERVER_CONTROL_ACTION_AUDIO_END) {
+                        if (!slot->audio_stream) {
+                            res->success = false;
+                            res->message = "not a realtime transcription slot";
+                        } else {
+                            auto * stream = slot->audio_stream.get();
+                            if (task.params.control_action == SERVER_CONTROL_ACTION_AUDIO_APPEND) {
+                                mtmd_audio_stream_push(stream, task.params.control_audio.data(), task.params.control_audio.size());
+                            } else {
+                                const int32_t ret = mtmd_audio_stream_flush(stream, task.params.control_action == SERVER_CONTROL_ACTION_AUDIO_END);
+                                // a non-final commit completes its item once the rows of its audio are decoded
+                                if (ret == 0 && task.params.control_action == SERVER_CONTROL_ACTION_AUDIO_COMMIT) {
+                                    slot->audio_commit_rows.push_back(mtmd_audio_stream_get_n_rows_flushed(stream));
+                                }
+                            }
+                            slot->audio_wait = false;
+                            res->success = true;
+                        }
                     } else {
                         res->success = false;
                         res->message = "unknown control action";
@@ -3253,6 +3402,55 @@ private:
     };
 #endif
 
+    // fill slot.inp_embd with the next rows of the audio stream
+    // returns false if the slot has nothing to decode now
+    bool slot_audio_step(server_slot & slot) {
+        if (!slot.inp_embd.empty()) {
+            return true; // rows from a previous step, not decoded yet
+        }
+
+        // every produced row is decoded and its delta queued, the commits ending there are complete
+        const int64_t n_rows = mtmd_audio_stream_get_n_rows(slot.audio_stream.get());
+        while (!slot.audio_commit_rows.empty() && slot.audio_commit_rows.front() <= n_rows) {
+            slot.audio_commit_rows.pop_front();
+            auto res = std::make_unique<server_task_result_cmpl_partial>();
+            res->id                   = slot.task->id;
+            res->index                = slot.task->index;
+            res->n_decoded            = slot.stats.n_gen;
+            res->n_prompt_tokens      = slot.task->n_tokens();
+            res->res_type             = slot.task->params.res_type;
+            res->oaicompat_model      = slot.task->params.oaicompat_model;
+            res->oaicompat_cmpl_id    = slot.task->params.oaicompat_cmpl_id;
+            res->audio_commit_drained = true;
+            queue_results.send(std::move(res));
+        }
+
+        const int32_t n = mtmd_audio_stream_step(slot.audio_stream.get(), slot.sampled);
+        if (n > 0) {
+            const float * rows = mtmd_audio_stream_get_output_embd(slot.audio_stream.get());
+            slot.inp_embd.assign(rows, rows + (size_t) n * batch.n_embd);
+            slot.audio_wait = false;
+            return true;
+        }
+        if (n == 0) {
+            slot.audio_wait = true;
+            return false;
+        }
+        if (n == -2) {
+            send_error(slot, "audio stream error", ERROR_TYPE_SERVER);
+            slot.release();
+            return false;
+        }
+
+        // end of stream
+        slot.stop           = STOP_TYPE_EOS;
+        slot.has_next_token = false;
+        slot.print_timings();
+        send_final_response(slot);
+        slot.release();
+        return false;
+    }
+
     void update_slots() {
 #ifdef DEBUG_TIMINGS
         static int64_t t_prev = 0;
@@ -3268,11 +3466,12 @@ private:
 #endif
 
         // check if all slots are idle
+        // a realtime slot waiting for audio has no work, the next audio control task wakes the loop
         {
             bool all_idle = true;
 
             for (auto & slot : slots) {
-                if (slot.is_processing()) {
+                if (slot.is_processing() && !slot.audio_wait) {
                     all_idle = false;
                     break;
                 }
@@ -3305,6 +3504,14 @@ private:
             return;
         }
 
+        // note: TTS slots bypass the shared batch entirely
+        try {
+            process_tts_slots();
+        } catch (const std::exception & e) {
+            SRV_ERR("process_tts_slots() failed: %s\n", e.what());
+            abort_all_slots("process_tts_slots() failed: " + std::string(e.what()));
+        }
+
         GGML_ASSERT(batch.slot_batched || batch.size() == 0);
 
         if (batch.slot_batched) {
@@ -3367,10 +3574,89 @@ private:
         }
     }
 
+    void process_tts_slots() {
+        iterate(slots, [&](server_slot & slot) {
+            if (!slot.is_processing() || slot.task->type != SERVER_TASK_TYPE_TTS) {
+                return;
+            }
+
+            llama_set_embeddings(ctx_tgt, true);
+
+            if (slot.state == SLOT_STATE_PROCESSING_PROMPT) {
+                const int32_t ret = slot.tts.ctx.step_prompt(llama_n_batch(ctx_tgt));
+                if (ret < 0) {
+                    send_error(slot, "TTS prompt processing failed", ERROR_TYPE_SERVER);
+                    slot.release();
+                } else if (ret == 0) {
+                    // done prompt, do sample and save h_state_prompt
+                    slot.tts.sampled = common_sampler_sample(slot.smpl.get(), ctx_tgt, -1);
+                    common_sampler_accept(slot.smpl.get(), slot.tts.sampled, true);
+                    const float * h_embd = llama_get_embeddings_ith(ctx_tgt, -1);
+                    slot.tts.h_state_prompt.assign(h_embd, h_embd + llama_model_n_embd(model_tgt));
+                    slot.tts.h_state = slot.tts.h_state_prompt.data();
+                    slot.state = SLOT_STATE_GENERATING;
+                }
+                return;
+            }
+
+            const int32_t n_predict = slot.n_predict_max > 0 ? slot.n_predict_max : 512;
+            if (slot.tts.stop || slot.tts.n_decoded >= n_predict) {
+                int32_t      sample_rate = 0;
+                const char * data        = nullptr;
+                size_t       data_len    = 0;
+                // generation truly ends here: force out any sub-window remainder still buffered
+                if (slot.tts.ctx.flush() != 0 || slot.tts.ctx.get_output(&sample_rate, &data, &data_len) != 0) {
+                    send_error(slot, "failed to finalize TTS output", ERROR_TYPE_SERVER);
+                } else {
+                    send_tts_result(slot, sample_rate, data, data_len, true);
+                }
+                slot.release();
+                return;
+            }
+
+            const float * h_state_next = nullptr;
+            bool          stop         = false;
+            if (slot.tts.ctx.step_gen(slot.tts.sampled, slot.tts.h_state, &h_state_next, &stop) != 0) {
+                send_error(slot, "TTS generation failed", ERROR_TYPE_SERVER);
+                slot.release();
+                return;
+            }
+            if (h_state_next == nullptr) {
+                // end-of-speech without a new frame (e.g. pocket-tts eos head)
+                slot.tts.stop = true;
+                return;
+            }
+            slot.tts.h_state = h_state_next;
+            slot.tts.n_decoded++;
+            slot.tts.stop = stop;
+
+            if (!stop) {
+                slot.tts.sampled = common_sampler_sample(slot.smpl.get(), ctx_tgt, -1);
+                common_sampler_accept(slot.smpl.get(), slot.tts.sampled, true);
+            }
+
+            if (slot.task->params.stream) {
+                int32_t      sample_rate = 0;
+                const char * data        = nullptr;
+                size_t       data_len    = 0;
+                if (slot.tts.ctx.get_output(&sample_rate, &data, &data_len) != 0) {
+                    send_error(slot, "TTS streaming output failed", ERROR_TYPE_SERVER);
+                    slot.release();
+                } else if (data_len > 0) {
+                    send_tts_result(slot, sample_rate, data, data_len, false);
+                }
+            }
+        });
+    }
+
     void pre_decode() {
         // apply context-shift if needed
         // TODO: simplify and improve
         iterate(slots, [&](server_slot & slot) {
+            if (slot.task && slot.task->type == SERVER_TASK_TYPE_TTS) {
+                // TTS slots drive their own decode loop in process_tts_slots(), never enter the shared batch
+                return;
+            }
             if (slot.state == SLOT_STATE_GENERATING && slot.prompt.n_tokens() + 1 >= slot.n_ctx) {
                 if (!params_base.ctx_shift) {
                     // this check is redundant (for good)
@@ -3443,10 +3729,14 @@ private:
 
         // determine which slots are generating and drafting
         iterate(slots, [&](server_slot & slot) {
-            if (slot.state != SLOT_STATE_GENERATING) {
+            if (slot.state != SLOT_STATE_GENERATING || slot.task->type == SERVER_TASK_TYPE_TTS) {
                 return;
             }
 
+            if (slot.audio_stream && !slot_audio_step(slot)) {
+                return; // waiting for audio, or the stream ended
+            }
+
             // check if we can batch this slot with the previous one
             if (!slot_batched) {
                 slot_batched = &slot;
@@ -3585,7 +3875,7 @@ private:
                     return; // batch is full, skip remaining slots
                 }
 
-                if (!slot.is_processing()) {
+                if (!slot.is_processing() || slot.task->type == SERVER_TASK_TYPE_TTS) {
                     return;
                 }
 
@@ -3600,6 +3890,11 @@ private:
                     return;
                 }
 
+                // no prompt, the rows come from the audio stream
+                if (slot.task->type == SERVER_TASK_TYPE_TRANSCRIBE_RT) {
+                    return;
+                }
+
                 // this slot still has a prompt to be processed
                 if (slot.state == SLOT_STATE_PROCESSING_PROMPT || slot.state == SLOT_STATE_STARTED) {
                     const auto & input_tokens = slot.task->tokens;
@@ -4521,11 +4816,14 @@ private:
 
             GGML_ASSERT(n_draft > 0);
 
+            // batch indices of the draft tokens, used to get the token probabilities below
+            auto spec_i_batch = std::move(slot.spec_i_batch);
+
             // verify and try to accept the draft
             {
                 common_sampler_ptr smpl_save(common_sampler_clone(slot.smpl.get()));
 
-                GGML_ASSERT(slot.spec_i_batch.size() == n_draft + 1);
+                GGML_ASSERT(spec_i_batch.size() == n_draft + 1);
                 GGML_ASSERT(slot.spec_draft_q.empty() || (slot.spec_draft_q.size() == slot.spec_draft.size()));
                 const auto & synth_probs = common_speculative_get_synth_probs(spec.get());
 
@@ -4536,16 +4834,15 @@ private:
                 if (!synth_probs.empty()) {
                     // synthetic acceptance replaces verification entirely, so it comes first
                     accepted = server_sample_and_accept_synth(
-                            slot.smpl.get(), slot.ctx_tgt, slot.spec_i_batch, slot.spec_draft,
+                            slot.smpl.get(), slot.ctx_tgt, spec_i_batch, slot.spec_draft,
                             synth_probs, slot.spec_synth_rng, slot.spec_is_replay);
                 } else if (slot.spec_is_replay && slot.use_spec_rejection()) {
-                    accepted = server_accept_replay(slot.smpl.get(), slot.ctx_tgt, slot.spec_i_batch, slot.spec_draft);
+                    accepted = server_accept_replay(slot.smpl.get(), slot.ctx_tgt, spec_i_batch, slot.spec_draft);
                 } else if (use_rejection) {
-                    accepted = common_sampler_sample_and_accept_n_rejection(slot.smpl.get(), slot.ctx_tgt, slot.spec_i_batch, slot.spec_draft, slot.spec_draft_q);
+                    accepted = common_sampler_sample_and_accept_n_rejection(slot.smpl.get(), slot.ctx_tgt, spec_i_batch, slot.spec_draft, slot.spec_draft_q);
                 } else {
-                    accepted = common_sampler_sample_and_accept_n(slot.smpl.get(), slot.ctx_tgt, slot.spec_i_batch, slot.spec_draft);
+                    accepted = common_sampler_sample_and_accept_n(slot.smpl.get(), slot.ctx_tgt, spec_i_batch, slot.spec_draft);
                 }
-                slot.spec_i_batch.clear();
 
                 GGML_ASSERT(accepted.size() >= 1);
 
@@ -4632,7 +4929,10 @@ private:
                 result.text_to_send = common_token_to_piece(slot.ctx_tgt, result.tok, accept_special_token(slot, result.tok));
                 result.prob         = 1.0f; // set later
 
-                // TODO: set result.probs
+                // post_sampling_probs is not supported with speculative decoding
+                if (slot.task->params.sampling.n_probs > 0 && !slot.task->params.post_sampling_probs) {
+                    populate_token_probs(slot, result, false, params_base.special, spec_i_batch[i]);
+                }
 
                 slot.stats.n_gen += 1;
 
@@ -4820,11 +5120,14 @@ server_context_meta server_context::get_meta() const {
         /* model_aliases           */ impl->model_aliases,
         /* model_tags              */ impl->model_tags,
         /* model_path              */ impl->params_base.model.path,
-        /* model_output_modalities */ server_model_output_modalities(common_get_decision_type(impl->model_tgt)),
+        /* model_output_modalities */ server_model_output_modalities(impl->model_tgt, impl->has_cap_chat(), impl->has_cap_tts()),
         /* has_mtmd                */ impl->mctx != nullptr,
         /* has_inp_image           */ impl->chat_params.allow_image,
         /* has_inp_audio           */ impl->chat_params.allow_audio,
         /* has_inp_video           */ impl->chat_params.allow_video,
+        /* has_cap_chat            */ impl->has_cap_chat(),
+        /* has_cap_tts             */ impl->has_cap_tts(),
+        /* has_audio_stream        */ impl->mctx != nullptr && mtmd_support_audio_stream(impl->mctx),
         /* json_ui_settings        */ impl->json_ui_settings,
         /* slot_n_ctx              */ impl->n_ctx_slot(),
         /* pooling_type            */ llama_pooling_type(impl->ctx_tgt),
@@ -4899,6 +5202,11 @@ std::unique_ptr<server_res_generator> server_routes::handle_completions_impl(
 
     res->set_req(&req); // will also set spipe if needed
 
+    if (!ctx_server.has_cap_chat()) {
+        res->error(format_error_response("this server does not support chat/completions", ERROR_TYPE_NOT_SUPPORTED));
+        return res;
+    }
+
     int32_t sse_ping_interval = params.sse_ping_interval;
 
     try {
@@ -4992,10 +5300,20 @@ std::unique_ptr<server_res_generator> server_routes::handle_completions_impl(
                 res->ok(arr[0]);
             } else if (res_type == TASK_RESPONSE_TYPE_OAI_CHAT || res_type == TASK_RESPONSE_TYPE_OAI_CMPL) {
                 // if multiple results in OAI format, we need to re-format them
+                json & usage   = arr[0]["usage"];
                 json & choices = arr[0]["choices"];
                 for (size_t i = 1; i < arr.size(); i++) {
                     choices.push_back(std::move(arr[i]["choices"][0]));
                 }
+
+                // OAI counts generated tokens across all choices
+                int64_t n_completion_tokens = 0;
+                for (auto & item : arr) {
+                    n_completion_tokens += item["usage"]["completion_tokens"].get<int64_t>();
+                }
+                usage["completion_tokens"] = n_completion_tokens;
+                usage["total_tokens"]      = usage["prompt_tokens"].get<int64_t>() + n_completion_tokens;
+
                 res->ok(arr[0]);
             } else {
                 // multi-results, non-OAI compat
@@ -5605,7 +5923,7 @@ void server_routes::init_routes() {
             server_task task(SERVER_TASK_TYPE_CONTROL);
             task.id              = rd.get_new_id();
             task.params.control_cmpl_id = cmpl_id;
-            task.params.control_action  = action;
+            task.params.control_action  = SERVER_CONTROL_ACTION_REASONING_END;
             rd.post_task(std::move(task));
         }
 
@@ -5680,6 +5998,200 @@ void server_routes::init_routes() {
             session);
     };
 
+    // realtime transcription over websocket, modeled after the OpenAI realtime API
+    // audio is PCM16 mono at the model sample rate, sent as base64 in input_audio_buffer.append events
+    // input_audio_buffer.commit with "final": true ends the input, closing the socket also ends it
+    this->ws_realtime = [this](const server_http_req &, server_http_context::ws_conn & conn) {
+        auto send_event = [&conn](json ev) {
+            ev["event_id"] = "event_" + random_string();
+            conn.send(safe_json_to_str(ev));
+        };
+        auto send_error_event = [&send_event](const std::string & message, const std::string & type) {
+            send_event(json {
+                {"type", "error"},
+                {"error", {
+                    {"type",    type},
+                    {"code",    nullptr},
+                    {"message", message},
+                    {"param",   nullptr},
+                }},
+            });
+        };
+
+        if (!meta->has_audio_stream) {
+            send_error_event("The current model does not support realtime transcription.", "invalid_request_error");
+            conn.close();
+            return;
+        }
+
+        const std::string session_id = "sess_" + random_string();
+        const json session_config = json {
+            {"id",     session_id},
+            {"object", "realtime.transcription_session"},
+            {"type",   "transcription"},
+            {"audio",  {{"input", {
+                {"format",          {{"type", "audio/pcm"}, {"rate", mtmd_get_audio_sample_rate(ctx_server.mctx)}}},
+                {"transcription",   {{"model", meta->model_name}}},
+                {"turn_detection",  nullptr},
+                {"noise_reduction", nullptr},
+            }}}},
+        };
+
+        auto res = create_response();
+        auto & rd = res->rd;
+        {
+            server_task task(SERVER_TASK_TYPE_TRANSCRIBE_RT);
+            task.id = rd.get_new_id();
+            task.params.sampling          = params.sampling;
+            task.params.stream            = true;
+            task.params.oaicompat_cmpl_id = session_id;
+            task.params.oaicompat_model   = meta->model_name;
+            rd.post_task(std::move(task));
+        }
+
+        // the slot answers once its audio stream is live, the session starts there
+        {
+            auto result = rd.next([&conn]() { return !conn.is_open(); });
+            if (!result || result->is_error()) {
+                if (result) {
+                    send_error_event(json_value(result->to_json(), "message", std::string("server error")), "server_error");
+                }
+                conn.close();
+                return;
+            }
+        }
+        send_event(json {{"type", "session.created"}, {"session", session_config}});
+
+        // one item per committed audio buffer, deltas are attributed to the current item
+        std::mutex  mutex_item;
+        std::string item_id = "item_" + random_string();
+        std::string item_prev; // the committed item before item_id, empty for the first one
+        std::string item_text;
+
+        // called with mutex_item held
+        auto send_completed = [&]() {
+            send_event(json {
+                {"type",          "conversation.item.input_audio_transcription.completed"},
+                {"item_id",       item_id},
+                {"content_index", 0},
+                {"transcript",    item_text},
+            });
+            item_text.clear();
+        };
+
+        auto post_control = [&](server_control_action action, std::vector<float> && audio) {
+            server_response_reader ctl(queue_tasks, queue_results, HTTP_POLLING_SECONDS);
+            server_task task(SERVER_TASK_TYPE_CONTROL);
+            task.id                     = ctl.get_new_id();
+            task.params.control_action  = action;
+            task.params.control_cmpl_id = session_id;
+            task.params.control_audio   = std::move(audio);
+            ctl.post_task(std::move(task));
+            auto result = ctl.next([&conn]() { return !conn.is_open(); });
+            auto * control = result ? dynamic_cast<server_task_result_control *>(result.get()) : nullptr;
+            return control && control->success;
+        };
+
+        // client events are read on this thread, the transcript is sent from the thread below
+        std::atomic<bool> input_ended{false};
+        std::thread reader([&]() {
+            std::string msg;
+            while (conn.read(msg) != 0) {
+                json ev;
+                try {
+                    ev = json::parse(msg);
+                } catch (const std::exception &) {
+                    send_error_event("invalid JSON", "invalid_request_error");
+                    continue;
+                }
+                const std::string type = json_value(ev, "type", std::string());
+                if (type == "session.update" || type == "transcription_session.update") {
+                    send_event(json {{"type", "session.updated"}, {"session", session_config}});
+                } else if (type == "input_audio_buffer.append") {
+                    std::string pcm;
+                    try {
+                        pcm = base64::decode(json_value(ev, "audio", std::string()));
+                    } catch (const std::exception &) {
+                        send_error_event("invalid base64 audio", "invalid_request_error");
+                        continue;
+                    }
+                    std::vector<float> samples(pcm.size() / 2);
+                    for (size_t i = 0; i < samples.size(); i++) {
+                        int16_t v;
+                        memcpy(&v, pcm.data() + 2 * i, sizeof(v));
+                        samples[i] = v / 32768.0f;
+                    }
+                    if (!post_control(SERVER_CONTROL_ACTION_AUDIO_APPEND, std::move(samples))) {
+                        break;
+                    }
+                } else if (type == "input_audio_buffer.commit") {
+                    // "final": true ends the input, the last item is completed when the stream drains
+                    if (json_value(ev, "final", false)) {
+                        input_ended = true;
+                        post_control(SERVER_CONTROL_ACTION_AUDIO_END, {});
+                        continue;
+                    }
+                    if (!post_control(SERVER_CONTROL_ACTION_AUDIO_COMMIT, {})) {
+                        break;
+                    }
+                    // completed is sent once the rows of the committed audio are decoded (audio_commit_drained below)
+                    std::lock_guard<std::mutex> lock(mutex_item);
+                    send_event(json {
+                        {"type",             "input_audio_buffer.committed"},
+                        {"previous_item_id", item_prev.empty() ? json(nullptr) : json(item_prev)},
+                        {"item_id",          item_id},
+                    });
+                } else if (type == "input_audio_buffer.clear") {
+                    send_event(json {{"type", "input_audio_buffer.cleared"}});
+                } else {
+                    send_error_event("unknown event type: " + type, "invalid_request_error");
+                }
+            }
+            if (!input_ended.exchange(true)) {
+                post_control(SERVER_CONTROL_ACTION_AUDIO_END, {});
+            }
+            // the result loop waits on the socket, nobody reads it from here on
+            conn.close();
+        });
+
+        while (true) {
+            auto result = rd.next([&conn]() { return !conn.is_open(); });
+            if (!result) {
+                break; // connection closed
+            }
+            if (result->is_error()) {
+                send_error_event(json_value(result->to_json(), "message", std::string("server error")), "server_error");
+                break;
+            }
+            if (auto * partial = dynamic_cast<server_task_result_cmpl_partial *>(result.get())) {
+                if (partial->audio_commit_drained) {
+                    // complete the committed item and open the next one
+                    std::lock_guard<std::mutex> lock(mutex_item);
+                    send_completed();
+                    item_prev = item_id;
+                    item_id   = "item_" + random_string();
+                } else if (!partial->content.text.empty()) {
+                    std::lock_guard<std::mutex> lock(mutex_item);
+                    item_text += partial->content.text;
+                    send_event(json {
+                        {"type",          "conversation.item.input_audio_transcription.delta"},
+                        {"item_id",       item_id},
+                        {"content_index", 0},
+                        {"delta",         partial->content.text},
+                    });
+                }
+            } else if (result->is_stop()) {
+                std::lock_guard<std::mutex> lock(mutex_item);
+                send_completed();
+                break;
+            }
+        }
+
+        input_ended = true;
+        conn.close();
+        reader.join();
+    };
+
     this->post_anthropic_messages = [this](const server_http_req & req) {
         auto res = create_response();
         std::vector<raw_buffer> files;
@@ -5798,82 +6310,171 @@ void server_routes::init_routes() {
     };
 
     this->post_rerank = [this](const server_http_req & req) {
+        return handle_rerank_impl(req);
+    };
+
+    this->post_tts = [this](const server_http_req & req) {
         auto res = create_response();
-        if (!params.embedding || params.pooling_type != LLAMA_POOLING_TYPE_RANK) {
-            res->error(format_error_response("This server does not support reranking. Start it with `--reranking`", ERROR_TYPE_NOT_SUPPORTED));
+        res->set_req(&req); // will also set spipe if needed
+
+        if (!ctx_server.has_cap_tts()) {
+            res->error(format_error_response("this server does not support audio generation", ERROR_TYPE_NOT_SUPPORTED));
             return res;
         }
 
-        const json body = json::parse(req.body);
+        const auto info = mtmd_gen_audio_get_info(ctx_server.mctx);
 
-        // if true, use TEI API format, otherwise use Jina API format
-        // Jina: https://jina.ai/reranker/
-        // TEI: https://huggingface.github.io/text-embeddings-inference/#/Text%20Embeddings%20Inference/rerank
-        bool is_tei_format = body.contains("texts");
+        json body = json::parse(req.body);
 
-        json query;
-        if (body.count("query") == 1) {
-            query = body.at("query");
-            if (!query.is_string()) {
-                res->error(format_error_response("\"query\" must be a string", ERROR_TYPE_INVALID_REQUEST));
+        // multipart form fields arrive as strings, correct the types of the numeric and boolean params
+        for (const char * k : { "top_k", "n_predict", "max_tokens", "seed" }) {
+            if (body.contains(k) && body[k].is_string()) {
+                body[k] = std::stoll(body[k].get<std::string>());
+            }
+        }
+        for (const char * k : { "top_p", "repeat_penalty" }) {
+            if (body.contains(k) && body[k].is_string()) {
+                body[k] = std::stof(body[k].get<std::string>());
+            }
+        }
+        if (body.contains("stream") && body["stream"].is_string()) {
+            body["stream"] = body["stream"] == "true";
+        }
+
+        std::string prompt = json_value(body, "input", json_value(body, "prompt", std::string()));
+        if (prompt.empty()) {
+            res->error(format_error_response("\"input\" must be a non-empty string", ERROR_TYPE_INVALID_REQUEST));
+            return res;
+        }
+
+        const std::string response_format = json_value(body, "response_format", std::string("wav"));
+
+        server_task task(SERVER_TASK_TYPE_TTS);
+        server_schema::eval_tts_schema(params, task, body);
+        const bool stream = task.params.stream;
+        task.tts_inp.set_prompt(prompt);
+        task.tts_inp.set_lang(json_value(body, "lang", std::string()));
+        task.tts_inp.data.stream    = stream;
+        task.tts_inp.data.out_type  = response_format == "pcm"
+            ? MTMD_HELPER_GEN_AUDIO_OUTTYPE_PCM
+            : MTMD_HELPER_GEN_AUDIO_OUTTYPE_WAV;
+        // note: -1 is clamped to 0 by the sampler, it will disable the penalty
+        task.params.sampling.penalty_last_n = task.params.n_predict > 0 ? task.params.n_predict : 512;
+        task.params.sampling.seed = task.tts_inp.data.seed; // same seed for the codec/vocoder RNG
+        if (task.tts_inp.data.top_k > 0) {
+            task.params.sampling.top_k = task.tts_inp.data.top_k;
+        }
+        if (task.tts_inp.data.top_p > 0) {
+            task.params.sampling.top_p = task.tts_inp.data.top_p;
+        }
+
+        // speaker reference: either an uploaded form file ("speaker_ref") or a base64 JSON field ("speaker_ref_b64")
+        const unsigned char * speaker_ref_data = nullptr;
+        size_t speaker_ref_len  = 0;
+        std::string speaker_ref_b64_decoded;
+
+        auto speaker_ref_file = req.files.find("speaker_ref");
+        if (speaker_ref_file != req.files.end()) {
+            speaker_ref_data = speaker_ref_file->second.data.data();
+            speaker_ref_len  = speaker_ref_file->second.data.size();
+        } else {
+            std::string speaker_ref_b64 = json_value(body, "speaker_ref_b64", std::string());
+            if (!speaker_ref_b64.empty()) {
+                try {
+                    speaker_ref_b64_decoded = base64::decode(speaker_ref_b64);
+                } catch (const std::exception &) {
+                    res->error(format_error_response("\"speaker_ref_b64\" is not valid base64", ERROR_TYPE_INVALID_REQUEST));
+                    return res;
+                }
+                speaker_ref_data = (const unsigned char *) speaker_ref_b64_decoded.data();
+                speaker_ref_len  = speaker_ref_b64_decoded.size();
+            }
+        }
+
+        if (speaker_ref_len > 0) {
+            auto wrapper = mtmd_helper_bitmap_init_from_buf(ctx_server.mctx, speaker_ref_data, speaker_ref_len, false, ctx_server.init_opt);
+            if (!wrapper.bitmap) {
+                res->error(format_error_response("failed to decode \"speaker_ref\"", ERROR_TYPE_INVALID_REQUEST));
                 return res;
             }
+            task.tts_inp.set_speaker_ref(mtmd::bitmap_ptr(wrapper.bitmap));
         } else {
-            res->error(format_error_response("\"query\" must be provided", ERROR_TYPE_INVALID_REQUEST));
-            return res;
+            SRV_WRN("%s", "no speaker reference provided, the model may behave randomly\n");
         }
 
-        std::vector<std::string> documents = json_value(body, "documents",
-                                             json_value(body, "texts", std::vector<std::string>()));
-        if (documents.empty()) {
-            res->error(format_error_response("\"documents\" must be a non-empty string array", ERROR_TYPE_INVALID_REQUEST));
-            return res;
-        }
-
-        int top_n = json_value(body, "top_n", (int)documents.size());
-
-        // create and queue the task
-        json responses = json::array();
         auto & rd = res->rd;
-        {
-            std::vector<server_task> tasks;
-            tasks.reserve(documents.size());
-            for (size_t i = 0; i < documents.size(); i++) {
-                auto tmp = format_prompt_rerank(ctx_server.model_tgt, ctx_server.vocab, ctx_server.mctx, query, documents[i], ctx_server.init_opt);
-                server_task task = server_task(SERVER_TASK_TYPE_RERANK);
-                task.id     = rd.get_new_id();
-                task.tokens = std::move(tmp);
-                tasks.push_back(std::move(task));
+        task.id = rd.get_new_id();
+        rd.post_task(std::move(task));
+
+        // raw float32 LE mono samples; audio/L16 would imply 16-bit big-endian (RFC 2586)
+        const std::string content_type = response_format == "pcm"
+            ? "audio/pcm;rate=" + std::to_string(info.sample_rate) + ";encoding=float;bits=32"
+            : "audio/wav";
+
+        if (!stream) {
+            auto result = rd.next(req.should_stop);
+            if (!result) {
+                GGML_ASSERT(req.should_stop());
+                return res; // connection is closed
             }
-            rd.post_tasks(std::move(tasks));
-        }
-
-        // wait for the results
-        auto all_results = rd.wait_for_all(req.should_stop);
-
-        // collect results
-        if (all_results.is_terminated) {
-            return res; // connection is closed
-        } else if (all_results.error) {
-            res->error(all_results.error->to_json());
+            if (result->is_error()) {
+                res->error(result->to_json());
+                return res;
+            }
+            auto * tts_res = dynamic_cast<server_task_result_tts *>(result.get());
+            GGML_ASSERT(tts_res != nullptr);
+            res->status       = 200;
+            res->content_type = content_type;
+            res->data         = std::move(tts_res->audio);
             return res;
         } else {
-            for (auto & res : all_results.results) {
-                GGML_ASSERT(dynamic_cast<server_task_result_rerank*>(res.get()) != nullptr);
-                responses.push_back(res->to_json());
+            auto first_result = rd.next(req.should_stop);
+            if (!first_result) {
+                GGML_ASSERT(req.should_stop());
+                return res; // connection is closed
             }
+            if (first_result->is_error()) {
+                res->error(first_result->to_json());
+                return res;
+            }
+            auto * first_tts_res = dynamic_cast<server_task_result_tts *>(first_result.get());
+            GGML_ASSERT(first_tts_res != nullptr);
+
+            res->status       = 200;
+            res->content_type = content_type;
+            res->data          = std::move(first_tts_res->audio);
+            bool is_done       = first_tts_res->final;
+
+            res->set_next([res_this = res.get(), is_done](std::string & output) mutable -> bool {
+                // flush buffered audio before is_done - the first result can already be final
+                if (!res_this->data.empty()) {
+                    output = std::move(res_this->data);
+                    res_this->data.clear();
+                    return true;
+                }
+                if (is_done) {
+                    return false;
+                }
+                if (res_this->should_stop()) {
+                    return false;
+                }
+
+                server_response_reader & rd = res_this->rd;
+                if (!rd.has_next()) {
+                    return false;
+                }
+                auto result = rd.next([&res_this]() { return res_this->should_stop(); });
+                if (!result || result->is_error()) {
+                    return false;
+                }
+                auto * tts_res = dynamic_cast<server_task_result_tts *>(result.get());
+                GGML_ASSERT(tts_res != nullptr);
+                output  = std::move(tts_res->audio);
+                is_done = tts_res->final;
+                return true;
+            });
         }
 
-        // write JSON response
-        json root = format_response_rerank(
-            body,
-            meta->model_name,
-            responses,
-            is_tei_format,
-            documents,
-            top_n);
-
-        res->ok(root);
         return res;
     };
 
@@ -5889,7 +6490,7 @@ void server_routes::init_routes() {
         const auto questions = decision.parse_questions(body);
 
         std::vector<raw_buffer> files;
-        const json state = decision.parse_state(body, files);
+        const json state = decision.prepare_state(decision.parse_state(body, files));
         if (!files.empty() && (!decision.can_use_images() || !meta->has_inp_image)) {
             res->error(format_error_response("This server does not support image input for decisions. For a model that supports it, start it with `--mmproj`", ERROR_TYPE_NOT_SUPPORTED));
             return res;
@@ -6171,6 +6772,7 @@ std::unique_ptr<server_res_generator> server_routes::handle_embeddings_impl(cons
         return tokenize_input_subprompt(ctx_server.vocab, ctx_server.mctx, p, true, true, ctx_server.init_opt);
     };
 
+    // dispatch to the appropriate tokenizer based on the shape of the input
     std::vector<server_tokens> tokenized_prompts;
     if (prompt.is_array() && !json_is_array_and_contains_numbers(prompt)) {
         for (const auto & p : prompt) {
@@ -6244,6 +6846,154 @@ std::unique_ptr<server_res_generator> server_routes::handle_embeddings_impl(cons
     return res;
 }
 
+std::unique_ptr<server_res_generator> server_routes::handle_rerank_impl(const server_http_req & req) {
+    auto res = create_response();
+    if (!params.embedding || params.pooling_type != LLAMA_POOLING_TYPE_RANK) {
+        res->error(format_error_response("This server does not support reranking. Start it with `--reranking`", ERROR_TYPE_NOT_SUPPORTED));
+        return res;
+    }
+
+    const json body = json::parse(req.body);
+
+    // if true, use TEI API format, otherwise use Jina API format
+    // Jina: https://jina.ai/reranker/
+    // TEI: https://huggingface.github.io/text-embeddings-inference/#/Text%20Embeddings%20Inference/rerank
+    bool is_tei_format = body.contains("texts");
+
+    // expand one rerank input item: plain string or {"text": str|[str], "image": url|data-uri|raw-base64|[urls]}
+    auto parse_item = [&](const json & item, std::string & out_text, std::vector<raw_buffer> & out_files) {
+        if (item.is_string()) {
+            out_text = item.get<std::string>();
+            return;
+        }
+        if (!item.is_object()) {
+            throw std::invalid_argument("rerank input must be a string or an object of the form {\"text\": ..., \"image\": ...}");
+        }
+        if (item.contains("video") || item.contains("fps") || item.contains("max_frames")) {
+            throw std::invalid_argument("video/fps/max_frames are not supported for rerank input");
+        }
+        json text = item.value("text", json());
+        if (text.is_string()) {
+            out_text += text.get<std::string>();
+        } else if (text.is_array()) {
+            for (const auto & t : text) {
+                if (!t.is_string()) {
+                    throw std::invalid_argument("\"text\" array elements must be strings");
+                }
+                out_text += t.get<std::string>();
+            }
+        } else if (!text.is_null()) {
+            throw std::invalid_argument("\"text\" must be a string or an array of strings");
+        }
+        json image = item.value("image", json());
+        auto add_image = [&](const std::string & url) {
+            // marker is appended by format_prompt_rerank, one per decoded file
+            try {
+                handle_media(out_files, url, params.media_path);
+            } catch (const std::runtime_error & e) {
+                throw std::invalid_argument(e.what());
+            }
+        };
+        if (image.is_string()) {
+            add_image(image.get<std::string>());
+        } else if (image.is_array()) {
+            for (const auto & u : image) {
+                if (!u.is_string()) {
+                    throw std::invalid_argument("\"image\" array elements must be strings");
+                }
+                add_image(u.get<std::string>());
+            }
+        } else if (!image.is_null()) {
+            throw std::invalid_argument("\"image\" must be a string or an array of strings");
+        }
+    };
+
+    // Parse query
+    std::string query_str;
+    std::vector<raw_buffer> query_files;
+    if (body.count("query") == 1) {
+        try {
+            parse_item(body.at("query"), query_str, query_files);
+        } catch (const std::invalid_argument & e) {
+            res->error(format_error_response(e.what(), ERROR_TYPE_INVALID_REQUEST));
+            return res;
+        }
+    } else {
+        res->error(format_error_response("\"query\" must be provided", ERROR_TYPE_INVALID_REQUEST));
+        return res;
+    }
+
+    // Resolve Jina/TEI format ambiguity
+    json documents_json = json_value(body, "documents",
+        json_value(body, "texts", json::array()));
+    if (!documents_json.is_array() || documents_json.empty()) {
+        res->error(format_error_response("\"documents\" must be a non-empty array of strings or objects", ERROR_TYPE_INVALID_REQUEST));
+        return res;
+    }
+
+    // Parse documents
+    std::vector<std::string>          documents(documents_json.size());
+    std::vector<std::vector<raw_buffer>> document_files(documents_json.size());
+    for (size_t i = 0; i < documents_json.size(); i++) {
+        try {
+            parse_item(documents_json[i], documents[i], document_files[i]);
+        } catch (const std::invalid_argument & e) {
+            res->error(format_error_response(e.what(), ERROR_TYPE_INVALID_REQUEST));
+            return res;
+        }
+    }
+
+    int top_n = json_value(body, "top_n", (int)documents.size());
+    if (top_n < 0) {
+        res->error(format_error_response("\"top_n\" must be >= 0", ERROR_TYPE_INVALID_REQUEST));
+        return res;
+    }
+
+    // create and queue the task
+    json responses = json::array();
+    auto & rd = res->rd;
+    {
+        std::vector<server_task> tasks;
+        tasks.reserve(documents.size());
+        for (size_t i = 0; i < documents.size(); i++) {
+            auto tmp = format_prompt_rerank(ctx_server.model_tgt, ctx_server.vocab, ctx_server.mctx, query_str, documents[i], query_files, document_files[i], ctx_server.init_opt);
+            server_task task = server_task(SERVER_TASK_TYPE_RERANK);
+            task.id     = rd.get_new_id();
+            task.tokens = std::move(tmp);
+            tasks.push_back(std::move(task));
+        }
+        rd.post_tasks(std::move(tasks));
+    }
+
+    // wait for the results
+    auto all_results = rd.wait_for_all(req.should_stop);
+
+    // collect results
+    if (all_results.is_terminated) {
+        return res; // connection is closed
+    } else if (all_results.error) {
+        res->error(all_results.error->to_json());
+        return res;
+    } else {
+        for (auto & res : all_results.results) {
+            GGML_ASSERT(dynamic_cast<server_task_result_rerank*>(res.get()) != nullptr);
+            responses.push_back(res->to_json());
+        }
+    }
+
+    // write JSON response
+    json root = format_response_rerank(
+        body,
+        meta->model_name,
+        responses,
+        is_tei_format,
+        documents,
+        top_n);
+
+    res->ok(root);
+    return res;
+}
+
 std::unique_ptr<server_res_generator> server_routes::handle_count_tokens(const server_http_req & req, task_response_type res_type) {
     auto res = create_response();
     std::vector<raw_buffer> files;
