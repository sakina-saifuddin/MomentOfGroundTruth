#!/usr/bin/env bash
# One-time setup on a fresh Ubuntu VM (OCI). Run from the cloned repo root: bash deploy/setup_vm.sh
set -euo pipefail
sudo apt update && sudo apt install -y python3-venv python3-pip git
if ! swapon --show | grep -q swapfile; then
  sudo fallocate -l 4G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile
fi
python3 -m venv .venv && source .venv/bin/activate
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8501 -j ACCEPT
sudo netfilter-persistent save || true
sudo cp deploy/gt-app.service /etc/systemd/system/gt-app.service
sudo systemctl daemon-reload && sudo systemctl enable --now gt-app
echo "Running on port 8501. Also open TCP 8501 in the OCI security list."
