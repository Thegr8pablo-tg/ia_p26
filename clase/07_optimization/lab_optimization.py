#!/usr/bin/env python3
"""
Laboratorio: Optimización (imágenes para las notas)

Uso:
    cd clase/07_optimization
    python lab_optimization.py

Genera imágenes en:
    clase/07_optimization/images/

Dependencias: numpy, matplotlib, scipy
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize, minimize_scalar, linprog

# -----------------------------------------------------------------------------
# Styling (same vibe as lab_informacion.py)
# -----------------------------------------------------------------------------

plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams["figure.figsize"] = (12, 8)
plt.rcParams["font.size"] = 11
plt.rcParams["axes.titlesize"] = 13
plt.rcParams["axes.labelsize"] = 11

COLORS = {
    "blue": "#2E86AB",
    "red": "#E94F37",
    "green": "#27AE60",
    "gray": "#7F8C8D",
    "orange": "#F39C12",
    "purple": "#8E44AD",
}

ROOT = Path(__file__).resolve().parent
IMAGES_DIR = ROOT / "images"
IMAGES_DIR.mkdir(exist_ok=True)

np.random.seed(42)


def _save(fig, name: str) -> None:
    out = IMAGES_DIR / name
    fig.savefig(out, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"✓ Generada: {out.name}")


# -----------------------------------------------------------------------------
# 1) Local vs global minima (1D)
# -----------------------------------------------------------------------------


def plot_local_vs_global():
    """1D function with annotated local and global minima."""
    x = np.linspace(-2, 6, 800)
    f = lambda t: (t - 2) ** 2 * np.sin(3 * t) + 0.5 * t

    y = f(x)

    # Find local minima (simple grid search)
    from scipy.signal import argrelextrema

    local_min_idx = argrelextrema(y, np.less, order=20)[0]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(x, y, color=COLORS["blue"], linewidth=2, label=r"$f(x) = (x-2)^2 \sin(3x) + 0.5x$")

    # Mark local minima
    global_idx = local_min_idx[np.argmin(y[local_min_idx])]
    for idx in local_min_idx:
        if idx == global_idx:
            ax.scatter(x[idx], y[idx], color=COLORS["red"], s=120, zorder=5,
                       edgecolors="black", linewidths=1.5)
            ax.annotate("Mínimo global", xy=(x[idx], y[idx]),
                        xytext=(x[idx] + 0.5, y[idx] - 3),
                        arrowprops=dict(arrowstyle="->", lw=1.5),
                        fontsize=11, fontweight="bold", color=COLORS["red"])
        else:
            ax.scatter(x[idx], y[idx], color=COLORS["orange"], s=80, zorder=4,
                       edgecolors="black", linewidths=1)
            ax.annotate("Mínimo local", xy=(x[idx], y[idx]),
                        xytext=(x[idx] + 0.4, y[idx] + 3),
                        arrowprops=dict(arrowstyle="->", lw=1),
                        fontsize=10, color=COLORS["orange"])

    ax.set_title("Mínimos locales vs mínimo global")
    ax.set_xlabel("x")
    ax.set_ylabel("f(x)")
    ax.legend(loc="upper left")
    _save(fig, "local_vs_global.png")


# -----------------------------------------------------------------------------
# 2) Saddle point (3D)
# -----------------------------------------------------------------------------


def plot_saddle_point_3d():
    """Contour + heatmap of f(x,y) = x^2 - y^2 showing a saddle point."""
    x = np.linspace(-2, 2, 300)
    y = np.linspace(-2, 2, 300)
    X, Y = np.meshgrid(x, y)
    Z = X**2 - Y**2

    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.pcolormesh(X, Y, Z, cmap="coolwarm", shading="auto")
    cs = ax.contour(X, Y, Z, levels=15, colors="black", linewidths=0.5, alpha=0.5)
    ax.clabel(cs, inline=True, fontsize=8)
    fig.colorbar(im, ax=ax, label="f(x,y)")

    ax.scatter([0], [0], color=COLORS["red"], s=150, zorder=5,
               edgecolors="black", linewidths=2)
    ax.annotate("Punto silla (0, 0)\nmín en x, máx en y",
                xy=(0, 0), xytext=(0.5, 1.2),
                arrowprops=dict(arrowstyle="->", lw=1.5, color=COLORS["red"]),
                fontsize=11, color=COLORS["red"], fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.9))

    # Show directions
    ax.annotate("", xy=(0, -1.5), xytext=(0, -0.3),
                arrowprops=dict(arrowstyle="->", lw=2, color=COLORS["green"]))
    ax.text(0.15, -1.0, "máx (en y)", fontsize=9, color=COLORS["green"])
    ax.annotate("", xy=(1.5, 0), xytext=(0.3, 0),
                arrowprops=dict(arrowstyle="->", lw=2, color=COLORS["blue"]))
    ax.text(0.8, 0.15, "mín (en x)", fontsize=9, color=COLORS["blue"])

    ax.set_title(r"Punto silla: $f(x,y) = x^2 - y^2$")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    _save(fig, "saddle_point_3d.png")


# -----------------------------------------------------------------------------
# 3) Convex vs non-convex
# -----------------------------------------------------------------------------


def plot_convex_vs_nonconvex():
    """Side-by-side: convex function vs non-convex function."""
    x = np.linspace(-3, 3, 400)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Convex: f(x) = x^2
    y_convex = x**2
    ax1.plot(x, y_convex, color=COLORS["blue"], linewidth=2)
    ax1.fill_between(x, y_convex, alpha=0.1, color=COLORS["blue"])
    # Show convexity: chord above curve
    x1, x2 = -2, 1.5
    y1, y2 = x1**2, x2**2
    ax1.plot([x1, x2], [y1, y2], "--", color=COLORS["red"], linewidth=1.5,
             label="Cuerda (siempre arriba)")
    lam = 0.4
    xm = lam * x1 + (1 - lam) * x2
    ax1.scatter([xm], [xm**2], color=COLORS["green"], s=60, zorder=5)
    ax1.scatter([xm], [lam * y1 + (1 - lam) * y2], color=COLORS["red"], s=60, zorder=5)
    ax1.annotate("f(λx₁+(1-λ)x₂)", xy=(xm, xm**2), xytext=(xm + 0.5, xm**2 + 1),
                 arrowprops=dict(arrowstyle="->"), fontsize=9, color=COLORS["green"])
    ax1.annotate("λf(x₁)+(1-λ)f(x₂)", xy=(xm, lam * y1 + (1 - lam) * y2),
                 xytext=(xm + 0.5, lam * y1 + (1 - lam) * y2 + 1.5),
                 arrowprops=dict(arrowstyle="->"), fontsize=9, color=COLORS["red"])
    ax1.set_title(r"Convexa: $f(x) = x^2$")
    ax1.set_xlabel("x")
    ax1.set_ylabel("f(x)")
    ax1.legend(fontsize=9)

    # Non-convex: f(x) = x^4 - 4x^2 + x
    y_nonconvex = x**4 - 4 * x**2 + x
    ax2.plot(x, y_nonconvex, color=COLORS["purple"], linewidth=2)
    # Show chord going below curve
    x1, x2 = -1.8, 1.5
    y1_nc = x1**4 - 4 * x1**2 + x1
    y2_nc = x2**4 - 4 * x2**2 + x2
    ax2.plot([x1, x2], [y1_nc, y2_nc], "--", color=COLORS["red"], linewidth=1.5,
             label="Cuerda (cruza la curva)")
    ax2.set_title(r"No convexa: $f(x) = x^4 - 4x^2 + x$")
    ax2.set_xlabel("x")
    ax2.set_ylabel("f(x)")
    ax2.legend(fontsize=9)

    fig.suptitle("Convexidad: la cuerda siempre queda arriba de la curva", fontsize=13, y=1.02)
    fig.tight_layout()
    _save(fig, "convex_vs_nonconvex.png")


# -----------------------------------------------------------------------------
# 4) Gradient descent on contour plot
# -----------------------------------------------------------------------------


def plot_gradient_descent_contour():
    """Contour plot of a quadratic with GD trajectory and arrows."""
    # f(x,y) = 3x^2 + y^2 (elongated bowl)
    f = lambda x, y: 3 * x**2 + y**2
    grad_f = lambda x, y: np.array([6 * x, 2 * y])

    # GD trajectory
    x0 = np.array([3.0, 3.0])
    lr = 0.08
    trajectory = [x0.copy()]
    for _ in range(25):
        x0 = x0 - lr * grad_f(x0[0], x0[1])
        trajectory.append(x0.copy())
    trajectory = np.array(trajectory)

    # Contour plot
    xg = np.linspace(-4, 4, 300)
    yg = np.linspace(-4, 4, 300)
    X, Y = np.meshgrid(xg, yg)
    Z = f(X, Y)

    fig, ax = plt.subplots(figsize=(8, 7))
    cs = ax.contour(X, Y, Z, levels=20, cmap="viridis", alpha=0.7)
    ax.clabel(cs, inline=True, fontsize=8)

    # Plot trajectory with arrows
    ax.plot(trajectory[:, 0], trajectory[:, 1], "o-", color=COLORS["red"],
            markersize=4, linewidth=1.5, label="Trayectoria GD")
    ax.scatter(trajectory[0, 0], trajectory[0, 1], color=COLORS["orange"],
               s=100, zorder=5, edgecolors="black", label="Inicio")
    ax.scatter(trajectory[-1, 0], trajectory[-1, 1], color=COLORS["green"],
               s=100, zorder=5, edgecolors="black", label="Final")

    # Arrows on a few steps
    for i in range(0, len(trajectory) - 1, 3):
        dx = trajectory[i + 1, 0] - trajectory[i, 0]
        dy = trajectory[i + 1, 1] - trajectory[i, 1]
        ax.annotate("", xy=(trajectory[i + 1, 0], trajectory[i + 1, 1]),
                     xytext=(trajectory[i, 0], trajectory[i, 1]),
                     arrowprops=dict(arrowstyle="->", color=COLORS["red"], lw=1.5))

    ax.set_title(r"Descenso de gradiente en $f(x,y) = 3x^2 + y^2$")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.legend(loc="upper right")
    _save(fig, "gradient_descent_contour.png")


# -----------------------------------------------------------------------------
# 5) GD on Rosenbrock
# -----------------------------------------------------------------------------


def plot_gd_rosenbrock():
    """GD trajectory on the Rosenbrock function (banana-shaped valley)."""
    rosenbrock = lambda x, y: (1 - x) ** 2 + 100 * (y - x**2) ** 2
    grad_rosen = lambda x, y: np.array([
        -2 * (1 - x) - 400 * x * (y - x**2),
        200 * (y - x**2),
    ])

    # GD with small learning rate
    x0 = np.array([-1.5, 2.0])
    lr = 0.001
    trajectory = [x0.copy()]
    for _ in range(5000):
        g = grad_rosen(x0[0], x0[1])
        x0 = x0 - lr * g
        trajectory.append(x0.copy())
    trajectory = np.array(trajectory)

    # Contour plot
    xg = np.linspace(-2, 2, 400)
    yg = np.linspace(-1, 3, 400)
    X, Y = np.meshgrid(xg, yg)
    Z = rosenbrock(X, Y)

    fig, ax = plt.subplots(figsize=(9, 7))
    cs = ax.contour(X, Y, np.log1p(Z), levels=30, cmap="inferno", alpha=0.7)

    # Subsample trajectory for plotting
    step = max(1, len(trajectory) // 200)
    traj_sub = trajectory[::step]
    ax.plot(traj_sub[:, 0], traj_sub[:, 1], "-", color=COLORS["blue"],
            linewidth=1, alpha=0.7, label="Trayectoria GD")
    ax.scatter(trajectory[0, 0], trajectory[0, 1], color=COLORS["orange"],
               s=100, zorder=5, edgecolors="black", label="Inicio")
    ax.scatter(trajectory[-1, 0], trajectory[-1, 1], color=COLORS["green"],
               s=100, zorder=5, edgecolors="black", label=f"Final ({len(trajectory)} pasos)")
    ax.scatter(1, 1, color=COLORS["red"], s=120, zorder=5,
               marker="*", edgecolors="black", label="Óptimo (1,1)")

    ax.set_title("Descenso de gradiente en la función de Rosenbrock")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.legend(loc="upper left")
    _save(fig, "gd_rosenbrock.png")


# -----------------------------------------------------------------------------
# 6) 1D scipy minimize
# -----------------------------------------------------------------------------


def plot_minimize_1d():
    """1D minimization with scipy: f(x) = (x-3)^2 + 2*sin(5x)."""
    f = lambda x: (x - 3) ** 2 + 2 * np.sin(5 * x)
    x = np.linspace(-1, 7, 800)
    y = f(x)

    result = minimize_scalar(f, bounds=(0, 6), method="bounded")
    x_min = result.x
    f_min = result.fun

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(x, y, color=COLORS["blue"], linewidth=2,
            label=r"$f(x) = (x-3)^2 + 2\sin(5x)$")
    ax.scatter([x_min], [f_min], color=COLORS["red"], s=120, zorder=5,
               edgecolors="black", linewidths=1.5)
    ax.annotate(f"Mínimo: x={x_min:.3f}\nf(x)={f_min:.3f}",
                xy=(x_min, f_min), xytext=(x_min + 1, f_min + 2),
                arrowprops=dict(arrowstyle="->", lw=1.5),
                fontsize=11, color=COLORS["red"],
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

    ax.set_title("Minimización 1D con scipy.optimize.minimize_scalar")
    ax.set_xlabel("x")
    ax.set_ylabel("f(x)")
    ax.legend(loc="upper right")
    _save(fig, "minimize_1d.png")


# -----------------------------------------------------------------------------
# 7) Linear programming — feasible region
# -----------------------------------------------------------------------------


def plot_linear_programming_2d():
    """Feasible region of a 2D LP with objective contours."""
    # max 5x1 + 4x2  s.t.  6x1 + 4x2 <= 24,  x1 + 2x2 <= 6, x1,x2 >= 0
    fig, ax = plt.subplots(figsize=(8, 7))

    x1 = np.linspace(0, 5, 400)

    # Constraints
    c1 = (24 - 6 * x1) / 4   # 6x1 + 4x2 <= 24
    c2 = (6 - x1) / 2        # x1 + 2x2 <= 6

    ax.plot(x1, c1, color=COLORS["blue"], linewidth=2, label=r"$6x_1 + 4x_2 \leq 24$")
    ax.plot(x1, c2, color=COLORS["green"], linewidth=2, label=r"$x_1 + 2x_2 \leq 6$")

    # Feasible region
    y_upper = np.minimum(c1, c2)
    y_upper = np.maximum(y_upper, 0)
    ax.fill_between(x1, 0, y_upper, where=(y_upper >= 0) & (x1 >= 0),
                     alpha=0.2, color=COLORS["blue"], label="Región factible")

    # Objective contours: 5x1 + 4x2 = k
    for k in [5, 10, 15, 20]:
        obj_line = (k - 5 * x1) / 4
        ax.plot(x1, obj_line, "--", color=COLORS["gray"], linewidth=0.8, alpha=0.6)
        # Label
        valid = (obj_line >= 0) & (x1 >= 0)
        if np.any(valid):
            idx = np.where(valid)[0][len(np.where(valid)[0]) // 2]
            ax.annotate(f"z={k}", xy=(x1[idx], obj_line[idx]), fontsize=8,
                        color=COLORS["gray"])

    # Vertices
    vertices = np.array([[0, 0], [4, 0], [3, 1.5], [0, 3]])
    ax.scatter(vertices[:, 0], vertices[:, 1], color=COLORS["red"], s=80,
               zorder=5, edgecolors="black")
    for v in vertices:
        ax.annotate(f"({v[0]:.0f}, {v[1]:.1f})", xy=(v[0], v[1]),
                    xytext=(5, 8), textcoords="offset points", fontsize=9)

    # Optimal vertex
    z_vals = 5 * vertices[:, 0] + 4 * vertices[:, 1]
    opt_idx = np.argmax(z_vals)
    ax.scatter(vertices[opt_idx, 0], vertices[opt_idx, 1], color=COLORS["red"],
               s=200, zorder=6, edgecolors="black", linewidths=2, marker="*")
    ax.annotate(f"Óptimo: z={z_vals[opt_idx]:.0f}",
                xy=(vertices[opt_idx, 0], vertices[opt_idx, 1]),
                xytext=(vertices[opt_idx, 0] + 0.3, vertices[opt_idx, 1] + 0.5),
                arrowprops=dict(arrowstyle="->", lw=1.5),
                fontsize=11, color=COLORS["red"], fontweight="bold")

    ax.set_xlim(-0.5, 5)
    ax.set_ylim(-0.5, 5)
    ax.set_title(r"Programación lineal: $\max\ 5x_1 + 4x_2$")
    ax.set_xlabel(r"$x_1$")
    ax.set_ylabel(r"$x_2$")
    ax.legend(loc="upper right")
    _save(fig, "linear_programming_2d.png")


# -----------------------------------------------------------------------------
# 8) LP solution with scipy linprog
# -----------------------------------------------------------------------------


def plot_linprog_feasible():
    """LP solved with scipy.optimize.linprog, solution plotted on feasible region."""
    # Same problem: max 5x1 + 4x2 → min -5x1 - 4x2
    c = [-5, -4]
    A_ub = [[6, 4], [1, 2]]
    b_ub = [24, 6]
    bounds = [(0, None), (0, None)]
    result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")

    fig, ax = plt.subplots(figsize=(8, 7))

    x1 = np.linspace(0, 5, 400)
    c1 = (24 - 6 * x1) / 4
    c2 = (6 - x1) / 2

    ax.plot(x1, c1, color=COLORS["blue"], linewidth=2, label=r"$6x_1 + 4x_2 \leq 24$")
    ax.plot(x1, c2, color=COLORS["green"], linewidth=2, label=r"$x_1 + 2x_2 \leq 6$")

    y_upper = np.minimum(c1, c2)
    y_upper = np.maximum(y_upper, 0)
    ax.fill_between(x1, 0, y_upper, where=(y_upper >= 0) & (x1 >= 0),
                     alpha=0.2, color=COLORS["blue"], label="Región factible")

    # scipy solution
    sol = result.x
    ax.scatter([sol[0]], [sol[1]], color=COLORS["red"], s=200, zorder=6,
               edgecolors="black", linewidths=2, marker="*")
    ax.annotate(f"scipy: ({sol[0]:.2f}, {sol[1]:.2f})\nz={-result.fun:.2f}",
                xy=(sol[0], sol[1]),
                xytext=(sol[0] + 0.3, sol[1] + 0.6),
                arrowprops=dict(arrowstyle="->", lw=1.5),
                fontsize=11, color=COLORS["red"], fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

    ax.set_xlim(-0.5, 5)
    ax.set_ylim(-0.5, 5)
    ax.set_title("Solución de LP con scipy.optimize.linprog")
    ax.set_xlabel(r"$x_1$")
    ax.set_ylabel(r"$x_2$")
    ax.legend(loc="upper right")
    _save(fig, "linprog_feasible.png")


# -----------------------------------------------------------------------------
# 9) SGD vs Batch GD convergence
# -----------------------------------------------------------------------------


def plot_sgd_vs_gd():
    """Convergence curves comparing batch GD and SGD on linear regression."""
    # Synthetic data: y = 2x + 1 + noise
    N = 200
    X_data = np.random.randn(N, 1)
    y_data = 2 * X_data[:, 0] + 1 + 0.5 * np.random.randn(N)
    X_aug = np.hstack([X_data, np.ones((N, 1))])

    mse = lambda w: np.mean((y_data - X_aug @ w) ** 2)
    grad_full = lambda w: -2 / N * X_aug.T @ (y_data - X_aug @ w)

    def grad_sgd(w, batch_size=32):
        idx = np.random.choice(N, batch_size, replace=False)
        return -2 / batch_size * X_aug[idx].T @ (y_data[idx] - X_aug[idx] @ w)

    w0 = np.array([0.0, 0.0])
    lr, n_steps = 0.05, 150

    # Batch GD
    losses_gd = []
    w = w0.copy()
    for _ in range(n_steps):
        losses_gd.append(mse(w))
        w = w - lr * grad_full(w)

    # SGD (batch_size=32)
    losses_sgd = []
    w = w0.copy()
    for _ in range(n_steps):
        losses_sgd.append(mse(w))
        w = w - lr * grad_sgd(w, batch_size=32)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(losses_gd, linewidth=2, color=COLORS["blue"], label="Batch GD (N=200)")
    ax.plot(losses_sgd, linewidth=1.5, color=COLORS["red"], alpha=0.8,
            label="SGD (batch=32)")
    ax.set_xlabel("Iteración")
    ax.set_ylabel("MSE Loss")
    ax.set_title("SGD vs Batch GD en regresión lineal")
    ax.legend()
    ax.set_yscale("log")
    _save(fig, "sgd_vs_gd.png")


# =============================================================================
# Main
# =============================================================================


def main():
    print("Generando imágenes para módulo 07: Optimización\n")
    plot_local_vs_global()
    plot_saddle_point_3d()
    plot_convex_vs_nonconvex()
    plot_gradient_descent_contour()
    plot_gd_rosenbrock()
    plot_minimize_1d()
    plot_linear_programming_2d()
    plot_linprog_feasible()
    plot_sgd_vs_gd()
    print(f"\n✓ Todas las imágenes generadas en {IMAGES_DIR}")


if __name__ == "__main__":
    main()
