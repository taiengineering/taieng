# WO-FRONT-E2E-ROUTE-SWITCH-001 — SaaS 진단 실행 경로 신규 파이프 전환

**작성일:** 2026-06-27 | **성격:** 프론트 라우팅 전환(엔진/어댑터/persist/transform/데이터계약 변경 0).
**상태:** 설계·데이터검증 완료 / 파일 적용은 Cursor 핸드오프(아래 EXACT DIFF). 적용·배포 후 브라우저 PASS.
**대상 파일:** `tai-admin / tadmin/full-version/html/horizontal-menu-template/diagnosis-step1.html` (sha `d87d6cd7`, ~660줄)

---

## ⚠️ 전환 시 의미 변화 (대표 확인 권장 — 적용 전 일독)
```
1) 입력폼 미소비:
   from-instances는 step1 입력(섹터·근로자수·위험물·면적 등)을 사용하지 않고
   기존 obligation_instance 행만 factory_id 기준으로 읽어 반환·persist한다.
   → "진단하기" = 입력 기반 실시간 평가가 아니라 "사전 생성된 의무 렌더".
   → obligation_instance가 없는 시설은 persisted=false → v2 이동 불가(가드 처리함).
   (전제: 시설별 obligation_instance가 사전/배치로 생성돼 있어야 함. e9c56af6은 171건 보유.)

2) 건설 섹터:
   현재 step1(CONSTRUCTION) → construction-diagnosis-step2.html(공정·설비 유료 흐름).
   이를 v2로 바꾸면 그 흐름이 끊김 → 본 WO에서 건설은 레거시 유지(전환 대상=비건설).
```

## TASK-001 — 현재 btnDiagnose 위치·동작 (확정)
```
파일:      tadmin/.../diagnosis-step1.html
버튼:      <button id="btnDiagnose">1단계 진단 실행</button>
핸들러:    runDiagnosis()  (IIFE 내부, btnDiagnose click 바인딩)
호출 API:  apiCall('POST','/legal-engine/diagnose/step1',{factory_id,sector,input})
redirect:  비건설 → diagnosis-result.html?... / 건설 → construction-diagnosis-step2.html?...
```

## 신규 호출 계약 (검증된 운영 엔드포인트, 코드 직독)
```
POST /obligation-adapter/from-instances/{factory_id}?persist=true
  body:    없음
  header:  Authorization: Bearer <token>  → created_by=users.id (apiCall이 자동 첨부)
  return:  { persisted:bool, diagnosis_id:str|null, obligation_count:int, verdict, obligations[], ... }
  의미:    obligation_count==0 → persist 생략, diagnosis_id=null (에러 아님)
다음:     diagnosis-result-v2.html?diagnosis_id={diagnosis_id}
           → GET /diagnosis/transform/{diagnosis_id} → 169 obligations
```

## 데이터 경로 사전 검증 (대상 factory e9c56af6, DB 직독)
```
factory_diagnosis_results 최신 obligations 행:
  diagnosis_id 0238b7fd-…  source FROM_INSTANCES_OBLIGATION_INSTANCE
  created_by 있음  is_latest true  raw 171  병합키(distinct) 169
→ from-instances(persist=true)+Bearer 시 동일 행 생성·created_by 세팅·transform 169 도달 확인(지난 세션 실호출).
```

---

## EXACT DIFF — Cursor 적용 (diagnosis-step1.html, runDiagnosis 교체)

### OLD (현재, 제거하지 말 것 — 아래 NEW로 교체하며 레거시는 else 블록에 보존됨)
```js
  // ── runDiagnosis ──────────────────────────────────────────────────
  async function runDiagnosis() {
    var factoryId = document.getElementById('selFactory') && document.getElementById('selFactory').value;
    if (!factoryId) { showToast('warning', '시설을 선택해 주세요.'); return; }
    if (!selectedSector) { document.getElementById('sectorHint').classList.remove('d-none'); return; }
    localStorage.setItem('selected_factory_id', factoryId);
    localStorage.setItem('current_factory_id', factoryId);
    var input = getFormInput(selectedSector);
    showLoading(true);
    try {
      var json = await apiCall('POST', '/legal-engine/diagnose/step1', {
        factory_id: factoryId,
        sector:     selectedSector,
        input:      input
      });
      var data = json.data || json;
      try {
        sessionStorage.setItem('tai_diagnosis_step1', JSON.stringify({ data: data, saved_at: Date.now() }));
      } catch (e) {}
      var did = data.diagnosis_id || '';
      if (did) localStorage.setItem('current_diagnosis_id', did);
      var q = new URLSearchParams({ factory_id: factoryId, sector: selectedSector });
      if (did) q.set('diagnosis_id', did);
      // ★ CONSTRUCTION → 건설 전용 2단계 페이지로 이동
      if (selectedSector === 'CONSTRUCTION') {
        location.href = 'construction-diagnosis-step2.html?' + q.toString();
      } else {
        location.href = 'diagnosis-result.html?' + q.toString();
      }
    } catch (e) {
      showToast('error', e.message || '진단 요청에 실패했습니다.');
    } finally {
      showLoading(false);
    }
  }
```

### NEW (전환 + 레거시 보존 Feature Flag)
```js
  // ── runDiagnosis ──────────────────────────────────────────────────
  // WO-FRONT-E2E-ROUTE-SWITCH-001: 신규 운영 파이프라인 전환
  //   USE_OBLIGATION_PIPELINE=true  → POST /obligation-adapter/from-instances/{id}?persist=true
  //                                   → diagnosis-result-v2.html?diagnosis_id=...  (obligations 169)
  //   USE_OBLIGATION_PIPELINE=false → (레거시 보존) /legal-engine/diagnose/step1 → diagnosis-result.html
  //   ※ CONSTRUCTION은 공정·설비(2·3단계) 전용 흐름 유지 위해 레거시 경로 유지.
  var USE_OBLIGATION_PIPELINE = true;

  async function runDiagnosis() {
    var factoryId = document.getElementById('selFactory') && document.getElementById('selFactory').value;
    if (!factoryId) { showToast('warning', '시설을 선택해 주세요.'); return; }
    if (!selectedSector) { document.getElementById('sectorHint').classList.remove('d-none'); return; }
    localStorage.setItem('selected_factory_id', factoryId);
    localStorage.setItem('current_factory_id', factoryId);
    localStorage.setItem('current_sector', selectedSector);
    showLoading(true);

    // ── 신규 운영 파이프라인 (비건설) ─────────────────────────────────
    if (USE_OBLIGATION_PIPELINE && selectedSector !== 'CONSTRUCTION') {
      try {
        var resp = await apiCall(
          'POST',
          '/obligation-adapter/from-instances/' + encodeURIComponent(factoryId) + '?persist=true',
          {}
        );
        var r   = (resp && resp.data) ? resp.data : resp;
        var did = (r && r.diagnosis_id) || '';
        if (!r || !r.persisted || !did) {
          showToast('warning', '이 시설에는 평가된 의무 데이터가 없습니다. 시설 정보 확인 후 다시 시도해 주세요.');
          showLoading(false);
          return;
        }
        localStorage.setItem('current_diagnosis_id', did);
        location.href = 'diagnosis-result-v2.html?diagnosis_id=' + encodeURIComponent(did);
        return;
      } catch (e) {
        showToast('error', e.message || '진단 요청에 실패했습니다.');
        showLoading(false);
        return;
      }
    }

    // ── 레거시 경로 (보존: CONSTRUCTION + 플래그 off) ────────────────
    var input = getFormInput(selectedSector);
    try {
      var json = await apiCall('POST', '/legal-engine/diagnose/step1', {
        factory_id: factoryId,
        sector:     selectedSector,
        input:      input
      });
      var data = json.data || json;
      try {
        sessionStorage.setItem('tai_diagnosis_step1', JSON.stringify({ data: data, saved_at: Date.now() }));
      } catch (e) {}
      var did = data.diagnosis_id || '';
      if (did) localStorage.setItem('current_diagnosis_id', did);
      var q = new URLSearchParams({ factory_id: factoryId, sector: selectedSector });
      if (did) q.set('diagnosis_id', did);
      if (selectedSector === 'CONSTRUCTION') {
        location.href = 'construction-diagnosis-step2.html?' + q.toString();
      } else {
        location.href = 'diagnosis-result.html?' + q.toString();
      }
    } catch (e) {
      showToast('error', e.message || '진단 요청에 실패했습니다.');
    } finally {
      showLoading(false);
    }
  }
```

**적용 메모(Cursor):** `runDiagnosis` 함수 1개만 위 NEW로 교체. 다른 코드/마크업/이벤트 바인딩 불변. legal-engine 호출은 **삭제 아님 — else 블록에 보존**(TASK-002/007 충족). 저장 후 `git push` → Cloudflare Pages 자동 배포.

---

## TASK별 충족
```
TASK-001 현재 경로 확인            ✓ (legal-engine/step1 → diagnosis-result.html)
TASK-002 legal-engine 보존        ✓ (Feature Flag else 블록 + CONSTRUCTION)
TASK-003 from-instances?persist   ✓ (비건설 분기, Bearer→created_by, 응답 persisted/diagnosis_id)
TASK-004 diagnosis_id → v2 이동    ✓ (diagnosis-result-v2.html?diagnosis_id=…)
TASK-005 브라우저 169 렌더         ⏳ 배포 후 검증 (아래 절차)
TASK-006 회귀 불변                 ✓ 코드측 무변경(엔진/어댑터/transform 0) — raw171/169/trigger/created_by 영향 없음
TASK-007 레거시 제거 금지          ✓ 사용 중단만(플래그), 삭제 0
```

## 배포 후 PASS 검증 절차 (TASK-005/006)
```
1. 로그인 상태에서 diagnosis-step1.html → 시설(e9c56af6 등) 선택 → 비건설 섹터 → "1단계 진단 실행"
2. 네트워크: POST /obligation-adapter/from-instances/{id}?persist=true → 200, persisted=true, diagnosis_id
3. 이동: diagnosis-result-v2.html?diagnosis_id=… 자동
4. 화면: Headline / obligations 169 / Category·Description·Evidence / ROI / Inspection Schedule 표시
5. DB 회귀: 새 행 source=FROM_INSTANCES_OBLIGATION_INSTANCE, created_by=현재 사용자, raw 171, 병합키 169
```
운영에서 1~5가 한 번의 클릭으로 완결되면 **PASS** → "법령엔진 1단계 MVP 파이프라인 종료" 선언 가능.

## Boundary 준수
```
Applicability/Generator/Glue/Adapter/Persist/Transform/DataContract/Architecture: 전부 NO.
변경 대상 = 프론트 실행 경로(diagnosis-step1.html runDiagnosis) 1개 함수.
새 Engine/Adapter/Persist/Router/JSON: 0. 법령로직/Check Engine/Transform: 미수정.
```

## 남은 실행(기계적)
```
① Cursor: 위 NEW로 runDiagnosis 교체 → git push (tai-admin)
② Cloudflare Pages 자동 배포
③ 브라우저 PASS 검증(위 절차) — 필요 시 Claude in Chrome로 대행 가능(로그인은 대표)
```

*WO-FRONT-E2E-ROUTE-SWITCH-001 — 설계·데이터검증 완료, 드롭인 코드 준비. 적용·배포 후 클릭 1회 E2E PASS 확인 남음. 단, "입력폼 미소비"·"건설 레거시 유지" 2건 대표 확인 권장.*
