# Agent Slot Pipeline (overview)

**Default for every new report:** this pipeline is how the skill is meant to run end-to-end. Rendering **without** `--slots` is a non-standard shortcut.

End state: six PNGs with **human-grade** Chinese copy **without** losing facts from the research HTML.

## Roles

| Stage | Agent | Input | Output |
|-------|--------|--------|--------|
| A | Content production | Report HTML + `financial_*.json` + `porter_analysis.json` (same folder) | `card_slots.json` (draft) |
| B | Layout fill | `card_slots.json` + design-spec + validation rules | `card_slots.json` (passes validator) |
| — | Renderer | HTML + final `card_slots.json` | `output/<stem>/*.png` |

Store **`card_slots.json` alongside** `Company_Research_CN.html` in the report workspace (e.g. `Amazon_Research_CN.card_slots.json`) so each package is self-contained.

## Why two layers

- **Agent A** optimizes for *substance*: lift thesis, Porter paragraphs, risks, and KPIs from the HTML; no pixel math.
- **Agent B** optimizes for *constraints*: line wraps, character budgets, mandatory “human voice” markers on Card 6, judgement box height — without watering down meaning.

## Commands

```bash
python3 scripts/validate_cards.py --input "/path/Company_Research_CN.html" --slots "/path/Company_Research_CN.card_slots.json" --brand "金融豹"
python3 scripts/generate_social_cards.py --input "/path/Company_Research_CN.html" --slots "/path/Company_Research_CN.card_slots.json" --brand "金融豹"
```

HTML still supplies Sankey numbers, tables, logos, and company metadata; JSON slots override **copy fields only** unless you also set `porter_scores` (five integers).
