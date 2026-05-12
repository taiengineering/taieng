# PWA 보강 작업 총괄 (2026-04-24)

두 세션(Claude Code / Cursor) 동시 진행. 이 문서는 두 지시서의 **의존성/순서**만 정리.

---

## 문서 위치

| 문서 | 레포 | 경로 | 대상 |
|---|---|---|---|
| 점검 리뷰 | tai-admin | `docs/PWA_APP_REVIEW_20260424.md` | — |
| 백엔드 오더 | **tai-api** (dev) | `docs/WORK_ORDER_20260424_pwa_backend.md` | **Claude Code** |
| 프론트 오더 | tai-admin (main) | `docs/WORK_ORDER_20260424_pwa_frontend.md` | **Cursor** |

---

## 병렬/순차 실행 플로우

```
┌─ Claude Code (tai-api dev) ────────────────────┐
│  T1: /uploads/inspection-photo 신설            │
│  T2: /emergency/report 보강 + FCM              │
│  T3: /safety-reports 보강 (photo_urls)         │
│  T4: /worker-check/submit 보강                 │
│  T5: /tbm/sign Auth                            │
│  T6: /notifications Auth                       │
│  T7: /workers/fcm-token Auth                   │
│         ↓                                       │
│  main 머지 → Railway 배포 → /health 200 확인   │
└────────────────────────────┬───────────────────┘
                             │
                             ↓ (배포 완료 통보)
┌─ Cursor (tai-admin main) ──────────────────────┐
│  [PART A] 독립 작업 - 즉시 착수 가능           │
│   - _utils.js 신설                             │
│   - firebase-messaging-sw.js URL 수정          │
│   - notifications/history 데모 제거            │
│   - camera.html / test.txt 삭제                │
│   - sw.js precache 확대                        │
│   - i18n 언어 감지                             │
│   - 로그아웃 정리                              │
│         ↓                                       │
│  [PART B] 백엔드 배포 후 착수                  │
│   - emergency.html 실패 처리                   │
│   - report.html 사진 분리 업로드               │
│   - inspect/construction_inspect 사진 분리     │
│   - tbm/corrective/work_request Auth 적용      │
│         ↓                                       │
│  [PART C] i18n 통합                            │
│   - 7개 페이지 EXT → i18n.js 통합              │
└────────────────────────────────────────────────┘
```

---

## 동시 진행 타이밍

- **Day 1 오전**: Claude Code T1~T4 착수 / Cursor PART A 착수
- **Day 1 오후**: 백엔드 dev → main 머지 + Railway 배포 / Cursor PART A 완료
- **Day 2**: Cursor PART B 착수 (백엔드 엔드포인트 연동)
- **Day 3**: Cursor PART C + 최종 QA

---

## 인터페이스 합의 (양측 반드시 준수)

### 사진 업로드 계약
- 엔드포인트: `POST /uploads/inspection-photo`
- 인증: `Authorization: Bearer {access_token}`
- 요청: `multipart/form-data` — `file`, `context`, `inspection_id`, `factory_id`, `site_id`
- 응답: `{url, path, size, mime}`
- 프론트는 `TAI.uploadPhoto(file, context, ids)` 래퍼 사용

### 신고 번호 계약
- 모든 신고(emergency/report) 번호는 **서버가 발급**
- 형식: `EMG-YYYYMMDD-{SEQ}`, `RPT-YYYYMMDD-{SEQ}`
- 프론트는 절대 `Date.now()`로 생성 금지
- 오프라인 큐에서 저장된 항목만 `OFFLINE-xxx` 임시 표시, 재전송 성공 시 실제 번호로 교체

### 사진 전송 계약
- **기존**: `photos: [base64...]` 또는 `photo_count: N`
- **신규**: `photo_urls: [url...]` 
- `/worker-check/submit`의 경우 각 item에 `photo_urls` 필드
- Base64는 클라이언트 미리보기 전용. 서버 전송 시 반드시 URL 변환

### 오프라인 큐 계약
- 키 prefix: `tai_queue_{kind}_{timestamp}` (kind: emergency | report | check | tbm 등)
- 최대 보관: kind당 20개 (초과 시 오래된 것부터 삭제)
- 페이지 로드 시 `TAI.queueFlush(kind, endpoint)` 자동 호출

---

## 완료 기준 (심태왕 최종 확인)

- [ ] 백엔드: `/uploads/inspection-photo` 실 파일 업로드 → Supabase `inspections` 버킷 확인
- [ ] 백엔드: `/emergency/report`로 Authorization 없이 호출 시 401
- [ ] 백엔드: `/safety-reports` `photo_urls` 배열로 정상 저장
- [ ] 프론트: `safe.taieng.co.kr/app/inspect.html`에서 사진 찍고 제출 → 서버 DB에 URL 저장 확인
- [ ] 프론트: 비행기 모드에서 긴급신고 → 오프라인 큐 저장 + 사용자 경고 문구 노출 → 네트워크 복구 시 자동 재전송
- [ ] 프론트: 로그아웃 후 재로그인 시 이전 사용자 서명/이력 노출 없음
- [ ] 프론트: 첫 방문자가 notifications/history에서 데모 알림 안 봄
- [ ] 프로덕션 `/health` 200 유지

---

## 리스크 & 롤백

- **백엔드 배포 실패 시**: main 이전 커밋으로 롤백, 프론트는 PART B 대기
- **프론트 PART B 후 문제 발생 시**: `_utils.js`의 `TAI.apiFetch`에 feature flag 추가해 기존 fetch로 fallback 가능
- **사진 업로드 쿼터 초과 시**: Supabase `inspections` 버킷 사이즈 모니터링 (현재 용량 미상 — 백엔드가 먼저 확인할 것)

---

**책임자**: 심태왕  
**조율자**: Claude (기획창)  
**실행**: Claude Code + Cursor 병렬
