from PIL import Image, ImageDraw

from scripts.generate_social_cards import (
    BG,
    CARD2_BG_PANEL_BOTTOM,
    CARD2_BG_PANEL_BOTTOM_INSET,
    H,
    W,
    ScaledDraw,
    card2_background_bullets_end_y,
)


def _draw() -> ScaledDraw:
    return ScaledDraw(ImageDraw.Draw(Image.new("RGB", (W, H), BG)), 1)


def test_card2_background_bullets_detects_stacked_overflow() -> None:
    overflowing_points = [
        "2025财年收入28.84亿美元，同比增2.7%，净利润1.63亿美元。",
        "2026财年一季度主站GMS为24.60亿美元，同比增5.5%。",
        "活跃买家环比恢复增长，单买家消费连续改善。",
        "2025财年自由现金流6.78亿美元，现金缓冲仍充足。",
    ]

    max_y = CARD2_BG_PANEL_BOTTOM - CARD2_BG_PANEL_BOTTOM_INSET

    assert card2_background_bullets_end_y(_draw(), overflowing_points) > max_y


def test_card2_background_bullets_accepts_compact_copy() -> None:
    fitting_points = [
        "2025财年收入28.84亿美元，净利1.63亿美元。",
        "一季度主站GMS同比增长5.5%。",
        "活跃买家环比恢复，单买家消费改善。",
        "2025财年FCF为6.78亿美元。",
    ]

    max_y = CARD2_BG_PANEL_BOTTOM - CARD2_BG_PANEL_BOTTOM_INSET

    assert card2_background_bullets_end_y(_draw(), fitting_points) <= max_y
