# engine-legal.html 자동점검리포트 수정
## 담당: Claude 프론트 창

## 문제
`renderReportCards` 함수에서 섹터편중 감지를 `unmapped > 0` 조건으로 잘못 처리.
uunmapped=0이 되자 섹터편중 항목도 같이 사라짐.

## 해결
`/engine-legal/stats` API 응답에 `rules_by_sector` 필드 존재.

이것을 활용해 renderReportCards를 아래로 수정:

```javascript
function renderReportCards(unmapped, formUnmapped, s) {
  var byS = s.rules_by_sector || {};
  var B  = byS.BUILDING        || 0;
  var M  = byS.MANUFACTURING   || 0;
  var C  = byS.CONSTRUCTION    || 0;

  // 섹터 편중 판단: M 또는 C가 B의 40% 미만이면 편중
  var biasCount = (M < B * 0.4 ? 1 : 0) + (C < B * 0.4 ? 1 : 0);
  var issues = [];

  // 1. 섹터 편중 (조건: biasCount > 0)
  if (biasCount > 0) {
    issues.push({
      cls: 'warning',
      icon: 'tabler-layout-distribute-horizontal',
      title: '섹터 편중 감지',
      badge: '검토필요 warning',
      desc: 'BUILDING ' + B + '개 / 제조업 ' + M + '개 / 건설 ' + C + '개 — 비율 불균형',
      count: biasCount + '개 섹터',
      pct: Math.min(100, Math.round((B - Math.min(M, C)) / (B || 1) * 100))
    });
  }

  // 2. 서식 미연결 (조건: formUnmapped > 0)
  if (formUnmapped > 0) {
    issues.push({
      cls: 'warning', icon: 'tabler-file-off',
      title: '서식 미연결', badge: '보완필요 warning',
      desc: '신고·보고 룰 중 form_code 없는 룰',
      count: formUnmapped + '개',
      pct: Math.min(100, Math.round(formUnmapped / 200 * 100))
    });
  }

  // 3. 별표 미완성 (항상 표시)
  issues.push({
    cls: 'warning', icon: 'tabler-database-off',
    title: '별표 미완성', badge: '수집필요 secondary',
    desc: '고압가스 종류·기준 데이터 미수집',
    count: '1개', pct: 10
  });

  // 렌더링
  var html = '<div class="row g-3">';
  issues.forEach(function(item) {
    var bp = item.badge.split(' ');
    var bc = bp[1]==='danger' ? 'bg-danger' : (bp[1]==='warning' ? 'bg-warning text-dark' : 'bg-secondary');
    var colCls = issues.length === 1 ? '12' : '6';
    html += '<div class="col-md-' + colCls + '">';
    html += '<div class="report-item ' + item.cls + ' p-3 border">';
    html += '<div class="d-flex align-items-start gap-3">';
    html += '<div class="avatar avatar-sm bg-label-' + item.cls + ' rounded flex-shrink-0"><i class="icon-base ti ' + item.icon + ' text-' + item.cls + '"></i></div>';
    html += '<div class="flex-grow-1">';
    html += '<div class="d-flex align-items-center gap-2 mb-1"><strong class="small">' + item.title + '</strong><span class="badge ' + bc + '">' + bp[0] + '</span></div>';
    html += '<div class="text-body-secondary small mb-2">' + item.desc + '</div>';
    html += '<div class="d-flex align-items-center gap-2"><div class="report-progress flex-grow-1"><div class="report-progress-fill" style="width:' + item.pct + '%;background:' + (item.cls==='danger'?'#ea5455':'#ff9f43') + '"></div></div>';
    html += '<span class="badge bg-label-' + item.cls + ' text-dark">' + item.count + '</span></div>';
    html += '</div></div></div></div>';
  });
  html += '</div>';

  document.getElementById('report-body').innerHTML = html;
  var hasDanger = issues.some(function(i) { return i.cls === 'danger'; });
  document.getElementById('report-count-badge').textContent = issues.length + '건 발견';
  document.getElementById('report-count-badge').className = 'badge ' + (hasDanger ? 'bg-danger' : 'bg-warning text-dark') + ' fs-6';
}
```

## 수정 대상 파일
`admin/full-version/html/horizontal-menu-template/engine-legal.html`

기존 `renderReportCards` 함수 전체 교체.

## git commit
`fix: engine-legal.html 섹터편중감지 리포트 수정 (rules_by_sector 활용)`
