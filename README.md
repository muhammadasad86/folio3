# folio3

Folio3 homepage — preview build

A static, dependency-free build of the redesigned Folio3 homepage.
`dist/index.html` is **one self-contained file**: all CSS, JavaScript, fonts references and Figma images are inlined,
so it can be hosted anywhere that serves static files. No build step is needed to *host* it.

```
folio3/
├── dist/index.html        ← the website (deploy this file) — Hero A (dot rain)
├── dist/index-hero-b.html ← same page, Hero B (dot-grid variation, data-hero-fx="grid") for comparison
├── src/styles.css         ← styles
├── src/main.js            ← interactions (menus, sliders, hero field, 3D globe, scroll effects)
├── build.py               ← assembles dist/index.html from src/ + assets/
├── assets/                ← Figma image exports (WebP), logo, globe/map data
├── tools/                 ← one-off asset scripts (logo trimming, globe data)
└── qa.py                  ← automated checks (Playwright)
```

---

## Live preview

https://muhammadasad86.github.io/folio3/ (Hero A) · https://muhammadasad86.github.io/folio3/index-hero-b.html (Hero B)

Every push to `main` rebuilds the site (`.github/workflows/preview.yml`) and publishes `dist/` to the `gh-pages` branch, which GitHub Pages serves.

## 0. Build it (after cloning)

`dist/` is generated and not committed. Requires Python 3.9+ and Pillow:

```bash
git clone https://github.com/muhammadasad86/folio3.git
cd folio3
pip install -r requirements.txt
python3 build.py          # writes dist/index.html and dist/index-hero-b.html
```

## 1. Run it locally

**Quickest:** double-click `dist/index.html` — it opens in your browser and works offline.

**As a local web server** (recommended for testing on your phone over Wi-Fi):

```bash
cd folio3/dist
python3 -m http.server 8080
```

* On your computer: open <http://localhost:8080>
* On your phone (same Wi-Fi): find your computer's IP (macOS: System Settings → Wi-Fi → Details → IP address,
  e.g. `192.168.1.23`) and open `http://192.168.1.23:8080`

## 2. Edit and rebuild

Edit `src/styles.css`, `src/main.js` or the content in `build.py`, then:

```bash
python3 build.py          # rewrites dist/index.html
python3 qa.py             # optional: needs `pip install playwright` + `playwright install chromium`
```

## 3. Deploy a live HTTPS preview (staging — not the production site)

Pick **one**. Each gives you a public `https://` link you can open on any phone or share.

### Option A — Netlify Drop (≈1 minute, no Git)
1. Go to <https://app.netlify.com/drop> and sign in (free account).
2. Drag the **`dist`** folder onto the page.
3. Netlify shows a URL like `https://random-name-123.netlify.app` — that's your live preview.
4. Optional: *Site configuration → Change site name* → e.g. `folio3-preview.netlify.app`.
5. Optional (keeps it private-ish): *Site configuration → Visitor access → Password protection* (paid plans), or keep the URL unshared.

**Update later:** open the site in Netlify → *Deploys* → drag the new `dist` folder onto the deploy area.

### Option B — GitHub Pages (free, versioned)
1. Create a new repository on GitHub, e.g. `folio3-preview` (Pages on a *private* repo needs a paid plan; a public repo exposes the code).
2. Upload `dist/index.html` to the repository root (*Add file → Upload files → Commit*).
3. *Settings → Pages → Build and deployment → Source: Deploy from a branch → Branch: `main` / `(root)` → Save*.
4. After ~1 minute the URL appears on the same page: `https://<your-username>.github.io/folio3-preview/`.

**Update later:** upload the new `index.html` (it replaces the old one) and commit; Pages redeploys automatically.
With Git installed:
```bash
git clone https://github.com/<you>/folio3-preview.git && cd folio3-preview
cp ../folio3-preview/dist/index.html . && git add index.html && git commit -m "Update preview" && git push
```

### Option C — Folio3's own staging server
Upload `dist/index.html` to any static path on the staging host (e.g. `https://staging.folio3.com/homepage-preview/`).
It has no server-side requirements. Do **not** place it on the production site without approval.

> CodePen / JSFiddle / StackBlitz also work (paste the file), but the file is ~4 MB because the images are inlined,
> which exceeds some of their editor limits — Netlify Drop or GitHub Pages are the better fit.

---

## 4. Testing checklist

| Where | How |
|---|---|
| **Chrome (desktop)** | Open the live URL. DevTools (⌥⌘I / F12) → device toolbar (⇧⌘M) → test iPhone SE, iPhone 14 Pro Max, Pixel 7, iPad Mini, iPad Pro. |
| **Safari (macOS)** | Open the live URL. Safari → Settings → Advanced → *Show features for web developers* → Develop → *Enter Responsive Design Mode* (⌥⌘R) → pick iPhone/iPad presets. |
| **iPhone (Safari)** | Open the live URL. Also test: landscape rotation, the menu (☰), the accordions, swiping the sliders, the contact form, and *Settings → Accessibility → Motion → Reduce Motion* (animations should calm down). |
| **Android (Chrome)** | Open the live URL. Same checks as iPhone. Optional: remote-debug from desktop Chrome via `chrome://inspect` with USB debugging on. |

What to look for on each device:
- No sideways scrolling anywhere on the page.
- Header: transparent over the hero, hides when scrolling down, returns when scrolling up.
- Menu: desktop mega menu (hover / click / keyboard); mobile full-screen menu with accordions.
- Sliders (Services, Solutions, Events) swipe smoothly; dots and arrows work.
- Hero background reacts to the mouse (desktop) or blooms gently (touch).
- Awards wall, static client grid, success-story tabs, testimonials tabs.
- Rotating 3D globe in the contact section (drag to spin).
- Contact form shows validation messages (it does **not** send — preview only).

## 5. Known limits of this preview
- The contact form validates but is not connected to a CRM.
- Practice icons in the "Folio3 Practices" menu and testimonial logos load from folio3.com servers.
- Brand fonts (Moderat / Euclid Circular A) are licensed; the build uses DM Sans / Plus Jakarta Sans stand-ins
  unless the licensed files are added.
