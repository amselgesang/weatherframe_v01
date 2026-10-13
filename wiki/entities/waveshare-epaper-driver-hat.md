---
title: Waveshare e-Paper Driver HAT Rev2.1
type: entity
sources:
  - raw/images/hat-front.jpg
  - raw/images/hat-back-ruler.jpg
related:
  - "[[custom-pcb-r1]]"
  - "[[frame]]"
created: 2026-10-13
updated: 2026-10-13
confidence: high
---
# Waveshare e-Paper Driver HAT Rev2.1 (archived)

Raspberry-Pi HAT that carries the panel's boost circuits and the 24-pin ZIF connector. Used with the
[[custom-pcb-r1]]; not needed with the [[seeed-ee05]], kept as a spare.

Measured from the owner's photos (`raw/images/`):
- 65 × 30.2 mm, four M2.5 holes in the Pi-Zero pattern 58 × 23 mm.
- 40-pin female header on the back, along the long edge **opposite** the ribbon connector, centre
  about 11.8 mm from the board centre (confirmed by the owner).
- Front: ZIF connector centred on one long edge, 8-pin JST PH side-entry (BUSY RST DC CS CLK DIN GND
  VCC), about 6 mm tall, on the other long edge; slide switches Display Config (set **B** for 7.5")
  and Interface Config (set **0** = 4-line SPI).

Sources: [[hat-photos]]
