import getpass

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        'Cria os usuários que terão acesso ao sistema (uso interativo). '
        'Pergunta usuário e senha para cada pessoa, um de cada vez. '
        'Usuários já existentes são pulados (edite-os pelo Django Admin).'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--quantidade',
            type=int,
            default=2,
            help='Quantidade de usuários a criar nesta execução (padrão: 2).',
        )

    def handle(self, *args, **options):
        User = get_user_model()
        quantidade = options['quantidade']

        self.stdout.write(self.style.NOTICE(
            f'Vamos cadastrar {quantidade} usuário(s) para acesso ao sistema.\n'
        ))

        for i in range(1, quantidade + 1):
            self.stdout.write(self.style.MIGRATE_HEADING(f'--- Usuário {i} de {quantidade} ---'))

            username = input('Nome de usuário: ').strip()
            if not username:
                self.stdout.write(self.style.ERROR('Nome de usuário não pode ser vazio. Pulando este usuário.\n'))
                continue

            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.WARNING(
                    f'Usuário "{username}" já existe. Pulando '
                    '(para trocar a senha, use o Django Admin ou "manage.py changepassword").\n'
                ))
                continue

            senha = self._pedir_senha()

            User.objects.create_user(username=username, password=senha)
            self.stdout.write(self.style.SUCCESS(f'Usuário "{username}" criado com sucesso.\n'))

        self.stdout.write(self.style.SUCCESS('Concluído.'))

    def _pedir_senha(self):
        while True:
            senha = getpass.getpass('Senha: ')
            confirmacao = getpass.getpass('Confirme a senha: ')

            if senha != confirmacao:
                self.stdout.write(self.style.ERROR('As senhas não coincidem. Tente novamente.'))
                continue
            if len(senha) < 8:
                self.stdout.write(self.style.ERROR('A senha deve ter pelo menos 8 caracteres. Tente novamente.'))
                continue
            return senha
