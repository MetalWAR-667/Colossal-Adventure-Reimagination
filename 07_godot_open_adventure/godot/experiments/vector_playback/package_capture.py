"""Optional review packaging of actual Godot captures (installed Pillow only).
Not used by the game, the renderer, or the tests. No frames feed playback.
Usage: python package_capture.py <raw capture folder> <evidence folder>
"""
from pathlib import Path
import json
import shutil
import sys
from PIL import Image, ImageDraw


def package(source, target):
    target.mkdir(parents=True, exist_ok=True)
    metrics = json.loads((source / "metrics.json").read_text(encoding="utf-8"))
    frames = [Image.open(source / s["file"]).convert("RGB") for s in metrics["samples"]]
    final = Image.open(source / "final.png").convert("RGB")
    palette = final.quantize(colors=256)
    indexed = [frame.quantize(palette=palette) for frame in frames + [final]]
    times = [s["elapsed"] for s in metrics["samples"]] + [metrics["target_seconds"]]
    durations = [max(10, round((b-a)*100)*10) for a, b in zip(times, times[1:])] + [1500]
    indexed[0].save(target / "playback.gif", save_all=True, append_images=indexed[1:],
                    duration=durations, loop=0, optimize=False, disposal=2)
    sheet = Image.new("RGB", (1280, 1260), "#ece9df")
    draw = ImageDraw.Draw(sheet)
    for position, index in enumerate([8, 14, 21, 23, 29, len(frames)]):
        frame = final if index == len(frames) else frames[index]
        elapsed = metrics["target_seconds"] if index == len(frames) else times[index]
        x, y = (position % 2)*640, (position//2)*420
        sheet.paste(frame, (x, y+20))
        draw.text((x+8, y+4), f"Godot actual capture / t={elapsed:.3f}s", fill="#263b38")
    sheet.save(target / "contact_sheet.png")
    shutil.copy2(source / "final.png", target / "final.png")
    metrics["sample_elapsed_seconds"] = [s["elapsed"] for s in metrics.pop("samples")]
    metrics["review_artifact"] = "playback.gif: sampled actual playback; GIF quantization and final hold, not timing/pixel proof"
    (target / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(f"Packaged {len(frames)} actual frames plus final; metrics, GIF and contact sheet.")


if __name__ == "__main__":
    package(Path(sys.argv[1]), Path(sys.argv[2]))
