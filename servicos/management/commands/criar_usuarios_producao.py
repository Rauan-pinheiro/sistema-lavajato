import os

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand

# Cada usuário é lido de um par de variáveis de ambiente: NOME + SENHA.
USUARIOS_ENV = [
    ('USUARIO_1_NOME', 'USUARIO_1_SENHA'),
    ('USUARIO_2_NOME', 'USUARIO_2_SENHA'),
]


class Command(BaseCommand):
    help = (
        'Cria (de forma não-interativa e idempotente) os usuários de acesso ao '
        'sistema, lendo usuário/senha de variáveis de ambiente. Pensado para '
        'rodar automaticamente no build (Render free, sem Shell interativo). '
        'Nunca falha por falta de variáveis ou usuário já existente — apenas '
        'avisa e pula, para não quebrar o build.'
    )

    def handle(self, *args, **options):
        User = get_user_model()

        for nome_var, senha_var in USUARIOS_ENV:
            username = os.environ.get(nome_var)
            senha = os.environ.get(senha_var)

            if not username or not senha:
                self.stdout.write(self.style.WARNING(
                    f'{nome_var}/{senha_var} não definidas no ambiente. '
                    f'Pulando a criação deste usuário.'
                ))
                continue

            username = username.strip()

            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.WARNING(
                    f'Usuário "{username}" já existe, ignorado.'
                ))
                continue

            try:
                validate_password(senha)
            except ValidationError as erro:
                self.stdout.write(self.style.ERROR(
                    f'Senha de "{username}" (var. {senha_var}) não passou na validação '
                    f'({"; ".join(erro.messages)}). Usuário NÃO foi criado.'
                ))
                continue

            User.objects.create_user(
                username=username,
                password=senha,
                is_staff=True,
                is_superuser=False,
            )
            self.stdout.write(self.style.SUCCESS(
                f'Usuário "{username}" criado com sucesso (is_staff=True).'
            ))

        self.stdout.write(self.style.SUCCESS('criar_usuarios_producao concluído.'))
