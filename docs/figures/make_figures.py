"""Regenerates the diagrams shown in the README.

    pip install matplotlib
    python docs/figures/make_figures.py

The diagrams are drawn by hand from the sources in Tp1/, tp2/, Tp3/ and Tp4/;
nothing here executes the course code.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, Rectangle

HERE = Path(__file__).resolve().parent
for f in Path("/usr/share/fonts/lm").glob("lm*10-*.otf"):  # Latin Modern, if installed
    font_manager.fontManager.addfont(str(f))
plt.style.use(HERE / "paper.mplstyle")
C = plt.rcParams["axes.prop_cycle"].by_key()["color"]
INK, GRAY = "#1a1a1a", "#8c8c8c"
TINT = {C[0]: "#e3eaf3", C[1]: "#f6e3df", C[2]: "#e2efe3", C[3]: "#ebe6f1", C[4]: "#f8eedb", C[5]: "#ececec"}
LH = 1.55  # line height in diagram units (1 unit = 0.1 in)


def save(fig, name):
    fig.savefig(HERE / name, metadata={"Date": None})
    plt.close(fig)


def canvas(w, h):
    fig = plt.figure(figsize=(w / 10, h / 10))
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


class Box:
    """A UML-style class box whose top-left corner is (x, y)."""

    def __init__(self, ax, x, y, w, name, members=(), color=C[0], abstract=False, note=None):
        h = LH * 1.25 + (LH * len(members) + 0.5 if members else 0)
        self.x, self.y, self.w, self.h = x, y, w, h
        ax.add_patch(Rectangle((x, y - h), w, h, fc="white", ec=INK, lw=0.7, zorder=2))
        ax.add_patch(Rectangle((x, y - LH * 1.25), w, LH * 1.25, fc=TINT[color], ec=INK, lw=0.7, zorder=2))
        label = f"{name}" if note is None else f"{name}  {note}"
        ax.text(x + w / 2, y - LH * 0.62, label, ha="center", va="center", fontsize=8.5, zorder=3,
                style="italic" if abstract else "normal", color=INK)
        for i, m in enumerate(members):
            ax.text(x + 0.6, y - LH * 1.25 - 0.35 - LH * (i + 0.5), m, ha="left", va="center",
                    fontsize=7, family="monospace", color=INK, zorder=3)

    def __getattr__(self, side):  # anchors: top, bottom, left, right
        cx, cy = self.x + self.w / 2, self.y - self.h / 2
        return {"top": (cx, self.y), "bottom": (cx, self.y - self.h),
                "left": (self.x, cy), "right": (self.x + self.w, cy)}[side]


def link(ax, a, b, kind="uses", label=None, at=0.5, off=(0.6, 0), rad=0.0):
    """Arrow from point a to point b. kind: 'is' (inheritance), 'uses', 'has' (composition)."""
    style = {"is": "-|>,head_length=0.9,head_width=0.45", "uses": "->,head_length=0.6,head_width=0.3",
             "has": "-"}[kind]
    ax.annotate("", xy=b, xytext=a, zorder=1,
                arrowprops=dict(arrowstyle=style, fc="white", ec=INK, lw=0.7, shrinkA=0, shrinkB=0,
                                connectionstyle=f"arc3,rad={rad}"))
    if kind == "has":  # filled diamond at the owner's end
        ax.plot(*a, marker="D", ms=4, mfc=INK, mec=INK, zorder=3)
    if label:
        mx, my = a[0] + (b[0] - a[0]) * at + off[0], a[1] + (b[1] - a[1]) * at + off[1]
        ax.text(mx, my, label, fontsize=7, family="monospace", color="#4d4d4d", ha="left", va="center")


def tag(ax, x, y, s):
    ax.text(x, y, s, fontsize=10, ha="left", va="top", color=INK)


# ---- Figure 1: TP1, Haskell data types and the region used in the tests
fig, ax = canvas(74, 36)
tag(ax, 0, 36, "(a) Abstract data types")
reg = Box(ax, 0.5, 32.5, 40.5, "Region", ["Reg [City] [Link] [Tunel]", "foundR, linkR, tunelR, linkedR,",
                                          "connectedR, delayR, pathR,", "availableCapacityForR, ..."], C[0])
tun = Box(ax, 0.5, 20, 11, "Tunel", ["Tun [Link]", "connectsT, usesT,", "delayT"], C[3])
lnk = Box(ax, 14.5, 20, 13.5, "Link", ["Lin City City Quality", "connectsL, linksL,", "capacityL, delayL"], C[1])
cit = Box(ax, 30.5, 20, 10.5, "City", ["Cit String Point", "nameC, distanceC"], C[2])
qua = Box(ax, 14.5, 8.5, 13.5, "Quality", ["Qua String Int Float", "capacityQ, delayQ"], C[4])
pnt = Box(ax, 30.5, 8.5, 10.5, "Point", ["Poi Int Int", "newP, difP"], C[5])
for b, lab in ((tun, "[Tunel]"), (lnk, "[Link]"), (cit, "[City]")):
    link(ax, (b.top[0], reg.bottom[1]), b.top, "has", lab, at=0.5, off=(0.5, 0))
link(ax, tun.right, lnk.left, "uses", "[ ]", at=0.1, off=(0, 0.9))
link(ax, lnk.right, cit.left, "uses", "2", at=0.3, off=(0, 0.9))
link(ax, lnk.bottom, qua.top, "uses", "1", at=0.5, off=(0.5, 0))
link(ax, cit.bottom, pnt.top, "uses", "1", at=0.5, off=(0.5, 0))

# (b) the three-city region built in testdelayR / testusedCapacityForR (Tp1/Test.hs)
tag(ax, 45, 36, "(b) Region built in the tests")
for i, s_ in enumerate(("tunelR r [Ciudad1, Ciudad2, Ciudad3]", "connectedR r Ciudad1 Ciudad3 == True",
                        "delayR r Ciudad1 Ciudad3     == 1.5")):
    ax.text(45.5, 32.4 - 1.8 * i, s_, fontsize=7.5, family="monospace")
ox, oy, sc = 47.5, 5, 3.3
city = {"Ciudad1": (0, 0), "Ciudad2": (3, 4), "Ciudad3": (5, 6)}
P = {k: (ox + sc * x, oy + sc * y) for k, (x, y) in city.items()}
for xi in range(0, 8):
    ax.plot([ox + sc * xi] * 2, [oy - 0.6, oy - 1.1], color=INK, lw=0.5)
    ax.text(ox + sc * xi, oy - 2.1, str(xi), fontsize=7, ha="center", va="center")
ax.plot([ox - 1, ox + sc * 7.3], [oy - 0.6] * 2, color=INK, lw=0.5)
ax.text(ox + sc * 7.45, oy - 0.6, "$x$", fontsize=8, va="center")
for a, b, q in (("Ciudad1", "Ciudad2", "q1: cap 10, delay 0.5"), ("Ciudad2", "Ciudad3", "q2: cap 20, delay 1.0")):
    ax.plot(*zip(P[a], P[b]), color="#d9d9d9", lw=6, solid_capstyle="round", zorder=1)
    ax.plot(*zip(P[a], P[b]), color=C[3], lw=1.1, zorder=2)
    mx, my = (P[a][0] + P[b][0]) / 2, (P[a][1] + P[b][1]) / 2
    ax.text(mx + 1.3, my - 1.0, q, fontsize=7, family="monospace", color="#4d4d4d", va="center")
for k, (px, py) in P.items():
    ax.plot(px, py, "o", ms=6, mfc=TINT[C[2]], mec=C[2], mew=1, zorder=3)
    x, y = city[k]
    ax.text(px + 1.2, py + 0.9, f"{k} ({x},{y})", fontsize=7.5, ha="left", va="center")
save(fig, "fig1-telco-adt.svg")

# ---- Figure 2: TP2, a queue without if statements
fig, ax = canvas(74, 26)
tag(ax, 0, 26, "(a) Classes")
q = Box(ax, 0.5, 22.5, 24, "Queue", ["- queue: ArrayList<Status>", "+ add(o), take(), head()", "+ isEmpty(), size()",
                                     "+ takeNotEmpty()", "+ headNotEmpty()"], C[0])
st = Box(ax, 29, 22.5, 14, "Status", ["isEmpty()", "take(q)", "head(q)", "getObject()"], C[5], abstract=True)
em = Box(ax, 22, 7.5, 11, "Empty", ["take: throw", "head: throw"], C[1])
ne = Box(ax, 35, 7.5, 13, "NotEmpty", ["object", "take: q.take...", "head: q.head..."], C[2])
link(ax, q.right, st.left, "has", "*", at=0.5, off=(-0.3, 0.9))
link(ax, em.top, (33, st.bottom[1]), "is")
link(ax, ne.top, (39, st.bottom[1]), "is")

tag(ax, 50, 26, "(b) new Queue().add(A).add(B)")
cells = [("Empty", C[1]), ("NotEmpty\n\"A\"", C[2]), ("NotEmpty\n\"B\"", C[2])]
for i, (s, c) in enumerate(cells):
    x0 = 51 + 7.4 * i
    ax.add_patch(Rectangle((x0, 12), 7.4, 5.5, fc=TINT[c], ec=INK, lw=0.7))
    ax.text(x0 + 3.7, 14.75, s, ha="center", va="center", fontsize=7, family="monospace", linespacing=1.3)
    ax.text(x0 + 3.7, 11.0, f"[{i}]", ha="center", va="center", fontsize=7, family="monospace", color=GRAY)
link(ax, (51 + 7.4 * 2.5, 21.5), (51 + 7.4 * 2.5, 17.7), "uses")
ax.text(51 + 7.4 * 2.5, 22.6, "dispatch on last", ha="center", fontsize=7)
link(ax, (51 + 7.4 * 1.5, 7.6), (51 + 7.4 * 1.5, 10.0), "uses")
ax.text(51 + 7.4 * 1.5, 6.4, "take / head read [1]", ha="center", fontsize=7)
ax.text(51 + 3.7, 8.6, "sentinel", ha="center", fontsize=7, color=GRAY)
save(fig, "fig2-queue.svg")

# ---- Figure 3: TP3, the submarine
fig, ax = canvas(74, 46)
tag(ax, 0, 46, "(a) Classes")
sub = Box(ax, 23, 42.5, 22, "Submarino", ["coordenada: Coordenada", "direction: Direction", "depth: ArrayList<Depth>",
                                          "down(), up(), moveFWD()", "turnLeft(), turnRight()", "launchICBM()"], C[0])
coo = Box(ax, 0.5, 42.5, 17, "Coordenada", ["x, y: int", "xForward() ...", "yBackward()"], C[5])
dirb = Box(ax, 0.5, 26, 17, "Direction", ["turnLeft()", "turnRight()", "moveFWD(c)"], C[2], abstract=True)
dep = Box(ax, 23, 26, 22, "Depth", ["down(stack)", "up(stack)", "launchICBM(): bool"], C[4], abstract=True)
cmd = Box(ax, 51, 42.5, 22.5, "Commands", ["execute(sub)", "createMovement(String)"], C[3], abstract=True)
link(ax, sub.left, (coo.right[0], sub.left[1]), "has")
link(ax, (25, sub.bottom[1]), (12, dirb.y), "has")
link(ax, (34, sub.bottom[1]), dep.top, "has", "* (stack)", at=0.5)
link(ax, (cmd.left[0], 38.5), (sub.right[0], 38.5), "uses", "execute", at=0.0, off=(-6.5, 1.0))
for i, n in enumerate(("North", "East", "South", "West")):
    b = Box(ax, 0.5 + 4.3 * i, 12.5, 4.0, n, [], C[2])
    link(ax, b.top, (2.5 + 3.5 * i, dirb.bottom[1]), "is")
for i, n in enumerate(("Surface", "FirstLevel", "Deep")):
    b = Box(ax, 23 + 7.6 * i, 12.5, 7.0, n, [], C[4])
    link(ax, b.top, (27 + 7 * i, dep.bottom[1]), "is")
keys = [("l", "TurnLeft"), ("r", "TurnRight"), ("f", "MoveFWD"), ("d", "Down"), ("u", "Up"), ("m", "LaunchICBM"),
        ("other", "NoOperation")]
for i, (k, n) in enumerate(keys):
    y = 33.5 - LH * 1.35 * i
    b = Box(ax, 59, y, 14.5, n, [], C[3])
    ax.text(57.6, y - LH * 0.62, f"'{k}'" if k != "other" else "else", fontsize=7, family="monospace",
            ha="right", va="center", color="#4d4d4d")
ax.plot([cmd.x + 2] * 2, [cmd.y - cmd.h, 33.5 - LH * 1.35 * 6 - LH * 0.62], color=INK, lw=0.7)
ax.plot(cmd.x + 2, cmd.y - cmd.h - 0.9, marker="^", ms=6, mfc="white", mec=INK, mew=0.7)

# (b) heading cycle and the effect of moveFWD
tag(ax, 0, 8.6, "(b) Heading (turnRight cycle)")
pos = {"N": (8, 1.5), "E": (14, 1.5), "S": (20, 1.5), "W": (26, 1.5)}
eff = {"N": "x+1", "E": "y+1", "S": "x-1", "W": "y-1"}
for k, (x, y) in pos.items():
    ax.add_patch(FancyBboxPatch((x - 2.2, y - 1.1), 4.4, 2.2, boxstyle="round,pad=0.1,rounding_size=0.6",
                                fc=TINT[C[2]], ec=INK, lw=0.7))
    ax.text(x, y + 0.2, f"{k}  {eff[k]}", ha="center", va="center", fontsize=7, family="monospace")
for a, b in (("N", "E"), ("E", "S"), ("S", "W")):
    link(ax, (pos[a][0] + 2.3, 1.5), (pos[b][0] - 2.3, 1.5), "uses")
ax.annotate("", xy=(8, 2.75), xytext=(26, 2.75),
            arrowprops=dict(arrowstyle="->,head_length=0.6,head_width=0.3", ec=INK, lw=0.7,
                            connectionstyle="arc3,rad=0.25", shrinkA=0, shrinkB=0))

# (c) depth stack and launchICBM
tag(ax, 36, 8.6, "(c) Depth stack and launchICBM()")
for i, (n, ok) in enumerate((("Surface", "true"), ("FirstLevel", "true"), ("Deep", "false"), ("Deep", "false"))):
    x = 40 + 8.6 * i
    ax.add_patch(FancyBboxPatch((x - 3.4, 0.4), 6.8, 2.2, boxstyle="round,pad=0.1,rounding_size=0.6",
                                fc=TINT[C[4]], ec=INK, lw=0.7))
    ax.text(x, 1.5, n, ha="center", va="center", fontsize=7, family="monospace")
    ax.text(x, -0.9, ok, ha="center", va="center", fontsize=7, family="monospace",
            color=C[2] if ok == "true" else C[1])
    if i < 3:
        link(ax, (x + 3.5, 1.9), (x + 5.1, 1.9), "uses")
        link(ax, (x + 5.1, 1.1), (x + 3.5, 1.1), "uses")
ax.text(72.5, 4.1, "down →   ← up", fontsize=6.5, color=GRAY, ha="right")
save(fig, "fig3-submarine.svg")

# ---- Figure 4: TP4, Connect Four
fig, ax = canvas(74, 40)
tag(ax, 0, 40, "(a) Classes")
lin = Box(ax, 14, 36.5, 22, "Linea", ["static gameBoard", "turn: Turn, modo: Mode", "playRedAt(c), playBlueAt(c)",
                                      "finished(), show()"], C[0])
gam = Box(ax, 0.5, 36.5, 10, "Game", ["main()"], C[5])
trn = Box(ax, 0.5, 22, 19, "Turn", ["RedTurn(col, t)", "BlueTurn(col, t)"], C[1], abstract=True)
mod = Box(ax, 23, 22, 19, "Mode", ["checkWin(l, col, p)", "selectMode(char)"], C[2], abstract=True)
link(ax, gam.right, (lin.left[0], gam.right[1]), "uses")
link(ax, (19, lin.bottom[1]), (10, trn.y), "has")
link(ax, (31, lin.bottom[1]), (32.5, mod.y), "has")
for i, n in enumerate(("RedTurn", "BlueTurn", "End")):
    b = Box(ax, 0.5 + 6.6 * i, 10, 6.0, n, [], C[1])
    link(ax, b.top, (3.5 + 6.6 * i, trn.bottom[1]), "is")
modes = (("AMode", "vertical +", "horizontal"), ("BMode", "diagonals", ""), ("CMode", "A or B", ""))
for i, (n, d1, d2) in enumerate(modes):
    b = Box(ax, 23 + 6.6 * i, 10, 6.0, n, [], C[2])
    link(ax, b.top, (26 + 6.6 * i, mod.bottom[1]), "is")
    ax.text(26 + 6.6 * i, 6.7, d1, ha="center", fontsize=6.5, color="#4d4d4d")
    ax.text(26 + 6.6 * i, 5.3, d2, ha="center", fontsize=6.5, color="#4d4d4d")
ax.text(0.5, 4.2, "RedTurn → BlueTurn → RedTurn ... ; a win or a full board → End;", fontsize=6.5,
        color="#4d4d4d")
ax.text(0.5, 2.6, "playing out of turn or after End throws RuntimeException", fontsize=6.5, color="#4d4d4d")

# (b) the position reached in LineaTest.testRedWinsDiagonal (4 x 4 board, mode 'B')
tag(ax, 48, 40, "(b) testRedWinsDiagonal, mode B")
moves = [1, 2, 2, 3, 3, 4, 3, 4, 4, 1, 4]  # columns, alternating red / blue, as in the test
height, cols = [0] * 4, 4
s, bx, by = 5.5, 50, 9.5
ax.add_patch(Rectangle((bx - 0.6, by - 0.6), cols * s + 1.2, 4 * s + 1.2, fc=TINT[C[0]], ec=INK, lw=0.7))
for c in range(cols):
    for r in range(4):
        ax.add_patch(plt.Circle((bx + s * (c + 0.5), by + s * (r + 0.5)), s * 0.38, fc="white", ec=INK, lw=0.5))
for i, m in enumerate(moves):
    r = height[m - 1]
    height[m - 1] += 1
    red = i % 2 == 0
    ax.add_patch(plt.Circle((bx + s * (m - 0.5), by + s * (r + 0.5)), s * 0.38, fc=C[1] if red else C[0],
                            ec=INK, lw=0.5))
    ax.text(bx + s * (m - 0.5), by + s * (r + 0.5), str(i + 1), ha="center", va="center", fontsize=7,
            color="white")
ax.plot([bx + s * 0.5, bx + s * 3.5], [by + s * 0.5, by + s * 3.5], color=INK, lw=1.2, alpha=0.6)
for c in range(cols):
    ax.text(bx + s * (c + 0.5), by - 2.0, str(c + 1), ha="center", fontsize=7)
ax.text(bx + s * 2, by - 4.4, "column", ha="center", fontsize=7)
ax.text(bx + s * 2, by + 4 * s + 1.6, "red X (odd moves)  ·  blue O (even)", ha="center", fontsize=7,
        color="#4d4d4d")
save(fig, "fig4-connect-four.svg")
