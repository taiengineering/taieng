# 백로그: xhtml2pdf 잔여 마이그레이션

**발견일**: 2026-04-25  
**우선순위**: 중 (운영 영향 없음, 환경 정리 효과 있음)

---

## 배경

2026-04-20 메모리 기록에는 "xhtml2pdf 완전 제거"라고 적혀 있었으나,
2026-04-25 환경 이전 작업 중 grep 검증으로 **2개 라우터에 xhtml2pdf가 살아있는 것** 확인:

| 파일 | 사용 위치 |
|---|---|
| `routers/report_forms.py` | `_generate_pdf_bytes()` — `pisa.CreatePDF()` 호출 |
| `routers/contract_kmong.py` | `pisa.pisaDocument()` 호출 |

Gotenberg 마이그레이션은 다음만 완료된 상태:
- ✅ `routers/diagnosis_proposal.py` v2.1.0
- ✅ `routers/diagnosis_report.py` v2.0.0
- ❌ `routers/report_forms.py` (서식 PDF)
- ❌ `routers/contract_kmong.py` (계약 PDF)

---

## 영향

### 현재 상태 (마이그레이션 미완료의 영향)

| 항목 | 영향 |
|---|---|
| `requirements.txt` | `xhtml2pdf` 1줄 + 그 의존성 체인 (svglib, rlpycairo, pycairo) |
| `Dockerfile` | `libcairo2-dev`, `pkg-config`, `python3-dev`, `libffi-dev`, `gcc` 시스템 패키지 5개 필요 |
| Railway 빌드 시간 | 시스템 패키지 설치 + pycairo 빌드로 +1~2분 |
| Docker 이미지 크기 | 시스템 패키지로 +50~100MB |
| 로컬 환경 (macOS) | `brew install pkg-config cairo` 필수 (오늘 환경 이전 시 발견) |

### 마이그레이션 완료 시 효과

- requirements.txt에서 xhtml2pdf 제거 가능
- Dockerfile에서 시스템 패키지 5개 제거 가능
- Railway 빌드 속도 개선
- Docker 이미지 크기 감소
- 로컬 환경 구성 단순화 (Cairo 불필요)
- PDF 엔진 통일 (Gotenberg 단일)

---

## 마이그레이션 작업 범위

### routers/report_forms.py
- `_generate_pdf_bytes(html_content)` 함수가 핵심
- 현재: xhtml2pdf로 HTML → PDF 변환
- 변경: Gotenberg HTTP 호출로 변환
- 영향 엔드포인트: `/report-forms/submissions/preview-pdf`, `/report-forms/submissions/{id}/pdf`

### routers/contract_kmong.py
- pisa.pisaDocument 호출 부분 식별 후 Gotenberg로 교체
- 영향 엔드포인트: 계약서 PDF 생성

### 참조 모델
이미 Gotenberg 전환 완료된 `diagnosis_proposal.py` v2.1.0 / `diagnosis_report.py` v2.0.0를 참고:
- Jinja2 템플릿 렌더링 → Gotenberg `/forms/chromium/convert/html` 호출
- `gotenberg.railway.internal:3000` 내부 URL 사용

### 정리 단계
1. report_forms.py Gotenberg 전환 (PR)
2. contract_kmong.py Gotenberg 전환 (PR)
3. 양쪽 라우터 검증 (실제 PDF 생성 테스트)
4. requirements.txt에서 xhtml2pdf 제거
5. Dockerfile 시스템 패키지 정리
6. Railway 재배포 + 회귀 테스트

---

## 우선순위 판단

**중간 우선순위.** 운영에는 영향 없으므로 다음 작업과 충돌 안 함:
- Play Console 출시 준비
- Capacitor 하이브리드 앱
- PWA P0/P1 잔여 마무리

PWA 출시 후 안정화 단계에서 진행 권장. 또는 다른 라우터 리팩토링 작업과 묶어서 진행.

---

**작성**: Claude (기획창)  
**발견자**: Cursor (xhtml2pdf grep 검증 중)  
**관련 작업**: `docs/WORK_ORDER_20260425_icloud_to_desktop_migration.md`
