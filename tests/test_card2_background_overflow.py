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
        {"step": "external_condition", "text": "据行业与监管数据，外部需求、供应约束、通胀、汇率和政策条件正在同时发生变化并形成压力。"},
        {"step": "transmission", "text": "这些变化先经过价格、销量、采购成本、工资和资本开支，再逐层传导到公司的经营结果。"},
        {"step": "company_outcome", "text": "公司收入增长但毛利率和自由现金流承压，区域之间的经营质量也出现明显而持续的分化。"},
        {"step": "watch_signal", "text": "下一期同时观察同店销售、全价售罄率、采购成本率、经营现金流与资本回报是否沿这条路径变化。"},
    ]

    max_y = CARD2_BG_PANEL_BOTTOM - CARD2_BG_PANEL_BOTTOM_INSET

    assert card2_background_bullets_end_y(_draw(), overflowing_points) > max_y


def test_card2_background_bullets_accepts_compact_copy() -> None:
    fitting_points = [
        {"step": "external_condition", "text": "据行业数据，服装需求转弱。"},
        {"step": "transmission", "text": "折扣先压低全价售罄率。"},
        {"step": "company_outcome", "text": "毛利率与现金流随之承压。"},
        {"step": "watch_signal", "text": "观察同店客流与折扣率。"},
    ]

    max_y = CARD2_BG_PANEL_BOTTOM - CARD2_BG_PANEL_BOTTOM_INSET

    assert card2_background_bullets_end_y(_draw(), fitting_points) <= max_y
