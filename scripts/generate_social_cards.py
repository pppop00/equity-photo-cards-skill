#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import sys
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont

# Logical layout size (design / validation coordinates). Layout code uses this space.
EXPORT_W, EXPORT_H = 1080, 1350
# Internal render scale; default PNG export is W×H (e.g. 2160×2700 when LAYOUT_SCALE=2).
LAYOUT_SCALE = 2
W = EXPORT_W * LAYOUT_SCALE
H = EXPORT_H * LAYOUT_SCALE
# When True, finalize_export() downscales to EXPORT_W×EXPORT_H. Default False = full canvas for zoom-friendly PNGs.
_EXPORT_DOWN_SAMPLE_TO_LOGICAL: bool = False
_ACTIVE_PALETTE: str | None = None

# Macaron palette: mirrors the updated HTML visual tokens.
BG = "#FBF6EF"
TEXT = "#3B3A4A"
MUTED = "#6C6A7C"
LINE = "#E9E2D6"
PANEL = "#FFF2E2"
RED = "#D86B79"
ORANGE = "#D68852"
GOLD = "#E9C17A"
GREEN = "#8FCF9F"
BLUE = "#9FB9E2"
WHITE = "#FFFFFF"

HEADER_BG: str | None = "#141A2C"
HEADER_BRAND_TEXT = "#FFFFFF"
HEADER_SUBTITLE_TEXT = "#F6B48A"
HEADER_PAGE_TEXT = "#F2EFE6"
HEADER_RULE = "#2A3046"

PANEL_MINT = "#E6F5E4"
PANEL_SKY = "#DCE9F7"
PANEL_PINK = "#FBE0E4"
PANEL_LILAC = "#EADCF3"
PANEL_CREAM = "#FFF2E2"
TRACK = "#F0EBE0"
PORTER_COLORS = ["#F6B48A", "#F4A5AE", "#9FB9E2", "#8FCF9F", "#B9A2D9"]

import os as _os


def apply_palette(name: str) -> None:
    """Switch global colors for preview / alternate looks. Call before rendering."""
    global _ACTIVE_PALETTE
    global BG, TEXT, MUTED, LINE, PANEL, RED, ORANGE, GOLD, GREEN, BLUE, WHITE
    global HEADER_BG, HEADER_BRAND_TEXT, HEADER_SUBTITLE_TEXT, HEADER_PAGE_TEXT, HEADER_RULE
    global PANEL_MINT, PANEL_SKY, PANEL_PINK, PANEL_LILAC, PANEL_CREAM, TRACK, PORTER_COLORS
    _ACTIVE_PALETTE = name
    if name == "macaron":
        BG = "#FBF6EF"
        TEXT = "#3B3A4A"
        MUTED = "#6C6A7C"
        LINE = "#E9E2D6"
        PANEL = "#FFF2E2"
        RED = "#D86B79"
        ORANGE = "#D68852"
        GOLD = "#E9C17A"
        GREEN = "#8FCF9F"
        BLUE = "#9FB9E2"
        WHITE = "#FFFFFF"
        HEADER_BG = "#141A2C"
        HEADER_BRAND_TEXT = "#FFFFFF"
        HEADER_SUBTITLE_TEXT = "#F6B48A"
        HEADER_PAGE_TEXT = "#F2EFE6"
        HEADER_RULE = "#2A3046"
        PANEL_MINT = "#E6F5E4"
        PANEL_SKY = "#DCE9F7"
        PANEL_PINK = "#FBE0E4"
        PANEL_LILAC = "#EADCF3"
        PANEL_CREAM = "#FFF2E2"
        TRACK = "#F0EBE0"
        PORTER_COLORS = ["#F6B48A", "#F4A5AE", "#9FB9E2", "#8FCF9F", "#B9A2D9"]
        return
    if name == "default":
        BG = "#FCFCFD"
        TEXT = "#111827"
        MUTED = "#667085"
        LINE = "#EAECF0"
        PANEL = "#FFF7ED"
        RED = "#E82127"
        ORANGE = "#B45309"
        GOLD = "#C9A35D"
        GREEN = "#12B76A"
        BLUE = "#1570EF"
        WHITE = "#FFFFFF"
        HEADER_BG = None
        HEADER_BRAND_TEXT = "#F8FAFC"
        HEADER_SUBTITLE_TEXT = "#FBBF24"
        HEADER_PAGE_TEXT = "#F8FAFC"
        HEADER_RULE = "#334155"
        PANEL_MINT = PANEL
        PANEL_SKY = WHITE
        PANEL_PINK = PANEL
        PANEL_LILAC = PANEL
        PANEL_CREAM = PANEL
        TRACK = LINE
        PORTER_COLORS = []
        return
    if name == "b":
        # Xiaohongshu-friendly: soft violet canvas + purple / emerald accents.
        BG = "#FAF5FF"
        TEXT = "#0F172A"
        MUTED = "#64748B"
        LINE = "#E9D5FF"
        PANEL = "#F3E8FF"
        RED = "#7C3AED"
        ORANGE = "#A855F7"
        GOLD = "#C9A35D"
        GREEN = "#059669"
        BLUE = "#6366F1"
        WHITE = "#FFFFFF"
        HEADER_BG = None
        HEADER_BRAND_TEXT = "#F8FAFC"
        HEADER_SUBTITLE_TEXT = "#FBBF24"
        HEADER_PAGE_TEXT = "#F8FAFC"
        HEADER_RULE = "#334155"
        PANEL_MINT = PANEL
        PANEL_SKY = WHITE
        PANEL_PINK = PANEL
        PANEL_LILAC = PANEL
        PANEL_CREAM = PANEL
        TRACK = LINE
        PORTER_COLORS = []
        return
    if name == "c":
        # Magazine-style: warm paper body + dark header bar.
        BG = "#FFFBF7"
        TEXT = "#0F172A"
        MUTED = "#57534E"
        LINE = "#E7E5E4"
        PANEL = "#FFF1E6"
        RED = "#E11D48"
        ORANGE = "#EA580C"
        GOLD = "#D97706"
        GREEN = "#059669"
        BLUE = "#2563EB"
        WHITE = "#FFFFFF"
        HEADER_BG = "#0F172A"
        HEADER_BRAND_TEXT = "#F8FAFC"
        HEADER_SUBTITLE_TEXT = "#FBBF24"
        HEADER_PAGE_TEXT = "#F8FAFC"
        HEADER_RULE = "#334155"
        PANEL_MINT = PANEL
        PANEL_SKY = WHITE
        PANEL_PINK = PANEL
        PANEL_LILAC = PANEL
        PANEL_CREAM = PANEL
        TRACK = LINE
        PORTER_COLORS = []
        return
    raise ValueError(f"Unknown palette: {name!r}")

def _pick_font_path(candidates: list) -> str:
    for p in candidates:
        if _os.path.exists(p):
            return p
    raise FileNotFoundError(f"None of the candidate fonts found: {candidates}")

SERIF = _pick_font_path([
    "/System/Library/Fonts/STSong.ttc",
    "/System/Library/Fonts/Supplemental/Songti.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc",
    "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
])
# Primary sans font for CJK body, labels, footer, and header.
ARIAL = _pick_font_path([
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
])
ARIAL_BOLD = _pick_font_path([
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
])
# Latin / number font, approximating Inter with system fonts.
_LATIN_FONT_PATH = _pick_font_path([
    "/System/Library/Fonts/SFNS.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
])
_LATIN_BOLD_PATH = _pick_font_path([
    "/System/Library/Fonts/SFNS.ttf",
    "/System/Library/Fonts/HelveticaNeue.ttc",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
])
_SINGLE_FONT_MODE = True
LEADING_PUNCT = set("，。；：、,.!?！？）》】」』）")
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
LOGO_CLEANUP_EXTS = IMAGE_EXTS | {".svg"}
WORD_TOKEN = re.compile(r"^[A-Za-z0-9.+/%$-]+$")
# CJK blocks for cover/footer company display (Card 1 red title must read Chinese when report is CN-facing)
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")
TEXT_RENDER_SCALE = 6


class ScaledDraw:
    """Layout uses logical (EXPORT_W×EXPORT_H) coordinates; underlying buffer is W×H."""

    def __init__(self, draw: ImageDraw.ImageDraw, scale: int):
        self._draw = draw
        self._s = scale

    @property
    def _image(self) -> Image.Image:
        return self._draw._image

    def textlength(self, text: str, font=None, **kwargs: Any) -> float:
        return self._draw.textlength(text, font=font, **kwargs)

    def line(self, xy: tuple[int, ...], fill: str | None = None, width: int = 0, **kwargs: Any) -> None:
        s = self._s
        self._draw.line([int(c * s) for c in xy], fill=fill, width=max(1, width * s) if width else width, **kwargs)

    def rounded_rectangle(
        self,
        xy: tuple[int, int, int, int],
        radius: int = 0,
        fill: str | None = None,
        outline: str | None = None,
        width: int = 1,
        **kwargs: Any,
    ) -> None:
        s = self._s
        x0, y0, x1, y1 = xy
        self._draw.rounded_rectangle(
            (x0 * s, y0 * s, x1 * s, y1 * s),
            radius=radius * s,
            fill=fill,
            outline=outline,
            width=width * s,
            **kwargs,
        )

    def ellipse(
        self,
        xy: tuple[int, int, int, int],
        fill: str | None = None,
        outline: str | None = None,
        width: int = 0,
        **kwargs: Any,
    ) -> None:
        s = self._s
        x0, y0, x1, y1 = xy
        self._draw.ellipse(
            (x0 * s, y0 * s, x1 * s, y1 * s),
            fill=fill,
            outline=outline,
            width=width * s,
            **kwargs,
        )


def finalize_export(img: Image.Image) -> Image.Image:
    if _EXPORT_DOWN_SAMPLE_TO_LOGICAL and LAYOUT_SCALE > 1:
        return img.resize((EXPORT_W, EXPORT_H), Image.Resampling.LANCZOS).convert("RGB")
    return img.convert("RGB")


def logical_font_size(font_obj: ImageFont.FreeTypeFont) -> int:
    return max(1, font_obj.size // LAYOUT_SCALE)
SENTENCE_END = "。！？"
STIFF_OPENERS = (
    "核心论点在于：",
    "核心论点在于:",
    "投资逻辑：",
    "投资逻辑:",
    "一句判断：",
    "一句判断:",
)
HUMAN_MARKERS = ("说白了", "别看", "账单", "印钱", "印钞", "踩油门", "真要看", "本质上", "先别", "盯着", "这就是", "眼下")
# Accepted only for Card 6 `post_content_lines` validation (tieba / forum colloquial voice).
CARD6_COLLOQUIAL_MARKERS = (
    "这波",
    "离谱",
    "吃瓜",
    "吐槽",
    "笑死",
    "绷不住",
    "好家伙",
    "上头",
    "麻了",
    "急了",
    "整活",
    "阴阳",
    "蚌埠住了",
    "破防",
    "下头",
    "夺笋",
    "狠狠",
    "怼",
    "杠",
    "扎心",
    "翻车",
    "背刺",
    "破圈",
    "爆款",
    "火出圈",
    "杀疯了",
    "真的会谢",
    "绷",
)
POST_TITLE_PREFIX = "一天吃透一家公司："
REQUIRED_POST_TAGS = ("#A股", "#美股")
MAX_POST_TAGS = 7
SOURCE_DISCLAIMER_MARKERS = (
    "不构成买入价位建议",
    "情景预测不构成",
    "本报告给",
    "本报告予",
    "评级侧重",
)
FORBIDDEN_GENERATED_MARKERS = (
    "不构成买入价位建议",
    "情景预测不构成",
    "本报告给",
    "本报告予",
)

FONT_HEADER_BRAND = 28
FONT_HEADER_SUBTITLE = 15
FONT_HEADER_PAGE = 32
FONT_FOOTER = 17
FONT_COVER_META = 27
FONT_INTRO = 29
FONT_PANEL_BODY = 25
FONT_BULLET = 25
FONT_BULLET_COMPACT = 23
FONT_BRAND_SUMMARY = 24
FONT_CONCLUSION = 23
FONT_PORTER_LABEL = 21
FONT_PORTER_SCORE = 25
FONT_CHART_LABEL = 23
FONT_CHART_VALUE = 28
FONT_JUDGEMENT = 21
FONT_JUDGEMENT_MIN = 18
FONT_POST_TITLE = 42
FONT_POST_LINE = 29
FONT_POST_TAG = 23
FONT_POST_FOOTER = 17
FONT_METRIC_LABEL_START = 20
FONT_METRIC_LABEL_MIN = 16
FONT_METRIC_VALUE_START = 29
FONT_METRIC_VALUE_MIN = 22

MIN_CARD1_FOCUS_CHARS = 150
LIMIT_CARD1_FOCUS_CHARS = 165
LIMIT_CARD2_INDUSTRY_CHARS = 113
LIMIT_CARD2_BG_BULLET_CHARS = 60
LIMIT_CARD3_EXPLAINER_CHARS = 58
# Yellow explainer panel: rounded rect ends at CARD3_EXPLAINER_PANEL_BOTTOM; bullets start at 1002.
# CARD3_EXPLAINER_BOTTOM_INSET reserves space inside the panel so the last line does not sit on the bottom edge.
CARD3_EXPLAINER_PANEL_BOTTOM = 1260
CARD3_EXPLAINER_START_Y = 1002
CARD3_EXPLAINER_BOTTOM_INSET = 16
LIMIT_CARD3_EXPLAINER_TOTAL_HEIGHT = CARD3_EXPLAINER_PANEL_BOTTOM - CARD3_EXPLAINER_START_Y - CARD3_EXPLAINER_BOTTOM_INSET
TEXT_COMPOSITE_PAD = 8  # matches draw_text(): 2 * pad where pad=4
LIMIT_CARD4_NOW_BULLET_CHARS = 72
LIMIT_CARD4_FUTURE_BULLET_CHARS = 62
LIMIT_CARD4_JUDGEMENT_CHARS = 52
CARD4_JUDGEMENT_MAX_LINES = 4
CARD4_JUDGEMENT_BOX_HEIGHT = 100

FORBIDDEN_TEMPLATE_PHRASES = (
    "盘子和押注分得很清楚",
    "主业还在赚钱，新故事也在烧钱",
    "基本盘要稳，新投入也得尽快回本",
    "还是收入基本盘",
    "利润底子并没有塌",
    "基本盘还在持续发力",
    "利润和收入大体同向在走",
)

CROSS_REPORT_NAME_MARKERS = (
    "亚马逊",
    "Amazon",
    "微软",
    "Microsoft",
    "Meta",
    "礼来",
    "Lilly",
    "拼多多",
    "PDD",
    "特斯拉",
    "Tesla",
    "Temu",
    "AWS",
    "Mounjaro",
    "Zepbound",
)

AUDIT_COMMON_CN_TERMS = {
    "公司",
    "行业",
    "市场",
    "增长",
    "利润",
    "收入",
    "业务",
    "估值",
    "现在",
    "未来",
    "基本盘",
    "故事",
    "投入",
    "兑现",
    "平台",
    "产品",
    "客户",
    "主业",
    "新业务",
    "现金流",
    "利润率",
    "规模",
    "逻辑",
    "竞争",
    "需求",
    "供给",
    "数据",
    "赛道",
    "护城河",
    "高增长",
    "增速",
    "回报",
    "效率",
}

AUDIT_COMMON_EN_TERMS = {
    "company",
    "market",
    "growth",
    "profit",
    "revenue",
    "business",
    "industry",
    "cash",
    "flow",
    "margin",
    "platform",
    "services",
}


@dataclass
class CardSlotOverrides:
    """Slot copy from the content + layout agents. The skill requires a complete file for every export (no heuristic-only path)."""

    schema_version: int = 1
    intro_sentence: str | None = None
    company_focus_paragraph: str | None = None
    background_bullets: list[str] | None = None
    industry_paragraph: str | None = None
    porter_scores: list[int] | None = None
    conclusion_block: str | None = None
    revenue_explainer_points: list[str] | None = None
    current_business_points: list[str] | None = None
    future_watch_points: list[str] | None = None
    judgement_paragraph: str | None = None
    brand_subheading: str | None = None
    brand_statement: str | None = None
    memory_points: list[str] | None = None
    cta_line: str | None = None
    logo_asset_path: str | None = None
    cover_company_name_cn: str | None = None
    post_title: str | None = None
    post_content_lines: list[str] | None = None
    hashtags: list[str] | None = None

    @staticmethod
    def from_json_dict(raw: dict[str, Any]) -> CardSlotOverrides:
        fields = {
            "schema_version",
            "intro_sentence",
            "company_focus_paragraph",
            "background_bullets",
            "industry_paragraph",
            "porter_scores",
            "conclusion_block",
            "revenue_explainer_points",
            "current_business_points",
            "future_watch_points",
            "judgement_paragraph",
            "brand_subheading",
            "brand_statement",
            "memory_points",
            "cta_line",
            "logo_asset_path",
            "cover_company_name_cn",
            "post_title",
            "post_content_lines",
            "hashtags",
        }
        kwargs: dict[str, Any] = {}
        for key in fields:
            if key not in raw:
                continue
            val = raw[key]
            kwargs[key] = int(val) if key == "schema_version" and val is not None else val
        return CardSlotOverrides(**kwargs)


def assert_card_slots_complete(slots: CardSlotOverrides) -> None:
    """Reject incomplete JSON so exports never fall back to template copy for missing slots."""

    def need_str(label: str, val: str | None) -> None:
        if not clean(val or ""):
            raise ValueError(f"card_slots.json missing or empty required field: {label}")

    def need_list(label: str, items: list[str] | None, min_n: int) -> None:
        if not items:
            raise ValueError(f"card_slots.json missing required list: {label} (need {min_n} items).")
        n = len([x for x in items if clean(x)])
        if n < min_n:
            raise ValueError(f"card_slots.json {label} needs at least {min_n} non-empty entries (got {n}).")

    need_str("intro_sentence", slots.intro_sentence)
    need_str("company_focus_paragraph", slots.company_focus_paragraph)
    need_list("background_bullets", slots.background_bullets, 4)
    need_str("industry_paragraph", slots.industry_paragraph)
    need_str("conclusion_block", slots.conclusion_block)
    need_list("revenue_explainer_points", slots.revenue_explainer_points, 3)
    need_list("current_business_points", slots.current_business_points, 4)
    need_list("future_watch_points", slots.future_watch_points, 4)
    need_str("judgement_paragraph", slots.judgement_paragraph)
    need_str("brand_statement", slots.brand_statement)
    need_list("memory_points", slots.memory_points, 3)
    need_str("post_title", slots.post_title)
    need_list("post_content_lines", slots.post_content_lines, 4)
    need_list("hashtags", slots.hashtags, 3)


def load_card_slots(path: Path) -> CardSlotOverrides:
    p = path.expanduser().resolve()
    if not p.is_file():
        raise FileNotFoundError(f"Slots file not found: {p}")
    raw = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("card_slots JSON root must be an object")
    slots = CardSlotOverrides.from_json_dict(raw)
    assert_card_slots_complete(slots)
    return slots


def resolve_slots_path(html_path: Path, slots_arg: Path, *, multiple_html: bool) -> Path:
    """Single HTML: --slots is the JSON file, or a directory containing <stem>.card_slots.json.
    Multiple HTML: --slots must be a directory with one <stem>.card_slots.json per report."""
    p = slots_arg.expanduser().resolve()
    if p.is_dir():
        cand = p / f"{html_path.stem}.card_slots.json"
        if not cand.is_file():
            raise SystemExit(f"Expected slots file for {html_path.name}: {cand} (not found).")
        return cand
    if p.is_file():
        if multiple_html:
            raise SystemExit(
                "Multiple HTML files in --input: pass --slots as a directory that contains "
                f"<stem>.card_slots.json (e.g. {html_path.stem}.card_slots.json for each report)."
            )
        return p
    raise SystemExit(f"--slots path does not exist: {p}")


@dataclass
class ReportData:
    stem: str
    source_dir: Path
    company_cn: str
    company_en: str
    ticker: str
    date: str
    summary: list[str]
    highlights: list[str]
    risks: list[str]
    thesis: str
    porter_industry: str
    porter_forward: str
    porter_scores_industry: list[int]
    sankey_actual: dict[str, Any]
    financial_data: dict[str, Any]
    financial_analysis: dict[str, Any]
    porter_analysis: dict[str, Any]
    card_slots: CardSlotOverrides | None = None


def f(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = ARIAL_BOLD if bold else ARIAL
    return ImageFont.truetype(path, size=size * LAYOUT_SCALE)


def fs(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Serif font for title, company, and value display."""
    return ImageFont.truetype(SERIF, size=size * LAYOUT_SCALE)


def _fl(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Latin font for the given size (same as f() on macOS, DejaVu on Linux)."""
    path = _LATIN_BOLD_PATH if bold else _LATIN_FONT_PATH
    return ImageFont.truetype(path, size=size * LAYOUT_SCALE)


def _is_cjk_char(ch: str) -> bool:
    cp = ord(ch)
    return (
        0x4E00 <= cp <= 0x9FFF   # CJK Unified Ideographs
        or 0x3400 <= cp <= 0x4DBF  # CJK Extension A
        or 0x20000 <= cp <= 0x2A6DF  # Extension B
        or 0x3000 <= cp <= 0x303F  # CJK Symbols and Punctuation
        or 0xFF00 <= cp <= 0xFFEF  # Halfwidth/Fullwidth Forms
        or 0x2E80 <= cp <= 0x2EFF  # CJK Radicals Supplement
        or 0xF900 <= cp <= 0xFAFF  # CJK Compatibility Ideographs
        or 0x2F00 <= cp <= 0x2FDF  # Kangxi Radicals
    )


def _char_font(ch: str, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Return the appropriate font for a single character."""
    if _SINGLE_FONT_MODE:
        return f(size, bold)
    if _is_cjk_char(ch):
        return f(size, bold)   # DroidSans for CJK
    return _fl(size, bold)     # DejaVu for Latin/numbers/punctuation


def _mixed_textlength(text: str, size: int, bold: bool = False) -> float:
    """Measure the pixel width of mixed CJK+Latin text."""
    if _SINGLE_FONT_MODE:
        return f(size, bold).getlength(text)
    total = 0.0
    for ch in text:
        font = _char_font(ch, size, bold)
        bbox = font.getbbox(ch)
        total += bbox[2] - bbox[0]
    return total


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def js_object_to_json(text: str) -> str:
    return re.sub(r'([{,]\s*)([A-Za-z_][A-Za-z0-9_]*)\s*:', r'\1"\2":', text)


def extract_json_var(html: str, var_name: str) -> dict[str, Any]:
    match = re.search(rf"const {re.escape(var_name)} = (\{{.*?\}});", html, re.S)
    return json.loads(js_object_to_json(match.group(1))) if match else {}


def extract_porter_scores(html: str) -> list[int]:
    match = re.search(r"industry:\s*\[(.*?)\]", html, re.S)
    return [int(p.strip()) for p in match.group(1).split(",")] if match else [3, 3, 3, 3, 3]


def get_nested(obj: dict[str, Any], *keys: str, default: Any = None) -> Any:
    cur: Any = obj
    for key in keys:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def pick_first(*values: Any) -> str:
    for value in values:
        if isinstance(value, str) and clean(value):
            return clean(value)
        if value is not None and not isinstance(value, str):
            return str(value)
    return ""


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = clean(str(value)).replace(",", "").replace("%", "")
    match = re.search(r"[-+]?\d+(?:\.\d+)?", text)
    if not match:
        return None
    return float(match.group(0))


def parse_html(path: Path) -> ReportData:
    raw = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(raw, "lxml")
    company_cn_node = soup.select_one(".company-name-cn")
    company_en_node = soup.select_one(".company-name-en")
    company_cn = clean(company_cn_node.get_text()) if company_cn_node else ""
    company_en_full = clean(company_en_node.get_text(" ")) if company_en_node else ""
    company_en = company_en_full.split("·")[0].strip() if company_en_full else company_cn
    ticker = company_en_full.split("·")[-1].strip() if "·" in company_en_full else company_en_full
    meta_spans = soup.select(".header-meta span")
    date = clean(meta_spans[0].get_text()) if meta_spans else ""
    summary = [clean(p.get_text(" ")) for p in soup.select("#section-summary .summary-para")]
    highlights = [clean(li.get_text(" ")) for li in soup.select(".highlights-box li")]
    risks = [clean(li.get_text(" ")) for li in soup.select(".risks-box li")]
    thesis_node = soup.select_one(".thesis-box")
    thesis = clean(thesis_node.get_text(" ").replace("投资逻辑：", "")) if thesis_node else ""
    porter_texts = [clean(div.get_text(" ")) for div in soup.select(".porter-text")]
    source_dir = path.parent
    return ReportData(
        stem=path.stem,
        source_dir=source_dir,
        company_cn=company_cn,
        company_en=company_en,
        ticker=ticker,
        date=date,
        summary=summary,
        highlights=highlights,
        risks=risks,
        thesis=thesis,
        porter_industry=porter_texts[1] if len(porter_texts) > 1 else "",
        porter_forward=porter_texts[2] if len(porter_texts) > 2 else "",
        porter_scores_industry=extract_porter_scores(raw),
        sankey_actual=extract_json_var(raw, "sankeyActualData"),
        financial_data=load_json(source_dir / "financial_data.json"),
        financial_analysis=load_json(source_dir / "financial_analysis.json"),
        porter_analysis=load_json(source_dir / "porter_analysis.json"),
        card_slots=None,
    )


def porter_scores_for_card(data: ReportData) -> list[int]:
    if data.card_slots and data.card_slots.porter_scores is not None:
        return data.card_slots.porter_scores
    return data.porter_scores_industry


def display_name(name: str) -> str:
    return name[:-2] if name.endswith("公司") else name


def has_cjk(text: str) -> bool:
    return bool(_CJK_RE.search(clean(text)))


def company_short_cn(data: ReportData) -> str:
    """
    Short Chinese name for Card 1 red title, footers, and post-title fallback.

    When ``card_slots.logo_asset_path`` is set, ``cover_company_name_cn`` must be
    set by the logo production agent (verified Chinese short name vs HTML; strip
    trailing ``公司`` via ``display_name``). The renderer does not translate.

    When no logo path: prefer HTML ``.company-name-cn`` if it contains CJK; else
    use ``cover_company_name_cn`` when present (e.g. English HTML before logo).
    """
    slots = data.card_slots
    logo_on = bool(slots and (slots.logo_asset_path or "").strip())
    cover = clean(slots.cover_company_name_cn or "") if slots else ""
    html_cn = clean(data.company_cn)
    if logo_on:
        return display_name(cover) if cover else display_name(html_cn)
    if has_cjk(html_cn):
        return display_name(html_cn)
    if cover:
        return display_name(cover)
    return display_name(html_cn)


def export_date_cn() -> str:
    now = datetime.now().astimezone()
    return f"{now.year}年{now.month}月{now.day}日"


def hashtag_token(text: str) -> str:
    return "#" + re.sub(r"\s+", "", text.lstrip("#"))


def join_tokens(tokens: list[str]) -> str:
    out: list[str] = []
    prev = ""
    for token in tokens:
        if out and WORD_TOKEN.match(prev) and WORD_TOKEN.match(token):
            out.append(" ")
        out.append(token)
        prev = token
    return "".join(out)


def wrap(draw: ImageDraw.ImageDraw, text: str, font_obj: ImageFont.FreeTypeFont, width: int) -> list[str]:
    tokens = re.findall(r"[A-Za-z0-9.+/%$-]+|[\u4e00-\u9fff]|[^\s]", clean(text))
    lines: list[str] = []
    cur_tokens: list[str] = []
    logical_size = logical_font_size(font_obj)
    max_px = width * LAYOUT_SCALE
    for token in tokens:
        trial = join_tokens(cur_tokens + [token])
        measure = (
            _mixed_textlength(trial, logical_size) if not _SINGLE_FONT_MODE else draw.textlength(trial, font=font_obj)
        )
        if measure <= max_px or not cur_tokens:
            cur_tokens.append(token)
        else:
            if token in LEADING_PUNCT and cur_tokens:
                if len(cur_tokens) >= 2:
                    moved = cur_tokens.pop()
                    lines.append(join_tokens(cur_tokens))
                    cur_tokens = [moved, token]
                else:
                    cur_tokens.append(token)
            else:
                lines.append(join_tokens(cur_tokens))
                cur_tokens = [token]
    if cur_tokens:
        lines.append(join_tokens(cur_tokens))
    return lines


def has_bad_linebreak(text: str, width: int, font_obj: ImageFont.FreeTypeFont, draw: ImageDraw.ImageDraw) -> bool:
    lines = wrap(draw, text, font_obj, width)
    return any(line and line[0] in LEADING_PUNCT for line in lines[1:])


def draw_text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, font_obj: ImageFont.FreeTypeFont, fill: str) -> None:
    px = xy[0] * LAYOUT_SCALE
    py = xy[1] * LAYOUT_SCALE
    pad = 4 * LAYOUT_SCALE
    if _SINGLE_FONT_MODE:
        # macOS: single Unicode font, use original fast path
        base = draw._image
        bbox = font_obj.getbbox(text)
        width = max(1, bbox[2] - bbox[0])
        height = max(1, bbox[3] - bbox[1])
        scale = TEXT_RENDER_SCALE
        hq_font = ImageFont.truetype(font_obj.path, size=font_obj.size * scale)
        hq = Image.new("RGBA", ((width + pad * 2) * scale, (height + pad * 2) * scale), (255, 255, 255, 0))
        hq_draw = ImageDraw.Draw(hq)
        hq_draw.text(((pad - bbox[0]) * scale, (pad - bbox[1]) * scale), text, font=hq_font, fill=fill)
        down = hq.resize((width + pad * 2, height + pad * 2), Image.Resampling.LANCZOS)
        base.alpha_composite(down, (px - pad, py - pad))
        return

    # Linux split-font path: render char-by-char with CJK / Latin font selection.
    # PIL's getbbox returns (x0, y0, x1, y1) relative to the drawing origin, with all
    # values POSITIVE and increasing downward. Drawing all chars at the same y=0 naturally
    # bottom-aligns Latin characters (they share the same y1 within the em square).
    phys_size = font_obj.size
    logical_size = logical_font_size(font_obj)
    scale = TEXT_RENDER_SCALE

    # Build char list with HQ scaled fonts; measure canvas dimensions
    char_entries: list[tuple[str, ImageFont.FreeTypeFont, tuple[int, int, int, int]]] = []
    total_w = 0
    max_y1 = 0  # Maximum bottom extent across all chars (determines canvas height)
    for ch in text:
        cf = _char_font(ch, logical_size)
        hq_cf = ImageFont.truetype(cf.path, size=phys_size * scale)
        bb = hq_cf.getbbox(ch)
        char_entries.append((ch, hq_cf, bb))
        total_w += bb[2] - bb[0]
        max_y1 = max(max_y1, bb[3])

    if total_w <= 0:
        return

    pad_logical = 4
    pad_out = pad_logical * LAYOUT_SCALE
    canvas_w = total_w + pad_logical * 2 * scale * LAYOUT_SCALE
    canvas_h = max_y1 + pad_logical * 2 * scale * LAYOUT_SCALE
    hq = Image.new("RGBA", (canvas_w, canvas_h), (255, 255, 255, 0))
    hq_draw = ImageDraw.Draw(hq)

    # Draw all characters at the same y=pad*scale; PIL positions each glyph
    # from (x, y+bb[1]) to (x, y+bb[3]), giving natural bottom alignment.
    cx = pad_logical * scale * LAYOUT_SCALE
    y0 = pad_logical * scale * LAYOUT_SCALE
    for ch, hq_cf, bb in char_entries:
        hq_draw.text((cx - bb[0], y0), ch, font=hq_cf, fill=fill)
        cx += bb[2] - bb[0]

    out_w = total_w // scale + pad_out * 2
    out_h = max_y1 // scale + pad_out * 2
    down = hq.resize((out_w, out_h), Image.Resampling.LANCZOS)
    draw._image.alpha_composite(down, (px - pad, py - pad))


def line_raster_height(draw: ImageDraw.ImageDraw, font_obj: ImageFont.FreeTypeFont, line: str) -> int:
    """Logical pixel height of one draw_text() line (must match vertical advance in block())."""
    if not clean(line):
        return 0
    pad_out = 4 * LAYOUT_SCALE
    scale = TEXT_RENDER_SCALE
    phys_size = font_obj.size
    logical_size = logical_font_size(font_obj)
    if _SINGLE_FONT_MODE:
        bbox = font_obj.getbbox(line)
        return max(1, (bbox[3] - bbox[1]) // LAYOUT_SCALE + TEXT_COMPOSITE_PAD)
    max_y1 = 0
    for ch in line:
        cf = _char_font(ch, logical_size)
        hq_cf = ImageFont.truetype(cf.path, size=phys_size * scale)
        bb = hq_cf.getbbox(ch)
        max_y1 = max(max_y1, bb[3])
    inner = max(1, max_y1 // scale + 2 * pad_out)
    return max(1, inner // LAYOUT_SCALE)


def block(
    draw: ImageDraw.ImageDraw,
    text: str,
    x: int,
    y: int,
    width: int,
    font_obj: ImageFont.FreeTypeFont,
    fill: str,
    line_gap: int,
    max_lines: int | None = None,
) -> int:
    lines = wrap(draw, clean(text), font_obj, width)
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
    for i, line in enumerate(lines):
        draw_text(draw, (x, y), line, font_obj, fill)
        y += line_raster_height(draw, font_obj, line)
        if i < len(lines) - 1:
            y += line_gap
    return y


def fit_font(draw: ImageDraw.ImageDraw, text: str, max_width: int, start_size: int, min_size: int) -> ImageFont.FreeTypeFont:
    size = start_size
    max_px = max_width * LAYOUT_SCALE
    while size > min_size:
        font_obj = f(size, True)
        measure = _mixed_textlength(text, size, bold=True) if not _SINGLE_FONT_MODE else draw.textlength(text, font=font_obj)
        if measure <= max_px:
            return font_obj
        size -= 2
    return f(min_size, True)


def _fit_serif(draw: ImageDraw.ImageDraw, text: str, max_width: int, start_size: int, min_size: int) -> ImageFont.FreeTypeFont:
    size = start_size
    max_px = max_width * LAYOUT_SCALE
    while size > min_size:
        font_obj = fs(size, True)
        measure = draw.textlength(text, font=font_obj)
        if measure <= max_px:
            return font_obj
        size -= 2
    return fs(min_size, True)


def sentence_chunks(text: str, limit: int = 3) -> list[str]:
    return [clean(x) for x in re.split(r"[。！？；]", text) if clean(x)][:limit]


def strip_stiff_opener(text: str) -> str:
    text = clean(text)
    for opener in STIFF_OPENERS:
        if text.startswith(opener):
            return clean(text[len(opener):])
    return text


def ensure_terminal_punct(text: str, punct: str = "。") -> str:
    text = clean(text).rstrip("，；：,;:")
    if not text:
        return ""
    return text if text.endswith(tuple(SENTENCE_END)) else text + punct


def sentence_parts(text: str) -> list[str]:
    return [clean(part) for part in re.findall(r"[^。！？；]+[。！？；]?", clean(text)) if clean(part)]


def is_source_disclaimer_sentence(text: str) -> bool:
    normalized = clean(text)
    if not normalized:
        return False
    if any(marker in normalized for marker in SOURCE_DISCLAIMER_MARKERS):
        return True
    return "本报告" in normalized and any(marker in normalized for marker in ("增持", "买入", "评级"))


def sanitize_source_text(text: str) -> str:
    kept: list[str] = []
    for part in sentence_parts(text):
        normalized = ensure_terminal_punct(strip_stiff_opener(part))
        if normalized and not is_source_disclaimer_sentence(normalized):
            kept.append(normalized)
    return "".join(kept)


def contains_ellipsis(text: str) -> bool:
    return "…" in text or "..." in text


def is_complete_copy(text: str) -> bool:
    text = clean(text)
    return bool(text) and not contains_ellipsis(text) and text.endswith(tuple(SENTENCE_END))


def is_human_copy(text: str) -> bool:
    return any(marker in text for marker in HUMAN_MARKERS)


def card6_line_sounds_human(text: str) -> bool:
    """Card 6 may use standard HUMAN_MARKERS or extra colloquial markers (see layout-fill / content agent)."""
    if is_human_copy(text) or "真要看" in text or "钱还在进" in text:
        return True
    return any(marker in text for marker in CARD6_COLLOQUIAL_MARKERS)


def fit_copy(candidates: list[str], limit: int, *, human: bool = False) -> str:
    normalized: list[str] = []
    for raw in candidates:
        text = ensure_terminal_punct(strip_stiff_opener(raw))
        if text:
            normalized.append(text)
    for text in normalized:
        if len(text) <= limit and (not human or is_human_copy(text)):
            return text
    for text in normalized:
        if len(text) <= limit:
            return text
    if normalized:
        shortest = min(normalized, key=len)
        clauses = [clean(part) for part in re.split(r"[，；：,;:]", shortest) if clean(part)]
        rebuilt = ""
        for clause in clauses:
            trial = clause if not rebuilt else f"{rebuilt}，{clause}"
            if len(ensure_terminal_punct(trial)) <= limit:
                rebuilt = trial
        if rebuilt and len(clean(strip_voice_shell(rebuilt))) >= 4:
            return ensure_terminal_punct(rebuilt)
        clip_base = strip_voice_shell(shortest)
        if not clip_base or len(clean(clip_base)) < 4:
            clip_base = clean(shortest)
        clipped = clean(clip_base)[: max(0, limit - 1)].rstrip("，；：,;: ")
        return ensure_terminal_punct(clipped)
    return ""


def paragraph_from_sentences(text: str, limit: int, sentences: int = 3) -> str:
    parts = [ensure_terminal_punct(strip_stiff_opener(part)) for part in sentence_chunks(text, sentences)]
    out = ""
    for part in parts:
        trial = out + part
        if len(trial) <= limit:
            out = trial
    return out


def flatten_text_values(value: Any) -> list[str]:
    out: list[str] = []
    if isinstance(value, str):
        text = clean(value)
        if text:
            out.append(text)
    elif isinstance(value, dict):
        preferred = ["text", "analysis", "note", "notes"]
        seen: set[str] = set()
        for key in preferred:
            if key in value:
                for item in flatten_text_values(value[key]):
                    if item not in seen:
                        out.append(item)
                        seen.add(item)
        for key, item in value.items():
            if key in preferred:
                continue
            for text in flatten_text_values(item):
                if text not in seen:
                    out.append(text)
                    seen.add(text)
    elif isinstance(value, list):
        for item in value:
            out.extend(flatten_text_values(item))
    return out


def prepend_human_opener(text: str, opener: str = "说白了，") -> str:
    text = clean(text)
    if not text:
        return ""
    if text.startswith(("说白了", "别看", "本质上", "眼下", "先别", "盯着")):
        return ensure_terminal_punct(text)
    return ensure_terminal_punct(opener + text)


def source_copy_candidates(
    texts: list[str],
    limit: int,
    *,
    opener: str | None = None,
    sentence_options: tuple[int, ...] = (1, 2),
    human: bool = False,
) -> list[str]:
    candidates: list[str] = []
    for raw in dedupe_texts(texts):
        raw = sanitize_source_text(raw)
        if not raw:
            continue
        base = ensure_terminal_punct(strip_stiff_opener(raw))
        if base:
            candidates.append(prepend_human_opener(base, opener) if opener else base)
        for count in sentence_options:
            budget = limit - len(opener or "")
            compressed = paragraph_from_sentences(raw, budget, sentences=count)
            if compressed:
                candidates.append(prepend_human_opener(compressed, opener) if opener else compressed)
        for part in sentence_chunks(raw, 4):
            normalized = ensure_terminal_punct(strip_stiff_opener(part))
            if normalized:
                candidates.append(prepend_human_opener(normalized, opener) if opener else normalized)
    out = dedupe_texts(candidates)
    if human:
        human_first = [text for text in out if is_human_copy(text)]
        return human_first + [text for text in out if text not in human_first]
    return out


def combined_source_texts(texts: list[str], max_parts: int = 2) -> list[str]:
    items = dedupe_texts([sanitize_source_text(text) for text in texts])
    combined: list[str] = []
    for i in range(len(items)):
        acc = ""
        for j in range(i, min(len(items), i + max_parts)):
            acc += ensure_terminal_punct(items[j])
        if acc:
            combined.append(acc)
    return dedupe_texts(combined)


def dense_source_paragraph(
    texts: list[str],
    limit: int,
    *,
    opener: str | None = None,
    max_sentences: int = 3,
) -> str:
    budget = limit - len(opener or "")
    picked: list[str] = []
    for text in dedupe_texts([sanitize_source_text(text) for text in texts]):
        for sentence in sentence_chunks(text, 4):
            normalized = ensure_terminal_punct(strip_stiff_opener(sentence))
            if not normalized or normalized in picked:
                continue
            trial = "".join(picked) + normalized
            if len(trial) <= budget:
                picked.append(normalized)
            if len(picked) >= max_sentences:
                break
        if len(picked) >= max_sentences:
            break
    out = "".join(picked)
    if opener and out:
        return prepend_human_opener(out, opener)
    return out


def porter_section_texts(data: ReportData, section: str) -> list[str]:
    pa = data.porter_analysis or {}
    mapping = {
        "company": [get_nested(pa, "company_level", "text"), pa.get("company_level"), pa.get("company_perspective_zh")],
        "industry": [get_nested(pa, "industry_level", "text"), pa.get("industry_level"), pa.get("industry_perspective_zh"), data.porter_industry],
        "forward": [get_nested(pa, "forward_looking", "text"), pa.get("forward_looking"), pa.get("forward_perspective_zh"), data.porter_forward],
    }
    return dedupe_texts(flatten_text_values(mapping.get(section, [])))


def summary_texts(data: ReportData) -> list[str]:
    return dedupe_texts(data.summary)


def highlight_texts(data: ReportData) -> list[str]:
    return dedupe_texts(data.highlights)


def risk_texts(data: ReportData) -> list[str]:
    return dedupe_texts(data.risks)


def executive_texts(data: ReportData) -> list[str]:
    return dedupe_texts(
        flatten_text_values(
            [
                get_nested(data.financial_analysis, "investment_thesis_short", default=""),
                data.thesis,
                get_nested(data.financial_analysis, "executive_summary", default=""),
            ]
        )
    )


def trend_texts(data: ReportData) -> list[str]:
    return dedupe_texts(
        flatten_text_values(
            [
                get_nested(data.financial_analysis, "trend_narratives", default={}),
                get_nested(data.financial_analysis, "trends", default={}),
            ]
        )
    )


def dedupe_texts(items: list[str], limit: int | None = None) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for item in items:
        cleaned = clean(item)
        key = re.sub(r"[^\w\u4e00-\u9fff]+", "", cleaned).lower()
        if cleaned and key and key not in seen:
            seen.add(key)
            out.append(cleaned)
            if limit is not None and len(out) >= limit:
                break
    return out


def fiscal_year(data: ReportData) -> str:
    return str(get_nested(data.financial_data, "fiscal_year", default="FY"))


def income_current(data: ReportData) -> dict[str, Any]:
    return get_nested(data.financial_data, "income_statement", "current_year", default={}) or {}


def metric_current_percent(data: ReportData, metric_name: str) -> float | None:
    for item in get_nested(data.financial_analysis, "metrics", default=[]) or []:
        if not isinstance(item, dict):
            continue
        if clean(str(item.get("metric", ""))) != metric_name:
            continue
        return as_float(item.get("current"))
    return None


def profitability(data: ReportData) -> dict[str, Any]:
    prof = get_nested(data.financial_analysis, "profitability", default={}) or {}
    normalized = dict(prof)
    if "gross_margin_current" in prof:
        normalized["gross_margin_pct"] = prof["gross_margin_current"]
    if "operating_margin_current" in prof:
        normalized["operating_margin_pct"] = prof["operating_margin_current"]
    if "net_margin_current" in prof:
        normalized["net_margin_pct"] = prof["net_margin_current"]
    # Use finance() so null operating_income can fall back to Sankey-derived op profit.
    fin = finance(data)
    revenue = as_float(fin.get("revenue"))
    gross = as_float(fin.get("gross"))
    op = as_float(fin.get("op"))
    net = as_float(fin.get("net"))
    if revenue:
        if normalized.get("gross_margin_pct") is None:
            normalized["gross_margin_pct"] = (gross / revenue * 100) if gross is not None else metric_current_percent(data, "毛利率")
        if normalized.get("operating_margin_pct") is None:
            normalized["operating_margin_pct"] = (op / revenue * 100) if op is not None else metric_current_percent(data, "营业利润率")
        if normalized.get("net_margin_pct") is None:
            normalized["net_margin_pct"] = (net / revenue * 100) if net is not None else as_float(
                get_nested(data.financial_analysis, "kpis", "net_margin", "value")
            )
    if normalized.get("gross_margin_pct") is None:
        normalized["gross_margin_pct"] = metric_current_percent(data, "毛利率")
    if normalized.get("operating_margin_pct") is None:
        normalized["operating_margin_pct"] = metric_current_percent(data, "营业利润率")
    if normalized.get("net_margin_pct") is None:
        normalized["net_margin_pct"] = as_float(get_nested(data.financial_analysis, "kpis", "net_margin", "value"))
    return normalized


def growth(data: ReportData) -> dict[str, Any]:
    growth_data = get_nested(data.financial_analysis, "growth", default={}) or {}
    if "yoy_revenue_pct" in growth_data or "yoy_net_income_pct" in growth_data:
        return growth_data
    normalized = dict(growth_data)
    if "revenue_growth_yoy_pct" in growth_data:
        normalized["yoy_revenue_pct"] = growth_data["revenue_growth_yoy_pct"]
    if "net_income_growth_yoy_pct" in growth_data:
        normalized["yoy_net_income_pct"] = growth_data["net_income_growth_yoy_pct"]
    return normalized


def cash_flow(data: ReportData) -> dict[str, Any]:
    cf = get_nested(data.financial_data, "cash_flow", default={}) or {}
    if "capex_purchases" in cf:
        return cf
    normalized = dict(cf)
    if "capex" in cf and cf["capex"] is not None:
        normalized["capex_purchases"] = abs(float(cf["capex"]))
    return normalized


def operational_kpis(data: ReportData) -> dict[str, Any]:
    return get_nested(data.financial_data, "operational_kpis", default={}) or {}


def segment_data(data: ReportData) -> list[dict[str, Any]]:
    return get_nested(data.financial_data, "segment_data", default=[]) or []


def revenue_yoy(data: ReportData) -> Any:
    value = get_nested(data.financial_data, "income_statement", "yoy_revenue_pct")
    if value is not None:
        return value
    value = growth(data).get("yoy_revenue_pct")
    if value is not None:
        return value
    current = get_nested(data.financial_data, "income_statement", "current_year", "revenue")
    prior = get_nested(data.financial_data, "income_statement", "prior_year", "revenue")
    if current and prior:
        return (float(current) / float(prior) - 1) * 100
    return None


def net_income_yoy(data: ReportData) -> Any:
    value = get_nested(data.financial_data, "income_statement", "yoy_net_income_pct")
    if value is not None:
        return value
    value = growth(data).get("yoy_net_income_pct")
    if value is not None:
        return value
    current = get_nested(data.financial_data, "income_statement", "current_year", "net_income")
    prior = get_nested(data.financial_data, "income_statement", "prior_year", "net_income")
    if current and prior:
        return (float(current) / float(prior) - 1) * 100
    return None


def segment_revenue_bn(segment: dict[str, Any]) -> float:
    if segment.get("revenue_bn") is not None:
        return float(segment["revenue_bn"])
    if segment.get("revenue") is not None:
        return float(segment["revenue"]) / 1000
    return 0.0


def sankey_value_by_node_name(data: ReportData, keywords: tuple[str, ...]) -> float:
    sankey = data.sankey_actual or {}
    nodes = sankey.get("nodes", []) or []
    links = sankey.get("links", []) or []
    if not nodes or not links:
        return 0.0
    matched_targets: set[int] = set()
    for idx, node in enumerate(nodes):
        name = clean(str(node.get("name", ""))).lower()
        if any(keyword.lower() in name for keyword in keywords):
            matched_targets.add(idx)
    if not matched_targets:
        return 0.0
    total = 0.0
    for link in links:
        try:
            target = int(link.get("target"))
        except (TypeError, ValueError):
            continue
        if target in matched_targets:
            total += float(link.get("value", 0.0))
    return total


def finance(data: ReportData) -> dict[str, float]:
    links = data.sankey_actual.get("links", [])
    lookup = {(l["source"], l["target"]): float(l["value"]) for l in links}
    sankey_fin = {"revenue": 0.0, "cogs": 0.0, "gross": 0.0, "op": 0.0, "net": 0.0}
    if links:
        revenue = sum(l["value"] for l in links if l["source"] == 0)
        cogs = lookup.get((0, 1), 0.0) or sankey_value_by_node_name(data, ("营业成本", "成本", "人工成本", "cogs"))
        gross = lookup.get((0, 2), 0.0) or sankey_value_by_node_name(data, ("毛利", "gross"))
        op = lookup.get((2, 6), 0.0) or sankey_value_by_node_name(data, ("营业利润", "operating profit", "operating income"))
        net = lookup.get((6, 8), 0.0) or sankey_value_by_node_name(data, ("净利润", "归母净利润", "net income"))
        sankey_fin = {
            "revenue": revenue,
            "cogs": cogs,
            "gross": gross,
            "op": op,
            "net": net,
        }

    current = income_current(data)
    if not current:
        return sankey_fin

    # Prefer normalized financial_data values when present; if a field is null/missing,
    # fall back to Sankey-derived values instead of coercing null to 0.
    def _prefer_current(field: str, fallback_key: str) -> float:
        value = current.get(field)
        if value is None:
            return sankey_fin[fallback_key]
        try:
            return float(value)
        except (TypeError, ValueError):
            return sankey_fin[fallback_key]

    return {
        "revenue": _prefer_current("revenue", "revenue"),
        "cogs": _prefer_current("cogs", "cogs"),
        "gross": _prefer_current("gross_profit", "gross"),
        "op": _prefer_current("operating_income", "op"),
        "net": _prefer_current("net_income", "net"),
    }


def yi(value: float) -> float:
    return value / 100


def chart_value_as_yi(value: float) -> float:
    """Headline amounts for Card 3 bars: millions → 亿 via yi(); native亿元 uses value as-is."""
    global _MONEY_VALUE_SCALE
    if _MONEY_VALUE_SCALE == "yi":
        return float(value)
    return yi(value)


_CURRENCY_LABEL: str = "美元"
# "millions": value is millions of reporting currency (yi = millions/100).
# "yi": value is already 亿元人民币 (亿元); sankey / finance() use same scale.
_MONEY_VALUE_SCALE: str = "millions"


def set_currency_label(data: "ReportData") -> None:
    global _CURRENCY_LABEL, _MONEY_VALUE_SCALE
    currency = str(get_nested(data.financial_data, "currency", default="USD")).upper()
    mapping = {
        "USD": "美元",
        "RMB": "元",
        "CNY": "元",
        "人民币": "元",
        "AUD": "澳元",
        "EUR": "欧元",
        "HKD": "港元",
        "JPY": "日元",
        "GBP": "英镑",
    }
    _CURRENCY_LABEL = mapping.get(currency, "美元")
    unit = str(get_nested(data.financial_data, "income_statement", "unit", default="")).lower()
    # e.g. "billions CNY (亿元人民币)" — amounts are already in 亿元
    _MONEY_VALUE_SCALE = (
        "yi"
        if ("亿元" in unit or "亿人民币" in unit) and "百万" not in unit and "万元" not in unit
        else "millions"
    )


def money_text(value: float) -> str:
    """Format headline money: millions path uses yi = millions/100; 亿元-native uses value as 亿."""
    global _MONEY_VALUE_SCALE
    if _MONEY_VALUE_SCALE == "yi":
        v = float(value)
        av = abs(v)
        if av >= 10000.0:
            return f"{v / 10000.0:.2f} 万亿{_CURRENCY_LABEL}"
        if av < 0.01:
            wan = v * 10000.0
            return f"{wan:.0f} 万{_CURRENCY_LABEL}"
        if av < 0.1:
            return f"{v:.2f} 亿{_CURRENCY_LABEL}"
        return f"{v:.1f} 亿{_CURRENCY_LABEL}"
    y = yi(value)
    if y < 0.01:
        wan = value * 100.0
        return f"{wan:.0f} 万{_CURRENCY_LABEL}"
    if y < 0.1:
        return f"{y:.2f} 亿{_CURRENCY_LABEL}"
    return f"{y:.1f} 亿{_CURRENCY_LABEL}"


AMOUNT_WITH_UNIT_RE = re.compile(
    r"([+\-]?\d{1,3}(?:,\d{3})+(?:\.\d+)?|[+\-]?\d+(?:\.\d+)?)\s*"
    r"(万亿元|万亿|千亿元|十亿元|亿美元|亿元|亿|billion|bn|B|million|mn|M)(?![A-Za-z])",
    re.I,
)


def amount_mentions_yi(text: str, keywords: tuple[str, ...] = (), *, keyword_before_only: bool = False) -> list[float]:
    """Extract headline money amounts and normalize them to 亿 units.

    This is a scale guard, not a currency converter: 1 billion == 10 亿, and
    1 million == 0.01 亿 in the report currency.
    """
    out: list[float] = []
    haystack = clean(text)
    haystack_lower = haystack.lower()
    lowered_keywords = tuple(k.lower() for k in keywords)
    for m in AMOUNT_WITH_UNIT_RE.finditer(haystack):
        start, end = m.span()
        if lowered_keywords:
            before = haystack_lower[max(0, start - 16):start]
            window = haystack_lower[max(0, start - 16):min(len(haystack), end + 16)]
            check_area = before if keyword_before_only else window
            if not any(k in check_area for k in lowered_keywords):
                continue
        value = float(m.group(1).replace(",", ""))
        unit = m.group(2).lower()
        if unit in {"万亿元", "万亿"}:
            value *= 10000.0
        elif unit == "千亿元":
            value *= 1000.0
        elif unit == "十亿元":
            value *= 10.0
        elif unit in {"billion", "bn", "b"}:
            value *= 10.0
        elif unit in {"million", "mn", "m"}:
            value /= 100.0
        out.append(value)
    return out


def _largest_headline_amount_yi(texts: list[str], keywords: tuple[str, ...]) -> float | None:
    values: list[float] = []
    for text in texts:
        values.extend(amount_mentions_yi(text, keywords, keyword_before_only=True))
    return max(values, key=abs) if values else None


def _rendered_money_yi(value: float) -> float | None:
    values = amount_mentions_yi(money_text(value))
    return values[0] if values else None


def money_scale_consistency_issues(data: ReportData, fin: dict[str, float], focus: str, bg_points: list[str]) -> list[str]:
    """Catch unit-scale drift between renderer-generated money and headline copy.

    The card renderer formats Card 1/Card 3 amounts from finance() + money_text().
    P12 reconciles card_slots.json, but those generated amounts are not in slots.
    Compare them against top-of-report revenue/profit mentions in slots/HTML so
    a unit bug like 1720.5亿元 becoming 1.7亿元 fails before export.
    """
    headline_texts = [focus, *data.summary[:2], *data.highlights[:3], *bg_points[:2]]
    checks = [
        ("revenue", "revenue", fin.get("revenue"), ("营业总收入", "总收入", "营收", "收入", "revenue")),
        ("net income", "net_income", fin.get("net"), ("归母净利润", "净利润", "net income")),
    ]
    issues: list[str] = []
    for label, field, value, keywords in checks:
        if value is None:
            continue
        rendered = _rendered_money_yi(float(value))
        stated = _largest_headline_amount_yi(headline_texts, keywords)
        if rendered is None or stated is None:
            continue
        rel = abs(rendered - stated) / max(abs(rendered), abs(stated), 1e-9)
        if rel > 0.05:
            issues.append(
                f"Money scale mismatch for {label}: renderer will show {money_text(float(value))} "
                f"from financial_data.{field}, but headline copy/HTML implies about {stated:g} 亿元. "
                "Check financial_data.income_statement.unit and amount scale before rendering cards."
            )
    return issues


def pct_text(value: Any, signed: bool = False) -> str:
    if value is None or value == "":
        return "--"
    num = float(value)
    if signed:
        return f"{num:+.1f}%"
    return f"{num:.1f}%"


def bn_to_yi(value: float) -> str:
    return f"{value * 10:.1f} 亿"


def clean_segment_name(name: str) -> str:
    name = re.sub(r"（.*?）", "", clean(name)).strip()
    replacements = {
        "Productivity and Business Processes": "生产力与业务流程",
        "Intelligent Cloud": "智能云",
        "More Personal Computing": "个人计算",
        "North America": "北美",
        "International": "国际",
    }
    return replacements.get(name, name)


def all_text(data: ReportData) -> str:
    items = [
        data.company_cn,
        data.company_en,
        data.thesis,
        " ".join(data.summary),
        " ".join(data.highlights),
        " ".join(data.risks),
        get_nested(data.financial_analysis, "executive_summary", default="") or "",
        get_nested(data.financial_analysis, "investment_thesis_short", default="") or "",
        get_nested(data.porter_analysis, "company_level", default="") or "",
        get_nested(data.porter_analysis, "industry_level", default="") or "",
        get_nested(data.porter_analysis, "forward_looking", default="") or "",
    ]
    return " ".join(clean(str(item)) for item in items if item is not None)


def strip_voice_shell(text: str) -> str:
    text = clean(text)
    for prefix in (
        "说白了，",
        "说白了",
        "别只看，",
        "别只看",
        "别看，",
        "别看",
        "本质上，",
        "本质上",
        "眼下，",
        "眼下",
        "先别看，",
        "先别看",
        "真要看的是：",
        "真要看的是",
        "后面真要看的是：",
        "后面真要看的是",
    ):
        if text.startswith(prefix):
            return clean(text[len(prefix):].lstrip("，,:： "))
    return text


def audit_source_terms(data: ReportData) -> list[str]:
    texts = dedupe_texts(
        [
            data.company_cn,
            data.company_en,
            data.ticker,
            data.thesis,
            *data.summary,
            *data.highlights,
            *data.risks,
            *porter_section_texts(data, "company"),
            *porter_section_texts(data, "industry"),
            *porter_section_texts(data, "forward"),
            *executive_texts(data),
            *trend_texts(data),
            *[clean_segment_name(seg.get("name", "")) for seg in segment_data(data)],
        ]
    )
    terms: list[str] = []
    seen: set[str] = set()
    blob = " ".join(texts)
    for token in re.findall(r"[A-Za-z][A-Za-z0-9.+/%-]{2,}", blob):
        key = token.lower()
        if key in AUDIT_COMMON_EN_TERMS or key in seen:
            continue
        seen.add(key)
        terms.append(token)
    for token in re.findall(r"[\u4e00-\u9fff]{2,8}", blob):
        if token in AUDIT_COMMON_CN_TERMS or token in seen:
            continue
        seen.add(token)
        terms.append(token)
    return sorted(terms, key=len, reverse=True)


def has_source_anchor(text: str, data: ReportData, source_terms: list[str] | None = None) -> bool:
    core = strip_voice_shell(text)
    if not core:
        return False
    if re.search(r"\d", core):
        return True
    if company_short_cn(data) in core or data.company_en in core or data.ticker in core:
        return True
    for term in source_terms or audit_source_terms(data):
        if term and term in core:
            return True
    return False


def operational_metric(data: ReportData) -> tuple[str, str, str]:
    kpis = operational_kpis(data)
    if "dap_billion" in kpis:
        return ("DAP", bn_to_yi(float(kpis["dap_billion"])), GREEN)
    if "mau_billion" in kpis:
        return ("MAU", bn_to_yi(float(kpis["mau_billion"])), GREEN)
    if "dau_million" in kpis:
        return ("DAU", f"{float(kpis['dau_million']):.0f} 百万", GREEN)
    if "subscribers_million" in kpis:
        return ("订阅用户", f"{float(kpis['subscribers_million']):.0f} 百万", GREEN)
    ocf = cash_flow(data).get("operating_cash_flow")
    if ocf:
        return ("经营现金流", money_text(float(ocf)), GREEN)
    net_margin = profitability(data).get("net_margin_pct")
    return ("净利率", pct_text(net_margin), GREEN)


def company_theme(data: ReportData) -> str:
    text = all_text(data).lower()
    sector = str(get_nested(data.financial_data, "sector", default="")).lower()
    currency = str(get_nested(data.financial_data, "currency", default="USD")).upper()
    if any(token in text for token in ("制药", "药企", "药物", "肥胖", "糖尿病", "临床", "管线", "mounjaro", "zepbound", "verzenio")) or "healthcare" in sector:
        return "pharma"
    # Chinese domestic + cross-border e-commerce (PDD/Temu model): RMB-reporting, no AWS
    if currency in ("RMB", "CNY") and any(token in text for token in ("拼多多", "temu", "跨境", "低价", "拼团")) and "aws" not in text:
        return "cn_ecom"
    if any(token in text for token in ("aws", "电商", "零售", "第三方卖家", "履约", "物流", "综合零售", "云服务", "prime", "亚马逊")) or any(
        token in sector for token in ("综合零售", "云服务", "非必需消费")
    ):
        return "ecom_cloud"
    if any(token in text for token in ("广告", "reels", "family of apps", "社交", "互动媒体")):
        return "ads_ai"
    if any(token in text for token in ("电动车", "robotaxi", "fsd", "储能", "汽车")):
        return "ev_ai"
    if any(token in text for token in ("订阅", "saas", "软件", "云", "license")):
        return "software"
    return "general"


def segment_sentence(data: ReportData) -> str:
    segments = segment_data(data)
    if len(segments) >= 2:
        seg1, seg2 = segments[0], segments[1]
        theme = company_theme(data)
        seg1_name = clean_segment_name(seg1.get("name", "主业务"))
        seg2_name = clean_segment_name(seg2.get("name", "次业务"))
        follow_up = {
            "ecom_cloud": f"{seg1_name}还是最大收入底盘，{seg2_name}体现了集团利润结构的分层",
            "cn_ecom": f"{seg1_name}和{seg2_name}双轮驱动，平台货币化结构比以前更均衡",
            "pharma": f"{seg1_name}和{seg2_name}说明增长不只靠单一大单品",
            "software": f"{seg1_name}和{seg2_name}说明收入结构并不单一",
            "ads_ai": f"{seg1_name}和{seg2_name}说明主平台之外还有新的增长抓手",
            "ev_ai": f"{seg1_name}和{seg2_name}说明报表已经不只靠单一业务在扛",
            "general": f"{seg1_name}和{seg2_name}说明收入重心与投入方向已经拉开",
        }[theme]
        return ensure_terminal_punct(
            f"{seg1_name} {segment_revenue_bn(seg1) * 10:.1f} 亿{_CURRENCY_LABEL}，"
            f"{seg2_name} {segment_revenue_bn(seg2) * 10:.1f} 亿{_CURRENCY_LABEL}，{follow_up}"
        )
    label, value, _ = operational_metric(data)
    return ensure_terminal_punct(f"{label}{value}，说明这门生意的底盘还在")


def segment_fact_line(data: ReportData) -> str:
    segments = segment_data(data)
    if len(segments) >= 2:
        seg1, seg2 = segments[0], segments[1]
        seg1_name = clean_segment_name(seg1.get("name", "主业务"))
        seg2_name = clean_segment_name(seg2.get("name", "次业务"))
        return ensure_terminal_punct(
            f"{seg1_name} {segment_revenue_bn(seg1) * 10:.1f} 亿{_CURRENCY_LABEL}，"
            f"{seg2_name} {segment_revenue_bn(seg2) * 10:.1f} 亿{_CURRENCY_LABEL}"
        )
    if len(segments) == 1:
        seg = segments[0]
        seg_name = clean_segment_name(seg.get("name", "主业务"))
        pct = seg.get("pct_of_total")
        pct_part = f"，收入占比约{float(pct):.1f}%" if pct is not None else ""
        return ensure_terminal_punct(f"{seg_name} {segment_revenue_bn(seg) * 10:.1f} 亿{_CURRENCY_LABEL}{pct_part}")
    return ""


def cover_intro(data: ReportData) -> str:
    if data.card_slots and data.card_slots.intro_sentence:
        return clean(data.card_slots.intro_sentence)
    theme = company_theme(data)
    label, value, _ = operational_metric(data)
    source_candidates = source_copy_candidates(
        executive_texts(data) + summary_texts(data) + highlight_texts(data),
        44,
        opener="说白了，",
        sentence_options=(1,),
        human=True,
    )
    candidates = {
        "ecom_cloud": [
            "说白了，市场现在盯的不是亚马逊还能不能卖货，而是 AWS、广告和履约效率能不能一起把利润率继续抬上去",
            "别看营收盘子已经很大，真正决定估值的，还是云业务、广告和零售效率能不能一起撑住利润弹性",
        ],
        "pharma": [
            "说白了，市场现在盯的不是礼来药卖得好不好，而是减重和糖尿病这条大单品曲线能不能继续往上冲，同时把产能和竞争都扛住",
            "别看礼来现在增长很猛，真正决定估值的，是爆款药能不能继续放量，产能瓶颈会不会先拖住收入",
        ],
        "ads_ai": [
            f"说白了，市场现在盯的不是广告还赚不赚钱，而是 {label}{value} 这台流量机器能不能一边印钱，一边把 AI 账单扛住",
            f"别看钱还在进，真正决定估值的，是 AI 投入多久能换回更高广告回报",
        ],
        "ev_ai": [
            "说白了，车还是基本盘，市场真正下注的是软件、储能和自动驾驶能不能兑现",
            "别看卖车还在卷，真正能抬估值的，是高毛利新业务跑得有多快",
        ],
        "software": [
            "说白了，市场盯的不是功能多不多，而是留存、提价和利润兑现能不能一起走",
            "别看故事讲得热闹，真正值钱的是客户续费和现金流是不是还在抬",
        ],
        "general": [
            "说白了，市场现在看的不是故事够不够大，而是增长和兑现能不能同时成立",
            "别看生意还在扩，真正决定估值的，是新投入多久能变成真钱",
        ],
    }
    return fit_copy(source_candidates + candidates.get(theme, candidates["general"]), 44, human=True)


def company_focus_paragraph(data: ReportData) -> str:
    if data.card_slots and data.card_slots.company_focus_paragraph:
        return clean(data.card_slots.company_focus_paragraph)
    theme = company_theme(data)
    fin = finance(data)
    label, value, _ = operational_metric(data)
    focus_texts = executive_texts(data) + summary_texts(data) + highlight_texts(data)
    source_candidates = source_copy_candidates(
        focus_texts + combined_source_texts(focus_texts, max_parts=2),
        LIMIT_CARD1_FOCUS_CHARS,
        opener="说白了，",
        sentence_options=(2, 3),
        human=True,
    )
    dense_candidate = dense_source_paragraph(focus_texts, LIMIT_CARD1_FOCUS_CHARS, opener="说白了，", max_sentences=3)
    candidates = {
        "cn_ecom": [
            f"说白了，这家公司眼下拼的不是故事大不大，而是拼多多国内低价流量和 Temu 全球扩张两条腿能不能同时走稳。{fiscal_year(data)} 营收 {money_text(fin['revenue'])}，自由现金流超千亿，说明平台变现能力扎实；但盈利重心已从高增速切换成全球化兑现，关税扰动和国内竞争都在压利润率，企稳节奏是市场核心观察点。",
            f"别只看国内基本盘，市场真正想看的是 Temu 跨境扩张能不能在关税压力下找到可持续的盈利节奏。{fiscal_year(data)} 营收 {money_text(fin['revenue'])}，现金头寸超四千亿，说明主平台现金创造没掉链子；但增长叙事已切换成全球化兑现，补贴和履约成本对利润率的压制能否收窄，是估值修复的关键前提。",
        ],
        "ecom_cloud": [
            f"说白了，这家公司现在拼的不是收入还能不能长，而是高毛利的 AWS、广告和第三方卖家服务，能不能把庞大的零售底盘真正变成更厚的利润池。{fiscal_year(data)} 营收 {money_text(fin['revenue'])}，{label}{value} 说明现金还在往里进，但只要云增速、履约效率或资本开支节奏一变，市场就会立刻重算它的利润弹性和估值。",
            f"别看亚马逊什么都在做，市场真正盯的还是三件事：AWS 增速能不能继续抬、广告和卖家服务能不能继续放大利润、零售网络是不是还在变得更高效。{fiscal_year(data)} 营收 {money_text(fin['revenue'])} 说明基本盘够大，但估值能不能再往上走，还是要看高利润业务能不能把整个集团带得更轻。",
        ],
        "pharma": [
            f"说白了，这门生意现在拼的不是药卖不卖得动，而是爆款能不能持续放量、产能能不能跟上、下一批管线能不能顺利接棒。{fiscal_year(data)} 营收 {money_text(fin['revenue'])}，{label}{value} 说明现金还在往里流，但只要供应、医保定价或竞争格局一有变化，市场就会立刻重算它的增速和估值。",
            f"别看礼来现在像在一路狂奔，市场真正盯的还是三件事：减重药供给够不够、糖尿病药渗透还能不能继续抬、后面新适应症能不能接上。{fiscal_year(data)} 营收 {money_text(fin['revenue'])} 说明基本盘已经做大，但高增长能跑多久，才是决定估值能站多高的核心。真要是哪条线先松一下，市场给它的高溢价也会跟着一起回吐。",
        ],
        "ads_ai": [
            f"说白了，这还是一台会印钱的广告机器，但 AI 基建也是真烧钱。{fiscal_year(data)} 营收 {money_text(fin['revenue'])}，{label}{value} 说明流量盘子没塌，广告引擎也没熄火。市场真正在算的，是这笔大投入多久能换回更高变现，别最后收入涨了，利润却先被账单吃掉。",
            f"别看 Meta 还在赚钱，资本市场现在更关心的是两件事：广告效率能不能继续抬，AI 投入多久能开始回本。{label}{value} 说明底盘还稳，但账单已经越来越大，后面要看的不是能不能投，而是投完之后利润能不能接得上。",
        ],
        "ev_ai": [
            f"说白了，车还是报表基本盘，软件和储能才是估值想象力。{fiscal_year(data)} 营收 {money_text(fin['revenue'])}，{label}{value} 说明新业务已经开始有存在感。市场接下来盯的，不是故事新不新，而是兑现快不快，毕竟高毛利业务一天不接棒，估值就一天站不稳。",
            "别看车卖得还是最多，真正抬估值的已经不是交付量，而是软件订阅、储能扩张和自动驾驶进展。眼前看现金流，中期看新业务兑现，谁先把新利润池做出来，谁的故事才更值钱。",
        ],
        "software": [
            f"说白了，这门生意现在不缺收入，缺的是让市场相信高增长和高利润能一起跑。{label}{value} 说明底盘还在，提价、续费和费用控制也都得继续兑现，不然收入看着热闹，利润表先发虚，估值也会跟着掉价。真正拉开差距的，不是谁功能更多，而是谁能把生态绑定和现金流一起守住。",
            f"别看业务线铺得很开，市场真正盯的还是两件事：客户愿不愿继续续费，云和 AI 能不能把更多现金流留在表里。{label}{value} 说明底盘还稳，但要是提价和扩张接不上，故事再大也会被打回现实，市场也不会一直替它买单。真到景气转弱时，先掉的往往不是收入，而是市场给它的溢价。",
        ],
        "general": [
            f"说白了，这家公司眼下不只是拼增长，更是在拼兑现速度。{fiscal_year(data)} 营收 {money_text(fin['revenue'])}，{label}{value} 说明基本盘还稳。市场接下来盯的，是新投入能不能换回更高回报，别最后规模做大了，利润却被摊薄。",
            "别看表面数据还行，真正让估值有弹性的，是主业守住基本盘的同时，新故事能不能尽快变成真钱。只有增长和兑现能一起跑，市场才会愿意继续给耐心。",
        ],
    }
    return fit_copy([dense_candidate] + source_candidates + candidates.get(theme, candidates["general"]), LIMIT_CARD1_FOCUS_CHARS, human=True)


def industry_paragraph(data: ReportData) -> str:
    if data.card_slots and data.card_slots.industry_paragraph:
        return clean(data.card_slots.industry_paragraph)
    theme = company_theme(data)
    industry_texts = porter_section_texts(data, "industry") + porter_section_texts(data, "company") + porter_section_texts(data, "forward")
    source_candidates = source_copy_candidates(
        industry_texts + combined_source_texts(industry_texts, max_parts=2),
        LIMIT_CARD2_INDUSTRY_CHARS,
        sentence_options=(2, 3),
    )
    dense_candidate = dense_source_paragraph(industry_texts, LIMIT_CARD2_INDUSTRY_CHARS, max_sentences=4)
    candidates = {
        "cn_ecom": [
            "中国综合电商与全球低价跨境平台的核心竞争，从来不只是谁价格更低，而是谁能把价格低的同时还守住商家 ROI 和平台自身利润。流量入口分散、消费者比价成本趋近于零，决定了平台必须持续用效率换留存。谁能把供给质量、履约速度和广告变现串成飞轮，谁就更难被替代。",
            "低价电商赛道表面上打的是价格战，骨子里拼的是供给稳定性、算法分发效率和跨境履约能力。中国市场用户高频、价格敏感，海外市场法规风险高、供应链长，两套逻辑都要跑顺，才能真正把平台规模变成持续盈利能力。",
        ],
        "ecom_cloud": [
            "这个行业表面上是零售，骨子里拼的是履约网络、卖家生态、广告变现和云基础设施。规模做大只是门槛，真正拉开差距的是谁能把低毛利交易流量导向更高毛利的云、广告和服务。谁只是卖货不控效率，利润率就很难抬起来。",
            "平台零售和云服务放在一起看，核心不是谁业务多，而是谁能把流量、商家、物流和算力串成一个飞轮。只要云和广告继续抬利润，零售就不只是包袱；反过来一旦履约和 capex 压力上来，估值也会很快被重估。",
        ],
        "pharma": [
            "这个行业表面上卖的是药，骨子里比的是临床数据、产能、渠道和专利壁垒。减重赛道把天花板抬得很高，也把竞争、供给和定价压力一起推了上来。谁能把爆款持续放量、把新适应症做宽，谁就更容易把高估值守住。",
            "创新药赛道不怕需求大，怕的是供给跟不上、专利和竞争提前松动。只要疗效、可及性和产能都在线，市场就愿意给高溢价；反过来一旦放量节奏掉下来，估值回撤通常也会来得很快。",
        ],
        "ads_ai": [
            "这个行业说到底就是抢注意力、拼算法，再把时长换成广告钱。AI 让投放更自动，也把算力和能源成本一起抬上去。头部平台吃肉，后排玩家找缝，真正的分水岭不在有没有流量，而在能不能把流量变成更高 ROI。",
            "互动媒体和在线广告这门生意，表面上看是卖流量，骨子里比的是算法、分发和转化。AI 把效率天花板抬高了，也把成本曲线一起顶上去了。谁能把广告主的钱花得更准，谁就更能在景气波动里守住利润。",
        ],
        "ev_ai": [
            "这个行业表面上在卷价格，骨子里在卷效率、软件和供应链。车企都想抢份额，但真正能把估值拉开的，还是自动驾驶、储能和制造效率。硬件是底座，软件和能源生态才是利润上限，谁只能靠降价，谁就更难守住利润。",
            "新能源车行业现在不是谁更会讲故事，而是谁能把规模、毛利和软件收入一起做出来。硬件越来越像底座，软件越来越像上限，谁能先把高毛利业务做厚，谁就更容易穿越价格战，也更容易让估值站稳。",
        ],
        "software": [
            "这个行业看起来是卖软件，实际上比的是续费、集成深度和提价权。AI 能拉高效率，也会加速同质化，所以最后拼的还是客户黏性、生态位和现金流。谁只是功能堆得多、迁移成本又不够高，谁就会被更便宜的新工具往后挤。",
            "企业软件赛道不怕故事多，怕的是替代成本不够高。只要留存稳、扩张率高、生态绑定深，市场就愿意给耐心；反过来估值掉得也会很快，因为客户一旦松动，利润通常会比收入更早塌下来。",
        ],
        "general": [
            "这个行业表面上在拼增长，实际上在拼谁能把规模、效率和利润一起做出来。上游成本、需求节奏和监管变化，都会直接改写利润率，谁的成本结构更硬，谁就更容易掉队。",
            "这门生意不是谁声音大谁赢，而是谁能把基本盘守住，再把新投入变成回报。景气一好，大家都能讲故事；景气一弱，现金流立刻见真章，市场会先挑最能兑现的公司站队。",
        ],
    }
    result = fit_copy([dense_candidate] + source_candidates + candidates.get(theme, candidates["general"]), LIMIT_CARD2_INDUSTRY_CHARS, human=True)
    if len(result) < 90:
        forward_bits = sentence_chunks(" ".join(porter_section_texts(data, "forward")), 2)
        for bit in forward_bits:
            bit = ensure_terminal_punct(strip_stiff_opener(bit))
            trial = result + bit
            if bit and len(trial) <= LIMIT_CARD2_INDUSTRY_CHARS:
                result = trial
                if len(result) >= 90:
                    break
    return result


def conclusion_block(data: ReportData) -> str:
    if data.card_slots and data.card_slots.conclusion_block:
        return clean(data.card_slots.conclusion_block)
    theme = company_theme(data)
    source_candidates = source_copy_candidates(
        porter_section_texts(data, "forward") + porter_section_texts(data, "company") + executive_texts(data),
        56,
        sentence_options=(1,),
        human=True,
    )
    candidates = {
        "cn_ecom": [
            "主站流量底盘还稳，Temu 全球化是中期变量，市场在等利润率企稳信号",
            "眼前靠国内高频流量扛报表，估值上限要看跨境业务能不能跑出可持续利润",
        ],
        "ecom_cloud": [
            "零售底盘还在转，真正的上限要看 AWS、广告和卖家服务能不能继续放大利润",
            "眼前靠零售和云撑盘子，估值上限还是看高毛利业务能不能继续接棒",
        ],
        "pharma": [
            "爆款药还在放量，真正的问号是产能、竞争和后续管线谁先掉链子",
            "眼前靠重磅药冲收入，估值上限还得看供给和新适应症能不能续上",
        ],
        "ads_ai": [
            "护城河还在，真正的问号是 AI 投入多久能换回更高广告回报",
            "平台没掉队，真正要盯的是 AI 账单何时开始反哺利润",
        ],
        "ev_ai": [
            "主业看现金流，上限看软件、储能和自动驾驶兑现",
            "车卖得再多只是基本盘，估值上限仍要看新业务兑现",
        ],
        "software": [
            "产品能卖不是终点，续费、提价和利润兑现才是关键",
            "真正值钱的不是增速一时多快，而是客户留得有多稳",
        ],
        "general": [
            "基本盘还在，真正的问号是新投入多久能变成真钱",
            "市场不是不给耐心，而是只给能兑现的耐心",
        ],
    }
    return fit_copy(source_candidates + candidates.get(theme, candidates["general"]), 56, human=True)


def judgement_paragraph(data: ReportData) -> str:
    if data.card_slots and data.card_slots.judgement_paragraph:
        return clean(data.card_slots.judgement_paragraph)
    theme = company_theme(data)
    source_candidates = source_copy_candidates(
        executive_texts(data) + porter_section_texts(data, "forward"),
        52,
        opener="说白了，",
        sentence_options=(1,),
        human=True,
    )
    candidates = {
        "cn_ecom": [
            "说白了，眼前看主站利润，估值看 Temu 何时兑现；两条腿走稳，故事才值钱",
            "别看盈利还厚，真正决定估值修复的是 Temu 本地化能不能跑通",
        ],
        "ecom_cloud": [
            "说白了，眼前看 AWS 和零售效率，估值看广告和高毛利服务能不能继续抬",
            "别看营收盘子够大，真正决定估值的还是利润结构能不能继续变轻",
        ],
        "pharma": [
            "说白了，眼前看爆款药放量，估值看产能和新适应症；供给跟得上，故事才值钱",
            "别看收入冲得快，真正决定估值的还是产能兑现和管线接棒",
        ],
        "ads_ai": [
            "说白了，广告还在印钱，AI 账单也在飞；收入扛得住，估值就撑得住",
            "别看利润还厚，市场真正盯的是 AI 投入会不会先把费用顶起来",
        ],
        "ev_ai": [
            "说白了，眼前看卖车，估值看软件和储能；主业稳得住，故事才有人信",
            "别看车还是主角，真正抬估值的要靠高毛利新业务兑现",
        ],
        "software": [
            "说白了，眼前看续费，估值看提价和利润；留存稳，故事才站得住",
            "别看增速还在，真正决定估值的还是客户黏性和现金流",
        ],
        "general": [
            "说白了，眼前看利润，估值看新业务多久兑现；基本盘稳，故事才值钱",
            "别看数据不差，市场真正算的是投入回报而不是口号",
        ],
    }
    return fit_copy(candidates.get(theme, candidates["general"]) + source_candidates, 52, human=True)


def brand_statement(data: ReportData) -> str:
    if data.card_slots and data.card_slots.brand_statement:
        return clean(data.card_slots.brand_statement)
    theme = company_theme(data)
    source_candidates = source_copy_candidates(
        executive_texts(data) + summary_texts(data) + highlight_texts(data),
        34,
        opener="说白了，",
        sentence_options=(1,),
        human=True,
    )
    candidates = {
        "cn_ecom": [
            "说白了，拼多多现在卖的不只是低价，而是供给效率、流量分发和 Temu 全球化的组合拳",
            "别看利润已经很厚，真正值钱的是两个平台能不能在高竞争里守住商家 ROI",
        ],
        "ecom_cloud": [
            "说白了，亚马逊现在卖的不只是货，而是零售底盘、云利润和广告飞轮的叠加",
            "别看盘子已经很大，真正值钱的是高毛利业务能不能继续把集团带轻",
        ],
        "pharma": [
            "说白了，礼来现在卖的不只是药，而是爆款放量、产能兑现和管线接棒的预期",
            "别看收入冲得猛，真正值钱的是爆款药还能跑多久、后面还有没有人接班",
        ],
        "ads_ai": [
            "广告机还在印钱，AI 账单已经追上来了",
            "流量还在变现，AI 投入也在猛踩油门",
        ],
        "ev_ai": [
            "说白了，车还是基本盘，软件和储能才值钱",
            "别看报表靠卖车，估值还是得靠新业务兑现",
        ],
        "software": [
            "说白了，微软现在卖的不只是软件，而是留存、提价和整套生态的黏性",
            "别看收入还在长，真正值钱的是客户不走、价格还能往上抬",
        ],
        "general": [
            f"说白了，{company_short_cn(data)}现在最值钱的，还是主业现金流和新投入兑现速度",
            f"别看故事还在展开，真正决定{company_short_cn(data)}定价的，还是基本盘和回报率",
        ],
    }
    return fit_copy(source_candidates + candidates.get(theme, candidates["general"]), 34, human=True)


def background_points(data: ReportData) -> list[str]:
    if data.card_slots and data.card_slots.background_bullets:
        bullets = [clean(x) for x in data.card_slots.background_bullets if clean(x)]
        return dedupe_texts(bullets, 4)
    fin = finance(data)
    rev_yoy = revenue_yoy(data)
    net_yoy = net_income_yoy(data)
    source_fact = source_copy_candidates(
        summary_texts(data) + highlight_texts(data) + executive_texts(data),
        LIMIT_CARD2_BG_BULLET_CHARS,
        sentence_options=(1,),
    )
    points = [
        fit_copy([f"{fiscal_year(data)} 营收 {money_text(fin['revenue'])}，同比{pct_text(rev_yoy, signed=True)}。"], LIMIT_CARD2_BG_BULLET_CHARS),
        fit_copy([f"净利润 {money_text(fin['net'])}，同比{pct_text(net_yoy, signed=True)}。"], LIMIT_CARD2_BG_BULLET_CHARS),
        fit_copy([segment_fact_line(data) or segment_sentence(data)], LIMIT_CARD2_BG_BULLET_CHARS),
        fit_copy(source_fact, LIMIT_CARD2_BG_BULLET_CHARS),
    ]
    return dedupe_texts(points, 4)


def revenue_explainer_points(data: ReportData) -> list[str]:
    if data.card_slots and data.card_slots.revenue_explainer_points:
        pts = [clean(x) for x in data.card_slots.revenue_explainer_points if clean(x)]
        return dedupe_texts(pts, 3)
    prof = profitability(data)
    narratives = get_nested(data.financial_analysis, "trend_narratives", default={}) or {}
    theme = company_theme(data)
    points = [
        fit_copy([f"毛利率 {pct_text(prof.get('gross_margin_pct'))}，营业利润率 {pct_text(prof.get('operating_margin_pct'))}，利润池依旧不小"], 40),
        fit_copy(
            [
                *source_copy_candidates(trend_texts(data), 54, sentence_options=(1,)),
                narratives.get("fcf", ""),
                "药卖得快，钱也回得快，但产能和投入一样都不能掉链子。",
                "现金流还在，但大额投入已经开始抢利润。",
                "账上的钱还够用，但投入节奏明显比以前猛。",
            ],
            LIMIT_CARD3_EXPLAINER_CHARS,
        ),
        fit_copy(
            {
                "cn_ecom": ["说白了，真正支撑估值的，不只是今天卖出多少货，而是 Temu 能不能跑通盈利模型、主站能不能守住利润率。"],
                "ecom_cloud": ["说白了，真正支撑估值的，不只是今天卖出多少货，而是 AWS、广告和卖家服务能不能把利润率继续往上抬。"],
                "pharma": ["说白了，真正支撑估值的，不只是今天卖了多少药，而是爆款能不能持续放量、后面还有没有新药接棒。"],
                "ads_ai": ["说白了，真正支撑估值的，不是今天赚了多少，而是 AI 投入以后能赚得更多。"],
                "ev_ai": ["说白了，真正支撑估值的，不是多卖几辆车，而是软件和储能能不能放大利润。"],
                "software": ["说白了，真正支撑估值的，不是功能多少，而是留存和提价能不能一起兑现。"],
                "general": ["说白了，真正支撑估值的，不只是今天赚多少钱，而是明天还能不能赚得更快。"],
            }[theme] + source_copy_candidates(executive_texts(data) + porter_section_texts(data, "forward"), 54, opener="说白了，", sentence_options=(1,), human=True),
            LIMIT_CARD3_EXPLAINER_CHARS,
            human=True,
        ),
    ]
    return dedupe_texts(points, 3)


def lead_business_point(data: ReportData) -> str:
    segments = segment_data(data)
    if not segments:
        return ""
    lead = max(segments, key=lambda seg: (seg.get("pct_of_total") or 0, segment_revenue_bn(seg)))
    name = clean_segment_name(lead.get("name", "主业务"))
    revenue_text = f"{segment_revenue_bn(lead) * 10:.1f} 亿{_CURRENCY_LABEL}"
    pct = lead.get("pct_of_total")
    pct_text_part = f"，收入占比约{float(pct):.1f}%" if pct is not None else ""
    theme = company_theme(data)

    if theme == "pharma":
        return fit_copy(
            [f"{name} {revenue_text}{pct_text_part}。"],
            LIMIT_CARD4_NOW_BULLET_CHARS,
        )
    if theme == "ecom_cloud":
        if name in {"北美", "国际"}:
            return fit_copy(
                [f"{name} {revenue_text}{pct_text_part}。"],
                LIMIT_CARD4_NOW_BULLET_CHARS,
            )
        if "云" in name:
            return fit_copy(
                [f"{name} {revenue_text}{pct_text_part}。"],
                LIMIT_CARD4_NOW_BULLET_CHARS,
            )
    if theme == "software":
        return fit_copy(
            [f"{name} {revenue_text}{pct_text_part}。"],
            LIMIT_CARD4_NOW_BULLET_CHARS,
        )
    if theme == "cn_ecom":
        return fit_copy(
            [f"{name} {revenue_text}{pct_text_part}。"],
            LIMIT_CARD4_NOW_BULLET_CHARS,
        )
    return fit_copy(
        [f"{name} {revenue_text}{pct_text_part}，仍是当前第一大产品线。"],
        LIMIT_CARD4_NOW_BULLET_CHARS,
    )


def operating_margin_point(data: ReportData) -> str:
    prof = profitability(data)
    margin = prof.get("operating_margin_pct")
    if margin is None:
        return ""
    prior = prof.get("operating_margin_prior_pct")
    if prior is None:
        return fit_copy([f"营业利润率 {pct_text(margin)}。"], LIMIT_CARD4_NOW_BULLET_CHARS)
    delta = float(margin) - float(prior)
    if abs(delta) < 0.2:
        return fit_copy([f"营业利润率 {pct_text(margin)}，与上年基本持平。"], LIMIT_CARD4_NOW_BULLET_CHARS)
    if delta > 0:
        return fit_copy([f"营业利润率 {pct_text(margin)}，较上年提升约{delta:.1f}个百分点。"], LIMIT_CARD4_NOW_BULLET_CHARS)
    return fit_copy([f"营业利润率 {pct_text(margin)}，较上年回落约{abs(delta):.1f}个百分点。"], LIMIT_CARD4_NOW_BULLET_CHARS)


def cash_flow_point(data: ReportData) -> str:
    cf = cash_flow(data)
    ocf = cf.get("operating_cash_flow")
    capex = cf.get("capex_purchases")
    fcf = cf.get("free_cash_flow")
    trend_candidates = source_copy_candidates(trend_texts(data), LIMIT_CARD4_NOW_BULLET_CHARS, sentence_options=(1,))
    if ocf and capex and fcf is not None:
        return fit_copy(
            [f"经营现金流 {money_text(float(ocf))}，Capex {money_text(float(capex))}，自由现金流 {money_text(float(fcf))}。", *trend_candidates],
            LIMIT_CARD4_NOW_BULLET_CHARS,
        )
    if ocf and capex:
        return fit_copy(
            [f"经营现金流 {money_text(float(ocf))}，Capex {money_text(float(capex))}。", *trend_candidates],
            LIMIT_CARD4_NOW_BULLET_CHARS,
        )
    return ""


def business_now_points(data: ReportData) -> list[str]:
    if data.card_slots and data.card_slots.current_business_points:
        pts = [clean(x) for x in data.card_slots.current_business_points if clean(x)]
        return dedupe_texts(pts, 4)
    points: list[str] = []
    lead_point = lead_business_point(data)
    if lead_point:
        points.append(lead_point)
    kpis = operational_kpis(data)
    if "dap_billion" in kpis:
        points.append(fit_copy([f"DAP {bn_to_yi(float(kpis['dap_billion']))}，流量底盘和分发效率都还在线，广告机器没有掉链子。"], LIMIT_CARD4_NOW_BULLET_CHARS))
    elif "ad_impressions_yoy_pct" in kpis:
        points.append(fit_copy([f"广告展示量同比{pct_text(kpis['ad_impressions_yoy_pct'], signed=True)}，平台活跃度还在往上走，用户时长也还撑得住。"], LIMIT_CARD4_NOW_BULLET_CHARS))
    margin_point = operating_margin_point(data)
    if margin_point:
        points.append(margin_point)
    cf_point = cash_flow_point(data)
    if cf_point:
        points.append(cf_point)
    now_texts = highlight_texts(data) + summary_texts(data) + executive_texts(data) + trend_texts(data)
    points.extend(
        fit_copy([text], LIMIT_CARD4_NOW_BULLET_CHARS)
        for text in source_copy_candidates(
            now_texts + combined_source_texts(now_texts, max_parts=2),
            LIMIT_CARD4_NOW_BULLET_CHARS,
            sentence_options=(1, 2),
        )
    )
    dense = dedupe_texts(points, 4)
    return dense


def future_watch_points(data: ReportData) -> list[str]:
    if data.card_slots and data.card_slots.future_watch_points:
        pts = [clean(x) for x in data.card_slots.future_watch_points if clean(x)]
        return dedupe_texts(pts, 4)
    theme = company_theme(data)
    points: list[str] = [
        fit_copy([text], LIMIT_CARD4_FUTURE_BULLET_CHARS)
        for text in source_copy_candidates(
            risk_texts(data) + porter_section_texts(data, "forward") + executive_texts(data) + summary_texts(data)[-1:],
            LIMIT_CARD4_FUTURE_BULLET_CHARS,
            sentence_options=(1,),
        )
    ]
    theme_points = {
        "cn_ecom": [
            "别只看收入增速，更要看 Temu 本地化后利润率能不能回升，不然全球化是在拿利润换规模。",
            "关税政策扰动是短期变量，但若持续收紧，Temu 的价格优势会被履约成本逐步对冲。",
            "阿里、京东、抖音持续加码补贴，国内平台 take rate 和广告效率是下一步核心分水岭。",
            "市场给低估值说明增长叙事已打折；一旦 Temu 利润开始兑现，重估空间仍然存在。",
        ],
        "ecom_cloud": [
            "别只看收入，更要看 AWS、广告和履约效率能不能一起守住，不然利润弹性很容易被成本吃掉。",
            "云服务和广告是估值锚，但零售网络、劳资和物流投入提醒市场，这门生意并不轻。",
            "高毛利业务继续提占比，市场就愿意给耐心；一旦云增速回落、capex 再抬，估值会很快被压缩。",
            "眼下大家买的是飞轮越转越顺，不是单看卖货规模；谁能把规模变成更厚利润，谁就更值钱。",
        ],
        "pharma": [
            "别只看销量，更要看产能爬坡、医保覆盖和竞品节奏能不能一起扛住，不然高增长很容易先撞到供给天花板。",
            "减重赛道够大，但越是高景气，市场越会盯供给、定价和长期安全性这些硬问题。",
            "新适应症一旦持续放量，估值天花板还会被往上抬；但只要临床或供给节奏一慢，市场也会立刻重估。",
            "眼下大家买的是爆款延续性和管线接棒，一旦这两条线松动，回撤通常不会太温和。",
        ],
        "ads_ai": [
            "别只看广告景气，更要看 AI 投入能不能换回更高 ROI，不然账单会先把利润吃薄。",
            "算力、电力和数据中心是硬约束，费用率短期还会紧，资本开支也未必马上降温。",
            "监管一收紧，广告定向和产品节奏都可能被打断，产品迭代会直接被拖慢。",
            "收入继续快跑，市场就夸它敢投；增速一掉，估值先挨打，情绪切得会非常快。",
        ],
        "ev_ai": [
            "别只看交付量，更要看软件付费和储能扩张能不能继续兑现，利润池能不能真正换挡。",
            "价格战如果拉太久，硬件利润会先被挤薄，现金流修复也会往后拖。",
            "自动驾驶一旦兑现，估值天花板会被重新打开，但市场不会无限等。",
            "市场现在买的是未来，兑现节奏一慢，回撤也会很快，故事反噬会比想象中更狠。",
        ],
        "software": [
            "别只看新单，更要看续费、扩张率和提价能不能一起守住，单靠签单堆不出好估值。",
            "AI 会拉高效率，也会加速同质化，护城河得靠客户黏性守，不能只靠新功能。",
            "宏观一转弱，预算和回款节奏会先传到报表里，利润弹性往往比收入更早变脸。",
            "增速守得住，估值就稳；留存一松，市场会立刻砍价，而且一点都不会客气。",
        ],
        "general": [
            "别只看收入，更要看新投入多久能变成真钱，不然规模越大反而越容易被质疑。",
            "上游成本、需求节奏和监管变化，都会先打到利润率，报表会比故事更早翻脸。",
            "故事讲得再大，兑现一慢，市场就会先收估值，而且通常不会给第二次解释机会。",
            "基本盘守得住，市场才愿意继续为远期叙事买单，不然耐心会掉得很快。",
        ],
    }
    points.extend(fit_copy([item], LIMIT_CARD4_FUTURE_BULLET_CHARS, human=("别看" in item or "夸它敢投" in item)) for item in theme_points[theme])
    return dedupe_texts(points, 4)


def brand_summary_points(data: ReportData) -> list[str]:
    if data.card_slots and data.card_slots.memory_points:
        pts = [clean(x) for x in data.card_slots.memory_points if clean(x)]
        return dedupe_texts(pts, 3)
    rev_yoy = revenue_yoy(data)
    points = [
        fit_copy([f"收入同比{pct_text(rev_yoy, signed=True)}，基本盘还稳。"], 24),
        fit_copy([brand_statement(data)], 24, human=True),
        fit_copy([future_watch_points(data)[0]], 28, human=True),
    ]
    return dedupe_texts(points, 3)


def watch_sentence(data: ReportData) -> str:
    right = future_watch_points(data)
    return right[0] if right else judgement_paragraph(data)


def post_title(data: ReportData) -> str:
    if data.card_slots and data.card_slots.post_title:
        return clean(data.card_slots.post_title)
    return f"{POST_TITLE_PREFIX}{company_short_cn(data)}"


def post_content_lines(data: ReportData) -> list[str]:
    if data.card_slots and data.card_slots.post_content_lines:
        lines = [clean(x) for x in data.card_slots.post_content_lines if clean(x)]
        return dedupe_texts(lines, 4)
    fin = finance(data)
    rev_yoy = revenue_yoy(data)
    label, value, _ = operational_metric(data)
    watch = clean(watch_sentence(data)).rstrip("。！？!?")
    lines = [
        fit_copy([brand_statement(data)], 42, human=True),
        fit_copy([f"{fiscal_year(data)} 营收 {money_text(fin['revenue'])}，同比{pct_text(rev_yoy, signed=True)}，钱还在进。"], 44),
        fit_copy([f"{label} {value}，这就是它眼下最值得盯的经营抓手。"], 44, human=True),
        fit_copy([f"后面真要看的是：{watch}？"], 44, human=True),
    ]
    return dedupe_texts(lines, 4)


def keyword_tags(data: ReportData) -> list[str]:
    text = all_text(data)
    tags: list[str] = [hashtag_token(company_short_cn(data))]
    if data.ticker:
        tags.append(hashtag_token(data.ticker))
    sector = str(get_nested(data.financial_data, "sector", default=""))
    if "通信" in sector or "广告" in text:
        tags.append("#数字广告")
    if "社交" in text:
        tags.append("#社交平台")
    if "AI" in text or "人工智能" in text:
        tags.append("#AI")
    if "云" in text:
        tags.append("#云计算")
    if "电动车" in text:
        tags.append("#电动车")
    tags.extend(["#商业模式", "#上市公司", "#金融豹"])
    return normalize_post_tags(tags)


def normalize_post_tags(raw_tags: list[Any]) -> list[str]:
    tags: list[str] = []
    seen: set[str] = set()
    base_limit = max(0, MAX_POST_TAGS - len(REQUIRED_POST_TAGS))
    required = set(REQUIRED_POST_TAGS)
    for raw in raw_tags:
        if not clean(str(raw)):
            continue
        token = hashtag_token(str(raw).lstrip("#"))
        if not token or token in seen or token in required:
            continue
        tags.append(token)
        seen.add(token)
        if len(tags) >= base_limit:
            break
    for token in REQUIRED_POST_TAGS:
        if token not in seen:
            tags.append(token)
            seen.add(token)
    return tags[:MAX_POST_TAGS]


def post_hashtags(data: ReportData) -> str:
    if data.card_slots and data.card_slots.hashtags:
        return " ".join(normalize_post_tags(data.card_slots.hashtags))
    return " ".join(keyword_tags(data))


def measure_block(
    draw: ImageDraw.ImageDraw,
    text: str,
    width: int,
    font_obj: ImageFont.FreeTypeFont,
    line_gap: int,
    max_lines: int | None = None,
) -> int:
    lines = wrap(draw, clean(text), font_obj, width)
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
    if not lines:
        return 0
    total = 0
    for i, line in enumerate(lines):
        total += line_raster_height(draw, font_obj, line)
        if i < len(lines) - 1:
            total += line_gap
    return total


def measure_bullets(
    draw: ImageDraw.ImageDraw,
    items: list[str],
    width: int,
    font_obj: ImageFont.FreeTypeFont,
    line_gap: int,
    gap_after: int,
    max_lines_per_item: int | None = None,
) -> int:
    total = 0
    for item in items:
        total += measure_block(draw, item, width - 24, font_obj, line_gap, max_lines=max_lines_per_item)
        total += gap_after
    return total


def wrapped_block_height(lines: list[str], font_obj: ImageFont.FreeTypeFont, line_gap: int) -> int:
    if not lines:
        return 0
    return len(lines) * font_obj.size + max(0, len(lines) - 1) * line_gap


def raster_text_block_height(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    font_obj: ImageFont.FreeTypeFont,
    line_gap: int,
) -> int:
    """Total pixel height of stacked lines as rendered by block(); must match vertical advance."""
    if not lines:
        return 0
    total = 0
    for i, line in enumerate(lines):
        total += line_raster_height(draw, font_obj, line)
        if i < len(lines) - 1:
            total += line_gap
    return total


def block_final_y(
    draw: ImageDraw.ImageDraw,
    text: str,
    y: int,
    width: int,
    font_obj: ImageFont.FreeTypeFont,
    line_gap: int,
    max_lines: int | None,
) -> int:
    """Same vertical advance as block() return y, without drawing (for layout validation)."""
    lines = wrap(draw, clean(text), font_obj, width)
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
    for i, line in enumerate(lines):
        y += line_raster_height(draw, font_obj, line)
        if i < len(lines) - 1:
            y += line_gap
    return y


def fit_block_font(
    draw: ImageDraw.ImageDraw,
    text: str,
    width: int,
    max_height: int,
    *,
    start_size: int,
    min_size: int,
    line_gap: int,
    max_lines: int | None = None,
    bold: bool = False,
) -> ImageFont.FreeTypeFont:
    for size in range(start_size, min_size - 1, -1):
        font_obj = f(size, bold)
        lines = wrap(draw, clean(text), font_obj, width)
        if max_lines is not None and len(lines) > max_lines:
            lines = lines[:max_lines]
        if raster_text_block_height(draw, lines, font_obj, line_gap) <= max_height:
            return font_obj
    return f(min_size, bold)


def generated_copy_slots(data: ReportData) -> dict[str, list[str]]:
    return {
        "Card 1 intro sentence": [cover_intro(data)],
        "Card 1 company-focus paragraph": [company_focus_paragraph(data)],
        "Card 2 background bullets": background_points(data),
        "Card 2 industry paragraph": [industry_paragraph(data)],
        "Card 2 conclusion": [conclusion_block(data)],
        "Card 3 explainer bullets": revenue_explainer_points(data),
        "Card 4 left column": business_now_points(data),
        "Card 4 right column": future_watch_points(data),
        "Card 4 judgement paragraph": [judgement_paragraph(data)],
        "Card 5 main statement": [brand_statement(data)],
        "Card 5 summary bullets": brand_summary_points(data),
        "Card 6 content lines": post_content_lines(data),
    }


def hardcode_logic_issues(data: ReportData) -> list[str]:
    issues: list[str] = []
    slots = generated_copy_slots(data)
    source_blob = all_text(data)
    source_terms = audit_source_terms(data)
    all_generated = "\n".join(text for items in slots.values() for text in items)

    for label, items in slots.items():
        for text in items:
            normalized = clean(text)
            for marker in FORBIDDEN_GENERATED_MARKERS:
                if marker in normalized:
                    issues.append(f"{label} contains rating/disclaimer boilerplate that must not appear in cards: {marker}")
            for phrase in FORBIDDEN_TEMPLATE_PHRASES:
                if phrase in normalized:
                    issues.append(f"{label} still contains forbidden hardcoded template wording: {phrase}")
            for marker in CROSS_REPORT_NAME_MARKERS:
                if marker in normalized and marker not in source_blob and marker not in data.company_cn and marker not in data.company_en and marker not in company_short_cn(data):
                    issues.append(f"{label} contains cross-report residue not found in this report package: {marker}")
            if (
                data.card_slots is None
                and label != "Card 2 background bullets"
                and not has_source_anchor(normalized, data, source_terms)
            ):
                issues.append(f"{label} looks like generic template copy without company-specific anchors: {normalized}")

    rev_yoy = revenue_yoy(data)
    net_yoy = net_income_yoy(data)
    if rev_yoy is not None and net_yoy is not None:
        if float(net_yoy) >= float(rev_yoy) + 15:
            for phrase in ("利润节奏暂时没跟上收入", "利润没跟上收入", "利润弱于收入"):
                if phrase in all_generated:
                    issues.append("Generated copy contradicts the facts: net-income growth is faster than revenue growth, so it cannot say profit lagged revenue.")
        if float(net_yoy) <= float(rev_yoy) - 10:
            for phrase in ("利润弹性明显快于收入增速", "利润快于收入", "利润跑得比收入更快"):
                if phrase in all_generated:
                    issues.append("Generated copy contradicts the facts: net-income growth trails revenue growth, so it cannot say profit outpaced revenue.")

    if len(segment_data(data)) < 2 and "双轮驱动" in all_generated:
        issues.append("Generated copy claims a two-engine business mix, but the normalized segment data does not support that framing.")

    return dedupe_texts(issues)


def validate_report(data: ReportData, brand: str, *, allow_no_logo: bool = False) -> None:
    img = Image.new("RGB", (W, H), BG)
    draw = ScaledDraw(ImageDraw.Draw(img), LAYOUT_SCALE)
    issues: list[str] = []
    if data.card_slots and data.card_slots.porter_scores is not None and len(data.card_slots.porter_scores) != 5:
        issues.append("When card_slots.porter_scores is set, it must contain exactly five integers.")
    logo_path_raw = (data.card_slots.logo_asset_path or "").strip() if data.card_slots else ""
    if logo_path_raw:
        logo_name = Path(logo_path_raw).name.lower()
        if any(marker in logo_name for marker in ("screenshot", "screencapture", "screen-capture", "captureui")):
            issues.append("card_slots.logo_asset_path must not point to a screenshot or screen capture.")
        logo_path = find_logo_asset(data)
        if not logo_path:
            issues.append("card_slots.logo_asset_path is set, but the logo file was not found or is not a supported image type.")
        else:
            issues.extend(logo_asset_dimension_issues(logo_path))
    else:
        if allow_no_logo:
            print(
                "WARNING: card_slots.logo_asset_path is not set — Card 1 will render without a logo "
                "(export used --allow-no-logo; use only when the customer explicitly waived the logo).",
                file=sys.stderr,
            )
        else:
            issues.append(
                "P0/logo: `card_slots.logo_asset_path` is empty. Run the logo production agent, "
                "save a ≥840px-wide transparent wordmark beside the report, set `logo_asset_path` and "
                "`cover_company_name_cn`, then validate again. If the customer explicitly waives the logo, "
                "re-run validation/export with `--allow-no-logo`."
            )
    issues.extend(hardcode_logic_issues(data))

    focus = company_focus_paragraph(data)
    intro = cover_intro(data)
    bg_points = background_points(data)
    industry = industry_paragraph(data)
    left = business_now_points(data)
    right = future_watch_points(data)
    brand_points = brand_summary_points(data)
    brand_line = brand_statement(data)
    title = post_title(data)
    lines = post_content_lines(data)
    tags = post_hashtags(data)
    fin = finance(data)
    prof = profitability(data)
    current_income = income_current(data)
    source_revenue = as_float(current_income.get("revenue"))
    source_net = as_float(current_income.get("net_income"))
    issues.extend(money_scale_consistency_issues(data, fin, focus, bg_points))

    # Card 3 hard gate: do not allow empty numeric fields/placeholder output ("--").
    required_fin = [
        ("revenue", "revenue", "Card 3 revenue"),
        ("cogs", "cogs", "Card 3 cogs"),
        ("gross_profit", "gross", "Card 3 gross profit"),
        ("operating_income", "op", "Card 3 operating profit"),
        ("net_income", "net", "Card 3 net income"),
    ]
    for source_key, fin_key, label in required_fin:
        source_value = as_float(current_income.get(source_key))
        rendered_value = as_float(fin.get(fin_key))
        if source_value is None and (rendered_value is None or abs(rendered_value) < 1e-9):
            issues.append(
                f"{label} is missing from both financial_data and Sankey fallback. "
                "Card output may not contain empty numeric placeholders."
            )

    # Zero-revenue guard: revenue=0 is a data error (missing extraction), not a valid company state.
    if source_revenue is not None and abs(source_revenue) < 1e-9:
        issues.append(
            "Card 3: financial_data.income_statement.current_year.revenue is zero. "
            "This indicates a data extraction error — re-extract from the report package before export."
        )
    rendered_revenue = as_float(fin.get("revenue"))
    if rendered_revenue is not None and source_revenue is None and abs(rendered_revenue) < 1e-9:
        issues.append(
            "Card 3: Sankey revenue resolves to zero. "
            "Verify sankeyActualData in the HTML or supply revenue via financial_data.json."
        )

    required_margins = [
        ("gross_margin_pct", "Card 3 gross margin"),
        ("operating_margin_pct", "Card 3 operating margin"),
        ("net_margin_pct", "Card 3 net margin"),
    ]
    for margin_key, label in required_margins:
        if as_float(prof.get(margin_key)) is None:
            issues.append(f"{label} is missing; cards must not show placeholder values like '--'.")

    cn_disp = company_short_cn(data)
    if logo_path_raw:
        cover_slot = clean(data.card_slots.cover_company_name_cn or "") if data.card_slots else ""
        if not cover_slot:
            issues.append(
                "When card_slots.logo_asset_path is set, logo production must also set "
                "card_slots.cover_company_name_cn (verified Chinese short name for Card 1 red title and footers)."
            )
    if not has_cjk(cn_disp):
        issues.append(
            "Card cover/footer company name must be Chinese: with a logo, set cover_company_name_cn in logo "
            "production; without a logo, use Chinese in HTML .company-name-cn or set cover_company_name_cn."
        )
    elif cn_disp.endswith("公司"):
        issues.append("Company display name must use the short Chinese name without '公司'.")
    if not data.date:
        issues.append("Date is missing.")
    if not brand:
        issues.append("Brand is missing.")
    if TEXT_RENDER_SCALE < 2:
        issues.append("Text rendering scale must be at least 2x for crisp export.")
    if "账号应该给人什么印象" in data.thesis:
        issues.append("Forbidden meta copy detected.")
    if source_net is not None and abs(float(fin.get("net", 0.0)) - source_net) > max(abs(source_net) * 0.02, 1.0):
        issues.append("Card 3 net income does not match financial_data income_statement.current_year.net_income.")
    if source_revenue:
        margin_sources = [
            ("gross_margin_pct", "gross_profit", "Card 3 gross margin"),
            ("operating_margin_pct", "operating_income", "Card 3 operating margin"),
            ("net_margin_pct", "net_income", "Card 3 net margin"),
        ]
        for margin_key, source_key, label in margin_sources:
            source_value = as_float(current_income.get(source_key))
            actual_margin = as_float(prof.get(margin_key))
            if source_value is not None and actual_margin is not None:
                expected_margin = source_value / source_revenue * 100
                if abs(actual_margin - expected_margin) > 0.5:
                    issues.append(f"{label} does not match financial_data income_statement.current_year.")
    for label, text in [
        ("Card 1 intro sentence", intro),
        ("Card 1 company-focus paragraph", focus),
        ("Card 2 industry paragraph", industry),
        ("Card 2 conclusion", conclusion_block(data)),
        ("Card 4 judgement paragraph", judgement_paragraph(data)),
        ("Card 5 main statement", brand_line),
    ]:
        if not is_complete_copy(text):
            issues.append(f"{label} must be a complete sentence or paragraph without ellipsis.")
    for label, text in [
        ("Card 4 judgement paragraph", judgement_paragraph(data)),
        ("Card 5 main statement", brand_line),
    ]:
        if not is_human_copy(text):
            issues.append(f"{label} must read like a human voice, not analyst template copy.")
    intro_font = f(FONT_INTRO)
    if len(wrap(draw, clean(intro), intro_font, 860)) > 2:
        issues.append("Card 1 intro sentence exceeds 2 lines.")
    if has_bad_linebreak(intro, 860, f(FONT_INTRO), draw):
        issues.append("Card 1 intro sentence contains a punctuation-led line break.")
    focus_font = f(FONT_PANEL_BODY)
    focus_lines = wrap(draw, clean(focus), focus_font, 860)
    if len(focus) < MIN_CARD1_FOCUS_CHARS:
        issues.append("Card 1 company-focus paragraph is too short.")
    if len(focus) > LIMIT_CARD1_FOCUS_CHARS:
        issues.append("Card 1 company-focus paragraph exceeds its character budget.")
    if len(focus_lines) < 3:
        issues.append("Card 1 company-focus paragraph leaves too much empty yellow-panel space.")
    if len(focus_lines) > 7:
        issues.append("Card 1 company-focus paragraph exceeds the allowed panel height.")
    if has_bad_linebreak(focus, 860, f(FONT_PANEL_BODY), draw):
        issues.append("Card 1 company-focus paragraph contains a punctuation-led line break.")

    left_card_height = measure_bullets(draw, bg_points, 446, f(FONT_BULLET), 12, 24, max_lines_per_item=4) + measure_block(
        draw, industry, 446, f(FONT_PANEL_BODY), 13, max_lines=11
    )
    if len(bg_points) != 4:
        issues.append("Card 2 must contain exactly 4 background bullets.")
    for point in bg_points:
        if not is_complete_copy(point):
            issues.append(f"Card 2 background bullet must be a complete sentence: {point}")
        if len(wrap(draw, clean(point), f(FONT_BULLET), 422)) > 4:
            issues.append(f"Card 2 background bullet is too long: {point}")
        if has_bad_linebreak(point, 422, f(FONT_BULLET), draw):
            issues.append(f"Card 2 background bullet contains a punctuation-led line break: {point}")

    if len(industry) < 80:
        issues.append("Card 2 industry paragraph is too short.")
    if len(industry) > LIMIT_CARD2_INDUSTRY_CHARS:
        issues.append("Card 2 industry paragraph exceeds its character budget.")
    if len(wrap(draw, clean(industry), f(FONT_PANEL_BODY), 446)) > 11:
        issues.append("Card 2 industry paragraph exceeds its section box.")
    if has_bad_linebreak(industry, 446, f(FONT_PANEL_BODY), draw):
        issues.append("Card 2 industry paragraph contains a punctuation-led line break.")
    y_card2 = 424
    for _bp in bg_points:
        y_card2 = block_final_y(draw, _bp, y_card2, 422, f(FONT_BULLET), 12, 4)
        y_card2 += 24
    industry_title_y_sim = max(728, y_card2 + 6)
    industry_body_y_sim = industry_title_y_sim + 58
    card2_industry_end_y = block_final_y(draw, industry, industry_body_y_sim, 446, f(FONT_PANEL_BODY), 13, 11)
    if card2_industry_end_y > 1224:
        issues.append(
            "Card 2 industry paragraph overflows the left panel (same dynamic layout as card_2: bullets push 行业层面 down). "
            "Shorten background_bullets or industry_paragraph."
        )
    if left_card_height < 360:
        issues.append("Card 2 left card is too sparse and leaves obvious whitespace.")
    conclusion = conclusion_block(data)
    if len(wrap(draw, clean(conclusion), f(FONT_CONCLUSION), 300)) > 4:
        issues.append("Card 2 conclusion exceeds its box.")

    if 710 < 438 + 4 * 56 + 28 + 20:
        issues.append("Card 3 metric cards are too close to the revenue rows.")
    explainer_points = revenue_explainer_points(data)
    explainer_height = measure_bullets(draw, explainer_points, 820, f(FONT_BULLET), 12, 12, max_lines_per_item=3)
    if explainer_height > LIMIT_CARD3_EXPLAINER_TOTAL_HEIGHT:
        issues.append("Card 3 explainer bullets exceed the yellow panel.")
    for point in explainer_points:
        if len(point) > LIMIT_CARD3_EXPLAINER_CHARS:
            issues.append(f"Card 3 explainer bullet exceeds its character budget: {point}")
        if not is_complete_copy(point):
            issues.append(f"Card 3 explainer bullet must be a complete sentence: {point}")
        if has_bad_linebreak(point, 796, f(FONT_BULLET), draw):
            issues.append(f"Card 3 explainer bullet contains a punctuation-led line break: {point}")

    left_height = measure_bullets(draw, left, 350, f(FONT_BULLET_COMPACT), 10, 18, max_lines_per_item=5)
    right_height = measure_bullets(draw, right, 368, f(FONT_BULLET_COMPACT), 10, 18, max_lines_per_item=5)
    if sum(len(x) for x in left) < 90:
        issues.append("Card 4 left column is too sparse.")
    if sum(len(x) for x in right) < 90:
        issues.append("Card 4 right column is too sparse.")
    if left_height < 320:
        issues.append("Card 4 left column leaves too much empty space.")
    if right_height < 320:
        issues.append("Card 4 right column leaves too much empty space.")
    if left_height > 520:
        issues.append("Card 4 left column exceeds its available height.")
    if right_height > 520:
        issues.append("Card 4 right column exceeds its available height.")
    for point in left:
        if not is_complete_copy(point):
            issues.append(f"Card 4 left column must use complete sentences: {point}")
        if len(point) > LIMIT_CARD4_NOW_BULLET_CHARS:
            issues.append(f"Card 4 left column exceeds its character budget: {point}")
        if has_bad_linebreak(point, 326, f(FONT_BULLET_COMPACT), draw):
            issues.append(f"Card 4 left column contains a punctuation-led line break: {point}")
    for point in right:
        if not is_complete_copy(point):
            issues.append(f"Card 4 right column must use complete sentences: {point}")
        if len(point) > LIMIT_CARD4_FUTURE_BULLET_CHARS:
            issues.append(f"Card 4 right column exceeds its character budget: {point}")
        if has_bad_linebreak(point, 344, f(FONT_BULLET_COMPACT), draw):
            issues.append(f"Card 4 right column contains a punctuation-led line break: {point}")

    judgement = judgement_paragraph(data)
    judgement_font = fit_block_font(
        draw,
        judgement,
        316,
        CARD4_JUDGEMENT_BOX_HEIGHT,
        start_size=FONT_JUDGEMENT,
        min_size=FONT_JUDGEMENT_MIN,
        line_gap=10,
        max_lines=CARD4_JUDGEMENT_MAX_LINES,
    )
    judgement_lines = wrap(draw, judgement, judgement_font, 316)
    if len(judgement) > LIMIT_CARD4_JUDGEMENT_CHARS:
        issues.append("Card 4 judgement paragraph exceeds its character budget.")
    if len(judgement_lines) > CARD4_JUDGEMENT_MAX_LINES:
        issues.append("Card 4 judgement paragraph exceeds its line budget.")
    jl_vis = judgement_lines[:CARD4_JUDGEMENT_MAX_LINES]
    if raster_text_block_height(draw, jl_vis, judgement_font, 10) > CARD4_JUDGEMENT_BOX_HEIGHT:
        issues.append(
            "Card 4 judgement paragraph exceeds its beige box height (raster line heights can exceed font.size estimates; shorten copy)."
        )
    if has_bad_linebreak(judgement, 316, judgement_font, draw):
        issues.append("Card 4 judgement paragraph contains a punctuation-led line break.")

    if len(wrap(draw, clean(brand_line), f(52, True), 760)) > 3:
        issues.append("Card 5 main statement exceeds its allowed block.")
    if measure_bullets(draw, brand_points, 820, f(FONT_BRAND_SUMMARY), 12, 22, max_lines_per_item=3) > 210:
        issues.append("Card 5 summary bullets exceed the yellow panel.")
    for point in brand_points:
        if not is_complete_copy(point):
            issues.append(f"Card 5 summary bullet must be a complete sentence: {point}")
        if has_bad_linebreak(point, 796, f(FONT_BRAND_SUMMARY), draw):
            issues.append(f"Card 5 summary bullet contains a punctuation-led line break: {point}")

    if len(wrap(draw, clean(title), f(FONT_POST_TITLE, True), 860)) > 2:
        issues.append("Card 6 title exceeds its allowed block.")
    if not clean(title).startswith(POST_TITLE_PREFIX):
        issues.append(f"Card 6 title must start with {POST_TITLE_PREFIX!r}.")
    if "一天吃透一家上市公司" in clean(title):
        issues.append("Card 6 title must use 一天吃透一家公司, not 一天吃透一家上市公司.")
    if has_bad_linebreak(title, 860, f(FONT_POST_TITLE, True), draw):
        issues.append("Card 6 title contains a punctuation-led line break.")
    if len(lines) != 4:
        issues.append("Card 6 content must contain exactly 4 bullet lines.")
    question_count = sum(1 for line in lines if clean(line).endswith(("？", "?")))
    if len(lines) == 4 and question_count != 1:
        issues.append("Card 6 content must contain exactly three statements and one question.")
    for line in lines:
        if not is_complete_copy(line):
            issues.append(f"Card 6 content line must be a complete sentence without ellipsis: {line}")
        if not card6_line_sounds_human(line):
            issues.append(f"Card 6 content line lacks a human voice: {line}")
        if len(wrap(draw, clean(line), f(FONT_POST_LINE), 860)) > 2:
            issues.append(f"Card 6 content line is too long: {line}")
        if has_bad_linebreak(line, 860, f(FONT_POST_LINE), draw):
            issues.append(f"Card 6 content line contains a punctuation-led line break: {line}")
    if len(wrap(draw, clean(tags), f(FONT_POST_TAG), 860)) > 4:
        issues.append("Card 6 hashtags exceed their section.")
    if has_bad_linebreak(tags, 860, f(FONT_POST_TAG), draw):
        issues.append("Card 6 hashtags contain a punctuation-led line break.")
    tag_tokens = clean(tags).split()
    for required_tag in REQUIRED_POST_TAGS:
        if required_tag not in tag_tokens:
            issues.append(f"Card 6 hashtags must include {required_tag}.")
    if len(tag_tokens) > MAX_POST_TAGS:
        issues.append(f"Card 6 hashtags may not exceed {MAX_POST_TAGS} tags.")

    if issues:
        raise ValueError("Validation failed:\n- " + "\n- ".join(issues))


def find_logo_asset(data: ReportData) -> Path | None:
    explicit = (data.card_slots.logo_asset_path or "").strip() if data.card_slots else ""
    if not explicit:
        return None
    raw = Path(explicit).expanduser()
    candidates = [raw] if raw.is_absolute() else [data.source_dir / raw, Path(__file__).resolve().parents[1] / raw]
    for path in candidates:
        if path.is_file() and path.suffix.lower() in IMAGE_EXTS:
            return path
    return None


# Card 1 logo area in logical design coordinates (must match logo_section / design-spec).
LOGO_BOX_CARD1_LOGICAL = (330, 1094, 750, 1238)
LOGO_SLOT_MAX_W = (LOGO_BOX_CARD1_LOGICAL[2] - LOGO_BOX_CARD1_LOGICAL[0]) * LAYOUT_SCALE
LOGO_SLOT_MAX_H = (LOGO_BOX_CARD1_LOGICAL[3] - LOGO_BOX_CARD1_LOGICAL[1]) * LAYOUT_SCALE
# Square / near-square marks (icons): require enough pixels for a sharp downscale into the slot.
LOGO_SQUAREISH_MIN_MAX_SIDE = 512
# Landscape vs portrait vs square-ish (same thresholds as layout heuristics elsewhere).
_LOGO_ASPECT_LANDSCAPE = 1.15


def logo_asset_dimension_issues(path: Path) -> list[str]:
    """
    Reject logos that are too small in the dominant dimension for the Card 1 slot.

    The renderer uses PIL thumbnail() which never upscales. A wide wordmark narrower than the
    slot width (e.g. 760px vs 840px) is almost always an upscaled favicon or soft raster — it
    looks blurry next to assets exported from SVG / high-res press PNG (compare NVIDIA ~1066px wide).
    """
    try:
        with Image.open(path) as im:
            w, h = im.size
    except OSError:
        return []
    if w <= 0 or h <= 0:
        return ["Logo image has invalid dimensions."]
    aspect = w / h if h else 0.0
    issues: list[str] = []
    if aspect >= _LOGO_ASPECT_LANDSCAPE:
        if w < LOGO_SLOT_MAX_W:
            issues.append(
                f"Logo bitmap width {w}px is below the Card 1 logo area width ({LOGO_SLOT_MAX_W}px at "
                f"LAYOUT_SCALE={LAYOUT_SCALE}). Export from official SVG or press-kit PNG at ≥{LOGO_SLOT_MAX_W}px "
                "wide; do not use favicons, social avatars, or upscaled low-resolution rasters."
            )
    elif aspect <= 1.0 / _LOGO_ASPECT_LANDSCAPE:
        if h < LOGO_SLOT_MAX_H:
            issues.append(
                f"Logo bitmap height {h}px is below the Card 1 logo area height ({LOGO_SLOT_MAX_H}px). "
                f"Use a vector or high-resolution vertical mark ≥{LOGO_SLOT_MAX_H}px tall."
            )
    else:
        if max(w, h) < LOGO_SQUAREISH_MIN_MAX_SIDE:
            issues.append(
                f"Logo bitmap is too small (longest side {max(w, h)}px; need ≥{LOGO_SQUAREISH_MIN_MAX_SIDE}px). "
                "Use an official icon or mark at sufficient resolution."
            )
    return issues


def logo_section(draw: ScaledDraw, img: Image.Image, data: ReportData) -> None:
    logo = find_logo_asset(data)
    if not logo:
        return
    paste_logo(img, logo, (330, 1094, 750, 1238))


def paste_logo(img: Image.Image, path: Path | None, box: tuple[int, int, int, int]) -> None:
    if not path:
        return
    try:
        logo = Image.open(path).convert("RGBA")
    except OSError:
        return
    s = LAYOUT_SCALE
    x0, y0, x1, y1 = box[0] * s, box[1] * s, box[2] * s, box[3] * s
    max_w = x1 - x0
    max_h = y1 - y0
    logo.thumbnail((max_w, max_h), Image.LANCZOS)
    canvas = Image.new("RGBA", img.size, (255, 255, 255, 0))
    x = x0 + (max_w - logo.width) // 2
    y = y0 + (max_h - logo.height) // 2
    canvas.alpha_composite(logo, (x, y))
    img.alpha_composite(canvas)


def cleanup_unused_logo_assets(data: ReportData, out_dir: Path) -> None:
    """Keep only the explicit Card 1 logo asset; remove temporary logo files."""
    used_logo = find_logo_asset(data)
    used_logo = used_logo.resolve() if used_logo else None
    root = out_dir.resolve()

    def is_inside(path: Path, parent: Path) -> bool:
        try:
            path.resolve().relative_to(parent.resolve())
            return True
        except ValueError:
            return False

    logo_sources = root / "logo_sources"
    if logo_sources.exists():
        if used_logo and is_inside(used_logo, logo_sources):
            for item in sorted(logo_sources.rglob("*"), key=lambda p: len(p.parts), reverse=True):
                if item.resolve() == used_logo:
                    continue
                if item.is_dir():
                    try:
                        item.rmdir()
                    except OSError:
                        pass
                elif item.is_file():
                    item.unlink()
        else:
            if logo_sources.is_dir() and not logo_sources.is_symlink():
                shutil.rmtree(logo_sources)
            else:
                logo_sources.unlink()

    for item in root.iterdir():
        if not item.is_file():
            continue
        if used_logo and item.resolve() == used_logo:
            continue
        if "logo" in item.name.lower() and item.suffix.lower() in LOGO_CLEANUP_EXTS:
            item.unlink()


def background() -> Image.Image:
    return Image.new("RGBA", (W, H), BG)


def panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill: str = WHITE, stroke: str = LINE, radius: int = 28) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=stroke, width=2)


def header(draw: ImageDraw.ImageDraw, card_no: int) -> None:
    if HEADER_BG:
        draw.rounded_rectangle((0, 0, 1080, 150), radius=0, fill=HEADER_BG)
        draw.line((72, 126, 1008, 126), fill=HEADER_RULE, width=1)
    else:
        draw.line((72, 126, 1008, 126), fill=LINE, width=2)

    brand = HEADER_BRAND_TEXT if HEADER_BG else TEXT
    sub = HEADER_SUBTITLE_TEXT if HEADER_BG else ORANGE
    page = HEADER_PAGE_TEXT if HEADER_BG else TEXT
    draw_text(draw, (72, 44), "金融豹", f(FONT_HEADER_BRAND, True), brand)
    draw_text(draw, (72, 86), "F I N A N C E   L E O P A R D", f(FONT_HEADER_SUBTITLE, True), sub)
    draw_text(draw, (948, 58), f"{card_no:02d}", _fl(FONT_HEADER_PAGE, True), page)


def footer(draw: ImageDraw.ImageDraw, data: ReportData) -> None:
    draw_text(draw, (72, 1288), f"{company_short_cn(data)} | {export_date_cn()}", f(FONT_FOOTER), MUTED)


def metric(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, label: str, value: str, accent: str) -> None:
    panel(draw, (x, y, x + w, y + 110), WHITE)
    draw.rounded_rectangle((x + 14, y + 14, x + 18, y + 96), radius=4, fill=accent)
    label_font = fit_font(draw, label, w - 42, FONT_METRIC_LABEL_START, FONT_METRIC_LABEL_MIN)
    value_font = fit_font(draw, value, w - 42, FONT_METRIC_VALUE_START, FONT_METRIC_VALUE_MIN)
    draw_text(draw, (x + 30, y + 18), label, label_font, MUTED)
    draw_text(draw, (x + 30, y + 52), value, value_font, TEXT)


def bullets(
    draw: ImageDraw.ImageDraw,
    items: list[str],
    x: int,
    y: int,
    width: int,
    max_items: int,
    max_lines: int,
    gap_after: int = 24,
    font_size: int = FONT_BULLET,
    line_gap: int = 12,
) -> int:
    for item in items[:max_items]:
        draw.ellipse((x, y + 12, x + 10, y + 22), fill=RED)
        y = block(draw, item, x + 24, y, width - 24, f(font_size), TEXT, line_gap, max_lines=max_lines)
        y += gap_after
    return y


def cover_metrics(data: ReportData) -> list[tuple[str, str, str]]:
    fin = finance(data)
    second_label = "净利润" if fin["net"] else "营业利润"
    second_value = money_text(fin["net"] or fin["op"])
    third_label, third_value, _ = operational_metric(data)
    return [
        (f"{fiscal_year(data)} 总收入", money_text(fin["revenue"]), GOLD),
        (second_label, second_value, RED),
        (third_label, third_value, GREEN),
    ]


def rate_metrics(data: ReportData) -> list[tuple[str, str, str]]:
    prof = profitability(data)
    return [
        ("毛利率", pct_text(prof.get("gross_margin_pct")), GREEN),
        ("营业利润率", pct_text(prof.get("operating_margin_pct")), BLUE),
        ("净利率", pct_text(prof.get("net_margin_pct")), RED),
    ]


def card_1(data: ReportData) -> Image.Image:
    img = background()
    d = ScaledDraw(ImageDraw.Draw(img), LAYOUT_SCALE)
    header(d, 1)
    draw_text(d, (72, 198), "每天学习一个公司", fs(58, True), TEXT)
    company_font = _fit_serif(d, company_short_cn(data), 860, 96, 58)
    draw_text(d, (72, 292), company_short_cn(data), company_font, RED)
    draw_text(d, (78, 412), f"{data.company_en} · {data.ticker}", f(FONT_COVER_META), MUTED)
    block(d, cover_intro(data), 78, 454, 860, f(FONT_INTRO), "#344054", 12, 2)
    for idx, (label, value, color) in enumerate(cover_metrics(data)):
        metric(d, 72 + idx * 300, 566, 280, label, value, color)
    draw_panel = (72, 736, 1008, 1060)
    d.rounded_rectangle(draw_panel, radius=28, fill=PANEL)
    draw_text(d, (108, 786), "公司看点", f(34, True), TEXT)
    block(d, company_focus_paragraph(data), 108, 842, 860, f(FONT_PANEL_BODY), "#344054", 12, 7)
    logo_section(d, img, data)
    footer(d, data)
    return finalize_export(img)


def card_2(data: ReportData) -> Image.Image:
    img = background()
    d = ScaledDraw(ImageDraw.Draw(img), LAYOUT_SCALE)
    header(d, 2)
    draw_text(d, (72, 198), "公司背景 + 行业介绍", f(58, True), TEXT)
    panel(d, (72, 314, 598, 1224))
    d.rounded_rectangle((622, 314, 1008, 1224), radius=28, fill=PANEL)
    draw_text(d, (108, 362), "公司背景", f(34, True), TEXT)
    left_end_y = bullets(d, background_points(data), 108, 424, 446, 4, 4)
    industry_title_y = max(728, left_end_y + 6)
    industry_body_y = industry_title_y + 58
    draw_text(d, (108, industry_title_y), "行业层面", f(34, True), TEXT)
    block(d, industry_paragraph(data), 108, industry_body_y, 446, f(FONT_PANEL_BODY), "#344054", 13, 11)
    draw_text(d, (656, 362), "波特五力", f(34, True), TEXT)
    labels = ["供应商", "买方", "新进入者", "替代品", "竞争强度"]
    y = 430
    for idx, (label, score) in enumerate(zip(labels, porter_scores_for_card(data))):
        draw_text(d, (656, y), label, f(FONT_PORTER_LABEL), "#475467")
        d.rounded_rectangle((656, y + 36, 856, y + 46), radius=8, fill=TRACK)
        color = PORTER_COLORS[idx] if idx < len(PORTER_COLORS) else (RED if score >= 4 else GOLD)
        d.rounded_rectangle((656, y + 36, 656 + int(200 * score / 5), y + 46), radius=8, fill=color)
        draw_text(d, (880, y + 6), f"{score}/5", f(FONT_PORTER_SCORE, True), TEXT)
        y += 110
    d.rounded_rectangle((622, 960, 1008, 1224), radius=28, fill=PANEL_PINK)
    draw_text(d, (656, 1018), "一句结论", f(30, True), TEXT)
    block(d, conclusion_block(data), 656, 1066, 300, f(FONT_CONCLUSION), "#344054", 12, 4)
    footer(d, data)
    return finalize_export(img)


def card_3(data: ReportData) -> Image.Image:
    img = background()
    d = ScaledDraw(ImageDraw.Draw(img), LAYOUT_SCALE)
    header(d, 3)
    draw_text(d, (72, 198), "实际收入分析", f(58, True), TEXT)
    panel(d, (72, 314, 1008, 856))
    draw_text(d, (108, 360), f"{fiscal_year(data)} 收入流", f(34, True), TEXT)
    fin = finance(data)
    rows = [
        ("总收入", chart_value_as_yi(fin["revenue"]), GOLD),
        ("营业成本", chart_value_as_yi(fin["cogs"]), RED),
        ("毛利润", chart_value_as_yi(fin["gross"]), GREEN),
        ("营业利润", chart_value_as_yi(fin["op"]), BLUE),
        ("净利润", chart_value_as_yi(fin["net"]), TEXT),
    ]
    maxv = max(abs(v) for _, v, _ in rows) or 1
    for idx, (label, value, color) in enumerate(rows):
        y = 438 + idx * 56
        draw_text(d, (108, y), label, f(FONT_CHART_LABEL), "#475467")
        d.rounded_rectangle((244, y + 6, 744, y + 28), radius=11, fill=TRACK)
        bar_color = RED if value < 0 else color
        d.rounded_rectangle((244, y + 6, 244 + int(500 * abs(value) / maxv), y + 28), radius=11, fill=bar_color)
        draw_text(d, (782, y - 6), f"{value:.1f} 亿{_CURRENCY_LABEL}", f(FONT_CHART_VALUE, True), TEXT)
    for idx, (label, value, color) in enumerate(rate_metrics(data)):
        metric(d, 108 + idx * 242, 710, 220, label, value, color)
    d.rounded_rectangle((72, 896, 1008, CARD3_EXPLAINER_PANEL_BOTTOM), radius=28, fill=PANEL)
    draw_text(d, (108, 942), "收入分析", f(34, True), TEXT)
    bullets(d, revenue_explainer_points(data), 108, CARD3_EXPLAINER_START_Y, 820, 3, 3, 12)
    footer(d, data)
    return finalize_export(img)


def card_4(data: ReportData) -> Image.Image:
    img = background()
    d = ScaledDraw(ImageDraw.Draw(img), LAYOUT_SCALE)
    header(d, 4)
    draw_text(d, (72, 198), "实际业务 + 未来展望", f(58, True), TEXT)
    d.rounded_rectangle((72, 314, 506, 1220), radius=28, fill=PANEL_SKY)
    d.rounded_rectangle((534, 314, 1008, 1220), radius=28, fill=PANEL_CREAM)
    draw_text(d, (108, 362), "现在靠什么赚钱", f(32, True), TEXT)
    bullets(d, business_now_points(data), 108, 424, 350, 4, 5, 18, font_size=FONT_BULLET_COMPACT, line_gap=10)
    draw_text(d, (570, 362), "未来 2-3 年看什么", f(32, True), TEXT)
    bullets(d, future_watch_points(data), 570, 424, 368, 4, 5, 18, font_size=FONT_BULLET_COMPACT, line_gap=10)
    d.rounded_rectangle((570, 980, 948, 1176), radius=24, fill=PANEL_PINK)
    draw_text(d, (602, 1028), "一句判断", f(28, True), TEXT)
    judgement = judgement_paragraph(data)
    judgement_font = fit_block_font(
        d,
        judgement,
        316,
        CARD4_JUDGEMENT_BOX_HEIGHT,
        start_size=FONT_JUDGEMENT,
        min_size=FONT_JUDGEMENT_MIN,
        line_gap=10,
        max_lines=CARD4_JUDGEMENT_MAX_LINES,
    )
    block(d, judgement, 602, 1076, 316, judgement_font, "#344054", 10, CARD4_JUDGEMENT_MAX_LINES)
    footer(d, data)
    return finalize_export(img)


def card_5(data: ReportData, brand: str) -> Image.Image:
    img = background()
    d = ScaledDraw(ImageDraw.Draw(img), LAYOUT_SCALE)
    header(d, 5)
    draw_text(d, (72, 214), brand, fs(110, True), TEXT)
    subtitle = (
        clean(data.card_slots.brand_subheading)
        if data.card_slots and data.card_slots.brand_subheading
        else f"一句话看{company_short_cn(data)}"
    )
    subtitle_font = _fit_serif(d, subtitle, 760, 46, 34)
    draw_text(d, (78, 346), subtitle, subtitle_font, ORANGE)
    statement_font = _fit_serif(d, brand_statement(data), 760, 52, 38)
    block(d, brand_statement(data), 78, 476, 760, statement_font, RED, 14, 3)
    d.rounded_rectangle((72, 646, 1008, 1006), radius=28, fill=PANEL_CREAM)
    draw_text(d, (108, 696), "今日总结", f(34, True), TEXT)
    bullets(d, brand_summary_points(data), 108, 758, 820, 3, 3, 22, font_size=FONT_BRAND_SUMMARY, line_gap=12)
    cta = (
        clean(data.card_slots.cta_line)
        if data.card_slots and data.card_slots.cta_line
        else "关注金融豹，每天学习一个公司。"
    )
    draw_text(d, (72, 1098), cta, f(34, True), TEXT)
    for x, y, s, col in [(900, 218, 88, RED), (980, 360, 64, GREEN), (900, 520, 74, ORANGE)]:
        d.ellipse((x, y, x + s, y + s), outline=col, width=3)
    paste_logo(img, find_logo_asset(data), (840, 240, 1010, 520))
    footer(d, data)
    return finalize_export(img)


def card_6(data: ReportData) -> Image.Image:
    img = Image.new("RGBA", (W, H), "#101318")
    d = ScaledDraw(ImageDraw.Draw(img), LAYOUT_SCALE)
    draw_text(d, (72, 64), "发帖文案", f(FONT_BULLET, True), "#F8FAFC")
    draw_text(d, (72, 104), "TITLE / CONTENT / HASHTAGS", f(FONT_HEADER_SUBTITLE), "#94A3B8")
    draw_text(d, (72, 190), post_title(data), f(FONT_POST_TITLE, True), "#F8FAFC")

    y = 310
    for line in post_content_lines(data):
        d.ellipse((72, y + 12, 84, y + 24), fill="#F6B48A")
        y = block(d, line, 102, y, 880, f(FONT_POST_LINE), "#E5E7EB", 14, 2)
        y += 30

    d.rounded_rectangle((72, y + 10, 1008, y + 210), radius=28, fill="#171B22")
    draw_text(d, (102, y + 42), post_hashtags(data), f(FONT_POST_TAG), "#F8FAFC")
    draw_text(d, (72, 1288), f"{company_short_cn(data)} | 发帖文案图", f(FONT_POST_FOOTER), "#94A3B8")
    return finalize_export(img)


def render_one(
    path: Path,
    output_root: Path,
    brand: str,
    slots_path: Path,
    *,
    copy_slots_to_output: bool = True,
    allow_no_logo: bool = False,
) -> list[Path]:
    data = parse_html(path)
    data.card_slots = load_card_slots(slots_path)
    set_currency_label(data)
    validate_report(data, brand, allow_no_logo=allow_no_logo)
    out_dir = output_root / data.stem
    out_dir.mkdir(parents=True, exist_ok=True)
    cards = [
        ("01_cover.png", card_1(data)),
        ("02_background_industry.png", card_2(data)),
        ("03_revenue.png", card_3(data)),
        ("04_business_outlook.png", card_4(data)),
        ("05_brand.png", card_5(data, brand)),
        ("06_post_copy.png", card_6(data)),
    ]
    paths = []
    for name, img in cards:
        out = out_dir / name
        img.save(out, quality=95)
        paths.append(out)
    if copy_slots_to_output:
        dest = out_dir / slots_path.name
        shutil.copy2(slots_path, dest)
        paths.append(dest)
    cleanup_unused_logo_assets(data, out_dir)
    return paths


def input_files(src: Path) -> list[Path]:
    return [src] if src.is_file() else sorted(src.glob("*.html"))


_SKILL_REPO_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_OUTPUT_ROOT = _SKILL_REPO_ROOT / "output"


def main() -> None:
    global _EXPORT_DOWN_SAMPLE_TO_LOGICAL
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="HTML file or folder.")
    parser.add_argument(
        "--output-root",
        default=str(_DEFAULT_OUTPUT_ROOT),
        help=f"Output root for PNG sets (default: {_DEFAULT_OUTPUT_ROOT})",
    )
    parser.add_argument("--brand", default="金融豹", help="Brand name.")
    parser.add_argument(
        "--slots",
        required=True,
        help="Path to card_slots.json (single HTML), or a directory of <stem>.card_slots.json (batch).",
    )
    parser.add_argument(
        "--export-logical-size",
        action="store_true",
        help=(
            "Export 1080×1350 PNGs (downscaled). Default: full render size "
            f"(W×H = {EXPORT_W * LAYOUT_SCALE}×{EXPORT_H * LAYOUT_SCALE} with current LAYOUT_SCALE={LAYOUT_SCALE})."
        ),
    )
    parser.add_argument(
        "--no-copy-slots",
        action="store_true",
        help="Do not copy card_slots.json into output/<stem>/ next to PNGs (default: copy for a single-folder bundle).",
    )
    parser.add_argument(
        "--palette",
        required=True,
        choices=["macaron", "default", "b", "c"],
        help=(
            "配色：macaron | default | b | c。必须使用 P0 已确认的配色。"
        ),
    )
    parser.add_argument(
        "--allow-no-logo",
        action="store_true",
        help=(
            "Allow export without card_slots.logo_asset_path (Card 1 has no logo). "
            "Use only when the customer explicitly waived the logo; default is to fail validation."
        ),
    )
    args = parser.parse_args()
    apply_palette(args.palette)
    _EXPORT_DOWN_SAMPLE_TO_LOGICAL = args.export_logical_size

    src = Path(args.input).expanduser().resolve()
    out_root = Path(args.output_root).expanduser().resolve()
    out_root.mkdir(parents=True, exist_ok=True)
    files = input_files(src)
    if not files:
        raise SystemExit(f"No HTML files found at: {src}")
    multiple = len(files) > 1
    copy_slots = not args.no_copy_slots
    for html in files:
        slots_path = resolve_slots_path(html, Path(args.slots), multiple_html=multiple)
        render_one(
            html,
            out_root,
            args.brand,
            slots_path,
            copy_slots_to_output=copy_slots,
            allow_no_logo=args.allow_no_logo,
        )
        print(f"generated: {html}")


if __name__ == "__main__":
    main()
