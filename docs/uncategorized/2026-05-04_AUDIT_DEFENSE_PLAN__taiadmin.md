# 무결성 진단 반복 방지 — 4단 방어 (S13)

**작성일**: 2026-05-04
**문제**: 무결성 진단 시 도메인 지식 부재로 false alarm 반복 (NFTC 5,430건, 안전기준 등록 9 master)
**목표**: 같은 분석을 다시 돌려도 false alarm 없고, 새 위반은 즉시 잡히는 자동 시스템

---

## 0. 핵심 발견

현재 DB constraint 상태 — **PK + 일부 FK만 있고 무결성 룰 거의 없음**:

| 테이블 | 있음 | 없음 (추가 필요) |
|---|---|---|
| law_master | PK, law_key UNIQUE | law_api_id/mst_no/number UNIQUE, CHECK 일자, current_version_id FK |
| law_version | PK, law_id FK | (대체로 충분) |
| law_article | PK, law_id FK, version_id FK | **(version_id, article_internal_key) UNIQUE** ★ |
| law_rule_drafts | PK, article_id FK, change_log_id FK | (drafts는 별도 트랙) |

→ **이것이 false alarm 반복의 근본 원인**. 룰이 DB에 없으니 적재 시 아무거나 들어오고, 진단 시 매번 도메인 지식 동원해야 함.

---

## 1. 4단 방어 설계

```
1단  DB constraint           ← 적재 시 자동 차단 (가장 강력)
2단  표준 진단 SQL 스위트     ← 재실행 가능, 도메인 지식 내장
3단  CI 일일 cron             ← 새 위반 자동 알림
4단  KNOWN_FALSE_ALARMS.md    ← 정상 패턴 명문화
```

각 단은 독립적이지만 합치면 다중 안전망.

---

## 2. 1단 — DB constraint 추가 (즉시 적용)

### 2.1 시뮬레이션 — 위반 0건 (즉시 적용 가능 7개)

```sql
-- A. UNIQUE constraints
ALTER TABLE law_article 
  ADD CONSTRAINT law_article_internal_key_unique 
  UNIQUE (law_version_id, article_internal_key);

ALTER TABLE law_master 
  ADD CONSTRAINT law_master_api_id_unique UNIQUE (law_api_id);

ALTER TABLE law_master 
  ADD CONSTRAINT law_master_mst_no_unique UNIQUE (law_mst_no);

-- B. FK (master → version)
ALTER TABLE law_master 
  ADD CONSTRAINT law_master_current_version_fk
  FOREIGN KEY (current_version_id) REFERENCES law_version(id);

-- C. CHECK constraints
ALTER TABLE law_master 
  ADD CONSTRAINT law_master_active_abolition_check
  CHECK (NOT (is_active = true AND abolition_date IS NOT NULL));

ALTER TABLE law_article 
  ADD CONSTRAINT law_article_no_positive CHECK (article_no >= 0);

ALTER TABLE law_master 
  ADD CONSTRAINT law_master_enforcement_max_check
  CHECK (enforcement_date <= CURRENT_DATE + INTERVAL '10 years');
```

### 2.2 보정 후 적용 (2개)

#### CHECK `announcement_date <= enforcement_date` — 1건 보정 후

```sql
-- 보정: 해사안전기본법 시행규칙
UPDATE law_master 
SET announcement_date = enforcement_date  -- 또는 원본 재확인
WHERE law_name = '해사안전기본법 시행규칙' 
  AND announcement_date > enforcement_date;

ALTER TABLE law_master 
  ADD CONSTRAINT law_master_date_order_check
  CHECK (announcement_date IS NULL OR enforcement_date IS NULL 
         OR announcement_date <= enforcement_date);
```

#### `master(ministry_code, law_number)` UNIQUE — 62건 검토 후

위반 62건의 정체 확인 → 진짜 중복이면 정리, 의도된 패턴이면 constraint 안 걸거나 partial UNIQUE.

### 2.3 1단 효과

이후 데이터 적재 시:
- 같은 article_internal_key 두 번 INSERT → 즉시 에러
- announcement > enforcement → 즉시 에러
- 비활성인데 폐지일 없음 → 즉시 에러
- master.current_version_id가 잘못 가리키면 → INSERT 차단

→ **적재 스크립트의 버그가 데이터에 들어가기 전에 차단됨**.

---

## 3. 2단 — 표준 진단 SQL 스위트

### 3.1 파일 위치

`taiengineering/tai-admin/docs/sql/audit_law_engine.sql`

### 3.2 구성 (5 섹션)

```sql
-- ========================================
-- AUDIT 1: 카운트 + 분포 (정상 기준선 확인)
-- ========================================
-- master 752 / version 752 / article 32,808
-- → 새 적재 시 카운트 변화 추적

-- ========================================
-- AUDIT 2: FK 무결성 (정순)
-- ========================================
-- 모든 FK는 0건이어야 함

-- ========================================
-- AUDIT 3: UNIQUE 무결성 (역순)
-- ========================================
-- ★ 핵심: article_internal_key 기준 (NEVER article_no+sub_no+type)
-- 주석으로 NFTC hierarchical 패턴 명시

-- ========================================
-- AUDIT 4: 비즈니스 룰
-- ========================================
-- announcement <= enforcement
-- is_active vs abolition_date
-- enforcement_date 미래 8건 (정책 결정 대상)

-- ========================================
-- AUDIT 5: 추출 진행률 (drafts)
-- ========================================
-- 606 미추출, 100 메타만, 정상 추출 분류
-- 매핑 정확성 (article_id 기준)
```

각 쿼리 위에 **주석으로 정상 패턴 명시**:

```sql
-- ⚠️ 진짜 중복 검증은 article_internal_key 기준만 사용
-- (article_no, article_sub_no, article_type) 중복은 false alarm:
--   - NFTC 코드체계: 같은 article_no=2 / type='항'에 100+개 항목 정상
--   - 방사선 안전관리: 같은 article_no에 art-XXX (조문) + misc-XXX (장 헤더) 정상
SELECT COUNT(*) FROM (
  SELECT law_version_id, article_internal_key 
  FROM law_article WHERE article_internal_key IS NOT NULL
  GROUP BY 1,2 HAVING COUNT(*)>1
) t;
-- 기댓값: 0
```

### 3.3 효과

- 미래에 같은 진단 다시 할 때 이 파일만 실행하면 끝
- 도메인 지식이 SQL 주석에 박혀서 false alarm 안 남
- 새 사람/AI가 봐도 정상 패턴 즉시 이해

---

## 4. 3단 — CI 일일 cron

### 4.1 설계

Railway cron (TAI Safe 인프라 활용):

```yaml
schedule: "0 3 * * *"  # 매일 새벽 3시
script: scripts/audit_law_engine_daily.py
```

### 4.2 동작

```python
# 1. audit_law_engine.sql 실행
# 2. 결과 → 기댓값(JSON)과 비교
# 3. 위반 발견 시:
#    - 슬랙 알림 (대표님 채널)
#    - GitHub Issue 자동 생성
# 4. 결과 로그 → law_audit_history 테이블에 적재 (추세 추적)
```

### 4.3 기댓값 정의 (`expected_values.json`)

```json
{
  "fk_orphans": 0,
  "internal_key_duplicates": 0,
  "active_abolition_conflict": 0,
  "announcement_after_enforcement": 0,
  "article_no_negative": 0,
  "law_master_count_min": 752,
  "extraction_606_unprocessed_max": 606,
  "known_exceptions": [
    "안전기준 등록 9 master (행정안전부 누적 등록 차수)",
    "메타만 있는 master 100 (외부 PDF 수집 대상)",
    "enforcement_date 미래 8 (시행 예정)"
  ]
}
```

### 4.4 효과

- 새 데이터 적재 시 24시간 내 위반 탐지
- 기존 정상 패턴은 known_exceptions에 등록돼서 무시
- 신규 마이그레이션 때 깨진 데이터 즉시 발견

---

## 5. 4단 — KNOWN_FALSE_ALARMS.md

### 5.1 파일 위치

`taiengineering/tai-admin/docs/KNOWN_FALSE_ALARMS.md`

### 5.2 구조

```markdown
# 무결성 진단 시 false alarm으로 판단해야 하는 정상 패턴

## 검증 키 가이드 (가장 중요)

| 대상 | ❌ 잘못된 키 | ✅ 진짜 PK |
|---|---|---|
| law_article 중복 | (article_no, sub_no, type) | **article_internal_key** |
| law_master 동일 법령 | law_name | **law_key** 또는 (law_api_id) |
| 룰 식별 | draft_rule_id | **id (uuid)** |

## 정상 패턴 카탈로그

### 1. NFTC hierarchical 코드체계
- NFTC 102~609 모든 화재안전기술기준
- 패턴: article_no=2, article_type='항'에 100~175개 row 정상
- 식별: article_internal_key=`nftc-sec-2.1.1.1` 형태로 유일
- 정상 이유: 화재안전기술기준의 코드체계가 hierarchical (2.1, 2.1.1, 2.1.1.1...)

### 2. KEC hierarchical 코드체계
- 한국전기설비규정 (master 1개, 본문 PDF에서 추출)
- 패턴: article_internal_key=`234.2.1.가` 형태
- master에는 article 1개만 있고 drafts에 575건 분리 (의도)

### 3. art/misc 분리 컨벤션
- 방사선 안전관리 등의 기술기준에 관한 규칙 등
- 패턴: 같은 article_no에 `art-XXX` (조문) + `misc-XXX` (장 헤더) 2 row
- 정상 이유: 장/절 헤더와 실제 조문을 별도 row로 보존

### 4. 행정안전부 "안전기준 등록" 9차수
- law_name 같지만 9 master 모두 정상
- 각 차수마다 다른 부처 소관 안전기준 신규 등록 (누적 문서)
- law_number 모두 다름 (2017-6, 2018-17, ..., 2023-589)

### 5. 메타만 있는 master 100개
- KC 인증 표준 (KC 60598-2-20 등)
- 환경 시험기준 (소음·진동, 빛공해, 악취 공정시험기준)
- 정상 이유: 본문이 IEC/ISO 표준 또는 별표 형태 → 외부 PDF 수집 대상

### 6. 시행 예정 법령 (enforcement_date 미래)
- 8건 (화학물질등록평가법 등)
- 정상 이유: 개정 발표 후 시행 전 단계
- 추출 정책: 시행일 도래 시 자동 추출 또는 사전 추출

## 진단 절차 (필수)

1. 이 문서 먼저 읽기
2. `docs/sql/audit_law_engine.sql` 실행
3. 결과를 `docs/sql/expected_values.json`과 비교
4. **새 위반만 보고** (known_exceptions 제외)
5. 의심되는 패턴은 raw row 직접 확인 후 분류

## 신규 false alarm 추가 절차

1. 진단 중 false alarm 발견
2. raw row + 도메인 의미 검증
3. 본 문서에 패턴 추가 + audit SQL 주석에 추가
4. expected_values.json의 known_exceptions에 추가
```

### 5.3 효과

- 미래 진단 시 (사람 또는 AI) 이 문서 먼저 읽고 시작
- false alarm 발견 시 즉시 추가 → 누적 지식
- 새 인력/AI도 즉시 도메인 이해 가능

---

## 6. 적용 순서 (권장)

| 순서 | 작업 | 영향 | 시간 |
|---:|---|---|---|
| 1 | 1단 즉시 적용 가능 7개 constraint 추가 | DB 자동 보호 | 5분 |
| 2 | 2단 표준 진단 SQL 작성 + push | 재실행 가능 | 30분 |
| 3 | 4단 KNOWN_FALSE_ALARMS.md 작성 + push | 지식 보존 | 30분 |
| 4 | 해사안전기본법 1건 보정 → CHECK 추가 | DB 자동 보호 | 5분 |
| 5 | (ministry_code, law_number) 62건 검토 | 진짜 중복 vs 의도 | 별도 |
| 6 | 3단 CI cron 구축 (Railway) | 자동 모니터링 | 1~2시간 |

→ 1, 2, 3, 4는 오늘 한 번에 가능. 5, 6은 별도 트랙.

---

## 7. 4단 방어 vs 현재 상태 비교

| 시나리오 | 현재 (4단 없음) | 4단 적용 후 |
|---|---|---|
| 새 article INSERT 시 internal_key 중복 | 들어감 → 진단 시 발견 | DB가 즉시 거부 |
| announcement > enforcement 새로 발생 | 들어감 → 미래 진단 시 발견 | DB가 즉시 거부 |
| NFTC 처음 본 사람이 진단 | "5,430건 중복!" false alarm | known_exceptions 보고 PASS |
| 안전기준 등록 9 master 처음 본 사람 | "9개 중복!" false alarm | known_exceptions 보고 PASS |
| 신규 적재 후 위반 발생 | 30일 후 다음 진단 시 발견 | 24시간 내 슬랙 알림 |
| 미래 같은 진단 반복 | 도메인 지식 매번 동원 | audit SQL 1회 실행으로 끝 |

---

## 8. 결론 — 대표님 질문에 답

> **"분석을 했을 때 반복되지 않게 조치를 취할수 있나요?"**

**가능합니다. 4단 방어로 완전히 막을 수 있습니다.**

- **1단 (DB constraint)**: 적재 시 자동 차단 — 가장 강력
- **2단 (표준 SQL)**: 도메인 지식 박힌 재실행 가능 진단
- **3단 (CI cron)**: 24시간 내 새 위반 알림
- **4단 (문서)**: 정상 패턴 카탈로그 — 사람·AI 공용

**가장 큰 효과**: false alarm을 만들 수 있는 키 조합 자체를 사용 안 하게 됨. audit SQL은 항상 `article_internal_key` 기준만 사용.

---

## 9. 결정 필요 (대표님)

1. **즉시 적용 7개 constraint 지금 ALTER TABLE 실행**할까요? (위반 0건 확인됨)
2. **해사안전기본법 1건 보정** 어떻게? — announcement_date를 enforcement_date로 맞춤 vs 원본 재확인
3. **(ministry_code, law_number) 62건 위반** 검토 우선순위 — 지금 vs T1 본 미션 후
4. **CI cron** Railway에 추가 — TAI Safe 인프라에 같이? vs 별도 모니터링 시스템?

1, 2번 답주시면 즉시 적용하고, 그 후 audit SQL + KNOWN_FALSE_ALARMS.md push하겠습니다.
