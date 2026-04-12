---
name: equity-photo-cards
description: >-
  HARD GATE: do not start any work until the customer has explicitly confirmed a color palette
  (list all: default / b / c; wait for their choice). No intake, extraction, slot writing,
  validation, or export before that confirmation. Then: equity research HTML → `*.card_slots.json` →
  Validator 1 (`validate_cards.py`) → Validator 2 (web fact-check of all card data per
  agents/validator-2-agent.md; fix and re-validate until fully correct) → only then
  `generate_social_cards.py` with `--slots` and `--palette default|b|c` (non-interactive).
---

# Equity Photo Cards

## 配色选择（硬门禁：客户未确认则不得开工）

<span id="palette-choice"></span>

**接到与本 skill 相关的任何任务后，第一步且仅第一步：向客户提问「需要哪一种配色？」并列出下表全部选项。在客户给出明确选择（`default` / `b` / `c` 之一）之前，禁止开始任何后续工作。**

**在客户确认配色之前，不得执行包括但不限于：** 接收材料后的实质处理、阅读报告并开始写槽位、运行 `validate_cards.py`、运行 `generate_social_cards.py`、或代客户默认任选一种配色。**「先做着再说」「默认用 default」均违规。**

客户确认后，将所选配色记为本次任务的**唯一** `--palette` 参数，全程沿用至导出。

| 选项 | `--palette` 参数 | 视觉说明 |
|------|-------------------|----------|
| **1** | `default` | 设计规范原版：灰白底 + 红橙强调 |
| **2** | `b` | 浅紫底 + 紫/绿强调（偏小红书向） |
| **3** | `c` | 暖纸色底 + 深色顶栏（杂志感） |

三种配色均保留在 [scripts/generate_social_cards.py](./scripts/generate_social_cards.py) 的 `apply_palette()` 中。执行 `generate_social_cards.py` 时必须带上与客户确认一致的 **`--palette default`**、**`--palette b`** 或 **`--palette c`**。若在**无 TTY** 的环境（Agent、CI）中运行脚本，**不能**依赖交互式 `input()`，必须以客户已确认的选项作为唯一来源并显式传入。

---

**What you are building:** Agents consume **equity research HTML** (and optional sibling JSON), write copy into a **fixed set of named slots** (`*.card_slots.json`), and the renderer places that text into **predetermined image frames** (six cards; **logical** layout 1080×1350, **default PNG export** 2160×2700 for zoom-friendly assets) — not a bespoke layout per company.

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

This skill is not a generic image-generation workflow. It is a deterministic report-to-card pipeline — **only after [配色选择](#palette-choice) 已由客户确认**：

0. **customer confirms palette** (`default` | `b` | `c`) — **no step below until this is done**
1. extract the report
2. normalize the facts into a stable internal structure
3. plan each card's content slots
4. write publishable copy into those slots
5. audit hardcoded wording and logic before layout
6. validate layout (Validator 1) and rewrite until every check passes
7. Validator 2: externally verify every material fact in the cards via web search; fix and repeat steps 6–7 until fully correct
8. render the final 6 images (with matching `--palette`)

The goal is that a new company HTML should normally flow through the same pipeline without adding a company-specific template. Code changes should only be needed when the upstream schema changes or when a truly new business-model pattern requires a new planner branch.

## Source Of Truth

**Specifications (read for schema and visuals):**

- Workflow and slot schema: [references/workflow-spec.md](./references/workflow-spec.md)
- Workflow diagrams — bundle 表 + 端到端 / CLI / 新报告 / 校验分层（Validator 1 + 2）/ 步骤含配色（Mermaid）: [references/workflow-flowchart.md](./references/workflow-flowchart.md)
- JSON slot contract (machine): [references/card-slots.schema.json](./references/card-slots.schema.json)
- New-report slot starter (copy → rename to `<stem>.card_slots.json`): [references/templates/card_slots.template.json](./references/templates/card_slots.template.json)
- Visual and layout rules: [references/design-spec.md](./references/design-spec.md)

**Agents (who does what before export):**

- Agent handoff: [agents/agent-slot-pipeline.md](./agents/agent-slot-pipeline.md)
- Logo production (web official logo → regenerated clean asset): [agents/logo-production-agent.md](./agents/logo-production-agent.md)
- Content production (HTML → draft slots): [agents/content-production-agent.md](./agents/content-production-agent.md)
- Layout fill (draft → validator-clean): [agents/layout-fill-agent.md](./agents/layout-fill-agent.md)
- Hardcode and logic audit policy: [agents/hardcode-audit-agent.md](./agents/hardcode-audit-agent.md)
- Validation policy (Validator 1 — `validate_cards.py`): [agents/validation-agent.md](./agents/validation-agent.md)
- Validator 2 (external fact-check before export): [agents/validator-2-agent.md](./agents/validator-2-agent.md)

**Tools:**

- Renderer: [scripts/generate_social_cards.py](./scripts/generate_social_cards.py)
- Validator: [scripts/validate_cards.py](./scripts/validate_cards.py)

## Operating Principle

Do not treat this skill as "pick an industry and emit canned sentences."

Use this skill as — **only after the customer has confirmed a palette** ([配色选择](#palette-choice)):

0. **`customer confirms palette`** → record `default` | `b` | `c` for this job; **do not proceed without this**
1. `report folder (JSON-first, HTML as render scaffold) -> structured report facts`
2. `structured report facts -> fixed card slot plan`
3. `company identity -> official logo asset` via the **logo production agent** ([logo-production-agent.md](./agents/logo-production-agent.md))
4. `slot plan + logo path -> copy` as **`card_slots.json`** written by the **content** then **layout** agents ([agent-slot-pipeline.md](./agents/agent-slot-pipeline.md)) — **this is the standard for every new report**, not optional
5. `copy -> hardcode / logic audit` (on the final slot text)
6. `audited copy -> Validator 1 / rewrite loop` (`validate_cards.py` — **`--slots` 必填**)
7. `Validator 1 clean -> Validator 2`（联网逐项核对卡片中的数字与事实，见 [validator-2-agent.md](./agents/validator-2-agent.md)；有错则改 slots 并回到步骤 6，直至两轮均通过）
8. `Validator 1 + Validator 2 passed -> exported cards` (`generate_social_cards.py` — **`--slots` 必填**, **`--palette` 须与客户确认一致**；export 后自动清理未使用 logo 文件)

**No alternate path:** The CLI **does not** accept a run without `--slots`. Incomplete JSON is **rejected** (`assert_card_slots_complete`): every required body slot must be present so export never silently falls back to Python template copy.

**Input convention:** Preferred user input is the whole report folder path, e.g. `.../NVIDIA_2026-04-12/`, containing `*_Research_CN.html` plus sibling JSON files. Treat JSON as the primary factual source (`financial_data.json`, `financial_analysis.json`, `porter_analysis.json`, etc.) because it is faster, less lossy, and easier to validate than scraping rendered HTML. Use HTML for identity/date, summary prose, embedded chart variables, and final rendering. If the user provides only one HTML file, still look for sibling JSON in the same folder. If the user provides only JSON without HTML, use it for analysis/copy drafting but ask for or locate the HTML before final PNG export.

**File convention:** **`Company_Research_CN.card_slots.json`** beside **`Company_Research_CN.html`** in the report folder. For a **single** report you may pass `--slots` as either the JSON file path or that **folder** (resolver loads `<stem>.card_slots.json`). For **`--input` 指向多只 HTML**，`--slots` **必须是目录**，且内含与每个 `stem` 对应的 `*.card_slots.json`。

**Logo convention:** Card 1 has a fixed small logo section below `公司看点`, drawn directly on the card background with no white logo container. Do **not** auto-discover local logos. Before writing final slots, run [logo-production-agent.md](./agents/logo-production-agent.md): search the web for official brand / press-kit / IR-media logo sources, regenerate a clean transparent logo asset from the official reference (SVG or high-res PNG; **horizontal wordmarks ≥840 px wide** at default render scale so they are not soft upscales), save it locally, then set `logo_asset_path` in `card_slots.json`. Never use screenshots, search-result thumbnails, or ticker-letter placeholders. `validate_cards.py` rejects logos below the minimum bitmap size. After export, keep only the logo file actually referenced by `logo_asset_path`; delete logo source downloads, alternatives, and temporary logo folders.

**Why there is no one “universal” filled `card_slots.json`:** The file is **per-company body copy** (facts, wording, hashtags) read by the renderer into **fixed** card frames. The skill ships a **structure template** you copy for each new stem — [references/templates/card_slots.template.json](./references/templates/card_slots.template.json) — plus machine schema [references/card-slots.schema.json](./references/card-slots.schema.json) and a worked example [references/examples/pdd_holdings_card_slots.example.json](./references/examples/pdd_holdings_card_slots.example.json). Agents still **author** `<stem>.card_slots.json` from the HTML package; the template only avoids starting from a blank file.

The important boundary is this:

- Company-specific facts should live in extracted and normalized data
- Card structure should live in the slot plan
- Visual constraints should live in the design spec and validation rules
- Industry tone should only influence framing and emphasis, not replace factual extraction
- Unified voice is allowed; hardcoded body copy is not

## Required Workflow

Follow these steps in order every time a new report arrives.

### 0. 配色确认（硬门禁；未完成则禁止进入步骤 1）

- 按 **[配色选择](#palette-choice)** 向客户列出三种配色，**取得客户的明确确认**（口头/文字均可，但必须对应 `default`、`b`、`c` 之一）。
- **在客户确认配色之前：不得执行步骤 1～8**（不得做 Intake、抽取、写槽位、校验、Validator 2、导出，也不得擅自默认配色）。
- 确认后，记下本次任务的 `--palette`；后续所有 `generate_social_cards.py` 调用必须与之一致。

### 1. Intake

- Prefer a report folder path over a standalone HTML path when the user can provide it
- Confirm the folder contains one report HTML, not an arbitrary marketing page or random article
- Check for sibling JSON files before reading the HTML body
- Treat the HTML plus sibling JSON as one report package, with JSON as the primary source for financial facts
- If the HTML exists but supporting JSON is missing, continue with best-effort extraction and flag the missing fields
- If JSON exists but HTML is missing, use JSON for analysis/copy drafting but do not export PNGs until the report HTML is located

### 2. Extraction

- Read sibling JSON files first when present; they are the preferred source for financial data, margins, segments, cash flow, Porter scores, and latest operating updates
- Read the report HTML after JSON to pull summary prose, rendered section text, identity/date, and embedded data blocks such as `sankeyActualData`
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
- official logo source candidates from web search

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

### 4.5 Logo Production

- Run [logo-production-agent.md](./agents/logo-production-agent.md) before finalizing `card_slots.json`.
- Search the web for official logo references; do not rely on local discovery.
- Regenerate a clean transparent logo asset from the official reference, save it locally, and set `logo_asset_path`.
- Do not use screenshots, browser crops, search thumbnails, or ticker-letter placeholders.
- After export, leave only the final `logo_asset_path` asset in the report output folder; remove downloaded source logos, rejected alternatives, and `logo_sources/`.

### 5. Copy Generation (standard = materialize `card_slots.json`)

- **Production:** Run the **logo production agent**, then the **content production agent**, then the **layout fill agent** so all body copy and `logo_asset_path` live in **`card_slots.json`** before any PNG export. See [logo-production-agent.md](./agents/logo-production-agent.md), [content-production-agent.md](./agents/content-production-agent.md), and [layout-fill-agent.md](./agents/layout-fill-agent.md).
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

### 6. Validator 1 And Rewrite Loop

- Run the hardcode and logic audit before layout validation
- Run **`validate_cards.py`** (Validator 1) before Validator 2 and before final export
- If any check fails, rewrite the slot copy and run Validator 1 again
- Do not accept a card simply because it renders without crashing
- A card with weak density, clipped text, broken line wraps, or corpse-like prose is a failure
- A slot that still reads like reusable template copy, or that contradicts the report facts, is also a failure

### 6.5 Validator 2（外部事实核查）

- After Validator 1 passes, run **[validator-2-agent.md](./agents/validator-2-agent.md)**: build a claim inventory from `card_slots.json` (and any figures pulled into cards from HTML/JSON), verify each material number and fact against **authoritative public sources** (filings, IR, official releases) via web search
- If anything is wrong or unverifiable at false precision, fix the slots (and note sibling JSON issues if needed), then **run Validator 1 again**, then **Validator 2 again** — repeat until both pass
- **Do not** run `generate_social_cards.py` until Validator 2 passes

Rewrite priority:

1. fix factual slot mapping mistakes
2. fix incomplete sentences
3. fix density and whitespace issues
4. fix human tone
5. only then consider shortening copy

### 7. Export

- Only export once **Validator 1 and Validator 2** have passed with the **intended** `card_slots.json`
- Export all 6 images for the report as one set (`generate_social_cards.py --input … --slots … --palette …`)，其中 **`--palette` 必须与步骤 0 中用户选择的配色一致**。
- Keep the file naming convention stable

## Fixed Card Schema

The fixed output is always:

- Card 1: cover + core tension
- Card 2: background + industry + Porter
- Card 3: revenue / profit flow
- Card 4: current business + next 2 to 3 years
- Card 5: brand close + three memory points
- Card 6: social post copy image with title, content, hashtags — **贴吧/热帖** tone (recent buzz, hot products, events; fun/angry/funny OK); **four** `post_content_lines`; each line must satisfy `card6_line_sounds_human` in `generate_social_cards.py` (see [content-production-agent.md](./agents/content-production-agent.md) Card 6)

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
  --brand "金融豹" \
  --palette default
```

**配色：** 接任务时必须先问并完成选择，见 **[配色选择](#palette-choice)**。三种预设均保留在 `apply_palette()`。用户在终端自己跑脚本且**不传 `--palette`** 时，脚本可交互询问 1/2/3；**Agent / 无 TTY 必须显式传入** `--palette`。

PNG sets default to this skill repo’s `output/<stem>/` unless you pass `--output-root`.

**Where `card_slots.json` lives:** The **authoritative** file stays beside the HTML in the report package (version control, re-validation). **`generate_social_cards.py` also copies** that resolved JSON into `output/<stem>/` next to the six PNGs so you have one folder per company for handoff—unless you pass **`--no-copy-slots`**.

**Folder batch（多只 `*.html`）:** `--slots` 传 **父目录**，其中包含 `Tesla_Research_CN.card_slots.json`、`Amazon_Research_CN.card_slots.json` 等与各 HTML **stem 一一对应** 的文件。不得用单个 JSON 路径套批多只无关报告。

Use `--output-root` only to override the default output directory.

## Maintenance Standard

- Keep extraction, normalization, planning, writing, validation, and rendering as separate concerns
- Update [references/workflow-spec.md](./references/workflow-spec.md) first when the pipeline contract changes
- Update [references/design-spec.md](./references/design-spec.md) first when visual rules change
- Keep the renderer aligned with the workflow and the validator
- Add new validation rules when a failure pattern repeats; extend [validator-2-agent.md](./agents/validator-2-agent.md) when repeated factual error classes appear
- Treat excessive whitespace, broken wraps, and stiff filler copy as product failures, not cosmetic issues
