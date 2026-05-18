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
2. **Preserve the content production agent’s structure:** same slot keys; same count of bullets (`background_bullets` 4, `revenue_explainer_points` 3, `current_business_points` 4, `future_watch_points` 4, `post_content_lines` 4, `memory_points` 3).
3. **Human voice checks:** Several slots require human-voice checks in `generate_social_cards.py`. For Card 6, use [card6-voice.md](../references/card6-voice.md) as the reasoning target; do not simply add markers like `说白了` / `换句话说` / `结合最近` to pass validation, and do not force examples into identical surface style. Card 6 **each** of the four lines must pass **`card6_line_sounds_human`** and also stay **three statements + one question**.
4. **Judgement + brand lines:** Must satisfy `is_human_copy` in validator — avoid pure analyst cliché without a marker.
5. **Porter scores:** If present, must be length **5**. Otherwise delete the key so the renderer uses auto scores.
6. **Run the validator iteratively.** Fix the **first** reported slot; re-run until clean.

## Typical fixes

- **Card 2 conclusion exceeds box:** Remove parallel clauses; keep subject–verb–object; one period.
- **Card 1 yellow too short / too long:** Tune `company_focus_paragraph` to **150–165 characters** (including punctuation and English) with two sharp ideas. Below 150 fails `MIN_CARD1_FOCUS_CHARS`; above 165 fails `LIMIT_CARD1_FOCUS_CHARS`.
- **Card 3 explainer exceeds yellow panel:** Height is measured from real glyph bounding boxes; prefer shorter third bullet or fewer wraps. Panel allows a fixed pixel budget — tighten wording before asking for renderer changes.
- **Card 3 bullet char limit:** Split one long bullet into two shorter ideas *only if* you still output exactly three bullets total (merge elsewhere).
- **Card 6 “lacks plain-spoken educational voice”:** Rewrite toward [card6-voice.md](../references/card6-voice.md): add a real contradiction, business-mechanism explanation, or useful comparison. Add a marker or metaphor only if it naturally belongs in the sentence.
- **Card 6 sounds formulaic:** Remove repeated openings (`财报里` / `换句话说` / `结合最近` / `真要看`) and replace them with a sharper sentence engine such as `表面是 X，本质是 Y`、`不是 X，而是 Y`、`对比 A，B 更像 C`.
- **Card 6 uses hype markers:** Remove `这波`、`离谱`、`吃瓜`、`笑死`、`好家伙`、`破防`、`扎心`、`爆款`、`杀疯了` and similar traffic-chasing wording.
- **Card 6 sounds like a路演:** Send back to the content production agent — Card 6 should teach the reader how to read the company in 大白话, not repeat FYxxxx figures or flatten the context.
- **Card 6 title/tags:** Title must start with `一天吃透一家公司：`; final hashtags must include `#A股` and `#美股` and stay within 7 tags.

## Output

Overwrite `card_slots.json` with the **final** version, then hand off to **[Validator 2](./validator-2-agent.md)** (external fact-check per validator-2-agent.md). Only after Validator 2 passes may you proceed to `generate_social_cards.py --slots`.
