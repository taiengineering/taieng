# TAI 작업지시서 — TBM + 안전보건위원회 + 위험성평가

> 작성일: 2026-03-31
> 관련 레포: tai-admin (프론트) + tai-api (백엔드)

---

## 모듈 개요

| 모듈 | 법적 근거 | 핵심 차별점 | 현재 단계 |
|------|---------|-----------|--------|
| TBM | 산안법 제29조 | 🎙️ 녹음 → STT 자동 변환 | 프론트+백엔드 |
| 안전보건위원회/협의체 | 산안법 제24조·제64조 | 📄 회의록 문서 보관 | 프론트+백엔드 |
| 위험성평가 | 산안법 제36조 | 📁 문서 업로드·보관 | 프론트+백엔드 |

---

## DB 현황 (migration 완료)

```
tbm_meetings          확장 완료 (audio_url, transcript_text, signature 등)
tbm_attendees         확장 완료 (worker_id, signature_url 등)
safety_committee_meetings  신규 생성
risk_assessments      신규 생성
```

---

## 모듈 1: TBM (작업 전 안전점검회의)

### 핵심 차별점
```
기존: 종이에 서명 → 분실
TAI Safe:
  ① 안전관리자가 TBM 개설 (모바일/웹)
  ② 작업 내용·위험요인 입력
  ③ 🎙️ 음성 녹음 → STT 자동 변환
     (Web Speech API 또는 Supabase Edge Function)
  ④ 작업자 모바일로 전자서명
  ⑤ PDF 자동 생성 → 3년 보존
```

### 페이지: `tbm-list.html` (신규)

```
┌─────────────────────────────────────────────────┐
│ TBM 관리              [+ TBM 등록]               │
├─────────────────────────────────────────────────┤
│ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐    │
│ │전체 45 │ │완료 38 │ │진행중 5│ │임시 2  │    │
├─────────────────────────────────────────────────┤
│ □ No │ 날짜 │ 작업명 │ 장소 │ 참석 │ 녹음 │ 상태│
│ □  1 │ 4/1 │용접작업│1공장 │ 5명  │ ✅   │완료 │
│ □  2 │ 4/1 │고소작업│옥상  │ 3명  │ ❌   │완료 │
└─────────────────────────────────────────────────┘
```

### TBM 작성 사이드패널

```html
<!-- 기본 정보 -->
<input id="tbm-work-date" type="date">       <!-- 작업일 -->
<input id="tbm-location" placeholder="작업 장소">
<textarea id="tbm-work-desc" placeholder="작업 내용 설명">

<!-- 위험요인 (태그 입력 방식) -->
<div id="tbm-risks"> ... 태그 추가 ...</div>

<!-- 안전수칙 (태그 입력 방식) -->
<div id="tbm-safety"> ... 태그 추가 ...</div>

<!-- 🎙️ 녹음 버튼 (핵심 차별점) -->
<div id="recorder-section">
  <button id="btn-record" class="btn btn-danger" onclick="toggleRecord()">
    <i class="ti tabler-microphone"></i> 녹음 시작
  </button>
  <div id="recording-timer" style="display:none">00:00</div>
  <!-- 녹음 후 STT 변환 상태 표시 -->
  <div id="stt-status"></div>
  <!-- 변환된 텍스트 편집 가능 -->
  <textarea id="transcript-text" placeholder="녹음 내용이 여기에 표시됩니다...">
</div>

<!-- 참석자 (worker_registry 연동) -->
<div id="attendee-section">
  <input id="attendee-search" placeholder="이름·연락처 검색">
  <div id="attendee-list"></div>
</div>
```

### 녹음 JS 핵심 로직

```javascript
let mediaRecorder, audioChunks = [], isRecording = false;

async function toggleRecord() {
  if (!isRecording) {
    // 녹음 시작
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];
    mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
    mediaRecorder.onstop = async () => {
      const blob = new Blob(audioChunks, { type: 'audio/webm' });
      await uploadAndTranscribe(blob);
    };
    mediaRecorder.start();
    isRecording = true;
    startTimer();
    document.getElementById('btn-record').innerHTML =
      '<i class="ti tabler-player-stop"></i> 녹음 중지';
    document.getElementById('btn-record').classList.replace('btn-danger','btn-warning');
  } else {
    // 녹음 중지
    mediaRecorder.stop();
    mediaRecorder.stream.getTracks().forEach(t => t.stop());
    isRecording = false;
    stopTimer();
    document.getElementById('btn-record').innerHTML =
      '<i class="ti tabler-microphone"></i> 다시 녹음';
  }
}

async function uploadAndTranscribe(blob) {
  document.getElementById('stt-status').innerHTML =
    '<div class="spinner-border spinner-border-sm me-2"></div>변환 중...';

  // 1. Supabase Storage에 업로드
  const formData = new FormData();
  formData.append('audio', blob, 'tbm_recording.webm');
  formData.append('tbm_id', currentTbmId);

  // 2. 백엔드 STT API 호출
  const res = await apiCall('POST', '/tbm/transcribe', formData);

  // 3. 변환된 텍스트 표시
  document.getElementById('transcript-text').value = res.data.text;
  document.getElementById('stt-status').innerHTML =
    '<span class="text-success">✅ 변환 완료</span>';
}
```

### 백엔드 API

```
POST /tbm                        TBM 생성
GET  /tbm?factory_id=&page=&size= 목록 조회
GET  /tbm/{id}                    상세 조회
PATCH /tbm/{id}                   수정
POST /tbm/{id}/complete           완료 처리
POST /tbm/transcribe              음성 → 텍스트 변환
  → Supabase Storage 업로드 후
  → OpenAI Whisper API 또는 Web Speech API
  → 변환 텍스트 반환 + DB 저장
POST /tbm/{id}/pdf                PDF 생성
GET  /tbm/{id}/attendees          참석자 목록
POST /tbm/{id}/attendees          참석자 추가
PATCH /tbm/{id}/attendees/{aid}/sign  전자서명 등록
```

### STT 구현 방법 (2가지 중 선택)

```
방법 A: Web Speech API (무료, 브라우저 내장)
  장점: 비용 0원, 즉시 구현 가능
  단점: 크롬에서만 안정적, 인터넷 필요, 한국어 인식률 보통
  코드: SpeechRecognition API

방법 B: OpenAI Whisper API (유료)
  비용: 1분당 약 $0.006 (TBM 10분 = $0.06 = 약 90원)
  장점: 한국어 인식률 매우 높음, 모든 브라우저
  단점: API 비용 발생

→ 현재 단계: 방법 A (Web Speech API)로 먼저 구현
→ 추후: 방법 B로 업그레이드 (프리미엄 기능)
```

---

## 모듈 2: 안전보건위원회 / 협의체 회의

### 법적 의무
```
산업안전보건위원회 (제24조): 100인 이상, 분기 1회, 회의록 3년 보존
도급 안전보건협의체 (제64조): 도급 현장, 월 1회, 회의록 보존
노사협의회 안전보건 (근참법): 30인 이상, 분기 1회
```

### 페이지: `safety-meeting-list.html` (신규)

```
┌─────────────────────────────────────────────────┐
│ 안전보건 회의 관리      [+ 회의록 등록]            │
├─────────────────────────────────────────────────┤
│ 회의유형[전체▼] 연도[2026▼] [검색]               │
├─────────────────────────────────────────────────┤
│ □ No │ 유형 │ 제목 │ 날짜 │ 참석 │ 파일 │ 상태 │
│ □  1 │위원회│1분기 │ 3/31 │ 10명 │  📎  │완료  │
│ □  2 │협의체│3월  │ 3/15 │  8명 │  📎  │완료  │
└─────────────────────────────────────────────────┘

※ 보존 기한 D-day 표시: "보존 만료 2029-03-31 (D-1095)"
```

### 회의록 작성 모달

```html
<!-- 회의 유형 -->
<select id="meeting-type">
  <option value="SAFETY_COMMITTEE">산업안전보건위원회 (제24조)</option>
  <option value="CONTRACTOR_COUNCIL">도급 안전보건협의체 (제64조)</option>
  <option value="LABOR_COUNCIL">노사협의회</option>
  <option value="OTHER">기타 안전회의</option>
</select>

<!-- 기본 정보 -->
<input id="meeting-title" placeholder="회의명">
<input id="meeting-date" type="date">
<input id="meeting-place" placeholder="장소">
<input id="chair-name" placeholder="의장">

<!-- 안건 (동적 추가) -->
<div id="agenda-items">
  <div class="agenda-item">
    <input placeholder="안건 번호"> <input placeholder="안건 내용">
  </div>
</div>
<button onclick="addAgenda()">+ 안건 추가</button>

<!-- 심의·의결 내용 -->
<textarea id="discussion-text" rows="4" placeholder="심의 내용 기술..."></textarea>
<textarea id="resolution-text" rows="3" placeholder="의결사항 기술..."></textarea>

<!-- 참석자 -->
<textarea id="attendees-text" placeholder="참석자 명단 (이름, 직책)"></textarea>

<!-- 파일 첨부 (기존 문서 업로드) -->
<div id="file-upload-area">
  <input type="file" multiple accept=".pdf,.hwp,.docx,.jpg,.png">
  <p>회의록 원본, 서명부 등 첨부</p>
</div>
```

### 백엔드 API

```
POST /safety-meetings              회의록 생성
GET  /safety-meetings?company_id=&type=&page= 목록
GET  /safety-meetings/{id}         상세
PATCH /safety-meetings/{id}        수정
POST  /safety-meetings/{id}/files  파일 첨부
DELETE /safety-meetings/{id}/files/{fid} 파일 삭제
POST  /safety-meetings/{id}/complete   완료 처리
GET   /safety-meetings/schedule    개최 일정 현황 (주기 준수 여부)
```

### 개최 주기 준수 모니터링

```javascript
// 대시보드에 표시
// 안전보건위원회: 분기별 개최 여부
// 협의체: 월별 개최 여부
async function checkMeetingCompliance(companyId) {
  const res = await apiCall('GET', '/safety-meetings/schedule?company_id=' + companyId);
  // 미개최 월/분기 → 경고 표시
  return res.data;
}
```

---

## 모듈 3: 위험성평가

### 현재 단계: 문서 보관 위주

```
지금: 기존 문서 업로드 + 기본 정보 입력
추후: AI 자동 생성 (산업안전기사 자격 취득 후)
```

### 페이지: `risk-assessment-list.html` (신규)

```
┌─────────────────────────────────────────────────┐
│ 위험성평가            [+ 평가 등록]               │
├─────────────────────────────────────────────────┤
│ 유형[전체▼] 연도[2026▼] [검색]                   │
├─────────────────────────────────────────────────┤
│ □ No │ 유형 │ 공정명 │ 평가일 │ 다음평가 │ 상태 │
│ □  1 │정기  │용접공정 │ 1/15  │ 내년1/15 │완료  │
│ □  2 │수시  │신설설비 │ 3/20  │     -    │완료  │
│ □  3 │최초  │전체공정 │ 2024  │올해예정⚠│완료  │
└─────────────────────────────────────────────────┘

※ 다음 평가 D-day 표시: "⚠️ 정기평가 기한 초과"
```

### 위험성평가 등록 모달

```html
<!-- 평가 유형 -->
<select id="assessment-type">
  <option value="INITIAL">최초평가 (사업 개시 후 1년 이내)</option>
  <option value="REGULAR">정기평가 (매년)</option>
  <option value="SPECIAL">수시평가 (설비도입·공정변경·중대재해)</option>
</select>

<!-- 기본 정보 -->
<input id="ra-title" placeholder="평가 제목">
<input id="ra-process" placeholder="공정명·작업명">
<input id="ra-date" type="date">
<input id="ra-assessor" placeholder="평가자">
<textarea id="ra-summary" placeholder="평가 요약 (선택)"></textarea>

<!-- 파일 첨부 (기존 문서) -->
<div id="ra-files">
  <input type="file" multiple accept=".pdf,.hwp,.docx,.xlsx">
  <p>기존 위험성평가표, 체크리스트 등 업로드</p>
</div>

<!-- 다음 정기평가 예정일 (자동 계산) -->
<input id="ra-next-review" type="date" readonly>
<!-- 정기평가 선택 시 평가일 + 1년 자동 입력 -->

<!-- 위험요인 간이 입력 (선택) -->
<div id="ra-items">
  <table class="table">
    <thead>
      <tr>
        <th>위험요인</th>
        <th>빈도(1-4)</th>
        <th>강도(1-4)</th>
        <th>위험성</th>
        <th>판정</th>
        <th>감소대책</th>
      </tr>
    </thead>
    <tbody id="ra-items-body"></tbody>
  </table>
  <button onclick="addRiskItem()">+ 위험요인 추가</button>
</div>
```

### 위험성 자동 계산 JS

```javascript
function calcRisk(freq, sev) {
  const score = freq * sev;
  let level, badge;
  if (score <= 4)      { level = '허용가능';  badge = 'bg-success'; }
  else if (score <= 9) { level = '개선필요';  badge = 'bg-warning'; }
  else                 { level = '즉시개선'; badge = 'bg-danger'; }
  return { score, level, badge };
}

function addRiskItem() {
  const row = `
    <tr>
      <td><input class="form-control form-control-sm" placeholder="위험요인"></td>
      <td>
        <select class="form-select form-select-sm risk-freq" onchange="updateRisk(this)">
          <option value="1">1</option><option value="2">2</option>
          <option value="3">3</option><option value="4">4</option>
        </select>
      </td>
      <td>
        <select class="form-select form-select-sm risk-sev" onchange="updateRisk(this)">
          <option value="1">1</option><option value="2">2</option>
          <option value="3">3</option><option value="4">4</option>
        </select>
      </td>
      <td class="risk-score">1</td>
      <td class="risk-level"><span class="badge bg-success">허용가능</span></td>
      <td><input class="form-control form-control-sm" placeholder="감소대책"></td>
      <td><button class="btn btn-sm btn-outline-danger" onclick="this.closest('tr').remove()">삭제</button></td>
    </tr>`;
  document.getElementById('ra-items-body').insertAdjacentHTML('beforeend', row);
}
```

### 백엔드 API

```
POST /risk-assessments              등록
GET  /risk-assessments?factory_id=&type=&page= 목록
GET  /risk-assessments/{id}         상세
PATCH /risk-assessments/{id}        수정
POST  /risk-assessments/{id}/files  파일 첨부
POST  /risk-assessments/{id}/complete 완료
GET   /risk-assessments/dashboard   현황 요약
  → 최초평가 여부, 정기평가 D-day, 수시평가 미완료 건수
```

---

## 메뉴 연동

`menu-tadmin.js`에 아래 메뉴 추가:
```javascript
// 작업관리 하위
{ label: 'TBM 관리',       href: 'tbm-list.html' }

// 안전보건 (신규 메뉴 그룹) 또는 문서관리 하위
{ label: '안전보건 회의',   href: 'safety-meeting-list.html' }
{ label: '위험성평가',      href: 'risk-assessment-list.html' }
```

---

## 완료 체크리스트

```
백엔드 (tai-api)
□ POST/GET/PATCH /tbm
□ POST /tbm/transcribe (STT - Web Speech API)
□ POST /tbm/{id}/complete
□ POST/GET/PATCH /safety-meetings
□ GET /safety-meetings/schedule (주기 준수 현황)
□ POST/GET/PATCH /risk-assessments
□ GET /risk-assessments/dashboard
□ 파일 업로드 공통 (Supabase Storage)
□ Railway 배포

프론트 (tai-admin)
□ tbm-list.html (목록 + 등록 사이드패널)
  □ 녹음 버튼 (Web Speech API)
  □ STT 변환 텍스트 표시
  □ 참석자 추가 (worker_registry 연동)
□ safety-meeting-list.html (목록 + 등록 모달)
  □ 회의 유형별 표시
  □ 파일 첨부
  □ 보존 기한 D-day 표시
□ risk-assessment-list.html (목록 + 등록 모달)
  □ 위험성 자동 계산 (빈도×강도)
  □ 파일 첨부
  □ 다음 평가일 D-day 표시
□ menu-tadmin.js 메뉴 추가
□ GitHub push
```
