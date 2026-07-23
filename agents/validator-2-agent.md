# Validator 2 — external evidence review

Run only after Validator 1 passes. Build a checklist from every material claim in `card_slots_worker_notes.json`; verify against primary filings and authoritative public sources. Do not treat the sidecar as proof merely because it is well formed.

Verify:

1. company identity, period, currency, units, and headline financials;
2. business model, segment/revenue mix, and the two core variables;
3. Porter evidence and its stated transmission;
4. all Card 3 values and Metric Basis ids, including FCF, capex, net debt, and geography basis;
5. valuation price date, denominator period, share count, and comparable/adjusted/not-comparable status;
6. governance, ownership, voting rights, incentive metrics, and capital-allocation facts;
7. accounting-quality evidence, one-off items, audit wording, cash conversion, and estimate dependence;
8. incorporation, listing, operations, and revenue geography separately;
9. Card 5 country facts from regulators, statistics agencies, central banks, labor/legal sources, or equivalent authorities;
10. every inference's stated mechanism and falsifier, including stereotype and overgeneralization risk; confirm Card 5's bounded country insight is not merely a duplicated company warning or an ungrammatical national generalization.

If a source does not support the precision or scope, correct the slot or downgrade it to `未披露/不可比` with a reason. Then rerun Validator 1 and repeat this review. Only a final clean pair permits rendering.
