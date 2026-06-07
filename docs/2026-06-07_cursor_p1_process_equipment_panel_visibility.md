# Cursor 작업지시서 — P1 입력단계: 공정·설비 패널 노출

## 작업 한 줄 요약
`taieng/nexas/free-diagnosis.html`의 **`applyDiagPanelVisibility()` 함수 1개만** 교체해서, sector·tier에 따라 공정·설비 패널을 보이게 한다. **그 외 어떤 것도 건드리지 않는다.**

## 절대 규칙 (어기면 작업 무효)
- 수정 파일은 **`taieng/nexas/free-diagnosis.html` 단 1개.**
- 그 안에서도 **`applyDiagPanelVisibility()` 함수 본문만** 교체. 다른 함수·HTML·CSS 건드리지 말 것.
- 새 함수 추가 금지. 새 변수 금지. 새 API 호출 금지. 기존 표 렌더 함수(`renderTableField`, `renderDynForm`, `initDiagnosisTables`)는 **이미 있는 것을 호출만** 한다.
- DB·백엔드·엔진·CSS·다른 HTML 파일 **수정 금지.**
- `loadFreeForm()`/`loadPaidForm()` 등 다른 함수의 호출 흐름 **변경 금지.**
- 판단이 필요한 상황이 생기면 **멈추고 보고.** 임의로 해석해서 진행하지 말 것.

## 현재 상태 (그대로 둘 것)
- 공정 패널 `#diagPanelProcess` → 내부 `#dynFormAreaProcess`
- 설비 패널 `#diagPanelEquipment` → 내부 `#dynFormAreaEquipment`
- 현재 두 패널은 `applyDiagPanelVisibility()`가 항상 `display:none` 처리 중.

## 정확히 할 일

### 단계 1 — `applyDiagPanelVisibility()` 함수를 아래로 **통째로 교체**

현재 코드:
```javascript
function applyDiagPanelVisibility() {
  const proc = document.getElementById('diagPanelProcess');
  const equip = document.getElementById('diagPanelEquipment');
  // Week1: 공정·설비 패널은 골격만 (항상 비노출)
  if (proc) proc.style.display = 'none';
  if (equip) equip.style.display = 'none';
}
```

교체할 코드:
```javascript
function applyDiagPanelVisibility(prefix) {
  // prefix: 'free' | 'paid' (기본 'free')
  const pfx = prefix || 'free';
  const proc = document.getElementById('diagPanelProcess');
  const equip = document.getElementById('diagPanelEquipment');

  // sector/tier별 노출 규칙 (INPUT_STAGE_COMPLETION_PLAN 작업3 표)
  // 공정: INDUSTRY PAID2+ / CONSTRUCTION PAID
  // 설비: BUILDING PAID / INDUSTRY PAID3 / CONSTRUCTION PAID
  const t = (pfx === 'paid') ? (paidTier || '') : 'FREE';
  let showProc = false, showEquip = false;

  if (sector === 'INDUSTRY') {
    showProc  = (t === 'STANDARD' || t === 'PREMIUM');
    showEquip = (t === 'PREMIUM');
  } else if (sector === 'CONSTRUCTION') {
    showProc  = (pfx === 'paid');
    showEquip = (pfx === 'paid');
  } else if (sector === 'BUILDING') {
    showProc  = false;            // 건물은 공정 없음
    showEquip = (pfx === 'paid');
  }

  if (proc)  proc.style.display  = showProc  ? '' : 'none';
  if (equip) equip.style.display = showEquip ? '' : 'none';
}
```

### 단계 2 — 패널이 보일 때 표를 그리도록, 기존 호출부에 한 줄씩만 추가

`loadFreeForm()` 안에서 `renderDynForm('dynFormArea', ...)` 직후에, 공정·설비 영역에도 같은 방식으로 그리도록 추가. **단, 필드가 없으면 아무것도 안 그림(기존 renderDynForm이 빈 배열이면 알아서 빈 처리).**

`loadFreeForm()`의 기존 마지막 try 블록:
```javascript
    const r = await fetch(`${API}/diagnosis/fields?sector=${sector}&tier=FREE`);
    const json = await r.json();
    renderDynForm('dynFormArea', json.data?.groups || [], 'free');
```
→ 이 줄 다음에 추가 없음. (FREE는 시설만이므로 공정·설비 안 그림 — 규칙상 맞음)

`loadPaidForm(tierCode)`의 기존 try 블록:
```javascript
    const r = await fetch(`${API}/diagnosis/fields?sector=${sector}&tier=${tierApi}`);
    const json = await r.json();
    renderDynForm('paidFormArea', json.data?.groups || [], 'paid');
```
→ 이 `renderDynForm` 줄 **다음에** 아래 3줄 추가:
```javascript
    applyDiagPanelVisibility('paid');
```
(주의: `loadPaidForm`은 `paidFormArea`에 전체 폼을 그리는 기존 구조다. 공정·설비 패널은 step2 영역이므로, **`loadPaidForm`에서는 패널 가시성만 갱신**하고 표는 기존 `paidFormArea` 흐름을 그대로 둔다. 표를 옮기거나 새로 그리지 말 것.)

### 단계 3 — `loadFreeForm()` 안의 기존 호출 확인
`loadFreeForm()`에는 이미 `applyDiagPanelVisibility();`가 있다. 이를 `applyDiagPanelVisibility('free');`로 인자만 추가. (없으면 추가하지 말고 보고.)

### 단계 4 — "Week2" 안내문 제거
HTML에서 아래 두 줄의 안내 문구만 빈 칸으로:
```html
<p class="diag-tier-placeholder">공정 입력은 Week2에서 제공됩니다.</p>
<p class="diag-tier-placeholder">설비 입력은 Week2에서 제공됩니다.</p>
```
→ `<div id="dynFormAreaProcess"></div>`, `<div id="dynFormAreaEquipment"></div>` 로 내부만 비움. (div id는 유지)

## 하지 말 것 (재확인)
- `process_list`/`equipment_list` 표를 step2 패널에 새로 그리는 로직을 **발명하지 말 것.** 이번 작업은 **패널 가시성 규칙 + 안내문 제거**까지만.
- 만약 "패널은 보이는데 안이 비어 있다"가 되더라도 그대로 보고. 표 렌더 연결은 다음 작업지시서에서 다룬다.
- 결제·진단 실행·결과 렌더 함수 일절 손대지 말 것.

## 배포
- `taieng` main push → Cloudflare Pages 자동 배포.
- 캐시: `free-diagnosis.html`은 즉시 반영되나, 혹시 안 보이면 강력 새로고침.

## 완료 보고 (이것만)
1. 수정 파일: `nexas/free-diagnosis.html` (1개 맞는지)
2. `applyDiagPanelVisibility()` 교체 여부
3. `loadPaidForm`에 `applyDiagPanelVisibility('paid')` 추가 여부
4. 안내문 2개 제거 여부
5. commit SHA
6. 그 외 변경한 것 (있으면 전부 — 없으면 "없음")

---

이 작업지시서가 폭주를 막는 핵심은 **세 가지**입니다: ① 수정 파일·함수를 1개로 못박음, ② 교체할 코드를 그대로 제공해 해석 여지를 없앰, ③ "표 렌더 연결은 이번 범위 아님"이라고 선을 그어 Cursor가 스스로 기능을 확장하지 못하게 함.
