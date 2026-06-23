#!/usr/bin/env bash
# Build the PDF edition of the introduction + all case studies.
# Same staging approach as build-epub.sh: pulls the CURRENT case sources
# from ../cases at build time, renders to PDF, copies the artifact to
# ../docs, then removes the temporary copies.
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

# Stage the cover image for the custom title page.
cp ../assets/images/pressbooks_cover.png ./pressbooks_cover.png

# Stage current sources, stripping each file's own "## References" block:
# the book uses a single consolidated bibliography (references.qmd), so a
# per-chapter #refs div would make citeproc repeat the whole bibliography
# in every chapter.
for f in "${files[@]}"; do
  cp "../cases/$f.qmd" "./$f.qmd"
  sed -i '/^## References$/,$d' "./$f.qmd"
done

quarto render --to pdf

mkdir -p ../docs
pdf=$(ls -t _output/*.pdf 2>/dev/null | head -1 || true)
if [ -n "${pdf:-}" ]; then
  cp "$pdf" "../docs/Thinking-with-Cases.pdf"
  echo "PDF written to docs/Thinking-with-Cases.pdf"
else
  echo "ERROR: no .pdf produced" >&2
  exit 1
fi
