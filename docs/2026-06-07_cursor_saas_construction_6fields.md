# Cursor 작업지시서 — SaaS 시설폼 건설 법령필드 6개 추가 + 리스트 배지

> **작성일:** 2026-06-07 / **대상 파일:** `tai-admin/tadmin/full-version/html/horizontal-menu-template/factory-list.html` (단 1개)
> **이전 작업:** 산업 법령필드 8개 추가 완료됨(이미 커밋됨). 이번은 **건설(CONSTRUCTION) 쪽**.
> **선행 완료(Claude):** factories 컬럼 6개 추가(add_legal_construction_columns_v1) + 백엔드 스키마 6개 추가(factories.py v2.4.0, commit e825569). 즉 아래 6개는 전부 서버 저장 가능.

---

## ★ 절대 준수 (out of scope = 금지)
- 이 파일 하나만 수정. 다른 파일·백엔드 금지(백엔드는 이미 준비됨).
- 기존 필드·함수 삭제/이름변경 금지. 오직 "추가"만.
- 산업 쪽 이미 추가한 8개는 건들지 말 것.
- 한글 그대로 유지(깨짐 주의). 전각괄호 금지, 일반괄호 사용.

---

## 작업 1 — 건설 입력폼에 6개 추가 (`fpSectorDetailBlock` 함수 내 건설 블록)

위치: `fpSectorDetailBlock(f,readOnly)`의 **건설 블록** `div.fp-fields-construction`. 현재 그 블록엔 construction_amount, construction_extra_fields(construction_type, subcontractor_worker_count)가 있음.

`construction_extra_fields` div 안, **하도급 근로자수(subcontractor_worker_count) 블록 다음**에 아래 6개 추가 (기존 dis, chk, fpPick 패턴 그대로):

```js
// ── 건설 법령 필드 추가 (6개) ──
'<div class="mb-2"><label class="form-label">하도급 업체 수</label><div class="input-group">'+
'<input type="number" class="form-control" id="fp-subcon-cnt" min="0" value="'+escapeHtml(fpPick(f,['subcontractor_count']))+'"'+dis+'>'+
'<span class="input-group-text">개사</span></div></div>'+
'<div class="form-check"><input class="form-check-input" type="checkbox" id="fp-tower-crane"'+chk(fpPick(f,['has_tower_crane']))+dis+'><label class="form-check-label" for="fp-tower-crane">타워크레인 사용</label></div>'+
'<div class="form-check"><input class="form-check-input" type="checkbox" id="fp-confined"'+chk(fpPick(f,['has_confined_space']))+dis+'><label class="form-check-label" for="fp-confined">밀폐공간 작업</label></div>'+
'<div class="form-check"><input class="form-check-input" type="checkbox" id="fp-asbestos"'+chk(fpPick(f,['has_asbestos_demo']))+dis+'><label class="form-check-label" for="fp-asbestos">석면해체 작업</label></div>'+
'<div class="form-check"><input class="form-check-input" type="checkbox" id="fp-blasting"'+chk(fpPick(f,['has_blasting']))+dis+'><label class="form-check-label" for="fp-blasting">발파 작업</label></div>'+
'<div class="form-check"><input class="form-check-input" type="checkbox" id="fp-diving"'+chk(fpPick(f,['has_diving']))+dis+'><label class="form-check-label" for="fp-diving">잠수 작업</label></div>'+
```

> 주의: 하도급근로자수 블록의 닫는 `</div></div>` 구조를 깨지 않도록, 그 블록이 끝난 지점(`total_worker_display` div 닫긌 뒤)에 `+` 연결로 이어붙일 것. construction_extra_fields div 안에 위치시키면 공사금액>0일 때만 보임(기존 동작 유지).

---

## 작업 2 — 저장 전송 (`collectFactoryBody` 함수, CONSTRUCTION 분기)

위치: `collectFactoryBody()`의 `if(sector==='CONSTRUCTION'){ ... }` 블록. 현재 construction_amount, construction_type, subcontractor_worker_count를 담는 곳.

**그 if 블록 끝(subcontractor_worker_count 처리 다음)에 추가:**

```js
var subCnt=document.getElementById('fp-subcon-cnt'); if(subCnt&&subCnt.value!=='') body.subcontractor_count=parseInt(subCnt.value,10);
var tc=document.getElementById('fp-tower-crane'); if(tc) body.has_tower_crane=tc.checked;
var cf=document.getElementById('fp-confined'); if(cf) body.has_confined_space=cf.checked;
var asb=document.getElementById('fp-asbestos'); if(asb) body.has_asbestos_demo=asb.checked;
var bl=document.getElementById('fp-blasting'); if(bl) body.has_blasting=bl.checked;
var dv=document.getElementById('fp-diving'); if(dv) body.has_diving=dv.checked;
```

> factories 컬럼 6개 모두 존재 확인됨(subcontractor_count, has_tower_crane, has_confined_space, has_asbestos_demo, has_blasting, has_diving). 백엔드 스키마도 준비됨(v2.4.0).

---

## 작업 3 — 리스트 배지에 건설 위험 추가 (fpRiskBadges 확장)

이미 산업에서 만든 `fpRiskBadges(f)` 함수에 건설 위험 배지를 추가. 기존 함수 마지막 return 전에 삽입:

```js
  if(f.has_tower_crane) b.push('<span class="badge bg-label-danger me-1">타워크레인</span>');
  if(f.has_blasting) b.push('<span class="badge bg-label-danger me-1">발파</span>');
  if(f.has_asbestos_demo) b.push('<span class="badge bg-label-warning me-1">석면</span>');
```

> 건설·산업 한 리스트에 섞일 수 있으나, 해당 boolean이 true인 것만 배지로 뜨므로 섬터 무관하게 안전. 산업 시설은 건설 boolean이 없으니 안 뜨고, 그 반대도 마찬가지.

---

## 검증 (Cursor 수행 후)
1. 계약섬터가 건설(CONSTRUCTION)인 계정으로 시설등록 → 공사금액 입력 시 하단에 6개 필드 노출(하도급업체수 + 체크박스 5개)
2. 입력·저장 → factories에 값 저장됨(Supabase 확인)
3. 리스트 '법령요소' 컴럼에 건설 위험 배지 표시
4. 산업 시설·기존 기능 정상(회귀 없음)

## 커밋 메시지
```
feat(tadmin): 건설 시설폼 법령필드 6개 추가(하도급업체수·타워크레인·밀폐공간·석면해체·발파·잠수) + 리스트 건설위험 배지
```

## 단계 선언
```text
건설 SaaS 시설폼 추가 작업지시서 — 작성 완료 (Claude가 factories 컬럼 6개 + 백엔드 스키마 6개 선행함)
Cursor 수행: 건설폼 6개 + collectBody 6개 + 리스트 배지 3개
제외(정책): process_list·subcontractor table은 시설폼에 넣지 않음(공정·협력업체 별도 화면)
```
