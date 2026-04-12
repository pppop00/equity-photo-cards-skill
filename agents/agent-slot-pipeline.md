# Agent Slot Pipeline (overview)

**Only supported path:** validators and renderer require **`--slots`** and a **complete** `card_slots.json`. There is no CLI-supported heuristic-only export.

End state: six PNGs with **human-grade** Chinese copy **without** losing facts from the research HTML.

## Roles

| Stage | Agent | Input | Output |
|-------|--------|--------|--------|
| A | Logo production | Company name / ticker + web search | Clean regenerated logo asset + `logo_asset_path` |
| B | Content production | Report HTML + `financial_*.json` + `porter_analysis.json` + logo path | `card_slots.json` (draft) |
| C | Layout fill | `card_slots.json` + design-spec + validation rules | `card_slots.json` (passes Validator 1) |
| D | Validator 2 | Final `card_slots.json` + HTML + sibling JSON + web search | Same files, **externally fact-checked** (see [validator-2-agent.md](./validator-2-agent.md)) |
| — | Renderer | HTML + final `card_slots.json` | `output/<stem>/*.png` |

Store **`card_slots.json` alongside** `Company_Research_CN.html` in the report workspace (e.g. `Amazon_Research_CN.card_slots.json`) so each package is self-contained.

## Why these stages

- **Agent A** optimizes for *logo quality*: search official web sources and regenerate a clean logo asset; no screenshots or local auto-discovery; export **SVG / high-res PNG** so wide wordmarks are **≥840 px** wide (validator rejects tiny or upscaled rasters).
- **Agent B** optimizes for *substance*: lift thesis, Porter paragraphs, risks, and KPIs from the HTML; no pixel math.
- **Agent C** optimizes for *constraints*: line wraps, character budgets, mandatory “human voice” markers on Card 6, judgement box height — without watering down meaning.
- **Stage D (Validator 2)** is not layout: it is a **web fact-check** of everything that will appear on the cards; see [validator-2-agent.md](./validator-2-agent.md). Run only after **Validator 1** passes.

## Commands

**Order:** Validator 1 → **Validator 2** (agent; no CLI) → export.

```bash
python3 scripts/validate_cards.py --input "/path/Company_Research_CN.html" --slots "/path/Company_Research_CN.card_slots.json" --brand "金融豹"
# … Validator 2: follow validator-2-agent.md (web search every factual claim) …
python3 scripts/generate_social_cards.py --input "/path/Company_Research_CN.html" --slots "/path/Company_Research_CN.card_slots.json" --brand "金融豹" --palette default
```

HTML still supplies Sankey numbers, tables, and company metadata. The logo is supplied only through `card_slots.logo_asset_path`, produced by the logo production agent. JSON slots override copy fields and may also set `porter_scores` (five integers).
