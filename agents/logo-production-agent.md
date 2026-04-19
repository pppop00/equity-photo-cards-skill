# Logo Production Agent

Run this agent for every new report after palette confirmation and **before** content agents finalize body copy in `card_slots.json` (logo path + cover name must exist for downstream steps and Validator 1).

## Goal

Create one clean company logo asset for Card 1, set `logo_asset_path` in `card_slots.json`, and set **`cover_company_name_cn`** — the **verified Chinese short name** used for Card 1’s red company line and the same string family as footers / post-title seed in the renderer (`company_short_cn()`).

## Inputs

- Report HTML: read **`.company-name-cn`**, **`.company-name-en`**, and ticker line (same fields the renderer uses for identity).
- Output folder for the current report, usually `output/<html_stem>/`.

## Chinese display name (`cover_company_name_cn`)

You **own** the canonical short Chinese name whenever you set **`logo_asset_path`**. The renderer **always** uses `cover_company_name_cn` for Card 1 red text when a logo path is present; it does not guess or auto-translate.

1. **If `.company-name-cn` contains CJK:** Treat it as the report’s Chinese label. **Reconcile** with the English line and IR/brand usage if needed, then write the **short** form into `cover_company_name_cn` (omit trailing **`公司`** in the slot text — the script may strip it, but prefer not ending with `公司`).
2. **If `.company-name-cn` is English-only** (common for ADRs): Resolve the **correct Chinese short name** for this issuer (official IR / brand / exchange brief + web search), write it into `cover_company_name_cn`.
3. **Validator 1:** Requires **`cover_company_name_cn`** whenever **`logo_asset_path`** is set, and requires the resolved string to contain CJK and not end with `公司`.

Later agents (**content production**, layout) must **not overwrite or clear** `cover_company_name_cn` or `logo_asset_path` once you set them.

## Rules

1. **Always search the web.** Do not rely on local logo discovery. Local files are outputs only.
2. **Prefer official sources:** company brand center, press kit, media kit, investor relations, website header assets, or CDN files referenced by those pages.
3. **No screenshots.** Do not paste webpage screenshots, search-result thumbnails, or cropped screen captures into Card 1.
4. **Regenerate a clean asset:** use official SVG/PNG source as reference, then produce a clean transparent PNG/WEBP suitable for rendering. Prefer converting official SVG/vector to PNG. If only raster exists, crop/clean it into a transparent wordmark. For simple wordmarks, redraw from the official reference with matching text, color, proportions, and spacing rather than using a noisy crop.
5. **Minimum pixel size (sharp Card 1):** The renderer’s logo slot is **840×288 px** at `LAYOUT_SCALE=2` (logical box 420×144). **Never** use favicons, social avatars, app icons, or search-result thumbnails as the final asset. **Never upscale** a small bitmap — that produces the soft “糊” look. For **horizontal wordmarks** (wider than tall), export so **width ≥ 840 px**. For **tall marks**, **height ≥ 288 px**. For **square / near-square** marks, **longest side ≥ 512 px**. Prefer SVG → rasterize at **≥2×** the slot width (e.g. **≥1680 px** wide for wordmarks) when the brand provides SVG, then you can downscale; the validator enforces the minimums above.
6. **Keep it modest:** the final asset should be a clean wordmark or official logo mark, not a full brand banner.
7. **If official logo cannot be found:** Stop immediately. Do not proceed to content production. Request the customer to provide:
   - Official logo source URL or file, or
   - Explicit confirmation that logo production should be skipped (customer waives logo requirement).

   Never synthesize a ticker-letter placeholder or use a low-quality substitute. Logo is P0 — do not pass this stage without resolution.

## Output

**Order matters — follow this sequence exactly:**

1. **Create the output folder first** — determine where the final 6 PNGs will land (the folder passed as `--output-root/<stem>/`, or the default `output/<html_stem>/` inside the EP skill repo). Create it now if it does not exist.
2. **Save the logo into that same output folder** — `<output_folder>/logo_official.png` (or `.webp`). Never save it to the report source folder or a temp path.
3. **Set `logo_asset_path`** in `card_slots.json` to the absolute path of the saved logo file.
4. **Set `cover_company_name_cn`** in the same `card_slots.json` to the verified Chinese short name (see § Chinese display name above). Required whenever `logo_asset_path` is set.
5. **Then** hand off to content production (which fills the rest of the slots without removing these two keys).

This order guarantees the logo and the 6 PNGs are always co-located in the same folder, so nothing needs to be moved manually after export.

- Record the source URL in working notes when available.
- After PNG export, keep only the file referenced by `logo_asset_path`. Delete downloaded source logos, rejected variants, and temporary folders such as `logo_sources/`.

## Quality Check

- Transparent or visually clean background.
- No visible browser chrome, page background, watermark, or screenshot artifacts.
- Logo remains readable when rendered inside Card 1's fixed logo area.
- Bitmap meets the **minimum pixel size** rule above so `validate_cards.py` passes (wide wordmarks **≥840 px** wide, etc.).
