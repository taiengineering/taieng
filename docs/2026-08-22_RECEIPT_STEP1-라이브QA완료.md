# STEP1 라이브 QA 완료 리시트 — 상태표 갱신 · 2026-08-22

> 이번 세션 STEP1 라이브 배치 마감. 코드+배포+라이브 3단 통과분을 **완료로 확정**한다.
> 근거: 운영자 라이브 QA(산업·건설 데모 계정) + 커밋 직독 + Railway/CF 배포 SUCCESS.

---

## 1. 이번 세션 닫힘 (완료 3단)

| # | 결함 | 반영 | 검증 |
|---|---|---|---|
| **§60** | 건설공정 계획일 저장 + 법령진단버튼 제거 | BE `5fa2a5c`(schemas alias)·FE `1aad9061` | 직독(AliasChoices)·라이브 |
| **⑤** | TBM 기록하기 404 → `/tbm-create` 신설 | FE | 라이브 |
| **§17** | 서식 페이지 → 메뉴명 「서식관리」 | FE | 라이브 |
| **§59** | 현장 주소 → 행안부 juso 검색·선택 | FE + SiteCreate alias | 라이브 |
| **§70** | 상태 영문→한글 표시 | `fab169b5`(statusLabels.ts) | 직독·라이브 |
| **§24·§68** | 담당자 드롭다운 빈 목록 (데모제외 오발동) | `6e0b4ef`(users.py v2.3.1) | 직독·배포 SUCCESS·라이브 |
| **㉑** | 마감일 저장 | 서버 v1.2.5 + 테스트데이터 | 라이브 |
| **§65** | 완료 카운트 | C-2 | 라이브 |
| ⑦·㉛·⑬ | 퇴직저장·설비통계·사업자등록증 | (기존) | 라이브(1차) |

## 2. C-2 값어휘 (서버·DB 완결)
§65·㊸·㊹·⑧·⑨ — PR#179(`8138059`) + DB 정규화(SCHEDULED→scheduled·ACTIVE→IN_PROGRESS·PASS→NORMAL) 백필 0. status_vocab 헬퍼·17tests·배포 SUCCESS.

## 3. 근본원인 기록 (재발방지)
- **§60**: 화면 `planned_start_date`/`is_hazardous`/`memo` ↔ DB `planned_start`/`is_high_risk`/`notes` 불일치 → AliasChoices로 양쪽 수용.
- **§24/§68**: `GET /users?factory_id=` 가 company_id 없이 호출 → v2.2.0 데모제외(`if not company_id`)가 오발동 → is_demo 회사 사용자 전부 제외. `and not factory_id` 추가로 해소. (실회사 무영향, 데모 QA 전용)
- **대시보드 할일목록**: work_schedules 직접 조회(배정 불요). 첫 0건은 건설 계정 데이터 부재였음.

## 4. 남은 것 (다음 배치)
- **STEP4 vue3**: ㉝(담당자 값출처 factory_contacts→users)·㉘(다음회차 문구)·§52(문의 배선)·§34(레거시)·§71(유령호출)
- **C-1 신설**: ⑱ 서식 PDF · tai-files/company-docs 버킷 · ㉗㊱64 보류
- **잔여 라이브 ◐**: §73·§46(API)·⑲ 등
- **부분**: §62 inspector_name·§63 ②③
- **D**: §66(weather debug 재현)
- **파킹(GPT)**: §57·⑫

## 5. 운영 메모
- 테스트 데이터: `[테스트]` work_schedules 6건(산업 3·건설 3) 데모 계정에 유지 중. 데모 시연에 활용 가능, 정리 시 description LIKE '[테스트]%'로 삭제.

---
*STEP1 라이브 배치 = 코드측 종료. danger/warn 삭제는 헬프센터가 위 완료분에 반영.*
