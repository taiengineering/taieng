# 2026-04-25 세션 작업 내역 + 미해결 이슈

## 완료된 작업

### 1. 유료진단 결과 페이지 v5 (taieng 레포)
- **커밋**: `32f4d64` → main
- SEC03 테이블 → 실행 가이드 카드(action-card) 전환
- 빈 필드 행 자동 숨김 (graceful degradation)
- 법령+조항에 law.go.kr 조문 링크 연결
- 세금계산서 요청 UI 삭제
- 부록 법령 링크 테이블 삭제

### 2. 법 엔진 9개 필드 보강 (tai-api 레포)
- **커밋**: `9f16b0e` → main
- `services/legal_format.py`에 9개 필드 추가 출력:
  - cycle_base_guide, due_days, form_name, form_code, form_url
  - online_system, system_url, report_method_std, tai_feature_code, qualification_code
- DB 채워진 비율: 50~78% (건설 섹터 503건 기준)

### 3. 법령 조문 뷰어 API (tai-api 레포)
- **커밋**: `9f16b0e` → main
- `routers/law_viewer.py` v1.0.0 신규 생성
- `GET /law/article?law_name=산업안전보건법&article_no=17&rule_id=CON-APPOINT-001`
- 조문 원문 (law_article 14,935건) + 판례 (graceful degradation, 현재 0건)
- `main.py`에 라우터 등록 완료

### 4. 결과 페이지에 "▼ 원문 보기" 기능 (taieng 레포)
- **커밋**: `19b61fd` → main
- 카드 클릭 시 `/law/article` API lazy load
- 카드 내부 펼침에 조문 원문 렌더
- precedents 있으면 판례 리스트 렌더

### 5. CORS 수정 — Capacitor 앱 지원 (tai-api 레포)
- **커밋**: `7476f80` → main
- `main.py` allow_origins에 추가:
  - `capacitor://localhost` (iOS)
  - `http://localhost` (Android)
  - `https://localhost` (Android 일부)

### 6. 앱 로그인 차단 수정 (tai-admin 레포)
- **커밋**: `ded9bdc` → main
- `auth-login-cover.html`에 Capacitor 감지 추가:
  ```javascript
  var IS_NATIVE_APP = !!(window.Capacitor && window.Capacitor.isNativePlatform && window.Capacitor.isNativePlatform());
  ```
- APP_ONLY_ROLES 차단을 앱 내에서는 우회

### 7. Capacitor 서버 URL 설정 (tai-admin 레포)
- **커밋**: `a977bb2` → main
- `capacitor.config.ts`에 server.url 추가:
  ```typescript
  server: {
    url: 'https://safe.taieng.co.kr/html/horizontal-menu-template/auth-login-cover',
    cleartext: false,
  }
  ```
- 이후 서버 코드 수정만으로 앱 즉시 반영 (리빌드 불필요)

---

## 🔴 미해결 이슈

### ISSUE-1: Android APK 빌드 실패 — JDK 21 Toolchain
```
Execution failed for task ':capacitor-android:compileReleaseJavaWithJavac'.
> error: invalid source release: 21
```

**상황:**
- macOS M2 Max
- JDK 17 (Temurin) + JDK 21 (Homebrew) 모두 설치됨
- `/usr/libexec/java_home -V`로 JDK 21 확인됨
- 그러나 Gradle 8.12의 toolchain이 JDK 21을 찾지 못함
- `JAVA_HOME` 환경변수 설정, `gradle.properties` 설정, 심링크 생성 모두 시도했으나 실패

**시도한 것:**
1. `JAVA_HOME=/opt/homebrew/.../openjdk@21 ./gradlew assembleRelease` → 실패
2. `gradle.properties`에 `org.gradle.java.installations.paths=...` 추가 → 실패
3. `/Library/Java/JavaVirtualMachines/`에 심링크 생성 → 실패
4. `settings.gradle`에 foojay-resolver-convention 플러그인 추가 → 실패

**추정 원인:**
- Gradle의 toolchain 탐색이 Homebrew 경로를 완전히 무시
- 또는 capacitor-android 플러그인의 build.gradle에서 JDK 21을 toolchain으로 강제 요구하는데, Gradle 8.12가 해당 JDK를 탐색하지 못하는 구조적 문제

**해결 방향:**
1. `capacitor-android`의 build.gradle에서 `java.toolchain.languageVersion`을 17로 변경
2. 또는 `brew install --cask temurin@21` (Adoptium JDK 21)로 설치하면 `/Library/Java/JavaVirtualMachines/`에 자동 설치되어 Gradle이 찾을 수 있음
3. 또는 `android/gradle.properties`에:
   ```
   org.gradle.java.installations.auto-download=false
   org.gradle.java.installations.fromEnv=JAVA_HOME
   ```

### ISSUE-2: settings.gradle 오염 상태
디버깅 과정에서 settings.gradle이 수정됨. 현재 상태:
```groovy
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

plugins {
    id 'org.gradle.toolchains.foojay-resolver-convention' version '0.8.0'
}

include ':app'
include ':capacitor-cordova-android-plugins'
project(':capacitor-cordova-android-plugins').projectDir = new File('./capacitor-cordova-android-plugins/')

apply from: 'capacitor.settings.gradle'
```
빌드 성공 후 원래 상태로 복원 필요.

### ISSUE-3: reparse 중 integer overflow
```
value "22213243035190" is out of range for type integer
```
- `condition_value` 컬럼이 integer인데 큰 숫자가 들어가고 있음
- bigint로 변경 필요 (DDL)
- 긴급하지 않으나 데이터 손실 방지를 위해 조치 필요

---

## 검증 필요 항목

| # | 항목 | 상태 |
|---|---|---|
| 1 | 유료진단 결과 v5 카드 렌더링 | ✅ 확인됨 (44카드, 빈필드 숨김) |
| 2 | 법 엔진 9필드 출력 | ⚠️ 실제 진단 실행 시 확인 필요 |
| 3 | /law/article API | ⚠️ 서버 배포 후 테스트 필요 |
| 4 | 원문 보기 펼침 | ⚠️ API 동작 후 확인 필요 |
| 5 | CORS Capacitor | ✅ API 로그인 200 OK 확인 |
| 6 | 앱 로그인 | 🔴 APK 리빌드 필요 (ISSUE-1) |

## 테스트 계정
```
이메일: worker@tai.com
비밀번호: tai1234!
(role_code: 014, 작업자)
→ API 로그인 성공 확인됨 (200 OK, 토큰 발급)
```

## 검증 URL
- 유료진단 결과: https://new.taieng.co.kr/paid-diagnosis-result.html?token=DEMO-CON-2026
- API 헬스: https://api.taieng.co.kr/health
