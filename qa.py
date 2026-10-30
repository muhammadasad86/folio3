"""QA: render dist/index.html at 3 widths, report overflow, console errors, interaction checks, and screenshots.
External images/fonts are blocked in this sandbox, so a neutral placeholder image is served for them."""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).parent
URL = (ROOT / "dist/index.html").resolve().as_uri()
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "qa-shots")
OUT.mkdir(parents=True, exist_ok=True)
PNG = bytes.fromhex("89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000d4944415478da63f8cfc0f01f0005000201a3c1d6c50000000049454e44ae426082")

def run(p, w, h, name):
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=1, has_touch=w < 768, is_mobile=w < 768)
    errs = []
    pg.on("console", lambda m: m.type == "error" and "Failed to load resource" not in m.text and errs.append(m.text))
    pg.on("pageerror", lambda ex: errs.append("PAGEERROR " + str(ex)))
    pg.route("http*://**", lambda r: r.fulfill(status=200, content_type="image/png", body=PNG) if r.request.resource_type == "image" else r.abort())
    pg.goto(URL, wait_until="load")
    pg.add_style_tag(content="html{scroll-behavior:auto!important}")
    pg.wait_for_timeout(1500)
    # scroll through page to trigger reveals
    total = pg.evaluate("document.documentElement.scrollHeight")
    y = 0
    while y < total:
        pg.evaluate(f"window.scrollTo(0,{y})"); pg.wait_for_timeout(120); y += h // 2
    pg.wait_for_timeout(1200)
    res = pg.evaluate("""() => {
      const vw = document.documentElement.clientWidth, over = [];
      document.querySelectorAll('body *').forEach(el => {
        const r = el.getBoundingClientRect();
        if (r.width && (r.right > vw + 1 || r.left < -1)) {
          // ignore children of horizontal scrollers / marquee / mobile menu
          if (el.closest('.carousel__track, .marquee, .tabs, .quotes, .mobile-menu, .dropdown')) return;
          over.push(el.tagName.toLowerCase() + '.' + [...el.classList].join('.') + ' ' + Math.round(r.left) + '→' + Math.round(r.right));
        }
      });
      const hidden = [...document.querySelectorAll('[data-reveal]:not(.is-in), [data-split]:not(.is-in)')].filter(e => e.offsetParent).length;
      return { docW: document.documentElement.scrollWidth, vw, over: over.slice(0, 15), unrevealed: hidden, height: document.documentElement.scrollHeight };
    }""")
    # interactions
    checks = {}
    pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(300)
    bar = pg.locator('[data-filter-for="story-grid"] button[data-cat="NetSuite"]')
    bar.scroll_into_view_if_needed(); bar.click(); pg.wait_for_timeout(400)
    checks["stories_netsuite_visible"] = pg.evaluate("[...document.querySelectorAll('#story-grid .story')].filter(s=>!s.hidden).map(s=>s.querySelector('.story__tag').textContent)")
    qb = pg.locator('[data-filter-for="quote-grid"] button[data-cat="Ecommerce"]')
    qb.scroll_into_view_if_needed(); qb.click(); pg.wait_for_timeout(400)
    checks["quotes_ecom_visible"] = pg.evaluate("[...document.querySelectorAll('#quote-grid .quote')].filter(s=>!s.hidden).map(s=>s.querySelector('strong').textContent)")
    nxt = pg.locator('#services [data-next]')
    if nxt.is_visible():
        nxt.scroll_into_view_if_needed(); before = pg.evaluate("document.querySelector('#services .carousel__track').scrollLeft"); nxt.click(); pg.wait_for_timeout(900)
        checks["industries_next_scrolls"] = pg.evaluate("document.querySelector('#services .carousel__track').scrollLeft") > before
    if w >= 1100:
        pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(300)
        b0 = pg.locator('.nav__link').first; b0.click(); pg.wait_for_timeout(500)
        checks["mega_open"] = pg.evaluate("document.querySelector('.nav__item.is-open .mega') && getComputedStyle(document.querySelector('.nav__item.is-open .mega')).visibility")
        checks["mega_links"] = pg.evaluate("document.querySelectorAll('.nav__item.is-open .mega a').length")
        pg.screenshot(path=str(OUT / f"{name}-mega.png"))
        pg.keyboard.press("Escape"); pg.wait_for_timeout(300)
        btn = pg.locator('.hero .btn--icon').first
        before = btn.bounding_box(); btn.hover(); pg.wait_for_timeout(500); after = btn.bounding_box()
        checks["btn_hover_no_resize"] = abs(before["width"]-after["width"]) < 0.5 and abs(before["x"]-after["x"]) < 0.5
        checks["btn_hover_bg"] = pg.evaluate("getComputedStyle(document.querySelector('.hero .btn--icon')).backgroundColor")
        pg.mouse.move(5,5); pg.wait_for_timeout(400)
        pos = lambda: pg.evaluate("[...document.querySelectorAll('.nav__link')].map(a=>Math.round(a.getBoundingClientRect().left*10)/10)")
        p0 = pos(); pg.locator('.header .btn--dark').hover(); pg.wait_for_timeout(500); p1 = pos()
        checks["cta_hover_nav_stable"] = p0 == p1
        checks["logo_loaded"] = pg.evaluate("document.querySelector('.logo img').naturalWidth")
        pg.mouse.move(5,5)
    pg.locator("#contact-form button[type=submit]").scroll_into_view_if_needed()
    pg.locator("#contact-form button[type=submit]").click(); pg.wait_for_timeout(200)
    checks["form_shows_errors"] = pg.evaluate("document.querySelectorAll('#contact-form .field.is-invalid').length")
    if w < 1100:
        pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(300)
        pg.locator(".burger").click(); pg.wait_for_timeout(700)
        checks["mobile_menu_open"] = pg.evaluate("document.documentElement.classList.contains('menu-open')")
        pg.screenshot(path=str(OUT / f"{name}-menu.png"))
        pg.locator(".burger").click(); pg.wait_for_timeout(700)
    pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(800)
    pg.screenshot(path=str(OUT / f"{name}-full.png"), full_page=True)
    b.close()
    return res, errs, checks

with sync_playwright() as p:
    for w, h, n in [(1440, 900, "desktop"), (768, 1024, "tablet"), (375, 812, "mobile")]:
        res, errs, checks = run(p, w, h, n)
        print(f"== {n} {w}px: docW={res['docW']} vw={res['vw']} height={res['height']} unrevealed={res['unrevealed']}")
        print("  overflow:", res["over"] or "none")
        print("  errors:", errs or "none")
        print("  checks:", checks)
