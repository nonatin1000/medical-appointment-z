#!/usr/bin/env bash
set -euo pipefail
cd /mnt/c/Users/nrdes/Workspace/medical-appointment-z
source ~/.pyenv/versions/3.12.13/envs/medical-appointment-z/bin/activate
python - <<'PY'
from pathlib import Path
from PIL import Image

demo = Path("docs/demo")


def make_gif(paths, out_name, durations):
    frames = [Image.open(demo / p).convert("RGB") for p in paths]
    width = min(img.width for img in frames)
    resized = []
    for img in frames:
        ratio = width / img.width
        height = int(img.height * ratio)
        resized.append(img.resize((width, height)))

    max_h = max(img.height for img in resized)
    normalized = []
    for img in resized:
        canvas = Image.new("RGB", (width, max_h), (255, 255, 255))
        canvas.paste(img, (0, 0))
        normalized.append(canvas)

    out = demo / out_name
    normalized[0].save(
        out,
        save_all=True,
        append_images=normalized[1:],
        duration=durations,
        loop=0,
        optimize=True,
    )
    print(f"created {out} ({out.stat().st_size} bytes)")


make_gif(
    [
        "swagger-01-request.png",
        "swagger-02-response.png",
        "swagger-03-response-body.png",
    ],
    "demo-swagger.gif",
    [1800, 2200, 3500],
)

make_gif(
    [
        "studio-01-graph.png",
        "studio-02-chat-input.png",
        "studio-03-chat-result.png",
    ],
    "demo-langgraph.gif",
    [1800, 2200, 3500],
)
PY
