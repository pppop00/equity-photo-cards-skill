---
name: equity-photo-cards
description: >-
  Turns equity research HTML (and optional sibling JSON) into six fixed-layout social images
  (e.g. Xiaohongshu / Douyin) by filling predefined card slots in `*.card_slots.json`, then
  validating and rendering with Python. Use whenever the user has report HTML to convert into
  slot-based PNGs, fixed 1080×1350 cards, `card_slots.json`, `validate_cards.py`, or
  `generate_social_cards.py` — even if they only say “put this HTML into the picture templates.”
  Mandatory path — agents must produce a complete `card_slots.json`; CLI requires `--slots`;
  no heuristic-only export.
---

# Equity Photo Cards

**What you are building:** Agents consume **equity research HTML** (and optional sibling JSON), write copy into a **fixed set of named slots** (`*.card_slots.json`), and the renderer places that text into **predetermined image frames** (six cards, 1080×1350) — not a bespoke layout per company.

## Skill layout (skill-creator anatomy)

```
equity-photo-cards/                    # Skill bundle (skill-creator anatomy)
├── SKILL.md                           # Entry point: workflow + links (keep < ~500 lines; details in references/)
├── agents/                            # Sub-agent briefs (who writes what before export)
├── references/
│   ├── workflow-spec.md               # Pipeline contract + slot keys
│   ├── workflow-flowchart.md          # Mermaid diagrams for humans (review here)
│   ├── design-spec.md                 # Visual / copy limits
│   ├── card-slots.schema.json         # Machine schema for slot JSON
│   ├── examples/                      # Filled example (e.g. PDD-shaped)
│   └── templates/                     # Empty-shape starter → copy to <stem>.card_slots.json
├── scripts/                           # validate_cards.py, generate_social_cards.py (deterministic)
├── evals/                             # Optional smoke prompts (evals.json)
└── output/                            # Default PNG output (gitignored; use --output-root to override)
```

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

**Specifications (read for schema and visuals):**

- Workflow and slot schema: [references/workflow-spec.md](./references/workflow-spec.md)
- Workflow diagrams — bundle 表 + 端到端 / CLI / 新报告 / 校验分层 / 九步（Mermaid）: [references/workflow-flowchart.md](./references/workflow-flowchart.md)
- JSON slot contract (machine): [references/card-slots.schema.json](./references/card-slots.schema.json)
- New-report slot starter (copy → rename to `<stem>.card_slots.json`): [references/templates/card_slots.template.json](./references/templates/card_slots.template.json)
- Visual and layout rules: [references/design-spec.md](./references/design-spec.md)

**Agents (who does what before export):**

- Two-agent handoff: [agents/agent-slot-pipeline.md](./agents/agent-slot-pipeline.md)
- Content production (HTML → draft slots): [agents/content-production-agent.md](./agents/content-production-agent.md)
- Layout fill (draft → validator-clean): [agents/layout-fill-agent.md](./agents/layout-fill-agent.md)
- Hardcode and logic audit policy: [agents/hardcode-audit-agent.md](./agents/hardcode-audit-agent.md)
- Validation policy: [agents/validation-agent.md](./agents/validation-agent.md)

**Tools:**

- Renderer: [scripts/generate_social_cards.py](./scripts/generate_social_cards.py)
- Validator: [scripts/validate_cards.py](./scripts/validate_cards.py)

## Operating Principle

Do not treat this skill as "pick an industry and emit canned sentences."

Use this skill as:

1. `HTML/JSON -> structured report facts`
2. `structured report facts -> fixed card slot plan`
3. `slot plan -> copy` as **`card_slots.json`** written by the **content** then **layout** agents ([agent-slot-pipeline.md](./agents/agent-slot-pipeline.md)) — **this is the standard for every new report**, not optional
4. `copy -> hardcode / logic audit` (on the final slot text)
5. `audited copy -> validation / rewrite loop` (`validate_cards.py` — **`--slots` 必填**)
6. `validated copy -> exported cards` (`generate_social_cards.py` — **`--slots` 必填**)

**No alternate path:** The CLI **does not** accept a run without `--slots`. Incomplete JSON is **rejected** (`assert_card_slots_complete`): every required body slot must be present so export never silently falls back to Python template copy.

**File convention:** **`Company_Research_CN.card_slots.json`** beside **`Company_Research_CN.html`** in the report folder. For a **single** report you may pass `--slots` as either the JSON file path or that **folder** (resolver loads `<stem>.card_slots.json`). For **`--input` 指向多只 HTML**，`--slots` **必须是目录**，且内含与每个 `stem` 对应的 `*.card_slots.json`。

**Why there is no one “universal” filled `card_slots.json`:** The file is **per-company body copy** (facts, wording, hashtags) read by the renderer into **fixed** card frames. The skill ships a **structure template** you copy for each new stem — [references/templates/card_slots.template.json](./references/templates/card_slots.template.json) — plus machine schema [references/card-slots.schema.json](./references/card-slots.schema.json) and a worked example [references/examples/pdd_holdings_card_slots.example.json](./references/examples/pdd_holdings_card_slots.example.json). Agents still **author** `<stem>.card_slots.json` from the HTML package; the template only avoids starting from a blank file.

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

### 5. Copy Generation (standard = materialize `card_slots.json`)

- **Production:** Run the **content production agent** then the **layout fill agent** so all body copy lives in **`card_slots.json`** before any PNG export. See [content-production-agent.md](./agents/content-production-agent.md) and [layout-fill-agent.md](./agents/layout-fill-agent.md).
- **`card_slots.json` 必须填满** 所有脚本要求的槽位（见 `assert_card_slots_complete`）；不允许依赖内置 `fit_copy` / `company_theme` 自动糊字作为交付物。
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

- Only export once the validator passes with the **intended** `card_slots.json` (`validate_cards.py --input … --slots …`)
- Export all 6 images for the report as one set (`generate_social_cards.py --input … --slots …`)
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

**Standard (every new report):** validate and render **with** `card_slots.json` next to the HTML (adjust paths):

```bash
python3 scripts/validate_cards.py \
  --input "/abs/path/Tesla_Research_CN.html" \
  --slots "/abs/path/Tesla_Research_CN.card_slots.json" \
  --brand "金融豹"

python3 scripts/generate_social_cards.py \
  --input "/abs/path/Tesla_Research_CN.html" \
  --slots "/abs/path/Tesla_Research_CN.card_slots.json" \
  --brand "金融豹"
```

PNG sets default to this skill repo’s `output/<stem>/` unless you pass `--output-root`.

**Where `card_slots.json` lives:** The **authoritative** file stays beside the HTML in the report package (version control, re-validation). **`generate_social_cards.py` also copies** that resolved JSON into `output/<stem>/` next to the six PNGs so you have one folder per company for handoff—unless you pass **`--no-copy-slots`**.

**Folder batch（多只 `*.html`）:** `--slots` 传 **父目录**，其中包含 `Tesla_Research_CN.card_slots.json`、`Amazon_Research_CN.card_slots.json` 等与各 HTML **stem 一一对应** 的文件。不得用单个 JSON 路径套批多只无关报告。

Use `--output-root` only to override the default output directory.

## Maintenance Standard

- Keep extraction, normalization, planning, writing, validation, and rendering as separate concerns
- Update [references/workflow-spec.md](./references/workflow-spec.md) first when the pipeline contract changes
- Update [references/design-spec.md](./references/design-spec.md) first when visual rules change
- Keep the renderer aligned with the workflow and the validator
- Add new validation rules when a failure pattern repeats
- Treat excessive whitespace, broken wraps, and stiff filler copy as product failures, not cosmetic issues
