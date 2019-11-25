from django.db import models
from datetime import datetime

class Funcionario(models.Model):
	nome = models.CharField(max_length=150)
	funcao = models.CharField(max_length=50)
	data_admissao = models.DateTimeField(default=datetime.now)
	codigo = models.TextField()
	responsavel = models.CharField(max_length=150)
	#ADICIONAR COLUNA CARGA_HORÁRIA

	def data_hora(self):
		self.data_admissao = datetime.now()
		self.save()

	def __str__(self):
		return self.nome

class Historico(models.Model):
	passagem = models.DateTimeField(default=datetime.now)
	data = models.CharField(max_length=10)
	codigo = models.TextField()

	def data_hora(self):
		self.passagem = datetime.now()
		self.save()

	def __str__(self):
		return self.codigo

	

