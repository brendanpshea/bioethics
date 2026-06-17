import json
import re

def infer_answer_style(choices):
    WORD_RE = re.compile(r"[A-Za-z0-9']+")
    word_counts = [len(WORD_RE.findall(choice)) for choice in choices]
    average_words = sum(word_counts) / len(word_counts)
    if average_words < 2.5:
        return 'single word or term'
    # if it's very long, make it complete sentence and add periods. BUT we shouldn't have long answers.
    return 'clause'

data = {
  'title': 'Chapter 09 Public Health Ethics',
  'source_csv': 'chapter-09-public-health.csv',
  'shuffle_answers': True,
  'questions': []
}

mc_qs = [
  {'p': 'In contrast to clinical ethics, what is the primary unit of ethical concern in public health?', 'choices': ['The entire population', 'The individual patient', 'The healthcare provider', 'The medical institution']},
  {'p': 'Unlike clinical ethics which focuses on individual autonomy, public health ethics broadly emphasizes what?', 'choices': ['Collective welfare', 'Individual autonomy', 'Strict informed consent', 'Extending terminal life']},
  {'p': "According to John Stuart Mill's harm principle, power may only be rightfully exercised against an individual's will for what purpose?", 'choices': ['To prevent harm to others', 'To prevent self-harm', 'To maximize total well-being', 'To enforce implicit consent']},
  {'p': 'The historical case of Mary Mallon (Typhoid Mary) illustrates tensions between collective welfare protection and what?', 'choices': ['Individual liberty', 'Informed consent', 'Medical rationing', 'Paternalism']},
  {'p': 'How do we describe a person who spreads an infectious disease without suffering from it themselves?', 'choices': ['A healthy carrier', 'An immune survivor', 'Vaccinated individual', 'A feverish patient']},
  {'p': 'In Jacobson v. Massachusetts (1905), the Supreme Court ruled that during a public health crisis states can do what?', 'choices': ['Compel vaccination', 'Ban unconstitutional quarantines', 'Override federal authorities', 'Suspend liberty forever']},
  {'p': 'According to the deficit model, people hold false medical beliefs because they lack what?', 'choices': ['Factual information', 'Group identity protection', 'Echo chamber feedback', 'Scientific institutions']},
  {'p': "Dan Kahan's concept of 'identity-protective cognition' argues that people reason primarily to protect what?", 'choices': ['Their group standing', 'Other social groups', 'Their primary physician', 'Their scientific literacy']},
  {'p': 'According to Kahan, when highly scientifically literate people evaluate politically charged questions, what happens to them?', 'choices': ['They become more polarized', 'They converge on truth', 'They discard group identity', 'They temporarily lose literacy']},
  {'p': 'According to C. Thi Nguyen, an epistemic bubble is a network where contrary voices are what?', 'choices': ['Accidentally excluded', 'Actively discredited', 'Systematically filtered', 'Intentionally manipulated']},
  {'p': 'Unlike an epistemic bubble, an echo chamber actively builds distrust and does what to outside voices?', 'choices': ['Preemptively discredits them', 'Accidentally excludes them', 'Easily accepts raw facts', 'Relies on the deficit model']},
  {'p': 'In 1998, Dr. Andrew Wakefield published a flawed study claiming a link between the MMR vaccine and what condition?', 'choices': ['Autism', 'Adult onset diabetes', 'Guillain-Barre syndrome', 'Polio']},
  {'p': "After discovering the data had been manipulated, what did the Lancet eventually do to Wakefield's 1998 paper?", 'choices': ['Fully retracted it', 'Adopted it globally', 'Spurred an FDA ban', 'Ignored it entirely']},
  {'p': "What hidden problem did journalist Brian Deer discover regarding Wakefield's study?", 'choices': ['Undisclosed financial conflicts', 'Stolen research data', 'NHS publication coercion', 'Secret corporate funding']},
  {'p': 'What term describes the strategy used by industries to protect themselves by introducing artificial scientific uncertainty?', 'choices': ['Manufactured doubt', 'Natural scientific phases', 'Identity-protective cognition', 'Legal stalling strategies']},
  {'p': 'Which pair of ethicists developed the five justificatory benchmarks for evaluating public health interventions?', 'choices': ['Childress and colleagues', 'Amartya Sen and Nussbaum', 'Nozick and Singer', 'Mill and Rawls']},
  {'p': 'Which of the following is NOT one of the five justificatory benchmarks for evaluating public health?', 'choices': ['Paternalistic advantage', 'Effectiveness', 'Proportionality', 'Necessity']},
  {'p': 'In vaccination contexts, what do we call a person who accepts the benefits of herd immunity without taking the vaccine risks?', 'choices': ['A free rider', 'An uninsured patient', 'Experimental volunteer', 'A taxed citizen']},
  {'p': 'What term describes the phenomenon where enough of a population is immune that a disease cannot sustain spread?', 'choices': ['Herd immunity', 'Population immunity', 'Individual immunity', 'Mandated immunity']},
  {'p': 'Which public health benchmark strictly calculates whether the overall benefits outweigh the infringed moral considerations?', 'choices': ['Proportionality', 'Effectiveness', 'Least infringement', 'Necessity']},
  {'p': 'Which public health benchmark requires choosing the specific option that restricts liberty the least while still succeeding?', 'choices': ['Least infringement', 'Necessity', 'Proportionality', 'Effectiveness']},
  {'p': 'In the infamous Buck v. Bell (1927) ruling, what public health case was used as the central legal precedent?', 'choices': ['Jacobson v. Massachusetts', 'Cruzan v. Director', 'Roe v. Wade', "Mary Mallon's quarantine"]},
  {'p': 'Using public health logic as justification, what catastrophic practice did Buck v. Bell (1927) legally defend?', 'choices': ['Compulsory sterilization', 'Mandatory organ donations', 'Psychiatric euthanasia', 'Indefinite healthy detention']},
  {'p': 'If a false belief survives because someone is trapped in an echo chamber, what is the best strategy?', 'choices': ['Rebuilding relationship trust', 'Supplying large study packets', 'Explaining the deficit model', 'Forcing opposing views']},
  {'p': 'Why is public health ethics often described as an inherently political discipline?', 'choices': ['It authorizes coercive state power', 'It only involves voting', 'It bypasses the Supreme Court', 'It ignores scientific findings']},
  {'p': "What was Wakefield's undisclosed financial conflict of interest while publishing the Lancet study?", 'choices': ['Funded by litigation lawyers', 'Paid by foreign governments', 'Selling rival vaccine patents', 'Short-selling Lancet shares']},
  {'p': 'Why do many public health interventions face intense public resistance?', 'choices': ['They burden some for others', 'They are entirely unproven', 'They focus on terminal patients', 'They require citizen consent']},
  {'p': 'In answering "Why trust science?", Naomi Oreskes argues that trust is fundamentally based on what?', 'choices': ['Sustained critical expert consensus', 'Lone genius breakthroughs', 'Direct foundational truth access', 'Deficit model adherence']},
  {'p': 'If a person refuses the MMR vaccine purely due to lacking information rather than politics, what condition do they have?', 'choices': ['A simple deficit', 'A deep echo chamber', 'Identity-protective cognition', 'Deliberate free-riding']},
  {'p': "Why did Mary Mallon's second lifelong confinement feel more ethically justified than her first?", 'choices': ['She cooked knowing she was infectious', 'She committed a violent crime', 'Laws banned Irish immigrants', 'The Supreme Court ruled on her']}
]

mr_qs = [
  {'p': "Which of the following are parts of Childress and colleagues' five justificatory benchmarks? (Select all that apply)", 'choices': ['Effectiveness', 'Proportionality', 'Necessity', 'Least infringement'], 'wrong': ['Financial yield']},
  {'p': 'What are defining features of an "echo chamber" according to Nguyen? (Select all that apply)', 'choices': ['Actively discredits outside voices', 'Dismisses contrary evidence', 'Builds distrust in mainstream'], 'wrong': ['Accidentally leaves out information', 'Easily popped by raw facts']},
  {'p': 'Which arguments did the Supreme Court use to allow compelled vaccination in Jacobson v. Massachusetts? (Select all that apply)', 'choices': ['Liberty is not absolute right', 'States have police power', 'Constitutional during active outbreaks'], 'wrong': ['Sterilization is vital to health', 'Federal government directs states']},
  {'p': "What was true regarding Mary Mallon's first confinement for typhoid? (Select all that apply)", 'choices': ['She committed no crime', 'She felt entirely healthy', 'No law allowed carrier quarantine'], 'wrong': ['She admitted spreading typhoid', 'It lasted until her death']},
  {'p': "What did Dan Kahan's research on identity-protective cognition show regarding deeply political science questions? (Select all that apply)", 'choices': ['Reasoning protects group standing', 'Science literacy increases polarization', 'Minds prioritize group alignment'], 'wrong': ['The deficit model is accurate', 'Only uneducated resist science']},
  {'p': 'What elements contributed to the immediate and lasting impact of the Wakefield MMR study? (Select all that apply)', 'choices': ['Published in the prestigious Lancet', 'Matched modern medicine anxieties', 'Uncritical spread by early media'], 'wrong': ['Verified clinically on thousands', 'Initially endorsed by the FDA']},
  {'p': 'What ethical principles must often be balanced directly against each other in public health decisions? (Select all that apply)', 'choices': ['Collective welfare', 'Individual autonomy or liberty', 'Justice or fairness in burdens'], 'wrong': ['Absolute right to refuse regulation', 'Market forces as determinants']},
  {'p': 'Which statements accurately describe a "free rider" problem in public health vaccination? (Select all that apply)', 'choices': ['Gain protection from vaccinated majority', 'Avoid personal risks of vaccines', "Leverage herd immunity unfairly"], 'wrong': ['Pay extreme out-of-pocket costs', 'Actively endure quarantine isolation']},
  {'p': 'What does Naomi Oreskes argue regarding how and why we should trust scientific establishments? (Select all that apply)', 'choices': ['Process of social consensus-building', 'Community of experts scrutinizing each other', 'Process corrects flawed individual studies'], 'wrong': ['Accesses absolute untainted foundational truth', 'Consensus is irrelevant to basic factuality']},
  {'p': 'How do epistemic bubbles differ from echo chambers according to Nguyen? (Select all that apply)', 'choices': ['Bubbles involve accidentally missing voices', 'Bubbles are easily fixed by information', 'Echo chambers involve active distrust of others'], 'wrong': ['Echo chambers are innocent filter bubbles', 'Bubbles actively attack opposing arguments']}
]

for q in mc_qs:
  data['questions'].append({'question_type': 'MC', 'answer_style': infer_answer_style(q['choices']), 'prompt': q['p'], 'answer_explanation': '', 'points': '', 'tags': ['chapter-09', 'mc'], 'choices': [{'text': c, 'correct': i==0} for i, c in enumerate(q['choices'])]})
for q in mr_qs:
  data['questions'].append({'question_type': 'MR', 'answer_style': infer_answer_style(q['choices'] + q['wrong']), 'prompt': q['p'], 'answer_explanation': '', 'points': '', 'tags': ['chapter-09', 'mr'], 'choices': [{'text': c, 'correct': True} for c in q['choices']] + [{'text': c, 'correct': False} for c in q['wrong']]})

with open('perusall_quiz/sources/chapter-09-public-health.quiz.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)
