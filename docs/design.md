# Weather Frame — Design Documentation

2026-10-13 · Tamas Marton · editable original: Claude Docs "Weather Frame — Design Documentation" · PDF with diagrams: `Weather_Frame_Design_Documentation.pdf`

## Overview

**Change of electronics, 13 Oct 2026:** JLCPCB can only place the ESP32-S3 module with Standard assembly, and the build has to work without any soldering. The electronics are therefore now a ready-made Seeed XIAO ePaper Display Board EE05 (ESP32-S3, 24-pin panel connector, battery charger), which replaces both the custom PCB and the Waveshare driver HAT. The firmware runs on it as `weatherframe_ee05.yaml`. The custom-PCB sections below remain as the design record for a possible later revision; the frame is being adapted to the EE05.

The Weather Frame is a battery-powered weather station built into a wall picture frame: a Waveshare 7.5" e-paper panel (800 × 480, 4-level grayscale) shows the current weather, an hourly chart and a 5-day forecast for Budapest, refreshed every 15 minutes from Open-Meteo over Wi-Fi. It runs for about two months on one charge of a 3000 mAh LiPo and charges over USB-C.

Requirements the design was built against:

- Looks like a picture frame on the wall: no visible cables, no visible electronics, hangs on two screws; a fold-out stand lets it stand on a cupboard instead.
- Rechargeable: 1S LiPo inside, charged over USB-C, no power supply on the wall.
- Wi-Fi only; no hub or server needed. Weather data straight from the Open-Meteo API.
- Indoor temperature and humidity on the display as well (SHT40 on the board).
- Manufacturable from one vendor: PCB and assembly at JLCPCB, frame parts at JLC3DP, no hand-placed SMD parts.
- German labels, metric units, quiet hours at night; all of this is configuration, not code.

The project has three parts, each generated from one source file so they stay consistent:

| Part | Source of truth | Output |
| --- | --- | --- |
| Main PCB (64 × 46 mm, ESP32-S3) | `hardware/kicad/weatherframe/gen/design.py` | KiCad schematic + board, JLCPCB Gerbers / BOM / CPL |
| Firmware | `firmware/weatherframe.yaml` + `weatherframe/weatherframe.h` | ESPHome build for the ESP32-S3 |
| Frame (bezel + back plate) | `hardware/mechanical/frame_geom.py` | Fusion 360 model, STEP / STL for printing |

## System architecture

The custom board is the only active electronics besides the Waveshare driver HAT: it owns power, charging, Wi-Fi and the sensor, and talks to the HAT over a 4-wire SPI cable. The HAT stays as bought, because it carries the panel's high-voltage boost circuits and the 24-pin ZIF connector that would be hard to replicate and test on a first board.

*(Diagram: system architecture, see the PDF.)*

```
 e-paper panel --FPC--> Driver HAT Rev2.1 --SPI + 3.3 V--> Main board (ESP32-S3, charger, buck-boost, SHT40)
                                                              ^ VBAT              ^ VBUS
                                                        LiPo 605080           USB-C (side wall)
 Wi-Fi / Open-Meteo API <-------------------------------------+
```

The panel's ribbon folds round the bottom edge of the glass into the HAT, which sits behind the glass on four standoffs; the custom board sits behind the right side of the glass with its USB-C port in the frame's side wall, and the battery lies flat behind the upper left.

## Electronics design decisions

Every part is in JLCPCB's assembly catalogue, with "basic" parts wherever a basic part would do, so the board can be assembled without hand soldering. Only J3 (the HAT cable) and the four mounting holes are left unpopulated.

| Block | Decision | Why |
| --- | --- | --- |
| MCU | ESP32-S3-WROOM-1-N16R8 module, ESP-IDF framework | Native USB for flashing without a UART bridge, 8 MB PSRAM for the 800 × 480 frame buffer and fonts, module with a certified antenna; the antenna end overhangs the board edge as the datasheet asks. |
| 3.3 V rail | TPS63001 buck-boost, 1.5 µH, 2 × 22 µF out | A LiPo swings from 4.2 V to 3.0 V and USB is 5 V; a buck-boost holds 3.3 V over the whole range, so the panel and the radio behave the same at a full and at an empty battery. PS/SYNC is tied low for power-save mode, which keeps the quiescent current low during deep sleep. |
| Charger | MCP73831-2, PROG = 2 kΩ → 500 mA | Simple, single-cell, cheap; 500 mA charges a 3000 mAh cell in about 7 hours and is well below the 0.5 C limit of a 605080 pouch. A red LED on STAT shows charging. |
| Load sharing | B5819W Schottky from VBUS plus AO3401A P-FET from VBAT | When USB is present the diode feeds the regulator and the FET's gate is pulled high, so the battery is not loaded while it charges; without USB the FET conducts and bypasses its own body diode. Standard "ideal diode" arrangement with two cheap parts. |
| USB-C | HRO TYPE-C-31-M-12 (16-pin), 5.1 kΩ on CC1/CC2, USBLC6-2SC6 ESD | The 5.1 kΩ pull-downs make a USB-C charger supply 5 V; D+/D− go to the ESP32-S3's native USB for flashing. The USBLC6 protects the data lines against ESD at the port. |
| Battery sensing | 1 MΩ / 1 MΩ divider with 100 nF into GPIO5 (ADC) | The divider halves 4.2 V to 2.1 V, inside the 12 dB attenuation range; 1 MΩ keeps the standing drain at 2 µA, and the capacitor gives the ADC a low-impedance source. |
| USB and charge status | 100 kΩ / 150 kΩ dividers into GPIO4 and GPIO15 | The ESP32-S3 is not 5 V tolerant; 5 V → 3.0 V stays above the 2.475 V logic-high threshold and below the 3.6 V absolute maximum across the 4.75–5.25 V USB range. |
| E-paper power | AO3401A P-FET on the HAT's 3.3 V, 100 kΩ pull-up, driven by GPIO6 | The HAT draws current even when idle; switching it off in deep sleep is the single largest contribution to the two-month runtime. The pull-up keeps it off while the ESP32 is in reset or asleep. |
| Indoor sensor | SHT40-AD1B on an isolated corner tab with a thermal slot, 4.7 kΩ I²C pull-ups | The ESP32 and the regulator warm the board by a degree or two; the slotted tab and no copper pour around the sensor keep it near room temperature. The firmware reads it before Wi-Fi starts for the same reason. |
| Controls | RESET and BOOT tactile switches, REFRESH button on GPIO13 (RTC wake), MAINT slide switch on GPIO14 | REFRESH wakes the device from deep sleep for an immediate update; MAINT keeps it awake so OTA updates and logs work without timing a 90-second window. |
| HAT connector | J3, 1 × 9 header footprint, hand-soldered | Kept as plain 2.54 mm holes so any cable can be used; in the frame the HAT's 8-wire cable is soldered in directly. |
| Board | 64 × 46 mm, 2 layers, 0.15 mm clearance, 0.2 mm tracks, 0.3 mm vias, M2.5 holes | Fits JLCPCB's standard 2-layer process with no extra-cost options; small enough to sit beside the HAT behind the glass. |

## Firmware design

The firmware is an ESPHome configuration (ESP-IDF framework, validated with ESPHome 2026.9.1) plus one C++ header for the Open-Meteo parsing and the screen layout. ESPHome was chosen over hand-written ESP-IDF code because it gives OTA updates, Wi-Fi handling, the e-paper driver, fonts and a Home Assistant API for free, and because the whole behaviour is readable in 220 lines of YAML.

*(Diagram: wake cycle, see the PDF.)* Wake (timer or REFRESH) → read SHT40 + battery → battery > 3.4 V? → Wi-Fi + SNTP (15 s) → fetch Open-Meteo, cache in RTC RAM → power the HAT, render, refresh → MAINT on? → yes: stay awake for OTA/logs · no: deep sleep to the next quarter hour. Low battery: skip Wi-Fi, show cached data, sleep 6 h.

Design choices that drive the battery life and the user experience:

- **Everything is time-boxed.** Wi-Fi gets 15 s, the clock 3 s, the HTTP request 10 s, the panel refresh 30 s, and `run_duration: 90s` is a hard ceiling. A failed step shows the cached data instead of waiting.
- **The weather is cached in RTC memory** across deep sleep, so a Wi-Fi outage keeps the last forecast on the screen with a "wifi-off" icon rather than a blank display.
- **Quiet hours.** `wf::next_sleep_ms()` aligns wakes to quarter hours and skips 00:00–06:00 (configurable), which saves about a quarter of the daily energy.
- **Low-battery mode** below 3.40 V without USB: no Wi-Fi, a battery-alert icon, and a 6-hour sleep so the cell is never deep-discharged.
- **Sensors first.** The SHT40 is read before Wi-Fi starts so the reading is not biased by the board warming up.
- **The panel is powered only while rendering** through the P-FET (`enable_pin` of the display component).
- **Rendering** uses Inter (Google Fonts) at four sizes with 1-bit glyph tables limited to the characters actually used, plus Material Design Icons for the weather symbols; the layout is shared with `preview.yaml`, which renders the same screen in an SDL window on the Mac for layout work without hardware.
- Location, language, units, interval and quiet hours are substitutions at the top of `weatherframe.yaml`; the pin map is listed there too and must match `design.py`.

## Mechanical design

The frame is three printed parts, 192.8 × 131.5 × 24 mm overall (27 mm including the folded stand), that screw together with four M3 screws into heat-set inserts: a **bezel** that holds the glass and a **back plate** that carries all the electronics, and a **fold-out stand** for standing it on a cupboard. The glass is clamped between the bezel's 2.5 mm lip and foam-backed press pads on the back plate, so no adhesive touches the panel and it can be replaced.

`frame_geom.py` is the single source: it expresses the whole design as a list of boxes, cylinders and slots in millimetres. The same list is built by CadQuery (STEP/STL, interference checks, previews) and by the Fusion 360 script, which was executed through the Fusion MCP connector; both produce identical volumes (bezel 59.4 cm³, back plate 86.2 cm³). Change a number in the `P` dict and re-run either.

| Element | Value | Reasoning |
| --- | --- | --- |
| Window | active area + 0.8 mm per side, 1 mm 45° chamfer | Shows the full image with a thin white panel border; the chamfer hides the print layer lines at the edge. |
| Panel recess | 170.2 × 111.2 mm + 0.4 mm clearance, 1.5 mm deep in a 4 mm face | Locates the glass in-plane; the active area is centred in the window although the panel's borders are 3.5 mm on three sides and 9.8 mm on the ribbon side. |
| Rim | 14 mm sides and top, 18 mm bottom | The bottom rim hides the ribbon fold and the HAT; 14 mm reads as a picture frame rather than a device. Outer corners R6. |
| Cavity | 17 mm deep, 2.5 mm walls | Set by the HAT: 7.5 mm standoffs, 1.6 mm board, 6 mm JST connector on top, 2.2 mm air to the glass. The 40-pin header on its back sinks 1.5 mm into the plate. |
| HAT mount | 4 × M2.5 standoffs, 58 × 23 mm (Pi-Zero pattern), ribbon edge 11.6 mm from the glass edge | Measured from the Rev2.1 board; the 24 mm ribbon has ~2 mm to spare after the fold and 3 mm insertion. |
| PCB mount | 4 × M2.5 standoffs 5 mm, components toward the plate | Puts the USB-C port in the right wall (wall thinned to 1 mm there so the plug seats), the MAINT lever under a slot and the three buttons under Ø3 holes in the plate. |
| Battery | 605080 pocket, 1 mm clearance, 3 mm fence with a lead gap | Lies flat behind the upper left; the fence stops it sliding onto the HAT or the pads. |
| Panel pads | 6 pads, 3 mm wide, topped with 1 mm foam | Placed on the panel borders where no electronics sit: top both sides of the keyholes, bottom both sides of the ribbon, lower left, upper right. |
| Hanging | 2 keyholes at x = ±45 mm, slot upward, 2 mm bosses inside | Two screws keep the frame level; the slot runs upward because the frame slides down onto the screw heads. |
| Vents | 5 slots over the SHT40 corner | Lets room air reach the sensor through the plate. |
| Flip-out stand | separate leg 60 × 75 × 3 mm, hinged 10 mm above centre on the back over 36.8 mm (three knuckles), M3 × 40 pin + nyloc, stop at 45° | Opens to 45° and stops there, so the frame stands on a cupboard leaning back 25° on its rear-bottom edge with a 59 mm footprint. Folded, leg and knuckles stand 3 mm proud, so on the wall the frame sits 3 mm off the wall. Swept 0–50° in CadQuery: free to 45°, contact from 46°; 2.5 mm of material behind the stop. |
| Labels | RESET, BOOT, MAINT engraved left of their openings and REFRESH right of its hole (as seen from behind), 3 mm bold, 0.5 mm deep | Buttons are pressed from outside with a pin through Ø3 mm holes; the labels make them findable without the docs. |
| Colour | white (SLA 9000R white or MJF dyed white/raw) | Chosen to sit quietly on a white woodchip wall. |
| Printing | all walls ≥ 1 mm, pockets ≥ 1.5 mm plate left, no overhangs on the plate | Suitable for MJF nylon or SLA at JLC3DP, or an FDM printer with the bezel face down. |

## Problems encountered and how they were resolved

All of these were found by review, simulation or geometry checks before anything was ordered; none required a board re-route.

| Area | Problem | Resolution |
| --- | --- | --- |
| Electronics | The USB-present and charger-status dividers were 100 kΩ / 100 kΩ: 5 V → 2.5 V, which sits on the ESP32-S3's logic-high threshold (0.75 × 3.3 V = 2.475 V) and reads as undefined on a 4.75 V supply. | Bottom resistors R6 and R11 changed to 150 kΩ (LCSC C25755): 5 V → 3.0 V, 2.85–3.15 V over the USB range. Same footprint, so only the values, the BOM and the schematic changed. |
| Electronics | The TPS63001 pin mapping in `design.py` had to be trusted blindly: FB tied to VOUT and VINA to VIN are easy to get wrong on this part. | Verified against the TI datasheet pin table and the KiCad library symbol extracted from the schematic: all ten pins are correct, PS/SYNC low = power-save. |
| Electronics | J3 was a vertical 2.54 mm header; with the board components facing the back plate, a header plus a cable housing needs ~14 mm, but only 5 mm exist. | The HAT's 8-wire cable is soldered directly into J3 for this revision; a right-angle JST-PH is noted for r2. |
| PCB | DRC reports 4 silkscreen-clipped warnings and 1 footprint mismatch. | Both are expected: the ESP32 antenna and the USB-C connector sit at the board edge by design, and the SHT40 footprint is a local copy without the central pad. 0 errors, 0 unconnected. |
| Firmware | The sandbox's ESPHome (2025.7) does not know the `epaper_spi` platform; a current one needs Python ≥ 3.11. | Installed ESPHome 2026.9.1 in a Python 3.12 venv with uv; the config validates. Google Fonts and the ESP-IDF download are blocked by the proxy, so fonts came from the cache of the earlier run and the compile is left to the Mac. |
| Tooling | The previous Claude Code session stopped when its API credit ran out, leaving no notes on where it stood; KiCad is only installed on the Mac and the Fusion MCP was not reachable from the shell. | State was reconstructed from file timestamps and reports; a `build.sh` was added so the KiCad pipeline is one command; the Fusion MCP connector was added to the desktop app, which made Fusion scriptable from the session. |
| Mechanical | First layout had the battery under a panel press pad, the PCB over a corner screw boss, and the keyholes inside the battery pocket. | Found by CadQuery interference checks between the printed parts and reference volumes; the battery moved above the HAT, the PCB up by 8 mm with the MAINT switch reached through a slot instead of the wall, keyholes moved to x = ±45 mm, y = 54 mm. |
| Mechanical | The panel recess was cut 1 mm into the cavity instead of into the face, leaving a 2 mm face. | Face thickness set to 4 mm with the 1.5 mm recess cut into it (2.5 mm lip). |
| Mechanical | The HAT's JST connector (6 mm tall) would have been 0.7 mm from the glass with the HAT on a fence. | HAT geometry re-measured from photos: four M2.5 holes, header on the far side from the ribbon. Four standoffs, the header pocketed 1.5 mm into the plate, cavity +1 mm → 2.2 mm clearance. |
| Mechanical | The ribbon length (24 mm) is tight for folding round the glass into the ZIF. | HAT ribbon edge placed 11.6 mm below the glass edge: fold + z-step + 3 mm insertion ≈ 21.6 mm. One parameter (`hat_center`) if it needs adjusting after the first fit. |
| Mechanical | The Waveshare spec PDF could not be downloaded through the proxy, and Chrome's PDF viewer could not be driven. | Read the mechanical drawing through the Google Docs viewer in the built-in browser; the border and ribbon dimensions in `frame_geom.py` come from that page. |
| Ordering | JLCPCB restricts the ESP32-S3 module to Standard assembly ($25 setup, break-off rails that clash with the antenna overhang), and the build must need no soldering. | Switched to a Seeed XIAO ePaper Display Board EE05, which plugs straight into the panel ribbon; firmware ported (`weatherframe_ee05.yaml`), frame holder to follow. |

## Open items and ideas for revision 2

Nothing below blocks ordering revision 1; the first three are checks to do when the parts arrive.

- [ ] Compile and flash the firmware on the real board; confirm the 15-minute cycle completes in under 90 s and measure the deep-sleep current (target under 100 µA with the HAT switched off).
- [ ] Fit check of the back plate: HAT on its standoffs, ribbon reach into the ZIF, battery in its pocket, USB-C plug seating through the side wall.
- [ ] Confirm the keyhole spacing (90 mm) against the wall screws and that the frame hangs plumb with the battery on the left.
- [ ] Battery lead: a 605080 cell usually comes with a 50–60 mm lead; J2 is about 80 mm away, so order the cell with a longer lead or add an extension.

Ideas for r2:

- Replace J3 with a right-angle JST-PH 8-pin so the HAT's cable plugs in; or move the HAT's boost circuit onto the main board and drive the panel's 24-pin ZIF directly, which would remove the HAT, 8 mm of thickness and the cable.
- A 2-pin JST-PH for the battery is standard but not polarised the same way by every supplier; a note on the silkscreen ("+ left") would prevent a reversed cell.
- Add a photoresistor or the SHT40's data to Home Assistant through the API while in MAINT mode.
- Consider 10 mm rims with a wood-look print finish once the first frame confirms the proportions.
