from django import forms

from .models import Execucao, Servico


class ServicoForm(forms.ModelForm):
    class Meta:
        model = Servico
        fields = ['nome', 'valor_padrao', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Lavagem completa'}),
            'valor_padrao': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ExecucaoForm(forms.ModelForm):
    servico = forms.ModelChoiceField(
        queryset=Servico.objects.filter(ativo=True),
        label='Serviço',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_servico'}),
    )

    class Meta:
        model = Execucao
        fields = ['servico', 'valor_cobrado', 'observacao']
        widgets = {
            'valor_cobrado': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'id': 'id_valor_cobrado',
            }),
            'observacao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Opcional. Ex: carro muito sujo, cobrado a mais.',
            }),
        }
