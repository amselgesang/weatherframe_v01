"""Render preview PNGs of the enclosure (matplotlib, no GPU needed)."""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import cadquery as cq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_cadquery import build  # noqa: E402


def tess(body, tol=0.3):
    verts, tris = body.val().tessellate(tol, 0.3)
    v = np.array([(p.x, p.y, p.z) for p in verts])
    t = np.array(tris)
    return v, t


def shade(ax, v, t, light, color, flip=False):
    # simple Lambert shading, painter's algorithm along the view axis
    tri = v[t]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    nn = np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
    n = n / nn
    if flip:
        n = -n
    lam = np.clip(n @ light, 0, 1) * 0.7 + 0.3
    return tri, lam


def view(bodies, names, axis, sign, fname, title, section_z=None, xlim=None, ylim=None):
    """Orthographic view along `axis` ('z' or 'y'), looking in direction `sign`."""
    fig, ax = plt.subplots(figsize=(11, 8), dpi=110)
    polys = []
    for name in names:
        b = bodies[name]
        if section_z is not None:
            d = -section_z  # keep material below section_z (z < section_z)
            cutter = cq.Workplane("XY").box(400, 400, 100, centered=(True, True, False)).translate((0, 0, section_z))
            b = b.cut(cutter)
        v, t = tess(b)
        tri = v[t]
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
        if axis == "z":
            light = np.array([0.3, 0.4, sign * 0.85])
            depth = tri[:, :, 2].mean(axis=1) * sign
            xy = tri[:, :, :2]
            if sign < 0:
                xy = xy * np.array([-1, 1])  # looking from behind: mirror X
        else:  # axis y: look from -y (front-bottom section)
            light = np.array([0.3, sign * 0.85, 0.4])
            depth = tri[:, :, 1].mean(axis=1) * sign
            xy = tri[:, :, [0, 2]]
        lam = np.abs(n @ light) * 0.75 + 0.25
        col = np.array(COL[name])
        alpha = 0.35 if name.startswith("ref_") else 1.0
        for k in range(len(tri)):
            polys.append((depth[k], xy[k], (*(col * lam[k]), alpha)))
    polys.sort(key=lambda p: p[0])
    from matplotlib.collections import PolyCollection
    pc = PolyCollection([p[1] for p in polys], facecolors=[p[2] for p in polys], edgecolors=(0, 0, 0, 0.15), linewidths=0.3)
    ax.add_collection(pc)
    ax.set_aspect("equal")
    ax.autoscale()
    if xlim:
        ax.set_xlim(*xlim)
    if ylim:
        ax.set_ylim(*ylim)
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(fname)
    plt.close(fig)
    print("wrote", fname)


COL = {"bezel": (0.86, 0.86, 0.84), "back": (0.62, 0.64, 0.66), "ref_panel": (0.97, 0.97, 0.93),
       "ref_pcb": (0.15, 0.45, 0.25), "ref_hat": (0.15, 0.25, 0.6), "ref_battery": (0.75, 0.72, 0.3)}

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "out"
    d, bodies = build()
    view(bodies, ["bezel", "ref_panel"], "z", +1, f"{out}/view_front.png", "Front (bezel + panel)")
    view(bodies, ["back", "ref_pcb", "ref_hat", "ref_battery"], "z", +1, f"{out}/view_inside_back.png",
         "Back plate seen from the front (inside): PCB green, HAT blue, battery yellow")
    view(bodies, ["back"], "z", -1, f"{out}/view_rear.png", "Rear face (keyholes, screw counterbores, buttons, vents, MAINT slot)")
    view(bodies, ["bezel", "ref_panel", "ref_hat", "ref_pcb", "ref_battery"], "z", -1, f"{out}/view_bezel_inside.png",
         "Bezel seen from behind (mirrored): recess, bosses, USB-C cut; electronics for reference")
