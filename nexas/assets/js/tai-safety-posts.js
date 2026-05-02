/**
 * 안전정보 목록 — api.taieng.co.kr/posts 연동 (기존 공개 사이트와 동일 API)
 */
(function () {
  var TAI_API_BASE = "https://api.taieng.co.kr";

  var CATEGORY_LABELS = {
    notice: "공지",
    safety_news: "안전뉴스",
    law_update: "법령안내",
    accident_case: "사고사례",
    kosha_guide: "기술지침",
    msds: "MSDS",
    hazmat: "유해화학",
    general: "안전팁",
  };

  var currentCat = "";
  var currentSearch = "";
  var currentSort = "latest";
  var currentPage = 1;
  var PAGE_SIZE = 9;
  var totalPages = 1;

  function esc(s) {
    if (s == null) return "";
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function formatDate(iso) {
    if (!iso) return "";
    var d = iso.slice(0, 10);
    return d;
  }

  function sourceLabel(src) {
    if (!src) return "TAI";
    var u = String(src).toUpperCase();
    if (u.indexOf("LIVE") >= 0) return "LIVE";
    if (u.indexOf("KOSHA") >= 0) return "KOSHA";
    if (u.indexOf("LAW") >= 0 || u.indexOf("법") >= 0) return "법제처";
    return src;
  }

  function sourceClass(src) {
    var u = String(src || "").toUpperCase();
    if (u.indexOf("LIVE") >= 0) return "tai-src-live";
    if (u.indexOf("KOSHA") >= 0) return "tai-src-kosha";
    if (u.indexOf("LAW") >= 0) return "tai-src-law";
    return "tai-src-tai";
  }

  function setLoading(on) {
    var el = document.getElementById("tai-posts-loading");
    var grid = document.getElementById("tai-posts-grid");
    if (el) el.classList.toggle("d-none", !on);
    if (grid) grid.classList.toggle("opacity-50", on);
  }

  function renderPagination() {
    var wrap = document.getElementById("tai-posts-pagination");
    if (!wrap) return;
    if (totalPages <= 1) {
      wrap.innerHTML = "";
      return;
    }
    var html = '<nav><ul class="pagination pagination-sm justify-content-center gap-1 flex-wrap">';
    if (currentPage > 1) {
      html +=
        '<li class="page-item"><a class="page-link" href="#" data-page="' +
        (currentPage - 1) +
        '">이전</a></li>';
    }
    var start = Math.max(1, currentPage - 2);
    var end = Math.min(totalPages, currentPage + 2);
    for (var i = start; i <= end; i++) {
      html +=
        '<li class="page-item' +
        (i === currentPage ? " active" : "") +
        '"><a class="page-link" href="#" data-page="' +
        i +
        '">' +
        i +
        "</a></li>";
    }
    if (currentPage < totalPages) {
      html +=
        '<li class="page-item"><a class="page-link" href="#" data-page="' +
        (currentPage + 1) +
        '">다음</a></li>';
    }
    html += "</ul></nav>";
    wrap.innerHTML = html;
    wrap.querySelectorAll("a[data-page]").forEach(function (a) {
      a.addEventListener("click", function (e) {
        e.preventDefault();
        currentPage = parseInt(a.getAttribute("data-page"), 10);
        loadPosts();
        var top = document.getElementById("tai-safety-list");
        if (top) top.scrollIntoView({ behavior: "smooth" });
      });
    });
  }

  function render(items, total) {
    var grid = document.getElementById("tai-posts-grid");
    var countEl = document.getElementById("tai-posts-count");
    if (countEl) countEl.textContent = "총 " + (total || 0) + "건";

    if (!grid) return;

    if (!items || !items.length) {
      grid.innerHTML =
        '<div class="col-12 text-center py-5"><p class="text-muted mb-0">표시할 글이 없습니다.</p></div>';
      return;
    }

    grid.innerHTML = items
      .map(function (p) {
        var cat =
          CATEGORY_LABELS[p.category] || esc(p.category || "");
        var title = esc(p.title || "");
        var sum = p.summary ? String(p.summary) : "";
        var summary = sum
          ? '<p class="small text-muted mb-2 tai-post-summary">' +
            esc(sum.slice(0, 160)) +
            (sum.length > 160 ? "…" : "") +
            "</p>"
          : "";
        var href =
          "safety-post-detail.html?id=" + encodeURIComponent(p.id);
        return (
          '<div class="col-md-6 col-lg-4">' +
          '<a href="' +
          href +
          '" class="text-decoration-none tai-safety-card-link">' +
          '<div class="single-service-inner tai-safety-card h-100">' +
          '<div class="d-flex align-items-center gap-2 mb-2 flex-wrap">' +
          '<span class="tai-src-badge ' +
          sourceClass(p.source) +
          '">' +
          esc(sourceLabel(p.source)) +
          "</span>" +
          '<span class="small text-muted">' +
          cat +
          "</span>" +
          "</div>" +
          "<h5 class='title tai-post-title'>" +
          title +
          "</h5>" +
          summary +
          '<div class="d-flex justify-content-between align-items-center mt-3 small text-muted">' +
          "<span><i class='far fa-calendar-alt me-1'></i>" +
          formatDate(p.published_at) +
          "</span>" +
          "<span><i class='far fa-eye me-1'></i>" +
          (p.view_count != null ? p.view_count : 0) +
          "</span>" +
          "</div>" +
          "</div></a></div>"
        );
      })
      .join("");
  }

  async function loadPosts() {
    setLoading(true);
    try {
      var params = new URLSearchParams();
      params.set("page", String(currentPage));
      params.set("size", String(PAGE_SIZE));
      params.set("status", "published");
      params.set("sort", currentSort === "views" ? "views" : "latest");
      if (currentCat) params.set("category", currentCat);
      if (currentSearch) params.set("search", currentSearch);

      var res = await fetch(TAI_API_BASE + "/posts?" + params.toString());
      var json = await res.json();

      if (!res.ok || !json || json.status !== "success" || !json.data) {
        throw new Error((json && json.detail) || "목록을 불러오지 못했습니다.");
      }

      var data = json.data;
      var items = data.items || [];
      var total = data.total != null ? data.total : items.length;
      totalPages = data.total_pages != null ? data.total_pages : 1;
      if (!totalPages || totalPages < 1) totalPages = 1;

      render(items, total);
      renderPagination();
    } catch (e) {
      var grid = document.getElementById("tai-posts-grid");
      if (grid) {
        grid.innerHTML =
          '<div class="col-12 text-center py-5"><p class="text-danger mb-1">' +
          esc(e.message || "오류") +
          '</p><p class="small text-muted mb-0">네트워크 또는 API 설정을 확인해 주세요.</p></div>';
      }
      var wrap = document.getElementById("tai-posts-pagination");
      if (wrap) wrap.innerHTML = "";
    } finally {
      setLoading(false);
    }
  }

  async function loadStats() {
    var elToday = document.getElementById("tai-stat-today");
    var elTotal = document.getElementById("tai-stat-total");
    if (!elToday && !elTotal) return;
    try {
      var res = await fetch(TAI_API_BASE + "/posts/stats/today");
      var json = await res.json();
      if (json.status === "success" && json.data) {
        var d = json.data;
        if (elToday)
          elToday.textContent =
            "오늘 등록 " + (d.today_count != null ? d.today_count : 0) + "건";
        if (elTotal)
          elTotal.textContent =
            "게시글 " + (d.total_count != null ? d.total_count : 0) + "건";
      }
    } catch (e) {
      if (elToday) elToday.textContent = "—";
      if (elTotal) elTotal.textContent = "—";
    }
  }

  function init() {
    document.querySelectorAll(".tai-cat-tab").forEach(function (btn) {
      btn.addEventListener("click", function () {
        document.querySelectorAll(".tai-cat-tab").forEach(function (b) {
          b.classList.remove("active");
        });
        btn.classList.add("active");
        currentCat = btn.getAttribute("data-cat") || "";
        currentPage = 1;
        loadPosts();
      });
    });

    var searchBtn = document.getElementById("tai-posts-search-btn");
    var searchInput = document.getElementById("tai-posts-search");
    if (searchBtn && searchInput) {
      searchBtn.addEventListener("click", function () {
        currentSearch = searchInput.value.trim();
        currentPage = 1;
        loadPosts();
      });
      searchInput.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
          currentSearch = searchInput.value.trim();
          currentPage = 1;
          loadPosts();
        }
      });
    }

    var sortSel = document.getElementById("tai-posts-sort");
    if (sortSel) {
      sortSel.addEventListener("change", function () {
        currentSort = sortSel.value;
        currentPage = 1;
        loadPosts();
      });
    }

    loadStats();
    loadPosts();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
