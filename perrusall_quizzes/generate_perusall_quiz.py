from __future__ import annotations

import argparse
import csv
import json
import random
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
META_PROMPT_RE = re.compile(r"\bpart\s+[ab]\b|\bthis lecture\b", re.IGNORECASE)
PREMISE_PROMPT_RE = re.compile(r"\bwhich premise\b", re.IGNORECASE)
PREMISE_CHOICE_RE = re.compile(r"Premise\s+\d+", re.IGNORECASE)
FACT_STYLE_PROMPT_RE = re.compile(r"^(Which facts|Which statements|Which details)\b", re.IGNORECASE)
SENTENCE_STYLE_PROMPT_RE = re.compile(r"\bwhat initially happened\b|\bdescribed as what\b", re.IGNORECASE)
STOPWORDS = {
    "a",
    "an",
    "the",
    "of",
    "to",
    "for",
    "and",
    "or",
    "by",
    "in",
    "on",
    "at",
    "is",
    "are",
    "was",
    "were",
    "what",
    "which",
    "who",
    "how",
    "when",
    "why",
    "does",
    "do",
    "did",
    "it",
    "this",
    "that",
    "their",
    "his",
    "her",
    "its",
    "main",
    "term",
    "called",
}
STYLE_SINGLE = "single word or term"
STYLE_CLAUSE = "clause"
STYLE_SENTENCE = "complete sentence"
STYLE_RULES = {
    STYLE_SINGLE: {"min_avg": 1.0, "max_avg": 3.0, "max_choice": 4, "needs_terminal_punctuation": False},
    STYLE_CLAUSE: {"min_avg": 2.5, "max_avg": 7.0, "max_choice": 10, "needs_terminal_punctuation": False},
    STYLE_SENTENCE: {"min_avg": 6.0, "max_avg": 30.0, "max_choice": 40, "needs_terminal_punctuation": True},
}
STYLE_ALIASES = {
    STYLE_SINGLE: STYLE_SINGLE,
    "term": STYLE_SINGLE,
    "single term": STYLE_SINGLE,
    "single-word or term": STYLE_SINGLE,
    "single_word_or_term": STYLE_SINGLE,
    STYLE_CLAUSE: STYLE_CLAUSE,
    STYLE_SENTENCE: STYLE_SENTENCE,
    "sentence": STYLE_SENTENCE,
    "complete_sentence": STYLE_SENTENCE,
}


def count_words(text: str) -> int:
    return len(WORD_RE.findall(text))


def has_terminal_punctuation(text: str) -> bool:
    return text.rstrip().endswith((".", "?", "!"))


def normalize_token(token: str) -> str:
    normalized = token.lower().strip("'")
    if normalized.endswith("'s"):
        normalized = normalized[:-2]
    if normalized.endswith("ies") and len(normalized) > 4:
        normalized = normalized[:-3] + "y"
    elif normalized.endswith("s") and len(normalized) > 3:
        normalized = normalized[:-1]
    return normalized


def content_tokens(text: str) -> list[str]:
    tokens = [normalize_token(token) for token in WORD_RE.findall(text)]
    return [token for token in tokens if token and token not in STOPWORDS]


def canonicalize_style(raw_style: str) -> str:
    normalized = re.sub(r"\s+", " ", raw_style.strip().lower())
    normalized = normalized.replace("-", " ")
    normalized = normalized.replace("/", " ")
    normalized = re.sub(r"\s+", " ", normalized)
    style = STYLE_ALIASES.get(normalized)
    if style is None:
        raise ValueError(
            f"unknown answer_style {raw_style!r}; expected one of: {STYLE_SINGLE!r}, {STYLE_CLAUSE!r}, {STYLE_SENTENCE!r}"
        )
    return style


def expand_sources(raw_paths: list[str]) -> list[Path]:
    sources: list[Path] = []
    for raw_path in raw_paths:
        path = Path(raw_path)
        if path.is_dir():
            sources.extend(sorted(path.glob("*.quiz.json")))
            continue
        sources.append(path)
    return sources


def resolve_output_path(source_path: Path, output: str | None, output_dir: str | None, many_sources: bool) -> Path:
    if output and output_dir:
        raise ValueError("use either --output or --output-dir, not both")

    if output:
        output_path = Path(output)
        if many_sources:
            raise ValueError("--output can only be used with a single source file")
        return output_path

    if output_dir:
        return Path(output_dir) / source_path.name.replace(".quiz.json", ".csv")

    return source_path.with_suffix("").with_suffix(".csv")


def load_source(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def get_top_level_shuffle(source: dict) -> bool:
    raw_value = source.get("shuffle_answers", True)
    if not isinstance(raw_value, bool):
        raise ValueError("top-level shuffle_answers must be true or false")
    return raw_value


def get_question_shuffle(question: dict, default_shuffle: bool) -> bool:
    raw_value = question.get("shuffle_answers", default_shuffle)
    if not isinstance(raw_value, bool):
        raise ValueError("question-level shuffle_answers must be true or false")
    return raw_value


def validate_tags(question: dict, question_number: int) -> None:
    raw_tags = question.get("tags", [])
    if not isinstance(raw_tags, list) or any(not isinstance(tag, str) for tag in raw_tags):
        raise ValueError(f"question {question_number}: tags must be a list of strings")


def build_choice_records(question: dict, question_number: int) -> list[dict[str, object]]:
    raw_choices = question.get("choices")
    if not isinstance(raw_choices, list):
        raise ValueError(f"question {question_number}: choices must be a list")
    if len(raw_choices) < 4 or len(raw_choices) > 5:
        raise ValueError(f"question {question_number}: choices must contain 4 or 5 options")

    records: list[dict[str, object]] = []
    for choice_number, raw_choice in enumerate(raw_choices, start=1):
        if not isinstance(raw_choice, dict):
            raise ValueError(f"question {question_number}: choice {choice_number} must be an object")
        text = str(raw_choice.get("text", "")).strip()
        if not text:
            raise ValueError(f"question {question_number}: choice {choice_number} text is blank")
        correct = raw_choice.get("correct")
        if not isinstance(correct, bool):
            raise ValueError(f"question {question_number}: choice {choice_number} must set correct to true or false")
        records.append({"text": text, "correct": correct})

    return records


def infer_style_warnings(
    style: str,
    prompt: str,
    choices: list[str],
    correct_choices: list[str],
    question_number: int,
) -> list[str]:
    rules = STYLE_RULES[style]
    word_counts = [count_words(choice) for choice in choices]
    average_words = sum(word_counts) / len(word_counts)
    warnings: list[str] = []

    if average_words < rules["min_avg"] or average_words > rules["max_avg"]:
        warnings.append(
            f"question {question_number}: answer_style {style!r} has average choice length {average_words:.2f} words"
        )

    if max(word_counts) > rules["max_choice"]:
        warnings.append(
            f"question {question_number}: answer_style {style!r} includes a choice with {max(word_counts)} words"
        )

    if rules["needs_terminal_punctuation"]:
        punctuated = sum(1 for choice in choices if choice.rstrip().endswith((".", "?", "!")))
        if punctuated < max(1, len(choices) // 2):
            warnings.append(
                f"question {question_number}: answer_style {style!r} looks sentence-like but most choices lack terminal punctuation"
            )

    punctuated = sum(1 for choice in choices if has_terminal_punctuation(choice))
    short_choice_count = sum(1 for count in word_counts if count <= 3)

    if META_PROMPT_RE.search(prompt):
        warnings.append(
            f"question {question_number}: prompt refers to course packaging (Part A/Part B/this lecture); ask about the content instead"
        )

    if PREMISE_PROMPT_RE.search(prompt) and choices and all(PREMISE_CHOICE_RE.fullmatch(choice) for choice in choices):
        warnings.append(
            f"question {question_number}: premise-number placeholders are not informative; restate the actual premises instead"
        )

    if FACT_STYLE_PROMPT_RE.search(prompt) and (
        short_choice_count >= max(2, len(choices) - 1) or (average_words < 4 and punctuated == 0)
    ):
        warnings.append(
            f"question {question_number}: prompt asks for facts/statements/details, but the answers are too compressed; use clauses or full sentences"
        )

    if SENTENCE_STYLE_PROMPT_RE.search(prompt) and average_words < 4.5 and punctuated == 0:
        warnings.append(
            f"question {question_number}: prompt looks explanatory or narrative; use fuller sentence-style answers with terminal punctuation"
        )

    prompt_tokens = set(content_tokens(prompt))
    for correct_choice in correct_choices:
        correct_tokens = content_tokens(correct_choice)
        if correct_tokens and len(correct_tokens) <= 2 and all(token in prompt_tokens for token in correct_tokens):
            warnings.append(
                f"question {question_number}: the correct answer may be cued by repeating its stem in the prompt"
            )
            break

    return warnings


def shuffle_records(choice_records: list[dict[str, object]], rng: random.Random) -> list[dict[str, object]]:
    shuffled = list(choice_records)
    rng.shuffle(shuffled)
    return shuffled


def build_row(question: dict, question_number: int, rng: random.Random, default_shuffle: bool) -> tuple[dict[str, str], str, list[int], list[str]]:
    question_type = str(question.get("question_type", "")).strip()
    if question_type not in {"MC", "MR", "TF", "NM"}:
        raise ValueError(f"question {question_number}: unsupported question_type {question_type!r}")

    prompt = str(question.get("prompt", "")).strip()
    if not prompt:
        raise ValueError(f"question {question_number}: prompt is blank")

    validate_tags(question, question_number)
    style = canonicalize_style(str(question.get("answer_style", "")).strip() or STYLE_CLAUSE)
    choice_records = build_choice_records(question, question_number)
    correct_count = sum(1 for choice in choice_records if bool(choice["correct"]))

    if question_type == "MC" and correct_count != 1:
        raise ValueError(f"question {question_number}: MC questions need exactly one correct choice")
    if question_type == "MR" and correct_count < 2:
        raise ValueError(f"question {question_number}: MR questions need at least two correct choices")
    if correct_count == 0:
        raise ValueError(f"question {question_number}: no correct choices were marked")

    should_shuffle = get_question_shuffle(question, default_shuffle)
    if should_shuffle:
        choice_records = shuffle_records(choice_records, rng)

    choice_texts = [str(choice["text"]) for choice in choice_records]
    correct_texts = [str(choice["text"]) for choice in choice_records if bool(choice["correct"])]
    warnings = infer_style_warnings(style, prompt, choice_texts, correct_texts, question_number)

    row = {
        "Question type": question_type,
        "Answer explanation": str(question.get("answer_explanation", "")).strip(),
        "Points": str(question.get("points", "")).strip(),
        "Prompt": prompt,
        "Correct answers": ",".join(
            str(index)
            for index, choice in enumerate(choice_records, start=1)
            if bool(choice["correct"])
        ),
    }

    for column_index, column_name in enumerate(CHOICE_COLUMNS, start=1):
        if column_index <= len(choice_records):
            row[column_name] = str(choice_records[column_index - 1]["text"])
        else:
            row[column_name] = ""

    return row, style, [count_words(text) for text in choice_texts], warnings


def generate_file(source_path: Path, output_path: Path, seed: int, max_average_words: float) -> tuple[list[str], list[str]]:
    source = load_source(source_path)
    questions = source.get("questions")
    if not isinstance(questions, list) or not questions:
        raise ValueError(f"{source_path}: source file must contain a non-empty questions list")

    default_shuffle = get_top_level_shuffle(source)
    file_seed = seed + sum(ord(character) for character in source_path.name)
    rng = random.Random(file_seed)

    rows: list[dict[str, str]] = []
    style_counts: Counter[str] = Counter()
    all_choice_lengths: list[int] = []
    warnings: list[str] = []

    for question_number, question in enumerate(questions, start=1):
        if not isinstance(question, dict):
            raise ValueError(f"{source_path}: question {question_number} must be an object")
        row, style, choice_lengths, row_warnings = build_row(question, question_number, rng, default_shuffle)
        rows.append(row)
        style_counts[style] += 1
        all_choice_lengths.extend(choice_lengths)
        warnings.extend(row_warnings)

    average_words = sum(all_choice_lengths) / len(all_choice_lengths)
    if average_words > max_average_words:
        raise ValueError(
            f"{source_path}: generated choices average {average_words:.2f} words, above max {max_average_words:.2f}"
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=EXPECTED_HEADERS)
        writer.writeheader()
        writer.writerows(rows)

    summary_lines = [
        f"Generated {output_path}",
        f"  Questions: {len(rows)}",
        f"  Average answer words: {average_words:.2f}",
        "  Styles: " + ", ".join(
            f"{style}={style_counts[style]}" for style in (STYLE_SINGLE, STYLE_CLAUSE, STYLE_SENTENCE) if style_counts[style]
        ),
    ]
    return summary_lines, warnings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate Perusall CSV quizzes from richer .quiz.json source files with answer-style tags."
    )
    parser.add_argument(
        "sources",
        nargs="+",
        help="One or more .quiz.json files or a directory containing them.",
    )
    parser.add_argument(
        "--output",
        help="Output CSV path for a single source file.",
    )
    parser.add_argument(
        "--output-dir",
        help="Directory where generated CSV files should be written.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=20260527,
        help="Base random seed for reproducible answer shuffling. Default: 20260527.",
    )
    parser.add_argument(
        "--max-average-answer-words",
        type=float,
        default=5.0,
        help="Maximum allowed average answer length across the generated quiz. Default: 5.0.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    sources = expand_sources(args.sources)
    if not sources:
        parser.error("no .quiz.json files found")

    had_warnings = False
    for source_path in sources:
        output_path = resolve_output_path(source_path, args.output, args.output_dir, len(sources) > 1)
        summary_lines, warnings = generate_file(source_path, output_path, args.seed, args.max_average_answer_words)
        for line in summary_lines:
            print(line)
        if warnings:
            had_warnings = True
            print("  Style warnings:")
            for warning in warnings:
                print(f"    - {warning}")

    return 0 if not had_warnings else 0


if __name__ == "__main__":
    sys.exit(main())