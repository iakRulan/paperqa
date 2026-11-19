# 回答状态与证据

## 证据检索

对每个问题：

1. 分词并去停用词（英文常见疑问词与虚词）。
2. 对每个段落计算命中词数 `hits` 与覆盖度 `coverage = hits / |question_terms|`。
3. 按 `(hits, coverage)` 降序，保留前 5 条。
4. 记录 `paragraph_id` / `quote`（≤400 字符）/ `matched_terms` / `score`。

## 状态判定

| status | 判据 |
|-|-|
| `answered` | 有证据且段落能完整回答（模型确认） |
| `partial` | 有证据但只能部分回答 |
| `insufficient_evidence` | 无任何命中段落：answer 留空，note 说明 |
| `input_error` | 输入读取失败 |

脚本只给出 `answered` / `insufficient_evidence` 的初判；`partial` 与 `input_error` 由模型按实际情况设置。

## 回答要求

- `answer` 只依据所引段落；数值、单位、样本量与原文一致。
- `conditions[]` 列出适用条件：材料体系、方法、量程、假设、边界。
- 不引入论文之外的知识；与论文冲突的常识不用。
- 每个 `question_id` 必须出现一次，不得省略。

## 输出层级（与赛题契约对齐）

```
case_id
paper_id
material_version
answers[]:
  question_id
  question
  answer
  conditions[]
  status
  evidence[]: {paragraph_id, quote, matched_terms, score}
  note
```
