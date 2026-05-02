/**
 * 안전정보 상세 — GET /posts/{id}
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
    return iso.slice(0, 10);
  }

  async function load() {
    var params = new URLSearchParams(location.search);
    var id = params.get("id");
    var titleEl = document.getElementById("tai-detail-title");
    var metaEl = document.getElementById("tai-detail-meta");
    var bodyEl = document.getElementById("tai-detail-body");
    var errEl = document.getElementById("tai-detail-error");

    if (!id) {
      if (errEl) errEl.textContent = "잘못된 링크입니다.";
      return;
    }

    try {
      var res = await fetch(
        TAI_API_BASE + "/posts/" + encodeURIComponent(id)
      );
      var json = await res.json();

      if (!res.ok || !json || json.status !== "success" || !json.data) {
        throw new Error(
          (json && json.detail) || "글을 불러오지 못했습니다."
        );
      }

      var d = json.data;
      var cat = CATEGORY_LABELS[d.category] || d.category || "";

      if (titleEl) {
        titleEl.textContent = d.title || "";
      }
      if (typeof TAIDetailMeta !== "undefined" && TAIDetailMeta.setDetailMeta) {
        var sum =
          d.summary ||
          (d.content ? TAIDetailMeta.stripHtml(d.content).slice(0, 400) : "") ||
          d.title ||
          "";
        TAIDetailMeta.setDetailMeta(d.title || "안전정보", sum);
      } else {
        document.title = (d.title || "안전정보") + " | TAI Safe";
      }
      if (metaEl) {
        metaEl.innerHTML =
          '<span class="me-3"><i class="far fa-folder-open me-1"></i>' +
          esc(cat) +
          "</span>" +
          '<span class="me-3"><i class="far fa-calendar-alt me-1"></i>' +
          esc(formatDate(d.published_at)) +
          "</span>" +
          '<span><i class="far fa-eye me-1"></i>' +
          (d.view_count != null ? d.view_count : 0) +
          "</span>";
      }

      if (bodyEl) {
        var html = d.content || d.summary || "";
        if (html) {
          bodyEl.innerHTML = html;
        } else {
          bodyEl.innerHTML =
            "<p class='text-muted'>본문이 없습니다.</p>";
        }
      }

      var prev = d.prev_post;
      var next = d.next_post;
      var nav = document.getElementById("tai-detail-nav");
      if (nav) {
        var parts = [];
        if (prev && prev.id) {
          parts.push(
            '<a href="safety-post-detail.html?id=' +
              encodeURIComponent(prev.id) +
              '" class="btn btn-border btn-sm">' +
              "이전글 · " +
              esc((prev.title || "").slice(0, 40)) +
              (prev.title && prev.title.length > 40 ? "…" : "") +
              "</a>"
          );
        }
        if (next && next.id) {
          parts.push(
            '<a href="safety-post-detail.html?id=' +
              encodeURIComponent(next.id) +
              '" class="btn btn-border btn-sm">' +
              "다음글 · " +
              esc((next.title || "").slice(0, 40)) +
              (next.title && next.title.length > 40 ? "…" : "") +
              "</a>"
          );
        }
        nav.innerHTML = parts.length
          ? '<div class="d-flex flex-wrap gap-2 justify-content-between">' +
            parts.join("") +
            "</div>"
          : "";
      }
    } catch (e) {
      if (errEl) errEl.textContent = e.message || "오류가 발생했습니다.";
      if (bodyEl) bodyEl.innerHTML = "";
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", load);
  } else {
    load();
  }
})();
