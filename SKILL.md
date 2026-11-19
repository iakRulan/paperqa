---
name: paperqa
description: "Answer questions about a scientific paper with per-question evidence: index the supplied numbered paragraphs, rank them per question, and emit answers[] with question_id, answer, conditions, status (answered/partial/insufficient_evidence/input_error) and exact paragraph citations. Trigger on: '文献智能问答', '论文问答', '回答问题并给依据', 'paper QA', 'read the paper and answer', 'question answering over a paper'. Not for: writing the paper, drawing figures, or auditing it."
---

# paperqa — Evidence-backed Question Answering over a Paper

Answer each supplied question and let the reader check it: every answer names the paragraph it came from, states the conditions under which it holds, and is marked `insufficient_evidence` when the paper doesn't say. The failure mode this skill exists to prevent: confident answers with no location, questions silently skipped, and "not reported" written as a fact.

**Method in one line:** index the numbered paragraphs → rank them per question by term overlap → compose the answer from the top paragraphs → set `status` honestly → cite paragraph ids and quotes.

## When to use

- Input: a case file (default `/input/case.json`) with `case_id`, `paper_id`, `material_version`, a paragraph list and a question list.
- Output: under `/app/output` — `answers.json`, `result.json`.

## Pipeline (run in order)

### Phase 1 — Retrieve evidence per question

```bash
python3 scripts/answer.py --case /input/case.json --work /app/work
```

- Normalizes `paragraphs[]` (inline text or objects with `paragraph_id`/`text`) and `questions[]` (`question_id`/`question`).
- Ranks paragraphs by term overlap (stop-words removed), keeps the top 5, and records `paragraph_id` + `quote` + matched terms + score.
- Sets `status` to `answered` when evidence exists, `insufficient_evidence` when it does not. **The script never writes the answer text** — that is the model's job.

### Phase 2 — Compose answers (model)

Read `answers.json` and the paragraphs, then for each question:

1. Write `answer` using only the cited paragraphs. Keep numbers and units exactly as the paper states them.
2. Fill `conditions[]`: the applicability conditions (material, method, range, assumptions) under which the answer holds.
3. Confirm or downgrade `status`:
   - `answered` — the paragraphs fully answer it;
   - `partial` — only part is answerable;
   - `insufficient_evidence` — the paper doesn't report it (leave `answer` empty and say so);
   - `input_error` — the question or material could not be read.
4. **Do not omit a question.** Every question_id must appear in `answers[]`.

### Phase 3 — Report

Copy to `/app/output`:

```bash
mkdir -p /app/output
cp /app/work/answers.json /app/work/result.json /app/output/
```

`result.json` carries `case_id`, `paper_id`, `material_version`, `status`, counts (`questions`/`answered`/`insufficient`), the full `answers[]`, `uncertainty`, `sources` and `changes`. Match the field names the case's output contract asks for; keep the meaning and hierarchy.

## Rules that must hold

1. **Every answer cites a paragraph.** An answer without a `paragraph_id` is not an answer.
2. **Numbers stay verbatim.** No rounding, converting or recomputing beyond what the paper states.
3. **Conditions are explicit.** What must hold for the answer to be valid (sample, method, range, assumption).
4. **No omission.** Unanswerable questions are `insufficient_evidence` with a note, never dropped.
5. **No outside knowledge.** The paper is the only source; general knowledge that contradicts it is not used.

## Exception handling

| Situation | Behaviour |
|-|-|
| Paragraph list empty | all questions `insufficient_evidence`; `status: partial` |
| Question list empty | `answers: []`, `status: partial` |
| Case fields missing | `paper_id`/`material_version` echoed as given (possibly empty) |
| Term overlap only partial | `partial` is available for the model to choose |

## Self-check

```bash
python3 -c "import json;a=json.load(open('/app/work/answers.json'));print([(x['question_id'], x['status'], len(x['evidence'])) for x in a['answers']])"
python3 -c "import json;r=json.load(open('/app/work/result.json'));print(r['case_id'], r['status'], r['counts'])"
```

Every `answered` item must have ≥1 evidence entry with a non-empty `quote`.
