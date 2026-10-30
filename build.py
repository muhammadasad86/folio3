"""Builds the Folio3 homepage preview into dist/index.html (inline CSS + JS, single file).

Content: www.folio3.com (captured 21 Oct 2026). Design/assets: Figma "Folio3-Website.v1" (node 12077:53354).
All imagery is exported from Figma (OFFbaLDr6mDzb2PhvqwAzm / IkJTEESOTOpXNOHibv1MIa) into assets/figma and inlined.
"""
import json
from html import escape as e
from pathlib import Path

ROOT = Path(__file__).parent
FIG = "https://www.figma.com/api/mcp/asset/"
CDN = "https://cdn-aiml.folio3.site/media/"

import base64 as _b64
def LA(name):
    """Local asset exported from Figma (OFFbaLDr6mDzb2PhvqwAzm, page 'Homepage — Coded Build'), stored in assets/figma/."""
    f = ROOT / "assets/figma" / f"{name}.webp"
    return "data:image/webp;base64," + _b64.b64encode(f.read_bytes()).decode()

A = {
    "logo": "data:image/svg+xml;base64," + __import__("base64").b64encode((ROOT / "assets/folio3-logo.svg").read_bytes()).decode(),
    "ind_app": LA("svc-app"),
    "ind_netsuite": LA("svc-netsuite"),
    "ind_dynamics": LA("svc-dynamics"),
    "ind_ecom": LA("svc-ecommerce"),
    "ind_ai": LA("svc-ai"),
    "ind_health": LA("svc-health"),
    "ind_agtech": LA("svc-agtech"),
    "ind_cloud": LA("svc-cloud"),
    "spot1": LA("spot-potato-expo"),
    "spot2": LA("spot-propertese"),
    "spot3": LA("spot-aws-lambda"),
}
BADGES = [(LA(f"badge-{i:02d}"), alt) for i, alt in enumerate([
    "AWS Partner — Advanced Tier Services", "Microsoft Silver Partner", "Oracle NetSuite Commerce Partner", "AWS Partner Network",
    "Microsoft Gold Partner", "Oracle NetSuite Partner of the Year 2018 — SuiteCloud International", "Oracle NetSuite Alliance Partner",
    "Oracle NetSuite Alliance Partner Spotlight Winner 2023", "AWS Partner — Advanced Tier Services", "Oracle NetSuite Alliance Partner Spotlight Winner 2022 — Automotive",
    "Oracle NetSuite Alliance Partner Spotlight Winner 2023 — Hospitality", "Oracle NetSuite Partner of the Year 2021 — EMEA", "Oracle NetSuite Alliance Partner Spotlight Winner 2023 — Financial Services"], 1)]

ICON = {
    "chev": '<svg class="chev" viewBox="0 0 7 12" aria-hidden="true"><path d="M1 1l5 5-5 5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "down": '<svg viewBox="0 0 12 12" aria-hidden="true"><path d="M2 4l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "left": '<svg viewBox="0 0 13 22" aria-hidden="true"><path d="M11 2L2 11l9 9" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "right": '<svg viewBox="0 0 13 22" aria-hidden="true"><path d="M2 2l9 9-9 9" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "arrow": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12h15M13 5l7 7-7 7" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "diag": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 17L17 7M8 7h9v9" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "check": '<svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="10"/><path d="M6 10.5l2.6 2.5L14 7.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "quote": '<svg class="quote__mark" viewBox="0 0 40 32" aria-hidden="true"><path fill="currentColor" d="M0 32V19.2C0 8.5 5.6 2.1 16.8 0l1.6 4.4C12.3 6 9.4 9.5 9.2 14.8H17V32H0zm23 0V19.2C23 8.5 28.6 2.1 39.8 0l1.6 4.4c-6.1 1.6-9 5.1-9.2 10.4H40V32H23z"/></svg>',
}

# Shared card interaction (reference: "Two Ways to Build With Us"): pointer-follow glow + top accent line
FX = '<span class="fx-glow" aria-hidden="true"></span><span class="fx-line" aria-hidden="true"></span>'
FX_GLOW = '<span class="fx-glow" aria-hidden="true"></span>'
PROJECT_FORM = "#project-form"   # every "Begin Your Project" CTA lands on the inquiry form itself (not the #contact section/globe)

def btn(label, href, cls="", icon=True, attrs=""):
    """Figma 'Frame 37447' / 'Frame 2050': on hover the chevron travels from the right of the label to the left
    (two chevrons trade width so the button never changes size)."""
    if not icon:
        return f'<a class="btn {cls}" href="{e(href)}" {attrs}><span class="btn__label">{e(label)}</span></a>'
    return (f'<a class="btn btn--icon {cls}" href="{e(href)}" {attrs}><span class="btn__chev btn__chev--l" aria-hidden="true">{ICON["chev"]}</span>'
            f'<span class="btn__label">{e(label)}</span><span class="btn__chev btn__chev--r" aria-hidden="true">{ICON["chev"]}</span></a>')

def btn_submit(label, cls=""):
    return (f'<button class="btn btn--icon {cls}" type="submit"><span class="btn__chev btn__chev--l" aria-hidden="true">{ICON["chev"]}</span>'
            f'<span class="btn__label">{e(label)}</span><span class="btn__chev btn__chev--r" aria-hidden="true">{ICON["chev"]}</span></button>')

# ---------------------------------------------------------------- Navigation (mirrors www.folio3.com header, captured 21 Oct 2026)
F = "https://www.folio3.com"
NAV = [
    ("AI Solutions", "mega", [
        ("", [("AI Guardian", "/ai/solutions/ai-guardian"), ("Talk to Your Data", "/ai/solutions/talk-to-your-data")]),
        ("Sports AI", [("Sports Video Analysis", "/ai/solutions/sports/ai-video-analysis"), ("Football Video Analysis", "/ai/solutions/sports/ai-video-analysis/football"),
                       ("Basketball Video Analysis", "/ai/solutions/sports/ai-video-analysis/basketball"), ("Cricket Video Analysis", "/ai/solutions/sports/ai-video-analysis/cricket"),
                       ("Swimming Video Analysis", "/ai/solutions/sports/ai-video-analysis/swimming"), ("Tennis Video Analysis", "/ai/solutions/sports/ai-video-analysis/tennis"),
                       ("Baseball Video Analysis", "/ai/solutions/sports/ai-video-analysis/baseball"), ("Golf Swing Analysis", "/ai/solutions/sports/ai-video-analysis/golf-swing"),
                       ("Horse Racing Video Analysis", "/ai/solutions/sports/ai-video-analysis/horse-racing"), ("Ice Hockey Video Analysis", "/ai/solutions/sports/ai-video-analysis/ice-hockey"),
                       ("Motorsports Video Analysis", "/ai/solutions/sports/ai-video-analysis/motorsports"), ("Sports Sponsorship Intelligence", "/ai/solutions/sports/sponsorship-intelligence"),
                       ("Gait Analysis", "/ai/solutions/sports/ai-gait-analysis")]),
        ("Agentic AI Solutions", [("Custom AI Agent Development", "/ai/services/ai-agent-development"), ("AI Agent Marketplace", "/ai/ai-agent-marketplace"),
                                  ("Healthcare AI Agents", "/ai/solutions/healthcare-ai-agents"), ("Banking AI Agents", "/ai/solutions/banking-ai-agents"),
                                  ("Insurance AI Agents", "/ai/solutions/insurance-ai-agents"), ("Sports AI Agents", "/ai/solutions/sports-ai-agents"),
                                  ("Education AI Agents", "/ai/solutions/education-ai-agents"), ("Legal AI Agents", "/ai/solutions/legal-ai-agents"),
                                  ("Real Estate AI Agents", "/ai/solutions/real-estate-ai-agents")]),
        ("Data Solutions", [("AI Enterprise Search", "/ai/solutions/data/ai-enterprise-search"), ("AI Data Extraction", "/ai/solutions/data/ai-data-extraction")]),
        ("Vehicle Intelligence Solutions", [("ALPR Software", "/ai/solutions/automatic-license-plate-recognition"), ("LPR Parking System", "/ai/solutions/lpr-parking"),
                                            ("AI Vehicle Counting", "/ai/solutions/ai-vehicle-counting-software"), ("AI Road Traffic Management", "/ai/solutions/traffic-management-software")]),
        ("Livestock & Cattle AI", [("Cattle Counting", "/ai/solutions/ai-cattle-counting"), ("Cattle Breed Identification", "/ai/solutions/cattle-breed-app"),
                                   ("AI Animal Detection", "/ai/solutions/ai-animal-detection"), ("AI Livestock Management", "/ai/solutions/ai-livestock-management")]),
        ("AI Detection", [("AI Object Recognition", "/ai/solutions/object-recognition-software"), ("AI Object Tracking", "/ai/solutions/object-tracking-software"),
                          ("AI Visual Search", "/ai/solutions/ai-visual-search"), ("Food Recognition", "/ai/solutions/food-recognition-api")]),
        ("Biometric & People Detection", [("Person Detection AI", "/ai/solutions/person-detection"), ("Face Recognition AI", "/ai/solutions/face-recognition-software"),
                                          ("Ethnicity Detection AI", "/ai/solutions/ethnicity-detection-ai"), ("AI Image Analysis", "/ai/solutions/ai-image-analysis-software")]),
        ("Aerial Intelligence", [("AI Drone Inspection", "/ai/solutions/drone/ai-drone-inspection-software"), ("Drone Solar Panel Inspection", "/ai/solutions/drone/solar-panel-inspection"),
                                 ("Drone Wildlife Detection", "/ai/solutions/drone/wildlife-monitoring"), ("Drone Wind Turbine Inspection", "/ai/solutions/drone/wind-turbine-inspection")]),
    ], ("Get Started with Folio3 AI", "/ai/contact-us")),
    ("AI Services", "mega", [
        ("AI Enablement", [("AI Enablement Program", "/ai/services/ai-enablement"), ("AI Readiness Assessment", "/ai/services/ai-enablement/ai-readiness-assessment"),
                           ("Enterprise AI Strategy", "/ai/services/ai-enablement/ai-strategy"), ("AI Transformation Services", "/ai/services/ai-enablement/ai-transformation"),
                           ("AI Workforce Training", "/ai/services/ai-enablement/ai-workforce-training"), ("AI Change Management", "/ai/services/ai-enablement/ai-change-management")]),
        ("Generative AI", [("Generative AI Services", "/ai/services/generative-ai-development"), ("Gen AI Integration", "/ai/services/generative-ai-integration"),
                           ("NLP Development", "/ai/services/generative-ai-development/nlp-development"), ("RAG Development", "/ai/services/generative-ai-development/rag-development"),
                           ("LLM Development", "/ai/services/generative-ai-development/llm-development"), ("LLM Fine-tuning", "/ai/services/generative-ai-development/llm-fine-tuning"),
                           ("ChatGPT Integration", "/ai/services/generative-ai-integration/chatgpt-integration"), ("Gemini Integration", "/ai/services/generative-ai-integration/gemini-integration"),
                           ("Prompt Engineering Services", "/ai/services/prompt-engineering")]),
        ("AI Development Services", [("AI Consulting Services", "/ai/services/ai-consulting"), ("AI Automation Services", "/ai/services/ai-consulting/ai-automation"),
                                     ("AI Implementation Services", "/ai/services/ai-consulting/ai-implementation"), ("Computer Vision Development", "/ai/services/computer-vision-development"),
                                     ("Machine Learning Development", "/ai/services/machine-learning-development"), ("Machine Learning Ops", "/ai/services/mlops-consulting")]),
        ("PoC & Prototyping", [("Rapid Prototyping", "/ai/services/prototyping"), ("Vibe Coding Services", "/ai/vibe-coding-agency-partner"),
                               ("Sports Software Development", "/ai/services/sports-software-development"), ("Cricket Software Development Services", "/ai/services/sports-software-development/cricket"),
                               ("Sports App Development Services", "/ai/services/sports-software-development/mobile-app"), ("Soccer Software Development Services", "/ai/services/sports-software-development/soccer")]),
        ("Data Services", [("AI Data Integration", "/ai/services/ai-data-integration"), ("Data Security & Protection", "/ai/services/data-security"),
                           ("Big Data Consulting", "/ai/services/big-data-consulting"), ("Predictive Analytics", "/ai/services/predictive-analytics-consulting")]),
        ("Specialised AI Services", [("Business Intelligence Services", "/ai/services/business-intelligence"), ("AWS AI & ML Services", "/ai/services/aws-ai-consulting")]),
        ("Hire AI Team", [("Hire Dedicated AI Teams", "/ai/folio3-teams"), ("Hire AI Engineers", "/ai/services/hire-ai-developers")]),
    ], None),
    ("Industries", "mega", [
        ("Transportation & Logistics", [("AI In Transportation", "/ai/industries/transportation"), ("AI Fleet Management", "/ai/industries/transportation/fleet-management"),
                                        ("AI in Logistics", "/ai/industries/transportation/logistics"), ("Aircraft Turnaround Control", "/ai/industries/transportation/aircraft-turnaround-control")]),
        ("AgTech", [("AI Agriculture Solutions", "/ai/industries/agriculture"), ("AI Smart Farming Intelligence", "/ai/industries/agriculture/smart-farming")]),
        ("Commerce & Hospitality", [("AI in eCommerce", "/ai/industries/ecommerce")]),
        ("Healthcare & Specialised", [("AI In Healthcare", "/ai/industries/healthcare"), ("AI in Aviation", "/ai/industries/aviation")]),
    ], None),
    ("Case Studies", "link", "/case-studies", None),
    ("Resources", "list", [("", [("Blogs", "/ai/blog"), ("Whitepapers", "/ai/resources#white-papers"), ("Guides and Brochures", "/ai/resources#brochures"), ("Webinars", "https://webinars.folio3.ai/")])], None),
    ("Company", "list", [("", [("About Us", "/about-us"), ("Leadership", "/leadership"), ("Partners", "/ai/partnerships"), ("Our Experts", "/ai/our-experts")])], None),
    ("Folio3 Practices", "practices", [
        ("AI & Data", "/ai", "main/AI-data-icon-40bfb8bb-3abe-487e-9490-d48b2e8f4732.webp"),
        ("App Development", "/app-development", "main/app-development-icon-092589b4-0ba9-4e78-9a3e-b06662a97ec7.webp"),
        ("Security", "https://manageditservices.folio3.com/", "main/security-icon-ed2eb336-b075-436b-9f71-1d49f745c102.webp"),
        ("AgTech", "https://agtech.folio3.com/", "main/agtech-icon-a5c216fc-df84-4a83-942d-7ac86f7565c9.webp"),
        ("FoodTech", "https://foodtech.folio3.com/", "main/foodtech-icon-f499b8f7-56e1-40a4-b9a3-d44b90f505fc.webp"),
        ("Digital Health", "https://digitalhealth.folio3.com/", "main/digital-health-icon-2158ccab-6a5e-4f43-a994-99972d9352b9.webp"),
        ("NetSuite", "https://netsuite.folio3.com/", "main/NetSuite-icon-2fa26af5-4db9-4b70-baaa-751749bab6ff.webp"),
        ("Microsoft Dynamics", "https://dynamics.folio3.com/", "main/Dynamics-icon-383bd74e-3981-4fa7-a00d-49f717d6be51.webp"),
        ("Salesforce CRM", "https://crm.folio3.com/", "main/Salesforce-icon-774209db-b9e7-4665-9847-c646fa453478.webp"),
        ("Ecommerce", "https://ecommerce.folio3.com/", "main/Ecommerce-icon-ce344633-d3c3-4e78-a8c3-342ad66d8695.webp"),
    ], None),
]

def roll(label):
    """Figma nav item: two stacked labels; on hover the first rolls up and the copy rolls in (300ms smart-animate)."""
    return f'<span class="roll" data-text="{e(label)}"><span>{e(label)}</span></span>'

# Mega menu presentation (Redstone-inspired: intro column · link columns · featured card). Every link is a real folio3.com
# destination from NAV above or an on-page section; featured images are Figma exports already used on this page.
MENU_META = {
    "AI Solutions": dict(desc="Ready-to-deploy AI products for sports, vehicles, livestock, drones and the enterprise.",
                         link=("Get started with Folio3 AI", "/ai/contact-us"),
                         feat=("menu-ai-guardian", "Featured product", "AI Guardian", "One place to control, track, and audit every AI request.", "/ai/solutions/ai-guardian")),
    "AI Services": dict(desc="From AI strategy and enablement to generative AI, ML engineering and dedicated AI teams.",
                        link=("Talk to an AI expert", "/ai/contact-us"),
                        feat=("menu-phase-zero", "Start here", "Phase Zero", "AI Process Discovery: find the use cases worth your budget first.", "/ai/solutions/phase-zero")),
    "Industries": dict(desc="AI built for transportation, agriculture, commerce and healthcare.",
                       link=("Talk to an AI expert", "/ai/contact-us"),
                       feat=("menu-agtech", "Industry focus", "AI Agriculture Solutions", "Smart farming and livestock intelligence.", "/ai/industries/agriculture")),
    "Resources": dict(desc="Insights, guides and sessions from the Folio3 AI team.",
                      link=("Read the blog", "/ai/blog"),
                      feat=("menu-stories", "Case studies", "Success stories", "How companies partner with Folio3 to grow.", "/case-studies"),
                      sub={"Blogs": "Latest thinking on AI and data", "Whitepapers": "In-depth research and reports",
                           "Guides and Brochures": "Practical guides and product brochures", "Webinars": "Live and on-demand sessions"}),
    "Company": dict(desc="The people, partners and experts behind Folio3.",
                    link=("About Folio3", "/about-us"),
                    feat=("menu-leap", "Event", "Folio3 at LEAP 2026", "Our team connected with tech leaders in Riyadh.", "#events"),
                    sub={"About Us": "Our story, mission and values", "Leadership": "The team leading Folio3",
                         "Partners": "Our technology partnerships", "Our Experts": "Meet Folio3's AI experts"}),
    "Folio3 Practices": dict(desc="Specialist Folio3 practices across AI, ERP, commerce, health and more.",
                             link=("Explore Folio3 AI & Data", "/ai"),
                             feat=("menu-ai", "Practice", "AI & Data", "Folio3's AI and data practice.", "/ai")),
}
ARROW = '<svg class="arr" viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'

def practice_icon(img):
    """Practice glyphs from folio3.com's CDN, bundled locally (assets/figma/practice-*.webp) so they never depend on the CDN."""
    return LA("practice-" + img.split("/")[-1].split("-icon")[0].lower())

def url(h):
    return h if h.startswith(("http", "#")) else F + h

def _svg(paths, cls="ico"):
    """Unified icon language — 48-grid geometric line glyphs, 1.6px stroke at every size (matches the Step-card icons)."""
    return f'<svg class="{cls} ic" viewBox="0 0 48 48" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{paths}</svg>'

MENU_ICON = {   # one glyph per top-level menu (intro badge + mobile accordion) — 48 grid
    "AI Solutions": '<path d="M21 7c1.3 8 4.7 11.4 12.7 12.7-8 1.3-11.4 4.7-12.7 12.7-1.3-8-4.7-11.4-12.7-12.7C16.3 18.4 19.7 15 21 7z"/><path d="M36 29c.7 4 2.3 5.6 6 6.3-3.7.7-5.3 2.3-6 6.3-.7-4-2.3-5.6-6-6.3 3.7-.7 5.3-2.3 6-6.3z"/>',
    "AI Services": '<path d="M7 14h21M36 14h5M7 24h7M22 24h19M7 34h17M32 34h9"/><circle cx="32" cy="14" r="4"/><circle cx="18" cy="24" r="4"/><circle cx="28" cy="34" r="4"/>',
    "Industries": '<path d="M6 41V24l10 6v-6l10 6v-6l10 6V9h6v32z"/><path d="M6 41h36M13 35h3M21 35h3M29 35h3"/>',
    "Resources": '<path d="M12 6h17l9 9v27H12z"/><path d="M29 6v9h9M18 24h14M18 30h14M18 36h8"/>',
    "Company": '<circle cx="19" cy="17" r="5.5"/><path d="M8.5 39c0-6.2 4.7-10.5 10.5-10.5S29.5 32.8 29.5 39"/><circle cx="33.5" cy="19.5" r="4.5"/><path d="M31 29.4c5.5-.9 9.5 3 9.5 8.6"/>',
    "Folio3 Practices": '<rect x="8" y="8" width="13" height="13" rx="3"/><rect x="27" y="8" width="13" height="13" rx="3"/><rect x="8" y="27" width="13" height="13" rx="3"/><rect x="27" y="27" width="13" height="13" rx="3"/>',
}
RICH_ICON = {   # Resources / Company link tiles — 48 grid
    "Blogs": '<path d="M9 39l2.2-8.6L31.5 10l6.5 6.5-20.4 20.3z"/><path d="M27.2 14.3l6.5 6.5M9 39h30"/>',
    "Whitepapers": '<path d="M12 6h17l9 9v27H12z"/><path d="M29 6v9h9M18 36v-6M24 36V24M30 36v-9"/>',
    "Guides and Brochures": '<path d="M7 11c6-3 12-3 17 1 5-4 11-4 17-1v27c-6-3-12-3-17 1-5-4-11-4-17-1z"/><path d="M24 12v27"/>',
    "Webinars": '<rect x="6" y="9" width="36" height="24" rx="4"/><path d="M21 16.5l8.5 4.5-8.5 4.5zM17 41h14M24 33v8"/>',
    "About Us": '<path d="M8 41V19L24 7l16 12v22"/><path d="M19 41V30h10v11M5 41h38"/>',
    "Leadership": '<path d="M24 7l5 10.4 11.4 1.6-8.2 8 2 11.3L24 33l-10.2 5.3 2-11.3-8.2-8 11.4-1.6z"/>',
    "Partners": '<circle cx="18" cy="24" r="10"/><circle cx="30" cy="24" r="10"/>',
    "Our Experts": '<circle cx="24" cy="16" r="7"/><path d="M10 41c0-8 6.3-13 14-13s14 5 14 13"/><path d="M19 35.5l3.5 3.2 6-6"/>',
}
PRACTICE_ICON = {   # Folio3 Practices drawer — line glyphs replace the CDN raster icons
    "AI & Data": '<rect x="13" y="13" width="22" height="22" rx="3"/><rect x="19" y="19" width="10" height="10" rx="1.5"/><path d="M19 6v7M29 6v7M19 35v7M29 35v7M6 19h7M6 29h7M35 19h7M35 29h7"/>',
    "App Development": '<rect x="14" y="5" width="20" height="38" rx="4"/><path d="M21 37h6M21 16l-3.5 4.5L21 25M27 16l3.5 4.5L27 25"/>',
    "Security": '<rect x="10" y="21" width="28" height="20" rx="4"/><path d="M16 21v-5a8 8 0 0 1 16 0v5M24 29v5"/>',
    "AgTech": '<path d="M24 41V24"/><path d="M24 24c0-8 6-13 14-13 0 8-6 13-14 13zM24 30c0-6-5-10-12-10 0 7 5 10 12 10z"/><path d="M14 41h20"/>',
    "FoodTech": '<path d="M7 25h34a17 17 0 0 1-34 0z"/><path d="M17 8c-2 3 2 5 0 8M24 6c-2 3 2 5 0 8M31 8c-2 3 2 5 0 8"/>',
    "Digital Health": '<rect x="6" y="9" width="36" height="25" rx="4"/><path d="M12 22h6l3-6 5 12 3-6h7M18 41h12M24 34v7"/>',
    "NetSuite": '<ellipse cx="24" cy="12" rx="14" ry="5"/><path d="M10 12v24c0 2.8 6.3 5 14 5s14-2.2 14-5V12M10 24c0 2.8 6.3 5 14 5s14-2.2 14-5"/>',
    "Microsoft Dynamics": '<path d="M7 41h34"/><path d="M10 33l9.5-9.5 7 6L39 17"/><path d="M31 17h8v8"/>',
    "Salesforce CRM": '<path d="M14 36a8 8 0 0 1-1.2-15.9A11 11 0 0 1 34 17.2 9.5 9.5 0 0 1 35 36z"/><path d="M24 31v-9M20 26l4-4 4 4"/>',
    "Ecommerce": '<path d="M5 9h6l4.5 21h21L41 15H13"/><circle cx="19" cy="38" r="2.6"/><circle cx="34" cy="38" r="2.6"/>',
}
COMPACT_MENUS = {"Industries", "Resources", "Company"}   # shorter content → shared compact panel height
MENU_COUNT_NOUN = {"AI Solutions": "solutions", "AI Services": "services", "Industries": "industry solutions", "Folio3 Practices": "practices"}

def header():
    items, mobile = [], []
    for i, (label, kind, data, cta) in enumerate(NAV):
        if kind == "practices":   # lives in the floating right-edge drawer only (practices_drawer)
            continue
        if kind == "link":
            items.append(f'<li class="nav__item"><a class="nav__link" href="{url(data)}">{roll(label)}</a></li>')
            mobile.append(f'<a class="mm-link" href="{url(data)}">{e(label)}{ARROW}</a>')
            continue
        meta = MENU_META[label]
        n_links = len(data) if kind == "practices" else sum(len(links) for _, links in data)
        if kind == "practices":
            body = '<div class="mega__practices">' + "".join(
                f'<a class="practice" href="{url(h)}" style="--i:{k}"><span class="practice__icon"><img src="{practice_icon(img)}" alt="" width="36" height="36" loading="lazy"></span><span>{e(t)}</span>{ARROW}</a>'
                for k, (t, h, img) in enumerate(data)) + '</div>'
            m_body = '<div class="mm-lead mm-lead--list">' + "".join(f'<a class="mm-sub" href="{url(h)}" style="--i:{k}">{e(t)}</a>' for k, (t, h, _) in enumerate(data)) + '</div>'
        else:
            groups, m_groups, k, lead = [], [], 0, ""
            for head, links in data:
                if kind == "list":
                    lis = "".join(f'<li><a class="mega__rich" href="{url(h)}"><span class="mega__rich-icon">{_svg(RICH_ICON[t])}</span>'
                                  f'<span class="mega__rich-text"><strong>{e(t)}</strong><span>{e(meta["sub"][t])}</span></span>{ARROW}</a></li>' for t, h in links)
                    groups.append(f'<div class="mega__group mega__group--rich" style="--i:{k}"><ul>{lis}</ul></div>')
                else:
                    if head:
                        lis = "".join(f'<li><a href="{url(h)}">{e(t)}</a></li>' for t, h in links)
                        groups.append(f'<div class="mega__group" style="--i:{k}"><h4>{e(head)}<span class="mega__count">{len(links)}</span></h4><ul>{lis}</ul></div>')
                    else:
                        lis = "".join(f'<li><a href="{url(h)}"><i aria-hidden="true"></i><span>{e(t)}</span>{ARROW}</a></li>' for t, h in links)
                        lead = f'<div class="mega__lead"><ul>{lis}</ul></div>'   # featured products sit with their heading (intro column)
                k += 1
                sub = "".join(f'<a class="mm-sub" href="{url(h)}" style="--i:{j}">{e(t)}</a>' for j, (t, h) in enumerate(links))
                if head:
                    gid = f"mm-{i}-{k}"
                    m_groups.append(f'<div class="mm-group"><button class="mm-group__btn" type="button" aria-expanded="false" aria-controls="{gid}">'
                                    f'<span>{e(head)}<small>{len(links)}</small></span><i aria-hidden="true"></i></button>'
                                    f'<div class="mm-collapse" id="{gid}" inert><div><div>{sub}</div></div></div></div>')
                else:
                    m_groups.append(f'<div class="mm-lead">{sub}</div>')
            body = f'<div class="mega__cols mega__cols--{kind}">{"".join(groups)}</div>'
            m_body = "".join(m_groups)
        lead = lead if kind != "practices" else ""
        img, kick, ftitle, fdesc, fhref = meta["feat"]
        lt, lh = meta["link"]
        noun = MENU_COUNT_NOUN.get(label)
        count = f'<span class="mega__stat"><b>{n_links}</b>{e(noun)}</span>' if noun else ""
        panel = (f'<div class="mega__card">'
                 f'<div class="mega__intro"><span class="mega__badge">{_svg(MENU_ICON[label])}</span><h3 class="mega__title">{e(label)}</h3>{lead}'
                 f'<p class="mega__desc">{e(meta["desc"])}</p>{count}'
                 f'<a class="mega__all" href="{url(lh)}">{e(lt)}{ARROW}</a></div>'
                 f'<div class="mega__body">{body}</div>'
                 f'<a class="mega__feature" href="{url(fhref)}"><span class="mega__feature-media"><img src="{LA(img)}" alt="" loading="lazy"></span>'
                 f'<span class="mega__feature-kicker"><i></i>{e(kick)}</span><strong>{e(ftitle)}</strong><span class="mega__feature-desc">{e(fdesc)}</span>'
                 f'<span class="mega__feature-go">Learn more{ARROW}</span></a>'
                 f'</div>')
        items.append(f'<li class="nav__item" data-dropdown><button class="nav__link" type="button" aria-expanded="false" aria-controls="mega-{i}">{roll(label)}{ICON["down"]}</button>'
                     f'<div class="mega" id="mega-{i}" role="region" aria-label="{e(label)}" data-size="{"compact" if label in COMPACT_MENUS else "tall"}"><div class="container">{panel}</div></div></li>')
        m_feat = (f'<a class="mm-feature" href="{url(fhref)}"><img src="{LA(img + "-sm")}" alt="" width="76" height="56" loading="lazy">'
                  f'<span><small>{e(kick)}</small><strong>{e(ftitle)}</strong></span>{ARROW}</a>')
        mobile.append(f'<div class="mm-item"><button class="mm-btn" type="button" aria-expanded="false" aria-controls="mm-{i}">'
                      f'<span class="mm-btn__label"><span class="mm-btn__icon">{_svg(MENU_ICON[label])}</span>{e(label)}</span><i aria-hidden="true"></i></button>'
                      f'<div class="mm-collapse" id="mm-{i}" inert><div><div class="mm-panel">{m_body}{m_feat}<a class="mm-all" href="{url(lh)}">{e(lt)}{ARROW}</a></div></div></div></div>')
    return f'''
<header class="header">
  <div class="container header__inner">
    <a class="logo" href="#top" aria-label="Folio3 home"><img src="{A["logo"]}" alt="Folio3" width="108" height="52"></a>
    <nav class="nav" aria-label="Primary">
      <ul class="nav__list">{"".join(items)}<li class="nav__indicator" aria-hidden="true"></li></ul>
      {btn("Begin Your Project", PROJECT_FORM, "btn--dark")}
      <button class="burger" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="mobile-menu"><span></span><span></span><span></span></button>
    </nav>
  </div>
  <div class="mega-plate" aria-hidden="true"><div class="container"><div class="mega-plate__card"></div></div></div>
</header>
<div class="mega-scrim" aria-hidden="true"></div>
<nav class="mobile-menu" id="mobile-menu" aria-label="Mobile" inert>
  <div class="mobile-menu__list">{"".join(mobile)}</div>
  {btn("Begin Your Project", PROJECT_FORM, "btn--dark")}
</nav>'''

# ---------------------------------------------------------------- Hero
STATS = [("20+", "Global Awards Won"), ("700+", "Global Employees"), ("20+", "Global Awards won"), ("5,000+", "Projects Delivered"), ("1000+", "Companies Served")]

def hero():
    stats = "".join(f'<div class="stat"><div class="stat__num" data-count="{n}">{n}</div><div class="stat__label">{e(l)}</div></div>' for n, l in STATS)
    return f'''
<section class="hero" id="top" aria-labelledby="hero-title">
  <div class="hero__fx" aria-hidden="true"><canvas class="hero__field"></canvas></div>
  <div class="container hero__inner">
    <div class="hero__copy">
      <h1 class="hero__title" id="hero-title" data-type>Lead the AI Shift<br>with Folio3</h1>
      <p class="hero__sub" data-type-sub>Your guide to secure, enterprise-ready AI.</p>
      <div class="hero__cta" data-type-cta>
        {btn("Start Your AI Journey", PROJECT_FORM)}
        {btn("Explore Case Studies", "#stories", "btn--ghost", False)}
      </div>
    </div>
    <div class="stats hero__stats" data-stagger>{stats}</div>
  </div>
</section>'''

# ---------------------------------------------------------------- Process
STEPS = [
    ("Prove and Build", "Connect and Listen", "We start with your problem or idea, your goals and what success looks like for your team.", []),
    ("", "Evaluate Your Systems", "We map how work actually flows across your tools, data and teams.", ["ERP", "CRM", "Email", "Docs", "Processes"]),
    ("", "Find the Highest-ROI Workflows", "We rank opportunities by business value and effort, so you invest where AI pays off first.", []),
    ("", "Validate", "We test the use case against your real data and constraints before any major spend.", []),
    ("", "Launch an MVP", "A working version in your users' hands, so results are measured, not assumed.", []),
    ("", "Build and Scale", "We harden it for production with security, governance and integrations, then scale it across teams.", []),
]

# Line glyphs for the six steps — thin 1.6 stroke, geometric, after the user's reference tiles (grey idle / black on focus)
STEP_ICONS = [
    '<path d="M10 11h28a4 4 0 0 1 4 4v15a4 4 0 0 1-4 4H22l-9 7v-7h-3a4 4 0 0 1-4-4V15a4 4 0 0 1 4-4z"/><path d="M16 20.5v4M20.5 18v9M25 16v13M29.5 18v9M34 20.5v4"/>',
    '<path d="M6 15V6h9M33 6h9v9M42 33v9h-9M15 42H6v-9"/><rect x="14" y="14" width="8.5" height="8.5" rx="2"/><rect x="25.5" y="14" width="8.5" height="8.5" rx="2"/><rect x="14" y="25.5" width="8.5" height="8.5" rx="2"/><circle cx="29.75" cy="29.75" r="4.25"/>',
    '<circle cx="24" cy="24" r="13.5"/><circle cx="24" cy="24" r="7"/><circle cx="24" cy="24" r="2.6" fill="currentColor" stroke="none"/><path d="M24 4.5v6M24 37.5v6M4.5 24h6M37.5 24h6"/>',
    '<path d="M24 5.5l14.5 5.2v11.1c0 9.3-6.2 16.6-14.5 20.7-8.3-4.1-14.5-11.4-14.5-20.7V10.7z"/><path d="M17 24.2l5 5 9.5-10.4"/>',
    '<path d="M9 39L39 9"/><path d="M24 12.5v23M12.5 24h23M16 16l16 16M30.5 15.5l-13 17"/>',
    '<path d="M24 7l17 8.5L24 24 7 15.5z"/><path d="M7 24l17 8.5L41 24"/><path d="M7 32.5L24 41l17-8.5"/>',
]

def process():
    n = len(STEPS)
    cards = []
    for i, (_phase, t, d, chips) in enumerate(STEPS):
        ch = f'<div class="chip-row">{"".join(f"<span class=chip>{e(c)}</span>" for c in chips)}</div>' if chips else ""
        cards.append(f'<li class="pcard{" is-current" if i == 0 else ""}" data-pcard style="--i:{i}"><div class="pcard__inner fx">{FX_GLOW}'
                     f'<div class="pcard__top"><span class="pcard__step">Step {i + 1:02d}<span> / {n:02d}</span></span>'
                     f'<svg class="pcard__icon" viewBox="0 0 48 48" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{STEP_ICONS[i]}</svg></div>'
                     f'<div class="pcard__body"><h3>{e(t)}</h3><p>{e(d)}</p>{ch}</div>'
                     f'<span class="pcard__num" aria-hidden="true">{i + 1:02d}</span></div></li>')
    return f'''
<section class="section process" id="approach" aria-labelledby="process-title">
  <div class="container process__grid">
    <div class="process__aside">
      <span class="eyebrow" data-reveal>Secure, enterprise-ready AI</span>
      <h2 class="h2" id="process-title" data-split>From First Conversation<br>to AI in Production</h2>
      <p class="lede" data-reveal>We don't start with a model. We start with your business, find where AI pays off, prove it works, and then build it to run at scale.</p>
      <div data-reveal>{btn("Book a Discovery Call", PROJECT_FORM)}</div>
    </div>
    <ol class="pstack" data-pstack>{"".join(cards)}</ol>
  </div>
</section>'''

# ---------------------------------------------------------------- Industries (dark)
INDUSTRIES = [
    ("Artificial Intelligence", "ind_ai", "Embrace boundless possibilities with Folio3's cutting-edge AI solutions.", "https://www.folio3.com/ai"),
    ("App Development", "ind_app", "Bring your ideas to life with Folio3's App Development.", "https://www.folio3.com/app-development"),
    ("NetSuite", "ind_netsuite", "Maximize your NetSuite potential with Folio3's expert implementation.", "https://netsuite.folio3.com/"),
    ("Microsoft Dynamics", "ind_dynamics", "Boost your business efficiency through Folio3's Microsoft Dynamics solutions.", "https://dynamics.folio3.com/"),
    ("Ecommerce", "ind_ecom", "Commerce builds, migrations and ERP integrations that scale with demand.", "https://ecommerce.folio3.com/"),
    ("AgTech", "ind_agtech", "Revolutionize agriculture with Folio3's smart AgTech services.", "https://agtech.folio3.com/"),
    ("Digital Health", "ind_health", "Excel in the new era of healthcare innovation with Folio3's Digital Health services.", "https://digitalhealth.folio3.com/"),
    ("Cloud Services", "ind_cloud", "Fuel your business growth with Folio3's state-of-the-art Cloud services.", "https://cloud.folio3.com/"),
]

def nav_btns(label):
    return f'<div class="carousel-nav"><button class="icon-btn" data-prev aria-label="Previous {label}">{ICON["left"]}</button><button class="icon-btn" data-next aria-label="Next {label}">{ICON["right"]}</button></div>'

def industries():
    cards = "".join(
        f'<a class="ind-card fx fx--dark" href="{e(h)}" data-reveal style="--i:{min(i,3)}"><img src="{A[k]}" alt="" width="560" height="365" loading="lazy">{FX}'
        f'<div class="ind-card__body"><div class="ind-card__title">{e(t)}<span class="ind-card__arrow">{ICON["diag"]}</span></div>'
        f'<div class="ind-card__desc"><span>{e(d)}</span></div></div></a>'
        for i, (t, k, d, h) in enumerate(INDUSTRIES))
    return f'''
<section class="section section--dark" id="services" aria-labelledby="ind-title" data-bg="dark">
  <div class="container section-head">
    <div class="section-head__text">
      <span class="eyebrow" data-reveal>Services</span>
      <h2 class="h2" id="ind-title" data-split>What Folio3 Can<br>Help You With</h2>
    </div>
    {nav_btns("service")}
  </div>
  <div class="carousel">
    <div class="carousel__track" tabindex="0" aria-label="Services">{cards}</div>
  </div>
  <div class="container"><div class="dots"></div></div>
</section>'''

# ---------------------------------------------------------------- Two ways
def ways():
    def card(num, tag, title, desc, points, best, cta, dark=False):
        lis = "".join(f'<li style="--i:{i}">{ICON["check"]}<span>{e(p)}</span></li>' for i, p in enumerate(points))
        return (f'<article class="way fx{" way--dark fx--dark" if dark else ""}" data-reveal>{FX}'
                f'<div class="way__top"><span class="way__tag">{e(tag)}</span><span class="way__num" aria-hidden="true">{num}</span></div>'
                f'<div class="way__head"><h3>{e(title)}</h3><p>{e(desc)}</p></div>'
                f'<ul class="way__list">{lis}</ul>'
                f'<div class="way__foot"><p class="way__best"><span>Best for</span>{e(best)}</p>{btn(cta, PROJECT_FORM, "btn--dark" if not dark else "")}</div></article>')
    return f'''
<section class="section ways-sec" id="engagement" aria-labelledby="ways-title">
  <div class="container">
    <div class="section-head">
      <div class="section-head__text">
        <span class="eyebrow" data-reveal>Engagement models</span>
        <h2 class="h2" id="ways-title" data-split>Two Ways to Build With Us</h2>
        <p class="lede" data-reveal>Pick the model that fits your team. Both follow the same process.</p>
      </div>
    </div>
    <div class="ways" data-stagger>
      {card("01", "Build Method", "We Build It for You", "Our team designs, develops and delivers the full solution, then hands it over ready to run.",
            ["A dedicated Folio3 team owns delivery end to end", "Clear scope, milestones and a single point of contact", "Delivered with documentation, testing and handover", "Ongoing support and improvements after launch"],
            "Teams that want an outcome delivered without adding internal headcount.", "Begin Your Project")}
      <div class="ways__or" aria-hidden="true"><span>or</span></div>
      {card("02", "Forward Deployed Engineers", "Our Engineers Inside Your Team", "Folio3 AI engineers embed with your people, work inside your systems and ship alongside you.",
            ["Engineers who work in your stack, tools and workflows", "Faster iteration with direct access to your business users", "Your team learns by building, not just receiving", "Knowledge stays in-house when the engagement ends"],
            "Companies building AI capability in-house who need experts on the ground.", "Talk to a Folio3 Guide", True)}
    </div>
  </div>
</section>'''

# ---------------------------------------------------------------- Solutions
SOLUTIONS = [
    ("AI Guardian", LA("sol-ai-guardian"), "One place to control, track, and audit every AI request. Available on Microsoft Marketplace.", "https://www.folio3.com/ai/solutions/ai-guardian", "AI"),
    ("Talk to Your Data", LA("sol-talk-to-your-data"), "Ask your business data questions in plain language and get answers from live data.", "https://www.folio3.com/ai/solutions/talk-to-your-data", "AI"),
    ("Phase Zero", LA("sol-phase-zero"), "AI Process Discovery.", "https://www.folio3.com/ai/solutions/phase-zero", "AI"),
    ("AgriERP", LA("sol-agrierp"), "An agriculture ERP built on Microsoft Dynamics 365 and NetSuite for farm finance, crop and livestock operations.", "https://www.agrierp.com/", "ERP"),
    ("Burq", LA("sol-burq"), "Delivery orchestration that decides how each order is fulfilled across stores, warehouses and delivery providers.", "https://burq.ai/", "Logistics"),
    ("Propertese", LA("sol-propertese"), "Manage properties, units, and tenants with ease using the power of NetSuite.", "https://www.propertese.com/", "NetSuite"),
    ("PACScribe", LA("sol-pacscribe"), "An AI-powered PACS medical imaging software for radiology groups that automates manual steps across imaging, reporting, and data flow.", "https://pacscribe.com/", "Healthcare"),
    ("Cattlytics", LA("sol-cattlytics"), "A cattle management app that organizes and tracks your cattle records.", "https://www.cattlytics.com/", "AgTech"),
]

def solutions():
    cards = "".join(
        f'<a class="sol-card fx" href="{e(h)}" data-reveal style="--i:{min(i,3)}"><div class="sol-card__media"><img src="{e(img)}" alt="{e(t)}" width="477" height="365" loading="lazy">{FX}<span class="tag">{e(tag)}</span></div>'
        f'<h3>{e(t)}{ICON["diag"]}</h3><p>{e(d)}</p></a>' for i, (t, img, d, h, tag) in enumerate(SOLUTIONS))
    return f'''
<section class="section section--surface" id="solutions" data-bg="gray" aria-labelledby="sol-title">
  <div class="container section-head">
    <div class="section-head__text">
      <span class="eyebrow" data-reveal>Our Solutions</span>
      <h2 class="h2" id="sol-title" data-split>We Innovate, Scale, and Save:<br>Cost-Efficient Scalable Products</h2>
    </div>
    {nav_btns("solution")}
  </div>
  <div class="carousel"><div class="carousel__track" tabindex="0" aria-label="Solutions" style="gap:24px">{cards}</div></div>
  <div class="container">
    <div class="dots"></div>
    <div class="cta-strip" data-reveal><div><strong>Not sure where AI fits?</strong><span>Start with AI Discovery and find the use cases worth your budget first.</span></div>{btn("Talk to a Folio3 Guide", PROJECT_FORM, "btn--dark")}</div>
  </div>
</section>'''

# ---------------------------------------------------------------- Technology
# Content: www.folio3.com — "AI That Already Speaks With Your Business" (cards, capabilities, links) and the
# "What Folio3 can help you with" section (practice tags). Interaction inspired by cosmoq.framer.website "Features".
STACK_ICONS = {   # 48 grid — same line language as the Step-card icons
    "erp": '<rect x="6" y="8" width="36" height="32" rx="4"/><path d="M6 17h36M17 17v23M23 26h13M23 32h9"/>',
    "agri": '<path d="M24 41V23"/><path d="M24 23c0-7.5 5.5-12.5 13.5-12.5 0 8-5.5 12.5-13.5 12.5zM24 29c0-6-4.6-10-11.5-10 0 7 4.6 10 11.5 10z"/><path d="M8 41h32"/>',
    "health": '<path d="M24 40S8 31 8 19.5a8 8 0 0 1 16-3 8 8 0 0 1 16 3C40 31 24 40 24 40z"/><path d="M13.5 23.5h5.5l2.5-5 4 9 2.5-4h6.5"/>',
    "retail": '<path d="M10 16h28l-2 25H12z"/><path d="M18 16v-3a6 6 0 0 1 12 0v3M18 23.5v.5M30 23.5v.5"/>',
    "sports": '<circle cx="24" cy="24" r="16"/><path d="M24 17l6.5 4.7-2.5 7.6h-8l-2.5-7.6zM24 8v9M39.2 19l-8.7 2.7M33.4 37l-5.4-7.7M14.6 37l5.4-7.7M8.8 19l8.7 2.7"/>',
    "security": '<path d="M24 5.5l14.5 5.2v11.1c0 9.3-6.2 16.6-14.5 20.7-8.3-4.1-14.5-11.4-14.5-20.7V10.7z"/><circle cx="24" cy="20.5" r="3.6"/><path d="M24 24.1v7"/>',
}
STACK = [
    ("erp", "ERP", "Put AI Agents to Work Inside Your ERP",
     "Finance and operations teams lose hours to manual entries, reconciliations and reports that are outdated by the time they are read.",
     "NetSuite AI Assistant", [("Invoices auto-matched", "Today"), ("Open exceptions", "Flagged for review"), ("Q4 demand forecast", "Updated")],
     "Vendor spend in Logistics is trending above budget. Want a breakdown by supplier?",
     [("Explore NetSuite Services", "https://netsuite.folio3.com/"), ("Explore Dynamics 365 Services", "https://dynamics.folio3.com/")], "NetSuite · Microsoft Dynamics"),
    ("agri", "Agriculture & Livestock", "See Every Animal and Acre, Every Day",
     "Herd health issues and crop risks are often spotted too late, after productivity has already dropped.",
     "Herd Monitoring", [("Animals tracked", "Live camera feed"), ("Behavior alerts", "3 to review"), ("Feeding pattern", "Normal")],
     "Pen 4 shows reduced movement since yesterday. Recommend a vet check.",
     [("Explore Folio3 AgTech", "https://agtech.folio3.com/")], "AgTech"),
    ("health", "Healthcare", "Less Paperwork, More Time With Patients",
     "Clinicians spend a large share of their day on documentation, intake and data lookups instead of care.",
     "Clinical Notes Copilot", [("Visit summary", "Drafted"), ("Intake forms", "Pre-filled"), ("PHI access", "Governed")],
     "Summary ready for review. 2 follow-up items detected from the visit transcript.",
     [("Explore Folio3 Digital Health", "https://digitalhealth.folio3.com/")], "Digital Health"),
    ("retail", "Retail & eCommerce", "Sell Smarter With AI Across the Funnel",
     "Generic storefronts, manual product content and guesswork inventory leave revenue on the table.",
     "Store Intelligence", [("Product descriptions", "Generated"), ("Low-stock risk", "5 SKUs"), ("Assistant chats", "Resolved by AI")],
     "Winter jackets are selling faster than forecast. Reorder suggested for 3 sizes.",
     [("Explore Folio3 eCommerce", "https://ecommerce.folio3.com/")], "Ecommerce"),
    ("sports", "Sports", "Turn Every Match Into Usable Data",
     "Coaches and analysts spend hours tagging footage by hand before any insight reaches the team.",
     "Match Analysis", [("Events tagged", "Automatically"), ("Highlights reel", "Ready"), ("Player heatmaps", "Generated")],
     "Most attacks came down the left flank in the second half.",
     [("Explore Sports Video Analysis", "https://www.folio3.com/ai/solutions/sports/ai-video-analysis")], "Artificial Intelligence"),
    ("security", "Security & Mobility", "Recognize, Track and Act in Real Time",
     "Gates, parking and roads still rely on manual checks that are slow and error-prone.",
     "Gate Recognition", [("Plates read", "Live"), ("Access granted", "Auto-verified"), ("Watchlist hits", "1 alert")],
     "Unregistered vehicle detected at Gate 2. Security notified.",
     [("Explore ALPR Solutions", "https://www.folio3.com/ai/solutions/automatic-license-plate-recognition")], "Artificial Intelligence"),
]

def stack_icon(k):
    return _svg(STACK_ICONS[k], "stack-ico")

def tech_img(k):
    """Technology card visuals — the images placed in Figma (Desktop 1440 · #technology), exported at the Figma crop.
    Desktop (two-column card, portrait visual) uses the exact Figma crop at 2x; stacked layouts (≤1240px, landscape
    visual) use a landscape cut centred on the same focal area, so nothing important is lost to object-fit."""
    d = ROOT / "assets/figma-tech"
    uri = lambda f: "data:image/jpeg;base64," + _b64.b64encode((d / f).read_bytes()).decode()
    dw, dh = (840, 1048) if k == "erp" else (840, 952)
    return (f'<picture><source media="(max-width: 1240px)" srcset="{uri(f"tech-{k}-m.jpg")}" width="1400" height="1000">'
            f'<img src="{uri(f"tech-{k}-d.jpg")}" alt="" width="{dw}" height="{dh}" loading="lazy" decoding="async"></picture>')

def stack_card(i, k, label, title, desc, widget, caps, insight, links, practice):
    caps_html = "".join(f'<li><span class="stack-card__tick" aria-hidden="true">{ICON["check"]}</span><span><strong>{e(c)}</strong><small>{e(v)}</small></span></li>' for c, v in caps)
    btns = "".join(btn(t, h, "btn--dark btn--sm" if j == 0 else "btn--ghost btn--sm", j == 0) for j, (t, h) in enumerate(links))
    return (f'<article class="stack-card fx{" is-active" if i == 0 else ""}" id="stack-{k}" data-stack-card="{i}" aria-labelledby="stack-{k}-title">{FX}'
            f'<div class="stack-card__copy">'
            f'<span class="stack-card__kicker"><span class="stack-card__icon">{stack_icon(k)}</span>{e(label)}</span>'
            f'<h3 class="stack-card__title" id="stack-{k}-title">{e(title)}</h3>'
            f'<p class="stack-card__desc">{e(desc)}</p>'
            f'<ul class="stack-card__caps">{caps_html}</ul>'
            f'<div class="stack-card__cta">{btns}</div></div>'
            f'<div class="stack-card__visual">{tech_img(k)}'
            f'<span class="stack-card__practice">Folio3 practice · {e(practice)}</span>'
            f'<div class="stack-card__widget" aria-hidden="true"><div class="stack-card__widget-head"><strong>{e(widget)}</strong><span><i></i>AI Active</span></div>'
            f'<p class="stack-card__insight"><b>AI</b>{e(insight)}</p></div></div></article>')

def tech():
    nav = "".join(f'<li><a class="stack-nav__item" href="#stack-{k}" data-stack-link="{i}"{" aria-current=" + chr(34) + "true" + chr(34) if i == 0 else ""}>'
                  f'<span class="stack-nav__num">0{i + 1}</span><span class="stack-nav__icon">{stack_icon(k)}</span><span class="stack-nav__label">{e(label)}</span>'
                  f'<span class="stack-nav__bar" aria-hidden="true"><i></i></span></a></li>' for i, (k, label, *_r) in enumerate(STACK))
    cards = "".join(stack_card(i, *row) for i, row in enumerate(STACK))
    return f'''
<section class="section" id="technology" aria-labelledby="tech-title">
  <div class="container">
    <div class="section-head stack-head">
      <div class="section-head__text">
        <span class="eyebrow" data-reveal>Technology</span>
        <h2 class="h2" id="tech-title" data-split>The Platforms and Stacks<br>We Build On</h2>
        <p class="lede" data-reveal>20+ years of building software inside these industries, now applied to AI. We bring it into the workflows you already run, so it fits how your business works.</p>
      </div>
    </div>
    <div class="stack" data-stack>
      <nav class="stack-nav" aria-label="Industries"><ol>{nav}</ol></nav>
      <div class="stack-cards">{cards}</div>
    </div>
    <div class="stack-cta" data-reveal>{btn("Start Your AI Journey", PROJECT_FORM)}</div>
  </div>
</section>'''

# ---------------------------------------------------------------- Spotlight
SPOTS = [
    (LA("event-leap-2026"), "LEAP 2026, RIYADH", "The Folio3 Team Was at LEAP 2026", "Our team connected with tech leaders on AI opportunities and showcased our products.", True),
    (A["spot1"], "", "Potato Expo 2024 — Step into the Future of Potato Farming", "", False),
    (A["spot3"], "", "Folio3 Achieves AWS Lambda Service Delivery Designation", "", False),
    (A["spot2"], "", "Propertese — a platform for every aspect of real estate operations", "", False),
]

def spotlight():
    slides = []
    for img, kicker, title, desc, cap in SPOTS:
        c = f'<div class="spot__caption"><small>{e(kicker)}</small><strong>{e(title)}</strong><span>{e(desc)}</span></div>' if cap else ""
        slides.append(f'<figure class="spot"><img src="{e(img)}" alt="{e(title)}" width="1196" height="562" loading="lazy">{c}</figure>')
    return f'''
<section class="section spotlight" id="events" aria-labelledby="spot-title">
  <div class="container section-head"><div class="section-head__text">
    <span class="eyebrow" data-reveal>Events</span>
    <h2 class="h2" id="spot-title" data-split>Spotlight Events at Folio3</h2>
  </div></div>
  <div class="carousel" data-center data-loop data-autoplay>
    <div class="carousel__track" tabindex="0" aria-label="Spotlight events">{"".join(slides)}</div>
    <div class="spotlight__nav"><button class="icon-btn" data-prev aria-label="Previous event">{ICON["left"]}</button><button class="icon-btn" data-next aria-label="Next event">{ICON["right"]}</button></div>
  </div>
  <div class="container"><div class="dots"></div></div>
</section>'''

# ---------------------------------------------------------------- About + recognitions
# Award badges + order exactly as shown on www.folio3.com ("Awards and Recognition"), captured 21 Oct 2026
NS = "https://netsuite.folio3.com/wp-content/uploads/"
AWARD_BADGES = [
    "Oracle NetSuite Industry Spotlight Winner 2026 — Electronics", "Oracle NetSuite Industry Spotlight Winner 2026 — Apparel, Footwear & Accessories",
    "Oracle NetSuite Industry Spotlight Winner 2025 — Sporting Goods", "Oracle NetSuite Partner of the Year 2025 — Middle East",
    "Oracle NetSuite Alliance Partner Spotlight Winner 2025 — Education", "Oracle NetSuite Alliance Partner Spotlight Winner 2024 — Building Materials",
    "Oracle NetSuite Alliance Partner Spotlight Winner 2024 — Apparel, Footwear & Accessories", "Oracle NetSuite Alliance Partner Spotlight Winner 2024 — Software & IT Services",
    "Oracle NetSuite Alliance Partner Spotlight Winner 2024 — Education", "Oracle NetSuite Alliance Partner Spotlight Winner 2022 — SuiteCommerce",
    "Oracle NetSuite Alliance Partner Spotlight Winner 2025 — Education", "Oracle NetSuite Alliance Partner Spotlight Winner 2022 — SuiteCommerce",
    "Oracle NetSuite Industry Spotlight Winner 2026 — Hospitality", "Oracle NetSuite Alliance Partner Spotlight Winner 2022 — Automotive",
    "Oracle NetSuite Partner of the Year 2021 — Most New Logos, EMEA", "Oracle NetSuite SuiteCommerce Partner of the Year 2017",
    "Clutch Top NetSuite Company 2024", "Clutch Top ERP Consulting Company 2024 — United Kingdom",
    "Clutch Top ERP Consulting Company 2024 — San Francisco", "Clutch Top IT Services Company 2024 — Automotive, San Francisco",
]

AWARD_TRIM = json.loads((ROOT / "assets/figma/award-trim.json").read_text())
FEATURED_AWARD = 4  # "Oracle NetSuite Partner of the Year 2025 — Middle East"

def award_tiles():
    tiles, k = [], 0
    for i, alt in enumerate(AWARD_BADGES, 1):
        ar = AWARD_TRIM[f"{i:02d}"]
        w = min((0.36 * 0.75 * ar) ** .5, 0.80, 0.72 * ar * 0.75)   # optical area on a 4:3 tile, height ≤ 72%
        img = f'<img src="{LA(f"award-{i:02d}-t")}" alt="{e(alt)}" style="--w:{w * 100:.1f}%" loading="lazy">'
        if i == FEATURED_AWARD:
            tiles.insert(0, f'<li class="award award--feature fx fx--dark" style="--i:0">{FX}<span class="award__kicker">Latest highlight</span>{img}<span class="award__name">{e(alt)}</span></li>')
        else:
            k += 1; tiles.append(f'<li class="award fx fx--dark" style="--i:{k}">{FX}{img}</li>')
    tiles.append(f'<li class="award award--stat" style="--i:{k + 1}"><strong data-count="20+">20+</strong><span>Global awards won</span></li>')
    return "".join(tiles)

def about():
    badges = "".join(f'<div class="badge" data-parallax="{0.04 + (i % 3) * 0.03:.2f}"><img src="{b}" alt="{e(alt)}" loading="lazy"></div>' for i, (b, alt) in enumerate(BADGES))
    return f'''
<section class="section" id="about" aria-labelledby="about-title">
  <div class="container about">
    <div class="about__copy">
      <h2 class="h2" id="about-title" data-split>Folio3 Where Tech Meets<br>Business Brilliance</h2>
      <p class="about__tagline" data-reveal>Creativity is our belief.<br>Brand growth is our motto.</p>
      <p class="about__body" data-reveal>Techies from Intel, Silicon Graphics, Qualcomm, MIT, and Caltech propel business growth with people-centric technology. We love all things digital and truly believe in what technology and people can achieve together.</p>
      <div data-reveal>{btn("Discover More", "https://www.folio3.com/about-us")}</div>
      <h3 class="h3 awards-title" data-reveal>Our Esteemed Partners<br>and Global Recognitions</h3>
    </div>
    <div class="badges">{badges}</div>
  </div>
  <div class="container awards-wrap">
    <div class="awards-wall" role="region" aria-labelledby="awards-title" data-reveal>
      <div class="awards-wall__head">
        <div class="awards-wall__heading">
          <span class="eyebrow">Recognition</span>
          <h3 class="awards-wall__title" id="awards-title">Awards and Recognition</h3>
        </div>
        <p class="awards-wall__note">Recognized by Oracle NetSuite and Clutch year after year. Also an Inc. 5000 Honoree (2021 and 2022) and on the AllWorld Arabia 500 (2012).</p>
      </div>
      <ul class="awards-grid" role="list">{award_tiles()}</ul>
    </div>
  </div>
</section>'''

# ---------------------------------------------------------------- Success stories — Figma "Component 13" (page 12077:35152), one variant per tab
M = CDN + "main/"
CS = "https://www.folio3.com/case-studies"
# (title, image, description, extra image style)
STORIES = {
    "App Dev": [("Aiden", [(LA("story-aiden"), "")],
                 "A serverless multi-cloud solution that ingests data from Aiden's car sensors."),
                ("AnyRoad", [(LA("story-anyroad"), "")], "How Folio3 simplified AnyRoad's operations and helped the platform scale."),
                ("Barnes and Nobles", [(LA("story-barnes-and-nobles"), "")], "How Folio3 helped Barnes & Noble accelerate growth and improve marketing efficiency."),
                ("Brighton Park", [(LA("story-brighton-park"), "")], "")],
    "AI": [("AiGenics", [(LA("story-aigenics"), "")], "AiGenics wanted to build a platform solution addressing mental health issues and provide an outlet for digital cognitivist behavioral therapies and self-meditation through different proven methods."),
           ("Logo Detection Solution", [(LA("story-logo-detection-solution"), "")], "Folio3 AI developed a state-of-the-art computer vision-based AI solution for a top manufacturer of wireless portable digital magnifier cameras with offices in North America, Europe, and Asia."),
           ("Object Detection Tennis", [(LA("story-object-detection-tennis"), "")], ""),
           ("Aiden", [(LA("story-aiden-ai"), "")], "Being the first and only software company that collects vehicle data through sensors and facilitates its use for consumers, Aiden had to face challenges while managing the machine learning workloads of the software projects.")],
    "NetSuite": [("Biomason", [(LA("story-biomason"), "")], "Folio3 successfully implemented the NetSuite SuiteSuccess Services Standard edition for Biomason, streamlining their financials, procurement, sales, and CRM operations."),
                 ("HSK Group", [(LA("story-hsk-group"), "")], "HSK Group was seeking to implement Oracle NetSuite ERP to streamline financials, property management, facility management, and CRM functionalities while ensuring real-time reporting."),
                 ("Naked Wardrobe", [(LA("story-naked-wardrobe"), "")], "Naked Wardrobe has built an impressive brand and is experiencing significant growth. To sustain it, they needed an ERP system to streamline operations and provide decision support data."),
                 ("4D Motion Inc", [(LA("story-4d-motion-inc"), "")], "4D Motion is a healthcare and fitness business that needed ERP integration with NetSuite. Folio3 provided the integration along with custom functionality to cater to their needs.")],
    "Microsoft Dynamics": [("Growers Express", [(LA("story-growers-express"), "")], "Growers Express grows and markets produce under well-known brands like Green Giant Fresh. Folio3 built an award-winning suite of mobile solutions later productized as TrueTrac — now acquired by FoodLink."),
                           ("Honda R&D Europe (UK) Ltd", [(LA("story-honda-rd-europe"), "")], "Honda focuses on creating safer and smarter mobility options for its worldwide customer base. Folio3 developed an AX Workflow Approval app designed to enhance the client's business operations."),
                           ("Savills", [(LA("story-savills"), "")], "Savills Timesheet App upgrade and improvements by Folio3 give app users a more streamlined and enjoyable experience."),
                           ("Daraz", [(LA("story-daraz"), "")], "Folio3 ComAX Connector provides fully automated data synchronization between leading ecommerce systems and Dynamics AX, keeping AX and ecommerce systems in sync.")],
    "Ecommerce": [("Greenlane", [(LA("story-greenlane"), "")], "Greenlane needed real-time business support for their Shopify stores. Folio3 delivered web store customizations — custom bundles, BOGO, announcement bar — and optimized store performance."),
                  ("Vector Laboratories", [(LA("story-vector-laboratories"), "")], "Vector Labs needed a native PHP to Magento 2 migration. Folio3 delivered one-page checkout, a customized JS tool, group-based pricing and more."),
                  ("Face Reality", [(LA("story-face-reality"), "")], "Face Reality wanted a better website experience. Folio3 built a credit app, custom credit and commission module, a referral management system and multiple integrations."),
                  ("Purelife Dental", [(LA("story-purelife-dental"), "")], "Purelife Dental wanted to improve customer retention. Folio3 delivered history-based promos and discounts, buy-now-pay-later and an algorithm to identify inactive customers.")],
    "AgTech": [("Hanor Farms", [(LA("story-hanor-farms"), "")], "Hanor Farms relied on paper processes and spreadsheets. Folio3's AgTech solution digitized workflows and automated task management and scheduling."),
               ("Gro Alliance", [(LA("story-gro-alliance"), "")], "Gro Alliance's application suffered runtime bugs, glitches and limited customizability, hurting productivity and data accuracy."),
               ("Elanco", [(LA("story-elanco"), "")], "Elanco needed a digital way for farmers to learn about ticks in cattle. Folio3 AgTech built a multilingual app connecting farmers, vets and investors."),
               ("Cactus Feeders", [(LA("story-cactus-feeders"), "")], "Helped manage animals coming in and out of the farm — feeding, weights, owners and movements — through to packing and shipping.")],
    "Digital Health": [("Speclipse", [(LA("story-speclipse"), "")], "Speclipse, a medical device company founded by Stanford graduates and a dermatologist, offers a cancer diagnostic solution based on Laser-Induced Plasma Spectroscopy and AI."),
                       ("Hamzavi Dermatology", [(LA("story-hamzavi-dermatology"), "")], "Leading dermatology specialists in skin cancer, surgical procedures, and pediatric and ethnic dermatology."),
                       ("HealthQuest", [(LA("story-healthquest"), "")], "HealthQuest Capital is a private asset firm improving patient outcomes by providing growth capital to healthcare companies, mainly in the US."),
                       ("Ivision", [(LA("story-ivision"), "")], "Ivision is a healthcare startup building telehealth and remote patient monitoring solutions.")],
    "Cloud Services": [("AzamPay", [(LA("story-azampay"), "")], "AzamPay, a Tanzanian digital commerce company, deployed a microservices-based delivery pipeline automation and monitoring solution."),
                       ("Tree3", [(LA("story-tree3"), "")], "A multi-tenant eCommerce platform cut AWS costs by 50% with a tailored Kubernetes, Terraform and kOps solution."),
                       ("Nutrition Detection App", [(LA("story-nutrition-detection-app"), "")], "Lets users detect the nutritional value of everyday food from their devices, built on cost-effective, scalable serverless components."),
                       ("Achelois Pharma", [(LA("story-achelois-pharma"), "")], "Achelois Pharma operates in the pharmaceutical and medicine manufacturing industry.")],
}

def filter_bar(target, cats, label):
    bs = "".join(f'<button type="button" class="tab" data-cat="{e(c)}" aria-pressed="{"true" if i == 0 else "false"}">{e(c)}{ICON["chev"]}</button>' for i, c in enumerate(cats))
    return f'<div class="tabs" data-filter-for="{target}" role="group" aria-label="{e(label)}" data-reveal>{bs}</div><p class="sr-only" aria-live="polite"></p>'

def inset_to_box(style):
    """Figma crop 'inset:T R B L' (percent) -> explicit top/left/width/height, which <img> honours."""
    if not style.startswith("inset:"):
        return style
    v = [float(x.rstrip("%")) for x in style[6:].split()]
    if len(v) == 3: v = [v[0], v[1], v[2], v[1]]
    if len(v) == 1: v = v * 4
    t, r, b, l = v
    return f"top:{t}%;left:{l}%;width:{100 - l - r:.2f}%;height:{100 - t - b:.2f}%"

def stories():
    cards = []
    for cat, items in STORIES.items():
        for t, imgs, d in items:
            layers = "".join(f'<img src="{e(src)}" alt="" loading="lazy" style="{inset_to_box(style)}"{" class=story__img--abs" if style.startswith("inset") else ""}>' for src, style in imgs)
            desc = f"<p>{e(d)}</p>" if d else ""
            aria = 'aria-label="Explore the ' + e(t) + ' case study"'
            cta = btn("Explore More", CS, "btn--sm", False, aria)
            cards.append(f'<article class="story fx" data-cat="{e(cat)}" tabindex="0"><div class="story__media">{layers}</div>{FX}<span class="story__tag">{e(t)}</span>'
                         f'<div class="story__panel"><strong>{e(t)}</strong>{desc}{cta}</div></article>')
    return f'''
<section class="section" id="stories" aria-labelledby="stories-title">
  <div class="container">
    <div class="section-head"><div class="section-head__text">
      <h2 class="h2" id="stories-title" data-split>Creating Success Stories<br>Around the Globe</h2>
      <p class="lede" data-reveal>Discover how other companies partner with Folio3 to create customer satisfaction — while maximizing operations.</p>
    </div></div>
    {filter_bar("story-grid", list(STORIES), "Filter case studies by service")}
    <div class="stories" id="story-grid">{"".join(cards)}</div>
  </div>
</section>'''

# ---------------------------------------------------------------- Clients — two rows exactly as on www.folio3.com (60s forward / 48s reverse)
CLIENTS = ["Parr Public Safety Equipment", "ApexChat", "Barnes & Noble", "Cisco", "Colgate-Palmolive", "Agri Beef Co.", "MIT",
           "Mercedes-Benz", "Honda", "SquareTrade", "HipLink", "Petzam", "Standard Chartered", "MySQL", "SAP"]
CLIENT_TRIM = json.loads((ROOT / "assets/figma/client-trim.json").read_text())

def client_cells():
    """Static grid; each logo sized by optical area (same visual weight regardless of shape), never stretched."""
    out = []
    for i, n in enumerate(CLIENTS, 1):
        ar = CLIENT_TRIM[f"{i:02d}"]
        w = min((0.085 * ar) ** .5, 0.70, 0.27 * ar)   # fraction of cell width; height capped at 54% of a 2:1 cell
        out.append(f'<li class="client" data-reveal style="--i:{(i - 1) % 5}"><img src="{LA(f"client-{i:02d}-t")}" alt="{e(n)}" style="--w:{w * 100:.1f}%" loading="lazy"></li>')
    return "".join(out)

def clients():
    return f'''
<section class="section section--surface" id="clients" data-bg="gray" aria-labelledby="clients-title">
  <div class="container section-head"><div class="section-head__text">
    <span class="eyebrow" data-reveal>Our Clients</span>
    <h2 class="h2" id="clients-title" data-split>Our Portfolio of Satisfied Partners</h2>
  </div></div>
  <div class="container"><ul class="client-grid" role="list">{client_cells()}</ul></div>
</section>'''

QUOTES = {
    "AI": [("Working with the Folio3 team has been a great experience. Your dedication, creativity, and adaptability in overcoming challenges for the Moodology app project are truly commendable.", "Azhar Ali", "Director, AiGenics", "https://digitalhealth.folio3.com/wp-content/uploads/2023/10/moodology.webp"),
           ("We had an insane few weeks with a big push to launch an end-to-end app that ties the entire Opsis process together. We couldn't have done it without the team that we have. So, thank you Folio3 for making our dream come true. Your efforts are much appreciated!", "Kevin Grundy", "Chief Executive Officer, Opsis Health", "https://cloud.folio3.com/wp-content/uploads/2022/09/opsis-health-logo.webp"),
           ("Folio3's expertise and industry partnerships made them the ideal choice for our startup. Their clear communication and technical skills in pose estimation and biometric tracking exceeded our expectations. The software's performance, especially in lacrosse, was outstanding.", "Andrew Clarkson", "Locked In Lacrosse", CDN + "96.webp")],
    "App Dev": [("I would like to give a special shout-out to the team. You are doing a great job as a team. I'm very proud of you guys. You all are making my ideas come to life. All your efforts are highly appreciated.", "Robin Mehdee", "Manager Web Development Team", M + "f3-f1b31a65a741-1acd6e80-4ae6-439d-a57b-3c4f98135784.png"),
                ("Folio3 successfully tackled and resolved all of the partner's challenges. They provide the appropriate level of project management, and proactiveness is a hallmark of their work.", "Omar Al-Midani", "Co-Founder & President", M + "f3-f617180dc7a7-1b88aeec-77c8-4bca-a570-a2cb5bbecbba.png"),
                ("The Folio3 team working with me on the HANOR LMS have been key in making my vision a reality. All the team members have shown that they understand and share the end goal as I do, which for me, made this project progress with ease.", "Jenna Mencke", "Training & Development Coordinator, HANOR", "https://cloud.folio3.com/wp-content/uploads/2022/09/hanor-logo.jpg")],
    "NetSuite": [("Folio3's initial project setup and understanding of ADM's needs were superior to previous NetSuite providers. The project went live on time despite complexities and adjustments, integrating two new international entities.", "Michael Thompson", "Financial Director, ADM", "https://netsuite.folio3.com/wp-content/uploads/2025/01/adm-financial-director.webp"),
                 ("Folio3 helped us connect our ERP system with our SuiteCommerce site. The upgrade significantly improved data management, inventory accuracy, and customer communication. Folio3's team was responsive and collaborative throughout the implementation process.", "Wendy Shu", "CEO, Eravant", "https://netsuite.folio3.com/wp-content/uploads/2025/01/Wendy-Shu.webp"),
                 ("Folio3 implemented NetSuite ERP for Naked Wardrobe to consolidate its disparate systems (Magento, ShipStation, Excel spreadsheets). The implementation involved significant customizations to manage orders at the style level crucial to the fashion industry.", "Kamelia Kaviani", "CFO, Naked Wardrobe", "https://netsuite.folio3.com/wp-content/uploads/2025/02/Frame-1410126437.png")],
    "Microsoft Dynamics": [("The team has done a tremendous job from testing and deploying our DAX applications to go live. They have also helped develop a reusable pattern for scheduling processes used by multiple workers. We will definitely continue to lean on Folio3 for future support of these applications.", "Maridee Lemieux", "IT Manager, Agri Beef", "https://agtech.folio3.com/wp-content/uploads/2026/09/image-69229-1.webp"),
                           ("Your business is one of the most impressive I've dealt with. So professional, great communicators, reasonable, and nothing is ever a problem.", "Healthy Life", "Microsoft Dynamics client", "https://dynamics.folio3.com/wp-content/uploads/2026/07/client-story-healthy-life.webp"),
                           ("The Folio3 team consistently exceeded our expectations. It felt as if we were working with an onshore team.", "TrueTrac", "Microsoft Dynamics client", "https://dynamics.folio3.com/wp-content/uploads/2026/07/client-story-true-trac.webp")],
    "Ecommerce": [("The Folio3 team has been absolutely amazing to work with. They're solution-oriented, deliver quality work based on our business requirements, and play a critical role in launching our initiatives.", "Face Reality Skin Care", "eCommerce client", "https://ecommerce.folio3.com/wp-content/uploads/2024/12/face-reality-thumb-1.webp"),
                  ("After months searching for the right partner, Folio3 completely nailed our complexity. Their detail-oriented, highly skilled team delivered a sophisticated website that created measurable business performance that we're thrilled with.", "PureLife Dental", "eCommerce client", "https://ecommerce.folio3.com/wp-content/uploads/2024/12/purelife-thumb.webp"),
                  ("Folio3 understands our vision perfectly, providing cost-effective solutions with zero communication barriers that tripled daily orders, allowing us to compete with industry leaders.", "HFF Custom Rods", "eCommerce client", "https://ecommerce.folio3.com/wp-content/uploads/2024/12/HFF-thumb.webp")],
    "AgTech": [("The team was intuitive, solution-minded, and genuinely driven to get the job done. What stood out wasn't just the technical output, it was the way the work got done. Personable, focused, and easy to work with.", "Trevor Gartner", "Vice President, Information Services, Vytelle", "https://agtech.folio3.com/wp-content/uploads/2026/09/image-69227.webp"),
               ("Great achievement by the team. Thank you for all the hard work that went into this project. I'm excited to see the impact the Tick Academy mobile app will have in the market.", "Veerle Hagemeers", "Global Innovation Marketing & Global Launch Lead (Farm Animals), Elanco", "https://agtech.folio3.com/wp-content/uploads/2026/09/image-69374.webp"),
               ("Our end users are very satisfied with the user interface and the performance of the app and are excited to be more mobile. I appreciate the hard work and commitment to deliver a top-quality solution.", "Sandy Kabat", "Systems Administrator, L&M", "https://agtech.folio3.com/wp-content/uploads/2026/09/Clip-path-group.webp")],
    "Digital Health": [("Team Folio3 brought my dream app to reality. They explained every step to our non-technical team professionally. Wireframe and design processes were outstanding, and they built a stunning and perfectly integrated application.", "Elizabeth Miazga", "MD FRCSC, Saint Michael's Medical Center", "https://digitalhealth.folio3.com/wp-content/uploads/2026/03/image-1-1-removebg-preview.webp"),
                       ("I appreciate your remarkable work during the recent laboratory service phase. Your determination, analytical thinking, and continuous efforts were crucial in overcoming challenges and achieving success.", "Maker Athian", "Founder, iVision", "https://digitalhealth.folio3.com/wp-content/uploads/2023/12/medical-logo.webp"),
                       ("Kudos to your team for outstanding work in the discovery phase! Your team understood our business and workflows by asking the right questions and extracting the most useful information.", "Shaukat Zakaria", "CEO, HealthQuest", "https://digitalhealth.folio3.com/wp-content/uploads/2023/12/Health-quest.webp")],
    "Cloud Services": [("The expertise showcased by Folio3's Cloud team is truly staggering. I know no other group of people who have come even half as close as you have to completing a complex system, while ensuring that it works seamlessly with the existing product.", "Joheem Loh", "Partner, Eike", "https://cloud.folio3.com/wp-content/uploads/2022/09/eike-consulting-logo.webp"),
                       ("With the support of your team, we were able to grow our customer list by almost 2X and close a districtwide contract with Houston ISD, the largest school district in Texas with over 274 schools.", "John P. Kresky", "Founder and CEO, Summit K12", "https://cloud.folio3.com/wp-content/uploads/2022/09/summit-K12.webp"),
                       ("Folio3 has a very good understanding of animal production business and is an expert in cloud design and development. The volume and quality of work that has been accomplished in a short amount of time is truly amazing.", "Corey White", "Director of Technology, Cactus Feeders", "https://cloud.folio3.com/wp-content/uploads/2022/09/cactusfeeders-logo.jpg")],
}

def testimonials():
    cards = "".join(f'<figure class="quote fx" data-cat="{e(cat)}">{FX}{ICON["quote"]}<blockquote>{e(q)}</blockquote><div class="quote__logo"><img src="{e(logo)}" alt="" loading="lazy"></div><figcaption class="quote__who"><strong>{e(n)}</strong><span>{e(r)}</span></figcaption></figure>'
                    for cat, items in QUOTES.items() for q, n, r, logo in items)
    return f'''
<section class="section" id="testimonials" aria-labelledby="quotes-title">
  <div class="container">
    <div class="section-head"><div class="section-head__text">
      <h2 class="h2" id="quotes-title" data-split>Echoes of Impact: Hear What<br>Clients Say About Folio3</h2>
      <p class="lede" data-reveal>Learn how Folio3 helped its clients every step of the way.</p>
    </div></div>
    {filter_bar("quote-grid", list(QUOTES), "Filter testimonials by service")}
    <div class="quotes" id="quote-grid">{cards}</div>
  </div>
</section>'''

# ---------------------------------------------------------------- Trending talks (dark)
TALKS = [("AI Governance", "What Is Shadow AI? The Risks It Creates and How to Control It", "https://www.folio3.com/ai/blog/what-is-shadow-ai"),
         ("AI Governance", "LLM Cost Optimization: Techniques, Strategies, and Software to Cut AI Spend", "https://www.folio3.com/ai/blog/llm-cost-optimization"),
         ("AI Governance", "AI Governance and Compliance Readiness: A Practical Guide", "https://www.folio3.com/ai/blog/ai-governance-and-compliance-readiness")]

def talks():
    rows = "".join(f'<a class="talk" href="{e(h)}" data-reveal><span class="talk__cat">{e(c)}</span><span class="talk__row"><span class="talk__title">{e(t)}</span><span class="talk__arrow">{ICON["arrow"]}</span></span></a>' for c, t, h in TALKS)
    return f'''
<section class="section section--dark" id="insights" aria-labelledby="talks-title" data-bg="dark">
  <div class="container">
    <div class="section-head"><div class="section-head__text">
      <span class="eyebrow" data-reveal>Insights</span>
      <h2 class="h2" id="talks-title" data-split>Trending Talks: Latest<br>Insights From Folio3</h2>
    </div></div>
    <div class="talks">{rows}</div>
    <div class="talks-cta" data-reveal>{btn("Read the Blog", "https://www.folio3.com/blog")}</div>
  </div>
</section>'''

# ---------------------------------------------------------------- Global presence + contact
GLOBE = (ROOT / "assets/map/globe.json").read_text()

def globe():
    return f'''<figure class="globe" data-reveal="fade">
        <div class="globe__stage" data-globe><canvas class="globe__canvas" role="img" aria-label="Rotating 3D globe marking Folio3 offices in the United States, Canada, Mexico, the United Kingdom, Bulgaria, Saudi Arabia, the UAE, Pakistan and Australia"></canvas>
          <script type="application/json" id="globe-data">{GLOBE}</script></div>
      </figure>'''

STATS2 = [("5,000+", "Projects Delivered"), ("700+", "Global Employees"), ("1,000+", "Companies Served"), ("20+", "Global Awards Won")]

def contact():
    st = "".join(f'<div class="stat"><div class="stat__num" data-count="{n}">{n}</div><div class="stat__label">{e(l)}</div></div>' for n, l in STATS2)
    fields = [("first", "First Name", "text", True, False, "given-name"), ("last", "Last Name", "text", True, False, "family-name"),
              ("email", "Email", "email", True, False, "email"), ("phone", "Phone Number", "tel", False, False, "tel"),
              ("org", "Organization", "text", True, True, "organization"), ("msg", "Tell us about your project", "textarea", True, True, "off")]
    fh = ""
    for fid, label, typ, req, full, ac in fields:
        star = "*" if req else ""
        ctl = (f'<textarea id="f-{fid}" placeholder=" " rows="3" autocomplete="off" {"required" if req else ""} aria-describedby="e-{fid}"></textarea>' if typ == "textarea"
               else f'<input id="f-{fid}" type="{typ}" placeholder=" " autocomplete="off" {"required" if req else ""} aria-describedby="e-{fid}">')
        fh += f'<div class="field{" field--full" if full else ""}">{ctl}<label for="f-{fid}">{e(label)}{star}</label><span class="field__err" id="e-{fid}"></span></div>'
    return f'''
<section class="section" id="contact" aria-labelledby="contact-title">
  <div class="container contact">
    <h2 class="h2 contact__title" id="contact-title" data-split>Revolutionizing Customer Experience<br>Worldwide with Build, Sell &amp; Scale</h2>
    <div class="contact__left">
      {globe()}
      <div class="stats contact__stats" style="border:0;margin:0;padding:0" data-stagger>{st}</div>
    </div>
    <div class="form-card" id="project-form" data-reveal="fade">
      <h3>Interested in Soaring High<br>and Thriving with Success?</h3>
      <p>Start Your Success Journey With Folio3 Today!</p>
      <form id="contact-form" action="#" novalidate data-demo-form aria-describedby="demo-note">
        <div class="form-grid">{fh}</div>
        <p class="form-note" id="demo-note">Demo form — this is an unofficial design preview. Nothing you type is sent, stored or shared.</p>
        <div style="margin-top:18px">{btn_submit("Submit")}</div>
      </form>
      <p class="form-success" tabindex="-1" role="status">Thanks! Your details passed validation. In this preview nothing was sent — the live form will connect to Folio3's CRM.</p>
    </div>
  </div>
</section>'''

# ---------------------------------------------------------------- Footer
def footer():
    col = lambda items: "".join(f'<li><a href="{e(h)}">{e(t)}</a></li>' for t, h in items)
    about = [("Industries", "#services"), ("Work", "https://www.folio3.com/case-studies"), ("Services", "#services"), ("Company", "https://www.folio3.com/about-us"), ("Careers", "https://www.folio3.com/careers")]
    svc = [("Artificial Intelligence", "https://www.folio3.com/ai"), ("App Development", "https://www.folio3.com/app-development"), ("NetSuite", "https://netsuite.folio3.com/"),
           ("Microsoft Dynamics", "https://dynamics.folio3.com/"), ("Ecommerce", "https://ecommerce.folio3.com/"), ("AgTech", "https://agtech.folio3.com/"),
           ("Digital Health", "https://digitalhealth.folio3.com/"), ("Cloud Services", "https://cloud.folio3.com/")]
    sup = [("Privacy Statement", "https://www.folio3.com/privacy-policy"), ("Terms & Conditions", "https://www.folio3.com/terms-and-conditions"), ("Cookie Policy/Settings", "#"), ("Accessibility Statement", "#"), ("Sitemap", "#")]
    return f'''
<footer class="footer" data-bg="black">
  <div class="container">
    <div class="footer__big" data-reveal><span>Let's build<br>what's <em>next.</em></span></div>
    <div class="footer__grid">
      <div><h4>About</h4><ul>{col(about)}</ul></div>
      <div><h4>Services</h4><ul class="footer__svc">{col(svc)}</ul></div>
      <div><h4>Support</h4><ul>{col(sup)}</ul></div>
      <div><h4>Stay Informed</h4>
        <form class="subscribe" id="subscribe" action="#" novalidate data-demo-form><label class="sr-only" for="sub-email">Email address</label><input id="sub-email" type="email" placeholder="Email Address" autocomplete="off">
        {btn_submit("Subscribe")}<span class="msg" aria-live="polite"></span></form></div>
    </div>
    <div class="footer__bottom"><span>© <span data-year>2026</span> Folio3 Software Inc. All Rights Reserved.</span><span>Unofficial design preview hosted on GitHub Pages — not the official Folio3 website (folio3.com)</span></div>
  </div>
</footer>'''

# ---------------------------------------------------------------- Floating "Folio3 Practices" (live folio3.com: right-edge tab → right drawer)
def practices_drawer():
    from urllib.parse import urlparse
    data = next(d for label, kind, d, _ in NAV if kind == "practices")
    def host(h):
        u = urlparse(url(h)); return (u.netloc.replace("www.", "") + (u.path.rstrip("/") if u.path not in ("", "/") else ""))
    items = "".join(f'<li style="--i:{i}"><a class="pd-item" href="{url(h)}"><span class="pd-item__icon">{_svg(PRACTICE_ICON[t])}</span>'
                    f'<span class="pd-item__text"><strong>{e(t)}</strong><small>{e(host(h))}</small></span>{ARROW}</a></li>' for i, (t, h, img) in enumerate(data))
    return f'''
<button class="pd-tab" type="button" aria-haspopup="dialog" aria-expanded="false" aria-controls="practices-drawer">{_svg(MENU_ICON["Folio3 Practices"], "pd-tab__icon")}<span>Folio3 Practices</span></button>
<div class="pd" id="practices-drawer" role="dialog" aria-modal="true" aria-labelledby="pd-title" hidden>
  <div class="pd__scrim" data-pd-close></div>
  <div class="pd__panel" tabindex="-1">
    <div class="pd__head">
      <span class="mega__badge">{_svg(MENU_ICON["Folio3 Practices"])}</span>
      <div><h2 class="pd__title" id="pd-title">Folio3 Practices</h2><p class="pd__desc">{e(MENU_META["Folio3 Practices"]["desc"])}</p></div>
      <button class="pd__close icon-btn" type="button" data-pd-close aria-label="Close Folio3 Practices"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></button>
    </div>
    <ul class="pd__list">{items}</ul>
  </div>
</div>'''

# ---------------------------------------------------------------- Floating "Back to top" (appears after section 2)
def preview_notice():
    """Persistent, low-key disclosure: this GitHub Pages build is a design preview, not Folio3's production site."""
    return ('<p class="preview-notice" role="note"><span class="preview-notice__dot" aria-hidden="true"></span>'
            'Unofficial preview<span class="preview-notice__more"> · not folio3.com</span></p>')

def to_top():
    return ('<a class="to-top" href="#top" aria-label="Back to top" tabindex="-1">'
            '<span class="to-top__icon"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 13V3M3.5 7.5L8 3l4.5 4.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg></span>'
            '<span class="to-top__label">Back to top</span></a>')

def page():
    css = (ROOT / "src/styles.css").read_text()
    js = (ROOT / "src/main.js").read_text()
    body = header() + '<main id="main">' + hero() + process() + industries() + ways() + solutions() + tech() + spotlight() + about() + stories() + clients() + testimonials() + talks() + contact() + "</main>" + footer() + practices_drawer() + to_top() + preview_notice()
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Folio3 homepage redesign — unofficial design preview</title>
<meta name="description" content="Unofficial design preview of a Folio3 homepage redesign (not the official website). Lead the AI shift with Folio3 — your guide to secure, enterprise-ready AI. Software engineering, NetSuite, Microsoft Dynamics, ecommerce and AI solutions.">
<meta name="robots" content="noindex, nofollow">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,700;9..40,800&family=Plus+Jakarta+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="preconnect" href="https://cdn-aiml.folio3.site">
<style>{css}</style>
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
{body}
<script>{js}</script>
</body>
</html>'''

# Hero variations: A = digital-rain matrix (index.html, approved); B = Boon-style dot grid (index-hero-b.html, for comparison).
HERO_TAG = '<section class="hero" id="top" aria-labelledby="hero-title">'

def add_img_dims(html):
    """Stamp intrinsic width/height on inlined images that lack them, so lazy images reserve their box before they decode.
    (Without it the awards wall grew ~86px on load, pushing every anchor below it — e.g. #project-form — off target.)"""
    import io, re as _re
    from PIL import Image
    def fix(m):
        tag = m.group(0)
        if " width=" in tag: return tag
        d = _re.search(r'src="data:image/[a-z+]+;base64,([^"]+)"', tag)
        if not d: return tag
        w, h = Image.open(io.BytesIO(_b64.b64decode(d.group(1)))).size
        return tag[:-1] + f' width="{w}" height="{h}">'
    return _re.sub(r"<img\b[^>]*>", fix, html)

if __name__ == "__main__":
    (ROOT / "dist").mkdir(exist_ok=True)
    html = add_img_dims(page())
    assert HERO_TAG in html
    variants = {"index.html": html,
                "index-hero-b.html": html.replace(HERO_TAG, HERO_TAG.replace('class="hero"', 'class="hero" data-hero-fx="grid"'), 1)
                                         .replace("<title>Folio3 homepage redesign", "<title>Folio3 homepage redesign (Hero B)", 1)}
    for name, doc in variants.items():
        out = ROOT / "dist" / name
        out.write_text(doc)
        print("wrote", out, out.stat().st_size, "bytes")
