from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

import pytest


SCRIPT = Path(__file__).parents[1] / "scripts" / "generate_social_cards.py"
SPEC = importlib.util.spec_from_file_location("generate_social_cards_v5", SCRIPT)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


TEMPLATE = Path(__file__).parents[1] / "references" / "templates" / "card_slots.template.json"


def slots_v5() -> dict:
    return json.loads(TEMPLATE.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> Path:
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return path


def claim(claim_id: str, slot_path: str, kind: str, *, basis_id: str | None = None) -> dict:
    value = {
        "claim_id": claim_id,
        "slot_path": slot_path,
        "epistemic_type": kind,
        "source_refs": [{"publisher": "测试来源", "url": "https://example.com/source"}],
        "as_of_date": "2026-07-13",
    }
    if kind in {"inference", "forecast"}:
        value["falsifier"] = "若下一期对应指标不再沿该路径变化，则推断失效。"
    if basis_id:
        value["basis_id"] = basis_id
    return value


def valid_worker_notes() -> dict:
    return {
        "claims": [
            claim("c01", "one_minute_summary.business_model", "company_disclosure"),
            claim("c02", "one_minute_summary.core_variables", "inference"),
            claim("c03", "one_minute_summary.primary_risk", "external_fact"),
            claim("c04", "industry_paragraph", "external_fact"),
            claim("c05", "background_bullets", "external_fact"),
            claim("c06", "five_year_arc.narrative", "company_disclosure"),
            claim("c07", "company_quality.valuation.finding", "external_fact"),
            claim("c08", "company_quality.governance_incentives.finding", "external_fact"),
            claim("c09", "company_quality.capital_allocation.finding", "company_disclosure"),
            claim("c10", "company_quality.accounting_quality.finding", "external_fact"),
            claim("c11", "country_lens.dimensions", "external_fact"),
            claim("c12", "country_lens.top_warnings", "inference"),
            claim("c13", "country_lens.company_to_country_insight", "inference"),
        ]
    }


def test_active_filenames_are_continuous_five_card_contract() -> None:
    assert module.CARD_FILENAMES == (
        "01_cover.png",
        "02_porter.png",
        "03_five_year_financials.png",
        "04_company_quality.png",
        "05_country_lens.png",
    )


def test_load_accepts_complete_schema_v5(tmp_path: Path) -> None:
    loaded = module.load_card_slots(write_json(tmp_path / "slots.json", slots_v5()))
    assert loaded.schema_version == 5
    assert loaded.cfa_lens is None


@pytest.mark.parametrize("version", [3, 4])
def test_load_rejects_archived_slot_versions(tmp_path: Path, version: int) -> None:
    slots = slots_v5()
    slots["schema_version"] = version
    with pytest.raises(ValueError, match="Re-run content production"):
        module.load_card_slots(write_json(tmp_path / f"slots-{version}.json", slots))


def test_schema_v5_rejects_cfa_lens(tmp_path: Path) -> None:
    slots = slots_v5()
    slots["cfa_lens"] = {"concept_key": "legacy"}
    with pytest.raises(ValueError, match="must not contain cfa_lens"):
        module.load_card_slots(write_json(tmp_path / "slots.json", slots))


def test_schema_v5_rejects_unordered_card2_context_facts(tmp_path: Path) -> None:
    slots = slots_v5()
    slots["background_bullets"][0], slots["background_bullets"][1] = (
        slots["background_bullets"][1],
        slots["background_bullets"][0],
    )
    with pytest.raises(ValueError, match="causal order"):
        module.load_card_slots(write_json(tmp_path / "slots.json", slots))


def test_claim_level_gate_accepts_full_visible_coverage() -> None:
    assert module.validate_card1_5_analytical_content(slots_v5(), valid_worker_notes()) == []


def test_claim_gate_rejects_unicode_math_minus_in_visible_copy() -> None:
    slots = slots_v5()
    slots["company_quality"]["capital_allocation"]["evidence"] = "按OCF−Capex计算自由现金流。"
    issues = module.validate_card1_5_analytical_content(slots, valid_worker_notes())
    assert any("U+2212" in issue for issue in issues)
    assert module.clean("按OCF−Capex计算") == "按OCF - Capex计算"


def test_card5_rejects_repeated_inference_openers() -> None:
    slots = slots_v5()
    slots["country_lens"]["dimensions"][0]["company_transmission"] = "据此推断，税率变化影响现金。"
    slots["country_lens"]["top_warnings"][0] = "据此推断，现金流可能承压。"
    slots["country_lens"]["company_to_country_insight"] = "据此推断，公司受本国规则影响。"
    issues = module.validate_card1_5_analytical_content(slots, valid_worker_notes())
    assert sum("Card 5 layout already conveys inference" in issue for issue in issues) == 3


def test_card5_warning_join_normalizes_prefixes_and_punctuation() -> None:
    text = module.join_card5_warnings([
        "据此推断，第一项预警。",
        "据此推断，第二项预警；",
    ])
    assert text == "第一项预警；第二项预警。"
    assert "。；" not in text


def test_card5_rejects_malformed_ba_easy_misread_word_order() -> None:
    slots = slots_v5()
    slots["country_lens"]["company_to_country_insight"] = "公司反映资本市场把再投资型现金流转负易误读为经营危机。"
    issues = module.validate_card1_5_analytical_content(slots, valid_worker_notes())
    assert any("malformed '把……易误读为……'" in issue for issue in issues)


def test_claim_level_gate_requires_basis_for_calculation() -> None:
    notes = copy.deepcopy(valid_worker_notes())
    notes["claims"][6]["epistemic_type"] = "analyst_calculation"
    issues = module.validate_card1_5_analytical_content(slots_v5(), notes)
    assert any("basis_id" in issue for issue in issues)


def test_claim_level_gate_rejects_unresolved_slot_path() -> None:
    notes = copy.deepcopy(valid_worker_notes())
    notes["claims"][0]["slot_path"] = "cfa_lens.formula"
    issues = module.validate_card1_5_analytical_content(slots_v5(), notes)
    assert any("does not resolve" in issue for issue in issues)
