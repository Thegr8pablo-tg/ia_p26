#!/usr/bin/env bash
# setup.sh — Create a local .venv and install deep RL dependencies.
#
# Usage:
#   cd clase/23_reinforcement_learning/deep_rl
#   ./setup.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

echo "============================================================"
echo "  Deep RL — Configuración del entorno virtual"
echo "============================================================"
echo ""

# ── Step 1: Check Python ────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 no encontrado. Instala Python 3.9+ primero."
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Usando Python $PYTHON_VERSION"

# ── Step 2: Create venv ─────────────────────────────────────────
if [ -d "$VENV_DIR" ]; then
    echo "El directorio .venv ya existe — omitiendo creación."
else
    echo "Creando entorno virtual en .venv/ ..."
    python3 -m venv "$VENV_DIR"
    echo "  ✓ Entorno virtual creado."
fi

# ── Step 3: Install dependencies ────────────────────────────────
echo ""
echo "Instalando dependencias desde requirements.txt ..."
echo "(Esto puede tardar unos minutos la primera vez)"
echo ""

"$VENV_DIR/bin/pip" install --upgrade pip --quiet
"$VENV_DIR/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"

echo ""
echo "  ✓ Dependencias instaladas correctamente."
echo ""
echo "============================================================"
echo "  Configuración completa. Ahora ejecuta:"
echo "============================================================"
echo ""
echo "    source .venv/bin/activate"
echo ""
echo "  Después puedes correr:"
echo ""
echo "    # Generar imágenes estáticas para el sitio del curso:"
echo "    python lab_deep_rl.py"
echo ""
echo "    # Demo interactivo — CartPole con DQN:"
echo "    python demo_cartpole.py --method dqn"
echo ""
echo "    # Demo con un método tabular:"
echo "    python demo_cartpole.py --method qtable"
echo "    python demo_cartpole.py --method sarsa"
echo "    python demo_cartpole.py --method qlearning"
echo ""
echo "    # Comparar los 4 métodos:"
echo "    python demo_cartpole.py --compare"
echo ""
echo "    # Demo rápido (200 episodios, velocidad alta):"
echo "    python demo_cartpole.py --method dqn --episodes 200 --speed fast"
echo ""
echo "  Para desactivar el entorno virtual:"
echo "    deactivate"
echo ""
