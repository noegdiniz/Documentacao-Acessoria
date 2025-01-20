# Documentação Acessoria

## Descrição

Documentação Acessoria é um sistema de gerenciamento de documentos desenvolvido em Flask. Ele permite que usuários façam upload, visualizem e gerenciem documentos de forma eficiente. O sistema inclui funcionalidades de autenticação, controle de acesso baseado em perfis, e registro de logs de ações.

## Estrutura do Projeto

```plaintext
.
├── __pycache__/
├── .env
├── .pytest_cache/
├── .vscode/
│   └── settings.json
├── app/
│   ├── __init__.py
│   ├── auth/
│   │   ├── __init__.py
│   │   └── auth.py
│   ├── blueprints/
│   │   ├── __init__.py
│   │   └── bps.py
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── CategoriaController.py
│   │   └── DocsControlller.py
│   ├── ext/
│   ├── mail/
│   ├── models/
│   ├── static/
│   │   ├── app.css
│   │   └── scripts.js
│   ├── templates/
│   │   ├── adm_cubo.html
│   │   ├── adm_documentos.html
│   │   ├── adm_empresas.html
│   │   ├── adm_logs.html
│   │   ├── blocked.html
│   │   ├── index.html
│   │   ├── index_prestadora.html
│   │   ├── list_contratos.html
│   │   ├── list_docs_filter.html
│   │   ├── list_logs.html
│   │   ├── list_perfil.html
│   │   ├── list_user.html
│   │   ├── login.html
│   │   ├── login_prestadora.html
│   │   ├── menu_categorias.html
│   │   ├── menu_contrato.html
│   │   ├── menu_cubo.html
│   │   ├── menu_perfil.html
│   │   ├── menu_user.html
│   │   ├── status_documentos.html
│   │   └── upload_file.html
├── config.py
├── credentials.json
├── db.sqlite
├── migrations/
│   ├── __pycache__/
│   ├── alembic.ini
│   ├── env.py
│   ├── README
│   ├── script.py.mako
│   └── versions/
├── tasks.json
└── teste.py
```

## Funcionalidades

- **Autenticação**: Login via Google OAuth.
- **Controle de Acesso**: Baseado em perfis de usuário.
- **Gerenciamento de Documentos**: Upload, visualização e status de documentos.
- **Logs de Ações**: Registro de ações dos usuários para auditoria.

## Instalação

### Pré-requisitos

- Python 3.8+
- Virtualenv
- Node.js (para gerenciamento de dependências front-end)

### Passos

1. Clone o repositório:

    ```sh
    git clone https://github.com/seu-usuario/documentacao-acessoria.git
    cd documentacao-acessoria
    ```

2. Crie e ative um ambiente virtual:

    ```sh
    python -m venv venv
    source venv/bin/activate  # No Windows use `venv\Scripts\activate`
    ```

3. Instale as dependências:

    ```sh
    pip install -r requirements.txt
    ```

4. Configure as variáveis de ambiente:

    ```sh
    cp .env.example .env
    ```

5. Inicie o servidor:

    ```sh
    flask run
    ```

## Estrutura de Arquivos

### Backend

- 

__init__.py

: Inicializa a aplicação Flask.
- 

bps.py

: Define as rotas e views.
- 

controllers

: Contém os controladores para as diferentes entidades.
- 

models

: Define os modelos de dados.
- 

auth

: Gerencia a autenticação dos usuários.
- 

mail

: Configurações de email.
- 

config.py

: Configurações da aplicação.

### Frontend

- 

static

: Arquivos estáticos como CSS e JavaScript.
- 

templates

: Templates HTML.

### Migrations

- 

migrations

: Gerenciamento de migrações de banco de dados com Alembic.

## Uso

### Autenticação

Os usuários podem se autenticar usando suas contas do Google. O sistema verifica se o email é válido e cria um perfil de usuário.

### Gerenciamento de Documentos

Os usuários podem fazer upload de documentos, que são armazenados no banco de dados. Cada documento tem um status que pode ser atualizado por usuários com permissões adequadas.

### Controle de Acesso

O acesso às funcionalidades é controlado por perfis de usuário. Cada perfil tem permissões específicas que determinam o que o usuário pode fazer.

### Logs de Ações

Todas as ações dos usuários são registradas em logs para auditoria. Isso inclui criação, atualização e exclusão de documentos, bem como mudanças de status.

## Contribuição

1. Fork o repositório.
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`).
3. Commit suas mudanças (

git commit -am 'Adiciona nova feature'

).
4. Push para a branch (`git push origin feature/nova-feature`).
5. Crie um novo Pull Request.

## Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo LICENSE para mais detalhes.

## Contato

Para mais informações, entre em contato com [noegddiniz@gmail.com](mailto:noegddiniz@gmail.com).

---

Feito com ❤️ por [Noe Gomes](https://github.com/nettosz).