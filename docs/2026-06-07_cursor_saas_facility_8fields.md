# Cursor 작업지시서 — SaaS 시설폼 법령필드 8개 추가 + 리스트 표시

> **작성일:** 2026-06-07 / **대상 파일:** `tai-admin/tadmin/full-version/html/horizontal-menu-template/factory-list.html` (단 1개)
> **이유:** 법(condition_code)이 쓰는 필드 중 SaaS 시설폼에 없던 8개를 입력폼에 추가하고, 리스트에 핵심을 표시.
> **근거 문서:** `45cminc/federation-contracts/docs/SAAS_FACILITY_FIELD_CROSSWALK_V1.md`
> **선행 완료(Claude):** factories 테이블에 누락했던 5개 컬럼 추가함(migration add_legal_facility_columns_v1). 즉 아래 8개는 전부 서버 저장 가능.

---

## ★ 절대 준수 (out of scope = 절대 금지)
- **이 파일 하나만 수정.** 다른 파일 건들지 말 것.
- 기존 필드·함수·구조 **삭제/이름변경 금지.** 오직 "추가"만.
- 백엔드/API/스키마 건들지 말 것 (factories 컬럼은 이미 준비됨).
- `collectFactoryBody`의 기존 전송 필드 수정 금지, 추가만.
- 한글 그대로 유지(깨짐 주의). 전각괄호() 쓰지 말고 일반괄호() 사용.

---

## 작업 1 — 입력폼에 8개 추가 (`fpSectorDetailBlock` 함수 내)

위치: `fpSectorDetailBlock(f,readOnly)` 함수의 **산업/일반 블록** `div.fp-fields-facility-industrial` 안. 현재 그 블록에는 fp-kw, fp-gas, fp-boiler, fp-lift, fp-toe, fp-area, fp-reg-factory, fp-hazmat, fp-multi가 있음.

**그 블록 마지막(다중이용 체크박스 뒤, `</div></div>` 전)에 아래 9개 입력칸 추가** (기존 변수 dis, chk, fpPick 패턴 그대로 사용):

```js
// ── 법령 필드 추가 (8개) ──
'<div class="col-6"><label class="form-label small">층수</label><input type="number" class="form-control" id="fp-floor" value="'+escapeHtml(fpPick(f,['floor_count']))+'"'+dis+'></div>'+
'<div class="col-6"><label class="form-label small">건물 등급</label><input type="number" class="form-control" id="fp-grade" value="'+escapeHtml(fpPick(f,['building_grade']))+'"'+dis+'></div>'+
'<div class="col-6"><label class="form-label small">가스 저장용량 (m3)</label><input type="number" class="form-control" id="fp-gas-m3" value="'+escapeHtml(fpPick(f,['gas_capacity_m3']))+'"'+dis+'></div>'+
'<div class="col-6"><label class="form-label small">변압기 용량 (kVA)</label><input type="number" class="form-control" id="fp-kva" value="'+escapeHtml(fpPick(f,['transformer_capacity_kva']))+'"'+dis+'></div>'+
'<div class="col-12"><div class="form-check"><input class="form-check-input" type="checkbox" id="fp-safety-mgr"'+chk(fpPick(f,['has_safety_manager']))+dis+'><label class="form-check-label" for="fp-safety-mgr">안전관리자 선임</label></div></div>'+
'<div class="col-12"><div class="form-check"><input class="form-check-input" type="checkbox" id="fp-high-gas"'+chk(fpPick(f,['has_high_pressure_gas']))+dis+'><label class="form-check-label" for="fp-high-gas">고압가스 취급</label></div></div>'+
'<div class="col-12"><div class="form-check"><input class="form-check-input" type="checkbox" id="fp-chem"'+chk(fpPick(f,['has_chemical_substance']))+dis+'><label class="form-check-label" for="fp-chem">화학물질 취급</label></div></div>'+
'<div class="col-12"><div class="form-check"><input class="form-check-input" type="checkbox" id="fp-has-boiler"'+chk(fpPick(f,['has_boiler']))+dis+'><label class="form-check-label" for="fp-has-boiler">보일러 보유</label></div></div>'+
```

> 주의: 위 9줄은 8개 필드(입력칸 기준). 기존 블록의 마지막 문자열 조각(`'...</label></div></div>'`)과 이어지도록 **마지막 체크박스(fp-multi) 줄 다음에 `+` 연결로 삽입**. JS 문자열 연결(`+`) 형식 유지.

---

## 작업 2 — 저장 전송 (`collectFactoryBody` 함수 내)

위치: `collectFactoryBody()`의 `else` 블록 (산업/일반, sector가 CONSTRUCTION 아닐 때). 현재 kw/gas/boiler/lift/toe/area/reg/haz/multi를 담는 곳.

**그 else 블록 끝(`body.is_multi_use=multi.checked;` 다음)에 추가:**

```js
var floor=document.getElementById('fp-floor'); if(floor&&floor.value) body.floor_count=parseInt(floor.value,10);
var grade=document.getElementById('fp-grade'); if(grade&&grade.value) body.building_grade=parseInt(grade.value,10);
var gasM3=document.getElementById('fp-gas-m3'); if(gasM3&&gasM3.value) body.gas_capacity_m3=parseFloat(gasM3.value);
var kva=document.getElementById('fp-kva'); if(kva&&kva.value) body.transformer_capacity_kva=parseFloat(kva.value);
var smgr=document.getElementById('fp-safety-mgr'); if(smgr) body.has_safety_manager=smgr.checked;
var hgas=document.getElementById('fp-high-gas'); if(hgas) body.has_high_pressure_gas=hgas.checked;
var chem=document.getElementById('fp-chem'); if(chem) body.has_chemical_substance=chem.checked;
var hboiler=document.getElementById('fp-has-boiler'); if(hboiler) body.has_boiler=hboiler.checked;
```

> factories 컬럼은 8개 모두 존재 확인됨(floor_count, building_grade, gas_capacity_m3, transformer_capacity_kva, has_safety_manager, has_high_pressure_gas, has_chemical_substance, has_boiler).

---

## 작업 3 — 리스트에 핵심 3개 컴럼 추가

확정: 핵심 3개만 표시 → **고압가스 / 화학물질 / 위험물** 유무를 배지로.

### 3-1. 테이블 헤더(thead) — '주소' th 앞에 1개 th 추가
현재 헤더: 체크박스 / No. / 시설코드 / 시설명 / 시설유형 / 인원 / 주소 / 등록일 / 상태

`<th>주소</th>` **앞**에 추가:
```html
<th>법령요소</th>
```

### 3-2. 콜스판(colspan) 수정
로딩/빈 행의 `colspan="9"` → **`colspan="10"`** (3군데: 로딩 tr, "등록된 시설이 없습니다" tr, catch 에러 tr).

### 3-3. tbody 행 렌더(loadList 내 items.map) — 주소 td 앞에 한 칸 추가
현재 `'<td>'+escapeHtml(f.address_road||f.address||'-')+'</td>'+` 줄 **앞**에 삽입:
```js
'<td>'+fpRiskBadges(f)+'</td>'+
```

### 3-4. 배지 헬퍼 함수 추가 (escapeHtml 함수 근처에 새 함수)
```js
function fpRiskBadges(f){
  var b=[];
  if(f.has_high_pressure_gas) b.push('<span class="badge bg-label-danger me-1">고압가스</span>');
  if(f.has_chemical_substance) b.push('<span class="badge bg-label-warning me-1">화학물질</span>');
  if(f.is_hazardous_material) b.push('<span class="badge bg-label-secondary me-1">위험물</span>');
  return b.length?b.join(''):'<span class="text-muted">-</span>';
}
```

> 리스트 API(/factories)가 has_high_pressure_gas 등을 내려주는지 확인 필요. 안 내려오면 배지는 '-'로 표시됨(오류 아님). 필요시 별도 백엔드 작업으로 /factories select 필드에 추가 — 이건 이 지시서 밖(별도 메모).

---

## 검증 (Cursor 수행 후 확인)
1. 시설등록 패널 열면 산업 상세에 8개 입력칸이 보임 (층수·등급·가스m3·변압기 + 체크박스 4개)
2. 입력 후 저장 → factories에 값 저장됨 (Supabase에서 확인 가능)
3. 리스트에 '법령요소' 컴럼이 주소 앞에 보임, 해당 시설은 배지 표시
4. 기존 저장·수정·삭제·검색 정상 동작(회귀 없음)

## 커밋 메시지
```
feat(tadmin): 시설폼 법령필드 8개 추가(층수·등급·가스m3·변압기·안전관리자·고압가스·화학물질·보일러) + 리스트 법령요소 배지
```

## 단계 선언
```text
SaaS 시설폼 추가 작업지시서 — 작성 완료 (Claude가 factories 컬럼 5개 선행추가함)
Cursor 수행: 입력폼 8개 + collectBody 8개 + 리스트 배지 3개
확인 필요(별도): /factories 리스트 API가 배지 3필드 내려주는지
```
