---
title: JLCPCB Economic vs Standard assembly
type: concept
sources:
  - raw/jlcpcb-assembly-message-2026-10-13.md
related:
  - "[[jlcpcb]]"
  - "[[custom-pcb-r1]]"
  - "[[custom-pcb-vs-ee05]]"
created: 2026-10-13
updated: 2026-10-13
confidence: high
---
# JLCPCB Economic vs Standard assembly

Economic PCBA is cheap but refuses some parts; on 2026-10-13 it refused the ESP32-S3-WROOM-1 module
(package/temperature limits). Standard PCBA accepts it but costs $25 setup per side and requires each
board side ≥ 70 mm with edge rails — JLC proposed 74 × 70 mm for the 64 × 46 mm [[custom-pcb-r1]].
Rails on all sides clash with parts that overhang an edge (the module's antenna, about 6 mm; USB-C).
A design meant for Standard assembly should keep the antenna inside the outline over a copper keep-out
and be panelised so rails only touch edges without overhangs.

Sources: [[jlcpcb-assembly-message]]
