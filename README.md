# Equity Photo Cards Skill

Agent skill and Python tooling that turn **equity research HTML** (plus optional sibling JSON) into **six fixed-layout social images** (e.g. Xiaohongshu / Douyin), with slot-based copy and **layout validation** before export.

**中文简介：** 将权益类研报 HTML 规范化为固定 **6 张卡片** 的图文素材；包含 Agent 工作流说明（`SKILL.md`）、版式与设计规范、以及 Python 渲染与校验脚本。

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

**Validate** (check layout / content constraints against parsed HTML):

```bash
python3 scripts/validate_cards.py \
  --input "/absolute/path/to/Company_Research_CN.html" \
  --brand "金融豹"
```

**Render** — single HTML file (defaults to repo `output/`):

```bash
python3 /absolute/path/to/equity-photo-cards-skill/scripts/generate_social_cards.py \
  --input "/absolute/path/to/Company_Research_CN.html" \
  --brand "金融豹"
```

Or from repo root:

```bash
python3 scripts/generate_social_cards.py \
  --input "/absolute/path/to/Company_Research_CN.html" \
  --brand "金融豹"
```

**Render** — batch all `*.html` in a folder:

```bash
python3 scripts/generate_social_cards.py \
  --input "/absolute/path/to/html-folder" \
  --brand "金融豹"
```

Override output location only when needed: `--output-root /other/path`.

Optional JSON next to the HTML (when your report package provides them): `financial_data.json`, `financial_analysis.json`, `porter_analysis.json`. The workflow is described in [references/workflow-spec.md](references/workflow-spec.md).

## Contributing

Maintain separation between extraction, normalization, planning, copy, validation, and rendering. When changing the pipeline contract, update `references/workflow-spec.md` first; for visual rules, update `references/design-spec.md` first ([SKILL.md](SKILL.md) maintenance section).
