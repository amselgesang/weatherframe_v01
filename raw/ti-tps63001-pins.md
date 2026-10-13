# Clipping: TI TPS63001 datasheet, DRC (VSON-10) pin functions

Source: https://www.ti.com/lit/ds/symlink/tps63001.pdf (read 2026-10-13)

| Pin | Name | Function |
|---|---|---|
| 1 | VOUT | buck-boost output |
| 2 | L2 | inductor |
| 3 | PGND | power ground |
| 4 | L1 | inductor |
| 5 | VIN | power stage supply |
| 6 | EN | enable, high = on |
| 7 | PS/SYNC | low = power-save mode enabled; high = fixed frequency; clock input for sync |
| 8 | VINA | control stage supply |
| 9 | GND | control ground |
| 10 | FB | feedback; "must be connected to VOUT on fixed output voltage versions" |
| pad | — | exposed thermal pad, connect to PGND |
