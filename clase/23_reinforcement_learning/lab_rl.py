"""
lab_rl.py — Genera las imágenes pedagógicas para clase/23_reinforcement_learning/

Ejecución:
    cd clase/23_reinforcement_learning && python lab_rl.py

Genera 7 imágenes en:
    clase/23_reinforcement_learning/images/

Dependencias: numpy, matplotlib
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from matplotlib.gridspec import GridSpec
import numpy as np

# ── Styling ───────────────────────────────────────────────────────────────────
plt.style.use("seaborn-v0_8-whitegrid")

COLORS = {
    "blue":   "#2E86AB",
    "red":    "#E94F37",
    "green":  "#27AE60",
    "gray":   "#7F8C8D",
    "orange": "#F39C12",
    "purple": "#8E44AD",
    "light":  "#ECF0F1",
    "dark":   "#2C3E50",
    "teal":   "#1ABC9C",
    "yellow": "#F1C40F",
}

plt.rcParams.update({
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "figure.dpi": 160,
})

ROOT       = Path(__file__).resolve().parent
IMAGES_DIR = ROOT / "images"
IMAGES_DIR.mkdir(exist_ok=True)

np.random.seed(42)

# ── Staircase problem (module 21 reused, rewards = -costs) ───────────────────
COSTS   = np.array([3, 2, 5, 10, 1, 0])
REWARDS = -COSTS.astype(float)   # r_i = -c_i
N       = len(COSTS)              # 6 states: 0..5
GOAL    = N - 1                   # state 5

# Actions: 0 = subir 1, 1 = saltar 2
# From state 4: only action 0 (state 6 doesn't exist)
A_LABELS = ["subir 1", "saltar 2"]

# Q* table (γ=1, analytically verified):
#   rows = states 0..4  (state 5 is terminal)
#   cols = actions +1, +2
_Q_STAR_DATA = [
    [-8.0, -6.0],    # s=0  argmax = +2 (col 1)
    [-6.0, -10.0],   # s=1  argmax = +1 (col 0)
    [-10.0, -1.0],   # s=2  argmax = +2 (col 1)
    [-1.0,  0.0],    # s=3  argmax = +2 (col 1)
    [ 0.0,  np.nan], # s=4  argmax = +1 (col 0), +2 unavailable
]
Q_STAR = np.array(_Q_STAR_DATA)   # shape (5, 2)

OPT_POLICY = [1, 0, 1, 1, 0]     # argmax col per state 0..4
OPT_TRAJ   = [0, 2, 4, 5]
OPT_RETURN = -6.0

# Q tables after designed episode traces (identical for SARSA & Q-learning)
# Episode 1: 0 →(+1)→ 1 →(+2)→ 3 →(+2)→ 5
# Episode 2: 0 →(+2)→ 2 →(+2)→ 4 →(+1)→ 5
Q_AFTER_EP1 = np.zeros((5, 2))
Q_AFTER_EP1[0, 0] = -1.0
Q_AFTER_EP1[1, 1] = -5.0

Q_AFTER_EP2 = Q_AFTER_EP1.copy()
Q_AFTER_EP2[0, 1] = -2.5
Q_AFTER_EP2[2, 1] = -0.5


# ── RL algorithms ─────────────────────────────────────────────────────────────

def _available(s):
    """Available action indices from state s."""
    if s == GOAL:
        return []
    return [0] if s == GOAL - 1 else [0, 1]


def _step(s, a):
    s2 = s + (1 if a == 0 else 2)
    return s2, float(REWARDS[s2])


def _eps_greedy(Q_full, s, eps, rng):
    avail = _available(s)
    if len(avail) == 1:
        return avail[0]
    if rng.random() < eps:
        return int(rng.choice(avail))
    q = [Q_full[s, a] for a in avail]
    return avail[int(np.argmax(q))]


def _run_sarsa(n_ep=200, alpha=0.5, gamma=1.0, eps=0.4, seed=0):
    rng = np.random.default_rng(seed)
    Q = np.zeros((N, 2))
    returns = []
    for _ in range(n_ep):
        s = 0
        a = _eps_greedy(Q, s, eps, rng)
        G = 0.0
        while s != GOAL:
            s2, r = _step(s, a)
            G += r
            a2 = _eps_greedy(Q, s2, eps, rng) if s2 != GOAL else 0
            tgt = r + gamma * (Q[s2, a2] if s2 != GOAL else 0.0)
            Q[s, a] += alpha * (tgt - Q[s, a])
            s, a = s2, a2
        returns.append(G)
    return Q, returns


def _run_qlearning(n_ep=200, alpha=0.5, gamma=1.0, eps=0.4, seed=0):
    rng = np.random.default_rng(seed)
    Q = np.zeros((N, 2))
    returns = []
    for _ in range(n_ep):
        s = 0
        G = 0.0
        while s != GOAL:
            a = _eps_greedy(Q, s, eps, rng)
            s2, r = _step(s, a)
            G += r
            avail2 = _available(s2)
            max_q2 = max(Q[s2, aa] for aa in avail2) if avail2 else 0.0
            Q[s, a] += alpha * (r + gamma * max_q2 - Q[s, a])
            s = s2
        returns.append(G)
    return Q, returns


def _save(fig, name):
    fig.savefig(IMAGES_DIR / name, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {name}")


# ── Plot helpers ──────────────────────────────────────────────────────────────

def _fancy_box(ax, x, y, w, h, label, sublabel="", facecolor=COLORS["light"],
               edgecolor=COLORS["dark"], fontsize=12):
    box = FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                         boxstyle="round,pad=0.05",
                         facecolor=facecolor, edgecolor=edgecolor,
                         linewidth=1.8, zorder=3)
    ax.add_patch(box)
    ytext = y + 0.07 if sublabel else y
    ax.text(x, ytext, label, ha="center", va="center",
            fontsize=fontsize, fontweight="bold", color=COLORS["dark"], zorder=4)
    if sublabel:
        ax.text(x, y - 0.14, sublabel, ha="center", va="center",
                fontsize=9, color=COLORS["gray"], zorder=4)


def _arrow(ax, x1, y1, x2, y2, label="", color=COLORS["dark"], fontsize=10):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.8))
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx, my + 0.07, label, ha="center", va="bottom",
                fontsize=fontsize, color=color)


def _draw_q_table(ax, Q_data, title, show_star=False):
    """Draw a Q-table as an annotated grid on ax."""
    ax.set_aspect("equal")
    ax.set_xlim(-0.1, 2.1)
    ax.set_ylim(-0.1, 5.6)
    ax.set_axis_off()
    ax.set_title(title, fontsize=11, color=COLORS["dark"], pad=4)

    col_labels = ["$+1$\n(subir 1)", "$+2$\n(saltar 2)"]
    row_labels = [f"$s={i}$" for i in range(5)]

    cw, rh = 0.9, 0.95

    # Header row
    for j, cl in enumerate(col_labels):
        ax.text(0.55 + j * cw, 5.25, cl, ha="center", va="center",
                fontsize=9, color=COLORS["dark"], fontweight="bold")

    # Data cells
    for i in range(5):
        ax.text(0.05, 5.25 - (i + 1) * rh + rh / 2, row_labels[i],
                ha="center", va="center", fontsize=9,
                color=COLORS["dark"], fontweight="bold")

        for j in range(2):
            x = 0.55 + j * cw
            y = 5.25 - (i + 1) * rh + rh / 2

            if np.isnan(Q_data[i, j]):
                val_str = "—"
                fc = COLORS["light"]
            elif Q_data[i, j] == 0.0 and not show_star:
                val_str = "0"
                fc = "#FFFFFF"
            else:
                val_str = f"{Q_data[i, j]:.1f}" if Q_data[i, j] != 0.0 else "0"
                fc = "#FFFFFF"

            rect = plt.Rectangle((x - cw / 2 + 0.02, y - rh / 2 + 0.03),
                                  cw - 0.04, rh - 0.06,
                                  facecolor=fc, edgecolor=COLORS["gray"],
                                  linewidth=0.8, zorder=2)
            ax.add_patch(rect)

            is_star = (show_star and not np.isnan(Q_data[i, j]) and
                       j == OPT_POLICY[i])
            star_suffix = " [opt]" if is_star else ""
            color = COLORS["blue"] if is_star else COLORS["dark"]

            ax.text(x, y, val_str + star_suffix, ha="center", va="center",
                    fontsize=9.5, color=color,
                    fontweight="bold" if is_star else "normal", zorder=3)


# ============================================================================
# Plot 1 — Agent-environment loop
# ============================================================================
def plot_agent_env_loop():
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5.5)
    ax.set_axis_off()
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")

    # ── AGENTE box (left) ────────────────────────────────────────────────────
    box_agent = FancyBboxPatch((0.3, 1.2), 3.8, 3.0,
                               boxstyle="round,pad=0.08",
                               facecolor="#EBF5FB", edgecolor=COLORS["blue"],
                               linewidth=2, zorder=3)
    ax.add_patch(box_agent)
    ax.text(2.2, 3.95, "AGENTE", ha="center", va="center",
            fontsize=13, fontweight="bold", color=COLORS["blue"], zorder=4)
    ax.text(2.2, 3.30, "mantiene $Q[s, a]$", ha="center", va="center",
            fontsize=9.5, color=COLORS["dark"], zorder=4)
    ax.text(2.2, 2.75, "elige $a_t$ con $\\varepsilon$-greedy$(Q, s_t)$", ha="center", va="center",
            fontsize=9.5, color=COLORS["dark"], zorder=4)
    ax.text(2.2, 2.20, "actualiza $Q$ con $(s_t, a_t, r_{t+1}, s_{t+1})$", ha="center", va="center",
            fontsize=9.5, color=COLORS["dark"], zorder=4)
    ax.text(2.2, 1.55, "(no conoce $T$ ni $R$)", ha="center", va="center",
            fontsize=8.5, color=COLORS["gray"], style="italic", zorder=4)

    # ── AMBIENTE box (right) ─────────────────────────────────────────────────
    box_env = FancyBboxPatch((5.9, 1.2), 3.8, 3.0,
                             boxstyle="round,pad=0.08",
                             facecolor="#FDFEFE", edgecolor=COLORS["gray"],
                             linewidth=2, zorder=3)
    ax.add_patch(box_env)
    ax.text(7.8, 3.95, "AMBIENTE", ha="center", va="center",
            fontsize=13, fontweight="bold", color=COLORS["gray"], zorder=4)
    ax.text(7.8, 3.30, "escalera con costos escondidos", ha="center", va="center",
            fontsize=9.5, color=COLORS["dark"], zorder=4)
    ax.text(7.8, 2.75, "conoce $T(s'|s,a)$ y $R(s,a,s')$", ha="center", va="center",
            fontsize=9.5, color=COLORS["dark"], zorder=4)
    ax.text(7.8, 2.20, "pero no los revela al agente", ha="center", va="center",
            fontsize=9.5, color=COLORS["dark"], zorder=4)
    ax.text(7.8, 1.55, "(caja negra para el agente)", ha="center", va="center",
            fontsize=8.5, color=COLORS["gray"], style="italic", zorder=4)

    # ── Action arrow (top, left to right) ────────────────────────────────────
    ax.annotate("", xy=(5.85, 3.7), xytext=(4.15, 3.7),
                arrowprops=dict(arrowstyle="-|>", color=COLORS["orange"], lw=2.2))
    ax.text(5.0, 4.0, "$a_t$  (acción)", ha="center", va="bottom",
            fontsize=11, color=COLORS["orange"], fontweight="bold")

    # ── Observation arrow (bottom, right to left) ────────────────────────────
    ax.annotate("", xy=(4.15, 1.7), xytext=(5.85, 1.7),
                arrowprops=dict(arrowstyle="-|>", color=COLORS["blue"], lw=2.2))
    ax.text(5.0, 1.35, "$s_{t+1},\\ r_{t+1}$  (observación)", ha="center", va="top",
            fontsize=11, color=COLORS["blue"], fontweight="bold")

    ax.set_title(
        "Bucle agente-ambiente: el agente actúa, observa y aprende — sin ver $T$ ni $R$",
        fontsize=12, color=COLORS["dark"], pad=10)

    _save(fig, "01_agent_env_loop.png")


# ============================================================================
# Plot 2 — Staircase with reward labels
# ============================================================================
def plot_staircase_rewards():
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.set_axis_off()
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")

    sw, sh = 1.5, 0.7
    for i in range(N):
        x0, y0 = i * sw, i * sh
        fc = COLORS["green"] if i == GOAL else COLORS["light"]
        ec = COLORS["green"] if i == GOAL else COLORS["gray"]
        rect = plt.Rectangle((x0, y0), sw, sh,
                              facecolor=fc, edgecolor=ec, linewidth=1.5, zorder=2)
        ax.add_patch(rect)
        ax.text(x0 + sw / 2, y0 + sh * 0.62, f"$s = {i}$",
                ha="center", va="center", fontsize=10,
                color=COLORS["dark"], fontweight="bold")
        r_str = ("$r = 0$\n(meta)" if i == GOAL
                 else f"$r = {int(REWARDS[i])}$")
        ax.text(x0 + sw / 2, y0 + sh * 0.25, r_str,
                ha="center", va="center", fontsize=9,
                color=COLORS["red"] if REWARDS[i] < 0 else COLORS["green"])

    # Actions
    arrowkw = dict(arrowstyle="-|>", lw=1.8)
    for i in range(N - 1):
        x_from = i * sw + sw
        y_from = i * sh + sh
        x_to1  = (i + 1) * sw + sw / 2
        y_to1  = (i + 1) * sh + sh
        ax.annotate("", xy=(x_to1, y_to1 + 0.12),
                    xytext=(x_from - 0.05, y_from + 0.12),
                    arrowprops=dict(color=COLORS["blue"], **arrowkw))
        if i < N - 2:
            x_to2 = (i + 2) * sw + sw / 2
            y_to2 = (i + 2) * sh + sh
            ax.annotate("", xy=(x_to2, y_to2 + 0.28),
                        xytext=(x_from - 0.05, y_from + 0.28),
                        arrowprops=dict(color=COLORS["orange"], **arrowkw))

    ax.plot([], [], color=COLORS["blue"], lw=2, label="subir 1 (+1)")
    ax.plot([], [], color=COLORS["orange"], lw=2, label="saltar 2 (+2)")
    ax.legend(loc="upper left", fontsize=10)

    ax.text(N * sw / 2, -0.55,
            "Las recompensas son $r_i = -c_i$ — mismo problema que módulo 21, "
            "signo invertido (maximizamos recompensas)",
            ha="center", fontsize=10, color=COLORS["gray"], style="italic")

    ax.set_xlim(-0.3, N * sw + 0.3)
    ax.set_ylim(-0.8, N * sh + 1.2)
    ax.set_title("La escalera con recompensas $r_i = -c_i$", fontsize=13,
                 color=COLORS["dark"], pad=8)
    _save(fig, "02_staircase_rewards.png")


# ============================================================================
# Plot 3 — Empty Q-table
# ============================================================================
def plot_q_table_empty():
    fig, ax = plt.subplots(figsize=(7, 7))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    Q_empty = np.full((5, 2), 0.0)
    Q_empty[4, 1] = np.nan

    cw, rh = 1.2, 0.85          # cell width, cell height (data units)
    x0 = 0.30                    # x-center of column 0
    header_h = 0.44              # height of column header band
    y0 = 4.25                    # y-center of row 0 (positioned below header)
    grid_cx = x0 + 0.5 * cw     # horizontal center of the two-column grid

    # header sits above row 0 with a small gap
    header_bot = y0 + rh * 0.5 + 0.08
    header_cy  = header_bot + header_h / 2

    ax.set_xlim(-1.2, 4.2)
    ax.set_ylim(-1.5, 6.4)
    ax.set_axis_off()

    # Title
    ax.text(grid_cx, 6.1,
            "Tabla $Q(s, a)$ — inicio del aprendizaje",
            ha="center", va="center",
            fontsize=12, fontweight="bold", color=COLORS["dark"])
    ax.text(grid_cx, 5.74,
            "Cada celda = retorno esperado si estoy en $s$, tomo $a$ y luego actúo óptimamente",
            ha="center", va="center",
            fontsize=8.5, color=COLORS["gray"], style="italic")

    # Column headers
    col_labels = ["Acción $+1$", "Acción $+2$"]
    for j, cl in enumerate(col_labels):
        hx = x0 + j * cw
        rect = plt.Rectangle(
            (hx - cw / 2 + 0.05, header_bot), cw - 0.10, header_h,
            facecolor=COLORS["blue"], edgecolor="white", linewidth=0.5, zorder=2)
        ax.add_patch(rect)
        ax.text(hx, header_cy, cl, ha="center", va="center",
                fontsize=10, color="white", fontweight="bold", zorder=3)

    # Rows: label + cells
    for i in range(5):
        ry = y0 - i * rh

        # Row label — well to the left of the grid
        ax.text(-0.55, ry, f"$s = {i}$",
                ha="center", va="center",
                fontsize=11, color=COLORS["dark"], fontweight="bold")

        for j in range(2):
            cx = x0 + j * cw
            na = np.isnan(Q_empty[i, j])
            fc = "#D5D8DC" if na else "#FDFEFE"

            rect = plt.Rectangle(
                (cx - cw / 2 + 0.05, ry - rh / 2 + 0.05),
                cw - 0.10, rh - 0.10,
                facecolor=fc, edgecolor=COLORS["gray"], linewidth=1.0, zorder=2)
            ax.add_patch(rect)

            if na:
                ax.text(cx, ry, "—", ha="center", va="center",
                        fontsize=20, color=COLORS["gray"], zorder=3)
            else:
                ax.text(cx, ry, "0", ha="center", va="center",
                        fontsize=20, color=COLORS["dark"],
                        fontweight="bold", zorder=3)

    # Arrow annotation for the unavailable cell
    na_ry = y0 - 4 * rh
    na_cx = x0 + cw
    right_edge = na_cx + cw / 2 - 0.06

    ax.annotate(
        "Acción $+2$ no disponible\ndesde $s = 4$",
        xy=(right_edge, na_ry),
        xytext=(right_edge + 0.40, na_ry),
        ha="left", va="center",
        fontsize=8.5, color=COLORS["gray"], style="italic",
        arrowprops=dict(arrowstyle="->", color=COLORS["gray"],
                        lw=0.9, connectionstyle="arc3,rad=0.0"))

    # Bottom note
    ax.text(grid_cx, -1.05,
            "Al principio no sabemos nada → todo se inicializa en 0.\n"
            "Con cada episodio, las celdas visitadas se actualizan.",
            ha="center", va="center",
            fontsize=9, color=COLORS["dark"], style="italic",
            bbox=dict(boxstyle="round,pad=0.35", facecolor="#EBF5FB",
                      edgecolor=COLORS["blue"], alpha=0.7))

    _save(fig, "03_q_table_empty.png")


# ============================================================================
# Plot 4 — Q-table evolution (3 snapshots: ep0, ep1, ep2)
# ============================================================================
def plot_q_table_evolution():
    # Q tables at the divergence point (ep 3, step 1: s=0, a=+2, r=-5, s'=2)
    Q_sarsa_ep3 = Q_AFTER_EP2.copy()
    Q_sarsa_ep3[0, 1] = -4.00   # SARSA uses the actual next action (explored +2)

    Q_ql_ep3 = Q_AFTER_EP2.copy()
    Q_ql_ep3[0, 1] = -3.75      # Q-learning uses max (greedy +1 value = 0)

    fig = plt.figure(figsize=(13, 9.5))

    # ── Top row: 3 identical snapshots ──────────────────────────────────────
    gs_top = GridSpec(1, 3, figure=fig,
                      left=0.04, right=0.96, top=0.86, bottom=0.50, wspace=0.38)

    fig.text(0.50, 0.92,
             "Episodios 1 y 2 — tabla idéntica para SARSA y Q-learning",
             ha="center", fontsize=12, fontweight="bold", color=COLORS["dark"])

    stages = [
        (np.zeros((5, 2)),  "Inicial\n(antes del ep. 1)"),
        (Q_AFTER_EP1,       "Después del ep. 1\n(0→1→3→5)"),
        (Q_AFTER_EP2,       "Después del ep. 2\n(0→2→4→5)"),
    ]
    for k, (Q, title) in enumerate(stages):
        Q_plot = Q.copy()
        Q_plot[4, 1] = np.nan
        ax = fig.add_subplot(gs_top[0, k])
        _draw_q_table(ax, Q_plot, title)
        ax.set_aspect("auto")

    # Divider
    line = plt.Line2D([0.04, 0.96], [0.48, 0.48],
                      color=COLORS["gray"], linewidth=1.5,
                      transform=fig.transFigure, zorder=10)
    fig.add_artist(line)

    # ── Bottom row: divergence ───────────────────────────────────────────────
    gs_bot = GridSpec(1, 2, figure=fig,
                      left=0.12, right=0.88, top=0.44, bottom=0.05, wspace=0.55)

    fig.text(0.50, 0.47,
             "Episodio 3, paso 1 — ¡las tablas divergen!   "
             "($s=0,\\ a=+2,\\ r=-5,\\ s'=2$)",
             ha="center", fontsize=12, fontweight="bold", color=COLORS["red"])

    cw, rh = 0.9, 0.95   # cell geometry (must match _draw_q_table)

    diverge_panels = [
        (Q_sarsa_ep3,  "SARSA  (on-policy)",  COLORS["blue"],
         -3.0, -4.00,
         "Usó $a'=+2$ (exploró en $s'=2$)\n"
         r"$\delta=-5+(-0.5)-(-2.5)=-3.0$"),
        (Q_ql_ep3,     "Q-learning  (off-policy)", COLORS["orange"],
         -2.5, -3.75,
         "Usó $\\max$ en $s'=2$ = 0\n"
         r"$\delta=-5+0-(-2.5)=-2.5$"),
    ]

    for k, (Q_div, algo_title, algo_color, delta, new_val, note) in enumerate(diverge_panels):
        Q_plot = Q_div.copy()
        Q_plot[4, 1] = np.nan
        ax = fig.add_subplot(gs_bot[0, k])
        _draw_q_table(ax, Q_plot, "")
        ax.set_aspect("auto")

        # Colored algorithm title
        ax.set_title(algo_title, fontsize=12, fontweight="bold",
                     color=algo_color, pad=6)

        # Highlight the changed cell: s=0 (i=0), action +2 (j=1)
        x_cell = 0.55 + 1 * cw
        y_cell = 5.25 - 1 * rh + rh / 2   # i=0 → row 0
        hl = plt.Rectangle(
            (x_cell - cw / 2 + 0.02, y_cell - rh / 2 + 0.03),
            cw - 0.04, rh - 0.06,
            facecolor="#FDEDEC", edgecolor=COLORS["red"],
            linewidth=2.5, zorder=4)
        ax.add_patch(hl)
        ax.text(x_cell, y_cell, f"{new_val:.2f}",
                ha="center", va="center",
                fontsize=10.5, color=COLORS["red"],
                fontweight="bold", zorder=5)

        # Note below the table
        ax.text(1.00, 0.05, note,
                ha="center", va="bottom", fontsize=9,
                color=algo_color, style="italic",
                transform=ax.transData)

    _save(fig, "04_q_table_evolution.png")


# ============================================================================
# Plot 5 — Converged Q* table with optimal policy
# ============================================================================
def plot_q_table_converged():
    fig, ax = plt.subplots(figsize=(5.5, 5.5))
    Q_plot = Q_STAR.copy()
    _draw_q_table(ax, Q_plot, "$Q^*$ convergida (Q-learning, ~100 episodios)",
                  show_star=True)

    ax.text(1.05, -0.08,
            "[opt] = $\\arg\\max_a Q^*(s,a)$ — la acción óptima\n"
            "Trayectoria: $0 \\to 2 \\to 4 \\to 5$ — retorno $= -6$ (igual que módulo 21)",
            ha="center", va="top", fontsize=9, color=COLORS["dark"],
            style="italic", transform=ax.transData)
    _save(fig, "05_q_table_converged.png")


# ============================================================================
# Plot 6 — Learning curves (SARSA vs Q-learning)
# ============================================================================
def plot_learning_curves():
    sarsa_Q, sarsa_ret = _run_sarsa(n_ep=300, seed=42)
    ql_Q, ql_ret      = _run_qlearning(n_ep=300, seed=42)

    def _smooth(x, w=15):
        return np.convolve(x, np.ones(w) / w, mode="valid")

    fig, ax = plt.subplots(figsize=(9, 4))

    eps = np.arange(1, len(sarsa_ret) + 1)
    ax.plot(eps, sarsa_ret, alpha=0.25, color=COLORS["blue"])
    ax.plot(eps[:len(_smooth(sarsa_ret))],
            _smooth(sarsa_ret), color=COLORS["blue"],
            lw=2.2, label="SARSA (promedio móvil)")

    ax.plot(eps, ql_ret, alpha=0.25, color=COLORS["orange"])
    ax.plot(eps[:len(_smooth(ql_ret))],
            _smooth(ql_ret), color=COLORS["orange"],
            lw=2.2, label="Q-learning (promedio móvil)")

    ax.axhline(OPT_RETURN, color=COLORS["green"], ls="--", lw=1.5,
               label=f"Retorno óptimo = {OPT_RETURN}")
    ax.set_xlabel("Episodio", fontsize=11)
    ax.set_ylabel("Retorno del episodio", fontsize=11)
    ax.set_title("Curvas de aprendizaje — SARSA vs Q-learning\n"
                 "(escalera, $\\alpha=0.5$, $\\gamma=1$, $\\varepsilon=0.4$, 300 episodios)",
                 fontsize=12, color=COLORS["dark"])
    ax.legend(fontsize=10)
    ax.set_ylim(-35, 2)
    _save(fig, "06_learning_curves.png")


# ============================================================================
# Plot 7 — RL landscape schematic
# ============================================================================
def plot_rl_landscape():
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 5.5)
    ax.set_axis_off()
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")

    # Central: Tabular RL
    _fancy_box(ax, 5.5, 3.8, 2.8, 0.9,
               "RL Tabular",
               "SARSA / Q-learning\n(este módulo)",
               facecolor="#EBF5FB", edgecolor=COLORS["blue"], fontsize=11)

    # Off-policy branch (right)
    _fancy_box(ax, 8.7, 2.4, 2.4, 0.75,
               "Off-policy",
               "Q-learning → DQN",
               facecolor="#FEF9E7", edgecolor=COLORS["orange"], fontsize=10)
    _fancy_box(ax, 8.7, 1.3, 2.4, 0.75,
               "DQN / Rainbow",
               "Atari, juegos",
               facecolor=COLORS["light"], edgecolor=COLORS["gray"], fontsize=9)

    # On-policy branch (left)
    _fancy_box(ax, 2.3, 2.4, 2.4, 0.75,
               "On-policy",
               "SARSA → PPO",
               facecolor="#EAFAF1", edgecolor=COLORS["green"], fontsize=10)
    _fancy_box(ax, 2.3, 1.3, 2.4, 0.75,
               "PPO / A3C",
               "Robótica, NLP",
               facecolor=COLORS["light"], edgecolor=COLORS["gray"], fontsize=9)

    # Function approximation node (center-bottom)
    _fancy_box(ax, 5.5, 1.85, 2.6, 0.75,
               "Aproximación de funciones",
               "$Q(s,a) \\approx f_\\theta(s,a)$ — redes neuronales",
               facecolor="#F5EEF8", edgecolor=COLORS["purple"], fontsize=9)

    # Arrows
    def _arr(x1, y1, x2, y2, col=COLORS["dark"]):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=1.6))

    _arr(5.5, 3.35, 8.7, 2.77, COLORS["orange"])
    _arr(5.5, 3.35, 2.3, 2.77, COLORS["green"])
    _arr(8.7, 2.02, 8.7, 1.67)
    _arr(2.3, 2.02, 2.3, 1.67)
    _arr(5.5, 3.35, 5.5, 2.22, COLORS["purple"])

    ax.text(7.2, 3.25, "off-policy", fontsize=9, color=COLORS["orange"],
            style="italic", rotation=-20)
    ax.text(3.3, 3.25, "on-policy", fontsize=9, color=COLORS["green"],
            style="italic", rotation=20)
    ax.text(5.52, 2.85, "$|S||A|$ explota →\nfunción aprox.",
            fontsize=8, color=COLORS["purple"], ha="center")

    ax.set_title("El paisaje del aprendizaje por refuerzo — de lo tabular hacia lo profundo",
                 fontsize=12, color=COLORS["dark"], pad=8)
    _save(fig, "07_rl_landscape.png")


# ============================================================================
# Entry point
# ============================================================================
def main():
    print(f"Saving images to: {IMAGES_DIR}")
    plot_agent_env_loop()
    plot_staircase_rewards()
    plot_q_table_empty()
    plot_q_table_evolution()
    plot_q_table_converged()
    plot_learning_curves()
    plot_rl_landscape()
    print("Done.")


if __name__ == "__main__":
    main()
