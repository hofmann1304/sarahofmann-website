document.addEventListener("DOMContentLoaded", function () {
  var yearEl = document.getElementById("year");
  if (yearEl) {
    yearEl.textContent = new Date().getFullYear();
  }

  // Faint brand watermark (the logo's swirl, orbit ring & scattered dots)
  // echoed behind the page content. Path prefix is derived from the header
  // logo's own src so this keeps working when opened directly via file://.
  var headerLogo = document.querySelector(".brand img");
  if (headerLogo) {
    var prefix = headerLogo.getAttribute("src").split("assets/images/")[0];
    var watermark = document.createElement("img");
    watermark.className = "brand-watermark";
    watermark.src = prefix + "assets/images/logo-icon-watermark.png";
    watermark.alt = "";
    watermark.setAttribute("aria-hidden", "true");
    document.body.insertBefore(watermark, document.body.firstChild);
  }

  var toggle = document.querySelector(".nav-toggle");
  var nav = document.querySelector(".main-nav");

  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var isOpen = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
    });

    nav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  var revealTargets = document.querySelectorAll(
    ".insight-card, .card-panel, .about-grid > *, .contact-layout > *"
  );

  function isInViewport(el) {
    var rect = el.getBoundingClientRect();
    return rect.top < window.innerHeight && rect.bottom > 0;
  }

  if (revealTargets.length && "IntersectionObserver" in window) {
    revealTargets.forEach(function (el) {
      el.classList.add("reveal");
      // Content already above the fold on load should never be stuck
      // waiting on the observer (which can lag behind first paint) -
      // reveal it immediately and only animate what's still off-screen.
      if (isInViewport(el)) {
        el.classList.add("is-visible");
      }
    });

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.15, rootMargin: "0px 0px -40px 0px" }
    );

    revealTargets.forEach(function (el) {
      if (!el.classList.contains("is-visible")) {
        observer.observe(el);
      }
    });
  } else {
    revealTargets.forEach(function (el) {
      el.classList.add("is-visible");
    });
  }

  var prefersReducedMotion =
    window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var hasFinePointer = window.matchMedia && window.matchMedia("(pointer: fine)").matches;
  var enableMotionExtras = !prefersReducedMotion && hasFinePointer;

  // 3D tilt effect on insight cards, following the cursor position.
  if (enableMotionExtras) {
    document.querySelectorAll(".insight-card").forEach(function (card) {
      card.addEventListener("mouseenter", function () {
        card.style.transition = "transform 0.15s ease-out";
      });
      card.addEventListener("mousemove", function (e) {
        var rect = card.getBoundingClientRect();
        var px = (e.clientX - rect.left) / rect.width;
        var py = (e.clientY - rect.top) / rect.height;
        var rotateY = (px - 0.5) * 8;
        var rotateX = (0.5 - py) * 8;
        card.style.transform =
          "perspective(700px) rotateX(" + rotateX + "deg) rotateY(" + rotateY + "deg) scale(1.015)";
      });
      card.addEventListener("mouseleave", function () {
        card.style.transition = "transform 0.35s ease";
        card.style.transform = "";
      });
    });
  }

  // Sliding gradient underline that glides between nav links on hover.
  (function () {
    var navList = document.querySelector(".main-nav__list");
    if (!navList || window.matchMedia("(max-width: 760px)").matches) {
      return;
    }

    var indicator = document.createElement("span");
    indicator.className = "nav-indicator";
    navList.appendChild(indicator);

    var currentLink = navList.querySelector('a[aria-current="page"]');

    function moveIndicatorTo(link) {
      if (!link) {
        indicator.style.opacity = "0";
        return;
      }
      indicator.style.left = link.offsetLeft + "px";
      indicator.style.width = link.offsetWidth + "px";
    }

    navList.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("mouseenter", function () {
        moveIndicatorTo(link);
      });
    });

    navList.addEventListener("mouseleave", function () {
      moveIndicatorTo(currentLink);
    });

    if (currentLink) {
      requestAnimationFrame(function () {
        moveIndicatorTo(currentLink);
        indicator.classList.add("is-ready");
      });
    }
  })();

  // Thin reading-progress bar across the very top of the viewport.
  (function () {
    var bar = document.createElement("div");
    bar.className = "scroll-progress";
    bar.setAttribute("aria-hidden", "true");
    document.body.appendChild(bar);

    function updateProgress() {
      var scrollTop = window.scrollY;
      var docHeight = document.documentElement.scrollHeight - window.innerHeight;
      var pct = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
      bar.style.width = pct + "%";
    }

    window.addEventListener("scroll", updateProgress, { passive: true });
    window.addEventListener("resize", updateProgress);
    updateProgress();
  })();
});
