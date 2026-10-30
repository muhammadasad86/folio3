"""Extract editable layer trees from the built site for the Figma sync.

python3 tools/figma_extract.py  ->  build/figma/<capture>.json  +  build/figma/assets/<hash>.<ext>
Each capture is a page state (desktop full page, mobile full page, mega menus, drawers, ...).
"""
import base64, hashlib, json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "build" / "figma"; (OUT / "assets").mkdir(parents=True, exist_ok=True)
URL = (ROOT / "dist" / "index.html").as_uri()
JS = (ROOT / "tools" / "extract_layers.js").read_text()
COMPONENTS = {".btn": "btn", ".pcard": "pcard", ".pd-tab": "tab", ".to-top": "totop"}
GROUPS = ".container, .ind-card, .sol-card, .way, .stack-card, .story, .quote, .award, .talk, .client, .spot, .form-card, .field, .stat, .mega__card, .mega__feature, .mega__rich, .pd-item, .mm-item, .chip, .tab, .stack-nav__item, .hero__copy, .section-head, .process__aside, .pstack"

PREP = """() => {
  document.documentElement.classList.remove('bg-fx');                   // sections show their own backgrounds (no scroll-linked fade)
  document.querySelectorAll('.stack-card').forEach(c => c.classList.add('is-active'));   // design view: every industry card at full strength
  const st = document.createElement('style'); st.textContent = '*,*::before,*::after{transition:none!important;animation-play-state:paused!important}'; document.head.appendChild(st);
}"""

def asset_store(nodes):
    """Replace data: URLs with hashes; write unique files to disk."""
    seen = {}
    def visit(n):
        for k in n.get("k", []): visit(k)
        full = n.pop("full", None)
        if not full: return
        if full.startswith("data:"):
            head, b64 = full.split(",", 1)
            ext = head.split("/")[1].split(";")[0].replace("jpeg", "jpg")
            raw = base64.b64decode(b64)
            h = hashlib.md5(raw).hexdigest()[:16]
            p = OUT / "assets" / f"{h}.{ext}"
            if not p.exists(): p.write_bytes(raw)
            n["asset"] = p.name; n["src"] = p.name
        else:
            n["remote"] = full; n["src"] = full
        seen[n["src"]] = seen.get(n["src"], 0) + 1
    for n in nodes: visit(n)
    return seen

def stats(nodes):
    c = {}
    def v(n):
        c[n["t"]] = c.get(n["t"], 0) + 1
        for k in n.get("k", []): v(k)
    for n in nodes: v(n)
    return c

def settle(pg, w):
    H = pg.evaluate("document.documentElement.scrollHeight")
    for y in range(0, H, 400): pg.evaluate(f"window.scrollTo({{top:{y},behavior:'instant'}})"); pg.wait_for_timeout(35)
    pg.wait_for_timeout(1500)
    pg.evaluate("window.scrollTo({top:0,behavior:'instant'})"); pg.wait_for_timeout(3500)   # hero intro (typing → subline → CTAs → stats) completes

def capture(b, name, w, h, roots, prep=None, fixed=False, full=True, skip=None, viewport_only=False):
    m = w <= 1024
    pg = b.new_context(viewport={"width": w, "height": h}, is_mobile=m, has_touch=m, device_scale_factor=1).new_page()
    pg.goto(URL); pg.wait_for_timeout(800)
    settle(pg, w)
    if prep: prep(pg)
    pg.evaluate(PREP); pg.wait_for_timeout(300)
    nodes = pg.evaluate(JS, {"roots": roots, "components": COMPONENTS, "groups": GROUPS, "fixedToViewport": fixed, "skip": skip, "viewportOnly": viewport_only})
    seen = asset_store(nodes)
    page_h = pg.evaluate("document.documentElement.scrollHeight") if full else h
    data = {"name": name, "w": w, "h": page_h, "nodes": nodes}
    (OUT / f"{name}.json").write_text(json.dumps(data, separators=(",", ":")))
    print(f"{name}: {w}x{page_h}  {stats(nodes)}  images:{len(seen)}  json:{len(json.dumps(data))//1024}KB")
    pg.close()

def open_menu(i):
    def f(pg):
        pg.locator(".nav__item[data-dropdown] > button").nth(i).click(); pg.wait_for_timeout(1200)
    return f

def mobile_menu(pg):
    pg.click(".burger"); pg.wait_for_timeout(900)
    pg.locator(".mm-btn").nth(1).click(); pg.wait_for_timeout(900)

def open_drawer(pg):
    pg.click(".pd-tab"); pg.wait_for_timeout(1300)

def scroll_to(sel):
    def f(pg):
        pg.evaluate(f"window.scrollTo({{top: document.querySelector('{sel}').offsetTop + 300, behavior: 'instant'}})"); pg.wait_for_timeout(1500)
        pg.evaluate("window.scrollBy(0,-1)"); pg.wait_for_timeout(900)   # header returns (scroll-up), chip visible
    return f

if __name__ == "__main__":
    which = sys.argv[1:] or ["desktop", "mobile", "states"]
    with sync_playwright() as p:
        b = p.chromium.launch()
        HIDE_FIXED_PAGE = ".mega, .mega-plate, .mega-scrim, .mobile-menu, .pd, .to-top"
        if "desktop" in which:
            capture(b, "desktop-1440", 1440, 900, ["main", "footer", "header.header", ".pd-tab"], skip=HIDE_FIXED_PAGE)
        if "mobile" in which:
            capture(b, "mobile-375", 375, 812, ["main", "footer", "header.header", ".pd-tab"], skip=HIDE_FIXED_PAGE)
        if "states" in which:
            for i, label in enumerate(["ai-solutions", "ai-services", "industries", "resources", "company"]):
                capture(b, f"state-mega-{label}", 1440, 900, ["header.header"], prep=open_menu(i), fixed=True, full=False)
            capture(b, "state-mobile-menu", 375, 812, ["header.header", ".mobile-menu"], prep=mobile_menu, fixed=True, full=False)
            for (w, h, nm) in [(1440, 900, "desktop"), (375, 812, "mobile")]:
                capture(b, f"state-drawer-{nm}", w, h, [".pd"], prep=open_drawer, fixed=True, full=False)
    print("done")
