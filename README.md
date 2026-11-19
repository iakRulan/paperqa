# paperqa — 文献智能问答 Skill

逐题回答并给出依据：每个回答标注来源段落、成立条件与状态；无法回答的题目不省略、不编造。

## 解决什么问题

普通 Agent 的常见失败：回答没有出处；把"论文没报告"写成事实；跳过不会答的题；把段落拼错。

## 安装与依赖

- Python 3.9+，仅标准库
- 无需联网

```
paperqa/
├── SKILL.md
├── README.md
├── GITHUB_URL.txt
├── references/
│   ├── answer-status.md
│   └── output-schema.md
├── examples/
│   ├── case.example.json
│   └── selftest-summary.md
└── scripts/
    └── answer.py
```

## 用法（最小示例）

```bash
python3 scripts/answer.py --case /input/case.json --work /app/work
```

输入示例：

```json
{
  "case_id": "demo",
  "paper_id": "P001",
  "material_version": "v3",
  "paragraphs": [{"paragraph_id": "1", "text": "The model achieves 28.4 BLEU."}],
  "questions": [{"question_id": "Q1", "question": "What BLEU score did the model achieve?"}]
}
```

> 以上为**示意示例**，不是正式案例结果。

## 输出

| 文件 | 内容 |
|-|-|
| `answers.json` | 逐题：`question_id` / `question` / `answer` / `conditions[]` / `status` / `evidence[]` / `note` |
| `result.json` | `case_id` / `paper_id` / `material_version` / `status` / counts / answers / uncertainty |

## 状态定义

| status | 含义 |
|-|-|
| `answered` | 段落完整回答 |
| `partial` | 只能部分回答 |
| `insufficient_evidence` | 材料未报告（answer 留空并说明） |
| `input_error` | 输入读取失败 |

## 关键设计

- **证据检索**：按词项重叠排序段落，取前 5。
- **不省略**：每个 question_id 都必须出现在 answers[]。
- **不编造**：脚本不写 answer 文本，由模型基于证据撰写。
- **数值保真**：不四舍五入、不换算。

## 局限

- 词面检索可能漏掉同义表述，需模型补充检索词；
- 不评估论文方法学质量。

## 许可与版本

- 版本：paperqa 1.0.0
- 纯 Python 标准库。
