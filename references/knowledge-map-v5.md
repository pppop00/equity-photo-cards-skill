# Five-card knowledge-map contract (schema v5)

## Purpose and reader test

The cards use one listed company to explain how a business and its country context work. After 60 seconds, a reader should be able to state the business model, exactly two core variables, and the primary risk. After delivery, recruit at least five real readers for the non-blocking study in the root `references/reader_test.md`: test immediate recall after a 60-second read and repeat the same unaided prompt seven days later. Agents must not simulate participants or invent results.

## Active files

| Card | Filename | Question answered |
|---|---|---|
| 1 | `01_cover.png` | How does it earn, what drives it, what can break? |
| 2 | `02_porter.png` | Which external forces transmit into results? |
| 3 | `03_five_year_financials.png` | How did the model become financial outcomes? |
| 4 | `04_company_quality.png` | What do pricing, governance, capital, and accounting reveal? |
| 5 | `05_country_lens.png` | How institutions and culture shape the company |

Archived four-card slots do not render. Schema v5 has no CFA field.

## Visible copy and evidence

Visible copy uses natural-language attribution, not confidence badges. A claim's sidecar record is authoritative for provenance:

```json
{
  "claim_id": "c4_accounting_cash_conversion",
  "slot_path": "company_quality.accounting_quality.finding",
  "epistemic_type": "analyst_calculation",
  "source_refs": [{"publisher": "Company annual report", "path": "annual_report.pdf", "page": 88}],
  "as_of_date": "2026-07-13",
  "basis_id": "fcf_ocf_minus_capex"
}
```

For `inference` or `forecast`, add a falsifier that states what observation would overturn the claim. Source refs must identify a publisher and a resolvable URL or local path.

## Copy budgets

- Card 1: business model and risk use at most two rendered lines; exactly two core variables use one aligned line each.
- Card 2: four ordered causal-chain entries (external condition → transmission → company outcome → watch signal), then five Porter evidence entries, one force each.
- Card 3: at least three dated inflection points and exactly six financial metrics.
- Card 4: each 2×2 panel has one finding, evidence, and watch item; valuation has 1–2 metrics.
- Card 5: exactly six dimensions, 1–2 warnings, one country insight, one unknown.

Deterministic pixel checks in the renderer remain the final authority when a textual limit and rendered geometry differ.

## Metric basis labels

Do not paste the upstream Metric Basis Registry onto cards. Show a short `basis_label` only for an easy-to-confuse metric, such as `未来12个月`, `OCF - Capex`, `公司口径`, or `固定汇率`. In Chinese prose prefer `经营现金流减资本开支`. Never put Unicode mathematical minus `−` (U+2212) in visible slots because the export font may render a missing-glyph box. The sidecar claim links calculations through `basis_id`; the Anamnesis harness validates that id against `metric_basis.json`.

## Country safeguards

- Title Card 5 `国家如何塑造公司` in Chinese and `How institutions and culture shape the company` in English.
- Treat incorporation, listing, operations, and revenue geography as distinct facts.
- Prefer regulator, statistics agency, central bank, labor authority, legal text, and company disclosures.
- State a bounded mechanism: country fact → company transmission → observable metric.
- Let the arrow and `公司级预警` / `国家观察` labels carry inference semantics; do not repeat `据此推断` in every Card 5 field.
- Keep warning items free of terminal separators before composition; reject `。；`, `；；`, and malformed `把……易误读为……` order.
- Do not turn one company into a claim about an entire country.
- Consumer culture claims need behavioral evidence; nationality-based adjectives are not evidence.
- If evidence is weak, write the unknown rather than filling the panel with a stereotype.

## Missing evidence

Required slots remain structurally present. Use concise language such as `未披露：公司未给出区域利润口径` or `不可比：同业采用不同租赁资本化口径`. Missingness is itself a claim and must have a source reference documenting the search boundary.
