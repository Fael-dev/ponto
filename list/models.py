from django.db import models
from datetime import datetime

class Funcionario(models.Model):
	nome = models.CharField(max_length=150)
	funcao = models.CharField(max_length=50)
	data_admissao = models.DateTimeField(default=datetime.now)
	codigo = models.TextField()
	responsavel = models.CharField(max_length=50)

	def data_hora(self):
		self.data_admissao = datetime.now()
		self.save()

	def __str__(self):
		return self.nome

class Historico(models.Model):
	intervalo = models.CharField(max_length=15)
	entrada = models.DateTimeField(default=datetime.now)
	saida = models.DateTimeField(default=datetime.now)
	data = models.DateTimeField(default=datetime.now)
	codigo = models.TextField()
	hora_extra = models.CharField(max_length=100)

	def data_hora(self):
		self.data = datetime.now()
		self.entrada = datetime.now()
		self.saida = datetime.now()
		self.save()

	def __str__(self):
		return self.codigo
	

