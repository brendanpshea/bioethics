"""
Rebuild styles/case-reference.docx with journal-like styling.

Strategy: start from the pandoc-default reference docx (already present),
parse word/styles.xml, modify built-in styles (Title, Heading1, Normal, ...)
and append our custom styles (CaseGlance, ContextBox, KeyTerm, PullQuote,
CalloutNote). Re-zip in place.

Run:  python styles/build_reference_docx.py
"""

from __future__ import annotations
import shutil, zipfile, subprocess, sys
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
REF = ROOT / "styles" / "case-reference.docx"

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
ET.register_namespace("w", W)
NS = {"w": W}

def regenerate_base():
    """Re-extract pandoc's default reference.docx as our starting point."""
    print("Regenerating base reference docx from pandoc default...")
    with REF.open("wb") as f:
        subprocess.run(
            ["pandoc", "--print-default-data-file", "reference.docx"],
            stdout=f, check=True,
        )

def read_styles_xml() -> bytes:
    with zipfile.ZipFile(REF, "r") as z:
        return z.read("word/styles.xml")

def write_styles_xml(data: bytes):
    tmp = REF.with_suffix(".tmp.docx")
    with zipfile.ZipFile(REF, "r") as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            payload = data if item.filename == "word/styles.xml" else zin.read(item.filename)
            zout.writestr(item, payload)
    shutil.move(tmp, REF)

def w(tag): return f"{{{W}}}{tag}"

def find_style(root, style_id):
    for s in root.findall(w("style"), NS):
        if s.get(w("styleId")) == style_id:
            return s
    return None

def ensure_child(parent, tag):
    el = parent.find(w(tag), NS)
    if el is None:
        el = ET.SubElement(parent, w(tag))
    return el

def set_attr(el, name, value):
    el.set(w(name), value)

def clear_and_set_rpr(style, **kwargs):
    """Replace rPr (run properties) on a style. kwargs: bold, italic, sz (half-pt), color, smallCaps, font."""
    rpr = ensure_child(style, "rPr")
    for child in list(rpr):
        rpr.remove(child)
    if kwargs.get("bold"):
        ET.SubElement(rpr, w("b"))
    if kwargs.get("italic"):
        ET.SubElement(rpr, w("i"))
    if kwargs.get("smallCaps"):
        ET.SubElement(rpr, w("smallCaps"))
    if "sz" in kwargs:
        el = ET.SubElement(rpr, w("sz"));    set_attr(el, "val", str(kwargs["sz"]))
        el = ET.SubElement(rpr, w("szCs"));  set_attr(el, "val", str(kwargs["sz"]))
    if "color" in kwargs:
        el = ET.SubElement(rpr, w("color")); set_attr(el, "val", kwargs["color"])
    if "font" in kwargs:
        el = ET.SubElement(rpr, w("rFonts"))
        for k in ("ascii", "hAnsi", "cs"):
            set_attr(el, k, kwargs["font"])

def clear_and_set_ppr(style, *, jc=None, spacing=None, ind=None, border_bottom=None, shading=None, keepNext=False):
    ppr = ensure_child(style, "pPr")
    for child in list(ppr):
        ppr.remove(child)
    if spacing:
        el = ET.SubElement(ppr, w("spacing"))
        for k, v in spacing.items():
            set_attr(el, k, str(v))
    if ind:
        el = ET.SubElement(ppr, w("ind"))
        for k, v in ind.items():
            set_attr(el, k, str(v))
    if jc:
        el = ET.SubElement(ppr, w("jc")); set_attr(el, "val", jc)
    if border_bottom:
        pbdr = ET.SubElement(ppr, w("pBdr"))
        bot = ET.SubElement(pbdr, w("bottom"))
        for k, v in border_bottom.items():
            set_attr(el := bot, k, str(v))
    if shading:
        el = ET.SubElement(ppr, w("shd"))
        for k, v in shading.items():
            set_attr(el, k, v)
    if keepNext:
        ET.SubElement(ppr, w("keepNext"))

# ---------- main ----------

regenerate_base()
xml_bytes = read_styles_xml()
root = ET.fromstring(xml_bytes)

# --- Typography & palette ---
# Body: Cambria (ubiquitous on Windows). Headings: EB Garamond (open-source,
# journal-classic). If EB Garamond isn't installed, Word falls back gracefully.
BODY_FONT = "Cambria"
HEAD_FONT = "EB Garamond"

# Palette: deep burgundy accent for title/H1, muted teal for H2, warm sienna
# for inline key terms. Inspired by university press journals.
INK      = "1a1a1a"
MUTED    = "555555"
BURGUNDY = "6b1f2b"   # title, H1, H1 rule, KeyTerm
TEAL     = "1f4e5f"   # H2, ContextBox accent
SIENNA   = "8a4b1f"   # alt accent
CREAM    = "F7F1E3"   # CaseGlance fill
CREAM_BD = "B8A77A"   # CaseGlance border
BLUEGREY = "EAF2F4"   # ContextBox fill

# Body font for the whole document: serif, 11pt
normal = find_style(root, "Normal")
if normal is not None:
    clear_and_set_rpr(normal, font=BODY_FONT, sz=22, color=INK)  # 22 half-pt = 11pt
    clear_and_set_ppr(normal, jc="both",
                      spacing={"after": "120", "line": "288", "lineRule": "auto"})

# Title: large display Garamond, burgundy, centered, with rule below
title = find_style(root, "Title")
if title is not None:
    clear_and_set_rpr(title, font=HEAD_FONT, sz=48, bold=True, color=BURGUNDY)  # 24pt
    clear_and_set_ppr(title, jc="center",
                      spacing={"before": "0", "after": "120"},
                      border_bottom={"val": "single", "sz": "8", "space": "4", "color": BURGUNDY})

subtitle = find_style(root, "Subtitle")
if subtitle is not None:
    clear_and_set_rpr(subtitle, font=HEAD_FONT, sz=26, italic=True, color=MUTED)  # 13pt
    clear_and_set_ppr(subtitle, jc="center",
                      spacing={"before": "120", "after": "240"})

# Author / Date: small caps, centered, muted
for sid in ("Author", "Date"):
    s = find_style(root, sid)
    if s is not None:
        clear_and_set_rpr(s, font=HEAD_FONT, sz=20, color=MUTED, smallCaps=True)  # 10pt
        clear_and_set_ppr(s, jc="center", spacing={"after": "60"})

# Heading 1: small-caps burgundy with hairline rule below
h1 = find_style(root, "Heading1")
if h1 is not None:
    clear_and_set_rpr(h1, font=HEAD_FONT, sz=30, bold=True, smallCaps=True, color=BURGUNDY)  # 15pt
    clear_and_set_ppr(h1,
                      spacing={"before": "360", "after": "120"},
                      border_bottom={"val": "single", "sz": "4", "space": "2", "color": BURGUNDY},
                      keepNext=True)

# Heading 2: bold italic teal
h2 = find_style(root, "Heading2")
if h2 is not None:
    clear_and_set_rpr(h2, font=HEAD_FONT, sz=26, bold=True, italic=True, color=TEAL)  # 13pt
    clear_and_set_ppr(h2, spacing={"before": "240", "after": "80"}, keepNext=True)

# Heading 3
h3 = find_style(root, "Heading3")
if h3 is not None:
    clear_and_set_rpr(h3, font=HEAD_FONT, sz=22, bold=True, color=INK)  # 11pt
    clear_and_set_ppr(h3, spacing={"before": "180", "after": "60"}, keepNext=True)

# Caption: small italic
caption = find_style(root, "Caption")
if caption is not None:
    clear_and_set_rpr(caption, font=BODY_FONT, sz=18, italic=True, color=MUTED)  # 9pt
    clear_and_set_ppr(caption, jc="center", spacing={"before": "60", "after": "180"})

# Block Quote: indented italic
bq = find_style(root, "BlockText")
if bq is None:
    bq = find_style(root, "Quote")
if bq is not None:
    clear_and_set_rpr(bq, font=BODY_FONT, sz=22, italic=True, color="333333")
    clear_and_set_ppr(bq, jc="both",
                      ind={"left": "720", "right": "720"},
                      spacing={"before": "120", "after": "120", "line": "288", "lineRule": "auto"})

# ---------- custom styles ----------

def add_paragraph_style(style_id, name, *, based_on="Normal", rpr=None, ppr=None):
    """Add a new paragraph style if not already present."""
    if find_style(root, style_id) is not None:
        return
    s = ET.SubElement(root, w("style"))
    set_attr(s, "type", "paragraph")
    set_attr(s, "styleId", style_id)
    nm = ET.SubElement(s, w("name")); set_attr(nm, "val", name)
    bo = ET.SubElement(s, w("basedOn")); set_attr(bo, "val", based_on)
    nx = ET.SubElement(s, w("next")); set_attr(nx, "val", "Normal")
    ET.SubElement(s, w("qFormat"))
    if ppr:
        clear_and_set_ppr(s, **ppr)
    if rpr:
        clear_and_set_rpr(s, **rpr)

def add_char_style(style_id, name, *, rpr):
    if find_style(root, style_id) is not None:
        return
    s = ET.SubElement(root, w("style"))
    set_attr(s, "type", "character")
    set_attr(s, "styleId", style_id)
    nm = ET.SubElement(s, w("name")); set_attr(nm, "val", name)
    ET.SubElement(s, w("qFormat"))
    clear_and_set_rpr(s, **rpr)

# CaseGlance — the "at a glance" abstract box: cream shading, burgundy rule.
add_paragraph_style(
    "CaseGlance", "CaseGlance",
    rpr={"font": BODY_FONT, "sz": 20, "color": INK},  # 10pt
    ppr={"jc": "left",
         "ind": {"left": "200", "right": "200"},
         "spacing": {"before": "120", "after": "120", "line": "276", "lineRule": "auto"},
         "shading": {"val": "clear", "color": "auto", "fill": CREAM},
         "border_bottom": {"val": "single", "sz": "6", "space": "4", "color": BURGUNDY}},
)

# ContextBox — "background science" sidebar: pale teal tint.
add_paragraph_style(
    "ContextBox", "ContextBox",
    rpr={"font": BODY_FONT, "sz": 20, "color": INK},
    ppr={"jc": "left",
         "ind": {"left": "240", "right": "120"},
         "spacing": {"before": "120", "after": "120", "line": "276", "lineRule": "auto"},
         "shading": {"val": "clear", "color": "auto", "fill": BLUEGREY}},
)

# CalloutNote — generic note callout.
add_paragraph_style(
    "CalloutNote", "CalloutNote",
    rpr={"font": BODY_FONT, "sz": 20, "italic": True, "color": "333333"},
    ppr={"ind": {"left": "240"},
         "spacing": {"before": "120", "after": "120"},
         "shading": {"val": "clear", "color": "auto", "fill": "F5F0EA"}},
)

# PullQuote — large display Garamond italic, burgundy.
add_paragraph_style(
    "PullQuote", "PullQuote",
    rpr={"font": HEAD_FONT, "sz": 28, "italic": True, "color": BURGUNDY},  # 14pt
    ppr={"jc": "center",
         "ind": {"left": "720", "right": "720"},
         "spacing": {"before": "180", "after": "180", "line": "312", "lineRule": "auto"}},
)

# KeyTerm — inline burgundy small-caps bold.
add_char_style(
    "KeyTerm", "KeyTerm",
    rpr={"bold": True, "smallCaps": True, "color": BURGUNDY},
)

# ---------- serialize ----------

body = ET.tostring(root, encoding="UTF-8")
out = b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' + body
write_styles_xml(out)
print(f"Updated {REF}")
