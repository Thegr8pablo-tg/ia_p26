"""
demo_cartpole.py — Demo interactivo de métodos de RL en CartPole-v1.

Uso:
    python demo_cartpole.py --method dqn                       # ventana live con DQN
    python demo_cartpole.py --method qtable --speed fast       # Q-tabla, actualización rápida
    python demo_cartpole.py --compare --episodes 300           # comparar 4 métodos
    python demo_cartpole.py --method sarsa --episodes 200 --speed slow

En modo live se abre una ventana con 4 paneles:
    - Arriba izquierda : animación del entorno CartPole
    - Arriba derecha   : recompensa por episodio + media móvil
    - Abajo izquierda  : pérdida MSE (DQN) o decaimiento ε (tabular)
    - Abajo derecha    : distribución Q-valores (DQN) o heatmap Q-tabla (tabular)

En modo --compare se ejecutan los 4 métodos en secuencia con barras de progreso
en terminal y al final se abre una sola ventana con las curvas superpuestas.
"""
from __future__ import annotations

import argparse
import collections
import os
import random
import sys
from pathlib import Path

import numpy as np

# ── Detección de entorno headless (antes de importar pyplot) ─────────────────
_has_display = (
    sys.platform in ("darwin", "win32")
    or bool(os.environ.get("DISPLAY"))
    or bool(os.environ.get("WAYLAND_DISPLAY"))
)

import matplotlib
if not _has_display:
    matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import torch
import torch.nn as nn
import torch.optim as optim
import gymnasium as gym
from tqdm import tqdm


# ─────────────────────────────────────────────────────────────────────────────
# Constantes
# ─────────────────────────────────────────────────────────────────────────────
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
}

METHOD_COLORS = {
    "qtable":    COLORS["gray"],
    "sarsa":     COLORS["blue"],
    "qlearning": COLORS["green"],
    "dqn":       COLORS["red"],
}

METHOD_LABELS = {
    "qtable":    "Q-tabla",
    "sarsa":     "SARSA",
    "qlearning": "Q-learning",
    "dqn":       "DQN",
}

# Pasos de entrenamiento entre actualizaciones de la ventana
SPEED_MAP = {"fast": 20, "normal": 5, "slow": 1}

DEVICE = torch.device("cpu")

plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams.update({"font.size": 10, "axes.titlesize": 11})


# ─────────────────────────────────────────────────────────────────────────────
# Modelos RL
# ─────────────────────────────────────────────────────────────────────────────
class DQN(nn.Module):
    """Red neuronal 4 → 64 → 64 → 2 con activaciones ReLU."""

    def __init__(self) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(4, 64), nn.ReLU(),
            nn.Linear(64, 64), nn.ReLU(),
            nn.Linear(64, 2),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class ReplayBuffer:
    """Buffer FIFO de experiencias con capacidad fija."""

    def __init__(self, capacity: int = 10_000) -> None:
        self.buf: collections.deque = collections.deque(maxlen=capacity)

    def push(self, s, a, r, s_next, done) -> None:
        self.buf.append((s, a, r, s_next, done))

    def sample(self, batch_size: int = 64):
        batch = random.sample(self.buf, batch_size)
        s, a, r, ns, d = zip(*batch)
        return (
            torch.tensor(np.array(s),  dtype=torch.float32, device=DEVICE),
            torch.tensor(a,            dtype=torch.long,    device=DEVICE),
            torch.tensor(r,            dtype=torch.float32, device=DEVICE),
            torch.tensor(np.array(ns), dtype=torch.float32, device=DEVICE),
            torch.tensor(d,            dtype=torch.float32, device=DEVICE),
        )

    def __len__(self) -> int:
        return len(self.buf)


# ─────────────────────────────────────────────────────────────────────────────
# Discretización del espacio de estados
# ─────────────────────────────────────────────────────────────────────────────
def _make_bins():
    return (
        np.linspace(-2.4, 2.4, 11),   # posición carro
        np.linspace(-3.0, 3.0, 11),   # velocidad carro
        np.linspace(-0.2, 0.2, 11),   # ángulo poste
        np.linspace(-3.0, 3.0, 11),   # velocidad angular poste
    )


def _disc(obs, bins) -> tuple:
    return tuple(
        max(0, min(9, int(np.digitize(obs[i], bins[i])) - 1))
        for i in range(4)
    )


# ─────────────────────────────────────────────────────────────────────────────
# Ventana matplotlib (modo live)
# ─────────────────────────────────────────────────────────────────────────────
def setup_window(method: str, n_episodes: int) -> dict:
    """Crea figura 2×2 + barra de estado. Devuelve dict con objetos de trazado."""
    fig = plt.figure(figsize=(14, 8))
    gs = gridspec.GridSpec(
        3, 2, figure=fig,
        height_ratios=[4, 4, 0.6],
        hspace=0.40, wspace=0.32
    )

    ax_anim   = fig.add_subplot(gs[0, 0])
    ax_reward = fig.add_subplot(gs[0, 1])
    ax_bot_l  = fig.add_subplot(gs[1, 0])
    ax_bot_r  = fig.add_subplot(gs[1, 1])
    ax_status = fig.add_subplot(gs[2, :])

    # ── Panel de animación ────────────────────────────────────────────────────
    ax_anim.set_axis_off()
    ax_anim.set_title("CartPole-v1", fontsize=11)
    im_anim = ax_anim.imshow(np.full((400, 600, 3), 220, dtype=np.uint8))

    # ── Recompensa por episodio ───────────────────────────────────────────────
    ax_reward.set_xlabel("Episodio")
    ax_reward.set_ylabel("Recompensa")
    ax_reward.set_title("Recompensa por episodio")
    ax_reward.set_xlim(1, n_episodes)
    ax_reward.set_ylim(0, 520)
    line_reward,  = ax_reward.plot([], [], color=METHOD_COLORS[method],
                                    alpha=0.28, lw=0.8)
    line_rolling, = ax_reward.plot([], [], color=METHOD_COLORS[method],
                                    lw=2.0, label="Media 50 ep.")
    ax_reward.axhline(475, color=COLORS["dark"], ls="--", lw=1.0, alpha=0.5,
                      label="Resuelto (475)")
    ax_reward.legend(fontsize=8, loc="upper left")

    # ── Panel inferior izquierdo: pérdida (DQN) o ε (tabular) ────────────────
    if method == "dqn":
        ax_bot_l.set_xlabel("Paso de entrenamiento")
        ax_bot_l.set_ylabel("Pérdida MSE")
        ax_bot_l.set_title("Pérdida DQN")
        line_bl,        = ax_bot_l.plot([], [], color=COLORS["orange"],
                                         alpha=0.28, lw=0.8)
        line_bl_smooth, = ax_bot_l.plot([], [], color=COLORS["red"],
                                         lw=2.0, label="Suavizado (50 pasos)")
        ax_bot_l.legend(fontsize=8)
    else:
        ax_bot_l.set_xlabel("Episodio")
        ax_bot_l.set_ylabel("ε (exploración)")
        ax_bot_l.set_title("Decaimiento de ε")
        ax_bot_l.set_xlim(1, n_episodes)
        ax_bot_l.set_ylim(0.0, 1.05)
        line_bl,       = ax_bot_l.plot([], [], color=COLORS["purple"], lw=1.8)
        line_bl_smooth = None

    # ── Panel inferior derecho: Q-dist (DQN) o Q-heatmap (tabular) ───────────
    if method == "dqn":
        ax_bot_r.set_title("Distribución de Q-valores")
        ax_bot_r.set_xlabel("Q-valor")
        ax_bot_r.set_ylabel("Frecuencia")
        im_qheat = None
    else:
        ax_bot_r.set_title("Q-tabla: ángulo × vel. angular (max Q)")
        ax_bot_r.set_xlabel("Vel. angular del poste")
        ax_bot_r.set_ylabel("Ángulo del poste")
        im_qheat = ax_bot_r.imshow(
            np.zeros((10, 10)), aspect="auto",
            cmap="RdYlGn", vmin=-5, vmax=5,
            origin="lower", interpolation="nearest"
        )
        plt.colorbar(im_qheat, ax=ax_bot_r, fraction=0.046, pad=0.04)

    # ── Barra de estado ───────────────────────────────────────────────────────
    ax_status.set_axis_off()
    status_text = ax_status.text(
        0.5, 0.5,
        f"Iniciando — {METHOD_LABELS[method]}",
        ha="center", va="center", fontsize=11,
        transform=ax_status.transAxes,
        bbox=dict(boxstyle="round,pad=0.3",
                  facecolor="#EBF5FB", edgecolor=COLORS["blue"])
    )

    fig.suptitle(
        f"Demo RL — CartPole-v1: {METHOD_LABELS[method]}",
        fontsize=13, fontweight="bold", color=COLORS["dark"]
    )
    plt.tight_layout()

    return {
        "fig": fig,
        "im_anim": im_anim,
        "ax_anim": ax_anim,
        "ax_reward": ax_reward,
        "line_reward": line_reward,
        "line_rolling": line_rolling,
        "ax_bot_l": ax_bot_l,
        "line_bl": line_bl,
        "line_bl_smooth": line_bl_smooth,
        "ax_bot_r": ax_bot_r,
        "im_qheat": im_qheat,
        "status_text": status_text,
        "method": method,
        # historial de ε para métodos tabulares
        "eps_hist":    [],
        "eps_ep_hist": [],
    }


def update_window(state: dict, frame,
                  reward_history: list, epsilon: float,
                  loss_history: list | None, Q_or_qvals) -> None:
    """Actualiza los 4 paneles y la barra de estado."""
    method = state["method"]

    # ── Animación ─────────────────────────────────────────────────────────────
    state["im_anim"].set_data(frame)
    state["ax_anim"].set_title(f"CartPole-v1  ε={epsilon:.3f}", fontsize=11)

    # ── Recompensa ────────────────────────────────────────────────────────────
    n_ep = len(reward_history)
    if n_ep > 0:
        ep_x = np.arange(1, n_ep + 1)
        state["line_reward"].set_data(ep_x, reward_history)
        if n_ep >= 50:
            roll = np.convolve(reward_history, np.ones(50) / 50, mode="valid")
            state["line_rolling"].set_data(np.arange(50, n_ep + 1), roll)

    # ── Panel inferior izquierdo ──────────────────────────────────────────────
    if method == "dqn":
        if loss_history:
            steps_l = [s for s, _ in loss_history]
            vals_l  = [v for _, v in loss_history]
            state["line_bl"].set_data(steps_l, vals_l)
            p95 = float(np.percentile(vals_l, 95)) if len(vals_l) > 1 else max(vals_l)
            state["ax_bot_l"].set_xlim(0, max(steps_l) + 1)
            state["ax_bot_l"].set_ylim(0, p95 * 1.3 + 1e-6)
            if len(vals_l) >= 50 and state["line_bl_smooth"] is not None:
                smooth = np.convolve(vals_l, np.ones(50) / 50, mode="valid")
                state["line_bl_smooth"].set_data(steps_l[49:], smooth)
    else:
        state["eps_hist"].append(epsilon)
        state["eps_ep_hist"].append(n_ep)
        state["line_bl"].set_data(state["eps_ep_hist"], state["eps_hist"])

    # ── Panel inferior derecho ────────────────────────────────────────────────
    if method == "dqn":
        ax_q = state["ax_bot_r"]
        ax_q.cla()
        ax_q.set_title("Distribución de Q-valores")
        ax_q.set_xlabel("Q-valor")
        ax_q.set_ylabel("Frecuencia")
        if Q_or_qvals is not None and len(Q_or_qvals) > 0:
            ax_q.hist(Q_or_qvals, bins=20,
                      color=COLORS["red"], alpha=0.75, edgecolor="white")
    else:
        if Q_or_qvals is not None:
            # max Q sobre acciones → promedio sobre (cart_pos, cart_vel)
            q_2d = np.max(Q_or_qvals, axis=4).mean(axis=(0, 1))  # (10,10)
            state["im_qheat"].set_data(q_2d)
            lo = float(q_2d.min())
            hi = max(float(q_2d.max()), lo + 0.01)
            state["im_qheat"].set_clim(lo, hi)

    # ── Barra de estado ───────────────────────────────────────────────────────
    avg = (float(np.mean(reward_history[-50:])) if n_ep >= 50
           else float(np.mean(reward_history)) if reward_history
           else 0.0)
    txt = f"Ep {n_ep}  |  ε={epsilon:.3f}  |  Media 50 ep: {avg:.1f}"
    if method == "dqn" and loss_history:
        txt += f"  |  Pérdida: {loss_history[-1][1]:.4f}"
    state["status_text"].set_text(txt)

    state["fig"].canvas.flush_events()
    plt.pause(0.001)


# ─────────────────────────────────────────────────────────────────────────────
# Bucles de entrenamiento — modo live (con ventana)
# ─────────────────────────────────────────────────────────────────────────────

def _train_tabular_live(win_state: dict, n_episodes: int,
                         render_every: int, use_sarsa: bool = False) -> list[float]:
    """Q-learning o SARSA con actualización live de la ventana."""
    alpha = 0.1
    gamma = 0.99
    eps   = 1.0
    bins  = _make_bins()
    Q     = np.zeros((10, 10, 10, 10, 2))
    env   = gym.make("CartPole-v1", render_mode="rgb_array")
    label = "SARSA" if use_sarsa else "Q-learning"
    returns: list[float] = []
    step = 0

    for _ in tqdm(range(n_episodes), desc=label, ncols=70, leave=True):
        obs, _ = env.reset()
        state  = _disc(obs, bins)

        if use_sarsa:
            action = (env.action_space.sample() if np.random.random() < eps
                      else int(np.argmax(Q[state])))
        done = False
        G    = 0.0

        while not done:
            if not use_sarsa:
                action = (env.action_space.sample() if np.random.random() < eps
                          else int(np.argmax(Q[state])))

            obs2, reward, te, tr, _ = env.step(action)
            done = te or tr
            G   += reward
            ns   = _disc(obs2, bins)

            if use_sarsa:
                if done:
                    na, nq = 0, 0.0
                else:
                    na = (env.action_space.sample() if np.random.random() < eps
                          else int(np.argmax(Q[ns])))
                    nq = float(Q[ns][na])
                Q[state][action] += alpha * (reward + gamma * nq - Q[state][action])
                action = na
            else:
                best = float(np.max(Q[ns])) if not done else 0.0
                Q[state][action] += alpha * (reward + gamma * best - Q[state][action])

            state = ns
            step += 1

            if step % render_every == 0:
                frame = env.render()
                update_window(win_state, frame, returns, eps, None, Q)

        eps = max(0.05, eps * 0.995)
        returns.append(G)

    env.close()
    return returns


def _train_dqn_live(win_state: dict, n_episodes: int,
                     render_every: int) -> list[float]:
    """DQN con actualización live de la ventana."""
    np.random.seed(42)
    torch.manual_seed(42)
    random.seed(42)

    env        = gym.make("CartPole-v1", render_mode="rgb_array")
    online_net = DQN().to(DEVICE)
    target_net = DQN().to(DEVICE)
    target_net.load_state_dict(online_net.state_dict())
    target_net.eval()
    optimizer  = optim.Adam(online_net.parameters(), lr=1e-3)
    buffer     = ReplayBuffer(capacity=10_000)

    eps       = 1.0
    returns:   list[float]             = []
    loss_hist: list[tuple[int, float]] = []
    step = 0

    for _ in tqdm(range(n_episodes), desc="DQN", ncols=70, leave=True):
        obs, _ = env.reset()
        state  = np.array(obs, dtype=np.float32)
        done   = False
        G      = 0.0

        while not done:
            if np.random.random() < eps:
                action = env.action_space.sample()
            else:
                with torch.no_grad():
                    qv = online_net(
                        torch.tensor(state, dtype=torch.float32).unsqueeze(0))
                action = int(qv.argmax().item())

            obs2, reward, te, tr, _ = env.step(action)
            done = te or tr
            ns   = np.array(obs2, dtype=np.float32)
            G   += reward

            buffer.push(state, action, reward, ns, float(done))
            state = ns
            step += 1

            if len(buffer) >= 64:
                sb, ab, rb, nsb, db = buffer.sample(64)
                with torch.no_grad():
                    nq  = target_net(nsb).max(dim=1).values
                    tgt = rb + 0.99 * nq * (1.0 - db)
                cq   = online_net(sb).gather(1, ab.unsqueeze(1)).squeeze(1)
                loss = nn.functional.mse_loss(cq, tgt)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                loss_hist.append((step, float(loss.item())))

            if step % 50 == 0:
                target_net.load_state_dict(online_net.state_dict())

            if step % render_every == 0:
                frame = env.render()
                q_sample: list[float] = []
                if len(buffer) >= 200:
                    recent = [t[0] for t in list(buffer.buf)[-200:]]
                    st_t = torch.tensor(np.array(recent),
                                        dtype=torch.float32, device=DEVICE)
                    with torch.no_grad():
                        q_sample = online_net(st_t).flatten().cpu().numpy().tolist()
                update_window(win_state, frame, returns, eps, loss_hist, q_sample)

        eps = max(0.05, eps * 0.995)
        returns.append(G)

    env.close()
    return returns


# ─────────────────────────────────────────────────────────────────────────────
# Entrenamiento sin ventana (modo compare y headless)
# ─────────────────────────────────────────────────────────────────────────────

def _train_headless(method: str, n_episodes: int) -> list[float]:
    """Entrena un método sin ventana gráfica. Devuelve lista de retornos."""
    alpha = 0.1
    gamma = 0.99
    returns: list[float] = []

    if method == "dqn":
        np.random.seed(42)
        torch.manual_seed(42)
        random.seed(42)
        env        = gym.make("CartPole-v1")
        online_net = DQN().to(DEVICE)
        target_net = DQN().to(DEVICE)
        target_net.load_state_dict(online_net.state_dict())
        target_net.eval()
        optimizer  = optim.Adam(online_net.parameters(), lr=1e-3)
        buf        = ReplayBuffer(capacity=10_000)
        eps = 1.0
        step = 0
        for _ in tqdm(range(n_episodes), desc="DQN", ncols=70, leave=True):
            obs, _ = env.reset()
            s = np.array(obs, dtype=np.float32)
            done = False
            G    = 0.0
            while not done:
                if np.random.random() < eps:
                    a = env.action_space.sample()
                else:
                    with torch.no_grad():
                        a = int(online_net(
                            torch.tensor(s, dtype=torch.float32).unsqueeze(0)
                        ).argmax().item())
                o2, r, te, tr, _ = env.step(a)
                done = te or tr
                ns   = np.array(o2, dtype=np.float32)
                G   += r
                buf.push(s, a, r, ns, float(done))
                s = ns
                step += 1
                if len(buf) >= 64:
                    sb, ab, rb, nsb, db = buf.sample(64)
                    with torch.no_grad():
                        tgt = rb + gamma * target_net(nsb).max(1).values * (1 - db)
                    cq = online_net(sb).gather(1, ab.unsqueeze(1)).squeeze(1)
                    l  = nn.functional.mse_loss(cq, tgt)
                    optimizer.zero_grad()
                    l.backward()
                    optimizer.step()
                if step % 50 == 0:
                    target_net.load_state_dict(online_net.state_dict())
            eps = max(0.05, eps * 0.995)
            returns.append(G)
        env.close()

    else:
        bins      = _make_bins()
        env       = gym.make("CartPole-v1")
        Q         = np.zeros((10, 10, 10, 10, 2))
        eps       = 1.0
        use_sarsa = (method == "sarsa")

        for _ in tqdm(range(n_episodes), desc=METHOD_LABELS[method],
                      ncols=70, leave=True):
            obs, _ = env.reset()
            state  = _disc(obs, bins)
            if use_sarsa:
                action = (env.action_space.sample() if np.random.random() < eps
                          else int(np.argmax(Q[state])))
            done = False
            G    = 0.0
            while not done:
                if not use_sarsa:
                    action = (env.action_space.sample() if np.random.random() < eps
                              else int(np.argmax(Q[state])))
                obs2, reward, te, tr, _ = env.step(action)
                done = te or tr
                G   += reward
                ns   = _disc(obs2, bins)
                if use_sarsa:
                    if done:
                        na, nq = 0, 0.0
                    else:
                        na = (env.action_space.sample() if np.random.random() < eps
                              else int(np.argmax(Q[ns])))
                        nq = float(Q[ns][na])
                    Q[state][action] += alpha * (reward + gamma * nq - Q[state][action])
                    action = na
                else:
                    best = float(np.max(Q[ns])) if not done else 0.0
                    Q[state][action] += alpha * (reward + gamma * best - Q[state][action])
                state = ns
            eps = max(0.05, eps * 0.995)
            returns.append(G)
        env.close()

    return returns


# ─────────────────────────────────────────────────────────────────────────────
# Modo compare
# ─────────────────────────────────────────────────────────────────────────────

def run_compare(n_episodes: int) -> None:
    """Ejecuta los 4 métodos secuencialmente y muestra la ventana final."""
    print("\nComparando 4 métodos en CartPole-v1:\n")
    all_returns: dict[str, list[float]] = {}
    for i, m in enumerate(["qtable", "sarsa", "qlearning", "dqn"]):
        print(f"[{i+1}/4] {METHOD_LABELS[m]}")
        all_returns[m] = _train_headless(m, n_episodes)
        print()

    _show_comparison_window(all_returns, n_episodes)


def _show_comparison_window(results: dict, n_episodes: int) -> None:
    """Muestra (o guarda) la ventana con las 4 curvas superpuestas."""
    fig, ax = plt.subplots(figsize=(12, 6))

    window = 50
    for m in ["qtable", "sarsa", "qlearning", "dqn"]:
        rets = results.get(m, [])
        if not rets:
            continue
        ep_x = np.arange(1, len(rets) + 1)
        ax.plot(ep_x, rets, alpha=0.18, color=METHOD_COLORS[m], lw=0.7)
        if len(rets) >= window:
            roll = np.convolve(rets, np.ones(window) / window, mode="valid")
            ax.plot(np.arange(window, len(rets) + 1), roll,
                    color=METHOD_COLORS[m], lw=2.5, label=METHOD_LABELS[m])

    ax.axhline(475, color=COLORS["dark"], ls="--", lw=1.2, alpha=0.6,
               label="Resuelto (475)")
    ax.set_xlabel("Episodio", fontsize=12)
    ax.set_ylabel("Recompensa", fontsize=12)
    ax.set_title(
        f"CartPole-v1 — comparación de métodos ({n_episodes} episodios)",
        fontsize=13, color=COLORS["dark"]
    )
    ax.legend(fontsize=11, loc="upper left")
    ax.set_ylim(0, 520)
    ax.set_xlim(1, n_episodes)

    fig.text(
        0.5, 0.01,
        "Entrenamiento completo — cierra la ventana para salir",
        ha="center", fontsize=11, color=COLORS["dark"],
        bbox=dict(boxstyle="round,pad=0.3",
                  facecolor="#EBF5FB", edgecolor=COLORS["blue"])
    )
    plt.tight_layout(rect=[0, 0.05, 1, 1])

    if _has_display:
        plt.show(block=True)
    else:
        fig.savefig("demo_results.png", dpi=120, bbox_inches="tight")
        print("No display found. Summary saved to demo_results.png")
        plt.close(fig)


# ─────────────────────────────────────────────────────────────────────────────
# Modo headless single-method
# ─────────────────────────────────────────────────────────────────────────────

def run_headless_single(method: str, n_episodes: int) -> None:
    """Entrena sin display y guarda resumen PNG."""
    print(f"Entrenando {METHOD_LABELS[method]} ({n_episodes} ep.) — sin pantalla...")
    returns = _train_headless(method, n_episodes)

    fig, ax = plt.subplots(figsize=(10, 5))
    ep_x = np.arange(1, len(returns) + 1)
    ax.plot(ep_x, returns, alpha=0.30, color=METHOD_COLORS[method], lw=0.8)
    if len(returns) >= 50:
        roll = np.convolve(returns, np.ones(50) / 50, mode="valid")
        ax.plot(np.arange(50, len(returns) + 1), roll,
                color=METHOD_COLORS[method], lw=2.2,
                label=f"{METHOD_LABELS[method]} — media 50 ep.")
    ax.axhline(475, color=COLORS["dark"], ls="--", lw=1.2, alpha=0.6,
               label="Resuelto (475)")
    ax.set_xlabel("Episodio")
    ax.set_ylabel("Recompensa")
    ax.set_title(f"CartPole-v1 — {METHOD_LABELS[method]}")
    ax.legend()
    fig.savefig("demo_results.png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    print("No display found. Summary saved to demo_results.png")


# ─────────────────────────────────────────────────────────────────────────────
# Argumentos y punto de entrada
# ─────────────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(
        description="Demo interactivo de RL en CartPole-v1",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python demo_cartpole.py --method dqn
  python demo_cartpole.py --method qtable --speed fast
  python demo_cartpole.py --compare --episodes 300
  python demo_cartpole.py --method sarsa --episodes 200 --speed slow
        """
    )
    p.add_argument(
        "--method",
        choices=["qtable", "sarsa", "qlearning", "dqn"],
        default="dqn",
        help="Algoritmo a ejecutar (default: dqn)"
    )
    p.add_argument(
        "--compare", action="store_true",
        help="Ejecutar todos los métodos y mostrar comparación final"
    )
    p.add_argument(
        "--episodes", type=int, default=500,
        help="Número de episodios de entrenamiento (default: 500)"
    )
    p.add_argument(
        "--speed", choices=["fast", "normal", "slow"], default="normal",
        help="Velocidad de animación: fast=20, normal=5, slow=1 pasos/frame"
    )
    return p.parse_args()


def main():
    args = parse_args()

    np.random.seed(42)
    torch.manual_seed(42)
    random.seed(42)

    render_every = SPEED_MAP[args.speed]

    # ── Modo headless ──────────────────────────────────────────────────────────
    if not _has_display:
        if args.compare:
            run_compare(args.episodes)
        else:
            run_headless_single(args.method, args.episodes)
        return

    # ── Modo compare (con display) ─────────────────────────────────────────────
    if args.compare:
        run_compare(args.episodes)
        return

    # ── Modo live single-method ────────────────────────────────────────────────
    plt.ion()
    win_state = setup_window(args.method, args.episodes)
    win_state["fig"].canvas.draw()
    plt.pause(0.1)

    print(f"\nEntrenando {METHOD_LABELS[args.method]} ({args.episodes} ep.)")
    print(f"Velocidad: {args.speed} (actualizar ventana cada {render_every} pasos)\n")

    if args.method == "dqn":
        returns = _train_dqn_live(win_state, args.episodes, render_every)
    elif args.method == "sarsa":
        returns = _train_tabular_live(win_state, args.episodes,
                                       render_every, use_sarsa=True)
    else:
        returns = _train_tabular_live(win_state, args.episodes,
                                       render_every, use_sarsa=False)

    # Mensaje final en la barra de estado
    avg_f = (float(np.mean(returns[-50:])) if len(returns) >= 50
             else float(np.mean(returns)) if returns else 0.0)
    win_state["status_text"].set_text(
        f"Entrenamiento completo — {METHOD_LABELS[args.method]}  |  "
        f"Media final (50 ep): {avg_f:.1f}  |  "
        "Cierra la ventana para salir"
    )
    win_state["fig"].canvas.flush_events()
    plt.ioff()
    plt.show(block=True)


if __name__ == "__main__":
    main()
