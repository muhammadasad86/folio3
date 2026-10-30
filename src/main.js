(() => {
  "use strict";
  const doc = document.documentElement;
  doc.classList.add("js");
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];

  /* ---------- Split headings into masked lines ---------- */
  $$("[data-split]").forEach((el) => {
    const lines = el.innerHTML.split(/<br\s*\/?>/i);
    el.innerHTML = lines.map((l, i) => `<span class="line"><span style="--l:${i}">${l.trim()}</span></span>`).join("");
  });

  /* ---------- Page load ---------- */
  /* ---------- Hero intro: type headline → reveal subline → CTAs → stats ----------
     Every character is laid out up front (opacity only), so the block never reflows; words never break mid-word. */
  const typeEl = $(".hero__title[data-type]"), subEl = $(".hero__sub[data-type-sub]"), ctaEl = $(".hero__cta[data-type-cta]");
  let typeChars = [], caret = null;
  if (typeEl) {
    const full = typeEl.innerHTML.split(/<br\s*\/?>/i).map((l) => l.trim());
    const words = (line) => line.split(" ").map((w) => `<span class="tw">${[...w].map((ch) => `<span class="tc">${ch}</span>`).join("")}</span>`).join('<span class="tc"> </span>');
    typeEl.innerHTML = `<span class="sr-only">${full.join(" ")}</span><span aria-hidden="true">${full.map(words).join('<br><span class="tc tc--br"></span>')}</span>`;
    typeChars = $$(".tc", typeEl);
    caret = document.createElement("span"); caret.className = "type-caret";
  }
  if (subEl) {
    const txt = subEl.textContent.trim();
    subEl.innerHTML = `<span class="sr-only">${txt}</span><span aria-hidden="true">${txt.split(" ").map((w, i) => `<span class="sw" style="--w:${i}">${w}</span>`).join(" ")}</span>`;
  }
  const heroRest = () => $$(".hero [data-reveal]").forEach((el, i) => setTimeout(() => el.classList.add("is-in"), 0));
  let introDone = false;
  const runIntro = () => {
    if (introDone) return; introDone = true;
    if (!typeEl || reduced) {
      typeChars.forEach((c) => c.classList.add("on")); subEl && subEl.classList.add("is-in"); ctaEl && ctaEl.classList.add("is-in"); heroRest(); return;
    }
    let i = 0;
    const step = () => {
      const c = typeChars[i];
      if (!c) {   // headline finished
        caret.classList.add("is-done");
        setTimeout(() => subEl && subEl.classList.add("is-in"), 140);
        setTimeout(() => ctaEl && ctaEl.classList.add("is-in"), 140 + 520);
        setTimeout(heroRest, 140 + 760);
        return;
      }
      c.classList.add("on"); c.after(caret); i++;
      // ~34ms/char with slight human variance; brief beat at the space and the line break
      const next = typeChars[i], pause = !next ? 0 : next.classList.contains("tc--br") ? 170 : c.textContent === " " ? 40 : 0;
      setTimeout(step, 30 + Math.random() * 16 + pause);
    };
    typeChars[0].before(caret);
    setTimeout(step, 260);
  };
  const onLoad = () => requestAnimationFrame(() => {
    doc.classList.add("is-loaded");
    runIntro();
  });
  if (document.readyState === "complete") onLoad(); else window.addEventListener("load", onLoad, { once: true });
  // Direct navigation / refresh with a hash: re-align once fonts and layout have settled (web fonts can reflow the page)
  if (location.hash.length > 1) {
    const settle = () => { const el = document.getElementById(decodeURIComponent(location.hash.slice(1))); if (el) el.scrollIntoView({ block: "start", behavior: "auto" }); };
    Promise.all([document.fonts ? document.fonts.ready : 0, new Promise((r) => (document.readyState === "complete" ? r() : addEventListener("load", r, { once: true })))]).then(() => requestAnimationFrame(settle));
  }
  setTimeout(onLoad, 1200); // never wait on slow remote images

  /* ---------- Reveal on scroll (staggered) ---------- */
  $$("[data-stagger]").forEach((group) => [...group.children].forEach((c, i) => { c.setAttribute("data-reveal", c.getAttribute("data-reveal") || ""); c.style.setProperty("--i", i % 8); }));
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => { if (e.isIntersecting) { e.target.classList.add("is-in"); io.unobserve(e.target); } });
  }, { rootMargin: "0px 0px -10% 0px", threshold: 0.12 });
  // Items inside horizontal carousels reveal together when the track enters the viewport
  const trackIO = new IntersectionObserver((entries) => {
    entries.forEach((e) => { if (e.isIntersecting) { $$("[data-reveal]", e.target).forEach((c) => c.classList.add("is-in")); trackIO.unobserve(e.target); } });
  }, { threshold: 0.15 });
  $$(".carousel__track").forEach((t) => trackIO.observe(t));
  $$("[data-reveal], [data-split]").forEach((el) => { if (!el.closest(".hero") && !el.closest(".carousel__track")) io.observe(el); });

  /* ---------- Count-up ---------- */
  const countIO = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      countIO.unobserve(e.target);
      const el = e.target, raw = el.dataset.count, m = raw.match(/^([\d,]+)(.*)$/);
      if (!m || reduced) return;
      const target = parseInt(m[1].replace(/,/g, ""), 10), suffix = m[2], comma = m[1].includes(",");
      const fmt = (n) => (comma ? n.toLocaleString("en-US") : String(n)) + suffix;
      const t0 = performance.now(), dur = 1600;
      const tick = (t) => {
        const p = Math.min(1, (t - t0) / dur), eased = 1 - Math.pow(1 - p, 4);
        el.textContent = fmt(Math.round(target * eased));
        if (p < 1) requestAnimationFrame(tick);
      };
      el.textContent = fmt(0);
      requestAnimationFrame(tick);
    });
  }, { threshold: 0.6 });
  $$("[data-count]").forEach((el) => countIO.observe(el));

  /* ---------- Header: transparent over the hero, white after it; hides on scroll down, returns on scroll up ---------- */
  const header = $(".header"), heroEl = $(".hero");
  let lastY = Math.max(0, scrollY), travel = 0;
  const onScrollHeader = () => {
    const y = Math.max(0, scrollY), dy = y - lastY;
    const heroEnd = heroEl ? heroEl.offsetTop + heroEl.offsetHeight - header.offsetHeight : 0;
    header.classList.toggle("is-scrolled", y > 24);
    header.classList.toggle("is-solid", y > heroEnd);
    travel = (dy > 0) === (travel > 0) ? travel + dy : dy;          // distance moved in the current direction
    const locked = doc.classList.contains("menu-open") || doc.classList.contains("mega-open") || header.matches(":focus-within");
    if (y <= 80) header.classList.remove("is-hidden");             // top of the page: always visible
    else if (!locked && travel > 10) header.classList.add("is-hidden");
    else if (travel < -10) header.classList.remove("is-hidden");
    doc.classList.toggle("hdr-hidden", header.classList.contains("is-hidden"));   // lets sticky elements move up with the header
    lastY = y;
    doc.style.setProperty("--hdr", header.getBoundingClientRect().bottom + "px");
  };

  /* ---------- Desktop mega menus: shared morphing plate, directional panel switch, sliding indicator,
                hover intent, click, keyboard (←/→ between items, ↓ into a panel, Esc to close) ---------- */
  const navList = $(".nav__list"), indicator = $(".nav__indicator"), plate = $(".mega-plate"), plateCard = $(".mega-plate__card");
  const ddItems = $$(".nav__item[data-dropdown]"), topLinks = $$(".nav__item > .nav__link");
  const fineNav = matchMedia("(hover: hover) and (pointer: fine)").matches;
  let current = null;
  const moveIndicator = (item) => {
    if (!item || !indicator) { navList.classList.remove("has-indicator"); return; }
    const lab = $(".roll", item) || item, lr = navList.getBoundingClientRect(), r = lab.getBoundingClientRect();
    indicator.style.width = r.width + "px";
    indicator.style.transform = `translate(${(r.left - lr.left).toFixed(1)}px, ${(r.bottom - lr.top + 7).toFixed(1)}px)`;
    navList.classList.add("has-indicator");
  };
  const cta = $(".header .nav > .btn");
  const placeMenu = () => {                 // open just below the "Begin Your Project" button (height: tall or compact panel, see CSS)
    const b = cta && cta.offsetParent ? cta.getBoundingClientRect().bottom : header.getBoundingClientRect().bottom - 20;
    doc.style.setProperty("--mega-top", Math.round(b + 10) + "px");
  };
  const setMegaOpen = (item, open) => { item.classList.toggle("is-open", open); $(".nav__link", item).setAttribute("aria-expanded", String(open)); };
  const openMenu = (item) => {
    if (current === item) return;
    const prev = current, dir = prev ? (ddItems.indexOf(item) > ddItems.indexOf(prev) ? 1 : -1) : 0;
    doc.style.setProperty("--hdr", header.getBoundingClientRect().bottom + "px");
    if (prev) { prev.style.setProperty("--mx", -dir * 10 + "px"); prev.style.setProperty("--my", "0px"); setMegaOpen(prev, false); }
    item.style.setProperty("--mx", dir * 10 + "px"); item.style.setProperty("--my", dir ? "0px" : "-8px");
    void item.offsetWidth;                      // commit the start position before animating in
    const compact = $(".mega", item).dataset.size === "compact";
    doc.style.setProperty("--mega-cur", compact ? "var(--mega-h-sm)" : "var(--mega-h-tall)");   // shared plate eases between heights
    setMegaOpen(item, true); current = item;
    placeMenu(); doc.classList.add("mega-open"); moveIndicator(item);
  };
  const closeMenu = () => {
    if (!current) return;
    current.style.setProperty("--mx", "0px"); current.style.setProperty("--my", "-8px");
    setMegaOpen(current, false); current = null; doc.classList.remove("mega-open");
    if (!navList.matches(":hover")) moveIndicator(null);
  };
  const closeAll = closeMenu;
  addEventListener("resize", () => { if (current) placeMenu(); });
  ddItems.forEach((item) => {
    const btn = $(".nav__link", item);
    let t;
    if (fineNav) {
      item.addEventListener("mouseenter", () => { clearTimeout(t); t = setTimeout(() => openMenu(item), current ? 0 : 90); });
      item.addEventListener("mouseleave", () => { clearTimeout(t); t = setTimeout(() => { if (current === item) closeMenu(); }, 180); });
    }
    btn.addEventListener("click", () => (current === item ? closeMenu() : openMenu(item)));
    item.addEventListener("keydown", (e) => {
      if (e.key === "Escape") { closeMenu(); btn.focus(); }
      if (e.key === "ArrowDown" && e.target === btn) { e.preventDefault(); openMenu(item); const first = $(".mega__body a", item) || $(".mega a", item); if (first) { const go = () => (getComputedStyle(first).visibility === "visible" ? first.focus() : requestAnimationFrame(go)); requestAnimationFrame(go); } }
    });
    item.addEventListener("focusout", (e) => { if (!item.contains(e.relatedTarget) && current === item) closeMenu(); });
  });
  $$(".nav__list > .nav__item").forEach((item) => item.addEventListener("mouseenter", () => moveIndicator(item)));
  navList.addEventListener("mouseleave", () => moveIndicator(current));
  topLinks.forEach((l, k) => l.addEventListener("keydown", (e) => {
    if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
    e.preventDefault();
    const wasOpen = !!current, next = topLinks[(k + (e.key === "ArrowRight" ? 1 : -1) + topLinks.length) % topLinks.length], it = next.parentElement;
    if (wasOpen && it.matches("[data-dropdown]")) openMenu(it);      // switch panels first so focusout doesn't close the menu
    next.focus(); moveIndicator(it);
    if (wasOpen && !it.matches("[data-dropdown]")) closeMenu();
  }));
  topLinks.forEach((l) => l.addEventListener("focus", () => moveIndicator(l.parentElement)));
  $(".mega-scrim").addEventListener("click", closeAll);
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeAll(); });

  /* ---------- Mobile menu ---------- */
  const burger = $(".burger");
  burger.addEventListener("click", () => {
    const open = !doc.classList.contains("menu-open");
    doc.classList.toggle("menu-open", open);
    burger.setAttribute("aria-expanded", String(open));
    document.body.style.overflow = open ? "hidden" : ""; doc.style.overflow = open ? "hidden" : "";   // iOS Safari needs the root locked too
    $(".mobile-menu").toggleAttribute("inert", !open);
  });
  $$(".mobile-menu a").forEach((a) => a.addEventListener("click", () => { if (doc.classList.contains("menu-open")) burger.click(); }));
  /* accordions: top level (one open at a time) → groups; animated with grid-template-rows, closed panels are inert */
  const setOpen = (btn, open) => {
    const panel = document.getElementById(btn.getAttribute("aria-controls"));
    btn.setAttribute("aria-expanded", String(open)); panel.classList.toggle("is-open", open); panel.toggleAttribute("inert", !open);
  };
  $$(".mm-btn").forEach((b) => b.addEventListener("click", () => {
    const open = b.getAttribute("aria-expanded") !== "true";
    if (open) $$(".mm-btn[aria-expanded=true]").forEach((o) => o !== b && setOpen(o, false));
    setOpen(b, open);
  }));
  $$(".mm-group__btn").forEach((b) => b.addEventListener("click", () => setOpen(b, b.getAttribute("aria-expanded") !== "true")));
  document.addEventListener("keydown", (e) => { if (e.key === "Escape" && doc.classList.contains("menu-open")) { burger.click(); burger.focus(); } });

  /* ---------- Carousels ---------- */
  const initCarousel = (root) => {
    const track = $(".carousel__track", root);
    if (!track) return;
    const host = root.closest("section") || root;
    const prev = $("[data-prev]", host), next = $("[data-next]", host), dotsEl = $(".dots", host);
    const center = root.hasAttribute("data-center");
    const items = () => [...track.children].filter((c) => c.offsetParent !== null);
    const step = () => { const it = items(); return it.length > 1 ? it[1].offsetLeft - it[0].offsetLeft : track.clientWidth; };
    const activeIndex = () => {
      const it = items(); if (!it.length) return 0;
      const ref = center ? track.scrollLeft + track.clientWidth / 2 : track.scrollLeft + parseFloat(getComputedStyle(track).scrollPaddingLeft || 0);
      let best = 0, bd = Infinity;
      it.forEach((c, i) => { const p = center ? c.offsetLeft + c.offsetWidth / 2 : c.offsetLeft; const d = Math.abs(p - ref); if (d < bd) { bd = d; best = i; } });
      return best;
    };
    const go = (i) => {
      const it = items(); i = Math.max(0, Math.min(it.length - 1, i)); const c = it[i];
      const left = center ? c.offsetLeft - (track.clientWidth - c.offsetWidth) / 2 : c.offsetLeft - parseFloat(getComputedStyle(track).scrollPaddingLeft || 0);
      track.scrollTo({ left, behavior: reduced ? "auto" : "smooth" });
    };
    let dotBtns = [];
    const buildDots = () => {
      if (!dotsEl) return;
      const n = items().length;
      dotsEl.innerHTML = "";
      dotBtns = Array.from({ length: n }, (_, i) => { const b = document.createElement("button"); b.type = "button"; b.setAttribute("aria-label", `Go to slide ${i + 1}`); b.addEventListener("click", () => go(i)); dotsEl.appendChild(b); return b; });
    };
    const update = () => {
      const i = activeIndex(), max = track.scrollWidth - track.clientWidth - 2;
      dotBtns.forEach((b, j) => b.setAttribute("aria-current", String(j === i)));
      if (center) items().forEach((c, j) => c.classList.toggle("is-active", j === i));
      if (prev && !root.hasAttribute("data-loop")) prev.disabled = track.scrollLeft <= 2;
      if (next && !root.hasAttribute("data-loop")) next.disabled = track.scrollLeft >= max;
    };
    prev && prev.addEventListener("click", () => { const i = activeIndex(); go(root.hasAttribute("data-loop") && i === 0 ? items().length - 1 : i - 1); });
    next && next.addEventListener("click", () => { const i = activeIndex(); go(root.hasAttribute("data-loop") && i >= items().length - 1 ? 0 : i + 1); });
    let raf; track.addEventListener("scroll", () => { cancelAnimationFrame(raf); raf = requestAnimationFrame(update); }, { passive: true });
    window.addEventListener("resize", update);

    // Mouse drag (touch uses native scrolling)
    let down = false, sx = 0, sl = 0, moved = false;
    track.addEventListener("pointerdown", (e) => { if (e.pointerType !== "mouse" || e.button !== 0) return; down = true; moved = false; sx = e.clientX; sl = track.scrollLeft; });
    window.addEventListener("pointermove", (e) => { if (!down) return; const dx = e.clientX - sx; if (Math.abs(dx) > 5 && !moved) { moved = true; track.classList.add("is-dragging"); } if (moved) track.scrollLeft = sl - dx; });
    window.addEventListener("pointerup", () => { if (!down) return; down = false; if (moved) { track.classList.remove("is-dragging"); go(activeIndex()); } });
    track.addEventListener("click", (e) => { if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; } }, true);
    track.addEventListener("keydown", (e) => { if (e.key === "ArrowRight") { e.preventDefault(); go(activeIndex() + 1); } if (e.key === "ArrowLeft") { e.preventDefault(); go(activeIndex() - 1); } });

    // Autoplay (spotlight only), pauses on hover/focus/offscreen
    if (root.hasAttribute("data-autoplay") && !reduced) {
      let timer, visible = false, hover = false;
      const run = () => { clearInterval(timer); timer = setInterval(() => { if (visible && !hover && !document.hidden) next.click(); }, 5000); };
      root.addEventListener("mouseenter", () => (hover = true)); root.addEventListener("mouseleave", () => (hover = false));
      root.addEventListener("focusin", () => (hover = true)); root.addEventListener("focusout", () => (hover = false));
      new IntersectionObserver(([e]) => (visible = e.isIntersecting), { threshold: 0.4 }).observe(root);
      run();
    }
    root._refresh = () => { buildDots(); track.scrollLeft = 0; update(); };
    buildDots();
    if (center) requestAnimationFrame(() => { go(0); update(); }); else update();
  };
  $$(".carousel").forEach(initCarousel);

  /* ---------- Category filters (success stories, testimonials) ---------- */
  $$("[data-filter-for]").forEach((bar) => {
    const target = document.getElementById(bar.dataset.filterFor);
    const btns = $$("button[data-cat]", bar);
    const apply = (btn) => {
      const cat = btn.dataset.cat;
      btns.forEach((b) => b.setAttribute("aria-pressed", String(b === btn)));
      const items = $$("[data-cat]", target);
      items.forEach((it) => { const on = it.dataset.cat === cat; it.hidden = !on; if (on) { it.classList.remove("is-entering"); void it.offsetWidth; it.classList.add("is-entering"); } });
      const car = target.closest(".carousel");
      if (car && car._refresh) car._refresh();
      const live = $("[aria-live]", bar.parentElement); if (live) live.textContent = `Showing ${items.filter((i) => !i.hidden).length} ${cat} items`;
    };
    btns.forEach((b) => b.addEventListener("click", () => { apply(b); b.scrollIntoView({ block: "nearest", inline: "nearest", behavior: reduced ? "auto" : "smooth" }); }));
    apply(btns.find((b) => b.getAttribute("aria-pressed") === "true") || btns[0]);
  });

  /* ---------- Process: stacked cards. Each pinned card recedes (--k) as the cards after it slide over it ---------- */
  const pcards = $$("[data-pcard]"), pinners = pcards.map((c) => $(".pcard__inner", c));
  /* Small screens: pin the "heading + card 01" frame. Card 01 rests 43px above the fold (reference), or the frame is
     centred on taller screens; if the heading can't fit above the card, only the cards pin and the heading scrolls. */
  const procSec = $("#approach"), procAside = $(".process__aside"), procGrid = $(".process__grid");
  const svhProbe = document.createElement("div");
  svhProbe.style.cssText = "position:fixed;left:0;top:0;width:0;height:100vh;height:100svh;visibility:hidden;pointer-events:none";
  document.body.appendChild(svhProbe);
  const smallMQ = matchMedia("(max-width: 900px) and (min-height: 561px)");
  const placeProcess = () => {
    if (!procSec || !pcards.length) return;
    const pstackEl = pcards[0].parentElement;
    const release = (m) => { procAside.style.marginBottom = m ? m + "px" : ""; pstackEl.style.marginTop = m ? -m + "px" : ""; };
    if (!smallMQ.matches) { procSec.classList.remove("is-framed"); procSec.style.removeProperty("--card-pin"); procSec.style.removeProperty("--aside-top"); release(0); return; }
    const vh = svhProbe.offsetHeight, ch = pcards[0].offsetHeight, ah = procAside.offsetHeight;
    const d = parseFloat(getComputedStyle(procGrid).rowGap) || 40, stackX = (pcards.length - 1) * 6;
    const total = ah + d + ch + stackX, bottomGap = Math.max(43, (vh - total) / 2);
    let cardPin = Math.round(vh - bottomGap - ch);
    const asideTop = cardPin - d - ah, framed = asideTop >= 12;
    if (!framed) cardPin = Math.round(Math.max(16, (vh - ch - stackX) / 2));   // heading can't fit above: centre the stack instead
    procSec.style.setProperty("--card-pin", cardPin + "px");
    procSec.style.setProperty("--aside-top", Math.round(asideTop) + "px");
    procSec.classList.toggle("is-framed", framed);
    /* Release the pinned heading together with the final card (root cause of 06/06 overlapping the heading):
       a sticky box only lets go when its containing block (.process__grid) runs out, and the grid ends at the bottom
       of the card stack — i.e. one card-height + gap AFTER card 06 has already come to rest. Extending the aside's
       margin box by exactly that distance (and pulling the stack up by the same amount, so nothing moves visually)
       makes the heading, copy and CTA start scrolling at the very moment card 06 settles, then everything leaves together. */
    if (framed) {
      const last = pcards[pcards.length - 1], padB = parseFloat(getComputedStyle(pstackEl).paddingBottom) || 0;
      release(Math.round(d + stackX + last.offsetHeight + padB));
    } else release(0);
  };
  placeProcess();
  let ppKey = "";   // svh ignores mobile toolbar show/hide, so the pin never jumps while scrolling
  addEventListener("resize", () => { const k = innerWidth + "x" + svhProbe.offsetHeight; if (k !== ppKey) { ppKey = k; placeProcess(); } }, { passive: true });
  smallMQ.addEventListener && smallMQ.addEventListener("change", placeProcess);
  document.fonts && document.fonts.ready.then(placeProcess);
  let curCard = 0;
  const updateSteps = () => {
    if (!pcards.length) return;
    const rects = pcards.map((c) => c.getBoundingClientRect());
    if (rects[rects.length - 1].bottom < -50 || rects[0].top > innerHeight) return;
    // Focused card = the latest card that has (at least half) reached its resting place on the stack
    const sticky = getComputedStyle(pcards[0]).position === "sticky";
    let cur = 0;
    pcards.forEach((c, j) => {
      const rest = sticky ? parseFloat(getComputedStyle(c).top) || 0 : innerHeight * 0.3;
      if (rects[j].top <= rest + rects[j].height * 0.5) cur = j;
    });
    if (cur !== curCard) { pcards[curCard].classList.remove("is-current"); pcards[cur].classList.add("is-current"); curCard = cur; }
    if (reduced) return;
    pcards.forEach((c, i) => {
      const H = rects[i].height || 1;
      let k = 0;   // how many cards (fractionally) now sit on top of this one
      for (let j = i + 1; j < pcards.length; j++) k += Math.max(0, Math.min(1, (rects[i].bottom - rects[j].top) / H));
      const v = Math.min(k, 3).toFixed(3);
      if (pinners[i]._k !== v) { pinners[i]._k = v; pinners[i].style.setProperty("--k", v); }
    });
  };

  /* ---------- Parallax (transform only, no scroll hijack) ---------- */
  const px = $$("[data-parallax]");
  const updateParallax = () => {
    if (reduced) return;
    const vh = innerHeight, small = innerWidth < 900;
    px.forEach((el) => {
      // Measure the (untransformed) parent so the offset never feeds back into itself
      const r = el.parentElement.getBoundingClientRect();
      if (r.bottom < -200 || r.top > vh + 200) return;
      if (small && el.closest(".badges")) { el.style.transform = ""; return; }
      const speed = parseFloat(el.dataset.parallax) || 0.1;
      const offset = Math.max(-60, Math.min(60, (r.top + r.height / 2 - vh / 2) * -speed));
      el.style.transform = `translate3d(0, ${offset.toFixed(1)}px, 0)`;
    });
  };

  /* ---------- Scroll-linked page background (Farco-style): white ↔ gray ↔ black blends for every [data-bg] section ---------- */
  const bgSecs = $$("[data-bg]");
  const smooth = (x) => { x = Math.max(0, Math.min(1, x)); return x * x * x * (x * (x * 6 - 15) + 10); }; // smootherstep
  const W = [255, 255, 255], BG = { dark: [23, 24, 25], gray: [245, 245, 245], black: [0, 0, 0] };
  if (bgSecs.length) doc.classList.add("bg-fx");
  const updateBg = () => {
    if (!bgSecs.length) return;
    const vh = innerHeight; let p = 0, C = W;
    bgSecs.forEach((s) => {
      const r = s.getBoundingClientRect();
      const enter = smooth((vh * 0.9 - r.top) / Math.max(1, Math.min(vh * 0.55, r.height - vh * 0.1))); // starts as the top enters; complete at ~35% (or once a short section, e.g. the footer, is fully in view)
      const exit = smooth((vh * 0.5 - r.bottom) / (vh * 0.45)); // releases as its bottom passes 50% → 5% of the viewport
      const w = enter * (1 - exit);
      if (w > p) { p = w; C = BG[s.dataset.bg] || BG.dark; }
    });
    const c = W.map((w, i) => Math.round(w + (C[i] - w) * p));
    document.body.style.backgroundColor = `rgb(${c[0]},${c[1]},${c[2]})`;
  };

  /* ---------- Shared card interaction (from "Two Ways"): pointer-follow glow; touch gets a short pressed state ---------- */
  const fxAt = (card, ev) => {
    const r = card.getBoundingClientRect();
    card.style.setProperty("--mx", ((ev.clientX - r.left) / r.width) * 100 + "%");
    card.style.setProperty("--my", ((ev.clientY - r.top) / r.height) * 100 + "%");
  };
  $$(".fx").forEach((card) => {
    if (!reduced) card.addEventListener("pointermove", (ev) => { if (ev.pointerType === "mouse") fxAt(card, ev); }, { passive: true });
    card.addEventListener("pointerdown", (ev) => {
      if (ev.pointerType === "mouse") return;
      fxAt(card, ev); card.classList.add("is-pressed");
      clearTimeout(card._fxT); card._fxT = setTimeout(() => card.classList.remove("is-pressed"), 650);
    }, { passive: true });
    ["pointercancel", "pointerleave"].forEach((t) => card.addEventListener(t, () => { clearTimeout(card._fxT); card._fxT = setTimeout(() => card.classList.remove("is-pressed"), 120); }, { passive: true }));
  });


  /* ---------- Hero: animated dotted matrix — "digital rain" (hover inspired by boonglobal.io, 2nd fold) ----------
     Columns of tiny dots fall in streams of varied length and speed; each column repeats on its own period, so the loop
     is seamless. Near the cursor a softly diffused heat field fades dots from #F3F3F3 to #FCE9B3 and lets them cool back.
     Touch: falling only. Reduced motion: one static frame. Pauses off-screen / in background tabs. */
  (() => {
    const hero = $(".hero"), cv = hero && $(".hero__field", hero);
    if (!cv) return;
    const ctx = cv.getContext("2d");
    if (!ctx) return;
    // Variation B (data-hero-fx="grid", index-hero-b.html): Boon-style dot grid with mixed dot sizes, slow breathing swell,
    // and a wider, slower brand-yellow hover. Variation A (default) keeps the digital-rain values below unchanged.
    const GRID = hero.dataset.heroFx === "grid";
    const BASE = GRID ? [0xD9, 0xDB, 0xDF] : [0xEB, 0xEB, 0xEB], HOT = GRID ? [0xFF, 0xCB, 0x11] : [0xFC, 0xE9, 0xB3];
    const fine = matchMedia("(hover: hover) and (pointer: fine)").matches;
    const GAP = 14, R_MIN = 0.55, R_MAX = 3.3, HEAT_CELL = 18, RADIUS = GRID ? 230 : 210, LEVELS = 10, DECAY = GRID ? 1100 : 650;
    let W = 0, H = 0, cols = [], heat = new Float32Array(0), hc = 0, hr = 0;
    let mx = -1e4, my = -1e4, sx = -1e4, sy = -1e4, inside = false, visible = true, raf = 0, last = 0, t0 = performance.now();
    const rand = (a, b) => a + Math.random() * (b - a);
    const buildColumns = () => {        // per column: period, speed, and stream segments (start, length in dots, size)
      cols = [];
      const n = Math.ceil(W / GAP) + 1, off = (W - (n - 1) * GAP) / 2;
      for (let i = 0; i < n; i++) {
        const period = Math.round(rand(1.1, 1.8) * Math.max(H, 600) / GAP) * GAP, streams = [];
        let y = rand(0, period * 0.4);
        while (y < period - GAP * 3) {
          const len = Math.round(rand(3, 16)), gap = Math.round(rand(2, 14)) * GAP;
          if (y + len * GAP > period) break;
          streams.push({ y, len, s: rand(0.55, 1.1) });                                  // thin and bold streams, as in the reference
          y += len * GAP + gap;
        }
        cols.push({ x: off + i * GAP, period, speed: rand(17, 50), phase: rand(0, period), streams });
      }
    };
    const resize = () => {
      const r = hero.getBoundingClientRect(), dpr = Math.min(2, window.devicePixelRatio || 1);
      W = r.width; H = r.height; cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr); ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      hc = Math.ceil(W / HEAT_CELL) + 1; hr = Math.ceil(H / HEAT_CELL) + 1; heat = new Float32Array(hc * hr);
      if (GRID) { buildGrid(); drawGrid(reduced ? 0 : performance.now() - t0); } else { buildColumns(); draw(reduced ? 0 : performance.now() - t0); }
    };
    const updateHeat = (dt) => {
      const decay = Math.exp(-dt / DECAY), rise = 1 - Math.exp(-dt / 120);
      for (let k = 0; k < heat.length; k++) heat[k] *= decay;
      if (!inside) return;
      const e = 1 - Math.exp(-dt / 90); sx += (mx - sx) * e; sy += (my - sy) * e;       // cursor follower (soft lag)
      const c0 = Math.max(0, Math.floor((sx - RADIUS) / HEAT_CELL)), c1 = Math.min(hc - 1, Math.ceil((sx + RADIUS) / HEAT_CELL));
      const r0 = Math.max(0, Math.floor((sy - RADIUS) / HEAT_CELL)), r1 = Math.min(hr - 1, Math.ceil((sy + RADIUS) / HEAT_CELL));
      for (let r = r0; r <= r1; r++) for (let c = c0; c <= c1; c++) {
        const d = Math.hypot(c * HEAT_CELL - sx, r * HEAT_CELL - sy) / RADIUS;
        if (d >= 1) continue;
        const target = Math.pow(1 - d * d, 1.35), k = r * hc + c;                         // wider, softer diffuse falloff (no hard edge)
        if (target > heat[k]) heat[k] += (target - heat[k]) * rise;
      }
    };
    const paths = Array.from({ length: LEVELS }, () => null);
    const draw = (t) => {
      ctx.clearRect(0, 0, W, H);
      for (let l = 0; l < LEVELS; l++) paths[l] = new Path2D();
      const sec = t / 1000;
      for (const col of cols) {
        const shift = (col.phase + sec * col.speed) % col.period;
        for (let rep = -1; rep * col.period < H + col.period; rep++) {
          const base = rep * col.period + shift - col.period;
          for (const st of col.streams) {
            const y0 = base + st.y;
            if (y0 > H || y0 + st.len * GAP < 0) continue;
            for (let j = 0; j < st.len; j++) {
              const y = y0 + j * GAP;
              if (y < -2 || y > H + 2) continue;
              const hx = Math.min(hc - 1, Math.max(0, Math.round(col.x / HEAT_CELL))), hy = Math.min(hr - 1, Math.max(0, Math.round(y / HEAT_CELL)));
              const h = heat[hy * hc + hx], lvl = Math.min(LEVELS - 1, Math.floor(h * LEVELS));
              const taper = st.len > 1 ? Math.pow(j / (st.len - 1), 1.25) : 1;                 // tiny at the tail → largest at the leading (bottom) dot
              const r = (R_MIN + (R_MAX - R_MIN) * taper) * st.s * (1 + 0.45 * h);
              paths[lvl].moveTo(col.x + r, y); paths[lvl].arc(col.x, y, r, 0, Math.PI * 2);
            }
          }
        }
      }
      for (let l = 0; l < LEVELS; l++) {
        const f = l === 0 ? 0 : (l + 0.5) / LEVELS, c = BASE.map((b, i) => Math.round(b + (HOT[i] - b) * f));
        ctx.fillStyle = `rgb(${c[0]},${c[1]},${c[2]})`; ctx.fill(paths[l]);
      }
    };
    // ---- Variation B: dot grid ----
    const LV = [0, 0.6, 1.0, 1.5, 2.15], WT = [0.2, 0.34, 0.25, 0.14, 0.07];   // size levels (radius px) and how often each occurs
    let gx = new Float32Array(0), gy = gx, glv = new Uint8Array(0), gph = gx;
    const buildGrid = () => {
      const pitch = W < 700 ? 14 : 16, nx = Math.ceil(W / pitch) + 1, ny = Math.ceil(H / pitch) + 1, n = nx * ny;
      const ox = (W - (nx - 1) * pitch) / 2, oy = (H - (ny - 1) * pitch) / 2;
      gx = new Float32Array(n); gy = new Float32Array(n); glv = new Uint8Array(n); gph = new Float32Array(n);
      for (let j = 0, k = 0; j < ny; j++) for (let i = 0; i < nx; i++, k++) {
        gx[k] = ox + i * pitch; gy[k] = oy + j * pitch; gph[k] = Math.random() * Math.PI * 2;
        let u = Math.random(), l = 0; while (l < WT.length - 1 && u > WT[l]) { u -= WT[l]; l++; } glv[k] = l;
      }
    };
    const drawGrid = (t) => {
      ctx.clearRect(0, 0, W, H);
      for (let l = 0; l < LEVELS; l++) paths[l] = new Path2D();
      const sec = t / 1000;
      for (let k = 0; k < gx.length; k++) {
        const x = gx[k], y = gy[k], lv = glv[k];
        const hx = Math.min(hc - 1, Math.max(0, Math.round(x / HEAT_CELL))), hy = Math.min(hr - 1, Math.max(0, Math.round(y / HEAT_CELL)));
        const h = heat[hy * hc + hx];
        const swell = 0.72 + 0.28 * Math.sin(x * 0.011 + sec * 0.45) + 0.28 * Math.sin(y * 0.014 - sec * 0.33 + x * 0.004);   // slow breathing field
        const tw = 1 + 0.14 * Math.sin(sec * 1.5 + gph[k]);                                                                    // gentle per-dot shimmer
        const r = LV[lv] * Math.max(0.35, swell) * tw * (1 + 0.85 * h) + (lv === 0 ? 1.3 * h * h : 0);                          // hover swells dots and fills empty cells
        if (r < 0.3) continue;
        const lvl = Math.min(LEVELS - 1, Math.floor(Math.pow(h, 0.8) * LEVELS));
        paths[lvl].moveTo(x + r, y); paths[lvl].arc(x, y, r, 0, Math.PI * 2);
      }
      for (let l = 0; l < LEVELS; l++) {
        const f = l === 0 ? 0 : (l + 0.5) / LEVELS, c = BASE.map((b, i) => Math.round(b + (HOT[i] - b) * f));
        ctx.fillStyle = `rgb(${c[0]},${c[1]},${c[2]})`; ctx.fill(paths[l]);
      }
    };
    const frame = (now) => {
      const dt = last ? Math.min(now - last, 64) : 16; last = now;
      updateHeat(dt); GRID ? drawGrid(now - t0) : draw(now - t0);
      raf = visible && !document.hidden ? requestAnimationFrame(frame) : 0;
      if (!raf) last = 0;
    };
    const kick = () => { if (!raf && visible && !reduced) raf = requestAnimationFrame(frame); };
    new ResizeObserver(resize).observe(hero);
    resize();
    if (reduced) return;                                                                   // static matrix only
    new IntersectionObserver((en) => { visible = en[0].isIntersecting; if (visible) kick(); }, { threshold: 0 }).observe(hero);
    document.addEventListener("visibilitychange", kick);
    if (fine) {
      hero.addEventListener("pointermove", (ev) => {
        if (ev.pointerType && ev.pointerType !== "mouse") return;
        const r = hero.getBoundingClientRect(); mx = ev.clientX - r.left; my = ev.clientY - r.top;
        if (!inside) { sx = mx; sy = my; inside = true; }
      }, { passive: true });
      hero.addEventListener("pointerleave", () => { inside = false; });
    } else if (GRID) {                                                                     // touch: a tap briefly lights the grid where touched
      let tOff;
      hero.addEventListener("pointerdown", (ev) => {
        const r = hero.getBoundingClientRect(); mx = sx = ev.clientX - r.left; my = sy = ev.clientY - r.top; inside = true;
        clearTimeout(tOff); tOff = setTimeout(() => { inside = false; }, 650);
      }, { passive: true });
    }
    kick();
  })();

  /* ---------- Contact: rotating 3D globe (inspired by the jeskojets.com footer globe) ----------
     Lightweight canvas renderer, no dependencies: orthographic projection, lit land dots + coastlines + graticule,
     atmosphere, raised great-circle routes with travelling highlights, pulsing office markers. Drag to spin. */
  (() => {
    const stage = $("[data-globe]");
    if (!stage) return;
    const cv = $(".globe__canvas", stage), fig = stage.closest(".globe"), ctx = cv.getContext && cv.getContext("2d");
    const raw = $("#globe-data");
    if (!ctx || !raw) { if (fig) fig.classList.add("globe--off"); return; }
    const data = JSON.parse(raw.textContent), D = Math.PI / 180;
    const unpack = (b64) => { const s = atob(b64), n = s.length >> 1, o = new Float32Array(n); for (let i = 0; i < n; i++) { let v = s.charCodeAt(2 * i) | (s.charCodeAt(2 * i + 1) << 8); if (v & 0x8000) v -= 0x10000; o[i] = v / 100; } return o; };
    const vec = (lat, lon) => [Math.cos(lat * D) * Math.sin(lon * D), Math.sin(lat * D), Math.cos(lat * D) * Math.cos(lon * D)];
    const toXYZ = (ll) => { const n = ll.length >> 1, o = new Float32Array(n * 3); for (let i = 0; i < n; i++) o.set(vec(ll[2 * i], ll[2 * i + 1]), i * 3); return o; };
    const dots = toXYZ(unpack(data.dots)), coast = data.coast.map((c) => toXYZ(unpack(c)));
    const grat = [];
    for (let lon = -180; lon < 180; lon += 30) { const l = []; for (let lat = -84; lat <= 84; lat += 4) l.push(lat, lon); grat.push(toXYZ(l)); }
    for (let lat = -60; lat <= 60; lat += 30) { const l = []; for (let lon = -180; lon <= 180; lon += 4) l.push(lat, lon); grat.push(toXYZ(l)); }
    const offices = data.offices.map((o) => ({ ...o, v: vec(o.lat, o.lon) })), extra = data.extra.map((o) => vec(o.lat, o.lon));
    const byName = Object.fromEntries(offices.map((o) => [o.c, o]));
    const routes = data.routes.map(([a, b], i) => {
      const A = byName[a].v, B = byName[b].v, om = Math.acos(Math.min(1, A[0] * B[0] + A[1] * B[1] + A[2] * B[2])), N = 56, h = 0.05 + 0.2 * om / Math.PI, pts = new Float32Array((N + 1) * 3);
      for (let k = 0; k <= N; k++) { const t = k / N, s1 = Math.sin((1 - t) * om) / Math.sin(om), s2 = Math.sin(t * om) / Math.sin(om), lift = 1 + h * Math.sin(Math.PI * t);
        for (let c = 0; c < 3; c++) pts[k * 3 + c] = (A[c] * s1 + B[c] * s2) * lift; }
      return { pts, N, off: i * 0.37 };
    });
    const L = (() => { const l = [-0.5, 0.55, 0.67], m = Math.hypot(...l); return l.map((x) => x / m); })();
    const font = (getComputedStyle(document.body).getPropertyValue("--font-ui") || "sans-serif").trim();
    let W = 0, H = 0, R = 0, cx = 0, cy = 0, sc = 1;
    let rot = -40, tilt = 20, vel = reduced ? 0 : 5, auto = reduced ? 0 : 5, drag = null, visible = false, raf = 0, last = 0, now = 0;
    const resize = () => {
      const r = stage.getBoundingClientRect(), dpr = Math.min(2, window.devicePixelRatio || 1);
      W = r.width; H = r.height; cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr); ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      R = Math.min(W * (W < 600 ? 0.44 : 0.4), H * 0.43); cx = W / 2; cy = H * 0.47; sc = Math.max(0.7, Math.min(1.35, R / 240));
      draw();
    };
    let cr, sr, ct, st;
    const P = (x, y, z, out) => { const x1 = x * cr + z * sr, z1 = -x * sr + z * cr, y2 = y * ct - z1 * st, z2 = y * st + z1 * ct; out[0] = cx + R * x1; out[1] = cy - R * y2; out[2] = z2; out[3] = x1; out[4] = y2; return out; };
    const q = new Float32Array(5), q2 = new Float32Array(5);
    const line = (arr, step = 1) => { // polyline, front hemisphere only
      ctx.beginPath(); let pen = false;
      for (let i = 0; i < arr.length; i += 3 * step) { P(arr[i], arr[i + 1], arr[i + 2], q); if (q[2] > 0.02) { pen ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1]); pen = true; } else pen = false; }
      ctx.stroke();
    };
    const visibleLifted = (o) => o[2] > 0 || o[3] * o[3] + o[4] * o[4] > 1;
    const DIRS = { e: [1, 0], w: [-1, 0], n: [0, -1], s: [0, 1], ne: [0.8, -0.8], nw: [-0.8, -0.8], se: [0.8, 0.8], sw: [-0.8, 0.8] };
    const draw = () => {
      if (!W) return;
      cr = Math.cos(rot * D); sr = Math.sin(rot * D); ct = Math.cos(tilt * D); st = Math.sin(tilt * D);
      ctx.clearRect(0, 0, W, H);
      // floor shadow + atmosphere
      let g = ctx.createRadialGradient(cx, cy + R * 1.08, 0, cx, cy + R * 1.08, R * 0.95);
      g.addColorStop(0, "rgba(23,24,25,0.16)"); g.addColorStop(1, "rgba(23,24,25,0)");
      ctx.save(); ctx.translate(cx, cy + R * 1.08); ctx.scale(1, 0.16); ctx.translate(-cx, -(cy + R * 1.08)); ctx.fillStyle = g; ctx.fillRect(cx - R, cy + R * 0.1, R * 2, R * 2); ctx.restore();
      g = ctx.createRadialGradient(cx, cy, R * 0.94, cx, cy, R * 1.2);
      g.addColorStop(0, "rgba(75,126,239,0.22)"); g.addColorStop(0.45, "rgba(75,126,239,0.07)"); g.addColorStop(1, "rgba(75,126,239,0)");
      ctx.fillStyle = g; ctx.beginPath(); ctx.arc(cx, cy, R * 1.2, 0, Math.PI * 2); ctx.fill();
      // sphere body, lit from the upper left
      g = ctx.createRadialGradient(cx - R * 0.4, cy - R * 0.45, R * 0.05, cx - R * 0.1, cy - R * 0.1, R * 1.35);
      g.addColorStop(0, "#ffffff"); g.addColorStop(0.42, "#f3f5f8"); g.addColorStop(0.78, "#e1e5eb"); g.addColorStop(1, "#cdd3dc");
      ctx.fillStyle = g; ctx.beginPath(); ctx.arc(cx, cy, R, 0, Math.PI * 2); ctx.fill();
      // graticule + coastlines
      ctx.lineWidth = 0.7; ctx.strokeStyle = "rgba(23,24,25,0.055)"; grat.forEach((l) => line(l));
      ctx.lineWidth = 0.9 * sc; ctx.strokeStyle = "rgba(23,24,25,0.26)"; coast.forEach((l) => line(l));
      // land dots, shaded by the light and faded toward the limb
      const B = 7, paths = Array.from({ length: B }, () => new Path2D());
      for (let i = 0; i < dots.length; i += 3) {
        P(dots[i], dots[i + 1], dots[i + 2], q); if (q[2] <= 0.01) continue;
        const lam = Math.max(0, q[3] * L[0] + q[4] * L[1] + q[2] * L[2]), a = (0.22 + 0.78 * lam) * Math.min(1, q[2] * 3.5);
        const b = Math.min(B - 1, Math.floor(a * B)), r = (0.75 + 0.6 * q[2]) * sc;
        paths[b].moveTo(q[0] + r, q[1]); paths[b].arc(q[0], q[1], r, 0, Math.PI * 2);
      }
      paths.forEach((p, b) => { ctx.fillStyle = `rgba(28,29,31,${(0.12 + 0.6 * (b + 0.5) / B).toFixed(3)})`; ctx.fill(p); });
      // rim shading for volume
      g = ctx.createRadialGradient(cx, cy, R * 0.72, cx, cy, R);
      g.addColorStop(0, "rgba(23,24,25,0)"); g.addColorStop(1, "rgba(23,24,25,0.09)");
      ctx.fillStyle = g; ctx.beginPath(); ctx.arc(cx, cy, R, 0, Math.PI * 2); ctx.fill();
      // routes: faint arc + travelling highlight
      routes.forEach((rt) => {
        ctx.lineWidth = 1 * sc; ctx.strokeStyle = "rgba(243,39,53,0.22)"; ctx.beginPath(); let pen = false;
        for (let k = 0; k <= rt.N; k++) { P(rt.pts[k * 3], rt.pts[k * 3 + 1], rt.pts[k * 3 + 2], q); if (visibleLifted(q)) { pen ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1]); pen = true; } else pen = false; }
        ctx.stroke();
        if (reduced) return;
        const head = ((now / 3600 + rt.off) % 1.5), tail = head - 0.28;
        if (head > 1.28) return;
        for (let k = Math.max(0, Math.floor(tail * rt.N)); k < Math.min(rt.N, Math.ceil(head * rt.N)); k++) {
          const f = (k / rt.N - tail) / (head - tail); if (f <= 0) continue;
          P(rt.pts[k * 3], rt.pts[k * 3 + 1], rt.pts[k * 3 + 2], q); P(rt.pts[k * 3 + 3], rt.pts[k * 3 + 4], rt.pts[k * 3 + 5], q2);
          if (!visibleLifted(q) || !visibleLifted(q2)) continue;
          ctx.strokeStyle = f > 0.7 ? `rgba(243,39,53,${f.toFixed(3)})` : `rgba(255,203,17,${(f * 1.2).toFixed(3)})`;
          ctx.lineWidth = (1 + 1.4 * f) * sc; ctx.beginPath(); ctx.moveTo(q[0], q[1]); ctx.lineTo(q2[0], q2[1]); ctx.stroke();
        }
      });
      // markers
      const mark = (v, i, small) => {
        P(v[0], v[1], v[2], q); if (q[2] <= 0) return null;
        const a = Math.min(1, q[2] * 5);
        if (!reduced && !small) { const ph = (now / 2600 + i * 0.17) % 1; ctx.strokeStyle = `rgba(243,39,53,${((1 - ph) * 0.55 * a).toFixed(3)})`; ctx.lineWidth = 1.4; ctx.beginPath(); ctx.arc(q[0], q[1], (4 + 13 * ph) * sc, 0, Math.PI * 2); ctx.stroke(); }
        ctx.globalAlpha = a; ctx.fillStyle = "#fff"; ctx.beginPath(); ctx.arc(q[0], q[1], (small ? 3.6 : 5.6) * sc, 0, Math.PI * 2); ctx.fill();
        ctx.fillStyle = "#F32735"; ctx.beginPath(); ctx.arc(q[0], q[1], (small ? 2.2 : 3.6) * sc, 0, Math.PI * 2); ctx.fill(); ctx.globalAlpha = 1;
        return [q[0], q[1], q[2]];
      };
      extra.forEach((v, i) => mark(v, i, true));
      const labels = offices.map((o, i) => [o, mark(o.v, i, false)]);
      ctx.font = `600 ${Math.round(12 * Math.min(1.1, Math.max(0.9, sc)))}px ${font}`; ctx.textBaseline = "middle";
      labels.forEach(([o, m]) => {
        if (!m || m[2] < 0.3) return;
        const a = Math.min(1, (m[2] - 0.3) * 4), [dx, dy] = DIRS[o.dir] || DIRS.e, tw = ctx.measureText(o.c).width, w = tw + 16, h = 24, gap = 12 * sc;
        let x = m[0] + dx * gap, y = m[1] + dy * gap;
        x = dx > 0.1 ? x : dx < -0.1 ? x - w : x - w / 2; y = dy > 0.1 ? y : dy < -0.1 ? y - h : y - h / 2;
        x = Math.max(4, Math.min(W - w - 4, x)); y = Math.max(4, Math.min(H - h - 4, y));   // keep pills inside the canvas on narrow screens
        ctx.globalAlpha = a; ctx.shadowColor = "rgba(0,0,0,0.14)"; ctx.shadowBlur = 14; ctx.shadowOffsetY = 4;
        ctx.fillStyle = "#fff"; ctx.beginPath(); ctx.roundRect ? ctx.roundRect(x, y, w, h, 8) : ctx.rect(x, y, w, h); ctx.fill();
        ctx.shadowColor = "transparent"; ctx.fillStyle = "#1c1d1f"; ctx.fillText(o.c, x + 8, y + h / 2 + 0.5); ctx.globalAlpha = 1;
      });
    };
    const frame = (t) => {
      const dt = last ? Math.min(t - last, 64) : 16; last = t; now = t;
      if (!drag) { vel += (auto - vel) * (1 - Math.exp(-dt / 1400)); rot += vel * dt / 1000; }
      draw();
      raf = visible && (!reduced || drag) ? requestAnimationFrame(frame) : 0;
      if (!raf) last = 0;
    };
    const kick = () => { if (!raf) raf = requestAnimationFrame(frame); };
    new ResizeObserver(resize).observe(stage);
    resize();
    new IntersectionObserver((en) => { visible = en[0].isIntersecting; if (visible) kick(); }, { rootMargin: "100px" }).observe(stage);
    stage.addEventListener("pointerdown", (ev) => { drag = { x: ev.clientX, y: ev.clientY, t: performance.now() }; vel = 0; stage.classList.add("is-drag"); stage.setPointerCapture(ev.pointerId); kick(); });
    stage.addEventListener("pointermove", (ev) => {
      if (!drag) return;
      const t = performance.now(), dx = ev.clientX - drag.x, dy = ev.clientY - drag.y, k = 0.32 / sc;
      rot += dx * k; tilt = Math.max(-10, Math.min(45, tilt + dy * k * 0.5));
      vel = (dx * k) / Math.max(8, t - drag.t) * 1000 * 0.6; drag = { x: ev.clientX, y: ev.clientY, t };
      if (reduced) draw();
    });
    const end = () => { if (!drag) return; drag = null; stage.classList.remove("is-drag"); if (reduced) vel = 0; kick(); };
    stage.addEventListener("pointerup", end); stage.addEventListener("pointercancel", end);
  })();


  /* ---------- Technology: sticky industry list synced to the scrolling cards (Cosmoq-style) ---------- */
  (() => {
    const root = $("[data-stack]");
    if (!root) return;
    const links = $$("[data-stack-link]", root), cards = $$("[data-stack-card]", root), list = $(".stack-nav ol", root);
    let active = 0, ticking = false;
    const setActive = (i) => {
      if (i === active) return;
      active = i;
      cards.forEach((c, k) => c.classList.toggle("is-active", k === i));
      links.forEach((l, k) => (k === i ? l.setAttribute("aria-current", "true") : l.removeAttribute("aria-current")));
      if (list.scrollWidth > list.clientWidth + 2) {   // chip bar (tablet/mobile): keep the active chip in view
        const l = links[i]; list.scrollTo({ left: l.offsetLeft - (list.clientWidth - l.offsetWidth) / 2, behavior: reduced ? "auto" : "smooth" });
      }
    };
    const update = () => {
      ticking = false;
      const line = innerHeight * 0.45; let idx = 0;
      cards.forEach((c, k) => {
        const r = c.getBoundingClientRect();
        if (r.top <= line) idx = k;
        links[k].style.setProperty("--p", Math.max(0, Math.min(1, (line - r.top) / r.height)).toFixed(3));
      });
      setActive(idx);
    };
    const onScroll = () => { if (!ticking) { ticking = true; requestAnimationFrame(update); } };
    addEventListener("scroll", onScroll, { passive: true });
    addEventListener("resize", onScroll);
    links.forEach((l, k) => l.addEventListener("click", (ev) => {
      ev.preventDefault();
      const offset = innerWidth <= 1100 ? 150 : 140;
      scrollTo({ top: cards[k].getBoundingClientRect().top + scrollY - offset, behavior: reduced ? "auto" : "smooth" });
      cards[k].setAttribute("tabindex", "-1"); cards[k].focus({ preventScroll: true });
    }));
    update();
  })();

  /* ---------- Scroll loop ---------- */
  let ticking = false;
  const onScroll = () => { if (ticking) return; ticking = true; requestAnimationFrame(() => { onScrollHeader(); updateSteps(); updateParallax(); updateBg(); ticking = false; }); };
  addEventListener("scroll", onScroll, { passive: true });
  addEventListener("resize", onScroll);
  onScroll();

  /* ---------- Marquee: duplicate rows for seamless loop ---------- */
  $$(".marquee__row").forEach((row) => { const clone = [...row.children].map((n) => { const c = n.cloneNode(true); c.setAttribute("aria-hidden", "true"); c.querySelectorAll("img").forEach((i) => (i.alt = "")); return c; }); row.append(...clone); });

  /* ---------- Contact form (preview: validates, does not send) ---------- */
  const form = $("#contact-form");
  if (form) {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      let ok = true;
      $$(".field", form).forEach((f) => {
        const input = $("input, textarea", f), err = $(".field__err", f);
        let msg = "";
        if (input.required && !input.value.trim()) msg = "This field is required.";
        else if (input.type === "email" && input.value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input.value)) msg = "Enter a valid email address.";
        f.classList.toggle("is-invalid", !!msg); input.setAttribute("aria-invalid", String(!!msg)); if (err) err.textContent = msg;
        if (msg && ok) { ok = false; input.focus(); }
      });
      if (ok) { form.closest(".form-card").classList.add("is-sent"); form.reset(); $(".form-success", form.closest(".form-card")).focus(); }
    });
  }
  const sub = $("#subscribe");
  if (sub) sub.addEventListener("submit", (e) => { e.preventDefault(); const i = $("input", sub), m = $(".msg", sub); const ok = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(i.value); m.textContent = ok ? "Thanks! (Preview only — not submitted.)" : "Please enter a valid email."; if (ok) sub.reset(); });

  /* ---------- Year ---------- */
  $$("[data-year]").forEach((el) => (el.textContent = new Date().getFullYear()));

  /* ---------- Floating "Folio3 Practices" drawer ---------- */
  (() => {
    const tab = $(".pd-tab"), pd = $("#practices-drawer");
    if (!tab || !pd) return;
    const panel = $(".pd__panel", pd);
    let lastFocus = null, closeT = 0;
    const focusables = () => $$('a[href], button:not([disabled])', panel);
    const open = () => {
      clearTimeout(closeT); lastFocus = document.activeElement;
      pd.hidden = false; doc.classList.add("pd-open"); tab.setAttribute("aria-expanded", "true");
      document.body.style.overflow = "hidden"; doc.style.overflow = "hidden";
      requestAnimationFrame(() => requestAnimationFrame(() => { pd.classList.add("is-open"); panel.focus({ preventScroll: true }); }));
    };
    const close = () => {
      pd.classList.remove("is-open"); doc.classList.remove("pd-open"); tab.setAttribute("aria-expanded", "false");
      document.body.style.overflow = ""; doc.style.overflow = "";
      closeT = setTimeout(() => { pd.hidden = true; }, reduced ? 0 : 560);
      if (lastFocus && lastFocus.focus) lastFocus.focus({ preventScroll: true });
    };
    tab.addEventListener("click", open);
    // Small screens: the compact handle slides mostly out of view while the page scrolls, so it never sits on content being read
    const tuckMQ = matchMedia("(max-width: 700px)");
    let tuckT = 0;
    addEventListener("scroll", () => {
      if (!tuckMQ.matches) return;
      tab.classList.add("is-tucked"); clearTimeout(tuckT);
      tuckT = setTimeout(() => tab.classList.remove("is-tucked"), 900);
    }, { passive: true });
    $$("[data-pd-close]", pd).forEach((b) => b.addEventListener("click", close));
    $$(".pd-item", pd).forEach((a) => a.addEventListener("click", close));
    pd.addEventListener("keydown", (e) => {
      if (e.key === "Escape") { e.preventDefault(); close(); return; }
      if (e.key !== "Tab") return;
      const f = focusables(); if (!f.length) return;
      const first = f[0], last = f[f.length - 1];
      if (e.shiftKey && (document.activeElement === first || document.activeElement === panel)) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    });
  })();

  /* ---------- Floating "Back to top": hidden over the hero + section 2, visible from section 3 through the footer ---------- */
  (() => {
    const btn = $(".to-top"), after = $("#approach");
    if (!btn || !after) return;
    let shown = false;
    const sync = () => {
      const show = after.getBoundingClientRect().bottom <= 0;
      if (show === shown) return;
      shown = show; btn.classList.toggle("is-visible", show);
      btn.tabIndex = show ? 0 : -1; btn.toggleAttribute("aria-hidden", !show);
    };
    addEventListener("scroll", sync, { passive: true }); addEventListener("resize", sync, { passive: true }); sync();
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      scrollTo({ top: 0, behavior: reduced ? "auto" : "smooth" });
      const logo = $(".logo"); if (logo) setTimeout(() => logo.focus({ preventScroll: true }), reduced ? 0 : 700);
    });
  })();
})();
