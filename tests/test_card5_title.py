from __future__ import annotations

from pathlib import Path

from scripts.generate_social_cards import card_5_title, parse_html


def _minimal_report(tmp_path: Path, lang: str) -> Path:
    path = tmp_path / f"report_{lang}.html"
    path.write_text(
        f'<html lang="{lang}"><body><div class="company-name-cn">测试公司</div></body></html>',
        encoding="utf-8",
    )
    return path


def test_parse_html_detects_chinese_report_language(tmp_path: Path) -> None:
    assert parse_html(_minimal_report(tmp_path, "zh-CN")).report_language == "cn"


def test_parse_html_detects_english_report_language(tmp_path: Path) -> None:
    assert parse_html(_minimal_report(tmp_path, "en-US")).report_language == "en"


def test_card5_titles_are_locked() -> None:
    assert card_5_title("cn") == "国家如何塑造公司"
    assert card_5_title("en") == "How institutions and culture shape the company"
