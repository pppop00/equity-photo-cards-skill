# Layout Fill Agent

You receive **draft** `card_slots.json` from the content agent. Your job is to **adjust wording only** so that:

`python3 scripts/validate_cards.py --input Report_CN.html --slots card_slots.json`

passes with **zero** issues.

## Inputs

- `card_slots.json` (draft)
- [design-spec.md](./design-spec.md) — canvas, fonts, copy limits
- [validation-agent.md](./validation-agent.md) — what the Python validator enforces
- Same `Report_CN.html` (for sanity checks: company name, tickers, numbers)

## Rules

1. **Do not invent facts.** If a trim would remove a critical number, shorten another clause or merge redundant phrases.
2. **Preserve Agent A’s structure:** same slot keys; same count of bullets (`background_bullets` 4, `revenue_explainer_points` 3, `current_business_points` 4, `future_watch_points` 4, `post_content_lines` 4, `memory_points` 3).
3. **Human voice checks:** Several slots require informal markers (see `HUMAN_MARKERS` in `generate_social_cards.py` — e.g. 说白了, 真要看, 别看). Card 6 **each** of the four lines needs at least one marker from that set.
4. **Judgement + brand lines:** Must satisfy `is_human_copy` in validator — avoid pure analyst cliché without a marker.
5. **Porter scores:** If present, must be length **5**. Otherwise delete the key so the renderer uses auto scores.
6. **Run the validator iteratively.** Fix the **first** reported slot; re-run until clean.

## Typical fixes

- **Card 2 conclusion exceeds box:** Remove parallel clauses; keep subject–verb–object; one period.
- **Card 1 yellow too short / too long:** Tune `company_focus_paragraph` toward 60–132 Chinese characters with two sharp ideas.
- **Card 3 bullet char limit:** Split one long bullet into two shorter ideas *only if* you still output exactly three bullets total (merge elsewhere).
- **Card 6 “lacks human voice”:** Prefix 说白了 / 别看 / 真要看 on the failing line.

## Output

Overwrite `card_slots.json` with the **final** version, then hand off to `generate_social_cards.py --slots`.
