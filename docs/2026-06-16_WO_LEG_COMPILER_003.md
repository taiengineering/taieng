# WO-LEG-Compiler-003: Actor Resolution Overlay

**작성일**: 2026-06-16  
**담당**: GPT (실행) + Claude (Supabase 적용)  
**상태**: GPT 작업 대기

---

## ⚠️ 이 WO의 목적

```
Actor Resolution의 역할 = 분류(Classification)
Actor Resolution의 역할 ≠ 제거(Filter)

성공 기준:
  "행정청 의무를 제거했다" → 아님
  "행정청 의무임을 표시할 수 있게 됐다" → 맞음

DROP 여부는 이 WO에서 결정하지 않는다.
DROP/KEEP는 D-002 Common Sieve 또는 D-006 Reverse Check 영역이다.
```

---

## ⚠️ 이 WO의 위치 (15차 흐름상)

```
오염 71%의 직접 원인은 Actor UNKNOWN이 아니다.
직접 원인: employee_count 280 ≥ 50 → 도메인 불문 APPLICABLE

예시:
  의료법·장애인연금법·학교안전공제·협회설립·위원회운영
  → 전부 "근로자 수 조건 충족" 하나로 통과

따라서 이 WO는 오염 해결 WO가 아니다.
이 WO는 D-004B 입력 데이터 준비 작업이다.

올바른 순서:
  D-004A 관찰 완료 (✅)
  ↓
  Actor Overlay 적용 (이 WO)
  ↓
  K-01~05 측정 (오염 감소량 확인)
  ↓
  주원인이 Actor인지 Domain인지 분리
  ↓
  D-004B 설계

가장 위험한 착각:
  "ACTOR UNKNOWN 43,432건을 해결하면 71% 오염이 해결될 것이다"
  → 실측 데이터상 아직 그 인과관계는 증명되지 않음
  → K-01~05가 증명 실험이다
```

---

## 배경

`/refinery/run?limit=500` 결과 209건 중 71%가 오염.
오염의 직접 원인은 `binding_field = employee_count` 하나로 도메인 불문 매칭.
Actor Overlay는 이 오염 중 "Actor 분류로 줄일 수 있는 부분"을 측정하는 도구다.

---

## 목표

`semantic_clause_fix`의 `executor_text` / `executor_fixed` 기준으로
명시적 주체를 ACTOR 코드로 분류한 오버레이 테이블을 생성한다.

**원본 `semantic_clause_fix` 수정 절대 금지.**

---

## 산출 테이블

### 테이블 1: `semantic_clause_actor_resolution`

```sql
CREATE TABLE semantic_clause_actor_resolution (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clause_id UUID NOT NULL,         -- semantic_clause_fix.id
    actor_raw TEXT,                  -- 원본 executor_text 또는 executor_fixed
    source_executor_field TEXT,      -- 'executor_text' 또는 'executor_fixed'
    actor_code TEXT,                 -- ACTOR:OWNER / ACTOR:GOV 등
    actor_group TEXT,                -- BUSINESS / AUTHORITY / ASSOCIATION / FRAGMENT / UNKNOWN
    confidence TEXT,                 -- HIGH / MEDIUM / LOW / REVIEW
    resolution_method TEXT,          -- RULE / LLM / MANUAL
    matched_pattern TEXT,            -- 매칭된 패턴 텍스트
    needs_review BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now()
);
-- DROP 여부 컬럼 없음 (분류만, 제거 결정은 이 테이블 범위 밖)
```

### 테이블 2: `actor_resolution_pattern`

```sql
CREATE TABLE actor_resolution_pattern (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern TEXT NOT NULL,
    actor_code TEXT NOT NULL,
    actor_group TEXT NOT NULL,
    match_type TEXT DEFAULT 'contains',  -- exact / contains / startswith
    priority INT DEFAULT 0,              -- 낮을수록 우선 (0이 최우선)
    note TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);
```

---

## ACTOR 코드 체계

```
BUSINESS 계열 (사업 주체):
  ACTOR:OWNER         사업주, 사업자, 고용주, 경영자
  ACTOR:CONSTRUCTOR   건축주, 시공자, 도급인, 수급인, 관계수급인
  ACTOR:MANUFACTURER  제조자, 제조업자, 수입자, 판매자
  ACTOR:MANAGER       관리주체, 관리자, 소유자, 점유자, 임차인

AUTHORITY 계열 (행정청 / 기관):
  ACTOR:GOV           장관, 대통령, 총리, 청장, 원장
  ACTOR:LOCAL_GOV     시장, 도지사, 군수, 구청장, 시·도지사
  ACTOR:AGENCY        공단, 안전보건공단, 근로복지공단, 공사

ASSOCIATION 계열 (별도 분리 — needs_review=true 권장):
  ACTOR:ASSOCIATION   협회, 조합, 연합회, 공제조합
  → confidence = MEDIUM, needs_review = true
  → 회원 사업자 의무인지 협회 자체 의무인지 맥락 확인 필요

FRAGMENT 계열 (주체 아닌 토큰):
  ACTOR:FRAGMENT
  → 효과, 경우, 해당, 다음, 이 경우, 정하는, 따른
  → 사항, 기준, 절차, 방법, 내용, 요건, 범위,
     비용, 금액, 결과, 조치, 자료, 서류, 기록

UNKNOWN:
  ACTOR:UNKNOWN       분류 불가 — 원본 그대로 보존, PENDING 처리
```

---

## Overlay 생성 SQL 원칙

패턴 매칭 시 **긴 패턴 우선** 적용:

```sql
ORDER BY
  length(pattern) DESC,  -- 긴 패턴 우선 (시·도지사 > 도지사)
  priority ASC           -- 우선순위 낮을수록 먼저
LIMIT 1                  -- 가장 먼저 맞는 패턴 1개 선택
```

---

## 성공 기준 (K-01~05)

Actor Overlay 완료 후 반드시 아래 5개를 측정한다.
이것이 "Actor 문제인가 vs Domain 문제인가"를 분리하는 실험이다.

```
K-01: 209건 결과에 Actor Overlay 적용
      → actor_group별 건수 집계

K-02: AUTHORITY 제거 시 감소량 측정
      → 209건 중 AUTHORITY 건수 / 제거 후 잔존 건수

K-03: ASSOCIATION 제거 시 감소량 측정
      → ASSOCIATION 건수 / 제거 후 잔존 건수

K-04: BUSINESS만 남겼을 때 잔존 오염률 측정
      → 남은 의무 중 실제 무관 법령 비율 (글읽기)

K-05: Top 50 잔존 오염 사례 분석
      → BUSINESS actor인데 여전히 무관한 것들 목록화
      → 예상: 건설기계대여업, 의료기관, 공동주택 등
      → 이것이 Domain 문제임을 확인하는 단계
```

K-04, K-05 결과로 다음 WO(D-004B vs Domain Rule WO) 결정.

---

## GPT에게 요청하는 산출물

### 1. 패턴 룰 CSV
`actor_resolution_pattern` 입력용 전체 목록
```
pattern, actor_code, actor_group, match_type, priority, note
사업주, ACTOR:OWNER, BUSINESS, contains, 0,
건축주, ACTOR:CONSTRUCTOR, BUSINESS, contains, 0,
시·도지사, ACTOR:LOCAL_GOV, AUTHORITY, exact, 0,
도지사, ACTOR:LOCAL_GOV, AUTHORITY, contains, 10,
...
```

### 2. 적용 SQL
`semantic_clause_actor_resolution` 생성 쿼리.
Claude가 Supabase `execute_sql`로 실행할 수 있는 형태.

### 3. 실측 통계 (추정 아닌 실측)
```
전체 clause:        53,053건
매칭 성공:          N건
  BUSINESS:         N건
  AUTHORITY:        N건
  ASSOCIATION:      N건 (REVIEW 대상)
  FRAGMENT:         N건
UNKNOWN 잔존:       N건
REVIEW 필요:        N건
```

### 4. REVIEW 목록
HIGH confidence 아닌 것들, 2차 작업 후보.

---

## 절대 금지

```
semantic_clause_fix 테이블 UPDATE/DELETE 금지
DROP 여부를 actor_resolution 테이블에 저장 금지
ACTOR:ASSOCIATION을 HIGH confidence로 표기 금지
LLM 판단을 HIGH confidence로 표기 금지
패턴 매칭 없이 임의 추측으로 actor_code 부여 금지
```

---

## 참고 데이터

현재 `semantic_clause_fix` 실측:
- 전체: 53,053건
- executor_text 샘플 상위: 시·도지사(다수), 효과, 일반수도사업자, 사업주, 간사 등
- ACTOR UNKNOWN family: 43,432건 (82%)

관련 문서:
- `taiengineering/taieng/docs/2026-06-11_LEGAL_ENGINE_V4_LAYER_REDESIGN.md` (v2.1)
- `taiengineering/taieng/docs/2026-06-16_WO_D_PIPELINE_IMPL.md`
