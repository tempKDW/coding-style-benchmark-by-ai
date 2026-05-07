# Subagent dispatch prompt 템플릿

답변 작성을 메인 세션에서 분리해 `general-purpose` subagent에 dispatch 할 때
사용하는 표준 프롬프트입니다. `<SCENARIO>` 를 실제 시나리오 디렉터리 이름으로
치환해서 그대로 복사·붙여넣기.

---

프로젝트 디렉터리: /Users/tempkdw/WorkSpace/llm-maintainability-benchmark

`reports/<SCENARIO>/prompts/` 디렉터리 안의 `.txt` 파일 N개를 각각 읽고, 각 파일에 적힌 Task 지시를 그대로 수행해 답변을 `reports/<SCENARIO>/answers/<stem>__run_1.txt` 에 저장하세요.

파일명 규칙: `prompts/foo__bar.txt` → `answers/foo__bar__run_1.txt`

각 prompt 파일 구조:
1. `Candidate: <filename>` 한 줄
2. `Task:` 다음에 작업 지시
3. 출력 형식 안내
4. `Code:` 다음에 수정 대상 Python 코드

답변 형식:
- prompt에 `Output the complete revised code only.` 가 있으면 (patch task): 수정된 전체 Python 코드만, markdown fence 없이 raw 코드. Task가 명시하지 않은 docstring/주석/공백 구조는 원본 그대로.
- prompt에 `JSON만 반환하세요.` 가 있으면 (analysis task): `{"target_locations": [...], "answer": "...", "confidence": 0.x}` 한 객체만.

작성 가이드 (반드시):
- 각 prompt에 적힌 Task와 그 아래의 Code 만을 근거로 답변. 다음 파일·디렉터리는 절대 참조 금지: `examples-<...>/`, `AGENTS.md`, `llm_code_benchmark/tasks.py`, `docs/scenario-mappings.md`, 다른 `reports/<...>/answers/` 디렉터리, `_mapping.json`.
- 답변을 임의로 길거나 짧게 부풀리지 말고, prompt가 요구하는 정확한 변경만.
- candidate 파일명(`Candidate:` 라인 값)을 답변 단서로 추측 금지. 단서는 코드 본문과 task 텍스트 뿐.
- patch 답변 작성 후 `python3 -c "import ast; ast.parse(open('답변파일경로').read())"` 로 syntax 확인. 실패시 수정 후 재저장.

완료 후 짧게 보고: 작성한 파일 경로 N개와 syntax 검증 결과 요약. 답변 내용 자체는 보고 금지.
