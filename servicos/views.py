from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, ProtectedError, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import ExecucaoForm, ServicoForm
from .models import Execucao, Servico


@login_required
def dashboard(request):
    hoje = date.today()

    execucoes_hoje = Execucao.objects.filter(data_hora__date=hoje)
    execucoes_mes = Execucao.objects.filter(
        data_hora__year=hoje.year,
        data_hora__month=hoje.month,
    )

    total_dia = execucoes_hoje.aggregate(total=Sum('valor_cobrado'))['total'] or 0
    total_mes = execucoes_mes.aggregate(total=Sum('valor_cobrado'))['total'] or 0

    servico_top = (
        execucoes_mes.values('servico__nome')
        .annotate(quantidade=Count('id'))
        .order_by('-quantidade')
        .first()
    )

    ultimos_lancamentos = Execucao.objects.select_related('servico').all()[:10]

    context = {
        'total_dia': total_dia,
        'total_mes': total_mes,
        'qtd_dia': execucoes_hoje.count(),
        'qtd_mes': execucoes_mes.count(),
        'servico_top': servico_top,
        'ultimos_lancamentos': ultimos_lancamentos,
    }
    return render(request, 'dashboard.html', context)


@login_required
def servico_lista(request):
    servicos = Servico.objects.all()
    return render(request, 'servicos/lista.html', {'servicos': servicos})


@login_required
def servico_criar(request):
    if request.method == 'POST':
        form = ServicoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Serviço cadastrado com sucesso.')
            return redirect('servicos:lista')
    else:
        form = ServicoForm()
    return render(request, 'servicos/form.html', {'form': form, 'titulo': 'Novo serviço'})


@login_required
def servico_editar(request, pk):
    servico = get_object_or_404(Servico, pk=pk)
    if request.method == 'POST':
        form = ServicoForm(request.POST, instance=servico)
        if form.is_valid():
            form.save()
            messages.success(request, 'Serviço atualizado com sucesso.')
            return redirect('servicos:lista')
    else:
        form = ServicoForm(instance=servico)
    return render(request, 'servicos/form.html', {'form': form, 'titulo': 'Editar serviço', 'servico': servico})


@login_required
def servico_excluir(request, pk):
    servico = get_object_or_404(Servico, pk=pk)
    if request.method == 'POST':
        try:
            servico.delete()
            messages.success(request, 'Serviço excluído com sucesso.')
        except ProtectedError:
            servico.ativo = False
            servico.save(update_fields=['ativo'])
            messages.warning(
                request,
                'Este serviço já possui lançamentos e não pode ser excluído. '
                'Ele foi desativado automaticamente.',
            )
        return redirect('servicos:lista')
    return render(request, 'servicos/confirmar_exclusao.html', {'servico': servico})


@login_required
def execucao_criar(request):
    if request.method == 'POST':
        form = ExecucaoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lançamento registrado com sucesso.')
            return redirect('servicos:execucoes_criar')
    else:
        form = ExecucaoForm()

    valores_padrao = {
        servico.pk: str(servico.valor_padrao)
        for servico in Servico.objects.filter(ativo=True)
    }
    ultimos_lancamentos = Execucao.objects.select_related('servico').all()[:10]

    context = {
        'form': form,
        'valores_padrao': valores_padrao,
        'ultimos_lancamentos': ultimos_lancamentos,
    }
    return render(request, 'execucoes/form.html', context)


@login_required
def execucao_lista(request):
    execucoes = Execucao.objects.select_related('servico').all()
    return render(request, 'execucoes/lista.html', {'execucoes': execucoes})
