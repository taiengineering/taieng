# law_rule_drafts 무결성 진단 (S13)

**작성일**: 2026-05-04
**대상**: `public.law_rule_drafts` (가장 중요한 원천 테이블)
**총 데이터**: 3,158 row / 139 법령 / 713 조항
**진단 시각**: KEC 575건 INSERT 직후 (S12 완료 시점)

---

## 0. 전체 분포

| 차원 | 값 |
|---|---|
| 총 row | 3,158 |
| 고유 법령(law_name) | 139 |
| 고유 조항(article_id) | 713 (단, article_id NULL 1,352건 별도) |
| status=APPROVED | 1,989 (63%) — 운영 적재 후보 |
| status=PENDING | 1,112 (35%) — 검수 대기 |
| status=NEEDS_REVIEW | 11 (0.3%) |
| status=REJECTED | 46 (1.5%) |
| status enum 외 | 0 ✅ |

---

## 1. 진단 통과 (이슈 없음)

| 항목 | 결과 |
|---|---|
| law_name / law_article / article_text / obligation_summary NULL | 0 ✅ |
| status / diagnosis_stage / created_at / ai_confidence / ai_reasoning NULL | 0 ✅ |
| article_id **orphan** (있는데 law_article 매칭 안 됨) | 0 ✅ |
| status enum 외 / diagnosis_stage 1-3 범위 외 / ai_confidence 0-100 외 | 0 ✅ |
| created_at > updated_at | 0 ✅ |
| obligation_summary = penalty_summary (잘못 매핑) | 0 ✅ |
| obligation_summary 따옴표 깨짐 / law_article 줄바꿈 | 0 ✅ |
| **KEC** ai_flags 객체 일관성 (verified/source_api/kec_master_id/page_no/v2_path) | 575/575 (100%) ✅ |
| **KEC** PENDING ↔ verified=true 일관성 / NEEDS_REVIEW ↔ verified=false 일관성 | 100% ✅ |

---

## 2. 유형별 이슈 (우선순위순)

### P1 — 운영 정합성 위협 (즉시 수정)

| # | 항목 | 건수 | 조치 방향 |
|---|---|---:|---|
| 1 | `registered_rule_id` 있는데 status ≠ APPROVED | **8** | 운영 적재됐는데 drafts status 잘못. 8건 row 직접 확인 후 status 보정 |
| 2 | APPROVED인데 `registered_rule_id` NULL | **1** | 운영 적재 누락 1건 — 등록 시도 또는 status 환원 |
| 3 | `law_changed_at` > `created_at` (시간 논리 오류) | **6** | 개정일이 생성일보다 미래. 데이터 입력 오류 |

### P2 — 정규화 표기 불일치 (일괄 변환)

#### 2-1. `condition_operator` 표기 분기 (같은 의미 다른 표기)

| 표기 | 건수 | 의미 |
|---|---:|---|
| `gte` | 784 | 이상 |
| `>=` | 25 | 동일 (표기만 다름) |
| `eq` | 495 | 같음 |
| `==` | 53 | 동일 (표기만 다름) |
| `gt` | 18 | 초과 |
| `>` | 3 | 동일 |
| `lt` | 5 | 미만 |
| `<` | 6 | 동일 |
| **`AND`** | **5** | ⚠️ **연산자가 아니라 논리결합자** (컬럼 잘못 사용) |

→ **약 87건 표기 통일 필요** (`>=`→`gte`, `==`→`eq`, `>`→`gt`, `<`→`lt`)
→ **`AND` 5건은 별도 처리** (다중 조건이면 condition_value에 JSON, 또는 룰 분리)

#### 2-2. `ai_flags` 컨벤션 3분기

| 타입 | 건수 | 정체 |
|---|---:|---|
| `object` | 575 | KEC PoC v2.10 결과 (`{verified, page_no, kec_master_id, ...}`) |
| `array` | 2,276 | 기존 데이터 — **검수 메모/주의사항 누적** (예: `["별표8 규제기준 확인 필요", "지역 구분 기준 충족 여부 판단 필요"]`) |
| `null` | 307 | NFTC 등 원본 입력 데이터 |

→ 둘 다 의미는 있으나 **컬럼 분리 권장**: `ai_flags`(object 메타) + `review_notes`(array 메모)
→ 또는 모두 object로 통일하고 array는 `{notes: [...]}` 키로 흡수

### P3 — 메타 누락 (운영 적재 전 채워야 함)

| # | 항목 | 건수 | 비율 |
|---|---|---:|---|
| 1 | **`article_id` NULL** | **1,352** | 43% — 원본 조항 추적 불가 |
| 2 | APPROVED인데 `condition_code` NULL | 1,017 | APPROVED 중 51% — 조건 없는 룰 (의도 검증 필요) |
| 3 | `reviewed_at` 있는데 `reviewed_by` NULL | 1,413 | 검수자 정보 누락 (자동 검수? 사람 누구?) |

#### 3-1. article_id NULL 1,352건 영향 법령 TOP 10

| 법령 | NULL건수 | 비율 |
|---|---:|---:|
| 산업안전보건기준에 관한 규칙 | 200 | 91% |
| 소방시설 설치 및 관리에 관한 법률 시행규칙 | 79 | 100% |
| 액화석유가스의 안전관리 및 사업법 | 74 | 100% |
| 화학물질관리법 | 67 | 100% |
| 건설업 산업안전보건관리비 계상 및 사용기준 | 64 | 100% |
| 승강기 안전관리법 | 61 | 95% |
| 화재의 예방 및 안전관리에 관한 법률 시행규칙 | 57 | 100% |
| 전기설비기술기준 | 57 | 100% |
| 고압가스 안전관리법 시행규칙 | 55 | 92% |
| 위험물안전관리법 | 55 | 57% |

→ 100% 누락 법령은 **law_article 테이블 자체에 해당 법령 article이 없을 가능성**. 추가 master/version/article 적재 필요

### P4 — 식별자 vs 그룹 키 컨벤션 혼동

| # | 항목 | 그룹수 | 영향 row | 의미 |
|---|---|---:|---:|---|
| 1 | `draft_rule_id` 중복 | 358 | 1,089 | 그룹 키 (예: `FIREACT-025-COMMON` 18 row) |
| 2 | `registered_rule_id` 중복 | 164 | 529 | 그룹 키 (예: `FIREACT-025-COMMON-V2` 17 row) |

→ **이름이 `_id`로 끝나서 식별자처럼 보이지만 실제는 그룹 키**. 진짜 PK는 `id` (uuid)
→ 컬럼 의미 명문화 필요. 또는 컬럼명 변경 (`rule_group_code`, `registered_group_code`)
→ 외부 시스템에서 이 ID로 룰을 호출하면 충돌 위험

### P5 — 실제 중복 정리

| # | 항목 | 그룹수 | 영향 row | 비고 |
|---|---|---:|---:|---|
| 1 | **모든 컬럼 일치 완전중복** (law+article+summary+condition+operator+value) | 18 | 40 | 진짜 중복. 가장 오래된 것 1건만 남기고 삭제 |
| 2 | (law, article, summary) 일치 (조건은 다를 수 있음) | 28 | 61 | 조건 다르면 정상. 일일이 검토 |
| 3 | (law, article) 일치 | 600 | 1,938 | 한 조항에서 여러 의무 파생 (정상 패턴 다수) |

### P6 — 사소한 정리

| # | 항목 | 건수 | 조치 |
|---|---|---:|---|
| 1 | `law_article` 양끝 공백/특수문자 | 21 | TRIM 일괄 |
| 2 | `obligation_summary` < 10자 | 2 | 거의 빈 룰 — 직접 확인 |
| 3 | `obligation_type` = `INSTALL` 단 1건 | 1 | 다른 5종(ACTION 1140, NOTIFY 569, REPORT 429, INSPECT 275, APPOINT 169)에 비해 비정상. 입력 실수 의심 |
| 4 | KEC `verification_note` 100자 초과 | 30 | v2.10 maxLength 제약 위반 (PoC 결과) |
| 5 | `appointment_target` 자유 텍스트 종류 | 57 | 정규화 안 된 자유 입력 — 표준 카테고리 매핑 필요 |
| 6 | `change_log_id` 있는 row | 0 | 변경 이력 한 번도 안 적힘 (의도된 것일 수 있음) |
| 7 | `related_doc_id` 있는 row | 427 | 서식 매핑된 룰 (정상) |

---

## 3. 다음 작업 제안 (우선순위 순)

### Phase 1 — 즉시 수정 (P1, 약 15건)
- `registered_rule_id` 있는데 status≠APPROVED인 8건 row 확인 → status 보정
- APPROVED인데 registered NULL인 1건 row 확인 → 등록 또는 환원
- `law_changed_at > created_at` 6건 row 확인 → 시간 보정

### Phase 2 — 표기 통일 (P2-1, 약 87건)
- `condition_operator` 일괄 UPDATE: `>=`→`gte`, `==`→`eq`, `>`→`gt`, `<`→`lt`
- `AND` 5건은 row별 직접 검토 (다중 조건 룰 재설계)

### Phase 3 — 완전중복 제거 (P5-1, 40건)
- 18그룹 중 가장 오래된 row만 남기고 39건 DELETE

### Phase 4 — 사소한 정리 (P6, 약 60건)
- `law_article` TRIM 21건
- KEC verification_note 100자 초과 30건 truncate (또는 그대로 두고 SCHEMA 완화)

### Phase 5 — 메타 보강 (P3 article_id 1,352건)
- 자동 가능: `(law_name, law_article)` → `law_article` 테이블 INNER JOIN으로 매칭 시도
- 매칭 안 되는 건 `law_master`/`law_version`/`law_article` 추가 적재 필요
- → **Python 스크립트 권장** (Supabase에서 데이터 다운로드 → 정규식·텍스트 매칭 → UPDATE)

### Phase 6 — 컨벤션 명문화 (P4)
- `draft_rule_id` / `registered_rule_id` 의미 명문화 또는 컬럼명 변경
- `ai_flags` array vs object 분기 처리 결정

### Phase 7 — 정규화 일관성 (P3-2, 1,017건 + P6-5, 57종)
- APPROVED 중 condition_code NULL 1,017건 검토 (조건 없이 항상 적용 OK인지)
- `appointment_target` 57종 → 표준 카테고리 매핑 (안전관리자 / 보건관리자 / 소방안전관리자 / 전기안전관리자 등)

---

## 4. Python으로 처리할 영역 (효율적)

SQL만으로 어려운 다음 작업은 Python 스크립트가 효율적:

1. **article_id 자동 매칭** — `(law_name, law_article)` 텍스트 정규화 후 `law_article` 테이블 join
   - `제 21 조` vs `제21조`, `제21조의2` 등 표기 통일
   - LIKE/유사도 매칭 후 confidence 기반 자동 UPDATE
2. **`appointment_target` 57종 정규화** — 표준 카테고리 매핑 사전 + 매핑 결과 검토 CSV 생성
3. **`ai_flags` array 통합** — array 안의 텍스트 메모를 카테고리화 (예: "별표 참조 필요", "조건 미명시", "별도 검토" 등)
4. **진짜 완전중복 40건 정리** — 가장 오래된 row 보존 + 나머지 DELETE (SQL로도 가능하지만 dry-run 검증 필요)

→ 모두 `~/dev/tai-poc-kec/`에서 Supabase Python client로 실행 가능

---

## 5. 미결정 사항

대표님 결정 필요:

1. **컨벤션 통일 시점**: 지금 모두 통일 vs Phase별 점진 적용
2. **`AND` 5건 처리**: 다중 조건 룰을 어떻게 모델링? (1) condition_value에 JSON, (2) 룰 분리, (3) 별도 condition_join_logic 컬럼
3. **`ai_flags` 컨벤션**: object 통일 vs `review_notes` 분리
4. **registered_rule_id 충돌 정책**: 그룹 키로 유지 vs PK 강제

---

## 6. 부록 — 진단 SQL 재실행 방법

본 보고서의 모든 수치는 `vwlahtguyggrhvslabax` (서울) Supabase에서 직접 SELECT한 결과.
재현은 `supabase:execute_sql` MCP로 동일 쿼리 실행.

문서 끝.
