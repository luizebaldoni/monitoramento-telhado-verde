# Guia rápido de deploy no Ubuntu Server
Este guia mostra passos práticos para colocar a API FastAPI e o Dashboard Streamlit em execução como serviços systemd no Ubuntu Server.

Pré-requisitos do servidor
- Ubuntu (20.04+ recomendado)
- Acesso root ou sudo
- Python 3.8+

1) Atualizar e instalar dependências básicas

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git nginx
```

2) Colocar o código no servidor
- Clone este repositório em `/srv/monitoramento-telhado-verde` ou copie os arquivos.

```bash
sudo mkdir -p /srv/monitoramento-telhado-verde
sudo chown $USER:$USER /srv/monitoramento-telhado-verde
git clone <REPO_URL> /srv/monitoramento-telhado-verde
```

3) API FastAPI

```bash
cd /srv/monitoramento-telhado-verde/api-fastapi
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
# coloque o arquivo de credenciais do Firebase em config/firebase-credentials.json
# crie .env com FIREBASE_CREDENTIALS_PATH=config/firebase-credentials.json
# testar
.venv/bin/uvicorn api_firebase:app --host 0.0.0.0 --port 8000 --reload
```

4) Dashboard Streamlit

```bash
cd /srv/monitoramento-telhado-verde/dashboard
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
# habilitar consumo via API
export USE_API=1
export API_URL=http://127.0.0.1:8000
streamlit run dashboard/dashboard.py --server.port 8501 --server.address 0.0.0.0
```

5) Systemd (opcional)
- Copie `api-fastapi/telhado-api.service` para `/etc/systemd/system/`
- Copie `dashboard/telhado-dashboard.service` para `/etc/systemd/system/`

```bash
sudo cp api-fastapi/telhado-api.service /etc/systemd/system/telhado-api.service
sudo cp dashboard/telhado-dashboard.service /etc/systemd/system/telhado-dashboard.service
sudo systemctl daemon-reload
sudo systemctl enable --now telhado-api
sudo systemctl enable --now telhado-dashboard
sudo journalctl -u telhado-api -f
sudo journalctl -u telhado-dashboard -f
```

6) (Opcional) Nginx como reverse proxy e SSL
- Configure Nginx para rotear /api para porta 8000 e /dashboard para 8501 e use Let's Encrypt para SSL.

```nginx
server {
    listen 80;
    server_name example.com;

    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location / {
        proxy_pass http://127.0.0.1:8501/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

7) Testes rápidos
- Postar dados de exemplo:
  curl -X POST http://127.0.0.1:8000/sensor-data -H "Content-Type: application/json" --data-binary @api-fastapi/sample.json
- Abrir dashboard: http://<IP_DO_SERVIDOR>:8501


Se você quiser, eu posso:
- Adicionar autenticação com API_KEY entre dashboard e API.
- Gerar o arquivo de configuração do Nginx e instruções para Let's Encrypt.
- Montar um script único para instalação automatizada.

