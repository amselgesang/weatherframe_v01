---
title: Custom PCB vs Seeed EE05
type: comparison
sources:
  - raw/jlcpcb-assembly-message-2026-10-13.md
  - raw/seeed-xiao-epaper-boards.md
related:
  - "[[seeed-ee05]]"
  - "[[custom-pcb-r1]]"
  - "[[no-solder-build]]"
  - "[[jlc-assembly-tiers]]"
created: 2026-10-13
updated: 2026-10-13
confidence: high
---
# Custom PCB vs Seeed EE05

Decision 2026-10-13: **Seeed EE05**, because the owner cannot solder and [[jlcpcb]]'s Economic
assembly refuses the ESP32 module ([[jlc-assembly-tiers]]).

| | [[custom-pcb-r1]] + [[waveshare-epaper-driver-hat]] | [[seeed-ee05]] |
|---|---|---|
| Soldering | ESP32 by hand (Economic) or none with Standard assembly + board revision | none |
| Cost | about €100 for 2 assembled boards (+$25 Standard setup) | about €13 |
| Panel link | HAT + 8-wire cable | ribbon straight in |
| Indoor sensor | SHT40 | none (tomorrow's forecast shown instead) |
| Panel power off in sleep | yes | yes |
| Battery charger / socket | MCP73831, JST-PH | built in, JST 2.0, slide switch |
| Effort left | re-layout for Standard assembly | frame holder; verify battery/button pins |

Options considered and rejected: hand-soldering the module (owner cannot solder); Standard assembly
without redesign (rails clash with the antenna overhang); nRF52840 variants EN04/EN05 (no Wi-Fi).

Sources: [[jlcpcb-assembly-message]], [[seeed-xiao-epaper-boards]]
