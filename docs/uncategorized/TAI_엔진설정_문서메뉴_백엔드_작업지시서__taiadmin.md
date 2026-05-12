# TAI Safe 엔진설정 > 문서 메뉴 — 백엔드 작업지시서

> 작성일: 2026-04-02  
> 대상: Cursor (백엔드 창)  
> 기술스택: FastAPI / Python / Supabase PostgreSQL

---

## 0. 작업 전 필수 확인

```
1. 기존 참고 라우터: legal_engine.py, price_setting.py
2. Railway 자동 배포 (main 브랜치 push 시)
3. api.taieng.co.kr 에서 배포 확인
4. DB: Supabase xntdkrjhgcscmqctdzyo
```

---

## 1. DB 마이그레이션 (Supabase에서 직접 실행)

### 1.1 form_templates 테이블 컬럼 추가

```sql
ALTER TABLE form_templates
  ADD COLUMN IF NOT EXISTS form_type        varchar(20) DEFAULT 'LEGAL',
  ADD COLUMN IF NOT EXISTS use_case         text,
  ADD COLUMN IF NOT EXISTS submit_agency    varchar(100),
  ADD COLUMN IF NOT EXISTS submit_method    varchar(50) DEFAULT 'KEEP',
  ADD COLUMN IF NOT EXISTS submit_url       text,
  ADD COLUMN IF NOT EXISTS retention_years  integer,
  ADD COLUMN IF NOT EXISTS penalty_summary  text,
  ADD COLUMN IF NOT EXISTS required_fields  jsonb,
  ADD COLUMN IF NOT EXISTS template_fields  jsonb,
  ADD COLUMN IF NOT EXISTS sector           varchar(20) DEFAULT 'BUILDING',
  ADD COLUMN IF NOT EXISTS sort_order       integer DEFAULT 0,
  ADD COLUMN IF NOT EXISTS updated_at       timestamptz DEFAULT now();
```

### 1.2 document_form_master 테이블 생성

```sql
CREATE TABLE IF NOT EXISTS document_form_master (
  id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  form_code         varchar(50) UNIQUE NOT NULL,
  form_name         varchar(200) NOT NULL,
  form_name_short   varchar(100),
  form_type         varchar(20) NOT NULL DEFAULT 'STANDARD',
  form_category     varchar(30),
  obligation_type   varchar(20),
  law_name          varchar(200),
  law_article       varchar(100),
  legal_basis       text,
  use_case          text,
  trigger_event     text,
  submit_agency     varchar(100),
  submit_method     varchar(50) DEFAULT 'KEEP',
  submit_url        text,
  submit_timing     varchar(100),
  retention_years   integer,
  retention_start   varchar(50) DEFAULT 'WRITE_DATE',
  penalty_summary   text,
  required_fields   jsonb,
  template_fields   jsonb,
  hwp_url           text,
  pdf_url           text,
  excel_url         text,
  sector            varchar(20) DEFAULT 'BUILDING',
  sort_order        integer DEFAULT 0,
  is_active         boolean DEFAULT true,
  created_at        timestamptz DEFAULT now(),
  updated_at        timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_doc_form_type ON document_form_master(form_type);
CREATE INDEX IF NOT EXISTS idx_doc_form_sector ON document_form_master(sector);
CREATE INDEX IF NOT EXISTS idx_doc_obligation_type ON document_form_master(obligation_type);
```

### 1.3 document_form_master 초기 데이터 INSERT

```sql
-- TAI표준서식 10종 초기 데이터
INSERT INTO document_form_master (
  form_code, form_name, form_name_short,
  form_type, form_category, obligation_type,
  law_name, law_article, legal_basis,
  use_case, trigger_event,
  submit_agency, submit_method, submit_timing,
  retention_years, retention_start,
  penalty_summary, required_fields,
  sector, sort_order, is_active
) VALUES
(
  'STD-RISK-001', '위험성평가 결과서', '위험성평가',
  'STANDARD', 'DOCUMENT', 'DOCUMENT',
  '산업안전보건법 시행규칙', '제37조제2항',
  '사업주는 위험성평가 실시내용 및 결과를 3년간 보존해야 한다.',
  '위험성평가를 실시한 후 그 결과와 조치사항을 기록할 때',
  '위험성평가 실시',
  '내부 보관', 'KEEP', '위험성평가 완료 즉시',
  3, 'WRITE_DATE',
  '미보존 시 과태료 500만원 이하',
  '["위험성평가 대상 유해·위험요인","위험성 결정의 내용","위험성 결정에 따른 조치 내용","평가 실시일 및 실시자","근로자 의견 청취 내용"]'::jsonb,
  'BUILDING', 1, true
),
(
  'STD-EDU-001', '안전보건교육 실시기록부', '교육실시기록',
  'STANDARD', 'DOCUMENT', 'DOCUMENT',
  '산업안전보건법 시행규칙', '제166조',
  '사업주는 안전보건교육 실시기록을 3년간 보존하여야 한다.',
  '근로자 안전보건교육(정기·채용 시·작업변경 시·특별교육)을 실시한 후',
  '안전보건교육 실시',
  '내부 보관', 'KEEP', '교육 실시 즉시',
  3, 'WRITE_DATE',
  '미보존 시 과태료 500만원 이하',
  '["교육 실시일시","교육 내용","교육 대상자 명단 및 서명","교육 시간","교육 실시자(강사)명"]'::jsonb,
  'BUILDING', 2, true
),
(
  'STD-MTG-001', '안전보건위원회 회의록', '위원회회의록',
  'STANDARD', 'DOCUMENT', 'DOCUMENT',
  '산업안전보건법', '제24조제3항',
  '산업안전보건위원회는 회의 결과를 회의록으로 작성하여 2년간 보존하여야 한다.',
  '산업안전보건위원회 회의 개최 후',
  '안전보건위원회 회의',
  '내부 보관', 'KEEP', '회의 개최 즉시',
  2, 'WRITE_DATE',
  '미보존 시 과태료 500만원 이하',
  '["개최 일시 및 장소","출석위원 명단","심의 내용 및 의결·결정 사항","그 밖의 토의사항","위원 서명"]'::jsonb,
  'BUILDING', 3, true
),
(
  'STD-ACC-001', '산업재해 발생 원인 기록서', '재해원인기록',
  'STANDARD', 'DOCUMENT', 'DOCUMENT',
  '산업안전보건법', '제57조제2항',
  '사업주는 산업재해의 발생 원인 등을 기록하여 보존하여야 한다.',
  '산업재해가 발생하였을 때 (산업재해조사표 작성과 별도)',
  '산업재해 발생',
  '내부 보관', 'KEEP', '재해 발생 즉시',
  3, 'EVENT_DATE',
  '미보존 시 과태료 500만원 이하',
  '["재해 발생 일시 및 장소","재해자 인적사항","재해 발생 원인","피해 규모","재발방지 조치사항","작성자 및 작성일"]'::jsonb,
  'BUILDING', 4, true
),
(
  'STD-COST-001', '안전관리비 사용명세서', '안전관리비명세',
  'STANDARD', 'DOCUMENT', 'DOCUMENT',
  '산업안전보건법', '제72조제3항',
  '건설공사도급인은 산업안전보건관리비 사용명세서를 작성하여 보존하여야 한다.',
  '산업안전보건관리비를 사용한 후 사용 내역을 기록할 때',
  '안전관리비 집행',
  '내부 보관', 'KEEP', '공사 완료 후',
  3, 'WRITE_DATE',
  '미보존 시 과태료 500만원 이하',
  '["사용 항목","사용 금액","사용 일자","사용처","증빙 서류 번호","잔액"]'::jsonb,
  'BUILDING', 5, true
),
(
  'STD-ELEC-001', '전기설비 점검일지', '전기점검일지',
  'STANDARD', 'DOCUMENT', 'DOCUMENT',
  '전기안전관리법 시행규칙', '제24조',
  '전기안전관리자는 전기설비 안전관리 사항을 기록하여 4년간 보존해야 한다.',
  '전기설비 정기점검 또는 일상점검 실시 후',
  '전기설비 점검',
  '내부 보관', 'KEEP', '점검 실시 즉시',
  4, 'WRITE_DATE',
  '미보존 시 과태료 300만원 이하',
  '["점검 일시","점검 설비명","점검 항목 및 결과","이상 유무","조치사항","점검자 서명"]'::jsonb,
  'BUILDING', 6, true
),
(
  'STD-ENV-001', '작업환경측정 결과 보관대장', '작업환경측정',
  'STANDARD', 'DOCUMENT', 'DOCUMENT',
  '작업환경측정 및 정도관리 등에 관한 고시', '제30조',
  '작업환경측정 결과 및 관련 서류를 5년간 보존해야 한다.',
  '작업환경측정기관으로부터 측정 결과를 받았을 때',
  '작업환경측정 결과 수령',
  '내부 보관', 'KEEP', '결과 수령 즉시',
  5, 'EVENT_DATE',
  '미보존 시 과태료 300만원 이하',
  '["측정 실시일","측정 대상 작업장","측정 항목(유해인자)","측정 결과 수치","노출기준 초과 여부","개선 조치사항"]'::jsonb,
  'BUILDING', 7, true
),
(
  'STD-HEALTH-001', '건강진단 결과 보관대장', '건강진단보관',
  'STANDARD', 'DOCUMENT', 'DOCUMENT',
  '산업안전보건법 시행규칙', '제241조제2항',
  '사업주는 근로자 건강진단 결과표를 5년간 보존해야 한다.',
  '근로자 건강진단 결과표를 수령하였을 때',
  '건강진단 결과 수령',
  '내부 보관', 'KEEP', '결과 수령 즉시',
  5, 'EVENT_DATE',
  '미보존 시 과태료 500만원 이하',
  '["수검자 성명","건강진단 종류","실시일","결과 판정","사후관리 내용","보관 시작일"]'::jsonb,
  'BUILDING', 8, true
),
(
  'STD-FIRE-001', '소방시설 자체점검 결과서', '소방자체점검',
  'STANDARD', 'DOCUMENT', 'DOCUMENT',
  '화재의 예방 및 안전관리에 관한 법률', '제43조',
  '소방시설 자체점검 결과를 2년간 보관하여야 한다.',
  '소방시설 자체점검 실시 후 (작동기능점검 또는 종합정밀점검)',
  '소방시설 자체점검',
  '내부 보관', 'KEEP', '점검 완료 후 즉시',
  2, 'WRITE_DATE',
  '미보관 시 과태료 200만원 이하',
  '["점검 일시","점검 종류(작동/종합)","점검 대상 소방시설 목록","점검 결과(정상/불량)","불량 내용 및 조치사항","점검자 서명"]'::jsonb,
  'BUILDING', 9, true
),
(
  'STD-INSPECT-001', '안전점검 결과서', '안전점검결과',
  'STANDARD', 'DOCUMENT', 'DOCUMENT',
  '다중이용업소의 안전관리에 관한 특별법', '제13조제1항',
  '다중이용업주는 안전시설 정기점검결과서를 1년간 보관하여야 한다.',
  '안전시설 정기점검 실시 후',
  '안전시설 정기점검',
  '내부 보관', 'KEEP', '점검 완료 즉시',
  1, 'WRITE_DATE',
  '미보관 시 과태료 200만원 이하',
  '["점검 일시","점검 대상 시설","점검 항목","점검 결과","조치 필요사항","점검자 서명"]'::jsonb,
  'BUILDING', 10, true
);
```

---

## 2. 라우터 파일 생성

**파일명:** `app/routers/engine_document.py`

### 2.1 엔드포인트 목록

| Method | URL | 설명 |
|--------|-----|------|
| GET | `/engine/forms` | 서식 목록 조회 |
| GET | `/engine/forms/{form_code}` | 서식 상세 조회 |
| GET | `/engine/forms/summary` | 보관현황 요약 |
| PATCH | `/engine/forms/{form_code}` | 서식 수정 (관리자) |

### 2.2 전체 코드

```python
from fastapi import APIRouter, Query, HTTPException
from app.database import get_supabase
from typing import Optional

router = APIRouter(prefix="/engine", tags=["engine-document"])


@router.get("/forms")
async def get_forms(
    form_type: Optional[str] = Query(None, description="LEGAL / STANDARD / FREE"),
    form_category: Optional[str] = Query(None),
    obligation_type: Optional[str] = Query(None),
    sector: str = Query("BUILDING"),
    is_active: bool = Query(True)
):
    """
    서식 목록 조회
    - form_type: LEGAL(법정서식) / STANDARD(TAI표준서식) / FREE(자유서식가이드)
    - form_category: REPORT / DOCUMENT / NOTIFY / APPOINT / INSPECT
    """
    supabase = get_supabase()

    # form_type에 따라 쿼리 테이블 분기
    if form_type == 'LEGAL':
        # form_templates 테이블 조회
        query = supabase.table("form_templates") \
            .select("*") \
            .eq("is_active", is_active)
        if sector:
            query = query.eq("sector", sector)
        result = query.order("sort_order").execute()
    else:
        # document_form_master 테이블 조회
        query = supabase.table("document_form_master") \
            .select("*") \
            .eq("is_active", is_active)
        if form_type:
            query = query.eq("form_type", form_type)
        if form_category:
            query = query.eq("form_category", form_category)
        if obligation_type:
            query = query.eq("obligation_type", obligation_type)
        if sector:
            query = query.eq("sector", sector)
        result = query.order("sort_order").execute()

    return {
        "success": True,
        "data": result.data,
        "total": len(result.data)
    }


@router.get("/forms/summary")
async def get_forms_summary(sector: str = Query("BUILDING")):
    """
    보관현황 요약 카드용 데이터
    """
    supabase = get_supabase()

    # document_form_master 기준 통계
    std = supabase.table("document_form_master") \
        .select("id, form_type, obligation_type") \
        .eq("is_active", True) \
        .eq("sector", sector) \
        .execute()

    # form_templates 기준 통계
    legal = supabase.table("form_templates") \
        .select("id, form_type") \
        .eq("is_active", True) \
        .execute()

    total_legal = len(legal.data)
    total_standard = len([x for x in std.data if x['form_type'] == 'STANDARD'])
    total_free = len([x for x in std.data if x['form_type'] == 'FREE'])

    return {
        "success": True,
        "data": {
            "total_legal": total_legal,
            "total_standard": total_standard,
            "total_free": total_free,
            "total_document_obligations": 52,
            "forms_stored": 0,       # Phase 3에서 document_storage 연동
            "expiring_soon": 0,       # Phase 3
            "expired": 0              # Phase 3
        }
    }


@router.get("/forms/{form_code}")
async def get_form_detail(form_code: str):
    """
    서식 상세 조회
    - form_code 패턴으로 테이블 자동 분기:
      OSHACT-FORM-* → form_templates
      STD-* / DOC-* → document_form_master
    """
    supabase = get_supabase()

    # form_templates 우선 조회
    result = supabase.table("form_templates") \
        .select("*") \
        .eq("form_code", form_code) \
        .execute()

    if result.data:
        return {"success": True, "data": result.data[0], "source": "form_templates"}

    # document_form_master 조회
    result = supabase.table("document_form_master") \
        .select("*") \
        .eq("form_code", form_code) \
        .execute()

    if result.data:
        return {"success": True, "data": result.data[0], "source": "document_form_master"}

    raise HTTPException(status_code=404, detail=f"Form not found: {form_code}")


@router.patch("/forms/{form_code}")
async def update_form(form_code: str, body: dict):
    """
    서식 정보 수정 (관리자용)
    """
    supabase = get_supabase()

    # 수정 불가 필드 제거
    body.pop("id", None)
    body.pop("form_code", None)
    body.pop("created_at", None)
    body["updated_at"] = "now()"

    # form_templates 우선 시도
    check = supabase.table("form_templates") \
        .select("id") \
        .eq("form_code", form_code) \
        .execute()

    if check.data:
        result = supabase.table("form_templates") \
            .update(body) \
            .eq("form_code", form_code) \
            .execute()
    else:
        result = supabase.table("document_form_master") \
            .update(body) \
            .eq("form_code", form_code) \
            .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Form not found")

    return {"success": True, "data": result.data[0]}
```

---

## 3. main.py 라우터 등록

```python
# app/main.py 에 추가
from app.routers import engine_document
app.include_router(engine_document.router)
```

---

## 4. 배포 확인

```bash
# Railway 자동 배포 후 확인
curl https://api.taieng.co.kr/engine/forms?form_type=LEGAL
curl https://api.taieng.co.kr/engine/forms?form_type=STANDARD
curl https://api.taieng.co.kr/engine/forms/summary
curl https://api.taieng.co.kr/engine/forms/STD-RISK-001
```

---

## 5. 완성 기준 체크리스트

```
□ document_form_master 테이블 생성
□ form_templates 컬럼 추가
□ 초기 데이터 10건 INSERT (TAI표준서식)
□ engine_document.py 라우터 생성
□ GET /engine/forms (form_type 파라미터 정상 동작)
□ GET /engine/forms/summary 정상 응답
□ GET /engine/forms/{form_code} 정상 응답
□ PATCH /engine/forms/{form_code} 정상 동작
□ main.py 라우터 등록
□ Railway 배포 완료
□ 전체 엔드포인트 curl 테스트 통과
```

---

## 6. 응답 예시

```json
// GET /engine/forms?form_type=STANDARD
{
  "success": true,
  "data": [
    {
      "form_code": "STD-RISK-001",
      "form_name": "위험성평가 결과서",
      "form_type": "STANDARD",
      "form_category": "DOCUMENT",
      "law_name": "산업안전보건법 시행규칙",
      "law_article": "제37조제2항",
      "use_case": "위험성평가를 실시한 후 그 결과와 조치사항을 기록할 때",
      "submit_agency": "내부 보관",
      "submit_method": "KEEP",
      "retention_years": 3,
      "penalty_summary": "미보존 시 과태료 500만원 이하",
      "required_fields": [
        "위험성평가 대상 유해·위험요인",
        "위험성 결정의 내용",
        "위험성 결정에 따른 조치 내용",
        "평가 실시일 및 실시자",
        "근로자 의견 청취 내용"
      ],
      "sort_order": 1
    }
  ],
  "total": 10
}
```
