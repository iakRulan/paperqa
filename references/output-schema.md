# 输出字段字典

## `answers.json` / `result.json`

| 字段 | 说明 |
|-|-|
| `case_id` | 输入标识，与案例一致 |
| `paper_id` | 论文标识，原样回传 |
| `material_version` | 材料版本，原样回传 |
| `answers[]` | 逐题回答（见下） |
| `status` | `complete` / `partial` |
| `counts` | `questions` / `answered` / `insufficient` |
| `uncertainty` | 限制说明 |
| `sources` / `changes` | |

## `answers[]`

| 字段 | 类型 | 说明 |
|-|-|-|
| `question_id` | string | 与案例问题标识一致 |
| `question` | string | 问题原文 |
| `answer` | string | 回答文本（模型撰写；无证据时为空） |
| `conditions[]` | array | 成立条件 |
| `status` | string | answered/partial/insufficient_evidence/input_error |
| `evidence[]` | array | `paragraph_id` / `quote` / `matched_terms` / `score` |
| `note` | string | 无法回答时的说明 |

字段名可按平台适配，但含义与层级保持一致。
