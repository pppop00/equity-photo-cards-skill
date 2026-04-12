# Logo Production Agent

Run this agent for every new report after palette confirmation and before final `card_slots.json` validation/export.

## Goal

Create one clean company logo asset for Card 1, then set `logo_asset_path` in `card_slots.json`.

## Inputs

- Company Chinese name, English name, and ticker from the report HTML.
- Output folder for the current report, usually `output/<html_stem>/`.

## Rules

1. **Always search the web.** Do not rely on local logo discovery. Local files are outputs only.
2. **Prefer official sources:** company brand center, press kit, media kit, investor relations, website header assets, or CDN files referenced by those pages.
3. **No screenshots.** Do not paste webpage screenshots, search-result thumbnails, or cropped screen captures into Card 1.
4. **Regenerate a clean asset:** use official SVG/PNG source as reference, then produce a clean transparent PNG/WEBP suitable for rendering. Prefer converting official SVG/vector to PNG. If only raster exists, crop/clean it into a transparent wordmark. For simple wordmarks, redraw from the official reference with matching text, color, proportions, and spacing rather than using a noisy crop.
5. **Minimum pixel size (sharp Card 1):** The renderer’s logo slot is **840×288 px** at `LAYOUT_SCALE=2` (logical box 420×144). **Never** use favicons, social avatars, app icons, or search-result thumbnails as the final asset. **Never upscale** a small bitmap — that produces the soft “糊” look. For **horizontal wordmarks** (wider than tall), export so **width ≥ 840 px**. For **tall marks**, **height ≥ 288 px**. For **square / near-square** marks, **longest side ≥ 512 px**. Prefer SVG → rasterize at **≥2×** the slot width (e.g. **≥1680 px** wide for wordmarks) when the brand provides SVG, then you can downscale; the validator enforces the minimums above.
6. **Keep it modest:** the final asset should be a clean wordmark or official logo mark, not a full brand banner.
7. **If confidence is low, omit `logo_asset_path`.** Never synthesize a ticker-letter placeholder.

## Output

- Save the generated logo asset as `output/<html_stem>/logo_official.png` or `logo_official.webp`.
- Record the source URL in working notes when available.
- Set `logo_asset_path` in `card_slots.json` to the saved asset path.
- After PNG export, keep only the file referenced by `logo_asset_path`. Delete downloaded source logos, rejected variants, and temporary folders such as `logo_sources/`.

## Quality Check

- Transparent or visually clean background.
- No visible browser chrome, page background, watermark, or screenshot artifacts.
- Logo remains readable when rendered inside Card 1's fixed logo area.
- Bitmap meets the **minimum pixel size** rule above so `validate_cards.py` passes (wide wordmarks **≥840 px** wide, etc.).
