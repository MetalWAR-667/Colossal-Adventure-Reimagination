#!/usr/bin/env python3
"""Phase A — minimal rendering fixture.

Pattern A (correct draw.io convention): <object id="NODE_A"> wrapper carries
the id; edge references that id.
Pattern B (Mission 003 bug): id on the inner mxCell; object wrapper has no id;
edge references the inner id.

Export to SVG/PNG and verify: A renders a connector, B does not.
"""
import xml.etree.ElementTree as ET
from pathlib import Path

mx = ET.Element("mxfile", {"host": "fixture", "type": "device", "version": "24.7.0"})
diag = ET.SubElement(mx, "diagram", {"id": "fix1", "name": "Fixture"})
model = ET.SubElement(diag, "mxGraphModel", {
    "dx": "800", "dy": "600", "grid": "1", "gridSize": "10", "guides": "1",
    "tooltips": "1", "connect": "1", "arrows": "1", "fold": "1", "page": "1",
    "pageScale": "1", "pageWidth": "850", "pageHeight": "400", "math": "0", "shadow": "0"})
root = ET.SubElement(model, "root")
ET.SubElement(root, "mxCell", {"id": "0"})
ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})

STYLE_BOX = "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#333333;"

# --- Pattern A: id on the <object> wrapper (draw.io convention) ---
for oid, x in (("NODE_A", 40), ("NODE_B", 400)):
    obj = ET.SubElement(root, "object", {"id": oid, "label": f"<b>{oid}</b>"})
    cell = ET.SubElement(obj, "mxCell", {"style": STYLE_BOX, "vertex": "1", "parent": "1"})
    ET.SubElement(cell, "mxGeometry", {"x": str(x), "y": "80", "width": "200",
                                       "height": "80", "as": "geometry"})

# Correct edge: references the OBJECT ids — should render.
e1 = ET.SubElement(root, "mxCell", {
    "id": "EDGE_GOOD",
    "style": "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;html=1;"
             "endArrow=block;endFill=1;strokeWidth=2.5;strokeColor=#000000;"
             "exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;",
    "edge": "1", "parent": "1", "source": "NODE_A", "target": "NODE_B",
    "value": "east &amp;rarr; visible arrow"})
ET.SubElement(e1, "mxGeometry", {"relative": "1", "as": "geometry"})

# --- Pattern B: id on the inner mxCell, object has no id (Mission 003 bug) ---
obj = ET.SubElement(root, "object", {"label": "<b>NODE_C</b>"})
cell = ET.SubElement(obj, "mxCell", {"id": "NODE_C", "style": STYLE_BOX,
                                     "vertex": "1", "parent": "1"})
ET.SubElement(cell, "mxGeometry", {"x": "40", "y": "240", "width": "200",
                                   "height": "80", "as": "geometry"})
obj = ET.SubElement(root, "object", {"label": "<b>NODE_D</b>"})
cell = ET.SubElement(obj, "mxCell", {"id": "NODE_D", "style": STYLE_BOX,
                                     "vertex": "1", "parent": "1"})
ET.SubElement(cell, "mxGeometry", {"x": "400", "y": "240", "width": "200",
                                   "height": "80", "as": "geometry"})

# Broken edge: references the inner-cell ids — expected NOT to render.
e2 = ET.SubElement(root, "mxCell", {
    "id": "EDGE_BROKEN",
    "style": "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=block;"
             "endFill=1;strokeWidth=2.5;strokeColor=#CC0000;"
             "exitX=1;exitY=0.5;entryX=0;entryY=0.5;",
    "edge": "1", "parent": "1", "source": "NODE_C", "target": "NODE_D",
    "value": "this arrow should vanish"})
ET.SubElement(e2, "mxGeometry", {"relative": "1", "as": "geometry"})

ET.indent(mx, space="  ")
out = Path("output/pilot/_fixture.drawio")
ET.ElementTree(mx).write(out, encoding="utf-8", xml_declaration=True)
print("wrote", out)
