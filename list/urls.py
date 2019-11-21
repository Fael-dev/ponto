from django.urls import path
from . import views
from django.conf.urls import url, include
from django.contrib.auth.models import User

urlpatterns = [
	path('', views.homepage, name='homepage'),
	path('lista/', views.listar, name='listar'),
	path('lista/delete/<int:id>', views.deleteObj, name='delete-teste'),
	path('lista/cadastro/<int:id>', views.add, name='add-objeto'),
	path('lista/historico/<str:code>', views.historico, name='historico'),
	path('lista/pdf/', views.gerar_pdf, name='pdf'),
	path('lista/pdf2.0/', views.pdf, name='pdf2.0'),
	path('lista/desvincular/<int:id>/', views.desvincular, name='desvincular'),
]
