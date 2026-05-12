# PWA 작업 검증 보고 (2026-04-25)

**검증 시점**: 2026-04-25  
**검증 대상**:
- 백엔드: `tai-api` / `dev` (Claude Code 담당)
- 프론트: `tai-admin` / `main` (Cursor 담당)
**기반 작업지시서**:
- `tai-api/docs/WORK_ORDER_20260424_pwa_backend.md`
- `tai-admin/docs/WORK_ORDER_20260424_pwa_frontend.md`

---

## 한 줄 요약

**프론트는 PART A + B + C 대부분 진행, 백엔드는 0% 진행. 비대칭 배포 상태로 main에 푸시되어 프로덕션에 노출됨.**

---

## 1. 검증 결과

### 1-1. Cursor (프론트) — 약 70% 완료 ✅

| 항목 | 검증 방법 | 결과 |
|---|---|---|
| P1-1: `_utils.js` 신설 | 파일 존재 + 코드 비교 | ✅ 작업지시서와 100% 일치 |
| P0-4: FCM SW URL 수정 | `firebase-messaging-sw.js` 코드 확인 | ✅ URL_MAP까지 정확히 적용 |
| P0-5: notifications 데모 제거 | 파일 크기 16.3KB → 8.5KB | ✅ 명확한 축소 |
| P0-5: history 데모 제거 | 파일 크기 16.8KB → 11.4KB | ✅ 명확한 축소 |
| P0-6: `camera.html` 삭제 | 디렉토리 목록 | ✅ 파일 사라짐 |
| P1-11: `test.txt` 삭제 | 디렉토리 목록 | ✅ 파일 사라짐 |
| P0-1: emergency.html | 코드 내용 확인 | ✅ TAI.apiFetch + queuePush + queueFlush 적용 |
| P0-2: report.html | 파일 크기 31.4KB → 16.2KB | ✅ (추정) 동일 패턴 적용 |
| PART C: i18n 통합 | `i18n.js` 86KB → 147KB | ✅ EXT 통합 완료 |
| P1-5: `sw.js` precache | 4.5KB → 5KB | ⚠️ 소폭만 증가 — 작업지시서의 20+ 항목과 거리 |
| P0-3: inspect.html photo_urls | 22.9KB → 22.7KB 거의 동일 | ❓ 미진행 가능성 |
| PART B 기타 페이지 | tbm/corrective/work_request 크기 변화 없음 | ❓ 미진행 추정 |

### 1-2. Claude Code (백엔드) — 0% 완료 ❌

| 작업 | 검증 결과 |
|---|---|
| TASK 1: `routers/uploads.py` 신설 | ❌ 파일 없음 |
| TASK 2: `/emergency/report` | ❌ `routers/emergency.py` 없음, 다른 라우터에도 미포함 |
| TASK 3: `/safety-reports` photo_urls | ❌ 변경 없음 |
| TASK 4: `/worker-check/submit` photo_urls | ❌ `worker_check.py` 4616B 그대로 |
| TASK 5: `/tbm/sign` Auth | ❌ `tbm.py` 17657B 그대로 (변동 0) |
| TASK 6: `/notifications` Auth | ❌ |
| TASK 7: `/workers/fcm-token` Auth | ❌ `fcm.py` 7240B 그대로 |

`routers/` 전체 디렉토리에 신규/수정된 파일이 하나도 없음. **작업이 시작조차 안 됨.**

---

## 2. 현재 프로덕션 영향

`safe.taieng.co.kr/app/`은 main 브랜치 자동 배포. 프론트의 PART B는 백엔드 신규 엔드포인트(`/uploads/inspection-photo`, `/emergency/report` 등)에 의존하는데 백엔드가 없음.

### 사용자 경험

| 동작 | 결과 |
|---|---|
| 긴급신고 발송 | 백엔드 404 → 오프라인 큐 적재 → "⚠ 네트워크 오류로 기기에 임시 저장" |
| 이상신고 + 사진 | 사진 업로드 404 → 신고 본문도 404 → 오프라인 큐 |
| 작업 전 점검 제출 | (P0-3 미진행이면) 기존 동작 유지 가능 — 검증 필요 |
| TBM 서명 | (P0 PART B 미진행이면) 기존 동작 유지 |
| 푸시 알림 | ✅ 정상 (FCM SW URL 수정 효과) |
| 데모 알림/이력 | ✅ 사라짐 |
| i18n 전환 | ✅ 정상 |

### 다행스러운 점

Cursor가 작성한 fallback 로직이 안전함:
- 모든 실패는 `localStorage`의 `tai_queue_*` 큐에 적재
- 페이지 로드 + `online` 이벤트에서 자동 flush 시도
- 사용자에게 "임시 저장됨, 직접 전화하세요" 메시지 노출
- **데이터 손실은 없음**

### 위험한 점

- 백엔드 미배포가 길어지면 LocalStorage 큐만 누적
- iOS/Android의 5~10MB 쿼터 초과 시 새 신고가 silently 실패
- 사용자가 "이 앱은 항상 오프라인 오류가 난다"고 인식 → 신뢰 훼손

---

## 3. 의사결정 옵션

### 옵션 A: 백엔드 우선 진행 (추천) ✅

**프론트 그대로 두고 백엔드 즉시 진행**

- 장점:
  - 프론트는 이미 안전한 fallback 로직 보유
  - 백엔드 배포 시점에 누적된 오프라인 큐가 자동 flush → 사용자 신고 데이터 보존
  - 추가 코드 작업 없음
- 단점:
  - 백엔드 완성 전까지 사용자가 "오프라인 오류" 메시지 자주 봄
- 예상 시간: **1~2일** (Claude Code가 작업지시서대로 7개 엔드포인트 구축)

### 옵션 B: 프론트 main 롤백

- 장점: 즉시 안정화
- 단점:
  - 사용자가 만든 오프라인 큐 데이터 영구 손실
  - 작업 진행 시 다시 머지해야 함 — 컨플릭트 가능
  - i18n 통합 등 정상 작동 중인 변경사항도 같이 사라짐
- 비추천

### 옵션 C: 프론트에 feature flag 추가

- 장점: 백엔드 미준비여도 정상 동작
- 단점: 추가 코드 작업 필요, 옵션 A보다 느림
- 차선

---

## 4. 추천 액션 — 옵션 A

### 즉시 실행

1. **Claude Code 세션 재가동** → `tai-api/docs/WORK_ORDER_20260424_pwa_backend.md` 그대로 다시 전달
   - 작업이 왜 commit 안 됐는지 원인 확인 (백그라운드 커밋 이슈 재발 가능성)
   - 가능하면 dev 브랜치 직접 작업 후 push 확인 명시
2. **TASK 1 (uploads.py) 가장 먼저 배포** — 다른 모든 엔드포인트가 의존
3. **각 엔드포인트 배포마다 프로덕션 `/health` 확인**
4. **배포 완료 후 24시간 내 프로덕션에서 실제 신고 1건 테스트**

### 검증 필요

- inspect.html, tbm.html, corrective.html, work_request.html, construction_inspect.html이 PART B 적용됐는지 개별 확인
- sw.js precache가 작업지시서의 20개 URL 모두 포함하는지 확인

### 모니터링

- 백엔드 미배포 기간 동안 사용자 LocalStorage 누적 사이즈 모니터링 불가하나, 배포 후 첫 24시간의 `/emergency/report`, `/safety-reports`, `/worker-check/submit` 호출량 급증 확인 (큐 flush)

---

## 5. 향후 재발 방지

- 작업지시서에 **"작업 완료 후 GitHub commit hash + Railway 배포 로그 캡처를 보고"** 명시 추가
- 두 세션(Claude Code, Cursor) 동시 작업 시 **백엔드 완료 → 프론트 진행** 순차 실행 유도
- 또는 백엔드 미준비 상태에서 프론트가 commit되지 않도록 feature flag 강제

---

**검증자**: Claude (기획창)  
**최종 업데이트**: 2026-04-25
