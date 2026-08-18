# 결정요청 — §62 건설점검 쓰기측 필드 유실 + inspector 처리

> 2026-08-18 · LEDGER §62[높음] · 대상 `tai-api` schemas/construction.py · construction_workflow_router.py · 화면 construction-inspection-list
> 실측 기반. **표시(read)분은 이미 배포**(`4fb9706`: inspection_datetime·defect_details·corrective_due 별칭 병기).
> 남은 것: **쓰기(create)측 필드명 불일치 4건 + inspector_name↔id 1건**.

## 실측 확정
`InspectionCreate`(schemas/construction.py)는 **DB 컬럼명**을 필드로 씀:
`inspection_date · inspector_id · defect_items · corrective_deadline · photo_urls`.
화면은 **다른 이름**을 보냄: `inspection_datetime · inspector_name · defect_details · corrective_due · photo_url`.
Pydantic v2 는 정의 안 된 필드를 무시 → 쓰기 시 5개 탈락.
(라이브 8건은 시드 삽입이라 inspection_date 는 정상. 폼 생성 경로에서 탈락이 재현됨.)
또한 `inspection_date` 는 **NOT NULL** 인데 `prepare_inspection_payload` 가 기본값을 넣지 않음 →
폼이 `inspection_datetime` 만 보내면 **INSERT 500**(NOT NULL 위반) 위험.

## 결정 A — 쓰기측 4개 별칭 (깨끗, 서버, 승인 시 즉시 처리 가능)
`InspectionCreate` 에 Pydantic `AliasChoices` + `populate_by_name=True` 로 화면 이름도 받게 함:
- `inspection_date` ← `inspection_datetime`
- `defect_items` ← `defect_details`
- `corrective_deadline` ← `corrective_due`
- `photo_urls` ← `photo_url` (**단수 문자열 → 배열 강제** validator 필요)

→ 승인(㉮)하면 schemas/construction.py 한 파일에서 처리(엔진·다른 스키마 불변). 폼 생성 시 5개 중 4개가 저장됨 + NOT NULL 500 회피.
**대안(㉯)**: 화면이 DB 이름으로 보내도록 프런트 수정(Cursor). 서버 계약은 더 깨끗하나 배포 2곳.

## 결정 B — inspector 처리 (제품 결정 필요, 서버만으론 불가)
DB 는 `inspector_id`(uuid)만 있고 화면은 `inspector_name`(이름)을 보냄. 이름↔uuid 라 별칭 불가.
셋 중 택1:
- **B-1** `construction_inspections` 에 `inspector_name`(text) 컬럼 추가(DDL) → 이름 그대로 저장·표시. **가장 단순, 법정기록에 점검자명 보존**. (권장)
- **B-2** 화면을 사용자 드롭다운으로 바꿔 `inspector_id` 를 보냄(Cursor). 정합성 최고이나 화면 변경 + 점검자가 시스템 사용자여야 함.
- **B-3** 서버가 이름→id 해석(users/workers 이름 매칭). 동명이인·미등록자에 취약 → 비권장.

## 요청
1. **A 는 ㉮(서버 별칭) / ㉯(프런트) 중?** — ㉮ 면 즉시 처리.
2. **B 는 B-1 / B-2 / B-3 중?** — B-1 이면 DDL(`alter table construction_inspections add column inspector_name text`) 후 A 에 inspector_name 별칭 추가로 마무리.

## 이미 처리된 표시분 (배포됨 4fb9706)
목록·상세 응답에 `inspection_datetime`·`defect_details`·`corrective_due` 별칭 병기 → 목록 날짜가 실제 점검일로 표시, 상세 결함·시정기한 노출. inspector 표시는 B 결정 후.
