"""Weather frame enclosure — single source of truth for the mechanical design.

Everything is expressed as a flat list of CSG primitives (boxes / cylinders, join or cut)
in mm so that the same geometry can be built by:
  * build_cadquery.py   -> STEP / STL / preview PNG (CadQuery, runs anywhere)
  * frame_fusion360.py  -> the same bodies inside Autodesk Fusion 360 (Scripts & Add-Ins)

Coordinate system (front view of the frame hanging on the wall):
  X right, Y up, Z toward the viewer.  Z = 0 is the FRONT FACE of the bezel; the
  enclosure extends into -Z.  The e-paper ACTIVE AREA is centred on X = Y = 0.

Parts:
  "bezel"  front frame: face plate with the window, panel recess behind it, side walls,
           four M3 heat-set-insert bosses.
  "back"   back plate: screws onto the bezel; carries the PCB standoffs, HAT locating
           fence, battery fence, panel press pads, keyhole hangers, vents and openings.

Panel geometry is taken from the Waveshare "7.5inch e-Paper V2 Specification" rev 2.0,
section 1.4 (mechanical drawing):  outline 170.2 x 111.2 x 1.18 mm, active area
163.2 x 97.92 mm, 3.5 mm border on three sides and 9.78 mm on the FPC side, FPC 22 mm
wide / 24 mm long leaving the long edge roughly centred.
"""

import math

# ----------------------------------------------------------------------------------
# Parameters (mm)
# ----------------------------------------------------------------------------------
P = dict(
    # --- e-paper panel (Waveshare 7.5" V2) ---
    panel_w=170.2, panel_h=111.2, panel_t=1.18,
    aa_w=163.2, aa_h=97.92,
    border_side=3.5, border_top=3.5, border_fpc=9.78,   # FPC side goes to the bottom
    fpc_w=22.0, fpc_slot_w=36.0,                          # slot width covers the +-3.4 mm offset
    panel_clear=0.4,                                      # recess clearance per side
    recess_depth=1.5,

    # --- bezel ---
    face_t=4.0,          # front face thickness (2.5 mm lip + 1.5 mm panel recess)
    rim_side=14.0,       # visible rim width left / right / top
    rim_bottom=18.0,     # wider at the bottom: room for the FPC fold and the HAT
    window_margin=0.8,   # window = active area + margin per side
    window_chamfer=1.0,  # 45 deg chamfer on the front edge of the window
    corner_r=6.0,        # outer corner radius
    wall=2.5,            # side wall thickness
    cavity_d=17.0,       # electronics cavity depth (behind the front face)
    boss_d=7.0, boss_hole=4.0,   # M3 heat-set insert: 4.0 mm hole, 7 mm boss
    boss_inset=4.5,

    # --- back plate ---
    back_t=3.0,
    back_clear=0.3,      # per side, so the back plate drops into the bezel walls
    screw_hole=3.4, screw_cbore=6.5, screw_cbore_d=1.8,
    keyhole_r=4.0, keyhole_slot_w=4.5, keyhole_slot_l=7.0, keyhole_boss=12.0, keyhole_boss_h=2.0,
    keyhole_x=45.0, keyhole_y=54.0,   # slot runs upward from the circle (frame slides down onto the screw)

    # --- main PCB (hardware/kicad/weatherframe, 64 x 46 mm, M2.5 holes) ---
    pcb_w=64.0, pcb_h=46.0, pcb_t=1.6,
    pcb_holes=[(3.5, 42.5), (60.5, 3.5), (3.5, 17.0), (60.5, 42.5)],   # KiCad coords, y down
    pcb_standoff_h=5.0, pcb_standoff_d=5.5, pcb_standoff_hole=2.1,       # M2.5 self-tapping / insert
    pcb_rot_deg=90.0,    # USB-C edge faces +X (right side wall)
    pcb_edge_gap=0.5,    # gap between PCB edge and inner wall on the USB side
    pcb_y_bottom=-52.0,  # frame Y of the PCB's lower edge (MAINT switch edge); clears the corner boss
    usb_cut_w=13.0, usb_cut_h=7.5,      # plug overmold clearance in the side wall
    usb_pocket_w=19.0, usb_pocket_h=13.0, usb_wall_left=1.0,   # outer pocket thins the wall so the plug seats fully
    usb_pos_kicad=(26.0, 46.0),         # J1 centre x, board edge
    maint_pos_kicad=(64.0, 22.0),       # SW4 lever at the right board edge
    maint_slot_l=12.0, maint_slot_w=5.0,   # finger slot in the back plate over the lever
    buttons_kicad=[(17.0, 4.5), (26.0, 4.5), (58.5, 33.5)],  # RESET, BOOT, REFRESH
    button_hole_d=3.0,
    sht40_kicad=(6.0, 5.0),
    vent_slot_w=1.4, vent_slot_l=10.0, vent_pitch=3.0, vent_n=5,

    # --- Waveshare e-Paper Driver HAT Rev2.1 (65.0 x 30.2, measured from photos 2026-10-13) ---
    hat_w=65.0, hat_h=30.2, hat_t=1.6,
    hat_center=(0.0, -31.0),   # ZIF edge at y = -46.1: panel edge -58.7 + fold + 3 mm insertion = ~21.6 of the 24 mm FPC
    hat_holes_dx=58.0, hat_holes_dy=23.0,                     # Pi-Zero pattern, M2.5
    hat_standoff_h=7.5, hat_standoff_d=5.5, hat_standoff_hole=2.1,
    hat_header_l=50.8, hat_header_w=5.1, hat_header_h=8.5,   # 2x20 female header on the back side
    hat_header_y_off=11.8,   # header centre offset from HAT centre (+ = away from the ZIF edge)
    hat_header_pocket_d=1.5, # header sinks into a pocket in the back plate (plate stays 1.5 mm there)
    hat_jst_h=6.0,           # 8-pin JST-PH side-entry on the front side (tallest front-side part)

    # --- battery: 1S LiPo 605080 (6 x 50 x 80 mm) with JST-PH lead ---
    bat_l=80.0, bat_w=50.0, bat_t=6.0, bat_clear=1.0,
    bat_center=(-51.0, 20.0),   # above the HAT, left of the PCB; clear of the stand's hinge boss
    bat_fence_h=3.0, bat_fence_w=1.6,

    # --- panel press pads (back plate -> panel rear border, with 1 mm foam tape) ---
    pad_w=3.0, foam_t=1.0,

    # --- engraved labels on the back (seen from behind: left of RESET/BOOT/MAINT, right of REFRESH) ---
    label_size=3.0, label_depth=0.5, label_gap=1.2,

    # --- flip-out stand (25 deg lean on a cupboard; folded it adds a 3 mm gap behind the frame) ---
    stand_hinge_y=10.0,      # hinge axis along X, on the back face of the plate
    stand_len=75.0,          # axis to foot
    stand_w=60.0, stand_t=3.0,
    stand_open_deg=45.0,     # built-in stop: 45 deg opening = 25 deg lean with the rear-bottom edge on the table
    knuckle_r=3.0, pin_hole=3.3, knuckle_gap=0.4,   # M3 x 40 screw + nyloc nut as the hinge pin
    leg_knuckle_w=16.0, plate_knuckle_w=10.0,         # hinge spans 36.8 mm
    stop_tab_l=5.0, stop_tab_t=2.0,
)


# ----------------------------------------------------------------------------------
def derive(p=P):
    """Compute all derived dimensions."""
    d = dict(p)
    d["window_w"] = p["aa_w"] + 2 * p["window_margin"]
    d["window_h"] = p["aa_h"] + 2 * p["window_margin"]
    d["outer_w"] = d["window_w"] + 2 * p["rim_side"]
    d["outer_h"] = d["window_h"] + p["rim_side"] + p["rim_bottom"]
    d["outer_x0"] = -d["outer_w"] / 2
    d["outer_x1"] = d["outer_w"] / 2
    d["outer_y1"] = d["window_h"] / 2 + p["rim_side"]
    d["outer_y0"] = -d["window_h"] / 2 - p["rim_bottom"]
    d["inner_x0"] = d["outer_x0"] + p["wall"]
    d["inner_x1"] = d["outer_x1"] - p["wall"]
    d["inner_y0"] = d["outer_y0"] + p["wall"]
    d["inner_y1"] = d["outer_y1"] - p["wall"]
    # panel centre: active area centred on origin, wide border at the bottom
    d["panel_cx"] = 0.0
    d["panel_cy"] = (p["border_top"] - p["border_fpc"]) / 2
    d["panel_y0"] = d["panel_cy"] - p["panel_h"] / 2
    d["panel_y1"] = d["panel_cy"] + p["panel_h"] / 2
    d["recess_w"] = p["panel_w"] + 2 * p["panel_clear"]
    d["recess_h"] = p["panel_h"] + 2 * p["panel_clear"]
    # Z levels (all <= 0)
    d["z_face_back"] = -p["face_t"]
    d["z_recess"] = -p["face_t"] + p["recess_depth"]     # recess is cut INTO the face
    d["z_panel_back"] = d["z_recess"] - p["panel_t"]
    d["z_cavity"] = -p["face_t"] - p["cavity_d"]        # inner face of the back plate
    d["z_back"] = d["z_cavity"] - p["back_t"]           # rear face of the back plate
    d["total_t"] = -d["z_back"]
    # bosses
    bi = p["boss_inset"]
    d["boss_xy"] = [(d["inner_x0"] + bi, d["inner_y0"] + bi), (d["inner_x1"] - bi, d["inner_y0"] + bi),
                    (d["inner_x0"] + bi, d["inner_y1"] - bi), (d["inner_x1"] - bi, d["inner_y1"] - bi)]
    # PCB placement: components face the back plate; viewed from the front we see the
    # board mirrored, then rotated so that the USB-C edge faces +X.
    d["pcb_cx"] = d["inner_x1"] - p["pcb_edge_gap"] - p["pcb_h"] / 2
    d["pcb_cy"] = p["pcb_y_bottom"] + p["pcb_w"] / 2
    d["z_pcb_back"] = d["z_cavity"] + p["pcb_standoff_h"]          # component side (faces -Z)
    d["z_pcb_front"] = d["z_pcb_back"] + p["pcb_t"]
    return d


def kicad_to_frame(d, kx, ky):
    """Map a KiCad board coordinate (origin top-left, y down) to frame XY."""
    import math
    # board centre
    x = kx - d["pcb_w"] / 2
    y = ky - d["pcb_h"] / 2
    # components face -Z (toward the back plate)
    x, y = -x, -y  # -x: component side seen from behind; -y: KiCad y grows downward
    a = math.radians(d["pcb_rot_deg"])
    xr = x * math.cos(a) - y * math.sin(a)
    yr = x * math.sin(a) + y * math.cos(a)
    return d["pcb_cx"] + xr, d["pcb_cy"] + yr


def primitives(p=P):
    """Return (derived, ops).  op = (body, kind, operation, *geom)
    kinds:  box  (x0,y0,x1,y1,z0,z1)      cyl (cx,cy,r,z0,z1)
            rbox (x0,y0,x1,y1,z0,z1,r)    rounded-corner box
            slot (cx,cy,l,w,z0,z1,angle)  obround slot, l along angle
            xcyl (cy,cz,r,x0,x1)        cylinder along X
    operation: 'join' | 'cut'
    """
    d = derive(p)
    ops = []
    J, C = "join", "cut"

    # ------------------------------------------------------------------ bezel
    ops.append(("bezel", "rbox", J, d["outer_x0"], d["outer_y0"], d["outer_x1"], d["outer_y1"],
                d["z_cavity"], 0.0, p["corner_r"]))
    # cavity (leaves front face + walls)
    ops.append(("bezel", "box", C, d["inner_x0"], d["inner_y0"], d["inner_x1"], d["inner_y1"],
                d["z_cavity"] - 1, d["z_face_back"]))
    # panel recess into the back of the front face
    ops.append(("bezel", "box", C, -d["recess_w"] / 2, d["panel_cy"] - d["recess_h"] / 2,
                d["recess_w"] / 2, d["panel_cy"] + d["recess_h"] / 2, d["z_face_back"] - 1, d["z_recess"]))
    # window
    ops.append(("bezel", "box", C, -d["window_w"] / 2, -d["window_h"] / 2, d["window_w"] / 2, d["window_h"] / 2,
                d["z_recess"] - 1, 1.0))
    ops.append(("bezel", "chamfer_window", None, p["window_chamfer"]))
    # insert bosses
    for (bx, by) in d["boss_xy"]:
        ops.append(("bezel", "cyl", J, bx, by, p["boss_d"] / 2, d["z_cavity"], d["z_face_back"]))
    for (bx, by) in d["boss_xy"]:
        ops.append(("bezel", "cyl", C, bx, by, p["boss_hole"] / 2, d["z_cavity"] - 1, d["z_face_back"] - 1.0))
    # USB-C opening in the right wall
    ux, uy = kicad_to_frame(d, *p["usb_pos_kicad"])
    zc = d["z_pcb_back"] - 1.6   # USB-C body centre is ~1.6 mm above the board
    ops.append(("bezel", "box", C, d["inner_x1"] - 1, uy - p["usb_cut_w"] / 2, d["outer_x1"] + 1,
                uy + p["usb_cut_w"] / 2, zc - p["usb_cut_h"] / 2, zc + p["usb_cut_h"] / 2))
    ops.append(("bezel", "box", C, d["inner_x1"] + p["usb_wall_left"], uy - p["usb_pocket_w"] / 2, d["outer_x1"] + 1,
                uy + p["usb_pocket_w"] / 2, zc - p["usb_pocket_h"] / 2, zc + p["usb_pocket_h"] / 2))
    # ------------------------------------------------------------------ back plate
    bc = p["back_clear"]
    ops.append(("back", "rbox", J, d["outer_x0"], d["outer_y0"], d["outer_x1"], d["outer_y1"],
                d["z_back"], d["z_cavity"], p["corner_r"]))
    # screw holes with counterbore
    for (bx, by) in d["boss_xy"]:
        ops.append(("back", "cyl", C, bx, by, p["screw_hole"] / 2, d["z_back"] - 1, d["z_cavity"] + 1))
        ops.append(("back", "cyl", C, bx, by, p["screw_cbore"] / 2, d["z_back"] - 1, d["z_back"] + p["screw_cbore_d"]))
    # lip: the plate is plain; inner features follow.
    # keyhole hangers
    for sx in (-1, 1):
        kx, ky = sx * p["keyhole_x"], p["keyhole_y"]
        ops.append(("back", "cyl", J, kx, ky, p["keyhole_boss"] / 2, d["z_cavity"], d["z_cavity"] + p["keyhole_boss_h"]))
        ops.append(("back", "box", J, kx - p["keyhole_boss"] / 2, ky, kx + p["keyhole_boss"] / 2, ky + p["keyhole_slot_l"],
                    d["z_cavity"], d["z_cavity"] + p["keyhole_boss_h"]))
        ops.append(("back", "cyl", C, kx, ky, p["keyhole_r"], d["z_back"] - 1, d["z_cavity"] + p["keyhole_boss_h"] + 1))
        ops.append(("back", "box", C, kx - p["keyhole_slot_w"] / 2, ky, kx + p["keyhole_slot_w"] / 2, ky + p["keyhole_slot_l"],
                    d["z_back"] - 1, d["z_cavity"] + p["keyhole_boss_h"] + 1))
    # PCB standoffs
    for (hx, hy) in p["pcb_holes"]:
        fx, fy = kicad_to_frame(d, hx, hy)
        ops.append(("back", "cyl", J, fx, fy, p["pcb_standoff_d"] / 2, d["z_cavity"], d["z_pcb_back"]))
        ops.append(("back", "cyl", C, fx, fy, p["pcb_standoff_hole"] / 2, d["z_cavity"] - 0.0 + 0.5 - p["back_t"], d["z_pcb_back"] + 1))
    # MAINT slide switch: finger slot in the back plate over the lever (travel along X)
    mx, my = kicad_to_frame(d, *p["maint_pos_kicad"])
    ops.append(("back", "slot", C, mx, my - 1.5, p["maint_slot_l"], p["maint_slot_w"], d["z_back"] - 1, d["z_cavity"] + 1, 0.0))
    # button access holes
    for (bx, by) in p["buttons_kicad"]:
        fx, fy = kicad_to_frame(d, bx, by)
        ops.append(("back", "cyl", C, fx, fy, p["button_hole_d"] / 2, d["z_back"] - 1, d["z_cavity"] + 1))
    # engraved labels: text box starts label_gap beyond the hole edge (frame +X = viewer's left from behind)
    LABEL_W = {"RESET": 3.33, "BOOT": 2.89, "REFRESH": 4.78, "MAINT": 3.17}   # width / font size (bold sans)
    ls, lg = p["label_size"], p["label_gap"]
    for name, (kx, ky), edge, side in (("RESET", p["buttons_kicad"][0], p["button_hole_d"] / 2, 1),
                                       ("BOOT", p["buttons_kicad"][1], p["button_hole_d"] / 2, 1),
                                       ("REFRESH", p["buttons_kicad"][2], p["button_hole_d"] / 2, -1),
                                       ("MAINT", p["maint_pos_kicad"], p["maint_slot_l"] / 2, 1)):
        fx, fy = kicad_to_frame(d, kx, ky)
        if name == "MAINT":
            fy -= 1.5
        w = LABEL_W[name] * ls
        # side +1 = frame +X = viewer's left from behind; -1 = viewer's right
        ops.append(("back", "text", C, fx + side * (edge + lg + w / 2), fy, d["z_back"], ls, p["label_depth"], name, w))
    # SHT40 vent slots (around the sensor corner)
    sx, sy = kicad_to_frame(d, *p["sht40_kicad"])
    for i in range(p["vent_n"]):
        off = (i - (p["vent_n"] - 1) / 2) * p["vent_pitch"]
        ops.append(("back", "slot", C, sx + off, sy, p["vent_slot_l"], p["vent_slot_w"], d["z_back"] - 1, d["z_cavity"] + 1, 90.0))
    # HAT: four M2.5 standoffs on the Pi-Zero hole pattern; the 2x20 header sinks into a pocket
    hx, hy = p["hat_center"]
    z_hat_back = d["z_cavity"] + p["hat_standoff_h"]
    for sxn in (-1, 1):
        for syn in (-1, 1):
            px, py = hx + sxn * p["hat_holes_dx"] / 2, hy + syn * p["hat_holes_dy"] / 2
            ops.append(("back", "cyl", J, px, py, p["hat_standoff_d"] / 2, d["z_cavity"], z_hat_back))
            ops.append(("back", "cyl", C, px, py, p["hat_standoff_hole"] / 2, d["z_cavity"] + 0.5 - p["back_t"], z_hat_back + 1))
    hl, hw = p["hat_header_l"] + 0.8, p["hat_header_w"] + 0.6
    hyc = hy + p["hat_header_y_off"]
    ops.append(("back", "box", C, hx - hl / 2, hyc - hw / 2, hx + hl / 2, hyc + hw / 2,
                d["z_cavity"] - p["hat_header_pocket_d"], d["z_cavity"] + 1))
    # battery fence
    bx, by = p["bat_center"]
    bl, bw = p["bat_l"] + 2 * p["bat_clear"], p["bat_w"] + 2 * p["bat_clear"]
    fw, fh = p["bat_fence_w"], p["bat_fence_h"]
    ops.append(("back", "box", J, bx - bl / 2 - fw, by - bw / 2 - fw, bx + bl / 2 + fw, by + bw / 2 + fw,
                d["z_cavity"], d["z_cavity"] + fh))
    ops.append(("back", "box", C, bx - bl / 2, by - bw / 2, bx + bl / 2, by + bw / 2, d["z_cavity"], d["z_cavity"] + fh + 1))
    # lead exit gap in the fence toward the PCB (+X side)
    ops.append(("back", "box", C, bx + bl / 2 - 1, by - 6, bx + bl / 2 + fw + 1, by + 6, d["z_cavity"], d["z_cavity"] + fh + 1))
    # panel press pads (top of pad = panel back - foam); kept clear of the PCB and the FPC
    z_pad = d["z_panel_back"] - p["foam_t"]
    pw = p["pad_w"]
    side_x = p["aa_w"] / 2 + p["border_side"] / 2 + 0.6          # on the 3.5 mm side border
    top_y = p["aa_h"] / 2 + p["border_top"] / 2 + 0.6
    bot_y = d["panel_y0"] + p["border_fpc"] / 2                  # on the 9.8 mm FPC border
    pads = [(-side_x, -45, -side_x, -20), (side_x, 16, side_x, 46),        # left below the battery, right above the PCB
            (-36, top_y, -10, top_y), (10, top_y, 36, top_y),              # top, either side of the keyholes
            (-75, bot_y, -35, bot_y), (20, bot_y, 44, bot_y)]              # bottom, either side of the FPC
    for (x0, y0, x1, y1) in pads:
        ops.append(("back", "box", J, x0 - pw / 2, y0 - pw / 2, x1 + pw / 2, y1 + pw / 2, d["z_cavity"], z_pad))

    # ------------------------------------------------------------------ flip-out stand
    yh, za = p["stand_hinge_y"], d["z_back"]           # hinge axis: y = yh, z = rear face of the plate
    kr, g = p["knuckle_r"], p["knuckle_gap"]
    lk = p["leg_knuckle_w"] / 2                        # leg knuckle half width
    pk0, pk1 = lk + g, lk + g + p["plate_knuckle_w"]   # plate knuckles from x = +-pk0 to +-pk1
    st, sw = p["stand_t"], p["stand_w"]
    # inner boss that backs up the stop pocket (inside the cavity, clear of the battery fence)
    ops.append(("back", "box", J, -lk - g - 1.0, yh - 5, lk + g + 1.0, yh + 7, d["z_cavity"], d["z_cavity"] + 3.0))
    # plate knuckles (behind the plate, max 3 mm proud = same as the folded leg)
    for sxn in (-1, 1):
        x0, x1 = sorted((sxn * pk0, sxn * pk1))
        ops.append(("back", "xcyl", J, yh, za, kr, x0, x1))
        ops.append(("back", "box", J, x0, yh - kr, x1, yh + kr, za, za + 1.0))   # web into the plate
    # clearance for the leg knuckle + stop tab swinging into the plate
    ops.append(("back", "xcyl", C, yh, za, kr + g, -lk - g, lk + g))
    tab_reach = p["stop_tab_l"] * math.sin(math.radians(p["stand_open_deg"]))   # stop: tab tip meets the pocket floor
    ops.append(("back", "box", C, -lk - g, yh, lk + g, yh + p["stop_tab_l"] + 0.6, za - 1, za + tab_reach))
    # hinge pin hole through the plate knuckles
    ops.append(("back", "xcyl", C, yh, za, p["pin_hole"] / 2, -pk1 - 1, pk1 + 1))
    # the leg (folded position): body, knuckle, stop tab, pin hole
    y_body_top = yh - kr - g - 0.5
    ops.append(("stand", "box", J, -sw / 2, yh - p["stand_len"], sw / 2, y_body_top, za - st, za))
    ops.append(("stand", "box", J, -lk, yh - kr - 1, lk, yh, za - st, za))
    ops.append(("stand", "xcyl", J, yh, za, kr, -lk, lk))
    ops.append(("stand", "box", J, -lk, yh, lk, yh + p["stop_tab_l"], za - p["stop_tab_t"], za))
    ops.append(("stand", "xcyl", C, yh, za, p["pin_hole"] / 2, -lk - 1, lk + 1))
    # finger notch at the foot to flip it out
    ops.append(("stand", "box", C, -6, yh - p["stand_len"] - 1, 6, yh - p["stand_len"] + 3, za - st - 1, za - st + 1.2))

    # ------------------------------------------------------------------ reference bodies (not printed)
    ops.append(("ref_panel", "box", J, -p["panel_w"] / 2, d["panel_y0"], p["panel_w"] / 2, d["panel_y1"],
                d["z_panel_back"], d["z_recess"]))
    ops.append(("ref_pcb", "box", J, d["pcb_cx"] - p["pcb_h"] / 2, d["pcb_cy"] - p["pcb_w"] / 2,
                d["pcb_cx"] + p["pcb_h"] / 2, d["pcb_cy"] + p["pcb_w"] / 2, d["z_pcb_back"], d["z_pcb_front"]))
    ops.append(("ref_hat", "box", J, hx - p["hat_w"] / 2, hy - p["hat_h"] / 2, hx + p["hat_w"] / 2, hy + p["hat_h"] / 2,
                z_hat_back, z_hat_back + p["hat_t"]))
    # tallest front-side part (JST-PH) and the header on the back, to catch clashes with panel / plate
    ops.append(("ref_hat", "box", J, hx - 6, hy + p["hat_h"] / 2 - 8, hx + 6, hy + p["hat_h"] / 2,
                z_hat_back + p["hat_t"], z_hat_back + p["hat_t"] + p["hat_jst_h"]))
    ops.append(("ref_hat", "box", J, hx - p["hat_header_l"] / 2, hyc - p["hat_header_w"] / 2, hx + p["hat_header_l"] / 2,
                hyc + p["hat_header_w"] / 2, z_hat_back - p["hat_header_h"], z_hat_back))
    ops.append(("ref_battery", "box", J, bx - p["bat_l"] / 2, by - p["bat_w"] / 2, bx + p["bat_l"] / 2, by + p["bat_w"] / 2,
                d["z_cavity"], d["z_cavity"] + p["bat_t"]))
    return d, ops


if __name__ == "__main__":
    d, ops = primitives()
    print("outer %.1f x %.1f x %.1f mm, %d primitives" % (d["outer_w"], d["outer_h"], d["total_t"], len(ops)))
    for k in ("panel_cy", "panel_y0", "inner_y0", "pcb_cx", "pcb_cy", "z_pcb_back", "z_cavity"):
        print(f"  {k} = {d[k]:.2f}")
