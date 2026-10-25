"""Original CAR-ART-001 concept studies; never loaded by the game.
Rebuild: python build_studies.py
Optional isolated current-renderer capture: python build_studies.py --godot <exe>
Core builder: Python standard library. Optional capture board uses installed Pillow; no downloaded artwork or fonts.
"""
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess, tempfile
from html import escape
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PALETTES = {
 "A": dict(name="Tinta de expedición", paper="#f1e8d2", ink="#263b38", sky="#d2e0d7", ground="#bfa983", leaf="#718e70", deep="#475e50", brick="#bb7756", roof="#76634e", water="#568c91", steel="#a9b6ae", light="#e1c27d"),
 "B": dict(name="Luz mineral", paper="#172c38", ink="#e3e2cc", sky="#91acac", ground="#686b5c", leaf="#41685e", deep="#294b49", brick="#ad7359", roof="#3e514e", water="#71b8b3", steel="#a5bdb6", light="#d9aa6d"),
 "C": dict(name="Línea solar", paper="#f8efdc", ink="#333d37", sky="#d8e7e2", ground="#d8bd83", leaf="#86a875", deep="#4c7863", brick="#cd8c64", roof="#92745a", water="#66a8ae", steel="#bdc9ba", light="#e4bb67"),
}
ROOMS = ["LOC_START", "LOC_BUILDING", "LOC_GRATE"]

class Drawing:
 def __init__(self, style):
  self.style=style; self.p=PALETTES[style]; self.fills=[]; self.strokes=[]
 def region(self,d,color,seed=None,outline=True,detail=False):
  self.fills.append((d,self.p[color],seed or (320,200)))
  if outline: self.line(d,detail)
 def line(self,d,detail=False):
  self.strokes.append((d,"detail" if detail else "contour"))
 def poly(self,pts,color,detail=False):
  self.region("M"+" L".join(f"{x},{y}" for x,y in pts)+" Z",color,pts[0],True,detail)
 def tree(self,x,y,w,h):
  # Original silhouettes vary between treatments. y = base.
  self.region(f"M{x-5},{y} L{x-3},{y-h*.48} L{x+6},{y-h*.48} L{x+8},{y} Z","roof",(x,y-15))
  if self.style=="A":
   d=f"M{x-w*.5},{y-h*.42} L{x-w*.58},{y-h*.72} L{x-w*.31},{y-h*.78} L{x-w*.23},{y-h*.96} L{x+w*.1},{y-h} L{x+w*.28},{y-h*.86} L{x+w*.51},{y-h*.81} L{x+w*.43},{y-h*.56} L{x+w*.15},{y-h*.43} Z"
  elif self.style=="B":
   d=f"M{x-w*.52},{y-h*.39} L{x-w*.6},{y-h*.72} L{x-w*.28},{y-h} L{x+w*.19},{y-h*.94} L{x+w*.55},{y-h*.64} L{x+w*.34},{y-h*.4} Z"
  else:
   d=f"M{x-w*.43},{y-h*.4} Q{x-w*.7},{y-h*.64} {x-w*.39},{y-h*.8} Q{x-w*.2},{y-h*1.1} {x+w*.08},{y-h*.96} Q{x+w*.56},{y-h*.98} {x+w*.53},{y-h*.64} Q{x+w*.54},{y-h*.37} {x-w*.43},{y-h*.4} Z"
  self.region(d,"leaf",(x,y-h*.67))
  self.line(f"M{x},{y-h*.1} L{x+1},{y-h*.55} M{x+1},{y-h*.38} L{x-w*.18},{y-h*.57}",True)
  if self.style!="B": self.line(f"M{x-w*.3},{y-h*.66} L{x-w*.15},{y-h*.72} L{x+w*.06},{y-h*.66}",True)
 def svg(self):
  bg=f'<rect width="640" height="400" fill="{self.p["paper"]}"/>'
  fills=[]
  for i,(d,c,seed) in enumerate(self.fills):
   fills.append(f'<path class="region" data-seed="{seed[0]},{seed[1]}" d="{d}" fill="{c}"/>')
  strokes=[]
  for d,phase in self.strokes:
   width = (1.35 if phase=="detail" else (2.6 if self.style!="B" else 3.0))
   strokes.append(f'<path class="ink" data-phase="{phase}" d="{d}" fill="none" stroke="{self.p["ink"]}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"/>')
  return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 400" role="img">'+bg+'<g class="fills">'+"".join(fills)+'</g><g class="strokes">'+"".join(strokes)+'</g></svg>'

def start(style):
 d=Drawing(style)
 d.region("M0,0 H640 V235 H0 Z","sky",(300,55),False)
 d.region("M0,218 L110,207 L201,218 L340,199 L480,215 L640,200 V400 H0 Z","ground",(280,340),False)
 # Different proportions/camera, not a palette substitution.
 hx,hy,hw,hh = {"A":(367,139,151,123),"B":(222,151,191,133),"C":(377,144,155,119)}[style]
 d.line(f"M0,218 L110,207 L201,218 M{hx+hw},215 L640,200")
 road = f"M0,400 L83,400 L{hx-15},{hy+hh+8} L{hx-47},{hy+hh+3} Z" if style!="C" else f"M0,400 L116,400 Q120,330 {hx-11},{hy+hh+9} L{hx-44},{hy+hh+4} Q153,306 0,366 Z"
 d.region(road,"paper",(70,360))
 d.poly([(hx,hy),(hx+hw,hy),(hx+hw,hy+hh),(hx,hy+hh)],"brick")
 d.poly([(hx+hw,hy),(hx+hw+42,hy-18),(hx+hw+42,hy+hh-17),(hx+hw,hy+hh)],"roof")
 d.poly([(hx-13,hy),(hx+hw*.45,hy-65),(hx+hw+42,hy-18),(hx+hw,hy)],"roof")
 # Door and water outlet are distinct; no invented bridge, path or stair.
 d.poly([(hx+28,hy+hh),(hx+28,hy+52),(hx+64,hy+52),(hx+64,hy+hh)],"deep")
 d.poly([(hx+hw-34,hy+hh),(hx+hw-34,hy+hh-18),(hx+hw-9,hy+hh-18),(hx+hw-9,hy+hh)],"deep")
 sx=hx+hw-23; sy=hy+hh
 d.region(f"M{sx-10},{sy} Q{sx-8},{sy+45} 548,350 L590,400 H625 L580,350 Q{sx+15},{sy+45} {sx+11},{sy} Z","water",(545,365))
 for x,y,w,h in ([(42,252,119,160),(135,237,88,140),(262,232,69,115),(604,246,91,166)] if style=="A" else [(51,254,120,178),(142,238,91,135),(577,286,154,247)] if style=="B" else [(45,240,105,140),(172,225,82,132),(284,230,59,106),(603,242,87,148)]):
  d.tree(x,y,w,h)
 # Broken brick marks rather than a uniform wallpaper.
 for x,y in [(hx+10,hy+25),(hx+77,hy+44),(hx+97,hy+79),(hx+73,hy+106)]:
  d.line(f"M{x},{y} h19 m-9,0 v8",True)
 d.line(f"M{sx+2},{sy+20} Q{sx+3},313 551,365 M540,370 l23,7 M565,390 l14,4",True)
 d.line(f"M105,352 l18,-4 M196,312 l15,-3 M297,287 l11,-2",True)
 return d

def props(d,ox=0,oy=0):
 # Initial-state objects on dry floor, never across the spring channel.
 lx, by, fx, kx = 130, 390, 435, 79
 d.region(f"M{lx},349 l3,-41 h35 l4,41 Z","light",(lx+14,311),True,True)
 d.line(f"M{lx+7},308 v-12 q14,-20 27,0 v12 M{lx+11},319 h19 M{lx+11},319 v20 h19 v-20",True)
 d.region(f"M{by},353 v-39 l10,-10 v-17 h17 v17 l10,10 v39 Z","water",(by+15,317),True,True)
 d.line(f"M{by+8},288 h21 M{by+8},326 h20",True)
 d.region(f"M{fx},350 q-6,-27 26,-28 q31,2 25,28 Z","light",(fx+23,322),True,True)
 d.line(f"M{fx+10},328 l8,8 M{fx+26},327 l8,8",True)
 d.line(f"M{kx+14},359 a7,7 0 1,0 -14,0 a7,7 0 1,0 14,0 l27,2 v7 m-10,-8 v8 M{kx+9},367 l-2,19 h25 v-7 m-7,7 v-7",True)

def building(style):
 d=Drawing(style)
 vx,vy={"A":(285,147),"B":(347,130),"C":(235,154)}[style]
 d.poly([(0,0),(640,0),(vx+175,vy),(vx-170,vy)],"brick")
 d.poly([(0,0),(vx-170,vy),(vx-170,vy+118),(0,400)],"roof")
 d.poly([(640,0),(vx+175,vy),(vx+175,vy+118),(640,400)],"ground")
 d.poly([(0,400),(vx-170,vy+118),(vx+175,vy+118),(640,400)],"paper")
 # A broad spring/stone basin rather than the current unidentified blue rectangle.
 bx= vx-72
 if style=="C": basin=f"M{bx-30},218 Q{bx-40},176 {bx+70},173 Q{bx+166},175 {bx+160},219 L{bx+142},255 H{bx-15} Z"
 else: basin=f"M{bx-30},210 L{bx+6},175 H{bx+130} L{bx+166},210 L{bx+140},255 H{bx-8} Z"
 d.region(basin,"steel",(vx,222))
 d.region(f"M{bx-11},210 L{bx+15},191 H{bx+120} L{bx+143},210 L{bx+126},232 H{bx+2} Z","water",(vx,214))
 d.line(f"M{bx+12},219 l53,-3 m15,0 h26",True)
 # Channel to the lower edge; two outflow pipes are not shown in this room study.
 d.region(f"M{bx+45},255 L{bx+78},255 L{bx+81},400 H{bx-6} Z","water",(bx+45,340))
 # Ground objects are deliberately away from the flowing channel.
 props(d,70 if style=="C" else 0,14 if style=="B" else 0)
 for y in (52,85,116):
  d.line(f"M{vx-115},{y} h85 m18,0 h90",True)
 d.line(f"M{vx-64},53 v20 M{vx+48},86 v19 M{vx-7},116 v19",True)
 d.line(f"M14,370 L{vx-155},{vy+119} M620,370 L{vx+160},{vy+119}",True)
 return d

def grate(style):
 d=Drawing(style)
 d.region("M0,0 H640 V400 H0 Z","ground",(25,50),False)
 if style=="A":
  d.region("M0,0 H640 V92 L540,115 L446,100 L340,130 L225,110 L112,140 L0,109 Z","leaf",(50,70))
  bed="M277,0 H355 L344,104 L314,164 L285,201 L252,191 L282,128 Z"
  frame=[(184,218),(393,194),(496,312),(186,351)]
 elif style=="B":
  d.region("M0,0 H640 V79 L535,116 L411,88 L275,105 L117,88 L0,130 Z","deep",(30,70))
  bed="M465,0 H555 L492,100 L407,158 L350,210 L308,193 L400,122 Z"
  frame=[(139,228),(377,189),(537,326),(143,378)]
 else:
  d.region("M0,0 H640 V82 Q450,142 309,101 Q120,147 0,107 Z","leaf",(35,60))
  bed="M287,0 H369 Q379,88 302,165 L267,207 L226,195 Q328,90 287,0 Z"
  frame=[(196,218),(402,200),(477,307),(186,330)]
 d.region(bed,"paper",(318,60))
 d.line("M0,187 L56,164 L105,181 M502,177 L560,148 L640,164")
 d.poly(frame,"steel")
 # Inset black void is contained by the concrete surround. Grate is horizontal.
 a,b,c,e=frame
 inner=[(a[0]+20,a[1]+9),(b[0]-12,b[1]+14),(c[0]-28,c[1]-13),(e[0]+22,e[1]-18)]
 d.poly(inner,"deep")
 # Perspective-correctish bars interpolate between the two sloping edges.
 for t in (.12,.25,.38,.51,.64,.77,.90):
  x1=inner[0][0]+(inner[1][0]-inner[0][0])*t; y1=inner[0][1]+(inner[1][1]-inner[0][1])*t
  x2=inner[3][0]+(inner[2][0]-inner[3][0])*t; y2=inner[3][1]+(inner[2][1]-inner[3][1])*t
  d.line(f"M{x1},{y1} L{x2},{y2}")
 d.line(f"M{inner[0][0]},{inner[0][1]+25} L{inner[1][0]+22},{inner[1][1]+25}",True)
 for x,y in [(91,286),(536,259),(120,161),(422,135),(319,88),(461,365)]:
  d.line(f"M{x},{y} l10,-5 l10,7 l-11,4 Z",True)
 d.line(f"M{a[0]+14},{a[1]+3} l8,5 M{b[0]-5},{b[1]+9} l6,5 M{c[0]-15},{c[1]-4} l6,4",True)
 d.line(f"M{inner[0][0]+85},{inner[0][1]+49} h14 v9 h-14 Z",True)
 return d

def build():
 svgs={}
 for key in PALETTES:
  for room,fn in zip(ROOMS,[start,building,grate]):
   drawing=fn(key); svg=drawing.svg(); filename=f"{key}_{room}.svg"
   (HERE/filename).write_text(svg+"\n",encoding="utf-8")
   svgs[key+"_"+room]=svg
 board=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1980 1430"><rect width="1980" height="1430" fill="#ece9df"/>',
        '<text x="25" y="36" font-family="sans-serif" font-size="25" fill="#263b38">CAR V1 / Estudios originales de dirección — PROPUESTAS, NO PRODUCCIÓN</text>']
 for col,key in enumerate(PALETTES):
  x=20+col*650
  board.append(f'<text x="{x}" y="76" font-family="sans-serif" font-size="24" fill="#263b38">{key} / {PALETTES[key]["name"]}</text>')
  for row,room in enumerate(ROOMS):
   y=111+row*437
   board.append(f'<text x="{x}" y="{y-10}" font-family="sans-serif" font-size="18" fill="#263b38">{room} · estado inicial</text>')
   board.append(svgs[key+"_"+room].replace('<svg xmlns="http://www.w3.org/2000/svg" viewBox=',f'<svg x="{x}" y="{y}" width="640" height="400" viewBox='))
 board.append("</svg>")
 (HERE/"comparison.svg").write_text("".join(board)+"\n",encoding="utf-8")
 # Four static stage studies: storyboard, not evidence of animation timing.
 ET.register_namespace("", "http://www.w3.org/2000/svg")
 ns={"s":"http://www.w3.org/2000/svg"}
 for frame in range(1,5):
  svg=ET.fromstring(svgs["A_LOC_START"])
  fills=svg.find("s:g[@class='fills']",ns); strokes=svg.find("s:g[@class='strokes']",ns)
  for i,p in enumerate(list(fills)):
   if frame<3 or (frame==3 and i>=int(len(fills)*.6)): fills.remove(p)
  contours=[p for p in list(strokes) if p.attrib.get("data-phase")=="contour"]
  details=[p for p in list(strokes) if p.attrib.get("data-phase")=="detail"]
  if frame==1:
   for p in details+contours[int(len(contours)*.55):]: strokes.remove(p)
  elif frame==2:
   for p in details[int(len(details)*.6):]: strokes.remove(p)
  (HERE/f"sequence_{frame}.svg").write_text(ET.tostring(svg,encoding="unicode")+"\n",encoding="utf-8")
 payload=json.dumps(svgs,ensure_ascii=False)
 html=HTML.replace("__SVG_DATA__",payload)
 (HERE/"review.html").write_text(html,encoding="utf-8")
 print("Generated 9 original SVG studies, comparison.svg and review.html.")

def capture(godot):
 art=ROOT/"07_godot_open_adventure/godot/data/art_ch01.json"
 renderer=ROOT/"07_godot_open_adventure/godot/src/render/room_illustration.gd"
 target=HERE/"audit_renderer.png"
 with tempfile.TemporaryDirectory(prefix="CAR-ART-001-capture-") as temp:
  t=Path(temp)
  shutil.copy2(art,t/"art.json"); shutil.copy2(renderer,t/"room_illustration.gd")
  (t/"project.godot").write_text('config_version=5\n[application]\nconfig/name="CAR art read-only capture"\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n')
  gd='''extends SceneTree
const Renderer = preload("res://room_illustration.gd")
func _initialize():
 var art = JSON.parse_string(FileAccess.get_file_as_string("res://art.json"))
 var ids = art.scenes.keys()
 ids.sort()
 var sheet = Image.create(576, 480, false, Image.FORMAT_RGBA8)
 sheet.fill(Color(0.05,0.05,0.08))
 for i in ids.size():
  var picture = Renderer.from_dict(art.scenes[ids[i]], art.meta.palette).render_image()
  picture.resize(192,120,Image.INTERPOLATE_NEAREST)
  sheet.blit_rect(picture,Rect2i(0,0,192,120),Vector2i((i%3)*192,int(i/3)*120))
 var result = sheet.save_png(TARGET)
 if result != OK: quit(1)
 else:
  print("PASS: isolated current-renderer capture; %d scenes" % ids.size())
  quit(0)
'''.replace("TARGET",json.dumps(target.as_posix()))
  (t/"capture.gd").write_text(gd)
  subprocess.run([godot,"--headless","--path",str(t),"--editor","--quit"],check=True,stdout=subprocess.DEVNULL)
  subprocess.run([godot,"--headless","--path",str(t),"--script","res://capture.gd"],check=True)
 # Rasterize authored vectors locally with Godot, not a browser.
 with tempfile.TemporaryDirectory(prefix="CAR-ART-001-svg-") as temp:
  t=Path(temp)
  (t/"project.godot").write_text('config_version=5\n[application]\nconfig/name="CAR SVG evidence"\n')
  paths=[str(p).replace("\\","/") for p in list(HERE.glob("[ABC]_LOC_*.svg"))+list(HERE.glob("sequence_[1-4].svg"))]
  code='''extends SceneTree
func _initialize():
 for file in FILES:
  var image = Image.new()
  var error = image.load_svg_from_string(FileAccess.get_file_as_string(file))
  if error != OK:
   printerr("SVG parse failed: " + file)
   quit(1)
   return
  image.save_png(file.replace(".svg",".png"))
 print("PASS: nine studies and four storyboard frames rasterized by Godot")
 quit(0)
'''.replace("FILES",json.dumps(paths))
  (t/"svg.gd").write_text(code)
  subprocess.run([godot,"--headless","--path",str(t),"--script","res://svg.gd"],check=True)
 from PIL import Image, ImageDraw, ImageFont
 board=Image.new("RGB",(1980,1430),"#ece9df"); pen=ImageDraw.Draw(board)
 titlefont=ImageFont.truetype("arial.ttf",size=27); labelfont=ImageFont.truetype("arial.ttf",size=23)
 pen.text((20,16),"CAR V1 / Estudios originales - PROPUESTAS, NO PRODUCCION",fill="#263b38",font=titlefont)
 for col,key in enumerate(PALETTES):
  x=20+col*650
  pen.text((x,53),key+" / "+PALETTES[key]["name"],fill="#263b38",font=labelfont)
  for row,room in enumerate(ROOMS):
   y=111+row*437
   pen.text((x,y-26),room+" / estado inicial",fill="#263b38",font=ImageFont.truetype("arial.ttf",size=18))
   png=HERE/(key+"_"+room+".png")
   picture=Image.open(png).convert("RGB");board.paste(picture,(x,y))
   png.unlink() # Only our just-generated nine intermediate renders.
 board.save(HERE/"comparison.png")
 sequence=Image.new("RGB",(1320,910),"#ece9df"); pen=ImageDraw.Draw(sequence)
 labels=["1 / Contornos (fragmento)", "2 / Detalles secundarios", "3 / Regiones en relleno", "4 / Composicion final"]
 for i in range(4):
  x=10+(i%2)*650; y=45+(i//2)*445
  pen.text((x,y-30),labels[i],font=labelfont,fill="#263b38")
  png=HERE/f"sequence_{i+1}.png"
  sequence.paste(Image.open(png).convert("RGB"),(x,y));png.unlink()
 sequence.save(HERE/"sequence.png")
 data=json.loads(art.read_text(encoding="utf-8-sig"))
 sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
 ev={"baseline":"2dfaa96bc6af7ab2ed8f6aab24e33c45b183acaf","method":"Exact current renderer and art copied into a disposable Godot project; no production execution/files overwritten.",
     "godot":subprocess.check_output([godot,"--version"],text=True).strip(),
     "renderer_sha256":sha(renderer),"art_sha256":sha(art),"audit_png_sha256":sha(target),
     "tracked_contact_sha256":sha(ROOT/"07_godot_open_adventure/godot/captures/scenes.png"),
     "audit_matches_tracked_contact_bytes":sha(target)==sha(ROOT/"07_godot_open_adventure/godot/captures/scenes.png"),
     "sorted_scene_order":sorted(data["scenes"]),
     "scene_stats":{k:{"lines":len(v["lines"]),"segments":sum(len(l["points"])-1 for l in v["lines"]),"fills":len(v["fills"])} for k,v in sorted(data["scenes"].items())}}
 (HERE/"audit_evidence.json").write_text(json.dumps(ev,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 print(json.dumps(ev,indent=2))

HTML=r'''<!doctype html>
<html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CAR-ART-001 · Mesa de revisión</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#ece9df;color:#263b38;font:16px/1.5 system-ui,sans-serif}main{max-width:1440px;margin:auto;padding:28px}h1{font-size:32px;letter-spacing:-1px;margin:3px 0 8px}h2{font-size:22px}small,.muted{color:#53665d}.tag{font-size:12px;letter-spacing:2px}button,select,input{font:inherit}button,select{border:1px solid #8b9b8c;background:#fffaf0;color:#263b38;border-radius:4px;padding:8px 12px}button{cursor:pointer}button:hover{background:#dbe3d7}button:focus-visible,select:focus-visible,input:focus-visible{outline:3px solid #bc7956;outline-offset:3px}.controls{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:16px 0}.viewer{display:grid;grid-template-columns:minmax(0,2fr) minmax(260px,1fr);gap:24px}.stage{border:1px solid #899286;aspect-ratio:8/5;background:#f1e8d2}.stage svg{display:block;width:100%;height:100%}aside{padding:8px 0}#phase{font-size:22px;font-weight:650}progress{width:100%;accent-color:#568c91}label{display:inline-flex;align-items:center;gap:6px}.board{display:block;width:100%;background:#ece9df}.audit{max-width:900px;image-rendering:pixelated;width:100%}footer{border-top:1px solid #abb7a8;margin-top:24px;padding:16px 0}.note{background:#e3e3d4;padding:12px;border-left:3px solid #718e70}.legend{display:flex;gap:22px;flex-wrap:wrap}a{color:#335e59}@media(max-width:800px){.viewer{grid-template-columns:1fr}main{padding:16px}h1{font-size:25px}}
</style>
<main><div class="tag">CAR-ART-001 / DECISION GATE / ESTUDIOS ORIGINALES</div>
<h1>Una aventura que se dibuja delante de ti</h1>
<p>Tres tratamientos, tres salas y una secuencia visible de contorno → detalle → relleno. Ninguna propuesta está aprobada para producción.</p>
<div class="controls">
<label>Tratamiento <select id="style"><option value="A">A · Tinta de expedición</option><option value="B">B · Luz mineral</option><option value="C">C · Línea solar</option></select></label>
<label>Sala <select id="room"><option>LOC_START</option><option>LOC_BUILDING</option><option>LOC_GRATE</option></select></label>
</div>
<div class="viewer"><div id="stage" class="stage"></div><aside><div id="phase">Composición final</div><progress id="progress" max="1" value="1"></progress>
<p id="brief"></p><p class="note">Prototipo web aislado. El relleno radial se recorta a regiones SVG cerradas; <b>no es flood fill</b>. No demuestra rendimiento ni integración en Godot.</p>
<div class="controls"><button id="play">Reproducir</button><button id="pause">Pausar</button><button id="skip">Omitir / final</button></div>
<div class="controls"><label>Duración <input id="duration" type="range" min="2" max="9" step=".5" value="5.5"><span id="durationText">5,5 s</span></label></div>
<div class="controls"><label>Velocidad <select id="speed"><option value="1">1×</option><option value="2">2×</option><option value="4">4×</option></select></label>
<label>Trazo <select id="trace"><option value="interpolated">Interpolado</option><option value="commands">Comandos completos</option></select></label>
<label>Relleno <select id="fill"><option value="radial">Región progresiva</option><option value="instant">Región instantánea</option></select></label></div>
<small>La página abre terminada y requiere reproducción explícita. Cambiar tratamiento/sala cancela la secuencia anterior. Omitir muestra el final exacto; el prototipo no captura el teclado del parser.</small>
</aside></div>
<h2>Comparativa de nueve composiciones</h2>
<p>Comparar primero encuadre y siluetas; después paleta. BUILDING y GRATE representan solo el estado inicial.</p>
<img class="board" src="comparison.svg" alt="Nueve propuestas: tres tratamientos para START, BUILDING y GRATE">
<h2>Evidencia del renderer actual</h2>
<p>Captura de las once ilustraciones con el renderer actual, ejecutado en un proyecto temporal aislado. Orden por filas: BUILDING, CLIFF, FOREST; GRATE, HILL, LEDGE; ROADEND, SEWER, SLIT; START, VALLEY.</p>
<img class="audit" src="audit_renderer.png" alt="Hoja de las once ilustraciones actuales sin modificar">
<footer><a href="../CHANGE.md">Informe, procedencia y requisitos para ingeniería</a> · V1 vectorial contemporánea. La elección corresponde al responsable humano.</footer></main>
<script>
const DATA=__SVG_DATA__;
const $=id=>document.getElementById(id);
let elapsed=1, running=false, last=0, paths=[], regions=[], frame=null;
function stop(){running=false;if(frame!==null)cancelAnimationFrame(frame);frame=null;}
const clamp=x=>Math.max(0,Math.min(1,x));
const BRIEFS={
 LOC_START:"Camino, casita de ladrillo, bosque y arroyo hacia la barranca. El agua sale de un hueco distinto de la puerta. El encuadre no representa una brújula ni añade salidas.",
 LOC_BUILDING:"Interior del pozo/manantial. Llaves, lámpara apagada, botella de agua y comida en el suelo: estado inicial. En producción estos elementos tendrían que reflejar el estado de partida.",
 LOC_GRATE:"Depresión de tierra desnuda con reja horizontal en hormigón; cauce seco. Estado inicial cerrado. No se anticipa ninguna escalera o contenido bajo la reja."
};
function load(){
 stop();elapsed=1;
 $("stage").innerHTML=DATA[$("style").value+"_"+$("room").value];
 const svg=$("stage").querySelector("svg");
 const ns="http://www.w3.org/2000/svg";const defs=document.createElementNS(ns,"defs");svg.prepend(defs);
 paths=Array.from(svg.querySelectorAll(".ink")).map(p=>({p,length:p.getTotalLength(),phase:p.dataset.phase}));
 regions=Array.from(svg.querySelectorAll(".region")).map((p,i)=>{
  const clip=document.createElementNS(ns,"clipPath");clip.id="region-reveal-"+i;clip.setAttribute("clipPathUnits","userSpaceOnUse");
  const circle=document.createElementNS(ns,"circle");const seed=p.dataset.seed.split(",");circle.setAttribute("cx",seed[0]);circle.setAttribute("cy",seed[1]);clip.append(circle);defs.append(clip);
  p.setAttribute("clip-path","url(#"+clip.id+")");return {p,circle};
 });
 $("brief").textContent=BRIEFS[$("room").value];render(1);
}
function strokePhase(name,fraction){
 const list=paths.filter(x=>x.phase===name);const total=list.reduce((a,x)=>a+x.length,0);let left=clamp(fraction)*total;
 for(const x of list){const q=clamp(left/Math.max(.001,x.length));x.p.style.strokeDasharray=x.length+" "+x.length;
  x.p.style.strokeDashoffset=x.length*(1-($("trace").value==="commands"?(q>=1?1:0):q));left-=x.length;}
}
function render(t){
 elapsed=clamp(t);strokePhase("contour",t/.45);strokePhase("detail",(t-.45)/.23);
 const f=clamp((t-.68)/.32);
 regions.forEach((x,i)=>{
  const q=clamp(f*regions.length-i);
  x.circle.setAttribute("r", $("fill").value==="instant"?(q>0?900:0):q*900);
 });
 $("progress").value=t;
 $("phase").textContent=t>=1?"Composición final":t<.45?"1 / Contornos":t<.68?"2 / Detalles secundarios":"3 / Relleno por regiones";
}
function tick(now){if(!running)return;const delta=(now-last)/1000;last=now;render(elapsed+delta*Number($("speed").value)/Number($("duration").value));if(elapsed>=1){running=false;return}frame=requestAnimationFrame(tick)}
$("play").onclick=()=>{stop();render(0);running=true;last=performance.now();frame=requestAnimationFrame(tick)};
$("pause").onclick=()=>{if(running){stop()}else if(elapsed<1){running=true;last=performance.now();frame=requestAnimationFrame(tick)}};
$("skip").onclick=()=>{stop();render(1)};
$("duration").oninput=()=>{$("durationText").textContent=$("duration").value.replace(".",",")+" s"};
$("style").onchange=load;$("room").onchange=load;
$("trace").onchange=()=>render(elapsed);$("fill").onchange=()=>render(elapsed);
load();
</script></html>
'''

if __name__=="__main__":
 parser=argparse.ArgumentParser();parser.add_argument("--godot");args=parser.parse_args()
 build()
 if args.godot: capture(args.godot)
