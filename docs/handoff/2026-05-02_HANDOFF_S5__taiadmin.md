# HANDOFF — 2026-05-02 세션 5 (검증된 인프라 원복 + 자동 트리거 차단)

> **작업명**: S4의 잘못된 진단(data.go.kr 전환) 원복 + 자동 파이프라인 차단
> **상태**: v3.0.6 deploy 완료, cron 5개 비활성화 완료, 법제처 API 야간/주말 불안정으로 검증 보류
> **다음 세션 진입점**: § 5. 평일 주간 debug/건축 호출 → catalog 트리거 → 30~60분 모니터링

---

## 0. 세션 흐름 (S1~S5 통합)

```
S1 (5/2 17:53): α 검증 시도 → 표면 일치 한계 발견
   ↓
S2 (5/2 19:00): 4가지 매핑 오류 패턴 + 정방향 패러다임 전환
   ↓
S3 (5/2 19:50): 4/22 archive 발견 + 통합 마스터 80개 추출 + 외부 카탈로그 인프라 작성
   ↓
S4 (5/2 20:30): Railway 인프라 디버깅 + DATA_GO_KR 환경변수 fallback (v3.0.2)
   ↓
S5 (5/2 22:30~): 검증된 인프라 원복 + 자동 트리거 차단 (현재)
   - S2/S3/S4 핸드오프 학습 → data.go.kr 파라미터 시도 (v3.0.3~3.0.5)
   - 사용자 지적: "법령엔진은 4/23에 검증 끝났다. 왜 자꾸 뜯어고치는가?"
   - 패러다임 정정: data.go.kr 분기 완전 폐기 → law.go.kr/DRF + OC 단일 경로 원복
   - cron 5개 비활성화로 매핑 오류 재발 방지
```

---

## 1. S5 작업 요약 (시간순)

### 1.1 잘못된 시도 (S4 잔재)

S2/S3/S4 핸드오프 학습 후 catalog 트리거 전 테스트 진행 — `debug/건축` 호출 시 `resultCode 03` (요청 파라미터 오류). data.go.kr 공식 스펙 검증을 위해 Chrome으로 https://www.data.go.kr/data/15000115/openapi.do 직접 확인. 5개 필수 파라미터(serviceKey/target/query/numOfRows/pageNo) 추출. 그러나 모든 파라미터 정렬 후에도 03 에러 지속.

| 시도 | commit | 변경 | 결과 |
|---|---|---|---|
| v3.0.3 | `13da69d2` | `pageIndex` → `pageNo` | 03 에러 그대로 |
| v3.0.4 | `33516f5a` | `target=law` 추가 | 03 에러 그대로 |
| v3.0.5 | `27aed365` | `type=xml` 제거 (공식 cURL 샘플 정확 매칭) | 03 에러 그대로 |

### 1.2 추가 발견 (Chrome 검증 부산물)

data.go.kr 데이터셋 구조 파악:

| 데이터셋 | API | 인증 |
|---|---|---|
| 15000115 법령정보 | REST API (`apis.data.go.kr/1170000/law/lawSearchList.do`) | data.go.kr serviceKey |
| 15057358 현행법령 본문 | **LINK** (`law.go.kr/LSO/openApi/lsNwInfoGuide`) | law.go.kr **OC** |
| 15057542 행정규칙 목록 | **LINK** (`law.go.kr/LSO/openApi/admrulListGuide`) | law.go.kr **OC** |
| 15056579 행정규칙 본문 | **LINK** (`law.go.kr/LSO/openApi/admrulInfoGuide`) | law.go.kr **OC** |

→ data.go.kr serviceKey는 법령 목록 1개에만 작동. 법령 본문/행정규칙 모두 law.go.kr/OC 필요.  
→ **즉 처음부터 law.go.kr/DRF + OC 단일 경로가 옳았음.**

### 1.3 사용자 핵심 지적 (패러다임 정정)

> **"법령엔진은 수집에 대해서 벌써 검증이 끝나서, 수집할 법령을 정의하면 수집이 되게 되어있는데. 왜 자꾸 뜯어고치는거죠?"**
> 
> **"먼저 문서는 참고이고, 실제 구현된것을 먼저 확인해야 하는거 아닌가요?"**
> 
> **"기존의 파이프라인을 원복하고, 수집해야할 대상에 대해 수집먼저 시행이 필요합니다. 다만 파이프라인이라. 등록과 동시에 바로 다음프로그램들이 작동을 하게 되면, 지금 발견했던 누락 오매칭이 나올수 있습니다. 이건 막고 수집하고, 테스트와 분석으로 그다음단계 다음단계 식으로 진행해야 합니다."**

→ S5의 진짜 작업은 **원복 + 차단**.

### 1.4 사용자 ON-RECORD 결정 (5/2 S5)

| 항목 | 결정 |
|---|---|
| Railway 고정 IP | ✅ 이미 구매·등록 완료 (Railway는 유동 IP라 고정 IP를 별도 구매해서 OC에 등록) |
| data.go.kr 전환 | ❌ 폐기 (불필요한 우회였음) |
| 4/23 검증 인프라 | ✅ 그대로 사용 (`law.go.kr/DRF` + `OC=taieng`) |
| 자동 cron | ✅ 모두 비활성화 (수집 → 자동 룰 생성 흐름 차단) |
| 작업 흐름 | "수집 → 테스트 → 분석 → 다음 단계" — 단계별 사용자 검증 |
| 이번 세션 검증 시도 | 법제처 야간/주말 불안정으로 보류 → 다음 세션 평일 주간 |

### 1.5 v3.0.6 코드 원복 (commit `b6a5d4b5`)

**`routers/law_collector.py` v3.0.6**:
- `DATA_GOV_KEY` / `DATA_GOV_BASE` 변수 + 모든 data.go.kr 분기 코드 제거
- `fetch_law_list`, `fetch_law_content` 모두 `LAW_API_BASE` (`http://www.law.go.kr/DRF`) + `OC=taieng` 단일 경로
- `debug/{law_name}` 응답에 `oc` 필드 추가 (검증용)
- `/status` 응답: `version: "3.0.6"`, `api_source: "law.go.kr/DRF"`, `oc: "taieng"`

**제거된 코드**:
```python
# 폐기
DATA_GOV_KEY  = os.environ.get("DATA_GO_KR_SERVICE_KEY", "") or os.environ.get("DATA_GOV_SERVICE_KEY", "")
DATA_GOV_BASE = "https://apis.data.go.kr/1170000/law"

if DATA_GOV_KEY:
    # data.go.kr 분기 (v3.0.0~3.0.5 시도) — 모두 제거
    ...
else:
    # law.go.kr/DRF
    ...
```

**남은 코드**:
```python
LAW_API_OC   = os.environ.get("LAW_API_OC", "taieng")
LAW_API_BASE = "http://www.law.go.kr/DRF"

def fetch_law_list(query, display=100, page=1):
    url = f"{LAW_API_BASE}/lawSearch.do"
    params = {"OC": LAW_API_OC, "target": "law", "type": "XML",
              "query": query, "display": display, "page": page}
    ...
```

### 1.6 자동 cron 5개 비활성화 (Supabase, S5 핵심 안전 조치)

scheduler.py가 startup에 `cron_job_master` 테이블에서 활성 작업을 load. v3.0.6 deploy로 Railway 재시작 → cron 새로 load → 비활성화 반영.

```sql
UPDATE cron_job_master
SET is_active = false, updated_at = NOW()
WHERE category = 'LAW'
  AND job_code IN (
    'LAW_COLLECT_MISSING',
    'LAW_UPDATE_CHECK',
    'LAW_RECOLLECT_15D',
    'RULE_REPARSE',
    'VALIDATE_MASTER'
  );
```

| job_code | 일정 | 위험도 | 차단 이유 |
|---|---|---|---|
| `RULE_REPARSE` | 매주 수 04:00 | **매우 높음** | `/law-rule-generator/reparse-master` — AI(Sonnet)로 룰 빈칸 자동 보강. **4/24~25 매핑 오류 진원 의심 1순위** |
| `LAW_COLLECT_MISSING` | 매주 일 04:00 | 높음 | 미수집 법령 자동 수집 (사용자 검증 없이) |
| `LAW_UPDATE_CHECK` | 매일 03:00 | 높음 | 자동 업데이트 |
| `LAW_RECOLLECT_15D` | 1·16일 03:00 | 중 | 변경 감지 + AI 룰 NEEDS_REVIEW 자동 표시 |
| `VALIDATE_MASTER` | 매주 금 06:00 | 낮음 | 검증 리포트 (수정 X, 노이즈) |

🟢 이미 비활성: `AUTO_PARSE_NEW` (사용자가 미리 차단해둠 — 4/24~25 매핑 오류 발견 후)

### 1.7 검증 시도 (timeout)

`curl https://api.taieng.co.kr/law-collector/debug/건축` 응답:

```json
{
  "error_type": "ConnectTimeout",
  "error_b64": "..."  // 디코드: HTTPConnectionPool(host='www.law.go.kr', port=80): 
                     //         Connection to www.law.go.kr timed out (connect timeout=30)
}
```

→ Railway → `www.law.go.kr:80` 연결 자체 timeout. IP 인증 거부(연결됨+응답거부)와 다른 양상.

**사용자 진단**: "법제처가 야간에 연결이 불안합니다. 주말에." → 평일 주간 재시도 필요.

---

## 2. 현재 시점 상태 (S5 종료 시점)

### 2.1 인프라
- 마지막 commit: `b6a5d4b5` (v3.0.6) — deploy 완료 확인 (`/status` 응답 `version:"3.0.6"`, `api_source:"law.go.kr/DRF"`, `oc:"taieng"`)
- 코드: 4/23 검증된 law.go.kr/DRF + OC 단일 경로
- Railway 환경변수: `LAW_API_OC=taieng` ✅ / `DATA_GO_KR_SERVICE_KEY` 등록되어 있으나 **코드가 안 봄** (제거 가능, 필수 아님)

### 2.2 자동 cron (모두 비활성)
- LAW 카테고리 5개: `LAW_COLLECT_MISSING`, `LAW_UPDATE_CHECK`, `LAW_RECOLLECT_15D`, `RULE_REPARSE`, `VALIDATE_MASTER` — 모두 `is_active=false`
- 사전 비활성: `AUTO_PARSE_NEW`
- 다른 카테고리 cron(DATA, education, REPORT, SYSTEM 등)은 영향 없음 — 그대로 활성

### 2.3 DB 상태
- `law_master`: 182개 (4/23 그대로)
- `law_external_catalog`: 0건 (수집 시도는 모두 실패 — data.go.kr 03 / law.go.kr timeout)
- `law_collection_target`: 기존 그대로
- `law_master_archive_20260422`: 48개 (변경 없음)

### 2.4 미해결 작업
- 평일 주간 `debug/건축` 검증 (가장 우선)
- 정상 시 → 외부 카탈로그 수집 트리거 (Step B-2)
- 30~60분 백그라운드 모니터링 → 분류 → 누락 추출 → 사용자 검토

---

## 3. 환경 정보

| 항목 | 값 |
|---|---|
| Supabase Project | 서울 `vwlahtguyggrhvslabax` |
| Railway URL | `https://api.taieng.co.kr` |
| Repo (admin) | `taiengineering/tai-admin` (docs/) |
| Repo (api) | `taiengineering/tai-api` (scripts/, routers/, docs/) |
| Railway 외부 IP | 고정 (사용자 별도 구매), open.law.go.kr OC=taieng에 등록 |
| 4/23 핵심 문서 | `tai-api/docs/LAW_COLLECTION_COMPLETE_2026-04-23.md` |
| 5/2 핸드오프 | `tai-admin/docs/HANDOFF_20260502_S{1,2,3,4,5}.md` |
| 사용자 환경 | Mac M2max, ~/dev/tai-api |

---

## 4. v3.0.6 코드 검증 포인트 (다음 세션 첫 작업)

### 4.1 Step B-1: API 연결 검증 (평일 주간)

```bash
curl -m 15 https://api.taieng.co.kr/law-collector/debug/건축
```

**기대 결과 (정상)**:
```json
{
  "api_source": "law.go.kr",
  "oc": "taieng",
  "query": "건축",
  "http_status": 200,
  "ok": true,
  "law_count": 5,           ← 0이 아님
  "xml_root_tag": "LawSearch",
  "first_law": {
    "법령ID": "...",
    "법령명한글": "건축법",
    ...
  }
}
```

**timeout 재발 시 진단 SQL** (사용자 로컬에서 같은 URL 직접 호출):
```bash
curl -m 15 'http://www.law.go.kr/DRF/lawSearch.do?OC=taieng&target=law&type=XML&query=건축&display=5'
```
- 정상 응답: Railway → law.go.kr 네트워크 차단 의심 (고정 IP가 OC 미등록 가능성)
- 동일 timeout: 법제처 서버 점검 (시간 두고 재시도)
- "사용자 정보 검증 실패" XML: 사용자 IP가 OC 미등록 (드문 케이스)

### 4.2 Step B-2: catalog 트리거

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
  "started_at": "2026-05-XX..."
}
```

### 4.3 Step B-3: 진행 모니터링

**curl 옵션**:
```bash
curl https://api.taieng.co.kr/law-collector/catalog-status
```

**Claude MCP 옵션** (사용자 "진행상황 봐줘" 요청 시):
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

### 4.4 Step C: 분류 SQL (Claude MCP)

수집 완료 후 Claude가 자동 실행:

```sql
-- 1. law_master 보유 여부
UPDATE law_external_catalog ec
SET is_in_law_master = EXISTS(
  SELECT 1 FROM law_master lm 
  WHERE lm.law_name = ec.law_name OR lm.law_api_id = ec.law_api_id
);

-- 2. law_collection_target 등록 여부
UPDATE law_external_catalog ec
SET is_in_collection_target = EXISTS(
  SELECT 1 FROM law_collection_target lct
  WHERE lct.law_name = ec.law_name OR lct.law_api_id = ec.law_api_id
);

-- 3. archive 보관 여부
UPDATE law_external_catalog ec
SET is_in_archive = EXISTS(
  SELECT 1 FROM law_master_archive_20260422 lma
  WHERE lma.law_name = ec.law_name OR lma.law_api_id = ec.law_api_id
);

-- 4. SaaS 관련성 분류 (S4 § 5 Step C 참조 — CASE 문 그대로)
UPDATE law_external_catalog ec SET saas_relevance = CASE ... END;
```

### 4.5 Step D: 누락 추출 + 사용자 검토 (자동 진행 차단)

```sql
SELECT law_name, law_type_code, ministry_name, saas_relevance, api_target, search_keyword
FROM law_external_catalog
WHERE is_in_law_master = FALSE
  AND is_in_collection_target = FALSE
  AND saas_relevance IN ('CORE', 'EXTENDED')
ORDER BY saas_relevance, ministry_name, law_name;
```

→ Claude가 결과 정리 (통합 마스터 80개와 비교, 외부 발견 별도 표시) → **사용자 검토 후 수동 승인** → 다음 단계.

### 4.6 Step E: 통합 마스터 → law_collection_target INSERT

S3 § 5 Step E 참조. archive 26개(api_id 보유) 직접 INSERT + C 12개 + B only 42개 이름만 등록.

**⚠️ 결정 보류**: 신규 도메인 추가 (WELFARE / COMMUNICATION 또는 BUILDING 통합) — 사용자 확정 필요.

### 4.7 Step F: 본 수집 (Railway 백그라운드)

```bash
curl -X POST https://api.taieng.co.kr/law-collector/collect/all
```

→ `law_collection_target` PENDING 항목 모두 수집. 30분~1시간.

### 4.8 Step G: 운영 13개 검증 불가 룰 정합화

archive 격리 13개 룰의 출처 검증 → 정합 룰만 유지, 잘못된 룰 archive로 이동.

### 4.9 Step H: 자동 cron 재활성화 (사용자 검토 후)

모든 단계 검증 + 사용자 승인 완료 후:
```sql
UPDATE cron_job_master
SET is_active = true, updated_at = NOW()
WHERE category = 'LAW'
  AND job_code IN (
    'LAW_COLLECT_MISSING',
    'LAW_UPDATE_CHECK',
    'LAW_RECOLLECT_15D',
    'VALIDATE_MASTER'
  );
-- RULE_REPARSE는 매핑 오류 정정 검증 후 별도 결정
```

`RULE_REPARSE`는 4/24~25 매핑 오류 진원 의심 1순위 — Phase 3+의 매핑 오류 정정 작업 완료 후 결정.

---

## 5. 🔴 다음 세션 — 즉시 실행 워크플로우

### 5.1 평일 주간 첫 명령

```bash
# Railway 검증
curl -m 15 https://api.taieng.co.kr/law-collector/debug/건축
```

→ `law_count > 0` 확인되면 § 4.2 catalog 트리거로 진행

### 5.2 timeout 재발 시 진단 (§ 4.1 참조)

사용자 로컬에서 같은 URL 직접 호출 → 결과로 다음 액션 결정.

---

## 6. 트러블슈팅 가이드 (S5 발견 사항)

### 증상 1: ConnectTimeout (Railway → www.law.go.kr:80)
- **시점**: 야간/주말 또는 법제처 서버 점검
- **확인**: 사용자 로컬에서 같은 URL 호출 → 정상이면 Railway 측 문제, 동일 timeout이면 법제처 측
- **해결**: 평일 주간 재시도 또는 사용자 로컬 우회 (`scripts/collect_v2.py` 직접 실행)

### 증상 2: "사용자 정보 검증 실패" XML 응답 (HTTP 200)
- **원인**: 호출 IP가 OC=taieng에 미등록
- **확인**: `curl ifconfig.me` 등으로 외부 IP 확인 → open.law.go.kr 등록 IP 대조
- **해결**: open.law.go.kr 로그인 → IP 추가 등록

### 증상 3: 자동 cron이 비활성 상태인데도 룰 자동 생성됨
- **원인**: scheduler가 새로 load 안 함 (Railway 재시작 안 됨)
- **확인**: Railway log에서 `[CRON] 등록: ...` 메시지 확인
- **해결**: Railway manual restart 또는 push로 재배포 트리거

### 증상 4 (S4 잔재): data.go.kr 03 에러
- **결론**: 폐기. v3.0.6에서 분기 자체 제거. 다시 시도하지 말 것.
- **이유**: 4/23 검증 인프라(law.go.kr/DRF + OC) 정상 작동 시 불필요

---

## 7. 미해결 결정 사항 (다음 세션 사용자 확정 필요)

### 7.1 신규 도메인 추가 여부 (S3 § 6.1 / S4 § 7.1 이월)
현재 11개: BUILDING/CONSTRUCTION/INDUSTRIAL_SAFETY/FIRE/GAS/ELECTRIC/CHEMICAL/ENERGY/ENVIRONMENT/DISASTER/LABOR

추가 후보:
- **WELFARE**: 의료/노인/사회복지/장애인/학교/어린이
- **COMMUNICATION**: 방송통신설비

또는 BUILDING에 통합?

### 7.2 사업장 다중 타입 모델링 (운영 단계)
사용자 통찰 "학교에 공장, 공장에 노인시설" → master_building_legal_rules 의 building_use_type_code/business_type_code 배열화? 또는 별도 매핑 테이블? 수집 완료 후 별도 설계.

### 7.3 추가 외부 발견 법령 (Step D 결과)
catalog 수집 완료 후 발견되는 미보유/미타겟 CORE/EXTENDED 법령들. 사용자 개별 검토 필요.

### 7.4 RULE_REPARSE 재활성화 시점
4/24~25 매핑 오류 진원 의심. Phase 3+의 AI_GENERATED 714건 49% 정합성 정정 작업 완료 후 결정.

---

## 8. Phase 3+ 미해결 과제 (S4에서 이월)

| 과제 | 상태 |
|---|---|
| 별표/서식 수집 | 4/23부터 미해결 (admrul_attachment 별도 API) |
| NFTC/NFPC 세부 파싱 | "1.1.1.1" 단위까지 paragraph/item 분리 |
| 자동 업데이트 재가동 | cron 비활성화됨 — Step H에서 재활성화 |
| 운영 13개 검증 불가 룰 정합화 | Step G에서 진행 |
| 매핑 오류 4개 패턴 정정 | AI_GENERATED 714건의 49% (S2 발견) — `RULE_REPARSE` 비활성화 유지 필요 |
| α 검증 작업 (S1) | 패러다임 전환으로 폐기 |
| 사용자 로컬 .env DNS 문제 | Railway 우회로 해결, 근본 해결 보류 |
| **data.go.kr 시도 (S5에서 추가)** | **폐기** — 4/23 검증 인프라가 옳음 |

---

## 9. 핵심 원칙 재확인 (S5에서 추가)

```
1. 임의해석 금지 — 컷오프/규칙은 모두 사용자 결정 또는 결정론적
2. 분할 검토는 AI 몰입 위험 — 큰 그림 유지
3. 데이터 인프라 먼저, 추출은 그 위에서
4. 적용 룰 1건 = 수백 업체 영향 — 신중
5. 신뢰 추락 방지 — 잘못 매핑 시 모든 사용업체가 안 해도 될 의무 수행
6. "건물/산업/건설 + 다중 부속시설" — 사용자 SaaS 통찰
7. 정방향 100% 패스 후 역방향 검증
8. 환경 디버깅보다 인프라 우회 — 사용자 시간 절약 우선 (S4)
9. ★ 검증된 인프라 먼저 확인 — 문서는 참고. 새 경로 시도하기 전에 기존 작동 코드 확인 (S5)
10. ★ 자동 파이프라인은 단계별 검증 후 재활성화 — 수집 → 자동 룰 생성 흐름은 매핑 오류 진원 (S5)
```

---

## 10. 다음 세션 첫 메시지 (예시)

**최단 진입 (평일 주간)**:
> "tai-admin/docs의 HANDOFF_20260502_S5.md 학습. debug/건축 결과 보여줘."

**상세 진입**:
> "S5 핸드오프 봤음. v3.0.6 deploy + cron 비활성화 모두 끝났으니, 평일 주간이라면 debug/건축 호출하고 결과 보고. 정상이면 catalog 트리거하고 30~60분 모니터링 시작."

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
| HANDOFF_20260502_S4.md | 5/2 20:30 | Railway 인프라 + DATA_GO_KR fallback (v3.0.2) |
| **HANDOFF_20260502_S5.md** (현재) | 5/2 22:30 | **검증된 인프라 원복(v3.0.6) + 자동 cron 차단** |

다음 세션 핸드오프: **HANDOFF_20260503_S6.md** (5/3 평일/주말, 내일 진행 시 일자 변경)

---

## 12. Commit 이력 (S5)

| 시각 | Commit | Repo | 내용 | 상태 |
|---|---|---|---|---|
| 12:00 | `13da69d2` | tai-api | v3.0.3 — pageIndex → pageNo | 폐기 (v3.0.6에 흡수) |
| 12:13 | `33516f5a` | tai-api | v3.0.4 — target=law 추가 | 폐기 |
| 12:45 | `27aed365` | tai-api | v3.0.5 — type 파라미터 제거 | 폐기 |
| 13:13 | **`b6a5d4b5`** | tai-api | **v3.0.6 — data.go.kr 분기 완전 제거 → law.go.kr/DRF + OC 단일 경로 원복** | ✅ **현재** |
| 13:14 | (Supabase) | — | LAW 카테고리 cron 5개 비활성화 | ✅ 적용됨 |

---

## 13. S5 핵심 학습 — Claude 자기 점검

**이번 세션에서 잘못된 패턴**:
1. S4 핸드오프의 "Railway IP 미등록 → data.go.kr 우회" 진단을 의심 없이 따름
2. 사용자가 4/23에 검증된 인프라를 가지고 있다는 정보(S3에 명시)를 흘림
3. data.go.kr 03 에러를 만나자 파라미터를 3번 연속 뜯어고침 (v3.0.3, v3.0.4, v3.0.5)
4. 사용자 명시적 지적 후에야 패러다임 정정

**다음 세션부터 적용**:
- 새 경로 시도 전에 기존 검증 인프라부터 확인
- 환경변수/설정 변경이 코드 변경보다 거의 항상 더 빠르고 안전
- 핸드오프 문서의 "현재 상태"보다 "검증된 작동 이력"을 우선

---

**작성**: 2026-05-02 22:30 KST
**Railway 마지막 commit**: `b6a5d4b5` (v3.0.6, deploy 완료)
**Supabase 마지막 변경**: cron_job_master LAW 5개 비활성화
**다음 세션 진입점**: § 5.1 평일 주간 debug/건축 호출
**예상 소요**: 검증 즉시 + Step B-3까지 30~60분 + Step C~G는 사용자 검토 포함 1~2시간
