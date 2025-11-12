# ⚡ Guia Rápido

### 1️⃣ Clone e Entre na Pasta
```bash
git clone <repositorio>
cd api-fastapi
```

### 2️⃣ Configure o Ambiente Virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OU: venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 3️⃣ Configure o Firebase

1. Acesse: https://console.firebase.google.com/
2. Crie um projeto novo
3. Vá em: **Configurações** → **Contas de Serviço**
4. Clique em: **Gerar nova chave privada**
5. Salve o arquivo em: `config/firebase-credentials.json`

### 4️⃣ Configure as Variáveis de Ambiente
```bash
cp .env.example .env
# O arquivo .env já está configurado, só verificar o caminho do Firebase
```

### 5️⃣ Rode a API
```bash
uvicorn api_firebase:app --reload
```

Acesse: http://localhost:8000/docs

---

## ✅ Teste Rápido

Em outro terminal:

```bash
# Ative o ambiente virtual
source venv/bin/activate

# Rode o script de demonstração
python scripts/script_demostracao.py
```

Você verá 30 leituras sendo enviadas e consultadas!

---

## 💡 Dicas

- Use o Swagger UI (http://localhost:8000/docs) para testar
- O script `script_demostracao.py` é ótimo para demonstrações
- Todos os dados ficam salvos no Firebase Console


