# Capacitor 하이브리드 앱 구축 진행 로그

**작업지시서**: `docs/WORK_ORDER_20260424_capacitor_setup.md`  
**시작일**: 2026-04-24  
**목표**: Play Console 승인 완료 시점에 AAB 업로드 준비 완료

---

## Phase 1: 심태왕 직접 작업

### Phase 1-1: 로컬 개발 환경 설치

| 항목 | 상태 | 완료일 | 비고 |
|---|---|---|---|
| Homebrew 5.1.7 | ✅ | 2026-04-24 | Apple Silicon (M2 Max) |
| Node.js 20 LTS | ✅ | 2026-04-24 | |
| Java JDK 17 (Temurin) | ✅ | 2026-04-24 | |
| Android Studio Panda 4 (2025.3.4) | ✅ | 2026-04-24 | |
| SDK Platforms (API 34, 33) | ✅ | 2026-04-24 | |
| SDK Tools (Build-Tools 34, Emulator, Platform-Tools) | ✅ | 2026-04-24 | |
| `$ANDROID_HOME` 환경변수 | ✅ | 2026-04-24 | `~/Library/Android/sdk` |
| `adb version` 검증 | ✅ | 2026-04-24 | |

### Phase 1-2: Firebase Console Android 앱 등록

| 항목 | 상태 | 완료일 | 비고 |
|---|---|---|---|
| Firebase 프로젝트 `tai-safe` 확인 | ✅ | 2026-04-24 | 기존 웹 FCM과 동일 |
| Android 앱 등록 (`kr.co.taieng.safe`) | ✅ | 2026-04-24 | 앱 ID: `1:897890995077:android:b9c8a3a9ed9111fb7e12ec` |
| `google-services.json` 1차 다운로드 | ⏳ 예정 | — | SHA-1 없는 버전 |

### Phase 1-3: Keystore 생성 ⏸️ 내일 진행

**중요도**: 🔴 최상 — 이 단계가 전체 프로젝트의 가장 중요한 지점

| 항목 | 상태 | 완료일 | 비고 |
|---|---|---|---|
| 1Password "TAI Safe Android Keystore" 노트 생성 | ⏸️ 내일 | — | 비밀번호 저장용 |
| `tai-safe-release.keystore` 생성 | ⏸️ 내일 | — | RSA 4096, 10000일 유효 |
| 1Password에 keystore 파일 첨부 | ⏸️ 내일 | — | 1차 백업 |
| 암호화 클라우드 백업 | ⏸️ 내일 | — | 2차 백업 |
| USB/외장SSD 백업 | ⏸️ 내일 | — | 3차 백업 |
| SHA-1, SHA-256 지문 추출 | ⏸️ 내일 | — | 1Password에 기록 |
| 바탕화면 keystore 파일 삭제 | ⏸️ 내일 | — | 백업 3중 확인 후 |

### Phase 1-4: Firebase에 SHA-1 추가 ⏸️ 대기

| 항목 | 상태 | 완료일 | 비고 |
|---|---|---|---|
| Firebase Console에 SHA-1 추가 | ⏸️ 1-3 완료 후 | — | |
| `google-services.json` 재다운로드 | ⏸️ 1-3 완료 후 | — | SHA-1 포함 버전 |

---

## Phase 2~5: 대기

| Phase | 담당 | 상태 |
|---|---|---|
| Phase 2: Cursor 프로젝트 스캐폴딩 | Cursor | ⏸️ Phase 1 완료 후 |
| Phase 3: 플러그인 + 코드 분기 | Cursor | ⏸️ |
| Phase 4: 빌드 & 테스트 | 심태왕 + Cursor | ⏸️ |
| Phase 5: Digital Asset Links | 심태왕 | ⏸️ |

---

## 내일 재개 시 첫 체크리스트

1. **Firebase Console 접속** — `tai-safe` 프로젝트
   - 아직 `google-services.json` 1차 다운로드 안 했으면 먼저 받기
   - `ls -lh ~/Downloads/google-services.json` 으로 확인

2. **1Password에 Secure Note 생성**:
   ```
   제목: TAI Safe Android Keystore
   Keystore 비밀번호: (16자 이상 강력한 비밀번호)
   Key alias: tai-safe
   생성일: 2026-04-25
   ```

3. **Keystore 생성 명령 실행**:
   ```bash
   cd ~/Desktop
   keytool -genkey -v \
     -keystore tai-safe-release.keystore \
     -alias tai-safe \
     -keyalg RSA \
     -keysize 4096 \
     -validity 10000
   ```

4. **입력할 정보 (미리 결정)**:
   - First/Last Name: `Taewang Shim`
   - OU: `Development`
   - Organization: `TAI Engineering`
   - City: `Seoul`
   - State: `Seoul`
   - Country: `KR`

5. **3중 백업** → SHA-1/256 추출 → Firebase 등록 → google-services.json 재다운로드

---

## 환경 확인 명령 (내일 터미널 열 때 먼저 실행)

모든 환경이 유지되고 있는지 확인:

```bash
node -v          # v20.x.x
java -version    # 17.x.x
adb version      # 35.x.x
echo $ANDROID_HOME  # /Users/taiwangsim/Library/Android/sdk
```

4개 모두 정상이면 바로 Phase 1-3 진행 가능.

---

## 리스크 리마인더

### 🔴 Keystore 분실 위험
- **영향**: TAI Safe 앱 영구 업데이트 불가
- **대응**: 반드시 3중 백업 (1Password + 클라우드 + USB)

### 🟠 비밀번호 유실 위험
- **영향**: Keystore 파일 있어도 열 수 없음 = 분실과 동일
- **대응**: 1Password에만 저장, 절대 메모장/채팅에 기록하지 말 것

### 🟡 google-services.json 유출
- **영향**: Firebase 프로젝트 API 키 노출, 가짜 앱 제작 위험
- **대응**: `.gitignore` 포함, 공개 저장소 업로드 절대 금지

---

**최종 업데이트**: 2026-04-24 (Phase 1-1, 1-2 완료, 1-3부터 내일 재개)  
**책임자**: 심태왕
