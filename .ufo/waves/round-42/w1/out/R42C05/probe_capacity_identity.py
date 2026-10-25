"""R42C05 probe: re-implements vLLM v0.32.0 kv_cache_utils.py:1210-1227 + 2300-2308
verbatim (cdiv, per-group per-request block demand, min over device/host pool,
int(max_concurrency * max_model_len)) and compares the result against the
S478 entry's identity: "capacity in tokens == the pool expressed in units of the
declared per-request length".

No vLLM import; the two formulas are transcribed from the committed copy
sha256 af4164bca819f1cdc416077522a7019936fd38a523a482283eb91b08dae0e57a.
"""

P = 16          # page_size_bytes expressed in tokens
B_PER_TOKEN = 1024  # bytes of KV per token per layer (arbitrary, cancels)
L = 8192        # max_model_len (declared per-request length)
W = 2048        # sliding window size
M = 20 * P * B_PER_TOKEN * 1000  # memory sized so the hybrid layout yields N=1000 blocks


def cdiv(a, b):
    return -(-a // b)


def capacity(groups, num_blocks, max_model_len, host_blocks=None, host_groups=()):
    """groups: list of per-request token demand T_g for device-resident groups.
    host_groups: same for host-resident groups."""
    dev_per_req = sum(cdiv(t, P) for t in groups)
    host_per_req = sum(cdiv(t, P) for t in host_groups)
    limits = [num_blocks / dev_per_req]
    if host_per_req:
        limits.append(host_blocks / host_per_req)
    conc = min(limits)
    return int(conc * max_model_len), conc, dev_per_req


def blocks_for(layers, memory):
    """bytes_per_block = layers * P * B_PER_TOKEN (block-outermost, one group set);
    num_blocks = memory // bytes_per_block  (kv_cache_utils.py:1627)."""
    return memory // (layers * P * B_PER_TOKEN)


print(f"P={P} tokens/block  L(max_model_len)={L}  W(window)={W}  memory={M} bytes")
print()

# Case A: uniform full attention, 20 layers, one group -> pool tokens == reported
n_a = blocks_for(20, M)
tok, conc, per_req = capacity([L], n_a, L)
print(f"A uniform FA       layers=20 N={n_a:5d} per_req_blocks={per_req:4d} "
      f"conc={conc:8.4f} reported={tok:6d} pool_tokens={n_a*P:6d} "
      f"ratio={tok/(n_a*P):.6f}")

# Case B: hybrid 10 FA + 20 SW, hybrid manager ENABLED.
#   SW group per-request demand is window-bounded (kv_cache_utils.py:1370-1377, 2584-2590);
#   bytes_per_block = max over groups of that group's layers = 20 layers.
n_b = blocks_for(20, M)
tok_b, conc_b, per_req_b = capacity([L, W], n_b, L)
print(f"B hybrid FA+SW     layers=20 N={n_b:5d} per_req_blocks={per_req_b:4d} "
      f"conc={conc_b:8.4f} reported={tok_b:6d} pool_tokens={n_b*P:6d} "
      f"ratio={tok_b/(n_b*P):.6f}  (L/sum(T_g)={L/(L+W):.4f})")
print(f"   stored tokens at full admission = conc*(L+W) = {conc_b*(L+W):.1f} "
      f"== pool {n_b*P}")

# Case C: same model, --disable-hybrid-kv-cache-manager -> SW promoted to FA
#   (kv_cache_utils.py:1733, 1737-1745, 1799-1822): one group, 30 layers.
n_c = blocks_for(30, M)
tok_c, conc_c, per_req_c = capacity([L], n_c, L)
print(f"C promoted to FA   layers=30 N={n_c:5d} per_req_blocks={per_req_c:4d} "
      f"conc={conc_c:8.4f} reported={tok_c:6d} pool_tokens={n_c*P:6d} "
      f"ratio={tok_c/(n_c*P):.6f}")

# Case D: host pool binds (hisparse). Device pool unchanged from A, host smaller.
tok_d, conc_d, per_req_d = capacity([L], n_a, L, host_blocks=500, host_groups=[L])
print(f"D host pool binds  deviceN={n_a:5d} hostN=  500 per_req_blocks={per_req_d:4d} "
      f"conc={conc_d:8.4f} reported={tok_d:6d} device_pool_tokens={n_a*P:6d} "
      f"ratio={tok_d/(n_a*P):.6f}")

# Case E: attention-free model -> empty group list (kv_cache_utils.py:1604-1615)
try:
    capacity([], 1, L)
except ZeroDivisionError as e:
    print(f"E attention-free   groups=[] num_blocks=1 -> ZeroDivisionError: {e} "
          f"(kv_cache_utils.py:1221)")

print()
print("identity 'reported == pool tokens' holds only where ratio==1.000000")
