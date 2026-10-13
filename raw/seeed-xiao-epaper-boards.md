# Clipping: Seeed Studio wiki, XIAO ePaper display boards (read 2026-10-13)

Sources:
- https://wiki.seeedstudio.com/epaper_ee05
- https://wiki.seeedstudio.com/epaper_ee04/
- https://wiki.seeedstudio.com/xiao_epaper_display_board_overview/
- https://wiki.seeedstudio.com/EE04_with_esphome_advanced
- https://openelab.io/pl/products/seeed-studio-xiao-epaper-board-ee05

EE05: XIAO ESP32-S3 Plus; 24-pin SPI FPC (0.5 mm); supported panels include 7.5" monochrome 800 × 480
(Seeed GFX combo 502, UC8179); JST 2.0 mm battery connector with hardware slide switch; power from 3.7 V
Li battery or USB-C; 1 reset + 3 side-mounted user buttons; built-in battery level detection;
"effectively controls or shuts down peripheral power consumption during MCU sleep"; extension IO port.
OpenELAB: €12.95, 52 × 27 mm, ships with a 24-pin adapter + FFC extension cable and a 2.4 GHz FPC antenna.

EE04 (same XIAO base): battery voltage on GPIO1 (A0), measured with GPIO6 (A5) driven high; example
scales the ADC reading by 7.16 (divider ratio not documented); user keys active-low on GPIO2, GPIO3,
GPIO5; 24-pin and 50-pin FPC selected by jumper.

ESPHome cookbook (EE0x): `spi: clk_pin GPIO7, mosi_pin GPIO9`; display `waveshare_epaper` model
`7.50inv2`, `cs_pin GPIO44`, `dc_pin GPIO10`, `busy_pin GPIO4`, `reset_pin GPIO38`.

EN04 / EN05: XIAO nRF52840 Plus (Bluetooth only, no Wi-Fi) — not suitable.
