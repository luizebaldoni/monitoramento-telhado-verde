# Sistema de Monitoramento do Telhado Verde — Software

Este repositório contém o **backend e frontend** desenvolvidos em **Django** para o Sistema de Monitoramento do Telhado Verde do Jardim Botânico da UFSM.

---

## 📑 Sumário
- [Estrutura](#estrutura)
- [Tecnologias](#tecnologias)
- [Instalação e Execução](#instalação-e-execução)
- [Uso](#uso)
- [Contribuição](#contribuição)
- [Licença](#licença)

---

## 📂 Estrutura

- **app/** — Aplicativo principal Django (views, models, urls, lógica de negócio)
- **templates/** — Páginas HTML renderizadas (base, home, includes)
- **Data_Visualization/** — Configurações do projeto, scripts e dashboards com Chart.js
- **db.sqlite3** — Banco de dados local (apenas para desenvolvimento)
- **manage.py** — Gerenciador de comandos do Django

---

## 🚀 Tecnologias

- **Backend:** Django (Python)
- **Frontend:** HTML5, CSS, JavaScript, Chart.js
- **Banco de dados:** SQLite (desenvolvimento) / Firebase (produção)
- **Integração:** API REST recebendo dados do ESP32

---

## 🔧 Instalação e Execução

1. Clone este repositório:
   ```bash
   git clone <url-do-repositorio>
   cd Data Visualization
   ```
2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # ou
   source venv/bin/activate  # Linux/Mac
   ```
3. Instale as dependências:
   ```bash
   pip install django
   # Adicione outros requisitos se necessário
   ```
4. Realize as migrações do banco de dados:
   ```bash
   python manage.py migrate
   ```
5. (Opcional) Crie um superusuário para acessar o admin:
   ```bash
   python manage.py createsuperuser
   ```
6. Execute o servidor de desenvolvimento:
   ```bash
   python manage.py runserver
   ```

---

## ▶️ Uso

- Acesse `http://127.0.0.1:8000/` para visualizar a página inicial.
- Acesse `http://127.0.0.1:8000/admin/` para o painel administrativo (requer superusuário).

---

## 📄 Licença

Este projeto é reservado aos autores e não possui licença aberta de uso ou distribuição.
