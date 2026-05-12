# NEXT SESSION PROMPT 2026-05-07 — 다음 세션 시작 가이드

> 이 문서는 다음 세션을 시작할 때 사용하는 프롬프트입니다. 
> 아래 "복붙용 프롬프트" 영역을 그대로 새 세션 첫 메시지로 사용하세요.

---

## 사용 방법

1. 새 Claude 세션 시작
2. 아래 **"복붙용 프롬프트"** 박스 안 내용을 그대로 복사 → 첫 메시지로 붙여넣기
3. Claude가 핸드오프 doc 자동 학습 후 다음 단계 안내

---

## 복붙용 프롬프트 (다음 세션 첫 메시지)

```
TAI Safe 작업 이어서 진행합니다.

먼저 다음 doc 읽고 컨텍스트 파악해주세요:
1. docs/extraction/HANDOFF_FINAL_2026-05-07.md (어제 통합 핸드오프 — 가장 중요)
2. docs/extraction/CURSOR_TASK_2026-05-07_decompose_v18.md (v1.8 patch 작업지시서)
3. docs/extraction/DESIGN_master_rule_v2_2026-05-07.md (master_rule_v2 설계)

저장소는 taiengineering/tai-admin (main only).

읽은 후 현재 진행도 + 다음 작업을 한 번 정리해주세요.
이후 진행 방향 답할게요.
```

---

## 다음 세션에서 Claude가 해야 할 일 (Claude 학습용)

### 1. 컨텍스트 학습 (필수)

다음 3개 doc을 순서대로 읽고 이해:

| 우선순위 | 파일 | 내용 |
|---|---|---|
| 1 | `HANDOFF_FINAL_2026-05-07.md` | 어제 작업 전체 요약 + 4계층 진행도 |
| 2 | `CURSOR_TASK_2026-05-07_decompose_v18.md` | v1.8 patch 명세 (Cursor 대기) |
| 3 | `DESIGN_master_rule_v2_2026-05-07.md` | master_rule_v2 5 테이블 설계 |

### 2. 현재 상황 파악

- **Layer 1** (semantic_clause): v1.7.1 → v1.8 보강 작업 중 (Cursor 대기)
- **Layer 2** (master_rule_v2): 5 테이블 생성 완료, 0 rows
- **Layer 3** (inspection_sets): 4가지 세팅 컬럼 보강 대기
- **Layer 4** (work_schedules): 인프라 준비됨

### 3. 다음 작업 후보 (우선순위 순)

| 후보 | 사용자가 보고할 내용 |
|---|---|
| **A** | "Cursor에서 v1.8 적용 완료, dry-run 결과 다음과 같음..." → 결과 검증 + 정확도 측정 |
| **B** | "v1.8 본 적용 완료, 무결성 검증 진행" → 5개 SQL 검증 + 새 문제점 발견 |
| **C** | "v1.8 통과, Phase B 본 변환 진입" → master_rule_v2 변환 알고리즘 작성 |
| **D** | "문제 발견, v1.9 보강 필요" → 추가 룰 설계 |
| **E** | 다른 작업 (Cursor sector 작업 / Phase D / etc.) |

### 4. 사용자 작업 원칙 재확인 (반드시 준수)

1. **AI/LLM 호출 0%** — 정규식/키워드 사전만
2. **검증 없는 완료 선언 금지** — "100% 완료", "사실상 PASS" 등 금지
3. **패턴 발견 → 룰 보강 → 재반복** (iterative refinement)
4. **정확함이 건수/비율보다 중요**
5. **ask_user_input_v0 사용 금지** — 텍스트로 직접 묻거나 즉시 실행
6. **200줄+ 파일은 GitHub MCP 직접 수정 금지** → Cursor 로컬
7. **비-OBLIGATION inherit는 needs_review로 마크** (silent failure 방지)
8. **의미절 출처 추적 가능** (FK), AI 임의판단 추적/차단

### 5. 사용자 의사소통 패턴

- 간결한 한국어 지시
- 즉시 실행 후 결과 보고 선호
- 방향이 잘못됐을 때 직접 지적 ("그게 아니라...")
- 검증 없는 완료 선언에 매우 민감
- 단계별 확인 후 진행 선호

### 6. 핵심 인프라 (반드시 기억)

```
Project ID: vwlahtguyggrhvslabax (Supabase 서울)
Repo:
  - taiengineering/tai-admin (main only — 이 저장소에 docs 있음)
  - taiengineering/tai-api (main only — 백엔드)
  - taiengineering/taieng (마케팅)

핵심 테이블:
  - semantic_clause (58,495 + sectors[] + recipient_text)
  - semantic_clause_iter1 (백업, 동일 스키마)
  - law_sector_mapping (366 법령)
  - master_rule_v2 + 4 부속 (executor/condition/exception/relation, 5 테이블 0 rows)

분해기:
  - docs/extraction/scripts/decompose_v1.py (v1.7.1, v1.8 patch 대기)
```

### 7. MCP 도구 사용 패턴

| 작업 | 도구 |
|---|---|
| DB 조회 | `supabase:execute_sql` |
| DB DDL | `supabase:apply_migration` (이름 고유) |
| 파일 읽기 | `github-tai:get_file_contents` 또는 `github-tai-admin:get_file_contents` |
| 파일 작성 | `github-tai-admin:create_or_update_file` (200줄+ 금지) |
| 코드 검색 | `github-tai:search_code` |

---

## 사용자 자주 쓰는 명령어 패턴

| 사용자 발화 | Claude 해석 |
|---|---|
| "yes" / "진행" / "A" / "옵션 A" | 직전 제안한 옵션 선택, 즉시 실행 |
| "그게 아니라..." | 방향 정정, Claude의 가정 재검토 |
| "전수검사" / "무결성 확인" | 모든 데이터 일관성 검증, 새 문제점 발굴 |
| "패턴 발견..." | 데이터 분석 후 룰 정정 또는 추가 |
| "사전작업 남았으면 먼저" | Phase 진입 전 인프라/표준 정비 우선 |
| "[기능]는 뭐죠?" | 용어/개념 설명 후 진행 |
| "이거 들어가기 전에 점검" | 본 작업 전 사전 검증 |

---

## 자주 만드는 실수 + 회피

| 실수 | 회피 방법 |
|---|---|
| 검증 없이 "100% 완료" 선언 | 항상 sample 검증 후 정확도 수치 보고 |
| AI/LLM 호출 (예: keyword 기반 자동 분류 시) | 정규식 + 키워드 사전만 사용 |
| ask_user_input_v0 (선택형 팝업) 사용 | 텍스트로 직접 옵션 제시 |
| 200줄+ 파일 GitHub MCP 직접 수정 | Cursor 작업지시서 작성 후 사용자에게 위임 |
| sectors[] 단일 컬럼 sector와 헷갈림 | 항상 sectors[] (배열) 우선 사용, sector는 deprecated |
| MANUFACTURING/INDUSTRY 변환 누락 | INDUSTRY → INDUSTRIAL 일괄 통일 |

---

## 확장 컨텍스트 (필요 시 참조)

이전 세션 핸드오프 시리즈:
- `HANDOFF_2026-05-05.md` — 분해기 v1.0~v1.4, KEC 완료
- `HANDOFF_2026-05-06_evening.md` — 의미절 v1.7.1 본 적용
- `HANDOFF_FINAL_2026-05-07.md` — 어제 통합 (가장 중요)

오늘(다음 세션) 만들 새 doc 명명 규칙:
- 작업지시서: `CURSOR_TASK_YYYY-MM-DD_<작업명>.md`
- Phase 완료: `PHASE_<X>_COMPLETE_YYYY-MM-DD.md`
- 핸드오프: `HANDOFF_YYYY-MM-DD.md`
- 무결성 검증: `<주제>_INTEGRITY_VERIFICATION_YYYY-MM-DD.md`

---

## 메모리 갱신 권고 (다음 세션 끝에)

다음 세션 마무리 시 사용자가 메모리 업데이트할 수 있도록 다음 내용 포함:

```
- 의미절 분해기 최신 버전 (v1.8 / v1.9 / v2.0)
- master_rule_v2 변환 진행도 (0 rows / 진행중 / 완료)
- 새 발견 패턴 또는 정책
- 미완료 TASK 갱신
```
