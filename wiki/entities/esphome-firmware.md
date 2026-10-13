---
title: ESPHome firmware
type: entity
sources:
  - firmware/weatherframe_ee05.yaml
  - firmware/weatherframe/common.yaml
related:
  - "[[wake-cycle]]"
  - "[[seeed-ee05]]"
  - "[[open-meteo]]"
created: 2026-10-13
updated: 2026-10-13
confidence: high
---
# ESPHome firmware

`firmware/weatherframe_ee05.yaml` (current, [[seeed-ee05]]) and `firmware/weatherframe.yaml`
(archived, [[custom-pcb-r1]]) share `weatherframe/common.yaml` (Open-Meteo fetch, fonts, render
lambda) and `weatherframe/weatherframe.h` (parser, RTC cache, layout). `preview.yaml` renders the screen
on the Mac (SDL).

- ESP-IDF framework, PSRAM octal; validated with ESPHome 2026.9.1 (needs Python ≥ 3.11).
- Inter fonts (Google Fonts) + Material Design Icons, 1-bit glyph tables.
- Behaviour: [[wake-cycle]]. Keys on the EE05: KEY1 refresh (also from deep sleep, ext1 wake),
  KEY2 maintenance mode (awake for OTA/logs/Home Assistant, auto-off after 30 min).
- Wi-Fi credentials in `secrets.yaml` (git-ignored). A fallback hotspot for changing Wi-Fi without a
  computer was offered, not built.
