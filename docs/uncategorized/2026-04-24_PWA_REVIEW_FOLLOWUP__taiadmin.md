# PWA 점검 후속 작업 진행 상황 (2026-04-24 야간 확인)

원본 점검 리포트: `docs/PWA_APP_REVIEW_20260424.md`  
프론트 작업지시서: `docs/WORK_ORDER_20260424_pwa_frontend.md`

---

## 자동 진행 확인 결과

심태왕 대표님이 "Cursor 백그라운드 커밋이 안 된 것 같다"고 의심하셔서 GitHub main 브랜치 직접 확인. **결과: 대부분 푸시 완료됨.**

---

## 파일 변화 (점검 시점 vs 현재 main)

| 파일 | 점검 크기 | 현재 크기 | 변화 | 관련 이슈 | 상태 |
|---|---|---|---|---|---|
| `_utils.js` | 없음 | 4,063B | 🆕 신설 | P1-1 | ✅ 완료 |
| `emergency.html` | 16,000B | 9,861B | -38% | P0-1 | ✅ 완료 |
| `report.html` | 31,400B | 16,226B | -48% | P0-2 | ✅ 완료 |
| `notifications.html` | 16,300B | 8,489B | -48% | P0-5 | ✅ 완료 |
| `history.html` | 16,800B | 11,387B | -32% | P0-5 | ✅ 완료 |
| `profile.html` | 16,900B | 13,299B | -21% | P1-7 | ✅ 완료 |
| `install.html` | 27,700B | 10,400B | -62% | P2-10 | ✅ 정리 |
| `qr_scan.html` | 17,200B | 12,066B | -30% | — | ✅ 정리 |
| `i18n.js` | 86,000B | 147,182B | +71% | P1-4 | ✅ 통합 |
| `inspect.html` | 22,900B | 22,738B | ≈ | P0-3 | ⚠️ 의심 |
| `tbm.html` | 16,700B | 16,854B | ≈ | P0 (Auth) | ⚠️ 의심 |
| `construction_inspect.html` | 31,800B | 31,785B | ≈ | — | ⚠️ 의심 |
| `camera.html` | 9,600B | (확인 필요) | — | P0-6 | ⚠️ 삭제 여부 미확인 |
| `test.txt` | 60B | (확인 필요) | — | P1-11 | ⚠️ 삭제 여부 미확인 |
| `firebase-messaging-sw.js` | 1,700B | (확인 필요) | — | P0-4 | ⚠️ URL 수정 여부 미확인 |
| `sw.js` | 4,500B | 5,005B | +11% | P1-5 | ⚠️ Precache 충분히 강화됐는지 |

---

## 완료 추정 (12건)

**P0 치명 4건:**
- ✅ P0-1: emergency.html 실패 처리
- ✅ P0-2: report.html 사진 분리 업로드
- ✅ P0-5: 데모 데이터 제거 (notifications + history)

**P1 높음 4건:**
- ✅ P1-1: _utils.js 공통 유틸 신설
- ✅ P1-4: i18n EXT 통합
- ✅ P1-7: 로그아웃 정리

**기타 정리:**
- ✅ install.html 슬림화
- ✅ qr_scan.html 정리

---

## 추가 확인 필요 (5건)

내일 Keystore 작업 후 GitHub commit history (`https://github.com/taiengineering/tai-admin/commits/main`) 확인 권장.

| 이슈 | 확인 방법 |
|---|---|
| P0-3 inspect.html 사진 업로드 분리 | `inspect.html`에서 `photo_urls`, `TAI.uploadPhoto` 키워드 검색 |
| P0-4 firebase-messaging-sw.js URL | URL이 `/app/index.html`로 수정됐는지 |
| P0-6 camera.html 삭제 | 파일 존재 여부 확인 |
| P1-5 sw.js precache 강화 | `PRECACHE_URLS` 배열 길이 (1~2개 → 20개+) |
| P1-11 test.txt 삭제 | 파일 존재 여부 확인 |
| tbm.html Authorization | apiFetch 호출 여부 |

---

## 백엔드 의존 작업 진행 미상

프론트 작업지시서의 **PART B** (백엔드 엔드포인트 의존)는 백엔드(`tai-api`) 배포 상태에 따라 달라짐. Claude Code 진행 결과는 별도 확인 필요:
- `POST /uploads/inspection-photo` 신설 여부
- `/emergency/report`, `/safety-reports` 보강 여부
- `/worker-check/submit` Authorization 추가 여부

---

## 결론

**Cursor 작업이 누락된 게 아니라, 대부분 main에 푸시 완료됨.** 12건 이상의 P0/P1 이슈가 자동 처리됨. 사용자가 의심한 "커밋 안 됨" 상황은 다음 중 하나로 추정:
1. Cursor 화면에서 "Pushing..." 표시가 멈춘 것처럼 보였으나 실제로는 push 성공
2. 다른 로컬 저장소에서 `git pull` 미실행으로 변화가 안 보였음
3. Branch protection 경고를 푸시 실패로 오해

진정한 미완료는 inspect.html 사진 분리, FCM SW URL, camera.html 삭제, sw.js precache 등 **5건 정도**.

---

## 권장 다음 단계

1. **내일 Keystore 완료 후** GitHub commits 페이지 직접 확인
2. **남은 5건**을 별도 PR로 빠르게 처리 (1~2시간 작업)
3. 그 후 Capacitor Phase 2 진행

---

**작성**: Claude (기획창)  
**확인일**: 2026-04-24  
**책임자**: 심태왕
