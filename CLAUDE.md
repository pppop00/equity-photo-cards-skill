# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A deterministic agent skill that converts **equity research HTML + sibling JSON** into **six fixed-layout social cards** (PNG, 2160×2700). The only output path is:

`card_slots.json` → `validate_cards.py` (Validator 1) → Validator 2 (web fact-check) → `generate_social_cards.py`

The renderer has no fallback copy generation. `--slots` is required on both scripts and incomplete JSON is rejected at load time.

## Python environment

```bash
pip install beautifulsoup4 pillow
# Font: requires Arial Unicode at /System/Library/Fonts/Supplemental/Arial Unicode.ttf (macOS)
```

Python 3.9+. Use `.venv/` (already present in repo root).

## Input convention

Preferred input is a report folder containing `*_Research_CN.html` + sibling JSON (`financial_data.json`, `financial_analysis.json`, `porter_analysis.json`, etc.). **Read JSON first** — it is the canonical source for numeric facts, margins, segments, cash flow, and Porter details. Read HTML second for identity/date, rendered prose, embedded chart variables (`sankeyActualData`), and the render scaffold. If only HTML is provided, look for sibling JSON in the same folder. If only JSON, use it for analysis but do not export PNGs until the HTML is located.

## P0 gates (enforced in scripts)

- **Palette:** `validate_cards.py` and `generate_social_cards.py` require the P0-confirmed `--palette` (`macaron|default|b|c`). Do not omit it or assume `macaron`.
- **Logo:** `validate_cards.py` / export **fail** if `card_slots.json` has no `logo_asset_path`, unless `--allow-no-logo` is passed (customer explicitly waived logo).

## Commands

Run `validate_cards.py` from the **repository root** so `scripts/` imports resolve. `generate_social_cards.py` may be run from any directory; PNGs default to `output/<stem>/` relative to the script.

```bash
# Validate (Validator 1)
python3 scripts/validate_cards.py \
  --input "/abs/path/Company_Research_CN.html" \
  --slots "/abs/path/Company_Research_CN.card_slots.json" \
  --brand "金融豹" \
  --palette <confirmed_palette>

# Render (pass the same P0-confirmed --palette used for validation)
python3 scripts/generate_social_cards.py \
  --input "/abs/path/Company_Research_CN.html" \
  --slots "/abs/path/Company_Research_CN.card_slots.json" \
  --brand "金融豹" \
  --palette <confirmed_palette>

# Batch (--slots must be a directory containing <stem>.card_slots.json per HTML)
python3 scripts/generate_social_cards.py \
  --input "/abs/path/reports/" \
  --slots "/abs/path/reports/" \
  --brand "金融豹" \
  --palette <confirmed_palette>

# Override output directory
python3 scripts/generate_social_cards.py ... --output-root /other/path

# Export at logical size instead of 2×
python3 scripts/generate_social_cards.py ... --export-logical-size

# Skip copying card_slots.json into output/<stem>/
python3 scripts/generate_social_cards.py ... --no-copy-slots
```

## Architecture

### Pipeline stages (strict order)

0. **Palette record** — record customer- or `USER.md`-confirmed `macaron` | `default` | `b` | `c`; stop if none is available
1. Ingest report package (`*_Research_CN.html` + sibling JSON: `financial_data.json`, `financial_analysis.json`, `porter_analysis.json`)
2. Extract → Normalize → Plan card slots → Logo production (web search; ≥840 px wide)
3. Content production agent → Layout fill agent → write `<stem>.card_slots.json` beside HTML
4. Hardcode/logic audit
5. Validator 1: `validate_cards.py` — structure, layout, internal consistency
6. Validator 2: web fact-check all material numbers; fix slots and repeat from step 5 until both pass
7. Export: `generate_social_cards.py` with the same `--palette` used by Validator 1

### Key files

| File | Role |
|------|------|
| `SKILL.md` | Pipeline contract and palette gate (entry point for the agent skill) |
| `references/workflow-spec.md` | Canonical slot schema and pipeline contract — update here first when pipeline changes |
| `references/design-spec.md` | Visual rules, copy character budgets, prohibited elements — update here first when layout rules change |
| `references/card-slots.schema.json` | Machine schema for `*.card_slots.json` |
| `references/templates/card_slots.template.json` | Starter template; copy to `<stem>.card_slots.json` for each report |
| `references/examples/pdd_holdings_card_slots.example.json` | Worked example |
| `scripts/generate_social_cards.py` | Renderer: parses HTML, applies palette, draws all 6 cards |
| `scripts/validate_cards.py` | Validator 1 wrapper (imports from `generate_social_cards`) |
| `agents/` | Sub-agent briefs (content-production, layout-fill, logo-production, hardcode-audit, validation, validator-2) |
| `evals/evals.json` | Smoke prompts for skill evaluation |

### Renderer internals

- Logical canvas: 1080×1350. `LAYOUT_SCALE=2` → internal buffer 2160×2700.
- `apply_palette(name)` in `generate_social_cards.py` switches all global color vars. Must be called once before rendering.
- `macaron` is one available visual system: warm cream canvas, dark header band, pastel accent strips. `default` and `b` use light headers; `c` uses a dark header. All six cards in one report **must** use the same P0-confirmed palette; palette is **not** stored in `card_slots.json`.
- `assert_card_slots_complete` runs at slot load time; missing required keys abort execution.
- `validate_cards.py` imports `load_card_slots`, `parse_html`, `resolve_slots_path`, `set_currency_label`, `validate_report` directly from `generate_social_cards`.

### Logo save order (mandatory)

1. Determine the final output folder for the 6 PNGs — create it now if it does not exist.
2. Save `logo_official.png` **directly into that output folder** (not the source report folder, not a temp path).
3. Set `logo_asset_path` in `card_slots.json` to the logo's absolute path inside the output folder.
4. Only then proceed through normalization, card planning, and copy generation.

This ensures the logo and PNGs are always co-located for handoff.

### Fixed card roles

| # | File | Content |
|---|------|---------|
| 1 | `01_cover.png` | Cover + core tension + logo |
| 2 | `02_background_industry.png` | Background + industry + Porter |
| 3 | `03_revenue.png` | Revenue/profit flow (data-forward) |
| 4 | `04_business_outlook.png` | Current business + next 2–3 years |
| 5 | `05_brand.png` | Brand close + three memory points |
| 6 | `06_post_copy.png` | Social post copy (贴吧 tone, exactly 3 statements + 1 question; title starts with `一天吃透一家公司：`; hashtags must include `#A股` and `#美股`) |

### Slot file convention

- Named `Company_Research_CN.card_slots.json`, placed **beside** `Company_Research_CN.html` in the report folder.
- `generate_social_cards.py` copies it into `output/<stem>/` alongside PNGs by default (skip with `--no-copy-slots`).
- `--slots` accepts: JSON file path, the containing folder (single HTML), or a directory of per-stem JSONs (batch mode).

### Single-card re-render trap

If re-running only one card (e.g. updating `01_cover.png`), use **the same `--palette`** as the original full set. The palette is applied in-process by `apply_palette()` and is **not stored** in `card_slots.json` — Validator 1 and 2 cannot detect a mismatch. Mixing palettes causes the re-rendered card's header to differ visually from the other five.

## When to change code

Only change `generate_social_cards.py` or `validate_cards.py` when:
- upstream HTML or sibling JSON schema changed
- normalization cannot recover a required field
- a new business model repeatedly fails the same card planner
- a systematic formatting gap should become an explicit validation rule

Do not patch the scripts for a single company's copy.
