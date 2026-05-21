import textstat, re, sys, os, glob

files = sorted(glob.glob("cases/0*.qmd"))
for f in files:
    with open(f, encoding="utf-8") as fp:
        raw = fp.read()
    # strip YAML front matter
    txt = re.sub(r"^---.*?---\n", "", raw, count=1, flags=re.S)
    # strip code blocks / divs / callouts markup
    txt = re.sub(r"```.*?```", "", txt, flags=re.S)
    txt = re.sub(r":::+[^\n]*", "", txt)
    txt = re.sub(r"\{[^}]*\}", "", txt)
    # strip headers markers, bullets, blockquotes
    body = re.sub(r"^[#>\-\*\d\.\s]+", "", txt, flags=re.M)
    # count bullet/numbered list lines
    bullets = len(re.findall(r"^\s*[-*]\s+\S", txt, flags=re.M))
    numbered = len(re.findall(r"^\s*\d+\.\s+\S", txt, flags=re.M))
    headers = len(re.findall(r"^#+\s", txt, flags=re.M))
    # remove links to plain text
    body = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", body)
    body = re.sub(r"\*+|_+", "", body)
    body = re.sub(r"\s+", " ", body).strip()
    fk = textstat.flesch_kincaid_grade(body)
    fre = textstat.flesch_reading_ease(body)
    gf = textstat.gunning_fog(body)
    smog = textstat.smog_index(body)
    words = textstat.lexicon_count(body)
    sents = textstat.sentence_count(body)
    asl = words/sents if sents else 0
    print(f"{os.path.basename(f)}")
    print(f"  words={words}  sentences={sents}  avg sent len={asl:.1f}")
    print(f"  Flesch-Kincaid Grade: {fk:.1f}")
    print(f"  Gunning Fog:          {gf:.1f}")
    print(f"  SMOG:                 {smog:.1f}")
    print(f"  Flesch Reading Ease:  {fre:.1f}")
    print(f"  Headers: {headers}  Bullets: {bullets}  Numbered: {numbered}")
    print()
