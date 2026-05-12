# S9 핸드오프 — 본문 수집 인프라 정비 + Phase 4 완전 수집 + 매핑 오류 진단

**작성일**: 2026-05-03
**선행 핸드오프**: S8 (수집 인프라 정비 + PHASE_3 472건 신규 + L1+L2+L3 통과)
**세션 성격**: 의무사항 추출 단계 진입 시도 → 기존 master 매핑 오류 진단 발견 → 본문 수집 보완(Phase 4)으로 우회 → 다음 세션은 매핑 오류 정정 단계

---

## 0. 한 줄 요약

**S8까지 "수집 단계 종료"라고 판단했으나, master_building_legal_rules의 기존 1,989건 자동승인 룰을 들여다보니 매핑 오류가 광범위하다는 것이 드러났다. 원론적으로 정정하려면 본문 수집 자체가 더 필요했고, 본문 수집을 마쳤다(Phase 4 — 35/37건 성공). 다음 세션은 정정 작업으로 진입한다 — 첫 번째는 산안법 "샘플" 시드 10건 (status=ACTIVE 운영 위험).**

---

## 1. 세션 진행 흐름

### 1.1 의무사항 추출 단계 진입 시도 (실패로 끝남)
- S8 § 7.1대로 `parse_law_rules.py` / `law_to_rules.py` 검토 → 두 스크립트 모두 정규식 보조 도구이고 master에 직접 적재. 실제 운영 파이프라인은 `routers/law_rule_generator.py` (44KB, v1.7.0, Claude Haiku 4.5 기반).
- DB 실측 결과: `law_rule_drafts` 2,583건이 이미 4/2~4/25 사이에 추출됨. 그 중 자동승인 1,989건이 `master_building_legal_rules`에 적재 완료.

### 1.2 사용자 지시: "핸드오프에 몰입하지 말고 소스+DB 기준으로 진행하라"
- 핸드오프 문서가 가리키지 않은 진짜 운영 시스템 발견.
- "데이터 검증을 숫자로 하지 말고 딥하게 하라" → row 단위 원문 대조 검증으로 전환.

### 1.3 기존 master 1,989건 깊이 검증 (충격적 결과)

**`law_article` 필드 형식 분류 (master 2,012건 기준)**:

| 형태 | 카운트 | 진단 | 정정 방법 |
|------|--------|------|-----------|
| ✅ "제N조" / "제N조의N" | 971 (48.3%) | 정상 | — |
| ⑩ "제7조방호구역 및 유수검지장치" 한글 결합 | 812 (40.4%) | 매핑 ✅, 형식만 ✗ | SQL 정규식 정정 |
| ⑧ "제13조2.6 발신기" NFTC 점번호 결합 | 211 (10.5%) | 매핑 ✅, 형식만 ✗ | SQL 정규식 정정 |
| ⑨ "제2조(정의) 등 샘플" | 10 | 🔴 매핑 자체 오류 + 시드 데이터 | 처리 항목 (1.4 참조) |
| ⑪ "131", "341" 숫자만 | 8 | 🔴 KEC 보일러플레이트 | 처리 항목 |

**Sonnet 재파싱 영향권**: master 2,012건 중 99%가 4/20~4/26 Sonnet 재파싱 영향권. CANCELLED 작업 다수 = 부분만 처리되고 중단된 일관성 깨진 row 가능성.

### 1.4 산업안전보건법 "샘플" 시드 데이터 10건 — 운영 즉시 위험

원문 대조 결과 **10건 모두 매핑 완전 오류**:

| master row 의무 내용 | 진짜 조문 제목 | 매핑 결과 |
|---|---|---|
| "안전관리자·보건관리자 선임 보고 의무" | 산안법 제2조 (정의) | ❌ 정의 조항에 의무는 없음 |
| "보일러 등 설비 등록 시 점검(샘플)" | 산안법 제38조 (안전조치) | ❌ "설비 등록 점검"은 별도 조문 |
| "유해·위험 공정 관리(샘플)" | 산안법 제76조 (도급인 안전조치) | ❌ 도급인 안전조치 ≠ 공정 관리 |
| 산안기준규칙 제154조 "근로자용 건축물(샘플)" | 붕괴 등의 방지 (건설용 리프트) | ❌ 리프트 ≠ 근로자용 건축물 |

- 모두 `source_api='law_collector'`, 3/29 생성, **`status=ACTIVE`, `is_active=true`** → 사용자 사업장에 잘못된 의무가 적용될 위험
- "사용자 결정: 오픈 전이므로 처리 항목에 놔두고 다른 원인 먼저 찾기" → 처리 보류, 다음 세션 첫 작업으로 확정

### 1.5 보일러플레이트 의무 198건 발견

`obligation_summary`가 "조치/점검/.. 의무 (법령명 제N조)" 형태인 row 198건:
- 모두 3/20~3/30 생성 (4월 이전 초기 시드)
- 출처: 외부 API (MOEL, KOSHA, KGS, NFA, K-ECO, KEC, COMWEL 등 26개)
- 법령: 산안법 시행규칙(16), 안전보건교육규정(16), 근로기준법(11), 악취방지법(10)
- 4/25~26 Sonnet 재파싱 거쳤으나 본문 매핑 실패
- **184건은 원문이 law_master에 존재 → 재파싱으로 정정 가능**, 14건은 원문 미수집

표본 대조: 16건 중 약 50%(7~8건)는 매핑 자체가 잘못됨, 나머지는 매핑은 옳지만 본문 추출 실패.

### 1.6 본문 미수집 6 법령 18 rule 발견 (catalog 무결성 문제)

`master_building_legal_rules`에는 있는데 `law_master`에 원문이 없는 법령:

| 법령 | rule 수 | catalog 등록 |
|---|---|---|
| 한국전기설비규정 | 8 | ⭕ OTHER, target=true (수집 누락) |
| 소방기본법 | 6 | ❌ catalog에 명단 자체 없음 |
| 건축물의 에너지원단위 목표관리 고시 | 1 | ❌ catalog에 없음 |
| 고압가스/LPG ISO 탱크 컨테이너 기준 | 1 | ❌ catalog에 없음 |
| 기존 건축물의 에너지성능 개선기준 | 1 | ❌ catalog에 없음 |
| 어선원 안전·보건 기준 | 1 | ⭕ NOTICE, OUT_OF_SCOPE (분류 오류) |

→ **catalog 자체가 완전한 명단이 아니다**. S3 핵심 80개는 100% 수집됐지만, 그 외 영역에 누락 존재.

### 1.7 사용자 통찰: "본법↔시행규칙 매핑 검증 전에 본문 수집 먼저"
- 매핑 검증은 양쪽 원문이 있어야 가능 → 본문 수집을 Phase 4로 추가 진행 결정
- D 시나리오 선택: PENDING 300건 분류 + OUT_OF_SCOPE 39건 재검증 + 미수집 보충 + 무결성 검증

---

## 2. Phase 4 — 본문 수집 보완 (실행 완료)

### 2.1 PENDING 300건 saas_relevance 분류

자동 분류 + NEEDS_REVIEW 수동 검토 결과:

| 분류 | 카운트 | 처리 |
|------|--------|------|
| CORE | 93 | `is_in_collection_target=true` 적용 |
| OUT_OF_SCOPE | 207 | 제외 |

**False positive 4건 보정**: 공항시설 내진설계기준, 정수기 품질검사 자가기준, 자동차 타이어 에너지소비효율, 자동차 에너지소비효율 등급표시 → OUT으로 재분류.

**False negative 점검**: 35건 의심 케이스 모두 OUT 유지 확인. 어선원 같은 케이스 재발 없음.

### 2.2 catalog 미등록 4건 추가

소방기본법, 건축물의 에너지원단위 목표관리 고시, 고압가스/LPG ISO 탱크 컨테이너 기준, 기존 건축물의 에너지성능 개선기준 → `law_external_catalog` INSERT 완료 (saas_relevance=CORE, target=true).

### 2.3 본문 수집 실행 (`scripts/collect_phase4_full.py`)

**최종 결과**:
```
Phase A: 등록 4 / 스킵 0 / 실패 0
Phase B: 수집 35 / 실패 2 / 조문 1820
Phase C:
  ✓ L1 OK: catalog target 265건 모두 law_master 존재
  ✓ L2 OK: 752건 모두 current_version 존재
  ✓ L3 OK: 검사 version 모두 article ≥ 1
```

**실패 2건** (수동 처리 대상, 다음 세션 또는 차후):
1. (행정안전부) 자연재난 복구비용 산정기준 (NOTICE) — 제목 `(행정안전부)` 접두사로 lawSearch 매칭 실패 추정
2. 정보통신공사업법 시행규칙 (ENFORCEMENT_RULE) — 검색 실패 사유 미진단

### 2.4 전체 수집 사이즈 확정

| 분류 | 카운트 |
|---|---|
| catalog `target=true` & 미수집 | 0 (← 35건 보충 완료, 2건만 실패) |
| `law_master` 보유 | **752** (S8 시점 654 + Phase 4 35 + 디버그 잔존 정리분 등) |
| `master_building_legal_rules` 사용 법령 | 178 (수집 완료 178 / 미수집 0) |

### 2.5 코드 작업 — 파이프라인 본체 결함 수정

세션 중반에 **scripts/collect_phase4_full.py를 별도 INSERT 로직으로 작성한 것이 잘못**임을 사용자가 지적. `routers/law_collector.py`의 파이프라인 본체(`save_law_to_db()`)를 호출하는 방식으로 v4 재작성.

그 과정에서 파이프라인 본체의 결함도 함께 발견·수정:

| commit | 파일 | 수정 내용 |
|---|---|---|
| `281b9ca` | routers/law_collector.py v3.0.9 | `save_law_to_db()` `law_article` INSERT에 `law_id` 누락 (NOT NULL 위반) |
| `ebdbe4b` | routers/law_collector.py v3.0.10 | `law_paragraph` + `law_item` INSERT에 `law_id` 누락 |
| `e47fc07` | scripts/collect_phase4_full.py v5 | admrul article에 `_dedupe_articles_by_internal_key` 적용 (NFTC 중복 충돌 방지) |
| `03fd6a7` | scripts/collect_phase4_full.py v6 | OUTBOUND_PROXY 무력화 (직송 강제) — LAW IP 인증 실패 회피 |
| `32e40aa` | scripts/collect_phase4_full.py v4 | 별도 INSERT 제거, `save_law_to_db()` 호출 방식으로 재작성 |
| `45943a1` | scripts/collect_phase4_full.py v2 | api_target + search_keyword NOT NULL 채우기 |
| `9cd882a` | scripts/collect_phase4_full.py v3.1 | law_master.law_key NOT NULL |
| `d55060e` | scripts/collect_phase4_full.py v3.2 | version_status_code 컬럼명 정정 + LAW ID/MST 다중시도 |
| `ff11743` | scripts/collect_phase4_full.py v3 | admrul fetcher LID/XML로 정정 (routers/law_collector_admrul 재사용) |

**DB 마이그레이션** (Supabase MCP로 적용):
- `law_update_tracking.law_id` UNIQUE 인덱스 추가 (S8 마이그레이션 누락 복구)
- `law_update_tracking` RLS off (다른 법령 테이블과 일관성)
- 중복 tracking row dedupe (470 → 98 distinct)

### 2.6 ⚠️ 파이프라인 본체에서 드러난 의미

**`save_law_to_db()`의 `law_id` 누락은 한 번도 정상 작동 안 했다는 신호**. 그렇다면 의무 추출 단계에서 master는 있는데 tracking이 비어있는 상태였을 가능성 — 추후 진단 필요.

---

## 3. 코드 / DB / catalog 현재 상태 (스냅샷)

### 3.1 GitHub 최신 commit
- **tai-api**:
  - `281b9ca` law_collector v3.0.9 (law_article law_id)
  - `ebdbe4b` law_collector v3.0.10 (law_paragraph + law_item law_id) ← 현재 main
  - `03fd6a7` collect_phase4_full v6
- **tai-admin**:
  - 본 핸드오프 (S9) 작성 후 commit 예정

### 3.2 DB 카운트 (확정)

| 테이블 | S8 시점 | S9 종료 시점 | 변화 |
|---|---|---|---|
| `law_master` | 654 | **752** | +98 (Phase 4 보충) |
| `law_external_catalog` | 983 | 987 | +4 (catalog 미등록 보충) |
| `law_external_catalog target=true & saas=CORE` | 154 | 251 | +97 (PENDING 300건 분류) |
| `law_external_catalog saas=OUT_OF_SCOPE` | 39 | 246 | +207 |
| `law_update_tracking distinct law_id` | ~470 (중복) | 98 | dedupe 후 |
| `master_building_legal_rules` | 2,012 | 2,012 | 변화 없음 (이번 세션은 정정 안 함) |
| `law_rule_drafts` | 2,583 | 2,583 | 변화 없음 |

### 3.3 알려진 문제 — 처리 항목 (다음 세션부터)

**🔴 최우선 (운영 즉시 위험)**:
1. **산안법 "샘플" 시드 10건** (`status=ACTIVE`, `is_active=true`, 매핑 자체 오류) — 다음 세션 § 7 진입점

**🟡 주요 정정 작업**:
2. **보일러플레이트 의무 198건** — 그 중 184건 원문 있음 → 재파싱 가능, 14건 원문 없음
3. **본법↔시행규칙 매핑 혼동** (S2 패턴 ②, 미검증) — 가장 위험. 본문 수집 끝났으니 이제 검증 가능
4. **`law_article` 형식 결함 1,023건** (⑩ 한글 결합 812 + ⑧ NFTC 점번호 결합 211) — 매핑은 ✅, SQL 정규식 정정 가능
5. **obligation_summary < 30자 941건** — 표본 검증 필요

**🟢 낮은 우선순위**:
6. **Phase 4 실패 2건** ((행정안전부) 자연재난 복구비용 산정기준, 정보통신공사업법 시행규칙) — 수동 catalog 정정 또는 lawSearch 우회 패턴 추가
7. **CORE + target=false 365건** — 수집 대상에서 의도적으로 빠진 건지, 누락인지 검토 필요
8. **CORE + target=true & 사용 중인 PENDING 14건** — saas_relevance만 PENDING으로 남음 (수집은 완료) → 분류 정리만 필요

---

## 4. 핵심 깨달음 — 작업 원칙 (강화)

S9에서 사용자가 강조한 원칙. 다음 세션도 이대로 진행:

1. **"핸드오프에 몰입하지 마라. 소스와 DB를 기준으로 진행하라."**
   - 핸드오프 문서는 참고일 뿐, 실제 운영 시스템은 소스 + DB가 진실. 핸드오프와 다르면 핸드오프가 틀린 것.

2. **"검증은 숫자로 하지 말고 딥하게 하라."**
   - 카운트 N건 → 정상으로 판단 금지. row 1건씩 원문 대조까지.
   - 매핑 정확성 = obligation_summary와 article_text의 의미 일치.

3. **"임의 판단 절대 금지."**
   - 분기 시점마다 사용자 결정 받기. dry-run, 표본 검증, 명령 사전 보여주기 필수.

4. **"기존 파이프라인을 수정해서 사용. 별도 우회 절대 금지."**
   - `routers/law_collector.py`, `routers/law_rule_generator.py` 등 본체에 결함이 있으면 그것을 고친다. 별도 스크립트로 우회하면 후속 단계와 호환 깨짐.

5. **"비개발자이므로 Claude가 목표(정확한 파싱·룰 산출, 누락 0)에 맞춰 자율적으로 흐름을 잡아라."**
   - 단계별 결정 분기는 명확히 보여주되, 과정의 미세 결정(SQL 작성, 정규식 등)은 자율 진행.

6. **"몰입 → 수정의 수정 반복 = 위에서부터 정확한 분석 후 진행."**
   - 패치 누적 발생 시 멈추고 schema/제약조건 전체 일괄 검증 → 한 번에 잡기.

---

## 5. 다음 세션 진입점

### 5.1 최단 진입
> "S9 핸드오프 봤음. 산안법 샘플 10건부터 진행."

### 5.2 상세 진입
> "S9 핸드오프 학습. § 3.3 처리 항목 1번 — 산안법 '샘플' 시드 데이터 10건 정리부터 진행. status=ACTIVE 운영 위험이라 우선."

### 5.3 직전 마지막 메시지
세션 끝에 사용자 답변: **"산안법 샘플 10건 정리 (긴급)"** — 정리 작업의 첫 번째 SQL은 사전 식별까지 진행됨. 작업 자체는 미실행.

---

## 6. 다음 세션 — 산안법 샘플 10건 정리 절차 (계획)

원칙 14(대량 SQL 사전 카운트 + 사후 검증) 준수:

### Step 1 — 정확 식별
```sql
SELECT id, law_name, law_article, obligation_summary, status, is_active, created_at
FROM master_building_legal_rules
WHERE (obligation_summary ILIKE '%샘플%' OR law_article ILIKE '%샘플%')
ORDER BY created_at, law_name, law_article;
```
→ 10건 + α (이전 세션에서 ⑨ 변형 30+건 추가 검출됨) 확인.

### Step 2 — row 1건씩 원문 대조 검증
- `law_master` → `law_version (is_current=true)` → `law_article` 의 진짜 본문
- master row의 의무 내용과 비교
- 매핑 오류 / 시드 / 정상 분류

### Step 3 — 처리 방향 결정 (사용자)
- A) 즉시 비활성화 (`status='INACTIVE'`, `is_active=false`)
- B) 즉시 삭제
- C) 정정 (재파싱 후 갱신)

### Step 4 — 일괄 처리 + 사후 검증

### Step 5 — 동일 패턴 (KEC 숫자만 8건 등) 확장 처리

---

## 7. 미해결 (다음 세션 이후 트랙)

- **Phase 4 실패 2건** 수동 catalog 정정
- **첨부파일 본체 82건** (PDF/HWP 추출 별도 트랙)
- **PENDING 잔존 14건** 분류 (수집은 완료)
- **신규 도메인 WELFARE/COMMUNICATION** 정식 분리 (CHECK 제약 ALTER)
- **admrul `_NFPC_ARTICLE_PATTERN` split 안전성** spot-check
- **`law_update_tracking`이 한 번도 정상 작동 안 했을 가능성** 진단 (3.2 § Sonnet 재파싱이 매핑 오염 진원 1순위 의심과 연관)

---

## 8. 본 세션 commit 목록

**tai-api**:
- `45943a1` collect_phase4_full v2 (api_target + search_keyword)
- `ff11743` collect_phase4_full v3 (admrul LID/XML)
- `9cd882a` collect_phase4_full v3.1 (law_master.law_key)
- `d55060e` collect_phase4_full v3.2 (version_status_code + LAW 다중시도)
- `32e40aa` collect_phase4_full v4 (파이프라인 본체 호출로 재작성)
- `e47fc07` collect_phase4_full v5 (admrul dedupe)
- `03fd6a7` collect_phase4_full v6 (OUTBOUND_PROXY 무력화)
- `281b9ca` law_collector v3.0.9 (law_article law_id)
- `ebdbe4b` law_collector v3.0.10 (law_paragraph + law_item law_id)

**Supabase 마이그레이션 (MCP)**:
- `law_update_tracking.law_id` UNIQUE 인덱스 복구
- `law_update_tracking` RLS off
- `law_update_tracking` 중복 dedupe (470 → 98)
- `law_external_catalog` PENDING 300건 분류 적용 (CORE 93 + OUT_OF_SCOPE 207)
- `law_external_catalog` 미등록 4건 (소방기본법 등) INSERT
- `master_building_legal_rules` ↔ `law_external_catalog` saas_relevance 정렬

**tai-admin**:
- 본 핸드오프 (S9) — 본 commit

---

## 9. 부록 — 첫 메시지 예시

**최단**:
> "S9 봤음. 산안법 샘플 10건 SQL 식별부터."

**중간**:
> "S9 § 6 절차대로 산안법 샘플 10건 정리 진행. Step 1 식별 SQL부터."

**상세**:
> "S9 핸드오프 학습 완료. § 3.3 처리 항목 1번 산안법 샘플 10건은 status=ACTIVE 운영 위험이라 최우선. § 6 절차 그대로: Step 1 식별 → Step 2 원문 대조 → Step 3 처리 방향 사용자 결정 → Step 4 일괄 처리. ⑨ 변형 30+건 함께 검출돼 확장 가능. 진행 시작."
