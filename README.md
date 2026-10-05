# 🚗 Financeiro Lava-Rápido

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-092E20?style=flat&logo=django&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap%205-7952B3?style=flat&logo=bootstrap&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat&logo=postgresql&logoColor=white)
![Render](https://img.shields.io/badge/deploy-Render-46E3B7?style=flat&logo=render&logoColor=white)

> **Destaques:** sistema enxuto que resolve um problema real de um lava-jato. Tem deploy automatizado no Render (`render.yaml` + `build.sh`), configuração por variáveis de ambiente, login obrigatório em todas as páginas e comandos próprios para criar os usuários em produção.

<!-- Adicione aqui um print do dashboard: ![Dashboard](docs/dashboard.png) -->

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
financeiro), ambos com acesso igual a tudo. Existem dois comandos, para dois
cenários diferentes:

- `criar_usuarios_iniciais` — **interativo**, pergunta usuário/senha pelo
  terminal. Use localmente, ou em produção se você tiver Shell disponível
  (plano pago do Render).
- `criar_usuarios_producao` — **não-interativo**, lê usuário/senha de
  variáveis de ambiente. Pensado para rodar sozinho durante o build, sem
  precisar de Shell (ver [Criando os usuários em produção](#criando-os-usuários-em-produção-render-plano-free--sem-shell)).
  Também pode ser rodado localmente, definindo as variáveis antes do comando.

#### Opção A — comando `criar_usuarios_iniciais` (interativo, recomendado localmente)

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

### Criando os usuários em produção (Render, plano free — sem Shell)

O plano **free** do Render não tem aba **Shell** (recurso do plano pago Starter),
então não dá para rodar `criar_usuarios_iniciais` (interativo) direto em produção.
Por isso os 2 usuários são criados **automaticamente durante o build**, pelo comando
não-interativo `criar_usuarios_producao`, que lê as credenciais de variáveis de
ambiente e já está encadeado no `build.sh` logo após o `migrate`.

1. **Antes do próximo deploy**, no painel do Render vá em
   **seu serviço web → Environment** e adicione 4 variáveis:
   - `USUARIO_1_NOME` e `USUARIO_1_SENHA`
   - `USUARIO_2_NOME` e `USUARIO_2_SENHA`

   Escolha você mesmo o usuário e a senha de cada pessoa (senha forte, sem
   valor padrão/fraco). Essas variáveis ficam guardadas apenas no painel do
   Render — nunca vão para o repositório.
2. Faça o deploy (push no repositório, ou "Manual Deploy" no painel). O
   `build.sh` roda `migrate` e, em seguida, `criar_usuarios_producao`, que:
   - cria os 2 usuários com `is_staff=True` (podem acessar `/admin/` se precisar,
     mas não são superusuário);
   - **não falha o build** se alguma variável estiver ausente — só avisa no
     log do build e pula aquele usuário;
   - é **idempotente**: se um usuário com aquele username já existir (por
     exemplo, em um deploy anterior), ele é ignorado com o aviso
     `usuário "X" já existe, ignorado` — não duplica, não dá erro.
3. Confira no log do build (aba **Logs** do serviço) se apareceu
   `Usuário "..." criado com sucesso` para os 2 usuários.
4. Os usuários já podem logar em `https://<seu-app>.onrender.com/login/` com o
   usuário/senha que você definiu no passo 1.

> **Recomendação de segurança (não implementada ainda, fica para depois):**
> depois que os usuários conseguirem logar com sucesso, o ideal é cada um trocar
> essa senha inicial por uma escolhida por eles — hoje a única forma é pelo
> `/admin/` (usuário logado → link "CHANGE PASSWORD" no topo da página) ou, se
> tiver acesso ao Shell (plano pago), `manage.py changepassword <usuario>`. Uma
> tela própria de "alterar senha" no sistema (`PasswordChangeView` do Django)
> é uma boa evolução futura, mas não é obrigatória agora.
>
> Depois que os 2 usuários forem criados com sucesso, também vale remover
> `USUARIO_1_SENHA`/`USUARIO_2_SENHA` da aba Environment do Render (ou trocar
> por um valor qualquer) — como o comando é idempotente, isso não afeta os
> usuários já criados, e evita manter a senha real guardada ali indefinidamente.

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
4. **Antes desse primeiro deploy** (ou antes de qualquer redeploy, se ainda não
   tiver feito), cadastre também `USUARIO_1_NOME`, `USUARIO_1_SENHA`,
   `USUARIO_2_NOME`, `USUARIO_2_SENHA` na aba **Environment** do serviço web —
   o `build.sh` usa essas variáveis para criar os 2 usuários de login
   automaticamente, sem precisar de Shell (veja
   [Criando os usuários em produção](#criando-os-usuários-em-produção-render-plano-free--sem-shell)).

### Variáveis de ambiente usadas

| Variável                   | Local (opcional)        | Render (produção)                    |
|-----------------------------|---------------------------|----------------------------------------|
| `SECRET_KEY`                | usa fallback de dev       | gerada automaticamente                 |
| `DEBUG`                     | `True` para ver erros     | `False`                                |
| `DATABASE_URL`              | ausente → cai no SQLite   | preenchida pelo banco Postgres         |
| `RENDER_EXTERNAL_HOSTNAME`  | não se aplica             | definida automaticamente pelo Render   |
| `USUARIO_1_NOME` / `USUARIO_1_SENHA` | não usada localmente (use `criar_usuarios_iniciais`) | **defina manualmente** antes do deploy |
| `USUARIO_2_NOME` / `USUARIO_2_SENHA` | não usada localmente (use `criar_usuarios_iniciais`) | **defina manualmente** antes do deploy |

Veja `.env.example` para o formato de cada uma — ele só lista os *nomes* das
variáveis, nunca valores reais (principalmente as senhas).

## 🤝 Desenvolvido em parceria com o Claude

Construí este sistema em parceria com o **Claude**, a IA da Anthropic, que trabalhou como meu par de programação. Eu conduzi o projeto: levantei as necessidades do negócio, tomei as decisões e validei tudo no uso real. O Claude me ajudou a escrever e revisar código, configurar o deploy e documentar.

## 👨‍💻 Autor

**Rauan Pinheiro Lima**
[LinkedIn](https://linkedin.com/in/rauanpinheiro-dev) · [GitHub](https://github.com/Rauan-pinheiro)
