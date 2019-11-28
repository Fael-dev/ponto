from django.urls import path
from . import views
from django.conf.urls import url, include
from django.contrib.auth.models import User

urlpatterns = [
	path('', views.homepage, name='homepage'),
	path('lista/', views.listar, name='listar'),
	path('lista/delete/<int:id>', views.deleteObj, name='delete-teste'),
	path('lista/cadastro/<int:id>', views.add, name='add-objeto'),
	path('lista/historico/<str:codigo>', views.historico, name='historico'),
	path('lista/historico/diaria/<int:id>', views.editarDia, name='editar-dia'),
	path('lista/historico/pdf/<str:codigo>', views.gerar_pdf, name='pdf'),
	path('lista/editar/<int:id>/', views.editar, name='editar'),
]