# LLM Maintainability Benchmark

## method_chain.py

- Average score: 92.94

| Task | Run | Score | Changed lines | Locations | Notes |
|---|---:|---:|---:|---:|---|
| rule_change | 1 | 89.69 | 2 | 0 |  |
| feature_add_local | 1 | 89.53 | 3 | 0 |  |
| feature_add_crosscut | 1 | 89.22 | 5 | 0 |  |
| extract_reuse | 1 | 100.0 | 0 | 2 |  |
| add_branch | 1 | 89.22 | 5 | 0 |  |
| explain_code | 1 | 100.0 | 0 | 0 |  |

## monolithic.py

- Average score: 92.73

| Task | Run | Score | Changed lines | Locations | Notes |
|---|---:|---:|---:|---:|---|
| rule_change | 1 | 89.2 | 2 | 0 |  |
| feature_add_local | 1 | 88.81 | 3 | 0 |  |
| feature_add_crosscut | 1 | 89.2 | 2 | 0 |  |
| extract_reuse | 1 | 100.0 | 0 | 2 |  |
| add_branch | 1 | 89.2 | 2 | 0 |  |
| explain_code | 1 | 100.0 | 0 | 0 |  |

## split_chain.py

- Average score: 92.51

| Task | Run | Score | Changed lines | Locations | Notes |
|---|---:|---:|---:|---:|---|
| rule_change | 1 | 89.49 | 2 | 0 |  |
| feature_add_local | 1 | 89.22 | 3 | 0 |  |
| feature_add_crosscut | 1 | 87.93 | 8 | 0 |  |
| extract_reuse | 1 | 100.0 | 0 | 1 |  |
| add_branch | 1 | 88.45 | 6 | 0 |  |
| explain_code | 1 | 100.0 | 0 | 0 |  |

## split_pipeline.py

- Average score: 88.70

| Task | Run | Score | Changed lines | Locations | Notes |
|---|---:|---:|---:|---:|---|
| rule_change | 1 | 89.56 | 2 | 0 |  |
| feature_add_local | 1 | 89.36 | 3 | 0 |  |
| feature_add_crosscut | 1 | 89.36 | 3 | 0 |  |
| extract_reuse | 1 | 100.0 | 0 | 2 |  |
| add_branch | 1 | 88.92 | 5 | 0 |  |
| explain_code | 1 | 75.0 | 0 | 0 |  |
