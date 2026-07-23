---
name: equity-photo-cards
description: >-
  Convert an equity-research HTML package into a deterministic five-card company-to-country
  knowledge map. Hard gates: the customer must explicitly choose macaron/default/b/c before
  intake, and final export requires an official logo asset unless the customer explicitly waives
  it. Produces schema-v5 slots, claim-level evidence notes, two-stage validation, and five
  2160×2700 PNGs: one-minute company, Porter, five-year financials, company quality, country lens.
---

# Equity Photo Cards — knowledge map v5

## Product task

通过一家上市公司，帮助读者理解它如何赚钱、哪些变量决定结果、主要风险来自哪里，以及国家制度与文化如何塑造这家公司。

The reader outcome is concrete: after sixty seconds, a reader should be able to explain the business model, two core variables, and the primary risk. This is not an investment recommendation or CFA teaching product.

## Blocking P0 gates

1. **Palette.** Before intake, logo work, extraction, validation, or export, obtain an explicit choice: `macaron` | `default` | `b` | `c`. Never infer a default. Use that value for both validator and renderer.
2. **Logo.** After palette confirmation, inspect the report/output folder and existing slots. Reuse a compliant official asset or run [logo-production-agent.md](./agents/logo-production-agent.md). Final slots require `logo_asset_path` and `cover_company_name_cn`; only an explicit customer waiver permits `--allow-no-logo`.

The renderer rejects screenshots, missing logo paths, and undersized bitmap wordmarks. Prefer a transparent horizontal wordmark at least 840 px wide at export scale.

## Active five-card contract

All new work uses `schema_version: 5`. Archived v3/v4 slots are not silently upgraded and cannot render; rerun content production (P8).

1. `01_cover.png` — one-minute company: how it earns, exactly two core variables, primary risk, headline metrics.
2. `02_porter.png` — industry forces expressed as external variable → transmission → observable risk.
3. `03_five_year_financials.png` — five-year business change and how it became revenue, profit, cash flow, and leverage.
4. `04_company_quality.png` — 2×2: valuation, governance/incentives, capital allocation, accounting quality. No composite score.
5. `05_country_lens.png` — incorporation/listing/operations/revenue geography plus six country dimensions and company-level warnings.

Logical layout is 1080×1350; default PNG export is 2160×2700. The HTML report remains the evidence and audit base; this skill does not change its page skeleton.

Read [references/knowledge-map-v5.md](./references/knowledge-map-v5.md) for slot semantics, claim evidence, country safeguards, and copy budgets. The machine contract is [references/card-slots.schema.json](./references/card-slots.schema.json); start from [references/templates/card_slots.template.json](./references/templates/card_slots.template.json).

## Fixed workflow

Follow in order:

0. Confirm palette.
1. Intake the full report folder. Read sibling JSON before HTML; use HTML for identity, prose, embedded chart variables, and rendering.
2. Produce/reuse the official logo after the palette gate. Save it in the final output folder and write its absolute path into slots.
3. Normalize facts. Resolve period, currency, unit, geography, and metric-definition drift before copywriting.
4. Write a complete `<stem>.card_slots.json` with schema v5.
5. Write `<stem>.card_slots_worker_notes.json` as the claim-level evidence sidecar.
6. Run the hardcode/logic audit and Validator 1; rewrite until clean.
7. Run Validator 2 against primary or authoritative web sources; fix and repeat Validator 1 after every change.
8. Render five PNGs atomically using the same confirmed palette.
9. Visually inspect all five at full size and run the parent harness OCR/numerical/web/database audit when invoked through Anamnesis.

There is no slotless path. `--slots` is required. Missing content must be shown as `未披露` or `不可比` with a reason in authored copy; never invent a fallback claim.

## Inputs and outputs

Preferred input is a report folder containing `*_Research_CN.html` and normalized JSON artifacts. For a single HTML, `--slots` may be the JSON file or its directory. For multiple HTML files, `--slots` must be a directory containing one matching `<stem>.card_slots.json` per report.

Output folder contains exactly the five active PNGs, the slots JSON copied beside them, and the one official logo file actually used. Remove rejected logo variants and temporary downloads after export.

## Claim-level evidence sidecar

`card_slots_worker_notes.json` must contain a non-empty `claims` array. Every material visible claim has:

- `claim_id`: stable unique id.
- `slot_path`: exact path into visible schema-v5 slots.
- `epistemic_type`: one of `company_disclosure | external_fact | analyst_calculation | external_estimate | inference | forecast`.
- `source_refs`: at least one object with `publisher` and `url` or local `path`.
- `as_of_date`: `YYYY-MM-DD`.
- `basis_id`: required for `analyst_calculation` and linked to the Metric Basis Registry upstream.
- `falsifier`: required for `inference` and `forecast`.

Do not render confidence badges. Make epistemic status legible in natural Chinese: `公司年报披露…`, `按经营现金流减资本开支计算…`, `据监管机构数据…`, `据此推断…`, `若…则预计…`. Full provenance stays in the sidecar and database. Use Unicode mathematical minus `−` (U+2212) only in non-rendered source notes; card-visible formulas must use Chinese `减` or ASCII ` - ` so the export font cannot render a missing-glyph box.

The blocking claim gate covers Card 1 business model, both variables, primary risk; Card 2 industry mechanism; Card 3 five-year narrative; all four Card 4 panels; Card 5 dimensions, warnings, and country insight.

## Card-specific rules

### Card 1

`one_minute_summary` replaces the old long company-focus paragraph. `core_variables` contains exactly two entries. Business model and risk may use two rendered lines; each variable must fit its own aligned line. Keep headline metrics to 3–4 `Label|Value` entries.

### Card 2

The right-side context is an ordered causal chain, not four unrelated facts. `background_bullets` must contain exactly these steps in order: `external_condition` → `transmission` → `company_outcome` → `watch_signal`. Every entry has `step` and `text`; each text must fit two lines. Porter evidence then explains each force separately.

Porter scores remain 1–5 and all five forces must be present exactly once. Evidence must explain a company-result transmission, not merely describe the industry. Separate supplier, buyer, rivalry, entrants, and substitutes.

### Card 3

The five-year narrative must connect a business-model or revenue-mix shift to revenue, margins, profit, cash flow, or leverage. The bottom grid contains exactly six metrics in fixed category order: three profitability, two cash-flow, one leverage. Use a short basis label only where readers could otherwise confuse definitions.

### Card 4

Each panel has `finding`, `evidence`, and `watch_item`. Valuation also has one or two as-of metrics with `basis_label`. Do not produce a composite quality score. If governance, incentive, accounting, or valuation evidence is insufficient, say `未披露` or `不可比` and explain why.

Write visible formulas as grammatical prose. Prefer `按经营现金流减资本开支计算` in Chinese; `OCF - Capex` is acceptable when brevity is essential. Never use U+2212 in slots, and do not compress a formula label and an unrelated calculation into malformed punctuation.

### Card 5

Render the title as `国家如何塑造公司` for Chinese reports and `How institutions and culture shape the company` for English reports.

First distinguish incorporation, listing, operations, and revenue geography. Then use the fixed order:

`tax`, `fx_inflation`, `regulation`, `labor`, `consumer_culture`, `minority_shareholder_protection`.

Every dimension uses `country_fact → company_transmission → watch_metric`. Avoid national stereotypes, do not infer operating exposure from incorporation, and do not treat one company as representative without a bounded, sourced mechanism. End with one or two company-level warnings, one country characteristic reflected by this company, and one unknown.

The arrow, `公司级预警`, and `国家观察` labels already make inference status visible. Do not begin every `company_transmission`, warning, or country insight with `据此推断`; reserve that phrase for slots whose layout does not otherwise signal interpretation. Write warning array items without trailing separators so the renderer can join them once. Make the country insight a complete bounded sentence with a concrete institution or market mechanism; reject malformed word order such as `把……易误读为……` and avoid duplicating a company warning as a national generalization.

## Validation and export

From this skill directory:

```bash
python scripts/validate_cards.py \
  --input /abs/path/Company_Research_CN.html \
  --slots /abs/path/Company_Research_CN.card_slots.json \
  --palette macaron

python scripts/generate_social_cards.py \
  --input /abs/path/Company_Research_CN.html \
  --slots /abs/path/Company_Research_CN.card_slots.json \
  --output-root /abs/path/output \
  --palette macaron
```

Use `--allow-no-logo` only after explicit waiver. Do not pass or recreate `--cfa-progress`; CFA Lens is historical and absent from schema v5.

Validator 1 checks schema, completeness, copy/geometry budgets, visible attribution, claim coverage, logo, period localization, and contradiction guards. Validator 2 independently verifies material names, dates, numbers, definitions, valuation time points, governance claims, accounting-quality claims, and country facts. A change after Validator 2 returns to Validator 1.

## Agent handoff

- [agent-slot-pipeline.md](./agents/agent-slot-pipeline.md) — ownership and handoff.
- [content-production-agent.md](./agents/content-production-agent.md) — normalized facts → v5 slots + evidence sidecar.
- [layout-fill-agent.md](./agents/layout-fill-agent.md) — copy fit without changing meaning.
- [hardcode-audit-agent.md](./agents/hardcode-audit-agent.md) — company specificity and logic.
- [validation-agent.md](./agents/validation-agent.md) — deterministic validation.
- [validator-2-agent.md](./agents/validator-2-agent.md) — external fact-check.
- [logo-production-agent.md](./agents/logo-production-agent.md) — official identity asset.

The old CFA selector may remain in repository history for archived schemas, but no active workflow references or invokes it.

## Acceptance checklist

- Explicit palette decision recorded before work.
- Official logo present, or explicit waiver recorded.
- Slots are schema v5; no `cfa_lens`.
- Sidecar claim coverage passes and every calculation references a basis id.
- Five filenames are continuous and exact.
- Cards contain no visible confidence badges or composite quality score.
- Registration/listing/operations/revenue geography are not conflated.
- Card 4 contains no U+2212 missing-glyph risk; Card 5 contains no repeated inference opener or composed punctuation such as `。；`.
- Validator 1 and Validator 2 pass after the last copy change.
- Five images inspected at 2160×2700 with no clipping or unreadable text.
