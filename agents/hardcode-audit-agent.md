# Hardcode and logic audit — schema v5

Audit the final slots before layout validation.

Reject:

- generic prose that could describe any company;
- unexplained number, period, currency, unit, or comparison-base drift;
- Card 2 force descriptions without a company-result transmission;
- Card 3 narratives that list products but do not connect change to financial outcomes;
- valuation without an as-of date or basis label;
- governance/incentive claims without company filings or other authoritative ownership/governance evidence;
- accounting-quality conclusions based on one ratio without cash-flow, disclosure, audit, or estimate context;
- composite quality scores;
- registration, listing, operations, and revenue geography conflation;
- national stereotypes or consumer-culture assertions without behavioral evidence;
- `analyst_calculation` claims without `basis_id`, and inference/forecast claims without falsifier;
- visible copy whose attribution language disagrees with its sidecar type;
- any active `cfa_lens`, CFA selector output, or CFA progress metadata.

Unknown evidence is not a failure when written honestly as `未披露/不可比` with a reason and search boundary. A fabricated answer is a blocking failure.
