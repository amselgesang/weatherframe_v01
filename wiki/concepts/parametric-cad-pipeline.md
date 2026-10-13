---
title: Parametric CAD pipeline
type: concept
sources:
  - hardware/mechanical/frame_geom.py
  - hardware/mechanical/build_cadquery.py
related:
  - "[[frame]]"
  - "[[fusion-360-mcp]]"
  - "[[flip-out-stand]]"
created: 2026-10-13
updated: 2026-10-13
confidence: high
---
# Parametric CAD pipeline

`frame_geom.py` describes the whole [[frame]] as a list of primitives (box, rounded box, cylinder, slot,
X-axis cylinder, engraved text) with a `P` parameter dict. Two builders consume it:

- `build_cadquery.py` → STEP/STL, interference checks against reference volumes (panel, PCB, HAT,
  battery), previews via `render.py`; hinge sweeps are done by rotating the stand body.
- `frame_fusion360.py` → the same bodies as a parametric timeline in Fusion 360; `build(name, hide)`
  is callable from the [[fusion-360-mcp]] without dialogs. Both builders produce the same volumes.

Rule: change numbers in `P`, rebuild both, re-run the checks, then update the wiki pages that quote them.
