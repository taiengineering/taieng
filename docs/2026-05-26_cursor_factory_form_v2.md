# Cursor 작업지시: factory-list.html 시설 폼 수정 (v2 — 정밀 범위)

> 대상: tai-admin `tadmin/.../factory-list.html` (51KB)
> ⚠️ 이전 Cursor 작업에서 탭을 삭제하는 실수가 있었음 — 이번에는 절대 탭을 삭제하지 말 것

---

## 절대 삭제 금지

1. **시설 상세옵션 탭 (fp-tab2)** — 탭 자체 유지, 내부 필드만 조건부 표시
2. **법령진단 탭 (fp-tab-legal)** — 변경 없음
3. **담당자 탭 (fp-tab3)** — 변경 없음
4. **건축물대장 자동채움 로직** — selectJusoItem → fetchBuildingInfo → autoFill 변경 없음
5. **fpTabNav() 함수** — 4개 탭 버튼 모두 유지

---

## 변경 1: fpTab1에서 KSIC 필드만 제거

fpTab1() 함수 내 "업종코드 KSIC" 블록만 제거:
```
'<div class="col-12"><label class="form-label">업종코드 KSIC</label>'+ ... (readOnly 조건부 블록 전체)
```

함께 제거:
- HTML `<!-- KSIC 업종 검색 모달 -->` 전체
- `fpKsicModal` 변수
- `openFpKsicSearch()`, `searchFpKsic()`, `selectFpKsic()`, `clearFpKsic()` 함수
- `fpKsicName` 변수
- `collectFactoryBody()`에서 `ksic_code`, `ksic_name` 필드
- 목록 테이블의 "업종" 컨럼 → "시설유형" (site_type_name) 으로 변경

---

## 변경 2: fpTab2 섹터별 조건부 표시

탭 자체는 유지. 내부 필드만 조건부 표시.

### 섹터 판단 방법
```js
var sector = localStorage.getItem('contract_sector') || 'INDUSTRIAL';
var isConstruction = (sector === 'CONSTRUCTION');
```

### 산업/건물일 때 (isConstruction = false):
표시: 전기 수전 용량, 가스 저장 용량, 보일러 용량, 승강기 수, 연간 에너지 사용량, 연면적
체크박스: 공장등록 여부, 위험물 시설 여부, 다중이용시설 여부
숨김: 공사금액, 건설공사 유형, 하도급 근로자수

### 건설일 때 (isConstruction = true):
표시: 공사금액, 건설공사 유형, 하도급 근로자수
숨김: 전기/가스/보일러/승강기/에너지/연면적, 체크박스 3개

### 구현 방법
fpTab2() 함수 내에서 각 필드의 col div에 조건부 클래스 추가:
```js
var hideIndustry = isConstruction ? ' d-none' : '';
var hideConstruction = isConstruction ? '' : ' d-none';
```

collectFactoryBody()도 동일하게 섹터 판단 후 해당 필드만 전송.

---

## 변경하지 않는 것 (명시)

- fpTabNav() — 4개 탭 버튼 모두 유지
- fpTab1() — KSIC 필드 외 전부 유지 (시설명, 시설유형, 인원, 주소, 상태)
- fpTab2() — 탭 자체 유지, 필드 visible/hidden만 조절
- fpTab3() — 변경 없음
- fpTabLegal() — 변경 없음
- loadLegalDiagnosisPanel() — 변경 없음
- selectJusoItem() → fetchBuildingInfo() → autoFill() — 변경 없음
- renderFactoryPanel() — 탭 구성 변경 없음
- bindConstructionExtraFields() — 변경 없음

---

## 체크리스트

- [ ] fpTab1: KSIC 필드 + 모달 + JS 함수 제거
- [ ] fpTab2: 섹터별 조건부 표시 (d-none 토글)
- [ ] fpTabNav: 4개 탭 모두 존재 확인
- [ ] fpTabLegal: 변경 없음 확인
- [ ] fpTab3: 변경 없음 확인
- [ ] 건축물대장 autoFill 정상 동작 확인
- [ ] collectFactoryBody: ksic 제거 + 섹터별 필드 필터
- [ ] site/ 동기화 필요 없음 (SaaS 전용)
