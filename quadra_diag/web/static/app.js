(function () {
  "use strict";

  /* ============================================================
     QuadraDiag v3.0 — Advanced Frontend Runtime
     ============================================================ */

  /* ===== Dark Mode ===== */
  const darkToggle = document.querySelector("[data-dark-toggle]");
  const html = document.documentElement;

  function initDarkMode() {
    const saved = localStorage.getItem("qd-dark-mode");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const isDark = saved === "true" || (saved === null && prefersDark);
    if (isDark) html.setAttribute("data-theme", "dark");
  }

  if (darkToggle) {
    darkToggle.addEventListener("click", () => {
      const isDark = html.getAttribute("data-theme") === "dark";
      if (isDark) {
        html.removeAttribute("data-theme");
        localStorage.setItem("qd-dark-mode", "false");
      } else {
        html.setAttribute("data-theme", "dark");
        localStorage.setItem("qd-dark-mode", "true");
      }
    });
  }

  initDarkMode();

  /* ===== Particle Background ===== */
  const canvas = document.getElementById("particle-canvas");
  if (canvas) {
    const ctx = canvas.getContext("2d");
    let particles = [];
    const PARTICLE_COUNT = 50;
    const CONNECTION_DIST = 120;

    function resizeCanvas() {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    }
    resizeCanvas();
    window.addEventListener("resize", resizeCanvas);

    class Particle {
      constructor() {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.vx = (Math.random() - 0.5) * 0.5;
        this.vy = (Math.random() - 0.5) * 0.5;
        this.radius = Math.random() * 2 + 1;
      }
      update() {
        this.x += this.vx;
        this.y += this.vy;
        if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
        if (this.y < 0 || this.y > canvas.height) this.vy *= -1;
      }
      draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        ctx.fillStyle = getComputedStyle(html).getPropertyValue("--accent").trim() || "#0d6b52";
        ctx.globalAlpha = 0.3;
        ctx.fill();
        ctx.globalAlpha = 1;
      }
    }

    for (let i = 0; i < PARTICLE_COUNT; i++) particles.push(new Particle());

    function animateParticles() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      particles.forEach((p, i) => {
        p.update();
        p.draw();
        for (let j = i + 1; j < particles.length; j++) {
          const dx = p.x - particles[j].x;
          const dy = p.y - particles[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < CONNECTION_DIST) {
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.strokeStyle = getComputedStyle(html).getPropertyValue("--accent").trim() || "#0d6b52";
            ctx.globalAlpha = 0.1 * (1 - dist / CONNECTION_DIST);
            ctx.lineWidth = 1;
            ctx.stroke();
            ctx.globalAlpha = 1;
          }
        }
      });
      requestAnimationFrame(animateParticles);
    }
    animateParticles();
  }

  /* ===== Navigation ===== */
  const navToggle = document.querySelector("[data-nav-toggle]");
  const navMenu = document.querySelector("[data-nav-menu]");
  if (navToggle && navMenu) {
    navToggle.addEventListener("click", () => {
      navMenu.classList.toggle("is-open");
      navToggle.classList.toggle("is-open");
    });
  }

  /* ===== Loader with timeout fallback ===== */
  const loader = document.querySelector("[data-app-loader]");
  const LOADER_TIMEOUT_MS = 8000;
  let loaderTimer = null;

  function showLoader() {
    if (!loader) return;
    loader.classList.add("is-active");
    loader.hidden = false;
    clearTimeout(loaderTimer);
    loaderTimer = setTimeout(() => {
      hideLoader();
      console.warn("Loader timeout reached — forcing hide.");
    }, LOADER_TIMEOUT_MS);
  }

  function hideLoader() {
    if (!loader) return;
    clearTimeout(loaderTimer);
    loader.classList.remove("is-active");
    setTimeout(() => {
      if (!loader.classList.contains("is-active")) loader.hidden = true;
    }, 350);
  }

  document.querySelectorAll("form").forEach((form) => {
    form.addEventListener("submit", () => {
      if (!form.hasAttribute("data-no-loader")) showLoader();
    });
  });

  window.addEventListener("load", hideLoader);
  window.addEventListener("pageshow", (e) => {
    hideLoader();
    if (e.persisted) document.querySelectorAll("form").forEach((f) => f.reset());
  });

  /* ===== Toasts with auto-dismiss ===== */
  function dismissToast(toast) {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(30px)";
    setTimeout(() => toast.remove(), 350);
  }

  document.querySelectorAll("[data-dismiss-toast]").forEach((btn) => {
    btn.addEventListener("click", () => dismissToast(btn.closest("[data-toast]")));
  });

  document.querySelectorAll("[data-toast]").forEach((toast) => {
    setTimeout(() => dismissToast(toast), 6000);
  });

  /* ===== Modals ===== */
  document.querySelectorAll("[data-open-modal]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const modal = document.getElementById(btn.getAttribute("data-open-modal"));
      if (modal) modal.showModal();
    });
  });

  document.querySelectorAll("[data-close-modal]").forEach((btn) => {
    btn.addEventListener("click", () => btn.closest("dialog")?.close());
  });

  document.querySelectorAll("dialog").forEach((dialog) => {
    dialog.addEventListener("click", (e) => { if (e.target === dialog) dialog.close(); });
  });

  /* ===== Scroll reveal ===== */
  const revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          revealObserver.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
  );

  document.querySelectorAll(".reveal").forEach((el) => revealObserver.observe(el));

  /* ===== File input ===== */
  const fileInput = document.querySelector("[data-file-input]");
  const fileLabel = document.querySelector("[data-file-label]");
  if (fileInput && fileLabel) {
    fileInput.addEventListener("change", () => {
      const name = fileInput.files?.[0]?.name;
      fileLabel.textContent = name ? `Selected: ${name}` : "Columns must match the disease template.";
    });
  }

  /* ===== Disease selector ===== */
  const selector = document.querySelector("[data-disease-selector]");
  const uploadForm = document.querySelector(".upload-form");
  const templateLink = document.querySelector("[data-template-link]");
  if (selector && uploadForm) {
    selector.addEventListener("change", () => {
      const disease = selector.value;
      uploadForm.setAttribute("action", `/batch-lab/${disease}`);
      if (templateLink) templateLink.setAttribute("href", `/templates/${disease}/download`);
    });
  }

  /* ===== Hero entrance sequence ===== */
  function runHeroEntrance() {
    document.querySelectorAll(".hero-home .reveal").forEach((el, i) => {
      setTimeout(() => el.classList.add("is-visible"), 120 + i * 140);
    });
  }

  if (document.querySelector(".hero-home")) {
    if (document.readyState === "complete") runHeroEntrance();
    else window.addEventListener("load", runHeroEntrance);
  }

  /* ===== Chart.js integration ===== */
  function getChartData(id) {
    const el = document.getElementById(id);
    if (!el) return null;
    try { return JSON.parse(el.dataset.json); } catch { return null; }
  }

  function initCharts() {
    if (typeof Chart === "undefined") return;

    const riskData = getChartData("risk-data");
    const riskCtx = document.getElementById("risk-chart");
    if (riskCtx && riskData) {
      new Chart(riskCtx, {
        type: "doughnut",
        data: {
          labels: riskData.labels,
          datasets: [{
            data: riskData.data,
            backgroundColor: riskData.colors,
            borderWidth: 0,
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: "70%",
          plugins: { legend: { position: "bottom" } },
        },
      });
    }

    const diseaseData = getChartData("disease-data");
    const diseaseCtx = document.getElementById("disease-chart");
    if (diseaseCtx && diseaseData) {
      new Chart(diseaseCtx, {
        type: "bar",
        data: {
          labels: diseaseData.labels,
          datasets: [{
            label: "Predictions",
            data: diseaseData.data,
            backgroundColor: diseaseData.colors,
            borderRadius: 8,
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } },
        },
      });
    }

    const trendData = getChartData("trend-data");
    const trendCtx = document.getElementById("trend-chart");
    if (trendCtx && trendData) {
      new Chart(trendCtx, {
        type: "line",
        data: {
          labels: trendData.labels,
          datasets: trendData.datasets.map((ds) => ({
            label: ds.label,
            data: ds.data,
            borderColor: ds.color,
            backgroundColor: ds.color + "20",
            fill: true,
            tension: 0.4,
            pointRadius: 4,
          })),
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: "top" } },
          scales: { y: { beginAtZero: true } },
        },
      });
    }
  }

  if (document.querySelector("canvas")) {
    const script = document.createElement("script");
    script.src = "https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js";
    script.onload = initCharts;
    document.head.appendChild(script);
  }

  /* ===== Risk gauge animation ===== */
  document.querySelectorAll(".risk-gauge-marker").forEach((marker) => {
    const target = parseFloat(marker.dataset.target || "0");
    setTimeout(() => { marker.style.left = `${target}%`; }, 300);
  });

  /* ===== Animated counters ===== */
  function animateCounters() {
    document.querySelectorAll(".trust-value[data-count]").forEach((el) => {
      const target = parseInt(el.dataset.count, 10) || 0;
      const duration = 1500;
      const start = performance.now();
      function update(now) {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.round(target * eased);
        if (progress < 1) requestAnimationFrame(update);
      }
      requestAnimationFrame(update);
    });
  }

  const counterObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        animateCounters();
        counterObserver.disconnect();
      }
    });
  }, { threshold: 0.3 });

  document.querySelectorAll(".section-trust").forEach((el) => counterObserver.observe(el));

  /* ===== Smooth scroll for anchor links ===== */
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", (e) => {
      const target = document.querySelector(anchor.getAttribute("href"));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  });

  /* ===== Form validation hints ===== */
  document.querySelectorAll(".form-field input").forEach((input) => {
    input.addEventListener("blur", () => {
      if (input.checkValidity()) {
        input.style.borderColor = "var(--low)";
      } else if (input.value) {
        input.style.borderColor = "var(--high)";
      }
    });
    input.addEventListener("input", () => {
      if (input.checkValidity()) input.style.borderColor = "var(--low)";
    });
  });

})();
