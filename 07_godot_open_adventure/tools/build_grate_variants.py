"""Author the two CAR-ART-005 grate variants with the existing LINE/FILL compiler.

The setting is shared. Only the steel gate and the exposed opening differ.
This tool uses the approved C palette and writes no historical source data.
"""
from pathlib import Path
import argparse
import importlib.util
import json

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "godot/data/vector_ch01"
spec = importlib.util.spec_from_file_location("ch01_vector_art", HERE / "build_ch01_vector_art.py")
art = importlib.util.module_from_spec(spec)
spec.loader.exec_module(art)


def gate_bar(drawing, top_left, top_right, bottom_left, bottom_right):
    drawing.poly([top_left, top_right, bottom_right, bottom_left], "steel")


def draw_grate(opened):
    d = art.study.Drawing("C")
    d.region("M0,0 H736 V400 H0 Z", "sky", (18, 18), False)
    d.region("M0,112 Q171,67 345,103 Q532,63 736,111 V400 H0 Z", "leaf", (55, 120), False)
    d.region("M0,173 Q151,126 313,159 Q542,132 736,172 V400 H0 Z", "ground", (90, 302), False)
    # A pale, dry bed descends toward the grate. It is not a walkable route.
    d.region("M300,0 H425 Q432,91 399,142 L445,219 L340,247 L303,192 Q352,122 300,0 Z", "paper", (372,78))
    d.region("M0,231 Q86,170 197,183 L279,319 L155,400 H0 Z", "roof", (65,321), False)
    d.region("M736,224 Q638,167 535,183 L470,312 L571,400 H736 Z", "roof", (678,320), False)
    d.region("M160,202 Q363,166 567,200 L736,400 H0 Z", "ground", (350,380), False)
    d.line("M0,231 Q86,170 197,183 L252,273 M736,224 Q638,167 535,183 L495,259")
    d.line("M12,163 Q92,135 158,159 M576,159 Q666,134 724,167", True)
    for x, y, width, height in [(78,170,70,139),(166,165,51,108),(589,163,53,110),(669,174,70,145)]:
        d.tree(x, y, width, height)
    for x, y in [(81,277),(156,307),(638,296),(677,339),(268,206),(472,194)]:
        d.line(f"M{x},{y} l16,-6 l13,7 l-14,5 Z", True)

    # Concrete rim and recess use the same coordinates in both states.
    d.poly([(161,240),(549,230),(621,367),(112,367)], "steel")
    d.poly([(204,255),(521,248),(576,339),(166,339)], "deep")
    d.line("M139,356 L604,356 M181,245 L536,236", True)
    d.line("M121,374 Q364,386 610,374 M112,394 Q351,398 627,393", True)
    if opened:
        # The opening remains clear; the grille is raised on its right hinge.
        d.poly([(514,244),(538,235),(556,253),(528,263)], "roof")
        d.poly([(531,240),(571,120),(654,145),(587,285)], "steel")
        d.poly([(545,234),(578,141),(637,157),(581,264)], "ground")
        for x0, y0, x1, y1 in [(560,193,594,149),(550,225,576,167),(578,239,614,160),(595,257,631,176)]:
            gate_bar(d, (x0,y0),(x0+5,y0+2),(x1,y1),(x1+5,y1+2))
        gate_bar(d, (551,217),(556,207),(602,232),(607,221))
        d.line("M529,245 L544,232 M583,283 L603,291", True)
    else:
        # Seven perspective bars plus cross rails make the shut grate readable.
        for n in range(8):
            t = n / 7
            xt = 219 + (503-219)*t
            xb = 181 + (559-181)*t
            if n == 5:
                # Keep this diagonal off a half-pixel raster tie in Vector2.
                xt += .0625
                xb += .0625
            gate_bar(d, (xt,253),(xt+5,253),(xb,337),(xb+6,337))
        gate_bar(d, (204,279),(523,273),(197,290),(537,283))
        gate_bar(d, (180,315),(556,308),(174,326),(566,319))
        d.poly([(368,290),(390,289),(391,310),(367,310)], "roof")
        d.line("M373,296 h12 v8 h-12 Z", True)
    return d


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        OUT.mkdir(parents=True, exist_ok=True)
    for variant, opened in (("GRATE_CLOSED", False), ("GRATE_OPEN", True)):
        data = art.compile_drawing(variant, draw_grate(opened))
        data["provenance"] = "Original CAR-ART-005 / C — Línea solar; state-selected grate, human review pending."
        text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
        path = OUT / (variant.lower() + ".json")
        if args.check:
            assert path.read_text(encoding="utf-8") == text, f"Generated art drift: {path}"
        else:
            path.write_text(text, encoding="utf-8")
        print(f"{variant}: {len(data['lines'])} paths / {len(data['regions'])} regions")
    print("PASS: two state-selected grate drawings" + (" deterministic" if args.check else " compiled"))


if __name__ == "__main__":
    main()
