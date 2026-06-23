"""Produce stripped-down, Pressbooks-ready HTML for each chapter.

Reads the already-rendered standalone pages in docs/cases/ (so run a normal
`quarto render` first), extracts just the article body, and writes one clean
folder per chapter to ../pressbooks-export/ (untracked):

    pressbooks-export/
      01-dax-cowart/
        01-dax-cowart.html      # body-only; citations are same-page anchors
        images/diagram-1.png    # Graphviz diagrams rasterized (SVG -> PNG)
      02-tuskegee-guatemala/
        02-tuskegee-guatemala.html
        images/peter_buxtun.jpg
        ...
      _manifest.txt             # chapter order + titles, for importing

Why this exists: the multi-file EPUB rewrites citation links across files
(ch003.xhtml#ref-...) and repeats the whole bibliography in every chapter,
both of which break on Pressbooks import. The standalone pages already use
same-page citation anchors (#ref-...) and per-chapter reference lists, so we
just strip the site chrome and localize the images.

Run: python book/build-pressbooks.py
"""
import os
import shutil
import sys
from bs4 import BeautifulSoup

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DOCS_CASES = os.path.join(ROOT, "docs", "cases")
DOCS_IMAGES = os.path.join(ROOT, "docs", "images")
REPO_IMAGES = os.path.join(ROOT, "images")
OUT = os.path.join(ROOT, "pressbooks-export")

CHAPTERS = [
    "00-introduction", "01-dax-cowart", "02-tuskegee-guatemala",
    "03-alzheimers-fraud", "04-kate-cox-karsan", "05-adriana-smith",
    "06-he-jiankui", "07-noelia-castillo", "08-singapore-healthcare",
    "09-wakefield-mmr", "10-optum-algorithm", "11-skrmetti",
    "12-bennett-xenotransplant",
]


def find_image_source(fname):
    """Locate an image file by name in docs/images, then repo images/."""
    for base in (DOCS_IMAGES, REPO_IMAGES):
        cand = os.path.join(base, fname)
        if os.path.exists(cand):
            return cand
    return None


def process(name):
    src_html = os.path.join(DOCS_CASES, f"{name}.html")
    with open(src_html, encoding="utf-8") as fh:
        soup = BeautifulSoup(fh, "html.parser")

    main = soup.find("main", id="quarto-document-content") or soup.find("main")
    if main is None:
        raise SystemExit(f"No <main> content found in {src_html}")

    chap_dir = os.path.join(OUT, name)
    img_dir = os.path.join(chap_dir, "images")
    n_diagrams = n_photos = 0

    # Pull the title (for <title> + manifest), then drop Quarto's title block
    # so Pressbooks' own chapter-title field isn't duplicated. Keep the
    # subtitle as a small italic line.
    title = name
    subtitle = None
    header = main.find("header", id="title-block-header")
    if header:
        h1 = header.find("h1")
        if h1:
            title = h1.get_text(strip=True)
        sub = header.find(class_="subtitle")
        if sub:
            subtitle = sub.get_text(strip=True)
        header.decompose()

    # Graphviz diagrams render as inline <svg>; WordPress/Pressbooks may strip
    # inline SVG, so swap each for the raster PNG built for the DOCX output.
    figdir = os.path.join(DOCS_CASES, f"{name}_files", "figure-docx")
    for i, svg in enumerate(main.find_all("svg"), 1):
        png = os.path.join(figdir, f"dot-figure-{i}.png")
        if os.path.exists(png):
            os.makedirs(img_dir, exist_ok=True)
            shutil.copy(png, os.path.join(img_dir, f"diagram-{i}.png"))
            img = soup.new_tag("img", src=f"images/diagram-{i}.png")
            img["alt"] = f"Diagram {i}"
            svg.replace_with(img)
            n_diagrams += 1

    # Localize photo <img> (referenced as ../images/foo.jpg). Skip remote URLs.
    for img in main.find_all("img"):
        src = img.get("src", "")
        if not src or src.startswith(("http://", "https://", "data:", "images/")):
            continue
        fname = os.path.basename(src.split("?")[0])
        source = find_image_source(fname)
        if source:
            os.makedirs(img_dir, exist_ok=True)
            shutil.copy(source, os.path.join(img_dir, fname))
            img["src"] = f"images/{fname}"
            n_photos += 1

    # Assemble a minimal, self-contained document.
    body = main.decode_contents()
    sub_html = f'<p class="case-subtitle"><em>{subtitle}</em></p>\n' if subtitle else ""
    doc = (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        f"<title>{title}</title>\n</head>\n<body>\n{sub_html}{body}\n</body>\n</html>\n"
    )

    os.makedirs(chap_dir, exist_ok=True)
    with open(os.path.join(chap_dir, f"{name}.html"), "w", encoding="utf-8") as fh:
        fh.write(doc)

    return title, n_diagrams, n_photos


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)

    manifest = ["# Import these into Pressbooks in order (Import type: HTML).\n"]
    for idx, name in enumerate(CHAPTERS):
        title, dia, pho = process(name)
        manifest.append(f"{idx:>2}. {name}/{name}.html\n    {title}\n")
        extras = []
        if dia:
            extras.append(f"{dia} diagram(s)")
        if pho:
            extras.append(f"{pho} photo(s)")
        print(f"  {name}: {title[:60]}" + (f"  [{', '.join(extras)}]" if extras else ""))

    with open(os.path.join(OUT, "_manifest.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(manifest))
    print(f"\nWrote {len(CHAPTERS)} chapters to {OUT}")


if __name__ == "__main__":
    main()
