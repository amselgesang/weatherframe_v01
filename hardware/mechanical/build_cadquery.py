"""Build the weather-frame enclosure with CadQuery and export STEP / STL / previews.

  python3 build_cadquery.py [outdir]

Outputs (per printed part):  bezel.step / bezel.stl, back.step / back.stl,
plus weatherframe_assembly.step (both parts + reference bodies) and preview PNGs.
"""
import os
import sys

import cadquery as cq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from frame_geom import primitives  # noqa: E402


def solid_for(op):
    kind = op[1]
    if kind == "box":
        x0, y0, x1, y1, z0, z1 = op[3:9]
        return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))
    if kind == "rbox":
        x0, y0, x1, y1, z0, z1, r = op[3:10]
        w = cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))
        return w.edges("|Z").fillet(r)
    if kind == "cyl":
        cx, cy, r, z0, z1 = op[3:8]
        return cq.Workplane("XY").circle(r).extrude(z1 - z0).translate((cx, cy, z0))
    if kind == "slot":
        cx, cy, l, w, z0, z1, ang = op[3:10]
        return cq.Workplane("XY").slot2D(l, w, ang).extrude(z1 - z0).translate((cx, cy, z0))
    if kind == "xcyl":
        cy, cz, r, x0, x1 = op[3:8]
        return cq.Workplane("YZ").circle(r).extrude(x1 - x0).translate((x0, cy, cz))
    if kind == "text":
        cx, cy, z0, size, depth, txt = op[3:9]
        pl = cq.Plane(origin=(cx, cy, z0), xDir=(-1, 0, 0), normal=(0, 0, -1))   # reads correctly from behind
        return cq.Workplane(pl).text(txt, size, -(depth + 0.01), kind="bold", halign="center", valign="center",
                                     font="Liberation Sans", combine=False)
    raise ValueError(kind)


def build():
    d, ops = primitives()
    bodies = {}
    for op in ops:
        body, kind, mode = op[0], op[1], op[2]
        if kind == "chamfer_window":
            # chamfer the front edges of the window opening
            b = bodies[body]
            sel = b.faces(">Z").edges(cq.selectors.BoxSelector(
                (-d["window_w"] / 2 - 0.5, -d["window_h"] / 2 - 0.5, -0.5),
                (d["window_w"] / 2 + 0.5, d["window_h"] / 2 + 0.5, 0.5)))
            bodies[body] = sel.chamfer(op[3])
            continue
        s = solid_for(op)
        if body not in bodies:
            bodies[body] = s
        elif mode == "join":
            bodies[body] = bodies[body].union(s)
        else:
            bodies[body] = bodies[body].cut(s)
    return d, bodies


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "out"
    os.makedirs(out, exist_ok=True)
    d, bodies = build()
    for name in ("bezel", "back", "stand"):
        b = bodies[name]
        cq.exporters.export(b, os.path.join(out, f"{name}.step"))
        cq.exporters.export(b, os.path.join(out, f"{name}.stl"), tolerance=0.05, angularTolerance=0.1)
        bb = b.val().BoundingBox()
        print(f"{name}: {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm, volume {b.val().Volume()/1000:.1f} cm3")
    asm = cq.Assembly()
    colors = {"stand": (0.7, 0.7, 0.7), "bezel": (0.85, 0.85, 0.82), "back": (0.6, 0.6, 0.6), "ref_panel": (0.95, 0.95, 0.9),
              "ref_pcb": (0.1, 0.4, 0.2), "ref_hat": (0.1, 0.2, 0.5), "ref_battery": (0.7, 0.7, 0.3)}
    for name, b in bodies.items():
        asm.add(b, name=name, color=cq.Color(*colors.get(name, (0.5, 0.5, 0.5))))
    asm.save(os.path.join(out, "weatherframe_assembly.step"))
    # interference checks between printed parts and reference bodies
    for a in ("bezel", "back", "stand"):
        for r in ("ref_panel", "ref_pcb", "ref_hat", "ref_battery"):
            v = bodies[a].intersect(bodies[r]).val().Volume() if bodies[a].intersect(bodies[r]).vals() else 0
            if v > 1e-3:
                print(f"  INTERFERENCE {a} x {r}: {v:.2f} mm3")
    v = bodies["bezel"].intersect(bodies["back"])
    vv = v.val().Volume() if v.vals() else 0
    print(f"bezel x back overlap: {vv:.2f} mm3 (expected 0)")
    print("total thickness %.1f mm, outer %.1f x %.1f mm" % (d["total_t"], d["outer_w"], d["outer_h"]))


if __name__ == "__main__":
    main()
