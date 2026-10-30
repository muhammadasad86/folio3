"""Re-render an extracted layer tree as absolutely-positioned HTML (fidelity check before the Figma build)."""
import json, sys, html
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "build" / "figma"

def css_color(c): return f"rgba({round(c['r']*255)},{round(c['g']*255)},{round(c['b']*255)},{c['a']})" if c else "transparent"

def frame_css(n, ox, oy):
    x, y, w, h = n["r"]; v = n.get("v", {})
    s = [f"left:{x-ox}px;top:{y-oy}px;width:{w}px;height:{h}px"]
    if v.get("bg"): s.append(f"background-color:{css_color(v['bg'])}")
    if v.get("grads"):
        gs = []
        for g in v["grads"]:
            stops = ",".join(f"{css_color(st['c'])} {st['p']*100:.1f}%" for st in g["stops"])
            gs.append(f"linear-gradient({g['angle']}deg,{stops})" if g["type"] == "linear" else f"radial-gradient({g.get('shape') or 'circle'},{stops})")
        s.append("background-image:" + ",".join(gs))
    if v.get("rad"): s.append("border-radius:" + " ".join(f"{r}px" for r in v["rad"]))
    if v.get("border"): b = v["border"]; s.append("border-style:solid;border-color:" + css_color(b["c"]) + ";border-width:" + " ".join(f"{w}px" for w in b["w"]) + ";box-sizing:border-box")
    if v.get("shadow"): s.append("box-shadow:" + ",".join(f"{'inset ' if sh['inset'] else ''}{sh['x']}px {sh['y']}px {sh['b']}px {sh['s']}px {css_color(sh['c'])}" for sh in v["shadow"]))
    if n.get("clip"): s.append("overflow:hidden")
    if n.get("o") is not None: s.append(f"opacity:{n['o']}")
    return ";".join(s)

def render(nodes, ox, oy):
    out = []
    for n in nodes:
        t = n["t"]; x, y, w, h = n["r"]
        if t == "f":
            out.append(f'<div class="n" style="{frame_css(n, ox, oy)}">{render(n.get("k", []), x, y)}</div>')
        elif t == "x":
            fam, wt, size, it = n["f"]
            lh = f"line-height:{n['lh']}px;" if n.get("lh") else ""
            runs = sorted(n["runs"], key=lambda r: r["s"]); chars = n["chars"]; body = ""; pos = 0
            for r in runs:
                if r["s"] > pos: body += html.escape(chars[pos:r["s"]])
                f2 = r["f"]; body += f'<span style="font-family:\'{f2[0]}\';font-weight:{f2[1]};font-size:{f2[2]}px;color:{css_color(r["c"])};letter-spacing:{r["ls"]}px">{html.escape(chars[r["s"]:r["e"]])}</span>'; pos = r["e"]
            body += html.escape(chars[pos:])
            out.append(f'<div class="n t" style="left:{x-ox}px;top:{y-oy}px;width:{w+2}px;font-family:\'{fam}\';font-weight:{wt};font-size:{size}px;{lh}letter-spacing:{n["ls"]}px;color:{css_color(n["c"])};text-align:{n["al"]};white-space:pre-wrap">{body.replace(chr(10), "<br>")}</div>')
        elif t in ("i", "cv"):
            src = ("assets/" + n["asset"]) if n.get("asset") else n.get("remote", "")
            rad = f"border-radius:{n['rad'][0]}px;" if n.get("rad") else ""
            out.append(f'<img class="n" src="{src}" style="left:{x-ox}px;top:{y-oy}px;width:{w}px;height:{h}px;object-fit:{n.get("fit","fill")};{rad}{"opacity:%s;"%n["o"] if n.get("o") is not None else ""}">')
        elif t == "s":
            out.append(f'<div class="n" style="left:{x-ox}px;top:{y-oy}px;width:{w}px;height:{h}px">{n["svg"]}</div>')
        elif t == "c":
            out.append(f'<div class="n" style="left:{x-ox}px;top:{y-oy}px;width:{w}px;height:{h}px;outline:2px dashed magenta;font:10px sans-serif;color:magenta">{html.escape(n["kind"])}</div>')
    return "".join(out)

if __name__ == "__main__":
    name = sys.argv[1]
    d = json.loads((D / f"{name}.json").read_text())
    page = f'<!doctype html><meta charset=utf-8><style>body{{margin:0}} .n{{position:absolute;box-sizing:border-box}} .t{{margin:0}}</style><div style="position:relative;width:{d["w"]}px;height:{d["h"]}px;background:#fff">{render(d["nodes"], 0, 0)}</div>'
    (D / f"{name}.preview.html").write_text(page); print("wrote", D / f"{name}.preview.html")
