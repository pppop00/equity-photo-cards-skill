# Validator 1 — deterministic five-card gate

Invocation:

```bash
python scripts/validate_cards.py --input <html-or-dir> --slots <json-or-dir> --palette <confirmed>
```

Use `--allow-no-logo` only after explicit waiver. There is no `--cfa-progress` option.

Blocking checks:

- schema version is exactly 5; old slots are told to rerun P8;
- five active card structures are complete and `cfa_lens` is absent;
- logo/name gate and consistent explicit palette;
- Card 1 has exactly two variables, each on its own aligned line, and all summary rows fit;
- Card 2 has the four causal steps in fixed order, five unique forces, mechanisms, and copy fit;
- Card 3 has a causal five-year story and six fixed-order metrics;
- Card 4 has four evidence-based panels, valuation time point, basis label, and no score;
- Card 5 separates four geographies and contains six fixed dimensions, warnings, insight, unknown;
- claim sidecar covers all required visible prefixes with valid type, date, source refs, basis/falsifier where required;
- visible attribution matches claim type;
- character, line, and pixel geometry budgets pass;
- contradiction, money-scale, period-localization, placeholder, and hardcode checks pass.

Validator 1 does not prove external truth. A clean result proceeds to Validator 2. Any subsequent edit invalidates both verdicts.
