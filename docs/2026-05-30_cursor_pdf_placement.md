# TAI Safe 서비스 소개서 PDF 배치 — Cursor 작업지시서

> 작성일: 2026-05-30
> 대상: taiengineering/taieng (nexas/)
> PDF: `TAI_Safe_Service.pdf` (10페이지)

---

## 1. PDF 파일 배치

PDF를 `nexas/assets/pdf/TAI_Safe_Service.pdf`에 저장.

```bash
mkdir -p nexas/assets/pdf
cp TAI_Safe_Service.pdf nexas/assets/pdf/TAI_Safe_Service.pdf
```

접근 URL: `https://taieng.co.kr/assets/pdf/TAI_Safe_Service.pdf`

---

## 2. 무료 법령진단 결과 페이지 하단

### 대상 파일
- `nexas/free-diagnosis-result.html`
- `nexas/paid-diagnosis-result.html`
- `nexas/sample-construction.html`
- `nexas/sample-manufacturing.html`
- `nexas/sample-facility.html`

### 추가 위치

기존 CTA 영역 (`saas-section` 또는 `paid-cta`) **아래**, 법적 면책(`legal-disclaimer`) **위에** 삽입:

```html
<!-- 서비스 소개서 CTA -->
<div style="border-top:1px solid #e2e8f0;margin-top:40px;padding:32px 20px;text-align:center;">
  <p style="font-size:1rem;font-weight:700;color:#0f172a;margin-bottom:6px;">더 자세히 알고 싶으신가요?</p>
  <p style="font-size:.88rem;color:#64748b;margin-bottom:16px;">
    TAI Safe가 법령을 업무로 바꾸고, 실행을 증빙으로 연결하는 과정을 소개합니다.
  </p>
  <a href="/assets/pdf/TAI_Safe_Service.pdf" target="_blank" rel="noopener"
     style="display:inline-block;padding:12px 28px;border-radius:8px;background:#0f172a;color:#fff;font-size:.9rem;font-weight:700;text-decoration:none;">
    TAI Safe 서비스 소개서 보기
  </a>
</div>
```

---

## 3. 상담 신청 완료 페이지

### 대상 파일 확인

상담 신청 완료 페이지가 존재하는지 확인:
- `nexas/fix-request.html` 또는 유사 파일에서 접수 완료 메시지 영역 찾기
- 또는 접수 완료 후 보여주는 alert/toast 영역

### 추가 내용

접수 완료 메시지 하단에:

```html
<div style="margin-top:20px;text-align:center;">
  <p style="font-size:.85rem;color:#64748b;margin-bottom:10px;">상담 검토를 기다리는 동안 TAI Safe를 먼저 살펴보세요.</p>
  <a href="/assets/pdf/TAI_Safe_Service.pdf" target="_blank" rel="noopener"
     style="color:#1A5FD4;font-weight:700;font-size:.85rem;text-decoration:none;">
    서비스 소개서 보기 →
  </a>
</div>
```

---

## 금지사항

- 상단 메뉴 추가 금지
- 메인페이지 배너 노출 금지
- 팝업 노출 금지
- 첫 화면 CTA 배치 금지
- 무료 법령진단 CTA 옆 배치 금지
- 서비스 소개서 전용 랜딩페이지 생성 금지

## 원칙

사용자의 첫 행동은 무료 법령진단이어야 한다.
서비스 소개서는 관심 고객이 검토 단계에서 확인하는 보조 자료로 사용한다.
소개서보다 진단 경험이 우선이다.
