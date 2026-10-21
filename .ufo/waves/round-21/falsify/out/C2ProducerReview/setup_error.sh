#!/usr/bin/env bash
# Scratch: real producer receipts for pre-launch setup errors. No server is ever
# started: both cases stop at a SetupError before Popen (stub llama-server is never run).
set -u
X=/tmp/kama-r21-C2ProducerReview/exp/unpin
LANE=/tmp/kama-r21-C2ProducerReview/lane
OLD=/tmp/kama-r21-C2ProducerReview/exp/old
rm -rf "$X"; mkdir -p "$X/bin/glibc-hwcaps/x86-64-v3" "$X/model" "$X/probe"
printf '#!/bin/sh\nexit 0\n' > "$X/bin/llama-server"; chmod +x "$X/bin/llama-server"
printf 'GGUF-stub\n' > "$X/model/tiny.gguf"
printf '# stub probe, never executed\n' > "$X/probe/kama-probe.sh"
SHA=$(sha256sum "$X/model/tiny.gguf" | cut -d' ' -f1)
WRONG=$(printf '0%.0s' $(seq 64))

echo "== new producer, unpinnable tree (glibc-hwcaps/ present) =="
timeout 60 python3 -B "$LANE/tools/kama-llamacpp-live.py" --server "$X/bin/llama-server" \
  --model "$X/model/tiny.gguf" --model-sha256 "$SHA" --probe "$X/probe/kama-probe.sh" \
  --out "$X/receipt-new-unpinnable.json"; echo "new_producer_exit=$?"

echo "== old producer (7a6bc911), wrong model digest: pre-existing setup-error shape =="
timeout 60 python3 -B "$OLD/kll_old.py" --server "$X/bin/llama-server" \
  --model "$X/model/tiny.gguf" --model-sha256 "$WRONG" --probe "$X/probe/kama-probe.sh" \
  --out "$X/receipt-old-digest-mismatch.json"; echo "old_producer_exit=$?"

echo "== gates on the unpinnable receipt =="
timeout 60 python3 -B "$LANE/tests/llamacpp-live/check-receipt.py" "$X/receipt-new-unpinnable.json"; echo "new_gate_on_new_unpinnable_exit=$?"
timeout 60 python3 -B "$OLD/check-receipt-old.py" "$X/receipt-new-unpinnable.json"; echo "old_gate_on_new_unpinnable_exit=$?"

echo "== gates on the pre-existing setup-error receipt =="
timeout 60 python3 -B "$LANE/tests/llamacpp-live/check-receipt.py" "$X/receipt-old-digest-mismatch.json"; echo "new_gate_on_old_digest_mismatch_exit=$?"
timeout 60 python3 -B "$OLD/check-receipt-old.py" "$X/receipt-old-digest-mismatch.json"; echo "old_gate_on_old_digest_mismatch_exit=$?"
