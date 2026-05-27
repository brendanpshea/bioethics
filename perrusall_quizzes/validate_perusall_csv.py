from __future__ import annotations

import argparse
import csv
import math
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

ALLOWED_TYPES = {"MC", "MR", "TF", "NM"}
DEFAULT_TYPES = {"MC", "MR"}
CHOICE_COLUMNS = [f"Answer choice {index}" for index in range(1, 6)]
LOADED_WORD_RE = re.compile(
    r"\b(always|never|all|none|only|must|every|no|cannot|can't|impossible|entirely)\b",
    re.IGNORECASE,
)
VOWEL_GROUP_RE = re.compile(r"[aeiouy]+", re.IGNORECASE)
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


class ValidationResult:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.question_types: Counter[str] = Counter()
        self.answer_word_lengths: list[int] = []
        self.prompt_texts: list[str] = []
        self.mc_correct_positions: list[tuple[int, int, bool, bool]] = []
        self.correct_loaded_terms = 0
        self.correct_choice_total = 0
        self.incorrect_loaded_terms = 0
        self.incorrect_choice_total = 0

    def add_error(self, message: str) -> None:
        self.errors.append(message)

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)


def count_words(text: str) -> int:
    return len(WORD_RE.findall(text))


def count_syllables(word: str) -> int:
    lowered = re.sub(r"[^A-Za-z]", "", word).lower()
    if not lowered:
        return 0
    if len(lowered) <= 3:
        return 1
    lowered = re.sub(r"e$", "", lowered)
    matches = VOWEL_GROUP_RE.findall(lowered)
    return max(1, len(matches))


def flesch_kincaid_grade(text: str) -> float:
    sentences = re.split(r"[.!?]+", text)
    sentence_count = len([sentence for sentence in sentences if sentence.strip()]) or 1
    words = WORD_RE.findall(text)
    word_count = len(words)
    if word_count == 0:
        return 0.0
    syllable_count = sum(count_syllables(word) for word in words)
    return 0.39 * (word_count / sentence_count) + 11.8 * (syllable_count / word_count) - 15.59


def normalize_choice(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


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


def parse_answer_indices(raw_value: str) -> list[int]:
    parts = [part.strip() for part in raw_value.split(",") if part.strip()]
    indices: list[int] = []
    for part in parts:
        if not part.isdigit():
            raise ValueError(f"contains a non-numeric answer key value: {part!r}")
        index = int(part)
        if index < 1 or index > 5:
            raise ValueError(f"contains an out-of-range answer key value: {part!r}")
        indices.append(index)
    return indices


def expand_inputs(paths: list[str]) -> list[Path]:
    expanded: list[Path] = []
    for raw_path in paths:
        path = Path(raw_path)
        if path.is_dir():
            for candidate in sorted(path.glob("*.csv")):
                if candidate.name.lower() == "quiz-template.csv":
                    continue
                expanded.append(candidate)
            continue
        expanded.append(path)
    return expanded


def validate_row(result: ValidationResult, row_number: int, row: dict[str, str]) -> None:
    question_type = row["Question type"].strip()
    prompt = row["Prompt"].strip()
    answer_key_raw = row["Correct answers"].strip()
    choices = [row[column].strip() for column in CHOICE_COLUMNS]
    non_empty_choices = [(index + 1, choice) for index, choice in enumerate(choices) if choice]

    if not question_type:
        result.add_error(f"row {row_number}: missing question type")
        return
    if question_type not in ALLOWED_TYPES:
        result.add_error(f"row {row_number}: unsupported question type {question_type!r}")
        return
    result.question_types[question_type] += 1
    if question_type not in DEFAULT_TYPES:
        result.add_error(
            f"row {row_number}: question type {question_type!r} violates the current house rule of MC/MR-only quizzes"
        )

    if not prompt:
        result.add_error(f"row {row_number}: prompt is blank")
    else:
        result.prompt_texts.append(prompt)
        if META_PROMPT_RE.search(prompt):
            result.add_warning(
                f"row {row_number}: prompt refers to course packaging (Part A/Part B/this lecture); ask about the content instead"
            )

    if len(non_empty_choices) < 4 and question_type in {"MC", "MR"}:
        result.add_error(f"row {row_number}: MC/MR questions need at least 4 answer choices")

    normalized_choices = [normalize_choice(choice) for _, choice in non_empty_choices]
    if len(normalized_choices) != len(set(normalized_choices)):
        result.add_error(f"row {row_number}: contains duplicate answer choices")

    if PREMISE_PROMPT_RE.search(prompt) and non_empty_choices and all(
        PREMISE_CHOICE_RE.fullmatch(choice) for _, choice in non_empty_choices
    ):
        result.add_warning(
            f"row {row_number}: premise-number placeholders are not informative; restate the actual premises instead"
        )

    for _, choice in non_empty_choices:
        result.answer_word_lengths.append(count_words(choice))

    if not answer_key_raw:
        result.add_error(f"row {row_number}: missing correct answers")
        return

    try:
        answer_indices = parse_answer_indices(answer_key_raw)
    except ValueError as exc:
        result.add_error(f"row {row_number}: correct answers {exc}")
        return

    if question_type == "MC" and len(answer_indices) != 1:
        result.add_error(f"row {row_number}: MC questions need exactly 1 correct answer")
    if question_type == "MR" and len(answer_indices) < 2:
        result.add_error(f"row {row_number}: MR questions need at least 2 correct answers")
    if len(answer_indices) != len(set(answer_indices)):
        result.add_error(f"row {row_number}: correct answers list repeats a choice number")

    available_indices = {index for index, _ in non_empty_choices}
    for answer_index in answer_indices:
        if answer_index not in available_indices:
            result.add_error(
                f"row {row_number}: answer key points to choice {answer_index}, but that choice is blank"
            )

    choice_lengths = {index: count_words(choice) for index, choice in non_empty_choices}
    if choice_lengths:
        longest = max(choice_lengths.values())
        shortest = min(choice_lengths.values())
        average_choice_words = sum(choice_lengths.values()) / len(choice_lengths)
        short_choice_count = sum(1 for length in choice_lengths.values() if length <= 3)
        punctuated_choice_count = sum(1 for _, choice in non_empty_choices if has_terminal_punctuation(choice))
        if longest - shortest > 3:
            result.add_warning(
                f"row {row_number}: answer lengths vary by more than 3 words; choices may not feel parallel"
            )

        if FACT_STYLE_PROMPT_RE.search(prompt) and (
            short_choice_count >= max(2, len(non_empty_choices) - 1)
            or (average_choice_words < 4 and punctuated_choice_count == 0)
        ):
            result.add_warning(
                f"row {row_number}: prompt asks for facts/statements/details, but the answers are too compressed; use clauses or full sentences"
            )

        if SENTENCE_STYLE_PROMPT_RE.search(prompt) and average_choice_words < 4.5 and punctuated_choice_count == 0:
            result.add_warning(
                f"row {row_number}: prompt looks explanatory or narrative; use fuller sentence-style answers with terminal punctuation"
            )

        if question_type == "MC" and len(answer_indices) == 1 and answer_indices[0] in choice_lengths:
            correct_index = answer_indices[0]
            correct_length = choice_lengths[correct_index]
            correct_tokens = content_tokens(dict(non_empty_choices)[correct_index])
            prompt_tokens = set(content_tokens(prompt))
            if correct_tokens and len(correct_tokens) <= 2 and all(token in prompt_tokens for token in correct_tokens):
                result.add_warning(
                    f"row {row_number}: the correct answer may be cued by repeating its stem in the prompt"
                )
            longest_count = sum(1 for length in choice_lengths.values() if length == longest)
            shortest_count = sum(1 for length in choice_lengths.values() if length == shortest)
            result.mc_correct_positions.append(
                (
                    row_number,
                    correct_index,
                    correct_length == longest and longest_count == 1,
                    correct_length == shortest and shortest_count == 1,
                )
            )

    for choice_index, choice in non_empty_choices:
        loaded_term_count = len(LOADED_WORD_RE.findall(choice))
        if choice_index in set(answer_indices):
            result.correct_loaded_terms += loaded_term_count
            result.correct_choice_total += 1
        else:
            result.incorrect_loaded_terms += loaded_term_count
            result.incorrect_choice_total += 1


def validate_file(path: Path, expected_questions: int, mc_target: int, mr_target: int) -> ValidationResult:
    result = ValidationResult(path)
    if not path.exists():
        result.add_error("file does not exist")
        return result

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        if fieldnames != EXPECTED_HEADERS:
            result.add_error(
                "header row does not match the Perusall template exactly; expected: "
                + ", ".join(EXPECTED_HEADERS)
            )
            return result

        rows = list(reader)

    if len(rows) != expected_questions:
        result.add_error(
            f"expected {expected_questions} questions, found {len(rows)}"
        )

    for row_index, row in enumerate(rows, start=2):
        validate_row(result, row_index, row)

    if result.answer_word_lengths:
        average_answer_words = sum(result.answer_word_lengths) / len(result.answer_word_lengths)
        if average_answer_words > 5.0:
            result.add_error(
                f"average answer length is {average_answer_words:.2f} words; house rule is <= 5.0"
            )

    if result.prompt_texts:
        combined_prompt_grade = flesch_kincaid_grade(" ".join(result.prompt_texts))
        if combined_prompt_grade > 12.0:
            result.add_warning(
                f"average prompt reading level is about grade {combined_prompt_grade:.1f}; target is below grade 12"
            )

    mc_count = result.question_types["MC"]
    mr_count = result.question_types["MR"]
    if mc_count != mc_target:
        result.add_warning(
            f"MC count is {mc_count}; the current target is {mc_target}"
        )
    if mr_count != mr_target:
        result.add_warning(
            f"MR count is {mr_count}; the current target is {mr_target}"
        )

    if result.mc_correct_positions:
        mc_total = len(result.mc_correct_positions)
        longest_count = sum(1 for _, _, is_longest, _ in result.mc_correct_positions if is_longest)
        shortest_count = sum(1 for _, _, _, is_shortest in result.mc_correct_positions if is_shortest)
        if longest_count / mc_total > 0.5:
            result.add_warning(
                f"correct answers are the longest option in {longest_count}/{mc_total} MC questions"
            )
        if shortest_count / mc_total > 0.5:
            result.add_warning(
                f"correct answers are the shortest option in {shortest_count}/{mc_total} MC questions"
            )

    if result.correct_choice_total and result.incorrect_choice_total:
        correct_rate = result.correct_loaded_terms / result.correct_choice_total
        incorrect_rate = result.incorrect_loaded_terms / result.incorrect_choice_total
        if incorrect_rate > correct_rate + 0.2:
            result.add_warning(
                "incorrect choices use noticeably more absolute or loaded terms than correct choices"
            )

    return result


def print_result(result: ValidationResult) -> None:
    print(f"\n{result.path}")
    if not result.errors and not result.warnings:
        print("  PASS")
        return
    if result.errors:
        print("  Errors:")
        for error in result.errors:
            print(f"    - {error}")
    if result.warnings:
        print("  Warnings:")
        for warning in result.warnings:
            print(f"    - {warning}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate Perusall quiz CSVs against the template and local house rules."
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="One or more CSV files or directories. Directories are expanded to *.csv, excluding quiz-template.csv.",
    )
    parser.add_argument(
        "--expected-questions",
        type=int,
        default=40,
        help="Required number of questions per quiz. Default: 40.",
    )
    parser.add_argument(
        "--mc-target",
        type=int,
        default=30,
        help="Recommended MC question count. Default: 30.",
    )
    parser.add_argument(
        "--mr-target",
        type=int,
        default=10,
        help="Recommended MR question count. Default: 10.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    targets = expand_inputs(args.paths)
    if not targets:
        parser.error("no CSV files found")

    overall_error_count = 0
    overall_warning_count = 0
    for target in targets:
        result = validate_file(target, args.expected_questions, args.mc_target, args.mr_target)
        print_result(result)
        overall_error_count += len(result.errors)
        overall_warning_count += len(result.warnings)

    print(
        f"\nSummary: {len(targets)} file(s), {overall_error_count} error(s), {overall_warning_count} warning(s)"
    )
    return 1 if overall_error_count else 0


if __name__ == "__main__":
    sys.exit(main())