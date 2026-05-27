"""Regression tests for validate_card1_4_analytical_content().

Contract (locked):
    validate_card1_4_analytical_content(
        card_slots: dict, worker_notes: dict | None
    ) -> list[str]

- Returns [] on pass; non-empty list of human-readable issue strings on fail.
- Checks Card 1-4 worker_notes for required hidden fields
  (data_anchor, variant_view, falsifier|primary_quote|catalyst_with_date).
- Authority slot (company_calculation, nested under cfa_lens)
  additionally requires primary_quote — the formula application must be
  backed by a citation of the actual financial source (10-K / earnings / IR).
- Nested worker_notes keys 'five_year_arc.narrative' and
  'cfa_lens.company_calculation' may be addressed either by the full
  dotted key or by the leaf name (e.g. 'narrative' / 'company_calculation').
"""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

# Ensure project root on sys.path so we can import scripts.generate_social_cards
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from scripts.generate_social_cards import (  # noqa: E402
    CardSlotOverrides,
    assert_card_slots_complete,
    validate_card1_4_analytical_content,
)


# ---------------------------------------------------------------------------
# Positive fixtures — clean, realistic, must pass.
# ---------------------------------------------------------------------------

POSITIVE_WORKER: dict = {
    "schema_version": 3,
    "intro_sentence": {
        "data_anchor": "datacenter revenue $30.8B Q3 vs peer AMD $3.5B",
        "variant_view": "Street under-models H200 mix shift through Q2 of next fiscal year",
        "falsifier": "Q+1 datacenter sequential <+5% with mix held constant",
        "primary_quote": {
            "speaker": "CFO Colette Kress",
            "venue": "FQ3-26 call",
            "quote": "mix favors H200 through FY26",
            "url_or_filing": "https://investor.nvidia.com/financial-info/financial-reports/",
        },
    },
    "company_focus_paragraph": {
        "data_anchor": "non-GAAP gross margin 75% vs peer median 56%",
        "variant_view": "consensus assumes margin compression on Blackwell ramp but pricing power holds",
        "catalyst_with_date": {
            "event": "Blackwell volume ramp",
            "date_window": "2026-Q2",
            "implication": "incremental gross profit lifts FY27 EPS by ~8%",
        },
    },
    "industry_paragraph": {
        "data_anchor": "TPU v5 vs H100 perf-per-dollar gap 1.4x (vs 1.1x prior gen)",
        "variant_view": "GCP TPU advantage narrower than Street currently prices into NVDA multiple",
        "falsifier": "TPU v6 ships >40% of GCP AI capacity by mid-FY26 production",
    },
    # Nested: writer may use 'five_year_arc.narrative' or 'narrative'.
    "five_year_arc.narrative": {
        "data_anchor": "datacenter revenue mix went from 27% (FY2020) to 87% (FY2026) vs peer AMD 22%->39%",
        "variant_view": "the 5-year arc is three distinct phases, not one — each phase has its own multiple",
        "falsifier": "FY26 datacenter revenue growth dropping below +30% YoY within next two quarters",
    },
    "revenue_explainer_points": {
        "data_anchor": "datacenter 87% of revenue vs peer median 65%",
        "variant_view": "mix shift to inference not yet in FY27 consensus revenue estimates",
        "falsifier": "datacenter mix drops below 80% for two consecutive quarters",
    },
    # AUTHORITY slot — requires primary_quote.
    "cfa_lens.company_calculation": {
        "data_anchor": "FY26 Q3 datacenter revenue +112% YoY vs total revenue +94% YoY (DOL ≈ 1.19) vs peer AMD DOL ~0.8",
        "variant_view": "Street is modeling DOL closer to 1.0; the 1.19 reading implies operating leverage will keep amplifying FY27 datacenter mix shift",
        "primary_quote": {
            "speaker": "CFO Colette Kress",
            "venue": "FY26 Q3 earnings call, 2025-11-19",
            "quote": "operating margin expansion tracking the platform mix shift",
            "url_or_filing": "https://investor.nvidia.com/q3-fy26-call",
        },
        "falsifier": "DOL compresses below 1.0 for two consecutive quarters as Blackwell ramp dilutes margins",
    },
}

POSITIVE_CARDS: dict = {
    "schema_version": 3,
    "intro_sentence": (
        "Datacenter revenue $30.8B Q3 — vs peer AMD $3.5B and $13.5B Q3 last year — "
        "driven by H200 mix entering production."
    ),
    "company_focus_paragraph": (
        "Non-GAAP gross margin held 75% (peer median 56%) while datacenter share "
        "moved to 87% of revenue."
    ),
    "metrics_row": ["FY26 Q3|$35.1B", "Datacenter|$30.8B", "GM|74.6%"],
    "industry_paragraph": (
        "AI compute is at the 'system > silicon' transition; CoWoS and HBM are "
        "the structural bottlenecks for 2026 throughput."
    ),
    "background_bullets": [
        "Supplier: TSMC CoWoS capacity rises sharply through 2026.",
        "Buyer: top 4 hyperscalers cluster around half of revenue.",
        "Rivalry: AMD full-year datacenter trails one NVDA quarter.",
        "Moat: CUDA + NVLink + InfiniBand stack lock.",
    ],
    "porter_evidence": [
        {"force": "rivalry",         "score": 2, "evidence": "Training share dominates; AMD full year only one tenth of NVDA quarterly."},
        {"force": "new_entrants",    "score": 3, "evidence": "TPU and Trainium are captive; ASIC ramp limited to self-use."},
        {"force": "supplier_power",  "score": 4, "evidence": "TSMC CoWoS allocation skewed to NVDA gives TSMC pricing leverage."},
        {"force": "buyer_power",     "score": 3, "evidence": "Top hyperscaler concentration is high; CUDA lock raises switching cost."},
        {"force": "substitutes",     "score": 2, "evidence": "Inference ASIC sub-25% share through 2026 according to peer guidance."},
    ],
    "five_year_arc": {
        "narrative": (
            "Over the past five years NVDA shifted from gaming-led to datacenter-led: "
            "datacenter share moved from low double digits in 2020 to high eighties in 2026, "
            "with gross margin climbing from low sixties to mid seventies. Operating margin "
            "tripled in the same window."
        ),
        "inflection_points": [
            "2020: A100 launch unlocks training capex.",
            "2022: ChatGPT moment shifts datacenter materially higher.",
            "2024: NVL72 system pricing multiplies order value sharply.",
        ],
    },
    "recent_financial_highlights": [
        "FY26 Q3 revenue near the upper end of guide.",
        "Datacenter posted another sequential record.",
        "Gross margin held firmly in the mid-seventies.",
        "Operating cash flow comfortably double-digit billions.",
    ],
    "revenue_explainer_points": [
        "Datacenter outpaces AMD and Intel by an order of magnitude.",
        "Gaming grew modestly but remains second-tier.",
        "Operating margin gap to peers reflects scale plus mix.",
    ],
    "cfa_lens": {
        "concept_key": "operating_leverage",
        "concept_name_cn": "经营杠杆",
        "concept_intro": (
            "DOL measures how a percentage change in revenue amplifies into "
            "operating profit when the fixed-cost base is large."
        ),
        "formula": "DOL = %ΔEBIT / %ΔRevenue",
        "company_calculation": [
            "FY26 Q3 营收同比+94%，营业利润同比+112%",
            "DOL ≈ 112 / 94 = 1.19",
        ],
        "company_application": [
            "Datacenter mix at 87% means fixed datacenter R&D amortizes across a wider revenue base.",
            "Each ten point increase in datacenter mix adds roughly 2pp to operating margin at constant cost base.",
            "Total option premium roughly a quarter of enterprise value versus peer median in single digits.",
        ],
        "different_angle_insight": (
            "Holding DOL at 1.19 implies FY27 operating margin reaches 64% under base-case "
            "revenue growth — meaningfully above the Street's 60% consensus."
        ),
        "cfa_progress_source": "default",
    },
}


def _fresh_fixture() -> tuple[dict, dict]:
    """Deep-copy the positive fixture so individual tests can mutate freely."""
    return copy.deepcopy(POSITIVE_CARDS), copy.deepcopy(POSITIVE_WORKER)


# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------


class PositiveFixtureTest(unittest.TestCase):
    """Sanity gate: the clean fixture must produce zero issues."""

    def test_positive_fixture_passes(self) -> None:
        cards, worker = _fresh_fixture()
        issues = validate_card1_4_analytical_content(cards, worker)
        self.assertEqual(
            issues,
            [],
            msg=f"Positive fixture should produce zero issues; got: {issues}",
        )

    def test_nested_worker_keys_addressable_by_leaf_name(self) -> None:
        """Writer may use 'narrative' instead of 'five_year_arc.narrative' in
        the worker_notes JSON. Both must resolve to the same slot."""
        cards, worker = _fresh_fixture()
        worker["narrative"] = worker.pop("five_year_arc.narrative")
        worker["company_calculation"] = worker.pop("cfa_lens.company_calculation")
        issues = validate_card1_4_analytical_content(cards, worker)
        self.assertEqual(
            issues, [], msg=f"Leaf-name addressing should pass; got: {issues}"
        )


class NegativeFixtureTests(unittest.TestCase):
    """Each test mutates one thing on the positive fixture and asserts that
    the validator surfaces an issue mentioning the offending slot/concept."""

    def _assert_any(self, issues: list[str], *needles: str) -> None:
        self.assertTrue(issues, msg="Expected at least one issue, got empty list.")
        joined = "\n".join(issues).lower()
        for needle in needles:
            self.assertIn(
                needle.lower(),
                joined,
                msg=f"Expected an issue mentioning {needle!r}; got issues:\n{issues}",
            )

    def test_missing_worker_notes_entirely(self) -> None:
        cards, _ = _fresh_fixture()
        issues = validate_card1_4_analytical_content(cards, None)
        self._assert_any(issues, "missing card_slots_worker_notes.json")

    def test_data_anchor_missing_number(self) -> None:
        cards, worker = _fresh_fixture()
        worker["intro_sentence"]["data_anchor"] = (
            "datacenter revenue strong vs peer AMD"
        )
        issues = validate_card1_4_analytical_content(cards, worker)
        self._assert_any(issues, "data_anchor", "number")

    def test_data_anchor_missing_comp_keyword(self) -> None:
        cards, worker = _fresh_fixture()
        worker["intro_sentence"]["data_anchor"] = "datacenter revenue $30.8B Q3"
        issues = validate_card1_4_analytical_content(cards, worker)
        self._assert_any(issues, "comp anchor")

    def test_variant_view_too_short(self) -> None:
        cards, worker = _fresh_fixture()
        worker["intro_sentence"]["variant_view"] = "wait and see"
        issues = validate_card1_4_analytical_content(cards, worker)
        self._assert_any(issues, "variant_view", "too short")

    def test_no_falsifier_quote_or_catalyst(self) -> None:
        cards, worker = _fresh_fixture()
        for key in ("falsifier", "primary_quote", "catalyst_with_date"):
            worker["intro_sentence"].pop(key, None)
        issues = validate_card1_4_analytical_content(cards, worker)
        self._assert_any(
            issues, "falsifier", "primary_quote", "catalyst_with_date"
        )

    def test_authority_slot_missing_primary_quote(self) -> None:
        cards, worker = _fresh_fixture()
        worker["cfa_lens.company_calculation"].pop("primary_quote", None)
        worker["cfa_lens.company_calculation"]["falsifier"] = (
            "DOL drops below 1.0 for two consecutive quarters as Blackwell ramp dilutes margins"
        )
        issues = validate_card1_4_analytical_content(cards, worker)
        self._assert_any(issues, "primary_quote", "authority")

    def test_backstop_shuobaile_in_intro(self) -> None:
        cards, worker = _fresh_fixture()
        cards["intro_sentence"] = "说白了，NVDA 卖的是 AI 算力。"
        issues = validate_card1_4_analytical_content(cards, worker)
        self._assert_any(issues, "说白了")

    def test_backstop_binary_flip_in_cfa_insight(self) -> None:
        cards, worker = _fresh_fixture()
        cards["cfa_lens"]["different_angle_insight"] = (
            "它不是芯片公司，而是 AI 算力总承包商。"
        )
        issues = validate_card1_4_analytical_content(cards, worker)
        self._assert_any(issues, "不是", "而是")

    def test_porter_evidence_banned_phrase_flagged(self) -> None:
        cards, worker = _fresh_fixture()
        cards["porter_evidence"][0]["evidence"] = "总而言之，竞争一般。"
        issues = validate_card1_4_analytical_content(cards, worker)
        self._assert_any(issues, "porter_evidence.evidence", "总而言之")

    def test_five_year_narrative_banned_phrase_flagged(self) -> None:
        cards, worker = _fresh_fixture()
        cards["five_year_arc"]["narrative"] = (
            "综上，这家公司过去 5 年增长很好。"
        )
        issues = validate_card1_4_analytical_content(cards, worker)
        self._assert_any(issues, "five_year_arc.narrative", "综上")


# ---------------------------------------------------------------------------
# Bad-lines regression fixture (CFA-lens flavored — successor to WDC fixture)
# ---------------------------------------------------------------------------


_REGRESSION_VALID_WORKER: dict = copy.deepcopy(POSITIVE_WORKER)


REGRESSION_BAD_CARDS: dict = {
    "schema_version": 3,
    "intro_sentence": (
        "西部数据现在最值钱的，不是硬盘这个老词，而是AI数据长期存储的供给瓶颈。"
    ),
    "company_focus_paragraph": (
        "Nearline HDD 容量出货同比增加 18%，云客户占比 56%。"
    ),
    "metrics_row": ["FY24 营收|$13B", "云客户占比|56%", "毛利率|31%"],
    "industry_paragraph": (
        "HDD 容量需求仍由超大规模云客户主导，行业不是没竞争，而是短期供需太紧。"
    ),
    "background_bullets": [
        "供应商:HDD 磁头供应集中度高。",
        "买方:云厂商占比 56% 议价权强。",
        "竞争:Seagate / Toshiba 三家分天下。",
        "护城河:Nearline 容量代际差。",
    ],
    "porter_evidence": [
        {"force": "rivalry",         "score": 3, "evidence": "总而言之，竞争一般，护城河可控。"},
        {"force": "new_entrants",    "score": 2, "evidence": "壁垒高，过去十年无新进入者。"},
        {"force": "supplier_power",  "score": 3, "evidence": "供给紧张，但合同期相对稳定。"},
        {"force": "buyer_power",     "score": 3, "evidence": "买方议价中等，云厂商占比有限。"},
        {"force": "substitutes",     "score": 2, "evidence": "NAND 替代有限，单位成本仍是 HDD 优势。"},
    ],
    "five_year_arc": {
        "narrative": "说白了，过去 5 年公司从消费 HDD 转向云客户为主，但商业模型本质没变。",
        "inflection_points": [
            "2020: Nearline 容量首破 16TB。",
            "2022: 消费 HDD 业务从 30% 萎缩到 12%。",
            "2024: 云客户占比突破一半。",
        ],
    },
    "recent_financial_highlights": [
        "FY24 营收 $13B 同比转正。",
        "毛利率 31% 比上年提升 8 个百分点。",
        "Nearline 容量出货创历史新高。",
    ],
    "revenue_explainer_points": [
        "Nearline 占总营收逾五成是真正的增长引擎。",
        "消费 HDD 持续萎缩但仍有现金贡献。",
        "Flash 业务通过 Kioxia 合资保留 optionality。",
    ],
    "cfa_lens": {
        "concept_key": "rim",
        "concept_name_cn": "剩余收益模型",
        "concept_intro": "剩余收益模型把企业价值拆成账面净资产 + 未来超额收益的现值。",
        "formula": "RI = (ROE − k) × B",
        "company_calculation": [
            "WDC 账面净资产 $5B，ROE 估算 18%，k 估算 10%",
            "RI = (18% − 10%) × $5B = $0.4B / 年",
        ],
        "company_application": [
            "WDC 账面净资产估算 $5B，ROE 估算 18%。",
            "WACC 估算 10%，超额收益率约 8pp。",
            "10 年超额收益现值约 $4B，加账面得 $9B 公允区间。",
        ],
        "different_angle_insight": (
            "说白了，它现在像 AI 基础设施；供给一松，又会被当周期股。"
        ),
        "cfa_progress_source": "default",
    },
}


class BadLinesRegressionTest(unittest.TestCase):
    def test_bad_lines_surface_expected_issues(self) -> None:
        issues = validate_card1_4_analytical_content(
            REGRESSION_BAD_CARDS, copy.deepcopy(_REGRESSION_VALID_WORKER)
        )
        self.assertTrue(
            issues, msg="Regression fixture should not validate clean."
        )
        joined_lc = "\n".join(issues).lower()

        # intro_sentence: binary flip 不是 X 而是 Y
        self.assertIn("intro_sentence", joined_lc)
        # industry_paragraph: same binary flip pattern
        self.assertIn("industry_paragraph", joined_lc)
        # five_year_arc.narrative: 说白了 backstop
        self.assertIn("five_year_arc.narrative", joined_lc)
        # cfa_lens.different_angle_insight: 说白了 backstop
        self.assertIn("cfa_lens.different_angle_insight", joined_lc)
        # porter_evidence: 总而言之 backstop
        self.assertIn("porter_evidence.evidence", joined_lc)

        distinct = {iss.strip() for iss in issues if iss.strip()}
        self.assertGreaterEqual(
            len(distinct),
            5,
            msg=(
                "Expected >=5 distinct issue messages across the bad-line "
                f"slots; got {len(distinct)}:\n{issues}"
            ),
        )


# ---------------------------------------------------------------------------
# Writing-style backstop (symbols, comparators, CN/EN mixing)
# Single source: Equity Research Skill/references/report_style_guide_cn.md
# ---------------------------------------------------------------------------


class TestWritingStyleBackstop(unittest.TestCase):
    def setUp(self) -> None:
        self.cards, self.notes = _fresh_fixture()

    def test_bare_plus_on_absolute_amount_flagged(self) -> None:
        self.cards["intro_sentence"] = "Salesforce 战略投资公允价值净收益+10.17亿美元，扭转去年亏损。"
        issues = validate_card1_4_analytical_content(self.cards, self.notes)
        self.assertTrue(
            any("bare '+'" in i and "intro_sentence" in i for i in issues),
            f"expected bare-+ flag on intro_sentence, got {issues}",
        )

    def test_plus_pct_without_comparator_flagged(self) -> None:
        self.cards["intro_sentence"] = "Q1收入6.398亿美元+34%，订单能见度尚稳。"
        issues = validate_card1_4_analytical_content(self.cards, self.notes)
        self.assertTrue(
            any("bare '+'" in i for i in issues),
            f"expected bare-+ flag on '+34%', got {issues}",
        )

    def test_plus_after_tongbi_passes(self) -> None:
        self.cards["intro_sentence"] = "Q1 收入 6.4 亿美元，同比+34%，订单能见度尚稳。"
        issues = validate_card1_4_analytical_content(self.cards, self.notes)
        self.assertFalse(
            any("bare '+'" in i for i in issues),
            f"comparator-prefixed + should be allowed, got {issues}",
        )

    def test_plus_after_huanbi_passes(self) -> None:
        self.cards["intro_sentence"] = "营业利润率环比+1.05个百分点。"
        issues = validate_card1_4_analytical_content(self.cards, self.notes)
        self.assertFalse(
            any("bare '+'" in i for i in issues),
            f"comparator-prefixed + should be allowed, got {issues}",
        )

    def test_CC_abbrev_flagged(self) -> None:
        self.cards["company_focus_paragraph"] = "cRPO 同比按 CC 增长 13%，弱于按报告值口径。"
        issues = validate_card1_4_analytical_content(self.cards, self.notes)
        self.assertTrue(
            any("'CC'" in i and "company_focus_paragraph" in i for i in issues),
            f"expected CC abbrev flag, got {issues}",
        )

    def test_YoY_abbrev_flagged(self) -> None:
        self.cards["industry_paragraph"] = "cRPO 351 亿美元同比按报告值 YoY 增长16%。"
        issues = validate_card1_4_analytical_content(self.cards, self.notes)
        self.assertTrue(
            any("'YoY'" in i for i in issues),
            f"expected YoY abbrev flag, got {issues}",
        )

    def test_first_mention_parens_whitelists_CC(self) -> None:
        """`恒定汇率（CC）` once in any Card 1-4 slot → later bare CC OK."""
        self.cards["intro_sentence"] = "恒定汇率（CC）口径下有机收入约 9%。"
        self.cards["company_focus_paragraph"] = "cRPO 同比按 CC 增长 13%。"
        issues = validate_card1_4_analytical_content(self.cards, self.notes)
        self.assertFalse(
            any("'CC'" in i for i in issues),
            f"first-mention 恒定汇率（CC） should whitelist later CC uses, got {issues}",
        )


_FULL_CARDS_BASE: dict = {
    "schema_version": 3,
    "logo_asset_path": "assets/logos/nvda.png",
    "cover_company_name_cn": "英伟达",
    "intro_sentence": (
        "FY26 Q3 datacenter revenue $30.8B vs peer AMD $3.5B (8.8x); "
        "total revenue $35.1B 同比+94%, vs FY25 Q3 $18.1B."
    ),
    "company_focus_paragraph": (
        "FY26 Q3 总营收 $35.1B、同比+94%，数据中心 $30.8B 占 87.7%。"
        "GAAP 毛利率 74.6%，营业利润率 62%；经营现金流 $17.6B。"
        "投资主线：Blackwell 出货节奏 vs 客户消化期，NVL72 配件供应能否及时到位。"
    ),
    "metrics_row": [
        "FY26 Q3 总营收|$35.1B",
        "数据中心|$30.8B",
        "GAAP 毛利率|74.6%",
    ],
    "industry_paragraph": (
        "AI 算力当前处于「系统集成 > 单芯片」阶段：客户单元从 H100 单卡升级为 NVL72 整柜。"
    ),
    "background_bullets": [
        "供应商：台积电 CoWoS 月产能 2026 升至 70k 片，NVDA 占 60%。",
        "买方：前四大云厂占 46%，CUDA 锁定提高切换成本。",
        "竞争强度：AMD MI300X 全年 $5B 指引 vs NVDA 数据中心单季 $30.8B。",
        "护城河：CUDA + NVLink + InfiniBand 三层栈。",
    ],
    "porter_evidence": [
        {"force": "rivalry",         "score": 2, "evidence": "训练市场 NVDA 份额>90%，AMD MI300X 全年仅 $5B。"},
        {"force": "new_entrants",    "score": 3, "evidence": "Google TPU / AWS Trainium 都是自用。"},
        {"force": "supplier_power",  "score": 4, "evidence": "TSMC CoWoS 月产 70k 中 NVDA 占 60%。"},
        {"force": "buyer_power",     "score": 3, "evidence": "前四大云厂占 46%，CUDA 锁定提高切换成本。"},
        {"force": "substitutes",     "score": 2, "evidence": "推理 ASIC 2026 替代率<25%。"},
    ],
    "five_year_arc": {
        "narrative": (
            "过去 5 年从游戏卡公司转向 AI 算力承包商：数据中心占比从 27% 到 87%，"
            "毛利率从 62% 到 74.6%。"
        ),
        "inflection_points": [
            "2020: A100 发布，云厂训练芯片第一次集中采购。",
            "2022: ChatGPT 出圈，FY23 数据中心收入翻倍。",
            "2024: Blackwell NVL72 出货，单笔订单价值放大 100 倍。",
        ],
    },
    "recent_financial_highlights": [
        "FY26 Q3 营收 $35.1B，同比+94%（vs 指引 $32.5B 上修 8%）。",
        "数据中心 $30.8B 占 87.7%，GAAP 毛利率 74.6%。",
        "运营利润率 62.0% vs AMD 11%、Intel-3%。",
    ],
    "revenue_explainer_points": [
        "数据中心 $30.8B vs AMD $3.5B、Intel $3.3B，占总营收 87.7%。",
        "游戏 $3.3B 同比+15%，汽车 $0.45B 同比+72%，合计 12%。",
        "运营利润率 62% vs AMD 11%、Intel-3%，规模效应在 OPEX 端兑现。",
    ],
}


def _full_positive_overrides() -> CardSlotOverrides:
    raw = copy.deepcopy(_FULL_CARDS_BASE)
    raw["cfa_lens"] = copy.deepcopy(POSITIVE_CARDS["cfa_lens"])
    return CardSlotOverrides.from_json_dict(raw)


class Card4SchemaTests(unittest.TestCase):
    """Schema v3: formula required + must have operators, company_calculation
    required + must have digits, takeaway removed."""

    def test_card4_formula_required_in_validator(self) -> None:
        slots = _full_positive_overrides()
        slots.cfa_lens = dict(slots.cfa_lens or {})
        slots.cfa_lens["formula"] = ""
        with self.assertRaises(ValueError) as ctx:
            assert_card_slots_complete(slots)
        self.assertIn("formula", str(ctx.exception))

    def test_card4_formula_must_have_operators(self) -> None:
        slots = _full_positive_overrides()
        slots.cfa_lens = dict(slots.cfa_lens or {})
        slots.cfa_lens["formula"] = "公式: 经营杠杆"
        with self.assertRaises(ValueError) as ctx:
            assert_card_slots_complete(slots)
        self.assertIn("formula", str(ctx.exception))
        self.assertIn("operator", str(ctx.exception).lower())

    def test_card4_formula_passes_with_equals_and_operator(self) -> None:
        slots = _full_positive_overrides()
        slots.cfa_lens = dict(slots.cfa_lens or {})
        slots.cfa_lens["formula"] = "DOL = %ΔEBIT / %ΔRevenue"
        try:
            assert_card_slots_complete(slots)
        except ValueError as exc:
            self.fail(f"Formula with '=' and operator should pass; got {exc}")

    def test_card4_company_calculation_must_have_digits(self) -> None:
        slots = _full_positive_overrides()
        slots.cfa_lens = dict(slots.cfa_lens or {})
        slots.cfa_lens["company_calculation"] = [
            "DOL = %ΔEBIT 比上 %ΔRevenue",
            "营业利润同比扩张超过收入同比",
        ]
        with self.assertRaises(ValueError) as ctx:
            assert_card_slots_complete(slots)
        self.assertIn("company_calculation", str(ctx.exception))
        self.assertIn("digit", str(ctx.exception).lower())

    def test_card4_company_calculation_required(self) -> None:
        slots = _full_positive_overrides()
        slots.cfa_lens = dict(slots.cfa_lens or {})
        slots.cfa_lens["company_calculation"] = []
        with self.assertRaises(ValueError) as ctx:
            assert_card_slots_complete(slots)
        self.assertIn("company_calculation", str(ctx.exception))

    def test_card4_takeaway_removed_from_schema(self) -> None:
        """The takeaway slot is gone in v3 — it must not appear in the
        dataclass-derived lens dict and assert_card_slots_complete must not
        require it."""
        slots = _full_positive_overrides()
        lens = slots.cfa_lens or {}
        self.assertNotIn("takeaway", lens)
        try:
            assert_card_slots_complete(slots)
        except ValueError as exc:
            self.fail(f"Positive v3 fixture should validate clean; got {exc}")

    def test_schema_version_is_three(self) -> None:
        slots = _full_positive_overrides()
        self.assertEqual(slots.schema_version, 3)


if __name__ == "__main__":
    unittest.main()
