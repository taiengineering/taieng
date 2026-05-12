# 설비 페이지 개선 작업 지시서
## 담당: Claude 프론트 창
## 대상 파일: admin/full-version/html/horizontal-menu-template/engine-equipment.html
## 참조: engine-legal.html (예외 기반 관리 구조 동일하게 적용)

---

## 현재 DB 현황
- 등록 설비: 71개
- 모델 미연결: 71개 (전체)
- 점검일 없음: 71개 (전체)
- 법정검사 대상 목록: 13개
- process_equipment_map: 1,188,161개 (자동 매핑 — 수동 수정 금지)

---

## 핵심 원칙 (UI에 반영)
```
process_equipment_map = 이론적 매핑 (자동 생성, 수동 추가 금지)
equipment_assets      = 실제 등록 설비 (사용자 입력)
```
수동으로 공정-설비 매핑을 추가하면 법령 판정 오류 발생.
이 페이지에서는 equipment_assets 관리만 다룬다.

---

## 상단 통계 카드 (4개) — 기존 교체

기존 카드(매핑전체건수/고유설비수/검토필요/모델마스터)를
아래로 교체:

| 카드 | 아이콘 | 색상 | 주숫자 | 부제 |
|------|--------|------|--------|------|
| 등록 설비 | tabler-tool | primary | equipment_assets COUNT | "법정대상 N개" |
| 모델 미연결 | tabler-link-off | danger | model_id IS NULL COUNT | "위험도 계산 불가" |
| 법정검사 미매핑 | tabler-alert-triangle | warning | 법정검사대상 vs 실제 미연결 수 | "안전검사 N종 대상" |
| 점검일 없음 | tabler-calendar-off | warning | last_inspection_date IS NULL | "점검 이력 없음" |

모델미연결 > 0 → 카드 왼쪽 테두리 빨간색
법정검사 미매핑 > 0 → 카드 왼쪽 테두리 주황색

API: GET /engine-equipment/stats (기존 유지)
모델미연결/점검일없음 숫자는 아래 API로 추가 호출:
GET /equipment-assets?model_id=null&count=true 없으면 하드코딩(71,71,13)

---

## 자동 점검 리포트 카드 (engine-legal.html 방식 동일)

제목: ⚠️ 설비 이상 감지
부제: 문제 있는 항목만 표시됩니다

아래 5개 행 하드코딩:

| 점검항목 | 문제내용 | 건수 | 상태배지 |
|---------|---------|------|--------|
| 모델 미연결 | equipment_assets 전체가 equipment_model_master 미연결 → 위험도 계산 불가 | 71개 | bg-danger 즉시조치 |
| 법정검사 미매핑 | 법정안전검사 대상 13종과 등록설비 자동매핑 미완료 | 확인필요 | bg-warning 검토필요 |
| 점검이력 없음 | last_inspection_date 없는 설비 | 71개 | bg-warning 입력필요 |
| 안전인증 여부 미확인 | is_legal_target=true이지만 인증종류 미기록 | 확인필요 | bg-warning 검토필요 |
| 공정-설비 수동추가 주의 | process_equipment_map은 자동생성. 수동추가 시 법령판정 오류 발생 | - | bg-info 유의사항 |

---

## 탭 구조 (기존 2탭 → 3탭으로 확장)

### 탭1: 설비 마스터 (기존 설비 마스터 탭 개선)

기존 필터에 추가:
- 모델연결: 전체 / 연결됨 / 미연결
- 법정검사: 전체 / 대상 / 비대상
- 품질등급: 전체 / 양호(80+) / 보통(50-79) / 미흡(0-49)

기존 컬럼에 추가:
| 기존 컬럼 유지 | 추가 컬럼 |
|-------------|----------|
| 설비명/카테고리/밴드/매핑공정수/검토상태 | 모델연결여부 / 법정검사여부 / 품질점수 |

**품질점수 계산 (100점):**
```javascript
function calcEquipScore(eq) {
  let score = 0;
  if (eq.facility_category) score += 20;     // 카테고리 분류
  if (eq.rule_count > 0)     score += 20;     // 법령룰 연결
  if (eq.has_inspection)     score += 20;     // 점검항목 연결
  if (eq.has_failure)        score += 20;     // 고장유형 연결
  if (eq.has_model)          score += 10;     // 모델 데이터
  if (eq.is_legal_target !== null) score += 10; // 안전인증 확인
  return score;
}
```

점수 배지:
- 80~100 → badge bg-success "양호"
- 50~79  → badge bg-warning "보통"
- 0~49   → badge bg-danger  "미흡"

모델미연결이면 설비명 옆에 `<span class="badge bg-danger ms-1">모델없음</span>`

행 클릭 → 사이드패널 (기존 유지 + 아래 추가):
- 법정검사 대상 여부 (master_legal_inspection_target 연결)
- 안전인증 대상 여부 (master_safety_certification 연결)
- 품질점수 바 차트

---

### 탭2: 설비 이상 감지 (신규)

제목: 설비 품질 문제 목록

서브탭 4개:

**서브탭A: 모델 미연결 (71개)**
- equipment_assets에서 equipment_model_id IS NULL인 설비 목록
- 컬럼: No. | 설비명 | 카테고리 | 설치연도 | 제조사 | 조치
- 조치버튼: "모델 연결" (클릭 → 모델 검색 모달)
- API: GET /engine-equipment/list?has_model=false

**서브탭B: 법정검사 미매핑**
- master_legal_inspection_target 13개 vs equipment_assets 비교
- 컬럼: No. | 법정검사종류 | 주기 | 등록된 설비 수 | 상태
- 등록설비 0개 → 빨간 badge "미등록"
- API: GET /byulpyo/legal-inspection (기존)

**서브탭C: 점검이력 없음**
- last_inspection_date IS NULL 설비
- 컬럼: No. | 설비명 | 카테고리 | 법정검사대상 | 설치연도 | 조치
- 조치버튼: "점검일 입력" (인라인 날짜 입력)
- API: GET /engine-equipment/list?no_inspection=true

**서브탭D: 안전인증 미확인**
- master_safety_certification의 CERT 30개와
  equipment_assets 비교 → 해당 설비 있는데 인증확인 안된 것
- 컬럼: No. | 인증대상품목 | 구분 | 등록설비 매칭 | 상태

---

### 탭3: 모델 마스터 (기존 탭2 그대로 이동)

기존 모델 마스터 탭을 탭3으로 이동. 내용 동일.

---

## 수동 추가 방지 안내 배너

탭1 상단에 info 배너 추가:
```html
<div class="alert alert-info d-flex align-items-center mb-3" role="alert">
  <i class="icon-base ti tabler-info-circle me-2"></i>
  <div>
    <strong>공정-설비 매핑은 자동 생성됩니다.</strong>
    이 페이지에서는 실제 등록 설비(equipment_assets)만 관리합니다.
    공정 매핑을 수동으로 수정하면 법령 판정 오류가 발생합니다.
  </div>
</div>
```

---

## API 정리

| 용도 | 엔드포인트 |
|------|----------|
| 통계 | GET /engine-equipment/stats |
| 설비 목록 (필터 확장) | GET /engine-equipment/list?has_model=true/false&no_inspection=true |
| 설비 상세 | GET /engine-equipment/detail/{name} |
| 법정검사 목록 | GET /byulpyo/legal-inspection |
| 안전인증 목록 | GET /byulpyo/safety-cert |
| 모델 목록 | GET /engine-equipment/models |

---

## 전역 규칙
- 첫 번째 컬럼: toggleAll 체크박스
- 두 번째 컬럼: No. (1부터)
- escapeHtml 함수 필수
- 인증 코드 기존과 동일
- 스크립트 세트 기존과 동일

---

## 완료 기준
- [ ] 상단 카드 4개 교체 (모델미연결/법정미매핑/점검없음)
- [ ] 자동 점검 리포트 카드 5개 행
- [ ] 탭1 필터 확장 + 품질점수 컬럼
- [ ] 탭2 이상감지 4개 서브탭
- [ ] 탭3 모델마스터 (기존 탭2 이동)
- [ ] 수동추가 방지 안내 배너
- [ ] git commit + push
- [ ] 커밋메시지: "feat: engine-equipment.html 설비 품질관리 + 이상감지 탭 추가"
