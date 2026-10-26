#!/usr/bin/env bash
# X2Revision reproduction — round 47, kama. Read-only against the lane.
# Scratch is the seat's own dir; nothing is written into kama-shokunin except the
# w1/out/X2Revision evidence dir this seat owns.
set -u
S=${S:-/fast/scratch/hyaku/kama-r47/X2Revision}
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
PIN=499bc8821c6b12b4e53c5bffcb21ec206f212d81
FILE_COMMIT=96f460f9c1e2ca43d0adc1c682b832525a2c0ea3
PARENT=22027b1ab988d9d04ec83020f28c2db533985059
OLD=688f41ddf8f3622d08c6954a061ff12999b6c8d8
mkdir -p "$S"; export TMPDIR="$S"; cd "$S" || exit 1

# 1. identity of the repo revision and of the blob at the path
curl -sS https://huggingface.co/api/models/ggml-org/models-moved | python3 -c 'import json,sys; d=json.load(sys.stdin); print("main:", d["sha"], d["lastModified"])'
git ls-remote https://huggingface.co/ggml-org/models-moved
curl -sS "https://huggingface.co/api/models/ggml-org/models-moved/tree/$PIN/tinyllamas" \
  | python3 -c 'import json,sys; [print(e["path"],e["oid"],e["size"],e["lfs"]["oid"]) for e in json.load(sys.stdin) if e["path"].endswith("stories260K.gguf")]'

# 2. the pinned URL serves the same bytes (302 + x-repo-commit + x-linked-etag)
curl -sSI "https://huggingface.co/ggml-org/models-moved/resolve/$PIN/tinyllamas/stories260K.gguf" \
  | grep -iE '^(HTTP|x-repo-commit|x-linked-etag|x-linked-size)'
curl -sSL "https://huggingface.co/ggml-org/models-moved/resolve/main/tinyllamas/stories260K.gguf" -o m-main.gguf
curl -sSL "https://huggingface.co/ggml-org/models-moved/resolve/$PIN/tinyllamas/stories260K.gguf" -o m-pin.gguf
sha256sum m-main.gguf m-pin.gguf
cmp m-main.gguf m-pin.gguf && echo CMP_IDENTICAL

# 3. `main` is a moving ref: neighbours on the same path serve other bytes
for c in $FILE_COMMIT $PARENT $OLD; do
  curl -sSL "https://huggingface.co/ggml-org/models-moved/resolve/$c/tinyllamas/stories260K.gguf" -o "m-$c.gguf"
  printf '%s ' "$c"; sha256sum "m-$c.gguf" | cut -d' ' -f1
done

# 4. end-to-end: the lane's replay tool re-acquires from the recorded URL and
#    re-runs the lifecycle. Reprint each C2 receipt once with the pinned URL.
for n in 1 2 3; do
  python3 - "$n" "$PIN" <<'PY'
import json, sys
n, pin = sys.argv[1], sys.argv[2]
src = f"/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/c2/live/receipt-{n}.json"
d = json.load(open(src))
d["provenance"]["model"]["url"] = ("https://huggingface.co/ggml-org/models-moved/resolve/"
                                   f"{pin}/tinyllamas/stories260K.gguf")
json.dump(d, open(f"receipt-{n}-pinned.json", "w"), indent=1)
PY
  python3 "$LANE/tools/kama-live-replay.py" --receipt "$S/receipt-$n-pinned.json" \
    --work "$S/replay-work-$n" --out "$S/replay-pinned-$n.json"; echo "receipt-$n EXIT=$?"
done

# 5. negative control: a revision that serves different bytes must be refused,
#    not silently accepted (digest check runs before extraction).
python3 - "$PIN" "$PARENT" <<'PY'
import json, sys
pin, parent = sys.argv[1], sys.argv[2]
d = json.load(open("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/c2/live/receipt-1.json"))
d["provenance"]["model"]["url"] = ("https://huggingface.co/ggml-org/models-moved/resolve/"
                                   f"{parent}/tinyllamas/stories260K.gguf")
json.dump(d, open("receipt-1-shifted.json", "w"), indent=1)
PY
python3 "$LANE/tools/kama-live-replay.py" --receipt "$S/receipt-1-shifted.json" \
  --work "$S/replay-shifted" --out "$S/replay-shifted.json"; echo "shifted EXIT=$?"
