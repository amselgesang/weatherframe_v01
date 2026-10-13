---
title: Open-Meteo API
type: entity
sources:
  - firmware/weatherframe/weatherframe.h
related:
  - "[[esphome-firmware]]"
  - "[[wake-cycle]]"
created: 2026-10-13
updated: 2026-10-13
confidence: high
---
# Open-Meteo API

Free weather API without a key. One HTTPS request per wake (current, hourly, daily; `timezone=auto`),
response up to 8 kB, parsed with ArduinoJson into an RTC-memory cache so a failed fetch still shows the
last forecast. Used by the [[esphome-firmware]].
