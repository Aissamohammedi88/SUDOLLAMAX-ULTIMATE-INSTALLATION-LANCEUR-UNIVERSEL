#!/bin/bash# ============================================================
# SUDOLLAMAX ULTIMATE — INSTALLATION + LANCEUR UNIVERSEL
# Auteur : Aissa Mohammedi
# Version : 2.0.0
# Description : Installe tout et lance n’importe quel modèle.
# ============================================================

set -e

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; BLUE='\033[0;34m'; NC='\033[0m'
info() { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[ATTENTION]${NC} $1"; }
fail() { echo -e "${RED}[ERREUR]${NC} $1"; }
section() { echo -e "\n${BLUE}===== $1 =====${NC}"; }

BASE_DIR="$HOME/sudollamax_ultimate"
VENV_DIR="$BASE_DIR/venv"
MODELS_DIR="$BASE_DIR/models"
LOGS_DIR="$BASE_DIR/logs"

mkdir -p "$BASE_DIR" "$MODELS_DIR" "$LOGS_DIR"

# ─── 1. INSTALLATION DES DÉPENDANCES SYSTÈME ─────────────────────

section "1. INSTALLATION DES DÉPENDANCES SYSTÈME"

sudo apt update
sudo apt install -y python3 python3-pip python3-venv \
build-essential git curl wget \
nvidia-cuda-toolkit \
libopenblas-dev libssl-dev \
cmake g++

# ─── 2. INSTALLATION D'OLLAMA ────────────────────────────────────

section "2. INSTALLATION D'OLLAMA"

if ! command -v ollama &>/dev/null; then
curl -fsSL https://ollama.com/install.sh | sh
else
info "Ollama déjà installé"
fi

# ─── 3. CRÉATION DE L'ENVIRONNEMENT VIRTUEL ──────────────────────

section "3. CRÉATION DE L'ENVIRONNEMENT VIRTUEL"

python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

# ─── 4. INSTALLATION DES PACKAGES PYTHON ─────────────────────────

section "4. INSTALLATION DES PACKAGES PYTHON"

pip install --upgrade pip

# Moteurs principaux
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install tensorflow
pip install transformers
pip install accelerate
pip install onnx onnxruntime
pip install jax jaxlib

# Utilitaires
pip install flask requests numpy pandas scikit-learn
pip install huggingface-hub
pip install sentencepiece
pip install protobuf

# ─── 5. INSTALLATION DE TENSORRT (NVIDIA) ───────────────────────

section "5. INSTALLATION DE TENSORRT"

if command -v nvcc &>/dev/null; then
pip install nvidia-tensorrt
else
warn "CUDA non détecté — TensorRT installé en mode CPU"
pip install tensorrt
fi

# ─── 6. CRÉATION DU LANCEUR UNIVERSEL ────────────────────────────

section "6. CRÉATION DU LANCEUR UNIVERSEL"

cat > "$BASE_DIR/sudollamax.py" << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SUDOLLAMAX ULTIMATE — LANCEUR UNIVERSEL
Auteur : Aissa Mohammedi
Version : 2.0.0
Description : Lance n’importe quel modèle IA.
"""

import os
import sys
import json
import importlib
from pathlib import Path

# ─── DÉTECTION AUTO ──────────────────────────────────────────────

def detect_model_type(model_path):
path = Path(model_path)
if path.is_dir():
if (path / "config.json").exists():
return "huggingface"
if (path / "saved_model.pb").exists():
return "tensorflow"
if (path / "pytorch_model.bin").exists() or (path / "model.pt").exists():
return "pytorch"
if (path / "model.onnx").exists():
return "onnx"
if (path / "model.engine").exists():
return "tensorrt"
if path.suffix == ".gguf":
return "ollama"
return "unknown"

# ─── LANCEURS ─────────────────────────────────────────────────────

def run_huggingface(model_path):
from transformers import pipeline
pipe = pipeline("text-generation", model=str(model_path))
result = pipe("Hello world", max_new_tokens=50)
print(result[0]["generated_text"])

def run_tensorflow(model_path):
import tensorflow as tf
model = tf.saved_model.load(str(model_path))
print("✅ Modèle TensorFlow chargé")
print(model.signatures)

def run_pytorch(model_path):
import torch
model = torch.load(model_path / "pytorch_model.bin", map_location="cpu")
print("✅ Modèle PyTorch chargé")
print(model)

def run_onnx(model_path):
import onnxruntime as ort
session = ort.InferenceSession(str(model_path / "model.onnx"))
print("✅ Modèle ONNX chargé")
print(session.get_inputs())

def run_tensorrt(model_path):
import tensorrt as trt
logger = trt.Logger(trt.Logger.WARNING)
with open(model_path / "model.engine", "rb") as f:
runtime = trt.Runtime(logger)
engine = runtime.deserialize_cuda_engine(f.read())
print("✅ Modèle TensorRT chargé")

def run_ollama(model_path):
import subprocess
subprocess.run(["ollama", "run", str(model_path)])

# ─── MAIN ─────────────────────────────────────────────────────────

def main():
if len(sys.argv) < 2:
print("Usage: sudollamax.py <model_path>")
sys.exit(1)

model_path = Path(sys.argv[1])
if not model_path.exists():
print(f"❌ {model_path} introuvable")
sys.exit(1)

model_type = detect_model_type(model_path)
print(f"🔍 Type détecté : {model_type}")

runners = {
"huggingface": run_huggingface,
"tensorflow": run_tensorflow,
"pytorch": run_pytorch,
"onnx": run_onnx,
"tensorrt": run_tensorrt,
"ollama": run_ollama,
}

runner = runners.get(model_type)
if runner:
runner(model_path)
else:
print(f"❌ Type non supporté : {model_type}")

if __name__ == "__main__":
main()
EOF

chmod +x "$BASE_DIR/sudollamax.py"

# ─── 7. ALIAS ──────────────────────────────────────────────────────

section "7. CRÉATION DE L'ALIAS"

echo "alias sudollamax='source $VENV_DIR/bin/activate && python3 $BASE_DIR/sudollamax.py'" >> ~/.bashrc
source ~/.bashrc

# ─── 8. TEST ──────────────────────────────────────────────────────

section "8. TEST DU LANCEUR"

info "Sudollamax installé. Test avec un modèle Ollama :"
ollama pull qwen2.5-coder:1.5b
sudollamax qwen2.5-coder:1.5b || true

# ─── 9. RAPPORT FINAL ─────────────────────────────────────────────

section "RAPPORT FINAL — SUDOLLAMAX ULTIMATE"
echo "📁 Dossier : $BASE_DIR"
echo "🐍 Venv : $VENV_DIR"
echo "📦 Modèles : $MODELS_DIR"
echo "📄 Lanceur : $BASE_DIR/sudollamax.py"
echo "✅ Installation terminée"
echo "📌 Utilisation : sudollamax <chemin_ou_nom_du_modèle>"
