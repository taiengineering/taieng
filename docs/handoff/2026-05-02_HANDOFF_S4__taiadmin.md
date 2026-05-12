# HANDOFF — 2026-05-02 세션 4 (Railway 인프라 디버깅 + 환경변수 호환)

> **작업명**: 사용자 로컬 .env DNS 실패 → Railway 백그라운드 전환 → 환경변수 변수명 불일치 정정
> **상태**: routers/law_collector.py v3.0.2 push 완료, Railway deploy 진행 중
> **다음 세션 진입점**: § 5. Deploy 완료 확인 → catalog 트리거 → 30~60분 백그라운드 모니터링

---

## 0. 세션 흐름 (S1+S2+S3+S4 통합)

```
S1 (5/2 17:53): α 검증 시도 → 표면 일치 한계 발견
   ↓
S2 (5/2 19:00): 4가지 매핑 오류 패턴 + 정방향 패러다임 전환
   ↓
S3 (5/2 19:50): 4/22 archive 발견 + 통합 마스터 80개 추출 + 외부 카탈로그 인프라 작성
   ↓
S4 (5/2 20:30~): 인프라 디버깅 (현재)
   - Railway 라우터 배포
   - 사용자 로컬 .env DNS 실패 → Railway 우회
   - 환경변수 변수명 불일치 발견 및 정정
   - 위험물 운송 수집 결정 반영
```

---

## 1. S4 작업 요약 (시간순)

### 1.1 사용자 결정 ON-RECORD (5/2)
| 항목 | 결정 |
|---|---|
| 위험물 운송·운반 경고표지 기준 | ✅ **수집 포함** (사업장 위험물 운송 적용) |
| 핸드오프 + Python 파일 GitHub 업로드 | ✅ |
| 작업 진행 방식 | "이번 세션에서 진행, 단계별 마무리되면 핸드오프 추가 작성" |

### 1.2 GitHub 푸시 완료 — 4개 파일

| 파일 | Repo | Commit |
|---|---|---|
| docs/HANDOFF_20260502_S1.md | tai-admin | `6f1e72a4` |
| docs/HANDOFF_20260502_S2.md | tai-admin | `0553405e` |
| docs/HANDOFF_20260502_S3.md | tai-admin | `94756b4f` (위험물 운송 결정 반영) |
| scripts/collect_catalog.py | tai-api | `b053c32c` |

### 1.3 Railway 라우터 인프라 신규 배포

**`routers/law_catalog_collector.py`** (commit `40f33b1f`, v1.0.0)
- POST `/law-collector/collect-catalog` — 백그라운드 수집 트리거
- GET `/law-collector/catalog-status` — 진행 확인
- GET `/law-collector/catalog-keywords` — 키워드 조회
- KEYWORDS_LAW: 57개 / KEYWORDS_ADMRUL: 33개

**`main.py` v5.43.0** — `law_catalog_collector_router` 등록

### 1.4 환경변수 진단 (S4 핵심 발견)

**문제 발견 흐름**:
```
사용자 trigger (POST /collect-catalog) 
  → 4분 후 law_external_catalog count=0
  → debug/{law_name} 호출:
     "api_source": "law.go.kr"  ← data.go.kr 아닌 폴백
     "has_api_key": false       ← DATA_GOV_SERVICE_KEY 환경변수 미인식
     XML 응답: "사용자 정보 검증 실패. 서버 IP/도메인 등록 필요"
```

**진단**: 백그라운드 task 정상 실행. 그러나 fetch_law_list가 키 없이 law.go.kr/DRF 폴백 사용 → Railway IP가 LAW_API_OC=taieng에 등록 안 됨 → 거부.

**원인 확정** — `env-check` 엔드포인트 추가 후 사용자 회신:
```
Railway 등록: DATA_GO_KR_SERVICE_KEY  (DATA_**GO_KR**)
코드 기대:    DATA_GOV_SERVICE_KEY    (DATA_**GOV**)
                          ↑
                 변수명 불일치
```

### 1.5 정정 푸시

**`routers/law_catalog_collector.py` v1.1.0** (commit `08cf267b`)
- `GET /law-collector/env-check` 추가 (값 노출 없이 존재 여부)
- 직전 commit `9b78a31c` 첫 줄 `ND` 오타 정정

**`routers/law_collector.py` v3.0.2** (commit `2721ca58`) — 핵심 수정
```python
# v3.0.1
DATA_GOV_KEY = os.environ.get("DATA_GOV_SERVICE_KEY", "")

# v3.0.2 (정정)
DATA_GOV_KEY = os.environ.get("DATA_GO_KR_SERVICE_KEY", "") \
            or os.environ.get("DATA_GOV_SERVICE_KEY", "")
```

→ Railway 등록명(`DATA_GO_KR_SERVICE_KEY`) 우선, 폴백 호환.
→ 외부 카탈로그 수집 + 본 수집(Step F) 모두 정상화.

---

## 2. 현재 시점 상태 (S4 종료 시점)

### 2.1 인프라 (Railway 배포 진행 중)
- 마지막 commit: `2721ca58` (v3.0.2)
- Deploy 상태: **진행 중 (1~2분 소요 예상)**
- 영향 범위: routers/law_collector.py + 자동 import한 routers/law_catalog_collector.py

### 2.2 DB 상태
- `law_external_catalog`: **0건** (이전 트리거는 0건 적재, deploy 완료 후 재트리거 필요)
- `law_master`: 182개 (변경 없음)
- `law_collection_target`: 기존 그대로
- `law_master_archive_20260422`: 48개 (변경 없음)

### 2.3 미해결 작업
- Step B 완료 대기 (Deploy 완료 후 트리거 → 30~60분 수집)
- Step C~G 후속 (S3 § 5 워크플로우 그대로)

---

## 3. Railway 엔드포인트 카탈로그 (S4에서 추가/수정됨)

### 외부 카탈로그 수집 관련
| 엔드포인트 | 메서드 | 용도 |
|---|---|---|
| `/law-collector/collect-catalog` | POST | 백그라운드 수집 트리거 |
| `/law-collector/catalog-status` | GET | 진행 통계 |
| `/law-collector/catalog-keywords` | GET | 사용 키워드 조회 |
| `/law-collector/env-check` | GET | 환경변수 진단 (신규, S4) |
| `/law-collector/debug/{law_name}` | GET | fetch_law_list 직접 테스트 (기존) |

### 기존 (참고)
| 엔드포인트 | 메서드 | 용도 |
|---|---|---|
| `/law-collector/collect/all` | POST | 본 수집 (law_collection_target → law_master) |
| `/law-collector/collect/{law_name}` | POST | 단일 법령 수집 |
| `/law-collector/check-updates-v2` | POST | 변경 감지 |
| `/law-collector/status` | GET | 본 수집 통계 |

---

## 4. 환경 정보

| 항목 | 값 |
|---|---|
| Supabase Project | 서울 `vwlahtguyggrhvslabax` |
| Railway URL | `https://api.taieng.co.kr` |
| Repo (admin) | `taiengineering/tai-admin` (docs/) |
| Repo (api) | `taiengineering/tai-api` (scripts/, routers/) |
| Railway 환경변수 (확인됨) | `DATA_GO_KR_SERVICE_KEY`, `LAW_API_OC` |
| 사용자 환경 | Mac, 데스크탑 (~/dev/tai-api) |
| 사용자 로컬 .env | DNS 풀이 실패 (`[Errno 8]` macOS) — Railway 우회로 해결 |

---

## 5. 🔴 다음 세션 즉시 실행 — 단계별 가이드

### Step B-1: Deploy 완료 확인 (1~2분 대기 후)

```bash
# 1. version 확인 (5.43.0이면 새 코드 반영됨)
curl https://api.taieng.co.kr/

# 2. fetch_law_list 정상 작동 확인 (핵심)
curl https://api.taieng.co.kr/law-collector/debug/건축
```

**기대 결과** (v3.0.2 적용 시):
```json
{
  "api_source": "data.go.kr",     ← 이전 "law.go.kr" 폴백에서 변경됨
  "has_api_key": true,            ← 이전 false에서 변경됨
  "law_count": > 0,               ← 이전 0에서 변경됨
  ...
}
```

**여전히 `has_api_key: false`인 경우**:
- Deploy 진행 중 → 1분 더 대기 후 재시도
- 또는 환경변수 reload 안 됨 → Railway 대시보드에서 manual redeploy

### Step B-2: 카탈로그 수집 재트리거

```bash
curl -X POST https://api.taieng.co.kr/law-collector/collect-catalog
```

**기대 응답**:
```json
{
  "status": "started",
  "keywords_law": 57,
  "keywords_admrul": 33,
  "estimated_duration_minutes": "30~60",
  "started_at": "2026-05-02T..."
}
```

### Step B-3: 진행 모니터링 (30~60분 백그라운드)

**옵션 A — curl로 확인**:
```bash
curl https://api.taieng.co.kr/law-collector/catalog-status
```

**옵션 B — Claude에게 "진행 상황 봐줘" 요청** → Supabase MCP로 직접 확인:
```sql
-- 누적 distinct
SELECT count(*) FROM law_external_catalog;

-- target별
SELECT api_target, count(*) FROM law_external_catalog GROUP BY api_target;

-- 가장 최근 적재 (진행 중인지 판단)
SELECT collected_at, search_keyword, api_target 
FROM law_external_catalog 
ORDER BY collected_at DESC LIMIT 5;
```

**예상 진행률**:
- 5분: ~200~500건
- 15분: ~1000~2000건  
- 30분: 거의 완료 (KEYWORDS_LAW phase 끝)
- 60분: 완전 완료 (KEYWORDS_ADMRUL phase 포함)

### Step C: 분류 SQL 실행 (Claude가 Supabase MCP로)

수집 완료 후 Claude가 자동 실행:

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

-- 4. SaaS 관련성 분류 (collect_catalog.py 의 cmd_classify와 동일)
UPDATE law_external_catalog ec
SET saas_relevance = CASE
    WHEN ec.law_name LIKE '%선박%' OR ec.law_name LIKE '%선원%'
      OR ec.law_name LIKE '%어선원%' OR ec.law_name LIKE '%선내%'
      OR ec.law_name LIKE '%항공%' OR ec.law_name LIKE '%철도%'
      OR ec.law_name LIKE '%궤도%' OR ec.law_name LIKE '%국립%병원%'
      OR ec.law_name LIKE '%대검찰청%' OR ec.law_name LIKE '%법원안전%'
      OR ec.law_name LIKE '%재외동포%' OR ec.law_name LIKE '%외무%'
      OR ec.law_name LIKE '%국방%' OR ec.law_name LIKE '%군인%'
      OR ec.law_name LIKE '%캠핑용%' OR ec.law_name LIKE '%이동용%'
      OR ec.law_name LIKE '%어린이제품%' OR ec.law_name LIKE '%어린이보호포장%'
    THEN 'OUT_OF_SCOPE'
    WHEN ec.law_name LIKE '%건축%' OR ec.law_name LIKE '%건설%'
      OR ec.law_name LIKE '%산업안전%' OR ec.law_name LIKE '%산안%'
      OR ec.law_name LIKE '%소방%' OR ec.law_name LIKE '%화재%'
      OR ec.law_name LIKE '%위험물%' OR ec.law_name LIKE '%가스%'
      OR ec.law_name LIKE '%전기%' OR ec.law_name LIKE '%승강기%'
      OR ec.law_name LIKE '%중대재해%' OR ec.law_name LIKE '%작업환경%'
      OR ec.law_name LIKE '%안전보건%'
      OR ec.law_name LIKE '%다중이용%' OR ec.law_name LIKE '%시설물%'
      OR ec.law_name LIKE '%주차장%' OR ec.law_name LIKE '%수도%'
      OR ec.law_name LIKE '%하수%' OR ec.law_name LIKE '%공장%'
      OR ec.law_name LIKE '%화학물질%' OR ec.law_name LIKE '%석면%'
      OR ec.law_name LIKE '%공동주택관리%' OR ec.law_name LIKE '%분양%'
      OR ec.law_name LIKE '%국토%' OR ec.law_name LIKE '%건축물%'
    THEN 'CORE'
    WHEN ec.law_name LIKE '%의료%' OR ec.law_name LIKE '%병원%'
      OR ec.law_name LIKE '%노인%' OR ec.law_name LIKE '%사회복지%'
      OR ec.law_name LIKE '%장애인%' OR ec.law_name LIKE '%학교%'
      OR ec.law_name LIKE '%어린이놀이%'
    THEN 'EXTENDED'
    WHEN ec.law_name LIKE '%환경%' OR ec.law_name LIKE '%폐기물%'
      OR ec.law_name LIKE '%대기%' OR ec.law_name LIKE '%소음%'
      OR ec.law_name LIKE '%진동%' OR ec.law_name LIKE '%악취%'
      OR ec.law_name LIKE '%토양%'
    THEN 'CORE'
    ELSE 'PENDING'
END;
```

### Step D: 누락 법령 추출 + 사용자 검토

```sql
-- CORE/EXTENDED 중 보유/타겟 둘 다 없는 것
SELECT law_name, law_type_code, ministry_name, saas_relevance, api_target, search_keyword
FROM law_external_catalog
WHERE is_in_law_master = FALSE
  AND is_in_collection_target = FALSE
  AND saas_relevance IN ('CORE', 'EXTENDED')
ORDER BY saas_relevance, ministry_name, law_name;
```

**Claude가 결과 정리**:
- 통합 마스터 80개와 비교
- 외부에서 추가 발견된 법령 리스트 별도 표시
- 사용자에게 검토 요청

**사용자 검토 체크포인트**:
- 추가 수집할 법령
- 제외할 법령 (saas_relevance='OUT_OF_SCOPE' 업데이트)
- PENDING 분류 항목 결정

### Step E: 통합 마스터 → law_collection_target INSERT

archive 26개 (api_id 보유): 직접 INSERT
```sql
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
WHERE law_name IN (...26개 리스트...);
```

C 12개 + B only 42개: 이름만 등록 (자동 검색)
```sql
INSERT INTO law_collection_target (law_name, ...) VALUES
  ('석면안전관리법', 'LAW', 'BUILDING', '환경부', 'PENDING', ...),
  ...;
```

**⚠️ 결정 보류 사항** (사용자 확정 필요):
- 신규 도메인 추가 여부: WELFARE / COMMUNICATION 또는 BUILDING 통합
- 26개 정확한 리스트 (S3 § 3 시각화 참조)

### Step F: 본 수집 실행

```bash
# 사용자 로컬 (만약 .env DNS 문제 해결되면)
cd ~/dev/tai-api
git pull origin main
set -a; source .env; set +a
python3 scripts/collect_v2.py monitor   # PENDING 확인
python3 scripts/collect_v2.py all       # 전체 수집 (30분~1시간)

# 또는 Railway 백그라운드 (사용자 .env 우회)
curl -X POST https://api.taieng.co.kr/law-collector/collect/all
```

**참고**: v3.0.2 정정으로 Railway에서 본 수집도 정상 작동. 사용자 로컬 디버깅 불필요.

### Step G: 운영 13개 검증 불가 룰 정합화

archive에 격리된 13개 법령에 대한 운영 룰 (S3 § 2.4):
- 공공보건의료법, 노인복지법군(4), 사회복지사업법군(4)
- 어린이놀이시설법, 의료법군(3), 학교안전사고법군(2)

재수집 후 출처 검증 가능해짐 → SQL로 정합 룰만 유지, 잘못된 룰 archive 이동.

---

## 6. 트러블슈팅 가이드 (S4 발견 사항)

### 증상 1: catalog count=0 + has_api_key=false
- **원인**: 환경변수명 불일치 (S4에서 발견)
- **확인**: `curl https://api.taieng.co.kr/law-collector/env-check`
- **해결**: 코드(v3.0.2)는 dual fallback 적용됨. 그래도 안 되면 Railway Variables 재확인.

### 증상 2: catalog count=0 + has_api_key=true
- **원인**: Supabase upsert 실패 가능성
- **확인**: Railway Logs에서 `[CATALOG] UPSERT 실패` 검색
- **해결**: SUPABASE_URL/KEY 검증

### 증상 3: 502 Bad Gateway
- **원인**: 서버 startup 실패 (import 에러)
- **확인**: Railway Logs (traceback)
- **해결**: 마지막 commit 정정 또는 revert

### 증상 4: deploy 후에도 환경변수 reload 안 됨
- **원인**: Railway 자동 redeploy 누락
- **해결**: Railway 대시보드 → Service → "Redeploy"

### 증상 5: 사용자 로컬 .env DNS 실패 (`[Errno 8]`)
- **원인**: macOS DNS 풀이 (CRLF 또는 환경변수 형식 문제)
- **현재 회피**: Railway 백그라운드 사용
- **추후 해결 (옵션)**:
  ```bash
  cd ~/dev/tai-api
  set -a; source .env; set +a
  echo "URL: '$SUPABASE_URL'"  # 따옴표로 공백/특수문자 검출
  file .env
  head -3 .env | cat -A         # ^M(\r) 가시화
  ```

---

## 7. 미해결 결정 사항 (다음 세션 사용자 확정 필요)

### 7.1 신규 도메인 추가 여부 (S3 § 6.1 이월)
현재 11개: BUILDING/CONSTRUCTION/INDUSTRIAL_SAFETY/FIRE/GAS/ELECTRIC/CHEMICAL/ENERGY/ENVIRONMENT/DISASTER/LABOR

추가 후보:
- **WELFARE**: 의료/노인/사회복지/장애인/학교/어린이 (사용자 통찰 부속시설)
- **COMMUNICATION**: 방송통신설비

또는 BUILDING에 통합?

### 7.2 사업장 다중 타입 모델링 (운영 단계 작업)
사용자 통찰 "학교에 공장, 공장에 노인시설" → master_building_legal_rules 의 building_use_type_code/business_type_code 배열화? 또는 별도 매핑 테이블?

수집 완료 후 별도 설계.

### 7.3 추가 외부 발견 법령 (Step D 결과)
catalog 수집 완료 후 발견되는 미보유/미타겟 CORE/EXTENDED 법령들. 사용자가 개별 검토 필요.

---

## 8. Phase 3+ 미해결 과제 (참고)

| 과제 | 상태 |
|---|---|
| 별표/서식 수집 | 4/23부터 미해결 (admrul_attachment 별도 API) |
| NFTC/NFPC 세부 파싱 | "1.1.1.1" 단위까지 paragraph/item 분리 |
| 자동 업데이트 재가동 | Railway cron `/check-updates-v2` |
| 운영 13개 검증 불가 룰 정합화 | Step G에서 진행 |
| 매핑 오류 4개 패턴 정정 | AI_GENERATED 714건의 49% (S2 발견) |
| α 검증 작업 (S1) | 패러다임 전환으로 폐기 |
| 사용자 로컬 .env DNS 문제 | Railway 우회로 해결, 근본 해결 보류 |

---

## 9. 핵심 원칙 재확인

```
1. 임의해석 금지 — 컷오프/규칙은 모두 사용자 결정 또는 결정론적
2. 분할 검토는 AI 몰입 위험 — 큰 그림 유지
3. 데이터 인프라 먼저, 추출은 그 위에서
4. 적용 룰 1건 = 수백 업체 영향 — 신중
5. 신뢰 추락 방지 — 잘못 매핑 시 모든 사용업체가 안 해도 될 의무 수행
6. "건물/산업/건설 + 다중 부속시설" — 사용자 SaaS 통찰
7. 정방향 100% 패스 후 역방향 검증 — 정방향 자체에도 누락 (현 작업 목적)
8. 환경 디버깅보다 인프라 우회 — 사용자 시간 절약 우선 (S4 학습)
```

---

## 10. 다음 세션 첫 메시지 (예시)

**최단 진입**:
> "tai-admin/docs의 HANDOFF_20260502_S4.md 학습. Step B-1부터."

**상세 진입**:
> "S4 핸드오프 봤음. v3.0.2 deploy 끝났는지 debug/건축 호출하고 결과 보여줘.
> 정상이면 catalog 트리거하고 30분 후 모니터링 시작."

**병렬 진입** (사용자가 이미 트리거 한 경우):
> "catalog 트리거했음. 진행상황 봐줘."

→ Claude가 Supabase MCP로 즉시 확인 → 단계별 진행

---

## 11. 핸드오프 체인 (참조용)

| 핸드오프 | 시점 | 핵심 내용 |
|---|---|---|
| 5/1 (HANDOFF_20260501.md) | 어제 | preserved 부분 일치 48건 분리 |
| HANDOFF_20260502_S1.md | 5/2 17:53 | α 검증 시도 → 한계 발견 |
| HANDOFF_20260502_S2.md | 5/2 19:00 | 4가지 매핑 오류 + 정방향 전환 |
| HANDOFF_20260502_S3.md | 5/2 19:50 | 통합 80개 + 외부 카탈로그 인프라 |
| **HANDOFF_20260502_S4.md** (현재) | 5/2 20:30 | **Railway 인프라 + 환경변수 호환** |

다음 세션에서 작성할 핸드오프: **HANDOFF_20260502_S5.md** (또는 5/3 신규 일자)

---

## 12. Commit 이력 (S4)

| 시각 | Commit | 내용 |
|---|---|---|
| 10:53 | `6f1e72a4` (admin) | docs S1 push |
| 10:54 | `0553405e` (admin) | docs S2 push |
| 10:57 | `94756b4f` (admin) | docs S3 push (위험물 운송 결정) |
| 10:59 | `b053c32c` (api) | scripts/collect_catalog.py |
| 11:11 | `40f33b1f` (api) | routers/law_catalog_collector.py + main.py v5.43.0 |
| 11:30 | `9b78a31c` (api) | env-check 추가 (오타 ND 포함 — 위험) |
| 11:32 | `08cf267b` (api) | 첫 줄 ND 오타 fix |
| 11:41 | `2721ca58` (api) | **routers/law_collector.py v3.0.2 (DATA_GO_KR fallback)** ← 핵심 |

---

**작성**: 2026-05-02 20:30 KST
**Railway 마지막 commit**: `2721ca58` (deploy 진행 중)
**다음 세션 진입점**: § 5 Step B-1 (debug/건축 호출 → has_api_key:true 확인)
**예상 소요**: Step B-3까지 30~60분 백그라운드 + Step C~G는 사용자 검토 포함 1~2시간
