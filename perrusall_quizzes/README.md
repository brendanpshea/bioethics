# Perusall Quiz Workflow

This folder now supports a two-step workflow:

1. Author or edit rich source files in `sources/*.quiz.json`.
2. Generate Perusall-ready CSV files from those sources.

The generated CSVs stay flat and importable. The source files hold the extra metadata that is hard to manage in CSV alone, especially `answer_style` and free-form `tags`.

## Source Format

Each source file is a `.quiz.json` document with this shape:

```json
{
  "title": "Chapter 1 - Principles and Reasoning",
  "shuffle_answers": true,
  "questions": [
    {
      "question_type": "MC",
      "answer_style": "clause",
      "prompt": "Which branch asks what people morally ought to do?",
      "answer_explanation": "",
      "points": "",
      "tags": ["principles", "ethics-branches"],
      "choices": [
        { "text": "The descriptive branch of ethics", "correct": false },
        { "text": "The normative branch of ethics", "correct": true },
        { "text": "The metaethical branch of ethics", "correct": false },
        { "text": "The clinical decision method", "correct": false }
      ]
    }
  ]
}
```

## `answer_style` Values

Use these exact values:

- `single word or term`: one-word answers, short terms, or very short noun phrases.
- `clause`: short clauses or compact phrases that usually run about 3 to 7 words.
- `complete sentence`: full-sentence options. Use sparingly so the quiz-wide average still stays below 5 words.

The generator and validator do not force a rigid length for every individual option, but they do report style mismatches and still enforce the quiz-wide average answer-length target.

## Commands

Convert existing flat CSVs into richer source files:

```powershell
python .\perrusall_quizzes\convert_perusall_csv_to_source.py .\perrusall_quizzes --output-dir .\perrusall_quizzes\sources
```

Generate CSVs from source files. Answer choices are shuffled by default with a reproducible seed:

```powershell
python .\perrusall_quizzes\generate_perusall_quiz.py .\perrusall_quizzes\sources --output-dir .\perrusall_quizzes
```

Validate the generated CSVs:

```powershell
python .\perrusall_quizzes\validate_perusall_csv.py .\perrusall_quizzes
```

If you only need to reshuffle an already-written CSV, the legacy flat-file script still exists:

```powershell
python .\perrusall_quizzes\shuffle_perusall_answers.py .\perrusall_quizzes
```

## Recommended Practice

- Edit the `.quiz.json` files, not the generated CSVs, unless you are making a quick emergency fix.
- Keep `tags` short and topic-oriented so you can later search for concepts, cases, and answer-style distributions.
- Ask about the underlying concept, case, argument, or doctrine, not the course packaging. Avoid prompts framed around `Part A`, `Part B`, or `this lecture`.
- When a prompt asks for a named term, doctrine, or test, preserve the canonical label verbatim. Do not replace `speciesism`, `eudaimonia`, or `the categorical imperative` with descriptive glosses.
- Avoid prompt wording that cues the answer by repeating its stem. If the theory name already contains the answer word, rewrite the prompt so students must recognize the concept rather than echo it.
- When a question is about events, facts, statements, or an argument's content, write the answer choices as clauses or complete sentences. Use periods on complete-sentence choices.
- Do not use placeholder answers like `Premise 1` or `Premise 2`. Put the actual premise statements in the answer choices.
- Use `complete sentence` only where the question actually benefits from full-sentence distractors.
- Run generation and validation together after every batch of edits.