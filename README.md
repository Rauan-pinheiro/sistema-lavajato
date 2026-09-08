# Financeiro Lava-Rápido

Sistema simples de controle financeiro para lavanderia/lavagem de veículos: cadastro de
serviços, registro de execuções (lançamentos) com valor ajustável e um dashboard básico
de faturamento. Django + Django Templates + Bootstrap 5, sem API separada e sem framework
JS no frontend.

## Stack

- Django (Templates, sem DRF)
- Bootstrap 5 via CDN
- SQLite em desenvolvimento, PostgreSQL em produção (Render)
- WhiteNoise para arquivos estáticos, Gunicorn como servidor WSGI em produção

## Rodando localmente

```bash
python -m venv venv
./venv/Scripts/activate        # Windows
pip install -r requirements.txt

python manage.py migrate
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/` — como o sistema agora exige login, você será
redirecionado para `http://127.0.0.1:8000/login/`.

## Autenticação

O sistema usa o sistema de autenticação nativo do Django (`django.contrib.auth`).
Não existe cadastro público: os usuários são criados manualmente por um administrador,
via Django Admin, `createsuperuser` ou o comando `criar_usuarios_iniciais` (abaixo).
Todos os usuários têm o mesmo nível de acesso — não há grupos nem permissões diferenciadas.

**Todas as páginas do sistema exigem login.** Um usuário não autenticado que tentar
acessar qualquer URL (inclusive digitando o endereço diretamente) é redirecionado
automaticamente para a tela de login (`/login/`), voltando para a página pedida
depois de autenticado.

### Fluxo de login/logout

1. Acesse a raiz do site (`/`) ou qualquer URL do sistema.
2. Se não estiver logado, você cai em `/login/`: informe usuário e senha e clique em
   **Entrar**. Credenciais inválidas mostram uma mensagem de erro na própria tela.
3. Após o login, você é redirecionado para o **Dashboard**.
4. Com a sessão ativa, o navbar mostra "Olá, `<usuário>`" e os links do sistema
   (Dashboard, Serviços, Novo Lançamento, Lançamentos) e o botão **Sair**.
5. Clicar em **Sair** encerra a sessão e redireciona de volta para `/login/`.

### Criando os usuários

O sistema é pensado para **2 usuários** (donos/funcionários responsáveis pelo
financeiro), ambos com acesso igual a tudo.

#### Opção A — comando `criar_usuarios_iniciais` (recomendado)

Comando interativo que pergunta usuário e senha para cada pessoa (a senha não fica
visível no terminal e não fica salva em nenhum arquivo/histórico de shell):

```bash
python manage.py criar_usuarios_iniciais
```

- Por padrão cria 2 usuários; para outra quantidade: `--quantidade 3`.
- Se o nome de usuário já existir, ele é pulado (edite pelo Django Admin ou use
  `manage.py changepassword <usuario>` para trocar a senha).
- Senha mínima de 8 caracteres, com confirmação.

#### Opção B — `createsuperuser`

Cria um usuário com acesso também ao Django Admin (`/admin/`), útil se essa mesma
pessoa também for manter os cadastros por lá:

```bash
python manage.py createsuperuser
```

#### Opção C — Django Admin

Com pelo menos um superusuário já criado (via `createsuperuser`), acesse
`/admin/` → **Users** → **Add user** para cadastrar a segunda pessoa.

### Criando os usuários em produção (Render)

1. No painel do serviço no Render, abra a aba **Shell** (terminal remoto do serviço
   já em execução).
2. Rode o mesmo comando usado localmente:
   ```bash
   python manage.py criar_usuarios_iniciais
   ```
   ou `python manage.py createsuperuser` se preferir a Opção B.
3. Responda aos prompts de usuário/senha normalmente — o Shell do Render é
   interativo, então o `getpass` (senha oculta) funciona como no terminal local.
4. Feche o Shell. Os usuários já podem logar em `https://<seu-app>.onrender.com/login/`.

> Rode isso **uma única vez** por usuário. Para trocar uma senha depois, use
> `python manage.py changepassword <usuario>` (local ou no Shell do Render) ou
> edite pelo `/admin/`.

## Segurança

- Não existe tela de cadastro público de usuário em lugar nenhum do sistema.
- O formulário de login usa o CSRF token padrão do Django.
- `LOGIN_URL`, `LOGIN_REDIRECT_URL` e `LOGOUT_REDIRECT_URL` estão configurados em
  `financeiro_lavagem/settings.py`.
- Todas as views de negócio (`dashboard`, CRUD de serviços, execuções) estão
  protegidas com `@login_required`.

## Deploy no Render

O projeto já vem com `render.yaml` (Blueprint), `build.sh` e as dependências de
produção (`psycopg2-binary`, `dj-database-url`, `whitenoise`, `gunicorn`) prontas.

1. Suba o repositório para o GitHub/GitLab.
2. No Render, crie um **Blueprint** apontando para o repositório — ele lê o
   `render.yaml` e cria automaticamente:
   - o serviço web (`financeiro-lavagem`), com `buildCommand: ./build.sh` e
     `startCommand: gunicorn financeiro_lavagem.wsgi:application`;
   - a variável `SECRET_KEY` (gerada automaticamente pelo Render);
   - `DEBUG=False`;
   - um banco PostgreSQL (`financeiro-lavagem-db`, plano free) já conectado via
     `DATABASE_URL`.
3. O Render injeta `RENDER_EXTERNAL_HOSTNAME` automaticamente — o `settings.py` já
   usa essa variável para liberar o domínio `*.onrender.com` em `ALLOWED_HOSTS`.
4. Após o primeiro deploy, crie os 2 usuários pelo Shell do Render (veja
   [Criando os usuários em produção](#criando-os-usuários-em-produção-render)).

### Variáveis de ambiente usadas

| Variável                    | Local (opcional)         | Render (produção)                  |
|------------------------------|---------------------------|-------------------------------------|
| `SECRET_KEY`                 | usa fallback de dev       | gerada automaticamente              |
| `DEBUG`                      | `True` para ver erros     | `False`                             |
| `DATABASE_URL`                | ausente → cai no SQLite   | preenchida pelo banco Postgres      |
| `RENDER_EXTERNAL_HOSTNAME`    | não se aplica             | definida automaticamente pelo Render|

Veja `.env.example` para o formato de cada uma.
