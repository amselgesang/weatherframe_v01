---
title: Custom main PCB r1
type: entity
sources:
  - raw/ti-tps63001-pins.md
  - raw/jlcpcb-assembly-message-2026-10-13.md
related:
  - "[[custom-pcb-vs-ee05]]"
  - "[[jlc-assembly-tiers]]"
  - "[[five-volt-sensing-dividers]]"
created: 2026-10-13
updated: 2026-10-13
confidence: high
---
# Custom main PCB r1 (archived)

64 × 46 mm, 2-layer, generated from `hardware/kicad/weatherframe/gen/design.py`; routed with
Freerouting; DRC 0 errors. Archived because [[jlcpcb]] will only place its ESP32 module in Standard
assembly and the owner cannot solder ([[custom-pcb-vs-ee05]]).

| Block | Part | Note |
|---|---|---|
| MCU | ESP32-S3-WROOM-1-N16R8 | antenna overhangs the top edge by about 6 mm |
| 3.3 V | TPS63001 buck-boost | pins verified against the TI table (FB→VOUT, VINA→VIN, PS/SYNC low) |
| Charger | MCP73831-2, PROG 2 kΩ → 500 mA | |
| Load sharing | B5819W + AO3401A | |
| USB-C | HRO TYPE-C-31-M-12, 5.1 kΩ CC, USBLC6-2SC6 | |
| Sensing | 1 M/1 M battery divider; 100 k/150 k for VBUS and STAT | see [[five-volt-sensing-dividers]] |
| Panel power | AO3401A P-FET | |
| Sensor | SHT40 on an isolated corner tab | |

Fab files (`fab/`) were regenerated after the R6/R11 change and are valid for a Standard-assembly order
if the board is ever revised (extend under the antenna, panel with rails — see [[jlc-assembly-tiers]]).

Sources: [[ti-tps63001-pins]], [[jlcpcb-assembly-message]]
