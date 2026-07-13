# Workflow specification — five-card schema v5

The canonical contract is:

`report package → normalized facts + metric/country context → schema-v5 slots + claim evidence → Validator 1 → Validator 2 → five PNGs`.

## Required inputs

- Research HTML as rendering/evidence scaffold.
- Sibling normalized research JSON when available.
- `company_quality.json`, `country_lens.json`, and `metric_basis.json` when invoked from Anamnesis.
- P0-confirmed palette and an official logo asset or explicit waiver.

JSON is preferred for facts; HTML is not a license to copy long paragraphs into cards.

## Required outputs

- `<stem>.card_slots.json`, `schema_version: 5`, conforming to [card-slots.schema.json](./card-slots.schema.json).
- `<stem>.card_slots_worker_notes.json` with the claim-level contract in [knowledge-map-v5.md](./knowledge-map-v5.md).
- Exactly five active PNGs with the continuous filenames listed there.

## Card slots

- Card 1: `intro_sentence`, `metrics_row`, `one_minute_summary.{business_model,core_variables[2],primary_risk}`.
- Card 2: `industry_paragraph`, four ordered `background_bullets` objects (`external_condition`, `transmission`, `company_outcome`, `watch_signal`), `porter_evidence[5]`, optional mirrored `porter_scores[5]`.
- Card 3: `five_year_arc.{narrative,inflection_points[3..4]}`, `financial_metrics_panel[6]`.
- Card 4: `company_quality.{valuation,governance_incentives,capital_allocation,accounting_quality,unknown}`.
- Card 5: `country_lens.{exposure_map,dimensions[6],top_warnings[1..2],company_to_country_insight,unknown}`.

Archived `company_focus_paragraph`, `recent_financial_highlights`, `revenue_explainer_points`, and `cfa_lens` are not active v5 fields.

## Claim sidecar

The root contains `claims`. Each claim has `claim_id`, exact `slot_path`, one fixed `epistemic_type`, non-empty `source_refs`, and `as_of_date`. Calculations add `basis_id`; inferences and forecasts add `falsifier`. Visible source wording must agree with the type.

Required coverage includes all Card 1 summary fields, Card 2 mechanism paragraph, Card 3 narrative, four Card 4 panels, Card 5 dimensions, warnings, and country insight.

## Phase ownership

Content production owns factual coherence across all five cards. Layout fill owns fit only. Validator 1 owns deterministic structure and geometry. Validator 2 owns external verification. The renderer owns pixels and filenames, not editorial fallback.

Any edit after validation returns to Validator 1. Rendering is atomic: an incomplete five-file set is a failure.
