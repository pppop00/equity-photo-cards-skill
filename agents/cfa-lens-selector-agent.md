# CFA Lens Selector Agent

**Invocation:** Run after the content production agent has drafted Cards 1–3 (so company business model, financial profile, and industry context are already understood). Output is the `cfa_lens` object in `<stem>.card_slots.json` — Card 4's entire payload.

## Job

Pick **one** concept from the owner's current CFA syllabus that maps best to **this specific company**, then write the four `cfa_lens` fields so that a reader (and the owner studying for the exam) learns the concept *through* the company, not in the abstract.

This is not a "show me you know finance" card. It is a teaching card with two simultaneous goals:
1. Make the company easier to evaluate by introducing one analytical lens.
2. Reinforce the owner's CFA prep with a concrete, defensible application.

## Inputs

- The drafted `card_slots.json` (so you can see the intro sentence, industry framing, five-year arc, recent financials)
- `analyst_call.json` and sibling financial / Porter JSON for grounding
- A **CFA progress hint** from one of these sources, evaluated in this order:

  | Priority | Source | How to read |
  |---|---|---|
  | 1 | CLI: `--cfa-progress "Level 2 - Fixed Income - Binomial Tree"` | Already on disk via `validate_cards.py` flag → re-exported to env `CFA_PROGRESS` |
  | 2 | Env var `CFA_PROGRESS` | Directly read |
  | 3 | `USER.md` sticky (anamnesis-research side) | Anamnesis wrapper passes through as CLI arg |
  | 4 | Agent default | Pick an equity-relevant CFA L2 concept that fits the company |

  Record which source you used in `cfa_lens.cfa_progress_source` (one of `CLI` / `env` / `USER.md` / `default`).

## Default-mode concept menu (when no hint)

If you fall through to the agent default, pick from CFA L2 equity-relevant concepts that map well to single-company analysis. Examples by company shape:

| Company shape | Suggested L2 concept | Why it fits |
|---|---|---|
| Mature dividend-paying with stable franchise | DDM multistage / Gordon | Cleanest fit; aliquot dividend assumption holds |
| High-FCF / capital-return platform | FCFE multistage | Better than DDM when buybacks dominate |
| ROE-spread compounder, asset-light | Residual income model (RIM) | Captures excess return without dividend assumption |
| Bond-heavy issuer / financial | OAS, credit-spread valuation, duration | Connects equity risk to balance-sheet structure |
| Strategic-optionality story (platform, biotech, growth) | Real options (Black-Scholes-style) | Prices unexercised expansion / abandonment value |
| Cyclical with binary catalysts (regulation, capex turn) | Binomial tree (state-contingent payoffs) | Decomposes "what is the market pricing" into node probabilities |
| Earnings-driven re-rating story | Justified P/E / P/B with sustainable ROE | Anchors multiple to a defensible spread |
| Heavy R&D / option-like pipeline | Decision-tree valuation | Maps clinical / launch milestones to terminal value |

Do **not** force-fit. If none of these maps cleanly, prefer DDM multistage (most universal) over a forced novel choice.

## Output: the `cfa_lens` object

Required fields (`assert_card_slots_complete` enforces all string fields are non-empty and `company_application` has ≥3 entries):

```json
"cfa_lens": {
  "concept_key": "binomial_tree",
  "concept_name_cn": "二叉树定价",
  "concept_intro": "1-2 句通俗解释这个 CFA 概念在做什么（≤110 字）。",
  "company_application": [
    "应用 1：把哪个变量/业务套进这个模型，关键节点是什么。",
    "应用 2：节点的输入怎么估，哪些 KPI 决定取值。",
    "应用 3：模型反推出来的隐含值 vs 市价，gap 多少。"
  ],
  "different_angle_insight": "1-2 句 — 用这个镜头看，能看到 surface 上看不到的什么（≤105 字）。必须含 primary_quote + 数据锚。",
  "takeaway": "1 句话记忆点（≤48 字）。",
  "cfa_progress_source": "CLI"
}
```

### Field-by-field rules

- **`concept_key`** — snake_case English identifier, e.g. `binomial_tree`, `ddm_multistage`, `residual_income_model`, `real_options`, `fcfe_multistage`, `justified_pe`. Stable across reports so the DB can group by concept.
- **`concept_name_cn`** — short Chinese name. Used as the red title at the top of Card 4.
- **`concept_intro`** — explain what the concept does, in plain language. Do **not** quote the textbook definition. Aim for: "It does X when you have Y." 80-110 字.
- **`company_application`** — 3 bullets (4 OK). Each bullet must:
  - name a concrete variable or business unit from THIS company
  - state how the concept's inputs map to that variable (probability, payoff, discount rate, growth assumption, etc.)
  - end with a number — implied value, gap to market, sensitivity, etc.
  - Banned: vague phrases like "this gives us better insight" without numbers.
- **`different_angle_insight`** — this is the **authority slot** (validator requires `primary_quote` in the worker_notes sidecar). It must:
  - contain at least one numeric data anchor
  - reference a real quote (CFO, CEO, IR transcript, filing) by speaker + venue + date
  - state explicitly what the lens *changes* about the consensus read
  - Banned: hedging phrases like "this might suggest" — be definite.
- **`takeaway`** — single sentence, ≤48 字. Think of it as a 座右铭 the reader will remember a week later. Banned: clickbait CTA, generic "投资有风险" boilerplate.

## Why-this-concept-fits justification (required in worker_notes)

In `<stem>.card_slots_worker_notes.json`, under the key `cfa_lens.different_angle_insight` (or just `different_angle_insight`), you must provide:
- `data_anchor`: the number that anchors the lens decomposition
- `variant_view`: what the lens reveals vs. consensus DCF / single-point estimate
- `primary_quote`: real quote, real speaker, real source URL/filing (REQUIRED — this is the AUTHORITY slot)
- Optional: `falsifier` or `catalyst_with_date` if it sharpens the call

The validator will block export if `primary_quote` is missing or stubbed.

## Handoff

After you write `cfa_lens`, the content production agent picks the file back up and runs Validator 1 (`validate_cards.py`) → Validator 2 (web fact-check). If Validator 1 reports a budget overflow on any `cfa_lens` field, trim that field rather than touching surrounding cards.

See also:
- `agents/content-production-agent.md` § Card 4 — for upstream handoff
- `agents/agent-slot-pipeline.md` — for the full Stage A → E sequence
- `scripts/generate_social_cards.py` § `cfa_lens_data` / `draw_card4_cfa` — for the rendered shape and character budgets
