from django.urls import path

from . import views

app_name = 'servicos'

urlpatterns = [
    # Serviços (CRUD)
    path('servicos/', views.servico_lista, name='lista'),
    path('servicos/novo/', views.servico_criar, name='criar'),
    path('servicos/<int:pk>/editar/', views.servico_editar, name='editar'),
    path('servicos/<int:pk>/excluir/', views.servico_excluir, name='excluir'),

    # Execuções (lançamentos)
    path('lancamentos/', views.execucao_lista, name='execucoes_lista'),
    path('lancamentos/novo/', views.execucao_criar, name='execucoes_criar'),

    # Dashboard
    path('', views.dashboard, name='dashboard'),
]
