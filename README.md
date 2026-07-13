# Equity Photo Cards

Deterministic tooling that converts a listed-company research package into five fixed-layout company-to-country knowledge-map images. Active inputs use schema v5 plus a claim-evidence sidecar; archived v3/v4 CFA assets do not render.

## Outputs

| File | Role |
|---|---|
| `01_cover.png` | One-minute business model, two variables, primary risk, headline metrics |
| `02_porter.png` | Industry forces, transmission, observable risk |
| `03_five_year_financials.png` | Five-year business change translated into financial outcomes |
| `04_company_quality.png` | Valuation, governance/incentives, capital allocation, accounting quality |
| `05_country_lens.png` | Exposure map, six country mechanisms, warnings and unknown |

Logical size is 1080×1350; default export is 2160×2700. All five use one explicitly confirmed palette.

## Workflow

Palette gate → official logo → normalized facts → complete schema-v5 slots and claim sidecar → hardcode/layout audit → Validator 1 → Validator 2 → five-card render.

Use [SKILL.md](SKILL.md) as the agent entry, [references/knowledge-map-v5.md](references/knowledge-map-v5.md) for semantics, [references/card-slots.schema.json](references/card-slots.schema.json) for the machine contract, and [references/templates/card_slots.template.json](references/templates/card_slots.template.json) as the starter.

```bash
python scripts/validate_cards.py \
  --input /absolute/path/Company_Research_CN.html \
  --slots /absolute/path/Company_Research_CN.card_slots.json \
  --palette macaron

python scripts/generate_social_cards.py \
  --input /absolute/path/Company_Research_CN.html \
  --slots /absolute/path/Company_Research_CN.card_slots.json \
  --output-root /absolute/path/output \
  --palette macaron
```

`--slots` and `--palette` are mandatory. `--allow-no-logo` is permitted only after explicit customer waiver. There is no active CFA progress option.

License: [Apache-2.0](LICENSE).
