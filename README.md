# Equity Photo Cards Skill

Agent skill and Python tooling that turn **equity research HTML** (plus optional sibling JSON) into **six fixed-layout social images** (e.g. Xiaohongshu / Douyin), with slot-based copy and **layout validation** before export.

**中文简介：** 将权益类研报 HTML 规范化为固定 **6 张卡片** 的图文素材。**唯一支持路径：** 两层 Agent 生成 **完整** `html_stem.card_slots.json` → `validate_cards.py` 与 `generate_social_cards.py` **必须带 `--slots`**；脚本在加载时会拒绝缺字段的 JSON，**不存在**「不写 slots、只靠 Python 模板糊字」的出口。

**Pipeline:** HTML in → content agent → layout agent → hardcode/logic audit on slot text → `validate_cards.py` → `generate_social_cards.py` (both CLIs require `--slots`; slots map copy into fixed card frames).

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

Layout coordinates: **1080 × 1350** (logical). Default PNG export: **2160 × 2700** (full render resolution; use `generate_social_cards.py --export-logical-size` for 1080×1350). Details: [references/design-spec.md](references/design-spec.md).

## Repository layout

Follows **skill-creator** bundle layout: **`SKILL.md`** (entry) → **`references/`** (progressive disclosure) → **`agents/`** (sub-agent instructions) → **`scripts/`** (CLI) → **`evals/`** (optional tests). Default PNGs go to **`output/<stem>/`** (gitignored).

| Path | Purpose |
|------|---------|
| [SKILL.md](SKILL.md) | Agent skill contract: intake → extract → normalize → plan → copy → validate → export |
| [references/workflow-spec.md](references/workflow-spec.md) | Pipeline and slot schema |
| [references/workflow-flowchart.md](references/workflow-flowchart.md) | Mermaid：bundle 表、端到端、CLI、`card_slots` 启动、校验分层、九步 |
| [references/templates/README.md](references/templates/README.md) | 模版目录说明（template vs example） |
| [references/design-spec.md](references/design-spec.md) | Typography, colors, spacing, copy limits |
| [references/card-slots.schema.json](references/card-slots.schema.json) | JSON Schema for slot file |
| [references/templates/card_slots.template.json](references/templates/card_slots.template.json) | Copy to `<stem>.card_slots.json` for each new report, then replace placeholders |
| [references/examples/pdd_holdings_card_slots.example.json](references/examples/pdd_holdings_card_slots.example.json) | Example slot file (PDD-shaped) |
| [agents/agent-slot-pipeline.md](agents/agent-slot-pipeline.md) | Two-agent copy → `card_slots.json` → render |
| [agents/content-production-agent.md](agents/content-production-agent.md) | Agent A: HTML → slot copy |
| [agents/layout-fill-agent.md](agents/layout-fill-agent.md) | Agent B: fit copy to layout rules |
| [agents/hardcode-audit-agent.md](agents/hardcode-audit-agent.md) | Hardcode / logic audit before validation |
| [agents/validation-agent.md](agents/validation-agent.md) | Validation policy (what `validate_cards.py` enforces) |
| [scripts/generate_social_cards.py](scripts/generate_social_cards.py) | Parse HTML and render PNGs |
| [scripts/validate_cards.py](scripts/validate_cards.py) | Run checks before export |
| [evals/evals.json](evals/evals.json) | Optional smoke-test prompts for the skill |

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

Produce a **complete** JSON per [content-production-agent.md](agents/content-production-agent.md) and [layout-fill-agent.md](agents/layout-fill-agent.md). Incomplete files fail at load (`assert_card_slots_complete`).

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

**与 PNG 同目录的 JSON：** 主副本仍在报告文件夹（与 HTML 并列）；`generate_social_cards.py` 默认会把同名的 `*.card_slots.json` **再复制一份**到 `output/<stem>/`，便于打包发图。不需要复制时加 `--no-copy-slots`。

Override output with `--output-root /other/path` if needed.

Optional JSON next to the HTML (when your report package provides them): `financial_data.json`, `financial_analysis.json`, `porter_analysis.json`. The workflow is described in [references/workflow-spec.md](references/workflow-spec.md).

## Contributing

Maintain separation between extraction, normalization, planning, copy, validation, and rendering. When changing the pipeline contract, update `references/workflow-spec.md` first; for visual rules, update `references/design-spec.md` first ([SKILL.md](SKILL.md) maintenance section).
