from django.contrib import admin

from .models import Execucao, Servico


@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'valor_padrao', 'ativo', 'criado_em')
    list_filter = ('ativo',)
    search_fields = ('nome',)
    ordering = ('nome',)


@admin.register(Execucao)
class ExecucaoAdmin(admin.ModelAdmin):
    list_display = ('servico', 'valor_cobrado', 'data_hora', 'observacao')
    list_filter = ('servico', 'data_hora')
    search_fields = ('servico__nome', 'observacao')
    date_hierarchy = 'data_hora'
    ordering = ('-data_hora',)
