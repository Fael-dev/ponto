from django import forms
from .models import Funcionario, Ponto, Diaria

class FuncForm(forms.ModelForm):
	class Meta:
		model = Funcionario
		fields = ('codigo',)

class CadFuncForm(forms.ModelForm):
	class Meta:
		model = Funcionario
		fields = ('nome', 'funcao', 'data_admissao', 'codigo', 'carga_horaria')

class HistForm(forms.ModelForm):
	class Meta:
		model = Ponto
		fields = ('codigo', 'data')

class DiaForm(forms.ModelForm):
	hrs_trabalhadas = forms.CharField(max_length=10, required=True)
	total_horas = forms.CharField(max_length=10, required=True)
	hora_extra = forms.CharField(max_length=10, required=True)
	intervalo = forms.CharField(max_length=10, required=True)
	class Meta:
		model = Diaria
		fields = ('hrs_trabalhadas', 'total_horas', 'hora_extra', 'intervalo', 'saida', 'entrada')

