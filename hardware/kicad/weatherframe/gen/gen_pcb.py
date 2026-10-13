"""Generate / finish weatherframe.kicad_pcb from design.py using KiCad's pcbnew module.

Run with KiCad's bundled Python (see build.sh):
  python gen_pcb.py place    -> board with outline, footprints, nets; exports weatherframe.dsn
  (Freerouting: weatherframe.dsn -> weatherframe.ses)
  python gen_pcb.py finish   -> imports the .ses, adds GND pours + silkscreen, saves the board
"""
import json
import os
import sys
import uuid

import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from design import BOARD_H, BOARD_W, PARTS  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PRJ = os.path.normpath(os.path.join(HERE, ".."))
PCB = os.path.join(PRJ, "weatherframe.kicad_pcb")
DSN = os.path.join(PRJ, "build", "weatherframe.dsn")
SES = os.path.join(PRJ, "build", "weatherframe.ses")
PLACED = os.path.join(PRJ, "build", "weatherframe_placed.kicad_pcb")
FPLIB = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"
NS = uuid.UUID("6f1d0c1e-8f3c-4a39-9b6e-57ef0a1b2c3d")  # same namespace as gen_sch.py

POWER_NETS = ["VBUS", "VSYS", "VBAT", "+3V3", "SW1", "SW2", "EPD_VCC"]
# SHT40 corner: thermal slot from the top edge, no copper pour around the sensor.
TAB_W, TAB_H = 10.5, 9.0
SLOT = 1.0
SLOT_DEPTH = 8.0


def mm(v):
    return pcbnew.FromMM(v)


def pt(x, y):
    return pcbnew.VECTOR2I(mm(x), mm(y))


def sym_uuid(ref):
    return str(uuid.uuid5(NS, "sym/" + ref))


def edge_poly(board, pts):
    for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(pt(x1, y1))
        s.SetEnd(pt(x2, y2))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(mm(0.1))
        board.Add(s)


def build_outline(board):
    """Rectangle with a 1 mm slot cut in from the top edge beside the SHT40 corner.

    The slot (and the no-pour area around the sensor) keeps regulator / MCU heat away from it.
    """
    W, H = BOARD_W, BOARD_H
    x0, x1 = TAB_W, TAB_W + SLOT
    edge_poly(board, [(0, 0), (x0, 0), (x0, SLOT_DEPTH), (x1, SLOT_DEPTH), (x1, 0), (W, 0), (W, H), (0, H)])


def setup_rules(board):
    ds = board.GetDesignSettings()
    ds.SetCopperLayerCount(2)
    ds.m_MinClearance = mm(0.15)
    ds.m_TrackMinWidth = mm(0.15)
    ds.m_ViasMinSize = mm(0.5)
    ds.m_MinThroughDrill = mm(0.2)  # ESP32 footprint thermal vias; JLCPCB min 0.2 mm
    ds.m_CopperEdgeClearance = mm(0.3)
    ds.m_HoleClearance = mm(0.25)
    ns = ds.m_NetSettings
    dflt = ns.GetDefaultNetclass()
    dflt.SetClearance(mm(0.15))
    dflt.SetTrackWidth(mm(0.2))
    dflt.SetViaDiameter(mm(0.6))
    dflt.SetViaDrill(mm(0.3))
    pwr = pcbnew.NETCLASS("Power")
    pwr.SetClearance(mm(0.15))
    pwr.SetTrackWidth(mm(0.35))
    pwr.SetViaDiameter(mm(0.7))
    pwr.SetViaDrill(mm(0.35))
    ns.SetNetclass("Power", pwr)
    for n in POWER_NETS:
        ns.SetNetclassPatternAssignment(n, "Power")


def write_project_netclasses():
    """Persist the same netclasses in the .kicad_pro (KiCad keeps them there, not in the board)."""
    path = os.path.join(PRJ, "weatherframe.kicad_pro")
    prj = json.load(open(path))
    prj.setdefault("meta", {})["filename"] = "weatherframe.kicad_pro"
    common = {"bus_width": 12, "diff_pair_gap": 0.25, "diff_pair_via_gap": 0.25, "diff_pair_width": 0.2,
              "line_style": 0, "microvia_diameter": 0.3, "microvia_drill": 0.1, "pcb_color": "rgba(0, 0, 0, 0.000)",
              "schematic_color": "rgba(0, 0, 0, 0.000)", "wire_width": 6}
    prj["net_settings"] = {
        "classes": [
            dict(common, name="Default", clearance=0.15, track_width=0.2, via_diameter=0.6, via_drill=0.3, priority=2147483647),
            dict(common, name="Power", clearance=0.15, track_width=0.35, via_diameter=0.7, via_drill=0.35, priority=0),
        ],
        "meta": {"version": 4},
        "net_colors": None,
        "netclass_assignments": None,
        "netclass_patterns": [{"netclass": "Power", "pattern": n} for n in POWER_NETS],
    }
    brd = prj.setdefault("board", {}).setdefault("design_settings", {})
    rules = brd.setdefault("rules", {})
    rules.update({"min_clearance": 0.15, "min_track_width": 0.15, "min_via_diameter": 0.5,
                  "min_through_hole_diameter": 0.2, "min_copper_edge_clearance": 0.3, "min_hole_clearance": 0.25})
    json.dump(prj, open(path, "w"), indent=2)


def place(board):
    nets = {}

    def net(name):
        if name not in nets:
            n = pcbnew.NETINFO_ITEM(board, name)
            board.Add(n)
            nets[name] = n
        return nets[name]

    for p in PARTS:
        lib, name = p["fp"].split(":")
        fp = pcbnew.FootprintLoad(os.path.join(FPLIB, lib + ".pretty"), name)
        if fp is None:
            raise SystemExit("footprint not found: " + p["fp"])
        fp.SetReference(p["ref"])
        fp.SetValue(p["value"])
        fp.SetFPID(pcbnew.LIB_ID(lib, name))
        if p["ref"] == "U4":
            # The library keepout covers the pad centres, which autorouters connect to.
            # The board-level "sensor_tab_no_pour" rule area keeps copper pour away instead.
            for z in list(fp.Zones()):
                fp.Remove(z)
        x, y, r, side = p["pcb"]
        board.Add(fp)
        if side == "B":
            fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_TOP_BOTTOM)
        fp.SetPosition(pt(x, y))
        fp.SetOrientationDegrees(r)
        # Dense board: keep reference designators on the fab layer (assembly drawing), not silkscreen.
        fp.Reference().SetLayer(pcbnew.B_Fab if side == "B" else pcbnew.F_Fab)
        if p["pins"]:  # symbol-backed part: link to schematic
            fp.SetPath(pcbnew.KIID_PATH("/" + sym_uuid(p["ref"])))
            fp.SetSheetfile("weatherframe.kicad_sch")
            fp.SetSheetname("/")
        for key in ("lcsc", "mpn"):
            if p.get(key):
                fp.SetField(key.upper(), p[key])
                field = fp.GetField(key.upper())
                field.SetVisible(False)
                field.SetLayer(pcbnew.F_Fab)
        for pad in fp.Pads():
            n = p["pins"].get(pad.GetNumber())
            if n:
                pad.SetNet(net(n))
        # mounting-pad / shield pads of connectors and switches
        if p["ref"] in ("SW4",):
            for pad in fp.Pads():
                if pad.GetNumber() == "SH":
                    pad.SetNet(net("GND"))
    return nets


def add_silk(board):
    def text(s, x, y, size=1.0, layer=pcbnew.F_SilkS, angle=0):
        t = pcbnew.PCB_TEXT(board)
        t.SetText(s)
        t.SetPosition(pt(x, y))
        t.SetLayer(layer)
        t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
        t.SetTextThickness(mm(size * 0.15))
        t.SetTextAngleDegrees(angle)
        t.SetMirrored(layer == pcbnew.B_SilkS)
        board.Add(t)

    text("WEATHER FRAME r1", 46, 23.5, 1.2)
    text("LiPo +", 9.5, 21.5, 0.8)
    text("VCC GND DIN CLK CS DC RST BUSY PWR", 45.2, 45.3, 0.8)
    text("MAINT", 60.5, 28.2, 0.8)
    text("SHT40", 5.5, 10.0, 0.8)
    text("WEATHER FRAME r1 - ESP32-S3 / MCP73831 / TPS63001", 32, 23, 1.0, layer=pcbnew.B_SilkS)


def add_zones(board, nets):
    W, H = BOARD_W, BOARD_H
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        z = pcbnew.ZONE(board)
        z.SetLayer(layer)
        z.SetNet(nets["GND"])
        z.SetAssignedPriority(0)
        z.SetLocalClearance(mm(0.25))
        z.SetMinThickness(mm(0.2))
        z.SetThermalReliefGap(mm(0.3))
        z.SetThermalReliefSpokeWidth(mm(0.4))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        ol = z.Outline()
        ol.NewOutline()
        for x, y in [(0, 0), (W, 0), (W, H), (0, H)]:
            ol.Append(mm(x), mm(y))
        board.Add(z)
    # No copper pour on the sensor tab or its bridge: keeps regulator/MCU heat away from the SHT40.
    ka = pcbnew.ZONE(board)
    ka.SetIsRuleArea(True)
    ka.SetDoNotAllowZoneFills(True)
    ka.SetDoNotAllowTracks(False)
    ka.SetDoNotAllowVias(False)
    ka.SetDoNotAllowPads(False)
    ka.SetDoNotAllowFootprints(False)
    ka.SetLayerSet(pcbnew.LSET.AllCuMask())
    ka.SetZoneName("sensor_tab_no_pour")
    ol = ka.Outline()
    ol.NewOutline()
    for x, y in [(0, 0), (TAB_W, 0), (TAB_W, TAB_H), (0, TAB_H)]:
        ol.Append(mm(x), mm(y))
    board.Add(ka)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())


def prune_dangling_gnd(board):
    """Delete GND track segments left with a free end (the pour connects GND pads anyway)."""
    while True:
        tracks = [t for t in board.GetTracks() if t.GetClass() == "PCB_TRACK"]
        vias = [t for t in board.GetTracks() if t.GetClass() == "PCB_VIA"]
        pads = [p for fp in board.GetFootprints() for p in fp.Pads()]
        dead = []
        for tr in tracks:
            if tr.GetNetname() != "GND":
                continue
            for end in (tr.GetStart(), tr.GetEnd()):
                hit = any(p.HitTest(end) and p.IsOnLayer(tr.GetLayer()) for p in pads if p.GetNetname() == "GND")
                hit = hit or any(v.GetPosition() == end for v in vias)
                hit = hit or any(o is not tr and o.GetLayer() == tr.GetLayer() and end in (o.GetStart(), o.GetEnd())
                                 for o in tracks)
                if not hit:
                    dead.append(tr)
                    break
        if not dead:
            return
        for tr in dead:
            board.Delete(tr)


def stage_place():
    board = pcbnew.NewBoard(PCB)
    setup_rules(board)
    write_project_netclasses()
    build_outline(board)
    place(board)
    board.Save(PCB)
    os.makedirs(os.path.dirname(DSN), exist_ok=True)
    board.Save(PLACED)
    ok = pcbnew.ExportSpecctraDSN(board, DSN)
    print("placed", len(PARTS), "footprints; DSN export:", ok, DSN)


def stage_finish():
    board = pcbnew.LoadBoard(PLACED)  # always start from the unrouted board
    setup_rules(board)
    ok = pcbnew.ImportSpecctraSES(board, SES)
    print("SES import:", ok)
    # Freerouting occasionally necks short GND stubs below the board minimum; the GND pours
    # make those connections anyway, so drop the stubs.
    for tr in list(board.GetTracks()):
        if tr.GetClass() == "PCB_TRACK" and tr.GetWidth() < mm(0.15):
            if tr.GetNetname() != "GND":
                raise SystemExit(f"narrow track on {tr.GetNetname()}: fix placement and re-route")
            board.Delete(tr)
    prune_dangling_gnd(board)
    add_zones(board, {"GND": board.FindNet("GND")})
    add_silk(board)
    board.Save(PCB)
    print("saved", PCB)


if __name__ == "__main__":
    {"place": stage_place, "finish": stage_finish}[sys.argv[1]]()
