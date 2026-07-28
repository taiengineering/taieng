---

class: plans
type: WORKORDER
scope: ops
project: tai-admin-ops
title: WO-9 파일·자산 통합뷰
version: 1
status: ACTIVE
owner: taiwang
---

# WO-9 — 파일·자산 통합뷰 (읽기 전용, 경량)

- **작성일:** 2026-07-28
- **Goal:** G-ms4je4z3-33eada
- **상위:** WORKPLAN §4 P1 WO-9
- **오브젝트:** v_files_unified 뷰(신설) + company 파일 조회 엔드포인트
- **닫는 시나리오:** S9(고객별 파일 통합 조회)

---

## 1. 현황 (실측)

파일 테이블이 여러 곳에 흩어짐. 격리 자산(legal_engine/document_engine의 document_schema·runtime_document 계열)은 제외. 실제 고객 파일 후보:

| 테이블 | company 연결 | 성격 | 건수(목업) |
|---|---|---|---|
| `documents` | company_id 직접 | **완전한 통합 스키마**(category/source/storage_path/deleted_at/retention) | 0 |
| `company_files` | company_id 직접 | 회사 업로드(계약서 등) | 0 |
| `generated_document` | factory_id→factories.company_id | 발급 문서 | 42 |
| `education_files` | history_id 경유(간접) | 교육 파일 | 0 |
| `attachments` | table_name+record_id(다형성) | 범용 첨부 | 0 |

**핵심:** `documents`가 이미 완전한 통합 스키마 = 설계 정본. 실데이터는 아직 목업뿐(실고객 0). 관계: 회사(1):회원(N), users.company_id. 결제=회사 단위 → 파일도 company_id 축으로 통합.

## 2. 결정 — 경량 읽기 통합뷰 (과잉 설계 회피)

실파일이 없으므로 무거운 적재·물리 마이그레이션 없이 **읽기 전용 뷰**만. 실파일 쌓이면 확장.

- **`v_files_unified`**: documents + company_files + generated_document(factory→company 조인)를 company_id 기준 UNION. 공통 컬럼으로 정규화: `company_id, source, file_name, file_ref(url/path), category, status, created_at, is_active`.
- education_files·attachments는 간접/다형성 연결이라 이번 제외(실사용 시 후속).

## 3. 엔드포인트

- `GET /companies/{company_id}/files` — 해당 회사의 통합 파일 목록(v_files_unified 조회). source 필터·페이지네이션.

## 4. 완료 판정 (IMPLEMENTED)

- v_files_unified 뷰 생성(3소스 UNION, company_id 정규화).
- files 조회 엔드포인트, saas_core 등록.
- `/health` 200, 배포 SUCCESS. 목업 표본(generated_document 42→factory 조인)으로 뷰 동작 확인.

## 5. 산출물

1. 마이그레이션: v_files_unified 뷰
2. `routers/company_files_unified.py` 또는 customer360에 통합
3. router_registry 등록
