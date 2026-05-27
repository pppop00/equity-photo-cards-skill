"""Regression tests for validate_card1_4_analytical_content().

Contract (locked):
    validate_card1_4_analytical_content(
        card_slots: dict, worker_notes: dict | None
    ) -> list[str]

- Returns [] on pass; non-empty list of human-readable issue strings on fail.
- Checks Card 1-4 worker_notes for required hidden fields
  (data_anchor, variant_view, falsifier|primary_quote|catalyst_with_date).
- Authority slot (different_angle_insight, nested under cfa_lens)
  additionally requires primary_quote.
- Nested worker_notes keys 'five_year_arc.narrative' and
  'cfa_lens.different_angle_insight' may be addressed either by the full
  dotted key or by the leaf name (e.g. 'narrative' / 'different_angle_insight').
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
    validate_card1_4_analytical_content,
)


# ---------------------------------------------------------------------------
# Positive fixtures — clean, realistic, must pass.
# ---------------------------------------------------------------------------

POSITIVE_WORKER: dict = {
    "schema_version": 2,
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
    "cfa_lens.different_angle_insight": {
        "data_anchor": "real-options decomposition implies FY26E ebit margin 60% vs management guide midpoint 58%",
        "variant_view": "guide under-models pricing power into FY26 H2 on Blackwell scarcity",
        "primary_quote": {
            "speaker": "CFO",
            "venue": "Q4 earnings call",
            "quote": "price discipline holding through CY26",
            "url_or_filing": "https://investor.nvidia.com/q4-call",
        },
        "falsifier": "price compression visible in any hyperscaler renegotiation",
    },
}

POSITIVE_CARDS: dict = {
    "schema_version": 2,
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
        "concept_key": "real_options",
        "concept_name_cn": "实物期权",
        "concept_intro": (
            "Real options frame strategic flexibility (expand / delay / abandon) as "
            "option-like value layered on top of base-case NPV."
        ),
        "company_application": [
            "NVDA is three nested options: CUDA training (exercised), inference expansion (pending), automotive (far OTM).",
            "Training option NPV is the largest piece; inference carries the bulk of remaining time value.",
            "Total option premium roughly a quarter of enterprise value versus peer median in single digits.",
        ],
        "different_angle_insight": (
            "Using real-options decomposition, the market cap implies a meaningful slice of "
            "time value from unexercised options that DCF alone would price too low."
        ),
        "takeaway": "Optionality premium is the floor, not the bubble.",
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
        worker["different_angle_insight"] = worker.pop("cfa_lens.different_angle_insight")
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
        worker["cfa_lens.different_angle_insight"].pop("primary_quote", None)
        worker["cfa_lens.different_angle_insight"]["falsifier"] = (
            "Real-options premium collapses if FY27 inference share drops below seventy percent"
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
    "schema_version": 2,
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
        "company_application": [
            "WDC 账面净资产估算 $5B，ROE 估算 18%。",
            "WACC 估算 10%，超额收益率约 8pp。",
            "10 年超额收益现值约 $4B，加账面得 $9B 公允区间。",
        ],
        "different_angle_insight": (
            "说白了，它现在像 AI 基础设施；供给一松，又会被当周期股。"
        ),
        "takeaway": "记住这一条：超额 ROE 是估值锚。",
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


if __name__ == "__main__":
    unittest.main()
