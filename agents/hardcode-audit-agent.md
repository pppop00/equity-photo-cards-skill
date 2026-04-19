# Hardcode Audit Agent

This audit runs after slot copy is generated and before layout validation. Its job is to block two classes of failure:

1. residual hardcoded body copy that could be reused across unrelated companies
2. sentences that contradict the normalized facts in the current report package

## Placement In The Loop

This agent runs at **step 5** in the pipeline. Steps 1–4 are upstream (already completed before this agent is invoked). The full sequence is shown below for context:

1. extract *(upstream)*
2. normalize *(upstream)*
3. logo production *(upstream)*
4. plan slots *(upstream)*
5. write slot copy (content production agent) *(upstream)*
6. **run hardcode and logic audit** ← **this agent**, before layout
7. run layout fill agent *(downstream)*
8. run Validator 1 (`validate_cards.py`) *(downstream)*
9. rewrite failing slots only → rerun layout → rerun Validator 1 *(downstream)*
10. run Validator 2 (web fact-check) *(downstream)*
11. export *(downstream)*

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

## Failure Policy

- Do not export if the audit fails
- Rewrite from source facts first
- Keep the voice shell if useful, but replace the body with report-specific substance
- If source text is thin, use normalized facts and measured inference instead of sector slogans
