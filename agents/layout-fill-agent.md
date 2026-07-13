# Layout Fill Agent — schema v5

Fit already-grounded copy into fixed five-card frames. Do not add facts, change sources, reclassify an epistemic type, or alter a metric basis.

Rules:

- Preserve all schema keys and counts: two Card 1 variables, four ordered Card 2 causal-chain entries, five forces, at least three Card 3 inflections, six financial metrics, four Card 4 panels, six Card 5 dimensions, 1–2 warnings.
- Card 1 uses fixed columns: do not merge the two core variables into one semicolon paragraph. Each variable must fit one line.
- Shorten mechanism wording before deleting the observable metric or attribution phrase.
- Never remove `未披露/不可比` reasons to save space.
- Keep `公司披露 / 据…数据 / 按…计算 / 据此推断 / 若…则预计` wording consistent with the sidecar.
- Do not put full metric registry records, source URLs, confidence labels, or composite scores on cards.
- If a panel cannot fit without changing meaning, return it to content production instead of forcing a tiny font.

After edits, update sidecar `slot_path` only if list indices changed, then rerun Validator 1 and Validator 2.
