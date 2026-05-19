import os
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

# Ensure fonts and aesthetics are clean
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'

def generate_timeline():
    # Milestones data
    milestones = [
        {"week": 0, "label": "Fertilization", "desc": "Sperm & egg fuse;\nzygote formed"},
        {"week": 2, "label": "Implantation", "desc": "Embryo attaches\nto uterine wall"},
        {"week": 6, "label": "Heartbeat Detectable", "desc": "Early cardiac tube\ncontracts; ultrasound"},
        {"week": 8, "label": "Fetal Stage Begins", "desc": "Embryonic organ\nformation complete"},
        {"week": 12, "label": "Neural Activity", "desc": "First electrical brain\nsignals detectable"},
        {"week": 18, "label": "Quickening", "desc": "Fetal movements\nfelt by pregnant person"},
        {"week": 24, "label": "Viability & Sentience", "desc": "Thalamocortical tracts active;\nearly survival potential"},
        {"week": 37, "label": "Full Term", "desc": "Fetus fully developed;\nready for birth"}
    ]

    weeks = [m["week"] for m in milestones]
    labels = [m["label"] for m in milestones]
    descs = [m["desc"] for m in milestones]

    # Create figure with custom size
    fig, ax = plt.subplots(figsize=(14, 7), dpi=300)
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')

    # Plot timeline line
    ax.plot([0, 42], [0, 0], color='#475569', linewidth=4, zorder=1)
    # Highlight viability point zone
    ax.axvspan(22, 25, color='#e2e8f0', alpha=0.6, label='Transition Zone (Viability)', zorder=0)

    # Plot ticks/dots for milestones
    colors = ['#475569', '#334155', '#0e7c86', '#0f766e', '#b07d1a', '#854d0e', '#c0392b', '#991b1b']
    
    # Alternate labels above and below
    for i, m in enumerate(milestones):
        x = m["week"]
        y = 0
        color = colors[i]
        
        # Plot point
        ax.scatter(x, y, color=color, s=200, zorder=3, edgecolors='white', linewidths=2)
        
        # Draw stem line
        is_above = (i % 2 == 0)
        stem_y = 1.1 if is_above else -1.1
        text_y = 1.25 if is_above else -1.75
        
        ax.plot([x, x], [0, stem_y], color=color, linestyle='--', linewidth=1.5, zorder=2)
        
        # Annotation text
        va = 'bottom' if is_above else 'top'
        # Title text (Enlarged for strong readability)
        ax.text(x, text_y, m["label"], ha='center', va=va, fontsize=13.5, fontweight='bold', color=color)
        # Description text (Enlarged and darkened to #1e293b for high contrast)
        desc_y = text_y + (0.35 if is_above else -0.35)
        ax.text(x, desc_y, m["desc"], ha='center', va=va, fontsize=10.5, color='#1e293b', style='italic')

    # Customize axes
    ax.set_xlim(-2, 44)
    ax.set_ylim(-3.5, 3.5)
    
    # Clean up ticks and spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.get_yaxis().set_visible(False)
    
    # Configure custom x-ticks for weeks (Enlarged for high readability)
    ax.set_xticks([0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40])
    ax.set_xticklabels([f"Wk {w}" for w in [0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40]], fontsize=11.5, color='#475569', fontweight='bold')
    ax.tick_params(axis='x', colors='#475569', width=1.5, length=6)
    
    # Add simple title and footer
    ax.text(21, 3.2, "Milestones in Fetal Development (Weeks from Last Menstrual Period)", 
            ha='center', va='center', fontsize=16, fontweight='bold', color='#1e293b')
    ax.text(21, -3.3, "*Note: Development is a continuous process. Timelines represent standard clinical averages & ranges.", 
            ha='center', va='center', fontsize=9.5, color='#64748b', style='italic')

    plt.tight_layout()
    output_path = Path("images/fetal_development_timeline.png")
    output_path.parent.mkdir(exist_ok=True)
    plt.savefig(output_path, bbox_inches='tight', transparent=False, facecolor='#ffffff')
    plt.close()
    print(f"Generated {output_path}")

def generate_concept_map():
    from graphviz import Digraph

    dot = Digraph('concept_map', comment='Moral Status Criteria')
    # Set size and aspect ratio suitable for full screen slide
    dot.attr(rankdir='TB', size='11,7.5', dpi='300')
    dot.attr('node', fontname='Arial', fontsize='12', shape='box', style='rounded,filled', margin='0.2,0.1')
    dot.attr('edge', fontname='Arial', fontsize='10', color='#64748b', penwidth='1.5', arrowsize='0.8')

    # Main root node
    dot.node('root', 'Moral Status in Bioethics\nWho counts as a moral subject?', 
             fillcolor='#1e293b', fontcolor='white', color='#0f172a', style='rounded,filled,bold', fontsize='15')

    # Criteria nodes
    dot.node('bio', 'Biological Humanity\nCoextensive with Homo Sapiens species', 
             fillcolor='#dfe6ee', color='#475569', penwidth='2.5', fontsize='13', fontweight='bold')
    dot.node('sent', 'Sentience\nCapacity to experience pleasure & pain', 
             fillcolor='#cfe9ec', color='#0e7c86', penwidth='2.5', fontsize='13', fontweight='bold')
    dot.node('pers', 'Personhood\nSelf-consciousness, rationality, agency', 
             fillcolor='#fce9d6', color='#b07d1a', penwidth='2.5', fontsize='13', fontweight='bold')
    dot.node('viab', 'Viability\nAbility to survive outside the uterus', 
             fillcolor='#fad7d2', color='#c0392b', penwidth='2.5', fontsize='13', fontweight='bold')

    dot.edge('root', 'bio')
    dot.edge('root', 'sent')
    dot.edge('root', 'pers')
    dot.edge('root', 'viab')

    # Merged Bio details node for compactness and large text scale
    dot.node('bio_details', 
             '• Includes: All human embryos, typical adults, PVS patients\n• Excludes: Non-human animals, hypothetical advanced AI\n• Philosophy: Don Marquis (Future-Like-Ours), Conservative view', 
             fillcolor='#f8fafc', color='#cbd5e1', fontsize='10.5')
    dot.edge('bio', 'bio_details')

    # Merged Sentience details node
    dot.node('sent_details', 
             '• Includes: Human fetuses >24 weeks, most animals\n• Excludes: Pre-viable/early embryos, brain-dead patients\n• Philosophy: Peter Singer (Utilitarianism), Animal welfare', 
             fillcolor='#f0fdfa', color='#0d9488', fontsize='10.5')
    dot.edge('sent', 'sent_details')

    # Merged Personhood details node
    dot.node('pers_details', 
             '• Includes: Typical human adults, advanced AI\n• Excludes: All human fetuses, infants, severe dementia\n• Philosophy: Mary Anne Warren, Michael Tooley (Liberal view)', 
             fillcolor='#fffbeb', color='#d97706', fontsize='10.5')
    dot.edge('pers', 'pers_details')

    # Merged Viability details node
    dot.node('viab_details', 
             '• Includes: Fetuses >22-24 weeks, typical adults\n• Excludes: Early-stage embryos, pre-viable fetuses\n• Alignment: Roe v. Wade, Planned Parenthood v. Casey', 
             fillcolor='#fef2f2', color='#dc2626', fontsize='10.5')
    dot.edge('viab', 'viab_details')

    output_path = Path("images/concept_map_moral_status")
    dot.render(output_path, format='png', cleanup=True)
    print(f"Generated {output_path}.png")

if __name__ == '__main__':
    generate_timeline()
    try:
        generate_concept_map()
    except Exception as e:
        print(f"Graphviz rendering failed, but timeline succeeded. Details: {e}")
