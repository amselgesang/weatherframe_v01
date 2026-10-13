"""Generate weatherframe.kicad_sch from design.py.

Every pin gets a short wire stub and a net label (or a no-connect flag), so the
schematic is fully label-connected. Run with any Python 3:  python3 gen_sch.py
"""
import copy
import math
import os
import uuid

from design import PARTS, PWR_FLAGS
from sexpr import Sym, dump, find, find1, parse

LIBDIR = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "weatherframe.kicad_sch")
PROJECT = "weatherframe"
# Stable UUIDs so regenerating keeps KiCad's sch<->pcb links intact.
NS = uuid.UUID("6f1d0c1e-8f3c-4a39-9b6e-57ef0a1b2c3d")
ROOT = str(uuid.uuid5(NS, "root"))


def uid(*key):
    return str(uuid.uuid5(NS, "/".join(map(str, key))))


_lib_cache = {}


def lib_symbols(lib):
    if lib not in _lib_cache:
        tree = parse(open(os.path.join(LIBDIR, lib + ".kicad_sym"), encoding="utf-8").read())
        _lib_cache[lib] = {s[1]: s for s in find(tree, "symbol")}
    return _lib_cache[lib]


def flat_symbol(lib_id):
    """Return the library symbol, flattened if it `extends` another, named 'Lib:Name'."""
    lib, name = lib_id.split(":")
    syms = lib_symbols(lib)
    sym = syms[name]
    ext = find1(sym, "extends")
    if ext:
        base = copy.deepcopy(syms[ext[1]])
        props = find(sym, "property")
        base = [x for x in base if not (isinstance(x, list) and x and x[0] == "property")]
        # insert derived properties after the header atoms
        head = [x for x in base if not isinstance(x, list) or x[0] not in ("symbol", "embedded_fonts")]
        tail = [x for x in base if isinstance(x, list) and x[0] in ("symbol", "embedded_fonts")]
        for sub in tail:
            if sub[0] == "symbol":
                sub[1] = sub[1].replace(ext[1] + "_", name + "_", 1)
        sym = head + copy.deepcopy(props) + tail
    else:
        sym = copy.deepcopy(sym)
    sym[1] = lib_id
    return sym


def pins_of(sym):
    out = []

    def walk(node):
        for x in node:
            if isinstance(x, list) and x:
                if x[0] == "pin":
                    at = find1(x, "at")
                    out.append(dict(num=find1(x, "number")[1], name=find1(x, "name")[1],
                                    x=float(at[1]), y=float(at[2]), a=float(at[3]) if len(at) > 3 else 0.0))
                else:
                    walk(x)

    walk(sym)
    return out


def rot(px, py, a):
    r = math.radians(a)
    return px * math.cos(r) - py * math.sin(r), px * math.sin(r) + py * math.cos(r)


def snap(v):
    return round(v / 1.27) * 1.27


def font(size=1.27):
    return [Sym("font"), [Sym("size"), size, size]]


def prop(name, value, x, y, hide=False, justify=None, angle=0):
    eff = [Sym("effects"), font()]
    if justify:
        eff.append([Sym("justify"), Sym(justify)])
    if hide:
        eff.append([Sym("hide"), Sym("yes")])
    return [Sym("property"), name, value, [Sym("at"), x, y, angle], eff]


items = []
lib_ids = {}


def place_symbol(ref, lib_id, value, fp, x, y, a=0, fields=None, pin_nets=None, in_bom=True, on_board=True):
    sym = flat_symbol(lib_id)
    lib_ids[lib_id] = sym
    pins = pins_of(sym)
    xs = [x + rot(p["x"], p["y"], a)[0] for p in pins] or [x]
    ys = [y - rot(p["x"], p["y"], a)[1] for p in pins] or [y]
    top, right = min(ys), max(xs)
    big = len(pins) > 3
    horizontal = not big and all(abs(yy - y) < 0.01 for yy in ys)
    if big:  # above the body, offset sideways from any top pin label
        ref_at, val_at, just = (snap(x + 5.08), snap(top - 6.35)), (snap(x + 5.08), snap(top - 3.81)), "left"
    elif horizontal:  # two-terminal part lying flat: text above it
        ref_at, val_at, just = (x, y - 5.08), (x, y - 2.54), None
    else:
        ref_at, val_at, just = (snap(right + 2.54), y - 1.27), (snap(right + 2.54), y + 1.27), "left"
    node = [Sym("symbol"), [Sym("lib_id"), lib_id], [Sym("at"), x, y, a], [Sym("unit"), 1],
            [Sym("exclude_from_sim"), Sym("no")], [Sym("in_bom"), Sym("yes" if in_bom else "no")],
            [Sym("on_board"), Sym("yes" if on_board else "no")], [Sym("dnp"), Sym("no")],
            [Sym("uuid"), uid("sym", ref)],
            prop("Reference", ref, *ref_at, justify=just),
            prop("Value", value, *val_at, justify=just),
            prop("Footprint", fp or "", x, y, hide=True),
            prop("Datasheet", "", x, y, hide=True)]
    for k, v in (fields or {}).items():
        node.append(prop(k, v, x, y, hide=True))
    seen = set()
    for p in pins:
        node.append([Sym("pin"), p["num"], [Sym("uuid"), uid("pin", ref, p["num"])]])
    node.append([Sym("instances"), [Sym("project"), PROJECT,
                                    [Sym("path"), "/" + ROOT, [Sym("reference"), ref], [Sym("unit"), 1]]]])
    items.append(node)

    # wire stubs + labels
    for p in pins:
        dx, dy = rot(p["x"], p["y"], a)
        cx, cy = round(x + dx, 2), round(y - dy, 2)
        if (cx, cy) in seen:
            continue
        seen.add((cx, cy))
        if pin_nets is None:
            continue
        if p["num"] not in pin_nets:
            raise SystemExit(f"{ref}: pin {p['num']} ({p['name']}) has no net assigned")
        net = pin_nets[p["num"]]
        if net is None:
            items.append([Sym("no_connect"), [Sym("at"), cx, cy], [Sym("uuid"), uid("nc", ref, p["num"])]])
            continue
        # outward direction = opposite of the pin's direction (screen coords, y down)
        pa = (p["a"] + a) % 360
        ox, oy = {0: (-1, 0), 180: (1, 0), 90: (0, 1), 270: (0, -1)}[int(round(pa)) % 360]
        ex, ey = round(cx + ox * 2.54, 2), round(cy + oy * 2.54, 2)
        items.append([Sym("wire"), [Sym("pts"), [Sym("xy"), cx, cy], [Sym("xy"), ex, ey]],
                      [Sym("stroke"), [Sym("width"), 0], [Sym("type"), Sym("default")]],
                      [Sym("uuid"), uid("w", ref, p["num"])]])
        langle, just = {(-1, 0): (180, "right"), (1, 0): (0, "left"), (0, -1): (90, "left"), (0, 1): (270, "right")}[(ox, oy)]
        items.append([Sym("label"), net, [Sym("at"), ex, ey, langle], [Sym("fields_autoplaced"), Sym("yes")],
                      [Sym("effects"), font(), [Sym("justify"), Sym(just), Sym("bottom")]],
                      [Sym("uuid"), uid("lbl", ref, p["num"])]])


def text(s, x, y, size=2.54):
    items.append([Sym("text"), s, [Sym("exclude_from_sim"), Sym("no")], [Sym("at"), x, y, 0],
                  [Sym("effects"), font(size), [Sym("justify"), Sym("left"), Sym("bottom")]],
                  [Sym("uuid"), uid("text", s)]])


def main():
    for p in PARTS:
        fields = {"LCSC": p.get("lcsc", ""), "MPN": p.get("mpn", p["value"])}
        place_symbol(p["ref"], p["sym"], p["value"], p["fp"], p["pos"][0], p["pos"][1], p.get("rot", 0),
                     fields=fields, pin_nets=p["pins"])
    for i, net in enumerate(PWR_FLAGS):
        place_symbol(f"#FLG0{i + 1}", "power:PWR_FLAG", "PWR_FLAG", "", 30.48 + 15.24 * i, 236.22,
                     pin_nets={"1": net}, in_bom=False, on_board=False)

    text("USB-C input + ESD", 25.4, 38.1)
    text("LiPo charger (500 mA)", 116.84, 38.1)
    text("Battery, load sharing, sense dividers", 25.4, 116.84)
    text("3.3 V buck-boost (TPS63001)", 116.84, 116.84)
    text("ESP32-S3-WROOM-1-N16R8", 203.2, 38.1)
    text("Buttons / MAINT switch", 203.2, 152.4)
    text("SHT40 indoor sensor (isolated tab)", 327.66, 38.1)
    text("E-paper HAT power switch + 9-pin header", 314.96, 116.84)
    text("Mounting holes", 325.12, 231.14)
    text("Power flags", 25.4, 226.06)

    sch = [Sym("kicad_sch"), [Sym("version"), 20250114], [Sym("generator"), "eeschema"],
           [Sym("generator_version"), "9.0"], [Sym("uuid"), ROOT], [Sym("paper"), "A3"],
           [Sym("title_block"), [Sym("title"), "E-Paper Weather Frame - main board"], [Sym("rev"), "1"],
            [Sym("comment"), 1, "ESP32-S3 + MCP73831 + TPS63001 + SHT40, drives Waveshare 7.5in e-Paper HAT"]],
           [Sym("lib_symbols"), *lib_ids.values()],
           *items,
           [Sym("sheet_instances"), [Sym("path"), "/", [Sym("page"), "1"]]],
           [Sym("embedded_fonts"), Sym("no")]]
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(dump(sch) + "\n")
    print("wrote", os.path.normpath(OUT), len(PARTS), "parts")


if __name__ == "__main__":
    main()
