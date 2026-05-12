# TAI 작업지시서 — 법령진단 결제 흐름 수정 (프론트)

> 작성일: 2026-04-01
> 대상: tai-admin (tadmin)

---

## 배경

```
기존 diagnosis-purchase.html:
  POST /diagnosis/purchases → 즉시 카드결제 처리 (잘못된 B2C 방식)

수정 방향 (B2B 방식):
  견적 신청 → 관리자 확인 → 계약 → 서비스 이용
  POST /diagnosis/request-quote → 견적 접수 안내 화면
```

---

## 작업 1: diagnosis-purchase.html 전면 수정

### 변경 전 (삭제할 내용)
```
결제 수단 선택 (카드/계좌이체/세금계산서)
POST /diagnosis/purchases 호출
has_access=true 즉시 반환
```

### 변경 후 (새 화면)
```
┌─────────────────────────────────────────────────┐
│  📋 법령진단 2단계 신청                           │
│  제조·공장 / 공정진단                             │
│  49,000원 (VAT 별도)                             │
├─────────────────────────────────────────────────┤
│  📌 신청 안내                                     │
│                                                 │
│  ① 신청서 제출 (지금)                             │
│  ② TAI 담당자 확인 (1 영업일 이내)               │
│  ③ 견적서 이메일 발송                             │
│  ④ 결제 완료 후 즉시 이용 가능                    │
│                                                 │
├─────────────────────────────────────────────────┤
│  담당자 정보                                      │
│  이름 *  [            ]                          │
│  연락처 * [            ]                          │
│  이메일  [            ]                          │
│  문의사항 [            ]                          │
├─────────────────────────────────────────────────┤
│  [취소]          [신청하기]                        │
└─────────────────────────────────────────────────┘
```

### HTML/JS 핵심 로직

```javascript
// URL 파라미터에서 sector, step, factory_id, diagnosis_id 읽기
const params = new URLSearchParams(location.search);
const sector = params.get('sector');       // MANUFACTURING
const step   = parseInt(params.get('step')); // 2
const factoryId = params.get('factory_id');
const diagnosisId = params.get('id');       // 진단 결과 ID

// 가격 표시
const SECTOR_PRICES = {
  BUILDING:         { s2: 29000, s3: 59000, report: 99000 },
  MANUFACTURING:    { s2: 49000, s3: 99000, report: 249000 },
  SPECIAL_FACILITY: { s2: 49000, s3: 99000, report: 199000 },
  CONSTRUCTION:     { s2: 79000, s3: 149000, report: 399000 },
};
const price = SECTOR_PRICES[sector][`s${step}`];

// 신청 제출
async function submitRequest() {
  const body = {
    factory_id:    factoryId,
    sector:        sector,
    step:          step,
    contact_name:  document.getElementById('contact-name').value.trim(),
    contact_phone: document.getElementById('contact-phone').value.trim(),
    contact_email: document.getElementById('contact-email').value.trim(),
    memo:          document.getElementById('contact-memo').value.trim(),
  };

  if (!body.contact_name || !body.contact_phone) {
    showToast('warning', '담당자 이름과 연락처를 입력하세요.');
    return;
  }

  const res = await apiCall('POST', '/diagnosis/request-quote', body);

  // 완료 화면으로 전환
  document.getElementById('form-section').style.display = 'none';
  document.getElementById('complete-section').style.display = '';
}
```

### 신청 완료 화면

```html
<div id="complete-section" style="display:none" class="text-center py-5">
  <div class="fs-1 mb-3">✅</div>
  <h4 class="mb-2">신청이 접수되었습니다</h4>
  <p class="text-muted mb-1">담당자가 1 영업일 이내 연락드립니다.</p>
  <p class="text-muted mb-4">견적서를 이메일로 발송해드립니다.</p>
  <div class="d-flex gap-2 justify-content-center">
    <a href="my-diagnosis.html" class="btn btn-outline-secondary">
      진단 내역 보기
    </a>
    <a href="diagnosis-step1.html" class="btn btn-primary">
      다른 진단 신청
    </a>
  </div>
</div>
```

---

## 작업 2: diagnosis-result.html 잠금 배너 수정

### 변경 전 잠금 배너
```javascript
// 기존: goToPurchase() → diagnosis-purchase.html?...
function goToPurchase(step) {
  location.href = 'diagnosis-purchase.html?step=' + step + '&sector=' + sector;
}
```

### 변경 후 (URL 파라미터 추가)
```javascript
function goToPurchase(step) {
  const diagId = new URLSearchParams(location.search).get('id');
  location.href = `diagnosis-purchase.html` +
    `?sector=${currentSector}` +
    `&step=${step}` +
    `&factory_id=${currentFactoryId}` +
    `&id=${diagId}`;
}
```

### 잠금 배너 문구 수정
```html
<!-- 기존: "단건 구매하기" -->
<!-- 수정: "신청하기" -->
<button class="btn btn-primary btn-lg px-5" onclick="goToPurchase(2)">
  <i class="ti tabler-file-invoice me-2"></i>2단계 진단 신청하기
</button>

<!-- 안내 문구 추가 -->
<p class="opacity-75 small mt-3">
  신청 후 담당자 확인 → 견적 발송 → 결제 완료 시 즉시 이용 가능합니다.
</p>
```

---

## 작업 3: diagnosis-step2.html / step3.html 잠금 배너 동일 수정

```javascript
// 두 파일 모두 동일하게 수정
// "단건 구매하기" → "신청하기"
// goToPurchase() 함수 파라미터 추가 (factory_id 포함)
function goToPurchase(step) {
  const factoryId = localStorage.getItem('current_factory_id');
  const sector = localStorage.getItem('current_diagnosis_sector');
  location.href = `diagnosis-purchase.html?sector=${sector}&step=${step}&factory_id=${factoryId}`;
}
```

---

## 완료 체크리스트

```
□ diagnosis-purchase.html 전면 수정
  □ 결제 수단 선택 화면 → 견적 신청 폼으로 교체
  □ POST /diagnosis/request-quote 연동
  □ 신청 완료 화면 구현

□ diagnosis-result.html 잠금 배너 수정
  □ goToPurchase() URL 파라미터에 factory_id 추가
  □ "단건 구매" → "신청하기" 문구 변경
  □ 신청 흐름 안내 문구 추가

□ diagnosis-step2.html 잠금 배너 동일 수정
□ diagnosis-step3.html 잠금 배너 동일 수정

□ GitHub push
```

---

## 주의사항

```
1. 기존 카드결제 코드(PG 연동 등) 완전 제거
2. SECTOR_PRICES는 표시 전용 (실제 금액 검증은 백엔드)
3. 신청 완료 후 has_access는 여전히 false
   → 관리자가 계약 생성해야 true
   → 사용자에게 "신청 접수" 상태로 안내
4. my-diagnosis.html에서 신청 현황 확인 가능하도록 연동
```
