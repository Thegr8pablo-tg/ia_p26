"""
lab_bellman_dp.py — Genera las imágenes pedagógicas para clase/21_programacion_dinamica/

Ejecución:
    cd clase/21_programacion_dinamica && python lab_bellman_dp.py
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
from pathlib import Path

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

# ── Running example — the staircase ────────────────────────────────────────────
# States 0..5, costs per step. Action set: {subir 1, saltar 2}. Goal = state 5.
COSTS       = np.array([3, 2, 7, 1, 4, 0])
N_STATES    = len(COSTS)
GOAL        = N_STATES - 1

# ── Pre-verified deterministic values (see design doc D2) ──────────────────────
V_DET       = np.array([6, 3, 8, 1, 4, 0])
POLICY_DET  = ["subir 1", "saltar 2", "subir 1", "saltar 2", "subir 1", "—"]
TRAJ_DET    = [0, 1, 3, 5]
COST_DET    = 6

# ── Pre-verified stochastic values ─────────────────────────────────────────────
# Action "saltar 2" lands at i+2 w.p. 0.8, slips to i+1 w.p. 0.2.
# From state 4 only "subir 1" is available (i+2 > 5).
P_SUCCESS   = 0.8
P_SLIP      = 0.2
V_STOCH     = np.array([8.2, 5.2, 8.8, 1.8, 4.0, 0.0])
POLICY_STOCH = ["subir 1", "saltar 2", "subir 1", "saltar 2", "subir 1", "—"]


def _save(fig, name):
    fig.savefig(IMAGES_DIR / name, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {name}")


# ── Drawing helpers ────────────────────────────────────────────────────────────
def _draw_staircase(ax, costs, x0=0.0, y0=0.0, step_w=1.2, step_h=0.6,
                    face=None, edge=None, highlight_states=None,
                    show_cost=True, show_state=True, cost_label_fmt="c={v}"):
    """Draw a staircase profile with labeled steps."""
    face = face or COLORS["light"]
    edge = edge or COLORS["dark"]
    highlight_states = highlight_states or {}

    for i in range(len(costs)):
        x = x0 + i * step_w
        y = y0 + i * step_h
        fc = highlight_states.get(i, face)
        rect = Rectangle((x, y), step_w, step_h, facecolor=fc,
                         edgecolor=edge, linewidth=1.4, zorder=2)
        ax.add_patch(rect)
        if show_state:
            ax.text(x + step_w / 2, y + step_h / 2 + 0.05, f"$i={i}$",
                    ha="center", va="center", fontsize=11, fontweight="bold",
                    color=COLORS["dark"], zorder=3)
        if show_cost:
            ax.text(x + step_w / 2, y + step_h / 2 - 0.18,
                    cost_label_fmt.format(v=costs[i]),
                    ha="center", va="center", fontsize=9.5,
                    color=COLORS["dark"], zorder=3)
    return x0 + (len(costs) - 1) * step_w + step_w, y0 + (len(costs) - 1) * step_h + step_h


def _arrow(ax, x0, y0, x1, y1, color=None, width=1.6, style="-|>",
           shrink=4, alpha=1.0, zorder=3):
    color = color or COLORS["dark"]
    arrow = FancyArrowPatch((x0, y0), (x1, y1), arrowstyle=style,
                            mutation_scale=14, color=color,
                            linewidth=width, alpha=alpha, zorder=zorder,
                            shrinkA=shrink, shrinkB=shrink)
    ax.add_patch(arrow)


# ============================================================================
# 01 — Staircase setup
# ============================================================================
def plot_escalera_setup():
    """The staircase the student is about to work with."""
    fig, ax = plt.subplots(figsize=(9, 5))
    _draw_staircase(ax, COSTS, step_w=1.3, step_h=0.55, show_cost=False)
    # Manual per-state cost annotation with subscript
    for i in range(N_STATES):
        x = i * 1.3 + 1.3 / 2
        y = i * 0.55 + 0.55 / 2 - 0.18
        ax.text(x, y, f"$c_{{{i}}} = {COSTS[i]}$", ha="center", va="center",
                fontsize=9.5, color=COLORS["dark"], zorder=4)

    # Demonstrate the action set at state 1 (arrows showing {subir 1, saltar 2})
    x1 = 1 * 1.3 + 1.3 / 2
    y1 = 1 * 0.55 + 0.55
    x_step1 = 2 * 1.3 + 1.3 / 2
    y_step1 = 2 * 0.55 + 0.55
    x_jump2 = 3 * 1.3 + 1.3 / 2
    y_jump2 = 3 * 0.55 + 0.55
    _arrow(ax, x1, y1 + 0.15, x_step1, y_step1 + 0.15,
           color=COLORS["blue"], width=2.0)
    _arrow(ax, x1, y1 + 0.15, x_jump2, y_jump2 + 0.15,
           color=COLORS["orange"], width=2.0)
    ax.text((x1 + x_step1) / 2, (y1 + y_step1) / 2 + 0.35, "subir 1",
            ha="center", color=COLORS["blue"], fontsize=10, fontweight="bold")
    ax.text((x1 + x_jump2) / 2, (y1 + y_jump2) / 2 + 0.42, "saltar 2",
            ha="center", color=COLORS["orange"], fontsize=10, fontweight="bold")

    # Goal annotation
    gx = (N_STATES - 1) * 1.3 + 1.3 / 2
    gy = (N_STATES - 1) * 0.55 + 0.55 + 0.25
    ax.annotate("meta", xy=(gx, gy - 0.1), xytext=(gx + 0.4, gy + 0.5),
                fontsize=10, color=COLORS["green"], fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=COLORS["green"], lw=1.5))

    ax.set_xlim(-0.5, N_STATES * 1.3 + 0.5)
    ax.set_ylim(-0.2, N_STATES * 0.55 + 1.2)
    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.set_title("La escalera: estados, costos y acciones disponibles",
                 fontsize=13, color=COLORS["dark"], pad=10)
    _save(fig, "01_escalera_setup.png")


# ============================================================================
# 02 — Greedy vs optimal trajectories
# ============================================================================
def _draw_trajectory_on_stairs(ax, costs, trajectory, step_w=1.1, step_h=0.5,
                                path_color=None):
    """Helper: draw staircase and highlight a trajectory."""
    path_color = path_color or COLORS["blue"]
    # Draw full staircase
    _draw_staircase(ax, costs, step_w=step_w, step_h=step_h, show_cost=False)
    for i in range(len(costs)):
        x = i * step_w + step_w / 2
        y = i * step_h + step_h / 2 - 0.16
        ax.text(x, y, f"{costs[i]}", ha="center", va="center", fontsize=9,
                color=COLORS["gray"])
    # Highlight states in trajectory
    for i in trajectory:
        x = i * step_w
        y = i * step_h
        rect = Rectangle((x, y), step_w, step_h, facecolor=path_color,
                         edgecolor=COLORS["dark"], linewidth=1.5,
                         alpha=0.4, zorder=2)
        ax.add_patch(rect)
    # Arrows for the trajectory
    for a, b in zip(trajectory[:-1], trajectory[1:]):
        xa = a * step_w + step_w / 2
        ya = a * step_h + step_h
        xb = b * step_w + step_w / 2
        yb = b * step_h + step_h
        _arrow(ax, xa, ya + 0.1, xb, yb + 0.1, color=path_color, width=2.2)


def _greedy_trajectory(costs):
    """Greedy: at each state pick the cheaper immediate next state."""
    i = 0
    traj = [0]
    N = len(costs)
    while i < N - 1:
        opts = []
        if i + 1 < N:
            opts.append((i + 1, costs[i + 1]))
        if i + 2 < N:
            opts.append((i + 2, costs[i + 2]))
        next_i, _ = min(opts, key=lambda t: t[1])
        traj.append(next_i)
        i = next_i
    return traj


def plot_greedy_vs_optimo():
    """Greedy and optimal trajectories side-by-side."""
    greedy = _greedy_trajectory(COSTS)
    optimal = TRAJ_DET
    greedy_cost = sum(COSTS[s] for s in greedy)
    opt_cost = sum(COSTS[s] for s in optimal)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    _draw_trajectory_on_stairs(axes[0], COSTS, greedy,
                                path_color=COLORS["orange"])
    _draw_trajectory_on_stairs(axes[1], COSTS, optimal,
                                path_color=COLORS["green"])

    for ax in axes:
        ax.set_xlim(-0.3, N_STATES * 1.1 + 0.3)
        ax.set_ylim(-0.2, N_STATES * 0.5 + 0.8)
        ax.set_aspect("equal")
        ax.set_axis_off()

    axes[0].set_title(f"Codicioso (miope) — trayectoria {greedy}\n"
                      f"costo total = {greedy_cost}",
                      color=COLORS["orange"], fontsize=12)
    axes[1].set_title(f"Óptimo (Bellman) — trayectoria {optimal}\n"
                      f"costo total = {opt_cost}",
                      color=COLORS["green"], fontsize=12)

    # Honest caption if they coincide
    if greedy == optimal:
        caption = ("En este vector de costos, el codicioso coincidió con el óptimo "
                   "por suerte. Necesitamos un método que no dependa de la suerte.")
    else:
        caption = (f"El codicioso pagó {greedy_cost - opt_cost} más que el óptimo: "
                   "una decisión miope hoy puede costar caro mañana.")
    fig.text(0.5, 0.02, caption, ha="center", fontsize=10,
             color=COLORS["dark"], style="italic", wrap=True)

    fig.suptitle("Decidir localmente vs. decidir a largo plazo",
                 fontsize=14, color=COLORS["dark"])
    fig.tight_layout(rect=[0, 0.06, 1, 0.96])
    _save(fig, "02_greedy_vs_optimo.png")


# ============================================================================
# 03 — V-table filled right to left
# ============================================================================
def plot_tabla_valores():
    """V-table with numbered fill-order arrows."""
    fig, ax = plt.subplots(figsize=(11, 5))

    # Table: row with state numbers, row with V values
    col_w = 1.3
    row_h = 0.9
    x0, y0 = 0.0, 0.0

    # Header row
    ax.text(x0 - col_w * 0.9, y0 + row_h * 1.5, "Estado $i$",
            ha="right", va="center", fontsize=11, fontweight="bold",
            color=COLORS["dark"])
    ax.text(x0 - col_w * 0.9, y0 + row_h * 0.5, "$V(i)$",
            ha="right", va="center", fontsize=11, fontweight="bold",
            color=COLORS["dark"])

    for i in range(N_STATES):
        x = x0 + i * col_w
        # state cell
        rect = Rectangle((x, y0 + row_h), col_w, row_h, facecolor=COLORS["light"],
                         edgecolor=COLORS["dark"], linewidth=1.3)
        ax.add_patch(rect)
        ax.text(x + col_w / 2, y0 + row_h * 1.5, f"{i}",
                ha="center", va="center", fontsize=13, fontweight="bold",
                color=COLORS["dark"])
        # value cell
        rect = Rectangle((x, y0), col_w, row_h,
                         facecolor=COLORS["blue"], alpha=0.12,
                         edgecolor=COLORS["dark"], linewidth=1.3)
        ax.add_patch(rect)
        ax.text(x + col_w / 2, y0 + row_h / 2, f"{V_DET[i]}",
                ha="center", va="center", fontsize=15, fontweight="bold",
                color=COLORS["blue"])

    # Fill-order labels (1..6) with right-to-left numbering
    for order_idx, i in enumerate(range(N_STATES - 1, -1, -1)):
        x = x0 + i * col_w + col_w / 2
        y = y0 - 0.45
        # Circle with step number
        circ = plt.Circle((x, y), 0.22, facecolor=COLORS["green"],
                          edgecolor=COLORS["dark"], linewidth=1.2, zorder=3)
        ax.add_patch(circ)
        ax.text(x, y, f"{order_idx + 1}", ha="center", va="center",
                fontsize=10, fontweight="bold", color="white", zorder=4)

    # Big arrow showing direction — drawn in the band between the cells and
    # the fill-order circles, so it never overlaps the V values.
    arrow_y = y0 - 0.15
    _arrow(ax, x0 + N_STATES * col_w + 0.2, arrow_y,
           x0 - 0.2, arrow_y,
           color=COLORS["orange"], width=2.5, style="-|>", shrink=0)
    ax.text(x0 + N_STATES * col_w / 2, arrow_y + 0.08,
            "dirección de llenado",
            ha="center", va="bottom", fontsize=9.5,
            color=COLORS["orange"], style="italic")

    ax.text(x0 + (N_STATES * col_w) / 2, y0 - 1.2,
            "Se llena de derecha a izquierda: desde la meta hacia el inicio",
            ha="center", va="center", fontsize=10.5, color=COLORS["dark"],
            style="italic")

    ax.text(x0 + N_STATES * col_w / 2, y0 + row_h * 2.3,
            "Ecuación de Bellman:  $V(i) = c_i + \\min_a V(T(i,a))$",
            ha="center", va="center", fontsize=12, color=COLORS["dark"])

    ax.set_xlim(x0 - col_w * 1.3, x0 + N_STATES * col_w + 0.8)
    ax.set_ylim(y0 - 1.5, y0 + row_h * 2.8)
    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.set_title("La tabla de valores, llenada de derecha a izquierda",
                 fontsize=13, color=COLORS["dark"], pad=10)
    _save(fig, "03_tabla_valores.png")


# ============================================================================
# 04 — Stochastic staircase
# ============================================================================
def plot_escalera_estocastica():
    """Branching transitions with slip probability, stochastic V values."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    # Left panel — deterministic recap
    ax = axes[0]
    _draw_staircase(ax, COSTS, step_w=1.1, step_h=0.5,
                    show_cost=False, show_state=False)
    for i in range(N_STATES):
        x = i * 1.1 + 1.1 / 2
        y = i * 0.5 + 0.5 / 2
        ax.text(x, y + 0.15, f"$i={i}$", ha="center", va="center",
                fontsize=10, fontweight="bold", color=COLORS["dark"])
        ax.text(x, y - 0.02, f"$c={COSTS[i]}$", ha="center", va="center",
                fontsize=8.5, color=COLORS["gray"])
        ax.text(x, y - 0.17, f"$V={V_DET[i]}$", ha="center", va="center",
                fontsize=9.5, color=COLORS["blue"], fontweight="bold")
    ax.set_xlim(-0.3, N_STATES * 1.1 + 0.3)
    ax.set_ylim(-0.2, N_STATES * 0.5 + 0.8)
    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.set_title("Determinista — $V(0) = 6$", color=COLORS["blue"], fontsize=12)

    # Right panel — stochastic
    ax = axes[1]
    _draw_staircase(ax, COSTS, step_w=1.1, step_h=0.5,
                    show_cost=False, show_state=False)
    for i in range(N_STATES):
        x = i * 1.1 + 1.1 / 2
        y = i * 0.5 + 0.5 / 2
        ax.text(x, y + 0.15, f"$i={i}$", ha="center", va="center",
                fontsize=10, fontweight="bold", color=COLORS["dark"])
        ax.text(x, y - 0.02, f"$c={COSTS[i]}$", ha="center", va="center",
                fontsize=8.5, color=COLORS["gray"])
        ax.text(x, y - 0.17, f"$V={V_STOCH[i]}$", ha="center", va="center",
                fontsize=9.5, color=COLORS["red"], fontweight="bold")

    # Branching transitions for "saltar 2" from state 1
    sx = 1 * 1.1 + 1.1 / 2
    sy = 1 * 0.5 + 0.5
    # Success branch: lands at 3
    tx = 3 * 1.1 + 1.1 / 2
    ty = 3 * 0.5 + 0.5
    _arrow(ax, sx, sy + 0.1, tx, ty + 0.1, color=COLORS["green"], width=1.8)
    ax.text((sx + tx) / 2, (sy + ty) / 2 + 0.55, "0.8",
            ha="center", color=COLORS["green"], fontsize=9.5, fontweight="bold")
    # Slip branch: lands at 2
    tx = 2 * 1.1 + 1.1 / 2
    ty = 2 * 0.5 + 0.5
    _arrow(ax, sx, sy + 0.1, tx, ty + 0.1, color=COLORS["red"], width=1.8,
           style="-|>")
    ax.text((sx + tx) / 2, (sy + ty) / 2 + 0.28, "0.2 (resbala)",
            ha="center", color=COLORS["red"], fontsize=9.5, fontweight="bold")

    ax.set_xlim(-0.3, N_STATES * 1.1 + 0.3)
    ax.set_ylim(-0.2, N_STATES * 0.5 + 0.8)
    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.set_title("Estocástico — $V(0) = 8.2$\n(precio de la incertidumbre: $8.2 - 6 = 2.2$)",
                 color=COLORS["red"], fontsize=12)

    fig.suptitle("Misma escalera, con probabilidad de resbalar",
                 fontsize=14, color=COLORS["dark"])
    fig.tight_layout()
    _save(fig, "04_escalera_estocastica.png")


# ============================================================================
# 05 — γ decay and termination probability
# ============================================================================
def plot_gamma_decaimiento():
    """Two panels: γ^t decay + termination-probability interpretation."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    t = np.arange(0, 51)
    gammas = [0.5, 0.9, 0.95, 0.99]
    gamma_colors = [COLORS["red"], COLORS["orange"], COLORS["blue"], COLORS["green"]]

    # Left — γ^t curves
    ax = axes[0]
    for g, c in zip(gammas, gamma_colors):
        ax.plot(t, g ** t, color=c, linewidth=2, label=f"$\\gamma = {g}$")
    ax.set_xlabel("pasos al futuro $t$")
    ax.set_ylabel("peso del futuro  $\\gamma^t$")
    ax.set_title("Descuento del futuro: $\\gamma^t$ para varios $\\gamma$",
                 color=COLORS["dark"])
    ax.legend(loc="upper right", fontsize=10)
    ax.set_ylim(-0.02, 1.05)

    # Right — termination-probability interpretation
    ax = axes[1]
    p_term = 0.05
    g = 1 - p_term
    ax.plot(t, g ** t, color=COLORS["blue"], linewidth=2.5,
            label=f"$P(\\text{{sigue activo en }} t) = \\gamma^t$\n($\\gamma = 1-p = {g}$)")
    ax.fill_between(t, 0, g ** t, alpha=0.18, color=COLORS["blue"])
    ax.set_xlabel("pasos $t$")
    ax.set_ylabel("probabilidad")
    ax.set_title(f"Interpretación: $\\gamma = 1 - p$ con $p = {p_term}$\n"
                 "(probabilidad de que la escalera termine cada paso)",
                 color=COLORS["dark"])
    ax.legend(loc="upper right", fontsize=10)
    ax.set_ylim(-0.02, 1.05)

    fig.suptitle("Dos maneras de ver $\\gamma$", fontsize=14, color=COLORS["dark"])
    fig.tight_layout()
    _save(fig, "05_gamma_decaimiento.png")


# ============================================================================
# 06 — MDP components
# ============================================================================
def plot_mdp_componentes():
    """5-box schematic tying MDP tuple to staircase instantiation."""
    fig, ax = plt.subplots(figsize=(14, 6))

    items = [
        ("$S$", "Estados", "$\\{0, 1, 2, 3, 4, 5\\}$", COLORS["blue"]),
        ("$A$", "Acciones", "$\\{$subir 1, saltar 2$\\}$", COLORS["orange"]),
        ("$T$", "Transición", "0.8 éxito / 0.2 resbala", COLORS["purple"]),
        ("$R$", "Costo", "$c = [3,2,7,1,4,0]$", COLORS["red"]),
        ("$\\gamma$", "Descuento", "$0.95$", COLORS["green"]),
    ]

    box_w, box_h = 2.4, 2.0
    spacing = 0.4
    total_w = len(items) * box_w + (len(items) - 1) * spacing

    for idx, (sym, name, instance, color) in enumerate(items):
        x = idx * (box_w + spacing)
        y = 0
        box = FancyBboxPatch((x, y), box_w, box_h,
                             boxstyle="round,pad=0.05",
                             facecolor=color, alpha=0.15,
                             edgecolor=color, linewidth=2.2)
        ax.add_patch(box)
        ax.text(x + box_w / 2, y + box_h - 0.35, sym,
                ha="center", va="center", fontsize=22, fontweight="bold",
                color=color)
        ax.text(x + box_w / 2, y + box_h - 0.95, name,
                ha="center", va="center", fontsize=11,
                color=COLORS["dark"])
        ax.text(x + box_w / 2, y + 0.45, instance,
                ha="center", va="center", fontsize=10,
                color=COLORS["dark"])

    ax.text(total_w / 2, box_h + 0.55,
            "Un MDP es la tupla  $(S, A, T, R, \\gamma)$",
            ha="center", va="center", fontsize=14,
            color=COLORS["dark"])
    ax.text(total_w / 2, -0.55,
            "La escalera, en vocabulario de MDP",
            ha="center", va="center", fontsize=11, style="italic",
            color=COLORS["gray"])

    ax.set_xlim(-0.3, total_w + 0.3)
    ax.set_ylim(-1.0, box_h + 1.1)
    ax.set_aspect("equal")
    ax.set_axis_off()
    _save(fig, "06_mdp_componentes.png")


# ============================================================================
# 07 — Naive call tree (the "must-see" image for Phase 4)
# ============================================================================
def plot_arbol_llamadas():
    """Recursion tree for OPTIMAL(0), repeated subproblems highlighted."""
    fig, ax = plt.subplots(figsize=(14, 9))

    # Build tree: nodes = list of (id, label, depth, x, parent_id)
    # We draw a truncated tree rooted at OPTIMAL(0).
    node_colors = {
        0: COLORS["dark"],
        1: COLORS["blue"],
        2: COLORS["red"],
        3: COLORS["orange"],
        4: COLORS["purple"],
        5: COLORS["green"],
    }

    def expand(state, depth, max_depth):
        if state >= GOAL or depth >= max_depth:
            return {"state": state, "children": []}
        children = []
        if state + 1 <= GOAL:
            children.append(expand(state + 1, depth + 1, max_depth))
        if state + 2 <= GOAL:
            children.append(expand(state + 2, depth + 1, max_depth))
        return {"state": state, "children": children}

    tree = expand(0, 0, max_depth=5)

    # Assign x-positions via DFS-based leaf counting
    def layout(node, depth, x_cursor):
        if not node["children"]:
            node["x"] = x_cursor[0]
            node["y"] = -depth
            x_cursor[0] += 1
            return
        for ch in node["children"]:
            layout(ch, depth + 1, x_cursor)
        node["x"] = np.mean([ch["x"] for ch in node["children"]])
        node["y"] = -depth

    x_cursor = [0]
    layout(tree, 0, x_cursor)

    # Draw edges + nodes
    def draw(node):
        x, y = node["x"], node["y"] * 1.3
        state = node["state"]
        for ch in node["children"]:
            cx, cy = ch["x"], ch["y"] * 1.3
            ax.plot([x, cx], [y, cy], color=COLORS["gray"],
                    linewidth=1.2, alpha=0.6, zorder=1)
            draw(ch)
        color = node_colors[state]
        # Highlight repeated subproblems with filled circle; unique with lighter fill
        circle = plt.Circle((x, y), 0.27, facecolor=color, alpha=0.85,
                             edgecolor=COLORS["dark"], linewidth=1.3, zorder=3)
        ax.add_patch(circle)
        ax.text(x, y, f"{state}", ha="center", va="center",
                fontsize=10, fontweight="bold", color="white", zorder=4)

    draw(tree)

    # Count repeated subproblems for caption
    counts = {s: 0 for s in range(N_STATES)}
    def count(node):
        counts[node["state"]] += 1
        for ch in node["children"]:
            count(ch)
    count(tree)
    repeats = {s: c for s, c in counts.items() if c > 1}

    # Legend
    legend_items = [mpatches.Patch(color=node_colors[s],
                                    label=f"OPTIMAL({s})  ×{counts[s]}")
                     for s in range(N_STATES) if counts[s] > 0]
    ax.legend(handles=legend_items, loc="upper right", fontsize=10,
              title="Subproblema", title_fontsize=11)

    ax.text(x_cursor[0] / 2, 1.2,
            "Cada OPTIMAL($i$) con el mismo color se recalcula cada vez.\n"
            "Los subproblemas se repiten — esto es lo que DP resuelve.",
            ha="center", va="center", fontsize=11, color=COLORS["dark"],
            style="italic")

    ax.set_xlim(-1, x_cursor[0])
    ax.set_ylim(-7, 2)
    ax.set_aspect("auto")
    ax.set_axis_off()
    ax.set_title("Árbol de llamadas de $\\mathrm{OPTIMAL}(0)$ — la versión ingenua",
                 fontsize=13, color=COLORS["dark"], pad=10)
    _save(fig, "07_arbol_llamadas.png")


# ============================================================================
# 08 — Memoization vs tabulation
# ============================================================================
def plot_memo_vs_tab():
    """Execution trace of memoization (DFS) vs tabulation (reverse loop)."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Memoization order: DFS from OPTIMAL(0). Simulate the order cache fills.
    # For the staircase, DFS explores left-first: 0 → 1 → 2 → 3 → 4 → 5, then
    # cache[5]=0, cache[4]=4, cache[3]=1, etc. Resolution order from bottom up.
    memo_order = [5, 4, 3, 2, 1, 0]  # order in which cache[i] is written
    tab_order = [5, 4, 3, 2, 1, 0]   # bottom-up explicit loop

    def draw_trace(ax, order, title, color):
        col_w = 1.3
        for idx in range(N_STATES):
            x = idx * col_w
            rect = Rectangle((x, 0), col_w, 1, facecolor=COLORS["light"],
                             edgecolor=COLORS["dark"], linewidth=1.2)
            ax.add_patch(rect)
            ax.text(x + col_w / 2, 1.25, f"$V({idx})$",
                    ha="center", va="center", fontsize=11,
                    color=COLORS["dark"])
        # Fill-order indices
        for fill_step, i in enumerate(order):
            x = i * col_w + col_w / 2
            # Show the value and step number
            ax.text(x, 0.65, f"{V_DET[i]}", ha="center", va="center",
                    fontsize=13, fontweight="bold", color=color)
            ax.text(x, 0.25, f"paso {fill_step + 1}", ha="center", va="center",
                    fontsize=9, color=COLORS["gray"])
        ax.set_xlim(-0.3, N_STATES * col_w + 0.3)
        ax.set_ylim(-0.6, 2.2)
        ax.set_aspect("equal")
        ax.set_axis_off()
        ax.set_title(title, fontsize=12, color=color, pad=10)

    draw_trace(axes[0], memo_order,
                "Memoización (top-down, DFS con caché)\n"
                "$V(0)$ se llama, baja recursivo hasta $V(5)$, cachea al regresar",
                COLORS["blue"])
    draw_trace(axes[1], tab_order,
                "Tabulación (bottom-up, loop inverso)\n"
                "for $i$ from $N-1$ downto $0$: llena $V[i]$",
                COLORS["green"])

    fig.suptitle("Dos formas de recorrer la MISMA ecuación — mismos valores, distinto orden",
                 fontsize=14, color=COLORS["dark"])
    fig.tight_layout()
    _save(fig, "08_memo_vs_tab.png")


# ============================================================================
# 09 — Subproblem DAG
# ============================================================================
def plot_dag_subproblemas():
    """DAG of V(i) dependencies with topological numbering."""
    fig, ax = plt.subplots(figsize=(13, 5))

    # Layout nodes left-to-right: V(0), V(1), ..., V(5)
    xs = np.arange(N_STATES) * 2.0
    ys = np.zeros(N_STATES)

    # Draw edges V(i) → V(i+1) and V(i) → V(i+2)
    for i in range(N_STATES):
        if i + 1 < N_STATES:
            _arrow(ax, xs[i] + 0.35, ys[i], xs[i + 1] - 0.35, ys[i + 1],
                   color=COLORS["blue"], width=1.6, shrink=0)
        if i + 2 < N_STATES:
            _arrow(ax, xs[i] + 0.35, ys[i] + 0.25,
                   xs[i + 2] - 0.35, ys[i + 2] + 0.25,
                   color=COLORS["orange"], width=1.6, shrink=0, style="-|>")

    # Nodes
    topo_order = list(range(N_STATES - 1, -1, -1))  # 5, 4, 3, 2, 1, 0
    topo_num = {s: i + 1 for i, s in enumerate(topo_order)}
    for i in range(N_STATES):
        circ = plt.Circle((xs[i], ys[i]), 0.38, facecolor=COLORS["light"],
                          edgecolor=COLORS["dark"], linewidth=1.8, zorder=3)
        ax.add_patch(circ)
        ax.text(xs[i], ys[i], f"$V({i})$", ha="center", va="center",
                fontsize=12, fontweight="bold", color=COLORS["dark"], zorder=4)
        ax.text(xs[i], ys[i] - 0.95, f"topológico: {topo_num[i]}",
                ha="center", va="center", fontsize=9.5,
                color=COLORS["green"])

    # Legend
    ax.plot([], [], color=COLORS["blue"], linewidth=2, label="subir 1")
    ax.plot([], [], color=COLORS["orange"], linewidth=2, label="saltar 2")
    ax.legend(loc="upper right", fontsize=10)

    ax.text(xs[-1] / 2, 1.4,
            "El DAG de subproblemas: cada $V(i)$ depende de $V(i+1)$ y $V(i+2)$",
            ha="center", fontsize=11, color=COLORS["dark"])
    ax.text(xs[-1] / 2, -1.8,
            "Bottom-up DP visita los nodos en orden topológico (derecha a izquierda).",
            ha="center", fontsize=10.5, color=COLORS["dark"], style="italic")

    ax.set_xlim(-1, xs[-1] + 1)
    ax.set_ylim(-2.3, 1.9)
    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.set_title("DAG de subproblemas para la escalera",
                 fontsize=13, color=COLORS["dark"], pad=10)
    _save(fig, "09_dag_subproblemas.png")


# ============================================================================
# 10 — Complexity curves
# ============================================================================
def plot_complejidad():
    """Exponential vs linear runtime, log scale."""
    # Count actual calls for naive recursion vs DP
    # For 1-or-2-step staircase, naive call count C(N) satisfies Fibonacci:
    # C(N) = 1 + C(N-1) + C(N-2),  C(0)=1, C(-1)=1 (treat out-of-range as leaves)
    def naive_calls(n):
        memo = {}
        def rec(k):
            if k in memo:
                return memo[k]
            if k >= n:
                memo[k] = 1
                return 1
            # Leaf counts 1 call for itself plus recursive children
            res = 1 + rec(k + 1)
            if k + 2 <= n:
                res += rec(k + 2)
            memo[k] = res
            return res
        # But we want NON-memoized count: expand recursively without caching
        def rec_no_memo(k):
            if k >= n:
                return 1
            total = 1
            total += rec_no_memo(k + 1)
            if k + 2 <= n:
                total += rec_no_memo(k + 2)
            return total
        return rec_no_memo(0)

    def dp_calls(n):
        # Bottom-up: one computation per state
        return n

    N_range = list(range(2, 31))
    naive = [naive_calls(n) for n in N_range]
    dp = [dp_calls(n) for n in N_range]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.semilogy(N_range, naive, marker="o", color=COLORS["red"],
                linewidth=2, markersize=4, label="Recursión ingenua")
    ax.semilogy(N_range, dp, marker="s", color=COLORS["green"],
                linewidth=2, markersize=4, label="DP (tabulación / memoización)")

    # Annotate gap at N=30
    n_ann = 30
    ax.annotate(f"N=30: ~{naive[-1]:,} llamadas",
                xy=(n_ann, naive[-1]), xytext=(21, naive[-1] * 0.3),
                fontsize=10, color=COLORS["red"],
                arrowprops=dict(arrowstyle="->", color=COLORS["red"]))
    ax.annotate(f"N=30: solo {dp[-1]} operaciones",
                xy=(n_ann, dp[-1]), xytext=(21, 2),
                fontsize=10, color=COLORS["green"],
                arrowprops=dict(arrowstyle="->", color=COLORS["green"]))

    ax.set_xlabel("tamaño del problema $N$ (pasos en la escalera)")
    ax.set_ylabel("número de operaciones (escala log)")
    ax.set_title("Exponencial vs. lineal: la diferencia se siente",
                 fontsize=13, color=COLORS["dark"])
    ax.legend(loc="center right", fontsize=11)
    ax.grid(True, which="both", alpha=0.3)

    fig.tight_layout()
    _save(fig, "10_complejidad.png")


# ============================================================================
# 11 — Policy extraction
# ============================================================================
def plot_politica():
    """Staircase with V values, policy arrows, and highlighted trajectory."""
    fig, ax = plt.subplots(figsize=(12, 6))

    step_w, step_h = 1.3, 0.55
    # Draw staircase (suppress default state label; we'll add our own layout)
    _draw_staircase(ax, COSTS, step_w=step_w, step_h=step_h,
                    show_cost=False, show_state=False)

    # Annotate i, V and c per state — non-overlapping layout
    for i in range(N_STATES):
        x = i * step_w + step_w / 2
        y = i * step_h + step_h / 2
        ax.text(x, y + 0.15, f"$i={i}$", ha="center", va="center",
                fontsize=10, fontweight="bold", color=COLORS["dark"])
        ax.text(x, y - 0.01, f"$V={V_DET[i]}$", ha="center", va="center",
                fontsize=10, color=COLORS["blue"], fontweight="bold")
        ax.text(x, y - 0.17, f"$c={COSTS[i]}$", ha="center", va="center",
                fontsize=8.5, color=COLORS["gray"])
        # Policy arrow
        if i < GOAL:
            act = POLICY_DET[i]
            target = i + (1 if act == "subir 1" else 2)
            color = COLORS["blue"] if act == "subir 1" else COLORS["orange"]
            xa = i * step_w + step_w
            ya = i * step_h + step_h
            xb = target * step_w + step_w / 2
            yb = target * step_h + step_h
            _arrow(ax, xa - 0.1, ya + 0.3, xb, yb + 0.3,
                   color=color, width=2.2)

    # Highlight the optimal trajectory
    for i in TRAJ_DET:
        x = i * step_w
        y = i * step_h
        rect = Rectangle((x, y), step_w, step_h,
                         facecolor=COLORS["green"], alpha=0.25,
                         edgecolor=COLORS["green"], linewidth=1.8, zorder=2)
        ax.add_patch(rect)

    # Summary
    ax.text(N_STATES * step_w / 2, N_STATES * step_h + 0.9,
            f"Política óptima $\\pi^*$: "
            + " → ".join([f"{s}" for s in TRAJ_DET])
            + f"  —  costo total = {COST_DET}",
            ha="center", fontsize=12, color=COLORS["dark"], fontweight="bold")

    # Legend
    ax.plot([], [], color=COLORS["blue"], linewidth=2.5, label="subir 1")
    ax.plot([], [], color=COLORS["orange"], linewidth=2.5, label="saltar 2")
    ax.plot([], [], color=COLORS["green"], linewidth=4, alpha=0.5,
            label="trayectoria óptima")
    ax.legend(loc="lower right", fontsize=10)

    ax.set_xlim(-0.5, N_STATES * step_w + 0.5)
    ax.set_ylim(-0.3, N_STATES * step_h + 1.8)
    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.set_title("$V^*$ te dice qué tan bueno es cada estado;  "
                 "$\\pi^*$ te dice qué hacer en cada uno",
                 fontsize=13, color=COLORS["dark"], pad=10)
    _save(fig, "11_politica.png")


# ============================================================================
# Entry point
# ============================================================================
def main():
    print(f"Saving images to: {IMAGES_DIR}")
    plot_escalera_setup()
    plot_greedy_vs_optimo()
    plot_tabla_valores()
    plot_escalera_estocastica()
    plot_gamma_decaimiento()
    plot_mdp_componentes()
    plot_arbol_llamadas()
    plot_memo_vs_tab()
    plot_dag_subproblemas()
    plot_complejidad()
    plot_politica()
    print("Done.")


if __name__ == "__main__":
    main()
