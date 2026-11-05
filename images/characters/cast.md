# Character Cast

Transparent PNGs in `figures/`, cut from the four sheets in `sheets/` by `split_sheets.py`. All figures share one pixel scale (heads about the same size), so two figures shown at the same CSS scale stand at matching sizes. Most face slightly toward the viewer's right; mirror one horizontally (`transform: scaleX(-1)`) to make a pair face each other.

`cast.png` shows every figure with its file name. To re-cut after replacing a sheet, put it in `sheets/` (kept out of git) and run `python split_sheets.py`, or pass a single sheet path.

## Using them: a dialogue slide

The styles live in `styles/custom.css` (layout, both formats) and `styles/slides.scss` (slide sizing). In a chapter, a conversation looks like this:

```markdown
## The Fifteen-Minute Visit

::::: {.dialogue}
:::: {.speaker}
![](../images/characters/figures/nurse-01.png){fig-alt="A nurse in teal scrubs holding a clipboard"}

[Nurse]{.who}
::::
:::: {.bubbles}
::: {.bubble .left}
Maya's due for her MMR today. Any questions before we start?
:::
::: {.bubble .right}
We're skipping that one. I've read a lot about it and autism.
:::
::: {.bubble .left}
It sounds like you've really done your homework. What worries you most?
:::
::::
:::: {.speaker .flip}
![](../images/characters/figures/family-01.png){fig-alt="A mother holding a toddler on her hip"}

[Parent]{.who}
::::
:::::
```

- `.bubble .left` is the left speaker; `.bubble .right` the right one. Their tails point at the speaker.
- `.flip` mirrors the right-hand figure so the two face each other. The figures carry no text, so mirroring is safe.
- Figures show at native size, so the cast keeps one scale: a child stays shorter than an adult.
- About three or four short exchanges fit on a slide. In the HTML notes, the same markup renders as a smaller inline conversation.

## Nurses and nursing staff (sheet 1)

| File | Who |
|---|---|
| `nurse-01` | nurse, woman, 30s, deep brown skin, natural hair puff, teal scrubs, clipboard |
| `nurse-02` | nurse, man, 40s, fair skin, ginger hair and beard, navy scrubs, tablet |
| `nurse-03` | nursing student, woman, ~20, East Asian, ponytail, light-blue scrubs, backpack |
| `nurse-04` | nurse, woman, 50s, South Asian, gray-streaked bun, green scrubs, medicine cup |
| `nurse-05` | nurse, man, 20s, dark brown skin, locs, charcoal scrubs, IV bag |
| `nurse-06` | nurse, woman, 30s, navy hijab, navy scrubs, blood-pressure cuff |
| `nurse-07` | nurse practitioner, androgynous, 30s, undercut, white coat over teal scrubs |
| `nurse-08` | senior nurse, man, ~60, Native American, gray braid, olive scrubs, clipboard |
| `nurse-09` | nursing assistant, woman, 40s, Filipina, bob, gray scrubs, folded towels |

## Physicians and the care team (sheet 2)

| File | Who |
|---|---|
| `staff-01` | physician, woman, 40s, dark brown skin, braids, white coat, tablet |
| `staff-02` | physician, Sikh man, 30s, navy turban, beard, white coat and tie |
| `staff-03` | surgeon, woman, ~50, fair skin, surgical cap, blue scrubs, mask at neck |
| `staff-04` | resident, man, ~28, East Asian, glasses, short white coat, coffee |
| `staff-05` | pharmacist, woman, 30s, Latina, curly hair, white coat, pill bottle |
| `staff-06` | social worker, man, 50s, dark brown skin, gray beard, cardigan, folder |
| `staff-07` | chaplain, woman, 60s, silver hair, green blazer, hands clasped |
| `staff-08` | ASL interpreter, woman, 30s, black top, signing |
| `staff-09` | research coordinator, androgynous, 30s, dark brown skin, mustard cardigan, clipboard |

## Adult patients (sheet 3)

| File | Who |
|---|---|
| `patient-01` | man, ~34, fair skin, power wheelchair (Daniel, Lecture 11B) |
| `patient-02` | woman, 70s, dark brown skin, gray hair, hospital gown, IV pole |
| `patient-03` | man, 60s, East Asian, gown and robe, walker |
| `patient-04` | pregnant woman, ~30, Latina, mustard top |
| `patient-05` | man, 40s, sweater, folder of printouts |
| `patient-06` | woman, ~25, red hair, hoodie, smartphone |
| `patient-07` | man, ~80, bald, white mustache, cardigan, hearing aid, cane |
| `patient-08` | man, ~40, South Asian, below-knee prosthetic leg |
| `patient-09` | woman, ~50, Native American, hospital gown, cup of water |

## Children, teens, and families (sheet 4)

| File | Who |
|---|---|
| `family-01` | mother, early 30s, fair skin, holding a toddler (the MMR case, Lecture 9B) |
| `family-02` | father, 40s, dark brown skin, navy pullover, concerned |
| `family-03` | teenager, ~15, light-brown skin, green hoodie (Riley, Lecture 11A) |
| `family-04` | girl, ~7, East Asian, pigtails, child's hospital gown, teddy bear |
| `family-05` | grandmother, 70s, South Asian, teal-and-gold salwar kameez, glasses |
| `family-06` | teen boy, ~16, Latino, red jersey, arm in a cast |
| `family-07` | adult daughter and caregiver, 40s, rain jacket, tote bag, folder |
| `family-08` | Deaf woman, ~30, dark brown skin, denim jacket, signing |
| `family-09` | older man, 70s, Pacific Islander, oxygen cannula and portable tank |
