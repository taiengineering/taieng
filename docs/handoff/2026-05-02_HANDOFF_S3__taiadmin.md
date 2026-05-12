# HANDOFF — 2026-05-02 세션 3 (외부 카탈로그 인프라 완성)

> **작업명**: 정방향 데이터 인프라 — 외부 카탈로그 수집 도구 작성
> **상태**: 통합 마스터 80개 추출 + collect_catalog.py 작성 + law_external_catalog 테이블 생성 완료
> **다음 세션 시작점**: § 7. 외부 카탈로그 수집 실행 (사용자 로컬)

---

## 0. 5/2 세션 통합 흐름 (S1 + S2 + S3)

```
S1: α 검증 시도 → 표면 일치 한계 발견
   ↓
S2: 원인 추적 → 4가지 매핑 오류 패턴 + 다중 누락 발견
   - 사용자 통찰: 임의해석 금지·정방향 우선·분할 검토 위험
   - 70개 미수집 + 5개 시스템 인지 0건 발견
   ↓
S3 (현재): 데이터 인프라 정공법
   - 4/22 archive 48개 발견 (학교/의료/복지/선박 의도 제외)
   - 4/23 LAW_COLLECTION_COMPLETE 문서 발견 (collect_v2.py 인프라 완비)
   - 사용자 결정: Q 전부 재수집, 한 번에 처리
   - 통합 마스터 80개 정확 추출
   - 외부 카탈로그 수집 인프라 작성 완료
```

---

## 1. 사용자 ON-RECORD 결정 사항 (5/2)

| 결정 | 사용자 답변 |
|---|---|
| Q1 어린이놀이시설 재수집 | ✅ |
| Q2 의료시설 재수집 | ✅ |
| Q3 학교/노인/사회복지/장애인편의 재수집 | ✅ |
| Q4 방송통신 재수집 (이슈 #1 정정 포함) | ✅ |
| PENDING 어린이제품 7개 | ❌ 제외 (제품 안전 기준 ≠ 사업장 의무) |
| PENDING 화학단편 1개 | ✅ 포함 |
| 위험물 운송·운반 경고표지 기준 | ✅ 포함 (사업장 위험물 운송 적용) |
| 작업 흐름 | **㉡ 외부 카탈로그 먼저 → 한꺼번에** (수집은 deterministic이라 분할 불필요) |
| 핵심 통찰 | **"학교에 공장, 공장에 노인시설"** — 다중 사업장 적용 |
| 중복 처리 | 중복 시 삭제 또는 전체 삭제 후 재수집 |

---

## 2. 결정적 발견 (S3에서 추가)

### 2.1 4/22 의도 제외 48개의 정체
- 커밋 `454202bd — 범위: 48개 제외 (학교/의료/복지/선박 등)`
- 테이블 `law_master_archive_20260422`
- 사용자 기억하시는 "초기 서비스하지 않는 분야 예외"의 정확한 근원
- 즉 SaaS 확장에 따라 **35개는 다시 필요** (선박/항공/철도/특정기관 13개만 진짜 SaaS 밖)

### 2.2 4/23 ATOMIC SWITCH 인프라 완비
- `scripts/collect_v2.py` — 메인 수집 스크립트 (조문 UUID 영구 유지)
- `routers/law_collector.py` — 법령 API (target=law)
- `routers/law_collector_admrul.py` — 행정규칙 API (target=admrul, LID 파라미터)
- 하이브리드 TX: 원본 XML 무조건 보존
- **즉 수집 인프라는 새로 작성 불필요. 타겟만 등록하면 됨.**

### 2.3 이슈 #1 자동 해결 확인
- archive에 "방송통신설비..." (api_id 010668) 중복 저장 흔적
- 현재 law_master에는 "전기설비기술기준" (api_id 31581) **정상 등록**
- 4/23 Atomic Switch 후 자동 정정됨 ✅

### 2.4 운영 위험 — 13개 검증 불가 룰
archive로 격리된 법령에 운영 룰 13개 존재:
```
공공보건의료법, 노인복지법군(4), 사회복지사업법군(4),
어린이놀이시설법, 의료법군(3), 학교안전사고법군(2)
```
→ 다중 사업장 시나리오를 인식하여 룰을 만들었으나 출처 원문 없음.
→ 재수집 후 출처 검증 정합화 필요 (별도 작업).

---

## 3. 통합 마스터 수집 리스트 — 정확히 80개

### 출처 분포
| 출처 | 건수 | api_id 보유 |
|---|---|---|
| A ∩ B (archive ∩ 미수집) | 19 | ✅ 모두 보유 |
| A only (archive 단독) | 7 | ✅ 모두 보유 |
| C only (시스템 인지 0건) | 12 | ❌ 미보유 — 검색 필요 |
| B only (미수집 단독) | 42 | ❌ 미보유 — 검색 필요 |
| **합계** | **80** | 26개 즉시 가능 / 54개 검색 필요 |

### 추가 제외 후보 (사용자 결정 5/2)
**제외 (4개)** — 명확히 SaaS 범위 밖:
- 어선원 안전ㆍ보건 및 재해예방 기준 (선박)
- 이동용 음식판매 화물자동차 LPG 특례기준 (차량)
- 캠핑용자동차 LPG 안전기준 (차량)
- 위험물검사원 선임인가 등에 관한 기준 (인적 자격)

**포함 (1개)** — 사업장에 위험물 운송 발생 가능:
- ✅ **위험물 운송·운반 시의 위험성 경고표지에 관한 기준** (사용자 5/2 결정)

→ 4개 제외 시 **76개**가 최종 후보

### 80개 출처 시각화
```
A_archive_재수집 + B_미수집70 (19개):
  공공보건의료에 관한 법률, 노인복지법군(3), 사회복지사업법군(3),
  의료법군(3), 의료기기법, 학교안전사고법군(3), 어린이놀이시설법군(3),
  장애인ㆍ노인ㆍ임산부 편의증진법, 방송통신설비 기술기준 규정

A_archive_재수집 only (7개):
  공중보건위기 운영세칙, 공중보건위기 안전사용 규정,
  보건복지부 중앙사고수습본부 규정, 종합병원 내진설계 기준,
  학교시설 내진설계 기준, 방송통신설비 표준시험방법,
  유해화학물질 예외적 사용 수산부산물 재활용 환경오염방지 기준

C_시스템인지0건 (12개):
  석면안전관리법군(3), 공동주택관리법군(3),
  건축물의 분양에 관한 법률군(3), 국토의 계획 및 이용에 관한 법률군(3)

B_미수집70 only (42개):
  건설업 산업안전보건관리비 계상 및 사용기준 (영향 174회 참조)
  작업환경측정 및 정도관리 등에 관한 고시 (137회)
  건설공사 안전보건대장 고시 (39회)
  화학물질 분류·표시 및 MSDS 기준 (33회)
  소방시설공사업법, 안전보건교육규정, 하수도법, 위험물안전관리 세부기준,
  소방기본법, 수도법, 한국전기설비규정(KEC), 환경기술 및 환경산업 지원법,
  주차장법, 건축물관리법군, 화학물질 노출기준,
  산업집적활성화 및 공장설립법군, 액화석유가스/고압가스/도시가스 통합고시,
  건설기계관리법군, 건설기계 안전기준 시행세칙, 건설기술진흥법 시행규칙,
  건축물 에너지 4개, 방호장치 자율안전기준, 기계식주차장 안전기준,
  승강기안전부품 안전기준, 전기설비기술기준 운영요령, 화학물질확인 제외기준,
  유해화학물질별 구체적 취급기준, 고압가스/LPG ISO 탱크 컨테이너 기준,
  위험물 운송·운반 시의 위험성 경고표지에 관한 기준 (사용자 5/2 결정 포함)
```

---

## 4. 외부 카탈로그 수집 인프라 (S3에서 작성 완료)

### 4.1 신규 테이블: `law_external_catalog`

```sql
-- 마이그레이션 완료 (5/2 세션 3에서 적용됨)
CREATE TABLE law_external_catalog (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  law_name TEXT NOT NULL,
  law_name_short TEXT,
  law_api_id TEXT,
  law_mst_no TEXT,
  law_type_name TEXT,
  law_type_code TEXT,
  ministry_code TEXT,
  ministry_name TEXT,
  law_number TEXT,
  announcement_date DATE,
  enforcement_date DATE,
  revision_type TEXT,
  api_target TEXT NOT NULL,        -- 'law' or 'admrul'
  search_keyword TEXT NOT NULL,    -- 어떤 키워드로 발견됐는지
  search_page INT,
  collected_at TIMESTAMPTZ DEFAULT NOW(),
  is_in_law_master BOOLEAN DEFAULT NULL,
  is_in_collection_target BOOLEAN DEFAULT NULL,
  is_in_archive BOOLEAN DEFAULT NULL,
  is_in_unified_80 BOOLEAN DEFAULT NULL,
  saas_relevance TEXT,             -- 'CORE'/'EXTENDED'/'OUT_OF_SCOPE'/'PENDING'
  UNIQUE (law_api_id, law_mst_no, api_target)
);
-- + 5개 인덱스
```

### 4.2 신규 스크립트: `scripts/collect_catalog.py`
- **위치**: `taiengineering/tai-api/scripts/collect_catalog.py` (5/2 push 완료)
- **키워드 카테고리**:
  - `KEYWORDS_LAW` (44개): 건축/건축물/다중이용/시설물안전/주차장/승강기/공동주택/분양/도시계획/국토계획/수도법/하수도/산업안전/산재/공장/공장설립/화학물질/위험물/중대재해/건설산업/건설기술/건설기계/건설공사/대기환경/물환경/폐기물/소음/진동/악취/토양환경/환경기술/고압가스/액화석유/도시가스/전기사업/전기안전/전기설비기술/전기공사/소방시설/화재예방/위험물안전/재난/근로기준/산업재해보상/에너지이용/탄소중립/의료법/의료기기/공공보건의료/노인복지/사회복지/장애인/학교안전/어린이놀이/방송통신설비/정보통신공사/석면
  - `KEYWORDS_ADMRUL` (32개): 안전기준/검사기준/시험기준/방호장치/자율안전/안전보건교육/작업환경측정/안전보건관리비/안전보건대장/물질안전보건자료/노출기준/가스안전관리기준/안전관리기준통합고시/NFPC/NFTC/화재안전성능기준/화재안전기술기준/전기설비기술기준/한국전기설비/승강기안전부품/내진설계/에너지효율/에너지절약/위험물안전관리세부기준/위험물안전관리/기계식주차장/유해화학물질/화학물질확인/어린이놀이시설안전/학교시설/종합병원/공중보건위기/방송통신설비기술기준

**명령어**:
```bash
python3 scripts/collect_catalog.py collect    # 카탈로그 수집 (1회 약 30~60분)
python3 scripts/collect_catalog.py classify   # 분류 SQL 출력 (Supabase에서 실행)
python3 scripts/collect_catalog.py status     # 진행 통계
python3 scripts/collect_catalog.py missing    # 진짜 누락 법령 추출
```

---

## 5. 🔴 다음 세션 — 즉시 실행 워크플로우

### Step A — collect_catalog.py 푸시 ✅ 완료
> 5/2 세션 3 마무리에서 `taiengineering/tai-api/scripts/collect_catalog.py` 로 push됨.

### Step B — 사용자 로컬에서 카탈로그 수집 실행
```bash
cd ~/dev/tai-api
git pull origin main
set -a; source .env; set +a

python3 scripts/collect_catalog.py collect
# 예상 시간: 30~60분 (76개 키워드 × 평균 5페이지)
# 결과: law_external_catalog 테이블에 distinct 법령 적재
```

### Step C — 분류 (Claude가 Supabase MCP로 직접 실행)
> Python supabase-py는 raw SQL UPDATE를 지원하지 않으므로 MCP 사용

```sql
-- 1. law_master 보유 여부
UPDATE law_external_catalog ec
SET is_in_law_master = (
  EXISTS(SELECT 1 FROM law_master lm 
         WHERE lm.law_name = ec.law_name OR lm.law_api_id = ec.law_api_id)
);

-- 2. law_collection_target 등록 여부
UPDATE law_external_catalog ec
SET is_in_collection_target = (
  EXISTS(SELECT 1 FROM law_collection_target lct
         WHERE lct.law_name = ec.law_name OR lct.law_api_id = ec.law_api_id)
);

-- 3. archive 보관 여부
UPDATE law_external_catalog ec
SET is_in_archive = (
  EXISTS(SELECT 1 FROM law_master_archive_20260422 lma
         WHERE lma.law_name = ec.law_name OR lma.law_api_id = ec.law_api_id)
);

-- 4. SaaS 관련성 분류 (CORE/EXTENDED/OUT_OF_SCOPE/PENDING)
-- (collect_catalog.py classify 명령어가 이 SQL 출력)
```

### Step D — 누락 법령 추출 + 사용자 검토
```bash
python3 scripts/collect_catalog.py missing
# 출력: CORE/EXTENDED 중 보유/타겟에 없는 법령 리스트
```

사용자가 검토 후:
- ✅ 추가 수집 결정 → 통합 마스터 리스트에 추가
- ❌ 제외 결정 → saas_relevance = 'OUT_OF_SCOPE' 업데이트

### Step E — 통합 = 80 + 외부 발견 → law_collection_target INSERT
```sql
-- archive 26개는 api_id 보유 → 직접 INSERT
INSERT INTO law_collection_target (
  law_name, law_api_id, law_api_mst_no, law_type_code, 
  domain_code, ministry_name, collection_status,
  collection_method, source_system, is_active, added_in_phase,
  collection_priority
)
SELECT 
  law_name, law_api_id, law_mst_no, law_type_code,
  CASE 
    WHEN law_name LIKE '%의료%' OR law_name LIKE '%병원%' THEN 'WELFARE'
    WHEN law_name LIKE '%노인%' OR law_name LIKE '%사회복지%' THEN 'WELFARE'
    WHEN law_name LIKE '%학교%' OR law_name LIKE '%어린이%' THEN 'WELFARE'
    WHEN law_name LIKE '%방송통신%' THEN 'COMMUNICATION'
    ELSE 'BUILDING'
  END AS domain_code,
  ministry_name, 'PENDING', 'API', 
  CASE WHEN law_type_code IN ('STANDARD','NOTICE') THEN 'law.go.kr/admrul' ELSE 'law.go.kr' END,
  TRUE, 'PHASE_3', 500
FROM law_master_archive_20260422
WHERE law_name IN (...26개...);
```

### Step F — 본 수집 실행
```bash
python3 scripts/collect_v2.py monitor   # PENDING 확인
python3 scripts/collect_v2.py all       # 전체 수집 (예상 30분~1시간)
```

### Step G — 운영 13개 검증 불가 룰 정합화
- 재수집 후 archive 13개 법령 룰들이 출처 검증 가능해짐
- 출처 정합 룰만 유지, 잘못된 룰 archive로 이동

---

## 6. 결정 보류 (다음 세션 시작 시 결정)

### 6.1 신규 도메인 추가 여부
현재 11개 도메인: BUILDING/CONSTRUCTION/INDUSTRIAL_SAFETY/FIRE/GAS/ELECTRIC/CHEMICAL/ENERGY/ENVIRONMENT/DISASTER/LABOR

추가 후보:
- **WELFARE**: 의료/노인/사회복지/장애인/학교/어린이 (사용자 통찰 부속시설)
- **COMMUNICATION**: 방송통신설비

또는 BUILDING에 통합? 사용자 결정 필요.

### 6.2 사업장 다중 타입 모델링 (별도 작업, 운영 단계)
사용자 통찰 "학교에 공장, 공장에 노인시설"은 운영 시:
- `master_building_legal_rules`의 `building_use_type_code`, `business_type_code`를 단일이 아닌 **배열/매트릭스**로 변경?
- 또는 별도 매핑 테이블 (사업장 ↔ 부속시설 ↔ 적용 법령)?

→ 수집 완료 후 별도 설계 작업.

---

## 7. 미해결 과제 (Phase 3+ 작업)

| 과제 | 상태 |
|---|---|
| 별표/서식 수집 | 4/23 시점부터 미해결 (admrul_attachment 등 별도 API 필요) |
| NFTC/NFPC 세부 파싱 | "1.1.1.1" 단위까지 paragraph/item 분리 |
| 자동 업데이트 재가동 | Railway cron `/check-updates-v2` |
| 운영 13개 검증 불가 룰 정합화 | 재수집 후 진행 |
| 매핑 오류 4개 패턴 정정 | AI_GENERATED 714건의 49% (S2 발견) |
| α 검증 작업 (S1) | 패러다임 전환으로 폐기 (정방향 우선) |

---

## 8. 환경 정보

| 항목 | 값 |
|---|---|
| Supabase Project | 서울 `vwlahtguyggrhvslabax` |
| Repo (admin) | `taiengineering/tai-admin` (docs/) |
| Repo (api) | `taiengineering/tai-api` (scripts/, routers/, docs/) |
| 사용자 환경 | Mac, 데스크탑 버전 |
| 4/23 핵심 문서 | `tai-api/docs/LAW_COLLECTION_COMPLETE_2026-04-23.md` |
| 5/2 핸드오프 | `tai-admin/docs/HANDOFF_20260502_S1.md` (S1) + `S2.md` (S2) + `S3.md` (이 문서) |
| Python 환경 | `cd ~/dev/tai-api; set -a; source .env; set +a` |

---

## 9. 다음 세션 첫 메시지 (예시)

> "tai-admin/docs의 HANDOFF_20260502_S3.md 학습. 외부 카탈로그 수집 시작."

또는 단계별:

> "Step B 로컬 실행: collect_catalog.py collect 결과 확인"
> 
> [Claude가 Step C SQL 실행 → Step D missing 추출]

---

## 10. 핵심 원칙 재확인

```
1. 임의해석 금지 — 컷오프/규칙은 모두 사용자 결정 또는 결정론적
2. 분할 검토는 AI 몰입 위험 — 큰 그림 유지
3. 데이터 인프라 먼저, 추출은 그 위에서
4. 적용 룰 1건 = 수백 업체 영향 — 신중
5. 신뢰 추락 방지 — 잘못 매핑 시 모든 사용업체가 안 해도 될 의무 수행
6. "건물/산업/건설 + 다중 부속시설" — 사용자 SaaS 통찰
7. 정방향 100% 패스 후 역방향 검증 — 그러나 정방향 자체에도 누락 (현 작업 목적)
```

---

**작성**: 2026-05-02 19:50 KST
**다음 세션 진입점**: § 5 Step B (로컬 collect 실행)
**산출물**: 
- `taiengineering/tai-api/scripts/collect_catalog.py` (Python 스크립트)
- `taiengineering/tai-admin/docs/HANDOFF_20260502_S{1,2,3}.md` (이 문서)
- DB: `law_external_catalog` 테이블 생성 완료
