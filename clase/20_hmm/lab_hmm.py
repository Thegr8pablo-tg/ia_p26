"""
lab_hmm.py — Genera las imágenes pedagógicas para clase/20_hmm/

Ejecución:
    cd clase/20_hmm && python lab_hmm.py
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
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
    "pink":   "#E91E8C",
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

# ── Toy example parameters (Lain / Clima) ────────────────────────────────────
PI  = np.array([0.6,  0.4])
A   = np.array([[0.7, 0.3],
                [0.4, 0.6]])
B   = np.array([[0.9, 0.1],
                [0.2, 0.8]])
OBS = np.array([0, 1, 1])   # 0=sin paraguas, 1=con paraguas
T   = len(OBS)
N   = len(PI)

STATES  = ["Sol (S)", "Lluvia (R)"]
SNAMES  = ["S", "R"]         # short names for trellis labels
SYMBOLS = ["0 (sin ☂)", "1 (con ☂)"]

# ── Pre-verified values (from diseño; usados en plots) ───────────────────────
ALPHA = np.array([[0.54000, 0.08000],
                  [0.04100, 0.16800],
                  [0.00959, 0.09048]])

BETA  = np.array([[0.14650, 0.26200],
                  [0.31000, 0.52000],
                  [1.00000, 1.00000]])

DELTA = np.array([[0.54000, 0.08000],
                  [0.03780, 0.12960],
                  [0.00518, 0.06221]])

PSI   = np.array([[0, 0],    # t=1: no backpointer
                  [0, 0],    # t=2: both came from S (index 0)
                  [1, 1]])   # t=3: both came from R (index 1)

GAMMA = np.array([[0.7906, 0.2094],
                  [0.1270, 0.8730],
                  [0.0958, 0.9042]])

P_OBS        = 0.10007
OPTIMAL_PATH = [0, 1, 1]    # S → R → R

A_HAT = np.array([[0.159, 0.841],
                  [0.071, 0.929]])
B_HAT = np.array([[0.780, 0.220],
                  [0.105, 0.895]])


# ── Helper ───────────────────────────────────────────────────────────────────
def _save(fig, name):
    fig.savefig(IMAGES_DIR / name, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {name}")


# ── Algorithms (for convergence plot) ────────────────────────────────────────
def _forward(obs, pi, a, b):
    T_ = len(obs)
    N_ = len(pi)
    alpha = np.zeros((T_, N_))
    alpha[0] = pi * b[:, obs[0]]
    for t in range(1, T_):
        alpha[t] = (alpha[t - 1] @ a) * b[:, obs[t]]
    return alpha, alpha[-1].sum()


def _backward(obs, a, b):
    T_ = len(obs)
    N_ = len(a)
    beta = np.zeros((T_, N_))
    beta[-1] = 1.0
    for t in range(T_ - 2, -1, -1):
        beta[t] = a @ (b[:, obs[t + 1]] * beta[t + 1])
    return beta


def _baum_welch_step(obs, pi, a, b):
    T_ = len(obs)
    N_ = len(pi)
    alpha, p_obs = _forward(obs, pi, a, b)
    beta          = _backward(obs, a, b)

    # γ
    gamma = (alpha * beta) / p_obs

    # ξ
    xi = np.zeros((T_ - 1, N_, N_))
    for t in range(T_ - 1):
        xi[t] = (alpha[t][:, None] * a * b[:, obs[t + 1]][None, :] *
                 beta[t + 1][None, :]) / p_obs

    # M-step
    pi_new = gamma[0]
    a_new  = xi.sum(axis=0) / gamma[:-1].sum(axis=0)[:, None]
    b_new  = np.zeros_like(b)
    for k in range(b.shape[1]):
        mask = (obs == k)
        b_new[:, k] = gamma[mask].sum(axis=0) / gamma.sum(axis=0)

    return pi_new, a_new, b_new, np.log(p_obs)


def _simulate(pi, a, b, length, rng):
    """Simulate an HMM sequence of given length."""
    state = rng.choice(len(pi), p=pi)
    obs_seq = []
    for _ in range(length):
        obs_seq.append(rng.choice(b.shape[1], p=b[state]))
        state = rng.choice(len(pi), p=a[state])
    return np.array(obs_seq)


# ── Trellis drawing helpers ───────────────────────────────────────────────────
def _trellis_axes(title, figsize=(11, 4.5)):
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(0.3, 3.7)
    ax.set_ylim(-0.6, 1.7)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=13, fontweight="bold", pad=14)
    return fig, ax


def _node(ax, x, y, label, facecolor, radius=0.22, fontsize=9, alpha_val=1.0,
          textcolor="white"):
    circle = plt.Circle((x, y), radius, color=facecolor, zorder=3,
                        alpha=alpha_val, linewidth=1.5, edgecolor="white")
    ax.add_patch(circle)
    ax.text(x, y, label, ha="center", va="center", fontsize=fontsize,
            fontweight="bold", color=textcolor, zorder=4)


def _arrow(ax, x0, y0, x1, y1, color, lw=1.5, alpha_val=0.7, label="",
           style="->", shrink=24):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle=style, color=color, lw=lw,
                                shrinkA=shrink, shrinkB=shrink,
                                connectionstyle="arc3,rad=0.0"),
                alpha=alpha_val, zorder=2)
    if label:
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        ax.text(mx, my + 0.07, label, ha="center", va="bottom",
                fontsize=7.5, color=color, zorder=5)


def _state_labels(ax, xs, ys, state_names):
    for s, (y, name) in enumerate(zip(ys, state_names)):
        ax.text(xs[0] - 0.45, y, name, ha="center", va="center",
                fontsize=10, fontweight="bold", color=COLORS["dark"])
    for t, x in enumerate(xs):
        ax.text(x, ys[-1] - 0.42, f"t={t + 1}", ha="center", va="center",
                fontsize=9, color=COLORS["gray"])


# ── Plot 01: MC vs HMM ────────────────────────────────────────────────────────
def plot_mc_vs_hmm():
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    for ax in axes:
        ax.set_xlim(0, 4)
        ax.set_ylim(-0.3, 2.2)
        ax.axis("off")

    # ── Left: Markov Chain (estados observables)
    ax = axes[0]
    ax.set_title("Cadena de Markov\n(estados observables)", fontsize=12,
                 fontweight="bold", color=COLORS["blue"])

    mc_x = [0.8, 2.0, 3.2]
    mc_labels = ["q₁", "q₂", "q₃"]
    for x, lbl in zip(mc_x, mc_labels):
        circle = plt.Circle((x, 1.0), 0.28, color=COLORS["blue"], zorder=3)
        ax.add_patch(circle)
        ax.text(x, 1.0, lbl, ha="center", va="center", fontsize=12,
                fontweight="bold", color="white", zorder=4)

    for i in range(2):
        ax.annotate("", xy=(mc_x[i + 1] - 0.3, 1.0),
                    xytext=(mc_x[i] + 0.3, 1.0),
                    arrowprops=dict(arrowstyle="->", color=COLORS["blue"],
                                   lw=2.0), zorder=2)

    ax.text(2.0, 0.35, "VES los estados directamente", ha="center",
            fontsize=10, color=COLORS["blue"], style="italic")
    ax.text(2.0, 0.05, "Solo necesitas: π  y  A", ha="center",
            fontsize=10, color=COLORS["dark"], fontweight="bold")

    # badge: 1 capa
    badge = mpatches.FancyBboxPatch((0.2, 1.65), 3.6, 0.38,
                                    boxstyle="round,pad=0.05",
                                    facecolor="#D6EAF8", edgecolor=COLORS["blue"],
                                    linewidth=1.5)
    ax.add_patch(badge)
    ax.text(2.0, 1.84, "1 capa", ha="center", va="center", fontsize=12,
            fontweight="bold", color=COLORS["blue"])

    # ── Right: HMM (2 capas)
    ax = axes[1]
    ax.set_title("Modelo Oculto de Markov\n(2 capas)", fontsize=12,
                 fontweight="bold", color=COLORS["purple"])

    hmm_x = [0.8, 2.0, 3.2]
    h_labels = ["q₁", "q₂", "q₃"]
    o_labels = ["o₁", "o₂", "o₃"]

    # hidden layer
    for x, lbl in zip(hmm_x, h_labels):
        circle = plt.Circle((x, 1.5), 0.26, color=COLORS["purple"], zorder=3,
                            linewidth=2, edgecolor=COLORS["purple"])
        ax.add_patch(circle)
        ax.text(x, 1.5, lbl, ha="center", va="center", fontsize=11,
                fontweight="bold", color="white", zorder=4)

    # transition arrows (hidden)
    for i in range(2):
        ax.annotate("", xy=(hmm_x[i + 1] - 0.28, 1.5),
                    xytext=(hmm_x[i] + 0.28, 1.5),
                    arrowprops=dict(arrowstyle="->", color=COLORS["purple"],
                                   lw=2.0), zorder=2)

    # observation layer
    for x, lbl in zip(hmm_x, o_labels):
        circle = plt.Circle((x, 0.5), 0.26, color=COLORS["teal"], zorder=3)
        ax.add_patch(circle)
        ax.text(x, 0.5, lbl, ha="center", va="center", fontsize=11,
                fontweight="bold", color="white", zorder=4)

    # emission arrows
    for x in hmm_x:
        ax.annotate("", xy=(x, 0.78), xytext=(x, 1.22),
                    arrowprops=dict(arrowstyle="->", color=COLORS["orange"],
                                   lw=1.8), zorder=2)

    # labels
    ax.text(4.05, 1.5, "← OCULTOS", ha="left", va="center", fontsize=9,
            color=COLORS["purple"], fontweight="bold")
    ax.text(4.05, 0.5, "← OBSERVADOS", ha="left", va="center", fontsize=9,
            color=COLORS["teal"], fontweight="bold")

    ax.text(2.0, 0.0, "Necesitas: π,  A  y  B", ha="center",
            fontsize=10, color=COLORS["dark"], fontweight="bold")

    # badge: 2 capas
    badge2 = mpatches.FancyBboxPatch((0.2, 1.83), 3.6, 0.3,
                                     boxstyle="round,pad=0.05",
                                     facecolor="#E8DAEF", edgecolor=COLORS["purple"],
                                     linewidth=1.5)
    ax.add_patch(badge2)
    ax.text(2.0, 1.98, "2 capas", ha="center", va="center", fontsize=12,
            fontweight="bold", color=COLORS["purple"])

    legend_items = [
        mpatches.Patch(color=COLORS["purple"], label="Estados ocultos (q)"),
        mpatches.Patch(color=COLORS["teal"],   label="Observaciones (o)"),
        mpatches.Patch(color=COLORS["orange"], label="Emisión B"),
    ]
    axes[1].legend(handles=legend_items, loc="lower right", fontsize=8.5,
                   framealpha=0.9)

    plt.tight_layout()
    _save(fig, "01_mc_vs_hmm.png")


# ── Plot 02: HMM structure with parameters ────────────────────────────────────
def plot_estructura_hmm():
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.set_xlim(0.0, 7.5)
    ax.set_ylim(-1.2, 3.2)
    ax.axis("off")
    ax.set_title(
        "El HMM de Lain: El Clima Oculto  (λ = A, B, π)",
        fontsize=13, fontweight="bold", pad=14
    )

    xs = [1.5, 3.5, 5.5]
    y_hid = 2.0
    y_obs = 0.5
    r = 0.32

    obs_vals  = [0, 1, 1]
    obs_str   = ["O₁=0\n(sin ☂)", "O₂=1\n(con ☂)", "O₃=1\n(con ☂)"]
    hid_str   = ["q₁", "q₂", "q₃"]

    # π annotation
    ax.annotate("", xy=(xs[0], y_hid + r),
                xytext=(xs[0] - 0.85, y_hid + 0.7),
                arrowprops=dict(arrowstyle="->", color=COLORS["green"], lw=2.0))
    ax.text(xs[0] - 1.0, y_hid + 0.85, "π", fontsize=15, color=COLORS["green"],
            fontweight="bold")
    ax.text(xs[0] - 1.35, y_hid + 0.55, "S: 0.6\nR: 0.4", fontsize=9,
            color=COLORS["green"], va="top")

    # Hidden nodes
    for i, (x, lbl) in enumerate(zip(xs, hid_str)):
        circle = plt.Circle((x, y_hid), r, color=COLORS["purple"], zorder=3,
                            linewidth=2, edgecolor="white")
        ax.add_patch(circle)
        ax.text(x, y_hid, lbl, ha="center", va="center", fontsize=12,
                fontweight="bold", color="white", zorder=4)

    # Transition arrows with A labels
    a_labels = [
        ("A_{SS}=0.7\nA_{SR}=0.3", "A_{RS}=0.4\nA_{RR}=0.6"),
        ("A_{SS}=0.7\nA_{SR}=0.3", "A_{RS}=0.4\nA_{RR}=0.6"),
    ]
    for i in range(2):
        x0, x1 = xs[i], xs[i + 1]
        ax.annotate("", xy=(x1 - r - 0.02, y_hid),
                    xytext=(x0 + r + 0.02, y_hid),
                    arrowprops=dict(arrowstyle="-|>", color=COLORS["purple"],
                                   lw=2.5, mutation_scale=16), zorder=2)
        ax.text((x0 + x1) / 2, y_hid + 0.25,
                f"S→S: 0.7  S→R: 0.3\nR→S: 0.4  R→R: 0.6",
                ha="center", va="bottom", fontsize=8, color=COLORS["purple"])

    # Observation nodes
    for i, (x, lbl, val) in enumerate(zip(xs, obs_str, obs_vals)):
        circle = plt.Circle((x, y_obs), r, color=COLORS["teal"], zorder=3)
        ax.add_patch(circle)
        ax.text(x, y_obs, lbl, ha="center", va="center", fontsize=8,
                fontweight="bold", color="white", zorder=4)

    # Emission arrows with B labels
    for i, x in enumerate(xs):
        ax.annotate("", xy=(x, y_obs + r + 0.02),
                    xytext=(x, y_hid - r - 0.02),
                    arrowprops=dict(arrowstyle="-|>", color=COLORS["orange"],
                                   lw=2.0, mutation_scale=14), zorder=2)

    # B matrix annotation
    ax.text(7.1, (y_hid + y_obs) / 2 + 0.1,
            "B (emisión):", fontsize=10, fontweight="bold",
            color=COLORS["orange"], ha="left", va="center")
    ax.text(7.1, (y_hid + y_obs) / 2 - 0.25,
            "       O=0   O=1\nS:  [0.9    0.1]\nR:  [0.2    0.8]",
            fontsize=9, color=COLORS["orange"], ha="left", va="top",
            family="monospace")

    # Layer labels
    ax.text(0.1, y_hid, "OCULTO\n(estado)", ha="center", va="center",
            fontsize=9, color=COLORS["purple"], fontweight="bold")
    ax.text(0.1, y_obs, "VISIBLE\n(obs)", ha="center", va="center",
            fontsize=9, color=COLORS["teal"], fontweight="bold")

    # Obs sequence label
    ax.text(3.5, -0.65, "Secuencia observada por Lain:  O = (0, 1, 1)",
            ha="center", fontsize=11, fontweight="bold", color=COLORS["dark"])
    ax.text(3.5, -1.0,
            "Pregunta: ¿Qué clima (Sol/Lluvia) hubo en cada día?",
            ha="center", fontsize=10, color=COLORS["gray"], style="italic")

    _save(fig, "02_estructura_hmm.png")


# ── Generic trellis helper ────────────────────────────────────────────────────
def _build_trellis(title, values, val_fmt, node_color_fn,
                   arrow_dir, arrow_color, figsize=(11, 4.5),
                   extra_fn=None, psi_arrows=None, path_edges=None):
    """
    values: (T, N) array of values to annotate on nodes.
    node_color_fn(t, s, val) -> color string
    arrow_dir: "right" or "left"
    psi_arrows: list of (t, s_from, s_to) to draw as orange backpointer arrows
    path_edges: list of (t, s) pairs indicating the optimal path nodes
    """
    xs = [1.0, 2.0, 3.0]   # time columns
    ys = [1.0, 0.0]         # states: S=top, R=bottom
    r  = 0.20

    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(0.35, 3.65)
    ax.set_ylim(-0.55, 1.65)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=13, fontweight="bold", pad=14)

    # state labels (left)
    for s, (y, name) in enumerate(zip(ys, SNAMES)):
        ax.text(xs[0] - 0.47, y, name, ha="center", va="center",
                fontsize=13, fontweight="bold", color=COLORS["dark"])

    # time labels (bottom)
    obs_labels = ["t=1\n(O=0)", "t=2\n(O=1)", "t=3\n(O=1)"]
    for t, x in enumerate(xs):
        ax.text(x, ys[1] - 0.38, obs_labels[t], ha="center", va="top",
                fontsize=9, color=COLORS["gray"])

    # transition arrows
    t_range = range(T - 1) if arrow_dir == "right" else range(T - 1, 0, -1)
    for t in range(T - 1):
        for s_from in range(N):
            for s_to in range(N):
                if arrow_dir == "right":
                    x0, y0 = xs[t], ys[s_from]
                    x1, y1 = xs[t + 1], ys[s_to]
                else:
                    x0, y0 = xs[t + 1], ys[s_to]
                    x1, y1 = xs[t], ys[s_from]

                lc = COLORS["gray"]
                lw = 0.8
                al = 0.35
                # check if this is a path edge
                if path_edges and arrow_dir == "right":
                    if (t, s_from) in path_edges and (t + 1, s_to) in path_edges:
                        lc = COLORS["green"]; lw = 3.0; al = 1.0

                ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                            arrowprops=dict(arrowstyle="->", color=lc, lw=lw,
                                           shrinkA=r * 72, shrinkB=r * 72,
                                           connectionstyle="arc3,rad=0.0"),
                            alpha=al, zorder=2)

    # backpointer arrows (orange, Viterbi)
    if psi_arrows:
        for (t, s_to, s_from) in psi_arrows:
            x0, y0 = xs[t - 1], ys[s_from]
            x1, y1 = xs[t], ys[s_to]
            ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                        arrowprops=dict(arrowstyle="-|>",
                                       color=COLORS["orange"], lw=2.5,
                                       shrinkA=r * 72, shrinkB=r * 72,
                                       connectionstyle="arc3,rad=0.25"),
                        alpha=0.9, zorder=3)

    # draw nodes
    for t, x in enumerate(xs):
        for s, y in enumerate(ys):
            val  = values[t, s]
            col  = node_color_fn(t, s, val)
            attn = 1.0
            if path_edges and (t, s) not in path_edges:
                attn = 0.30

            circle = plt.Circle((x, y), r, color=col, zorder=4,
                                alpha=attn, linewidth=1.5,
                                edgecolor="white")
            ax.add_patch(circle)
            lbl = val_fmt(t, s, val)
            ax.text(x, y, lbl, ha="center", va="center", fontsize=8,
                    fontweight="bold", color="white", zorder=5)

    if extra_fn:
        extra_fn(ax)

    return fig


# ── Plot 03: Forward trellis ───────────────────────────────────────────────────
def plot_forward_trellis():
    max_a = ALPHA.max()
    min_a = ALPHA.min()

    def color_fn(t, s, val):
        intensity = 0.25 + 0.75 * (val - min_a) / (max_a - min_a + 1e-12)
        r_hex = int(0x2E * (1 - intensity) + 0xFF * intensity * 0.2)
        g_hex = int(0x86 * intensity)
        b_hex = int(0xAB * intensity)
        return f"#{r_hex:02x}{g_hex:02x}{b_hex:02x}"

    # use fixed blue shades instead
    node_colors = [
        [COLORS["teal"], COLORS["blue"]],
        [COLORS["blue"], COLORS["blue"]],
        [COLORS["blue"], COLORS["blue"]],
    ]
    # brighter = higher alpha value
    alpha_norm = (ALPHA - ALPHA.min()) / (ALPHA.max() - ALPHA.min())

    def color_fn2(t, s, val):
        # interpolate from light blue to dark blue
        intensity = 0.3 + 0.7 * alpha_norm[t, s]
        base = np.array([0x2E, 0x86, 0xAB]) / 255
        white = np.array([1.0, 1.0, 1.0])
        c = white * (1 - intensity) + base * intensity
        return (c[0], c[1], c[2])

    def extra(ax):
        ax.text(2.0, 1.52,
                f"P(O | λ) = α₃(S) + α₃(R) = {ALPHA[2,0]:.5f} + {ALPHA[2,1]:.5f} = {P_OBS:.5f}",
                ha="center", fontsize=10, color=COLORS["dark"],
                fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.4", facecolor="#D6EAF8",
                          edgecolor=COLORS["blue"], alpha=0.9))
        # direction label
        ax.annotate("dirección →", xy=(3.3, 1.55), fontsize=9,
                    color=COLORS["blue"])

    def val_fmt(t, s, val):
        return f"α{t+1}({'S' if s==0 else 'R'})\n{val:.5f}"

    fig = _build_trellis(
        title="Algoritmo Forward — α_t(i) = P(O₁…O_t, q_t=i | λ)",
        values=ALPHA, val_fmt=val_fmt,
        node_color_fn=color_fn2,
        arrow_dir="right", arrow_color=COLORS["blue"],
        extra_fn=extra,
    )
    _save(fig, "03_forward_trellis.png")


# ── Plot 04: Backward trellis ─────────────────────────────────────────────────
def plot_backward_trellis():
    beta_norm = (BETA - BETA.min()) / (BETA.max() - BETA.min() + 1e-12)

    def color_fn(t, s, val):
        intensity = 0.3 + 0.7 * beta_norm[t, s]
        base  = np.array([0xE9, 0x4F, 0x37]) / 255
        white = np.array([1.0, 1.0, 1.0])
        c = white * (1 - intensity) + base * intensity
        return (c[0], c[1], c[2])

    def extra(ax):
        ax.text(1.5, 1.52,
                "Inicialización: β₃(S)=1  β₃(R)=1",
                ha="center", fontsize=9.5, color=COLORS["red"],
                bbox=dict(boxstyle="round,pad=0.3", facecolor="#FDEDEC",
                          edgecolor=COLORS["red"], alpha=0.9))
        ax.annotate("← dirección", xy=(0.6, 1.55), fontsize=9,
                    color=COLORS["red"])
        # cross-check
        cross = (PI[0] * B[0, OBS[0]] * BETA[0, 0] +
                 PI[1] * B[1, OBS[0]] * BETA[0, 1])
        ax.text(2.0, -0.52,
                f"Verificación: Σᵢ π(i)·B(i,O₁)·β₁(i) = {cross:.5f} = P(O|λ) ✓",
                ha="center", fontsize=9, color=COLORS["green"],
                fontweight="bold")

    def val_fmt(t, s, val):
        return f"β{t+1}({'S' if s==0 else 'R'})\n{val:.5f}"

    fig = _build_trellis(
        title="Algoritmo Backward — β_t(i) = P(O_{t+1}…O_T | q_t=i, λ)",
        values=BETA, val_fmt=val_fmt,
        node_color_fn=color_fn,
        arrow_dir="left", arrow_color=COLORS["red"],
        extra_fn=extra,
    )
    _save(fig, "04_backward_trellis.png")


# ── Plot 05: Forward vs Backward comparison ───────────────────────────────────
def plot_forward_vs_backward():
    fig, ax = plt.subplots(figsize=(13, 5.5))
    ax.set_xlim(0, 13)
    ax.set_ylim(-0.5, 4.5)
    ax.axis("off")
    ax.set_title("Forward vs. Backward — ¿Qué sabe cada algoritmo?",
                 fontsize=13, fontweight="bold", pad=14)

    # ── Forward (top row)
    ax.text(0.1, 3.8, "FORWARD  α_t(i)", fontsize=12, fontweight="bold",
            color=COLORS["blue"])
    ax.text(0.1, 3.35, "Acumula pasado + estado actual →", fontsize=10,
            color=COLORS["blue"])

    fwd_boxes = [(1.5, 3.5), (4.5, 3.5), (7.5, 3.5)]
    fwd_info  = ["α₁(i)\n= P(O₁, q₁=i|λ)",
                 "α₂(i)\n= P(O₁,O₂, q₂=i|λ)",
                 "α₃(i)\n= P(O₁,O₂,O₃, q₃=i|λ)"]
    for (x, y), info in zip(fwd_boxes, fwd_info):
        box = mpatches.FancyBboxPatch((x - 1.2, y - 0.55), 2.4, 1.1,
                                      boxstyle="round,pad=0.1",
                                      facecolor="#D6EAF8",
                                      edgecolor=COLORS["blue"], linewidth=1.5)
        ax.add_patch(box)
        ax.text(x, y, info, ha="center", va="center", fontsize=8.5,
                color=COLORS["dark"])
    for i in range(2):
        ax.annotate("", xy=(fwd_boxes[i+1][0]-1.2, fwd_boxes[i+1][1]),
                    xytext=(fwd_boxes[i][0]+1.2, fwd_boxes[i][1]),
                    arrowprops=dict(arrowstyle="->", color=COLORS["blue"],
                                   lw=2.0))

    # ── Backward (middle row)
    ax.text(0.1, 2.3, "BACKWARD  β_t(i)", fontsize=12, fontweight="bold",
            color=COLORS["red"])
    ax.text(0.1, 1.85, "← Acumula futuro dado estado actual", fontsize=10,
            color=COLORS["red"])

    bwd_boxes = [(1.5, 2.0), (4.5, 2.0), (7.5, 2.0)]
    bwd_info  = ["β₁(i)\n= P(O₂,O₃|q₁=i,λ)",
                 "β₂(i)\n= P(O₃|q₂=i,λ)",
                 "β₃(i)\n= 1  (init)"]
    for (x, y), info in zip(bwd_boxes, bwd_info):
        box = mpatches.FancyBboxPatch((x - 1.2, y - 0.55), 2.4, 1.1,
                                      boxstyle="round,pad=0.1",
                                      facecolor="#FDEDEC",
                                      edgecolor=COLORS["red"], linewidth=1.5)
        ax.add_patch(box)
        ax.text(x, y, info, ha="center", va="center", fontsize=8.5,
                color=COLORS["dark"])
    for i in range(1, -1, -1):
        ax.annotate("", xy=(bwd_boxes[i][0]+1.2, bwd_boxes[i][1]),
                    xytext=(bwd_boxes[i+1][0]-1.2, bwd_boxes[i+1][1]),
                    arrowprops=dict(arrowstyle="->", color=COLORS["red"],
                                   lw=2.0))

    # ── Combined γ
    gamma_box = mpatches.FancyBboxPatch((9.3, 0.3), 3.4, 3.8,
                                        boxstyle="round,pad=0.15",
                                        facecolor="#E8F8F5",
                                        edgecolor=COLORS["green"], linewidth=2.5)
    ax.add_patch(gamma_box)
    ax.text(11.0, 3.8, "JUNTOS", ha="center", fontsize=12,
            fontweight="bold", color=COLORS["green"])
    ax.text(11.0, 3.35, "γ_t(i) = P(q_t=i | O, λ)", ha="center",
            fontsize=10, color=COLORS["dark"], fontweight="bold")
    ax.text(11.0, 2.8, "α_t(i) · β_t(i)", ha="center", fontsize=12,
            color=COLORS["dark"])
    ax.text(11.0, 2.5, "─" * 16, ha="center", fontsize=10,
            color=COLORS["dark"])
    ax.text(11.0, 2.2, "P(O | λ)", ha="center", fontsize=12,
            color=COLORS["dark"])
    ax.text(11.0, 1.6, "= Posterior completo\nde cada estado", ha="center",
            fontsize=10, color=COLORS["green"], style="italic")

    # γ values
    ax.text(11.0, 1.0, "Ejemplo:", ha="center", fontsize=9,
            color=COLORS["gray"])
    ax.text(11.0, 0.65, "γ₁(S)=0.791  γ₁(R)=0.209", ha="center",
            fontsize=8.5, color=COLORS["dark"])
    ax.text(11.0, 0.35, "γ₃(R)=0.904  →  Lluvia con 90%", ha="center",
            fontsize=8.5, color=COLORS["dark"])

    # comparison table
    ax.text(0.1, 1.2, "¿Cuándo usar cada uno?", fontsize=11,
            fontweight="bold", color=COLORS["dark"])
    rows = [
        ("Forward solo",   "P(O|λ)",          "→",  "Evaluación, reconocimiento"),
        ("Backward solo",  "complemento",     "←",  "Rara vez solo"),
        ("α × β = γ",     "P(q_t=i|O,λ)",    "↔",  "Suavizado, Baum-Welch"),
    ]
    col_x = [0.2, 3.3, 5.3, 6.2]
    headers = ["Algoritmo", "Computa", "Dir.", "Uso principal"]
    for j, (hdr, cx) in enumerate(zip(headers, col_x)):
        ax.text(cx, 0.85, hdr, fontsize=9, fontweight="bold",
                color=COLORS["gray"])
    for i, (alg, comp, direc, uso) in enumerate(rows):
        y = 0.55 - i * 0.28
        for j, (val, cx) in enumerate(zip([alg, comp, direc, uso], col_x)):
            ax.text(cx, y, val, fontsize=8.5, color=COLORS["dark"])

    _save(fig, "05_forward_vs_backward.png")


# ── Plot 06: γ posterior bar chart ────────────────────────────────────────────
def plot_gamma_posteriors():
    fig, ax = plt.subplots(figsize=(8, 5))

    bar_w = 0.5
    xs    = [1, 2, 3]

    for t, x in enumerate(xs):
        g_s = GAMMA[t, 0]
        g_r = GAMMA[t, 1]
        # Sol bar
        ax.bar(x, g_s, bar_w, color=COLORS["blue"], alpha=0.85,
               label="Sol (S)" if t == 0 else "")
        # Lluvia bar (stacked)
        ax.bar(x, g_r, bar_w, bottom=g_s, color=COLORS["red"], alpha=0.85,
               label="Lluvia (R)" if t == 0 else "")

        # percentage labels
        if g_s > 0.05:
            ax.text(x, g_s / 2, f"{g_s*100:.1f}%", ha="center", va="center",
                    fontsize=11, fontweight="bold", color="white")
        if g_r > 0.05:
            ax.text(x, g_s + g_r / 2, f"{g_r*100:.1f}%", ha="center",
                    va="center", fontsize=11, fontweight="bold", color="white")

    ax.set_xticks(xs)
    obs_tick = ["t=1\n(O=0, sin ☂)", "t=2\n(O=1, con ☂)", "t=3\n(O=1, con ☂)"]
    ax.set_xticklabels(obs_tick, fontsize=10)
    ax.set_ylabel("P(estado | O, λ)", fontsize=11)
    ax.set_ylim(0, 1.12)
    ax.set_title("Probabilidades Posteriores γ_t(i) = P(q_t=i | O, λ)",
                 fontsize=13, fontweight="bold")
    ax.legend(fontsize=11, loc="upper right")
    ax.axhline(0.5, color=COLORS["gray"], lw=0.8, ls="--", alpha=0.5)
    ax.grid(axis="y", alpha=0.4)
    ax.set_axisbelow(True)

    ax.text(1.0, 1.05, "79% Sol", ha="center", fontsize=9,
            color=COLORS["blue"], fontweight="bold")
    ax.text(2.0, 1.05, "87% Lluvia", ha="center", fontsize=9,
            color=COLORS["red"], fontweight="bold")
    ax.text(3.0, 1.05, "90% Lluvia", ha="center", fontsize=9,
            color=COLORS["red"], fontweight="bold")

    plt.tight_layout()
    _save(fig, "06_gamma_posteriors.png")


# ── Plot 07: Viterbi trellis ───────────────────────────────────────────────────
def plot_viterbi_trellis():
    path_edges = {(0, 0), (1, 1), (2, 1)}   # S, R, R = (t,s) pairs

    # backpointer arrows: at t=2 both came from S(0), at t=3 both came from R(1)
    psi_arrows = [
        (1, 0, 0),   # t=2, state S ← from S
        (1, 1, 0),   # t=2, state R ← from S
        (2, 0, 1),   # t=3, state S ← from R
        (2, 1, 1),   # t=3, state R ← from R
    ]

    delta_norm = (DELTA - DELTA.min()) / (DELTA.max() - DELTA.min() + 1e-12)

    def color_fn(t, s, val):
        intensity = 0.3 + 0.7 * delta_norm[t, s]
        base  = np.array([0x27, 0xAE, 0x60]) / 255
        white = np.array([1.0, 1.0, 1.0])
        c = white * (1 - intensity) + base * intensity
        return (c[0], c[1], c[2])

    def val_fmt(t, s, val):
        return f"δ{t+1}({'S' if s==0 else 'R'})\n{val:.5f}"

    def extra(ax):
        ax.text(2.0, 1.52,
                "Camino óptimo: S → R → R  (línea verde)",
                ha="center", fontsize=10, fontweight="bold",
                color=COLORS["green"],
                bbox=dict(boxstyle="round,pad=0.35", facecolor="#D5F5E3",
                          edgecolor=COLORS["green"], alpha=0.9))
        ax.text(2.0, -0.52,
                "Flechas naranjas = backpointers ψ   |   Nodos atenuados = no óptimos",
                ha="center", fontsize=8.5, color=COLORS["gray"])
        # backtrack annotation
        ax.text(3.55, 0.0, "Mejor\nen t=3:\nLluvia",
                ha="left", va="center", fontsize=8.5, color=COLORS["dark"])

    fig = _build_trellis(
        title="Algoritmo de Viterbi — δ_t(i) = probabilidad máxima de camino",
        values=DELTA, val_fmt=val_fmt,
        node_color_fn=color_fn,
        arrow_dir="right", arrow_color=COLORS["green"],
        extra_fn=extra,
        psi_arrows=psi_arrows,
        path_edges=path_edges,
    )
    _save(fig, "07_viterbi_trellis.png")


# ── Plot 08: Baum-Welch convergence ───────────────────────────────────────────
def plot_baum_welch_convergencia():
    # generate a T=60 sequence from true params
    rng = np.random.default_rng(42)
    long_obs = _simulate(PI, A, B, length=60, rng=rng)

    # initial parameters (slight perturbation from true to show convergence)
    pi0 = np.array([0.5, 0.5])
    a0  = np.array([[0.6, 0.4], [0.5, 0.5]])
    b0  = np.array([[0.7, 0.3], [0.3, 0.7]])

    pi_cur, a_cur, b_cur = pi0.copy(), a0.copy(), b0.copy()
    log_likes = []
    n_iter = 35

    for _ in range(n_iter):
        pi_cur, a_cur, b_cur, ll = _baum_welch_step(long_obs, pi_cur, a_cur, b_cur)
        log_likes.append(ll)

    fig, ax = plt.subplots(figsize=(10, 5))

    iters = list(range(1, n_iter + 1))
    ax.plot(iters, log_likes, color=COLORS["blue"], lw=2.5, marker="o",
            markersize=5, label="log P(O | λ)")

    # convergence line
    converged_ll = log_likes[-1]
    ax.axhline(converged_ll, color=COLORS["gray"], lw=1.2, ls="--",
               alpha=0.8, label=f"Convergencia ≈ {converged_ll:.2f}")

    ax.set_xlabel("Iteración", fontsize=12)
    ax.set_ylabel("log P(O | λ)", fontsize=12)
    ax.set_title(
        "Baum-Welch: Convergencia de la Log-Verosimilitud (T=60, N=2)",
        fontsize=13, fontweight="bold"
    )
    ax.legend(fontsize=11)
    ax.grid(alpha=0.4)

    # monotonicity check annotation
    is_monotone = all(log_likes[i] <= log_likes[i+1] + 1e-10
                      for i in range(len(log_likes)-1))
    ax.text(0.97, 0.05,
            "✓ Monótonamente no decreciente\n  (garantía del algoritmo EM)",
            transform=ax.transAxes, ha="right", va="bottom",
            fontsize=9.5, color=COLORS["green"],
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#D5F5E3",
                      edgecolor=COLORS["green"], alpha=0.85))

    plt.tight_layout()
    _save(fig, "08_baum_welch_convergencia.png")


# ── Plot 09: Parameters before / after ───────────────────────────────────────
def plot_parametros_antes_despues():
    fig, axes = plt.subplots(2, 2, figsize=(11, 7))

    titles = [
        "A original (λ₀)",
        f"A actualizada (1 iteración)",
        "B original (λ₀)",
        f"B actualizada (1 iteración)",
    ]
    mats = [A, A_HAT, B, B_HAT]
    row_labels_ab = [["S", "R"], ["S", "R"]]
    col_labels_a  = ["→ S", "→ R"]
    col_labels_b  = ["O=0", "O=1"]
    col_labels = [col_labels_a, col_labels_a, col_labels_b, col_labels_b]
    colors_border = [COLORS["blue"], COLORS["blue"],
                     COLORS["orange"], COLORS["orange"]]

    for idx, (ax, title, mat, cl, cb) in enumerate(
            zip(axes.flat, titles, mats, col_labels, colors_border)):

        im = ax.imshow(mat, vmin=0, vmax=1, cmap="Blues" if idx < 2 else "Oranges",
                       aspect="auto")
        ax.set_title(title, fontsize=11, fontweight="bold", color=cb)

        ax.set_xticks(range(mat.shape[1]))
        ax.set_xticklabels(cl, fontsize=10)
        ax.set_yticks(range(mat.shape[0]))
        ax.set_yticklabels(["S", "R"], fontsize=10)

        for i in range(mat.shape[0]):
            for j in range(mat.shape[1]):
                val = mat[i, j]
                tc = "white" if val > 0.55 else COLORS["dark"]
                ax.text(j, i, f"{val:.3f}", ha="center", va="center",
                        fontsize=12, fontweight="bold", color=tc)

        for spine in ax.spines.values():
            spine.set_edgecolor(cb)
            spine.set_linewidth(2.0)

    # overall title / annotation
    fig.suptitle("Parámetros antes y después de una iteración de Baum-Welch",
                 fontsize=13, fontweight="bold", y=1.01)

    # highlight key changes
    ax_list = list(axes.flat)
    # A_RR: 0.6 → 0.929  (ax_list[1], cell [1,1])
    ax_list[1].add_patch(mpatches.FancyBboxPatch(
        (0.5, 0.5), 1.0, 1.0,
        boxstyle="round,pad=0.05",
        facecolor="none", edgecolor=COLORS["red"], linewidth=3,
        transform=ax_list[1].transData, clip_on=False
    ))
    ax_list[1].text(1.05, -0.6, "↑ A_RR: 0.60→0.93\nLluvia más pegajosa",
                    ha="center", fontsize=8.5, color=COLORS["red"],
                    fontweight="bold")

    # B_R1: 0.8 → 0.895  (ax_list[3], cell [1,1])
    ax_list[3].add_patch(mpatches.FancyBboxPatch(
        (0.5, 0.5), 1.0, 1.0,
        boxstyle="round,pad=0.05",
        facecolor="none", edgecolor=COLORS["red"], linewidth=3,
        transform=ax_list[3].transData, clip_on=False
    ))
    ax_list[3].text(1.05, -0.6, "↑ B(R,1): 0.80→0.90\nLluvia más distinguible",
                    ha="center", fontsize=8.5, color=COLORS["red"],
                    fontweight="bold")

    plt.tight_layout()
    _save(fig, "09_parametros_antes_despues.png")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("Generando imágenes para clase/20_hmm/ …")
    plot_mc_vs_hmm()
    plot_estructura_hmm()
    plot_forward_trellis()
    plot_backward_trellis()
    plot_forward_vs_backward()
    plot_gamma_posteriors()
    plot_viterbi_trellis()
    plot_baum_welch_convergencia()
    plot_parametros_antes_despues()
    print(f"\nListo. {len(list(IMAGES_DIR.glob('*.png')))} imágenes en {IMAGES_DIR}")


if __name__ == "__main__":
    main()
