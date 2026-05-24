# Cursor 작업지시서 — PDF→documents 와이어링 복구

**작성일:** 2026-05-24
**작업 유형:** 기존 구현 연결 복구 (신규 구현 금지)
**예상 소요:** 2~3시간

---

## 절대 규칙

1. **신규 파일 생성 금지**
2. **`services/document_svc.py` 수정 금지** — 이미 완성됨
3. **`documents` 테이블 스키마 변경 금지** — enum, 컬럼 모두 준비됨
4. **PDF 생성 로직 변경 금지** — HTML→PDF 변환 코드 손대지 말 것
5. **Gotenberg 설정 변경 금지**
6. **`routers/report_forms.py` 수정 금지** — 이미 자체 Storage(`form-outputs` 버킷 + `form_submissions.pdf_url`)가 동작함

---

## 현재 상태 (이미 완성된 것)

### services/document_svc.py (수정 금지)
```python
async def register_generated(
    file_bytes: bytes,          # PDF 바이트
    file_name: str,             # 파일명
    mime_type: str,             # "application/pdf"
    company_id: str,            # 회사 ID
    category: str,              # doc_category enum 값
    generated_by: str,          # 생성 라우터명
    generation_params=None,
    factory_id=None,
    linked_table=None,
    linked_id=None,
    title=None,
    **kwargs
) -> Dict[str, Any]:
```

### documents 테이블 (변경 금지)
- **category enum:** `tbm`, `inspection`, `report`, `contract`, `general` 등 13개
- **source enum:** `USER_UPLOAD`, `AUTO_GENERATED`, `MIGRATED`
- **Storage bucket:** `company-docs` (private, 존재)
- **path 규칙:** `{company_id}/{category}/{YYYY-MM}/{uuid}.pdf`

---

## 수정 대상 (4개 파일)

### 1. routers/document_engine.py (최우선 — TBM PDF)
- **엔드포인트:** `POST /document-forms/{doc_id}/generate`
- **엔진:** Gotenberg (async)
- **category:** `"tbm"`
- **linked_table:** `"tbm_meetings"`
- **company_id:** 현재 없음 → `factories` 테이블에서 1회 조회 필요
- **위치:** `generate_document()` 함수, `return Response(...)` 직전

### 2. routers/diagnosis_report.py (진단 리포트)
- **엔진:** Gotenberg (async)
- **category:** `"report"`
- **linked_table:** `"diagnosis_results"`

### 3. routers/diagnosis_proposal.py (제안서)
- **엔진:** Gotenberg (async)
- **category:** `"report"`

### 4. routers/contract_kmong.py (계약서)
- **엔진:** xhtml2pdf (sync 주의)
- **category:** `"contract"`
- **linked_table:** `"contracts"`
- **sync/async 주의:** 엔드포인트가 sync(`def`)이면 `async def`로 변경하거나 `asyncio.run()` 사용

---

## 수정하지 말 것

| 파일 | 이유 |
|------|------|
| `services/document_svc.py` | 이미 완성 |
| `routers/report_forms.py` | 자체 Storage 동작 중 |
| `routers/document_engine_api.py` | 별도 체계 |
| `documents` 테이블 | 스키마 완성 |
| `services/document_engine/` | 엔진 영역 (GPT 도메인) |

---

## 공통 추가 패턴

각 PDF 반환 직전에 아래 코드 추가:

```python
# ── documents 기록 ──
try:
    from services.document_svc import register_generated
    if company_id:  # 이미 조회된 변수 사용
        await register_generated(
            file_bytes=pdf_bytes,
            file_name=filename,
            mime_type="application/pdf",
            company_id=company_id,
            category="{해당 category}",   # tbm / report / contract
            generated_by="{라우터명}",
            factory_id=factory_id,         # 있으면 전달
            linked_table="{테이블명}",
            linked_id=str(linked_id),      # 있으면 전달
            title="{문서 제목}",
        )
except Exception as _doc_err:
    import logging
    logging.getLogger(__name__).warning(
        f"documents 기록 실패 (PDF는 정상 반환): {_doc_err}"
    )
# ── 끝 ──
```

**핵심:** documents 기록 실패가 PDF 반환을 차단하면 안 됨 (try/except 필수)

---

## 테스트

```sql
SELECT id, company_id, factory_id, category, source, file_name,
       storage_path, generated_by, linked_table, linked_id, uploaded_at
FROM documents ORDER BY uploaded_at DESC LIMIT 10;
```

## 작업 브랜치: `dev` (tai-api는 dev 브랜치 사용)
