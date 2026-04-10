# Equity Photo Cards Skill

Agent skill and Python tooling that turn **equity research HTML** (plus optional sibling JSON) into **six fixed-layout social images** (e.g. Xiaohongshu / Douyin), with slot-based copy and **layout validation** before export.

**中文简介：** 将权益类研报 HTML 规范化为固定 **6 张卡片** 的图文素材。**唯一支持路径：** 两层 Agent 生成 **完整** `html_stem.card_slots.json` → `validate_cards.py` 与 `generate_social_cards.py` **必须带 `--slots`**；脚本在加载时会拒绝缺字段的 JSON，**不存在**「不写 slots、只靠 Python 模板糊字」的出口。

**Pipeline:** Content agent → layout agent → complete `*.card_slots.json` → validate → render (both commands require `--slots`).

- **Repository:** [pppop00/equity-photo-cards-skill](https://github.com/pppop00/equity-photo-cards-skill)  
- **License:** [Apache-2.0](LICENSE)

## What you get

| Output | Role |
|--------|------|
| Card 1 | Cover + core tension |
| Card 2 | Background + industry + Porter |
| Card 3 | Revenue / profit flow |
| Card 4 | Current business + next 2–3 years |
| Card 5 | Brand close + three memory points |
| Card 6 | Social post copy image (title, body, hashtags) |

Canvas: **1080 × 1350**. Details: [references/design-spec.md](references/design-spec.md).

## Repository layout

| Path | Purpose |
|------|---------|
| [SKILL.md](SKILL.md) | Agent skill contract: intake → extract → normalize → plan → copy → validate → export |
| [references/workflow-spec.md](references/workflow-spec.md) | Pipeline and slot schema |
| [references/design-spec.md](references/design-spec.md) | Typography, colors, spacing, copy limits |
| [references/validation-agent.md](references/validation-agent.md) | Validation policy |
| [references/agent-slot-pipeline.md](references/agent-slot-pipeline.md) | Two-agent copy → `card_slots.json` → render |
| [references/content-production-agent.md](references/content-production-agent.md) | Agent A: HTML → slot copy |
| [references/layout-fill-agent.md](references/layout-fill-agent.md) | Agent B: fit copy to layout rules |
| [references/card-slots.schema.json](references/card-slots.schema.json) | JSON Schema for slot file |
| [references/examples/pdd_holdings_card_slots.example.json](references/examples/pdd_holdings_card_slots.example.json) | Example slot file (PDD-shaped) |
| [scripts/generate_social_cards.py](scripts/generate_social_cards.py) | Parse HTML and render PNGs |
| [scripts/validate_cards.py](scripts/validate_cards.py) | Run checks before export |
| [references/figma-template-sync.js](references/figma-template-sync.js) | Optional Figma helper |

## Using this as an Agent Skill

Copy or symlink this repo (or its files) into your agent’s skills directory, following your tool’s layout rules (e.g. Cursor / Codex skill folders). The entry point for the model is **`SKILL.md`**.

## Python environment

**Requirements:** Python 3.9+ recommended.

**Dependencies:**

```bash
pip install beautifulsoup4 pillow
```

**Fonts:** The renderer defaults to **Arial Unicode** on macOS:

`/System/Library/Fonts/Supplemental/Arial Unicode.ttf`

On other systems, install a compatible font and adjust the `ARIAL` path in `scripts/generate_social_cards.py` if needed.

## Commands

Run **`validate_cards`** from the **repository root** so `scripts/` imports resolve. **`generate_social_cards`** may be run from any working directory: unless you pass `--output-root`, PNG sets are written under this repo’s **`output/<report_stem>/`** (path is fixed relative to the script location, not your shell cwd).

### Validate + render (`--slots` 必填)

Produce a **complete** JSON per [content-production-agent.md](references/content-production-agent.md) and [layout-fill-agent.md](references/layout-fill-agent.md). Incomplete files fail at load (`assert_card_slots_complete`).

**单份 HTML：** `--slots` 传 **`Company_Research_CN.card_slots.json` 的路径**，或传其**所在目录**（脚本会找 `<stem>.card_slots.json`）。

```bash
python3 scripts/validate_cards.py \
  --input "/absolute/path/to/Company_Research_CN.html" \
  --slots "/absolute/path/to/Company_Research_CN.card_slots.json" \
  --brand "金融豹"

python3 scripts/generate_social_cards.py \
  --input "/absolute/path/to/Company_Research_CN.html" \
  --slots "/absolute/path/to/Company_Research_CN.card_slots.json" \
  --brand "金融豹"
```

**批量多只 HTML：** `--input` 指向含多个 `*.html` 的目录时，`--slots` **必须为目录**，且内含与每个 `stem` 对应的 `<stem>.card_slots.json`。

Override output with `--output-root /other/path` if needed.

Optional JSON next to the HTML (when your report package provides them): `financial_data.json`, `financial_analysis.json`, `porter_analysis.json`. The workflow is described in [references/workflow-spec.md](references/workflow-spec.md).

## Contributing

Maintain separation between extraction, normalization, planning, copy, validation, and rendering. When changing the pipeline contract, update `references/workflow-spec.md` first; for visual rules, update `references/design-spec.md` first ([SKILL.md](SKILL.md) maintenance section).
