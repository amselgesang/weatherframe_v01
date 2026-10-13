---
title: Frame (bezel, back plate, stand)
type: entity
sources:
  - hardware/mechanical/frame_geom.py
  - raw/requirements-2026-10-13.md
related:
  - "[[flip-out-stand]]"
  - "[[waveshare-7in5-v2-panel]]"
  - "[[seeed-ee05]]"
  - "[[parametric-cad-pipeline]]"
created: 2026-10-13
updated: 2026-10-13
confidence: high
---
# Frame

Three printed parts, white, 192.8 × 131.5 × 24 mm (27 mm with the folded stand). Single source:
`hardware/mechanical/frame_geom.py` → CadQuery (`build_cadquery.py`) and Fusion 360
(`frame_fusion360.py`, see [[fusion-360-mcp]] and [[parametric-cad-pipeline]]).

- **Bezel:** window = active area + 0.8 mm, 1 mm chamfer; 14 mm rims, 18 mm at the bottom; 4 mm face
  with a 1.5 mm panel recess; 17 mm cavity; four M3 screw bosses (heat-set inserts in the current files,
  self-tapping planned for the EE05 version).
- **Back plate:** keyholes at x = ±45 mm; foam press pads; engraved labels RESET/BOOT/MAINT left of
  their openings and REFRESH right of its hole (as seen from behind), 3 mm bold, 0.5 mm deep; mounts for
  the archived PCB and HAT (to be replaced by an EE05 holder).
- **Stand:** see [[flip-out-stand]].

Fusion document `weather_station_v02`, latest component `WeatherFrame_r5`.
Print: MJF PA12 or SLA 9000R white at [[jlcpcb]] (JLC3DP); hold the order until the EE05 version exists.

Sources: [[requirements-2026-10-13]]
