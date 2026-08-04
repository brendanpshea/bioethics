# Image Sourcing Plan

Instructor working document. Chapters 1–4 carry 20 of the course's 22 images; Chapters 5–12 —
roughly 540 slides — have one between them. This is the shortlist for closing that gap.

**Status:** candidates identified, **licenses not yet verified.** The container this was drafted in
can search the web but cannot open image pages or download files, so every entry below needs a
click-through before use. Treat this as a research shortcut, not a cleared list.

---

## 1. Licensing rules for this project

The course is **CC BY-NC 4.0**. That constrains what can go in it.

| License | Verdict | Note |
|---|---|---|
| Public domain / PD-USGov / CC0 | ✅ **Safe** | No conditions. Prefer these. |
| CC BY | ✅ **Safe** | Attribute in the `.attribution` div. |
| CC BY-NC | ⚠️ **Usable** | Fine for this NC course, but narrows downstream reuse of the OER. |
| CC BY-SA | ❌ **Avoid** | Share-alike may pull obligations onto the work. |
| CC BY-ND / CC BY-NC-ND | ❌ **Avoid** | No-derivatives. Cropping or resizing for a slide may breach it. |
| Press/news photos | ❌ **Avoid** | Nearly all rights-reserved. This rules out most photos of He Jiankui, Brittany Maynard, Kate Cox, and the *Skrmetti* plaintiffs. |

**Rule of thumb:** if the license isn't stated on the page in plain words, don't use it.

## 2. Collections worth searching first

Reported terms — confirm on the page.

| Collection | Reported terms |
|---|---|
| **CDC PHIL** — `phil.cdc.gov` | Most images public domain; a per-image fair-use statement flags exceptions. Strong for infectious disease, vaccination, lab work. |
| **NIH NIGMS Image Gallery** — `nigms.nih.gov/image-gallery` | Public domain; credit to NIH/HHS requested. Best CRISPR and molecular illustrations. |
| **NHGRI** — `genome.gov/image-gallery` + NHGRI Flickr | Public domain unless noted; credit "National Human Genome Research Institute." Genome sequencing, HGP history. |
| **Wikimedia Commons** | Per-file. Filter to PD-USGov, CC0, CC BY. Each file page states the license explicitly. |
| **Library of Congress — Carol M. Highsmith Archive** | Public domain, no restrictions. Excellent US institutional architecture, incl. the Supreme Court. |
| **Wellcome Collection** | ⚠️ Mixed. Large open-access set, but many are CC BY-**NC-ND** — which we avoid. Check each one. |
| **Unsplash** | Own license: commercial use, no attribution required. Not a CC license. Good for generic clinical settings. |

---

## 3. Where a chart beats a photograph

Three of these slides don't need an image — they need data. Adding a decorative photo would be worse
than adding nothing.

- **8B, "The Paradox"** — the US-vs-OECD spending and life-expectancy gap. A chart *is* the argument.
- **7B, assisted-death jurisdictions** — growth from 11 to 14 US jurisdictions. Chart, not photo.
- **11A, state bans** — the count over time, and the ban/shield split. Chart, not photo.

Same matplotlib approach as the 12b pilot.

---

## 4. Per-chapter shortlist

### Ch 5A — Paternalism
| Slide | Image | Where |
|---|---|---|
| A Demand in the Delivery Room | Labor & delivery room, no identifiable faces | Unsplash |
| A Puzzle to Hold | Naloxone kit — anchors the overdose-decline discussion | CDC PHIL, search *naloxone* |

*Mill's portrait is already in `images/mill.jpg` — reuse it on the harm-principle slide.*

### Ch 5B — Reproductive Markets
| Slide | Image | Where |
|---|---|---|
| What IVF Actually Does | IVF lab, micromanipulation rig | Unsplash; Wikimedia *in vitro fertilisation* |
| ICSI and Why It Exists | ICSI micrograph — a single sperm injected into an egg | Wikimedia Commons, check per-file license |

*Skip Baby M press photos — rights-reserved.*

### Ch 6A — Reading Genomes
| Slide | Image | Where |
|---|---|---|
| A Thirteen-Year Arc | Human Genome Project–era sequencing floor | NHGRI gallery / NHGRI Flickr |
| Promised vs. Delivered | Modern sequencer, or a sequence trace | NHGRI |

*Avoid 23andMe product shots — trademarked packaging.*

### Ch 6B — Engineering Persons
| Slide | Image | Where |
|---|---|---|
| A Working Definition | CRISPR-Cas9 mechanism illustration | **NIGMS gallery** — items 3719, 6486, 7036 surfaced in search |

*He Jiankui photos are press images. Use the mechanism illustration instead; the case study carries the narrative.*

### Ch 7A — Death & Dying
| Slide | Image | Where |
|---|---|---|
| The Spectrum of Consciousness | EEG trace or ICU monitor | Wikimedia *electroencephalography*; Unsplash |
| Coma / brain death | ICU bed with ventilator, no patient visible | Unsplash |

*Consider building a blank advance-directive graphic rather than sourcing one — cleaner and license-free.*

### Ch 7B — Euthanasia
Sensitive chapter. **Prefer a jurisdictions chart to photographs of dying people.** If one image is
wanted, use a legislature or courthouse exterior (Library of Congress, PD).

### Ch 8A — Justice & Allocation
| Slide | Image | Where |
|---|---|---|
| Distributive Justice | Organ transport cooler, or transplant OR | CDC PHIL; Unsplash |

*The Seattle "God Committee" photographs are Life magazine — rights-reserved.*

### Ch 8B — US Health Care
Chart-first (see §3). One photo candidate: an itemized hospital bill — **fabricate a synthetic one**
rather than sourcing a real patient's document.

### Ch 9A — Public Health
| Slide | Image | Where |
|---|---|---|
| What the City Actually Did | Already have `john_snow_map.jpg` ✅ |
| The Patient in Front of You Isn't the Only Patient | Mass vaccination clinic | CDC PHIL, search *vaccination clinic* |

### Ch 9B — False Beliefs
| Slide | Image | Where |
|---|---|---|
| Opening / measles return | **Measles rash, 1958** — search surfaced this as PD, no copyright restrictions | CDC PHIL |

### Ch 10A — Medical AI
| Slide | Image | Where |
|---|---|---|
| What the Model Actually Learned | Chest X-ray | NIH Clinical Center chest X-ray dataset (PD) |
| Training Data, Features, Labels | Retinal fundus image — the diabetic-retinopathy case | National Eye Institute image bank (PD) |

### Ch 10B — The Fifth Principle
No good photographic subject. Keep it diagrammatic; the existing components carry it.

### Ch 11A — Gender-Affirming Care
Sensitive. **Do not use photographs of identifiable trans people or minors.** Use the US Supreme
Court exterior (Highsmith / LoC, PD) for the *Skrmetti* material, and a chart for the state counts.

### Ch 11B — Disability & Identity
| Slide | Image | Where |
|---|---|---|
| The Social Model | A curb cut or ramp — the canonical social-model illustration | Unsplash |
| Identity | Already have `disability_pride_flag.svg` ✅ |

### Ch 12A — Moral Status of Animals
| Slide | Image | Where |
|---|---|---|
| The Spectrum of Views | Laboratory mouse | CDC PHIL; NIH galleries |
| Speciesism | Retired chimpanzee at sanctuary | Wikimedia, verify per file |

### Ch 12B — Industrial Animals & Xeno
| Slide | Image | Where |
|---|---|---|
| The Scale Is the Argument | **`File:Confined-animal-feeding-operation.jpg`** — Wikimedia, reported **PD-USGov** (EPA source). Best-verified candidate on this list. |
| It Harms Humans Too: Antibiotics | Antibiotic-resistance lab plate | CDC PHIL, search *antimicrobial resistance* |
| Why Xenotransplantation | Surgical team / transplant OR | Unsplash |

---

## 5. Workflow when adding one

1. Open the file page. **Read the license in plain words.** If it's ND or SA, stop.
2. Download the largest available version; downscale locally rather than hotlinking.
3. Save to `images/` with a descriptive snake_case name.
4. Reference with alt text — every existing figure in this course has `fig-alt`, keep that:

```markdown
![](../images/cafo_barn.jpg){width="80%" fig-alt="Interior of a confined animal feeding operation, rows of pens under artificial light."}

::: {.attribution}
US EPA, via Wikimedia Commons. Public domain.
:::
```

5. Record source and license in the `.attribution` div — that div is already styled in both the HTML
   and slide themes.
