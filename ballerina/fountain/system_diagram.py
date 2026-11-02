import numpy as np, trimesh, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Rectangle, Polygon as P, FancyBboxPatch

# layout (mm), section through the middle, viewed from her front
FLOOR_TOP, WATER, WALL_TOP = 35, 60, 80           # pool floor, water surface, rim
R_IN, R_OUT = 150, 165                            # basin wall
ISL_R, ISL_TOP = 62, 85                           # island pedestal
WELL_R, WELL_BOT = 45, 4                          # pump well under the island
LIP_Z_FIG, LIP_R = 169.5, 22                      # slot height on her (model units) and radius

m = trimesh.load('../ballerina_b2_original_hands.stl')
f = np.array([np.cos(np.radians(-55)), np.sin(np.radians(-55)), 0])
u = np.array([-f[1], f[0], 0])
keep = m.triangles_center[:, 2] > 24.5            # drop her old display base; the island replaces it
tri = m.triangles[keep]
xy = np.stack([tri @ u, tri[:, :, 2] - 24.5 + ISL_TOP], -1)
lip_z = LIP_Z_FIG - 24.5 + ISL_TOP

fig, ax = plt.subplots(figsize=(12, 13))
stone, water_c, dark = '#9a948a', '#7fb8e6', '#555'
# basin: floor slab + walls (stone), well pocket under the island
ax.add_patch(Rectangle((-R_OUT, 0), 2 * R_OUT, FLOOR_TOP, color=stone))
for s in (-1, 1):
    ax.add_patch(Rectangle((s * R_IN if s > 0 else -R_OUT, 0), R_OUT - R_IN, WALL_TOP, color=stone))
ax.add_patch(Rectangle((-WELL_R, WELL_BOT), 2 * WELL_R, FLOOR_TOP - WELL_BOT, color='white'))
# water: pool + well
ax.add_patch(Rectangle((-R_IN, FLOOR_TOP), 2 * R_IN, WATER - FLOOR_TOP, color=water_c))
ax.add_patch(Rectangle((-WELL_R, WELL_BOT), 2 * WELL_R, WATER - WELL_BOT, color=water_c, zorder=1))
# island: hollow rock pedestal with crevice openings at its foot, lift-off top
wall_t = 6
for s in (-1, 1):
    x0 = s * ISL_R - (wall_t if s > 0 else 0)
    ax.add_patch(Rectangle((x0, FLOOR_TOP + 9), wall_t, ISL_TOP - 6 - FLOOR_TOP - 9, color='#8a847a', zorder=3))
    ax.add_patch(Rectangle((x0, FLOOR_TOP), wall_t, 2, color='#8a847a', zorder=3))   # small feet between crevices
ax.add_patch(Rectangle((-ISL_R - 3, ISL_TOP - 6), 2 * ISL_R + 6, 6, color='#6f6a62', zorder=4))  # removable top
# pump
ax.add_patch(FancyBboxPatch((-18, WELL_BOT + 1), 36, 40, boxstyle='round,pad=1', color='#333', zorder=5))
ax.text(0, WELL_BOT + 21, 'PUMP', color='white', ha='center', va='center', fontsize=10, weight='bold', zorder=6)
# hose from pump up to her foot
foot_x = np.mean(xy[(xy[:, :, 1] < ISL_TOP + 8).all(1)][:, :, 0])
hx = [0, 0, foot_x * 0.6, foot_x]
hz = [WELL_BOT + 42, ISL_TOP - 25, ISL_TOP - 10, ISL_TOP + 2]
ax.plot(hx, hz, color='#1d5fa8', lw=4, zorder=6, solid_capstyle='round')
# figure silhouette
ax.add_collection(PolyCollection(xy, facecolors='#e8b89a', edgecolors='none', zorder=7))
# water path inside her leg (schematic) and hip ring
ax.plot([foot_x, foot_x * 0.6, 0], [ISL_TOP + 2, (ISL_TOP + lip_z) / 2, lip_z - 8], color='#1d5fa8', lw=2.5, ls='--', zorder=8)
# sheet trajectories at three exit speeds
g = 9.81
for v, ls in ((1.0, '-'), (1.5, '--'), (2.0, ':')):
    for s in (-1, 1):
        vx, vz = v * np.cos(np.radians(50)) * 1000, -v * np.sin(np.radians(50)) * 1000
        t = np.linspace(0, 1, 400)
        x = s * (LIP_R + vx * t); z = lip_z + vz * t - 0.5 * g * 1000 * t ** 2
        k = z >= WATER
        ax.plot(x[k], z[k], color='#2b7bd0', lw=1.6, ls=ls, zorder=6)
    land = LIP_R + vx * t[k][-1]
    ax.plot([], [], color='#2b7bd0', lw=1.6, ls=ls, label=f'exit {v:.1f} m/s: lands {land:.0f} mm from center')
ax.axvline(R_IN, ymin=0, ymax=0, color='none', label=f'(pool inside edge at {R_IN} mm)')
ax.legend(loc='upper right', fontsize=9.5, title='water sheet paths', frameon=True)
# cord
ax.plot([-R_OUT + 5, -R_OUT - 40, -R_OUT - 60], [10, 10, 10], color='k', lw=2)
ax.plot([-WELL_R + 4, -R_OUT + 5], [10, 10], color='k', lw=2, ls=':')
ax.add_patch(Rectangle((-R_OUT - 95, 2), 34, 16, color='#222'))
ax.text(-R_OUT - 78, -3, '12 V adapter + speed knob\n(plugs into the wall)', ha='center', va='top', fontsize=9)

def note(xy_, txt, xyt):
    ax.annotate(txt, xy=xy_, xytext=xyt, fontsize=10, ha='left' if xyt[0] > xy_[0] else 'right', va='center',
                arrowprops=dict(arrowstyle='->', color='k', lw=1), zorder=10)
note((LIP_R, lip_z), 'water sheet ("tutu") leaves\nthe slot under her belt', (95, lip_z + 40))
note((foot_x * 0.3, (ISL_TOP + lip_z) / 2 - 20), 'channel up one leg\n(hidden inside her)', (-175, 235))
note((foot_x * 0.8, ISL_TOP - 14), 'hose from pump to her foot,\nhidden inside the island', (-175, 165))
note((-R_IN - 7, WALL_TOP - 8), 'stone-block basin wall\n(printed texture, painted)', (-175, 125))
note((-110, WATER - 8), 'pool, ~25 mm deep', (-175, 95))
note((-12, WELL_BOT + 30), 'submersible 12 V pump\nat the bottom of the well', (-175, 55))
note((ISL_R - 3, ISL_TOP - 3), 'island top lifts off with her on it\n(to reach the pump)', (110, 150))
note((ISL_R, FLOOR_TOP + 4), "hidden crevices at the island's foot:\npool water flows into the well", (110, 18))
ax.set_xlim(-290, 290); ax.set_ylim(-25, ISL_TOP + 300)
ax.set_aspect('equal'); ax.axis('off')
ax.set_title('Ballerina fountain: how the water goes round (cut through the middle, to scale, mm)', fontsize=13)
plt.tight_layout(); plt.savefig('system_diagram.png', dpi=100)
print('lip height above water:', lip_z - WATER)
