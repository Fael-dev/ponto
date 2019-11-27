from django.db import models
from datetime import datetime

class Funcionario(models.Model):
	nome = models.CharField(max_length=150)
	funcao = models.CharField(max_length=50)
	data_admissao = models.DateTimeField(default=datetime.now)
	codigo = models.TextField()
	responsavel = models.CharField(max_length=150)
	carga_horaria = models.IntegerField(null=True)

	def data_hora(self):
		self.data_admissao = datetime.now()
		self.save()

	def __str__(self):
		return self.nome

class Ponto(models.Model):
	data = models.DateTimeField(default=datetime.now)
	dia = models.CharField(max_length=10)
	codigo = models.TextField()

	def data_hora(self):
		self.data = datetime.now()
		self.save()

	def __str__(self):
		return self.codigo
class Diaria(models.Model):
	codigo = models.TextField()
	data = models.CharField(max_length=10)
	hrs_trabalhadas = models.CharField(max_length=10, blank=True)# TEM QUE SER FLOAT
	total_horas = models.CharField(max_length=10, blank=True) # TEM QUE SER FLOAT
	hora_extra = models.CharField(max_length=10, blank=True) 
	intervalo = models.CharField(max_length=10, blank=True) # TEM QUE SER FLOAT
	entrada = models.DateTimeField(auto_now = False , auto_now_add = False)
	saida = models.DateTimeField(auto_now = False , auto_now_add = False, null=True)

	def __str__(self):
		return self.codigo

	

