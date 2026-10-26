# /tokenize and /detokenize at llama.cpp caa8191df159f764fb0160e3d2fc6be008948aee

Fetched with `curl -sS https://raw.githubusercontent.com/ggml-org/llama.cpp/caa8191df159f764fb0160e3d2fc6be008948aee/<path>` (all HTTP 200);
line numbers are from those files. The installed `llama-server` reports `version: 0.7.0-dev (build 11909, commit caa8191df)`.

## tools/server/server-context.cpp:6248-6302

```c++
 6248          }
 6249          return res;
 6250      };
 6251  
 6252      this->post_tokenize = [this](const server_http_req & req) {
 6253          auto res = create_response();
 6254          const json body = json::parse(req.body);
 6255          json tokens_response = json::array();
 6256          if (body.count("content") != 0) {
 6257              const bool add_special = json_value(body, "add_special", false);
 6258              const bool parse_special = json_value(body, "parse_special", true);
 6259              const bool with_pieces = json_value(body, "with_pieces", false);
 6260  
 6261              llama_tokens tokens = tokenize_mixed(ctx_server.vocab, body.at("content"), add_special, parse_special);
 6262  
 6263              if (with_pieces) {
 6264                  for (const auto& token : tokens) {
 6265                      std::string piece = common_token_to_piece(ctx_server.vocab, token);
 6266                      json piece_json;
 6267  
 6268                      // Check if the piece is valid UTF-8
 6269                      if (is_valid_utf8(piece)) {
 6270                          piece_json = piece;
 6271                      } else {
 6272                          // If not valid UTF-8, store as array of byte values
 6273                          piece_json = json::array();
 6274                          for (unsigned char c : piece) {
 6275                              piece_json.push_back(static_cast<int>(c));
 6276                          }
 6277                      }
 6278  
 6279                      tokens_response.push_back({
 6280                          {"id", token},
 6281                          {"piece", piece_json}
 6282                      });
 6283                  }
 6284              } else {
 6285                  tokens_response = tokens;
 6286              }
 6287          }
 6288  
 6289          res->ok(json{{"tokens", std::move(tokens_response)}});
 6290          return res;
 6291      };
 6292  
 6293      this->post_detokenize = [this](const server_http_req & req) {
 6294          auto res = create_response();
 6295          const json body = json::parse(req.body);
 6296  
 6297          std::string content;
 6298          if (body.count("tokens") != 0) {
 6299              const llama_tokens tokens = body.at("tokens").get<llama_tokens>();
 6300              content = tokens_to_str(ctx_server.vocab, tokens);
 6301          }
 6302  
```

## tools/server/server.cpp:196-206

```c++
  196      ctx_http.post("/reranking",                ex_wrapper(routes.post_rerank));
  197      ctx_http.post("/v1/rerank",                ex_wrapper(routes.post_rerank));
  198      ctx_http.post("/v1/reranking",             ex_wrapper(routes.post_rerank));
  199      ctx_http.post("/v1/systemone",             ex_wrapper(routes.post_systemone));
  200      ctx_http.post("/tokenize",                 ex_wrapper(routes.post_tokenize));
  201      ctx_http.post("/detokenize",               ex_wrapper(routes.post_detokenize));
  202      ctx_http.post("/apply-template",           ex_wrapper(routes.post_apply_template));
  203      // token counting
  204      ctx_http.post("/chat/completions/input_tokens",    ex_wrapper(routes.post_chat_completions_tok));
  205      ctx_http.post("/v1/chat/completions/input_tokens", ex_wrapper(routes.post_chat_completions_tok));
  206      ctx_http.post("/responses/input_tokens",           ex_wrapper(routes.post_responses_tok_oai));
```

## tools/server/server-common.cpp:986-1010

```c++
  986  }
  987  
  988  llama_tokens tokenize_mixed(const llama_vocab * vocab, const json & json_prompt, bool add_special, bool parse_special) {
  989      // If `add_bos` is true, we only add BOS, when json_prompt is a string,
  990      // or the first element of the json_prompt array is a string.
  991      llama_tokens prompt_tokens;
  992  
  993      if (json_prompt.is_array()) {
  994          bool first = true;
  995          for (const auto & p : json_prompt) {
  996              if (p.is_string()) {
  997                  auto s = p.template get<std::string>();
  998  
  999                  llama_tokens p;
 1000                  if (first) {
 1001                      p = common_tokenize(vocab, s, add_special, parse_special);
 1002                      first = false;
 1003                  } else {
 1004                      p = common_tokenize(vocab, s, false, parse_special);
 1005                  }
 1006  
 1007                  prompt_tokens.insert(prompt_tokens.end(), p.begin(), p.end());
 1008              } else {
 1009                  if (first) {
 1010                      first = false;
```

## tools/server/server-common.cpp:1715-1736

```c++
 1715  }
 1716  
 1717  // TODO: reuse llama_detokenize
 1718  template <class Iter>
 1719  static std::string tokens_to_str(const llama_vocab * ctx, Iter begin, Iter end) {
 1720      std::string ret;
 1721      for (; begin != end; ++begin) {
 1722          ret += common_token_to_piece(ctx, *begin);
 1723      }
 1724  
 1725      return ret;
 1726  }
 1727  
 1728  std::string tokens_to_str(llama_context * ctx, const llama_tokens & tokens) {
 1729      auto model = llama_get_model(ctx);
 1730      return tokens_to_str(llama_model_get_vocab(model), tokens.begin(), tokens.end());
 1731  }
 1732  
 1733  std::string tokens_to_str(const llama_vocab * vocab, const llama_tokens & tokens) {
 1734      return tokens_to_str(vocab, tokens.begin(), tokens.end());
 1735  }
 1736  
```

## tools/server/server-common.cpp:1815-1846

```c++
 1815  bool is_valid_utf8(const std::string & str) {
 1816      const unsigned char* bytes = reinterpret_cast<const unsigned char*>(str.data());
 1817      const unsigned char* end = bytes + str.length();
 1818  
 1819      while (bytes < end) {
 1820          if (*bytes <= 0x7F) {
 1821              // 1-byte sequence (0xxxxxxx)
 1822              bytes++;
 1823          } else if ((*bytes & 0xE0) == 0xC0) {
 1824              // 2-byte sequence (110xxxxx 10xxxxxx)
 1825              if (end - bytes < 2 || (bytes[1] & 0xC0) != 0x80)
 1826                  return false;
 1827              bytes += 2;
 1828          } else if ((*bytes & 0xF0) == 0xE0) {
 1829              // 3-byte sequence (1110xxxx 10xxxxxx 10xxxxxx)
 1830              if (end - bytes < 3 || (bytes[1] & 0xC0) != 0x80 || (bytes[2] & 0xC0) != 0x80)
 1831                  return false;
 1832              bytes += 3;
 1833          } else if ((*bytes & 0xF8) == 0xF0) {
 1834              // 4-byte sequence (11110xxx 10xxxxxx 10xxxxxx 10xxxxxx)
 1835              if (end - bytes < 4 || (bytes[1] & 0xC0) != 0x80 ||
 1836                  (bytes[2] & 0xC0) != 0x80 || (bytes[3] & 0xC0) != 0x80)
 1837                  return false;
 1838              bytes += 4;
 1839          } else {
 1840              // Invalid UTF-8 lead byte
 1841              return false;
 1842          }
 1843      }
 1844  
 1845      return true;
 1846  }
```

## common/common.cpp:1875-1896

```c++
 1875  std::string common_token_to_piece(const struct llama_context * ctx, llama_token token, bool special) {
 1876      const llama_model * model = llama_get_model(ctx);
 1877      const llama_vocab * vocab = llama_model_get_vocab(model);
 1878      return common_token_to_piece(vocab, token, special);
 1879  }
 1880  
 1881  std::string common_token_to_piece(const struct llama_vocab * vocab, llama_token token, bool special) {
 1882      std::string piece;
 1883      piece.resize(piece.capacity());  // using string internal cache, 15 bytes + '\n'
 1884      const int n_chars = llama_token_to_piece(vocab, token, &piece[0], piece.size(), 0, special);
 1885      if (n_chars < 0) {
 1886          piece.resize(-n_chars);
 1887          int check = llama_token_to_piece(vocab, token, &piece[0], piece.size(), 0, special);
 1888          GGML_ASSERT(check == -n_chars);
 1889      }
 1890      else {
 1891          piece.resize(n_chars);
 1892      }
 1893  
 1894      return piece;
 1895  }
 1896  
```

## src/llama-vocab.cpp:109-120

```c++
  109  struct llm_tokenizer_spm_session {
  110      llm_tokenizer_spm_session(const llama_vocab & vocab) : vocab(vocab) {}
  111  
  112      void tokenize(const std::string & text, std::vector<llama_token> & output) {
  113          // split string into utf8 chars
  114          int index = 0;
  115          size_t offs = 0;
  116          while (offs < text.size()) {
  117              llm_symbol sym;
  118              size_t len = unicode_len_utf8(text[offs]);
  119              sym.text = text.c_str() + offs;
  120              sym.n = std::min(len, text.size() - offs);
```

## src/llama-vocab.cpp:176-200

```c++
  176              todo.pop_back();
  177  
  178              auto text = std::string(cur.text, cur.n);
  179              auto token = vocab.text_to_token(text);
  180  
  181              // Do we need to support is_unused?
  182              if (token != LLAMA_TOKEN_NULL) {
  183                  output.push_back(token);
  184                  continue;
  185              }
  186  
  187              const auto p = rev_merge.find(text);
  188  
  189              if (p == rev_merge.end()) {
  190                  // output any symbols that did not form tokens as bytes.
  191                  output.reserve(output.size() + cur.n);
  192                  for (int j = 0; j < (int)cur.n; ++j) {
  193                      llama_token id = vocab.byte_to_token(cur.text[j]);
  194                      output.push_back(id);
  195                  }
  196                  continue;
  197              }
  198  
  199              todo.push_back(&symbols[p->second.second]);
  200              todo.push_back(&symbols[p->second.first]);
```

## src/llama-vocab.cpp:3751-3778

```c++
 3751  std::string llama_vocab::impl::token_to_piece_for_cache(llama_token token, bool special) const {
 3752      std::string piece;
 3753      piece.resize(piece.capacity());  // using string internal cache
 3754      const int n_chars = vocab.token_to_piece(token, &piece[0], piece.size(), 0, special);
 3755      if (n_chars < 0) {
 3756          piece.resize(-n_chars);
 3757          int check = vocab.token_to_piece(token, &piece[0], piece.size(), 0, special);
 3758          GGML_ASSERT(check == -n_chars);
 3759      }
 3760      else {
 3761          piece.resize(n_chars);
 3762      }
 3763  
 3764      return piece;
 3765  }
 3766  
 3767  static void llama_escape_whitespace(std::string & text) {
 3768      replace_all(text, " ", "\xe2\x96\x81");
 3769  }
 3770  
 3771  static void llama_unescape_whitespace(std::string & word) {
 3772      replace_all(word, "\xe2\x96\x81", " ");
 3773  }
 3774  
 3775  static std::string llama_decode_text(const std::string & text) {
 3776      std::string decoded_text;
 3777      decoded_text.reserve(text.size());
 3778  
```

## src/llama-vocab.cpp:3811-3844

```c++
 3811          case LLAMA_VOCAB_TYPE_SPM:
 3812              {
 3813                  // OG tokenizer behavior:
 3814                  //
 3815                  // tokenizer.encode('', add_special_tokens=True)  returns [1]
 3816                  // tokenizer.encode('', add_special_tokens=False) returns []
 3817  
 3818                  // TODO: honor metaspace_prepend_scheme (add_space_prefix currently behaves like "always")
 3819                  bool is_prev_special = true;  // prefix with space if first token
 3820  
 3821                  if (add_special && add_bos) {
 3822                      GGML_ASSERT(special_bos_id != LLAMA_TOKEN_NULL);
 3823                      output.push_back(special_bos_id);
 3824                      is_prev_special = true;
 3825                  }
 3826  
 3827                  for (const auto & fragment : fragment_buffer) {
 3828                      if (fragment.type == FRAGMENT_BUFFER_VARIANT_TYPE_RAW_TEXT) {
 3829                          std::string text;
 3830  
 3831                          // prefix with space if previous is special
 3832                          if (add_space_prefix && is_prev_special) {
 3833                              text = ' ';
 3834                          }
 3835  
 3836                          text += fragment.raw_text.substr(fragment.offset, fragment.length);
 3837  
 3838  #ifdef PRETOKENIZERDEBUG
 3839                          LLAMA_LOG_WARN("TT: (%ld %ld %ld) '%s'\n", text.length(), fragment.offset, fragment.length, text.c_str());
 3840  #endif
 3841                          llama_escape_whitespace(text);
 3842                          llm_tokenizer_spm_session session(vocab);
 3843                          session.tokenize(text, output);
 3844                          is_prev_special = false;
```

## src/llama-vocab.cpp:4064-4072

```c++
 4064  int32_t llama_vocab::impl::token_to_piece(llama_token token, char * buf, int32_t length, int32_t lstrip, bool special) const {
 4065      // ref: https://github.com/ggml-org/llama.cpp/pull/7587#discussion_r1620983843
 4066      static const int attr_special = LLAMA_TOKEN_ATTR_UNKNOWN | LLAMA_TOKEN_ATTR_CONTROL;
 4067      const llama_token_attr attr = token_get_attr(token);
 4068      if (!special && (attr & attr_special)) {
 4069          return 0;
 4070      }
 4071  
 4072      // copy piece chars to output text buffer
```

## src/llama-vocab.cpp:4100-4120

```c++
 4100      if (0 <= token && token < (int32_t) id_to_token.size()) {
 4101          const std::string & token_text = id_to_token[token].text;
 4102          switch (get_type()) {
 4103              case LLAMA_VOCAB_TYPE_WPM:
 4104              case LLAMA_VOCAB_TYPE_SPM:
 4105              case LLAMA_VOCAB_TYPE_UGM: {
 4106                  // NOTE: we accept all unsupported token types,
 4107                  // suppressing them like CONTROL tokens.
 4108                  if (attr & (attr_special | LLAMA_TOKEN_ATTR_USER_DEFINED)) {
 4109                      return _try_copy(token_text.data(), token_text.size());
 4110                  }
 4111                  if (attr & LLAMA_TOKEN_ATTR_NORMAL) {
 4112                      std::string result = token_text;
 4113                      llama_unescape_whitespace(result);
 4114                      return _try_copy(result.data(), result.size());
 4115                  }
 4116                  if (attr & LLAMA_TOKEN_ATTR_BYTE) {
 4117                      char byte = (char) token_to_byte(token);
 4118                      return _try_copy((char*) &byte, 1);
 4119                  }
 4120                  break;
```

## src/llama-vocab.cpp:4210-4218

```c++
 4210      int32_t avail = text_len_max;
 4211      int32_t total = 0;
 4212  
 4213      // remove the leading space
 4214      bool remove_space = add_space_prefix;
 4215  
 4216      if (remove_special && add_bos) {
 4217          if (n_tokens > 0 && tokens[0] == special_bos_id) {
 4218              remove_space = false;
```

## src/llama-vocab.cpp:2760-2766

```c++
 2760                  throw std::runtime_error(format("unknown pre-tokenizer type: '%s'", tokenizer_pre.c_str()));
 2761              }
 2762          } else if (type == LLAMA_VOCAB_TYPE_SPM) {
 2763              pre_type = LLAMA_VOCAB_PRE_TYPE_DEFAULT;
 2764              add_space_prefix = true;
 2765              clean_spaces = false;
 2766              add_bos = true;
```

## src/llama-vocab.cpp:2789-2790

```c++
 2789          ml.get_key(LLM_KV_TOKENIZER_ADD_PREFIX,      add_space_prefix,         false);
 2790          ml.get_key(LLM_KV_TOKENIZER_REMOVE_EXTRA_WS, remove_extra_whitespaces, false);
```

## src/llama-vocab.cpp:2841-2862

```c++
 2841      id_to_token.resize(n_tokens);
 2842      token_to_id.reserve(n_tokens);
 2843  
 2844      for (uint32_t i = 0; i < n_tokens; i++) {
 2845          std::string word = gguf_get_arr_str(ctx, token_idx, i);
 2846          if (word.empty()) {
 2847              LLAMA_LOG_WARN("%s: empty token at index %u\n", __func__, i);
 2848              word = "[EMPTY_" + std::to_string(i) + "]";
 2849          }
 2850  
 2851          token_to_id[word] = i;
 2852          max_token_len = std::max(max_token_len, (int) word.size());
 2853  
 2854          auto & token_data = id_to_token[i];
 2855          token_data.text  = std::move(word);
 2856          if (scores) {
 2857              token_data.score = scores[i];
 2858          } else if (iscores) {
 2859              token_data.score = static_cast<float>(iscores[i]);
 2860          } else {
 2861              token_data.score = 0.0f;
 2862          }
```

## src/llama-vocab.cpp:3565-3582

```c++
 3565  uint8_t llama_vocab::impl::token_to_byte(llama_token id) const {
 3566      GGML_ASSERT(get_type() != LLAMA_VOCAB_TYPE_NONE);
 3567      GGML_ASSERT(is_byte(id));
 3568      const auto & token_data = id_to_token.at(id);
 3569      switch (get_type()) {
 3570          case LLAMA_VOCAB_TYPE_SPM:
 3571          case LLAMA_VOCAB_TYPE_UGM: {
 3572              auto buf = token_data.text.substr(3, 2);
 3573              return strtol(buf.c_str(), NULL, 16);
 3574          }
 3575          case LLAMA_VOCAB_TYPE_BPE: {
 3576              // Gemma4 uses BPE with SPM-style byte fallback tokens (<0xXX>)
 3577              auto buf = token_data.text.substr(3, 2);
 3578              return strtol(buf.c_str(), NULL, 16);
 3579          }
 3580          case LLAMA_VOCAB_TYPE_WPM: {
 3581              GGML_ABORT("fatal error");
 3582          }
```

## tools/server/README.md:686-701

```c++
  686  ### POST `/tokenize`: Tokenize a given text
  687  
  688  *Options:*
  689  
  690  `content`: (Required) The text to tokenize.
  691  
  692  `add_special`: (Optional) Boolean indicating if special tokens, i.e. `BOS`, should be inserted.  Default: `false`
  693  
  694  `parse_special`: (Optional) Boolean indicating if special tokens should be tokenized. When `false` special tokens are treated as plaintext.  Default: `true`
  695  
  696  `with_pieces`: (Optional) Boolean indicating whether to return token pieces along with IDs.  Default: `false`
  697  
  698  **Response:**
  699  
  700  Returns a JSON object with a `tokens` field containing the tokenization result. The `tokens` array contains either just token IDs or objects with `id` and `piece` fields, depending on the `with_pieces` parameter. The piece field is a string if the piece is valid unicode or a list of bytes otherwise.
  701  
```

## tools/server/README.md:731-736

```c++
  731  ### POST `/detokenize`: Convert tokens to text
  732  
  733  *Options:*
  734  
  735  `tokens`: Set the tokens to detokenize.
  736  
```
