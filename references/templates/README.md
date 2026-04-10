# Card slots templates

- **`card_slots.template.json`** — Structural starter for a **new** report package. Copy to `<html_stem>.card_slots.json` beside the HTML, then replace every field with copy grounded in **that** report (HTML + sibling JSON). The placeholders satisfy `load_card_slots` shape checks; they are **not** intended to pass `validate_cards.py` until replaced with real analysis.
- For a **filled** reference shape, see [`../examples/pdd_holdings_card_slots.example.json`](../examples/pdd_holdings_card_slots.example.json).
