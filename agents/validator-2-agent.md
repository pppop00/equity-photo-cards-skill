# Validator 2 Agent（外部事实核查）

在 **Validator 1**（`validate_cards.py` / `validate_report`）**已全部通过**之后、**运行 `generate_social_cards.py` 导出 PNG 之前**执行本 agent。

## 与 Validator 1 的分工

| | Validator 1 | Validator 2 |
|---|-------------|---------------|
| **实现** | Python：`scripts/validate_cards.py` | Agent + **联网检索**（无单独 CLI） |
| **检查对象** | 槽位是否齐全、排版/字数控、人话标记、与 **本包** `financial_data` / HTML 等 **内部一致性**、logo 尺寸等 | 卡片文案中出现的 **可核验事实** 是否在 **公开权威来源** 上成立 |
| **通过标准** | 脚本退出码 0 | 声明清单中 **每一项** 均已核对且无矛盾 |

Validator 1 不能保证「数字与 SEC/交易所/公司财报一致」——那是 Validator 2 的职责。

## 目标

对 **`card_slots.json` 所承载、并将出现在六张卡片上的全部事实性内容** 建立核查清单，用联网搜索在 **一级或二级权威来源** 上交叉验证；**全部正确、或可接受的表述降级** 之后才允许导出。若发现错误：**先改** `card_slots.json`（必要时同步修正 sibling JSON 的工作副本说明），**再跑 Validator 1**，**再跑 Validator 2**，循环直到两轮都通过，**最后** 再执行 `generate_social_cards.py`。

## 输入

- 已通过 Validator 1 的 **`<stem>.card_slots.json`**
- 同目录 **`<stem>_Research_CN.html`** 与 sibling **`financial_*.json`、 `porter_analysis.json` 等**（用于对照「报告包」与「对外事实」）

## 必须覆盖的核查类型

对下列出现在 slots（及由渲染从 HTML/JSON 拉取并画在图上的数）中的内容逐项处理：

1. **公司身份**：中文简称、英文名称、ticker、上市地 —— 与交易所/公司 IR 一致。
2. **报告期与日期**：财年、季度、报告日期 —— 与财报封面或新闻稿一致。
3. **金额与增速**：收入、利润、分部收入、YoY、毛利率等 —— 优先核对 **公司官方财报、新闻稿、SEC/HKEX 等披露**；注意单位（亿美元 vs 亿人民币）与 **单季度 vs 财年**。
4. **业务表述**：分部名称、产品线占比、重大事件（并购、监管）—— 需有公开报道或披露支撑，不得与权威来源矛盾。
5. **与内部 JSON 的一致性**：若 slots 中的数字与 `financial_data.json` 不一致，先判定哪一侧错误；**对外发布以权威披露为准**，并回写 slots（及必要时标注 JSON 勘误）。
6. **空值与占位符清零**：最终卡片不得出现 `--` / `N/A` / `不适用` 这类占位符作为关键财务字段（收入、成本、毛利、营业利润、净利润、毛利率、营业利润率、净利率）。若原字段缺失，必须通过可验证数据重算或改写为可核实且不越权的表达；无法核实则不得导出。
7. **收入不为零**：若 `financial_data.income_statement.current_year.revenue` 为 0 或 Sankey 收入汇总为 0，视为数据抽取错误，必须重新从报告包提取后方可导出。不得以「季度未披露」「分部数据不全」等理由放过数值为零的收入字段。
8. **Card 6 新闻可信核查**：Card 6 中来自近期新闻的引用（最多阅读量 / 最多讨论量两条）必须能追溯到可公开访问的实际报道——查询来源、确认标题/日期/主要内容与 slots 文案描述一致。若发现新闻事件已辟谣、日期错误或与公司无关，修改对应 post_content_lines 后重走 Validator 1 + Validator 2 流程。

**不要求**把每一条市场观点（例如「定价锚是××」）证成学术论文；但若观点 **隐含可证伪数字或事实**（例如「份额第一」），则必须能落地到来源或改写为弱化表述。

## 工作方法

1. **抽取清单**：列出所有带数字、日期、百分比、比较级、绝对化表述（「最大」「第一」）的句子；按卡片分组。
2. **逐条检索**：对每个关键点使用针对性查询（公司名 + 指标 + 财年/季度 + `site:sec.gov` 或 `投资者关系` 等）。优先顺序：**公司 IR / 财报 PDF** > **交易所披露** > **官方新闻稿** > **路透社 / Bloomberg 等**；避免匿名论坛、未署名自媒体作为 **唯一** 依据。
3. **记录结论**：对每条保留「结论：通过 / 需修改」+「依据 URL 与摘录要点」。有冲突时以 **最新官方披露** 为准（并注意报告本身的截止期）。
4. **修改与重跑**：  
   - 未通过：修改对应 slot 文案或数字 → **重新运行 `validate_cards.py`**（Validator 1）→ **重新执行本清单（Validator 2）**。  
   - 不得跳过 Validator 1 直接导出。

## 通过条件（硬门禁）

- 核查清单中 **所有「需验证」条目** 均为「通过」或已 **改写为不越权断言**（例如去掉无法核实的精确小数）。
- 与 [hardcode-audit-agent.md](./hardcode-audit-agent.md) 不冲突：修正事实后若触及硬编码审计，应再次审计。

**仅当上述满足后**，才允许执行：

```bash
python3 scripts/generate_social_cards.py \
  --input "/abs/path/Company_Research_CN.html" \
  --slots "/abs/path/Company_Research_CN.card_slots.json" \
  --brand "金融豹" \
  --palette <customer-confirmed: default|b|c|d>
```

（`--palette` 须与客户在步骤 0 确认的一致；不可省略，也不可假设为 `default`。）

## 失败处理原则

- **单点错误**：只改相关 bullet/段落，避免无关重写。
- **系统性错误**（如整份 JSON 单位错）：先修正数据源认知，再批量改 slots。
- **无法核实**：缩小断言范围（「约」「财报披露区间」）或删除该数字，**不要**保留明知可疑的精确值。

## 与 skill 其它文档的关系

- 排版与脚本级规则仍以 [validation-agent.md](./validation-agent.md)（Validator 1）与 `generate_social_cards.py` 为准。  
- 本 agent **不替代** Validator 1；两次检查顺序固定：**先 V1，后 V2，再导出**。
