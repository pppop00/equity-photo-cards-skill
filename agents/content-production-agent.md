# Content Production Agent

**Invocation:** For **every** new Equity Research report package, you run after the logo production agent and before the CFA lens selector. You own Cards 1–3 of the v2 four-card layout; Card 4 (`cfa_lens`) is delegated to [cfa-lens-selector-agent.md](./cfa-lens-selector-agent.md). Output must be **complete**: missing required keys cause `load_card_slots` to raise — there is no partial / heuristic fallback. Downstream: CFA lens selector → layout agent → **`validate_cards.py`** → **[validator-2-agent.md](./validator-2-agent.md)** → **`generate_social_cards.py`** (**`--slots` mandatory**).

Before you materialize `card_slots.json`, follow [SKILL.md](../SKILL.md) **Required Workflow §2–4**: whole-package extraction, normalization, and a four-card slot plan. This file's job is to **write the Cards 1–3 slot copy** once that planning is done. Skipping normalization often yields inconsistent figures across cards or internal contradictions — that conflicts with the grounding rules below.

You turn one **equity research report folder** into **`html_stem.card_slots.json`** beside the HTML (e.g. `Amazon_Research_CN.card_slots.json`), using the field names in [workflow-spec.md](../references/workflow-spec.md) §4 and §10 and the machine shape in [card-slots.schema.json](../references/card-slots.schema.json). Prefer folder input over a standalone HTML path whenever available.

## Inputs

- Preferred input: a report folder containing `*_Research_CN.html` plus sibling JSON files.
- **Primary driver for Cards 1–3:** `<Company>_Research_<lang>.analyst_call.json` — the analyst-layer sidecar from the Equity Research Skill (schema: [`analyst_call.schema.json`](../../Equity%20Research%20Skill/references/analyst_call.schema.json) in the sister repo). **Required. If missing, abort the run — do not heuristic-extract from the HTML to fake it.** See the **Cards 1–3 methodology contract** section below.
- Primary factual sources (for grounding numbers, exact filing quotes, segment shares): `financial_data.json`, `financial_analysis.json`, `porter_analysis.json`.
- Render scaffold: `*_Research_CN.html` (or equivalent) with sections like `#section-summary`, `.highlights-box`, `.risks-box`, `.thesis-box`, `.porter-text`, embedded `sankeyActualData`.
- **Reading order:** `analyst_call.json` **first** (it tells you the call, variant view, key number, comp anchors, catalysts, falsifiers, quotes, asymmetry — i.e. the entire Cards 1–3 spine). HTML + financial / Porter JSON **second**, for fact lookup.

## Non-negotiables

1. **Grounding:** Any number, YoY, margin, or segment share must appear in the HTML or JSON you were given. Do not extrapolate missing figures.
2. **No disclaimers in body slots:** Do not paste rating boilerplate ("不构成投资建议…") into card bodies.
3. **Completeness:** Prefer **full sentences** ending in 。！？ — the validator rejects ellipsis and half sentences.
4. **Card 2 Porter bars + evidence:** `porter_evidence` is required (v2): exactly five entries, one per force (`rivalry`, `new_entrants`, `supplier_power`, `buyer_power`, `substitutes`), each `{force, score 1..5, evidence ≤70 chars}`. `porter_scores` is optional; when present it must be five integers in display order 供应商、买方、新进入者、替代品、竞争强度 and overrides scores from `porter_evidence`.
5. **Logo asset:** Use the `logo_asset_path` produced by [logo-production-agent.md](./logo-production-agent.md). That agent may reuse a valid folder logo after palette confirmation; content production must not independently search folders, clear the path, or use screenshots/ticker-letter placeholders.
6. **Card 1 red-line identity:** If the logo agent already wrote **`logo_asset_path`** and **`cover_company_name_cn`**, treat them as read-only — **do not clear, rename, or overwrite** them when you write the rest of `card_slots.json`.
7. **Card 4 hand-off:** You do NOT write `cfa_lens`. Hand the draft over to [cfa-lens-selector-agent.md](./cfa-lens-selector-agent.md); that agent merges its `cfa_lens` payload into the same file.

## Cards 1–3 methodology contract

Cards 1–3 are **analyst notes**, not HTML compression. The previous brief asked you to compress the locked report into slot prose; that path produced 公众号 clickbait (`说白了…`, `X 不是 Y 而是 Z`, `已不是核心叙事`) because the only way to sound interesting without conviction is rhetorical patois. The fix is to **install the analyst substrate first**: voice is downstream of methodology, never of rhetoric.

Card 4 (CFA lens) is **not** covered here — see [cfa-lens-selector-agent.md](./cfa-lens-selector-agent.md). The contract below applies only to Cards 1–3.

### Reading order (mandatory)

You must open inputs in this order, every run:

1. **`<Company>_Research_<lang>.analyst_call.json`** — the analyst-layer sidecar produced by the Equity Research Skill. **If this file is missing, abort with a clear error message — do not heuristic-extract from the HTML to fake it.** Cards 1–3 are driven by this file.
2. **`<Company>_Research_<lang>.html`** and sibling `financial_*.json` / `porter_analysis.json` — fact lookup (exact numbers, segment shares, verbatim quotes, 5-year history if present).

### New semantics for Cards 1–3

| Card | Role |
|------|------|
| 1 cover | **The call:** 立场 (`call`) + 1-句 variant view + 1 个 anchored 数字 + `metrics_row` |
| 2 Porter | **Industry structure + per-force evidence:** consensus vs variant in the industry paragraph; per-force evidence on each Porter row |
| 3 财务分析 (v4) | **5-year arc + recent quarter bars + 6-metric grid:** transformation story + inflection points + most-recent-quarter Sankey bars + CFA-importance metrics panel (3 profitability + 2 cash-flow + 1 leverage) |

### Slot ↔ `analyst_call.json` field mapping (mandatory)

| Card | Slot | `analyst_call.json` source(s) |
|------|------|-------------------------------|
| 1 | `intro_sentence` | `call` + `variant_view[0]` + 1 `comp_anchor` (highest-magnitude divergence) |
| 1 | `company_focus_paragraph` | `consensus_view` + 1 `key_number` (metric + our_estimate vs consensus) + 1 `comp_anchor` |
| 1 | `metrics_row` (3–4) | Top KPIs from `financial_data.json`; each entry as `"Label\|Value"` |
| 2 | `industry_paragraph` | `porter_analysis.json` industry-context **paired with** consensus-vs-variant framing — explicit "市场认为 X，我们认为 Y" |
| 2 | `background_bullets` (4) | 4 industry facts from `financial_*.json` / `porter_analysis.json` — each bullet 1 number + 1 comp |
| 2 | `porter_evidence` (5) | One entry per force `{force, score 1..5, evidence}`. Pull each `evidence` from `porter_analysis.json` and tie the driver (concentration, switching cost, regulation, moat, capacity cycle, price war, bargaining power) to margins / pricing power / growth / risk |
| 3 | `five_year_arc.narrative` | 2-3 sentence 5-year transformation pulled from `analyst_call.json.thesis_history` or HTML/financial JSON history. Must read in Chinese as: business shift → key financial effect → what changes next. |
| 3 | `five_year_arc.inflection_points` (3–4) | Year-tagged KPI moves: structure change, margin restructuring, geography shift, capital intensity, regulation, customer change |
| 3 | `financial_metrics_panel` (=6, fixed order) | 6 CFA-importance metrics — see "Card 3 metrics panel contract" below. Replaces the v3 `revenue_explainer_points` 收入分析 bullet panel. |
| 3 | `recent_financial_highlights` (legacy, optional) | Old v3 slot. v4 keeps it accepted for backward compatibility but does not render it; you can omit it for new reports. |
| 3 | `revenue_explainer_points` (legacy, optional) | Old v3 slot. Same as above — no longer rendered, may be omitted. |

`logo_asset_path`, `cover_company_name_cn`, and Card 4 `cfa_lens` are **not** authored here — they come from the logo agent and the CFA lens selector respectively.

### Hidden mental fields — required `worker_notes` sidecar

Before writing prose into each Card 1–3 narrative slot, you MUST fill four hidden analytical fields in a **parallel file** named `<Company>_Research_<lang>.card_slots_worker_notes.json`, saved beside `card_slots.json`. These are your "show your work" — the validator and Validator 2 read them to confirm you actually pulled from the analyst layer before writing copy.

Required top-level shape (v2):

```json
{
  "schema_version": 2,
  "intro_sentence":                       { "data_anchor": "...", "variant_view": "...", "falsifier": "...", "primary_quote": { ... } },
  "company_focus_paragraph":              { "data_anchor": "...", "variant_view": "...", "catalyst_with_date": { ... } },
  "industry_paragraph":                   { "data_anchor": "...", "variant_view": "...", "falsifier": "..." },
  "five_year_arc.narrative":              { "data_anchor": "...", "variant_view": "...", "catalyst_with_date": { ... } },
  "cfa_lens.different_angle_insight":     { "data_anchor": "...", "variant_view": "...", "primary_quote": { ... } }
}
```

The last entry (`cfa_lens.different_angle_insight`) is owned by the CFA lens selector — you do NOT write it, but you MUST hand the selector a file with the other four entries filled in.

**v4 note:** the old `revenue_explainer_points` worker-note block was removed alongside the prose slot it backed. Card 3 v4 renders the 6-metric `financial_metrics_panel` instead — that slot is source-anchored numerics, fact-checked against filings by Validator 2, and does not need the analyst-substrate worker_notes scaffolding (which exists to discipline prose, not numbers).

**Required keys per slot block:**

- `data_anchor` — string, **≥10 chars**, must contain a number and at least one comp keyword (`peer` / `历史` / `guidance` / `consensus`) OR a scenario / bull-case / FY-year / 4-digit-year pattern.
- `variant_view` — string, **≥15 chars**, one specific divergence from consensus with a stated mechanism.
- **At least one** of: `falsifier` (≥20 chars), `primary_quote` (object with `speaker`, `venue`, `quote`, `url_or_filing`), `catalyst_with_date` (object with `event`, `date_window` matching `^[0-9]{4}(-(Q[1-4]|[0-9]{2}|H[12]))$` or a range, `implication`).

**`primary_quote` is required (not optional) for `cfa_lens.different_angle_insight`** — the only AUTHORITY slot in v2. The CFA lens selector fills this; you do not.

**Nested-key addressing.** The validator accepts both dotted (`five_year_arc.narrative`) and bare-leaf (`narrative`) keys at the top level of `worker_notes`.

### Banned phrases for Cards 1–4 (backstop only)

These are caught at validator time, but the listing belongs here as a writer-side smell test:

- `说白了`
- The `X 不是 Y，而是 Z` template (regex: `不是.{1,20}[，,]\s*而是`)
- `已不是核心叙事` / `已不重要` / `体现了` / `总而言之` / `综上` / `简单来说`

These phrases are **symptoms** of the methodology gap, not causes. If `data_anchor` / `variant_view` / `falsifier` / `primary_quote` are filled honestly, you will not reach for them.

### Writing style for Cards 1–4: symbols, comparators, CN/EN mixing (backstop also)

The same single-source writing-style rules used by the HTML report apply to card prose. The full reasoning + examples live in the ER repo at `references/report_style_guide_cn.md` §"符号与比较语规范" and §"中英混杂规范"; the validator (`validate_card1_4_analytical_content` in `scripts/generate_social_cards.py`) enforces them. Three patterns you must avoid even when the card budget is tight:

- **Bare `+` in front of absolute amounts.** `Q1收入6.398亿美元，同比增加34%` ✓ — not `Q1收入6.398亿美元+34%` ✗ and not `净收益+10.17亿美元` ✗. The "+" sign is the marker for a relative change; gluing it onto a level (revenue, ARR, FCF, net income) misreads as same-period growth.
- **`+N%` without an explicit comparator base.** Always write 同比 / 环比 / 年化 / 较[基期] before the number. Card layout phase will not let you cheat this by dropping "同比" to fit the budget — trim downstream phrasing, not the comparator. `cRPO 351亿美元，同比按报告值增加16%` ✓; `cRPO +16%` ✗.
- **CN/EN mixing for ratios, units, and time-frame markers.** Company names, product names, and industry abbreviations (Salesforce / Microsoft Dynamics 365 / GAAP / non-GAAP / ARR / RPO / cRPO / SBC) stay English. But `CC` → 恒定汇率, `YoY` → 同比, `QoQ` → 环比, `FX` → 汇率, `pricing power` → 定价权 — these are not acceptable inside card prose. First-mention parentheses are fine (`恒定汇率口径下（CC）`), then drop the English.

Same principle as the banned-phrase backstop: if you fill `data_anchor` (number + comp) and `variant_view` (≥15 chars expressing what the variant view actually is) honestly, you won't be tempted to lean on `+34%` as a substitute for thinking through 同比 vs 环比.

## Field cheat sheet (copy targets — Cards 1–3 only; Card 4 handed off)

| JSON key | Card | Source hints |
|----------|------|----------------|
| `intro_sentence` | 1 | **The call.** `analyst_call.call` + `variant_view[0]` + 1 highest-magnitude `comp_anchor`. Fill `worker_notes.intro_sentence` first. |
| `company_focus_paragraph` | 1 yellow | **Consensus frame + the one number.** `consensus_view` + `key_number` + 1 `comp_anchor`. 150–165 chars. |
| `metrics_row` | 1 metrics | 3 or 4 entries shaped as `"Label\|Value"` (e.g. `"FY26 Q3 总营收\|$35.1B"`). Renderer splits on `\|`. |
| `industry_paragraph` | 2 left | **Porter synthesis paired with consensus-vs-variant.** `porter_analysis` industry-context + explicit "市场认为 X，我们认为 Y". ≤113 chars. |
| `background_bullets` | 2 right | **4 industry bullets, each = 1 number + 1 comp.** ≤60 chars each. |
| `porter_evidence` | 2 bottom | **5 entries, one per force.** Each `{force, score 1..5, evidence ≤70 chars complete sentence}`. The evidence renders next to its score bar. |
| `porter_scores` | 2 (optional) | If supplied, must be 5 integers in display order 供应商、买方、新进入者、替代品、竞争强度; overrides scores from `porter_evidence`. |
| `five_year_arc.narrative` | 3 top | **5-year transformation story.** 2-3 sentences (≤140 chars). Write for Chinese readers: 先说公司做什么变化，再说收入/利润/现金流结果，最后说下一阶段变量。v4 dropped the "过去 5 年的故事" subheader inside the panel; the card-level title 财务分析 frames the section instead. |
| `five_year_arc.inflection_points` | 3 top | 3-4 year-tagged single-sentence inflections, ≤56 chars each. |
| `financial_metrics_panel` | 3 bottom | **6-metric CFA-importance grid (v4).** See the "Card 3 metrics panel contract" section below for the fixed display order, formatting rules, and net-cash fallback. |
| `recent_financial_highlights` | _legacy_ | Old v3 mid-panel labels. Not rendered in v4; safe to omit. |
| `revenue_explainer_points` | _legacy_ | Old v3 收入分析 bottom panel. Replaced by `financial_metrics_panel`; not rendered in v4; safe to omit. |
| `cfa_lens` | 4 | **Owned by [cfa-lens-selector-agent.md](./cfa-lens-selector-agent.md).** Do not write here; hand off Cards 1–3 to that agent. |
| `logo_asset_path` | 1 logo | From the logo production agent. |
| `cover_company_name_cn` | 1 red title | From the logo production agent when `logo_asset_path` is set; you may fill it only when there is no logo AND the HTML `.company-name-cn` is English-only. |

## Card 3 metrics panel contract (v4)

The bottom of Card 3 is a 2×3 frosted-glass grid of 6 CFA-importance financial metrics. The slot is **`financial_metrics_panel`** — a list of exactly 6 objects in this **fixed display order** (the renderer hard-codes which cell gets which category color, so reordering = wrong colors):

| Slot # | label_cn (default) | Category | Cell color |
|--------|--------------------|----------|------------|
| 0 | 毛利率 | `profitability` | GREEN |
| 1 | 营业利润率 | `profitability` | GREEN |
| 2 | 净利率 | `profitability` | GREEN |
| 3 | FCFF | `cash_flow` | BLUE |
| 4 | FCFE | `cash_flow` | BLUE |
| 5 | 净债务/EBITDA 或 净现金 | `leverage` | RED |

**Why these 6.** Three profitability margins are the CFA-canonical income-statement quality gauge. FCFF and FCFE separate firm-level vs equity-level cash returns (CFA L2 valuation staple). Net Debt / EBITDA is the most-cited solvency ratio in CFA + sell-side analyst practice. We deliberately excluded ROE/ROIC (overlaps with margins+leverage), Interest Coverage (collapses on low-leverage software / chip companies), and Debt/FCFE (not standard).

**Per-entry shape:**

```json
{
  "label_cn":  "毛利率",
  "value":    "75.7%",
  "period_cn": "FY2025",
  "category":  "profitability"
}
```

**Formatting rules — strict, validated:**

- `label_cn`: ≤12 CJK chars. Stick to the defaults unless the company's filing genuinely uses a different label (e.g. some SaaS report "经营利润率" rather than "营业利润率" — fine).
- `value`: ≤14 chars. **No currency symbols, no `美元`, no `$`, no `近似` inside the cell** — the unit context is fixed by `data.currency`. Use:
  - Percentages → `"75.7%"` (1 decimal)
  - Currency (FCFF/FCFE) → `"23.37亿"` (2 decimals, just `亿`)
  - Ratio (D/EBITDA) → `"0.5×"` (1 decimal, U+00D7 multiplication sign)
  - Net cash → `label_cn: "净现金"`, `value: "11.89亿"` (2 decimals). Do **not** write `label_cn: "净债务/EBITDA"` with `value: "净现金 11.89亿"`; that mixes a ratio label with a balance-sheet amount.
- `period_cn`: ≤14 chars. `"FY2025"`, `"Q1 FY2026"`, `"近12个月"`, etc.
- `category`: must match the slot's expected category exactly. Validator-1 rejects mismatches.

**Period-label rule.** Still fill `period_cn` for every metric so Validator 2 can fact-check the data period, but do not use it as visual filler. The renderer localizes and collapses a shared period into one panel-level caption (for example `2025财年口径`) instead of printing `FY2025` under all six values. Only mixed-period panels should show per-cell periods, and mixed periods need a real reason (for example margins are FY2025 while FCFF/FCFE are 近12个月).

**Chinese-reader clarity rule for Card 3 top panel.** The top panel is not a list of product names. It must answer, in plain Chinese, three questions:

1. 过去五年公司从什么业务/收入结构变成了什么？
2. 这个变化怎样落到收入、利润率、现金流或资产负债表？
3. 下一阶段哪一个产品、客户、产能、价格或资本开支变量会验证这条线？

Use English only for company/product/protocol names that Chinese investors normally see in English (`Scorpio`, `PCIe`, `CXL`, `NVLink`, `FCFF`, `FCFE`, `EBITDA`). Translate finance/time-frame words: `YoY` → `同比`, `QoQ` → `环比`, `margin` → `利润率`, `revenue stream` → `收入流/收入结构`. Do not write hybrid fragments like `ALAB从PCIe/CXL重定时器扩到Scorpio交换芯片` unless the following clause explains the business meaning in Chinese.

**Example rewrite pattern (do not copy numbers blindly):**

- Weak: `ALAB从PCIe/CXL重定时器扩到Scorpio交换芯片，FY2025收入翻倍、利润转正。`
- Better: `过去五年，阿斯特拉从单一重定时器供应商扩成AI机架连接平台，收入随云厂服务器放量翻倍。高毛利叠加费用摊薄让2025财年转为盈利；接下来要看Scorpio交换芯片能否把产品线从“配套芯片”推向“平台入口”。`

**Source rules:**

- Compute from `financial_data.json` first; fall back to `financial_analysis.json.profitability` / `.cash_flow` / `.leverage` only if the raw numerator/denominator is missing.
- Margins: `gross_margin = gross_profit / revenue`, `operating_margin = operating_income / revenue`, `net_margin = net_income / revenue`. All percentages to 1 decimal.
- FCFF: `CFO + Interest_expense × (1 − effective_tax_rate) − CapEx`. If interest_expense or tax_rate is missing in the source, fall back to `CFO − CapEx`; keep the visible cell as `"2.82亿"` and document approximation in Validator 2 notes, not on the card.
- FCFE: `FCFF − Interest_expense × (1 − tax_rate) + Net_Borrowing`. If net_borrowing is missing, fall back to `CFO − CapEx`; keep the visible cell as `"2.82亿"` and document approximation in Validator 2 notes, not on the card.
- Net Debt / EBITDA: `net_debt / EBITDA`, where `net_debt = total_debt − cash − short_term_investments`. If net debt is positive and EBITDA is usable, report `label_cn = "净债务/EBITDA"`, `value = "0.5×"`. If net debt is negative (net cash), do **not** show a ratio; report `label_cn = "净现金"`, `value = "11.89亿"`. A negative net-debt/EBITDA ratio is not reader-friendly, and a ratio label with a cash value is invalid.
- EBITDA: `Operating_income + D&A`. If D&A is not extractable from cash flow statement, fall back to `Operating_income` only when net debt is positive and label the metric as ratio; if the company is net-cash, skip EBITDA and show net cash amount.
- Period selection: pick the most-recent **annual** value (FY) for stability. Only use a quarterly value if the FY is older than 12 months from report date. If the middle revenue-flow bar chart uses the same annual pool, the chart title should read `20xx财年收入流`, not `FYxxxx 最近季度收入流`.

**Self-check before handoff:** the values you write here must be reproducible from `financial_data.json` to within ±0.5pp (margins) / ±0.5% relative (cash flows). Validator 2 will fact-check each number against the 10-K/10-Q.

## Length

Do **not** micro-fit in this agent. Write natural copy; the layout agent will compress to [design-spec.md](../references/design-spec.md) budgets. If a slot is obviously long, still prefer substance — the layout agent will cut repetition first.

## Output

This agent emits **two** files side-by-side beside the HTML:

1. `<stem>.card_slots.json` — Valid JSON only, UTF-8, `schema_version: 4`. Cards 1–3 filled; `cfa_lens` left to the CFA-lens selector. If you start from a **partial** `card_slots.json` produced by the logo agent, **merge** your body copy into it so **`logo_asset_path`** and **`cover_company_name_cn`** remain exactly as the logo agent set them.
2. `<stem>.card_slots_worker_notes.json` — Valid JSON only, UTF-8, `schema_version: 2`. Hidden analytical fields for Cards 1–3 narrative slots (intro_sentence, company_focus_paragraph, industry_paragraph, five_year_arc.narrative). **Required for every run.** Must be written *before* you draft the prose.

See worked shape for `card_slots.json`: [examples/pdd_holdings_card_slots.example.json](../references/examples/pdd_holdings_card_slots.example.json).
