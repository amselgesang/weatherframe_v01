# Wiki index

Catalog of every page; read this first. Updated on every ingest.

## Overview

- [[overview]] — A battery-powered weather station built into a white wall picture frame: a [[waveshare-7in5-v2-panel]] shows time, date, current weather, an hourly chart and a 5-day forecast for Budapest from …

## Entities

- [[custom-pcb-r1]] — 64 × 46 mm, 2-layer, generated from `hardware/kicad/weatherframe/gen/design.py`; routed with Freerouting; DRC 0 errors.
- [[esphome-firmware]] — `firmware/weatherframe_ee05.yaml` (current, [[seeed-ee05]]) and `firmware/weatherframe.yaml` (archived, [[custom-pcb-r1]]) share `weatherframe/common.yaml` (Open-Meteo fetch, fonts, render lambda) …
- [[frame]] — Three printed parts, white, 192.8 × 131.5 × 24 mm (27 mm with the folded stand).
- [[fusion-360-mcp]] — Autodesk's MCP server for Fusion (`http://127.0.0.1:27182/mcp` on the Mac).
- [[jlcpcb]] — Manufacturer chosen by the owner.
- [[lipo-605080]] — 1S 3.7 V, 6 × 50 × 80 mm, about 3000 mAh, with protection PCB and JST-PH 2.0 plug.
- [[open-meteo]] — Free weather API without a key.
- [[seeed-ee05]] — XIAO ESP32-S3 Plus on a carrier with the 24-pin panel connector, battery charger, JST 2.0 mm battery socket with slide switch, reset + 3 user keys.
- [[waveshare-7in5-v2-panel]] — The owner's display: 800 × 480 px, 4 grey levels, UC8179 controller, 24-pin FPC.
- [[waveshare-epaper-driver-hat]] — Raspberry-Pi HAT that carries the panel's boost circuits and the 24-pin ZIF connector.

## Concepts

- [[five-volt-sensing-dividers]] — The ESP32-S3 is not 5 V tolerant (absolute max 3.6 V) and reads logic high only above 0.75 × 3.3 V = 2.475 V.
- [[flip-out-stand]] — A printed leg hinged on the back plate so the [[frame]] can stand on a cupboard.
- [[jlc-assembly-tiers]] — Economic PCBA is cheap but refuses some parts; on 2026-10-13 it refused the ESP32-S3-WROOM-1 module (package/temperature limits).
- [[no-solder-build]] — Constraint since 2026-10-13: the owner cannot solder, so every electrical connection must plug in and every mechanical one must use a screwdriver.
- [[parametric-cad-pipeline]] — `frame_geom.py` describes the whole [[frame]] as a list of primitives (box, rounded box, cylinder, slot, X-axis cylinder, engraved text) with a `P` parameter dict.
- [[wake-cycle]] — Every 15 minutes, aligned to :00/:15/:30/:45, skipping 00:00–06:00: wake → read battery → Wi-Fi + SNTP (15 s / 3 s timeouts) → [[open-meteo]] (10 s) → power the panel, render, refresh (30 s) → …

## Comparisons

- [[custom-pcb-vs-ee05]] — Decision 2026-10-13: **Seeed EE05**, because the owner cannot solder and [[jlcpcb]]'s Economic assembly refuses the ESP32 module ([[jlc-assembly-tiers]]).

## Sources

- [[hat-photos]] — Two photos of the [[waveshare-epaper-driver-hat]] Rev2.1: front (labels, switches, ZIF, JST PH) and back with a cm ruler (65 mm width, 40-pin header along the edge opposite the ribbon, four …
- [[jlcpcb-assembly-message]] — JLCPCB refused U1 (ESP32-S3-WROOM-1) in Economic assembly and proposed Standard assembly ($25 setup, board enlarged to 74 × 70 mm with rails).
- [[requirements-2026-10-13]] — Weather station on the owner's [[waveshare-7in5-v2-panel]], used as a wall picture frame, Wi-Fi, rechargeable battery; frame and PCB to be designed, in Fusion 360 and KiCad where possible; made by …
- [[seeed-gfx-epaper-board-pins]] — `User_Setups/EPaper_Board_Pins_Setups.h` from Seeed_GFX (MIT): SPI, CS, DC, BUSY, RST and `TFT_ENABLE` (panel power, GPIO43, driven HIGH) for the EE02–EE05 and EN04/EN05 boards.
- [[seeed-xiao-epaper-boards]] — Wiki and shop pages for EE04/EE05/EN04/EN05 and the ESPHome cookbook: board features, supported panels, EE04 battery and key pins, ESPHome display pins.
- [[ti-tps63001-pins]] — Used to verify the buck-boost wiring of the [[custom-pcb-r1]]: FB must go to VOUT on fixed versions, PS/SYNC low enables power-save mode.
- [[waveshare-7in5-v2-mechanical]] — Outline, active area, layer steps and FPC data for the [[waveshare-7in5-v2-panel]]; the basis for the window, recess and ribbon routing of the [[frame]].
