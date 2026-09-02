import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

assets_dir = Path("assets")
assets_dir.mkdir(parents=True, exist_ok=True)

# Generate a crisp PNG logo using matplotlib
fig, ax = plt.subplots(figsize=(8, 2), dpi=200)
fig.patch.set_facecolor('#FFFFFF')
ax.set_facecolor('#FFFFFF')

# Draw icon box
rect = patches.FancyBboxPatch((0.02, 0.15), 0.16, 0.7, boxstyle="round,pad=0.03", ec="none", fc="#1E3A8A")
ax.add_patch(rect)

# Draw stylized cube on icon
polygon1 = patches.Polygon([[0.1, 0.7], [0.15, 0.58], [0.1, 0.46], [0.05, 0.58]], closed=True, fc='#93C5FD')
polygon2 = patches.Polygon([[0.05, 0.58], [0.1, 0.46], [0.1, 0.28], [0.05, 0.4]], closed=True, fc='#3B82F6')
polygon3 = patches.Polygon([[0.15, 0.58], [0.1, 0.46], [0.1, 0.28], [0.15, 0.4]], closed=True, fc='#1D4ED8')
ax.add_patch(polygon1)
ax.add_patch(polygon2)
ax.add_patch(polygon3)

# Text: RetailSphere
ax.text(0.24, 0.52, "Retail", fontsize=24, fontweight='bold', color='#0F172A', va='center')
ax.text(0.44, 0.52, "Sphere", fontsize=24, fontweight='bold', color='#2563EB', va='center')

# Subtitle
ax.text(0.24, 0.28, "ENTERPRISE DATA WAREHOUSE & GOVERNANCE", fontsize=8, fontweight='semibold', color='#64748B', va='center')

# Live Badge
badge = patches.FancyBboxPatch((0.85, 0.45), 0.12, 0.25, boxstyle="round,pad=0.02", ec="none", fc="#10B981")
ax.add_patch(badge)
ax.text(0.91, 0.57, "● LIVE", fontsize=8, fontweight='bold', color='#FFFFFF', ha='center', va='center')

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

plt.tight_layout()
plt.savefig(assets_dir / "logo.png", bbox_inches='tight', dpi=300, facecolor=fig.get_facecolor(), transparent=False)
plt.close()

print("PNG Logo generated at assets/logo.png")
