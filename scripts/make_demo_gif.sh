#!/usr/bin/env bash
set -euo pipefail
cd /mnt/c/Users/nrdes/Workspace/medical-appointment-z
source ~/.pyenv/versions/3.12.13/envs/medical-appointment-z/bin/activate
python - <<'PY'
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    import subprocess
    subprocess.check_call(["pip", "install", "pillow"])
    from PIL import Image

demo = Path("docs/demo")
frames = [
    Image.open(demo / "01-docs.png").convert("RGB"),
    Image.open(demo / "02-request.png").convert("RGB"),
    Image.open(demo / "03-response.png").convert("RGB"),
]

# Normalize sizes to the first frame width
width = min(img.width for img in frames)
resized = []
for img in frames:
    ratio = width / img.width
    height = int(img.height * ratio)
    resized.append(img.resize((width, height)))

# Crop tall response frame to a readable viewport-like height
max_h = max(resized[0].height, resized[1].height)
cropped = []
for img in resized:
    if img.height > max_h + 200:
        img = img.crop((0, 0, img.width, max_h + 200))
    cropped.append(img)

out = demo / "demo.gif"
cropped[0].save(
    out,
    save_all=True,
    append_images=cropped[1:],
    duration=[1800, 2200, 3200],
    loop=0,
    optimize=True,
)
print(f"created {out} ({out.stat().st_size} bytes)")
PY
