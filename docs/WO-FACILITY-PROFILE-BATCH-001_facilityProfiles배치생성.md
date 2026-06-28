# WO-FACILITY-PROFILE-BATCH-001 — facility_profiles 배치 생성 (P1-1) ✅ PASS

**작성일:** 2026-06-27 | **완료:** 2026-06-28 | **상태:** 100 코호트 생성·전수검증 완료. **PASS.**
**원칙:** 기존 `facility_profile_service`만 사용. 새 generator 0. 실행=대표 curl(200×100), 검증=Claude(Supabase MCP).

> 결과 요약: A티어 100 코호트 전부 `POST /facility-profiles/{id}` 200 성공. facility_profiles 시설 2→102. 누락 0 / NULL 0 / 중복 0. 값 보존(글읽기) 정상.

---

## ✅ 실행 결과 (TASK-007 최종)
```
생성 전 facility_profiles  rows 4   / factories 2
생성 후 facility_profiles  rows 104 / factories 102
코호트 생성               100 / 100   (성공률 100%)
실패                      0
중복(코호트 시설 2행+)     0
NULL(sector/factory_id)   0
profile_version           2 (신규 전건)
글읽기 검증               sector/ksic 실값, regular_workers PRESENT+실값(예 350·600·120),
                         construction_amount PRESENT+실값, UNKNOWN-as-value 위반 0
HTTP 결과                 200 × 100 (대표 실행 로그 fp_batch_result.log)
```

## TASK-001 — 생성 경로 (코드 직독)
```
POST /facility-profiles/{factory_id}  (routers/facility_profile_api.py, 인증 없음, 단건)
build_facility_profile(row)  : 순수함수(stdlib만). null→UNKNOWN / 값→PRESENT. sector 없으면 INDUSTRIAL.
                               존재하지 않는 컬럼은 None→UNKNOWN (에러 없음).
profile_to_db_row(profile)   : 11차원 평탄화 + profile_snapshot(JSON). 기존 있으면 version=max+1.
배치 함수 없음 → id별 POST 반복이 유일 경로.
```

## TASK-002 — A Tier 코호트 (재현 가능)
```sql
SELECT f.id FROM factories f
WHERE nullif(trim(f.sector),'') IS NOT NULL
  AND nullif(trim(f.ksic_code),'') IS NOT NULL
  AND f.employee_count IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM facility_profiles p WHERE p.factory_id=f.id)
ORDER BY f.id LIMIT 100;
```
구성: CONSTRUCTION 93 / INDUSTRIAL 5 / BUILDING 2. A티어 잔여(생성 후) 5,298.

## TASK-003 — 실행 (대표 curl, 완료)
`ids.txt`(100) → `while read id; do curl -X POST $API/facility-profiles/$id; done` → 200×100.

## TASK-004 — 전수 검증 (완료, 위 결과)
created=100 / missing=0 / sector_null=0 / fid_null=0 / 코호트 중복=0. **전 항목 PASS.**

## TASK-005 — Applicability 입력 가능성 증가
```
Before  facility_profiles factories = 2
After   facility_profiles factories = 102   (+100)
→ 입력계층 확보 +100 시설. (Applicability 실행은 본 WO 범위 아님.)
```

## TASK-006 — 확대 제안 (실행 안 함, 제안만)
```
100 코호트 PASS → 확대 가능.
경로:  100(완료) → 500 → 1,000 → 5,298(A티어 잔여 전량)
단위:  배치 500 권장. 각 배치마다 TASK-004 전수검증 + 글읽기 샘플.
주의:  코호트 SQL의 NOT EXISTS 조건이 이미 생성분을 자동 제외 → 재실행 안전(중복 방지).
       섹터 편중(건설 90%)이라 산업/건물 소수는 조기 전량 포함 권장.
다음 권장: 500 배치(동일 SQL LIMIT 500) → 검증 → 1,000 → 잔여.
```

## Boundary 준수
```
facility_profiles 생성: 기존 service만. Applicability 실행/수정·obligation_instance·Check·Diagnosis·Transform·Legal Engine: 미수정.
새 generator/우회: 0. Claude=코호트·검증(읽기), 대표=100회 POST.
```

*WO-FACILITY-PROFILE-BATCH-001 — PASS. facility_profiles 2→102, 성공률 100%, 누락·NULL·중복 0, 값 보존 정상. 다음: 500 배치 확대(동일 SQL, 재실행 안전).*
