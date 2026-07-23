# Content Production Agent — schema v5

Run after normalization and logo production. Own all five cards and both output files:

1. `<stem>.card_slots.json` — complete schema v5.
2. `<stem>.card_slots_worker_notes.json` — claim-level evidence.

Read [knowledge-map-v5.md](../references/knowledge-map-v5.md), the machine [schema](../references/card-slots.schema.json), and the normalized research artifacts. Never start from HTML rhetoric alone.

## Writing sequence

1. Freeze company identity, date, reporting period, currency/unit, and incorporation/listing/operations/revenue geography.
2. Resolve every easy-to-confuse number against `metric_basis.json`. Put only short `basis_label` text on cards; keep formulas and comparability state upstream.
3. Draft Card 1 first: business model, exactly two result variables, primary risk. A reader must be able to repeat these after 60 seconds.
4. Draft Card 2 with an explicit context chain before the five forces: external condition → transmission mechanism → company outcome → observable signal. These are four ordered beats, not a fact list. Then write each force as force → transmission → observable risk, not a five-forces definition lesson.
5. Draft Card 3 as business change → revenue/profit/cash-flow result. Use exactly six metrics in the fixed category order.
6. Draft Card 4 from `company_quality.json`: valuation, governance/incentives, capital allocation, accounting quality. No composite score. Write `未披露/不可比` plus reason when needed. In Chinese visible copy, spell formulas as `经营现金流减资本开支` or use ASCII `OCF - Capex`; never emit U+2212.
7. Draft Card 5 from `country_lens.json`: distinct exposure geographies; six fixed dimensions; 1–2 warnings; one bounded country insight; one unknown. Let the arrow and section labels signal interpretation; do not repeat `据此推断` at the start of dimension transmissions, warnings, or the country insight.
8. Build the sidecar by mapping each material statement to its exact `slot_path`.

## Epistemic language

Use only these types:

`company_disclosure | external_fact | analyst_calculation | external_estimate | inference | forecast`.

Make the type audible without badges:

- 公司年报披露……
- 据监管机构或统计机构数据……
- 按经营现金流减资本开支计算……
- 据外部机构估计……
- 据此推断……
- 若……则预计……

Calculations require a valid `basis_id`. Inferences and forecasts require a falsifier. Every claim needs dated source refs. Do not convert missing evidence into a confident sentence.

## Card 3 metric order

`profitability ×3 → cash_flow ×2 → leverage ×1`. Each entry has `label_cn`, `value`, `period_cn`, `category`. For net-cash companies use a net-cash amount, not a net-debt/EBITDA ratio label. Numerical definitions come from the Metric Basis Registry, not from an assumed universal formula.

## Country rules

The fixed dimension order is tax, FX/inflation, regulation, labor, consumer culture, minority-shareholder protection. Each item must contain a sourced country fact, a company-specific transmission, and an observable metric. Reject stereotypes, registration-as-operations shortcuts, and country-wide conclusions drawn from one company.

Write `company_transmission` as the mechanism only because the renderer supplies the causal arrow. Write each `top_warnings` item as a clean clause without a leading inference formula or trailing `；`; the renderer owns joining and final punctuation. Write `company_to_country_insight` as a complete, bounded sentence tied to a named institution, disclosure convention, ownership rule, or market mechanism. Reject `把……易误读为……`; use grammatical order such as `市场容易把……误读为……`.

## Handoff check

- `schema_version` is 5 and `cfa_lens` is absent.
- Logo fields from the logo agent are preserved.
- Required fields are present even when the content says `未披露/不可比`.
- Every required slot prefix has at least one sidecar claim.
- Natural-language attribution agrees with `epistemic_type`.
- Visible copy contains no U+2212; Card 5 contains no repeated `据此推断`, `。；`, or `；；`.
- No visible confidence label or company-quality score.
