---
title: Fusion 360 MCP connector
type: entity
sources:
  - hardware/mechanical/frame_fusion360.py
related:
  - "[[parametric-cad-pipeline]]"
  - "[[frame]]"
created: 2026-10-13
updated: 2026-10-13
confidence: high
---
# Fusion 360 MCP connector

Autodesk's MCP server for Fusion (`http://127.0.0.1:27182/mcp` on the Mac). Not reachable from the
session's shell VM directly; works once added as a connector in the Claude desktop app. Tools: execute
Python scripts in Fusion (`run(context)` entry point), read screenshots, documents, API docs, undo/redo.
`editImage` (AI rendering) is not available for this client.

Scripts are refused while a Fusion command dialog (e.g. Press Pull) is open. Large scripts are best
loaded from the project folder with `importlib` instead of pasted (see [[parametric-cad-pipeline]]).
