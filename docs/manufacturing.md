# Weather Frame — Manufacturing & Ordering Guide

2026-10-13 · Tamas Marton · editable original: Claude Docs "Weather Frame — Manufacturing & Ordering Guide" · PDF: `Weather_Frame_Manufacturing_Guide.pdf`

## Shopping list

Two orders cover everything, and nothing needs soldering: a ready-made Seeed EE05 board that plugs straight into the panel, and the frame at JLC3DP. There is no PCB order any more. Budget about €13 for the EE05, €15–20 for the battery, €60–90 for the frame, plus a few euros of screws and shipping.

| Item | Qty | Spec | Where |
| --- | --- | --- | --- |
| Seeed Studio XIAO ePaper Display Board EE05 | 1 | XIAO ESP32-S3 Plus, 24-pin FPC for the panel, JST 2.0 mm battery socket with charger and slide switch, 3 buttons; ships with a 24-pin extension cable and a Wi-Fi antenna | [OpenELAB](https://openelab.io/pl/products/seeed-studio-xiao-epaper-board-ee05), Seeed Studio |
| LiPo cell | 1 | 1S 3.7 V, **605080** (6 × 50 × 80 mm), 3000 mAh, with protection PCB and JST-PH 2.0 mm plug | Amazon / eBay / Eckstein / Berrybase |
| Frame bezel + back plate + stand | 1 each | STL files from `hardware/mechanical/export/` (EE05 version follows, see below) | JLC3DP |
| Screws, back plate | 4 | M3 × 10 mm self-tapping screws for plastic | hardware shop |
| Stand hinge pin | 1 + 1 | M3 × 40 mm screw + M3 nyloc nut | hardware shop |
| Screws, board holder | 2 | M2 × 6 mm self-tapping for plastic | hardware shop |
| Foam tape | 1 roll | 1 mm thick, 3–5 mm wide, double-sided (EVA or PE) for the six panel pads | hardware shop |
| Wall screws | 2 | any Ø 3.5–4 mm head ≤ Ø 8 mm, 90 mm apart | hardware shop |
| USB-C cable | 1 | any USB-C charging cable | existing |

You already have the Waveshare 7.5" e-paper panel. Its e-Paper Driver HAT and 8-wire cable are not needed with the EE05; keep them as spares.

Not needed any more: heat-set inserts (the EE05 version of the frame uses self-tapping screws, so no soldering iron is involved), the JLCPCB board order, and any Raspberry Pi parts.

## Electronics: Seeed EE05 instead of the custom PCB

The custom board cannot be ordered fully assembled in JLCPCB's Economic service: the ESP32-S3 module is restricted to Standard assembly, which adds a $25 setup fee and break-off rails that clash with the module's antenna overhang. Since no soldering is possible, the electronics are now one ready-made board, the Seeed XIAO ePaper Display Board EE05. It replaces both the custom PCB and the Waveshare driver HAT. The custom PCB design stays in `hardware/kicad/` in case it is ever revised for Standard assembly.

| Function | Custom PCB (archived) | EE05 |
| --- | --- | --- |
| Microcontroller | ESP32-S3-WROOM-1 | XIAO ESP32-S3 Plus, external Wi-Fi antenna |
| Panel connection | Waveshare HAT + 8-wire cable | 24-pin ribbon straight into the board |
| Battery | JST-PH socket, MCP73831 charger | JST 2.0 mm socket, built-in charger, slide switch |
| Panel power in sleep | switched off (P-FET) | switched off (GPIO43) |
| Buttons | reset, boot, refresh, MAINT switch | reset + 3 keys: KEY1 refresh, KEY2 maintenance mode |
| Indoor temperature / humidity | SHT40 | none; the screen shows tomorrow's forecast in that spot |
| Cost | about €100 for 2 assembled boards | about €13 |

## JLC3DP frame order

**Hold this order for now.** The current STL files still carry the mounts for the custom PCB and the Waveshare HAT. The EE05 version (a holder for the 52 × 27 mm board, openings for its USB-C, power switch and buttons, self-tapping screw bosses instead of heat-set inserts) follows once the board's exact connector and button positions are confirmed. The print settings below stay the same.

On jlc3dp.com (or *3D Printing* in the JLCPCB menu) upload `hardware/mechanical/export/bezel.stl`, `back.stl` and `stand.stl` as three items in the same order (the stand in the same material and colour as the bezel). Order the back plate first if you want a cheap fit test: it is the part everything has to fit on, and it is the easier of the two to re-print after a change.

| Option | Bezel | Back plate |
| --- | --- | --- |
| File | `bezel.stl` (192.8 × 131.5 × 21 mm, 59 cm³) | `back.stl` (192.8 × 131.5 × 19 mm, 86 cm³) |
| Technology | **MJF** (recommended) or SLA | MJF |
| Material | PA12 nylon (MJF) — or 9000R resin for SLA | PA12 nylon |
| Colour / finish | **White**: SLA 9000R white for the smoothest face, or MJF in white / dyed white | same as the bezel (the edges show from the side) |
| Quantity | 1 | 1 |
| Surface | standard; for a smoother face order "vapor smoothing" if offered | standard |
| Build orientation | leave automatic, or note "front face down" in the remarks | automatic |

Why MJF: it is strong enough at 2.5 mm walls, has no support marks (the bezel face stays clean), holds the 0.4 mm panel clearance within its ±0.3 % tolerance, and nylon takes heat-set inserts well. SLA gives a glossier front but needs supports on the inside and is more brittle around the inserts.

If you print at home instead: FDM with 0.2 mm layers, bezel face down on the bed (the chamfer prints clean), back plate inner side up, 3 perimeters, no supports needed on either part. PETG is a better choice than PLA for a frame near a window.

## Assembly after delivery

Total hands-on time is about 30 minutes with a screwdriver; nothing is soldered. Set up and test the electronics on the table (steps 1–4) before anything goes into the frame.

1. **Battery polarity.** Compare the cell's plug with the + / − marking at the EE05's BAT socket before plugging it in: red must go to +. JST battery leads are not standardised — if it is reversed, lift the two metal contacts out of the plastic housing with a needle and swap them, or exchange the cell. A reversed cell damages the charger.
2. **Panel.** Open the latch of the EE05's 24-pin connector, slide the panel's ribbon in (contacts as marked on the board), close the latch. If the board sits farther from the panel than the ribbon reaches, use the extension cable and adapter that come with the EE05.
3. **Antenna.** Click the Wi-Fi antenna onto the small round socket of the XIAO module.
4. **Flash and test** (next section) with the battery switch off and USB-C plugged in. The panel should show the forecast within a minute.
5. **Panel into the bezel.** Lay the bezel face down, drop the panel into the recess active side down with the ribbon toward the wider bottom rim, and fold the ribbon over the bottom edge of the glass.
6. **Back plate.** Stick 1 mm foam tape onto the six press pads. Put the EE05 into its holder (USB-C toward the side opening) and fix it with the two M2 screws, lay the battery in its pocket and plug it in, and connect the panel ribbon.
7. **Close.** Lower the back plate onto the bezel, check that USB-C, power switch and buttons line up with their openings, and drive in the four M3 self-tapping screws until snug, not tight.
8. **Switch on** the battery with the EE05's slide switch.
9. **Stand.** Put the leg's knuckle between the two hinge knuckles, push the M3 × 40 screw through and tighten the nyloc nut until the leg holds by friction. It opens to its stop at 45°; the frame then leans back 25°. A felt pad under the foot stops it sliding.
10. **Or hang it.** Fold the leg flat. Two screws 90 mm apart, heads about 6 mm proud of the wall; hook the keyholes and slide down.

## Firmware flashing and first start

The EE05 uses its own configuration, `firmware/weatherframe_ee05.yaml`; the screen layout is shared with the custom-PCB version. The first flash goes over USB-C; later updates go over Wi-Fi while maintenance mode is on.

1. On the Mac: `cd firmware`, then check `secrets.yaml` (Wi-Fi name, password and an OTA password of your choice).
2. Connect the EE05 by USB-C and run `esphome run weatherframe_ee05.yaml`, choosing the USB port. If no port appears, hold the small BOOT button on the XIAO module while plugging the cable in. The first build downloads ESP-IDF and takes 5–10 minutes.
3. The log should show the battery voltage, Wi-Fi joining, the Open-Meteo request and a panel refresh, then "entering deep sleep" — within 90 s.
4. **Calibrate the battery reading once:** measure the battery with a multimeter and compare it with "Battery voltage" in the log. If they differ, set `battery_divider` to (multimeter ÷ log) × 2.0 and flash again. A reading outside 2.8–4.5 V is ignored, so a wrong value can never lock the frame into low-battery mode.
5. **Buttons:** KEY1 refreshes immediately (also from deep sleep). KEY2 switches maintenance mode on: the frame stays awake for OTA updates, logs and Home Assistant, and goes back to sleep after another KEY2 press or after 30 minutes.

Settings worth changing before the first flash are all in the `substitutions` block of `weatherframe_ee05.yaml`: `location_name`, `latitude`, `longitude`, `german`, `fahrenheit`, `interval_s`, `quiet_start` / `quiet_end`, `battery_divider`, and `maint_timeout_min`.
