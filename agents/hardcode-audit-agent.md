# Hardcode Audit Agent

This audit runs after slot copy is generated and before layout validation. Its job is to block two classes of failure:

1. residual hardcoded body copy that could be reused across unrelated companies
2. sentences that contradict the normalized facts in the current report package

## Placement In The Loop

This agent runs after both the content production agent (Cards 1–3) and the CFA lens selector (Card 4) have written their copy. Full pipeline for context:

1. extract *(upstream)*
2. normalize *(upstream)*
3. logo production *(upstream)*
4. plan slots *(upstream)*
5. write Cards 1–3 (content production agent) *(upstream)*
6. write Card 4 (CFA lens selector) *(upstream)*
7. **run hardcode and logic audit** ← **this agent**, before layout
8. run layout fill agent *(downstream)*
9. run Validator 1 (`validate_cards.py`) *(downstream)*
10. rewrite failing slots only → rerun layout → rerun Validator 1 *(downstream)*
11. run Validator 2 (web fact-check) *(downstream)*
12. export *(downstream)*

Running audit before layout means bad copy is caught while it is still full-length and easy to read. Layout compression can obscure the same issue by making a vague sentence harder to spot.

## What The Audit Must Reject

- Any known forbidden template phrase that survived from old theme-based fallbacks
- Any cross-report company name or product residue that does not appear in the current report package
- Any body copy that has no company-specific anchor
- Any claim that contradicts normalized facts such as growth, segment mix, or profitability direction

## Company-Specific Anchor Rule

Voice shells are allowed:

- `说白了`
- `别看`
- `真要看的是`

But the body after that shell must still anchor to the current report through at least one of:

- company name or ticker
- a real metric or number
- a source keyword from summary, highlights, risks, thesis, Porter text, or normalized segment names

If the sentence could be copied into another company card by changing only the numbers, reject it.

## Logic Checks

At minimum, check for:

- if net-income growth is materially faster than revenue growth, copy must not say profit lagged revenue
- if net-income growth materially trails revenue growth, copy must not say profit outpaced revenue
- if normalized segment data does not support a two-engine framing, copy must not claim `双轮驱动`

Add new logic checks whenever a recurring factual contradiction is discovered.

## Card 4 formula sanity check

Card 4 ships a CFA L2 formula plus a worked numeric calculation. Reject these failure modes:

- **Textual claim posing as a formula.** `cfa_lens.formula` must contain `=` AND at least one math operator (`/`, `×`, `+`, `−`, `-`, `(`, `Δ`, `%`). Examples to reject:
  - `公式：经营杠杆` (no operator, just a label)
  - `就是 ROE` (no `=`)
  - `DOL > 1 意味着有杠杆` (`>` is not on the operator list; rewrite as `DOL = %ΔEBIT / %ΔRevenue`)
- **Unknown-variable formula.** Variables in the formula must come from the CFA-known whitelist:
  `ROE`, `ROA`, `ROIC`, `EBIT`, `EBITDA`, `EPS`, `FCFE`, `FCFF`, `WACC`, `D/E`, `P/E`, `P/B`, `ΔRevenue`, `ΔEBIT`, `ΔSales`, `Payout`, `Retention`, `g`, `k`, `r`, `β`, `σ`, `COGS`, `NI`, `CFO`, `CapEx`, `NOPAT`, `Equity`, `Debt`, `Sales`, `B` (book equity), `D` (dividend), `V` / `V₀` / `Vu` / `Vd`, `KRD`, `OAS`, `Z-spread`, `DOL`, `DFL`, `DTL`, `SGR`, `TV` (terminal value), `p` (risk-neutral probability), `Δy` / `Δyᵢ`.
  Extend the whitelist when a legitimate L2 concept introduces a new symbol; do not allow ad-hoc variables that aren't on a CFA L2 syllabus. This audit is heuristic — a few false positives are OK if the writer can override with a clear justification line in worker_notes.
- **Symbol-only `company_calculation`.** Reject entries that contain ONLY letters / symbols and no digits — the whole point is to plug REAL company numbers into the formula. The validator already enforces "at least one entry contains a digit"; this audit goes further and flags individual entries that are clearly variable-only restatements (e.g. `g = ROE × (1 − Payout)` repeated without numbers).
- **Formula / calculation mismatch.** If the formula is `DOL = %ΔEBIT / %ΔRevenue`, the calculation must visibly divide an EBIT-style growth number by a revenue-style growth number. Calculations that name unrelated quantities (e.g. "FY2024 revenue was 8000 亿") fail.
- **Concept / company mismatch.** Do not let the writer use DDM on a company that has never paid a dividend, or a binomial tree on a single-deterministic-cash-flow utility. If concept_key is wrong for the company shape, send the writer back to `cfa-lens-selector-agent.md` § "Formula-bearing concept menu" to re-pick.

Acceptable override: if the writer writes a clear `formula_justification` line in `<stem>.card_slots_worker_notes.json` under `cfa_lens.company_calculation`, the auditor may pass a borderline formula. The override is on the writer, not the auditor.

## Failure Policy

- Do not export if the audit fails
- Rewrite from source facts first
- Keep the voice shell if useful, but replace the body with report-specific substance
- If source text is thin, use normalized facts and measured inference instead of sector slogans
