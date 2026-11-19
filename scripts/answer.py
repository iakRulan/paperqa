#!/usr/bin/env python3
"""answer — question answering over a numbered paper, with evidence.

Usage:
    python3 answer.py --case /input/case.json --work /app/work

The case supplies `case_id`, `paper_id`, `material_version`, a paragraph list
(`paragraphs[]` with `paragraph_id`/`text`, or a text file with numbered
paragraphs) and a question list (`questions[]` with `question_id`/`question`).

For every question this script:
  * ranks paragraphs by term overlap,
  * marks the answerable status,
  * records the exact paragraph ids and quotes that ground the answer.

It never writes a final answer on its own: the model reads the evidence and
composes `answer` + `conditions`, then sets `status`. Questions with no
supporting paragraph are `insufficient_evidence`, not guessed.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

VERSION = "1.0.0"

STOP = {"the", "and", "for", "of", "in", "on", "a", "an", "to", "with", "by",
        "from", "is", "are", "as", "at", "that", "this", "what", "which",
        "what's", "how", "why", "when", "where", "does", "do", "did", "is",
        "are", "was", "were", "can", "could", "we", "our", "their", "its"}


def load(path: Path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def save(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


def tokenize(text):
    return [t for t in re.findall(r"[a-z0-9]{2,}", (text or "").lower()) if t not in STOP]


def load_case(case_path: Path) -> dict:
    case_path = Path(case_path)
    if case_path.is_dir():
        return {"case_id": case_path.name, "paper_id": "", "material_version": "",
                "paragraphs": [], "questions": [], "raw": {}}
    raw = load(case_path)
    case = dict(raw) if isinstance(raw, dict) else {"value": raw}
    paras = case.get("paragraphs") or case.get("paragraph_list") or case.get("passages") or []
    questions = case.get("questions") or case.get("question_list") or case.get("queries") or []
    # paragraphs may be file paths or inline strings
    norm_paras = []
    for i, p in enumerate(paras):
        if isinstance(p, str):
            norm_paras.append({"paragraph_id": str(i + 1), "text": p})
        elif isinstance(p, dict):
            norm_paras.append({
                "paragraph_id": str(p.get("paragraph_id") or p.get("id") or i + 1),
                "text": p.get("text") or p.get("content") or "",
            })
    norm_qs = []
    for i, q in enumerate(questions):
        if isinstance(q, str):
            norm_qs.append({"question_id": f"Q{i+1}", "question": q})
        elif isinstance(q, dict):
            norm_qs.append({
                "question_id": str(q.get("question_id") or q.get("id") or f"Q{i+1}"),
                "question": q.get("question") or q.get("q") or q.get("text") or "",
            })
    return {
        "case_id": case.get("case_id") or case.get("id") or case_path.stem,
        "paper_id": str(case.get("paper_id") or case.get("paper") or ""),
        "material_version": str(case.get("material_version") or case.get("version") or ""),
        "paragraphs": norm_paras,
        "questions": norm_qs,
        "raw": case,
    }


def rank(question_terms, paragraphs):
    terms = set(question_terms)
    scored = []
    for p in paragraphs:
        text = p.get("text", "")
        hay = text.lower()
        hits = [t for t in terms if t in hay]
        if not hits:
            continue
        scored.append((len(hits), len(hits) / len(terms), hits, p))
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return scored


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", required=True)
    ap.add_argument("--work", required=True)
    args = ap.parse_args(argv)

    case = load_case(Path(args.case))
    work = Path(args.work)
    work.mkdir(parents=True, exist_ok=True)

    answers = []
    for q in case["questions"]:
        terms = tokenize(q["question"])
        scored = rank(terms, case["paragraphs"])
        top = scored[:5]
        if top:
            status = "answered"  # model confirms/refines
            evidence = [
                {"paragraph_id": p["paragraph_id"], "quote": p["text"][:400],
                 "matched_terms": hits, "score": n}
                for n, cov, hits, p in top
            ]
        else:
            status = "insufficient_evidence"
            evidence = []
        answers.append({
            "question_id": q["question_id"],
            "question": q["question"],
            "answer": "",
            "conditions": [],
            "status": status,
            "evidence": evidence,
            "note": None if evidence else "在所提供的段落中未找到可定位依据",
        })

    out = {
        "case_id": case["case_id"],
        "paper_id": case["paper_id"],
        "material_version": case["material_version"],
        "paragraph_count": len(case["paragraphs"]),
        "answers": answers,
        "uncertainty": [
            "证据来自给定段落，不外推未提供的信息；",
            "answer 文本需模型基于证据撰写，条件与适用边界需人工确认。",
        ],
        "script_version": VERSION,
    }
    save(work / "answers.json", out)

    result = {
        "case_id": case["case_id"],
        "paper_id": case["paper_id"],
        "material_version": case["material_version"],
        "task": "paper-question-answering",
        "status": "complete" if all(a["evidence"] for a in answers) else "partial",
        "deliverables": {"answers": "answers.json"},
        "counts": {
            "questions": len(answers),
            "answered": sum(1 for a in answers if a["evidence"]),
            "insufficient": sum(1 for a in answers if not a["evidence"]),
        },
        "answers": answers,
        "uncertainty": out["uncertainty"],
        "sources": [str(Path(args.case))],
        "changes": [
            {"step": "retrieve", "detail": f"{len(case['paragraphs'])} paragraphs indexed"},
            {"step": "answer", "detail": f"{sum(1 for a in answers if a['evidence'])}/{len(answers)} with evidence"},
        ],
    }
    save(work / "result.json", result)
    print(f"answer: {len(answers)} questions, "
          f"{sum(1 for a in answers if a['evidence'])} with evidence -> {work / 'answers.json'}")
    return out


if __name__ == "__main__":
    main()
