# CFA Lens Selector Agent

**Invocation:** Run after the content production agent has drafted Cards 1–3 (so company business model, financial profile, and industry context are already understood). Output is the entire `cfa_lens` object in `<stem>.card_slots.json` — Card 4's full payload.

## Job

Pick **one** CFA L2 concept from the **formula-bearing** menu that maps best to **this specific company**, write the formula in concise Unicode-math form, then plug real numbers from the report into the formula. A reader (and the owner studying for the exam) should learn the concept *through* the company, not in the abstract.

This is not a "show me you know finance" card. It is a teaching card with three simultaneous goals:
1. Make the company easier to evaluate by introducing one analytical lens.
2. Reinforce the owner's CFA prep with a concrete, defensible application.
3. **Carry the formula and worked numbers on the card itself** — the redesigned Card 4 shows formula + company_calculation as first-class slots, not buried in prose.

## Explicit responsibilities, in order

1. **Read CFA progress** from one of these sources, in priority order:

   | Priority | Source | How to read |
   |---|---|---|
   | 1 | CLI: `--cfa-progress "Level 2 - Equity - Operating Leverage"` | Already on disk via `validate_cards.py` flag → re-exported to env `CFA_PROGRESS` |
   | 2 | Env var `CFA_PROGRESS` | Directly read |
   | 3 | `USER.md` sticky (anamnesis-research side) | Anamnesis wrapper passes through as CLI arg |
   | 4 | Agent default | Pick an equity-side L2 concept that fits the company |

   Record which source you used in `cfa_lens.cfa_progress_source` (one of `CLI` / `env` / `USER.md` / `default`).

2. **Pick `concept_key` from FORMULA-BEARING concepts only.** Pure qualitative frameworks (behavioural biases, ethics scenarios, narrative-only Porter overlays) are EXCLUDED because Card 4's formula gate (`'=' + operator`) will reject them.

3. **Write the formula** in concise, Unicode-math form. Must contain `=` and at least one of `/`, `×`, `+`, `−`, `-`, `(`, `Δ`, `%`. Examples below. Keep it to ≤80 characters so it fits the panel.

4. **Write `company_calculation`** (1–3 lines). Plug real numbers from `financial_data.json` / `financial_analysis.json` into the formula. At least one entry MUST contain a digit (validator enforces this). End with the scalar result. This slot is now the **authority slot** — `<stem>.card_slots_worker_notes.json` must back it with a `primary_quote` (CFO / CEO / IR transcript / filing).

5. **Write `concept_intro`** — 1–2 sentences in plain Chinese explaining what the concept does (≤110 chars).

6. **Write `company_application`** — 3 bullets (4 OK). Each bullet must name a concrete variable or business unit from THIS company, state how the concept's inputs map to that variable, and end with a number.

7. **Write `different_angle_insight`** — 1–2 sentences. What does this lens reveal that surface analysis misses? Cite the formula result. ≤105 chars. (No longer the authority slot — `company_calculation` is.)

## Formula-bearing concept menu

Pick the concept that fits the company's economics; do not force-fit. If the upstream `--cfa-progress` hint names a specific L2 module, prefer a formula from that module.

| Concept | Formula (Unicode-math) | Fits |
|---|---|---|
| Operating leverage | `DOL = %ΔEBIT / %ΔRevenue` | High fixed-cost / scale-effect companies (semis, software, datacenter) |
| Sustainable growth rate | `g = ROE × (1 − Payout)` | Compounders, dividend-paying mature franchises |
| Multistage DDM | `V = Σ Dₜ/(1+k)ᵗ + TV/(1+k)ⁿ` | Stable dividend payers transitioning growth phases |
| Gordon constant-growth DDM | `V = D₁ / (k − g)` | Mature dividend-paying utility / staples |
| FCFE multistage | `V = Σ FCFEₜ/(1+k)ᵗ + TV/(1+k)ⁿ` | Capital-return-via-buyback platforms |
| Residual income | `V = B + Σ (ROE − k) × B / (1+k)ᵗ` | High-ROE, asset-light platforms (payments, software) |
| Binomial tree (one-period) | `V₀ = (p × Vu + (1−p) × Vd) / (1+r)` | Binary-catalyst stories (regulation, capex turn) |
| Justified P/E (Gordon-derived) | `P/E = (1 − b) / (k − g)` | Earnings-driven re-ratings |
| Justified P/B | `P/B = (ROE − g) / (k − g)` | ROE-spread compounders |
| OAS / Z-spread | `OAS = Z-spread − option cost` | Bond-heavy issuers, MBS / convertible exposure |
| Key rate duration | `ΔP/P ≈ −Σ KRDᵢ × Δyᵢ` | Insurers, banks, BDCs with curve exposure |

Banned: any "concept" that doesn't yield a formula with `=` and an operator (e.g. "porter's five forces", "Buffett's circle of competence"). Card 4 rejects these on validation.

## Worked examples

The three examples below are concrete enough to crib from. They show the full `cfa_lens` block as it should land in `card_slots.json`.

### Example 1 — Operating leverage / Broadcom (or NVDA)

```json
"cfa_lens": {
  "concept_key": "operating_leverage",
  "concept_name_cn": "经营杠杆",
  "concept_intro": "DOL 衡量收入变化在营业利润上被放大的倍数；固定成本越重、规模效应越强，DOL 越大。",
  "formula": "DOL = %ΔEBIT / %ΔRevenue",
  "company_calculation": [
    "FY26 Q3 营收同比+94%（$35.1B vs $18.1B），营业利润同比+112%",
    "DOL ≈ 112 / 94 = 1.19",
    "FY27 若营收+25%，营业利润弹性约+30%"
  ],
  "company_application": [
    "数据中心占比 87% 意味着固定 R&D 在更宽的收入基础上摊销。",
    "每 10pp 数据中心 mix 提升带来约 2pp 运营利润率改善。",
    "持续的 DOL>1 表明规模效应仍在兑现，未 price-in 到 FY27 共识。"
  ],
  "different_angle_insight": "Street 把 DOL 模型成 1.0（线性），1.19 的实际读数意味着 FY27 运营利润率应达 64%，高于共识 60%。",
  "cfa_progress_source": "CLI"
}
```

### Example 2 — Sustainable growth rate / Micron (or Alibaba)

```json
"cfa_lens": {
  "concept_key": "sustainable_growth_rate",
  "concept_name_cn": "可持续增长率",
  "concept_intro": "SGR 反推一家公司在不增发、不加杠杆的前提下，靠留存利润能撑住的内生增长率上限。",
  "formula": "g = ROE × (1 − Payout)",
  "company_calculation": [
    "FY2024 ROE 约 8.5%（净利润 870 亿 / 平均股东权益 10,200 亿）",
    "回购+分红 ≈ 1,210 亿，Payout ≈ 139%",
    "g = 8.5% × (1 − 1.39) ≈ −3.3%"
  ],
  "company_application": [
    "Payout 超过 100% 意味着账面增长引擎已熄火。",
    "未来增长必须靠云与国际业务的 ROIC，而非淘天的留存利润。",
    "若 ROE 修复到 12% 且 Payout 降到 60%，g 才能回到约 5%。"
  ],
  "different_angle_insight": "SGR 拆出来后，FY2024 阿里返还股东超过净利润，账面增长来自动用现金而非留存——市场仍按内生增长定价。",
  "cfa_progress_source": "default"
}
```

### Example 3 — Multistage DDM / a dividend payer

```json
"cfa_lens": {
  "concept_key": "ddm_multistage",
  "concept_name_cn": "多阶段股利贴现模型",
  "concept_intro": "把公司分成高增长期 → 过渡期 → 永续期，对每段单独估增长率与分红率，再折现回今天。",
  "formula": "V = Σ Dₜ/(1+k)ᵗ + Dₙ₊₁/((k − g) × (1+k)ⁿ)",
  "company_calculation": [
    "D₁ = $5.50/股（FY26 分红），阶段 1 g = 8% 持续 3 年",
    "永续 g = 3%，k = 9%",
    "V = $5.50/(0.09−0.03) ≈ $92/股，vs 当前价 $75（折价 18%）"
  ],
  "company_application": [
    "阶段 1（FY26-FY28）：分红同比+8%，由 cash-generative core 驱动。",
    "阶段 2 转换点：当 Payout 突破 70% 时分红增速降到 4%。",
    "永续阶段：g=3% 对应 GDP-like 假设；terminal value 占今天估值 70%。"
  ],
  "different_angle_insight": "Gordon 段 terminal value 占 70% 说明估值核心在永续假设，对 k 与 g 的 50bp 移动极敏感——这是市场用 18% 折价定的「永续假设折让」。",
  "cfa_progress_source": "CLI"
}
```

## Field-by-field rules

- **`concept_key`** — snake_case English identifier, stable across reports for DB grouping (`operating_leverage`, `sustainable_growth_rate`, `ddm_multistage`, `binomial_tree`, `residual_income_model`, `fcfe_multistage`, `justified_pe`, `key_rate_duration`, etc.).
- **`concept_name_cn`** — short Chinese name. Used as the big red title at the top of the merged Card 4 panel.
- **`concept_intro`** — explain what the concept does, in plain language. Do **not** quote the textbook. ≤110 chars.
- **`formula`** — Unicode-math, ≤80 chars, must contain `=` and at least one of `/`, `×`, `+`, `−`, `-`, `(`, `Δ`, `%`. The hardcode auditor also rejects formulas that name an unknown variable not in the CFA-known whitelist (ROE, ROA, ROIC, EBIT, EBITDA, FCFE, FCFF, WACC, D/E, P/E, P/B, ΔRevenue, ΔEBIT, Payout, Retention, g, k, r, β, σ, COGS, NI, CFO, CapEx, NOPAT, Equity, Debt, Sales — extend as appropriate).
- **`company_calculation`** — 1–3 lines, each ≤70 chars. At least one entry must contain a digit (validator). End with the scalar result. The numbers MUST be traceable to `financial_data.json` / `financial_analysis.json`; Validator 2 cross-checks.
- **`company_application`** — 3 bullets (4 OK). Each bullet must name a concrete variable or business unit from THIS company, map the concept's inputs to it, and end with a number. Banned: vague phrases like "this gives us better insight".
- **`different_angle_insight`** — 1–2 sentences, ≤105 chars. State explicitly what the lens *changes* about the consensus read. Banned: hedging phrases like "this might suggest".

## Authority-slot rules (worker_notes)

Card 4's authority slot moved from `different_angle_insight` to `company_calculation` in schema v3. In `<stem>.card_slots_worker_notes.json`, under the key `cfa_lens.company_calculation` (or just `company_calculation`), you MUST provide:

- `data_anchor`: the number/comp that anchors the formula inputs (where did ROE / DOL / probability come from?)
- `variant_view`: how the formula's output differs from the consensus single-point view
- `primary_quote`: real quote, real speaker, real source URL/filing (REQUIRED — authority)
- Optional: `falsifier` or `catalyst_with_date` if it sharpens the call

The validator blocks export if `primary_quote` is missing or stubbed.

## Handoff

After you write `cfa_lens`, the content production agent picks the file back up and runs Validator 1 (`validate_cards.py`) → Validator 2 (web fact-check). If Validator 1 reports a panel-overflow on the merged Card 4 panel, trim `concept_intro`, then `company_calculation` lines, then `different_angle_insight` — in that order; do not touch surrounding cards.

See also:
- `agents/content-production-agent.md` § Card 4 — for upstream handoff
- `agents/agent-slot-pipeline.md` — for the full Stage A → E sequence
- `scripts/generate_social_cards.py` § `cfa_lens_data` / `card_4_cfa` — for the rendered shape and character budgets
