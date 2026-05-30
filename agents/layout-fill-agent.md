# Layout Fill Agent

You receive **draft** `card_slots.json` from the content agent. Your job is to **adjust wording only** so that:

`python3 scripts/validate_cards.py --input Report_CN.html --slots card_slots.json --palette <confirmed_palette>`

passes with **zero** issues (Validator 1 only). After that, **[validator-2-agent.md](./validator-2-agent.md)** runs externally — do not treat layout validation as permission to export until Validator 2 also passes.

## Inputs

- `card_slots.json` (draft)
- [design-spec.md](../references/design-spec.md) — canvas, fonts, copy limits
- [validation-agent.md](./validation-agent.md) — what the Python validator enforces
- Same `Report_CN.html` (for sanity checks: company name, tickers, numbers)

## Rules

1. **Do not invent facts.** If a trim would remove a critical number, shorten another clause or merge redundant phrases.
2. **Preserve the upstream agents' structure:** same slot keys; same counts (`metrics_row` 3-4, `background_bullets` 4, `porter_evidence` 5, `five_year_arc.inflection_points` 3-4, `financial_metrics_panel` =6 fixed order, `cfa_lens.company_application` 3-4). The v3-era `recent_financial_highlights` / `revenue_explainer_points` are no longer rendered in v4 (财务分析). If the upstream agent already wrote them, leave as-is for backward compatibility but do not create new ones; instead author the 6-metric `financial_metrics_panel`.
3. **Card 4 CFA insight tone:** `cfa_lens.different_angle_insight` is the analyst-authority slot — keep the real quote and the number it anchors. If you trim, trim the surrounding description, not the source attribution.
4. **Porter scores:** `porter_evidence` is required (5 entries, one per force). `porter_scores` is optional but if present must be length 5. Otherwise delete the optional key so the renderer derives scores from `porter_evidence`.
5. **Run the validator iteratively.** Fix the **first** reported slot; re-run until clean.

## Typical fixes

- **Card 1 yellow too short / too long:** Tune `company_focus_paragraph` to **150–165 characters** (including punctuation and English). Below 150 fails `MIN_CARD1_FOCUS_CHARS`; above 165 fails `LIMIT_CARD1_FOCUS_CHARS`.
- **Card 2 industry paragraph exceeds box:** Cap at 113 chars; remove parallel clauses.
- **Card 2 porter_evidence too long:** Each `evidence` ≤70 chars; rewrite as a single complete sentence rather than two clauses.
- **Card 3 five_year_arc.narrative overflows:** Cap at 140 chars; trim the inflection_points instead if the narrative itself is essential.
- **Card 3 top story is hard to understand:** Rewrite for a Chinese reader before micro-fitting. Use the Chinese company short name, explain the business shift, then the financial result, then the next validation variable. Replace `FY2025` / `2026 Q1` / `2026 H2` / `同比+N%` with `2025财年` / `2026财年一季度` / `2026年下半年` / `同比增长N%` in visible Chinese prose.
- **Card 3 metrics period repeats visually:** Keep `financial_metrics_panel[].period_cn` in JSON for audit. If all six periods match, the renderer shows one panel-level caption and hides repeated per-cell footers; do not delete `period_cn` to solve visual clutter.
- **Card 3 explainer exceeds yellow panel:** Legacy v3 only. In v4, do not create `revenue_explainer_points`; use `financial_metrics_panel`.
- **Card 4 cfa_lens fields exceed budgets:** concept_intro ≤110, company_application bullets ≤95 each, different_angle_insight ≤105, takeaway ≤48. The takeaway is hardest to compress without losing meaning — work on the surrounding fields first.

## Output

Overwrite `card_slots.json` with the **final** version, then hand off to **[Validator 2](./validator-2-agent.md)** (external fact-check per validator-2-agent.md). Only after Validator 2 passes may you proceed to `generate_social_cards.py --slots`.
