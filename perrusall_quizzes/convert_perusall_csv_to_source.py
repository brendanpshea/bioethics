from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path


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

CHOICE_COLUMNS = [f"Answer choice {index}" for index in range(1, 6)]
WORD_RE = re.compile(r"[A-Za-z0-9']+")
STYLE_SINGLE = "single word or term"
STYLE_CLAUSE = "clause"
STYLE_SENTENCE = "complete sentence"


def count_words(text: str) -> int:
    return len(WORD_RE.findall(text))


def parse_indices(raw_value: str) -> set[int]:
    return {int(part.strip()) for part in raw_value.split(",") if part.strip()}


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


def resolve_output_path(source_path: Path, output: str | None, output_dir: str | None, many_sources: bool) -> Path:
    if output and output_dir:
        raise ValueError("use either --output or --output-dir, not both")

    if output:
        if many_sources:
            raise ValueError("--output can only be used with a single CSV file")
        return Path(output)

    if output_dir:
        return Path(output_dir) / source_path.name.replace(".csv", ".quiz.json")

    return source_path.with_suffix(".quiz.json")


def infer_answer_style(choices: list[str]) -> str:
    word_counts = [count_words(choice) for choice in choices]
    average_words = sum(word_counts) / len(word_counts)
    has_sentence_punctuation = sum(1 for choice in choices if choice.rstrip().endswith((".", "?", "!")))

    if average_words <= 2.75 and max(word_counts) <= 4:
        return STYLE_SINGLE
    if has_sentence_punctuation >= max(1, len(choices) // 2):
        return STYLE_SENTENCE
    return STYLE_CLAUSE


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != EXPECTED_HEADERS:
            raise ValueError(f"{path}: unexpected headers; expected the Perusall template")
        return list(reader)


def convert_file(csv_path: Path, output_path: Path) -> list[str]:
    rows = load_rows(csv_path)
    questions: list[dict[str, object]] = []
    style_counts: Counter[str] = Counter()
    all_choice_lengths: list[int] = []

    for question_number, row in enumerate(rows, start=1):
        correct_indices = parse_indices(row["Correct answers"])
        choices: list[dict[str, object]] = []
        choice_texts: list[str] = []
        for choice_index, column_name in enumerate(CHOICE_COLUMNS, start=1):
            text = row[column_name].strip()
            if not text:
                continue
            choices.append({"text": text, "correct": choice_index in correct_indices})
            choice_texts.append(text)

        answer_style = infer_answer_style(choice_texts)
        style_counts[answer_style] += 1
        all_choice_lengths.extend(count_words(text) for text in choice_texts)

        questions.append(
            {
                "question_type": row["Question type"].strip(),
                "answer_style": answer_style,
                "prompt": row["Prompt"].strip(),
                "answer_explanation": row["Answer explanation"].strip(),
                "points": row["Points"].strip(),
                "tags": [],
                "choices": choices,
            }
        )

    title = csv_path.stem.replace("-", " ").replace("_", " ").title()
    source = {
        "title": title,
        "source_csv": csv_path.name,
        "shuffle_answers": True,
        "questions": questions,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(source, handle, indent=2)
        handle.write("\n")

    average_words = sum(all_choice_lengths) / len(all_choice_lengths) if all_choice_lengths else 0.0
    return [
        f"Converted {csv_path} -> {output_path}",
        f"  Questions: {len(questions)}",
        f"  Average answer words: {average_words:.2f}",
        "  Inferred styles: " + ", ".join(
            f"{style}={style_counts[style]}" for style in (STYLE_SINGLE, STYLE_CLAUSE, STYLE_SENTENCE) if style_counts[style]
        ),
    ]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert Perusall CSV quizzes into richer .quiz.json source files with inferred answer-style tags."
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="One or more quiz CSV files or a directory containing them.",
    )
    parser.add_argument(
        "--output",
        help="Output .quiz.json path for a single CSV input.",
    )
    parser.add_argument(
        "--output-dir",
        help="Directory where converted .quiz.json files should be written.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    inputs = expand_inputs(args.paths)
    if not inputs:
        parser.error("no quiz CSV files found")

    for csv_path in inputs:
        output_path = resolve_output_path(csv_path, args.output, args.output_dir, len(inputs) > 1)
        summary_lines = convert_file(csv_path, output_path)
        for line in summary_lines:
            print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())