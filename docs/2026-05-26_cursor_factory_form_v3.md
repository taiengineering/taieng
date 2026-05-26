# Cursor 작업지시: factory-list.html 시설 폼 수정 (v3 — 최종)

> 대상: tai-admin `tadmin/.../factory-list.html` (51KB)
> 롤백 완료 상태에서 수정

---

## 탭 구성 변경

| 기존 | 변경 후 |
|------|--------|
| 기본정보 / 시설 상세옵션 / 담당자 / 법령진단 | **기본정보 / 담당자** |

- **시설 상세옵션 탭 삭제** — 내용을 기본정보 탭으로 통합
- **법령진단 탭 삭제**
- **담당자 탭 유지 + 개선**

fpTabNav() 변경:
```js
function fpTabNav() {
  return '<ul class="nav nav-tabs mb-3" role="tablist">' +
    '<li class="nav-item"><button type="button" class="nav-link active" data-bs-toggle="tab" data-bs-target="#fp-tab1" role="tab">기본정보</button></li>' +
    '<li class="nav-item"><button type="button" class="nav-link" data-bs-toggle="tab" data-bs-target="#fp-tab3" role="tab">담당자</button></li>' +
    '</ul><div class="tab-content">';
}
```

---

## 변경 1: fpTab1 기본정보 탭

### KSIC 필드 제거
- "업종코드 KSIC" 전체 블록 제거
- KSIC 모달 HTML 제거
- `openFpKsicSearch`, `searchFpKsic`, `selectFpKsic`, `clearFpKsic`, `fpKsicModal`, `fpKsicName` 제거
- `collectFactoryBody()`에서 `ksic_code`, `ksic_name` 제거

### 상태 필드 → 표시 전용
- 등록/수정 모드에서 `fp-status` select → disabled 또는 읽기전용으로 변경
- 상태는 시스템이 자동 관리 (TRIAL/ACTIVE 등)

### 섹터별 필드 통합 (기존 fpTab2 내용을 fpTab1 하단에 추가)

주소/상태 필드 아래에 섹터별 필드 추가:

```js
var sector = localStorage.getItem('contract_sector') || 'INDUSTRIAL';
var isConstruction = (sector === 'CONSTRUCTION');
```

#### 산업/건물 (isConstruction = false):
```html
<hr class="my-3">
<h6 class="text-primary small fw-bold">시설 상세</h6>
<!-- 전기 수전 용량 (kW) -->
<!-- 가스 저장 용량 (kg) -->
<!-- 보일러 용량 (톤/h) -->
<!-- 승강기 수 (대) -->
<!-- 연간 에너지 사용량 (TOE) -->
<!-- 연면적 (㎡) -->
<!-- 공장등록 여부, 위험물 시설 여부, 다중이용시설 여부 -->
```

#### 건설 (isConstruction = true):
```html
<hr class="my-3">
<h6 class="text-primary small fw-bold">건설 상세</h6>
<!-- 공사금액 (원) -->
<!-- 건설공사 유형 (건축/토목/복합/기타) -->
<!-- 하도급 근로자수 합계 -->
```

### 건축물대장 자동채움 — 변경 없음
- selectJusoItem() → fetchBuildingInfo() → autoFill() 그대로 유지
- 연면적, 승강기 수 등이 자동채움됨

---

## 변경 2: fpTab2 (fpTab2 함수 삭제)

- fpTab2() 함수 삭제
- fpTabLegal() 함수 삭제
- loadLegalDiagnosisPanel() 함수 삭제
- bindLegalStartBtn() 함수 삭제
- renderFactoryPanel()에서 fpTab2(), fpTabLegal() 호출 제거

---

## 변경 3: fpTab3 담당자 탭 개선

현재: 인라인 폼으로 담당자 입력
변경:
1. **구분 (contact_type)** — select로 선택 가능 (안전담당자/시설담당자/전기담당자/기타)
2. **등록 폼** — 상단에 입력 폼 (구분, 이름, 연락처, 이메일, 직책) + "담당자 추가" 버튼
3. **등록된 담당자 리스트** — 하단에 테이블/카드로 출력
4. **수정 가능** — 각 담당자 행에 수정/삭제 버튼

API:
- GET /companies/{company_id}/contacts — 목록
- POST /companies/{company_id}/contacts — 추가
- PATCH /companies/{company_id}/contacts/{id} — 수정
- DELETE /companies/{company_id}/contacts/{id} — 삭제

주의: 시설(factory)의 담당자이므로 API 경로는 factories/{factory_id}/contacts를 사용할 수도 있음.
기존 fpTab3/fpOneContact/bindFpContacts/collectFpContacts 함수 기반으로 개선.

---

## 변경 4: 하단 등록설비/설비목록보기 삭제

- `fpLinkedHtml()` 함수 삭제
- renderFactoryPanel()에서 fpLinkedHtml() 호출 제거
- `mockEquipmentCount()` 함수 제거

---

## 목록 테이블 컨럼 변경

"업종" 컨럼 → "시설유형" (site_type_name || site_type)

---

## 체크리스트

- [ ] fpTabNav: 2개 탭으로 변경 (기본정보, 담당자)
- [ ] fpTab1: KSIC 제거 + 상태 disabled + 섹터별 필드 통합
- [ ] fpTab2, fpTabLegal: 함수 삭제
- [ ] fpTab3: 담당자 등록폼 + 리스트 + 수정
- [ ] fpLinkedHtml, mockEquipmentCount: 삭제
- [ ] collectFactoryBody: ksic 제거 + 섹터별 필드
- [ ] 목록: 업종 → 시설유형
- [ ] 건축물대장 autoFill 정상 동작 확인
- [ ] site/ 동기화 필요 없음 (SaaS 전용)
