# Projeto de Gerenciamento de Provas com Django, Ninja e Docker

Este projeto é uma aplicação de gerenciamento de provas que utiliza Django, Django Ninja e Docker. Ele permite o gerenciamento completo de usuários, provas, questões, escolhas, participantes, respostas, correção automática e rankings.

![Python](https://img.shields.io/badge/Python-3.13-blue) ![Django](https://img.shields.io/badge/Django-5.1.3-green) ![Django Ninja](https://img.shields.io/badge/Django%20Ninja-1.3.0-blue) ![Poetry](https://img.shields.io/badge/Poetry-1.8.4-orange) ![Cache](https://img.shields.io/badge/Cache-Memcached-yellow) ![Pytest](https://img.shields.io/badge/Pytest-8.3.3-red) ![Psycopg2](https://img.shields.io/badge/Psycopg2-2.9.10-lightblue)

---

## **Pré-requisitos**

Certifique-se de ter as seguintes ferramentas instaladas na sua máquina:

- **Docker**: Para instalar, acesse a [documentação oficial do Docker](https://docs.docker.com/get-docker/).
- **Docker Compose**: Normalmente incluído ao instalar o Docker Desktop.

---

## **Iniciando a Aplicação com Docker**

### **Passos para iniciar:**

1. **Construa os containers Docker:**

   ```bash
   docker compose build
   ```

2. **Inicie a aplicação:**

   ```bash
   docker compose up
   ```

   Este comando irá iniciar os containers da aplicação, incluindo o banco de dados PostgreSQL.

3. **Acessando a aplicação:**

   Após inicializar, a API estará disponível no endereço:

   ```
   http://127.0.0.1:8000
   ```

---

## **Carregamento de Dados Iniciais**

Ao inicializar o Docker, os dados iniciais são automaticamente carregados a partir do arquivo `fixture-db.json`. Esses dados incluem:

- Usuários
- Provas
- Questões
- Escolhas
- Participantes

> **Obs**: Todos usuários da fixture têm o password: `@dmin123`

---

## **Rodando os Testes**

Os testes devem ser executados **fora do ambiente Docker**. Para isso, siga os passos abaixo:

### **Passos para rodar os testes:**

1. **Configure o banco de dados em `settings.py`:**

   Descomente as configurações de banco SQLite no arquivo `settings.py`:

   ```python
   # DATABASES = {
   #     'default': {
   #         'ENGINE': 'django.db.backends.sqlite3',
   #         'NAME': BASE_DIR / 'db.sqlite3',
   #     }
   # }
   ```

2. **Ative o ambiente virtual:**

   Certifique-se de estar em um ambiente Python virtual com as dependências instaladas via `poetry`:

   ```bash
   poetry install
   ```

3. **Execute os testes:**

   Use o comando abaixo para rodar os testes:

   ```bash
   pytest
   ```

4. **Resultados esperados:**

   Os testes validarão funcionalidades como criação de usuários, gerenciamento de provas, autenticação JWT, entre outros.

---

## **Endpoints com Autenticação, Paginação, Query e Cache**

A aplicação utiliza alguns endpoints com autenticação JWT, paginação, query e cache para melhorar a performance e segurança dos endpoints.

## **Principais Endpoints**

A aplicação expõe os seguintes endpoints principais:

### **Autenticação**

- `http://127.0.0.1:8000/api/auth/docs#/` - Documentação da API de Autenticação.

### **Usuários**

- `http://127.0.0.1:8000/api/users/docs#/` - Documentação da API de Usuários.

### **Provas**

- `http://127.0.0.1:8000/api/exams/docs#/` - Documentação da API de Provas.

### **Participantes**

- `http://127.0.0.1:8000/api/participants/docs#/` - Documentação da API de Participantes.

### **Questões**

- `http://127.0.0.1:8000/api/questions/docs#/` - Documentação da API de Questões.

### **Escolhas**

- `http://127.0.0.1:8000/api/choices/docs#/` - Documentação da API de Escolhas.

### **Respostas**

- `http://127.0.0.1:8000/api/answers/docs#/` - Documentação da API de Respostas.

### **Rankings**

- `http://127.0.0.1:8000/api/rankings/docs#/` - Documentação da API de Ranking.

### **Correção**

- `http://127.0.0.1:8000/api/corrections/docs#/` - Documentação da API de Correção.

---
