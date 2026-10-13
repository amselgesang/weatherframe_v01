# Weather Frame — project schema for LLM agents

This repository is an e-paper weather station built as a wall picture frame. It is also an
**LLM-maintained wiki** following Andrej Karpathy's *LLM Wiki* pattern: knowledge is compiled once
into interlinked Markdown pages and kept current, instead of being re-derived from raw files on every
question. This file is the schema: it tells an agent (Claude Code or any other) how the project and
the wiki are organised and how to work on them. Humans and the agent refine it together.

## Repository layout

| Path | What it is | Who edits |
|---|---|---|
| `raw/` | Immutable source material: requirements, photos, vendor messages, datasheet clippings, code excerpts | Human adds; agent reads, **never edits** |
| `wiki/` | The knowledge base: entity, concept, source and comparison pages + `index.md` + `log.md` | Agent writes; human reads and corrects |
| `docs/` | Published outputs: design documentation, manufacturing guide (Markdown + PDF), images | Generated from the wiki and the design files |
| `firmware/` | ESPHome firmware (`weatherframe_ee05.yaml` = current hardware, `weatherframe.yaml` = archived custom PCB) | Code |
| `hardware/kicad/` | Archived custom PCB, generated from `gen/design.py` | Code |
| `hardware/mechanical/` | Frame (bezel, back plate, stand), generated from `frame_geom.py` | Code |

Secrets (`firmware/secrets.yaml`) are git-ignored and must never be copied into `raw/`, `wiki/` or `docs/`.

## Wiki conventions

- One Markdown file per page, kebab-case file names. Folders: `wiki/entities/` (things: parts, boards,
  vendors, tools), `wiki/concepts/` (ideas, mechanisms, design rules), `wiki/sources/` (one summary per
  file in `raw/`), `wiki/comparisons/` (option A vs B, decisions).
- YAML frontmatter on every page: `title`, `type` (entity | concept | source-summary | comparison |
  overview), `sources` (paths in `raw/` or repo files), `related` (`"[[page-name]]"`), `created`,
  `updated` (YYYY-MM-DD), `confidence` (high | medium | low).
- Link pages with `[[page-name]]` (file name without `.md`). Every claim should trace to a source page,
  a `raw/` file or a design file in the repo; mark unverified claims `confidence: low` and say so in the text.
- `wiki/index.md` is the catalog: every page, one line each, grouped by folder. Read it first.
- `wiki/log.md` is append-only. Each entry starts with `## [YYYY-MM-DD] <op> | <title>` where op is
  `ingest`, `decision`, `query`, `lint` or `change`, so `grep "^## \[" wiki/log.md | tail -5` shows recent activity.

## Workflows

**Ingest** (a new file in `raw/`, or a design change worth recording):
1. Read the source; note the key takeaways with the human if they are around.
2. Write `wiki/sources/<name>.md` summarising it.
3. Update every entity/concept page it touches (often several); create pages for new things.
4. If it changes a decision or a number, update `wiki/overview.md` and the affected comparison page.
5. Update `wiki/index.md`; append an `ingest` (or `decision`) entry to `wiki/log.md`.

**Query** (a question about the project):
1. Read `wiki/index.md`, then the relevant pages; fall back to `raw/` and the design files.
2. Answer with `[[wikilinks]]` as citations.
3. If the answer is worth keeping, file it as a page and log it as `query`.

**Lint** (periodically, or before an order):
- Check for contradictions between pages and with the design files (e.g. a dimension in a page that no
  longer matches `frame_geom.py`), stale claims, orphan pages, concepts mentioned without a page, and
  open questions. Write the result to `docs/lint-YYYY-MM-DD.md` and log it as `lint`.

**Design files are the ground truth for numbers.** When a page and `frame_geom.py`, `design.py` or a
firmware YAML disagree, the file wins and the page gets fixed.

## Building things

- Frame: `cd hardware/mechanical && python3 build_cadquery.py export` (STEP/STL), or run
  `frame_fusion360.py` in Fusion 360 (`build("WeatherFrame_rN")`).
- Firmware: `cd firmware && esphome run weatherframe_ee05.yaml`.
- Custom PCB (archived): `cd hardware/kicad/weatherframe && ./build.sh all`.
