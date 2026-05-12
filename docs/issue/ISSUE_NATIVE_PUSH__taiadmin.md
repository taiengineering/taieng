# ISSUE: 네이티브 푸시 전환 (@capacitor/push-notifications)

**우선순위:** 높음 (출시 후 첫 번째 업데이트)  
**등록일:** 2026-04-29  
**영향:** 앱 종료/백그라운드/로그아웃 시 푸시 알림 미수신  

---

## 현재 상태

- 웹 Firebase SDK (`firebase-messaging-sw.js`) 사용 중
- `@capacitor/push-notifications` 플러그인 설치됨 (package.json) 그러나 **코드에서 미사용**
- 앱이 열려 있을 때만 푸시 수신 가능

## 문제

| 상황 | 웹 푸시 (현재) | 네이티브 푸시 (목표) |
|---|---|---|
| 앱 열려 있음 (포그라운드) | ✅ | ✅ |
| 앱 백그라운드 | ❌ 불안정 | ✅ |
| 앱 완전 종료 (killed) | ❌ 안 옴 | ✅ |
| 로그아웃 후 | ❌ 불안정 | ✅ |
| 잠금화면 알림 | ❌ | ✅ |

안전관리 앱 특성상 **긴급 알림은 앱 상태와 무관하게 반드시 도착**해야 함.

## 작업 범위

### 프론트엔드 (tai-admin)

1. `index.html`의 `registerFCM()` 함수를 네이티브 플러그인으로 전환:

```javascript
const IS_NATIVE = !!window.Capacitor?.isNativePlatform();

async function registerFCM() {
  if (IS_NATIVE) {
    // 네이티브 Capacitor 푸시
    const { PushNotifications } = Capacitor.Plugins;
    
    const perm = await PushNotifications.requestPermissions();
    if (perm.receive !== 'granted') return;
    
    await PushNotifications.register();
    
    PushNotifications.addListener('registration', async (token) => {
      localStorage.setItem('tai_fcm_token', token.value);
      await fetch(API + '/workers/fcm-token', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          fcm_token: token.value,
          phone: _user?.phone,
          platform: 'android'
        })
      });
    });
    
    PushNotifications.addListener('pushNotificationReceived', (notification) => {
      // 포그라운드 알림 처리
      showToast('🔔 ' + (notification.title || '') + ' ' + (notification.body || ''));
    });
    
    PushNotifications.addListener('pushNotificationActionPerformed', (action) => {
      // 알림 클릭 시 처리
      const url = action.notification?.data?.url;
      if (url) location.href = url;
    });
    
  } else {
    // 기존 웹 푸시 (브라우저 접속 시)
    // 현재 firebase-messaging 코드 유지
  }
}
```

2. `doLogout()`에서 FCM 토큰 삭제하지 않도록 확인 (현재 logoutClean이 tai_fcm_token을 삭제하는데, 서버 토큰은 유지되므로 문제 없음. 단 네이티브 전환 후에도 동일 동작 유지)

### 백엔드 (tai-api)

- 변경 없음. `POST /workers/fcm-token`과 `POST /workers/send-push`는 웹/네이티브 구분 없이 동일하게 동작함. `platform` 필드로 구분 가능.

### Android 빌드

- `google-services.json`이 `android/app/`에 이미 있는지 확인 필요
- 없으면 Firebase Console → 프로젝트 설정 → Android 앱 → `google-services.json` 다운로드 → 배치
- 리빌드 1회 필요 (네이티브 플러그인 코드 반영)

### 테스트 체크리스트

- [ ] 앱 포그라운드에서 푸시 수신
- [ ] 앱 백그라운드에서 푸시 수신 (잠금화면 표시)
- [ ] 앱 완전 종료(kill) 후 푸시 수신
- [ ] 로그아웃 후 푸시 수신
- [ ] 알림 클릭 → 앱 열림 → 해당 페이지 이동
- [ ] 토큰 갱신 시 서버 재등록

## 관련 파일

- `tadmin/full-version/app/index.html` — registerFCM() 함수
- `tadmin/full-version/app/_utils.js` — logoutClean()
- `routers/fcm.py` — FCM 토큰 등록/발송
- `package.json` — @capacitor/push-notifications (이미 설치됨)
- `android/app/google-services.json` — Firebase 설정

## 예상 소요

- 프론트 코드 전환: 2~3시간
- 빌드 + 테스트: 1~2시간
- Play Store 재배포: 심사 3~7일
