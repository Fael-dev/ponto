from django import forms
from .models import Funcionario, Ponto

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
