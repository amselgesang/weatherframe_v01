"""Export JLCPCB fabrication + assembly files into ../fab/ using kicad-cli.

  python3 export_fab.py

Produces:
  fab/weatherframe_gerbers.zip   upload as "Gerber file"
  fab/bom_jlc.csv                PCB Assembly -> BOM   (Comment, Designator, Footprint, LCSC Part #)
  fab/cpl_jlc.csv                PCB Assembly -> CPL   (Designator, Mid X, Mid Y, Layer, Rotation)
"""
import csv
import os
import shutil
import subprocess
import sys
import zipfile
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from design import PARTS  # noqa: E402

KICAD_CLI = os.environ.get("KICAD_CLI", "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
PRJ = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
PCB = os.path.join(PRJ, "weatherframe.kicad_pcb")
FAB = os.path.join(PRJ, "fab")
TMP = os.path.join(PRJ, "build", "fab_tmp")

LAYERS = "F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts"


def cli(*args):
    r = subprocess.run([KICAD_CLI, *args], capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stdout + r.stderr)
        raise SystemExit(f"kicad-cli {' '.join(args[:3])} failed")


def gerbers():
    shutil.rmtree(TMP, ignore_errors=True)
    os.makedirs(TMP)
    cli("pcb", "export", "gerbers", "--layers", LAYERS, "--subtract-soldermask", "--no-x2", "-o", TMP + "/", PCB)
    cli("pcb", "export", "drill", "--format", "excellon", "--drill-origin", "absolute", "--excellon-units", "mm",
        "--excellon-oval-format", "alternate", "-o", TMP + "/", PCB)
    out = os.path.join(FAB, "weatherframe_gerbers.zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir(TMP)):
            z.write(os.path.join(TMP, f), f)
    print("gerbers:", out, len(os.listdir(TMP)), "files")


def bom():
    groups = OrderedDict()
    for p in PARTS:
        if not p.get("lcsc"):
            continue  # hand-soldered / mechanical
        key = (p["value"], p["fp"].split(":")[1], p["lcsc"])
        groups.setdefault(key, []).append(p["ref"])
    out = os.path.join(FAB, "bom_jlc.csv")
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
        for (val, fp, lcsc), refs in groups.items():
            w.writerow([val, ",".join(refs), fp, lcsc])
    print("bom:", out, len(groups), "lines")


def cpl():
    raw = os.path.join(TMP, "pos.csv")
    cli("pcb", "export", "pos", "--side", "both", "--format", "csv", "--units", "mm", "--smd-only",
        "--exclude-dnp", "-o", raw, PCB)
    assembled = {p["ref"] for p in PARTS if p.get("lcsc")}
    out = os.path.join(FAB, "cpl_jlc.csv")
    n = 0
    with open(raw) as fi, open(out, "w", newline="") as fo:
        w = csv.writer(fo)
        w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
        for row in csv.DictReader(fi):
            if row["Ref"] not in assembled:
                continue
            w.writerow([row["Ref"], row["PosX"] + "mm", row["PosY"] + "mm",
                        "Top" if row["Side"] == "top" else "Bottom", row["Rot"]])
            n += 1
    missing = assembled - {r for r in assembled}
    print("cpl:", out, n, "placements", "(missing: %s)" % missing if missing else "")


if __name__ == "__main__":
    os.makedirs(FAB, exist_ok=True)
    gerbers()
    bom()
    cpl()
