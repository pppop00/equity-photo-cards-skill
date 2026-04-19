# Validation Agent（Validator 1）

This document describes what **`scripts/validate_cards.py`** enforces — **Validator 1** (layout, completeness, internal consistency with the report package, logo rules). It does **not** replace **[validator-2-agent.md](./validator-2-agent.md)** (external fact-check via web search before export).

Run this validation pass after card slots have been planned, filled with copy, and audited for hardcoded wording and logical consistency, but **before** [Validator 2](./validator-2-agent.md) and **before** final image export. If any check fails, revise the failing slot copy or slot mapping and validate again until every check passes.

**P0 / logo（硬门禁，无自动跳过）:** By default, **`logo_asset_path` must be set**，文件必须存在且通过尺寸检查，否则 Validator 1 **强制失败**。Logo 不是可选的；即使脚本支持 `--allow-no-logo` 标志，也仅在客户**明确书面放弃 logo** 时允许使用。

具体要求：
- `logo_asset_path` 必须是非空的绝对路径，指向存在于 **output folder 同级** 的真实文件（与 6 张 PNG 同目录）。
- Logo 文件必须通过 `logo_asset_dimension_issues` 检查：水平字标 **≥840 px 宽**，竖向 **≥288 px 高**，方形 **≥512 px** 长边。放大的 favicon 和模糊位图会失败。
- `cover_company_name_cn` 必须同时设置——供 Card 1 红色标题使用。

**标准流程**：
1. Logo production agent 搜索官方 logo → 找不到就停止，等待客户决策（无自动跳过）
2. 如果客户明确放弃，才可在 Validator 1 和 export 时传入 `--allow-no-logo`
3. 不得因为脚本支持这个标志就默认跳过——「支持跳过」≠「允许跳过」

**原则**：缺失或无效 logo 是阻塞缺陷，不是警告。

Validation belongs inside the generation loop:

1. plan card slots
2. write slot copy
3. audit hardcoded wording and logic
4. **Validator 1:** `validate_cards.py`
5. rewrite only the failing slot, then **Validator 1** again until clean
6. **Validator 2:** [validator-2-agent.md](./validator-2-agent.md) — web fact-check every material claim in slots; fix copy and repeat steps 4–5 until **both** pass
7. export (`generate_social_cards.py`) only after Validator 1 **and** Validator 2 pass

## What Validator 1 does **not** check

- **Runtime `--palette` consistency:** The same report’s six PNGs must all be rendered with the **same** `--palette` (`macaron` | `default` | `b` | `c`). Validator 1 now accepts `--palette` and defaults to `macaron`; use the same palette for validation and export. The slot file does not store palette, so if someone re-renders only `01_cover.png` with a different palette than cards 2–6, the **top header colors** will mismatch.

## Three categories of Validator 1 checks

### 1. Language fluency (语句通顺)
Every body slot must be grammatically coherent Chinese — not just punctuation-terminated. The script enforces:
- `is_complete_copy()`: no ellipsis, ends with `。！？`, non-empty text.
- `is_human_copy()` / `card6_line_sounds_human()`: must contain a human-voice marker (Card 4 judgement, Card 5 brand statement, all Card 6 lines).

The **agent-level** check for semantic coherence sits in the hardcode-audit-agent and layout-fill-agent: a sentence that ends with `。` but is semantically empty ("说白了，这家公司很好。") is a layout-agent failure, not a script-level pass. If the validator passes but the copy sounds hollow, rewrite before export anyway.

### 2. Layout overflow (排版不超框)
The script measures real pixel heights using the same font/wrapping engine as the renderer. Every slot has both a character budget (static) and a rendered-height budget (dynamic). Both must pass:
- **Character budgets** are constants (`LIMIT_CARD1_FOCUS_CHARS`, `LIMIT_CARD2_INDUSTRY_CHARS`, `LIMIT_CARD3_EXPLAINER_CHARS`, etc.) — quick first-pass check.
- **Pixel-height budgets** use `measure_bullets()` / `block_final_y()` on the actual glyph bounding boxes — these can reject copy that is under the character limit but wraps too wide.

Do not try to fix an overflow by compressing whitespace alone. Rewrite the copy to be shorter.

### 3. Data integrity (数据完整性)
- **Missing fields:** `assert_card_slots_complete` blocks export if any required slot key is absent or empty.
- **Placeholder values:** Card 3 numeric and margin fields may not render as `--` / `N/A` / `不适用`. Must derive from financial_data or Sankey before export.
- **Zero revenue:** `revenue = 0` in `financial_data.income_statement.current_year` is treated as an extraction error and blocks export. Re-extract from the report package.
- **Margin consistency:** Gross / operating / net margins are cross-checked against `financial_data` income statement values. Discrepancy > 0.5 pp is a hard failure.

## Required Checks

- `card_slots.json` must pass **`assert_card_slots_complete`** (all required slot keys populated) before layout checks run
- When `logo_asset_path` is set, **`validate_report`** checks logo file dimensions (`logo_asset_dimension_issues` in `generate_social_cards.py`): horizontal wordmarks must be **≥840 px** wide (Card 1 slot at `LAYOUT_SCALE=2`), vertical marks **≥288 px** tall, square-ish marks **≥512 px** on the long side — this blocks upscaled favicons and other soft rasters
- Company display name must use the short Chinese company name, not the full legal name with `公司` (resolved via `company_short_cn()` in `generate_social_cards.py`: **with `logo_asset_path` set, always `card_slots.cover_company_name_cn`** from logo production; **without a logo**, HTML `.company-name-cn` when it contains CJK, else `cover_company_name_cn` if the content agent filled it for English-only HTML)
- When **`logo_asset_path`** is set, **`cover_company_name_cn` must be non-empty** (logo production agent)
- The resolved cover name **must contain CJK** — otherwise validation fails
- Footer must be exactly `公司名 | 日期`
- Font family must stay in the Arial family
- Colors must stay inside the approved palette in `design-spec.md`
- No text may overlap another text block, decorative element, or section frame
- No text may exceed its section box
- Numbers, percentages, tickers, and English words must not be split across lines
- Approved English proper nouns such as `FSD`, `Robotaxi`, and `Optimus` are allowed, but they still may not be split across lines
- Commas, periods, semicolons, colons, enumeration commas, and equivalent punctuation must remain attached to the previous line
- Any line that starts with `，。；：、,.!?` or equivalent closing punctuation fails validation
- Card 1 `公司看点` must use enough copy to avoid large empty yellow-panel space
- Card 1 `公司看点` must also stay inside its explicit character budget
- Card 2 `行业层面` must be a complete summarized paragraph, not a clipped fragment
- Card 2 `行业层面` must stay inside its explicit character budget
- Card 3 explainer bullets must stay inside their per-bullet character budget and the yellow panel's **measured** height budget (validator sums `line_raster_height` per wrapped line, matching `draw_text`, not `font.size` alone; panel bottom y is **1260** with bottom inset reserved)
- Card 3 title must be `实际收入分析`
- Card 3 yellow panel title must be `收入分析`
- Card 3 numeric fields and margin fields must not render as placeholders (`--`, `N/A`, `不适用`); if source data is missing, derive from available report data (e.g., Sankey + income statement) or fail and revise before export
- Card 2 left card must feel editorially dense: prefer 4 bullets and enough copy to avoid large empty lower-half whitespace
- Card 2, Card 4 judgement, Card 5 main statement, and Card 6 content lines must not use ellipses or half-sentences as a layout escape hatch
- Any paragraph or bullet that is meant to be read as body copy must end as a complete Chinese sentence
- Card 4 judgement, Card 5 main statement, and Card 6 content must sound like a smart human explaining the company, not like stiff analyst boilerplate
- Card 4 left and right columns should be filled as much as possible without overflow
- Card 4 left and right columns must hit a minimum occupied height; obvious dead air is a validation failure
- Card 4 left and right columns must obey their per-bullet character budgets
- Card 5 must not include `今天这家公司，特斯拉` or any equivalent preface line
- Card 6 must include `title`, `content`, and `hashtags`; title must start with `一天吃透一家公司：`
- Card 6 content must contain exactly 4 bullet lines as **three statements + one question**; each line must pass **`card6_line_sounds_human`** (`HUMAN_MARKERS` or `CARD6_COLLOQUIAL_MARKERS` in `generate_social_cards.py`); **editorial pass:** tone should match [content-production-agent.md](./content-production-agent.md) Card 6 (贴吧 / forum energy, hidden insight, not sell-side recap)
- Card 6 hashtags must fit inside the hashtag section, include `#A股` and `#美股`, and the total hashtag count may not exceed 7
- Text rendering must use high-quality supersampling so exported fonts remain crisp

## Execution

`--slots` is **required** for both tools. Pass a **JSON file** (single HTML) or a **directory** of `<stem>.card_slots.json` when `--input` lists multiple HTML files. The loader rejects incomplete slot files before these checks run.

```bash
python3 scripts/validate_cards.py \
  --input "/abs/path/to/Company_Research_CN.html" \
  --slots "/abs/path/to/Company_Research_CN.card_slots.json" \
  --brand "金融豹" \
  --palette macaron

python3 scripts/generate_social_cards.py \
  --input "/abs/path/to/Company_Research_CN.html" \
  --slots "/abs/path/to/Company_Research_CN.card_slots.json" \
  --brand "金融豹" \
  --palette macaron
```

(Renderer defaults to this skill repo’s `output/<report_stem>/`; pass `--output-root` to override.)

**After** the commands above succeed, run **[Validator 2](./validator-2-agent.md)** before `generate_social_cards.py`.

## Failure Policy

- Do not produce final images if **Validator 1** or **Validator 2** fails
- Fix the failing slot, not the whole report, unless the slot failure reveals an upstream planning mistake
- Fix content density before shrinking fonts
- Fix numeric and English line wrapping before shortening copy
- Do not replace approved English product names with Chinese unless layout truly cannot pass validation
- Prefer rewriting copy into complete Chinese sentences over clipping with ellipses
- If copy sounds dead, rewrite it; do not let layout validation excuse corpse-like prose
