#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from generate_social_cards import parse_html, validate_report, set_currency_label


def input_files(src: Path) -> list[Path]:
    return [src] if src.is_file() else sorted(src.glob("*.html"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Validation agent for equity social cards.")
    parser.add_argument("--input", required=True, help="HTML file or folder.")
    parser.add_argument("--brand", default="金融豹", help="Brand name.")
    args = parser.parse_args()

    src = Path(args.input).expanduser().resolve()
    files = input_files(src)
    if not files:
        raise SystemExit(f"No HTML files found at: {src}")

    for html in files:
        data = parse_html(html)
        set_currency_label(data)
        validate_report(data, args.brand)
        print(f"validated: {html}")


if __name__ == "__main__":
    main()
