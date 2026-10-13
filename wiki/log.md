# Wiki log

Append-only. Entry prefix: `## [YYYY-MM-DD] <op> | <title>` (op = ingest, decision, query, lint, change).
Recent activity: `grep "^## \[" wiki/log.md | tail -5`.

## [2026-10-13] change | Resumed the project after the previous Claude Code session stopped
State reconstructed from files: firmware, generated KiCad board and JLC fab files existed; no notes.

## [2026-10-13] ingest | TI TPS63001 pin table
Verified the custom PCB's buck-boost wiring. Pages: [[ti-tps63001-pins]], [[custom-pcb-r1]].

## [2026-10-13] change | R6/R11 changed to 150 kΩ
5 V sensing dividers moved off the logic threshold. Pages: [[five-volt-sensing-dividers]], [[custom-pcb-r1]].

## [2026-10-13] ingest | Waveshare 7.5" V2 mechanical drawing
Pages: [[waveshare-7in5-v2-mechanical]], [[waveshare-7in5-v2-panel]], [[frame]].

## [2026-10-13] change | Frame designed and built in Fusion through the MCP connector
Pages: [[frame]], [[parametric-cad-pipeline]], [[fusion-360-mcp]].

## [2026-10-13] ingest | HAT photos with ruler
HAT mounted on four standoffs; header pocket; cavity +1 mm. Pages: [[hat-photos]], [[waveshare-epaper-driver-hat]], [[frame]].

## [2026-10-13] decision | White frame, flip-out stand at 25° with 3 mm wall gap
Pages: [[flip-out-stand]], [[frame]].

## [2026-10-13] change | Engraved labels; hinge widened to 36.8 mm; stand widened to 60 mm
Pages: [[frame]], [[flip-out-stand]].

## [2026-10-13] ingest | JLCPCB assembly message
ESP32 module refused in Economic assembly. Pages: [[jlcpcb-assembly-message]], [[jlc-assembly-tiers]].

## [2026-10-13] decision | Switch to Seeed EE05 (no soldering)
Pages: [[custom-pcb-vs-ee05]], [[seeed-ee05]], [[no-solder-build]], [[overview]].

## [2026-10-13] ingest | Seeed XIAO ePaper board docs and Seeed_GFX pin definitions
Firmware ported to `weatherframe_ee05.yaml`. Pages: [[seeed-xiao-epaper-boards]], [[seeed-gfx-epaper-board-pins]], [[seeed-ee05]], [[esphome-firmware]].

## [2026-10-13] change | Wiki created (Karpathy LLM-wiki pattern) and project put under git
Pages: all; schema in `CLAUDE.md`.
