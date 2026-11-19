# 自测记录（示例，非平台正式案例）

- 日期：2026-11-19
- 输入：本地构造的 3 段论文 + 3 个问题
- 命令：

```bash
python3 scripts/answer.py --case case.json --work .
```

## 结果摘要

| 问题 | 状态 | 证据段落 |
|-|-|-|
| Q1 BLEU | answered | 1（score 3） |
| Q2 GPU 数 | answered | 2（score 3） |
| Q3 法国首都 | insufficient_evidence | 无 |

## 验证要点

- 证据按词项重叠排序，返回段落号与引文；
- 无依据的问题标为 `insufficient_evidence`，不编造；
- 脚本不代写 answer 文本，留给模型基于证据撰写。

> 本文件为**技能自测示例**，不冒充平台正式案例结果。
