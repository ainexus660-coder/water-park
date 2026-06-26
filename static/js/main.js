/* AquaVerse — interactions: navbar, reveal, counters, lightbox,
   ticket calculator, forms, popup, FAQ. */
(function () {
  "use strict";

  /* ---- Sticky navbar shade on scroll ---- */
  const nav = document.getElementById("nav");
  const onScroll = () => nav && nav.classList.toggle("scrolled", window.scrollY > 40);
  window.addEventListener("scroll", onScroll);
  onScroll();

  /* ---- Mobile menu ---- */
  const toggle = document.getElementById("navToggle");
  const links = document.getElementById("navLinks");
  if (toggle && links) {
    toggle.addEventListener("click", () => links.classList.toggle("open"));
    links.querySelectorAll("a").forEach(a =>
      a.addEventListener("click", () => links.classList.remove("open")));
  }

  /* ---- Reveal on scroll ---- */
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } });
  }, { threshold: 0.12 });
  document.querySelectorAll(".reveal").forEach(el => io.observe(el));

  /* ---- Animated counters ---- */
  const counters = document.querySelectorAll("[data-count]");
  const cObserver = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      const el = e.target, target = +el.dataset.count;
      let cur = 0; const step = Math.max(1, target / 60);
      const tick = () => {
        cur += step;
        if (cur >= target) { el.textContent = target.toLocaleString() + (el.dataset.suffix || ""); }
        else { el.textContent = Math.floor(cur).toLocaleString() + (el.dataset.suffix || ""); requestAnimationFrame(tick); }
      };
      tick(); cObserver.unobserve(el);
    });
  }, { threshold: 0.4 });
  counters.forEach(c => cObserver.observe(c));

  /* ---- Special offer popup (once per session) ---- */
  const popup = document.getElementById("offerPopup");
  if (popup && !sessionStorage.getItem("aqOfferSeen")) {
    setTimeout(() => { popup.hidden = false; }, 6000);
  }
  window.closePopup = function () {
    if (popup) { popup.hidden = true; sessionStorage.setItem("aqOfferSeen", "1"); }
  };

  /* ---- FAQ accordion ---- */
  document.querySelectorAll(".faq__q").forEach(q => {
    q.addEventListener("click", () => {
      const item = q.parentElement;
      const a = item.querySelector(".faq__a");
      const open = item.classList.toggle("open");
      a.style.maxHeight = open ? a.scrollHeight + "px" : 0;
    });
  });

  /* ---- Lightbox gallery ---- */
  const lb = document.getElementById("lightbox");
  if (lb) {
    const img = lb.querySelector("img");
    const figures = Array.from(document.querySelectorAll(".gallery-grid figure"));
    let idx = 0;
    const srcs = figures.map(f => f.querySelector("img").src);
    const show = i => { idx = (i + srcs.length) % srcs.length; img.src = srcs[idx]; };
    figures.forEach((f, i) => f.addEventListener("click", () => { lb.classList.add("open"); show(i); }));
    lb.querySelector(".lightbox__close").addEventListener("click", () => lb.classList.remove("open"));
    lb.querySelector(".prev").addEventListener("click", () => show(idx - 1));
    lb.querySelector(".next").addEventListener("click", () => show(idx + 1));
    lb.addEventListener("click", e => { if (e.target === lb) lb.classList.remove("open"); });
    document.addEventListener("keydown", e => {
      if (!lb.classList.contains("open")) return;
      if (e.key === "Escape") lb.classList.remove("open");
      if (e.key === "ArrowLeft") show(idx - 1);
      if (e.key === "ArrowRight") show(idx + 1);
    });

    /* gallery filtering */
    document.querySelectorAll(".gallery-filter button").forEach(btn => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".gallery-filter button").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        const cat = btn.dataset.cat;
        figures.forEach(f => {
          f.style.display = (cat === "all" || f.dataset.cat === cat) ? "" : "none";
        });
      });
    });
  }

  /* ---- Toast helper ---- */
  window.showToast = function (msg) {
    let t = document.querySelector(".toast");
    if (!t) { t = document.createElement("div"); t.className = "toast"; document.body.appendChild(t); }
    t.textContent = msg; t.classList.add("show");
    clearTimeout(t._timer);
    t._timer = setTimeout(() => t.classList.remove("show"), 4200);
  };

  /* ---- Ticket calculator ---- */
  const calc = document.getElementById("calc");
  if (calc) {
    const prices = JSON.parse(calc.dataset.prices);
    const counts = { adult: 0, kid: 0, senior: 0 };
    const totalEl = document.getElementById("calcTotal");
    const qr = document.getElementById("upiQr");
    const upiLink = document.getElementById("upiLink");

    const buildUpiLink = amt => {
      if (!qr) return "#";
      const p = new URLSearchParams({
        pa: qr.dataset.vpa, pn: qr.dataset.pn, cu: "INR", tn: "AquaVerse Tickets",
      });
      if (amt > 0) p.set("am", amt.toFixed(2));
      return "upi://pay?" + p.toString();
    };

    const updateUpi = total => {
      if (qr) qr.src = qr.dataset.base + "?amount=" + total;
      if (upiLink) upiLink.href = buildUpiLink(total);
    };

    const render = () => {
      Object.keys(counts).forEach(k => {
        const span = calc.querySelector(`[data-count-for="${k}"]`);
        if (span) span.textContent = counts[k];
      });
      const total = counts.adult * prices.adult + counts.kid * prices.kid + counts.senior * prices.senior;
      if (totalEl) totalEl.textContent = "₹" + total;
      updateUpi(total);
    };
    calc.querySelectorAll("[data-step]").forEach(b => {
      b.addEventListener("click", () => {
        const key = b.dataset.step, dir = +b.dataset.dir;
        counts[key] = Math.max(0, counts[key] + dir);
        render();
      });
    });
    render();
    window._ticketCounts = counts;
  }

  /* ---- Generic async form submit ---- */
  document.querySelectorAll("form[data-api]").forEach(form => {
    form.addEventListener("submit", async e => {
      e.preventDefault();
      const url = form.dataset.api;
      const payload = Object.fromEntries(new FormData(form).entries());
      if (form.id === "bookingForm" && window._ticketCounts) {
        payload.adults = window._ticketCounts.adult + "";
        payload.kids = (window._ticketCounts.kid + window._ticketCounts.senior) + "";
      }
      try {
        const res = await fetch(url, {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        const data = await res.json();
        let msg = data.message || "Done!";
        if (data.reference) msg += ` Ref: ${data.reference} · Total ₹${data.total}`;
        showToast("✅ " + msg);
        form.reset();
      } catch (err) {
        showToast("⚠️ Something went wrong. Please call us instead.");
      }
    });
  });
})();
