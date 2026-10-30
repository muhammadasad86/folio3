"""Turn extracted layer trees (build/figma/*.json) into use_figma scripts (build/figma/calls/*.js), each < 50k chars.

Layers are rebuilt as native Figma nodes: frames (fills, gradients, radii, strokes, shadows, clipping),
editable text (font runs), vector icons (SVG), image rectangles and component instances (buttons, process cards,
floating tab). Image rectangles get a coded placeholder colour (asset index) that tools/figma_images.py swaps
for the real image later. Large subtrees are split across calls by addressing the parent via child-index paths.
"""
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "build" / "figma"; CALLS = D / "calls"; CALLS.mkdir(exist_ok=True)
LIMIT = 42000
STYLE = {300: "Light", 400: "Regular", 500: "Medium", 600: "SemiBold", 700: "Bold", 800: "ExtraBold", 900: "Black"}

def style_of(w, it):
    w = min(STYLE, key=lambda k: abs(k - int(w)))
    s = STYLE[w]
    return (s + " Italic" if s != "Regular" else "Italic") if it else s

ASSETS = json.loads((D / "asset_index.json").read_text()) if (D / "asset_index.json").exists() else []
def asset_idx(a):
    if a not in ASSETS: ASSETS.append(a)
    return ASSETS.index(a)

r3 = lambda v: round(v, 3)
def col(c): return [r3(c["r"]), r3(c["g"]), r3(c["b"]), r3(c["a"])] if c else None
def i1(v): return round(v, 1) if abs(v - round(v)) > 0.05 else int(round(v))

import xml.etree.ElementTree as ET
CANVAS = {}
def compact_svg(s):
    try: ET.fromstring(s)
    except ET.ParseError as e: print("WARN invalid svg dropped:", str(e)[:60]); return None
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"(\d+\.\d{2})\d+", r"\1", s)
    s = re.sub(r' (class|data-[a-z-]+|aria-hidden|focusable|role)="[^"]*"', "", s)
    return s.replace("> <", "><")

def conv(n, ox, oy, cw):
    """compact array form, coordinates relative to parent origin (ox, oy)."""
    x, y, w, h = n["r"]; rx, ry = i1(x - ox), i1(y - oy)
    t = n["t"]
    if t == "f":
        v = n.get("v", {}); st = {}
        if v.get("bg"): st["b"] = col(v["bg"])
        if v.get("grads"): st["g"] = [[g["type"][0], g["angle"], [[r3(s["p"])] + col(s["c"]) for s in g["stops"]]] for g in v["grads"]]
        if v.get("rad"): rr = [i1(r) for r in v["rad"]]; st["r"] = rr[0] if len(set(rr)) == 1 else rr
        if v.get("border"): st["s"] = [[i1(w_) for w_ in v["border"]["w"]], col(v["border"]["c"])]
        if v.get("shadow"): st["e"] = [[1 if s["inset"] else 0, i1(s["x"]), i1(s["y"]), i1(s["b"]), i1(s["s"]), col(s["c"])] for s in v["shadow"]]
        if v.get("blur"): st["bl"] = i1(v["blur"])
        if n.get("clip"): st["c"] = 1
        if n.get("o") is not None: st["o"] = r3(n["o"])
        return ["f", n["n"][:60], rx, ry, i1(w), i1(h), st, [conv(k, x, y, cw) for k in n.get("k", [])]]
    if t == "x":
        fam, wt, size, it = n["f"]
        base = [fam, style_of(wt, it), i1(size)]
        runs = []
        for r in n["runs"]:
            f2 = r["f"]; rb = [f2[0], style_of(f2[1], f2[3]), i1(f2[2])]
            if rb != base or (r["c"] and col(r["c"]) != col(n["c"])) or abs(r["ls"] - n["ls"]) > 0.05:
                runs.append([r["s"], r["e"], rb, col(r["c"]), i1(r["ls"])])
        nw = 1 if (n.get("ws") in ("nowrap", "pre") or (n.get("lh") and h < n["lh"] * 1.6) or (not n.get("lh") and h < size * 1.9)) else 0
        out = ["x", rx, ry, i1(w), i1(h), n["chars"], base, col(n["c"]), i1(n["lh"]) if n.get("lh") else 0, i1(n["ls"]), n["al"][0], nw, runs]
        if n.get("stroke"): out.append([i1(n["stroke"]["w"]), col(n["stroke"]["c"])])
        return out
    if t in ("i", "cv"):
        a = n.get("asset")
        if t == "cv":   # one still per canvas kind + breakpoint (hero dots / globe)
            key = ("hero" if "hero" in n["n"] else "globe") + ("-m" if cw < 700 else "-d")
            a = CANVAS.setdefault(key, a)
        rad = n.get("rad"); rad = (i1(rad[0]) if rad and len(set(rad)) == 1 else [i1(r) for r in rad]) if rad else 0
        name = ("Canvas / " + ("Hero background — animated dot matrix (live in code)" if "hero" in n["n"] else "Interactive 3D globe (live in code)")) if t == "cv" else "Image / " + (n["n"] or "image")[:50]
        return ["i", name, rx, ry, i1(w), i1(h), asset_idx(a) if a else -1, 1 if n.get("fit") == "contain" else 0, rad, r3(n["o"]) if n.get("o") is not None else 1, n.get("remote", "")[:120]]
    if t == "s":
        sv = compact_svg(n["svg"])
        if sv is None: return ["f", "Icon (unsupported) / " + n["n"][:30], rx, ry, i1(w), i1(h), {}, []]
        return ["s", n["n"][:40], rx, ry, i1(w), i1(h), sv]
    if t == "c":
        d = {k: n[k] for k in ("label", "cls", "dark", "i", "focused") if k in n}
        return ["c", n["kind"], rx, ry, i1(w), i1(h), d, n["n"][:60]]
    raise ValueError(t)

BUILDER = r"""
const FONTS=__FONTS__;for(const f of FONTS)await figma.loadFontAsync({family:f[0],style:f[1]});
await figma.setCurrentPageAsync(await figma.getNodeByIdAsync('4:813'));const PG=figma.currentPage;
let ROOT=PG.children.find(n=>n.type==='FRAME'&&n.name===__ROOTNAME__);
if(!ROOT){ROOT=figma.createFrame();ROOT.name=__ROOTNAME__;ROOT.resize(__RW__,__RH__);ROOT.x=__RX__;ROOT.y=__RY__;ROOT.fills=[{type:'SOLID',color:{r:1,g:1,b:1}}];ROOT.clipsContent=true;PG.appendChild(ROOT);}
let P=ROOT;for(const i of __PATH__)P=P.children[i];
const pc=c=>({type:'SOLID',color:{r:c[0],g:c[1],b:c[2]},opacity:c[3]});
const rgba=c=>({r:c[0],g:c[1],b:c[2],a:c[3]});
const grad=g=>{const stops=g[2].map(s=>({position:Math.min(1,Math.max(0,s[0])),color:rgba(s.slice(1))}));
 if(g[0]==='r')return{type:'GRADIENT_RADIAL',gradientTransform:[[1,0,0],[0,1,0]],gradientStops:stops};
 const a=(g[1]-90)*Math.PI/180,c=Math.cos(a),s=Math.sin(a);
 return{type:'GRADIENT_LINEAR',gradientTransform:[[c,s,0.5-0.5*c-0.5*s],[-s,c,0.5+0.5*s-0.5*c]],gradientStops:stops};};
const rad=(n,r)=>{if(!r)return;if(Array.isArray(r)){n.topLeftRadius=r[0];n.topRightRadius=r[1];n.bottomRightRadius=r[2];n.bottomLeftRadius=r[3];}else n.cornerRadius=r;};
const sz=(n,w,h)=>n.resize(Math.max(.01,w),Math.max(.01,h));
const BTN=await figma.getNodeByIdAsync('4:899'),PCS=await figma.getNodeByIdAsync('65:1575'),ICS=await figma.getNodeByIdAsync('65:1509'),TAB=await figma.getNodeByIdAsync('66:1525'),TOT=await figma.getNodeByIdAsync('76:3670');
const STEPS=[['Connect and Listen','We start with your problem or idea, your goals and what success looks like for your team.'],['Evaluate Your Systems','We map how work actually flows across your tools, data and teams.'],['Find the Highest-ROI Workflows','We rank opportunities by business value and effort, so you invest where AI pays off first.'],['Validate','We test the use case against your real data and constraints before any major spend.'],['Launch an MVP','A working version in your users’ hands, so results are measured, not assumed.'],['Build and Scale','We harden it for production with security, governance and integrations, then scale it across teams.']];
const pkey=n=>Object.keys(PCS.componentPropertyDefinitions).find(k=>k.startsWith(n+'#'));
let count=0;
async function mk(d,par){
 const t=d[0];let n;
 if(t==='f'){const st=d[6];n=figma.createFrame();n.name=d[1];sz(n,d[4],d[5]);
  const fills=[];if(st.b)fills.push(pc(st.b));if(st.g)for(const g of [...st.g].reverse())fills.push(grad(g));n.fills=fills;
  rad(n,st.r);
  if(st.s){const w=st.s[0];n.strokes=[pc(st.s[1])];n.strokeAlign='INSIDE';if(w.every(x=>x===w[0]))n.strokeWeight=w[0];else{n.strokeTopWeight=w[0];n.strokeRightWeight=w[1];n.strokeBottomWeight=w[2];n.strokeLeftWeight=w[3];}}
  const fx=[];if(st.e)for(const e of st.e)fx.push({type:e[0]?'INNER_SHADOW':'DROP_SHADOW',color:rgba(e[5]),offset:{x:e[1],y:e[2]},radius:e[3],spread:e[4],visible:true,blendMode:'NORMAL'});
  if(st.bl)fx.push({type:'BACKGROUND_BLUR',radius:st.bl,visible:true});if(fx.length)n.effects=fx;
  n.clipsContent=!!st.c;if(st.o!==undefined)n.opacity=st.o;
  par.appendChild(n);n.x=d[2];n.y=d[3];
  for(const k of d[7])await mk(k,n);}
 else if(t==='x'){n=figma.createText();const b=d[6];n.fontName={family:b[0],style:b[1]};n.fontSize=b[2];n.characters=d[5];
  n.fills=d[7]?[pc(d[7])]:[];if(d[8])n.lineHeight={unit:'PIXELS',value:d[8]};if(d[9])n.letterSpacing={unit:'PIXELS',value:d[9]};
  n.textAlignHorizontal=({l:'LEFT',s:'LEFT',c:'CENTER',r:'RIGHT',e:'RIGHT',j:'JUSTIFIED'})[d[10]]||'LEFT';
  for(const r of d[12]){if(r[1]<=r[0])continue;n.setRangeFontName(r[0],r[1],{family:r[2][0],style:r[2][1]});n.setRangeFontSize(r[0],r[1],r[2][2]);if(r[3])n.setRangeFills(r[0],r[1],[pc(r[3])]);if(r[4])n.setRangeLetterSpacing(r[0],r[1],{unit:'PIXELS',value:r[4]});}
  if(d[13]){n.strokes=[pc(d[13][1])];n.strokeWeight=d[13][0];n.strokeAlign='CENTER';}
  par.appendChild(n);
  if(d[11]&&d[10]!=='c'&&d[10]!=='r'){n.textAutoResize='WIDTH_AND_HEIGHT';}else{n.resize(Math.max(1,d[3]+2),Math.max(1,d[4]));n.textAutoResize='HEIGHT';}
  n.x=d[1]-(d[10]==='c'?1:0);n.y=d[2];}
 else if(t==='i'){n=figma.createRectangle();n.name=d[1];sz(n,d[4],d[5]);
  n.fills=[{type:'SOLID',color:{r:(d[6]%250)/255,g:d[7]?0.2:0.1,b:0.987-Math.floor(d[6]/250)*0.01}}];
  rad(n,d[8]);if(d[9]<1)n.opacity=d[9];par.appendChild(n);n.x=d[2];n.y=d[3];}
 else if(t==='s'){try{n=figma.createNodeFromSvg(d[6]);n.name='Icon / '+d[1];}catch(e){n=figma.createRectangle();n.name='Icon (svg failed) / '+d[1];n.fills=[];}
  par.appendChild(n);try{sz(n,d[4],d[5]);}catch(e){}n.x=d[2];n.y=d[3];}
 else if(t==='c'){const k=d[1],o=d[6];
  if(k==='btn'){const c=o.cls||'';const style=/btn--dark/.test(c)?'Dark':/btn--ghost/.test(c)?'Ghost':'Primary';const size=/btn--sm/.test(c)?'Small':'Default';
   const v=BTN.children.find(x=>x.name===`Style=${style}, Size=${size}, State=Default`)||BTN.children[0];n=v.createInstance();
   const tx=n.findOne(x=>x.type==='TEXT');if(tx){await figma.loadFontAsync(tx.fontName);tx.characters=o.label||'Button';}
   n.name='Button / '+(o.label||'');}
  else if(k==='pcard'){const sizeV=__RW__<700?'Mobile':'Desktop';const v=PCS.children.find(x=>x.name===`State=${o.focused?'Focused':'Default'}, Size=${sizeV}`);n=v.createInstance();const i=o.i||0;
   n.setProperties({[pkey('Title')]:STEPS[i][0],[pkey('Description')]:STEPS[i][1],[pkey('Step label')]:`STEP ${String(i+1).padStart(2,'0')} / 06`,[pkey('Number')]:String(i+1).padStart(2,'0'),[pkey('Show chips')]:i===1});
   const ic=n.findOne(x=>x.name==='Icon');ic.swapComponent(ICS.children[i]);const cc=o.focused?{r:0,g:0,b:0}:{r:179/255,g:179/255,b:179/255};
   ic.findAll(x=>'strokes' in x&&x.strokes.length).forEach(x=>x.strokes=[{type:'SOLID',color:cc}]);ic.findAll(x=>'fills' in x&&x.type!=='FRAME'&&x.fills.length&&x.strokes.length===0).forEach(x=>x.fills=[{type:'SOLID',color:cc}]);
   n.name='Process Card / '+String(i+1).padStart(2,'0')+(o.focused?' (focused)':'');}
  else if(k==='tab'){n=TAB.children.find(x=>x.name===`Size=${__RW__<700?'Mobile':'Desktop'}, State=Default`).createInstance();n.name='Floating Tab / Folio3 Practices (fixed)';}
  else if(k==='totop'){n=TOT.children.find(x=>x.name===`Size=${__RW__<700?'Mobile':'Desktop'}, State=Default`).createInstance();n.name='Floating CTA / Back to top (fixed)';}
  par.appendChild(n);if(k!=='tab'&&k!=='totop'){try{sz(n,d[4],d[5]);}catch(e){}}n.x=d[2];n.y=d[3];}
 count++;return n;}
for(const d of DATA)await mk(d,P);
return {root:ROOT.id,parentPath:__PATH__,created:count,parentKids:P.children.length};
"""

def fonts_in(nodes, acc):
    for d in nodes:
        if d[0] == "x":
            acc.add((d[6][0], d[6][1]))
            for r in d[12]: acc.add((r[2][0], r[2][1]))
        if d[0] == "f": fonts_in(d[7], acc)
    return acc

def plan(cap_name, root_name, page_x, page_y):
    cap = json.loads((D / f"{cap_name}.json").read_text())
    W, H = cap["w"], cap["h"]
    top = [conv(n, 0, 0, W) for n in cap["nodes"]]
    calls = []          # (path, [nodes])
    def size(d): return len(json.dumps(d, separators=(",", ":"), ensure_ascii=False))
    # each "slot" = list of children to append under parent path; existing count tracked to compute indices
    kid_count = {}
    def emit(nodes, path):
        cur = []; cur_size = 0
        def flush():
            nonlocal cur, cur_size
            if cur: calls.append((path, cur)); cur = []; cur_size = 0
        for d in nodes:
            s = size(d)
            if s + cur_size <= LIMIT:
                cur.append(d); cur_size += s
                kid_count[tuple(path)] = kid_count.get(tuple(path), 0) + 1
                continue
            if d[0] == "f" and s > LIMIT:
                shell = d[:7] + [[]]
                if cur_size + size(shell) > LIMIT: flush()
                cur.append(shell); cur_size += size(shell)
                idx = kid_count.get(tuple(path), 0); kid_count[tuple(path)] = idx + 1
                flush()
                emit(d[7], path + [idx])
            else:
                flush(); cur.append(d); cur_size = s
                kid_count[tuple(path)] = kid_count.get(tuple(path), 0) + 1
                if s > LIMIT: print("WARN oversized leaf", d[0], s)
        flush()
    emit(top, [])
    files = []
    for k, (path, nodes) in enumerate(calls):
        fonts = sorted(fonts_in(nodes, set()) | {("DM Sans", "Regular")})
        code = (BUILDER.replace("__FONTS__", json.dumps(fonts)).replace("__ROOTNAME__", json.dumps(root_name))
                .replace("__RW__", str(W)).replace("__RH__", str(H)).replace("__RX__", str(page_x)).replace("__RY__", str(page_y))
                .replace("__PATH__", json.dumps(path)))
        code = "const DATA=" + json.dumps(nodes, separators=(",", ":"), ensure_ascii=False) + ";\n" + code
        f = CALLS / f"{cap_name}_{k:02d}.js"; f.write_text(code); files.append((f.name, len(code), path, len(nodes)))
    (D / "asset_index.json").write_text(json.dumps(ASSETS))
    return files

if __name__ == "__main__":
    jobs = {"desktop-1440": ("Desktop — 1440 · Latest build", 2100, 0), "mobile-375": ("Mobile — 375 · Latest build", 3700, 4600)}
    which = sys.argv[1:] or list(jobs)
    for w in which:
        if w in jobs:
            fs = plan(w, *jobs[w])
        else:
            nm, x, y = sys.argv[2], int(sys.argv[3]), int(sys.argv[4]); fs = plan(w, nm, x, y); which = [w]
        for f in fs: print(f)
        if w not in jobs: break
    print("assets indexed:", len(ASSETS))
