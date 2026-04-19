#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from generate_social_cards import load_card_slots, parse_html, resolve_slots_path, set_currency_label, validate_report


def input_files(src: Path) -> list[Path]:
    return [src] if src.is_file() else sorted(src.glob("*.html"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Validation agent for equity social cards.")
    parser.add_argument("--input", required=True, help="HTML file or folder.")
    parser.add_argument("--brand", default="金融豹", help="Brand name.")
    parser.add_argument(
        "--slots",
        required=True,
        help="Path to card_slots.json (single HTML), or directory of <stem>.card_slots.json (batch).",
    )
    parser.add_argument(
        "--allow-no-logo",
        action="store_true",
        help="Allow validation without logo_asset_path (customer explicitly waived logo). Default: require logo.",
    )
    args = parser.parse_args()

    src = Path(args.input).expanduser().resolve()
    files = input_files(src)
    if not files:
        raise SystemExit(f"No HTML files found at: {src}")
    multiple = len(files) > 1

    for html in files:
        data = parse_html(html)
        slots_path = resolve_slots_path(html, Path(args.slots), multiple_html=multiple)
        data.card_slots = load_card_slots(slots_path)
        set_currency_label(data)
        validate_report(data, args.brand, allow_no_logo=args.allow_no_logo)
        print(f"validated: {html}")


if __name__ == "__main__":
    main()
