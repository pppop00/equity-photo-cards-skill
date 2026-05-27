#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from generate_social_cards import (
    apply_palette,
    load_card_slots,
    parse_html,
    resolve_slots_path,
    set_currency_label,
    validate_card1_4_analytical_content,
    validate_report,
)


def input_files(src: Path) -> list[Path]:
    return [src] if src.is_file() else sorted(src.glob("*.html"))


def worker_notes_path_for(slots_path: Path) -> Path:
    """Return the convention-mate worker_notes sibling for a given slots path.

    Convention: if `slots_path` is `<dir>/<stem>.card_slots.json`,
    worker notes live at `<dir>/<stem>.card_slots_worker_notes.json`.
    """
    name = slots_path.name
    if name.endswith(".card_slots.json"):
        stem = name[: -len(".card_slots.json")]
    else:
        stem = slots_path.stem
    return slots_path.with_name(f"{stem}.card_slots_worker_notes.json")


def load_worker_notes(slots_path: Path) -> dict | None:
    """Load <stem>.card_slots_worker_notes.json if present, else return None."""
    notes_path = worker_notes_path_for(slots_path)
    if not notes_path.is_file():
        return None
    with notes_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        return None
    return data


def load_card_slots_raw(slots_path: Path) -> dict:
    """Load card_slots.json as a raw dict (for content gate)."""
    with slots_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        return {}
    return data


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Validation agent for equity social cards. Runs structural checks plus the "
            "Cards 1-4 analyst-content gate. Each HTML must have a sibling "
            "<stem>.card_slots.json AND a sibling <stem>.card_slots_worker_notes.json "
            "with the hidden analyst fields (data_anchor / variant_view / "
            "falsifier|primary_quote|catalyst_with_date)."
        )
    )
    parser.add_argument("--input", required=True, help="HTML file or folder.")
    parser.add_argument("--brand", default="金融豹", help="Brand name.")
    parser.add_argument(
        "--slots",
        required=True,
        help=(
            "Path to card_slots.json (single HTML), or directory of "
            "<stem>.card_slots.json (batch). Each must have a sibling "
            "<stem>.card_slots_worker_notes.json (required by the "
            "Cards 1-4 analyst-content gate)."
        ),
    )
    parser.add_argument(
        "--allow-no-logo",
        action="store_true",
        help="Allow validation without logo_asset_path (customer explicitly waived logo). Default: require logo.",
    )
    parser.add_argument(
        "--palette",
        required=True,
        choices=["macaron", "default", "b", "c"],
        help="Required P0-confirmed palette for validation geometry/color paths: macaron | default | b | c.",
    )
    parser.add_argument(
        "--cfa-progress",
        default=None,
        help=(
            "Optional CFA progress hint (e.g. 'Level 2 - Fixed Income - Binomial Tree'). "
            "Exported to env var CFA_PROGRESS so the CFA-lens selector can pick a fitting concept. "
            "Precedence: --cfa-progress > existing CFA_PROGRESS env > USER.md sticky > agent default."
        ),
    )
    args = parser.parse_args()
    apply_palette(args.palette)

    if args.cfa_progress is not None:
        os.environ["CFA_PROGRESS"] = args.cfa_progress

    src = Path(args.input).expanduser().resolve()
    files = input_files(src)
    if not files:
        raise SystemExit(f"No HTML files found at: {src}")
    multiple = len(files) > 1

    overall_failed = False
    for html in files:
        data = parse_html(html)
        slots_path = resolve_slots_path(html, Path(args.slots), multiple_html=multiple)
        data.card_slots = load_card_slots(slots_path)
        set_currency_label(data)
        validate_report(data, args.brand, allow_no_logo=args.allow_no_logo)

        # Cards 1-4 analyst-content gate (blocking).
        raw_slots = load_card_slots_raw(slots_path)
        worker_notes = load_worker_notes(slots_path)
        content_issues = validate_card1_4_analytical_content(raw_slots, worker_notes)
        if content_issues:
            overall_failed = True
            print(
                f"\n=== Card 1-4 analytical-content gate FAILED for {html} ===",
                file=sys.stderr,
            )
            print(
                f"  slots:        {slots_path}\n"
                f"  worker_notes: {worker_notes_path_for(slots_path)}",
                file=sys.stderr,
            )
            for issue in content_issues:
                print(f"  - {issue}", file=sys.stderr)
            print(
                "  (Cards 1-4 analyst-voice contract. See "
                "references/card_voice_examples/ for required substrate.)",
                file=sys.stderr,
            )
            continue

        print(f"validated: {html}")

    if overall_failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
