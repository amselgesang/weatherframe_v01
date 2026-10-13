---
title: Waveshare 7.5" e-Paper V2 panel
type: entity
sources:
  - raw/waveshare-7in5-v2-mechanical.md
  - raw/seeed-xiao-epaper-boards.md
related:
  - "[[frame]]"
  - "[[seeed-ee05]]"
  - "[[waveshare-epaper-driver-hat]]"
created: 2026-10-13
updated: 2026-10-13
confidence: high
---
# Waveshare 7.5" e-Paper V2 panel

The owner's display: 800 × 480 px, 4 grey levels, UC8179 controller, 24-pin FPC.

| Property | Value |
|---|---|
| Outline | 170.2 × 111.2 × 1.18 mm |
| Active area | 163.2 × 97.92 mm |
| Borders | 3.5 mm on three sides, 9.78 mm on the ribbon side (vertical split inferred from the layer steps) |
| FPC | 24 pins, 0.5 mm pitch, 22 mm wide, 24 mm tail |
| Controller | UC8179 (ESPHome `epaper_spi` model `waveshare-7.5in-v2`; Seeed lists it as combo 502) |

In the [[frame]] the glass sits in a 1.5 mm recess behind a 2.5 mm lip, held by foam pads, with the
ribbon folded round the bottom edge. Driven first through the [[waveshare-epaper-driver-hat]], now
directly by the [[seeed-ee05]].

Sources: [[waveshare-7in5-v2-mechanical]], [[seeed-xiao-epaper-boards]]
