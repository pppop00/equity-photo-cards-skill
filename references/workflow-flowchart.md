# Equity Photo Skill — 流程图（审阅版）

与 [SKILL.md](../SKILL.md)、[workflow-spec.md](./workflow-spec.md) 一致；在支持 Mermaid 的编辑器或 GitHub 中预览。

---

## 0. Skill 目录 bundle（skill-creator anatomy）

| 路径 | 职责 |
|------|------|
| `SKILL.md` | 模型入口：原则、步骤、链接（正文保持精简） |
| `agents/` | 子 Agent 说明：内容生产 → 排版填充 → 硬编码/逻辑审计 → 校验策略 |
| `references/` | 规格、设计、Schema、**示例**、**新报告模版**、**本文流程图** |
| `scripts/` | `validate_cards.py`、`generate_social_cards.py`（确定性渲染与校验） |
| `evals/` | 可选回归提示 `evals.json` |
| `output/` | 默认 PNG 输出目录（`.gitignore`；可用 `--output-root` 改） |

---

## 1. 端到端总览（唯一出图路径）

**硬性规则：** `--slots` 必填；`load_card_slots` → `assert_card_slots_complete`；无「不写 slots 纯启发式出图」路径。

```mermaid
flowchart TB
    subgraph INPUT["输入"]
        HTML["研报 HTML\n*_Research_CN.html"]
        JSON["同目录 JSON\nfinancial_*.json, porter_*.json …"]
        TPL["可选：references/templates/\ncard_slots.template.json\n复制为 stem.card_slots.json"]
    end

    subgraph EXTRACT["理解与起草"]
        C["Content Agent\n依据 HTML/JSON 写满\nstem.card_slots.json"]
    end

    subgraph REFINE["约束与审计"]
        L["Layout Agent\n按 design-spec 压缩换行、\n控制字数与口语标记"]
        H["Hardcode / logic audit\n（政策见 agents/）\n槽位文案与事实一致"]
    end

    subgraph GATE["Python 门槛"]
        A["load_card_slots\nassert_card_slots_complete"]
        V["validate_cards.py\nvalidate_report：\n语义 + 排版像素近似"]
    end

    subgraph RENDER["渲染"]
        G["generate_social_cards.py\nHTML + slots → 6×PNG"]
    end

    subgraph OUT["输出"]
        PNG["output/&lt;stem&gt;/\n01–06.png\n+ card_slots.json 副本\n（主副本仍在报告目录）"]
    end

    TPL -.->|新报告可复制| C
    HTML --> C
    JSON --> C
    C --> L
    L --> H
    H --> A
    A -->|缺字段| ERR["退出：补全 JSON"]
    A -->|通过| V
    V -->|失败| L
    V -->|通过| G
    G --> PNG
```

---

## 2. 新报告如何得到 `card_slots.json`

```mermaid
flowchart LR
    A["复制\ntemplates/card_slots.template.json"] --> B["改名为\n&lt;stem&gt;.card_slots.json"]
    B --> C["放在 HTML 同目录"]
    C --> D["按报告替换全部槽位\n或对照 examples/"]
    D --> E["Layout Agent 迭代"]
    E --> F["validate_cards.py"]
```

---

## 3. `--slots` 路径解析（CLI）

```mermaid
flowchart TD
    START(["执行 validate / generate"]) --> MULTI{"--input 下\n多个 *.html？"}
    MULTI -->|否| ONE["--slots 可为：\n• 单个 JSON 文件路径\n• 或目录（读 stem.card_slots.json）"]
    MULTI -->|是| DIR["--slots 必须是目录\n且含与各 stem 对应的\n*.card_slots.json"]
    ONE --> LOAD["resolve_slots_path → load_card_slots"]
    DIR --> LOAD
    LOAD --> ASSERT["assert_card_slots_complete"]
```

---

## 4. 校验分层（为何稳定）

```mermaid
flowchart TB
    L1["① 结构：JSON 键齐全、列表条数达标\nassert_card_slots_complete"]
    L2["② 语义：硬编码/逻辑审计、人话标记、\n与 HTML 事实锚点\nvalidate_report 内"]
    L3["③ 排版：行数/字符预算、\nCard2 动态 y、Card4 判断框等\n像素级近似\n（与 generate_social_cards 一致）"]
    L1 --> L2 --> L3
    L3 --> OK["通过后可 generate"]
```

---

## 5. 与 workflow-spec 九步对应

```mermaid
flowchart LR
    S1["1 ingest"] --> S2["2 extract"]
    S2 --> S3["3 normalize"]
    S3 --> S4["4 plan slots"]
    S4 --> S5["5 write JSON\nContent + Layout"]
    S5 --> S6["6 audit"]
    S6 --> S7["7 validate\n--slots"]
    S7 --> S8{"8 通过？"}
    S8 -->|否| S5
    S8 -->|是| S9["9 export\n--slots"]
```

详述与必填槽位列表见 [workflow-spec.md §10](./workflow-spec.md)。
