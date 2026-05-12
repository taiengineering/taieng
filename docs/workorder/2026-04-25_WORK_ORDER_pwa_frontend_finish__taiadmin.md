# WORK ORDER 2026-04-25 · PWA 프론트 마무리 (잔여 P0/P1)

- **대상**: Cursor (프론트창)
- **레포/브랜치**: `tai-admin` / `main`
- **선행 작업**: PR `69d030e` (PWA 1차 보강) 이미 main에 반영 완료
- **본 작업 범위**: 1차 보강에서 누락된 잔여 P0/P1 항목

---

## 사전 점검 결과 (2026-04-25 GitHub main 직접 확인)

### ✅ 1차 보강(`69d030e`)에서 이미 완료된 항목

| 이슈 | 파일 | 확인 |
|---|---|---|
| P1-1 공통 유틸 신설 | `_utils.js` | ✅ apiFetch/uploadPhoto/queuePush/queueFlush/logoutClean 모두 구현 |
| P0-1 emergency 실패 처리 | `emergency.html` | ✅ 16KB → 9.8KB로 정리 |
| P0-2 report 사진 분리 | `report.html` | ✅ 31KB → 16KB로 정리 |
| P0-4 FCM SW URL 수정 | `firebase-messaging-sw.js` | ✅ URL_MAP + `/app/index.html` 기본값 |
| P0-5 데모 데이터 제거 | `notifications.html`, `history.html` | ✅ 둘 다 정리 |
| P1-4 i18n 통합 | `i18n.js` | ✅ 86KB → 147KB (EXT 흡수) |
| P1-5 sw.js precache 강화 | `sw.js` | ✅ 21개 URL precache |
| P1-7 로그아웃 정리 | `profile.html` | ✅ 정리됨 |

### ⚠️ 본 작업으로 처리해야 할 잔여 항목

| 이슈 | 파일 | 문제 |
|---|---|---|
| **P0-3** 사진 업로드 분리 | `inspect.html` | submitCheck가 `photo_count`만 전송, 사진 자체가 서버에 안 감 |
| **P0-3** 동일 패턴 | `construction_inspect.html` | 1차 보강에서 거의 미반영 (31.8KB → 31.7KB) |
| **P0-6** dead code 삭제 | `camera.html`, `test.txt` | 파일 삭제 필요 |
| Auth 적용 점검 | `tbm.html`, `corrective.html`, `work_request.html` | TAI.apiFetch 사용 여부 확인 |

---

## TASK 1. inspect.html 사진 업로드 분리 (P0-3)

### 현재 코드 (문제 지점)

```js
async function submitCheck(){
  ...
  const items=_items.map(it=>({
    name:it.name,
    result:_results[it.id]?.val||'ok',
    memo:_results[it.id]?.memo||'',
    photo_count:(_results[it.id]?.photos||[]).length   // ← 개수만
  }));
  ...
}
```

### 변경 후

`submitCheck()` 함수를 다음과 같이 교체:

```js
async function submitCheck(){
  const btn=document.getElementById('submitBtn');
  btn.disabled=true;
  btn.textContent=t('saving');

  // 각 item 사진을 서버에 먼저 업로드 → URL 확보
  const items = [];
  for (const it of _items) {
    const r = _results[it.id] || {};
    const photo_urls = [];
    const photos = r.photos || [];
    for (let i = 0; i < photos.length; i++) {
      try {
        const file = TAI.dataUrlToFile(photos[i], `${it.id}_${i+1}.jpg`);
        const up = await TAI.uploadPhoto(file, 'inspection', {
          factory_id: user.factory_id,
        });
        photo_urls.push(up.url);
      } catch (e) {
        // 사진 일부 실패해도 점검 자체는 계속 진행
        console.warn('photo upload failed', it.id, i, e);
      }
    }
    items.push({
      name: it.name,
      result: r.val || 'ok',
      memo: r.memo || '',
      photo_urls,                          // 신규: URL 배열
      photo_count: photo_urls.length,      // 백엔드 미배포 시 호환용 (당분간 유지)
    });
  }

  const body = {
    phone: user.phone || '',
    worker_id: user.worker_id || null,
    factory_id: user.factory_id || null,
    schedule_id: _scheduleId || null,
    inspection_type: isCon ? 'BEFORE_WORK_CON' : 'BEFORE_WORK',
    items,
    submitted_at: new Date().toISOString(),
  };
  _lastBody = body;

  let saved = false;
  try {
    const res = await TAI.apiFetch('/worker-check/submit', {
      method: 'POST',
      body: JSON.stringify(body),
    });
    if (res.ok) saved = true;
  } catch (e) {}

  if (!saved) {
    TAI.queuePush('check', body);
    document.getElementById('retryBar').style.display = '';
  }

  // 활동 로그 (기존 로직 유지)
  const acts = JSON.parse(localStorage.getItem('tai_activities') || '[]');
  const badCount = items.filter(i => i.result === 'bad').length;
  acts.unshift({
    type: badCount ? 'bad' : 'ok',
    icon: badCount ? '⚠️' : '✅',
    title: t('inspect_title') + ' ' + t('inspect_done_ok_title').split('!')[0],
    sub: badCount ? `${t('inspect_done_issues_lbl')} ${badCount}건` : 'OK',
    time: new Date().toLocaleTimeString('ko-KR', {hour:'2-digit', minute:'2-digit'}),
  });
  localStorage.setItem('tai_activities', JSON.stringify(acts.slice(0, 10)));

  showDone(items.filter(i => i.result === 'bad').map(i => i.name), saved);
}
```

### 핵심 변경
- 각 사진(dataURL)을 `TAI.dataUrlToFile()` → `TAI.uploadPhoto()` 시퀀스로 서버 업로드
- 실패 사진은 console.warn만 하고 점검은 계속 (사진 한장 실패로 전체 점검 차단 금지)
- items에 `photo_urls` 배열 추가 (신규 백엔드용)
- `photo_count`도 당분간 유지 (백엔드 P0 배포 전 호환)

### 백엔드 의존성

본 작업은 **`POST /uploads/inspection-photo` 엔드포인트가 배포된 후** 정상 작동.  
백엔드 미배포 상태에서는 photo_urls가 빈 배열이 되고 점검만 정상 제출됨 (graceful degradation).

⚠️ 백엔드 작업지시서: `tai-api/docs/WORK_ORDER_20260424_pwa_backend.md`

---

## TASK 2. construction_inspect.html 동일 패턴 적용

`inspect.html`과 거의 동일한 구조이므로 같은 패턴 적용.

1. `submitCheck()` 함수 위치 찾기
2. TASK 1과 동일한 변경 적용
3. context는 `'inspection'` 그대로 (건설/산업 구분은 inspection_type 필드로)

---

## TASK 3. dead code 삭제 (P0-6, P1-11)

```bash
git rm tadmin/full-version/app/camera.html
git rm tadmin/full-version/app/test.txt
```

**삭제 전 확인**:
- `camera.html`이 어디에서도 import되거나 location.href로 호출되지 않는지 grep
  ```bash
  grep -rn "camera.html" tadmin/full-version/
  ```
- 결과 0건이면 삭제 안전

---

## TASK 4. Auth 적용 점검 (tbm/corrective/work_request)

다음 3개 파일에서 검증:

```bash
grep -n "TAI.apiFetch\|fetch(API" tadmin/full-version/app/tbm.html
grep -n "TAI.apiFetch\|fetch(API" tadmin/full-version/app/corrective.html
grep -n "TAI.apiFetch\|fetch(API" tadmin/full-version/app/work_request.html
```

**기준**:
- `fetch(API` 패턴이 남아있으면 → `TAI.apiFetch` 호출로 교체
- `Authorization` 헤더 수동 추가 코드 있으면 제거 (apiFetch가 자동 처리)
- 401 처리 코드 있으면 제거 (apiFetch가 자동 처리)

각 파일에서 변경된 부분만 minimal diff로 커밋.

---

## TASK 5. 검증 (배포 후)

main에 push되면 Cloudflare Pages 자동 배포. 5분 후:

1. `https://safe.taieng.co.kr/app/inspect.html` 모바일 접속
2. 점검 항목 1개 "이상" 선택 → 사진 1장 첨부 → 제출
3. 브라우저 DevTools → Network 탭에서 다음 확인:
   - `POST /uploads/inspection-photo` 요청 발생 (multipart)
   - `POST /worker-check/submit` body에 `photo_urls: ["https://..."]` 포함
4. 백엔드 미배포 상태이면 `/uploads/inspection-photo` 404 → 점검은 정상 제출 확인

---

## 커밋 규칙

각 TASK 별도 커밋 권장:

```
fix(P0-3): inspect.html 사진 업로드를 photo_urls 방식으로 분리
fix(P0-3): construction_inspect.html 동일 패턴 적용
chore(P0-6): camera.html dead code 삭제
chore(P1-11): test.txt 삭제
fix: tbm/corrective/work_request에 TAI.apiFetch 적용
```

---

## 체크리스트

- [ ] `inspect.html` submitCheck 사진 업로드 분리
- [ ] `construction_inspect.html` 동일 패턴 적용
- [ ] `camera.html` 삭제 (호출처 grep 0건 확인 후)
- [ ] `test.txt` 삭제
- [ ] `tbm.html` apiFetch 점검 / 적용
- [ ] `corrective.html` apiFetch 점검 / 적용
- [ ] `work_request.html` apiFetch 점검 / 적용
- [ ] main push → Cloudflare Pages 배포 확인
- [ ] 모바일 실기기 테스트 (사진 첨부 → Network 탭 확인)

---

**작성**: Claude (기획창)  
**실행**: Cursor (프론트창)  
**검증**: 심태왕
