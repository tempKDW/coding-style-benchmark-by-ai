# LLM Maintainability Benchmark

짧은 예시 코드를 여러 구현 스타일로 두고, LLM이 얼마나 쉽게 읽고 수정하는지 비교하는 작은 벤치마크입니다.

## 측정하는 5개 태스크

- `locate_change`: 변경해야 할 위치 찾기
- `policy_change`: 기존 정책 변경
- `feature_add`: 새 정책 추가
- `edge_bugfix`: edge case 버그 수정
- `explain_code`: 코드 흐름과 변경 지점 설명

## 실행

프롬프트만 확인:

```bash
python3 benchmark.py --dry-run
```

샘플 답변으로 리포트 생성:

```bash
python3 benchmark.py --sample
```

실제 LLM 호출 — 평가자(=작업을 수행하는 LLM)는 작업 환경에 맞춰 OpenAI 또는 Anthropic을 고를 수 있습니다. 비교의 축은 LLM이 아니라 `examples/` 안의 **코드 스타일**이며, provider는 단지 손에 잡힌 키에 맞춰 바꿔 쓰는 용도입니다.

OpenAI 키가 있을 때 (Codex CLI 환경 등):

```bash
OPENAI_API_KEY=... python3 benchmark.py --model gpt-4.1-mini
```

Anthropic 키가 있을 때 (Claude Code 환경 등):

```bash
ANTHROPIC_API_KEY=... python3 benchmark.py --model claude-opus-4-7
```

provider는 모델명 prefix로 자동 감지됩니다 (`gpt-`, `o1-`, `o3-`, `o4-` → openai / `claude-` → anthropic). 자동 감지가 어려운 경우 `--provider` 로 명시할 수 있습니다.

반복 실행 (같은 평가자로 노이즈를 줄이고 스타일별 점수 차이를 명확히 보고 싶을 때):

```bash
ANTHROPIC_API_KEY=... python3 benchmark.py --model claude-sonnet-4-6 --runs 5
```

결과는 `reports/report.md`, `reports/scores.csv`, `reports/scores.json`에 생성됩니다.

## 점수 해석

총점은 100점 기준입니다.

- 정답성: 40
- 변경 위치 정확도: 20
- diff 최소성: 15
- edge case 보존: 15
- 설명 품질: 10

짧은 코드에서는 성공/실패만으로 차이가 잘 드러나지 않기 때문에, 변경 라인 수, 변경 지점 수, 설명 품질 같은 마찰 비용을 함께 봅니다.
