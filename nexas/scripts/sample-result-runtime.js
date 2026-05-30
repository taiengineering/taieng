function buildLawGroups(rules) {
  const map = {};
  rules.forEach(r => {
    const name = r.law_name || '기타';
    if (!map[name]) map[name] = { law_name: name, count: 0, rules: [] };
    map[name].count++;
    map[name].rules.push(r);
  });
  return Object.values(map);
}

const nowDate = new Date().toISOString().slice(0, 10);
const REPORT_METHOD = { keep: '자체 보관', submit: '관할 기관 제출', form: '서식 제출', online: '온라인 제출', '': '-' };
const QUAL_LABEL = {
  safety_manager: '안전관리자',
  fire_safety_manager: '소방안전관리자',
  construction_safety_judge: '건설안전판정사',
  electrical_safety_manager: '전기안전관리자',
  instructor: '교육 강사',
  qualified: '해당 자격자',
  none: '-',
  '': '-'
};
const GOV_CHECKS = [
  ['선임 의무 관련', '안전관리자 선임 신고서 사본이 있습니까?'],
  ['선임 의무 관련', '선임 자격을 증명하는 서류가 있습니까?'],
  ['점검 의무 관련', '법정 점검 기록부가 최근 3년간 보관되어 있습니까?'],
  ['점검 의무 관련', '점검 결과에 따른 시정 조치 기록이 있습니까?'],
  ['조치 의무 관련', '위험성평가 보고서가 작성되어 있습니까?'],
  ['조치 의무 관련', '안전보건교육 이수 기록이 있습니까?'],
  ['보고·신고 의무 관련', '유해위험방지계획서를 제출하셨습니까?'],
  ['보고·신고 의무 관련', '산업재해 발생 시 보고 절차가 수립되어 있습니까?']
];
const DOC_ROWS = [
  ['안전관리자 선임 신고서', '선임', '재직 기간', '고용노동부 제출'],
  ['점검 기록부', '점검', '3년', '자체 보관'],
  ['위험성평가 보고서', '조치', '3년', '연 1회 갱신'],
  ['안전보건교육 이수증', '조치', '3년', '분기별'],
  ['유해위험방지계획서', '보고', '공사 완료 시까지', 'KOSHA 제출']
];
const esc = v => (v ?? '').toString().replace(/[&<>"']/g, m => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m]));
const n = v => Number(v || 0).toLocaleString();
const clsRisk = r => {
  r = (r || 'LOW').toUpperCase();
  if (r === 'HIGH') return 'b-high';
  if (r === 'MEDIUM') return 'b-med';
  return 'b-low';
};
const parseWon = t => {
  if (!t) return 0;
  t = String(t);
  let s = 0;
  const e = t.match(/(\d+)\s*억/);
  const c = t.match(/(\d+)\s*천\s*만/);
  const m = t.match(/(\d+)\s*만/);
  if (e) s += Number(e[1]) * 1e8;
  if (c) s += Number(c[1]) * 1e7;
  if (m) s += Number(m[1]) * 1e4;
  return s;
};
const fmtWon = v => (v >= 1e8 ? `약 ${(v / 1e8).toFixed(1)}억원` : `${n(v)}원`);

function lawLink(l, a) {
  const ln = encodeURIComponent(l || '');
  const ar = encodeURIComponent(a || '');
  return `https://www.law.go.kr/법령/${ln}/${ar}`;
}

function drawGauge(level) {
  const map = { HIGH: [85, '#DC2626'], MEDIUM: [50, '#D97706'], LOW: [20, '#0F9D6A'] };
  const [pct, color] = map[level] || map.LOW;
  const start = 180;
  const sweep = start * (pct / 100);
  const toXY = d => {
    const r = d * Math.PI / 180;
    return [100 + 80 * Math.cos(r), 100 - 80 * Math.sin(r)];
  };
  const [x1, y1] = toXY(start);
  const [x2, y2] = toXY(start - sweep);
  document.getElementById('riskGauge').innerHTML = `<path d="M20 100 A80 80 0 0 1 180 100" stroke="#E2E6F0" stroke-width="14" fill="none"/><path d="M ${x1} ${y1} A 80 80 0 0 1 ${x2} ${y2}" stroke="${color}" stroke-width="14" fill="none"/><text x="100" y="90" text-anchor="middle" class="dm" style="font-size:26px;font-weight:800;fill:${color};">${pct}%</text>`;
}

function setupObserver() {
  const rows = [...document.querySelectorAll('.toc-row')];
  const m = new Map(rows.map(r => [r.getAttribute('href'), r]));
  const io = new IntersectionObserver(es => es.forEach(e => {
    if (e.isIntersecting) {
      rows.forEach(r => r.classList.remove('active'));
      const row = m.get(`#${e.target.id}`);
      if (row) row.classList.add('active');
    }
  }), { rootMargin: '-35% 0px -55% 0px', threshold: 0.01 });
  ['overview', 'sec01', 'sec02', 'sec03', 'sec04', 'sec05', 'sec06', 'secSaaS'].forEach(id => {
    const el = document.getElementById(id);
    if (el) io.observe(el);
  });
}

function setupMobileToc() {
  document.getElementById('mobileToc').addEventListener('change', e => {
    const id = e.target.value;
    const el = id && document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
}

function riskLevelFromRule(r) {
  const p = String(r.penalty_summary || '');
  if (p.includes('징역')) return 'HIGH';
  const w = parseWon(p);
  if (w >= 5e7) return 'HIGH';
  if (w >= 1e7) return 'MEDIUM';
  return 'LOW';
}

function rowHtml(label, val, key) {
  if (!val || val === '-' || val === '') return '';
  return `<div class="ac-row" data-field="${key}"><span class="ac-key">${label}</span><span class="ac-val">${val}</span></div>`;
}

function articleNoFromLawArticle(v) {
  const m = String(v || '').match(/(\d+)/);
  return m ? Number(m[1]) : 0;
}

function renderPrecedents(items) {
  if (!items || !items.length) return '<div class="small text-muted mt-1">관련 판례 없음</div>';
  return items.map(p => `<div class="prec-item"><div style="font-weight:700;">${esc(p.case_name || p.case_number || '판례')}</div><div class="small text-muted">${esc(p.court_name || '')} ${esc(p.decision_date || '')}</div><div style="margin-top:4px;">${esc(p.summary || '-')}</div></div>`).join('');
}

function loadLawDetail(btn) {
  if (btn.dataset.loaded === '1') return;
  const lawName = btn.dataset.lawName || '';
  const articleNo = Number(btn.dataset.articleNo || 0);
  const box = document.getElementById(btn.dataset.targetId);
  if (!box || !lawName || !articleNo) {
    if (box) box.innerHTML = '<div class="small text-muted">조문 정보가 없습니다.</div>';
    btn.dataset.loaded = '1';
    return;
  }
  const articleText = btn.dataset.articleText || '샘플 리포트에서는 조문 원문 미리보기가 제공되지 않습니다. 유료 진단 리포트에서 전체 원문을 확인할 수 있습니다.';
  box.innerHTML = `<div><strong>${esc(lawName)} 제${articleNo}조</strong></div><div style="white-space:pre-wrap;margin-top:6px;">${esc(articleText)}</div><div style="margin-top:8px;font-weight:700;">관련 판례</div>${renderPrecedents([])}`;
  btn.dataset.loaded = '1';
}

function renderActionCard(rule) {
  const type = (rule.obligation_type || '').toUpperCase();
  const title = esc(rule.obligation_summary || '-');
  const lawN = rule.law_name || '';
  const lawA = rule.law_article || '';
  const lawTxt = `${esc(lawN)} ${esc(lawA)}`;
  const when = esc(rule.cycle_base_guide || rule.inspection_cycle || '');
  const days = Number(rule.due_days || 0);
  const who = esc(rule.executor_type_label || '');
  const form = esc(rule.form_name || '');
  const formUrl = rule.form_url || '';
  const system = esc(rule.online_system || '');
  const sysUrl = rule.system_url || '';
  const storage = esc(REPORT_METHOD[rule.report_method_std || ''] || rule.report_method_std || '');
  const penalty = esc(rule.penalty_summary || '');
  const remarks = esc(rule.remarks || '');
  const qual = esc(QUAL_LABEL[rule.qualification_code || rule.appointment_qualification_code || ''] || '');
  const articleNo = articleNoFromLawArticle(lawA);
  const detailId = `law-detail-${esc((rule.rule_id || `${lawN}-${lawA}-${title}`).replace(/[^a-zA-Z0-9_-]/g, ''))}`;
  const articleText = esc(rule.article_text || '');
  const formVal = formUrl && form ? `${form} <a href="${esc(formUrl)}" target="_blank">→ 바로가기</a>` : form;
  const sysVal = sysUrl && system ? `${system} <a href="${esc(sysUrl)}" target="_blank">→ 바로가기</a>` : system;
  const html = `<div class="action-card type-${esc(type || 'OTHER')}"><div class="ac-head"><span class="ob ob-${esc(type || 'OTHER')}">${esc(type || 'OTHER')}</span><h4 class="ac-title">${title}</h4></div><div class="ac-body">${rowHtml('📅 기한', days > 0 ? `${days}일 이내` : when, 'when')}${rowHtml('👤 수행', who, 'who')}${rowHtml('🎓 자격', qual, 'qual')}${rowHtml('📄 서류', formVal, 'form')}${rowHtml('🖥️ 신고', sysVal, 'system')}${rowHtml('📁 보관', storage, 'storage')}${rowHtml('⚠️ 과태료', `<span class="ac-val penalty">${penalty}</span>`, 'penalty')}<div class="ac-row ac-law"><span class="ac-key">📖 근거</span><span class="ac-val"><a href="${lawLink(lawN, lawA)}" target="_blank">${lawTxt}</a><div class="law-toggle" data-target-id="${detailId}" data-law-name="${esc(lawN)}" data-article-no="${articleNo}" data-article-text="${articleText}">▼ 원문 보기</div></span></div><div class="law-detail" id="${detailId}"></div>${rowHtml('💡 비고', remarks, 'remarks')}</div></div>`;
  return html.replace('<span class="ac-val"><span class="ac-val penalty">', '<span class="ac-val penalty">').replace('</span></span>', '</span>');
}

function renderObBlock(title, cls, desc, rows) {
  return `<div class="ob-header ${cls}"><span class="ob-count">${rows.length}</span><div><div class="ob-title">${title}</div><div class="ob-desc">${desc}</div></div></div>${rows.map(renderActionCard).join('') || '<div class="text-muted small">데이터가 없습니다.</div>'}`;
}

function renderGov() {
  document.getElementById('govChecks').innerHTML = GOV_CHECKS.map((r, i) => `<div class="rc ${i < 2 ? 'red' : 'orange'}"><div class="idx">${i + 1}</div><div><div style="font-weight:800;">${esc(r[0])}</div><div>${esc(r[1])}</div></div></div>`).join('');
  document.getElementById('docTable').innerHTML = DOC_ROWS.map(r => `<tr><td>${esc(r[0])}</td><td>${esc(r[1])}</td><td>${esc(r[2])}</td><td>${esc(r[3])}</td></tr>`).join('');
}

function renderReport(d) {
  const s = d.summary || {};
  const rules = d.rules_table || [];
  const risk = (d.risk_level || 'LOW').toUpperCase();
  const token = d.public_token || 'SAMPLE';

  document.querySelectorAll('#pdfTopBtn,#pdfBottomBtn').forEach(btn => { btn.style.display = 'none'; });

  document.getElementById('coverCompany').textContent = d.company_name || '사업장';
  document.getElementById('coverSector').textContent = d.sector_label || d.sector || '-';
  document.getElementById('coverRisk').textContent = risk;
  document.getElementById('coverRisk').className = `badge ${clsRisk(risk)}`;
  document.getElementById('coverDate').textContent = `진단일 ${nowDate}`;
  document.getElementById('coverReceipt').textContent = `접수번호 ${token}`;
  drawGauge(risk);
  document.getElementById('riskGaugeLabel').textContent = risk;

  const total = Number(s.total || 0);
  const appoint = Number(s.appointment || 0);
  const inspect = Number(s.inspection || 0);
  const action = Number(s.action || 0);
  const report = Number(s.report || 0);
  const notify = Number(s.notify || 0);

  document.getElementById('overviewStats').innerHTML = `<div class="sc"><div class="k">총 의무건수</div><div class="v dm">${n(total)}</div></div><div class="sc"><div class="k">적용 법령</div><div class="v dm">${n(s.law_count || 0)}</div></div><div class="sc"><div class="k">점검 의무</div><div class="v dm">${n(inspect)}</div></div><div class="sc red"><div class="k">선임 의무</div><div class="v dm">${n(appoint)}</div></div>`;

  const donutVals = [['선임', appoint, '#1e40af'], ['점검', inspect, '#15803d'], ['조치', action, '#991b1b'], ['보고', report, '#854d0e'], ['신고', notify, '#475569']];
  const donutTotal = donutVals.reduce((a, b) => a + b[1], 0) || 1;
  let acc = 0;
  document.getElementById('obDonut').style.background = `conic-gradient(${donutVals.map(v => {
    const p = v[1] / donutTotal * 100;
    const s0 = acc;
    acc += p;
    return `${v[2]} ${s0.toFixed(1)}% ${acc.toFixed(1)}%`;
  }).join(',')})`;
  document.getElementById('donutTotal').textContent = n(donutTotal);
  document.getElementById('donutLegend').innerHTML = donutVals.map(v => `<div class="donut-legend-item"><span class="donut-legend-dot" style="background:${v[2]}"></span>${v[0]} ${n(v[1])}건</div>`).join('');

  const penaltyTotal = rules.reduce((sum, r) => sum + parseWon(r.penalty_summary), 0);
  document.getElementById('totalPenalty').textContent = fmtWon(penaltyTotal);
  document.getElementById('overviewWarn').textContent = s.csia_applicable === true
    ? '⚠ 중대재해법 적용 사업장: 사망 시 1년 이상 징역 또는 10억원 이하 벌금, 경영책임자 형사처벌 대상입니다.'
    : '주요 의무 이행 증빙 체계를 구축하면 과태료·행정처분 리스크를 크게 줄일 수 있습니다.';

  const i = d.input_data || {};
  document.getElementById('profileGrid').innerHTML = `<div class="profile-item"><div class="profile-val dm">${esc(d.sector_label || d.sector || '-')}</div><div>섹터</div></div><div class="profile-item"><div class="profile-val dm">${n(i.worker_count || 0)}</div><div>근로자</div></div><div class="profile-item"><div class="profile-val dm">${i.floor_area ? n(i.floor_area) : '-'}</div><div>면적</div></div><div class="profile-item"><div class="profile-val dm">${risk}</div><div>위험등급</div></div>`;
  document.getElementById('sec01Table').innerHTML = [
    ['사업장명', i.company_name || d.company_name || '-', 'WHO'],
    ['사업자등록번호', i.business_no || '-', 'WHO'],
    ['대표자', i.ceo_name || '-', 'WHO'],
    ['소재지', i.address || '-', 'WHERE'],
    ['상시근로자', i.worker_count ? `${n(i.worker_count)}명` : '-', 'WHAT'],
    ['면적', i.floor_area ? `${n(i.floor_area)}㎡` : '-', 'WHAT']
  ].map(r => `<tr><td>${esc(r[0])}</td><td>${esc(r[1])}</td><td>${esc(r[2])}</td></tr>`).join('');
  document.getElementById('sec01Info').textContent = s.csia_applicable === true
    ? `상시근로자 ${n(i.worker_count || 0)}명으로 중대재해처벌법 적용 대상입니다.`
    : '중대재해처벌법 적용 여부는 고용형태/실질 인원 기준으로 추가 검토하세요.';

  const lawGroups = (d.law_groups || buildLawGroups(rules)).slice().sort((a, b) => (b.count || 0) - (a.count || 0));
  const maxLaw = Math.max(...lawGroups.map(x => x.count || 0), 1);
  document.getElementById('lawBarChart').innerHTML = lawGroups.map(g => `<div class="bar-row"><div class="bar-label">${esc(g.law_name || '-')}</div><div class="bar-track"><div class="bar-fill" style="width:${((g.count || 0) / maxLaw * 100)}%"><span>${n(g.count || 0)}건</span></div></div></div>`).join('') || '<div class="small text-muted">법령 그룹 데이터가 없습니다.</div>';
  document.getElementById('sec02Table').innerHTML = lawGroups.map(g => {
    const tc = {};
    (g.rules || []).forEach(r => {
      const t = r.obligation_type || 'OTHER';
      tc[t] = (tc[t] || 0) + 1;
    });
    const typeText = Object.entries(tc).map(([k, v]) => `${k} ${v}`).join(' / ');
    return `<tr><td>${esc(g.law_name || '-')}</td><td>${n(g.count || 0)}건</td><td>${esc(typeText || '-')}</td></tr>`;
  }).join('');
  document.getElementById('sec02Hl').innerHTML = `<div><div class="n dm">${n(total)}</div><div class="t">총 의무건수</div></div><div><div class="n dm">${n(s.law_count || lawGroups.length)}</div><div class="t">적용 법령</div></div><div><div class="n dm">${n(inspect)}</div><div class="t">점검 의무</div></div><div><div class="n dm">${n(appoint)}</div><div class="t">선임 의무</div></div>`;

  document.getElementById('sec03Stats').innerHTML = `<div class="sc"><div class="k">적용 법령</div><div class="v dm">${n(s.law_count || 0)}</div></div><div class="sc"><div class="k">선임 의무</div><div class="v dm">${n(appoint)}</div></div><div class="sc"><div class="k">정기 점검</div><div class="v dm">${n(inspect)}</div></div><div class="sc red"><div class="k">즉시조치 필요</div><div class="v dm">${n(action)}</div></div>`;

  const appointRows = rules.filter(r => (r.obligation_type || '') === 'APPOINT');
  const inspectRows = rules.filter(r => (r.obligation_type || '') === 'INSPECT');
  const actionRows = rules.filter(r => (r.obligation_type || '') === 'ACTION');
  const reportRows = rules.filter(r => (r.obligation_type || '') === 'REPORT');
  const notifyRows = rules.filter(r => (r.obligation_type || '') === 'NOTIFY');
  document.getElementById('obBlocks').innerHTML = renderObBlock('선임 의무', 'appoint', '법령에서 정한 자격자를 반드시 배치해야 하는 의무', appointRows)
    + renderObBlock('점검·검사 의무', 'inspect', '정기/수시 점검 주기 준수와 결과 기록 보관 의무', inspectRows)
    + renderObBlock('조치 의무', 'action', '위험요인 발견 시 즉시 시정 및 재발방지 조치 의무', actionRows)
    + renderObBlock('보고 의무', 'report', '법정 기한 내 제출·보고 의무', reportRows)
    + renderObBlock('신고 의무', 'notify', '발생 즉시 통보 및 신고 의무', notifyRows);

  document.querySelectorAll('.ac-row[data-field]').forEach(row => {
    const v = row.querySelector('.ac-val')?.textContent.trim();
    if (!v || v === '-') row.style.display = 'none';
  });
  document.querySelectorAll('.law-toggle').forEach(btn => btn.addEventListener('click', () => {
    const box = document.getElementById(btn.dataset.targetId);
    if (!box) return;
    const open = box.classList.toggle('open');
    btn.textContent = open ? '▲ 원문 닫기' : '▼ 원문 보기';
    if (open) loadLawDetail(btn);
  }));

  const periodic = ((d.inspection_schedule || {}).periodic || []);
  const before = ((d.inspection_schedule || {}).before_work || []);
  const groups = {};
  periodic.forEach(it => {
    const u = String(it.inspection_cycle || it.cycle || '').toLowerCase();
    let k = '기타';
    if (u.includes('year') || u.includes('년')) k = '연간';
    else if (u.includes('6') || u.includes('half') || u.includes('반기')) k = '반기';
    else if (u.includes('3') || u.includes('quarter') || u.includes('분기')) k = '분기';
    else if (u.includes('month') || u.includes('개월') || u.includes('월')) k = '매월';
    else if (u.includes('day') || u.includes('매일') || u.includes('일')) k = '수시';
    (groups[k] = groups[k] || []).push(it);
  });
  if (before.length) groups['수시'] = (groups['수시'] || []).concat(before);
  document.getElementById('timeline').innerHTML = ['매월', '분기', '반기', '연간', '수시', '기타'].filter(k => groups[k] && groups[k].length).map(k => `<div class="tl-group"><div class="tl-period">${k}</div>${groups[k].map(it => `<div class="tl-item"><span>${esc(it.obligation_summary || it.title || it.rule_id || '점검 항목')}</span><span>${esc(it.executor_type_label || it.executor || '')}</span></div>`).join('')}</div>`).join('') || '<div class="small text-muted">점검 일정 데이터가 없습니다.</div>';

  const pRows = rules.filter(r => !!r.penalty_summary).map(r => ({ ...r, won: parseWon(r.penalty_summary), risk: riskLevelFromRule(r) }));
  document.getElementById('sec04Penalty').textContent = fmtWon(pRows.reduce((a, b) => a + b.won, 0));
  const topP = pRows.slice().sort((a, b) => b.won - a.won).slice(0, 10);
  const maxP = Math.max(...topP.map(x => x.won), 1);
  document.getElementById('penaltyBars').innerHTML = topP.map(r => `<div class="bar-row"><div class="bar-label">${esc(r.obligation_summary || r.law_name || '-')}</div><div class="bar-track"><div class="bar-fill red" style="width:${r.won / maxP * 100}%"><span>${fmtWon(r.won)}</span></div></div></div>`).join('') || '<div class="small text-muted">처벌 데이터가 없습니다.</div>';
  document.getElementById('sec04Table').innerHTML = pRows.map(r => `<tr><td>${esc(r.obligation_summary || '-')}</td><td>${esc(r.law_name || '-')}</td><td>${esc(r.law_article || '-')}</td><td class="td-red">${esc(r.penalty_summary || '-')}</td><td><span class="badge ${clsRisk(r.risk)}">${r.risk}</span></td></tr>`).join('') || '<tr><td colspan="5">처벌 항목 없음</td></tr>';
  document.getElementById('csiaPb').textContent = s.csia_applicable === true
    ? '중대재해법: 사망사고 1년 이상 징역 또는 10억원 이하 벌금 가능'
    : '중대재해법 적용 여부를 별도 검토하세요.';

  renderGov();
  const key = d.key_obligations || [];
  const nowList = key.filter(x => String(x.type || x.obligation_type || '').toUpperCase() === 'APPOINT' && (x.penalty || x.penalty_summary)).slice(0, 3);
  const shortList = key.filter(x => String(x.type || x.obligation_type || '').toUpperCase() === 'ACTION' && (x.penalty || x.penalty_summary)).slice(0, 5);
  const periodicList = key.filter(x => String(x.type || x.obligation_type || '').toUpperCase() === 'INSPECT');
  document.getElementById('actNow').innerHTML = nowList.map((x, i) => `<div class="rc red"><div class="idx">${i + 1}</div><div><div style="font-weight:700;">${esc(x.title || x.obligation_summary || '-')}</div><div style="font-size:8pt;color:var(--gray-600);">근거: ${esc(x.law || x.law_name || '-')} / 미이행: ${esc(x.penalty || x.penalty_summary || '-')}</div></div></div>`).join('') || '<div class="small text-muted">즉시 조치 항목 없음</div>';
  document.getElementById('actShort').innerHTML = shortList.map((x, i) => `<div class="rc orange"><div class="idx">${i + 1}</div><div><div style="font-weight:700;">${esc(x.title || x.obligation_summary || '-')}</div><div style="font-size:8pt;color:var(--gray-600);">근거: ${esc(x.law || x.law_name || '-')} / 미이행: ${esc(x.penalty || x.penalty_summary || '-')}</div></div></div>`).join('') || '<div class="small text-muted">단기 조치 항목 없음</div>';
  document.getElementById('actPeriodic').textContent = periodicList.length
    ? `정기 점검 대상 ${periodicList.length}건: 매년/반기/분기/월 반복 점검 대상입니다.`
    : '정기 점검 항목을 추가 확인하세요.';
  document.getElementById('actChecklist').innerHTML = key.map(x => `<li><div><div style="font-weight:700;">${esc(x.title || x.obligation_summary || '-')}</div><div style="font-size:8pt;color:var(--gray-600);">${esc(x.law_article || x.law || '-')} - ${esc(x.penalty || x.penalty_summary || '-')}</div></div></li>`).join('') || '<li><div>체크리스트 항목 없음</div></li>';

  const rp = d.recommended_plan || {};
  document.getElementById('cmpPrice').textContent = rp.price || '도입 상담';
  if ((rp.name || '').includes('건물')) document.getElementById('planB').classList.add('reco');
  else if ((rp.name || '').includes('산업')) document.getElementById('planI').classList.add('reco');
  else if ((rp.name || '').includes('건설')) document.getElementById('planC').classList.add('reco');

  setupObserver();
  setupMobileToc();
}

function init() {
  renderReport(SAMPLE_DATA);
}

init();
