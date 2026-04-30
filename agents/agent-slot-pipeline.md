# Agent Slot Pipeline (overview)

**Only supported path:** validators and renderer require **`--slots`** and a **complete** `card_slots.json`. There is no CLI-supported heuristic-only export.

End state: six PNGs with **human-grade** Chinese copy **without** losing facts from the research HTML.

## P0 硬门禁（必须先于所有 Stage 完成）

**两个硬门禁都必须解决，才能进入 Stage A–F：**

### 门禁 1: 配色记录
- 必须先由客户或 `USER.md:default_palette` sticky preference 明确选择 `macaron` | `default` | `b` | `c`。
- 接到任务后先记录本次任务唯一的 `--palette` 参数（见 [SKILL.md §配色选择](../SKILL.md#palette-choice)）。
- 没有用户回复或 sticky preference 时停止等待；不得自动把 `macaron` 作为默认值继续。
- 后续所有 `validate_cards.py` 与 `generate_social_cards.py` 调用必须使用同一参数。
- 不得在同一组六张卡中混用不同 palette。

### 门禁 2: Logo 确认
- Logo 是强制要求，无自动跳过选择。
- Stage A (Logo Production) 的规则：**找不到官方 logo → 停止**，等待客户提供官方来源或明确确认放弃。
- 「确认放弃」必须是客户的书面或对话声明，不能是 agent 的假设或自动行为。
- 仅当客户明确放弃时，后续 Validator 1 和 Export 才可使用 `--allow-no-logo` 标志。
- 即使脚本技术上支持无 logo 导出，也禁止默认跳过——「支持」不等于「允许」。

## Roles

| Stage | Agent | Input | Output |
|-------|--------|--------|--------|
| **0** | **Palette record** | Customer conversation or `USER.md` sticky | Record confirmed `macaron` \| `default` \| `b` \| `c`; use it for all downstream CLI calls |
| A | Logo production | HTML identity + web search | `logo_official.png` in **output folder** (create it first); `card_slots.json` updated with **`logo_asset_path`** and **`cover_company_name_cn`** (verified Chinese short name for Card 1 red text) |
| B | Content production | Report HTML + `financial_*.json` + `porter_analysis.json` + logo path | `card_slots.json` (draft) |
| B.5 | Hardcode & logic audit | `card_slots.json` (draft) + normalized report facts | Same file, body copy verified against report facts (see [hardcode-audit-agent.md](./hardcode-audit-agent.md)) |
| C | Layout fill | `card_slots.json` (audited draft) + design-spec + validation rules | `card_slots.json` (Validator 1–ready) |
| D | Validator 1 | `card_slots.json` + HTML | Script exit 0 (`validate_cards.py`) |
| E | Validator 2 | Validator-1-clean `card_slots.json` + HTML + sibling JSON + web search | Same files, **externally fact-checked** (see [validator-2-agent.md](./validator-2-agent.md)) |
| — | Renderer | HTML + final `card_slots.json` | `output/<stem>/*.png` |

Store **`card_slots.json` alongside** `Company_Research_CN.html` in the report workspace (e.g. `Amazon_Research_CN.card_slots.json`) so each package is self-contained.

## Why these stages

- **Stage A** optimizes for *logo quality + canonical cover name*: search official web sources, create the output folder first, save the logo there, set `logo_asset_path` **and** `cover_company_name_cn` (reconcile or translate vs HTML `.company-name-cn` per [logo-production-agent.md](./logo-production-agent.md)); no screenshots or local auto-discovery; export **SVG / high-res PNG** so wide wordmarks are **≥840 px** wide (validator rejects tiny or upscaled rasters).
- **Stage B** optimizes for *substance*: lift thesis, Porter paragraphs, risks, and KPIs from the HTML; no pixel math.
- **Stage B.5 (Hardcode audit)** catches copy that has no company-specific anchor or contradicts normalized facts — runs before layout so bad copy is fixed at the meaning level, before layout compression makes the problem harder to spot.
- **Stage C** optimizes for *constraints*: line wraps, character budgets, mandatory “human voice” markers on Card 6, judgement box height — without watering down meaning.
- **Stage D (Validator 1)** is the script gate: `validate_cards.py` exit 0 required before Validator 2.
- **Stage E (Validator 2)** is not layout: it is a **web fact-check** of everything that will appear on the cards; see [validator-2-agent.md](./validator-2-agent.md). Run only after Validator 1 passes.

## Commands

**Order:** Hardcode audit → Validator 1 → **Validator 2** (agent; no CLI) → export.

```bash
python3 scripts/validate_cards.py --input “/path/Company_Research_CN.html” --slots “/path/Company_Research_CN.card_slots.json” --brand “金融豹” --palette <confirmed_palette>
# … Validator 2: follow validator-2-agent.md (web search every factual claim) …
python3 scripts/generate_social_cards.py --input “/path/Company_Research_CN.html” --slots “/path/Company_Research_CN.card_slots.json” --brand “金融豹” --palette <confirmed_palette>
```

HTML still supplies Sankey numbers, tables, and company metadata. The Card 1 logo file and **red-title Chinese short name** are supplied through `card_slots.logo_asset_path` and **`card_slots.cover_company_name_cn`**, both produced by the logo production agent when a logo is used. JSON slots override copy fields and may also set `porter_scores` (five integers).
