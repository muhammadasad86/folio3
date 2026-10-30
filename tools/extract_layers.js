// Walks the rendered page and returns a Figma-ready layer tree (absolute page coordinates).
// Used by tools/figma_sync.py — run inside the page via Playwright: page.evaluate(EXTRACT, options)
(opts) => {
  const ROOTS = opts.roots.map((s) => document.querySelector(s)).filter(Boolean);
  const SX = opts.fixedToViewport ? 0 : scrollX, SY = opts.fixedToViewport ? 0 : scrollY;
  const px = (v) => parseFloat(v) || 0;
  const rgba = (c) => {
    const m = c && c.match(/rgba?\(([^)]+)\)/); if (!m) return null;
    const p = m[1].split(/[ ,/]+/).filter(Boolean).map(Number);
    return { r: +(p[0] / 255).toFixed(4), g: +(p[1] / 255).toFixed(4), b: +(p[2] / 255).toFixed(4), a: p.length > 3 ? p[3] : 1 };
  };
  const box = (r) => [Math.round((r.left + SX) * 10) / 10, Math.round((r.top + SY) * 10) / 10, Math.round(r.width * 10) / 10, Math.round(r.height * 10) / 10];
  const splitTop = (s) => { const out = []; let d = 0, cur = ""; for (const ch of s) { if (ch === "(") d++; if (ch === ")") d--; if (ch === "," && d === 0) { out.push(cur.trim()); cur = ""; } else cur += ch; } if (cur.trim()) out.push(cur.trim()); return out; };
  const gradient = (g) => {
    const lin = g.match(/^(repeating-)?(linear|radial)-gradient\((.*)\)$/s); if (!lin || lin[1]) return null;
    const parts = splitTop(lin[3]); let angle = 180, shape = null;
    if (lin[2] === "linear") { const a = parts[0].match(/^(-?[\d.]+)deg$/); if (a) { angle = +a[1]; parts.shift(); } else if (/^to /.test(parts[0])) { const t = parts.shift(); angle = { "to top": 0, "to right": 90, "to bottom": 180, "to left": 270 }[t] ?? 180; } }
    else { if (!/^rgba?\(/.test(parts[0])) shape = parts.shift(); }
    const stops = []; parts.forEach((p, i) => { const c = p.match(/rgba?\([^)]+\)/); if (!c) return; const pos = p.slice(c.index + c[0].length).match(/(-?[\d.]+)%/); stops.push({ c: rgba(c[0]), p: pos ? +pos[1] / 100 : null }); });
    if (stops.length < 2) return null;
    stops.forEach((s, i) => { if (s.p == null) s.p = i / (stops.length - 1); });
    return { type: lin[2], angle, shape, stops };
  };
  const shadows = (s) => s === "none" ? [] : splitTop(s).map((sh) => { const c = sh.match(/rgba?\([^)]+\)/); const nums = sh.replace(c ? c[0] : "", "").replace("inset", "").trim().split(/\s+/).map(px); return { c: rgba(c && c[0]), x: nums[0] || 0, y: nums[1] || 0, b: nums[2] || 0, s: nums[3] || 0, inset: /inset/.test(sh) }; }).filter((x) => x.c && x.c.a > 0);
  const visual = (cs, w, h) => {
    const v = {}; const bg = rgba(cs.backgroundColor); if (bg && bg.a > 0) v.bg = bg;
    if (cs.backgroundImage && cs.backgroundImage !== "none") { const gs = splitTop(cs.backgroundImage).map(gradient).filter(Boolean); const bs = cs.backgroundSize; if (gs.length && (bs === "auto" || /100%/.test(bs) || /^auto/.test(bs))) v.grads = gs; }
    const bw = [cs.borderTopWidth, cs.borderRightWidth, cs.borderBottomWidth, cs.borderLeftWidth].map(px);
    if (bw.some((x) => x > 0) && (cs.borderTopStyle !== "none" || cs.borderBottomStyle !== "none")) { const bc = rgba(cs.borderTopColor && bw[0] ? cs.borderTopColor : cs.borderBottomColor); if (bc && bc.a > 0) v.border = { w: bw, c: bc }; }
    const rad = [cs.borderTopLeftRadius, cs.borderTopRightRadius, cs.borderBottomRightRadius, cs.borderBottomLeftRadius].map((r) => /%/.test(r) ? Math.min(w, h) * px(r) / 100 : px(r));
    if (rad.some((x) => x > 0)) v.rad = rad.map((r) => Math.min(r, Math.min(w, h) / 2));
    const sh = shadows(cs.boxShadow); if (sh.length) v.shadow = sh;
    if (/blur/.test(cs.backdropFilter || "")) v.blur = px((cs.backdropFilter.match(/blur\(([\d.]+)px/) || [])[1]);
    return v;
  };
  const hasVis = (v) => v.bg || v.grads || v.border || v.shadow || v.blur;
  const hidden = (el, cs) => cs.display === "none" || cs.visibility === "hidden" || +cs.opacity < 0.02 || el.classList.contains("sr-only") || el.hasAttribute("hidden") || el.closest("[hidden]");
  const INLINE = new Set(["inline", "contents"]);
  const isInlineLike = (el) => { if (el.nodeType !== 1) return true; const cs = getComputedStyle(el); if (el.tagName === "BR") return true; if (el.classList.contains("sr-only") || el.classList.contains("type-caret")) return true; if (["SVG", "IMG", "CANVAS", "svg"].includes(el.tagName)) return false; if (INLINE.has(cs.display)) { const v = visual(cs, 1, 1); return !hasVis(v) || (!v.bg && !v.border && !v.grads); } if (cs.display === "inline-block" && !hasVis(visual(cs, 1, 1)) && [...el.childNodes].every(isInlineLike)) return true; return false; };
  const famOf = (cs) => { const f = cs.fontFamily.toLowerCase(); if (f.indexOf("plus jakarta") > -1 && (f.indexOf("dm sans") < 0 || f.indexOf("plus jakarta") < f.indexOf("dm sans"))) return "Plus Jakarta Sans"; return "DM Sans"; };
  const fontKey = (cs) => [famOf(cs), +cs.fontWeight, px(cs.fontSize), cs.fontStyle === "italic"];
  const transform = (s, cs) => cs.textTransform === "uppercase" ? s.toUpperCase() : s;
  // text: collect visible text with style runs
  const textOf = (el) => {
    let chars = ""; const runs = [];
    const walk = (n, inherited) => {
      if (n.nodeType === 3) { let t = n.textContent.replace(/\s+/g, " "); if (!t) return; const cs = getComputedStyle(n.parentElement); if (+cs.opacity < 0.02 && n.parentElement !== el) return; t = transform(t, cs); const s = chars.length; chars += t; runs.push({ s, e: chars.length, f: fontKey(cs), c: rgba(cs.color), ls: px(cs.letterSpacing) || 0 }); return; }
      if (n.nodeType !== 1) return;
      if (n.tagName === "BR") { chars += "\n"; return; }
      if (n.classList.contains("sr-only") || n.classList.contains("type-caret")) return;
      const cs = getComputedStyle(n); if (cs.display === "none" || cs.visibility === "hidden") return;
      n.childNodes.forEach((c) => walk(c));
    };
    el.childNodes.forEach((c) => walk(c));
    // trim + collapse spaces around newlines, re-index runs
    const keep = []; let out = "";
    for (let i = 0; i < chars.length; i++) { const ch = chars[i]; const prev = out[out.length - 1]; if (ch === " " && (out.length === 0 || prev === " " || prev === "\n")) continue; if (ch === "\n" && prev === " ") { out = out.slice(0, -1); keep.pop(); } out += ch; keep.push(i); }
    while (out.endsWith(" ") || out.endsWith("\n")) { out = out.slice(0, -1); keep.pop(); }
    const map = new Map(keep.map((orig, idx) => [orig, idx]));
    const R = []; runs.forEach((r) => { let s = null, e = null; for (let i = r.s; i < r.e; i++) if (map.has(i)) { if (s == null) s = map.get(i); e = map.get(i) + 1; } if (s != null) R.push({ ...r, s, e }); });
    return { chars: out, runs: R };
  };
  const svgMarkup = (svg) => {
    const clone = svg.cloneNode(true); const src = [svg, ...svg.querySelectorAll("*")], dst = [clone, ...clone.querySelectorAll("*")];
    src.forEach((n, i) => { const cs = getComputedStyle(n); const d = dst[i]; ["fill", "stroke"].forEach((p) => { const v = cs[p]; if (v && v !== "none") { const c = rgba(v); if (c) { d.setAttribute(p, `rgb(${Math.round(c.r * 255)},${Math.round(c.g * 255)},${Math.round(c.b * 255)})`); if (c.a < 1) d.setAttribute(p + "-opacity", c.a); } } else if (v === "none") d.setAttribute(p, "none"); }); if (cs.strokeWidth && n !== svg) d.setAttribute("stroke-width", px(cs.strokeWidth)); if (+cs.opacity < 1) d.setAttribute("opacity", cs.opacity); });
    const r = svg.getBoundingClientRect(); clone.setAttribute("width", r.width); clone.setAttribute("height", r.height); clone.setAttribute("xmlns", "http://www.w3.org/2000/svg"); clone.removeAttribute("class"); clone.removeAttribute("style");
    return clone.outerHTML;
  };
  const nameOf = (el) => {
    if (el.dataset.figmaName) return el.dataset.figmaName;
    if (el.tagName === "SECTION" || el.tagName === "HEADER" || el.tagName === "FOOTER" || el.tagName === "NAV") { const h = el.querySelector("h1,h2"); return (el.id ? `#${el.id}` : el.tagName.toLowerCase()) + (h ? " — " + h.textContent.replace(/\s+/g, " ").trim().slice(0, 60) : ""); }
    if (el.tagName === "MAIN") return "Main";
    const cls = (el.className && typeof el.className === "string" ? el.className.split(" ").filter((c) => c && !/^(is-|fx|js)/.test(c))[0] : "") || el.tagName.toLowerCase();
    const pretty = cls.replace(/__/g, " / ").replace(/--/g, " · ").replace(/-/g, " ").replace(/^./, (c) => c.toUpperCase());
    const CARD = /^(ind-card|sol-card|way|stack-card|story|quote|award|talk|spot|pcard|mega__rich|mega__feature|pd-item|stat|client|mm-item|stack-nav__item)$/;
    const label = CARD.test(cls) ? (el.querySelector("h3,strong,.ind-card__title,.talk__title,.stat__label,.stack-nav__label,.mm-btn__label,img[alt]") || {}) : {};
    const txt = label.alt || label.textContent;
    return pretty + (txt ? " — " + txt.replace(/\s+/g, " ").trim().slice(0, 40) : "");
  };
  const pseudo = (el, which, rect) => {
    const cs = getComputedStyle(el, which); if (!cs || cs.content === "none" || cs.content === "normal" || cs.display === "none") return null;
    let w = px(cs.width), h = px(cs.height), x, y;
    if (cs.position === "absolute" || cs.position === "fixed") {
      const L = cs.left, T = cs.top, R = cs.right, B = cs.bottom;
      if (L !== "auto" && R !== "auto" && !(w > 0 && cs.width !== "auto")) w = rect.width - px(L) - px(R);
      if (T !== "auto" && B !== "auto" && !(h > 0 && cs.height !== "auto")) h = rect.height - px(T) - px(B);
      if (/%/.test(cs.width)) w = rect.width * px(cs.width) / 100;
      x = L !== "auto" ? px(L) : rect.width - px(R) - w; y = T !== "auto" ? px(T) : rect.height - px(B) - h;
    } else { if (!(w > 0 && h > 0)) return null; x = which === "::before" ? px(getComputedStyle(el).paddingLeft) : rect.width - w; y = (rect.height - h) / 2; }
    if (!(w > 0 && h > 0) || w > 4000 || h > 4000) return null;
    const m = cs.transform.match(/matrix\(([^)]+)\)/); if (m) { const q = m[1].split(",").map(Number); if (Math.abs(q[0]) < 0.01 || Math.abs(q[3]) < 0.01) return null; }
    const v = visual(cs, w, h); if (!v.bg && !v.grads && !v.border) return null;
    return { t: "f", n: el.className.toString().split(" ")[0] + which, r: [Math.round((rect.left + SX + x) * 10) / 10, Math.round((rect.top + SY + y) * 10) / 10, Math.round(w * 10) / 10, Math.round(h * 10) / 10], v, o: +cs.opacity < 1 ? +cs.opacity : undefined, k: [] };
  };
  const COMP = opts.components || {};
  const walk = (el, out, depth) => {
    if (el.nodeType !== 1) return;
    const cs = getComputedStyle(el);
    if (hidden(el, cs)) return;
    if (["SCRIPT", "STYLE", "NOSCRIPT", "TEMPLATE"].includes(el.tagName)) return;
    const r = el.getBoundingClientRect();
    const tag = el.tagName;
    if (opts.skip && el.matches(opts.skip)) return;
    if (opts.viewportOnly && cs.position !== "fixed" && (r.bottom < -1 || r.top > innerHeight + 1) && !el.contains(document.querySelector(".pd-tab"))) return;
    // component hooks
    for (const [sel, kind] of Object.entries(COMP)) if (el.matches(sel)) {
      if (r.width < 1 || r.height < 1) return;
      const data = { t: "c", kind, r: box(r), n: nameOf(el) };
      if (kind === "btn") { data.label = (el.querySelector(".btn__label") || el).textContent.replace(/\s+/g, " ").trim(); data.cls = el.className; data.dark = !!el.closest(".section--dark, .footer, .way--dark, .mega__feature"); }
      if (kind === "pcard") { data.i = +getComputedStyle(el).getPropertyValue("--i"); data.focused = el.classList.contains("is-current"); }
      out.push(data); return;
    }
    if (tag === "IMG" && /^data:image\/svg\+xml/.test(el.src)) { if (r.width < 1 || r.height < 1) return; const raw = el.src.split(",", 2)[1]; let svg = /;base64/.test(el.src.split(",")[0]) ? atob(raw) : decodeURIComponent(raw); svg = svg.replace(/<svg\b([^>]*)>/, (m, attrs) => `<svg${attrs.replace(/\s(width|height)="[^"]*"/g, "")} width="${r.width}" height="${r.height}">`); out.push({ t: "s", r: box(r), svg, n: el.alt || "logo" }); return; }
    if (tag === "IMG") { if (r.width < 1 || r.height < 1) return; const src = el.currentSrc || el.src; out.push({ t: "i", r: box(r), src: src.slice(0, 64) + "#" + src.length, full: src, n: el.alt || el.className || "image", fit: cs.objectFit, pos: cs.objectPosition, o: +cs.opacity < 1 ? +cs.opacity : undefined, rad: visual(cs, r.width, r.height).rad }); return; }
    if (tag === "CANVAS") { if (r.width < 1) return; let url = null; try { url = el.toDataURL("image/png"); } catch (e) {} out.push({ t: "cv", r: box(r), n: el.className || "canvas", full: url }); return; }
    if (tag.toLowerCase() === "svg") { if (r.width < 1 || r.height < 1) return; out.push({ t: "s", r: box(r), svg: svgMarkup(el), n: (el.getAttribute("class") || "icon") }); return; }
    const v = visual(cs, r.width, r.height);
    if (/(hidden|clip)/.test(cs.overflowY) && r.height < 1) return;            // collapsed (e.g. hover-reveal descriptions)
    if ((tag === "INPUT" || tag === "TEXTAREA") && r.width >= 1) {
      const node = { t: "f", n: (el.name || el.type || "field") + " input", r: box(r), v, k: [] }; out.push(node);
      const ph = (el.value || el.placeholder || "").trim();
      if (ph) { const pcs = el.value ? cs : getComputedStyle(el, "::placeholder"); const pl = px(cs.paddingLeft), pt = px(cs.paddingTop);
        node.k.push({ t: "x", n: ph.slice(0, 40), r: [Math.round((r.left + SX + pl + px(cs.borderLeftWidth)) * 10) / 10, Math.round((r.top + SY + pt) * 10) / 10, r.width - pl - px(cs.paddingRight), px(cs.lineHeight) || px(cs.fontSize) * 1.3], chars: ph, runs: [], f: fontKey(cs), c: rgba(pcs.color), lh: px(cs.lineHeight) || null, ls: 0, al: "left", ws: "nowrap" }); }
      return;
    }
    const clip = /(hidden|clip|auto|scroll)/.test(cs.overflowX + cs.overflowY);
    const semantic = /^(SECTION|HEADER|FOOTER|NAV|ARTICLE|FIGURE|FORM|MAIN)$/.test(tag) || el.matches(opts.groups || "x");
    const kids = [...el.childNodes].filter((n) => n.nodeType === 1 || (n.nodeType === 3 && n.textContent.trim()));
    const textBlock = kids.length && kids.some((n) => n.nodeType === 3 || (n.nodeType === 1 && !["SVG", "svg"].includes(n.tagName))) && kids.every(isInlineLike) && el.textContent.trim().length > 0;
    const makeFrame = hasVis(v) || semantic || (clip && v.rad) || (clip && depth < 3 && (r.width < innerWidth - 2)) || (+cs.opacity < 1);
    let node = null, target = out;
    if (makeFrame && r.width >= 1 && r.height >= 1) { node = { t: "f", n: nameOf(el), r: box(r), v, clip: clip || undefined, o: +cs.opacity < 1 ? +cs.opacity : undefined, k: [] }; out.push(node); target = node.k; }
    const b = pseudo(el, "::before", r); if (b) target.push(b);
    if (textBlock) {
      const tx = textOf(el); if (tx.chars) {
        const pl = px(cs.paddingLeft), pr = px(cs.paddingRight), pt = px(cs.paddingTop), pb = px(cs.paddingBottom);
        const bl = px(cs.borderLeftWidth), bt = px(cs.borderTopWidth);
        // measure the real ink box of the text content
        const range = document.createRange(); range.selectNodeContents(el); const rr = range.getBoundingClientRect();
        const tr = rr.width ? rr : { left: r.left + pl + bl, top: r.top + pt + bt, width: r.width - pl - pr, height: r.height - pt - pb };
        const lh = cs.lineHeight === "normal" ? null : px(cs.lineHeight);
        const stw = px(cs.webkitTextStrokeWidth); const stroke = stw > 0 ? { w: stw, c: rgba(cs.webkitTextStrokeColor) } : undefined;
        target.push({ t: "x", n: tx.chars.slice(0, 40), r: box(tr), chars: tx.chars, runs: tx.runs, f: fontKey(cs), c: rgba(cs.color), lh, ls: px(cs.letterSpacing) || 0, al: cs.textAlign, ws: cs.whiteSpace, stroke });
      }
    } else el.childNodes.forEach((c) => {
      if (c.nodeType === 3 && c.textContent.trim()) {   // stray text next to block children
        const range = document.createRange(); range.selectNodeContents(c); const rr = range.getBoundingClientRect(); if (!rr.width) return;
        const t = transform(c.textContent.replace(/\s+/g, " ").trim(), cs);
        target.push({ t: "x", n: t.slice(0, 40), r: box(rr), chars: t, runs: [], f: fontKey(cs), c: rgba(cs.color), lh: cs.lineHeight === "normal" ? null : px(cs.lineHeight), ls: px(cs.letterSpacing) || 0, al: cs.textAlign, ws: cs.whiteSpace });
      } else walk(c, target, depth + (node ? 1 : 0));
    });
    const a = pseudo(el, "::after", r); if (a) target.push(a);
  };
  const out = [];
  ROOTS.forEach((r) => walk(r, out, 0));
  return out;
}
