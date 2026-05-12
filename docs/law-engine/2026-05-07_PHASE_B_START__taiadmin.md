# PHASE B 진입 — 의미절 v1.8 보강 작업 시작 (2026-05-07)

> Phase A 완료 후 Phase B 시작 — 의미절 → master_rule_v2 변환의 base 정확도 향상.
>
> 사용자 결정: "의미절이 완벽해질때까지 의미절 작업만"

---

## Phase B 시작 배경

### 발견된 문제 — sample 20건 검증

master_rule_v2 변환 알고리즘 설계 중 의미절 sample 20건 분석 결과:

| 문제 | 영향 |
|---|---|
| **executor_text 깨짐** | "기본계획에", "변경하려는 경우에", "이 경우" 등 가짜 주어 |
| **NULL executor 23.7%** | 10,920건 추출 실패 |
| **condition_text 부정확** | 본문 그대로 = 의미 없음 |
| **exception_text 거의 빈 상태** | 단서 추출 미흡 |
| **수신자(recipient) 없음** | "~에게/~로" 패턴 미추출, 컬럼 자체도 없음 |
| **다중 행위자/수신자** | "사업주가 고용노동부장관에게 보고" 패턴 미처리 |

### 핵심 통찰 (사용자)

**"주어가 없는 경우, 상단(article)에 존재할 확률이 높음"**

법령 구조:
```
제42조 (안전보건진단)
  ① 사업주는 ~ 진단을 받아야 한다.   ← 주어 명시
     1. 위험작업                       ← 주어 없음, ① 상속
     2. 유해작업                       ← 주어 없음, ① 상속
```

**검증 결과** (NULL executor 10,951건):
- 같은 paragraph 내 inherit 가능: 5.8% (638건)
- **같은 article 내 inherit 가능: 83.1% (9,095건) ✅**
- 채울 수 없음: 16.9% (1,856건)

→ Article 단위 inherit이 핵심 보강.

---

## v1.8 보강 작업 — 옵션 B 채택

### 작업 범위 7가지

1. **FAKE_EXECUTOR 필터** — 부사구/조건절/종속어 가짜 주어 제거
2. **extract_executor_text() 정정** — 가짜 검사 추가
3. **NO_INHERIT_PATTERNS** — 위임/수범 조항 inherit 금지 룰
4. **paragraph 단위 inherit** — 같은 part 내 첫 valid executor를 NULL 의미절에 적용
5. **article 단위 inherit (post-processing)** — 같은 article의 다른 paragraph에서 inherit
6. **recipient_text 추출** — `~에게/~한테/~로` 정규식 신규 패턴
7. **decomposition_version v1.8 표기**

### 작업지시서 push 완료
`docs/extraction/CURSOR_TASK_2026-05-07_decompose_v18.md`

---

## DB 사전 작업 (이미 완료)

### recipient_text 컬럼 추가

```sql
ALTER TABLE semantic_clause ADD COLUMN recipient_text TEXT;
ALTER TABLE semantic_clause_iter1 ADD COLUMN recipient_text TEXT;
CREATE INDEX idx_semantic_clause_recipient ON semantic_clause(recipient_text) 
  WHERE recipient_text IS NOT NULL;
```

✅ 완료 (2026-05-07)

---

## 다음 단계 — Cursor 작업

### Step 1. 로컬 분해기 수정

```bash
# Cursor에서
cd docs/extraction/scripts
# decompose_v1.py 수정 (CURSOR_TASK_2026-05-07_decompose_v18.md 참고)
```

### Step 2. dry-run 검증

```bash
python decompose_v1.py --dry-run --sample-size 200 --sampling stratified --seed 42
```

### Step 3. 정확도 측정

| 지표 | v1.7.1 (현재) | v1.8 (목표) |
|---|---|---|
| executor 채움률 | 76% | >90% |
| 가짜 executor | 3,224건 | 0건 |
| recipient 채움률 | 0% | >70% (보고/신고/제출) |
| Article inherit | 0건 | ~9,000건 |

### Step 4. 본 적용 (정확도 90%+ 도달 시)

```bash
python decompose_v1.py --apply --truncate-first --sample-size 100000
```

### Step 5. 무결성 재검증 (사용자 지시)

```sql
-- 1. executor 채움률
-- 2. 가짜 executor 잔존 (0이어야)
-- 3. recipient 채움률
-- 4. inherit 적용 분포
-- 5. needs_review 분포
```

### Step 6. 새 문제점 발견 시 v1.9 보강 (iterative)

---

## 4계층 흐름 진행도 (현재)

```
[Layer 1] semantic_clause (58,495)        ← 🔄 v1.8 보강 작업 중
              │
              │ (Phase B 본 변환은 v1.8 완료 후)
              ▼
[Layer 2] master_rule_v2 (44 cols, 0 rows) ← ✅ Phase A 완료 (DDL만), Phase B 변환 대기
              │
              ▼
[Layer 3] inspection_sets (324)            ← 🟡 Phase D 컬럼 보강 대기
              │
              ▼
[Layer 4] work_schedules (0)              ← ✅ 인프라 준비됨
```

---

## master_rule_v2 부속 테이블 추가 완료 (Phase A 보강)

사용자 지시 — "객체화" 결정에 따라 4 부속 테이블 추가 생성:

| 테이블 | 역할 |
|---|---|
| `master_rule_v2` | 메인 룰 (43 컬럼) |
| `master_rule_executor` | 행위자/수신자/대체 (1:N) |
| `master_rule_condition` | 조건 (if, 1:N) |
| `master_rule_exception` | 예외/단서 (but, 1:N) |
| `master_rule_relation` | 룰 간 관계 (다대다) |

5 테이블 모두 생성 완료 (DDL만, 0 rows).

---

## 작업 원칙 재확인

1. **AI/LLM 호출 0%** — 정규식/키워드 사전만
2. **검증 없는 완료 선언 금지**
3. **패턴 발견 → 룰 보강 → 재반복** (iterative)
4. **정확함이 건수보다 중요**
5. **200줄+ 파일은 GitHub MCP 직접 수정 금지** → Cursor 로컬

---

## 핵심 인프라

- Project ID: `vwlahtguyggrhvslabax` (서울)
- 의미절: `semantic_clause` (58,495 rows + sectors[] + recipient_text)
- 백업: `semantic_clause_iter1` (동일 스키마)
- 분해기: `docs/extraction/scripts/decompose_v1.py` (v1.7.1 → v1.8 보강 대기)
- master_rule_v2 + 4 부속 테이블 (Phase A 완료)

---

## 관련 문서

- `HANDOFF_2026-05-07.md` — 어제 핸드오프
- `PHASE_A_COMPLETE_2026-05-07.md` — Phase A (master_rule_v2 생성)
- `CURSOR_TASK_2026-05-07_decompose_v18.md` — **v1.8 patch 작업지시서**
- `DESIGN_master_rule_v2_2026-05-07.md` — master_rule_v2 설계
- 본 문서 — Phase B 시작 + v1.8 진입
