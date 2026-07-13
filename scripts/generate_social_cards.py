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
BG = "#FFF9F3"
TEXT = "#24263A"
MUTED = "#5C5A6D"
LINE = "#EEDFCC"
PANEL = "#FFF3E6"
RED = "#E44F67"
ORANGE = "#E07A3D"
GOLD = "#F1B84B"
GREEN = "#25B879"
BLUE = "#4E8DEB"
WHITE = "#FFFFFF"

HEADER_BG: str | None = "#141A2C"
HEADER_BRAND_TEXT = "#FFFFFF"
HEADER_SUBTITLE_TEXT = "#FFBF7A"
HEADER_PAGE_TEXT = "#F2EFE6"
HEADER_RULE = "#2A3046"

PANEL_MINT = "#E8F8EC"
PANEL_SKY = "#E7F0FF"
PANEL_PINK = "#FFE3E8"
PANEL_LILAC = "#EFE3FA"
PANEL_CREAM = "#FFF3E6"
TRACK = "#EFE6D8"
PORTER_COLORS = ["#FFB06F", "#F6788C", "#68A2F2", "#42C487", "#A77AE4"]

# Frosted-glass "Apple card" tokens used by Card 3 metrics panel.
# PANEL_GLASS is a near-white tinted with each palette's warmth — lighter than
# PANEL_CREAM so it reads as an elevated translucent surface against the body.
# GLASS_STROKE is the 1.5px hairline outline; GLASS_DIVIDER is the inner grid.
PANEL_GLASS = "#FFF8EC"
GLASS_STROKE = "#EBD8BA"
GLASS_DIVIDER = "#E9DCC5"
GLASS_LABEL = "#4F4A5A"
GLASS_PERIOD = "#A98662"

import os as _os


CARD_FILENAMES = (
    "01_cover.png",
    "02_porter.png",
    "03_five_year_financials.png",
    "04_company_quality.png",
    "05_country_lens.png",
)


def apply_palette(name: str) -> None:
    """Switch global colors for preview / alternate looks. Call before rendering."""
    global _ACTIVE_PALETTE
    global BG, TEXT, MUTED, LINE, PANEL, RED, ORANGE, GOLD, GREEN, BLUE, WHITE
    global HEADER_BG, HEADER_BRAND_TEXT, HEADER_SUBTITLE_TEXT, HEADER_PAGE_TEXT, HEADER_RULE
    global PANEL_MINT, PANEL_SKY, PANEL_PINK, PANEL_LILAC, PANEL_CREAM, TRACK, PORTER_COLORS
    global PANEL_GLASS, GLASS_STROKE, GLASS_DIVIDER, GLASS_LABEL, GLASS_PERIOD
    _ACTIVE_PALETTE = name
    if name == "macaron":
        BG = "#FFF9F3"
        TEXT = "#24263A"
        MUTED = "#5C5A6D"
        LINE = "#EEDFCC"
        PANEL = "#FFF3E6"
        RED = "#E44F67"
        ORANGE = "#E07A3D"
        GOLD = "#F1B84B"
        GREEN = "#25B879"
        BLUE = "#4E8DEB"
        WHITE = "#FFFFFF"
        HEADER_BG = "#141A2C"
        HEADER_BRAND_TEXT = "#FFFFFF"
        HEADER_SUBTITLE_TEXT = "#FFBF7A"
        HEADER_PAGE_TEXT = "#F2EFE6"
        HEADER_RULE = "#2A3046"
        PANEL_MINT = "#E8F8EC"
        PANEL_SKY = "#E7F0FF"
        PANEL_PINK = "#FFE3E8"
        PANEL_LILAC = "#EFE3FA"
        PANEL_CREAM = "#FFF3E6"
        TRACK = "#EFE6D8"
        PORTER_COLORS = ["#FFB06F", "#F6788C", "#68A2F2", "#42C487", "#A77AE4"]
        PANEL_GLASS = "#FFF8EC"
        GLASS_STROKE = "#EBD8BA"
        GLASS_DIVIDER = "#E9DCC5"
        GLASS_LABEL = "#4F4A5A"
        GLASS_PERIOD = "#A98662"
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
        PANEL_GLASS = "#FAFAFA"
        GLASS_STROKE = "#E6E6E6"
        GLASS_DIVIDER = "#EBEBEB"
        GLASS_LABEL = "#6B7280"
        GLASS_PERIOD = "#9CA3AF"
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
        PANEL_GLASS = "#F8F4FE"
        GLASS_STROKE = "#EAE0F4"
        GLASS_DIVIDER = "#EFE6F9"
        GLASS_LABEL = "#6B7280"
        GLASS_PERIOD = "#9CA3AF"
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
        PANEL_GLASS = "#FAF4E5"
        GLASS_STROKE = "#E6DCC1"
        GLASS_DIVIDER = "#EBE2CB"
        GLASS_LABEL = "#57534E"
        GLASS_PERIOD = "#A8A29E"
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
FONT_PORTER_LABEL = 21
FONT_PORTER_SCORE = 25
FONT_PORTER_EVIDENCE = 19
FONT_CHART_LABEL = 23
FONT_CHART_VALUE = 28
FONT_CFA_BODY = 22
FONT_CFA_TAKEAWAY = 24
FONT_METRIC_LABEL_START = 20
FONT_METRIC_LABEL_MIN = 16
FONT_METRIC_VALUE_START = 29
FONT_METRIC_VALUE_MIN = 22

MIN_CARD1_FOCUS_CHARS = 150
LIMIT_CARD1_FOCUS_CHARS = 165
LIMIT_CARD2_INDUSTRY_CHARS = 113
LIMIT_CARD2_BG_BULLET_CHARS = 60
LIMIT_CARD2_PORTER_EVIDENCE_CHARS = 70
# Card 2 right-side background panel geometry. Keep renderer and validator
# synchronized so stacked bullets cannot pass validation while spilling outside.
CARD2_BG_PANEL_BOTTOM = 720
CARD2_BG_PANEL_BOTTOM_INSET = 10
CARD2_BG_BULLETS_START_Y = 306
CARD2_BG_BULLETS_WIDTH = 320
CARD2_BG_BULLETS_TEXT_WIDTH = CARD2_BG_BULLETS_WIDTH
CARD2_BG_BULLET_MAX_ITEMS = 4
CARD2_BG_BULLET_MAX_LINES = 2
CARD2_BG_BULLET_GAP_AFTER = 18
CARD2_BG_BULLET_LINE_GAP = 5
CARD2_BG_CHAIN_FONT = 18
CARD2_BG_CHAIN_ROW_HEIGHT = 99
CARD2_BG_CHAIN_TEXT_TOP = 29
CARD2_BG_CHAIN_BOTTOM_GUTTER = 12
LIMIT_CARD3_EXPLAINER_CHARS = 58
LIMIT_CARD3_FIVE_YEAR_NARRATIVE_CHARS = 140
LIMIT_CARD3_INFLECTION_CHARS = 56
# Five-year arc panel (72,270..1008,630) holds narrative + 3 inflection
# bullets directly below it (no 拐点 sublabel — the RED ellipse markers in
# bullets() already distinguish them). At FONT_PANEL_BODY (25) the narrative
# can wrap to 3 lines (~120 px) leaving ~240 px below for the bullet block
# (3 × ~39 px = 117 px) plus a 22 px separator and a 16 px bottom inset.
CARD3_NARRATIVE_MAX_LINES = 3
CARD3_FIVE_YEAR_PANEL_BOTTOM = 630
CARD3_FIVE_YEAR_PANEL_BOTTOM_INSET = 16
# v4 (财务分析): the "过去 5 年的故事" subheader was removed; narrative now
# begins at panel-top + ~36px so the panel still breathes correctly without
# the subheader label above it. Old value 346 (subheader at 298 + ~48 gap).
CARD3_NARRATIVE_START_Y = 306
# v4 frosted-glass metrics panel (replaces the old yellow 收入分析 panel).
# Panel rounded-rect spans Y=940..1300 (height 360); the 2×3 grid sits inside
# with `CARD3_METRICS_*` padding tokens.
CARD3_METRICS_PANEL_TOP = 940
CARD3_METRICS_PANEL_BOTTOM = 1300
CARD3_METRICS_PANEL_LEFT = 72
CARD3_METRICS_PANEL_RIGHT = 1008
CARD3_METRICS_INNER_PAD_X = 36
CARD3_METRICS_INNER_PAD_Y = 32
CARD3_METRICS_DIVIDER_INSET = 32
# Legacy tokens kept so older Card 3 callsites don't break before refactor lands.
CARD3_EXPLAINER_PANEL_BOTTOM = CARD3_METRICS_PANEL_BOTTOM
CARD3_EXPLAINER_START_Y = 1024
CARD3_EXPLAINER_BOTTOM_INSET = 16
LIMIT_CARD3_EXPLAINER_TOTAL_HEIGHT = CARD3_EXPLAINER_PANEL_BOTTOM - CARD3_EXPLAINER_START_Y - CARD3_EXPLAINER_BOTTOM_INSET
TEXT_COMPOSITE_PAD = 8  # matches draw_text(): 2 * pad where pad=4
LIMIT_CARD4_CONCEPT_INTRO_CHARS = 110
LIMIT_CARD4_APPLICATION_CHARS = 95
LIMIT_CARD4_ANGLE_CHARS = 105
LIMIT_CARD4_FORMULA_CHARS = 80
LIMIT_CARD4_CALC_LINE_CHARS = 70

# Card 4 merged cream panel geometry. One panel, top-to-bottom blocks:
# concept title (red) → formula → concept_intro → company_calculation →
# divider → two-column footer (application bullets | different_angle_insight).
# Footer line sits at Y=1320; reserve 16 px gap inside the panel.
CARD4_PANEL_TOP = 198
CARD4_PANEL_BOTTOM = 1300
CARD4_PANEL_LEFT = 72
CARD4_PANEL_RIGHT = 1008
CARD4_INNER_PAD = 36
CARD4_DIVIDER_Y = 750
CARD4_TWO_COL_TOP_Y = 776
CARD4_COL_GAP = 32
CARD4_LEFT_COL_W = 408
CARD4_RIGHT_COL_X = CARD4_PANEL_LEFT + CARD4_INNER_PAD + CARD4_LEFT_COL_W + CARD4_COL_GAP
CARD4_RIGHT_COL_W = CARD4_PANEL_RIGHT - CARD4_INNER_PAD - CARD4_RIGHT_COL_X
CARD4_INNER_W = CARD4_PANEL_RIGHT - CARD4_PANEL_LEFT - 2 * CARD4_INNER_PAD

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

    schema_version: int = 3
    intro_sentence: str | None = None
    company_focus_paragraph: str | None = None
    one_minute_summary: dict[str, Any] | None = None
    metrics_row: list[str] | None = None
    background_bullets: list[Any] | None = None
    industry_paragraph: str | None = None
    porter_scores: list[int] | None = None
    porter_evidence: list[dict[str, Any]] | None = None
    five_year_arc: dict[str, Any] | None = None
    recent_financial_highlights: list[str] | None = None
    revenue_explainer_points: list[str] | None = None
    financial_metrics_panel: list[dict[str, Any]] | None = None
    company_quality: dict[str, Any] | None = None
    country_lens: dict[str, Any] | None = None
    # Historical schema v3/v4 field. Kept readable for old archived bundles,
    # but active schema v5 rejects it and never renders a CFA card.
    cfa_lens: dict[str, Any] | None = None
    logo_asset_path: str | None = None
    cover_company_name_cn: str | None = None

    @staticmethod
    def from_json_dict(raw: dict[str, Any]) -> CardSlotOverrides:
        fields = {
            "schema_version",
            "intro_sentence",
            "company_focus_paragraph",
            "one_minute_summary",
            "metrics_row",
            "background_bullets",
            "industry_paragraph",
            "porter_scores",
            "porter_evidence",
            "five_year_arc",
            "recent_financial_highlights",
            "revenue_explainer_points",
            "financial_metrics_panel",
            "company_quality",
            "country_lens",
            "cfa_lens",
            "logo_asset_path",
            "cover_company_name_cn",
        }
        kwargs: dict[str, Any] = {}
        for key in fields:
            if key not in raw:
                continue
            val = raw[key]
            kwargs[key] = int(val) if key == "schema_version" and val is not None else val
        return CardSlotOverrides(**kwargs)


PORTER_FORCE_KEYS = ("rivalry", "new_entrants", "supplier_power", "buyer_power", "substitutes")
PORTER_FORCE_LABEL_CN = {
    "rivalry": "竞争强度",
    "new_entrants": "新进入者",
    "supplier_power": "供应商",
    "buyer_power": "买方",
    "substitutes": "替代品",
}

BACKGROUND_CHAIN_STEPS = (
    "external_condition",
    "transmission",
    "company_outcome",
    "watch_signal",
)
BACKGROUND_CHAIN_LABEL_CN = {
    "external_condition": "外部条件",
    "transmission": "传导机制",
    "company_outcome": "公司结果",
    "watch_signal": "观察信号",
}

CFA_LENS_REQUIRED_STR_KEYS = (
    "concept_key",
    "concept_name_cn",
    "concept_intro",
    "formula",
    "different_angle_insight",
)

# Formula must contain '=' AND at least one math operator. Bare textual claims
# like "公式：经营杠杆" must be rejected — formulas need operators.
CFA_FORMULA_OPERATORS = ("/", "×", "*", "+", "−", "-", "(", "Δ", "%")


def assert_card_slots_complete(slots: CardSlotOverrides) -> None:
    """Reject incomplete JSON so exports never fall back to template copy for missing slots."""

    def need_str(label: str, val: str | None) -> None:
        if not clean(val or ""):
            raise ValueError(f"card_slots.json missing or empty required field: {label}")

    def need_list(label: str, items: list[Any] | None, min_n: int) -> None:
        if not items:
            raise ValueError(f"card_slots.json missing required list: {label} (need {min_n} items).")
        n = len([x for x in items if clean(str(x))])
        if n < min_n:
            raise ValueError(f"card_slots.json {label} needs at least {min_n} non-empty entries (got {n}).")

    if slots.schema_version == 5:
        need_str("intro_sentence", slots.intro_sentence)
        need_list("metrics_row", slots.metrics_row, 3)

        summary = slots.one_minute_summary
        if not isinstance(summary, dict):
            raise ValueError("card_slots.json missing required object: one_minute_summary.")
        for key in ("business_model", "primary_risk"):
            if not clean(str(summary.get(key) or "")):
                raise ValueError(f"card_slots.json one_minute_summary.{key} must be non-empty text.")
        variables = summary.get("core_variables")
        if not isinstance(variables, list) or len([x for x in variables if clean(str(x))]) != 2:
            raise ValueError("card_slots.json one_minute_summary.core_variables must contain exactly 2 non-empty entries.")

        _assert_cards_2_and_3_complete(slots)
        _assert_company_quality_complete(slots.company_quality)
        _assert_country_lens_complete(slots.country_lens)
        if slots.cfa_lens:
            raise ValueError("card_slots.json schema v5 must not contain cfa_lens; CFA Lens was removed from the active product.")
        return

    # Historical v3/v4 validation retained for archived bundles and regression
    # tests. load_card_slots() rejects these versions for new renders.
    # Card 1
    need_str("intro_sentence", slots.intro_sentence)
    need_str("company_focus_paragraph", slots.company_focus_paragraph)
    need_list("metrics_row", slots.metrics_row, 3)

    # Card 2
    need_str("industry_paragraph", slots.industry_paragraph)
    need_list("background_bullets", slots.background_bullets, 4)
    if not slots.porter_evidence or not isinstance(slots.porter_evidence, list):
        raise ValueError("card_slots.json missing required list: porter_evidence (need 5 entries).")
    if len(slots.porter_evidence) != 5:
        raise ValueError(
            f"card_slots.json porter_evidence must contain exactly 5 entries (got {len(slots.porter_evidence)})."
        )
    seen_forces: set[str] = set()
    for idx, entry in enumerate(slots.porter_evidence):
        if not isinstance(entry, dict):
            raise ValueError(f"card_slots.json porter_evidence[{idx}] must be an object.")
        force = entry.get("force")
        if force not in PORTER_FORCE_KEYS:
            raise ValueError(
                f"card_slots.json porter_evidence[{idx}].force must be one of {PORTER_FORCE_KEYS} (got {force!r})."
            )
        if force in seen_forces:
            raise ValueError(f"card_slots.json porter_evidence has duplicate force: {force!r}.")
        seen_forces.add(force)
        score = entry.get("score")
        if not isinstance(score, int) or score < 1 or score > 5:
            raise ValueError(
                f"card_slots.json porter_evidence[{idx}].score must be integer 1..5 (got {score!r})."
            )
        if not clean(str(entry.get("evidence") or "")):
            raise ValueError(f"card_slots.json porter_evidence[{idx}].evidence must be non-empty text.")

    # Card 3
    arc = slots.five_year_arc
    if not isinstance(arc, dict):
        raise ValueError("card_slots.json missing required object: five_year_arc.")
    if not clean(str(arc.get("narrative") or "")):
        raise ValueError("card_slots.json five_year_arc.narrative must be non-empty text.")
    arc_points = arc.get("inflection_points")
    if not isinstance(arc_points, list) or len([x for x in arc_points if clean(str(x))]) < 3:
        raise ValueError("card_slots.json five_year_arc.inflection_points needs at least 3 non-empty entries.")
    # `recent_financial_highlights` and `revenue_explainer_points` are legacy
    # slots from the v2/v3 layout; the v4 Card 3 (财务分析) renders a 6-metric
    # frosted-glass grid instead of a revenue-analysis bullet panel. The legacy
    # slots are still accepted (so old card_slots.json files load), but no
    # longer required.
    #
    # `financial_metrics_panel`: 6 entries authored by the content production
    # agent, in this fixed display order (CFA importance × 3 profitability + 2
    # cash-flow + 1 leverage). Each entry: label_cn, value, period_cn, category.
    panel_metrics = slots.financial_metrics_panel
    if not isinstance(panel_metrics, list):
        raise ValueError(
            "card_slots.json missing required list: financial_metrics_panel "
            "(need exactly 6 entries, one per CFA-importance metric)."
        )
    if len(panel_metrics) != 6:
        raise ValueError(
            f"card_slots.json financial_metrics_panel must contain exactly 6 entries (got {len(panel_metrics)})."
        )
    _ALLOWED_METRIC_CATEGORIES = {"profitability", "cash_flow", "leverage"}
    for idx, entry in enumerate(panel_metrics):
        if not isinstance(entry, dict):
            raise ValueError(f"card_slots.json financial_metrics_panel[{idx}] must be an object.")
        for key in ("label_cn", "value", "period_cn", "category"):
            if not clean(str(entry.get(key) or "")):
                raise ValueError(
                    f"card_slots.json financial_metrics_panel[{idx}].{key} must be non-empty text."
                )
        if entry.get("category") not in _ALLOWED_METRIC_CATEGORIES:
            raise ValueError(
                f"card_slots.json financial_metrics_panel[{idx}].category must be one of "
                f"{sorted(_ALLOWED_METRIC_CATEGORIES)} (got {entry.get('category')!r})."
            )
        label = clean(str(entry.get("label_cn") or ""))
        value = clean(str(entry.get("value") or ""))
        if any(marker in value for marker in ("近似", "$", "美元")):
            raise ValueError(
                f"card_slots.json financial_metrics_panel[{idx}].value must not contain "
                f"visible approximation/currency markers ('近似', '$', '美元'): {value!r}."
            )
        if "净现金" in value:
            raise ValueError(
                f"card_slots.json financial_metrics_panel[{idx}] must put net-cash wording in "
                f"label_cn='净现金' and keep value as a plain amount like '11.89亿'."
            )
        if idx == 5:
            if label == "净债务/EBITDA":
                if "×" not in value:
                    raise ValueError(
                        "card_slots.json financial_metrics_panel[5] label_cn='净债务/EBITDA' "
                        "requires a ratio value like '0.5×'. Use label_cn='净现金' for net-cash companies."
                    )
            elif label in {"净现金", "净现金头寸"}:
                if "亿" not in value or "×" in value:
                    raise ValueError(
                        "card_slots.json financial_metrics_panel[5] label_cn='净现金' "
                        "requires a plain amount value like '11.89亿'."
                    )
            else:
                raise ValueError(
                    "card_slots.json financial_metrics_panel[5].label_cn must be "
                    "'净债务/EBITDA' for positive net debt or '净现金' for net-cash companies."
                )

    # Card 4 (CFA lens)
    lens = slots.cfa_lens
    if not isinstance(lens, dict):
        raise ValueError("card_slots.json missing required object: cfa_lens.")
    for key in CFA_LENS_REQUIRED_STR_KEYS:
        if not clean(str(lens.get(key) or "")):
            raise ValueError(f"card_slots.json cfa_lens.{key} must be non-empty text.")
    formula = clean(str(lens.get("formula") or ""))
    if "=" not in formula or not any(op in formula for op in CFA_FORMULA_OPERATORS):
        raise ValueError(
            "card_slots.json cfa_lens.formula must contain '=' and at least one math operator "
            f"(one of {CFA_FORMULA_OPERATORS}); got: {formula!r}"
        )
    application = lens.get("company_application")
    if not isinstance(application, list) or len([x for x in application if clean(str(x))]) < 3:
        raise ValueError("card_slots.json cfa_lens.company_application needs at least 3 non-empty entries.")
    calc = lens.get("company_calculation")
    if not isinstance(calc, list):
        raise ValueError("card_slots.json cfa_lens.company_calculation must be a list of 1-3 strings.")
    calc_clean = [clean(str(x)) for x in calc if clean(str(x))]
    if not (1 <= len(calc_clean) <= 3):
        raise ValueError(
            "card_slots.json cfa_lens.company_calculation needs 1-3 non-empty entries "
            f"(got {len(calc_clean)})."
        )
    if not any(any(ch.isdigit() for ch in entry) for entry in calc_clean):
        raise ValueError(
            "card_slots.json cfa_lens.company_calculation must include at least one entry "
            "that contains a digit — the whole point is to plug real company numbers into the formula."
        )


def _assert_cards_2_and_3_complete(slots: CardSlotOverrides) -> None:
    """Shared structural checks for active schema-v5 Cards 2 and 3."""
    if not clean(slots.industry_paragraph or ""):
        raise ValueError("card_slots.json missing or empty required field: industry_paragraph")
    if not isinstance(slots.background_bullets, list) or len(slots.background_bullets) != 4:
        raise ValueError("card_slots.json background_bullets must contain exactly 4 ordered chain entries.")
    actual_steps: list[str] = []
    for idx, entry in enumerate(slots.background_bullets):
        if not isinstance(entry, dict):
            raise ValueError(
                f"card_slots.json background_bullets[{idx}] must be an object with step and text; "
                "schema v5 does not accept an unordered fact bullet."
            )
        step = str(entry.get("step") or "")
        text = clean(str(entry.get("text") or ""))
        if not text:
            raise ValueError(f"card_slots.json background_bullets[{idx}].text must be non-empty.")
        actual_steps.append(step)
    if tuple(actual_steps) != BACKGROUND_CHAIN_STEPS:
        raise ValueError(
            "card_slots.json background_bullets must follow the causal order "
            f"{BACKGROUND_CHAIN_STEPS}; got {tuple(actual_steps)}."
        )
    if not isinstance(slots.porter_evidence, list) or len(slots.porter_evidence) != 5:
        raise ValueError("card_slots.json porter_evidence must contain exactly 5 entries.")
    seen: set[str] = set()
    for idx, entry in enumerate(slots.porter_evidence):
        if not isinstance(entry, dict):
            raise ValueError(f"card_slots.json porter_evidence[{idx}] must be an object.")
        force = entry.get("force")
        if force not in PORTER_FORCE_KEYS or force in seen:
            raise ValueError(f"card_slots.json porter_evidence[{idx}].force is invalid or duplicated: {force!r}.")
        seen.add(force)
        score = entry.get("score")
        if not isinstance(score, int) or not 1 <= score <= 5:
            raise ValueError(f"card_slots.json porter_evidence[{idx}].score must be integer 1..5.")
        if not clean(str(entry.get("evidence") or "")):
            raise ValueError(f"card_slots.json porter_evidence[{idx}].evidence must be non-empty text.")

    arc = slots.five_year_arc
    if not isinstance(arc, dict) or not clean(str(arc.get("narrative") or "")):
        raise ValueError("card_slots.json five_year_arc.narrative must be non-empty text.")
    points = arc.get("inflection_points")
    if not isinstance(points, list) or len([x for x in points if clean(str(x))]) < 3:
        raise ValueError("card_slots.json five_year_arc.inflection_points needs at least 3 non-empty entries.")
    metrics = slots.financial_metrics_panel
    if not isinstance(metrics, list) or len(metrics) != 6:
        raise ValueError("card_slots.json financial_metrics_panel must contain exactly 6 entries.")
    expected_categories = ("profitability", "profitability", "profitability", "cash_flow", "cash_flow", "leverage")
    for idx, (entry, category) in enumerate(zip(metrics, expected_categories)):
        if not isinstance(entry, dict):
            raise ValueError(f"card_slots.json financial_metrics_panel[{idx}] must be an object.")
        for key in ("label_cn", "value", "period_cn", "category"):
            if not clean(str(entry.get(key) or "")):
                raise ValueError(f"card_slots.json financial_metrics_panel[{idx}].{key} must be non-empty text.")
        if entry.get("category") != category:
            raise ValueError(f"card_slots.json financial_metrics_panel[{idx}].category must be {category!r}.")


def _assert_company_quality_complete(value: dict[str, Any] | None) -> None:
    if not isinstance(value, dict):
        raise ValueError("card_slots.json missing required object: company_quality.")
    for section in ("valuation", "governance_incentives", "capital_allocation", "accounting_quality"):
        panel = value.get(section)
        if not isinstance(panel, dict):
            raise ValueError(f"card_slots.json company_quality.{section} must be an object.")
        for key in ("finding", "evidence", "watch_item"):
            if not clean(str(panel.get(key) or "")):
                raise ValueError(f"card_slots.json company_quality.{section}.{key} must be non-empty text.")
        if section == "valuation":
            metrics = panel.get("metrics")
            if not isinstance(metrics, list) or not 1 <= len(metrics) <= 2:
                raise ValueError("card_slots.json company_quality.valuation.metrics must contain 1-2 entries.")
            for idx, metric in enumerate(metrics):
                if not isinstance(metric, dict):
                    raise ValueError(f"card_slots.json company_quality.valuation.metrics[{idx}] must be an object.")
                for key in ("label_cn", "value", "basis_label", "as_of_date"):
                    if not clean(str(metric.get(key) or "")):
                        raise ValueError(f"card_slots.json company_quality.valuation.metrics[{idx}].{key} must be non-empty text.")
    if not clean(str(value.get("unknown") or "")):
        raise ValueError("card_slots.json company_quality.unknown must be non-empty text.")


COUNTRY_LENS_DIMENSIONS = (
    "tax",
    "fx_inflation",
    "regulation",
    "labor",
    "consumer_culture",
    "minority_shareholder_protection",
)


def _assert_country_lens_complete(value: dict[str, Any] | None) -> None:
    if not isinstance(value, dict):
        raise ValueError("card_slots.json missing required object: country_lens.")
    exposure = value.get("exposure_map")
    if not isinstance(exposure, dict):
        raise ValueError("card_slots.json country_lens.exposure_map must be an object.")
    for key in ("incorporation", "listing", "operations", "revenue"):
        if not clean(str(exposure.get(key) or "")):
            raise ValueError(f"card_slots.json country_lens.exposure_map.{key} must be non-empty text.")
    dimensions = value.get("dimensions")
    if not isinstance(dimensions, list) or len(dimensions) != 6:
        raise ValueError("card_slots.json country_lens.dimensions must contain exactly 6 entries.")
    keys = [entry.get("key") for entry in dimensions if isinstance(entry, dict)]
    if tuple(keys) != COUNTRY_LENS_DIMENSIONS:
        raise ValueError(f"card_slots.json country_lens.dimensions must use fixed order {COUNTRY_LENS_DIMENSIONS}.")
    for idx, entry in enumerate(dimensions):
        for key in ("label_cn", "country_fact", "company_transmission", "watch_metric"):
            if not clean(str(entry.get(key) or "")):
                raise ValueError(f"card_slots.json country_lens.dimensions[{idx}].{key} must be non-empty text.")
    warnings = value.get("top_warnings")
    if not isinstance(warnings, list) or not 1 <= len([x for x in warnings if clean(str(x))]) <= 2:
        raise ValueError("card_slots.json country_lens.top_warnings must contain 1-2 non-empty entries.")
    for key in ("company_to_country_insight", "unknown"):
        if not clean(str(value.get(key) or "")):
            raise ValueError(f"card_slots.json country_lens.{key} must be non-empty text.")


def load_card_slots(path: Path) -> CardSlotOverrides:
    p = path.expanduser().resolve()
    if not p.is_file():
        raise FileNotFoundError(f"Slots file not found: {p}")
    raw = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("card_slots JSON root must be an object")
    slots = CardSlotOverrides.from_json_dict(raw)
    if slots.schema_version != 5:
        raise ValueError(
            f"card_slots.json schema_version must be 5 for the active five-card knowledge-map layout; "
            f"got {slots.schema_version!r}. Re-run content production (P8) for archived v3/v4 slots."
        )
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
    """Five Porter scores in display order: 供应商、买方、新进入者、替代品、竞争强度.
    Prefer explicit `card_slots.porter_scores`; otherwise derive from
    `card_slots.porter_evidence` (keyed by force); else fall back to HTML."""
    if data.card_slots and data.card_slots.porter_scores is not None:
        return data.card_slots.porter_scores
    if data.card_slots and data.card_slots.porter_evidence:
        order = ("supplier_power", "buyer_power", "new_entrants", "substitutes", "rivalry")
        by_force = {
            entry.get("force"): entry.get("score")
            for entry in data.card_slots.porter_evidence
            if isinstance(entry, dict)
        }
        out: list[int] = []
        for force in order:
            score = by_force.get(force)
            out.append(int(score) if isinstance(score, int) else 3)
        if len(out) == 5:
            return out
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


def logical_text_width(draw: ImageDraw.ImageDraw, text: str, font_obj: ImageFont.FreeTypeFont) -> float:
    """Measure a rendered line in the logical coordinate system."""
    return draw.textlength(text, font=font_obj) / LAYOUT_SCALE


def draw_centered_text_in_rect(
    draw: ImageDraw.ImageDraw,
    rect: tuple[int, int, int, int],
    text: str,
    font_obj: ImageFont.FreeTypeFont,
    fill: str,
) -> None:
    """Center one line horizontally and vertically inside a logical rect."""
    left, top, right, bottom = rect
    width = logical_text_width(draw, text, font_obj)
    height = line_raster_height(draw, font_obj, text)
    x = int(round(left + ((right - left) - width) / 2))
    y = int(round(top + ((bottom - top) - height) / 2))
    draw_text(draw, (x, y), text, font_obj, fill)


def draw_centered_block_in_rect(
    draw: ImageDraw.ImageDraw,
    rect: tuple[int, int, int, int],
    text: str,
    font_obj: ImageFont.FreeTypeFont,
    fill: str,
    *,
    line_gap: int,
    max_lines: int,
) -> None:
    """Center a wrapped block as one unit, retaining left alignment within it."""
    left, top, right, bottom = rect
    lines = wrap(draw, clean(text), font_obj, right - left)[:max_lines]
    if not lines:
        return
    heights = [line_raster_height(draw, font_obj, line) for line in lines]
    block_h = sum(heights) + line_gap * max(0, len(lines) - 1)
    block_w = max(logical_text_width(draw, line, font_obj) for line in lines)
    x = int(round(left + ((right - left) - block_w) / 2))
    y = int(round(top + ((bottom - top) - block_h) / 2))
    for idx, line in enumerate(lines):
        draw_text(draw, (x, y), line, font_obj, fill)
        y += heights[idx] + (line_gap if idx < len(lines) - 1 else 0)


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


# ---------------------------------------------------------------------------
# Cards 1-4 analyst-voice gate
# ---------------------------------------------------------------------------
_NUMBER_RE = re.compile(r"\d+(?:\.\d+)?(?:%|亿|万|TB|EB|bps|x|倍|个|人|百万|亿元|\$|B|M|K)")
_COMP_KEYWORDS = ("peer", "同业", "consensus", "guide", "历史", "vs", "同比", "环比", "相比", "过去", "去年", "上一", "管理层指引")
# Additional analyst-comp idioms regex-matched on data_anchor (case-insensitive):
# scenario-based comp (bull/bear/base case + midpoint + range), fiscal year refs (FY20xx, 财年20xx),
# bare 4-digit year refs (1900-2099). These are legitimate anchors a strict 1-2 word keyword list misses.
_COMP_PATTERNS = (
    re.compile(r"\bfy\d{2,4}\b", re.IGNORECASE),
    re.compile(r"财年\s*\d{2,4}"),
    re.compile(r"\b(bull|bear|base)\s+case\b", re.IGNORECASE),
    re.compile(r"\bmidpoint\b|\bscenarios?\b|\brange\b", re.IGNORECASE),
    re.compile(r"\b(low|high)\s+end\b", re.IGNORECASE),
    re.compile(r"\b(19|20)\d{2}\b"),
)
_BANNED_PHRASES = ("说白了", "已不是核心叙事", "已不重要", "体现了", "总而言之", "综上", "简单来说", "本质上市场")
_BINARY_FLIP_RE = re.compile(r"不是.{1,20}[，,]\s*而是")
_CLICKBAIT_CTA_RE = re.compile(r"关注[^，,。]{1,8}[，,。].*每天.*学")
_DATE_WINDOW_RE = re.compile(r"\d{4}-(?:0[1-9]|1[0-2]|Q[1-4]|H[12])")

# Writing-style regex bank — same rules as the HTML report (single source:
# Equity Research Skill/references/report_style_guide_cn.md §"符号与比较语规范"
# and §"中英混杂规范"). Three patterns, applied to Card 1-5 prose only:
#
#   (1) Bare "+" in front of a number without an explicit comparator base
#       (同比/环比/年化/较/相比/约/±/增长/下降/扩张/收窄/提升/增加) within 15
#       chars before. Catches both "+34%" shortcuts and "+10.17亿美元"-style
#       absolute decorations. Card layout phase cannot drop the comparator to
#       fit char budgets — trim downstream phrasing instead.
#
#   (2) Banned English abbreviations (CC / YoY / Y/Y / QoQ / Q/Q / FX / CAGR)
#       in body prose. First-mention parens like "恒定汇率（CC）" elsewhere
#       in the same card_slots object whitelists later bare uses.
_BARE_PLUS_RE = re.compile(
    r"\+\d+(?:\.\d+)?(?:\s*[-–~至]\s*\d+(?:\.\d+)?)?"
    r"\s*(?:%|pp|个百分点|亿|万|百万|千|元|美元|港元|人民币)?"
)
_COMPARATOR_BEFORE_PLUS_RE = re.compile(
    r"(同比|环比|年化|较|相比|约|±|增长|下降|扩张|收窄|提升|增加)"
)
_STYLE_BANNED_ABBREVS = ("CC", "YoY", "Y/Y", "QoQ", "Q/Q", "FX", "CAGR")
_STYLE_BANNED_ABBREV_RE = re.compile(
    r"\b(" + "|".join(re.escape(a) for a in _STYLE_BANNED_ABBREVS) + r")\b"
)
_STYLE_FIRST_MENTION_RE = re.compile(
    r"[（(][^（()）]{0,40}\b(CC|YoY|Y/Y|QoQ|Q/Q|FX|CAGR)\b[^（()）]{0,40}[)）]"
)
_CN_RAW_PERIOD_TOKEN_RE = re.compile(
    r"(?:Q[1-4]\s*FY\d{4}|FY\d{4}|\d{4}\s*Q[1-4]|\d{4}\s*H[12])",
    re.IGNORECASE,
)
_TICKER_LED_CN_RE = re.compile(r"^\s*[A-Z]{2,5}(?:从|的|在|是|由|把|靠)")
_CARD3_CHANGE_VERBS = ("从", "扩到", "扩至", "转向", "切入", "升级为", "变成", "转为", "走向")
_CARD3_FIN_RESULT_TERMS = ("收入", "利润", "毛利率", "利润率", "现金流", "转正", "亏损", "净现金")
_CN_INFLECTION_TIME_RE = re.compile(r"^\s*(?:19|20)\d{2}(?:年|财年)")

# slot keys covered by Cards 1-4 contract
# Note: five_year_arc.narrative and cfa_lens.company_calculation are nested;
# the worker_notes file uses the bare leaf name as the top-level key.
#
# v4: Card 3 dropped `revenue_explainer_points` (the old 收入分析 bullet panel)
# in favor of the 6-metric `financial_metrics_panel` grid. Numeric metrics are
# source-anchored (validator-2 fact-checks each number against filings) and do
# not need worker_notes analyst substrate the way prose slots do.
CARD1_4_WORKER_SLOTS = (
    "intro_sentence",                # Card 1
    "company_focus_paragraph",       # Card 1
    "industry_paragraph",            # Card 2
    "five_year_arc.narrative",       # Card 3 (nested)
    "cfa_lens.company_calculation",  # Card 4 (nested, AUTHORITY)
)
# slots that REQUIRE primary_quote (analyst-authority slots)
AUTHORITY_SLOTS = ("company_calculation",)

# Card 1-4 prose keys that get backstop banned-phrase checks. Includes nested
# leaves we extract via helper below.
CARD1_4_PROSE_TOP_LEVEL_KEYS = (
    "intro_sentence",
    "company_focus_paragraph",
    "background_bullets",
    "industry_paragraph",
)


def _worker_note_leaf_key(slot: str) -> str:
    """Map 'five_year_arc.narrative' → 'narrative' for worker_notes lookup keys
    and for AUTHORITY_SLOTS membership checks."""
    return slot.rsplit(".", 1)[-1]


def _collect_card1_4_prose(card_slots: dict) -> list[tuple[str, str]]:
    """Return (display_key, text) pairs for every prose chunk on Cards 1-4
    that should be subject to banned-phrase / writing-style backstops."""
    out: list[tuple[str, str]] = []
    for key in CARD1_4_PROSE_TOP_LEVEL_KEYS:
        value = card_slots.get(key)
        if isinstance(value, list):
            for v in value:
                if isinstance(v, str):
                    out.append((key, v))
                elif isinstance(v, dict) and isinstance(v.get("text"), str):
                    out.append((key, v["text"]))
        elif isinstance(value, str):
            out.append((key, value))

    # porter_evidence: each entry's evidence string
    pe = card_slots.get("porter_evidence")
    if isinstance(pe, list):
        for entry in pe:
            if isinstance(entry, dict):
                ev = entry.get("evidence")
                if isinstance(ev, str):
                    out.append(("porter_evidence.evidence", ev))

    # five_year_arc nested fields
    arc = card_slots.get("five_year_arc")
    if isinstance(arc, dict):
        narrative = arc.get("narrative")
        if isinstance(narrative, str):
            out.append(("five_year_arc.narrative", narrative))
        for pt in arc.get("inflection_points") or []:
            if isinstance(pt, str):
                out.append(("five_year_arc.inflection_points", pt))

    # cfa_lens nested fields
    lens = card_slots.get("cfa_lens")
    if isinstance(lens, dict):
        for key in ("concept_intro", "different_angle_insight"):
            value = lens.get(key)
            if isinstance(value, str):
                out.append((f"cfa_lens.{key}", value))
        for pt in lens.get("company_application") or []:
            if isinstance(pt, str):
                out.append(("cfa_lens.company_application", pt))
        for pt in lens.get("company_calculation") or []:
            if isinstance(pt, str):
                out.append(("cfa_lens.company_calculation", pt))
    return out


def validate_card1_4_analytical_content(
    card_slots: dict,
    worker_notes: dict | None = None,
) -> list[str]:
    """Validate that Card 1-4 slots have the analyst-content substrate.

    Returns a list of human-readable issue strings. Empty list = pass.
    Checks worker_notes for required hidden fields (data_anchor, variant_view,
    falsifier|primary_quote|catalyst_with_date) and card_slots for backstop
    banned phrases.
    """
    issues: list[str] = []
    if worker_notes is None:
        issues.append("missing card_slots_worker_notes.json sidecar")
        return issues

    for slot in CARD1_4_WORKER_SLOTS:
        leaf = _worker_note_leaf_key(slot)
        note = worker_notes.get(slot)
        if note is None:
            # Fall back to the leaf key so writers may either use the full
            # 'five_year_arc.narrative' or just 'narrative' in worker_notes.
            note = worker_notes.get(leaf)
        if not note or not isinstance(note, dict):
            issues.append(f"worker_notes.{slot}: missing or not an object")
            continue

        # data_anchor: number + comp keyword
        da = (note.get("data_anchor") or "").strip()
        if len(da) < 10:
            issues.append(f"worker_notes.{slot}.data_anchor: too short (<10 chars)")
        elif not _NUMBER_RE.search(da):
            issues.append(f"worker_notes.{slot}.data_anchor: no parseable number")
        elif not (
            any(k in da.lower() for k in _COMP_KEYWORDS)
            or any(p.search(da) for p in _COMP_PATTERNS)
        ):
            issues.append(
                f"worker_notes.{slot}.data_anchor: no comp anchor "
                f"(keywords peer/同业/consensus/guide/历史/vs/同比/环比/相比/过去/去年/上一/管理层指引 "
                f"OR scenario/bull case/bear case/base case/midpoint/range/FY-year/4-digit-year)"
            )

        # variant_view: ≥15 chars
        vv = (note.get("variant_view") or "").strip()
        if len(vv) < 15:
            issues.append(f"worker_notes.{slot}.variant_view: too short (<15 chars)")

        # at least 1 of: falsifier / primary_quote / catalyst_with_date
        has_falsifier = isinstance(note.get("falsifier"), str) and len(note["falsifier"].strip()) >= 20
        pq = note.get("primary_quote")
        has_quote = (
            isinstance(pq, dict)
            and isinstance(pq.get("speaker"), str)
            and len(pq.get("speaker", "").strip()) > 0
            and isinstance(pq.get("quote"), str)
            and len(pq.get("quote", "").strip()) >= 10
        )
        cw = note.get("catalyst_with_date")
        has_catalyst = (
            isinstance(cw, dict)
            and isinstance(cw.get("date_window"), str)
            and bool(_DATE_WINDOW_RE.search(cw.get("date_window", "")))
        )
        if not (has_falsifier or has_quote or has_catalyst):
            issues.append(
                f"worker_notes.{slot}: missing all of (falsifier ≥20chars, primary_quote with speaker+quote, catalyst_with_date)"
            )

        # authority slots must have a primary_quote
        if leaf in AUTHORITY_SLOTS and not has_quote:
            issues.append(
                f"worker_notes.{slot}: primary_quote required (analyst-authority slot)"
            )

    prose_chunks = _collect_card1_4_prose(card_slots)

    # Pre-scan the entire card_slots prose for first-mention parens that
    # whitelist later bare-abbrev uses. "恒定汇率（CC）" once → later "CC" OK.
    all_text = " ".join(text for _, text in prose_chunks)
    style_first_mention_abbrevs: set[str] = set()
    for m in _STYLE_FIRST_MENTION_RE.finditer(all_text):
        style_first_mention_abbrevs.add(m.group(1))

    for key, text in prose_chunks:
        text_clean = clean(text)
        if key == "intro_sentence" and text.lstrip().startswith("说白了"):
            issues.append(f"card_slots.{key}: starts with '说白了' (banned on Cards 1-4)")
        for phrase in _BANNED_PHRASES:
            if phrase in text:
                issues.append(f"card_slots.{key}: contains banned phrase '{phrase}'")
                break
        if _BINARY_FLIP_RE.search(text):
            issues.append(f"card_slots.{key}: contains 'X 不是 Y 而是 Z' template (banned on Cards 1-4)")

        # Writing-style rule (1)+(2): bare "+" without comparator base
        for m in _BARE_PLUS_RE.finditer(text):
            window_before = text[max(0, m.start() - 15):m.start()]
            if _COMPARATOR_BEFORE_PLUS_RE.search(window_before):
                continue
            snippet = text[max(0, m.start() - 15):min(len(text), m.end() + 10)]
            issues.append(
                f"card_slots.{key}: writing-style — bare '+' without comparator base "
                f"(同比/环比/年化/较/相比 must precede +N within 15 chars): "
                f"...{snippet}..."
            )

        # Writing-style rule (3): banned English abbreviation
        for m in _STYLE_BANNED_ABBREV_RE.finditer(text):
            abbrev = m.group(1)
            if abbrev in style_first_mention_abbrevs:
                continue
            snippet = text[max(0, m.start() - 10):min(len(text), m.end() + 10)]
            issues.append(
                f"card_slots.{key}: writing-style — English abbreviation '{abbrev}' "
                f"in body prose (CC→恒定汇率, YoY→同比, QoQ→环比, FX→汇率, "
                f"CAGR→复合年化增长率; first-mention '恒定汇率（CC）' would "
                f"whitelist later uses): ...{snippet}..."
            )

        # Chinese-reader localization: visible Chinese card prose should not
        # expose raw fiscal shorthand that reads like an English spreadsheet.
        # Keep product/protocol names in English when normal, but localize
        # time labels and growth syntax for CN cards.
        if has_cjk(text_clean):
            period_match = _CN_RAW_PERIOD_TOKEN_RE.search(text_clean)
            if period_match:
                issues.append(
                    f"card_slots.{key}: Chinese prose should localize fiscal period "
                    f"'{period_match.group(0)}' (e.g. FY2025→2025财年, "
                    f"Q1 FY2026→2026财年一季度, 2026 H2→2026年下半年)."
                )
            if _TICKER_LED_CN_RE.search(text_clean):
                issues.append(
                    f"card_slots.{key}: Chinese prose should use the Chinese company short name, "
                    "not a ticker-led sentence."
                )

            if key == "five_year_arc.inflection_points":
                if not _CN_INFLECTION_TIME_RE.search(text_clean):
                    issues.append(
                        f"card_slots.{key}: Card 3 inflection bullet must start with "
                        f"Chinese time wording like '2025财年' or '2026年下半年': {text_clean}"
                    )
                if re.search(r"\b(?:FY|Q[1-4]|H[12])\b", text_clean, flags=re.IGNORECASE):
                    issues.append(
                        f"card_slots.{key}: Card 3 inflection bullet should localize "
                        f"FY/Q/H labels for Chinese readers: {text_clean}"
                    )

            if key == "five_year_arc.narrative":
                if not (card_slots.get("cover_company_name_cn") or "公司" in text_clean):
                    issues.append(
                        "card_slots.five_year_arc.narrative: Card 3 top story should name "
                        "the Chinese company short name or say 公司 so readers know the subject."
                    )
                if not any(term in text_clean for term in _CARD3_CHANGE_VERBS):
                    issues.append(
                        "card_slots.five_year_arc.narrative: Card 3 top story must explain "
                        "the business shift (从/转向/切入/升级为/扩到等), not just list products."
                    )
                if not any(term in text_clean for term in _CARD3_FIN_RESULT_TERMS):
                    issues.append(
                        "card_slots.five_year_arc.narrative: Card 3 top story must connect "
                        "the shift to a financial result (收入/利润/毛利率/现金流/转正等)."
                    )

    return issues


EPISTEMIC_TYPES = {
    "company_disclosure",
    "external_fact",
    "analyst_calculation",
    "external_estimate",
    "inference",
    "forecast",
}

CLAIM_REQUIRED_PREFIXES = (
    "one_minute_summary.business_model",
    "one_minute_summary.core_variables",
    "one_minute_summary.primary_risk",
    "industry_paragraph",
    "background_bullets",
    "five_year_arc.narrative",
    "company_quality.valuation",
    "company_quality.governance_incentives",
    "company_quality.capital_allocation",
    "company_quality.accounting_quality",
    "country_lens.dimensions",
    "country_lens.top_warnings",
    "country_lens.company_to_country_insight",
)

_ATTRIBUTION_MARKERS = {
    "company_disclosure": ("披露", "年报", "财报", "公告"),
    "external_fact": ("据", "官方", "监管", "统计"),
    "analyst_calculation": ("按", "计算", "折算"),
    "external_estimate": ("据", "估计", "市场预期"),
    "inference": ("据此", "推断", "意味着", "说明"),
    "forecast": ("若", "预计", "将", "情景"),
}


def _strings_under_slot(node: Any, path: str = "") -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    if isinstance(node, str):
        out.append((path, node))
    elif isinstance(node, list):
        for idx, item in enumerate(node):
            out.extend(_strings_under_slot(item, f"{path}[{idx}]"))
    elif isinstance(node, dict):
        for key, value in node.items():
            child = f"{path}.{key}" if path else key
            out.extend(_strings_under_slot(value, child))
    return out


def _visible_text_for_claim(card_slots: dict, slot_path: str) -> str:
    """Return visible text at an exact path or the nearest parent subtree."""
    parts = re.findall(r"([^.\[\]]+)|\[(\d+)\]", slot_path)
    node: Any = card_slots
    for key, index in parts:
        if index and isinstance(node, list):
            idx = int(index)
            node = node[idx] if idx < len(node) else None
        elif key and isinstance(node, dict):
            node = node.get(key)
        else:
            node = None
        if node is None:
            break
    if isinstance(node, str):
        return clean(node)
    return " ".join(text for _, text in _strings_under_slot(node))


def validate_card1_5_analytical_content(card_slots: dict, worker_notes: dict | None) -> list[str]:
    """Active schema-v5 gate: claim provenance plus visible attribution."""
    issues: list[str] = []
    if worker_notes is None:
        return ["missing card_slots_worker_notes.json sidecar"]
    claims = worker_notes.get("claims")
    if not isinstance(claims, list) or not claims:
        return ["worker_notes.claims: missing non-empty claim-level evidence array"]

    covered: list[str] = []
    seen_ids: set[str] = set()
    for idx, claim in enumerate(claims):
        prefix = f"worker_notes.claims[{idx}]"
        if not isinstance(claim, dict):
            issues.append(f"{prefix}: must be an object")
            continue
        claim_id = clean(str(claim.get("claim_id") or ""))
        slot_path = clean(str(claim.get("slot_path") or ""))
        kind = clean(str(claim.get("epistemic_type") or ""))
        if not claim_id or claim_id in seen_ids:
            issues.append(f"{prefix}.claim_id: missing or duplicated")
        seen_ids.add(claim_id)
        if not slot_path or not _visible_text_for_claim(card_slots, slot_path):
            issues.append(f"{prefix}.slot_path: does not resolve to visible card copy: {slot_path!r}")
        else:
            covered.append(slot_path)
        if kind not in EPISTEMIC_TYPES:
            issues.append(f"{prefix}.epistemic_type: must be one of {sorted(EPISTEMIC_TYPES)}")
        as_of = clean(str(claim.get("as_of_date") or ""))
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", as_of):
            issues.append(f"{prefix}.as_of_date: must be YYYY-MM-DD")
        refs = claim.get("source_refs")
        if not isinstance(refs, list) or not refs:
            issues.append(f"{prefix}.source_refs: must contain at least one source")
        else:
            for ref_idx, ref in enumerate(refs):
                if not isinstance(ref, dict) or not clean(str(ref.get("publisher") or "")):
                    issues.append(f"{prefix}.source_refs[{ref_idx}]: publisher is required")
                if isinstance(ref, dict) and not (clean(str(ref.get("url") or "")) or clean(str(ref.get("path") or ""))):
                    issues.append(f"{prefix}.source_refs[{ref_idx}]: url or path is required")
        if kind == "analyst_calculation" and not clean(str(claim.get("basis_id") or "")):
            issues.append(f"{prefix}.basis_id: required for analyst_calculation")
        if kind in {"inference", "forecast"} and len(clean(str(claim.get("falsifier") or ""))) < 12:
            issues.append(f"{prefix}.falsifier: at least 12 characters required for {kind}")
        visible = _visible_text_for_claim(card_slots, slot_path)
        markers = _ATTRIBUTION_MARKERS.get(kind, ())
        if visible and markers and not any(marker in visible for marker in markers):
            issues.append(
                f"{prefix}: visible copy must naturally attribute {kind}; expected one of {markers} in {slot_path}"
            )

    for required in CLAIM_REQUIRED_PREFIXES:
        if not any(path == required or path.startswith(required + ".") or path.startswith(required + "[") for path in covered):
            issues.append(f"worker_notes.claims: no claim covers required visible slot prefix {required}")

    active_copy = {
        key: value for key, value in card_slots.items()
        if key not in {"schema_version", "logo_asset_path", "cover_company_name_cn", "cfa_lens"}
    }
    prose = _strings_under_slot(active_copy)
    all_text = " ".join(text for _, text in prose)
    first_mentions = {m.group(1) for m in _STYLE_FIRST_MENTION_RE.finditer(all_text)}
    for path, text in prose:
        for phrase in _BANNED_PHRASES:
            if phrase in text:
                issues.append(f"card_slots.{path}: contains banned phrase '{phrase}'")
        if _BINARY_FLIP_RE.search(text):
            issues.append(f"card_slots.{path}: contains banned 'X 不是 Y 而是 Z' template")
        for match in _BARE_PLUS_RE.finditer(text):
            before = text[max(0, match.start() - 15):match.start()]
            if not _COMPARATOR_BEFORE_PLUS_RE.search(before):
                issues.append(f"card_slots.{path}: bare '+' without comparator base")
        for match in _STYLE_BANNED_ABBREV_RE.finditer(text):
            if match.group(1) not in first_mentions:
                issues.append(f"card_slots.{path}: unexplained English abbreviation {match.group(1)!r}")
    return dedupe_texts(issues)


def fit_copy(candidates: list[str], limit: int) -> str:
    normalized: list[str] = []
    for raw in candidates:
        text = ensure_terminal_punct(strip_stiff_opener(raw))
        if text:
            normalized.append(text)
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
        if rebuilt and len(clean(rebuilt)) >= 4:
            return ensure_terminal_punct(rebuilt)
        clipped = clean(shortest)[: max(0, limit - 1)].rstrip("，；：,;: ")
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


def source_copy_candidates(
    texts: list[str],
    limit: int,
    *,
    sentence_options: tuple[int, ...] = (1, 2),
) -> list[str]:
    candidates: list[str] = []
    for raw in dedupe_texts(texts):
        raw = sanitize_source_text(raw)
        if not raw:
            continue
        base = ensure_terminal_punct(strip_stiff_opener(raw))
        if base:
            candidates.append(base)
        for count in sentence_options:
            compressed = paragraph_from_sentences(raw, limit, sentences=count)
            if compressed:
                candidates.append(compressed)
        for part in sentence_chunks(raw, 4):
            normalized = ensure_terminal_punct(strip_stiff_opener(part))
            if normalized:
                candidates.append(normalized)
    return dedupe_texts(candidates)


def dense_source_paragraph(
    texts: list[str],
    limit: int,
    *,
    max_sentences: int = 3,
) -> str:
    picked: list[str] = []
    for text in dedupe_texts([sanitize_source_text(text) for text in texts]):
        for sentence in sentence_chunks(text, 4):
            normalized = ensure_terminal_punct(strip_stiff_opener(sentence))
            if not normalized or normalized in picked:
                continue
            trial = "".join(picked) + normalized
            if len(trial) <= limit:
                picked.append(normalized)
            if len(picked) >= max_sentences:
                break
        if len(picked) >= max_sentences:
            break
    return "".join(picked)


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


def current_financial_period(data: ReportData) -> str:
    """Visible period label for renderer-generated Card 3 financial bars."""
    current = income_current(data)
    return pick_first(
        current.get("period"),
        current.get("period_cn"),
        current.get("fiscal_period_label"),
        current.get("fiscal_year"),
        get_nested(data.financial_data, "income_statement", "period"),
        get_nested(data.financial_data, "fiscal_period"),
        fiscal_year(data),
    )


def normalize_period_key(period: str) -> str:
    return re.sub(r"\s+", "", clean(period)).upper().replace("FY", "FY")


_CN_QUARTER_LABEL = {"1": "一季度", "2": "二季度", "3": "三季度", "4": "四季度"}
_CN_HALF_LABEL = {"1": "上半年", "2": "下半年"}


def period_display_cn(period: str) -> str:
    """Localize common fiscal shorthand for visible Chinese card labels."""
    raw = clean(period)
    if not raw:
        return ""
    m = re.search(r"\bFY(\d{4})\s+ended\s+\d{4}-\d{2}-\d{2}\b", raw, flags=re.IGNORECASE)
    if m:
        return f"{m.group(1)}财年"
    m = re.search(r"\bFY(\d{4})\s+Q([1-4])\s+ended\s+\d{4}-\d{2}-\d{2}\b", raw, flags=re.IGNORECASE)
    if m:
        return f"{m.group(1)}财年{_CN_QUARTER_LABEL[m.group(2)]}"
    compact = normalize_period_key(raw)
    m = re.fullmatch(r"FY(\d{4})", compact)
    if m:
        return f"{m.group(1)}财年"
    m = re.fullmatch(r"Q([1-4])FY(\d{4})", compact)
    if m:
        return f"{m.group(2)}财年{_CN_QUARTER_LABEL[m.group(1)]}"
    m = re.fullmatch(r"FY(\d{4})Q([1-4])", compact)
    if m:
        return f"{m.group(1)}财年{_CN_QUARTER_LABEL[m.group(2)]}"
    m = re.fullmatch(r"(\d{4})Q([1-4])", compact)
    if m:
        return f"{m.group(1)}年{_CN_QUARTER_LABEL[m.group(2)]}"
    m = re.fullmatch(r"(\d{4})H([12])", compact)
    if m:
        return f"{m.group(1)}年{_CN_HALF_LABEL[m.group(2)]}"
    return raw


def card3_income_flow_title(data: ReportData) -> str:
    period = period_display_cn(current_financial_period(data))
    return f"{period}收入流" if period else "收入流"


def fit_font_for_width(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
    sizes: tuple[int, ...],
    *,
    bold: bool = True,
) -> ImageFont.FreeTypeFont:
    """Pick the largest listed font size that fits max_width logical pixels."""
    raw_draw = draw._draw if isinstance(draw, ScaledDraw) else draw
    for size in sizes:
        candidate = f(size, bold)
        bbox = raw_draw.textbbox((0, 0), text, font=candidate)
        text_w = (bbox[2] - bbox[0]) / LAYOUT_SCALE
        if text_w <= max_width:
            return candidate
    return f(sizes[-1], bold)


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
        "CHF": "瑞郎",
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
    ay = abs(y)
    if ay < 0.01:
        wan = value * 100.0
        return f"{wan:.0f} 万{_CURRENCY_LABEL}"
    if ay < 0.1:
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


def cover_intro(data: ReportData) -> str:
    if data.card_slots and data.card_slots.intro_sentence:
        return clean(data.card_slots.intro_sentence)
    raise RuntimeError(
        f"Slot 'intro_sentence' missing in card_slots.json for {company_short_cn(data) or data.company_en or data.ticker}. "
        f"Renderer no longer emits a default fallback — writer must produce all slot content."
    )


def company_focus_paragraph(data: ReportData) -> str:
    if data.card_slots and data.card_slots.company_focus_paragraph:
        return clean(data.card_slots.company_focus_paragraph)
    raise RuntimeError(
        f"Slot 'company_focus_paragraph' missing in card_slots.json for {company_short_cn(data) or data.company_en or data.ticker}. "
        f"Renderer no longer emits a default fallback — writer must produce all slot content."
    )


def one_minute_summary(data: ReportData) -> dict[str, Any]:
    value = data.card_slots.one_minute_summary if data.card_slots else None
    if not isinstance(value, dict):
        raise RuntimeError("Slot 'one_minute_summary' missing in schema-v5 card_slots.json.")
    variables = [clean(str(x)) for x in value.get("core_variables") or [] if clean(str(x))]
    return {
        "business_model": clean(str(value.get("business_model") or "")),
        "core_variables": variables[:2],
        "primary_risk": clean(str(value.get("primary_risk") or "")),
    }


def company_quality_data(data: ReportData) -> dict[str, Any]:
    value = data.card_slots.company_quality if data.card_slots else None
    if not isinstance(value, dict):
        raise RuntimeError("Slot 'company_quality' missing in schema-v5 card_slots.json.")
    return value


def country_lens_data(data: ReportData) -> dict[str, Any]:
    value = data.card_slots.country_lens if data.card_slots else None
    if not isinstance(value, dict):
        raise RuntimeError("Slot 'country_lens' missing in schema-v5 card_slots.json.")
    return value


def industry_paragraph(data: ReportData) -> str:
    if data.card_slots and data.card_slots.industry_paragraph:
        return clean(data.card_slots.industry_paragraph)
    raise RuntimeError(
        f"Slot 'industry_paragraph' missing in card_slots.json for {company_short_cn(data) or data.company_en or data.ticker}. "
        f"Renderer no longer emits a default fallback — writer must produce all slot content."
    )


def background_points(data: ReportData) -> list[dict[str, str]]:
    """Return the four causal beats shown on Card 2 in fixed reading order."""
    raw = data.card_slots.background_bullets if data.card_slots else None
    if not isinstance(raw, list):
        return []
    out: list[dict[str, str]] = []
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        step = str(entry.get("step") or "")
        text = clean(str(entry.get("text") or ""))
        if step in BACKGROUND_CHAIN_STEPS and text:
            out.append({"step": step, "text": text})
    return out[:4]


def porter_evidence_entries(data: ReportData) -> list[dict[str, Any]]:
    if not data.card_slots or not data.card_slots.porter_evidence:
        return []
    out: list[dict[str, Any]] = []
    for entry in data.card_slots.porter_evidence:
        if not isinstance(entry, dict):
            continue
        out.append({
            "force": entry.get("force"),
            "score": entry.get("score"),
            "evidence": clean(str(entry.get("evidence") or "")),
        })
    return out


def revenue_explainer_points(data: ReportData) -> list[str]:
    if data.card_slots and data.card_slots.revenue_explainer_points:
        pts = [clean(x) for x in data.card_slots.revenue_explainer_points if clean(x)]
        return dedupe_texts(pts, 4)
    raise RuntimeError(
        f"Slot 'revenue_explainer_points' missing in card_slots.json for {company_short_cn(data) or data.company_en or data.ticker}. "
        f"Renderer no longer emits a default fallback — writer must produce all slot content."
    )


def five_year_narrative(data: ReportData) -> str:
    arc = data.card_slots.five_year_arc if data.card_slots else None
    if not isinstance(arc, dict):
        raise RuntimeError(
            f"Slot 'five_year_arc' missing in card_slots.json for {company_short_cn(data) or data.company_en or data.ticker}."
        )
    return clean(str(arc.get("narrative") or ""))


def five_year_inflection_points(data: ReportData) -> list[str]:
    arc = data.card_slots.five_year_arc if data.card_slots else None
    if not isinstance(arc, dict):
        return []
    pts = [clean(str(x)) for x in (arc.get("inflection_points") or []) if clean(str(x))]
    return dedupe_texts(pts, 4)


def financial_metrics_panel(data: ReportData) -> list[dict[str, Any]]:
    """Return the 6-metric Card 3 grid (v4: replaces revenue_explainer_points).

    Each entry is a dict with keys (label_cn, value, period_cn, category).
    Display order is fixed by CFA importance: 3 profitability rows first, then
    2 cash-flow rows, then 1 leverage row.
    """
    if not data.card_slots or not data.card_slots.financial_metrics_panel:
        raise RuntimeError(
            f"Slot 'financial_metrics_panel' missing in card_slots.json for "
            f"{company_short_cn(data) or data.company_en or data.ticker}. "
            f"Renderer no longer emits a default fallback — writer must produce all slot content."
        )
    out: list[dict[str, Any]] = []
    for entry in data.card_slots.financial_metrics_panel:
        if not isinstance(entry, dict):
            continue
        out.append({
            "label_cn": clean(str(entry.get("label_cn") or "")),
            "value": clean(str(entry.get("value") or "")),
            "period_cn": clean(str(entry.get("period_cn") or "")),
            "category": entry.get("category"),
        })
    return out


def recent_financial_highlights(data: ReportData) -> list[str]:
    if not data.card_slots or not data.card_slots.recent_financial_highlights:
        raise RuntimeError(
            f"Slot 'recent_financial_highlights' missing in card_slots.json for {company_short_cn(data) or data.company_en or data.ticker}."
        )
    items = [clean(x) for x in data.card_slots.recent_financial_highlights if clean(x)]
    return dedupe_texts(items, 4)


_FORMULA_GLYPH_FALLBACKS = {
    # The default macOS Hiragino face that backs ARIAL/ARIAL_BOLD lacks
    # U+2212 (MINUS SIGN); substitute the ASCII hyphen-minus so the formula
    # renders. JSON keeps U+2212 for semantic correctness; this is a
    # render-time-only normalization.
    "−": "-",
}


def _render_safe_math(text: str) -> str:
    for src, dst in _FORMULA_GLYPH_FALLBACKS.items():
        text = text.replace(src, dst)
    return text


def cfa_lens_data(data: ReportData) -> dict[str, Any]:
    lens = data.card_slots.cfa_lens if data.card_slots else None
    if not isinstance(lens, dict):
        raise RuntimeError(
            f"Slot 'cfa_lens' missing in card_slots.json for {company_short_cn(data) or data.company_en or data.ticker}."
        )
    application = [clean(str(x)) for x in (lens.get("company_application") or []) if clean(str(x))]
    calculation = [_render_safe_math(clean(str(x))) for x in (lens.get("company_calculation") or []) if clean(str(x))]
    return {
        "concept_key": clean(str(lens.get("concept_key") or "")),
        "concept_name_cn": clean(str(lens.get("concept_name_cn") or "")),
        "concept_intro": clean(str(lens.get("concept_intro") or "")),
        "formula": _render_safe_math(clean(str(lens.get("formula") or ""))),
        "company_calculation": calculation[:3],
        "company_application": dedupe_texts(application, 4),
        "different_angle_insight": clean(str(lens.get("different_angle_insight") or "")),
        "cfa_progress_source": clean(str(lens.get("cfa_progress_source") or "")),
    }


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


def card2_background_bullets_end_y(draw: ImageDraw.ImageDraw, items: list[Any]) -> int:
    texts = [clean(str(item.get("text") or "")) if isinstance(item, dict) else clean(str(item)) for item in items]
    overflow = 0
    for text in texts[:CARD2_BG_BULLET_MAX_ITEMS]:
        font_obj = f(CARD2_BG_CHAIN_FONT)
        lines = wrap(draw, text, font_obj, CARD2_BG_BULLETS_TEXT_WIDTH)
        content_h = sum(line_raster_height(draw, font_obj, line) for line in lines)
        content_h += CARD2_BG_BULLET_LINE_GAP * max(0, len(lines) - 1)
        available = CARD2_BG_CHAIN_ROW_HEIGHT - CARD2_BG_CHAIN_TEXT_TOP - CARD2_BG_CHAIN_BOTTOM_GUTTER
        overflow += max(0, content_h - available)
    return CARD2_BG_BULLETS_START_Y + len(texts[:CARD2_BG_BULLET_MAX_ITEMS]) * CARD2_BG_CHAIN_ROW_HEIGHT + overflow


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
    minute = one_minute_summary(data)
    quality = company_quality_data(data)
    country = country_lens_data(data)
    quality_texts: list[str] = []
    for key in ("valuation", "governance_incentives", "capital_allocation", "accounting_quality"):
        panel = quality.get(key) or {}
        quality_texts.extend(str(panel.get(field) or "") for field in ("finding", "evidence", "watch_item"))
    country_texts: list[str] = []
    for entry in country.get("dimensions") or []:
        country_texts.extend(str(entry.get(field) or "") for field in ("country_fact", "company_transmission", "watch_metric"))
    return {
        "Card 1 intro sentence": [cover_intro(data)],
        "Card 1 business model": [minute["business_model"]],
        "Card 1 core variables": minute["core_variables"],
        "Card 1 primary risk": [minute["primary_risk"]],
        "Card 2 background chain": [entry["text"] for entry in background_points(data)],
        "Card 2 industry paragraph": [industry_paragraph(data)],
        "Card 2 Porter evidence": [
            entry["evidence"] for entry in porter_evidence_entries(data) if entry.get("evidence")
        ],
        "Card 3 five-year narrative": [five_year_narrative(data)],
        "Card 3 inflection points": five_year_inflection_points(data),
        "Card 3 financial metrics labels": [
            f"{m['label_cn']} {m['value']} ({m['period_cn']})" for m in financial_metrics_panel(data)
        ],
        "Card 4 company quality": quality_texts,
        "Card 5 country lens": country_texts,
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
                and label != "Card 2 background chain"
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

    minute = one_minute_summary(data)
    focus = " ".join([minute["business_model"], *minute["core_variables"], minute["primary_risk"]])
    intro = cover_intro(data)
    bg_points = background_points(data)
    industry = industry_paragraph(data)
    porter_evidence = porter_evidence_entries(data)
    metrics_panel = financial_metrics_panel(data)
    five_year_text = five_year_narrative(data)
    inflection_points = five_year_inflection_points(data)
    quality = company_quality_data(data)
    country = country_lens_data(data)
    fin = finance(data)
    prof = profitability(data)
    current_income = income_current(data)
    source_revenue = as_float(current_income.get("revenue"))
    source_net = as_float(current_income.get("net_income"))
    issues.extend(
        money_scale_consistency_issues(
            data,
            fin,
            focus,
            [point["text"] for point in bg_points],
        )
    )

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
        ("Card 1 business model", minute["business_model"]),
        ("Card 1 primary risk", minute["primary_risk"]),
        ("Card 2 industry paragraph", industry),
        ("Card 3 five-year narrative", five_year_text),
    ]:
        if not is_complete_copy(text):
            issues.append(f"{label} must be a complete sentence or paragraph without ellipsis.")
    intro_font = f(FONT_INTRO)
    if len(wrap(draw, clean(intro), intro_font, 860)) > 2:
        issues.append("Card 1 intro sentence exceeds 2 lines.")
    if has_bad_linebreak(intro, 860, f(FONT_INTRO), draw):
        issues.append("Card 1 intro sentence contains a punctuation-led line break.")
    minute_rows = [minute["business_model"], minute["primary_risk"]]
    if len(minute["core_variables"]) != 2:
        issues.append("Card 1 one_minute_summary.core_variables must contain exactly two entries.")
    for idx, text in enumerate(minute_rows):
        if len(text) > 64:
            issues.append(f"Card 1 one-minute summary row[{idx}] exceeds 64 characters: {text}")
        if len(wrap(draw, clean(text), f(21), 690)) > 2:
            issues.append(f"Card 1 one-minute summary row[{idx}] exceeds two rendered lines: {text}")
    for idx, text in enumerate(minute["core_variables"]):
        if len(text) > 32:
            issues.append(f"Card 1 core variable[{idx}] exceeds 32 characters: {text}")
        if len(wrap(draw, clean(text), f(20), 666)) > 1:
            issues.append(
                f"Card 1 core variable[{idx}] must fit one aligned line; shorten the wording: {text}"
            )

    # Card 1 metric tile overflow gate. Tiles are sized at runtime as
    # (total_w - gap*(n-1)) // n with total_w=936 and gap=16, so a 3-tile row
    # is ~301px wide and a 4-tile row is ~225px wide. The drawable interior is
    # tile_w - 42 (left accent + padding). fit_font silently returns the min
    # font even when the text still overflows, so we re-measure at min size
    # here and fail loudly. Authors must shorten the label/value or drop the
    # metric — Cards 1 cannot ship text running off the tile.
    raw_metrics_row = (
        [m for m in (data.card_slots.metrics_row or []) if clean(str(m))]
        if data.card_slots and data.card_slots.metrics_row else []
    )
    if raw_metrics_row:
        slot_count = min(len(raw_metrics_row), 4)
        metric_tile_w = max(180, (936 - 16 * (slot_count - 1)) // slot_count)
        metric_text_w = metric_tile_w - 42
        label_min_font = f(FONT_METRIC_LABEL_MIN, True)
        value_min_font = f(FONT_METRIC_VALUE_MIN, True)
        for entry in raw_metrics_row[:slot_count]:
            entry_clean = clean(str(entry))
            if "|" not in entry_clean:
                issues.append(
                    f"Card 1 metrics_row entry must use 'Label|Value' format: {entry_clean!r}"
                )
                continue
            label_part, value_part = entry_clean.split("|", 1)
            label_part = clean(label_part)
            value_part = clean(value_part)
            if not label_part or not value_part:
                issues.append(
                    f"Card 1 metrics_row entry needs non-empty label and value: {entry_clean!r}"
                )
                continue
            if draw.textlength(label_part, font=label_min_font) > metric_text_w * LAYOUT_SCALE:
                issues.append(
                    f"Card 1 metrics_row label too long for tile width at min font: {label_part!r}"
                )
            if draw.textlength(value_part, font=value_min_font) > metric_text_w * LAYOUT_SCALE:
                issues.append(
                    f"Card 1 metrics_row value too long for tile width at min font: {value_part!r}"
                )

    # ---- Card 2 ----
    if len(bg_points) != 4:
        issues.append("Card 2 must contain exactly 4 background bullets.")
    actual_chain_steps = tuple(point.get("step") for point in bg_points)
    if actual_chain_steps != BACKGROUND_CHAIN_STEPS:
        issues.append(
            "Card 2 background chain must read external condition → transmission → "
            "company outcome → watch signal."
        )
    for point in bg_points:
        text = point.get("text") or ""
        if not is_complete_copy(text):
            issues.append(f"Card 2 background chain text must be a complete sentence: {text}")
        if len(text) > LIMIT_CARD2_BG_BULLET_CHARS:
            issues.append(f"Card 2 background chain text exceeds its character budget: {text}")
        chain_font = f(CARD2_BG_CHAIN_FONT)
        chain_lines = wrap(draw, clean(text), chain_font, CARD2_BG_BULLETS_TEXT_WIDTH)
        if len(chain_lines) > CARD2_BG_BULLET_MAX_LINES:
            issues.append(f"Card 2 background chain text exceeds two rendered lines: {text}")
        chain_height = sum(line_raster_height(draw, chain_font, line) for line in chain_lines)
        chain_height += CARD2_BG_BULLET_LINE_GAP * max(0, len(chain_lines) - 1)
        chain_available = CARD2_BG_CHAIN_ROW_HEIGHT - CARD2_BG_CHAIN_TEXT_TOP - CARD2_BG_CHAIN_BOTTOM_GUTTER
        if chain_height > chain_available:
            issues.append(
                "Card 2 background chain text overlaps the next step: "
                f"rendered height {chain_height}px > row allowance {chain_available}px: {text}"
            )
        if has_bad_linebreak(text, CARD2_BG_BULLETS_TEXT_WIDTH, f(CARD2_BG_CHAIN_FONT), draw):
            issues.append(f"Card 2 background chain text contains a punctuation-led line break: {text}")
    bg_end_y = card2_background_bullets_end_y(draw, bg_points)
    bg_max_y = CARD2_BG_PANEL_BOTTOM - CARD2_BG_PANEL_BOTTOM_INSET
    if bg_end_y > bg_max_y:
        issues.append(
            "Card 2 background bullets overflow their panel: "
            f"rendered end-y {bg_end_y} > max {bg_max_y}. "
            "Shorten bullets or reduce line count before rendering."
        )

    if len(industry) < 80:
        issues.append("Card 2 industry paragraph is too short.")
    if len(industry) > LIMIT_CARD2_INDUSTRY_CHARS:
        issues.append("Card 2 industry paragraph exceeds its character budget.")
    if len(wrap(draw, clean(industry), f(FONT_PANEL_BODY), 446)) > 11:
        issues.append("Card 2 industry paragraph exceeds its section box.")
    if has_bad_linebreak(industry, 446, f(FONT_PANEL_BODY), draw):
        issues.append("Card 2 industry paragraph contains a punctuation-led line break.")

    expected_forces = set(PORTER_FORCE_KEYS)
    actual_forces = {entry.get("force") for entry in porter_evidence}
    if actual_forces != expected_forces:
        issues.append(
            f"Card 2 porter_evidence must cover exactly {sorted(expected_forces)} (got {sorted(actual_forces)})."
        )
    for entry in porter_evidence:
        ev = entry.get("evidence") or ""
        if not is_complete_copy(ev):
            issues.append(f"Card 2 porter_evidence[{entry.get('force')}] must be a complete sentence: {ev}")
        if len(ev) > LIMIT_CARD2_PORTER_EVIDENCE_CHARS:
            issues.append(
                f"Card 2 porter_evidence[{entry.get('force')}] exceeds its character budget: {ev}"
            )

    # ---- Card 3 ----
    if len(five_year_text) > LIMIT_CARD3_FIVE_YEAR_NARRATIVE_CHARS:
        issues.append("Card 3 five-year narrative exceeds its character budget.")
    # Five-year-arc panel overflow: the narrative + 3 inflection bullets must
    # fit inside the panel that ends at CARD3_FIVE_YEAR_PANEL_BOTTOM. In v4 the
    # "过去 5 年的故事" subheader was removed; narrative starts higher (Y=306),
    # so there's even more slack — the panel is more generous now, but the
    # same overflow guard still catches edge cases.
    narrative_end_y = block_final_y(
        draw, five_year_text, CARD3_NARRATIVE_START_Y, 880, f(FONT_PANEL_BODY), 12,
        CARD3_NARRATIVE_MAX_LINES,
    )
    inflection_bullets_y = narrative_end_y + 22
    inflection_block_height = measure_bullets(
        draw, inflection_points[:3], 856, f(FONT_BULLET_COMPACT), 8, 8,
        max_lines_per_item=1,
    )
    inflection_end_y = inflection_bullets_y + inflection_block_height
    if inflection_end_y > CARD3_FIVE_YEAR_PANEL_BOTTOM - CARD3_FIVE_YEAR_PANEL_BOTTOM_INSET:
        issues.append(
            "Card 3 five-year arc panel overflow: narrative + inflection bullets do not fit "
            f"inside the panel (end Y={inflection_end_y}, panel bottom={CARD3_FIVE_YEAR_PANEL_BOTTOM}). "
            "Shorten the narrative or the inflection bullets."
        )
    if len(inflection_points) < 3:
        issues.append("Card 3 five_year_arc.inflection_points must contain at least 3 entries.")
    for pt in inflection_points:
        if not is_complete_copy(pt):
            issues.append(f"Card 3 inflection point must be a complete sentence: {pt}")
        if len(pt) > LIMIT_CARD3_INFLECTION_CHARS:
            issues.append(f"Card 3 inflection point exceeds its character budget: {pt}")
        if has_bad_linebreak(pt, 396, f(FONT_BULLET_COMPACT), draw):
            issues.append(f"Card 3 inflection point contains a punctuation-led line break: {pt}")
    # ---- Card 3 metrics panel (v4 frosted-glass 6-cell grid) ----
    # The v4 bottom panel replaces the old 收入分析 explainer bullets with a
    # 2×3 grid of CFA-importance financial metrics. Order is fixed (the writer
    # must place them this way so the renderer renders the right category color
    # in each cell): 0..2 = profitability, 3..4 = cash_flow, 5 = leverage.
    _EXPECTED_PANEL_LAYOUT = (
        (0, "profitability"),
        (1, "profitability"),
        (2, "profitability"),
        (3, "cash_flow"),
        (4, "cash_flow"),
        (5, "leverage"),
    )
    if len(metrics_panel) != 6:
        issues.append(
            f"Card 3 financial_metrics_panel must contain exactly 6 entries (got {len(metrics_panel)})."
        )
    else:
        for slot_idx, expected_category in _EXPECTED_PANEL_LAYOUT:
            actual = metrics_panel[slot_idx].get("category")
            if actual != expected_category:
                issues.append(
                    f"Card 3 financial_metrics_panel[{slot_idx}].category must be "
                    f"{expected_category!r} (got {actual!r}). Fixed display order: "
                    "3 profitability → 2 cash_flow → 1 leverage."
                )
    # Per-cell budget: value text must fit cleanly inside the cell. The cell
    # inner width allows ~14 CJK chars at value font size. Labels are short
    # CN nouns (毛利率 etc.) so they have generous budget. period_cn is for the
    # tiny FY/quarter footnote.
    for idx, entry in enumerate(metrics_panel):
        label = entry.get("label_cn") or ""
        value = entry.get("value") or ""
        period = entry.get("period_cn") or ""
        if len(label) > 12:
            issues.append(
                f"Card 3 financial_metrics_panel[{idx}].label_cn exceeds 12 chars ({len(label)}): {label}"
            )
        if len(value) > 14:
            issues.append(
                f"Card 3 financial_metrics_panel[{idx}].value exceeds 14 chars ({len(value)}): {value}. "
                "Compress: drop '美元'/'$', use '亿' alone; ratios use '×' or '0.5×' form."
            )
        if any(marker in value for marker in ("近似", "$", "美元")):
            issues.append(
                f"Card 3 financial_metrics_panel[{idx}].value must not contain visible "
                f"approximation/currency markers ('近似', '$', '美元'): {value}"
            )
        if "净现金" in value:
            issues.append(
                f"Card 3 financial_metrics_panel[{idx}] must put net-cash wording in "
                "label_cn='净现金' and keep value as a plain amount like '11.89亿'."
            )
        if idx == 5:
            if label == "净债务/EBITDA" and "×" not in value:
                issues.append(
                    "Card 3 financial_metrics_panel[5] label '净债务/EBITDA' requires a ratio "
                    "value like '0.5×'. Use label '净现金' for net-cash companies."
                )
            elif label in {"净现金", "净现金头寸"}:
                if "亿" not in value or "×" in value:
                    issues.append(
                        "Card 3 financial_metrics_panel[5] label '净现金' requires a plain amount "
                        "value like '11.89亿'."
                    )
            else:
                issues.append(
                    "Card 3 financial_metrics_panel[5].label_cn must be '净债务/EBITDA' "
                    "for positive net debt or '净现金' for net-cash companies."
                )
        if len(period) > 14:
            issues.append(
                f"Card 3 financial_metrics_panel[{idx}].period_cn exceeds 14 chars ({len(period)}): {period}"
            )

    # Pixel-fit the Card 3 metrics grid with the same geometry and font-size
    # fallback used by the renderer. Character counts alone are not enough for
    # mixed CJK + digits strings such as "11.89亿".
    if len(metrics_panel) == 6:
        panel_periods = [clean(str(entry.get("period_cn") or "")) for entry in metrics_panel]
        shared_period = len({normalize_period_key(p) for p in panel_periods if p}) == 1
        inner_left = CARD3_METRICS_PANEL_LEFT + CARD3_METRICS_INNER_PAD_X
        inner_right = CARD3_METRICS_PANEL_RIGHT - CARD3_METRICS_INNER_PAD_X
        inner_top = CARD3_METRICS_PANEL_TOP + CARD3_METRICS_INNER_PAD_Y
        inner_bottom = CARD3_METRICS_PANEL_BOTTOM - CARD3_METRICS_INNER_PAD_Y
        cell_w = (inner_right - inner_left) // 3
        cell_h = (inner_bottom - inner_top) // 2
        for idx, entry in enumerate(metrics_panel):
            row = idx // 3
            col = idx % 3
            cell_x = inner_left + col * cell_w
            cell_y = inner_top + row * cell_h
            strip_left = cell_x + 16
            text_x = strip_left + 24
            cell_right = inner_left + (col + 1) * cell_w
            text_max_w = cell_right - text_x - 16
            label = entry.get("label_cn") or ""
            value = entry.get("value") or ""
            period = period_display_cn(entry.get("period_cn") or "")

            label_font = f(26, True)
            value_font = fit_font_for_width(
                draw, value, text_max_w, (60, 56, 52, 48, 44, 40, 36, 32, 28), bold=True
            )
            value_bbox = draw._draw.textbbox((0, 0), value, font=value_font)
            value_w = (value_bbox[2] - value_bbox[0]) / LAYOUT_SCALE
            if value_w > text_max_w:
                issues.append(
                    f"Card 3 financial_metrics_panel[{idx}].value does not fit its cell at min font: {value}"
                )
            label_bottom = cell_y + 14 + line_raster_height(draw, label_font, label)
            value_bottom = cell_y + 52 + line_raster_height(draw, value_font, value)
            if label_bottom > cell_y + 48:
                issues.append(f"Card 3 financial_metrics_panel[{idx}].label collides with value: {label}")
            value_limit = cell_y + cell_h - (14 if shared_period else 38)
            if value_bottom > value_limit:
                issues.append(
                    f"Card 3 financial_metrics_panel[{idx}].value vertically overflows its cell: {value}"
                )
            if not shared_period:
                period_font = f(18)
                period_bbox = draw._draw.textbbox((0, 0), period, font=period_font)
                period_w = (period_bbox[2] - period_bbox[0]) / LAYOUT_SCALE
                if period_w > text_max_w:
                    issues.append(
                        f"Card 3 financial_metrics_panel[{idx}].period_cn display text does not fit: {period}"
                    )
                period_top = cell_y + cell_h - 34
                if value_bottom > period_top - 4:
                    issues.append(
                        f"Card 3 financial_metrics_panel[{idx}].value collides with period label: {value}"
                    )

    # Pixel-fit the middle revenue-flow value column. The text is renderer
    # generated, so slot reconciliation alone will not catch long currency
    # labels running past the panel.
    chart_labels = [
        chart_value_as_yi(fin["revenue"]),
        chart_value_as_yi(fin["cogs"]),
        chart_value_as_yi(fin["gross"]),
        chart_value_as_yi(fin["op"]),
        chart_value_as_yi(fin["net"]),
    ]
    chart_value_w = 1008 - 782 - 36
    for value in chart_labels:
        value_text = f"{value:.1f} 亿{_CURRENCY_LABEL}"
        value_font = fit_font_for_width(draw, value_text, chart_value_w, (FONT_CHART_VALUE, 26, 24, 22), bold=True)
        value_bbox = draw._draw.textbbox((0, 0), value_text, font=value_font)
        value_w = (value_bbox[2] - value_bbox[0]) / LAYOUT_SCALE
        if value_w > chart_value_w:
            issues.append(f"Card 3 revenue-flow value does not fit the value column: {value_text}")

    # ---- Card 4 (company quality) ----
    for section in ("valuation", "governance_incentives", "capital_allocation", "accounting_quality"):
        panel_value = quality.get(section) or {}
        for field, limit in (("finding", 60), ("evidence", 92), ("watch_item", 42)):
            text = clean(str(panel_value.get(field) or ""))
            if len(text) > limit:
                issues.append(f"Card 4 company_quality.{section}.{field} exceeds {limit} characters: {text}")
        if section == "valuation":
            for idx, metric in enumerate(panel_value.get("metrics") or []):
                if len(clean(str(metric.get("basis_label") or ""))) > 24:
                    issues.append(f"Card 4 valuation metric[{idx}].basis_label exceeds 24 characters.")
                if len(clean(str(metric.get("value") or ""))) > 18:
                    issues.append(f"Card 4 valuation metric[{idx}].value exceeds 18 characters.")
    if len(clean(str(quality.get("unknown") or ""))) > 80:
        issues.append("Card 4 company_quality.unknown exceeds 80 characters.")

    # ---- Card 5 (country lens) ----
    exposure = country.get("exposure_map") or {}
    for key in ("incorporation", "listing", "operations", "revenue"):
        if len(clean(str(exposure.get(key) or ""))) > 30:
            issues.append(f"Card 5 country_lens.exposure_map.{key} exceeds 30 characters.")
    for idx, entry in enumerate(country.get("dimensions") or []):
        for field, limit in (("country_fact", 52), ("company_transmission", 52), ("watch_metric", 30)):
            text = clean(str(entry.get(field) or ""))
            if len(text) > limit:
                issues.append(f"Card 5 country_lens.dimensions[{idx}].{field} exceeds {limit} characters: {text}")
    if len("；".join(clean(str(x)) for x in country.get("top_warnings") or [])) > 100:
        issues.append("Card 5 country_lens.top_warnings exceed the bottom-panel budget.")
    for field in ("company_to_country_insight", "unknown"):
        if len(clean(str(country.get(field) or ""))) > 90:
            issues.append(f"Card 5 country_lens.{field} exceeds 90 characters.")

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
    paste_logo(img, logo, (330, 1110, 750, 1260))


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
    draw_text(draw, (72, 1320), f"{company_short_cn(data)} | {export_date_cn()}", f(FONT_FOOTER), MUTED)


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
    """Card 1 metric cards. Writer supplies `metrics_row` entries as
    `"label|value"` strings (e.g. `"FY2026Q2 总收入|352 亿美元"`); split on
    the first `|` to fill the label/value tiles. Accent colors cycle through
    GOLD / RED / GREEN / BLUE."""
    accents = [GOLD, RED, GREEN, BLUE]
    items: list[tuple[str, str, str]] = []
    raw_entries: list[str] = []
    if data.card_slots and data.card_slots.metrics_row:
        raw_entries = [clean(x) for x in data.card_slots.metrics_row if clean(x)]
    for idx, entry in enumerate(raw_entries[:4]):
        if "|" in entry:
            label, value = entry.split("|", 1)
            label, value = clean(label), clean(value)
        else:
            # No pipe → validator should have caught this; fall back to first
            # whitespace split, and leave value empty if there is no whitespace
            # (no silent label→value mirror, which previously rendered the same
            # overflowing string in both tile lines).
            parts = entry.split(maxsplit=1)
            label = parts[0]
            value = parts[1] if len(parts) > 1 else ""
        items.append((label or "指标", value, accents[idx % len(accents)]))
    return items


def rate_metrics(data: ReportData) -> list[tuple[str, str, str]]:
    prof = profitability(data)
    margin_labels = get_nested(data.financial_data, "income_statement", "margin_labels", default={}) or {}
    return [
        (str(margin_labels.get("gross_margin") or "毛利率"), pct_text(prof.get("gross_margin_pct")), GREEN),
        (str(margin_labels.get("operating_margin") or "营业利润率"), pct_text(prof.get("operating_margin_pct")), BLUE),
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

    metrics = cover_metrics(data)
    if metrics:
        slot_count = min(len(metrics), 4)
        total_w = 936
        gap = 16
        tile_w = max(180, (total_w - gap * (slot_count - 1)) // slot_count)
        for idx, (label, value, color) in enumerate(metrics[:slot_count]):
            metric(d, 72 + idx * (tile_w + gap), 566, tile_w, label, value, color)

    draw_panel = (72, 716, 1008, 1090)
    d.rounded_rectangle(draw_panel, radius=28, fill=PANEL)
    draw_text(d, (108, 744), "一分钟理解", f(34, True), TEXT)
    minute = one_minute_summary(data)
    d.line((108, 792, 972, 792), fill=LINE, width=1)

    def minute_label(label: str, row_top: int, row_bottom: int, color: str) -> None:
        pill_y = int(round((row_top + row_bottom - 40) / 2))
        pill = (108, pill_y, 228, pill_y + 40)
        d.rounded_rectangle(pill, radius=18, fill=color)
        label_font = fit_font_for_width(d._draw, label, 96, (20, 18, 16), bold=True)
        draw_centered_text_in_rect(d, pill, label, label_font, WHITE)

    # Every label is centered inside one fixed-width capsule.  Each body is
    # centered as a measured block inside its own row rather than nudged with
    # hand-tuned baselines.
    body_rect_x = (248, 972)
    row1 = (792, 876)
    row2 = (876, 986)
    row3 = (986, 1090)

    minute_label("怎么赚钱", *row1, GREEN)
    draw_centered_block_in_rect(
        d, (body_rect_x[0], row1[0], body_rect_x[1], row1[1]),
        minute["business_model"], f(21), "#344054", line_gap=7, max_lines=2,
    )
    d.line((108, row1[1], 972, row1[1]), fill=LINE, width=1)

    minute_label("核心变量", *row2, BLUE)
    variable_font = f(20)
    variable_lines = [f"•  {variable}" for variable in minute["core_variables"]]
    variable_heights = [line_raster_height(d, variable_font, line) for line in variable_lines]
    variable_gap = 12
    variable_h = sum(variable_heights) + variable_gap
    variable_w = max(logical_text_width(d, line, variable_font) for line in variable_lines)
    variable_x = int(round(body_rect_x[0] + ((body_rect_x[1] - body_rect_x[0]) - variable_w) / 2))
    variable_y = int(round(row2[0] + ((row2[1] - row2[0]) - variable_h) / 2))
    for idx, line in enumerate(variable_lines):
        draw_text(d, (variable_x, variable_y), line, variable_font, "#344054")
        variable_y += variable_heights[idx] + (variable_gap if idx == 0 else 0)
    d.line((108, row2[1], 972, row2[1]), fill=LINE, width=1)

    minute_label("主要风险", *row3, RED)
    draw_centered_block_in_rect(
        d, (body_rect_x[0], row3[0], body_rect_x[1], row3[1]),
        minute["primary_risk"], f(21), "#344054", line_gap=7, max_lines=2,
    )
    logo_section(d, img, data)
    footer(d, data)
    return finalize_export(img)


def card_2(data: ReportData) -> Image.Image:
    """Card 2: Porter five forces — per-force evidence on the left,
    score bars on the right. Replaces the old left-side背景 + right-side
    conclusion box; evidence now lives beside its own bar so the reader sees
    the score and the reasoning together."""
    img = background()
    d = ScaledDraw(ImageDraw.Draw(img), LAYOUT_SCALE)
    header(d, 2)
    draw_text(d, (72, 198), "竞争结构 + 波特五力", f(58, True), TEXT)

    # Top: industry-structure paragraph + 4 background bullets (left + right).
    panel(d, (72, 290, 598, 720))
    draw_text(d, (108, 320), "行业结构", f(30, True), TEXT)
    block(d, industry_paragraph(data), 108, 372, 446, f(FONT_PANEL_BODY), "#344054", 13, 10)

    d.rounded_rectangle((622, 290, 1008, 720), radius=28, fill=PANEL)
    chain_colors = (GOLD, BLUE, GREEN, RED)
    for idx, entry in enumerate(background_points(data)):
        row_top = CARD2_BG_BULLETS_START_Y + idx * CARD2_BG_CHAIN_ROW_HEIGHT
        step = entry["step"]
        draw_text(
            d,
            (656, row_top),
            f"0{idx + 1}  {BACKGROUND_CHAIN_LABEL_CN[step]}",
            f(17, True),
            chain_colors[idx],
        )
        block(
            d,
            entry["text"],
            656,
            row_top + CARD2_BG_CHAIN_TEXT_TOP,
            CARD2_BG_BULLETS_WIDTH,
            f(CARD2_BG_CHAIN_FONT),
            "#344054",
            CARD2_BG_BULLET_LINE_GAP,
            CARD2_BG_BULLET_MAX_LINES,
        )
        if idx < 3:
            d.line((656, row_top + 94, 976, row_top + 94), fill=LINE, width=1)

    # Bottom: per-force evidence with score bar + evidence text.
    panel(d, (72, 740, 1008, 1240))
    draw_text(d, (108, 770), "波特五力 — 每股力量证据", f(30, True), TEXT)
    evidence_by_force = {entry["force"]: entry for entry in porter_evidence_entries(data)}
    display_order = ("supplier_power", "buyer_power", "new_entrants", "substitutes", "rivalry")
    y = 826
    for idx, force in enumerate(display_order):
        entry = evidence_by_force.get(force, {})
        score = entry.get("score") or 3
        label = PORTER_FORCE_LABEL_CN[force]
        draw_text(d, (108, y), label, f(FONT_PORTER_LABEL, True), TEXT)
        d.rounded_rectangle((216, y + 12, 416, y + 22), radius=8, fill=TRACK)
        color = PORTER_COLORS[idx] if idx < len(PORTER_COLORS) else (RED if score >= 4 else GOLD)
        d.rounded_rectangle((216, y + 12, 216 + int(200 * score / 5), y + 22), radius=8, fill=color)
        draw_text(d, (438, y - 4), f"{score}/5", f(FONT_PORTER_SCORE, True), TEXT)
        ev_text = clean(str(entry.get("evidence") or ""))
        if ev_text:
            block(d, ev_text, 496, y - 6, 488, f(FONT_PORTER_EVIDENCE), "#475467", 6, 2)
        y += 80

    footer(d, data)
    return finalize_export(img)


def card_3(data: ReportData) -> Image.Image:
    """Card 3 (v4 财务分析): five-year arc + recent quarter bars + 6-metric
    frosted-glass grid. Top panel = transformation narrative + inflection
    points (no subheader). Middle band = recent-quarter Sankey-style bars.
    Bottom panel = 2×3 Apple-style metrics grid (3 profitability + 2 cash flow
    + 1 leverage) — replaces the v3 收入分析 explainer bullets."""
    img = background()
    d = ScaledDraw(ImageDraw.Draw(img), LAYOUT_SCALE)
    header(d, 3)
    draw_text(d, (72, 198), "财务分析", f(58, True), TEXT)

    # 1) Five-year arc panel (top). v4 drops the "过去 5 年的故事" subheader
    # — the card-level title "财务分析" already frames this section, and the
    # extra subheader read as 公众号-cheap. The narrative now starts at
    # CARD3_NARRATIVE_START_Y (Y=306) instead of 346, restoring tight visual
    # rhythm at the top of the panel.
    d.rounded_rectangle((72, 270, 1008, CARD3_FIVE_YEAR_PANEL_BOTTOM), radius=28, fill=PANEL)
    narrative_end_y = block(
        d, five_year_narrative(data), 108, CARD3_NARRATIVE_START_Y, 880,
        f(FONT_PANEL_BODY), "#344054", 12, CARD3_NARRATIVE_MAX_LINES,
    )
    bullets(
        d,
        five_year_inflection_points(data),
        108,
        narrative_end_y + 22,
        880,
        max_items=3,
        max_lines=1,
        gap_after=8,
        font_size=FONT_BULLET_COMPACT,
        line_gap=8,
    )

    # 2) Current-period financial bars (middle). The data source is the same
    # `income_statement.current_year` pool used for Sankey, so the title must
    # say that period directly rather than always saying "最近季度".
    panel(d, (72, 648, 1008, 922))
    draw_text(d, (108, 676), card3_income_flow_title(data), f(30, True), TEXT)
    fin = finance(data)
    chart_labels = get_nested(data.financial_data, "income_statement", "chart_labels", default={}) or {}
    rows = [
        (str(chart_labels.get("revenue") or "总收入"), chart_value_as_yi(fin["revenue"]), GOLD),
        (str(chart_labels.get("cogs") or "营业成本"), chart_value_as_yi(fin["cogs"]), RED),
        (str(chart_labels.get("gross") or "毛利润"), chart_value_as_yi(fin["gross"]), GREEN),
        (str(chart_labels.get("op") or "营业利润"), chart_value_as_yi(fin["op"]), BLUE),
        (str(chart_labels.get("net") or "净利润"), chart_value_as_yi(fin["net"]), TEXT),
    ]
    maxv = max(abs(v) for _, v, _ in rows) or 1
    for idx, (label, value, color) in enumerate(rows):
        y = 724 + idx * 38
        draw_text(d, (108, y), label, f(FONT_CHART_LABEL), "#475467")
        d.rounded_rectangle((244, y + 6, 744, y + 24), radius=9, fill=TRACK)
        bar_color = RED if value < 0 else color
        d.rounded_rectangle((244, y + 6, 244 + int(500 * abs(value) / maxv), y + 24), radius=9, fill=bar_color)
        value_text = f"{value:.1f} 亿{_CURRENCY_LABEL}"
        value_font = fit_font_for_width(d._draw, value_text, 1008 - 782 - 36, (FONT_CHART_VALUE, 26, 24, 22), bold=True)
        draw_text(d, (782, y - 4), value_text, value_font, TEXT)

    # 3) Frosted-glass 6-metric grid (bottom). See _draw_card3_metrics_panel.
    _draw_card3_metrics_panel(d, data)
    footer(d, data)
    return finalize_export(img)


def _draw_card3_metrics_panel(d: "ScaledDraw", data: ReportData) -> None:
    """Apple-style frosted-glass 2×3 metric grid at the bottom of Card 3.

    Authoritative source: ``card_slots.financial_metrics_panel`` (6 entries,
    fixed display order — see assert_card_slots_complete and validate_report).

    Design intent: the panel reads as an elevated, translucent surface above
    the warm card body. Big numbers carry the hierarchy; the label and period
    are quiet. Category tells the cell where to draw its accent (left-edge
    color strip + value color):

      - profitability → GREEN  (mint, comparable across companies)
      - cash_flow     → BLUE   (capital returns / liquidity)
      - leverage      → RED    (risk / debt)

    The grid uses hairline dividers rather than gaps between cells, so the six
    metrics feel like one continuous surface — closer to an Apple Watch
    activity grid than to six independent tiles. Values follow the convention:
        % ratios          → "75.7%"   (≤6 chars)
        亿 currency        → "23.37亿" (≤8 chars; no '$' or '美元' inside cell)
        Net-cash variant   → label "净现金" + value "24.56亿"
        Net Debt / EBITDA  → label "净债务/EBITDA" + value "0.5×"
    """
    pl = CARD3_METRICS_PANEL_LEFT
    pt = CARD3_METRICS_PANEL_TOP
    pr = CARD3_METRICS_PANEL_RIGHT
    pb = CARD3_METRICS_PANEL_BOTTOM

    # Frosted-glass base: lighter than PANEL_CREAM with a hairline outline.
    # The outline gives the panel an "Apple card" elevation feel without
    # needing a real Gaussian-blurred backdrop (which a static PIL canvas
    # cannot fake convincingly).
    d.rounded_rectangle((pl, pt, pr, pb), radius=28, fill=PANEL_GLASS)
    d.rounded_rectangle((pl, pt, pr, pb), radius=28, outline=GLASS_STROKE, width=2)

    metrics = financial_metrics_panel(data)
    if len(metrics) != 6:
        # Validator should have caught this; fail loudly here so a malformed
        # slot file never silently truncates the grid.
        raise RuntimeError(
            f"Card 3 financial_metrics_panel must contain exactly 6 entries; got {len(metrics)}."
        )

    panel_periods = [clean(str(metric.get("period_cn") or "")) for metric in metrics]
    unique_period_keys = {normalize_period_key(period) for period in panel_periods if period}
    shared_period = ""
    if len(unique_period_keys) == 1:
        shared_period = next((period for period in panel_periods if period), "")
    if shared_period:
        period_caption = f"{period_display_cn(shared_period)}口径"
        caption_font = fit_font_for_width(d._draw, period_caption, 210, (18, 16, 14), bold=True)
        bbox = d._draw.textbbox((0, 0), period_caption, font=caption_font)
        caption_w = (bbox[2] - bbox[0]) / LAYOUT_SCALE
        draw_text(d, (int(pr - CARD3_METRICS_INNER_PAD_X - caption_w), pt + 22), period_caption, caption_font, GLASS_PERIOD)

    # 2 rows × 3 cols
    inner_left = pl + CARD3_METRICS_INNER_PAD_X
    inner_right = pr - CARD3_METRICS_INNER_PAD_X
    inner_top = pt + CARD3_METRICS_INNER_PAD_Y
    inner_bottom = pb - CARD3_METRICS_INNER_PAD_Y
    cell_w = (inner_right - inner_left) // 3
    cell_h = (inner_bottom - inner_top) // 2

    # Hairline dividers — vertical (between cols 1|2 and 2|3) and horizontal
    # (between row 1 and row 2). Inset slightly from the panel edges so the
    # divider does not visually touch the rounded border.
    inset = CARD3_METRICS_DIVIDER_INSET
    for col in (1, 2):
        x = inner_left + col * cell_w
        d.line((x, pt + inset, x, pb - inset), fill=GLASS_DIVIDER, width=2)
    y_div = inner_top + cell_h
    d.line((pl + inset, y_div, pr - inset, y_div), fill=GLASS_DIVIDER, width=2)

    accent_for_category = {
        "profitability": GREEN,
        "cash_flow": BLUE,
        "leverage": RED,
    }

    for idx, metric in enumerate(metrics):
        row = idx // 3
        col = idx % 3
        cell_x = inner_left + col * cell_w
        cell_y = inner_top + row * cell_h
        accent = accent_for_category.get(metric.get("category"), TEXT)

        # Left-edge accent strip: 4px wide vertical bar, 60% of cell height,
        # centered vertically. This is the only chromatic element per cell —
        # everything else is grayscale typography, so the grid reads as
        # quiet/elegant rather than busy.
        strip_height = int(cell_h * 0.58)
        strip_top = cell_y + (cell_h - strip_height) // 2
        strip_left = cell_x + 16
        d.rounded_rectangle(
            (strip_left, strip_top, strip_left + 5, strip_top + strip_height),
            radius=3, fill=accent,
        )

        # Text column starts 24px right of the strip. The available text width
        # is the distance from text_x to the next column's accent strip (or to
        # the panel edge for the last column), minus a 16px right gutter.
        text_x = strip_left + 24
        cell_right = inner_left + (col + 1) * cell_w
        text_max_w = cell_right - text_x - 16

        # Label (e.g. 毛利率) — small medium-weight gray. Always fits at 26.
        label = metric.get("label_cn") or ""
        draw_text(d, (text_x, cell_y + 14), label, f(26, True), GLASS_LABEL)

        # Value — the big number. Auto-shrink from target_size down to a
        # readable floor so values like "11.89亿" or longer ratios
        # (CJK + digits + 亿) actually fit inside the cell. Crude char-length
        # heuristics fail because CJK glyphs are ~2× as wide as digits in the
        # default font; bbox-measure to be safe.
        value = metric.get("value") or ""
        value_font = None
        for size in (60, 56, 52, 48, 44, 40, 36, 32, 28):
            candidate = f(size, True)
            # ScaledDraw exposes the underlying ImageDraw via ._draw; measure
            # in logical pixels because LAYOUT_SCALE multiplication is applied
            # by draw_text/text positioning code.
            bbox = d._draw.textbbox((0, 0), value, font=candidate)
            text_w = (bbox[2] - bbox[0]) / LAYOUT_SCALE
            if text_w <= text_max_w:
                value_font = candidate
                break
        if value_font is None:
            value_font = f(28, True)
        draw_text(d, (text_x, cell_y + 52), value, value_font, accent)

        # Period only renders per cell when mixed periods are intentional.
        # When all six metrics share one FY/LTM/Q period, a single panel-level
        # caption avoids the visual noise of repeating "FY2025" six times.
        period = period_display_cn(metric.get("period_cn") or "")
        if not shared_period:
            draw_text(d, (text_x, cell_y + cell_h - 34), period, f(18), GLASS_PERIOD)


CARD4_CONTENT_X = CARD4_PANEL_LEFT + CARD4_INNER_PAD
CARD4_CONCEPT_TITLE_Y = CARD4_PANEL_TOP + 28
CARD4_SUBHEAD_GAP = 8
CARD4_SECTION_GAP = 22
CARD4_FORMULA_FONT_SIZE = 30


def _card4_layout(
    draw: ImageDraw.ImageDraw,
    lens: dict[str, Any],
) -> dict[str, int]:
    """Compute Y-coordinates for the merged Card 4 panel based on rendered
    heights of each block. Used by both the renderer and the validator
    pre-check so they agree on overflow."""
    inner_w = CARD4_INNER_W
    concept_label = lens.get("concept_name_cn") or lens.get("concept_key") or "CFA 概念"
    title_font = _fit_serif(draw, concept_label, inner_w, 56, 36)
    title_y = CARD4_CONCEPT_TITLE_Y
    title_end = title_y + line_raster_height(draw, title_font, concept_label)

    formula_label_y = title_end + CARD4_SECTION_GAP
    formula_label_h = line_raster_height(draw, f(22, True), "公式")
    formula_text_y = formula_label_y + formula_label_h + CARD4_SUBHEAD_GAP
    formula_font = fit_block_font(
        draw, lens.get("formula") or "—", inner_w, 9999,
        start_size=CARD4_FORMULA_FONT_SIZE, min_size=20, line_gap=8, max_lines=2, bold=True,
    )
    formula_end = block_final_y(
        draw, lens.get("formula") or "", formula_text_y, inner_w, formula_font, 8, 2,
    )

    intro_text_y = formula_end + CARD4_SECTION_GAP
    intro_end = block_final_y(
        draw, lens.get("concept_intro") or "", intro_text_y, inner_w,
        f(FONT_CFA_BODY), 10, 4,
    )

    calc_label_y = intro_end + CARD4_SECTION_GAP
    calc_label_h = line_raster_height(draw, f(22, True), "在这家公司怎么算")
    calc_text_y = calc_label_y + calc_label_h + CARD4_SUBHEAD_GAP

    calc_lines = lens.get("company_calculation") or []
    calc_end = calc_text_y
    arrow_marker_font = f(FONT_CFA_BODY, True)
    for entry in calc_lines:
        calc_end = block_final_y(
            draw, entry, calc_end, inner_w - 28, arrow_marker_font, 8, 3,
        )
        calc_end += 10

    return {
        "inner_w": inner_w,
        "title_font": title_font,
        "title_y": title_y,
        "title_end": title_end,
        "formula_label_y": formula_label_y,
        "formula_text_y": formula_text_y,
        "formula_font": formula_font,
        "formula_end": formula_end,
        "intro_text_y": intro_text_y,
        "intro_end": intro_end,
        "calc_label_y": calc_label_y,
        "calc_text_y": calc_text_y,
        "calc_end": calc_end,
    }


def card_4_upper_block_end_y(draw: ImageDraw.ImageDraw, lens: dict[str, Any]) -> int:
    return _card4_layout(draw, lens)["calc_end"]


def card_4_lower_block_end_y(draw: ImageDraw.ImageDraw, lens: dict[str, Any]) -> int:
    """Two-column footer below the divider. Returns the larger of the two
    columns' rendered end-Y. The left column has bulleted application points;
    the right column has the insight paragraph."""
    y_top = CARD4_TWO_COL_TOP_Y
    sub_h = line_raster_height(draw, f(24, True), "用到这家公司")
    body_y = y_top + sub_h + 14

    left_y = body_y
    for item in (lens.get("company_application") or [])[:3]:
        left_y = block_final_y(
            draw, item, left_y, CARD4_LEFT_COL_W - 24, f(FONT_BULLET_COMPACT), 8, 3,
        )
        left_y += 12

    right_y = block_final_y(
        draw, lens.get("different_angle_insight") or "",
        body_y, CARD4_RIGHT_COL_W, f(FONT_CFA_BODY), 10, 10,
    )
    return max(left_y, right_y)


def card_4_cfa(data: ReportData) -> Image.Image:
    """Card 4: one merged cream panel teaching a CFA L2 concept through the
    company. Upper block: concept title + formula + concept_intro +
    company_calculation. Divider. Lower block (two columns): bulleted
    application | insight paragraph."""
    img = background()
    d = ScaledDraw(ImageDraw.Draw(img), LAYOUT_SCALE)
    header(d, 4)

    lens = cfa_lens_data(data)
    geom = _card4_layout(d, lens)

    d.rounded_rectangle(
        (CARD4_PANEL_LEFT, CARD4_PANEL_TOP, CARD4_PANEL_RIGHT, CARD4_PANEL_BOTTOM),
        radius=28, fill=PANEL_CREAM,
    )

    concept_label = lens.get("concept_name_cn") or lens.get("concept_key") or "CFA 概念"
    draw_text(d, (CARD4_CONTENT_X, geom["title_y"]), concept_label, geom["title_font"], RED)

    draw_text(d, (CARD4_CONTENT_X, geom["formula_label_y"]), "公式", f(22, True), MUTED)
    block(
        d, lens.get("formula") or "—",
        CARD4_CONTENT_X, geom["formula_text_y"], geom["inner_w"],
        geom["formula_font"], TEXT, 8, 2,
    )

    block(
        d, lens.get("concept_intro") or "",
        CARD4_CONTENT_X, geom["intro_text_y"], geom["inner_w"],
        f(FONT_CFA_BODY), "#344054", 10, 4,
    )

    draw_text(d, (CARD4_CONTENT_X, geom["calc_label_y"]), "在这家公司怎么算", f(22, True), MUTED)
    calc_y = geom["calc_text_y"]
    marker_font = f(FONT_CFA_BODY, True)
    for idx, entry in enumerate(lens.get("company_calculation") or []):
        marker = f"{idx + 1}. " if idx < len(lens.get("company_calculation") or []) - 1 else "→ "
        marker_w_px = d.textlength(marker, font=marker_font)
        marker_w = int(marker_w_px / LAYOUT_SCALE) + 4
        draw_text(d, (CARD4_CONTENT_X, calc_y), marker, marker_font, RED)
        calc_y = block(
            d, entry,
            CARD4_CONTENT_X + marker_w, calc_y, geom["inner_w"] - marker_w,
            f(FONT_CFA_BODY), TEXT, 8, 3,
        )
        calc_y += 10

    d.line(
        (CARD4_CONTENT_X, CARD4_DIVIDER_Y, CARD4_PANEL_RIGHT - CARD4_INNER_PAD, CARD4_DIVIDER_Y),
        fill=LINE, width=2,
    )

    sub_y = CARD4_TWO_COL_TOP_Y
    body_y = sub_y + line_raster_height(d, f(24, True), "用到这家公司") + 14

    draw_text(d, (CARD4_CONTENT_X, sub_y), "用到这家公司", f(24, True), TEXT)
    bullets(
        d,
        lens["company_application"],
        CARD4_CONTENT_X,
        body_y,
        CARD4_LEFT_COL_W,
        max_items=3,
        max_lines=3,
        gap_after=12,
        font_size=FONT_BULLET_COMPACT,
        line_gap=8,
    )

    draw_text(d, (CARD4_RIGHT_COL_X, sub_y), "不同角度看到了什么", f(24, True), TEXT)
    block(
        d, lens["different_angle_insight"],
        CARD4_RIGHT_COL_X, body_y, CARD4_RIGHT_COL_W,
        f(FONT_CFA_BODY), "#344054", 10, 12,
    )

    footer(d, data)
    return finalize_export(img)


def _quality_panel(
    d: ScaledDraw,
    rect: tuple[int, int, int, int],
    title: str,
    value: dict[str, Any],
    accent: str,
) -> None:
    left, top, right, bottom = rect
    d.rounded_rectangle(rect, radius=26, fill=PANEL_GLASS, outline=GLASS_STROKE, width=2)
    d.rounded_rectangle((left, top, left + 8, bottom), radius=4, fill=accent)
    draw_text(d, (left + 30, top + 24), title, f(27, True), TEXT)
    y = top + 72
    y = block(d, clean(str(value.get("finding") or "")), left + 30, y, right - left - 56, f(22, True), TEXT, 7, 3)
    y += 14
    draw_text(d, (left + 30, y), "证据", f(18, True), MUTED)
    y += 28
    y = block(d, clean(str(value.get("evidence") or "")), left + 30, y, right - left - 56, f(19), "#475467", 6, 3)
    y += 14
    draw_text(d, (left + 30, y), "下一项观察", f(18, True), accent)
    block(d, clean(str(value.get("watch_item") or "")), left + 142, y - 2, right - left - 168, f(18), "#475467", 5, 2)


def card_4_company_quality(data: ReportData) -> Image.Image:
    """Card 4: market pricing, governance, capital allocation and accounting quality."""
    img = background()
    d = ScaledDraw(ImageDraw.Draw(img), LAYOUT_SCALE)
    header(d, 4)
    draw_text(d, (72, 198), "公司质量体检", f(58, True), TEXT)
    quality = company_quality_data(data)
    panels = (
        ((72, 286, 526, 714), "估值与市场定价", quality["valuation"], GOLD),
        ((554, 286, 1008, 714), "治理与激励", quality["governance_incentives"], BLUE),
        ((72, 742, 526, 1170), "资本配置", quality["capital_allocation"], GREEN),
        ((554, 742, 1008, 1170), "会计质量", quality["accounting_quality"], RED),
    )
    for rect, title, panel_value, accent in panels:
        _quality_panel(d, rect, title, panel_value, accent)

    valuation = quality["valuation"]
    metrics = valuation.get("metrics") or []
    if metrics:
        metric_text = "  ·  ".join(
            f"{m.get('label_cn')} {m.get('value')}（{m.get('basis_label')}，{m.get('as_of_date')}）"
            for m in metrics[:2]
        )
        block(d, metric_text, 100, 1190, 880, f(17), MUTED, 5, 2)
    block(d, f"仍未知：{quality.get('unknown')}", 100, 1250, 880, f(18), RED, 5, 2)
    footer(d, data)
    return finalize_export(img)


def _country_dimension_panel(
    d: ScaledDraw,
    rect: tuple[int, int, int, int],
    entry: dict[str, Any],
    accent: str,
) -> None:
    left, top, right, bottom = rect
    d.rounded_rectangle(rect, radius=22, fill=PANEL_GLASS, outline=GLASS_STROKE, width=2)
    draw_text(d, (left + 22, top + 20), clean(str(entry.get("label_cn") or "")), f(24, True), accent)
    y = block(d, clean(str(entry.get("country_fact") or "")), left + 22, top + 62, right - left - 44, f(18), TEXT, 5, 3)
    y += 9
    y = block(d, "→ " + clean(str(entry.get("company_transmission") or "")), left + 22, y, right - left - 44, f(18, True), "#344054", 5, 3)
    y += 9
    block(d, "观察：" + clean(str(entry.get("watch_metric") or "")), left + 22, y, right - left - 44, f(16), MUTED, 4, 2)


def card_5_country_lens(data: ReportData) -> Image.Image:
    """Card 5: balanced country institutions → company transmission map."""
    img = background()
    d = ScaledDraw(ImageDraw.Draw(img), LAYOUT_SCALE)
    header(d, 5)
    draw_text(d, (72, 198), "从公司看国家", f(58, True), TEXT)
    lens = country_lens_data(data)
    exposure = lens["exposure_map"]
    exposure_text = (
        f"注册 {exposure['incorporation']}  ·  上市 {exposure['listing']}  ·  "
        f"经营 {exposure['operations']}  ·  收入 {exposure['revenue']}"
    )
    d.rounded_rectangle((72, 282, 1008, 374), radius=24, fill=PANEL)
    block(d, exposure_text, 104, 310, 872, f(21, True), TEXT, 6, 2)

    accents = (GOLD, BLUE, RED, GREEN, ORANGE, PORTER_COLORS[4] if len(PORTER_COLORS) > 4 else BLUE)
    grid_left, grid_top = 72, 402
    # Leave a deliberate gutter between the second panel row and the warning
    # band.  The v5 warning is a separate conclusion, not a seventh panel.
    cell_w, cell_h, gap = 296, 298, 24
    for idx, entry in enumerate(lens["dimensions"]):
        row, col = divmod(idx, 3)
        left = grid_left + col * (cell_w + gap)
        top = grid_top + row * (cell_h + gap)
        _country_dimension_panel(d, (left, top, left + cell_w, top + cell_h), entry, accents[idx])

    warnings = "；".join(clean(str(x)) for x in lens.get("top_warnings") or [])
    block(d, f"公司级预警：{warnings}", 88, 1054, 904, f(19, True), RED, 6, 2)
    block(d, f"国家特征：{lens.get('company_to_country_insight')}", 88, 1120, 904, f(18), TEXT, 6, 2)
    block(d, f"仍未知：{lens.get('unknown')}", 88, 1184, 904, f(18), MUTED, 6, 2)
    footer(d, data)
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
    images = [
        card_1(data),
        card_2(data),
        card_3(data),
        card_4_company_quality(data),
        card_5_country_lens(data),
    ]
    assert len(images) == len(CARD_FILENAMES), (
        f"Card renderer count drift: {len(images)} images vs {len(CARD_FILENAMES)} filenames."
    )
    paths = []
    for name, img in zip(CARD_FILENAMES, images):
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


def resolve_palette(cli_palette: str | None) -> str:
    """Resolve CLI palette; omitted values are blocked by the workflow gate."""
    if cli_palette is not None:
        return cli_palette
    raise SystemExit(
        "Missing required --palette. Ask the customer to choose macaron | default | b | c before validation/export."
    )


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
            "配色：macaron | default | b | c。必须由客户确认后显式传入。"
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
