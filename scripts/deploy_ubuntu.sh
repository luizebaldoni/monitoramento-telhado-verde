#!/usr/bin/env bash
# Script helper para deploy rápido (precisa de sudo para instalar serviços)
set -euo pipefail

BASE_DIR="/srv/monitoramento-telhado-verde"

if [ "$EUID" -ne 0 ]; then
  echo "Run as root or use sudo to install services. This script will only print commands to run." >&2
fi

cat <<'EOF'
# Resumo de comandos para rodar manualmente:
# Criar diretório e clonar repo
sudo mkdir -p /srv/monitoramento-telhado-verde
sudo chown $USER:$USER /srv/monitoramento-telhado-verde
# git clone <REPO_URL> /srv/monitoramento-telhado-verde

# API
cd /srv/monitoramento-telhado-verde/api-fastapi
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
# coloque config/firebase-credentials.json
# criar .env com FIREBASE_CREDENTIALS_PATH=config/firebase-credentials.json
.venv/bin/uvicorn api_firebase:app --host 0.0.0.0 --port 8000

# Dashboard
cd /srv/monitoramento-telhado-verde/dashboard
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
export USE_API=1
export API_URL=http://127.0.0.1:8000
.venv/bin/streamlit run dashboard/dashboard.py --server.port 8501 --server.address 0.0.0.0

# Install services
sudo cp api-fastapi/telhado-api.service /etc/systemd/system/
sudo cp dashboard/telhado-dashboard.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now telhado-api
sudo systemctl enable --now telhado-dashboard
EOF

