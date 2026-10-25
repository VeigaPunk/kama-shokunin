diff --git a/tools/server/server-http.cpp b/tools/server/server-http.cpp
index 33cbb156c..cf147c7e7 100644
--- a/tools/server/server-http.cpp
+++ b/tools/server/server-http.cpp
@@ -11,6 +11,7 @@
 #include <memory>
 #include <string>
 #include <thread>
+#include <mutex>
 
 //
 // HTTP implementation using cpp-httplib
@@ -744,6 +745,56 @@ void server_http_context::post(const std::string & path, const server_http_conte
     }
 }
 
+void server_http_context::ws(const std::string & path, const server_http_context::ws_handler_t & handler) const {
+    const std::string full_path = path_prefix + path;
+
+    auto callback = [handler](const httplib::Request & req, httplib::ws::WebSocket & sock) {
+        struct conn_impl : server_http_context::ws_conn {
+            httplib::ws::WebSocket & sock;
+            std::mutex mutex_send;
+            conn_impl(httplib::ws::WebSocket & sock) : sock(sock) {}
+            int read(std::string & msg) override {
+                switch (sock.read(msg)) {
+                    case httplib::ws::Text:   return 1;
+                    case httplib::ws::Binary: return 2;
+                    default:                  return 0;
+                }
+            }
+            bool send(const std::string & msg) override {
+                std::lock_guard<std::mutex> lock(mutex_send);
+                return sock.send(msg);
+            }
+            bool send_binary(const std::string & msg) override {
+                std::lock_guard<std::mutex> lock(mutex_send);
+                return sock.send(msg.data(), msg.size());
+            }
+            bool is_open() const override {
+                return sock.is_open();
+            }
+            void close() override {
+                sock.close();
+            }
+        };
+        conn_impl conn(sock);
+        const std::function<bool()> should_stop = [&sock]() {
+            return !sock.is_open();
+        };
+        server_http_req request{
+            get_params(req),
+            get_headers(req),
+            req.path,
+            build_query_string(req),
+            req.body,
+            {},
+            should_stop
+        };
+        handler(request, conn);
+    };
+    for (const auto & srv : pimpl->servers) {
+        srv->WebSocket(full_path, callback);
+    }
+}
+
 void server_http_context::del(const std::string & path, const server_http_context::handler_t & handler) const {
     handlers.emplace(path, handler);
     auto callback = [handler](const httplib::Request & req, httplib::Response & res) {
