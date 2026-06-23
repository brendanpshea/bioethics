"""Generate a simple, clean EPUB cover (cover.png) with matplotlib.
Run: python make_cover.py
"""
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

W, H = 1600, 2400  # ~2:3, standard ebook cover ratio
fig = plt.figure(figsize=(W / 200, H / 200), dpi=200)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")

teal, dark, accent, soft = "#0e7c86", "#095058", "#c0392b", "#f5f8f9"

# Background
ax.add_patch(Rectangle((0, 0), 1, 1, color=teal, zorder=0))
# Lower band
ax.add_patch(Rectangle((0, 0), 1, 0.16, color=dark, zorder=1))
# Thin accent rules framing the title block
ax.plot([0.12, 0.88], [0.66, 0.66], color="white", lw=2, zorder=2)
ax.plot([0.12, 0.88], [0.46, 0.46], color="white", lw=2, zorder=2)
ax.plot([0.12, 0.30], [0.40, 0.40], color=accent, lw=5, zorder=2)

# Title
ax.text(0.5, 0.595, "Thinking\nwith Cases", ha="center", va="center",
        color="white", family="serif", fontsize=64, fontweight="bold",
        linespacing=1.05, zorder=3)
# Subtitle
ax.text(0.5, 0.435, "An Introduction to Bioethics", ha="center", va="center",
        color="white", family="sans-serif", fontsize=27, zorder=3)
# Tagline
ax.text(0.5, 0.30, "Real medical dilemmas, taken apart —\nso you can decide what you think.",
        ha="center", va="center", color="#dCEefb", family="serif",
        fontsize=20, fontstyle="italic", linespacing=1.4, zorder=3)
# Author
ax.text(0.5, 0.08, "BRENDAN SHEA, PhD", ha="center", va="center",
        color="white", family="sans-serif", fontsize=22,
        fontweight="bold", zorder=3)

fig.savefig("cover.png", dpi=200)
print("wrote cover.png")
