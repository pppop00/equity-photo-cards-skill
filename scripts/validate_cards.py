#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from generate_social_cards import load_card_slots, parse_html, set_currency_label, validate_report


def input_files(src: Path) -> list[Path]:
    return [src] if src.is_file() else sorted(src.glob("*.html"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Validation agent for equity social cards.")
    parser.add_argument("--input", required=True, help="HTML file or folder.")
    parser.add_argument("--brand", default="金融豹", help="Brand name.")
    parser.add_argument("--slots", default=None, help="Optional card_slots.json to validate with agent copy.")
    args = parser.parse_args()

    src = Path(args.input).expanduser().resolve()
    slots_path = Path(args.slots).expanduser().resolve() if args.slots else None
    files = input_files(src)
    if not files:
        raise SystemExit(f"No HTML files found at: {src}")

    for html in files:
        data = parse_html(html)
        if slots_path is not None:
            data.card_slots = load_card_slots(slots_path)
        set_currency_label(data)
        validate_report(data, args.brand)
        print(f"validated: {html}")


if __name__ == "__main__":
    main()
