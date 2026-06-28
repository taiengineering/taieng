# WO-FACILITY-PROFILE-BATCH-001 — facility_profiles 배치 생성 (P1-1)

**작성일:** 2026-06-27 | **상태:** 코호트 선정·before-snapshot·검증계획 완료 / **100회 POST 실행은 대표·Cursor 핸드오프**(네트워크 제약).
**원칙:** 기존 `facility_profile_service`만 사용. 새 generator 0. 읽기·검증은 Claude(Supabase MCP), 실행은 인증 HTTP.

> 실행 제약(정직): `facility_profile_service`는 `POST /facility-profiles/{factory_id}` **단건 엔드포인트**로만 호출된다(배치 엔드포인트 없음). Claude는 bash 네트워크 OFF로 HTTP 호출 불가, SQL 직접 생성은 "service 우회 금지"에 위배. 따라서 100회 POST는 대표/Cursor가 실행, Claude가 전후 DB 전수 검증.

---

## TASK-001 — 생성 경로 (코드 직독)
```
엔드포인트: POST /facility-profiles/{factory_id}   (routers/facility_profile_api.py, 인증 없음)
서비스:    services/facility_profile_service.py
  build_facility_profile(row) : factories row → 프로파일 dict (순수함수, stdlib만, 외부의존 0)
     - TriValue: null→{state:UNKNOWN,value:null} / 값→{state:PRESENT,value:..}
     - sector 없으면 'INDUSTRIAL' 기본(provenance=DEFAULT)
     - 존재하지 않는 컬럼은 row.get()→None→UNKNOWN (에러 없음·안전)
     - profile_version 기본 2
  profile_to_db_row(profile) : 11차원 평탄화 컬럼 + profile_snapshot(JSON 전체)
업데이트 조건: 기존 프로파일 있으면 API가 profile_version = max+1 로 증가 insert
출력: facility_profiles 1행 (factory_id, profile_version, sector, ksic_code, *_state/value/provenance, profile_snapshot)
배치 함수: 없음 → id별 POST 반복이 유일 경로
```

## TASK-002 — A Tier 코호트 (재현 가능)
```sql
-- 코호트 100건 (sector+ksic+employee 완비, 기존 프로파일 없음, 결정적 정렬)
SELECT f.id
FROM factories f
WHERE nullif(trim(f.sector),'') IS NOT NULL
  AND nullif(trim(f.ksic_code),'') IS NOT NULL
  AND f.employee_count IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM facility_profiles p WHERE p.factory_id = f.id)
ORDER BY f.id
LIMIT 100;
```
구성: CONSTRUCTION 93 / INDUSTRIAL 5 / BUILDING 2 (3섹터 포함). A티어 잔여 모집단 5,398.
id 범위: 000ddd5e… ~ 04b42b88…

## before-snapshot
```
facility_profiles  rows 4 / distinct factories 2   ← 생성 전 기준선
A티어(프로파일 없음)  5,398
```

## TASK-003 — 코호트 실행 (대표/Cursor 핸드오프)
**옵션 A — 대표 curl 루프(bash):**
```bash
API=https://api.taieng.co.kr
# 1) 위 코호트 SQL 결과를 ids.txt(한 줄당 UUID)로 저장
# 2) 100회 POST
while read id; do
  curl -s -o /dev/null -w "%{http_code}  $id\n" -X POST "$API/facility-profiles/$id"
done < ids.txt
# 기대: 전부 200
```
**옵션 B — Cursor 스크립트(엔드포인트 사용, 우회 아님):**
```python
import requests
from supabase import create_client  # 기존 클라이언트 사용
ids = [r["id"] for r in supabase.rpc(...) ]  # 또는 위 SQL로 조회
for fid in ids:
    r = requests.post(f"https://api.taieng.co.kr/facility-profiles/{fid}")
    print(r.status_code, fid)
```
※ 두 옵션 모두 기존 service/endpoint만 호출 — 새 generator/우회 없음.

## TASK-004 — 생성 결과 전수 검증 (실행 후 Claude가 Supabase로)
```sql
-- (a) 성공 수 / 시설 수
SELECT count(*) rows_after, count(DISTINCT factory_id) factories_after FROM facility_profiles;
-- (b) 코호트 100건 생성 여부(누락=실패)
WITH cohort AS (
  SELECT f.id FROM factories f
  WHERE nullif(trim(f.sector),'') IS NOT NULL AND nullif(trim(f.ksic_code),'') IS NOT NULL
    AND f.employee_count IS NOT NULL
  ORDER BY f.id LIMIT 100)
SELECT count(*) cohort, count(p.factory_id) created,
       count(*)-count(p.factory_id) AS missing_failed
FROM cohort c LEFT JOIN facility_profiles p ON p.factory_id=c.id;
-- (c) NULL 필드(필수): sector/factory_id NULL = 0 이어야
SELECT count(*) FILTER (WHERE sector IS NULL) sector_null,
       count(*) FILTER (WHERE factory_id IS NULL) fid_null FROM facility_profiles;
-- (d) 중복: 코호트 시설이 2행 이상이면 중복
SELECT factory_id, count(*) c FROM facility_profiles GROUP BY 1 HAVING count(*)>1 ORDER BY c DESC;
```
검증 기준: created=100, missing_failed=0, sector_null=0, fid_null=0, 코호트 중복 0.

## TASK-005 — Applicability 입력 가능성 증가 (실행 안 함, 분석만)
```
Before  facility_profiles factories = 2
After   facility_profiles factories = 102  (예상)
→ profiles 보유 시설 2 → 102. (Applicability 실행은 본 WO 범위 아님 — 입력계층 확보만.)
※ 동일 섹터에서 facility_applicability MISSING_DATA% 재측정은 후속(STEP 별도).
```

## TASK-006 — 확대 제안 (실행 안 함, 제안만)
```
100 코호트 전부 PASS 시 확대 경로:
  100 → 500 → 1,000 → 5,398(A티어 전량)
배치 단위 500 권장(POST 부하·검증 주기). 각 배치마다 TASK-004 전수 검증.
섹터 편중(건설 90%) 고려: 산업/건물은 소수라 조기 전량 포함 가능.
```

## TASK-007 — 최종 보고 (실행 후 채움)
```
생성 전 facility_profiles factories   2
생성 후 facility_profiles factories   __ (목표 102)
성공률                                 __% (목표 100/100)
실패                                   __건 (목표 0)
중복                                   __건 (목표 0)
NULL(sector/factory_id)                __건 (목표 0)
```

## Boundary 준수
```
facility_profiles 생성: YES(기존 service). Applicability 실행/수정: NO. obligation_instance: NO.
Check/Diagnosis/Transform/Legal Engine: 미수정. 새 generator/service 우회: 0.
Claude 실행분: 코호트 선정·before/after 전수 검증(읽기). 100회 POST: 대표/Cursor.
```

*WO-FACILITY-PROFILE-BATCH-001 — 코호트 100(재현가능)·before 2시설·검증쿼리 준비 완료. 100회 POST 실행 시 Claude가 즉시 전수 검증→TASK-007 채움→확대 판단.*
