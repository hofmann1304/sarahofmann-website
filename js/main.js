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
    var firstNavLink = nav.querySelector("a");

    function closeNav(returnFocus) {
      nav.classList.remove("is-open");
      document.body.classList.remove("nav-open");
      toggle.setAttribute("aria-expanded", "false");
      toggle.setAttribute("aria-label", "Menü öffnen");
      if (returnFocus) {
        toggle.focus();
      }
    }

    toggle.addEventListener("click", function () {
      var isOpen = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
      toggle.setAttribute("aria-label", isOpen ? "Menü schließen" : "Menü öffnen");
      document.body.classList.toggle("nav-open", isOpen);
      if (isOpen && firstNavLink) {
        firstNavLink.focus();
      }
    });

    nav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        closeNav(false);
      });
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && nav.classList.contains("is-open")) {
        closeNav(true);
      }
    });

    window.addEventListener("resize", function () {
      if (window.innerWidth > 760 && nav.classList.contains("is-open")) {
        closeNav(false);
      }
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

});
