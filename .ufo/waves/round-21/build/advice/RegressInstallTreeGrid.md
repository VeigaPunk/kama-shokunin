VERDICT: confirm - six-pin and no-tree-pin grid results are unchanged at the assigned draft commit.

Axes: operability (gate regression behavior); calibration (agreement with round-20 recorded outputs).

Scratch clone: `/tmp/kama-r21-RegressInstallTreeGrid-6/lane`, checked out `a29bb84abbb8b4d328f5970a89e448330a3a42ac`; clone/checkout command exited 0 and printed that exact HEAD.

Commands followed round-20 `recipe.json` entries `grid-tree-pin` and `grid-no-tree-pin` (same receipt and five SHA pins; tree-pin adds `--tree-sha 6c216313a88d71b141bc62f684b8f95c040710ff050801b13521861826785a2c`):

```sh
python3 /tmp/kama-r21-RegressInstallTreeGrid-6/lane/tests/llamacpp-live/install-tree-grid.py --gate /tmp/kama-r21-RegressInstallTreeGrid-6/lane/tests/llamacpp-live/check-receipt.py --receipt /tmp/kama-r21-RegressInstallTreeGrid-6/lane/.ufo/waves/round-18/live-recovery/receipt-1.json --model-sha 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d --server-sha b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804 --impl-sha e404b91a81c9ab65756b6a57b97b42115a5f429c5060c4b7f0d717ca595b59ed --probe-sha 36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3 --tool-sha 83eac5c0489377a88c8ecead89af4ca5f057bd0463d8bf8a79467eb6c5de88c4 --json --tree-sha 6c216313a88d71b141bc62f684b8f95c040710ff050801b13521861826785a2c
```

Script exit **0****;** stdout (compact JSON, same fields/values as emitted):
```json
{"schema":"kama-install-tree-grid/v1","gate":"/tmp/kama-r21-RegressInstallTreeGrid-6/lane/tests/llamacpp-live/check-receipt.py","receipt":"/tmp/kama-r21-RegressInstallTreeGrid-6/lane/.ufo/waves/round-18/live-recovery/receipt-1.json","tree_pin":true,"baseline":"VALID","members":3,"rejected":3,"errors":0,"rows":[{"member":"libggml-base.so.0.27.0","gate_exit":1,"status":"rejected","stdout":"INVALID /tmp/install-tree-grid-ewai_jax/libggml-base.so.0.27.0.json: 1 problem(s)\n  - server.install_tree_sha256 2e52b818fe4989da622baeff150c82a2778151753aa4dc45bc8970373c09a1f9 != expected 6c216313a8","stderr":""},{"member":"libllama-common.so.0.7.0","gate_exit":1,"status":"rejected","stdout":"INVALID /tmp/install-tree-grid-ewai_jax/libllama-common.so.0.7.0.json: 1 problem(s)\n  - server.install_tree_sha256 5f6d2fd51af093db4e48256c20c9b4b614df517f87982c873e32e4293214af7b != expected 6c216313","stderr":""},{"member":"libllama.so.0.7.0","gate_exit":1,"status":"rejected","stdout":"INVALID /tmp/install-tree-grid-ewai_jax/libllama.so.0.7.0.json: 1 problem(s)\n  - server.install_tree_sha256 486c924d9bb63626a363c9d185139a158fef2dc4c32f15d8196b2a334645a20b != expected 6c216313a88d71b","stderr":""}]}
```

```sh
python3 /tmp/kama-r21-RegressInstallTreeGrid-6/lane/tests/llamacpp-live/install-tree-grid.py --gate /tmp/kama-r21-RegressInstallTreeGrid-6/lane/tests/llamacpp-live/check-receipt.py --receipt /tmp/kama-r21-RegressInstallTreeGrid-6/lane/.ufo/waves/round-18/live-recovery/receipt-1.json --model-sha 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d --server-sha b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804 --impl-sha e404b91a81c9ab65756b6a57b97b42115a5f429c5060c4b7f0d717ca595b59ed --probe-sha 36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3 --tool-sha 83eac5c0489377a88c8ecead89af4ca5f057bd0463d8bf8a79467eb6c5de88c4 --json
```

Script exit **1** (round-20 recipe expected 1); stdout (compact JSON, same fields/values as emitted):
```json
{"schema":"kama-install-tree-grid/v1","gate":"/tmp/kama-r21-RegressInstallTreeGrid-6/lane/tests/llamacpp-live/check-receipt.py","receipt":"/tmp/kama-r21-RegressInstallTreeGrid-6/lane/.ufo/waves/round-18/live-recovery/receipt-1.json","tree_pin":false,"baseline":"VALID","members":3,"rejected":0,"errors":0,"rows":[{"member":"libggml-base.so.0.27.0","gate_exit":0,"status":"accepted","stdout":"VALID /tmp/install-tree-grid-6e588yz3/libggml-base.so.0.27.0.json","stderr":""},{"member":"libllama-common.so.0.7.0","gate_exit":0,"status":"accepted","stdout":"VALID /tmp/install-tree-grid-6e588yz3/libllama-common.so.0.7.0.json","stderr":""},{"member":"libllama.so.0.7.0","gate_exit":0,"status":"accepted","stdout":"VALID /tmp/install-tree-grid-6e588yz3/libllama.so.0.7.0.json","stderr":""}]}
```

Comparison evidence read from round-20 `runs/9add96e4/grid-tree-pin.stdout` and `grid-no-tree-pin.stdout`: same `members=3`, `rejected=3/0`, `errors=0`, with the same three members rejected/accepted respectively. Round-20 recipe records expected command exits `0/1`; observed script exits are `0/1`. No install/update performed. Scratch was removed after the runs.
