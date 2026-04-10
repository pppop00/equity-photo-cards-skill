---
name: equity-photo-cards
description: Convert one or more equity research HTML outputs into 6 social-post assets for Xiaohongshu or Douyin. Use when Codex has repeatable equity-research HTML reports and needs a fixed card template, structured content planning, strict copy compression, and deterministic layout validation before export.
---

# Equity Photo Cards

This skill is not a generic image-generation workflow. It is a deterministic report-to-card pipeline:

1. extract the report
2. normalize the facts into a stable internal structure
3. plan each card's content slots
4. write publishable copy into those slots
5. audit hardcoded wording and logic before layout
6. validate layout and rewrite until every card passes
7. render the final 6 images

The goal is that a new company HTML should normally flow through the same pipeline without adding a company-specific template. Code changes should only be needed when the upstream schema changes or when a truly new business-model pattern requires a new planner branch.

## Source Of Truth

- Workflow and slot schema: [references/workflow-spec.md](./references/workflow-spec.md)
- JSON slot contract (machine): [references/card-slots.schema.json](./references/card-slots.schema.json)
- Two-agent handoff: [references/agent-slot-pipeline.md](./references/agent-slot-pipeline.md)
- Content production agent brief: [references/content-production-agent.md](./references/content-production-agent.md)
- Layout fill agent brief: [references/layout-fill-agent.md](./references/layout-fill-agent.md)
- Visual and layout rules: [references/design-spec.md](./references/design-spec.md)
- Hardcode and logic audit policy: [references/hardcode-audit-agent.md](./references/hardcode-audit-agent.md)
- Validation policy: [references/validation-agent.md](./references/validation-agent.md)
- Renderer: [scripts/generate_social_cards.py](./scripts/generate_social_cards.py)
- Validator: [scripts/validate_cards.py](./scripts/validate_cards.py)

## Operating Principle

Do not treat this skill as "pick an industry and emit canned sentences."

Use this skill as:

1. `HTML/JSON -> structured report facts`
2. `structured report facts -> fixed card slot plan`
3. `slot plan -> copy` (**LLM agents** may write `card_slots.json`; otherwise renderer heuristics)
4. `copy -> hardcode / logic audit`
5. `audited copy -> validation / rewrite loop`
6. `validated copy -> exported cards`

**Rich HTML reports:** Prefer the two-agent slot pipeline ([agent-slot-pipeline.md](./references/agent-slot-pipeline.md)) and `--slots card_slots.json` so narrative from the HTML is not collapsed by built-in `company_theme` / `fit_copy` shortcuts.

The important boundary is this:

- Company-specific facts should live in extracted and normalized data
- Card structure should live in the slot plan
- Visual constraints should live in the design spec and validation rules
- Industry tone should only influence framing and emphasis, not replace factual extraction
- Unified voice is allowed; hardcoded body copy is not

## Required Workflow

Follow these steps in order every time a new report arrives.

### 1. Intake

- Confirm the input is a report HTML, not an arbitrary marketing page or random article
- Check whether sibling JSON files exist in the same folder
- Treat the HTML plus sibling JSON as one report package
- If the HTML exists but supporting JSON is missing, continue with best-effort extraction and flag the missing fields

### 2. Extraction

- Read the report HTML and pull all text and embedded data blocks that are relevant to company analysis
- Read sibling JSON files when present
- Prefer over-extraction to under-extraction at this stage
- Do not write card copy yet

Required extraction targets:

- company identity
- report date / fiscal period
- summary paragraphs
- highlights
- risks
- thesis or key claim
- Porter analysis text and scores
- revenue / margin / cash-flow facts
- segment or product mix
- operating KPIs
- locally available logo assets

### 3. Normalization

- Convert all extracted facts into one canonical report model before any copywriting
- Resolve schema drift here, not in the card templates
- Compute missing but derivable facts such as YoY growth when current and prior values exist
- Normalize business lines, product lines, and KPI labels into publishable Chinese phrasing
- Produce a stable internal shape even if the upstream file names or field names vary

If the source uses different names such as `revenue_growth_yoy_pct` vs `yoy_revenue_pct`, or `capex` vs `capex_purchases`, fix it in normalization. Do not leak source-specific field names into card logic.

### 4. Card Planning

- Build a slot plan for all 6 cards using the normalized model
- Decide what each card must say before writing polished copy
- Treat the cards as fixed containers with placeholders to fill, not as blank canvases
- Every slot should be backed by a fact, a compressed inference, or a curated framing sentence

The slot schema is defined in [references/workflow-spec.md](./references/workflow-spec.md). Use it every time.

### 5. Copy Generation

- Write copy slot by slot, not card by card in one pass
- Use report facts first, thematic framing second
- It is acceptable to standardize voice cues such as `说白了` or `别只看`, but the substance after that cue must come from the current report package
- Do not reuse the same explanatory sentence across different companies unless it is a true fallback and source text is unavailable
- Control slot length by explicit character budget first; do not rely on sentence count as the primary guardrail
- Prefer complete Chinese sentences that sound publishable and human
- Avoid dead analyst boilerplate and avoid empty editorial fluff
- If a slot looks sparse, expand the factual explanation before shrinking fonts
- If a slot overflows, rewrite or compress the copy before touching layout

### 6. Validation And Rewrite Loop

- Run the hardcode and logic audit before layout validation
- Run validation before final export
- If any check fails, rewrite the slot copy and validate again
- Do not accept a card simply because it renders without crashing
- A card with weak density, clipped text, broken line wraps, or corpse-like prose is a failure
- A slot that still reads like reusable template copy, or that contradicts the report facts, is also a failure

Rewrite priority:

1. fix factual slot mapping mistakes
2. fix incomplete sentences
3. fix density and whitespace issues
4. fix human tone
5. only then consider shortening copy

### 7. Export

- Only export once the validator passes
- Export all 6 images for the report as one set
- Keep the file naming convention stable

## Fixed Card Schema

The fixed output is always:

- Card 1: cover + core tension
- Card 2: background + industry + Porter
- Card 3: revenue / profit flow
- Card 4: current business + next 2 to 3 years
- Card 5: brand close + three memory points
- Card 6: social post copy image with title, content, hashtags

Do not change the card count or reorder the card roles unless the design spec is explicitly revised.

## Placeholder Logic

The correct mental model is "fill placeholders," not "invent six unrelated pages."

For each new report:

1. create the normalized report model
2. fill the card slot placeholders from that model
3. rewrite any slot that fails density, tone, or wrapping constraints
4. render after the placeholders are stable

Examples of placeholders:

- `core_tension`
- `intro_sentence`
- `metrics_row`
- `background_bullets`
- `industry_paragraph`
- `revenue_explainer_points`
- `current_business_points`
- `future_watch_points`
- `brand_statement`
- `memory_points`
- `post_title`
- `post_content_lines`
- `hashtags`

These placeholders must always be filled from normalized facts first. Theme or sector logic should only help decide emphasis, ordering, and wording.

## When To Change Code

Do not patch the skill for every company.

Change code only when one of these is true:

- the upstream HTML structure changed
- the sibling JSON schema changed
- normalization cannot recover a required field
- a new business model repeatedly fails the same card planner
- validation reveals a systematic formatting gap that should become an explicit rule

Do not change code merely because one company's current wording feels bland. First fix the planner or copy generation logic at the slot level.

## Renderer Usage

Validation first:

```bash
python3 scripts/validate_cards.py \
  --input "/abs/path/Tesla_Research_CN.html" \
  --brand "金融豹"
```

Single file (PNG sets default to this skill repo’s `output/<stem>/`):

```bash
python3 scripts/generate_social_cards.py \
  --input "/abs/path/Tesla_Research_CN.html" \
  --brand "金融豹"
```

With **agent-produced copy** (same `card_slots.json` reused if you batch multiple HTML files — only use when appropriate):

```bash
python3 scripts/generate_social_cards.py \
  --input "/abs/path/Tesla_Research_CN.html" \
  --slots "/abs/path/card_slots.json" \
  --brand "金融豹"
```

Folder batch:

```bash
python3 scripts/generate_social_cards.py \
  --input "/abs/path/to/html-folder" \
  --brand "金融豹"
```

Use `--output-root` only to override the default output directory.

## Maintenance Standard

- Keep extraction, normalization, planning, writing, validation, and rendering as separate concerns
- Update [references/workflow-spec.md](./references/workflow-spec.md) first when the pipeline contract changes
- Update [references/design-spec.md](./references/design-spec.md) first when visual rules change
- Keep the renderer aligned with the workflow and the validator
- Add new validation rules when a failure pattern repeats
- Treat excessive whitespace, broken wraps, and stiff filler copy as product failures, not cosmetic issues
