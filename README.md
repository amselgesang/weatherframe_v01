# Weather Frame

> **13 Oct 2026 — electronics changed.** JLCPCB can only place the ESP32-S3 module with Standard assembly, and the build must need no soldering. The electronics are now a ready-made **Seeed XIAO ePaper Display Board EE05**, which replaces the custom PCB and the Waveshare HAT. Firmware: `firmware/weatherframe_ee05.yaml`. The custom PCB below is kept as an archived design. Shopping list, assembly and flashing: `docs/manufacturing.md`.


A wall-hung weather station in a picture frame: Waveshare 7.5" e-paper (800 × 480,
4-level grayscale), custom ESP32-S3 board with a rechargeable 1S LiPo, Wi-Fi + Open-Meteo.
Wakes every 15 minutes, refreshes the display, sleeps. Charges over USB-C.

```
docs/                    design documentation + manufacturing & ordering guide (Markdown + PDF)
firmware/                ESPHome configuration (esp-idf, ESP32-S3)
hardware/kicad/          main PCB (64 × 46 mm, 2-layer) — generated from gen/design.py
hardware/kicad/.../fab/  JLCPCB upload set: Gerbers, BOM, CPL (LCSC part numbers)
hardware/mechanical/     wall frame: Fusion 360 script + CadQuery build + STEP/STL
```

## Status (2026-10-13)

| Part | State |
|---|---|
| Schematic / PCB | Routed. DRC: 0 errors, 0 unconnected; 4 expected silkscreen warnings (antenna overhang, USB-C at the edge) + 1 harmless local-footprint note (SHT40). |
| JLCPCB files | `fab/weatherframe_gerbers.zip`, `fab/bom_jlc.csv`, `fab/cpl_jlc.csv` — all parts in LCSC stock, basic parts where possible. **Re-export after the R6/R11 change (see below) with `./build.sh fab` so the CPL/Gerbers are from the same run.** |
| Firmware | Validates with ESPHome 2026.9.1 (`esphome config weatherframe.yaml`). Not compiled yet — compile and flash on the Mac. |
| Display layout | `firmware/.esphome/snapshots/weatherframe-preview/preview.bmp` (from `esphome run preview.yaml`). |
| Frame | Designed: two printed parts (bezel + back plate), 192.8 × 131.5 × 24 mm, built in Fusion (`weather_station_v01`, component `WeatherFrame_r2`) + STEP/STL. HAT geometry measured from the real Rev2.1 board. **Not yet printed/verified physically.** |

### Change in this session: R6 / R11 100 k → 150 k (C25755)

The VBUS-sense (GPIO4) and charger-STAT (GPIO15) dividers were 100 k/100 k: 5 V → 2.5 V, which
sits exactly on the ESP32-S3's VIH minimum (0.75 × 3.3 V = 2.475 V) and reads undefined on a
4.75 V USB supply. With 150 k on the bottom they give 3.0 V (2.85–3.15 V over the USB range),
still below the 3.6 V absolute maximum. Changed in `gen/design.py`, the schematic, the board and
the BOM; same footprint, so the routing is unchanged.

The rest of the pin map was checked against the KiCad library symbols: every firmware GPIO
matches the module pin it is wired to, the TPS63001 (FB → VOUT, VINA → VIN, PS/SYNC low =
power-save), MCP73831, USBLC6, AO3401A load-sharing, SHT40 and switch wiring are all correct.

## Ordering from JLCPCB

**PCB + assembly:** upload `fab/weatherframe_gerbers.zip` (2 layers, 1.6 mm, any colour),
tick *PCB Assembly* (top side, economic), then upload `bom_jlc.csv` and `cpl_jlc.csv`.
Not assembled (hand-solder): J3 (9-pin header / cable to the HAT) and the mounting holes.
Check the preview that JLC's rotation of U1 (ESP32 module), J1 (USB-C) and U3 (TPS63001,
pin 1 dot) matches the render in `build/render_top.png` — rotate in their viewer if not.

**Frame (JLC3DP):** upload `hardware/mechanical/export/bezel.stl` and `back.stl`.
Recommended: MJF, PA12 nylon, dyed black or grey (bezel), or SLA 9000R resin for a smoother
face. Both parts fit the standard build volumes. Expect about 58 cm³ + 86 cm³ of material.

## Frame design

`hardware/mechanical/frame_geom.py` is the single source of truth (all dimensions in mm, with
the panel data from the Waveshare 7.5" V2 spec sheet, section 1.4). Two ways to get geometry:

* **Fusion 360:** `frame_fusion360.py` — Utilities ▸ Add-Ins ▸ Scripts and Add-Ins ▸ create a
  Python script, replace its .py with this file, Run. It builds the bodies `bezel`, `back`
  (print these) and `ref_panel`, `ref_pcb`, `ref_hat`, `ref_battery` (reference only). Edit
  the `P` dict and re-run to change anything. Verified: the script was executed inside Fusion
  through the Fusion MCP connector on 2026-10-13 and produced the same body volumes as the
  CadQuery build (bezel 57.7 cm³, back 86.2 cm³).
* **No Fusion needed:** `python3 build_cadquery.py export` (pip install cadquery) regenerates
  the STEP/STL files; `python3 render.py export` writes the preview PNGs.

Layout (front view, active area centred at the origin, Z toward the viewer):

* **Bezel** — 4 mm face (2.5 mm lip over the 3.5 mm panel border, 1.5 mm panel recess),
  window = active area + 0.8 mm, 1 mm chamfer, 14 mm rim (18 mm at the bottom for the FPC
  fold), 2.5 mm walls, 17 mm cavity, four M3 heat-set-insert bosses, USB-C opening in the
  right wall (wall thinned to 1 mm locally so the plug seats).
* **Back plate** — 3 mm, M3 counterbored screws, two keyhole hangers (circle Ø8, slot up),
  PCB on four M2.5 standoffs (components facing the plate, USB-C to the right wall, MAINT
  switch reachable through a slot at the bottom edge, RESET/BOOT/REFRESH through Ø3 holes,
  vent slots over the SHT40 corner), four M2.5 standoffs for the e-Paper Driver HAT Rev2.1
  (Pi-Zero 58 × 23 mm hole pattern; its 2×20 header sinks into a 1.5 mm pocket), battery fence
  for a 605080 LiPo (6 × 50 × 80 mm, ~3000 mAh ≈ 2 months per charge), and press pads that
  hold the glass against the lip with 1 mm foam tape.
* HAT sits with its switches / ZIF / JST side toward the panel (2.2 mm clearance to the
  glass) and the 40-pin header toward the back plate; the panel FPC folds around the bottom
  edge of the glass into the ZIF (24 mm tail, ~21.6 mm used). HAT switches: Display Config
  **B**, Interface Config **0** (4-line SPI). Its 8-wire PH2.0 cable (BUSY RST DC CS CLK DIN
  GND VCC) is soldered into J3 — J3's second VCC pin stays unused.

Assembly notes: glue 1 mm foam tape on the six pads before closing; the HAT cable is soldered
directly into J3 (a vertical header would not fit under the back plate — for a PCB r2 consider
a right-angle JST-PH there to use the HAT's cable as-is); the battery lead reaches J2 across
the top of the HAT, an 80 mm lead or an extension is needed. Screws: 4× M3×8 (back plate into
heat-set inserts), 8× M2.5×5 self-tapping (PCB + HAT standoffs).

## Bring-up

```sh
cd firmware
cp secrets.yaml.example secrets.yaml   # fill in Wi-Fi + OTA password
esphome run weatherframe.yaml          # USB-C the first time; set MAINT on for OTA/logs later
esphome run preview.yaml               # desktop layout preview (SDL window + BMP snapshot)
```

Pins, intervals, location and language are substitutions at the top of `weatherframe.yaml`.

## Regenerating the hardware

```sh
cd hardware/kicad/weatherframe
./build.sh sch      # schematic from gen/design.py
./build.sh check    # ERC + DRC + render into build/
./build.sh fab      # JLCPCB files into fab/
# full re-route only if footprints/positions change: ./build.sh place -> Freerouting -> ./build.sh finish
```
