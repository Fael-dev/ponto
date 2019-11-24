from django import forms
from .models import Funcionario, Historico

class FuncForm(forms.ModelForm):
	class Meta:
		model = Funcionario
		fields = ('codigo',)

class CadFuncForm(forms.ModelForm):
	class Meta:
		model = Funcionario
		fields = ('nome', 'funcao', 'data_admissao', 'codigo')

class HistForm(forms.ModelForm):
	class Meta:
		model = Historico
		fields = ('codigo', 'data', 'passagem')
