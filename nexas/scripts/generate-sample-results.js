const fs = require('fs');
const path = require('path');

const src = fs.readFileSync(path.join(__dirname, '..', 'paid-diagnosis-result.html'), 'utf8');

const sectors = {
  'sample-facility.html': {
    title: '건물 샘플 리포트 | TAI Safe',
    desc: 'TAI 유료진단 건물(시설) 샘플 리포트',
    topbar: 'TAI 유료진단 샘플 리포트 — 건물(시설)',
    data: {
      company_name: '(주)삼성빌딩관리',
      sector: 'BUILDING',
      sector_label: '건물',
      public_token: 'SAMPLE-BLD-2026',
      risk_level: 'MEDIUM',
      summary: { total: 18, appointment: 4, inspection: 6, action: 5, report: 2, notify: 1, law_count: 8, csia_applicable: false },
      input_data: { company_name: '(주)삼성빌딩관리', business_no: '123-45-67890', ceo_name: '김시설', address: '서울특별시 강남구 테헤란로 123', worker_count: 45, floor_area: 8500 },
      recommended_plan: { name: '건물 STANDARD', price: '99,000원/월' },
      rules_table: [
        { rule_id: 'b1', obligation_type: 'APPOINT', obligation_summary: '소방안전관리자 선임', law_name: '소방시설법', law_article: '제26조', due_days: 14, executor_type_label: '사업주', qualification_code: 'fire_safety_manager', penalty_summary: '200만원 이하 과태료', report_method_std: 'submit', online_system: '소방청', system_url: 'https://www.nema.go.kr', form_name: '소방안전관리자 선임신고서', remarks: '연면적 3,000㎡ 이상 건축물' },
        { rule_id: 'b2', obligation_type: 'APPOINT', obligation_summary: '승강기 안전관리자 선임', law_name: '승강기안전관리법', law_article: '제32조', due_days: 14, executor_type_label: '사업주', penalty_summary: '300만원 이하 과태료', report_method_std: 'submit' },
        { rule_id: 'b3', obligation_type: 'APPOINT', obligation_summary: '전기안전관리자 선임', law_name: '전기안전관리법', law_article: '제22조', executor_type_label: '사업주', qualification_code: 'electrical_safety_manager', penalty_summary: '300만원 이하 과태료' },
        { rule_id: 'b4', obligation_type: 'APPOINT', obligation_summary: '안전관리자 선임', law_name: '산업안전보건법', law_article: '제17조', due_days: 14, executor_type_label: '사업주', qualification_code: 'safety_manager', penalty_summary: '500만원 이하 과태료' },
        { rule_id: 'b5', obligation_type: 'INSPECT', obligation_summary: '건축물 정기점검', law_name: '건축법', law_article: '제35조', inspection_cycle: '2년마다', cycle_base_guide: '2년마다', executor_type_label: '건축주', penalty_summary: '300만원 이하 과태료' },
        { rule_id: 'b6', obligation_type: 'INSPECT', obligation_summary: '소방시설 자체점검', law_name: '소방시설법', law_article: '제22조', inspection_cycle: '6개월마다', executor_type_label: '소방안전관리자', penalty_summary: '1,500만원 이하 과태료' },
        { rule_id: 'b7', obligation_type: 'INSPECT', obligation_summary: '승강기 정기검사', law_name: '승강기안전관리법', law_article: '제28조', inspection_cycle: '1년마다', executor_type_label: '승강기 안전관리자', penalty_summary: '1,000만원 이하 과태료' },
        { rule_id: 'b8', obligation_type: 'INSPECT', obligation_summary: '전기설비 정기점검', law_name: '전기안전관리법', law_article: '제23조', inspection_cycle: '3년마다', executor_type_label: '전기안전관리자', penalty_summary: '300만원 이하 과태료' },
        { rule_id: 'b9', obligation_type: 'INSPECT', obligation_summary: '화재예방 안전점검', law_name: '화재예방법', law_article: '제17조', inspection_cycle: '6개월마다', penalty_summary: '200만원 이하 과태료' },
        { rule_id: 'b10', obligation_type: 'INSPECT', obligation_summary: '실내공기질 측정', law_name: '실내공기질 관리법', law_article: '제7조', inspection_cycle: '1년마다', penalty_summary: '100만원 이하 과태료' },
        { rule_id: 'b11', obligation_type: 'ACTION', obligation_summary: '근로자 안전보건교육 실시', law_name: '산업안전보건법', law_article: '제29조', inspection_cycle: '분기마다', executor_type_label: '안전관리자', penalty_summary: '500만원 이하 과태료' },
        { rule_id: 'b12', obligation_type: 'ACTION', obligation_summary: '위험성평가 실시', law_name: '산업안전보건법', law_article: '제36조', executor_type_label: '안전관리자', penalty_summary: '500만원 이하 과태료' },
        { rule_id: 'b13', obligation_type: 'ACTION', obligation_summary: '비상대피 훈련 실시', law_name: '소방시설법', law_article: '제24조', inspection_cycle: '1년마다', penalty_summary: '200만원 이하 과태료' },
        { rule_id: 'b14', obligation_type: 'ACTION', obligation_summary: '석면 안전관리', law_name: '석면안전관리법', law_article: '제12조', penalty_summary: '500만원 이하 과태료' },
        { rule_id: 'b15', obligation_type: 'ACTION', obligation_summary: '에너지 사용량 보고', law_name: '에너지이용 합리화법', law_article: '제27조', penalty_summary: '300만원 이하 과태료' },
        { rule_id: 'b16', obligation_type: 'REPORT', obligation_summary: '건축물 관리대장 작성', law_name: '건축물관리법', law_article: '제11조', report_method_std: 'keep', penalty_summary: '100만원 이하 과태료' },
        { rule_id: 'b17', obligation_type: 'REPORT', obligation_summary: '소방시설 점검결과 보고', law_name: '소방시설법', law_article: '제23조', report_method_std: 'submit', penalty_summary: '300만원 이하 과태료' },
        { rule_id: 'b18', obligation_type: 'NOTIFY', obligation_summary: '화재 발생 신고', law_name: '화재예방법', law_article: '제21조', report_method_std: 'online', penalty_summary: '' }
      ],
      inspection_schedule: {
        periodic: [
          { obligation_summary: '소방시설 자체점검', inspection_cycle: '6개월마다', executor_type_label: '소방안전관리자' },
          { obligation_summary: '화재예방 안전점검', inspection_cycle: '6개월마다', executor_type_label: '소방안전관리자' },
          { obligation_summary: '근로자 안전보건교육', inspection_cycle: '3개월마다', executor_type_label: '안전관리자' },
          { obligation_summary: '승강기 정기검사', inspection_cycle: '1년마다', executor_type_label: '승강기 안전관리자' },
          { obligation_summary: '실내공기질 측정', inspection_cycle: '1년마다', executor_type_label: '관리자' },
          { obligation_summary: '건축물 정기점검', inspection_cycle: '2년마다', executor_type_label: '건축주' }
        ],
        before_work: []
      },
      key_obligations: [
        { type: 'APPOINT', title: '소방안전관리자 선임', law_name: '소방시설법', law_article: '제26조', penalty: '200만원 이하 과태료' },
        { type: 'APPOINT', title: '안전관리자 선임', law_name: '산업안전보건법', law_article: '제17조', penalty: '500만원 이하 과태료' },
        { type: 'ACTION', title: '위험성평가 실시', law_name: '산업안전보건법', law_article: '제36조', penalty: '500만원 이하 과태료' },
        { type: 'ACTION', title: '근로자 안전보건교육 실시', law_name: '산업안전보건법', law_article: '제29조', penalty: '500만원 이하 과태료' },
        { type: 'INSPECT', title: '소방시설 자체점검', law_name: '소방시설법', law_article: '제22조', penalty: '1,500만원 이하 과태료' }
      ]
    }
  },
  'sample-manufacturing.html': {
    title: '산업(제조) 샘플 리포트 | TAI Safe',
    desc: 'TAI 유료진단 산업(제조) 샘플 리포트',
    topbar: 'TAI 유료진단 샘플 리포트 — 산업(제조)',
    data: {
      company_name: '(주)한국정밀',
      sector: 'INDUSTRY',
      sector_label: '산업',
      public_token: 'SAMPLE-IND-2026',
      risk_level: 'HIGH',
      summary: { total: 22, appointment: 3, inspection: 8, action: 8, report: 2, notify: 1, law_count: 9, csia_applicable: true },
      input_data: { company_name: '(주)한국정밀', business_no: '234-56-78901', ceo_name: '박제조', address: '경기도 안산시 단원구 공단로 45', worker_count: 120, floor_area: 12000 },
      recommended_plan: { name: '산업 BUSINESS', price: '79,000원/월' },
      rules_table: [
        { rule_id: 'm1', obligation_type: 'APPOINT', obligation_summary: '안전관리자 선임', law_name: '산업안전보건법', law_article: '제17조', due_days: 14, executor_type_label: '사업주', qualification_code: 'safety_manager', penalty_summary: '5천만원 이하 과태료' },
        { rule_id: 'm2', obligation_type: 'APPOINT', obligation_summary: '보건관리자 선임', law_name: '산업안전보건법', law_article: '제29조', due_days: 14, executor_type_label: '사업주', penalty_summary: '500만원 이하 과태료' },
        { rule_id: 'm3', obligation_type: 'APPOINT', obligation_summary: '전기안전관리자 선임', law_name: '전기안전관리법', law_article: '제22조', executor_type_label: '사업주', qualification_code: 'electrical_safety_manager', penalty_summary: '300만원 이하 과태료' },
        { rule_id: 'm4', obligation_type: 'INSPECT', obligation_summary: '유해위험기계·기구 점검', law_name: '산업안전보건법', law_article: '제83조', inspection_cycle: '6개월마다', executor_type_label: '안전관리자', penalty_summary: '500만원 이하 과태료' },
        { rule_id: 'm5', obligation_type: 'INSPECT', obligation_summary: '전기설비 정기점검', law_name: '전기안전관리법', law_article: '제23조', inspection_cycle: '3년마다', penalty_summary: '300만원 이하 과태료' },
        { rule_id: 'm6', obligation_type: 'INSPECT', obligation_summary: '압력용기 정기검사', law_name: '고압가스안전관리법', law_article: '제16조', inspection_cycle: '1년마다', penalty_summary: '500만원 이하 과태료' },
        { rule_id: 'm7', obligation_type: 'INSPECT', obligation_summary: '위험물 저장시설 점검', law_name: '위험물안전관리법', law_article: '제9조', inspection_cycle: '6개월마다', penalty_summary: '500만원 이하 과태료' },
        { rule_id: 'm8', obligation_type: 'INSPECT', obligation_summary: '소방시설 자체점검', law_name: '소방시설법', law_article: '제22조', inspection_cycle: '6개월마다', penalty_summary: '1,500만원 이하 과태료' },
        { rule_id: 'm9', obligation_type: 'INSPECT', obligation_summary: '환경오염 방지시설 점검', law_name: '대기환경보전법', law_article: '제39조', inspection_cycle: '6개월마다', penalty_summary: '500만원 이하 과태료' },
        { rule_id: 'm10', obligation_type: 'INSPECT', obligation_summary: '작업환경측정', law_name: '산업안전보건법', law_article: '제46조', inspection_cycle: '6개월마다', penalty_summary: '500만원 이하 과태료' },
        { rule_id: 'm11', obligation_type: 'INSPECT', obligation_summary: '특수건강검진 실시', law_name: '산업안전보건법', law_article: '제129조', inspection_cycle: '1년마다', penalty_summary: '500만원 이하 과태료' },
        { rule_id: 'm12', obligation_type: 'ACTION', obligation_summary: '위험성평가 실시', law_name: '산업안전보건법', law_article: '제36조', executor_type_label: '안전관리자', penalty_summary: '500만원 이하 과태료' },
        { rule_id: 'm13', obligation_type: 'ACTION', obligation_summary: '근로자 안전보건교육', law_name: '산업안전보건법', law_article: '제29조', inspection_cycle: '분기마다', penalty_summary: '500만원 이하 과태료' },
        { rule_id: 'm14', obligation_type: 'ACTION', obligation_summary: '개인보호구 지급', law_name: '산업안전보건법', law_article: '제34조', penalty_summary: '1,000만원 이하 과태료' },
        { rule_id: 'm15', obligation_type: 'ACTION', obligation_summary: '유해위험방지계획서 작성', law_name: '산업안전보건법', law_article: '제38조', penalty_summary: '500만원 이하 과태료' },
        { rule_id: 'm16', obligation_type: 'ACTION', obligation_summary: '안전보건관리체계 구축', law_name: '중대재해처벌법', law_article: '제4조', penalty_summary: '징역 1년 또는 10억원 이하 벌금' },
        { rule_id: 'm17', obligation_type: 'ACTION', obligation_summary: '화학물질 취급 교육', law_name: '화학물질관리법', law_article: '제32조', penalty_summary: '500만원 이하 과태료' },
        { rule_id: 'm18', obligation_type: 'ACTION', obligation_summary: '배출시설 정상운영', law_name: '대기환경보전법', law_article: '제31조', penalty_summary: '500만원 이하 과태료' },
        { rule_id: 'm19', obligation_type: 'ACTION', obligation_summary: 'TBM(안전점검회의) 실시', law_name: '산업안전보건법', law_article: '제29조', inspection_cycle: '매일', penalty_summary: '500만원 이하 과태료' },
        { rule_id: 'm20', obligation_type: 'REPORT', obligation_summary: '산업재해 발생 보고', law_name: '산업안전보건법', law_article: '제57조', report_method_std: 'submit', penalty_summary: '1,000만원 이하 과태료' },
        { rule_id: 'm21', obligation_type: 'REPORT', obligation_summary: '유해위험방지계획서 제출', law_name: '산업안전보건법', law_article: '제38조', report_method_std: 'submit', penalty_summary: '500만원 이하 과태료' },
        { rule_id: 'm22', obligation_type: 'NOTIFY', obligation_summary: '중대산업재해 발생 신고', law_name: '중대재해처벌법', law_article: '제6조', report_method_std: 'online', penalty_summary: '징역 1년 또는 10억원 이하 벌금' }
      ],
      inspection_schedule: {
        periodic: [
          { obligation_summary: 'TBM(안전점검회의)', inspection_cycle: '매일', executor_type_label: '관리감독자' },
          { obligation_summary: '유해위험기계·기구 점검', inspection_cycle: '6개월마다', executor_type_label: '안전관리자' },
          { obligation_summary: '작업환경측정', inspection_cycle: '6개월마다', executor_type_label: '보건관리자' },
          { obligation_summary: '압력용기 정기검사', inspection_cycle: '1년마다', executor_type_label: '안전관리자' },
          { obligation_summary: '특수건강검진', inspection_cycle: '1년마다', executor_type_label: '보건관리자' }
        ],
        before_work: []
      },
      key_obligations: [
        { type: 'APPOINT', title: '안전관리자 선임', law_name: '산업안전보건법', law_article: '제17조', penalty: '5천만원 이하 과태료' },
        { type: 'APPOINT', title: '보건관리자 선임', law_name: '산업안전보건법', law_article: '제29조', penalty: '500만원 이하 과태료' },
        { type: 'ACTION', title: '안전보건관리체계 구축', law_name: '중대재해처벌법', law_article: '제4조', penalty: '징역 1년 또는 10억원 이하 벌금' },
        { type: 'ACTION', title: '위험성평가 실시', law_name: '산업안전보건법', law_article: '제36조', penalty: '500만원 이하 과태료' },
        { type: 'ACTION', title: '개인보호구 지급', law_name: '산업안전보건법', law_article: '제34조', penalty: '1,000만원 이하 과태료' },
        { type: 'INSPECT', title: '작업환경측정', law_name: '산업안전보건법', law_article: '제46조', penalty: '500만원 이하 과태료' }
      ]
    }
  },
  'sample-construction.html': {
    title: '건설 샘플 리포트 | TAI Safe',
    desc: 'TAI 유료진단 건설 샘플 리포트',
    topbar: 'TAI 유료진단 샘플 리포트 — 건설',
    data: {
      company_name: '(주)대한건설',
      sector: 'CONSTRUCTION',
      sector_label: '건설',
      public_token: 'SAMPLE-CON-2026',
      risk_level: 'HIGH',
      summary: { total: 20, appointment: 3, inspection: 7, action: 7, report: 2, notify: 1, law_count: 7, csia_applicable: true },
      input_data: { company_name: '(주)대한건설', business_no: '345-67-89012', ceo_name: '이건설', address: '서울특별시 송파구 올림픽로 300', worker_count: 50, floor_area: 0 },
      recommended_plan: { name: '건설 STANDARD', price: '145,000원/월' },
      rules_table: [
        { rule_id: 'c1', obligation_type: 'APPOINT', obligation_summary: '안전관리자 선임', law_name: '산업안전보건법', law_article: '제17조', due_days: 7, executor_type_label: '시공자', qualification_code: 'safety_manager', penalty_summary: '5천만원 이하 과태료' },
        { rule_id: 'c2', obligation_type: 'APPOINT', obligation_summary: '건설안전관리기술자 배치', law_name: '건설기술진흥법', law_article: '제62조', due_days: 7, executor_type_label: '시공자', qualification_code: 'construction_safety_judge', penalty_summary: '500만원 이하 과태료' },
        { rule_id: 'c3', obligation_type: 'APPOINT', obligation_summary: '관리감독자 지정', law_name: '산업안전보건법', law_article: '제16조', due_days: 7, executor_type_label: '시공자', penalty_summary: '500만원 이하 과태료' },
        { rule_id: 'c4', obligation_type: 'INSPECT', obligation_summary: '가설구조물 점검', law_name: '산업안전보건기준에관한규칙', law_article: '제75조', inspection_cycle: '1개월마다', executor_type_label: '안전관리자', penalty_summary: '500만원 이하 과태료' },
        { rule_id: 'c5', obligation_type: 'INSPECT', obligation_summary: '방호장치 기능점검', law_name: '산업안전보건기준에관한규칙', law_article: '제38조', inspection_cycle: '1개월마다', penalty_summary: '500만원 이하 과태료' },
        { rule_id: 'c6', obligation_type: 'INSPECT', obligation_summary: '크레인 정기검사', law_name: '산업안전보건법', law_article: '제83조', inspection_cycle: '1년마다', penalty_summary: '500만원 이하 과태료' },
        { rule_id: 'c7', obligation_type: 'INSPECT', obligation_summary: '전기설비 점검', law_name: '전기안전관리법', law_article: '제23조', inspection_cycle: '1년마다', penalty_summary: '300만원 이하 과태료' },
        { rule_id: 'c8', obligation_type: 'INSPECT', obligation_summary: '소방시설 점검', law_name: '소방시설법', law_article: '제22조', inspection_cycle: '6개월마다', penalty_summary: '1,500만원 이하 과태료' },
        { rule_id: 'c9', obligation_type: 'INSPECT', obligation_summary: '비계·거푸집 점검', law_name: '산업안전보건기준에관한규칙', law_article: '제74조', inspection_cycle: '1개월마다', penalty_summary: '500만원 이하 과태료' },
        { rule_id: 'c10', obligation_type: 'INSPECT', obligation_summary: '굴착작업 안전점검', law_name: '산업안전보건기준에관한규칙', law_article: '제78조', inspection_cycle: '매일', executor_type_label: '관리감독자', penalty_summary: '500만원 이하 과태료' },
        { rule_id: 'c11', obligation_type: 'ACTION', obligation_summary: '위험성평가 실시', law_name: '산업안전보건법', law_article: '제36조', executor_type_label: '안전관리자', penalty_summary: '500만원 이하 과태료' },
        { rule_id: 'c12', obligation_type: 'ACTION', obligation_summary: '안전보건교육 실시', law_name: '산업안전보건법', law_article: '제29조', inspection_cycle: '분기마다', penalty_summary: '500만원 이하 과태료' },
        { rule_id: 'c13', obligation_type: 'ACTION', obligation_summary: '개인보호구 지급', law_name: '산업안전보건법', law_article: '제34조', penalty_summary: '1,000만원 이하 과태료' },
        { rule_id: 'c14', obligation_type: 'ACTION', obligation_summary: '안전보건관리체계 구축', law_name: '중대재해처벌법', law_article: '제4조', penalty_summary: '징역 1년 또는 10억원 이하 벌금' },
        { rule_id: 'c15', obligation_type: 'ACTION', obligation_summary: 'TBM(안전점검회의) 실시', law_name: '산업안전보건법', law_article: '제29조', inspection_cycle: '매일', penalty_summary: '500만원 이하 과태료' },
        { rule_id: 'c16', obligation_type: 'ACTION', obligation_summary: '작업허가제 운영', law_name: '산업안전보건기준에관한규칙', law_article: '제38조', penalty_summary: '500만원 이하 과태료' },
        { rule_id: 'c17', obligation_type: 'ACTION', obligation_summary: '유해위험방지계획서 작성', law_name: '산업안전보건법', law_article: '제38조', penalty_summary: '500만원 이하 과태료' },
        { rule_id: 'c18', obligation_type: 'REPORT', obligation_summary: '유해위험방지계획서 제출', law_name: '산업안전보건법', law_article: '제38조', report_method_std: 'submit', penalty_summary: '500만원 이하 과태료' },
        { rule_id: 'c19', obligation_type: 'REPORT', obligation_summary: '산업재해 발생 보고', law_name: '산업안전보건법', law_article: '제57조', report_method_std: 'submit', penalty_summary: '1,000만원 이하 과태료' },
        { rule_id: 'c20', obligation_type: 'NOTIFY', obligation_summary: '중대산업재해 발생 신고', law_name: '중대재해처벌법', law_article: '제6조', report_method_std: 'online', penalty_summary: '징역 1년 또는 10억원 이하 벌금' }
      ],
      inspection_schedule: {
        periodic: [
          { obligation_summary: 'TBM(안전점검회의)', inspection_cycle: '매일', executor_type_label: '관리감독자' },
          { obligation_summary: '굴착작업 안전점검', inspection_cycle: '매일', executor_type_label: '관리감독자' },
          { obligation_summary: '가설구조물 점검', inspection_cycle: '1개월마다', executor_type_label: '안전관리자' },
          { obligation_summary: '방호장치 기능점검', inspection_cycle: '1개월마다', executor_type_label: '안전관리자' },
          { obligation_summary: '안전보건교육', inspection_cycle: '3개월마다', executor_type_label: '안전관리자' },
          { obligation_summary: '소방시설 점검', inspection_cycle: '6개월마다', executor_type_label: '안전관리자' },
          { obligation_summary: '크레인 정기검사', inspection_cycle: '1년마다', executor_type_label: '안전관리자' }
        ],
        before_work: [
          { obligation_summary: '작업 시작 전 안전점검', title: '작업 시작 전 안전점검', executor_type_label: '관리감독자' }
        ]
      },
      key_obligations: [
        { type: 'APPOINT', title: '안전관리자 선임', law_name: '산업안전보건법', law_article: '제17조', penalty: '5천만원 이하 과태료' },
        { type: 'APPOINT', title: '건설안전관리기술자 배치', law_name: '건설기술진흥법', law_article: '제62조', penalty: '500만원 이하 과태료' },
        { type: 'ACTION', title: '위험성평가 실시', law_name: '산업안전보건법', law_article: '제36조', penalty: '500만원 이하 과태료' },
        { type: 'ACTION', title: '개인보호구 지급', law_name: '산업안전보건법', law_article: '제34조', penalty: '1,000만원 이하 과태료' },
        { type: 'ACTION', title: '안전보건교육 실시', law_name: '산업안전보건법', law_article: '제29조', penalty: '500만원 이하 과태료' },
        { type: 'INSPECT', title: '가설구조물 점검', law_name: '산업안전보건기준에관한규칙', law_article: '제75조', penalty: '500만원 이하 과태료' }
      ]
    }
  }
};

const runtimeScript = fs.readFileSync(path.join(__dirname, 'sample-result-runtime.js'), 'utf8');

for (const [filename, cfg] of Object.entries(sectors)) {
  let html = src;
  html = html.replace(/<meta name="description" content="[^"]*">/, `<meta name="description" content="${cfg.desc}">`);
  html = html.replace(/<title>[^<]*<\/title>/, `<title>${cfg.title}</title>`);
  html = html.replace('TAI 유료진단 결과 리포트 v5', cfg.topbar);
  const sampleData = 'const SAMPLE_DATA = ' + JSON.stringify(cfg.data, null, 2) + ';\n';
  html = html.replace(/<script>\nconst API=[\s\S]*?init\(\);\n<\/script>/, '<script>\n' + sampleData + runtimeScript + '\n</script>');
  fs.writeFileSync(path.join(__dirname, '..', filename), html);
  console.log('created', filename);
}
