#!/usr/bin/env bash
# Build the EPUB of the introduction + all case studies.
# Pulls the CURRENT case sources from ../cases at build time (no duplicated
# source is committed here), renders, copies the .epub to ../docs, then
# removes the temporary copies.
set -euo pipefail
cd "$(dirname "$0")"

files=(
  00-introduction 01-dax-cowart 02-tuskegee-guatemala 03-alzheimers-fraud
  04-kate-cox-karsan 05-adriana-smith 06-he-jiankui 07-noelia-castillo
  08-singapore-healthcare 09-wakefield-mmr 10-optum-algorithm 11-skrmetti
  12-bennett-xenotransplant
)

cleanup() {
  for f in "${files[@]}"; do rm -f "./$f.qmd"; done
  rm -f ./pressbooks_cover.png
}
trap cleanup EXIT

# Stage the cover image (used as the EPUB cover).
cp ../assets/images/pressbooks_cover.png ./pressbooks_cover.png

# Stage current sources, stripping each file's own "## References" block:
# the book uses a single consolidated bibliography (references.qmd), so a
# per-chapter #refs div would make citeproc repeat the whole bibliography
# in every chapter.
for f in "${files[@]}"; do
  cp "../cases/$f.qmd" "./$f.qmd"
  sed -i '/^## References$/,$d' "./$f.qmd"
done

# Render the book to EPUB.
quarto render --to epub

# Publish the artifact.
mkdir -p ../docs
epub=$(ls -t _output/*.epub 2>/dev/null | head -1 || true)
if [ -n "${epub:-}" ]; then
  cp "$epub" "../docs/Thinking-with-Cases.epub"
  echo "EPUB written to docs/Thinking-with-Cases.epub"
else
  echo "ERROR: no .epub produced" >&2
  exit 1
fi
