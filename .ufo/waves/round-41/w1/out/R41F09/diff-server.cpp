diff --git a/tools/server/server.cpp b/tools/server/server.cpp
index b16824107..b6ebf7523 100644
--- a/tools/server/server.cpp
+++ b/tools/server/server.cpp
@@ -37,12 +37,17 @@ static inline void signal_handler(int signal) {
     shutdown_handler(signal);
 }
 
+// how the server is run; everything is on when it is the llama-server binary
+struct server_run_opts {
+    bool install_signal_handlers = true; // off when embedded in llama-cli, which handles them itself
+    bool resolve_model           = true; // download / resolve -hf and docker models; off when the caller did it already
+};
+
 // satisfies -Wmissing-declarations (used by llama command)
 int llama_server(int argc, char ** argv);
 
 // to be used via CLI (argc / argv are used by router mode only)
 int llama_server(common_params & params, int argc, char ** argv);
-int llama_server(common_params & params, int argc, char ** argv, server_child & child);
 void llama_server_terminate();
 void llama_server_terminate() {
     if (shutdown_handler) {
@@ -91,72 +96,24 @@ static server_http_context::handler_t ex_wrapper(server_http_context::handler_t
     };
 }
 
-int llama_server(int argc, char ** argv) {
-    server_child child;
+//
+// shared by every role
+//
 
-    std::setlocale(LC_NUMERIC, "C");
-
-#ifndef _WIN32
-    // Ignore SIGPIPE so the server does not crash if a child (MCP server, tools runtime) exits while we are writing to its stdin
-    signal(SIGPIPE, SIG_IGN);
-#endif
-
-    // own arguments required by this example
-    common_params params;
-
-    common_init();
-
-    // start the stream session manager GC right after common init, before any HTTP route can
-    // touch it. lifecycle is symmetric, stop_gc() runs in clean_up() before backend free
-    server_stream_session_manager_start();
-
-    if (!common_params_parse(argc, argv, params, LLAMA_EXAMPLE_SERVER)) {
-        return 1;
+static server_role_type server_role_detect(const common_params & params, server_role & role) {
+    if (role.is_managed_by_router()) {
+        return role.get_role();
     }
-
-    SRV_INF("%s", "initializing ...\n");
-
-    llama_backend_init();
-    llama_numa_init(params.numa);
-
-    const int result = llama_server(params, argc, argv, child);
-    common_log_flush(common_log_main());
-    return result;
+    // a server given no model is a router
+    const bool has_model = !params.model.path.empty()
+                        || !params.model.hf_repo.empty()
+                        || !params.model.docker_repo.empty();
+    return has_model ? SERVER_ROLE_INSTANCE : SERVER_ROLE_ROUTER;
 }
 
-int llama_server(common_params & params, int argc, char ** argv) {
-    server_child child;
-    return llama_server(params, argc, argv, child);
-}
-
-int llama_server(common_params & params, int argc, char ** argv, server_child & child) {
-    bool is_run_by_cli = (argv == nullptr);
-
-    common_models_handler models_handler;
-
-    // note: router mode also accepts -hf remote-preset, so we need to check that first
-    if (!is_run_by_cli && !params.model.hf_repo.empty()) {
-        try {
-            models_handler = common_models_handler_init(params, LLAMA_EXAMPLE_SERVER);
-            if (common_models_handler_is_preset_repo(models_handler)) {
-                // apply the preset and start the server in router mode
-                common_models_handler_apply(models_handler, params);
-            }
-        } catch (const std::exception & e) {
-            SRV_ERR("failed to fetch model metadata: %s\n", e.what());
-            return 1;
-        }
-    }
-
-    // router server never loads a model and must not touch the GPU
-    const bool is_router_server = params.model.path.empty()
-                               && params.model.hf_repo.empty()
-                               && params.model.docker_repo.empty();
-
-    // skip device enumeration so the CUDA primary context stays uncreated
-    common_params_print_info(params, !is_router_server);
-
-    if (!is_router_server) {
+// adjust the params for the role; returns false on a configuration error
+static bool server_prepare_params(common_params & params, server_role_type role_type) {
+    if (role_type != SERVER_ROLE_ROUTER) {
         // validate batch size for embeddings
         // embeddings require all tokens to be processed in a single ubatch
         // see https://github.com/ggml-org/llama.cpp/issues/12836
@@ -197,7 +154,7 @@ int llama_server(common_params & params, int argc, char ** argv, server_child &
         const std::string reason = server_connect::unavailable_reason(params);
         if (!reason.empty()) {
             SRV_ERR("--connect is not available: %s\n", reason.c_str());
-            return 1;
+            return false;
         }
         params.server_connect_code = server_connect::resolve_code(params.server_connect_code);
     } else if (!params.server_connect_code.empty()) {
@@ -206,75 +163,11 @@ int llama_server(common_params & params, int argc, char ** argv, server_child &
         params.server_connect_code.clear();
     }
 
-    // note: this is guaranteed to out-live ctx_http and tools
-    server_mcp mcp_mgr;
-
-    // struct that contains llama context and inference
-    server_context ctx_server;
-
-    //
-    // Router
-    //
-
-    // register API routes
-    server_routes routes(params, ctx_server);
-    server_tools tools;
-
-    std::optional<server_models_routes> models_routes{};
-
-    server_http_context ctx_http;
-    if (!ctx_http.init(params)) {
-        SRV_ERR("%s", "failed to initialize HTTP server\n");
-        return 1;
-    }
-
-    if (is_router_server) {
-        // setup server instances manager
-        try {
-            models_routes.emplace(params, argc, argv);
-        } catch (const std::exception & e) {
-            SRV_ERR("failed to initialize router models: %s\n", e.what());
-            return 1;
-        }
-
-        // proxy handlers
-        // note: routes.get_health stays the same
-        routes.get_metrics                 = models_routes->proxy_get;
-        routes.post_props                  = models_routes->proxy_post;
-        routes.post_completions            = models_routes->proxy_post;
-        routes.post_completions_oai        = models_routes->proxy_post;
-        routes.post_chat_completions       = models_routes->proxy_post;
-        routes.post_control                = models_routes->proxy_post;
-        routes.post_responses_oai          = models_routes->proxy_post;
-        routes.post_transcriptions_oai     = models_routes->proxy_post;
-        routes.post_anthropic_messages     = models_routes->proxy_post;
-        routes.post_anthropic_count_tokens = models_routes->proxy_post;
-        routes.post_infill                 = models_routes->proxy_post;
-        routes.post_embeddings             = models_routes->proxy_post;
-        routes.post_embeddings_oai         = models_routes->proxy_post;
-        routes.post_rerank                 = models_routes->proxy_post;
-        routes.post_systemone              = models_routes->proxy_post;
-        routes.post_tokenize               = models_routes->proxy_post;
-        routes.post_detokenize             = models_routes->proxy_post;
-        routes.post_apply_template         = models_routes->proxy_post;
-        routes.post_chat_completions_tok   = models_routes->proxy_post;
-        routes.post_responses_tok_oai      = models_routes->proxy_post;
-        routes.get_lora_adapters           = models_routes->proxy_get;
-        routes.post_lora_adapters          = models_routes->proxy_post;
-        routes.get_slots                   = models_routes->proxy_get;
-        routes.post_slots                  = models_routes->proxy_post;
-
-        // custom routes for router
-        routes.get_props                   = models_routes->get_router_props;
-        routes.get_models                  = models_routes->get_router_models;
-
-        ctx_http.post("/models",               ex_wrapper(models_routes->post_router_models));
-        ctx_http.post("/models/load",          ex_wrapper(models_routes->post_router_models_load));
-        ctx_http.post("/models/unload",        ex_wrapper(models_routes->post_router_models_unload));
-        ctx_http.get ("/models/sse",           ex_wrapper(models_routes->get_router_models_sse));
-        ctx_http.del ("/models",               ex_wrapper(models_routes->del_router_models));
-    }
+    return true;
+}
 
+// the API of every server; a router points the handlers in routes at its proxies before calling this
+static void server_register_routes(server_http_context & ctx_http, server_routes & routes) {
     ctx_http.get ("/health",                   ex_wrapper(routes.get_health)); // public endpoint (no API key check)
     ctx_http.get ("/v1/health",                ex_wrapper(routes.get_health)); // public endpoint (no API key check)
     ctx_http.get ("/metrics",                  ex_wrapper(routes.get_metrics));
@@ -292,6 +185,8 @@ int llama_server(common_params & params, int argc, char ** argv, server_child &
     ctx_http.post("/responses",                ex_wrapper(routes.post_responses_oai));
     ctx_http.post("/v1/audio/transcriptions",  ex_wrapper(routes.post_transcriptions_oai));
     ctx_http.post("/audio/transcriptions",     ex_wrapper(routes.post_transcriptions_oai));
+    ctx_http.post("/tts",                      ex_wrapper(routes.post_tts));
+    ctx_http.ws  ("/v1/realtime",              routes.ws_realtime);
     ctx_http.post("/v1/messages",              ex_wrapper(routes.post_anthropic_messages)); // anthropic messages API
     ctx_http.post("/infill",                   ex_wrapper(routes.post_infill));
     ctx_http.post("/embedding",                ex_wrapper(routes.post_embeddings)); // legacy
@@ -318,27 +213,30 @@ int llama_server(common_params & params, int argc, char ** argv, server_child &
     ctx_http.get ("/slots",                    ex_wrapper(routes.get_slots));
     ctx_http.post("/slots/:id_slot",           ex_wrapper(routes.post_slots));
 
-    // resumable streaming: a child binds the local session factories, the router binds
-    // proxies that resolve the owning child, see server-stream.h
-    server_http_context::handler_t stream_get_h;
-    server_http_context::handler_t streams_lookup_h;
-    server_http_context::handler_t stream_delete_h;
-    if (is_router_server) {
-        stream_get_h     = models_routes->router_stream_get;
-        streams_lookup_h = models_routes->router_streams_lookup;
-        stream_delete_h  = models_routes->router_stream_delete;
-    } else {
-        stream_get_h     = server_stream_make_get_handler();
-        streams_lookup_h = server_stream_make_lookup_handler();
-        stream_delete_h  = server_stream_make_delete_handler();
-    }
-    ctx_http.get ("/v1/stream",                ex_wrapper(stream_get_h));
-    ctx_http.post("/v1/streams/lookup",        ex_wrapper(streams_lookup_h));
-    ctx_http.del ("/v1/stream",                ex_wrapper(stream_delete_h));
-
     // Google Cloud Platform (Vertex AI) compat
     ctx_http.register_gcp_compat();
+}
 
+// resumable streaming, see server-stream.h: an instance binds the local session factories,
+// a router binds proxies that resolve the owning child
+static void server_register_stream_routes(
+        server_http_context & ctx_http,
+        const server_http_context::handler_t & stream_get,
+        const server_http_context::handler_t & streams_lookup,
+        const server_http_context::handler_t & stream_delete) {
+    ctx_http.get ("/v1/stream",                ex_wrapper(stream_get));
+    ctx_http.post("/v1/streams/lookup",        ex_wrapper(streams_lookup));
+    ctx_http.del ("/v1/stream",                ex_wrapper(stream_delete));
+}
+
+// the features behind a flag, and the warning about the ones that must not face untrusted clients
+// returns false when one of them fails to start
+static bool server_setup_features(
+        server_http_context & ctx_http,
+        const common_params & params,
+        server_mcp & mcp_mgr,
+        server_tools & tools,
+        server_role_type role_type) {
     // return 403 for disabled features
     server_http_context::handler_t res_403 = [](const server_http_req &) {
         auto res = std::make_unique<server_http_res>();
@@ -356,9 +254,8 @@ int llama_server(common_params & params, int argc, char ** argv, server_child &
         SRV_WRN("%s", "security: no API key is set and CORS allows all origins (see https://github.com/ggml-org/llama.cpp/pull/25655)\n");
     }
 
-    // CORS proxy (EXPERIMENTAL, only used by the Web UI for MCP)
     std::vector<std::string> warn_names;
-    if (is_router_server) {
+    if (role_type == SERVER_ROLE_ROUTER) {
         warn_names.push_back("router mode");
     }
 
@@ -366,6 +263,7 @@ int llama_server(common_params & params, int argc, char ** argv, server_child &
         warn_names.push_back("peer-to-peer tunnel (llama-connect, experimental)");
     }
 
+    // CORS proxy (EXPERIMENTAL, only used by the Web UI for MCP)
     if (params.ui_mcp_proxy) {
         ctx_http.get ("/cors-proxy",      ex_wrapper(proxy_handler_get));
         ctx_http.post("/cors-proxy",      ex_wrapper(proxy_handler_post));
@@ -379,7 +277,7 @@ int llama_server(common_params & params, int argc, char ** argv, server_child &
         mcp_mgr.start(params);
     } catch (const std::exception & e) {
         SRV_ERR("MCP starting failed: %s\n", e.what());
-        return 1;
+        return false;
     }
 
     if (!params.server_tools.empty() || !mcp_mgr.empty()) {
@@ -387,7 +285,7 @@ int llama_server(common_params & params, int argc, char ** argv, server_child &
             tools.setup(params.server_tools, mcp_mgr, params.server_tools_runtime);
         } catch (const std::exception & e) {
             SRV_ERR("tools setup failed: %s\n", e.what());
-            return 1;
+            return false;
         }
         ctx_http.get ("/tools",           ex_wrapper(tools.handle_get));
         ctx_http.post("/tools",           ex_wrapper(tools.handle_post));
@@ -414,15 +312,267 @@ int llama_server(common_params & params, int argc, char ** argv, server_child &
         SRV_WRN("security: %s enabled - do not expose to untrusted environments\n", features.c_str());
     }
 
-    //
-    // Handle downloading model
-    //
+    return true;
+}
 
-    if (child.is_child() && child.get_mode() == SERVER_CHILD_MODE_DOWNLOAD) {
-        return child.run_download(params);
-    } else if (!is_router_server && !is_run_by_cli) {
-        // single-model mode (NOT spawned by router)
-        // if this is invoked by CLI, model downloading should be already handled
+static void server_install_signal_handlers() {
+#if defined (__unix__) || (defined (__APPLE__) && defined (__MACH__))
+    struct sigaction sigint_action;
+    sigint_action.sa_handler = signal_handler;
+    sigemptyset (&sigint_action.sa_mask);
+    sigint_action.sa_flags = 0;
+    sigaction(SIGINT, &sigint_action, NULL);
+    sigaction(SIGTERM, &sigint_action, NULL);
+#elif defined (_WIN32)
+    auto console_ctrl_handler = +[](DWORD ctrl_type) -> BOOL {
+        return (ctrl_type == CTRL_C_EVENT) ? (signal_handler(SIGINT), true) : false;
+    };
+    SetConsoleCtrlHandler(reinterpret_cast<PHANDLER_ROUTINE>(console_ctrl_handler), true);
+#endif
+}
+
+// once the HTTP server listens: log the addresses and spawn llama-connect if asked, so the port is
+// bound and the child startup health check reaches us. the destructor of connect_proc stops it
+static bool server_on_listening(server_http_context & ctx_http, const common_params & params, server_connect & connect_proc) {
+    for (const auto & address : ctx_http.listening_addresses) {
+        SRV_INF("listening on %s\n", address.c_str());
+    }
+
+    if (params.server_connect && !connect_proc.start(params, ctx_http.port)) {
+        SRV_ERR("%s", "exiting due to llama-connect error\n");
+        return false;
+    }
+    return true;
+}
+
+//
+// download worker: a child of the router that pulls a model into the cache and reports the progress
+//
+
+struct server_download_state : public common_download_callback {
+    server_role * role;
+    std::function<bool()> should_stop;
+    std::atomic<int64_t> last_progress_time{0}; // multiple files downloading in different threads
+    bool is_ok = false;
+
+    server_download_state(server_role * r) : role(r) {}
+
+    bool run(common_params & params) {
+        try {
+            common_models_handler handler = common_models_handler_init(params, LLAMA_EXAMPLE_SERVER);
+            common_models_handler_apply(handler, params, this);
+            is_ok = true;
+        } catch (const std::exception & e) {
+            auto model_name = params.model.get_name();
+            SRV_ERR("download failed for model name=%s: %s\n", model_name.c_str(), e.what());
+            is_ok = false;
+        }
+        return is_ok;
+    }
+    void on_progress(const common_download_progress & p) {
+        json data = {
+            {"url", p.url},
+            {"downloaded", p.downloaded},
+            {"total", p.total},
+        };
+        role->notify_to_router(server_state_to_str(SERVER_STATE_DOWNLOADING), data);
+    }
+    void on_start(const common_download_progress & p) override {
+        on_progress(p);
+    }
+    void on_update(const common_download_progress & p) override {
+        int64_t now = ggml_time_ms();
+        // throttle progress updates to avoid flooding logs
+        if (now - last_progress_time.load(std::memory_order_relaxed) >= 100) {
+            on_progress(p);
+            last_progress_time.store(now, std::memory_order_relaxed);
+        }
+    }
+    void on_done(const common_download_progress & p, bool) override {
+        on_progress(p);
+    }
+    bool is_cancelled() const override {
+        return should_stop ? should_stop() : false;
+    }
+};
+
+static int server_run_download(common_params & params, server_role & role) {
+    auto cancelled = std::make_shared<std::atomic<bool>>(false);
+
+    // monitor stdin for cancellation command from the router
+    std::thread signal_thread = role.setup([cancelled](int) {
+        cancelled->store(true, std::memory_order_relaxed);
+    });
+
+    server_download_state dl(&role);
+    dl.should_stop = [cancelled]() {
+        return cancelled->load(std::memory_order_relaxed);
+    };
+
+    bool ok = dl.run(params);
+
+    role.notify_to_router(server_state_to_str(SERVER_STATE_DOWNLOADING), {
+        {"result", ok ? "download_finished" : "download_failed"},
+    });
+
+    // router should send CMD_ROUTER_TO_CHILD_EXIT after receiving the result
+    if (signal_thread.joinable()) {
+        signal_thread.join();
+    }
+
+    SRV_INF("download completed %s\n", ok ? "successfully" : "with errors");
+    return 0;
+}
+
+//
+// router
+//
+
+static int server_run_router(common_params & params, int argc, char ** argv, const server_run_opts & opts) {
+    SRV_INF("%s", "starting server in router mode. models will be automatically loaded on-demand\n");
+
+    // note: this is guaranteed to out-live ctx_http and tools
+    server_mcp mcp_mgr;
+
+    // the router loads no model, its context stays empty; the routes it does not proxy still need one
+    server_context ctx_server;
+    server_routes  routes(params, ctx_server);
+    server_tools   tools;
+
+    server_http_context ctx_http;
+    if (!ctx_http.init(params)) {
+        SRV_ERR("%s", "failed to initialize HTTP server\n");
+        return 1;
+    }
+
+    // setup server instances manager
+    std::optional<server_models_routes> models_routes;
+    try {
+        models_routes.emplace(params, argc, argv);
+    } catch (const std::exception & e) {
+        SRV_ERR("failed to initialize router models: %s\n", e.what());
+        return 1;
+    }
+
+    // proxy handlers
+    // note: routes.get_health stays the same
+    routes.get_metrics                 = models_routes->proxy_get;
+    routes.post_props                  = models_routes->proxy_post;
+    routes.post_completions            = models_routes->proxy_post;
+    routes.post_completions_oai        = models_routes->proxy_post;
+    routes.post_chat_completions       = models_routes->proxy_post;
+    routes.post_control                = models_routes->proxy_post;
+    routes.post_responses_oai          = models_routes->proxy_post;
+    routes.post_transcriptions_oai     = models_routes->proxy_post;
+    routes.post_tts                    = models_routes->proxy_post;
+    routes.ws_realtime                 = models_routes->proxy_ws;
+    routes.post_anthropic_messages     = models_routes->proxy_post;
+    routes.post_anthropic_count_tokens = models_routes->proxy_post;
+    routes.post_infill                 = models_routes->proxy_post;
+    routes.post_embeddings             = models_routes->proxy_post;
+    routes.post_embeddings_oai         = models_routes->proxy_post;
+    routes.post_rerank                 = models_routes->proxy_post;
+    routes.post_systemone              = models_routes->proxy_post;
+    routes.post_tokenize               = models_routes->proxy_post;
+    routes.post_detokenize             = models_routes->proxy_post;
+    routes.post_apply_template         = models_routes->proxy_post;
+    routes.post_chat_completions_tok   = models_routes->proxy_post;
+    routes.post_responses_tok_oai      = models_routes->proxy_post;
+    routes.get_lora_adapters           = models_routes->proxy_get;
+    routes.post_lora_adapters          = models_routes->proxy_post;
+    routes.get_slots                   = models_routes->proxy_get;
+    routes.post_slots                  = models_routes->proxy_post;
+
+    // custom routes for router
+    routes.get_props                   = models_routes->get_router_props;
+    routes.get_models                  = models_routes->get_router_models;
+
+    ctx_http.post("/models",               ex_wrapper(models_routes->post_router_models));
+    ctx_http.post("/models/load",          ex_wrapper(models_routes->post_router_models_load));
+    ctx_http.post("/models/unload",        ex_wrapper(models_routes->post_router_models_unload));
+    ctx_http.get ("/models/sse",           ex_wrapper(models_routes->get_router_models_sse));
+    ctx_http.del ("/models",               ex_wrapper(models_routes->del_router_models));
+
+    server_register_routes(ctx_http, routes);
+    server_register_stream_routes(ctx_http,
+        models_routes->router_stream_get,
+        models_routes->router_streams_lookup,
+        models_routes->router_stream_delete);
+
+    if (!server_setup_features(ctx_http, params, mcp_mgr, tools, SERVER_ROLE_ROUTER)) {
+        return 1;
+    }
+
+    auto clean_up = [&models_routes, &mcp_mgr]() {
+        SRV_INF("%s: cleaning up before exit...\n", __func__);
+        // stop the session GC first, it finalizes live sessions and wakes pending readers
+        server_stream_session_manager_stop();
+        if (models_routes.has_value()) {
+            models_routes->stopping.store(true); // maybe redundant, but just to be safe
+            models_routes->models.unload_all();
+        }
+        mcp_mgr.shutdown();
+        llama_backend_free();
+    };
+
+    if (!ctx_http.start()) {
+        clean_up();
+        SRV_ERR("%s", "exiting due to HTTP server error\n");
+        return 1;
+    }
+    ctx_http.is_ready.store(true);
+
+    shutdown_handler = [&](int) {
+        if (models_routes.has_value()) {
+            // important to disconnect any SSE clients
+            models_routes->stopping.store(true);
+        }
+        mcp_mgr.shutdown();
+        ctx_http.stop();
+    };
+
+    try {
+        models_routes->models.load_startup_models();
+    } catch (const std::exception & e) {
+        SRV_ERR("failed to load models on startup: %s\n", e.what());
+        ctx_http.stop();
+        ctx_http.join();
+        clean_up();
+        return 1;
+    }
+
+    if (opts.install_signal_handlers) {
+        server_install_signal_handlers();
+    }
+
+    server_connect connect_proc;
+    if (!server_on_listening(ctx_http, params, connect_proc)) {
+        ctx_http.stop();
+        ctx_http.join();
+        clean_up();
+        return 1;
+    }
+
+    if (!params.models_preset_hf.empty()) {
+        SRV_WRN(      "NOTE: using preset.ini from HF repo '%s'\n", params.models_preset_hf.c_str());
+        SRV_WRN("%s", "      please only use presets that you can trust! Unknown presets may be unsafe\n");
+    }
+
+    ctx_http.join(); // keep the main thread alive
+
+    // when the HTTP server stops, clean up and exit
+    clean_up();
+
+    return 0;
+}
+
+//
+// instance
+//
+
+static int server_run_instance(common_params & params, server_role & role, common_models_handler & models_handler, const server_run_opts & opts) {
+    // -hf / docker: download if needed and resolve the local path. a child resolves what the router downloaded
+    if (opts.resolve_model) {
         try {
             common_models_handler_apply(models_handler, params);
         } catch (const std::exception & e) {
@@ -431,161 +581,188 @@ int llama_server(common_params & params, int argc, char ** argv, server_child &
         }
     }
 
-    //
-    // Start the server
-    //
+    // note: this is guaranteed to out-live ctx_http and tools
+    server_mcp mcp_mgr;
 
-    std::function<void()> clean_up;
+    // struct that contains llama context and inference
+    server_context ctx_server;
+    server_routes  routes(params, ctx_server);
+    server_tools   tools;
 
-    if (is_router_server) {
-        SRV_INF("%s", "starting server in router mode. models will be automatically loaded on-demand\n");
-
-        clean_up = [&models_routes, &mcp_mgr]() {
-            SRV_INF("%s: cleaning up before exit...\n", __func__);
-            // stop the session GC first, it finalizes live sessions and wakes pending readers
-            server_stream_session_manager_stop();
-            if (models_routes.has_value()) {
-                models_routes->stopping.store(true); // maybe redundant, but just to be safe
-                models_routes->models.unload_all();
-            }
-            mcp_mgr.shutdown();
-            llama_backend_free();
-        };
-
-        if (!ctx_http.start()) {
-            clean_up();
-            SRV_ERR("%s", "exiting due to HTTP server error\n");
-            return 1;
-        }
-        ctx_http.is_ready.store(true);
-
-        shutdown_handler = [&](int) {
-            if (models_routes.has_value()) {
-                // important to disconnect any SSE clients
-                models_routes->stopping.store(true);
-            }
-            mcp_mgr.shutdown();
-            ctx_http.stop();
-        };
-
-        try {
-            models_routes->models.load_startup_models();
-        } catch (const std::exception & e) {
-            SRV_ERR("failed to load models on startup: %s\n", e.what());
-            ctx_http.stop();
-            ctx_http.join();
-            clean_up();
-            return 1;
-        }
-
-    } else {
-        // setup clean up function, to be called before exit
-        clean_up = [&ctx_http, &ctx_server, &mcp_mgr]() {
-            SRV_INF("%s: cleaning up before exit...\n", __func__);
-            // stop the session GC first, it finalizes live sessions and wakes pending readers
-            server_stream_session_manager_stop();
-            ctx_http.stop();
-            ctx_server.terminate();
-            mcp_mgr.shutdown();
-            llama_backend_free();
-        };
-
-        // start the HTTP server before loading the model to be able to serve /health requests
-        if (!ctx_http.start()) {
-            clean_up();
-            SRV_ERR("%s", "exiting due to HTTP server error\n");
-            return 1;
-        }
-
-        // setup communication child --> router if necessary
-        if (child.is_child()) {
-            ctx_server.set_state_callback([&](server_state state, json payload) {
-                child.notify_to_router(server_state_to_str(state), payload);
-            });
-        }
-
-        if (!ctx_server.load_model(params)) {
-            clean_up();
-            ctx_http.join();
-            SRV_ERR("%s", "exiting due to model loading error\n");
-            return 1;
-        }
-
-        routes.update_meta(ctx_server);
-        ctx_http.is_ready.store(true);
-
-        SRV_INF("%s", "model loaded\n");
-
-        shutdown_handler = [&](int) {
-            mcp_mgr.shutdown();
-            // this will unblock start_loop()
-            ctx_server.terminate();
-        };
+    server_http_context ctx_http;
+    if (!ctx_http.init(params)) {
+        SRV_ERR("%s", "failed to initialize HTTP server\n");
+        return 1;
     }
 
-    // register signal handler if not running by CLI
-    if (!is_run_by_cli) {
-#if defined (__unix__) || (defined (__APPLE__) && defined (__MACH__))
-        struct sigaction sigint_action;
-        sigint_action.sa_handler = signal_handler;
-        sigemptyset (&sigint_action.sa_mask);
-        sigint_action.sa_flags = 0;
-        sigaction(SIGINT, &sigint_action, NULL);
-        sigaction(SIGTERM, &sigint_action, NULL);
-#elif defined (_WIN32)
-        auto console_ctrl_handler = +[](DWORD ctrl_type) -> BOOL {
-            return (ctrl_type == CTRL_C_EVENT) ? (signal_handler(SIGINT), true) : false;
-        };
-        SetConsoleCtrlHandler(reinterpret_cast<PHANDLER_ROUTINE>(console_ctrl_handler), true);
-#endif
+    server_register_routes(ctx_http, routes);
+    server_register_stream_routes(ctx_http,
+        server_stream_make_get_handler(),
+        server_stream_make_lookup_handler(),
+        server_stream_make_delete_handler());
+
+    if (!server_setup_features(ctx_http, params, mcp_mgr, tools, SERVER_ROLE_INSTANCE)) {
+        return 1;
     }
 
-    for (const auto & address : ctx_http.listening_addresses) {
-        SRV_INF("listening on %s\n", address.c_str());
+    // setup clean up function, to be called before exit
+    auto clean_up = [&ctx_http, &ctx_server, &mcp_mgr]() {
+        SRV_INF("%s: cleaning up before exit...\n", __func__);
+        // stop the session GC first, it finalizes live sessions and wakes pending readers
+        server_stream_session_manager_stop();
+        ctx_http.stop();
+        ctx_server.terminate();
+        mcp_mgr.shutdown();
+        llama_backend_free();
+    };
+
+    // start the HTTP server before loading the model to be able to serve /health requests
+    if (!ctx_http.start()) {
+        clean_up();
+        SRV_ERR("%s", "exiting due to HTTP server error\n");
+        return 1;
+    }
+
+    // setup communication child --> router if necessary
+    if (role.is_managed_by_router()) {
+        ctx_server.set_state_callback([&](server_state state, json payload) {
+            role.notify_to_router(server_state_to_str(state), payload);
+        });
+    }
+
+    if (!ctx_server.load_model(params)) {
+        clean_up();
+        ctx_http.join();
+        SRV_ERR("%s", "exiting due to model loading error\n");
+        return 1;
+    }
+
+    routes.update_meta(ctx_server);
+    ctx_http.is_ready.store(true);
+
+    SRV_INF("%s", "model loaded\n");
+
+    shutdown_handler = [&](int) {
+        mcp_mgr.shutdown();
+        // this will unblock start_loop()
+        ctx_server.terminate();
+    };
+
+    if (opts.install_signal_handlers) {
+        server_install_signal_handlers();
     }
 
-    // spawn only once listening, so the port is bound and the child startup health check reaches us. the destructor stops it
     server_connect connect_proc;
-    if (params.server_connect && !connect_proc.start(params, ctx_http.port)) {
-        SRV_ERR("%s", "exiting due to llama-connect error\n");
+    if (!server_on_listening(ctx_http, params, connect_proc)) {
         ctx_http.stop();
         ctx_http.join();
         clean_up();
         return 1;
     }
 
-    if (is_router_server) {
-        if (!params.models_preset_hf.empty()) {
-            SRV_WRN(      "NOTE: using preset.ini from HF repo '%s'\n", params.models_preset_hf.c_str());
-            SRV_WRN("%s", "      please only use presets that you can trust! Unknown presets may be unsafe\n");
-        }
+    // optionally, notify router server that this instance is ready
+    std::thread monitor_thread;
+    if (role.is_managed_by_router()) {
+        monitor_thread = role.setup(shutdown_handler);
+        role.notify_to_router(server_state_to_str(SERVER_STATE_READY), routes.get_model_info());
+    }
 
-        ctx_http.join(); // keep the main thread alive
+    // this call blocks the main thread until queue_tasks.terminate() is called
+    ctx_server.start_loop();
 
-        // when the HTTP server stops, clean up and exit
-        clean_up();
-    } else {
-        // optionally, notify router server that this instance is ready
-        std::thread monitor_thread;
-        if (child.is_child()) {
-            monitor_thread = child.setup(shutdown_handler);
-            child.notify_to_router(server_state_to_str(SERVER_STATE_READY), routes.get_model_info());
-        }
+    clean_up();
+    ctx_http.join();
+    if (monitor_thread.joinable()) {
+        monitor_thread.join();
+    }
 
-        // this call blocks the main thread until queue_tasks.terminate() is called
-        ctx_server.start_loop();
-
-        clean_up();
-        ctx_http.join();
-        if (monitor_thread.joinable()) {
-            monitor_thread.join();
-        }
-
-        auto * ll_ctx = ctx_server.get_llama_context();
-        if (ll_ctx != nullptr) {
-            common_memory_breakdown_print(ll_ctx);
-        }
+    auto * ll_ctx = ctx_server.get_llama_context();
+    if (ll_ctx != nullptr) {
+        common_memory_breakdown_print(ll_ctx);
     }
 
     return 0;
 }
+
+//
+// entry points
+//
+
+static int server_run(common_params & params, int argc, char ** argv, server_role & role, const server_run_opts & opts) {
+    common_models_handler models_handler;
+
+    // -hf may name a preset repo, which makes this a router: settle that before deciding the role
+    if (opts.resolve_model && !params.model.hf_repo.empty()) {
+        try {
+            models_handler = common_models_handler_init(params, LLAMA_EXAMPLE_SERVER);
+            if (common_models_handler_is_preset_repo(models_handler)) {
+                // apply the preset and start the server in router mode
+                common_models_handler_apply(models_handler, params);
+            }
+        } catch (const std::exception & e) {
+            SRV_ERR("failed to fetch model metadata: %s\n", e.what());
+            return 1;
+        }
+    }
+
+    const server_role_type role_type = server_role_detect(params, role);
+
+    // only an instance loads a model; the others must not touch the GPU, so skip the
+    // device enumeration for them and the CUDA primary context stays uncreated
+    common_params_print_info(params, role_type == SERVER_ROLE_INSTANCE);
+
+    if (!server_prepare_params(params, role_type)) {
+        return 1;
+    }
+
+    switch (role_type) {
+        case SERVER_ROLE_DOWNLOAD: return server_run_download(params, role);
+        case SERVER_ROLE_ROUTER:   return server_run_router(params, argc, argv, opts);
+        case SERVER_ROLE_INSTANCE: return server_run_instance(params, role, models_handler, opts);
+    }
+
+    GGML_ABORT("invalid server role");
+}
+
+int llama_server(int argc, char ** argv) {
+    server_role role;
+
+    std::setlocale(LC_NUMERIC, "C");
+
+#ifndef _WIN32
+    // Ignore SIGPIPE so the server does not crash if a child (MCP server, tools runtime) exits while we are writing to its stdin
+    signal(SIGPIPE, SIG_IGN);
+#endif
+
+    // own arguments required by this example
+    common_params params;
+
+    common_init();
+
+    // start the stream session manager GC right after common init, before any HTTP route can
+    // touch it. lifecycle is symmetric, stop_gc() runs in clean_up() before backend free
+    server_stream_session_manager_start();
+
+    if (!common_params_parse(argc, argv, params, LLAMA_EXAMPLE_SERVER)) {
+        return 1;
+    }
+
+    SRV_INF("%s", "initializing ...\n");
+
+    llama_backend_init();
+    llama_numa_init(params.numa);
+
+    const int result = server_run(params, argc, argv, role, server_run_opts{});
+    common_log_flush(common_log_main());
+    return result;
+}
+
+int llama_server(common_params & params, int argc, char ** argv) {
+    // embedded in llama-cli: it handles the signals, and the model is resolved already
+    server_run_opts opts;
+    opts.install_signal_handlers = false;
+    opts.resolve_model           = false;
+
+    server_role role;
+    return server_run(params, argc, argv, role, opts);
+}
