# Cursor 작업지시: factory-list.html 시설등록 폼 개선

> 대상: tai-admin `tadmin/.../factory-list.html` (51KB)
> site/ 동기화 필요 없음 (SaaS 전용 페이지)

---

## 변경 1: fpTab1에서 KSIC 업종코드 필드 삭제

`fpTab1()` 함수 내 "업종코드 KSIC" 전체 블록 제거:
```
'<div class="col-12"><label class="form-label">업종코드 KSIC</label>'+ ...
```

함께 제거:
- `fpKsicModal` 변수
- `openFpKsicSearch()`, `searchFpKsic()`, `selectFpKsic()`, `clearFpKsic()` 함수들
- `collectFactoryBody()`에서 `ksic_code`, `ksic_name` 필드
- HTML의 `<!-- KSIC 업종 검색 모달 -->` 전체
- `fpKsicName` 변수 및 관련 참조

---

## 변경 2: fpTab2 섹터별 조건부 표시

현재 `fpTab2()`는 모든 필드를 표시. 섹터에 따라 구분 필요.

섹터 판단 방법:
```js
var sector = localStorage.getItem('contract_sector') || 'INDUSTRIAL';
var isConstruction = (sector === 'CONSTRUCTION');
```

### 산업/건물만 표시 (isConstruction = false):
- 전기 수전 용량 (kW)
- 가스 저장 용량 (kg)
- 보일러 용량 (톤/h)
- 승강기 수 (대)
- 연간 에너지 사용량 (TOE)
- 연면적 (㎡)
- 공장등록 여부
- 위험물 시설 여부
- 다중이용시설 여부

### 건설만 표시 (isConstruction = true):
- 공사금액 (원)
- 건설공사 유형 (건축/토목/복합/기타)
- 하도급 근로자수 합계

구현 방법: `fpTab2()` 함수에 sector 파라미터 추가하거나, 각 필드를 `data-sector="INDUSTRIAL"` / `data-sector="CONSTRUCTION"` 속성으로 구분 후 JS로 토글.

---

## 변경 3: 담당자 섹션 fpTab1에서 제거

현재 fpTab1에 담당자 필드가 노출되는 경우 제거.
담당자는 오직 fpTab3 (담당자 탭)에서만 입력/수정 가능.

fpTab3 탭 자체는 유지:
- 구분 (select): 안전담당자, 시설담당자, 전기담당자, 기타
- 이름, 연락처, 이메일, 직책
- 담당자 추가/삭제/저장

---

## 체크리스트

- [ ] fpTab1: KSIC 필드 + 모달 + JS 함수 제거
- [ ] fpTab2: 섹터별 조건부 표시
- [ ] fpTab1 내 담당자 섹션 확인 후 제거
- [ ] collectFactoryBody()에서 ksic_code, ksic_name 제거
- [ ] 테스트: 시설등록 → 산업 섹터일때 필드 확인
- [ ] 테스트: 시설등록 → 건설 섹터일때 필드 확인
