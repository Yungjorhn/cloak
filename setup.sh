#!/usr/bin/env bash
# One-time setup: install libraries, fetch Leffa source code and only the
# checkpoints CLOAK needs (skips the large pose-transfer / SDXL weights).
set -euo pipefail
cd "$(dirname "$0")"

LEFFA_COMMIT=05a259104b6927607776c7edb3e86b75406f20aa   # pinned for reproducibility

echo "==> Installing Python libraries"
pip install -q -r requirements.txt

echo "==> Fetching Leffa source (MIT) at commit ${LEFFA_COMMIT:0:7}"
mkdir -p third_party
if [ ! -d third_party/Leffa/.git ]; then
  git clone -q https://github.com/franciszzj/Leffa.git third_party/Leffa
fi
git -C third_party/Leffa fetch -q --depth 1 origin "$LEFFA_COMMIT" || true
git -C third_party/Leffa checkout -q "$LEFFA_COMMIT"

echo "==> Downloading model checkpoints from Hugging Face (a few GB, first time only)"
python - <<'EOF'
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id="franciszzj/Leffa",
    local_dir="./ckpts",
    allow_patterns=[
        "virtual_tryon.pth",            # Leffa try-on model trained on VITON-HD (tops)
        "virtual_tryon_dc.pth",         # Leffa try-on model trained on DressCode (tops, bottoms, dresses)
        "stable-diffusion-inpainting/*",  # base architecture configs
        "humanparsing/*",               # body-part segmentation (ONNX)
        "openpose/*",                   # body keypoints
        "densepose/*",                  # body surface map
        "examples/*",                   # sample people and garments for quick testing
    ],
)
print("Checkpoints ready in ./ckpts")
EOF

echo "==> Setup complete. Start the app with:  python app.py"
