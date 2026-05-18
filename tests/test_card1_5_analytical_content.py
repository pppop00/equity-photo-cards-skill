"""Regression tests for validate_card1_5_analytical_content().

Contract (locked):
    validate_card1_5_analytical_content(
        card_slots: dict, worker_notes: dict | None
    ) -> list[str]

- Returns [] on pass; non-empty list of human-readable issue strings on fail.
- Checks Card 1-5 worker_notes for required hidden fields
  (data_anchor, variant_view, falsifier|primary_quote|catalyst_with_date)
  and card_slots for backstop banned phrases.
- Authority slots (brand_statement, judgement_paragraph) additionally require
  primary_quote.
- Card 6 slots (post_title, post_content_lines, etc.) are NOT checked.
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
    validate_card1_5_analytical_content,
)


# ---------------------------------------------------------------------------
# Positive fixtures — clean, realistic, must pass.
# ---------------------------------------------------------------------------

POSITIVE_WORKER: dict = {
    "schema_version": 1,
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
    "conclusion_block": {
        "data_anchor": "TPU v5 vs H100 perf-per-dollar gap 1.4x (vs 1.1x prior gen)",
        "variant_view": "GCP TPU advantage narrower than Street currently prices into NVDA multiple",
        "falsifier": "TPU v6 ships >40% of GCP AI capacity by mid-FY26 production",
    },
    "revenue_explainer_points": {
        "data_anchor": "datacenter 87% of revenue vs peer median 65%",
        "variant_view": "mix shift to inference not yet in FY27 consensus revenue estimates",
        "falsifier": "datacenter mix drops below 80% for two consecutive quarters",
    },
    "judgement_paragraph": {
        "data_anchor": "FY26E ebit margin 60% vs management guide midpoint 58%",
        "variant_view": "guide under-models pricing power into FY26 H2 on Blackwell scarcity",
        "primary_quote": {
            "speaker": "CFO",
            "venue": "Q4 earnings call",
            "quote": "price discipline holding through CY26",
            "url_or_filing": "https://investor.nvidia.com/q4-call",
        },
        "falsifier": "price compression visible in any hyperscaler renegotiation",
    },
    "brand_statement": {
        "data_anchor": "free cash flow yield 4% vs peer median 1.5%",
        "variant_view": "asymmetric upside on AI capex sustainability through CY27 capex cycle",
        "primary_quote": {
            "speaker": "CEO Jensen Huang at GTC 2025-03",
            "venue": "GTC keynote",
            "quote": "sovereign AI is multi-year tailwind",
            "url_or_filing": "https://nvidia.com/gtc2025",
        },
    },
}

POSITIVE_CARDS: dict = {
    "intro_sentence": (
        "Datacenter revenue $30.8B Q3 — vs peer AMD $3.5B and $13.5B Q3 last year — "
        "driven by H200 mix entering production."
    ),
    "company_focus_paragraph": (
        "Non-GAAP gross margin held 75% (peer median 56%) while datacenter share "
        "moved to 87% of revenue."
    ),
    "background_bullets": ["bullet 1", "bullet 2", "bullet 3", "bullet 4"],
    "industry_paragraph": "Industry context paragraph for cards.",
    "conclusion_block": (
        "Consensus prices in TPU narrowing the perf gap; we model a wider gap "
        "holding through CY26 because v6 ramp lags shipped roadmap by 6 months."
    ),
    "revenue_explainer_points": ["explainer 1", "explainer 2", "explainer 3"],
    "current_business_points": ["current 1", "current 2"],
    "future_watch_points": ["watch 1", "watch 2"],
    "judgement_paragraph": (
        "Future 18-month verification: pricing discipline holds through CY26; "
        "thesis breaks if any hyperscaler renegotiation cuts ASP >10%."
    ),
    "brand_subheading": "high-conviction long-bias",
    "brand_statement": (
        "Asymmetric upside on AI capex sustainability — free cash flow yield 4% "
        "vs peer 1.5%, with CEO signaling multi-year sovereign-AI tailwind at GTC."
    ),
    "memory_points": ["memory 1", "memory 2", "memory 3"],
    "cta_line": "下季关键验证清单：H200 mix、HBM 供给紧张持续、Blackwell ramp 节奏。",
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
        issues = validate_card1_5_analytical_content(cards, worker)
        self.assertEqual(
            issues,
            [],
            msg=f"Positive fixture should produce zero issues; got: {issues}",
        )


class NegativeFixtureTests(unittest.TestCase):
    """Each test mutates one thing on the positive fixture and asserts that
    the validator surfaces an issue mentioning the offending slot/concept."""

    # Helpers --------------------------------------------------------------

    def _assert_any(self, issues: list[str], *needles: str) -> None:
        """All needles must appear (case-insensitive) somewhere in issues."""
        self.assertTrue(
            issues, msg="Expected at least one issue, got empty list."
        )
        joined = "\n".join(issues).lower()
        for needle in needles:
            self.assertIn(
                needle.lower(),
                joined,
                msg=(
                    f"Expected an issue mentioning {needle!r}; "
                    f"got issues:\n{issues}"
                ),
            )

    # Tests ---------------------------------------------------------------

    def test_missing_worker_notes_entirely(self) -> None:
        cards, _ = _fresh_fixture()
        issues = validate_card1_5_analytical_content(cards, None)
        self._assert_any(issues, "missing card_slots_worker_notes.json")

    def test_data_anchor_missing_number(self) -> None:
        cards, worker = _fresh_fixture()
        worker["intro_sentence"]["data_anchor"] = (
            "datacenter revenue strong vs peer AMD"
        )
        issues = validate_card1_5_analytical_content(cards, worker)
        self._assert_any(issues, "data_anchor", "number")

    def test_data_anchor_missing_comp_keyword(self) -> None:
        cards, worker = _fresh_fixture()
        worker["intro_sentence"]["data_anchor"] = "datacenter revenue $30.8B Q3"
        issues = validate_card1_5_analytical_content(cards, worker)
        self._assert_any(issues, "comp anchor")

    def test_variant_view_too_short(self) -> None:
        cards, worker = _fresh_fixture()
        worker["intro_sentence"]["variant_view"] = "wait and see"
        issues = validate_card1_5_analytical_content(cards, worker)
        self._assert_any(issues, "variant_view", "too short")

    def test_no_falsifier_quote_or_catalyst(self) -> None:
        cards, worker = _fresh_fixture()
        for key in ("falsifier", "primary_quote", "catalyst_with_date"):
            worker["intro_sentence"].pop(key, None)
        issues = validate_card1_5_analytical_content(cards, worker)
        self._assert_any(
            issues, "falsifier", "primary_quote", "catalyst_with_date"
        )

    def test_authority_slot_missing_primary_quote(self) -> None:
        cards, worker = _fresh_fixture()
        # Drop primary_quote from brand_statement but leave a falsifier so the
        # falsifier|quote|catalyst check still passes (we want to isolate the
        # authority-slot quote requirement).
        worker["brand_statement"].pop("primary_quote", None)
        worker["brand_statement"]["falsifier"] = (
            "FCF yield collapses below 2% on capex resumption"
        )
        issues = validate_card1_5_analytical_content(cards, worker)
        self._assert_any(issues, "primary_quote", "authority")

    def test_backstop_shuobaile_in_intro(self) -> None:
        cards, worker = _fresh_fixture()
        cards["intro_sentence"] = "说白了，WDC 卖的是云存储容量。"
        issues = validate_card1_5_analytical_content(cards, worker)
        self._assert_any(issues, "说白了")

    def test_backstop_binary_flip_in_judgement(self) -> None:
        cards, worker = _fresh_fixture()
        cards["judgement_paragraph"] = "它不是周期股，而是 AI 基础设施。"
        issues = validate_card1_5_analytical_content(cards, worker)
        self._assert_any(issues, "不是", "而是")

    def test_backstop_clickbait_cta(self) -> None:
        cards, worker = _fresh_fixture()
        cards["cta_line"] = "关注金融豹，每天学习一个公司。"
        issues = validate_card1_5_analytical_content(cards, worker)
        # Accept either "subscription-bait" or "验证清单" framing — both encode
        # the same gate per spec.
        self.assertTrue(issues, msg="Expected clickbait cta to surface issues.")
        joined = "\n".join(issues).lower()
        self.assertIn("cta_line", joined)
        self.assertTrue(
            ("subscription-bait" in joined) or ("验证清单" in joined),
            msg=(
                "Expected cta_line issue to mention 'subscription-bait' or "
                f"'验证清单'; got issues:\n{issues}"
            ),
        )

    def test_card6_slots_are_exempt(self) -> None:
        cards, worker = _fresh_fixture()
        # Inject a Card-6-only ban-listed phrase plus a Card-6 title; with
        # valid worker_notes for Cards 1-5, validation must still pass.
        cards["post_content_lines"] = [
            "说白了, X",
            "Y placeholder line",
            "Z placeholder line",
            "Q placeholder?",
        ]
        cards["post_title"] = "说白了, this is the card-6 title"
        issues = validate_card1_5_analytical_content(cards, worker)
        self.assertEqual(
            issues,
            [],
            msg=(
                "Card 6 slots must be exempt from the Card 1-5 analytical "
                f"content gate; got: {issues}"
            ),
        )


# ---------------------------------------------------------------------------
# WDC bad-lines regression fixture
# ---------------------------------------------------------------------------


# Minimal valid worker_notes covering all six Card 1-5 worker slots so the
# *worker_notes* half of the gate passes — every failure surfaced by the WDC
# fixture must come from the *backstop banned-phrase* half of the gate.
_WDC_VALID_WORKER: dict = copy.deepcopy(POSITIVE_WORKER)


WDC_BAD_CARDS: dict = {
    "intro_sentence": (
        "西部数据现在最值钱的，不是硬盘这个老词，而是AI数据长期存储的供给瓶颈。"
    ),
    "company_focus_paragraph": (
        "Nearline HDD 容量出货 +18% YoY，云客户占比 56%。"
    ),
    "background_bullets": ["b1", "b2", "b3", "b4"],
    "industry_paragraph": "HDD 容量需求仍由超大规模云客户主导。",
    "conclusion_block": (
        "行业不是没竞争，而是短期供需太紧，让竞争从价格战变成产能和路线图之争。"
    ),
    "revenue_explainer_points": ["r1", "r2", "r3"],
    "current_business_points": ["c1", "c2"],
    "future_watch_points": ["w1", "w2"],
    "judgement_paragraph": (
        "说白了，它现在像AI基础设施；供给一松，又会被当周期股。"
    ),
    "brand_subheading": "asymmetric",
    "brand_statement": (
        "说白了，WDC卖的是大规模、低成本、能被云厂商长期锁定的数据存储容量。"
    ),
    "memory_points": ["m1", "m2", "m3"],
    "cta_line": "关注金融豹，每天学习一个公司。",
}


class WdcBadLinesRegressionTest(unittest.TestCase):
    def test_wdc_bad_lines_surface_all_five_issues(self) -> None:
        issues = validate_card1_5_analytical_content(
            WDC_BAD_CARDS, copy.deepcopy(_WDC_VALID_WORKER)
        )
        self.assertTrue(
            issues, msg="WDC bad-line fixture should not validate clean."
        )
        joined = "\n".join(issues)
        joined_lc = joined.lower()

        # 1. intro_sentence — binary flip "不是 X 而是 Y"
        self.assertIn("intro_sentence", joined_lc)
        # 2. conclusion_block — same binary flip template
        self.assertIn("conclusion_block", joined_lc)
        # 3. judgement_paragraph — 说白了
        self.assertIn("judgement_paragraph", joined_lc)
        self.assertIn("说白了", joined)
        # 4. brand_statement — 说白了
        self.assertIn("brand_statement", joined_lc)
        # 5. cta_line — clickbait
        self.assertIn("cta_line", joined_lc)

        # Sanity: at least 5 *distinct* issue messages (one per offending slot).
        distinct = {iss.strip() for iss in issues if iss.strip()}
        self.assertGreaterEqual(
            len(distinct),
            5,
            msg=(
                "Expected >=5 distinct issue messages across the five WDC "
                f"slots; got {len(distinct)}:\n{issues}"
            ),
        )


if __name__ == "__main__":
    unittest.main()
