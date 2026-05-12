# 출시 준비도 종합 점검 (2026-04-25)

**점검 시점**: 환경 이전 완료 직후  
**점검 방법**: GitHub MCP로 main/dev 브랜치 직접 검증  
**판정**: 🟡 **출시 준비 미완료** (핵심 P0 잔여)

---

## 📊 한눈에 보는 점수

| 영역 | 진척도 | 상태 |
|---|---|---|
| 인프라/환경 | 100% | ✅ 완료 |
| Play Console 가입 | 50% | ⏳ 본인확인 대기 |
| Capacitor 환경 | 25% | ⏸️ Phase 1-1, 1-2 완료, Keystore 대기 |
| **PWA 프론트 P0/P1** | **75%** | 🔴 **사진 업로드 핵심 미완** |
| **백엔드 P0** | **0%** | 🔴 **착수 안 함** |
| 출시 자료 | 30% | ⏳ 일부 (아이콘만) |
| **종합** | **약 50%** | 🟡 절반 |

---

## 1️⃣ PWA 프론트 (tai-admin/main)

### ✅ 완료 (1차 보강 PR `69d030e` + 2차 작업)

| 이슈 | 검증 방법 | 결과 |
|---|---|---|
| P1-1 _utils.js 신설 | 파일 존재 + 함수 5개 확인 | ✅ apiFetch/uploadPhoto/queuePush/queueFlush/logoutClean |
| P0-1 emergency 실패처리 | 파일 크기 16KB→9.8KB | ✅ |
| P0-2 report 사진 분리 | 파일 크기 31KB→16KB | ✅ |
| P0-4 firebase-messaging-sw URL | URL_MAP + /app/ 경로 | ✅ |
| P0-5 데모 데이터 제거 | notifications/history 정리 | ✅ |
| P0-6 camera.html, test.txt 삭제 | 파일 디렉토리 검색 | ✅ |
| P1-4 i18n EXT 통합 | 86KB→147KB | ✅ |
| P1-5 sw.js precache 강화 | 21개 URL precache | ✅ |
| P1-7 로그아웃 정리 | profile.html 정리 | ✅ |

### 🔴 미완료 (출시 차단 수준)

#### P0-3 사진 업로드 분리 — **inspect.html, construction_inspect.html**

`inspect.html` 코드 직접 확인 결과:

```js
async function submitCheck(){
  const items=_items.map(it=>({
    name:it.name,
    result:_results[it.id]?.val||'ok',
    memo:_results[it.id]?.memo||'',
    photo_count:(_results[it.id]?.photos||[]).length    // ← 사진 개수만
  }));
  // photo_urls 배열 생성 코드 없음
  // TAI.uploadPhoto 호출 흔적 없음
}
```

**영향**:
- 작업자가 이상 발견 시 찍은 증거 사진이 서버에 저장 안 됨
- localStorage에만 dataURL로 쌓임 → iOS 5MB 한도 도달 시 손실
- **법적 증빙 불가** (산안법 §52 보고 시 사진 첨부 의무 무력화)

`_utils.js`에 `uploadPhoto`, `dataUrlToFile`이 있지만 inspect.html이 호출 안 함.
construction_inspect.html은 1차 보강에서 거의 변화 없음 (동일 패턴 의심).

#### Auth 적용 점검 미실행

`tbm.html`, `corrective.html`, `work_request.html`이 `TAI.apiFetch`를 사용하는지 확인되지 않음. 1차 보강에서 변화 미미.

---

## 2️⃣ 백엔드 (tai-api/dev)

### 🔴 P0 전부 미시작

GitHub MCP로 routers/ 디렉토리 직접 검증:

| 필요 엔드포인트 | 파일 | 상태 |
|---|---|---|
| POST `/uploads/inspection-photo` | `routers/uploads.py` | **❌ 파일 없음** |
| POST `/emergency/report` | `routers/emergency.py` | **❌ 파일 없음** |
| POST `/safety-reports` | `routers/safety_reports.py` | **❌ 파일 없음** |
| POST `/worker-check/submit` | `routers/worker_check.py` | ✅ 존재 (4.6KB), Auth 추가 필요 |
| POST `/tbm/sign` | `routers/tbm.py` | ✅ 존재 (17.7KB), Auth 추가 필요 |
| GET `/notifications` | `routers/notifications.py` | ✅ 존재 (15KB), Auth 추가 필요 |
| POST `/workers/fcm-token` | `routers/fcm.py` | ✅ 존재 (7.2KB), Auth 추가 필요 |

### 영향 (프론트 ↔ 백엔드 의존성)

```
프론트 P0-2 (report.html 사진 분리) 
  ↓ 호출
백엔드 POST /uploads/inspection-photo
  ↓ 미구현
404 응답 → 프론트 graceful degradation으로 사진 없이 신고만 제출
  ↓
실제 사용자 입장에서: "사진 첨부했는데 서버에 안 보임"
```

**현재 상태**: 프론트가 사진 업로드 시도해도 백엔드 404. 사진 전송 기능 자체가 작동 안 함.

---

## 3️⃣ Play Console

### ✅ 완료
- 조직 계정 가입
- 개발자 프로필 입력 (조직명/주소/연락처)
- 개발자 아이콘 + 헤더 이미지 업로드
- 등록비 $25 결제
- 경력 자기소개 제출 (1,000자, 하이브리드 앱 기준)

### ⏳ 대기
- **본인 확인 (Identity Verification)** — 메일 미수신 (확인 필요)
- **조직 검증 (D-U-N-S)** — D-U-N-S 발급 상태 미확인
- 최종 승인 (보통 2~14일)

### 🔴 매일 체크 필수
이전 Webis Co., Ltd. 계정이 "기한 전 계정 확인 미완료" 사유로 삭제됨.
같은 사유 재발 절대 금지. **24시간 내 응답 원칙.**

---

## 4️⃣ Capacitor 하이브리드 앱

### ✅ Phase 1-1 + 1-2 완료
- Node 20 LTS, JDK 17, Android Studio 설치
- Android SDK API 34, 33, Build-Tools 등
- 환경변수 설정 (`$ANDROID_HOME`)
- Firebase Console에 Android 앱 등록 (`kr.co.taieng.safe`)
- `google-services.json` 다운로드 (단, SHA-1 추가 후 재다운로드 필요)

### ⏸️ Phase 1-3 대기 (Keystore)
🔴 **가장 중요한 단계**. 분실 시 앱을 영구 업데이트 불가.

진행 안 됨:
- `tai-safe-release.keystore` 생성
- 1Password 저장
- 3중 백업 (1Password + 클라우드 + USB)
- SHA-1, SHA-256 추출
- Firebase에 SHA-1 추가
- google-services.json 재다운로드

### ⏸️ Phase 2~5 미시작
- Phase 2: Cursor mobile/ 프로젝트 스캐폴딩
- Phase 3: 네이티브 플러그인 + 코드 분기
- Phase 4: 빌드 & 테스트
- Phase 5: Digital Asset Links

---

## 5️⃣ 출시 자료 (Play Store 등록 화면)

| 항목 | 상태 |
|---|---|
| 앱 아이콘 (512×512) | ✅ Play Console 업로드됨 |
| 헤더 이미지 (4096×2304) | ✅ Play Console 업로드됨 |
| 앱 이름 | ⏳ "TAI Safe" 결정 |
| 짧은 설명 (80자) | ❌ 미작성 |
| 긴 설명 (4,000자) | ❌ 미작성 |
| 기능 그래픽 (1024×500) | ❌ 미제작 |
| 스크린샷 (최소 2장) | ❌ 미준비 |
| 콘텐츠 등급 설문 | ❌ 미진행 |
| **개인정보처리방침 URL** | ❌ **미작성 (taieng.co.kr/privacy 필요)** |
| **데이터 안전(Data Safety) 섹션** | ❌ **미작성 (출시 거절 1순위 사유)** |

---

## 🎯 출시까지 잔여 작업 (우선순위)

### 🔴 P0 — 출시 직접 차단 (즉시 진행)

1. **PWA 프론트 P0-3** (Cursor 작업)
   - `inspect.html` submitCheck에 사진 업로드 분리
   - `construction_inspect.html` 동일 패턴
   - 작업지시서: `docs/WORK_ORDER_20260425_pwa_frontend_finish.md`
   - 소요: 30~60분

2. **백엔드 P0** (Claude Code 작업)
   - `routers/uploads.py` 신설 (`/uploads/inspection-photo`)
   - `routers/emergency.py` 신설 (`/emergency/report`)
   - `routers/safety_reports.py` 신설 (`/safety-reports`)
   - `routers/worker_check.py` Auth 추가
   - `routers/tbm.py` Auth 추가
   - 작업지시서: `tai-api/docs/WORK_ORDER_20260424_pwa_backend.md`
   - 소요: 4~6시간

3. **Keystore 생성** (본인 직접, 집중)
   - 1Password 노트 + 3중 백업
   - SHA-1, SHA-256 추출
   - Firebase 등록
   - 소요: 30분

4. **Play Console 본인확인 메일 응답**
   - 매일 메일 체크
   - 메일 도착 시 24시간 내 응답
   - 서류 미리 준비: 신분증, 사업자등록증, 법인등기부등본 (700원)

### 🟠 P1 — 출시 자료 (Keystore 후 시작)

5. **개인정보처리방침 페이지** (`taieng.co.kr/privacy`)
   - GDPR + 개인정보보호법 부합
   - 수집 항목, 보관 기간, 제3자 제공, 권리 행사 방법
   - 소요: 2~3시간

6. **앱 설명 + 데이터 안전 섹션 작성**
   - 짧은 설명 80자
   - 긴 설명 4,000자 (산안법 근거 강조)
   - Data Safety 정확 기재 (수집/공유 데이터 모두)
   - 소요: 2~3시간

7. **스크린샷 + 기능 그래픽**
   - 모바일 실기기에서 주요 화면 캡처 (5~7장)
   - 1024×500 기능 그래픽 제작
   - 소요: 2시간

### 🟡 P2 — Capacitor 빌드 (P0 + 출시자료 후)

8. **Capacitor Phase 2**: mobile/ 프로젝트 스캐폴딩
9. **Capacitor Phase 3**: 네이티브 플러그인 + 코드 분기
10. **Capacitor Phase 4**: AAB 빌드
11. **Capacitor Phase 5**: Digital Asset Links

### 🟢 P3 — 마무리

12. Closed Testing 등록 (테스터 20명, 14일 대기)
13. Production 심사 제출
14. 승인 후 출시

---

## ⏱️ 출시까지 예상 일정

| 작업 | 시간 | 누적 |
|---|---|---|
| PWA 프론트 P0-3 | 1시간 | Day 1 |
| 백엔드 P0 (5개 엔드포인트) | 6시간 | Day 1 |
| Keystore 생성 | 30분 | Day 1 |
| 개인정보처리방침 | 3시간 | Day 2 |
| 앱 설명 + Data Safety | 3시간 | Day 2 |
| 스크린샷 + 그래픽 | 2시간 | Day 2 |
| Capacitor Phase 2~3 | 8시간 | Day 3~4 |
| Capacitor Phase 4 (빌드) | 4시간 | Day 5 |
| Capacitor Phase 5 (Digital Asset Links) | 2시간 | Day 5 |
| Play Console 본인확인 응답 대기 | (병렬, 2~14일) | — |
| Closed Testing | 14일 | Day 6~20 |
| Production 심사 | 7일 | Day 21~27 |
| **출시** | | **약 4주 후 (5월 22일경)** |

병목: Play Console 검증(최대 2주) + Closed Testing(14일).
실제 작업 시간은 **3~4일 집중**이면 충분.

---

## 🎯 결론

### 현재 상태
**출시 준비 약 50%**. 환경/문서/Play Console 가입은 OK지만, **실제 앱 동작에 필요한 핵심 P0가 미완** (사진 업로드 + 백엔드 5개 엔드포인트).

### 즉시 해야 할 일 (오늘/내일)
1. ☑️ Cursor에 PWA P0-3 작업지시서 전달
2. ☑️ Claude Code에 백엔드 P0 작업지시서 전달
3. ☑️ Keystore 생성 (집중 시간 30분)
4. ☑️ Play Console 메일함 매일 확인

### 출시 차단 핵심
- **사진 업로드 미작동** = 산안법 증빙 의무 미준수
- **이상신고 백엔드 미구현** = 핵심 기능 작동 안 함
- **개인정보처리방침 페이지 없음** = Play Store 심사 거절

위 3개가 해결돼야 의미 있는 베타 테스트 가능.

---

**작성**: Claude (기획창)  
**점검 방법**: GitHub MCP 직접 검증  
**다음 점검**: P0 작업 완료 후 재점검
