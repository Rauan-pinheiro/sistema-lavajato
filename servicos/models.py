from django.db import models


class Servico(models.Model):
    nome = models.CharField('Nome', max_length=100)
    valor_padrao = models.DecimalField(
        'Valor padrão',
        max_digits=8,
        decimal_places=2,
        help_text='Valor de referência cobrado normalmente por este serviço.',
    )
    ativo = models.BooleanField(
        'Ativo',
        default=True,
        help_text='Serviços inativos não aparecem para novos lançamentos.',
    )
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Serviço'
        verbose_name_plural = 'Serviços'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Execucao(models.Model):
    servico = models.ForeignKey(
        Servico,
        on_delete=models.PROTECT,
        related_name='execucoes',
        verbose_name='Serviço',
    )
    valor_cobrado = models.DecimalField(
        'Valor cobrado',
        max_digits=8,
        decimal_places=2,
        help_text='Valor efetivamente cobrado nesta execução (pode diferir do valor padrão).',
    )
    observacao = models.TextField('Observação', blank=True)
    data_hora = models.DateTimeField('Data/hora', auto_now_add=True)

    class Meta:
        verbose_name = 'Execução'
        verbose_name_plural = 'Execuções'
        ordering = ['-data_hora']

    def __str__(self):
        return f'{self.servico.nome} - R$ {self.valor_cobrado} ({self.data_hora:%d/%m/%Y %H:%M})'
