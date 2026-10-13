#!/usr/bin/env bash
# Regenerate the KiCad project, run ERC/DRC and export JLCPCB files.
# Needs KiCad 9 (macOS app bundle) and, for a full re-route, Freerouting.
#
#   ./build.sh sch       schematic from gen/design.py
#   ./build.sh place     unrouted board + Specctra DSN (then route with Freerouting)
#   ./build.sh finish    import the .ses, pours, silkscreen -> weatherframe.kicad_pcb
#   ./build.sh check     ERC + DRC reports into build/
#   ./build.sh fab       Gerbers / BOM / CPL for JLCPCB into fab/
#   ./build.sh all       sch + check + fab (board already routed)
set -euo pipefail
cd "$(dirname "$0")"
KICAD_APP=${KICAD_APP:-/Applications/KiCad/KiCad.app}
KICAD_CLI="$KICAD_APP/Contents/MacOS/kicad-cli"
KICAD_PY="$KICAD_APP/Contents/Frameworks/Python.framework/Versions/Current/bin/python3"
export KICAD_CLI

case "${1:-all}" in
  sch)    python3 gen/gen_sch.py ;;
  place)  "$KICAD_PY" gen/gen_pcb.py place
          echo "Now route build/weatherframe.dsn with Freerouting and save build/weatherframe.ses" ;;
  finish) "$KICAD_PY" gen/gen_pcb.py finish ;;
  check)  mkdir -p build
          "$KICAD_CLI" sch erc --severity-all --exit-code-violations -o build/erc.rpt weatherframe.kicad_sch || echo "ERC: see build/erc.rpt"
          "$KICAD_CLI" pcb drc --severity-all -o build/drc.rpt weatherframe.kicad_pcb
          "$KICAD_CLI" pcb drc --severity-error --exit-code-violations -o build/drc_err.rpt weatherframe.kicad_pcb
          "$KICAD_CLI" pcb render --side top --quality basic -w 1600 -h 1200 -o build/render_top.png weatherframe.kicad_pcb
          grep -E "Found .* violations|unconnected" build/drc.rpt ;;
  fab)    python3 gen/export_fab.py ;;
  all)    "$0" sch; "$0" check; "$0" fab ;;
  *)      echo "usage: $0 {sch|place|finish|check|fab|all}"; exit 1 ;;
esac
