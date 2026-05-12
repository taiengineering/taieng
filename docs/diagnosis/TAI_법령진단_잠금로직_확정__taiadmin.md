# TAI Safe — 법령진단 잠금 로직 확정

> 확정일: 2026-03-31

---

## 핵심 결정

**법령진단은 SaaS 구독(STARTER/BUSINESS/ENTERPRISE)과 완전히 분리된 별도 유료 서비스입니다.**

SaaS 구독 여부와 관계없이, 법령진단 2단계·3단계는 단건 결제한 경우에만 해제됩니다.

---

## 서비스 구조

```
[SaaS 구독]                    [법령진단 단건]
 STARTER / BUSINESS / ENTERPRISE   1단계 무료
  → 점검 관리                       2단계 단건 결제
  → 교육 발령·이수 관리              3단계 단건 결제
  → 작업자 관리                      종합리포트 단건 결제
  → 신고·보고 일정
  → 알림
  ↕ 완전 분리                       ↕ 별도 과금
```

---

## 단계별 접근 조건

| 단계 | 접근 조건 | 비고 |
|------|---------|------|
| 1단계 기초진단 | 로그인만 하면 가능 | 무료 |
| 2단계 공정/공종진단 | diagnosis_purchase 테이블에 step2 결제 기록 있어야 | 단건 구매 |
| 3단계 설비/공정상세 | diagnosis_purchase 테이블에 step3 결제 기록 있어야 | 단건 구매 |
| 종합리포트 PDF | diagnosis_purchase 테이블에 report 결제 기록 있어야 | 단건 구매 |

**SaaS 계약 레벨(contract_level)로는 어떤 단계도 해제되지 않습니다.**

---

## 잠금 체크 로직

```javascript
// 단계 접근 가능 여부 체크
async function canAccessDiagnosisStage(factoryId, stage) {
  if (stage === 1) return true; // 항상 무료

  // SaaS 구독 레벨 체크 안 함 — 법령진단은 별도 서비스
  // 단건 결제 기록만 체크
  const res = await apiCall('GET',
    `/diagnosis/access-check?factory_id=${factoryId}&step=${stage}`);
  return res.data.has_access;
}
```

```python
# 백엔드: GET /diagnosis/access-check
def check_diagnosis_access(factory_id: str, step: int, current_user):
    # contract_level 체크 없음
    # diagnosis_purchases 테이블에서 단건 결제 기록만 확인
    purchase = supabase.table('diagnosis_purchases')
        .select('id')
        .eq('factory_id', factory_id)
        .eq('company_id', current_user.company_id)
        .eq('step', step)
        .eq('status', 'PAID')
        .limit(1).execute()

    return {'has_access': len(purchase.data) > 0}
```

---

## 잠금 배너 (2단계·3단계 공통)

```html
<div class="card border-warning" id="lock-banner">
  <div class="card-body text-center py-5">
    <div class="fs-1 mb-3">🔒</div>
    <h5 class="mb-2">유료 서비스입니다</h5>
    <p class="text-muted mb-1">법령진단은 SaaS 구독과 별도로 과금됩니다.</p>
    <p class="text-muted mb-4" id="lock-price-text"></p>
    <div class="d-flex gap-2 justify-content-center">
      <button class="btn btn-primary px-4" onclick="goToPurchase()">
        <i class="ti tabler-credit-card me-1"></i>단건 구매하기
      </button>
      <a href="my-diagnosis.html" class="btn btn-outline-secondary">
        진단 내역 보기
      </a>
    </div>
    <p class="text-muted small mt-3">
      ※ 구독 플랜(STARTER/BUSINESS/ENTERPRISE)으로는 해제되지 않습니다.
    </p>
  </div>
</div>
```

---

## 단건 가격표 (요금체계 v2.0 기준)

| 섹터 | 2단계 | 3단계 | 종합리포트 |
|------|------|------|----------|
| 일반건물 | 29,000원 | 59,000원 | 99,000원 |
| 제조·공장 | 49,000원 | 99,000원 | 249,000원 |
| 건설현장 | 79,000원 | 149,000원 | 399,000원 |
| 특수시설(일반) | 49,000원 | 99,000원 | 199,000원 |

---

## DB 테이블

```sql
-- 법령진단 단건 결제 기록
CREATE TABLE IF NOT EXISTS diagnosis_purchases (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id  UUID NOT NULL REFERENCES companies(id),
  factory_id  UUID NOT NULL REFERENCES factories(id),
  sector      TEXT NOT NULL,       -- BUILDING / MANUFACTURING / CONSTRUCTION 등
  step        INTEGER NOT NULL,    -- 2 or 3
  price       INTEGER NOT NULL,
  status      TEXT DEFAULT 'PAID', -- PAID / REFUNDED
  paid_at     TIMESTAMPTZ DEFAULT now(),
  expires_at  TIMESTAMPTZ,         -- NULL = 영구 (단건)
  created_at  TIMESTAMPTZ DEFAULT now()
);
```
