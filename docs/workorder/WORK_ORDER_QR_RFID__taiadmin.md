# QR / RFID 설비 체크인 기능 작업지시서

생성일: 2026-04-08  
담당창: 백엔드(tai-api), 프론트(tai-admin)

---

## 개요

현장 작업자가 설비에 부착된 **QR 코드** 또는 **RFID 태그**를 인식하여  
직접 점검 체크인을 수행하는 기능을 구현한다.

### 설계 원칙
- QR 코드는 **온디맨드 생성** (전체 사전 생성 금지)
- QR 내용: `https://safe.taieng.co.kr/html/.../qr-check.html?id={equipment_asset_id}`
- 스캔 시 서버에서 **회사→사업장→공정→설비** 전체 정보 조회
- RFID는 동일 체크인 페이지를 rfid_tag ID로 조회
- 로그인 없이 QR 스캔만으로 체크인 가능 (익명 접근 허용)

### DB 변경 완료 (2026-04-08)

`equipment_assets` 테이블에 추가된 컬럼:

| 컬럼명 | 타입 | 설명 |
|---|---|---|
| `factory_process_id` | uuid | 공정 연결 (factory_process.id FK) |
| `rfid_tag` | text UNIQUE | RFID 물리 태그 고유 ID |
| `rfid_tag_type` | text | NFC / HF_13MHZ / UHF_900MHZ |
| `qr_code_generated_at` | timestamptz | 마지막 QR 생성 시각 |
| `qr_print_count` | integer | QR 출력 누적 횟수 |
| `qr_code` | text | (기존) QR URL 저장 |

---

## 백엔드 작업 (tai-api)

### 1. 설비 QR 생성 API

```
POST /equipment-assets/{id}/generate-qr
```

**동작:**
1. `equipment_assets.qr_code` 에 URL 저장
   - 형식: `https://safe.taieng.co.kr/html/vertical-menu-template-no-customizer/qr-check.html?id={id}`
2. `qr_code_generated_at` = NOW()
3. 응답: `{ qr_url, qr_content, equipment_info }`

**권한:** 로그인 필요 (사업장 소속 확인)

---

### 2. QR/RFID 스캔 조회 API (인증 불필요)

```
GET /equipment-assets/scan?id={equipment_asset_id}
GET /equipment-assets/scan?rfid={rfid_tag}
```

**응답 데이터:**
```json
{
  "equipment": {
    "id": "uuid",
    "asset_name": "지게차 3호기",
    "asset_code": "FK-003",
    "equipment_type_code": "forklift",
    "main_image_url": "..."
  },
  "factory": {
    "id": "uuid",
    "name": "대성정밀 1공장",
    "company_id": "uuid"
  },
  "company": {
    "id": "uuid",
    "name": "대성정밀(주)"
  },
  "process": {
    "id": "uuid",
    "process_path": "제조 > 기계가공 > 선반"
  },
  "pending_schedules": [
    {
      "id": "uuid",
      "description": "작업 전 점검",
      "planned_date": "2026-04-08"
    }
  ]
}
```

**권한:** 인증 불필요 (QR 스캔 공개 접근)

---

### 3. QR 스캔 점검 체크인 API (인증 불필요)

```
POST /equipment-assets/scan/checkin
```

**Request Body:**
```json
{
  "equipment_asset_id": "uuid",
  "schedule_id": "uuid",          // 연결할 점검 일정 (선택)
  "checkin_items": [
    { "item_key": "tire", "item_label": "타이어 상태", "result": "OK" },
    { "item_key": "brake", "item_label": "브레이크", "result": "OK" },
    { "item_key": "horn", "item_label": "경적", "result": "NG", "note": "작동 불량" }
  ],
  "overall_result": "NG",          // OK | NG | HOLD
  "worker_name": "김작업",           // 미로그인 시 직접 입력
  "worker_id": "uuid",              // 로그인 시
  "signature_data": "base64...",    // 전자서명 (선택)
  "location": { "lat": 37.12, "lng": 127.34 }  // GPS (선택)
}
```

**응답:** `{ checkin_id, status, message }`

**저장 테이블:** `equipment_checkins` (신규 테이블 — 아래 참조)

---

### 4. 신규 테이블: equipment_checkins

```sql
CREATE TABLE equipment_checkins (
  id                   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  equipment_asset_id   uuid REFERENCES equipment_assets(id),
  schedule_id          uuid REFERENCES work_schedules(id),
  factory_id           uuid REFERENCES factories(id),
  company_id           uuid REFERENCES companies(id),
  
  -- 작업자
  worker_id            uuid,           -- 로그인 사용자
  worker_name          text,           -- 미로그인 직접 입력
  
  -- 점검 결과
  checkin_items        jsonb,          -- 항목별 결과
  overall_result       text,           -- OK | NG | HOLD
  note                 text,
  
  -- 증빙
  signature_data       text,           -- base64 서명
  photo_urls           text[],         -- 사진 첨부
  
  -- 인식 방법
  scan_method          text,           -- QR | RFID | MANUAL
  
  -- 위치
  latitude             numeric,
  longitude            numeric,
  
  -- 시간
  checkin_at           timestamptz DEFAULT NOW(),
  created_at           timestamptz DEFAULT NOW()
);
```

### 5. QR 출력 카운트 API

```
POST /equipment-assets/{id}/qr-printed
```
→ `qr_print_count += 1` 업데이트

---

## 프론트엔드 작업 (tai-admin / safe)

### [safe] qr-check.html (신규)

**경로:** `site/full-version/html/vertical-menu-template-no-customizer/qr-check.html`

**흐름:**
1. URL 파라미터 `?id=` 또는 `?rfid=` 파싱
2. `GET /equipment-assets/scan` 호출 → 설비 정보 표시
3. 오늘 예정 점검 일정 목록 표시
4. 점검 항목 체크 (정상/이상/보류)
5. 이름 입력 + 간단 서명
6. 완료 제출 → `POST /equipment-assets/scan/checkin`
7. 완료 화면 표시 (이상 있을 경우 관리자 알림 FCM 발송)

**UI 특징:**
- 로그인 없이 접근 가능
- 모바일 최적화 (폰트 크고 버튼 큼)
- 지게차 점검 UI 시안(`tai_forklift_check_ui_html.html`) 스타일 참조

---

### [safe] equipment-qr-manager.html (신규)

**경로:** `site/full-version/html/vertical-menu-template-no-customizer/equipment-qr-manager.html`

**기능:**
1. 사업장 내 설비 목록 표시
2. 설비별 QR 생성 여부 / 마지막 생성일 / 출력 횟수 표시
3. [QR 생성] 버튼 → API 호출 → QR 이미지 표시
4. [프린트] 버튼 → 인쇄 최적화 레이아웃 (설비명, QR코드, asset_code 포함)
5. RFID 태그 ID 입력 필드 (수동 등록)
6. 공정 연결 선택 (factory_process 드롭다운)

**QR 프린트 레이아웃:**
```
┌─────────────────────┐
│  [TAI Safe 로고]     │
│  대성정밀 1공장      │
│  선반 공정           │
│                      │
│  [QR 코드 이미지]    │
│                      │
│  지게차 3호기        │
│  FK-003              │
│  스캔하여 점검 시작  │
└─────────────────────┘
```

---

## 구현 우선순위

1. **백엔드** `GET /equipment-assets/scan` API
2. **백엔드** `POST /equipment-assets/scan/checkin` API + `equipment_checkins` 테이블
3. **백엔드** `POST /equipment-assets/{id}/generate-qr` API
4. **프론트** `qr-check.html` (작업자 체크인 화면)
5. **프론트** `equipment-qr-manager.html` (QR 생성/프린트)

---

## QR 라이브러리

프론트엔드 QR 생성: `qrcode.js` (CDN)
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
```

QR 스캔: `html5-qrcode` (CDN, 카메라 접근)
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/html5-qrcode/2.3.8/html5-qrcode.min.js"></script>
```
