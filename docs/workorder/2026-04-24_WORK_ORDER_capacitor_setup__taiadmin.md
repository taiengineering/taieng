# WORK ORDER 2026-04-24 · Capacitor 하이브리드 앱 구축

- **목표**: TAI Safe PWA를 Capacitor로 감싸 Android APK/AAB 빌드 → Play Store 제출 준비 완료
- **병렬성**: Play Console 승인 대기(2~14일) 중 전 과정 완료 가능
- **대상**: 심태왕(로컬 환경 + Firebase) + Cursor(코드 작업)
- **레포/브랜치**: `tai-admin` / `main`
- **신설 경로**: `tai-admin/mobile/`
- **관련 문서**:
  - PWA 리뷰: `docs/PWA_APP_REVIEW_20260424.md`
  - Play Console 진행: `docs/PLAY_CONSOLE_SIGNUP_20260424.md`
  - PWA 프론트 오더: `docs/WORK_ORDER_20260424_pwa_frontend.md`

---

## 핵심 결정 사항 (변경 불가)

| 항목 | 값 | 비고 |
|---|---|---|
| 프레임워크 | Capacitor 6.x | Ionic 공식 |
| 패키지 ID | `kr.co.taieng.safe` | **영구 고정** — 변경 시 신규 앱 등록 필요 |
| 앱 이름 | `TAI Safe` | Play Store 표시명은 향후 수정 가능 |
| 최소 Android | API 24 (Android 7.0) | Play Console 최소 요구 수준 |
| 타겟 Android | API 34 (Android 14) | 2026년 Play Store 필수 수준 |
| 배포 형식 | AAB (Android App Bundle) | APK 아님 |
| Firebase 프로젝트 | `tai-safe` (기존 웹 FCM과 동일) | ID: `897890995077` |

---

## 디렉토리 구조 (최종)

```
tai-admin/
├── tadmin/full-version/app/        ← 기존 PWA 21개 파일 (수정 없음, 공용 사용)
└── mobile/                         ← 신설
    ├── package.json                ← Capacitor CLI + 플러그인
    ├── capacitor.config.json       ← 앱 설정
    ├── www/                        ← 빌드 타깃 (PWA 파일 복사본)
    ├── scripts/
    │   └── sync-web.js             ← PWA → www/ 자동 동기화
    ├── android/                    ← npx cap add android 자동 생성
    │   └── app/
    │       ├── google-services.json  ← Firebase Console에서 다운로드
    │       └── release-key.keystore  ← 서명 키 (❗ .gitignore 필수)
    ├── .gitignore
    └── README.md
```

---

## 🔴 Phase 1: 심태왕 직접 작업 (로컬 환경)

Cursor로는 못 하는 GUI/계정 작업.

### 1-1. 로컬 개발 환경 설치 (순서대로)

**Node.js 20 LTS**
- https://nodejs.org 에서 LTS 버전 다운로드
- 설치 후 터미널에서 확인: `node -v` → v20.x.x 이상

**Java JDK 17**
- Capacitor 6.x는 JDK 17 필수
- macOS: `brew install openjdk@17`
- Windows: Adoptium Temurin 17 (https://adoptium.net)
- 확인: `java -version`

**Android Studio (최신)**
- https://developer.android.com/studio 다운로드
- 설치 후 첫 실행:
  - `Android SDK` (API 34, 33, 31 설치)
  - `Android SDK Command-line Tools` 체크 필수
  - `Android Emulator` 설치
  - 환경변수 설정 (macOS `~/.zshrc`, Windows 시스템 환경변수):
    ```
    export ANDROID_HOME=$HOME/Library/Android/sdk   # macOS
    export ANDROID_HOME=%LOCALAPPDATA%\Android\Sdk   # Windows
    export PATH=$PATH:$ANDROID_HOME/platform-tools:$ANDROID_HOME/tools
    ```

**검증 명령어 3종**
```bash
node -v          # v20.x.x
java -version    # 17.x.x
adb version      # Android Debug Bridge
```

모두 정상 응답하면 1-1 완료.

---

### 1-2. Firebase Console에서 Android 앱 등록

기존 웹 FCM이 쓰는 Firebase 프로젝트(`tai-safe`)에 **Android 앱을 추가**합니다.

1. https://console.firebase.google.com → `tai-safe` 프로젝트 선택
2. 톱니바퀴 → 프로젝트 설정 → 하단 "내 앱" → **Android 아이콘 클릭**
3. 입력:
   - **Android 패키지 이름**: `kr.co.taieng.safe` (정확히 일치, 오타 금지)
   - **앱 닉네임**: `TAI Safe Android`
   - **디버그 서명 인증서 SHA-1**: ⏳ **Phase 2 완료 후 입력 (지금 건너뛰기)**
4. **"앱 등록"** 클릭
5. **`google-services.json` 다운로드** → 바탕화면에 임시 보관 (Phase 3에서 사용)
6. 이후 단계 "Firebase SDK 추가"와 "SDK 설치 확인"은 **전부 건너뛰기** (Capacitor가 자동 처리)

⚠️ **지금 단계에서는 google-services.json만 확보하면 됨**. SHA-1은 keystore 만든 후 돌아와서 추가.

---

### 1-3. Keystore 생성 (앱 서명 키)

**이 키를 잃으면 TAI Safe 앱을 영원히 업데이트 못 합니다.** 이중 백업 필수.

터미널에서:
```bash
cd ~/Desktop   # 임시 위치, 나중에 옮김
keytool -genkey -v \
  -keystore tai-safe-release.keystore \
  -alias tai-safe \
  -keyalg RSA \
  -keysize 4096 \
  -validity 10000
```

입력 값 (예시):
```
비밀번호:        (강력한 비밀번호, 1Password에 저장)
First/Last Name: Taewang Shim
Organizational Unit: Development
Organization:     TAI Engineering
City:             Seoul
State:            Seoul
Country Code:     KR
```

**완료 후 즉시:**
1. `tai-safe-release.keystore` 파일을 **1Password의 Secure Note에 첨부**
2. 비밀번호도 같은 노트에 기록
3. 별도 암호화 USB 또는 클라우드(Google Drive 암호화 zip)에 **이중 백업**
4. 바탕화면에서는 삭제 (임시로만)

**SHA-1 / SHA-256 지문 추출** (Firebase와 Digital Asset Links에 사용):
```bash
keytool -list -v -keystore tai-safe-release.keystore -alias tai-safe
```

출력에서 다음을 메모:
- `SHA1: XX:XX:XX:...`  → Firebase Console에 입력
- `SHA256: XX:XX:XX:...` → Digital Asset Links에 입력

---

### 1-4. Firebase에 SHA-1 지문 추가

Phase 1-2에서 등록한 Android 앱으로 돌아가서:
1. Firebase Console → 프로젝트 설정 → 내 앱 → Android 앱 → "SHA 인증서 지문 추가"
2. Phase 1-3에서 추출한 **SHA-1** 붙여넣기
3. 저장 → **google-services.json 다시 다운로드** (SHA 추가된 최신 버전)

---

## 🟡 Phase 2: Cursor 작업 (프로젝트 스캐폴딩)

Phase 1 완료 후 Cursor에게 이 섹션을 전달.

### 2-1. mobile/ 디렉토리 초기화

```bash
cd tai-admin
mkdir mobile && cd mobile

npm init -y
npm install --save @capacitor/core @capacitor/cli @capacitor/android
```

### 2-2. capacitor.config.json 생성

**파일**: `tai-admin/mobile/capacitor.config.json`

```json
{
  "appId": "kr.co.taieng.safe",
  "appName": "TAI Safe",
  "webDir": "www",
  "server": {
    "androidScheme": "https"
  },
  "android": {
    "allowMixedContent": false,
    "webContentsDebuggingEnabled": false
  },
  "plugins": {
    "SplashScreen": {
      "launchShowDuration": 1500,
      "launchAutoHide": true,
      "backgroundColor": "#0d1b2a",
      "androidScaleType": "CENTER_CROP",
      "showSpinner": false
    },
    "PushNotifications": {
      "presentationOptions": ["badge", "sound", "alert"]
    }
  }
}
```

### 2-3. package.json 스크립트 정의

**파일**: `tai-admin/mobile/package.json` — scripts 섹션을 다음으로 교체

```json
{
  "scripts": {
    "sync:web": "node scripts/sync-web.js",
    "sync:android": "npm run sync:web && npx cap sync android",
    "open:android": "npx cap open android",
    "build:android": "npm run sync:android && cd android && ./gradlew bundleRelease",
    "clean": "rm -rf www android node_modules"
  }
}
```

### 2-4. PWA 파일 동기화 스크립트

**파일**: `tai-admin/mobile/scripts/sync-web.js` (신설)

```javascript
#!/usr/bin/env node
// tadmin/full-version/app/ → mobile/www/ 복사
const fs = require('fs');
const path = require('path');

const SRC = path.resolve(__dirname, '../../tadmin/full-version/app');
const DEST = path.resolve(__dirname, '../www');

function copyRecursive(src, dest) {
  if (!fs.existsSync(dest)) fs.mkdirSync(dest, { recursive: true });
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    if (entry.isDirectory()) copyRecursive(srcPath, destPath);
    else fs.copyFileSync(srcPath, destPath);
  }
}

// 기존 www 삭제 후 재복사
if (fs.existsSync(DEST)) fs.rmSync(DEST, { recursive: true });
copyRecursive(SRC, DEST);

// assets/img 아이콘도 복사 (manifest.json 경로 대응)
const ASSETS_SRC = path.resolve(__dirname, '../../tadmin/full-version/assets');
const ASSETS_DEST = path.resolve(__dirname, '../www/assets');
if (fs.existsSync(ASSETS_SRC)) copyRecursive(ASSETS_SRC, ASSETS_DEST);

console.log('✓ Synced PWA → mobile/www/');
```

### 2-5. .gitignore (Keystore 유출 방지)

**파일**: `tai-admin/mobile/.gitignore`

```
node_modules/
www/
android/app/build/
android/build/
android/.gradle/
android/local.properties
android/app/google-services.json
android/app/*.keystore
android/app/*.jks
*.log
.DS_Store
```

⚠️ **google-services.json과 keystore는 절대 git에 커밋하지 말 것**. Play Store 앱 탈취 위험.

### 2-6. Android 프로젝트 추가

```bash
cd mobile
npm run sync:web          # PWA → www/ 복사
npx cap add android       # android/ 디렉토리 자동 생성
```

이 시점에서 `android/app/build.gradle`을 열어 다음 두 줄 확인:
```gradle
minSdkVersion 24
targetSdkVersion 34
```

---

## 🟡 Phase 3: 네이티브 플러그인 + 코드 분기

### 3-1. 플러그인 설치

```bash
cd tai-admin/mobile

# 필수 플러그인 (Priority 1)
npm install \
  @capacitor/camera \
  @capacitor/geolocation \
  @capacitor/push-notifications \
  @capacitor/preferences \
  @capacitor/network \
  @capacitor/app \
  @capacitor/status-bar \
  @capacitor/splash-screen \
  @capacitor/haptics

# 커뮤니티 플러그인 (QR 스캐너)
npm install @capacitor-mlkit/barcode-scanning

npm run sync:android   # Android 프로젝트에 플러그인 반영
```

### 3-2. Firebase 파일 배치

Phase 1-4에서 다운로드한 `google-services.json`을:
```
mobile/android/app/google-services.json
```
위치에 복사. `.gitignore`에 포함돼 있으므로 커밋 안 됨.

### 3-3. _utils.js에 네이티브 분기 추가

**파일**: `tai-admin/tadmin/full-version/app/_utils.js` — PWA 프론트 오더에서 신설되는 파일. **거기에 이 블록을 추가**:

```javascript
// ============================================
// Capacitor 네이티브 브리지
// ============================================

const IS_NATIVE = !!(window.Capacitor && window.Capacitor.isNativePlatform && window.Capacitor.isNativePlatform());

// 카메라 — 기존 dataUrlToFile을 네이티브로 대체
async function takePhotoNative() {
  if (!IS_NATIVE) return null;
  const { Camera } = window.Capacitor.Plugins;
  const image = await Camera.getPhoto({
    quality: 80,
    allowEditing: false,
    resultType: 'uri',
    source: 'CAMERA',
    saveToGallery: false,
  });
  // URI → Blob 변환해 서버 업로드에 사용
  const res = await fetch(image.webPath);
  const blob = await res.blob();
  return new File([blob], `photo_${Date.now()}.jpg`, { type: blob.type });
}

// 위치 — navigator.geolocation보다 정확
async function getLocationNative() {
  if (!IS_NATIVE) return null;
  const { Geolocation } = window.Capacitor.Plugins;
  const pos = await Geolocation.getCurrentPosition({
    enableHighAccuracy: true,
    timeout: 5000,
  });
  return { lat: pos.coords.latitude, lng: pos.coords.longitude };
}

// 푸시 알림 — FCM 토큰 등록 (앱 시작 시 1회)
async function registerPushNative() {
  if (!IS_NATIVE) return;
  const { PushNotifications } = window.Capacitor.Plugins;

  let perm = await PushNotifications.checkPermissions();
  if (perm.receive === 'prompt') perm = await PushNotifications.requestPermissions();
  if (perm.receive !== 'granted') return;

  await PushNotifications.register();

  PushNotifications.addListener('registration', async (token) => {
    localStorage.setItem('tai_fcm_token_native', token.value);
    // 기존 /workers/fcm-token 엔드포인트로 전송 (platform: 'android')
    try {
      await TAI.apiFetch('/workers/fcm-token', {
        method: 'POST',
        body: JSON.stringify({
          fcm_token: token.value,
          platform: 'android',
        }),
      });
    } catch (e) {}
  });

  PushNotifications.addListener('pushNotificationReceived', (notif) => {
    // 포그라운드 알림 — 기존 toast 재사용
    if (typeof showToast === 'function') {
      showToast('🔔 ' + (notif.title || '알림') + ' ' + (notif.body || ''));
    }
  });

  PushNotifications.addListener('pushNotificationActionPerformed', (action) => {
    const type = action.notification?.data?.type;
    const urlMap = {
      emergency: '/app/emergency.html',
      check: '/app/inspect.html',
      corrective: '/app/corrective.html',
      approve: '/app/work_request.html',
      notice: '/app/notifications.html',
    };
    const target = urlMap[type] || '/app/index.html';
    location.href = target;
  });
}

// Preferences — localStorage 대체 (iOS 사파리 쿼터 제한 회피)
async function storageSet(key, value) {
  if (IS_NATIVE) {
    const { Preferences } = window.Capacitor.Plugins;
    await Preferences.set({ key, value: JSON.stringify(value) });
  } else {
    localStorage.setItem(key, JSON.stringify(value));
  }
}
async function storageGet(key) {
  if (IS_NATIVE) {
    const { Preferences } = window.Capacitor.Plugins;
    const { value } = await Preferences.get({ key });
    return value ? JSON.parse(value) : null;
  } else {
    const v = localStorage.getItem(key);
    return v ? JSON.parse(v) : null;
  }
}

// Network — 온/오프라인 감지
async function isOnline() {
  if (IS_NATIVE) {
    const { Network } = window.Capacitor.Plugins;
    const status = await Network.getStatus();
    return status.connected;
  }
  return navigator.onLine;
}

// 앱 시작 시 자동 호출
if (IS_NATIVE && document.readyState !== 'loading') {
  registerPushNative();
} else if (IS_NATIVE) {
  document.addEventListener('DOMContentLoaded', registerPushNative);
}

// TAI 네임스페이스 확장
if (window.TAI) {
  Object.assign(window.TAI, {
    IS_NATIVE,
    takePhotoNative,
    getLocationNative,
    registerPushNative,
    storageSet,
    storageGet,
    isOnline,
  });
}
```

### 3-4. 페이지별 native 우선 호출 패턴

**예시: `report.html`의 takePhoto() 수정**

```javascript
async function takePhoto() {
  if (TAI.IS_NATIVE) {
    try {
      const file = await TAI.takePhotoNative();
      // 기존 업로드 경로에 File 바로 전달
      const up = await TAI.uploadPhoto(file, 'report', {
        factory_id: user.factory_id,
      });
      _photos.push(up.url);  // URL 저장 (dataURL이 아님)
      renderThumbs();
      return;
    } catch (e) { /* 사용자 취소 등은 무시 */ }
  }
  // 폴백: 웹 파일 선택
  document.getElementById('photoInput').click();
}
```

**예시: geolocation 강화**

```javascript
async function getLocation() {
  if (TAI.IS_NATIVE) {
    const loc = await TAI.getLocationNative();
    if (loc) { _location = { ...loc, text: `${loc.lat.toFixed(5)}, ${loc.lng.toFixed(5)}` }; return; }
  }
  // 폴백: navigator.geolocation
  navigator.geolocation.getCurrentPosition(...);
}
```

---

## 🟢 Phase 4: 빌드 & 테스트

### 4-1. 디버그 빌드 (로컬 실기기/에뮬레이터)

```bash
cd tai-admin/mobile
npm run sync:android
npm run open:android    # Android Studio 자동 실행
```

Android Studio에서:
1. 상단 "Device Manager" → 에뮬레이터 생성 (Pixel 6, API 34)
2. 또는 USB 디버깅 켠 실기기 연결
3. "Run" 버튼 (▶) 클릭 → 빌드 + 설치 자동

### 4-2. 기능별 실기기 테스트 체크리스트

| 기능 | 확인 방법 | 예상 결과 |
|---|---|---|
| 앱 실행 | 아이콘 탭 | 1.5초 스플래시 → TAI Safe 홈 |
| 로그인 (OTP) | 전화번호 인증 | SMS 수신, 로그인 완료 |
| 카메라 | 이상 신고 → 사진 찍기 | 네이티브 카메라 실행, 사진 서버 업로드 |
| 위치 | 긴급 신고 | GPS 좌표 정확 획득 |
| 푸시 알림 | 서버에서 테스트 알림 전송 | Lock 화면에서도 표시, 탭 시 해당 페이지 |
| QR 스캔 | 출입 기록 | 네이티브 스캐너, 오프라인 동작 |
| 오프라인 | 비행기 모드 → 점검 제출 | 오프라인 큐 저장, 네트워크 복구 시 자동 전송 |
| 딥링크 | `https://safe.taieng.co.kr/app/` 탭 | 웹 아닌 앱에서 열림 (Digital Asset Links 이후) |

### 4-3. 릴리스 AAB 빌드

Phase 1-3 keystore를 `mobile/android/app/` 로 임시 복사 후:

```bash
cd tai-admin/mobile
npm run build:android
# 출력: mobile/android/app/build/outputs/bundle/release/app-release.aab
```

이 AAB를 Play Console에 업로드.

⚠️ 빌드 완료 후 keystore는 `mobile/android/app/` 에서 삭제 (1Password에만 보관).

---

## 🟢 Phase 5: Digital Asset Links (딥링크)

Play Store 앱이 `safe.taieng.co.kr/app/` URL을 **앱에서 열리도록** 만들려면 공개 파일 호스팅 필요.

### 5-1. assetlinks.json 생성

Phase 1-3에서 추출한 SHA-256 지문을 다음 JSON에 삽입:

**파일**: `tai-admin/tadmin/full-version/.well-known/assetlinks.json`

```json
[{
  "relation": ["delegate_permission/common.handle_all_urls"],
  "target": {
    "namespace": "android_app",
    "package_name": "kr.co.taieng.safe",
    "sha256_cert_fingerprints": [
      "XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX"
    ]
  }
}]
```

### 5-2. Cloudflare Pages 라우트 확인

- 파일이 `https://safe.taieng.co.kr/.well-known/assetlinks.json` 으로 200 응답 필수
- `Content-Type: application/json` 헤더 필수 (Cloudflare는 기본 적용됨)
- 확인: `curl -I https://safe.taieng.co.kr/.well-known/assetlinks.json`

### 5-3. AndroidManifest.xml에 딥링크 인텐트 필터 추가

**파일**: `mobile/android/app/src/main/AndroidManifest.xml`

`<activity>` 내부에 다음 추가:
```xml
<intent-filter android:autoVerify="true">
  <action android:name="android.intent.action.VIEW" />
  <category android:name="android.intent.category.DEFAULT" />
  <category android:name="android.intent.category.BROWSABLE" />
  <data android:scheme="https" android:host="safe.taieng.co.kr" android:pathPrefix="/app/" />
</intent-filter>
```

---

## 체크리스트 (전 과정)

### Phase 1 (심태왕 직접)
- [ ] Node.js 20 LTS 설치
- [ ] Java JDK 17 설치
- [ ] Android Studio + SDK 34 설치
- [ ] Firebase Console에 Android 앱 등록 (`kr.co.taieng.safe`)
- [ ] `google-services.json` 다운로드 (1차, SHA-1 없이)
- [ ] Keystore 생성 (`tai-safe-release.keystore`)
- [ ] 1Password에 keystore + 비밀번호 저장
- [ ] 별도 클라우드 이중 백업
- [ ] SHA-1 / SHA-256 지문 추출 및 메모
- [ ] Firebase에 SHA-1 추가
- [ ] `google-services.json` 재다운로드 (SHA-1 포함)

### Phase 2 (Cursor)
- [ ] `mobile/` 디렉토리 생성
- [ ] Capacitor CLI + core + android 설치
- [ ] `capacitor.config.json` 작성
- [ ] `package.json` scripts 정의
- [ ] `scripts/sync-web.js` 작성
- [ ] `.gitignore` 작성
- [ ] `npx cap add android` 실행

### Phase 3 (Cursor)
- [ ] 9개 필수 플러그인 설치
- [ ] `@capacitor-mlkit/barcode-scanning` 설치
- [ ] `google-services.json` 배치
- [ ] `_utils.js`에 네이티브 분기 블록 추가
- [ ] 페이지별 `takePhoto`, `getLocation` native 우선 호출 수정

### Phase 4 (심태왕 + Cursor)
- [ ] Android Studio 에뮬레이터 실행
- [ ] 실기기 USB 디버깅 테스트
- [ ] 8가지 기능 체크리스트 완료
- [ ] 릴리스 AAB 빌드 성공

### Phase 5 (심태왕)
- [ ] `assetlinks.json` 작성 및 커밋
- [ ] Cloudflare Pages 배포 확인
- [ ] `AndroidManifest.xml`에 딥링크 필터 추가
- [ ] 딥링크 실기기 테스트

---

## 리스크 & 대응

### 🔴 R1. Keystore 분실
- **영향**: TAI Safe 앱 영구 업데이트 불가 → 새 패키지 ID로 신규 출시 필요
- **대응**: 1Password + 암호화 USB + 암호화 클라우드 **3중 백업**

### 🟠 R2. google-services.json 유출
- **영향**: 타인이 가짜 Android 앱 만들어 푸시 알림 가로채기 가능
- **대응**: `.gitignore` 철저, 팀원에게도 Slack 비공개 채널로 전달

### 🟡 R3. Web FCM과 Native FCM 충돌
- **영향**: 한 사용자가 웹과 앱 양쪽에서 토큰 등록 → 알림 중복
- **대응**: 서버 `/workers/fcm-token`에서 `platform` 필드로 구분 저장. 한 사용자당 최신 토큰만 활성 처리

### 🟡 R4. PWA 보강 작업(P0/P1)과 충돌
- **영향**: `_utils.js`를 PWA 오더와 Capacitor 오더 양쪽에서 편집
- **대응**: PWA P0 완료 후 Capacitor Phase 3 진행. 순차 커밋으로 충돌 회피

### 🟢 R5. Play Console 승인 지연
- **영향**: 빌드는 완료됐으나 업로드 대기
- **대응**: 승인 대기 중 **Closed Testing 준비** (테스터 20명 리스트, 테스트 시나리오 문서)

---

## 예상 타임라인

| 일차 | 작업 |
|---|---|
| Day 0 (오늘) | Phase 1-1 환경 설치 시작 |
| Day 1 | Phase 1-2 Firebase 등록 + 1-3 Keystore |
| Day 2~3 | Phase 2 프로젝트 스캐폴딩 (Cursor) |
| Day 3~5 | Phase 3 플러그인 + 코드 분기 (Cursor) |
| Day 5~7 | Phase 4 빌드 + 실기기 테스트 |
| Day 7 | Phase 5 Digital Asset Links |
| Day 7~14 | Play Console 승인 대기 |
| 승인 즉시 | AAB 업로드 → Closed Testing 등록 |

---

**작성**: Claude (기획창)  
**실행**: 심태왕(Phase 1,5) + Cursor(Phase 2,3)  
**검증**: 심태왕  
**최종 목표**: Play Store 출시 준비 완료 (Day 14)
