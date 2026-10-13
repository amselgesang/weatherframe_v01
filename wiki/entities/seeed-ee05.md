---
title: Seeed XIAO ePaper Display Board EE05
type: entity
sources:
  - raw/seeed-gfx-epaper-board-pins.h
  - raw/seeed-xiao-epaper-boards.md
related:
  - "[[esphome-firmware]]"
  - "[[custom-pcb-vs-ee05]]"
  - "[[lipo-605080]]"
  - "[[frame]]"
created: 2026-10-13
updated: 2026-10-13
confidence: medium
---
# Seeed XIAO ePaper Display Board EE05 (current electronics)

XIAO ESP32-S3 Plus on a carrier with the 24-pin panel connector, battery charger, JST 2.0 mm battery
socket with slide switch, reset + 3 user keys. 52 × 27 mm, about €13. Chosen because it needs no
soldering ([[no-solder-build]], [[custom-pcb-vs-ee05]]).

## Pin map used in `weatherframe_ee05.yaml`

| Signal | GPIO | Source | Confidence |
|---|---|---|---|
| SPI CLK / MOSI | 7 / 9 | Seeed_GFX EE05 + ESPHome cookbook | high |
| CS / DC / RST / BUSY | 44 / 10 / 38 / 4 | Seeed_GFX EE05 | high |
| Panel power enable (high = on) | 43 | Seeed_GFX EE05, `TFT_ENABLE` driven HIGH by the drivers | high |
| Battery ADC / divider enable | 1 / 6 | EE04 wiki (same base) | medium |
| KEY1 refresh / KEY2 maintenance / KEY3 spare | 2 / 3 / 5 | EE04 wiki | medium |

Battery divider ratio is undocumented: the firmware uses `battery_divider: 2.0` and ignores readings
outside 2.8–4.5 V; calibrate once with a multimeter. GPIO3 is a strapping pin (JTAG source select) —
ESPHome warns, harmless here.

No temperature sensor on board: the screen shows tomorrow's forecast where the indoor reading was.
The board's exact USB-C, switch and button positions are still to be measured for the [[frame]].

Sources: [[seeed-gfx-epaper-board-pins]], [[seeed-xiao-epaper-boards]]
