# WO-RESTORE-ORIGINAL-PATH-001 — 원래 설계된 입력→입력표준 경로 규명·복원 지점

**작성일:** 2026-06-28 | **성격:** 읽기 전용. 기존 설계 문서·코드만 확인. **새 연결/수정/브릿지/FieldMap/Adapter 제안 없음.**
**근거 문서:** WO-INPUT-BINDING-ARCHITECTURE-001(2026-06-24), WO-DIAGNOSIS-TO-OBLIGATION-PIPELINE-001(2026-06-24), services/facility_profile_service.py(docstring "사용자 입력 계약 전체를 FacilityProfile 계약으로 정합").

> 허용된 결론 3가지만 기재.

---

## ① 원래 설계된 경로 (기존 문서가 규정한 그대로)
```
[소비자 입력 3섹션]  diagnosis_input_fields (BUILDING / INDUSTRIAL / CONSTRUCTION)
        │   + 주소 → building_register API (provenance=API)
        ▼
[입력표준]  facility_profiles  (정규화 저장소 = "입력표준")
        │   sector / ksic_code
        │   *_value / *_state / *_provenance  (THRESHOLD 9 numeric)
        │   input_fields (has_*)              (EXISTS)
        │   ※ build_facility_profile: 입력 계약 전체를 profile 계약으로 정합(수집→전달)
        ▼
[Binding Layer]  facility_profiles → Generator Input Contract
        │   has_* 28개 1:1 (변환 없음, MISSING 0)
        │   sector NULL→ksic 추론 / worker_count 동의어 COALESCE
        ▼
[obligation_generator]  Input Contract → cmc CONFIRMED 452 매칭
        ▼
[obligation_instance]
        ▼
[Check Engine / 6W]
```
설계 핵심(WO-INPUT-BINDING-ARCHITECTURE-001): **"입력표준과 generator는 이미 같은 언어를 쓴다. Binding은 변환이 아니라 조립."** has_* 28개가 입력표준 field_code와 100% 일치(MISSING 0)하도록 처음부터 동일 명명으로 설계됨.

※ 주의(트랙 구분): 이 경로의 입력표준은 **facility_profiles**다. `run_facility_applicability.py`의 `FIELD_MAP→factories` (facility_applicability 생성)는 **다른 트랙**이며, 의무생성 설계 입력표준이 아니다.

## ② 현재 그 경로의 어디까지 살아있는가 (실측)
```
[소비자 입력 3섹션] diagnosis_input_fields      ✔ 살아있음 (100필드, 3섹션·has_* 정의 존재)
[입력표준]          facility_profiles 테이블     ✔ 살아있음 (스키마 + build_facility_profile 서비스)
                    └ EXPANSION으로 has_*/construction_work/equipment/process 그룹까지 정합 완료
[Binding 규격]      WO-INPUT-BINDING-ARCHITECTURE ✔ 규격 완료 (has_* 1:1 매핑표 확정)
[obligation_generator + cmc 452]                  ✔ 존재 (테스트 1개 시설 obligation_instance 171/75 실증)
```
→ **테이블·서비스·규격·생성기는 전부 살아있음.** 부품은 설계대로 존재.

## ③ 끊긴 지점 (기존 설계 안에서만 — 2곳)
```
끊김-1 : 소비자 입력 3섹션 → facility_profiles "적재(정규화 저장)" 미배선
  설계: 진단 UI 입력(has_* 포함) + building_register → facility_profiles 채움.
  실측: build_facility_profile이 받는 row가 진단 입력이 아니라 factories(목업) row.
        (POST /facility-profiles/{factory_id} 가 factories를 읽어 build)
        → factories에는 has_*/process/equipment 컬럼이 없어 전부 UNKNOWN.
        → 진단 경로(anonymous/public/factory_diagnosis_results)와 facility_profiles의 factory_id 공유 0.
  = 설계상 "진단입력 → 입력표준" 적재 연결이 끊김 (WO-DIAGNOSIS-TO-OBLIGATION-PIPELINE-001 단절A와 동일).

끊김-2 : facility_profiles → Binding Layer → generator "실행" 미배선
  설계: WO-INPUT-BINDING-ARCHITECTURE(규격 완료) → WO-INPUT-BINDING-IMPLEMENTATION-001(구현·실행).
  실측: 규격은 완료, 그러나 facility_profiles → Generator Input Contract → generator 의 라이브 실행이
        테스트 1개 시설 외 운영 미연결 (obligation_instance가 1 시설에만 존재).
  = 설계의 마지막 "조립·실행" 단계가 미배선.
```

---

## 요약 (세 줄)
```
원래 경로 : 입력3섹션 → facility_profiles(입력표준) → Binding → generator → obligation_instance.
살아있는 곳: 입력계약·입력표준 테이블·build_facility_profile·바인딩 규격·생성기 전부 존재(부품 OK).
끊긴 곳   : (1) 진단입력→facility_profiles 적재가 factories(목업)에서 들어와 끊김,
            (2) facility_profiles→generator 바인딩 "실행"이 테스트 1건 외 미배선.
            ※ 두 지점 모두 기존 설계(WO-INPUT-BINDING-ARCHITECTURE/IMPLEMENTATION) 안의 단계이며 새 계층이 아님.
```

## Boundary 준수
```
읽기 전용. 코드/DB/INSERT/UPDATE/DELETE 0. 새 연결/수정/브릿지/FieldMap/Adapter 제안 없음.
결론은 허용된 3가지(원래 경로 / 생존 범위 / 끊긴 지점)만 기재.
```

*WO-RESTORE-ORIGINAL-PATH-001 — 원래 경로=입력3섹션→facility_profiles(입력표준)→Binding→generator. 부품 전부 생존. 끊긴 곳=①진단입력→profiles 적재(현재 factories 목업에서 유입), ②profiles→generator 바인딩 실행(테스트 1건 외 미배선). 둘 다 기존 설계 내 단계.*
