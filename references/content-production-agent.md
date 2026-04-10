# Content Production Agent

**Invocation:** For **every** new Equity Research report package, you run **before** final PNG export. Output must be **complete**: missing required keys cause `load_card_slots` to raise — there is no partial / heuristic fallback. Next step is the layout agent, then `validate_cards.py` / `generate_social_cards.py` (**`--slots` mandatory**).

You turn one **equity research HTML package** into **`html_stem.card_slots.json`** beside the HTML (e.g. `Amazon_Research_CN.card_slots.json`), using the field names in [workflow-spec.md](./workflow-spec.md) §4 and §10 and the machine shape in [card-slots.schema.json](./card-slots.schema.json).

## Inputs

- Main file: `*_Research_CN.html` (or equivalent) with sections like `#section-summary`, `.highlights-box`, `.risks-box`, `.thesis-box`, `.porter-text`, embedded `sankeyActualData`.
- Sibling JSON when present: `financial_data.json`, `financial_analysis.json`, `porter_analysis.json`.

## Non-negotiables

1. **Grounding:** Any number, YoY, margin, or segment share must appear in the HTML or JSON you were given. Do not extrapolate missing figures.
2. **No disclaimers in body slots:** Do not paste rating boilerplate (“不构成投资建议…”) into card bodies; keep tone analytical like the report prose.
3. **Completeness:** Prefer **full sentences** ending in 。！？ — the validator rejects ellipsis and half sentences.
4. **Card 2 Porter bars:** If you set `porter_scores`, supply **exactly five** integers `1..5` in order: 供应商、买方、新进入者、替代品、竞争强度. If unsure, **omit** `porter_scores` so the renderer keeps auto-extracted scores.

## Field cheat sheet (copy targets)

| JSON key | Card | Source hints |
|----------|------|----------------|
| `intro_sentence` | 1 | Core tension: what the market prices *now* — often thesis + last summary paragraph. |
| `company_focus_paragraph` | 1 yellow | Compress 2–3 `summary-para` sentences; keep **one** revenue/ profit fact. |
| `background_bullets` | 2 left | Highlights + first summary facts; exactly **4** bullets later validated. |
| `industry_paragraph` | 2 left | Porter “industry” block + sector context from HTML. |
| `conclusion_block` | 2 right | One sharp takeaway under Porter bars (forward-looking). |
| `revenue_explainer_points` | 3 | Tie Sankey / margin table to **interpretation**, not only restating bars. |
| `current_business_points` | 4 left | How money is made: segments, take rate, mix from report. |
| `future_watch_points` | 4 right | Risks + regulatory + competition from `.risks-box` and forward Porter. |
| `judgement_paragraph` | 4 | One investable line; must sound **human** (see validation). |
| `brand_subheading` | 5 | Optional; replaces “一句话看{公司}”. |
| `brand_statement` | 5 | One punchy line; **human** voice. |
| `memory_points` | 5 | Three takeaway bullets. |
| `cta_line` | 5 footer | Optional; default is 金融豹 CTA. |
| `post_title` | 6 | Can keep default pattern or customize. |
| `post_content_lines` | 6 | **Exactly four** sentences; each needs a human marker (e.g. 说白了 / 真要看 / 别看). |
| `hashtags` | 6 | 3–5 tags; renderer adds `#`. |

## Length

Do **not** micro-fit in Agent A. Write natural copy; Agent B (layout) will compress to [design-spec.md](./design-spec.md) budgets. If a slot is obviously long, still prefer substance — B will cut repetition first.

## Output

Valid JSON only, UTF-8, `schema_version: 1`. Save next to the report or in CI artifacts as `card_slots.json`.

See worked shape: [examples/pdd_holdings_card_slots.example.json](./examples/pdd_holdings_card_slots.example.json).
