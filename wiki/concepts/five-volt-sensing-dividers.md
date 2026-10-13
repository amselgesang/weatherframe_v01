---
title: Sensing 5 V signals on the ESP32-S3
type: concept
sources:
  - hardware/kicad/weatherframe/gen/design.py
related:
  - "[[custom-pcb-r1]]"
created: 2026-10-13
updated: 2026-10-13
confidence: high
---
# Sensing 5 V signals on the ESP32-S3

The ESP32-S3 is not 5 V tolerant (absolute max 3.6 V) and reads logic high only above 0.75 × 3.3 V =
2.475 V. A 100 k/100 k divider gives 2.5 V from 5 V — on the threshold, undefined at a 4.75 V supply.
100 k/150 k gives 3.0 V (2.85–3.15 V over 4.75–5.25 V). Applied to R6/R11 on the [[custom-pcb-r1]].
