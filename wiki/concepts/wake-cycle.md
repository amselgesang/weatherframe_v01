---
title: Wake cycle and power budget
type: concept
sources:
  - firmware/weatherframe_ee05.yaml
related:
  - "[[esphome-firmware]]"
  - "[[lipo-605080]]"
  - "[[seeed-ee05]]"
created: 2026-10-13
updated: 2026-10-13
confidence: medium
---
# Wake cycle and power budget

Every 15 minutes, aligned to :00/:15/:30/:45, skipping 00:00–06:00: wake → read battery → Wi-Fi + SNTP
(15 s / 3 s timeouts) → [[open-meteo]] (10 s) → power the panel, render, refresh (30 s) → panel off →
deep sleep. `run_duration: 90s` is the hard ceiling. Below 3.40 V without USB: no Wi-Fi, a "please
charge" screen and 6-hour sleeps.

Battery life of about two months on a [[lipo-605080]] depends mainly on cutting panel power in sleep
(P-FET on the [[custom-pcb-r1]], GPIO43 on the [[seeed-ee05]]) and on the quiet hours (about a quarter of
the daily energy).
