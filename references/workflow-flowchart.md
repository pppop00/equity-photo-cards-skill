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

    subgraph LOGO["Logo 生产（Stage A）"]
        LG["Logo Agent\n建 output folder → 存 logo_official.png\n→ 设 logo_asset_path"]
    end

    subgraph EXTRACT["内容起草（Stage B）"]
        C["Content Agent\n依据 HTML/JSON 写满\nstem.card_slots.json"]
    end

    subgraph AUDIT["硬编码审计（Stage B.5）"]
        H["Hardcode / logic audit\n槽位文案须有公司锚点\n且与 normalized facts 一致"]
    end

    subgraph REFINE["排版压缩（Stage C）"]
        L["Layout Agent\n按 design-spec 压缩换行\n控制字数与口语标记"]
    end

    subgraph GATE["Python 门槛（Stage D）"]
        A["load_card_slots\nassert_card_slots_complete"]
        V["validate_cards.py\nvalidate_report：\n语义 + 排版像素近似"]
    end

    subgraph V2["外部事实核查（Stage E）"]
        F2["Validator 2\n联网核对财报 / IR / SEC\n全部通过才允许导出"]
    end

    subgraph RENDER["渲染"]
        G["generate_social_cards.py\nHTML + slots + --palette → 6×PNG"]
    end

    subgraph OUT["输出"]
        PNG["output/&lt;stem&gt;/\n01–06.png + logo_official.png\n+ card_slots.json 副本"]
    end

    TPL -.->|新报告可复制| C
    HTML --> LG
    HTML --> C
    JSON --> C
    LG --> C
    C --> H
    H -->|有问题| C
    H -->|通过| L
    L --> A
    A -->|缺字段| ERR["退出：补全 JSON"]
    A -->|通过| V
    V -->|失败| L
    V -->|通过| F2
    F2 -->|有错| L
    F2 -->|通过| G
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
    L2["② 语义：硬编码/逻辑审计、人话标记、\n与包内 financial_data 等\nvalidate_report（Validator 1）"]
    L3["③ 排版：行数/字符预算、\nCard2 动态 y、Card4 判断框等\n像素级近似\n（与 generate_social_cards 一致）"]
    L4["④ 外部事实：Validator 2\n联网核对披露/财报与 card 数字"]
    L1 --> L2 --> L3 --> L4
    L4 --> OK["通过后可 generate"]
```

---

## 5. 与 workflow-spec 步骤对应（含配色确认与 Validator 2）

```mermaid
flowchart LR
    S0["0 配色确认\nclient: default|b|c"] --> SA["1 Logo 生产\n建 output folder\n存 logo_official.png"]
    SA --> S1["2 ingest"]
    S1 --> S2["3 extract"]
    S2 --> S3["4 normalize"]
    S3 --> S4["5 plan slots"]
    S4 --> S5["6 write JSON\nContent Agent (Stage B)"]
    S5 --> S6["7 Hardcode 审计\nStage B.5"]
    S6 -->|有问题| S5
    S6 -->|通过| S7["8 Layout Agent\nStage C"]
    S7 --> S8["9 Validator 1\nvalidate_cards --slots"]
    S8 -->|失败| S7
    S8 -->|通过| S9["10 Validator 2\n联网事实核查"]
    S9 -->|有错| S7
    S9 -->|通过| S10["11 export\n--slots --palette <confirmed>"]
```

详述与必填槽位列表见 [workflow-spec.md §10](./workflow-spec.md)。
