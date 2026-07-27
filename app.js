/* =========================================================
   Y Academy — moteur de rendu (accueil / cours / leçon)
   Données : window.ACADEMY_DATA (data.js)
   Progression : localStorage "yacademy-progress"
   ========================================================= */
(function () {
  "use strict";

  var DATA = window.ACADEMY_DATA;
  var CFG = DATA.config;
  var PKEY = "yacademy-progress";
  var BKEY = "yacademy-bookmarks";

  /* ---------- helpers ---------- */
  function qs(name) {
    return new URLSearchParams(location.search).get(name);
  }
  function el(tag, cls, html) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html !== undefined) e.innerHTML = html;
    return e;
  }
  function getProgress() {
    try { return JSON.parse(localStorage.getItem(PKEY)) || {}; }
    catch (e) { return {}; }
  }
  function setDone(courseId, lessonId) {
    var p = getProgress();
    p[courseId] = p[courseId] || {};
    p[courseId][lessonId] = true;
    localStorage.setItem(PKEY, JSON.stringify(p));
  }
  function isDone(courseId, lessonId) {
    var p = getProgress();
    return !!(p[courseId] && p[courseId][lessonId]);
  }
  function courseById(id) {
    return DATA.courses.filter(function (c) { return c.id === id; })[0];
  }
  function flatLessons(course) {
    var out = [];
    course.sections.forEach(function (s) {
      s.lessons.forEach(function (l) { out.push(l); });
    });
    return out;
  }
  function doneCount(course) {
    return flatLessons(course).filter(function (l) {
      return isDone(course.id, l.id);
    }).length;
  }
  function firstIncomplete(course) {
    var lessons = flatLessons(course);
    for (var i = 0; i < lessons.length; i++) {
      if (!isDone(course.id, lessons[i].id)) return lessons[i];
    }
    return lessons[0];
  }
  function progressLabel(done, total) {
    var pct = total ? Math.round((done / total) * 100) : 0;
    return CFG.progressLabel
      .replace("{done}", done)
      .replace("{total}", total)
      .replace("{pct}", pct);
  }

  /* Icône livre façon dessin au trait */
  var BOOK_SVG =
    '<svg viewBox="0 0 120 120" fill="none" stroke="#141413" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round">' +
    '<path d="M24 82 Q22 78 28 77 L92 70 Q97 69.5 97.5 74 L98.5 86 Q99 91 93 91.7 L30 98.5 Q24.5 99 24 94 Z" fill="#fff"/>' +
    '<path d="M28 77 Q30 72 38 71 L94 65" stroke-width="2.6"/>' +
    '<path d="M60 70 C42 66 40 40 52 32 C60 27 68 30 70 36 C76 28 88 32 88 44 C88 58 74 68 60 70 Z" fill="#e8ddc7"/>' +
    '<path d="M69 32 Q70 22 79 18" stroke-width="2.8"/>' +
    '<path d="M79 18 Q88 14 92 20 Q86 26 79 18 Z" fill="#e8ddc7" stroke-width="2.4"/>' +
    "</svg>";

  var BOOKMARK_SVG =
    '<svg viewBox="0 0 24 24"><path d="M6 3h12v18l-6-5-6 5V3z"/></svg>';

  function ringHTML(done) {
    return '<span class="ring' + (done ? " done" : "") + '"></span>';
  }

  /* ---------- header ---------- */
  function renderHeader(backHref) {
    var h = el("header", "site-header");
    var inner =
      (backHref ? '<a class="back-arrow" href="' + backHref + '">&#8592;</a>' : "") +
      '<a class="logo" href="index.html">' + CFG.siteName + "</a>" +
      '<nav class="header-nav">' +
      '<a href="' + CFG.academyUrl + '">' + CFG.academyLabel + "</a>" +
      '<a href="index.html">' + CFG.coursesLabel + "</a>" +
      '<span class="avatar"></span>' +
      "</nav>";
    h.innerHTML = inner;
    if (backHref) document.body.classList.add("has-back");
    document.body.prepend(h);
  }

  function breadcrumbHTML() {
    return (
      '<div class="breadcrumb">' +
      '<a href="index.html">' + CFG.breadcrumbRoot + "</a>" +
      '<span class="sep">/</span>' +
      '<a href="index.html">' + CFG.breadcrumbCourses + "</a>" +
      "</div>"
    );
  }

  /* ---------- page accueil ---------- */
  function renderHome(root) {
    document.title = CFG.homeTitle;
    renderHeader(null);
    var c = el("div", "home-container");
    c.innerHTML =
      breadcrumbHTML() +
      '<h1 class="home-title">' + CFG.heroTitle + "</h1>";
    DATA.courses.forEach(function (course) {
      var card = el("a", "course-card");
      card.href = "course.html?course=" + encodeURIComponent(course.id);
      card.innerHTML =
        '<span class="icon">' + BOOK_SVG + "</span>" +
        "<span>" +
        "<h2>" + course.title + "</h2>" +
        "<p>" + course.shortDescription + "</p>" +
        "</span>" +
        (course.registered
          ? '<span class="pill">' + CFG.registeredLabel + "</span>"
          : "");
      c.appendChild(card);
    });
    root.appendChild(c);
  }

  /* ---------- page cours ---------- */
  function renderCourse(root) {
    var course = courseById(qs("course")) || DATA.courses[0];
    document.title = course.title;
    renderHeader("index.html");

    var total = flatLessons(course).length;
    var done = doneCount(course);
    var pct = total ? Math.round((done / total) * 100) : 0;
    var target = firstIncomplete(course);
    var startLabel = done > 0 ? CFG.resumeLabel : CFG.startLabel;

    var c = el("div", "course-container");
    c.innerHTML =
      '<div class="course-hero">' +
      '<div class="course-hero-left">' +
      breadcrumbHTML() +
      '<h1 class="course-title">' + course.title + "</h1>" +
      "</div>" +
      '<div class="course-hero-right">' +
      '<span class="icon">' + BOOK_SVG + "</span>" +
      '<div class="progress-text">' + progressLabel(done, total) + "</div>" +
      '<div class="progress-track"><div class="progress-fill" style="width:' + pct + '%"></div></div>' +
      '<div class="hero-actions">' +
      '<a class="btn-primary" href="lesson.html?course=' + course.id + "&lesson=" + target.id + '">' + startLabel + "</a>" +
      '<button class="btn-bookmark" title="Sauvegarder">' + BOOKMARK_SVG + "</button>" +
      "</div>" +
      "</div>" +
      "</div>";
    root.appendChild(c);

    var band = el("div", "tab-band");
    band.innerHTML =
      '<div class="course-container"><span class="tab">' + CFG.curriculumLabel + "</span></div>";
    root.appendChild(band);

    var wrap = el("div", "course-container");
    var cur = el("div", "curriculum");
    cur.innerHTML = "<h2>" + CFG.courseOverviewLabel + "</h2>";

    course.sections.forEach(function (section) {
      var head = el(
        "div",
        "section-header",
        '<span class="caret">&#9660;</span>' + section.title
      );
      var list = el("ul", "lesson-list");
      section.lessons.forEach(function (lesson) {
        var li = el("li");
        var a = el("a", "lesson-row");
        a.href = "lesson.html?course=" + course.id + "&lesson=" + lesson.id;
        a.innerHTML = ringHTML(isDone(course.id, lesson.id)) + lesson.title;
        li.appendChild(a);
        list.appendChild(li);
      });
      head.addEventListener("click", function () {
        head.classList.toggle("collapsed");
        list.style.display = head.classList.contains("collapsed") ? "none" : "";
      });
      cur.appendChild(head);
      cur.appendChild(list);
    });

    wrap.appendChild(cur);
    root.appendChild(wrap);

    /* bookmark */
    var bm = c.querySelector(".btn-bookmark");
    var marks = JSON.parse(localStorage.getItem(BKEY) || "{}");
    if (marks[course.id]) bm.classList.add("saved");
    bm.addEventListener("click", function () {
      marks[course.id] = !marks[course.id];
      localStorage.setItem(BKEY, JSON.stringify(marks));
      bm.classList.toggle("saved", marks[course.id]);
    });
  }

  /* ---------- page leçon ---------- */
  function renderLesson(root) {
    var course = courseById(qs("course")) || DATA.courses[0];
    var lessons = flatLessons(course);
    var lessonId = qs("lesson") || lessons[0].id;
    var idx = lessons.findIndex(function (l) { return l.id === lessonId; });
    if (idx < 0) idx = 0;
    var lesson = lessons[idx];

    document.title = lesson.title;
    document.body.classList.add("lesson-view");
    renderHeader(null);

    var layout = el("div", "lesson-layout");

    /* sidebar */
    var side = el("aside", "lesson-sidebar");
    var sideHTML =
      '<div class="sidebar-head">' +
      "<h2>" + course.title + "</h2>" +
      '<a class="overview-link" href="course.html?course=' + course.id + '">' +
      CFG.overviewLabel + "</a>" +
      "</div>";
    course.sections.forEach(function (section) {
      sideHTML += '<div class="sidebar-section">' + section.title + "</div>";
      section.lessons.forEach(function (l) {
        var active = l.id === lesson.id;
        sideHTML +=
          '<a class="sidebar-lesson' + (active ? " active" : "") + '" ' +
          'href="lesson.html?course=' + course.id + "&lesson=" + l.id + '">' +
          ringHTML(isDone(course.id, l.id)) + l.title + "</a>";
      });
    });
    side.innerHTML = sideHTML;

    /* contenu */
    var main = el("main", "lesson-main");
    var meta = lesson.duration
      ? '<p><strong>Durée estimée :</strong> ' + lesson.duration + "</p>"
      : "";
    main.innerHTML =
      '<div class="lesson-inner">' +
      '<h1 class="lesson-title">' + lesson.title + "</h1>" +
      '<hr class="lesson-title-rule">' +
      '<div class="md-content">' + meta + lesson.html + "</div>" +
      "</div>";

    layout.appendChild(side);
    layout.appendChild(main);
    root.appendChild(layout);

    /* barre bas */
    var footer = el("div", "lesson-footer");
    var prev = idx > 0 ? lessons[idx - 1] : null;
    var next = idx < lessons.length - 1 ? lessons[idx + 1] : null;
    if (prev) {
      var bp = el("button", "btn-nav btn-prev", CFG.prevLabel);
      bp.addEventListener("click", function () {
        location.href = "lesson.html?course=" + course.id + "&lesson=" + prev.id;
      });
      footer.appendChild(bp);
    }
    var bn = el("button", "btn-nav btn-next", next ? CFG.nextLabel : CFG.completeLabel);
    bn.addEventListener("click", function () {
      setDone(course.id, lesson.id);
      if (next) {
        location.href = "lesson.html?course=" + course.id + "&lesson=" + next.id;
      } else {
        location.href = "course.html?course=" + course.id;
      }
    });
    footer.appendChild(bn);
    var fs = el("button", "btn-fullscreen", "&#x26F6;");
    fs.title = "Plein écran";
    fs.addEventListener("click", function () {
      if (!document.fullscreenElement) document.documentElement.requestFullscreen();
      else document.exitFullscreen();
    });
    footer.appendChild(fs);
    root.appendChild(footer);

    /* scroll la leçon active dans la sidebar */
    var act = side.querySelector(".sidebar-lesson.active");
    if (act) act.scrollIntoView({ block: "center" });
  }

  /* ---------- routage ---------- */
  document.addEventListener("DOMContentLoaded", function () {
    var root = document.getElementById("app");
    var page = document.body.getAttribute("data-page");
    if (page === "course") renderCourse(root);
    else if (page === "lesson") renderLesson(root);
    else renderHome(root);
  });
})();
