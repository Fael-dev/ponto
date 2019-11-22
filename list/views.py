from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator 
from .models import Funcionario, Historico
from .forms import FuncForm, HistForm, CadFuncForm
import time
from datetime import datetime
from django.contrib import messages
from .utils import render_to_pdf 
from django.template.loader import get_template
from django.http import HttpResponse


'''
	Função 'HOMEPAGE' recebe as informações enviadas pela antena e 
	faz os tratamentos certos antes de salvar.
'''
def homepage(request):
	template_name = 'homepage.html'
	if request.method == 'POST':
		form = FuncForm(request.POST)
		fml = form.save(commit=False)
		func = Funcionario.objects.filter(codigo=fml.codigo).first()
		if func:
			pass
		else:
			fml.save()
	else:
		form = FuncForm()
	
	return render(request, template_name)

	'''
	log = datetime.now()
	if request.method == 'POST':
		form = FuncForm(request.POST)
		fml = form.save(commit=False)
		obj1 = Funcionario.objects.filter(codigo=fml.codigo).first()
		# Verifica se existe algum Funcionario cadastrado com esse código
		if obj1:
			# Pega a data do Funcionario, converte para TIMESTAMP e subtrai pela data atual
		    timestamp = datetime.timestamp(obj1.date)
		    timesnow = datetime.timestamp(datetime.now())
		    result = (timesnow - timestamp)
		    print('Resultado: {} do Código: {} '.format(result, obj1.codigo))
			
		    # Se o resultado desse subtração for maior que 60(1 minuto) ele pode cadastrar
		    if result > 60:
		    	# Adicionando o atual Funcionario ao Historico antes de atualizá-lo
		    	hist = Historico()
		    	hist.server = fml.server
		    	hist.antena = fml.antena
		    	hist.codigo = fml.codigo
		    	hist.Funcionario = obj1.Funcionario
		    	hist.date = fml.date
		    	hist.save() 
		    	# Atualizando o Funcionario anterior, pelo que acabou de receber
		    	obj = Funcionario.objects.get(codigo=fml.codigo)
		    	obj.server = fml.server
		    	obj.antena = fml.antena
		    	obj.codigo = fml.codigo
		    	obj.date = datetime.now()
		    	obj.save()
		    	return redirect('/') 

		    # Se o resultado for menor que 1 minuto
		    else:
		    	return redirect('/')

		# Se o Funcionario não existe, ele é cadastrado no ELSE
		else:
			hist = Historico()
			hist.server = fml.server
			hist.antena = fml.antena
			hist.codigo = fml.codigo
			hist.date = datetime.now()
			hist.save()
			fml.date = datetime.now()
			fml.save()

		return redirect('/')
	
	# Se o Formulário não for o método POST ele vem pro ELSE
	else:
		form = FuncForm()

	return render(request, template_name, {'log':log})
	'''
	
'''
	Função 'LISTAR' Lista os dados do banco na tela e também de pesquisas e filtros.
'''
@login_required
def listar(request):
	search = request.GET.get('search')
	filtro = request.GET.get('filter')
	sem = Funcionario.objects.filter(nome='').count()
	total = Funcionario.objects.all().count()
	com = total - sem
	
	filtro_select = request.GET.get('selectcodigo')
	if filtro_select == 'todos':
		hist = Historico.objects.all().order_by('-data_admissao')
	else:
		hist = Historico.objects.filter(codigo=filtro_select)

	if search:
		obj = Funcionario.objects.filter(nome__icontains=search) 

	elif filtro:
		if filtro == 'sem':
			obj = Funcionario.objects.filter(nome='')
		elif filtro == 'todos':
			lista = Funcionario.objects.all().order_by('-data_admissao')
			paginator = Paginator(lista, 10)
			page = request.GET.get('page')
			obj = paginator.get_page(page)
		else:
			obj = Funcionario.objects.exclude(nome='')

	else:
		lista = Funcionario.objects.all().order_by('-data_admissao')
		paginator = Paginator(lista, 10)
		page = request.GET.get('page')
		obj = paginator.get_page(page)


	template_name = 'index.html'

	return render(request, template_name, {'obj':obj, 'sem': sem, 'com': com, 'total':total, 'hist':hist})


'''
	Função 'DELETEOBJ' deleta os Funcionarios e o histórico relacionado automaticamente.
'''
@login_required
def deleteObj(request, id):
	obj = get_object_or_404(Funcionario, pk=id)
	while Historico.objects.filter(codigo=obj.codigo):
		hist = Historico.objects.filter(codigo=obj.codigo)
		hist.delete()
	obj.delete()
	messages.info(request, 'Registro ('+obj.codigo+') deletado com sucesso')
	return redirect('/lista')


'''
	Função 'EDITAR' Edita cadastro do funcionário.
'''
@login_required
def editar(request, id):
	obj = Funcionario.objects.get(pk=id)
	form = CadFuncForm(instance=obj)
	template_name = 'editar.html'
	if request.method == 'POST':
		form = CadFuncForm(request.POST, instance=obj)
		if form.is_valid():
			obj.save()
			return redirect('/lista')
		else:
			return redirect('/lista')
	else:
		return render(request, template_name, {'form':form})
	return render(request, template_name, {'form':form})

'''
	Função 'ADD' Relaciona Funcionarios a determinado código.
'''
@login_required
def add(request, id):
	objt = get_object_or_404(Funcionario, pk=id) 
	form = CadFuncForm(instance=objt)
	template_name = 'add.html'
	if request.method == 'POST':
		form = CadFuncForm(request.POST, instance=objt)
		if form.is_valid():
			objt.save()
			return redirect('/lista')
		else:
			return render(request, template_name, {'form':form})
	else:
		return render(request, template_name, {'form': form})


'''
	Função 'HISTORICO' Lista todos os registros de um determinado código.
'''
@login_required
def historico(request, codigo):
	total = Historico.objects.filter(codigo=codigo).count()
	his = list(Historico.objects.filter(codigo=codigo).order_by('-data'))
	paginator = Paginator(his, 10)
	page = request.GET.get('page')
	hist = paginator.get_page(page)
	
	if not hist:
		return render(request, '404.html')

	template_name = 'historico.html'
	return render(request, template_name, {'hist':hist, 'codigo':codigo, 'total':total })

'''
	Função 'GERAR_PDF' Gera relatório em formato PDF a partir de uma filtragem realizada previamente.
'''
@login_required
def gerar_pdf(request):
	
	sem = Funcionario.objects.filter(nome='').count()
	total = Funcionario.objects.all().count()
	com = total - sem
	data_emissao = datetime.now()
	user = request.user

	filtro_select = request.POST.get('selectcodigo')
	option = request.POST.get('selectcampos')

	if filtro_select == 'todos':
		codigo = filtro_select
		hist = Historico.objects.all().order_by('-codigo')
	else:
		codigo = filtro_select
		hist = Historico.objects.filter(codigo=filtro_select).order_by('-codigo')


	data = {'hist': hist, 'user':user, 'data_emissao':data_emissao, 'codigo':codigo, 'opt':option, 'com':com, 'sem': sem, 'total':total}
	pdf = render_to_pdf('relatorio.html', data)

	return HttpResponse(pdf, content_type='application/pdf')

def pdf(request):
	template_name = 'pdf.html'
	pdf = render_to_pdf(template_name)
	return HttpResponse(pdf, content_type='application/pdf')

def post(request):
	template_name = 'pdf.html'
	log = datetime.now()

	if request.method == 'POST':
		form = FuncForm(request.POST)
		fml = form.save(commit=False)
		obj1 = Funcionario.objects.filter(codigo=fml.codigo).first()
		# Verifica se existe algum Funcionario cadastrado com esse código
		if obj1:
			# Pega a data do Funcionario, converte para TIMESTAMP e subtrai pela data atual
		    timestamp = datetime.timestamp(obj1.date)
		    timesnow = datetime.timestamp(datetime.now())
		    result = (timesnow - timestamp)
		    print('Resultado: {} do Código: {} '.format(result, obj1.codigo))
			
		    # Se o resultado desse subtração for maior que 60(1 minuto) ele pode cadastrar
		    if result > 60:
		    	# Adicionando o atual Funcionario ao Historico antes de atualizá-lo
		    	hist = Historico()
		    	hist.server = fml.server
		    	hist.antena = fml.antena
		    	hist.codigo = fml.codigo
		    	hist.Funcionario = obj1.Funcionario
		    	hist.date = fml.date
		    	hist.save() 
		    	# Atualizando o Funcionario anterior, pelo que acabou de receber
		    	obj = Funcionario.objects.get(codigo=fml.codigo)
		    	obj.server = fml.server
		    	obj.antena = fml.antena
		    	obj.codigo = fml.codigo
		    	obj.date = datetime.now()
		    	obj.save()
		    	return redirect('/') 

		    # Se o resultado for menor que 1 minuto
		    else:
		    	return redirect('/')

		# Se o Funcionario não existe, ele é cadastrado no ELSE
		else:
			hist = Historico()
			hist.server = fml.server
			hist.antena = fml.antena
			hist.codigo = fml.codigo
			hist.date = datetime.now()
			hist.save()
			fml.date = datetime.now()
			fml.save()

		return redirect('/')
	
	# Se o Formulário não for o método POST ele vem pro ELSE
	else:
		form = FuncForm()

	return render(request, template_name, {'log':log})