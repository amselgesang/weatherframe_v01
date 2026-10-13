---
title: Weather Frame — overview
type: overview
sources:
  - raw/requirements-2026-10-13.md
related:
  - "[[seeed-ee05]]"
  - "[[frame]]"
  - "[[esphome-firmware]]"
  - "[[custom-pcb-vs-ee05]]"
created: 2026-10-13
updated: 2026-10-13
confidence: high
---
# Weather Frame — overview

A battery-powered weather station built into a white wall picture frame: a [[waveshare-7in5-v2-panel]]
shows time, date, current weather, an hourly chart and a 5-day forecast for Budapest from
[[open-meteo]], refreshed every 15 minutes over Wi-Fi ([[wake-cycle]]). The frame hangs on two
keyholes or stands on a cupboard on a [[flip-out-stand]].

## Current state (2026-10-13)

- **Electronics:** [[seeed-ee05]] (XIAO ESP32-S3 Plus) plugged straight into the panel ribbon, with a
  [[lipo-605080]] battery. No soldering anywhere ([[no-solder-build]]). The [[custom-pcb-r1]] and the
  [[waveshare-epaper-driver-hat]] are archived — see [[custom-pcb-vs-ee05]] for why.
- **Firmware:** [[esphome-firmware]], `firmware/weatherframe_ee05.yaml`; validates with ESPHome
  2026.9.1, not yet compiled on hardware.
- **Frame:** [[frame]] (bezel, back plate, stand), white, built from `frame_geom.py` in CadQuery and
  in Fusion 360 through the [[fusion-360-mcp]]. Still carries the mounts for the archived PCB and HAT;
  the EE05 holder is the next step.
- **Manufacturing:** frame at [[jlcpcb]]'s JLC3DP; electronics bought ready-made.

## Open items

- Adapt the back plate to the EE05 (holder, USB-C/switch/button openings, self-tapping screw bosses)
  once the board is measured.
- Verify the EE05 battery and button pins on the real board and calibrate `battery_divider`
  ([[seeed-ee05]], confidence medium).
- First fit print of the back plate and the stand.

Sources: [[requirements-2026-10-13]]
