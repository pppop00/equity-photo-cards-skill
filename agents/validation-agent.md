# Validation Agent（Validator 1）

This document describes what **`scripts/validate_cards.py`** enforces — **Validator 1** (layout, completeness, internal consistency with the report package, logo rules). It does **not** replace **[validator-2-agent.md](./validator-2-agent.md)** (external fact-check via web search before export).

Run this validation pass after card slots have been planned, filled with copy, and audited for hardcoded wording and logical consistency, but **before** [Validator 2](./validator-2-agent.md) and **before** final image export. If any check fails, revise the failing slot copy or slot mapping and validate again until every check passes.

Validation belongs inside the generation loop:

1. plan card slots
2. write slot copy
3. audit hardcoded wording and logic
4. **Validator 1:** `validate_cards.py`
5. rewrite only the failing slot, then **Validator 1** again until clean
6. **Validator 2:** [validator-2-agent.md](./validator-2-agent.md) — web fact-check every material claim in slots; fix copy and repeat steps 4–5 until **both** pass
7. export (`generate_social_cards.py`) only after Validator 1 **and** Validator 2 pass

## Required Checks

- `card_slots.json` must pass **`assert_card_slots_complete`** (all required slot keys populated) before layout checks run
- When `logo_asset_path` is set, **`validate_report`** checks logo file dimensions (`logo_asset_dimension_issues` in `generate_social_cards.py`): horizontal wordmarks must be **≥840 px** wide (Card 1 slot at `LAYOUT_SCALE=2`), vertical marks **≥288 px** tall, square-ish marks **≥512 px** on the long side — this blocks upscaled favicons and other soft rasters
- Company display name must use the short Chinese company name, not the full legal name with `公司`
- Footer must be exactly `公司名 | 日期`
- Font family must stay in the Arial family
- Colors must stay inside the approved palette in `design-spec.md`
- No text may overlap another text block, decorative element, or section frame
- No text may exceed its section box
- Numbers, percentages, tickers, and English words must not be split across lines
- Approved English proper nouns such as `FSD`, `Robotaxi`, and `Optimus` are allowed, but they still may not be split across lines
- Commas, periods, semicolons, colons, enumeration commas, and equivalent punctuation must remain attached to the previous line
- Any line that starts with `，。；：、,.!?` or equivalent closing punctuation fails validation
- Card 1 `公司看点` must use enough copy to avoid large empty yellow-panel space
- Card 1 `公司看点` must also stay inside its explicit character budget
- Card 2 `行业层面` must be a complete summarized paragraph, not a clipped fragment
- Card 2 `行业层面` must stay inside its explicit character budget
- Card 3 explainer bullets must stay inside their per-bullet character budget and the yellow panel's **measured** height budget (validator sums `line_raster_height` per wrapped line, matching `draw_text`, not `font.size` alone; panel bottom y is **1260** with bottom inset reserved)
- Card 3 title must be `实际收入分析`
- Card 3 yellow panel title must be `收入分析`
- Card 2 left card must feel editorially dense: prefer 4 bullets and enough copy to avoid large empty lower-half whitespace
- Card 2, Card 4 judgement, Card 5 main statement, and Card 6 content lines must not use ellipses or half-sentences as a layout escape hatch
- Any paragraph or bullet that is meant to be read as body copy must end as a complete Chinese sentence
- Card 4 judgement, Card 5 main statement, and Card 6 content must sound like a smart human explaining the company, not like stiff analyst boilerplate
- Card 4 left and right columns should be filled as much as possible without overflow
- Card 4 left and right columns must hit a minimum occupied height; obvious dead air is a validation failure
- Card 4 left and right columns must obey their per-bullet character budgets
- Card 5 must not include `今天这家公司，特斯拉` or any equivalent preface line
- Card 6 must include `title`, `content`, and `hashtags`
- Card 6 content must contain exactly 4 bullet lines; each line must pass **`card6_line_sounds_human`** (`HUMAN_MARKERS` or `CARD6_COLLOQUIAL_MARKERS` in `generate_social_cards.py`); **editorial pass:** tone should match [content-production-agent.md](./content-production-agent.md) Card 6 (贴吧 / forum energy, not sell-side recap)
- Card 6 hashtags must fit inside the hashtag section without overflow, and the total hashtag count may not exceed 5
- Text rendering must use high-quality supersampling so exported fonts remain crisp

## Execution

`--slots` is **required** for both tools. Pass a **JSON file** (single HTML) or a **directory** of `<stem>.card_slots.json` when `--input` lists multiple HTML files. The loader rejects incomplete slot files before these checks run.

```bash
python3 scripts/validate_cards.py \
  --input "/abs/path/to/Company_Research_CN.html" \
  --slots "/abs/path/to/Company_Research_CN.card_slots.json" \
  --brand "金融豹"

python3 scripts/generate_social_cards.py \
  --input "/abs/path/to/Company_Research_CN.html" \
  --slots "/abs/path/to/Company_Research_CN.card_slots.json" \
  --brand "金融豹"
```

(Renderer defaults to this skill repo’s `output/<report_stem>/`; pass `--output-root` to override.)

**After** the commands above succeed, run **[Validator 2](./validator-2-agent.md)** before `generate_social_cards.py`.

## Failure Policy

- Do not produce final images if **Validator 1** or **Validator 2** fails
- Fix the failing slot, not the whole report, unless the slot failure reveals an upstream planning mistake
- Fix content density before shrinking fonts
- Fix numeric and English line wrapping before shortening copy
- Do not replace approved English product names with Chinese unless layout truly cannot pass validation
- Prefer rewriting copy into complete Chinese sentences over clipping with ellipses
- If copy sounds dead, rewrite it; do not let layout validation excuse corpse-like prose
