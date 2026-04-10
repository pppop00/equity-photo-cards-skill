# Workflow Spec

This file defines the canonical workflow for turning a research report package into the fixed 6-card output. It is the contract between extraction, planning, copy generation, validation, and rendering.

The pipeline is:

1. ingest
2. extract
3. normalize
4. plan card slots
5. write copy into slots
6. audit hardcoded wording and logic
7. validate
8. rewrite until pass
9. export

## 1. Input Contract

Expected primary input:

- one report HTML file

Expected sibling inputs when available:

- `financial_data.json`
- `financial_analysis.json`
- `porter_analysis.json`
- optional local logo assets

The workflow should assume the report package may have schema drift. It should not assume every report uses the exact same field names.

## 2. Extraction Contract

Extraction should gather raw source facts without forcing them into card language yet.

Required raw extraction buckets:

- `identity`
- `dates`
- `summary`
- `highlights`
- `risks`
- `thesis`
- `porter`
- `financials`
- `segments_or_products`
- `operational_kpis`
- `available_assets`

Extraction should preserve source detail even if some of it is not used later.

## 3. Normalized Report Model

Before card planning, convert source data into one canonical report object.

Minimum normalized fields:

```text
company_display_cn
company_display_en
ticker
report_date
fiscal_year
sector
industry
summary_points[]
highlight_points[]
risk_points[]
thesis
porter_industry_text
porter_forward_text
porter_scores[]
revenue
revenue_yoy
gross_profit
gross_margin
operating_income
operating_margin
net_income
net_income_yoy
net_margin
operating_cash_flow
capex
free_cash_flow
segment_mix[]
key_products[]
operational_kpis[]
logo_asset_path
theme_hint
```

Normalization rules:

- compute missing YoY when current and prior values exist
- normalize margin fields to one naming convention
- normalize segment revenue to one unit convention
- convert legal names into short display names when needed
- preserve approved English product names only when helpful
- map product-heavy healthcare reports into usable product / franchise summaries

## 4. Card Planning Contract

Each card should be planned as a dictionary of fixed placeholders. Rendering should consume placeholders, not raw source data.

### Card 1 Slots

```text
cover_title
company_name
english_ticker_line
intro_sentence
metrics_row[3]
company_focus_paragraph
```

Planning rule:

- `intro_sentence` should state the central tension or what the market is really watching
- `company_focus_paragraph` should explain the current setup in 2 complete sentences when possible
- use actual metrics to support the framing, not replace it

### Card 2 Slots

```text
background_bullets[4]
industry_paragraph
porter_labels[5]
porter_scores[5]
conclusion_block
```

Planning rule:

- `background_bullets` explain company setup, scale, mix, and economics
- `industry_paragraph` explains how the industry works and where current pressure sits
- `conclusion_block` compresses the Porter takeaway into one short judgement

### Card 3 Slots

```text
revenue_flow_rows[5]
margin_metric_cards[3]
revenue_explainer_points[3]
```

Planning rule:

- this is the data-forward card
- the explanatory bullets should interpret the flow, not repeat the numbers blindly

### Card 4 Slots

```text
current_business_points[4]
future_watch_points[4]
judgement_paragraph
```

Planning rule:

- left column explains where money is made now
- right column explains what changes the story over the next 2 to 3 years
- judgement compresses the full card into one investable view

### Card 5 Slots

```text
brand_subheading
brand_statement
memory_points[3]
cta_line
```

Planning rule:

- `brand_statement` is the strongest single-line company take
- `memory_points` should help the reader remember the company in 3 facts or frames

### Card 6 Slots

```text
post_title
post_content_lines[4]
hashtags[3..5]
```

Planning rule:

- this should read like a real social post draft
- every line must be publishable without additional editing

## 5. Copywriting Rules

When turning slots into copy:

- facts first
- interpretation second
- filler never
- character budget before sentence count

Required style rules:

- publishable Chinese prose
- complete sentences
- concise but not skeletal
- strong human voice
- voice consistency may be standardized, but substantive claims must be derived from the current report's extracted facts
- no internal strategy notes
- no clipped thesis fragments
- no generic industry filler that could fit any company

Copy priority:

1. say what the company actually does
2. say what drives the numbers now
3. say what the market is really watching
4. say why the next 2 to 3 years matter

## 6. Validation Loop

Validation is not a final polish step. It is part of generation.
Hardcode and logic audit runs before layout validation, not after export.

For each failed validation:

1. identify the failing slot
2. rewrite the slot, not the entire report
3. re-run validation
4. repeat until all slots pass

Rewrite order:

1. slot meaning
2. slot completeness
3. slot density
4. slot tone
5. slot length

If a slot is too empty:

- add one more factual clause or interpretive clause
- do not immediately shrink the text size

If a slot is too long:

- remove repetition
- compress phrasing
- preserve the central idea and metrics
- obey the slot's character budget before relying on max-lines clipping

If a slot sounds dead:

- rewrite with a sharper market-facing framing
- keep the same facts

## 7. What Should Not Trigger A New Template

These should be handled by extraction, normalization, or planning, not by creating a new company-specific hardcoded template:

- different field names for the same metric
- different legal company names
- product-led vs segment-led business mix
- missing direct YoY fields when current and prior values exist
- healthcare reports using products instead of segments
- cloud / software reports using business units instead of product SKUs

## 8. What May Require A New Planner Branch

Add a new planner branch only when a category repeatedly needs different framing logic, for example:

- ad platform economics
- EV + autonomy + energy systems
- enterprise software / cloud
- branded pharma / biotech
- consumer marketplace / e-commerce

A planner branch should change emphasis and narrative framing, not bypass the normalized slot contract.

## 9. Export Contract

The renderer should only receive already-planned slot content.

Expected final output:

- `01_cover.png`
- `02_background_industry.png`
- `03_revenue.png`
- `04_business_outlook.png`
- `05_brand.png`
- `06_post_copy.png`

If validation fails, do not export.

## 10. Standard copy pipeline (only path; enforced in CLI)

**Every** export uses **`--slots`**. Incomplete JSON is rejected at load time (`assert_card_slots_complete` in `scripts/generate_social_cards.py`) so body copy cannot silently fall back to `company_theme` / `fit_copy` heuristics.

**Required slot keys (non-empty; list lengths as shown):** `intro_sentence`, `company_focus_paragraph`, `background_bullets` (≥4), `industry_paragraph`, `conclusion_block`, `revenue_explainer_points` (≥3), `current_business_points` (≥4), `future_watch_points` (≥4), `judgement_paragraph`, `brand_statement`, `memory_points` (≥3), `post_title`, `post_content_lines` (≥4), `hashtags` (≥3). **`porter_scores`** is optional (exactly five integers if present); otherwise Porter scores come from the HTML package.

**Standard flow (every new `*_Research_CN.html`):**

1. **Content production agent** writes **`html_stem.card_slots.json`** beside the HTML — see [content-production-agent.md](../agents/content-production-agent.md) and [card-slots.schema.json](./card-slots.schema.json).
2. **Layout fill agent** refines copy per [design-spec.md](./design-spec.md) and [validation-agent.md](../agents/validation-agent.md).
3. `python3 scripts/validate_cards.py --input …/Report_CN.html --slots …` until clean.
4. `python3 scripts/generate_social_cards.py --input …/Report_CN.html --slots …`.

**`--slots` argument:** For **one** HTML file, pass the JSON file path **or** the **folder** that contains `<stem>.card_slots.json`. For **several** HTML files under `--input`, `--slots` **must** be a **directory** containing one `<stem>.card_slots.json` per HTML.

Hand-off overview: [agent-slot-pipeline.md](../agents/agent-slot-pipeline.md).

**流程图（Mermaid）:** [workflow-flowchart.md](./workflow-flowchart.md)

Example (PDD-shaped): [examples/pdd_holdings_card_slots.example.json](./examples/pdd_holdings_card_slots.example.json).
