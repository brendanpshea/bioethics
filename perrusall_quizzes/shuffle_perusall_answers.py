from __future__ import annotations

import argparse
import csv
import random
import sys
from pathlib import Path


CHOICE_COLUMNS = [f"Answer choice {index}" for index in range(1, 6)]
EXPECTED_HEADERS = [
    "Question type",
    "Answer explanation",
    "Points",
    "Prompt",
    "Correct answers",
    "Answer choice 1",
    "Answer choice 2",
    "Answer choice 3",
    "Answer choice 4",
    "Answer choice 5",
]


def parse_indices(raw_value: str) -> list[int]:
    return [int(part.strip()) for part in raw_value.split(",") if part.strip()]


def expand_inputs(raw_paths: list[str]) -> list[Path]:
    targets: list[Path] = []
    for raw_path in raw_paths:
        path = Path(raw_path)
        if path.is_dir():
            for candidate in sorted(path.glob("*.csv")):
                if candidate.name.lower() == "quiz-template.csv":
                    continue
                targets.append(candidate)
            continue
        targets.append(path)
    return targets


def shuffle_file(path: Path, base_seed: int, verbose: bool) -> None:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != EXPECTED_HEADERS:
            raise ValueError(f"{path}: unexpected headers; expected the Perusall template")
        rows = list(reader)

    file_seed = base_seed + sum(ord(character) for character in str(path.name))
    rng = random.Random(file_seed)

    for row_number, row in enumerate(rows, start=2):
        answer_key = parse_indices(row["Correct answers"])
        populated_choices = []
        for index, column in enumerate(CHOICE_COLUMNS, start=1):
            choice = row[column].strip()
            if choice:
                populated_choices.append(
                    {
                        "original_index": index,
                        "text": choice,
                        "is_correct": index in answer_key,
                    }
                )

        if len(populated_choices) <= 1:
            continue

        rng.shuffle(populated_choices)

        for output_index, column in enumerate(CHOICE_COLUMNS, start=1):
            if output_index <= len(populated_choices):
                row[column] = populated_choices[output_index - 1]["text"]
            else:
                row[column] = ""

        new_key = [
            str(output_index)
            for output_index, choice in enumerate(populated_choices, start=1)
            if choice["is_correct"]
        ]
        row["Correct answers"] = ",".join(new_key)

        if verbose:
            print(f"{path.name}: shuffled row {row_number}")

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=EXPECTED_HEADERS)
        writer.writeheader()
        writer.writerows(rows)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Randomize Perusall answer-option order and rewrite the correct-answer indices."
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="One or more quiz CSV files or a directory containing them.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=20260527,
        help="Base random seed for reproducible shuffling. Default: 20260527.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print each shuffled row.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    targets = expand_inputs(args.paths)
    if not targets:
        parser.error("no quiz CSV files found")

    for target in targets:
        shuffle_file(target, args.seed, args.verbose)
        print(f"Shuffled {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())