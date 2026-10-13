---
title: Flip-out stand
type: concept
sources:
  - hardware/mechanical/frame_geom.py
  - raw/requirements-2026-10-13.md
related:
  - "[[frame]]"
created: 2026-10-13
updated: 2026-10-13
confidence: high
---
# Flip-out stand

A printed leg hinged on the back plate so the [[frame]] can stand on a cupboard.

- Leg 60 × 75 × 3 mm (axis to foot); hinge axis along X, 10 mm above centre, on the plate's back face.
- Three knuckles spanning 36.8 mm (leg knuckle 16 mm, plate knuckles 10 mm each), M3 × 40 pin + nyloc
  nut for friction.
- Built-in stop: a 5 mm tab on the leg meets a pocket floor at 45° opening; 2.5 mm material behind it.
- Geometry: hinge at y = 10 mm, rear-bottom edge on the table, 75 mm leg at 45° → **25.1° lean**, 59 mm
  footprint (the owner asked for 25°).
- Folded, leg and knuckles stand 3 mm proud: the frame hangs 3 mm off the wall (accepted by the owner).
- Verified by sweeping the leg 0–50° against the back plate in CadQuery: free to 45°, contact from 46°.

Sources: [[requirements-2026-10-13]]
