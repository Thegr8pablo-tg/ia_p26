"""
lab_deep_rl.py — Genera las imágenes pedagógicas para las páginas 06-08 del
módulo 23 (aprendizaje por refuerzo profundo).

Ejecución:
    cd clase/23_reinforcement_learning/deep_rl && python lab_deep_rl.py

Genera 6 imágenes en:
    clase/23_reinforcement_learning/images/

    08_dqn_architecture.png      — diagrama de la red neuronal DQN
    09_experience_replay.png     — buffer de repetición de experiencia
    10_target_network.png        — red online vs red objetivo
    11_convergence_comparison.png — comparación Q-tabla / SARSA / Q-learning / DQN
    12_loss_curve.png            — pérdida de entrenamiento DQN
    13_cartpole_frames.png       — fotogramas de un episodio resuelto

Dependencias: torch (CPU), gymnasium[classic-control], numpy, matplotlib, tqdm
"""

from __future__ import annotations

import collections
import random
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import gymnasium as gym

# ── Reproducibilidad ──────────────────────────────────────────────────────────
np.random.seed(42)
torch.manual_seed(42)
random.seed(42)

# ── Estilo ────────────────────────────────────────────────────────────────────
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

IMAGES_DIR = Path("../images")
IMAGES_DIR.mkdir(exist_ok=True)

DEVICE = torch.device("cpu")


def _save(fig, name: str) -> None:
    fig.savefig(IMAGES_DIR / name, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"  Guardado: {name}")


# ============================================================================
# Plot 08 — Arquitectura DQN
# ============================================================================
def plot_dqn_architecture() -> None:
    """Diagrama de la red neuronal DQN: 4 → 64 → 64 → 2."""
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 6)
    ax.set_axis_off()
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")

    # ── Definición de capas ───────────────────────────────────────────────────
    layers = [
        {"x": 1.1, "n": 4,  "color": COLORS["blue"],   "label": "Entrada\n(4 neuronas)",
         "neuron_labels": ["pos. carro", "vel. carro", "ángulo poste", "vel. angular"]},
        {"x": 4.0, "n": 5,  "color": COLORS["teal"],   "label": "ReLU (64)",
         "neuron_labels": None},  # representamos 64 con 5 círculos + puntos suspensivos
        {"x": 7.0, "n": 5,  "color": COLORS["teal"],   "label": "ReLU (64)",
         "neuron_labels": None},
        {"x": 9.9, "n": 2,  "color": COLORS["orange"], "label": "Salida\n(2 neuronas)",
         "neuron_labels": ["izquierda", "derecha"]},
    ]

    neuron_radius = 0.28
    y_centers: list[list[float]] = []

    for layer in layers:
        n = layer["n"]
        x = layer["x"]
        # Centrar verticalmente
        total_h = (n - 1) * 1.0
        y_start = 3.0 - total_h / 2
        ys = [y_start + i * 1.0 for i in range(n)]
        y_centers.append(ys)

        for idx, y in enumerate(ys):
            circle = plt.Circle((x, y), neuron_radius,
                                 facecolor=layer["color"], edgecolor="white",
                                 linewidth=1.5, zorder=4)
            ax.add_patch(circle)

        # Etiquetas de neuronas (sólo entrada y salida)
        if layer["neuron_labels"] is not None:
            for idx, (y, lbl) in enumerate(zip(ys, layer["neuron_labels"])):
                ha = "right" if x < 5.5 else "left"
                offset = -0.5 if x < 5.5 else 0.5
                ax.text(x + offset, y, lbl, ha=ha, va="center",
                        fontsize=8.5, color=COLORS["dark"])

        # Puntos suspensivos para capas ocultas (indicar 64 neuronas)
        if layer["neuron_labels"] is None:
            ax.text(x, ys[-1] - 1.1, "·  ·  ·", ha="center", va="center",
                    fontsize=14, color=COLORS["gray"])

        # Etiqueta de capa
        ax.text(x, 0.35, layer["label"], ha="center", va="bottom",
                fontsize=9.5, color=COLORS["dark"], fontweight="bold",
                multialignment="center")

    # ── Conexiones entre capas ────────────────────────────────────────────────
    for li in range(len(layers) - 1):
        ys_from = y_centers[li]
        ys_to   = y_centers[li + 1]
        x_from  = layers[li]["x"] + neuron_radius
        x_to    = layers[li + 1]["x"] - neuron_radius
        for y1 in ys_from:
            for y2 in ys_to:
                ax.plot([x_from, x_to], [y1, y2],
                        color=COLORS["gray"], alpha=0.18, lw=0.7, zorder=2)

    # ── Etiqueta de pesos θ ───────────────────────────────────────────────────
    for li in range(len(layers) - 1):
        mx = (layers[li]["x"] + layers[li + 1]["x"]) / 2
        ax.text(mx, 5.55, f"$W_{li+1}, b_{li+1}$", ha="center", va="center",
                fontsize=9, color=COLORS["purple"])

    ax.set_title(
        "Arquitectura DQN: $Q_\\theta(s, a)$ — red neuronal 4 → 64 → 64 → 2",
        fontsize=12, color=COLORS["dark"], pad=10)

    _save(fig, "08_dqn_architecture.png")


# ============================================================================
# Plot 09 — Experience Replay Buffer
# ============================================================================
def plot_experience_replay() -> None:
    """Diagrama conceptual del replay buffer."""
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 5.5)
    ax.set_axis_off()
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")

    # ── Buffer principal ──────────────────────────────────────────────────────
    buf_x, buf_y, buf_w, buf_h = 3.0, 0.8, 5.0, 3.8
    buf_box = FancyBboxPatch((buf_x, buf_y), buf_w, buf_h,
                             boxstyle="round,pad=0.1",
                             facecolor="#F8F9FA", edgecolor=COLORS["dark"],
                             linewidth=2, zorder=2)
    ax.add_patch(buf_box)
    ax.text(buf_x + buf_w / 2, buf_y + buf_h + 0.22,
            r"Replay Buffer $\mathcal{D}$  (10 000 transiciones)",
            ha="center", va="bottom",
            fontsize=11, fontweight="bold", color=COLORS["dark"])

    # ── Filas de transiciones dentro del buffer ───────────────────────────────
    row_labels = [
        (r"$(s_1,\ a_1,\ r_1,\ s'_1)$",  0.15),
        (r"$(s_2,\ a_2,\ r_2,\ s'_2)$",  0.15),
        (r"$(s_3,\ a_3,\ r_3,\ s'_3)$",  0.40),
        (r"$(s_4,\ a_4,\ r_4,\ s'_4)$",  0.65),
        (r"$(s_5,\ a_5,\ r_5,\ s'_5)$",  0.90),
        (r"$\cdots$",                      1.00),
        (r"$(s_N,\ a_N,\ r_N,\ s'_N)$",  0.15),
    ]
    n_rows = len(row_labels)
    row_h = buf_h * 0.80 / n_rows
    for i, (lbl, alpha) in enumerate(row_labels):
        ry = buf_y + buf_h * 0.90 - i * (buf_h * 0.80 / n_rows)
        fc_alpha = max(0.08, 0.65 - i * 0.08)
        row_rect = FancyBboxPatch(
            (buf_x + 0.2, ry - row_h * 0.35), buf_w - 0.4, row_h * 0.7,
            boxstyle="round,pad=0.04",
            facecolor=COLORS["blue"], edgecolor="none",
            alpha=fc_alpha if lbl != r"$\cdots$" else 0.0,
            linewidth=0, zorder=3)
        ax.add_patch(row_rect)
        ax.text(buf_x + buf_w / 2, ry, lbl, ha="center", va="center",
                fontsize=9, color="white" if fc_alpha > 0.3 else COLORS["gray"],
                alpha=min(1.0, alpha + 0.3))

    # ── Caja Ambiente ─────────────────────────────────────────────────────────
    env_x, env_y = 0.2, 2.5
    env_box = FancyBboxPatch((env_x, env_y), 2.0, 0.9,
                             boxstyle="round,pad=0.08",
                             facecolor="#EBF5FB", edgecolor=COLORS["blue"],
                             linewidth=1.8, zorder=3)
    ax.add_patch(env_box)
    ax.text(env_x + 1.0, env_y + 0.45, "Ambiente", ha="center", va="center",
            fontsize=10, fontweight="bold", color=COLORS["blue"])

    # ── Caja Optimizador ──────────────────────────────────────────────────────
    opt_x, opt_y = 8.8, 2.5
    opt_box = FancyBboxPatch((opt_x, opt_y), 2.0, 0.9,
                             boxstyle="round,pad=0.08",
                             facecolor="#FEF9E7", edgecolor=COLORS["orange"],
                             linewidth=1.8, zorder=3)
    ax.add_patch(opt_box)
    ax.text(opt_x + 1.0, opt_y + 0.45, "Optimizador", ha="center", va="center",
            fontsize=10, fontweight="bold", color=COLORS["orange"])

    # ── Flecha Ambiente → Buffer ──────────────────────────────────────────────
    ax.annotate("",
                xy=(buf_x, 2.95), xytext=(env_x + 2.0, 2.95),
                arrowprops=dict(arrowstyle="-|>", color=COLORS["blue"], lw=2.0))
    ax.text(1.5 + (buf_x - 2.2) / 2, 3.20,
            r"almacena $(s, a, r, s')$",
            ha="center", va="bottom", fontsize=9, color=COLORS["blue"])

    # ── Flecha Buffer → Optimizador ───────────────────────────────────────────
    ax.annotate("",
                xy=(opt_x, 2.95), xytext=(buf_x + buf_w, 2.95),
                arrowprops=dict(arrowstyle="-|>", color=COLORS["orange"], lw=2.0))
    ax.text(buf_x + buf_w + (opt_x - buf_x - buf_w) / 2, 3.20,
            "muestra mini-lote (64)",
            ha="center", va="bottom", fontsize=9, color=COLORS["orange"])

    ax.set_title(
        "Repetición de experiencia: romper la correlación temporal",
        fontsize=12, color=COLORS["dark"], pad=10)

    _save(fig, "09_experience_replay.png")


# ============================================================================
# Plot 10 — Target Network
# ============================================================================
def plot_target_network() -> None:
    """Diagrama de red online vs red objetivo."""
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 5.5)
    ax.set_axis_off()
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")

    # ── Red Online ────────────────────────────────────────────────────────────
    online_x, online_y = 0.5, 2.2
    online_w, online_h = 3.8, 2.2
    online_box = FancyBboxPatch((online_x, online_y), online_w, online_h,
                                boxstyle="round,pad=0.1",
                                facecolor="#EBF5FB", edgecolor=COLORS["blue"],
                                linewidth=2.5, zorder=3)
    ax.add_patch(online_box)
    ax.text(online_x + online_w / 2, online_y + online_h * 0.72,
            r"Red online $Q_\theta$",
            ha="center", va="center",
            fontsize=12, fontweight="bold", color=COLORS["blue"])
    ax.text(online_x + online_w / 2, online_y + online_h * 0.40,
            "(se actualiza cada paso)",
            ha="center", va="center",
            fontsize=9.5, color=COLORS["dark"])
    ax.text(online_x + online_w / 2, online_y + online_h * 0.15,
            r"$\theta \leftarrow \theta - \alpha \nabla_\theta L$",
            ha="center", va="center",
            fontsize=9, color=COLORS["blue"])

    # ── Red Objetivo ──────────────────────────────────────────────────────────
    target_x, target_y = 6.7, 2.2
    target_w, target_h = 3.8, 2.2
    target_box = FancyBboxPatch((target_x, target_y), target_w, target_h,
                                boxstyle="round,pad=0.1",
                                facecolor="#FEF9E7", edgecolor=COLORS["orange"],
                                linewidth=2.5, zorder=3)
    ax.add_patch(target_box)
    ax.text(target_x + target_w / 2, target_y + target_h * 0.72,
            r"Red objetivo $Q_{\theta^-}$",
            ha="center", va="center",
            fontsize=12, fontweight="bold", color=COLORS["orange"])
    ax.text(target_x + target_w / 2, target_y + target_h * 0.40,
            "(congelada)",
            ha="center", va="center",
            fontsize=9.5, color=COLORS["dark"])
    ax.text(target_x + target_w / 2, target_y + target_h * 0.15,
            r"$\theta^- \leftarrow \theta$ cada $C{=}50$ pasos",
            ha="center", va="center",
            fontsize=9, color=COLORS["orange"])

    # ── Flecha de copia ───────────────────────────────────────────────────────
    arrow_y = online_y + online_h / 2
    ax.annotate("",
                xy=(target_x, arrow_y), xytext=(online_x + online_w, arrow_y),
                arrowprops=dict(arrowstyle="-|>", color=COLORS["dark"],
                                lw=2.2, connectionstyle="arc3,rad=0.0"))
    ax.text((online_x + online_w + target_x) / 2, arrow_y + 0.22,
            r"copia cada $C{=}50$ pasos",
            ha="center", va="bottom", fontsize=9.5, color=COLORS["dark"])

    # ── Ecuación TD target ────────────────────────────────────────────────────
    eq_y = 1.5
    eq_box = FancyBboxPatch((2.0, 0.35), 7.0, 1.0,
                            boxstyle="round,pad=0.1",
                            facecolor="#FDFEFE", edgecolor=COLORS["purple"],
                            linewidth=1.5, zorder=2)
    ax.add_patch(eq_box)
    ax.text(5.5, 0.85,
            r"$y_i = r + \gamma \max_b Q_{\theta^-}(s', b)$",
            ha="center", va="center",
            fontsize=12, color=COLORS["purple"])
    ax.text(5.5, 0.50,
            r"el objetivo $y_i$ usa $Q_{\theta^-}$ (congelada) — blanco estable",
            ha="center", va="center",
            fontsize=9, color=COLORS["gray"])

    # ── Anotación apuntando a red objetivo ────────────────────────────────────
    ax.annotate("",
                xy=(target_x + target_w / 2, target_y),
                xytext=(5.5, 1.35),
                arrowprops=dict(arrowstyle="-|>", color=COLORS["purple"],
                                lw=1.5, linestyle="dashed"))

    ax.set_title(
        "Red objetivo: fijar el blanco $y_i$ para estabilizar el entrenamiento",
        fontsize=12, color=COLORS["dark"], pad=10)

    _save(fig, "10_target_network.png")


# ============================================================================
# Métodos tabulares — CartPole discretizado
# ============================================================================

def _make_bins():
    """Genera los bins de discretización para CartPole-v1."""
    cart_pos_bins  = np.linspace(-2.4, 2.4, 11)
    cart_vel_bins  = np.linspace(-3.0, 3.0, 11)
    pole_ang_bins  = np.linspace(-0.2, 0.2, 11)
    pole_vel_bins  = np.linspace(-3.0, 3.0, 11)
    return cart_pos_bins, cart_vel_bins, pole_ang_bins, pole_vel_bins


def _discretize(obs, bins):
    """Convierte observación continua a índice discreto."""
    cart_pos_bins, cart_vel_bins, pole_ang_bins, pole_vel_bins = bins
    i0 = int(np.digitize(obs[0], cart_pos_bins)) - 1
    i1 = int(np.digitize(obs[1], cart_vel_bins)) - 1
    i2 = int(np.digitize(obs[2], pole_ang_bins)) - 1
    i3 = int(np.digitize(obs[3], pole_vel_bins)) - 1
    # Clip a [0, 9]
    i0 = max(0, min(9, i0))
    i1 = max(0, min(9, i1))
    i2 = max(0, min(9, i2))
    i3 = max(0, min(9, i3))
    return i0, i1, i2, i3


def run_qtable(n_episodes=500, alpha=0.1, gamma=0.99,
               eps_start=1.0, eps_end=0.05, eps_decay=0.995):
    """Q-learning tabular en CartPole-v1 con estado discretizado."""
    env = gym.make("CartPole-v1")
    bins = _make_bins()
    Q = np.zeros((10, 10, 10, 10, 2))
    eps = eps_start
    returns = []

    for _ in range(n_episodes):
        obs, _ = env.reset()
        state = _discretize(obs, bins)
        done = False
        G = 0.0

        while not done:
            if np.random.random() < eps:
                action = env.action_space.sample()
            else:
                action = int(np.argmax(Q[state]))

            obs2, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            G += reward
            next_state = _discretize(obs2, bins)

            # Q-learning update (off-policy)
            best_next = float(np.max(Q[next_state])) if not done else 0.0
            Q[state][action] += alpha * (
                reward + gamma * best_next - Q[state][action]
            )
            state = next_state

        eps = max(eps_end, eps * eps_decay)
        returns.append(G)

    env.close()
    return returns


def run_sarsa(n_episodes=500, alpha=0.1, gamma=0.99,
              eps_start=1.0, eps_end=0.05, eps_decay=0.995):
    """SARSA (on-policy) en CartPole-v1 con estado discretizado."""
    env = gym.make("CartPole-v1")
    bins = _make_bins()
    Q = np.zeros((10, 10, 10, 10, 2))
    eps = eps_start
    returns = []

    for _ in range(n_episodes):
        obs, _ = env.reset()
        state = _discretize(obs, bins)

        if np.random.random() < eps:
            action = env.action_space.sample()
        else:
            action = int(np.argmax(Q[state]))

        done = False
        G = 0.0

        while not done:
            obs2, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            G += reward
            next_state = _discretize(obs2, bins)

            if done:
                next_action = 0  # irrelevante para estado terminal
                next_q = 0.0
            else:
                if np.random.random() < eps:
                    next_action = env.action_space.sample()
                else:
                    next_action = int(np.argmax(Q[next_state]))
                next_q = float(Q[next_state][next_action])

            # SARSA update (on-policy)
            Q[state][action] += alpha * (
                reward + gamma * next_q - Q[state][action]
            )
            state = next_state
            action = next_action

        eps = max(eps_end, eps * eps_decay)
        returns.append(G)

    env.close()
    return returns


def run_qlearning_tabular(n_episodes=500, alpha=0.1, gamma=0.99,
                           eps_start=1.0, eps_end=0.05, eps_decay=0.995):
    """Q-learning tabular (alias explícito) en CartPole-v1."""
    return run_qtable(n_episodes=n_episodes, alpha=alpha, gamma=gamma,
                      eps_start=eps_start, eps_end=eps_end, eps_decay=eps_decay)


# ============================================================================
# DQN — red neuronal + replay buffer + red objetivo
# ============================================================================

class DQN(nn.Module):
    """Red neuronal 4 → 64 → 64 → 2 con activaciones ReLU."""

    def __init__(self) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(4, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, 2),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:  # type: ignore[override]
        return self.net(x)


class ReplayBuffer:
    """Buffer de repetición de experiencia con capacidad fija."""

    def __init__(self, capacity: int = 10_000) -> None:
        self.buf: collections.deque = collections.deque(maxlen=capacity)

    def push(self, s, a, r, s_next, done) -> None:
        self.buf.append((s, a, r, s_next, done))

    def sample(self, batch_size: int = 64):
        batch = random.sample(self.buf, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        return (
            torch.tensor(np.array(states), dtype=torch.float32, device=DEVICE),
            torch.tensor(actions, dtype=torch.long, device=DEVICE),
            torch.tensor(rewards, dtype=torch.float32, device=DEVICE),
            torch.tensor(np.array(next_states), dtype=torch.float32, device=DEVICE),
            torch.tensor(dones, dtype=torch.float32, device=DEVICE),
        )

    def __len__(self) -> int:
        return len(self.buf)


def run_dqn(n_episodes=500, alpha=1e-3, gamma=0.99,
            eps_start=1.0, eps_end=0.05, eps_decay=0.995,
            batch_size=64, target_update=50, buffer_capacity=10_000):
    """
    Entrena DQN en CartPole-v1.

    Returns:
        episode_returns: lista de retornos por episodio
        loss_history: lista de tuplas (step, loss_value)
    """
    env = gym.make("CartPole-v1")
    torch.manual_seed(42)
    np.random.seed(42)
    random.seed(42)

    online_net = DQN().to(DEVICE)
    target_net = DQN().to(DEVICE)
    target_net.load_state_dict(online_net.state_dict())
    target_net.eval()

    optimizer = optim.Adam(online_net.parameters(), lr=alpha)
    buffer = ReplayBuffer(capacity=buffer_capacity)

    eps = eps_start
    episode_returns = []
    loss_history: list[tuple[int, float]] = []
    step = 0

    for ep in range(n_episodes):
        obs, _ = env.reset()
        state = np.array(obs, dtype=np.float32)
        done = False
        G = 0.0

        while not done:
            # ε-greedy
            if np.random.random() < eps:
                action = env.action_space.sample()
            else:
                with torch.no_grad():
                    q_vals = online_net(
                        torch.tensor(state, dtype=torch.float32, device=DEVICE).unsqueeze(0)
                    )
                action = int(q_vals.argmax(dim=1).item())

            obs2, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            next_state = np.array(obs2, dtype=np.float32)
            G += reward

            buffer.push(state, action, reward, next_state, float(done))
            state = next_state
            step += 1

            # Aprender si el buffer tiene suficientes muestras
            if len(buffer) >= batch_size:
                states_b, actions_b, rewards_b, next_states_b, dones_b = buffer.sample(batch_size)

                with torch.no_grad():
                    # max_b Q_theta-(s', b)
                    next_q = target_net(next_states_b).max(dim=1).values
                    targets = rewards_b + gamma * next_q * (1.0 - dones_b)

                current_q = online_net(states_b).gather(1, actions_b.unsqueeze(1)).squeeze(1)
                loss = nn.functional.mse_loss(current_q, targets)

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                loss_history.append((step, float(loss.item())))

            # Actualizar red objetivo
            if step % target_update == 0:
                target_net.load_state_dict(online_net.state_dict())

        eps = max(eps_end, eps * eps_decay)
        episode_returns.append(G)

    env.close()
    return episode_returns, loss_history


# ============================================================================
# Plot 11 — Comparación de convergencia
# ============================================================================
def plot_convergence_comparison(returns_qtable, returns_sarsa,
                                 returns_qlearning, returns_dqn) -> None:
    """Curvas de aprendizaje de los 4 métodos superpuestas."""
    fig, ax = plt.subplots(figsize=(10, 5))

    methods = [
        ("Q-tabla",    returns_qtable,    COLORS["gray"]),
        ("SARSA",      returns_sarsa,     COLORS["blue"]),
        ("Q-learning", returns_qlearning, COLORS["green"]),
        ("DQN",        returns_dqn,       COLORS["red"]),
    ]

    window = 50

    for label, rets, color in methods:
        eps_arr = np.arange(1, len(rets) + 1)
        ax.plot(eps_arr, rets, alpha=0.20, color=color, lw=0.8)
        # Media móvil
        if len(rets) >= window:
            roll = np.convolve(rets, np.ones(window) / window, mode="valid")
            ax.plot(np.arange(window, len(rets) + 1), roll,
                    color=color, lw=2.2, label=label)

    ax.axhline(475, color=COLORS["dark"], ls="--", lw=1.2, alpha=0.6,
               label="Umbral resuelto (475)")
    ax.set_xlabel("Episodio", fontsize=11)
    ax.set_ylabel("Recompensa del episodio", fontsize=11)
    ax.set_title(
        "Convergencia: CartPole-v1 — 4 métodos",
        fontsize=13, color=COLORS["dark"])
    ax.legend(fontsize=10, loc="upper left")
    ax.set_ylim(0, 520)
    ax.set_xlim(1, len(returns_dqn))

    _save(fig, "11_convergence_comparison.png")


# ============================================================================
# Plot 12 — Curva de pérdida DQN
# ============================================================================
def plot_loss_curve(loss_history) -> None:
    """Pérdida MSE de DQN vs paso de entrenamiento."""
    if not loss_history:
        print("  AVISO: loss_history vacío, omitiendo 12_loss_curve.png")
        return

    steps, losses = zip(*loss_history)
    steps  = np.array(steps)
    losses = np.array(losses)

    # Buffer lleno aproximadamente en el primer paso donde step >= 10000
    buffer_full_step = None
    for s, _l in loss_history:
        if s >= 10_000:
            buffer_full_step = s
            break

    fig, ax = plt.subplots(figsize=(10, 4.5))

    # Línea delgada — valores crudos
    ax.plot(steps, losses, alpha=0.25, color=COLORS["blue"], lw=0.8)

    # Suavizado con ventana de 200
    window = 200
    if len(losses) >= window:
        smooth = np.convolve(losses, np.ones(window) / window, mode="valid")
        ax.plot(steps[window - 1:], smooth,
                color=COLORS["blue"], lw=2.2, label="Pérdida suavizada (ventana=200)")

    if buffer_full_step is not None:
        ax.axvline(buffer_full_step, color=COLORS["orange"],
                   ls="--", lw=1.8, label=f"Buffer lleno (paso ~{buffer_full_step:,})")
        # Usar percentil para posición vertical de la anotación
        y_pos = float(np.percentile(losses, 85))
        y_text = y_pos * 0.95
        ax.annotate(
            "Buffer lleno —\ninicia aprendizaje real",
            xy=(buffer_full_step, y_pos),
            xytext=(buffer_full_step + float(max(steps)) * 0.05, y_text),
            fontsize=8.5, color=COLORS["orange"],
            arrowprops=dict(arrowstyle="->", color=COLORS["orange"], lw=1.2),
            ha="left", va="center")

    ax.set_xlabel("Paso de entrenamiento", fontsize=11)
    ax.set_ylabel("Pérdida MSE", fontsize=11)
    ax.set_title("Pérdida de entrenamiento DQN — CartPole-v1", fontsize=13, color=COLORS["dark"])
    ax.legend(fontsize=10)

    _save(fig, "12_loss_curve.png")


# ============================================================================
# Plot 13 — Fotogramas CartPole (agente entrenado)
# ============================================================================
def plot_cartpole_frames(dqn_model: DQN) -> None:
    """Captura 4 fotogramas espaciados de un episodio resuelto."""
    env = gym.make("CartPole-v1", render_mode="rgb_array")
    dqn_model.eval()

    frames = []
    obs, _ = env.reset()
    state = np.array(obs, dtype=np.float32)
    done = False

    while not done:
        frame = env.render()
        frames.append(frame)
        with torch.no_grad():
            q_vals = dqn_model(
                torch.tensor(state, dtype=torch.float32, device=DEVICE).unsqueeze(0)
            )
        action = int(q_vals.argmax(dim=1).item())
        obs2, _, terminated, truncated, _ = env.step(action)
        done = terminated or truncated
        state = np.array(obs2, dtype=np.float32)

    env.close()

    if len(frames) < 4:
        # Si el episodio fue muy corto, repetir último frame
        while len(frames) < 4:
            frames.append(frames[-1])

    # 4 fotogramas equiespaciados
    n = len(frames)
    indices = [0, n // 3, 2 * n // 3, n - 1]
    selected = [frames[i] for i in indices]
    step_labels = [f"Paso {indices[i]}" for i in range(4)]

    fig, axes = plt.subplots(1, 4, figsize=(12, 3.5))
    for ax, frame, lbl in zip(axes, selected, step_labels):
        ax.imshow(frame)
        ax.set_title(lbl, fontsize=10, color=COLORS["dark"])
        ax.set_axis_off()

    fig.suptitle(
        "Agente DQN entrenado — CartPole-v1 (poste equilibrado)",
        fontsize=12, color=COLORS["dark"], y=1.01)
    fig.tight_layout()

    _save(fig, "13_cartpole_frames.png")


# ============================================================================
# main
# ============================================================================
def main() -> None:
    print(f"Guardando imágenes en: {IMAGES_DIR.resolve()}")
    print()

    # Imágenes conceptuales (no requieren entrenamiento)
    print("Generando diagramas conceptuales...")
    plot_dqn_architecture()
    plot_experience_replay()
    plot_target_network()

    # Entrenamiento de métodos tabulares
    print()
    print("Entrenando métodos tabulares (500 episodios cada uno)...")
    print("  → Q-tabla...")
    returns_qtable = run_qtable()
    print("  → SARSA...")
    returns_sarsa = run_sarsa()
    print("  → Q-learning tabular...")
    returns_qlearning = run_qlearning_tabular()

    # Entrenamiento DQN
    print()
    print("Entrenando DQN (500 episodios)...")
    returns_dqn, loss_history = run_dqn()

    # Gráficas de resultados
    print()
    print("Generando gráficas de resultados...")
    plot_convergence_comparison(returns_qtable, returns_sarsa,
                                returns_qlearning, returns_dqn)
    plot_loss_curve(loss_history)

    # Fotogramas del agente entrenado
    print("  Capturando fotogramas del agente DQN entrenado...")
    # Re-entrenar un modelo breve con semilla fija para obtener un agente razonablemente bueno
    # (usamos el mismo run_dqn que ya terminamos, pero necesitamos el objeto modelo)
    torch.manual_seed(42)
    np.random.seed(42)
    random.seed(42)

    env_tmp = gym.make("CartPole-v1")
    model_for_frames = DQN().to(DEVICE)
    target_tmp = DQN().to(DEVICE)
    target_tmp.load_state_dict(model_for_frames.state_dict())
    target_tmp.eval()
    opt_tmp = optim.Adam(model_for_frames.parameters(), lr=1e-3)
    buf_tmp = ReplayBuffer(capacity=10_000)

    eps = 1.0
    step = 0
    for ep in range(500):
        obs, _ = env_tmp.reset()
        s = np.array(obs, dtype=np.float32)
        done = False
        while not done:
            if np.random.random() < eps:
                a = env_tmp.action_space.sample()
            else:
                with torch.no_grad():
                    qv = model_for_frames(
                        torch.tensor(s, dtype=torch.float32).unsqueeze(0)
                    )
                a = int(qv.argmax(dim=1).item())
            o2, r, te, tr, _ = env_tmp.step(a)
            done = te or tr
            ns = np.array(o2, dtype=np.float32)
            buf_tmp.push(s, a, r, ns, float(done))
            s = ns
            step += 1
            if len(buf_tmp) >= 64:
                sb, ab, rb, nsb, db = buf_tmp.sample(64)
                with torch.no_grad():
                    nq = target_tmp(nsb).max(dim=1).values
                    tgt = rb + 0.99 * nq * (1.0 - db)
                cq = model_for_frames(sb).gather(1, ab.unsqueeze(1)).squeeze(1)
                loss = nn.functional.mse_loss(cq, tgt)
                opt_tmp.zero_grad()
                loss.backward()
                opt_tmp.step()
            if step % 50 == 0:
                target_tmp.load_state_dict(model_for_frames.state_dict())
        eps = max(0.05, eps * 0.995)
    env_tmp.close()

    plot_cartpole_frames(model_for_frames)

    print()
    print("Done.")


if __name__ == "__main__":
    main()
