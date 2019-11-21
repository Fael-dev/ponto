from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator 
from .models import Objeto, Historico
from .forms import ObjForm, HistForm
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
	log = datetime.now()

	if request.method == 'POST':
		form = ObjForm(request.POST)
		fml = form.save(commit=False)
		obj1 = Objeto.objects.filter(code=fml.code).first()
		# Verifica se existe algum objeto cadastrado com esse código
		if obj1:
			# Pega a data do objeto, converte para TIMESTAMP e subtrai pela data atual
		    timestamp = datetime.timestamp(obj1.date)
		    timesnow = datetime.timestamp(datetime.now())
		    result = (timesnow - timestamp)
		    print('Resultado: {} do Código: {} '.format(result, obj1.code))
			
		    # Se o resultado desse subtração for maior que 60(1 minuto) ele pode cadastrar
		    if result > 60:
		    	# Adicionando o atual objeto ao Historico antes de atualizá-lo
		    	hist = Historico()
		    	hist.server = fml.server
		    	hist.antena = fml.antena
		    	hist.code = fml.code
		    	hist.objeto = obj1.objeto
		    	hist.date = fml.date
		    	hist.save() 
		    	# Atualizando o objeto anterior, pelo que acabou de receber
		    	obj = Objeto.objects.get(code=fml.code)
		    	obj.server = fml.server
		    	obj.antena = fml.antena
		    	obj.code = fml.code
		    	obj.date = datetime.now()
		    	obj.save()
		    	return redirect('/') 

		    # Se o resultado for menor que 1 minuto
		    else:
		    	return redirect('/')

		# Se o objeto não existe, ele é cadastrado no ELSE
		else:
			hist = Historico()
			hist.server = fml.server
			hist.antena = fml.antena
			hist.code = fml.code
			hist.date = datetime.now()
			hist.save()
			fml.date = datetime.now()
			fml.save()

		return redirect('/')
	
	# Se o Formulário não for o método POST ele vem pro ELSE
	else:
		form = ObjForm()

	return render(request, template_name, {'log':log})
	
	
'''
	Função 'LISTAR' Lista os dados do banco na tela e também de pesquisas e filtros.
'''
@login_required
def listar(request):
	search = request.GET.get('search')
	filtro = request.GET.get('filter')
	sem = Objeto.objects.filter(objeto='').count()
	total = Objeto.objects.all().count()
	com = total - sem
	
	filtro_select = request.GET.get('selectcode')
	if filtro_select == 'todos':
		hist = Historico.objects.all().order_by('-date')
	else:
		hist = Historico.objects.filter(code=filtro_select)

	if search:
		obj = Objeto.objects.filter(objeto__icontains=search) 

	elif filtro:
		if filtro == 'sem':
			obj = Objeto.objects.filter(objeto='')
		elif filtro == 'todos':
			lista = Objeto.objects.all().order_by('-date')
			paginator = Paginator(lista, 10)
			page = request.GET.get('page')
			obj = paginator.get_page(page)
		else:
			obj = Objeto.objects.exclude(objeto='')

	else:
		lista = Objeto.objects.all().order_by('-date')
		paginator = Paginator(lista, 10)
		page = request.GET.get('page')
		obj = paginator.get_page(page)


	template_name = 'index.html'

	return render(request, template_name, {'obj':obj, 'sem': sem, 'com': com, 'total':total, 'hist':hist})


'''
	Função 'DELETEOBJ' deleta os objetos e o histórico relacionado automaticamente.
'''
@login_required
def deleteObj(request, id):
	obj = get_object_or_404(Objeto, pk=id)
	while Historico.objects.filter(code=obj.code):
		hist = Historico.objects.filter(code=obj.code)
		hist.delete()
	obj.delete()
	messages.info(request, 'Registro ('+obj.code+') deletado com sucesso')
	return redirect('/lista')


'''
	Função 'DESVINCULAR' desvincula objeto relacionado ao código acidentalmente.
'''
@login_required
def desvincular(request, id):
	obj = Objeto.objects.filter(pk=id).first()
	if request.method == 'POST':
		obj.objeto = ''
		obj.save()
	else:
		return redirect('/lista')
	return redirect('/lista')


'''
	Função 'ADD' Relaciona objetos a determinado código.
'''
@login_required
def add(request, id):
	objt = get_object_or_404(Objeto, pk=id) 
	hist = Historico.objects.filter(code=objt.code).last()
	formHist = HistForm(instance=hist)
	form = ObjForm(instance=objt)
	template_name = 'add.html'
	if request.method == 'POST':
		form = ObjForm(request.POST, instance=objt)
		if form.is_valid():
			hist.objeto = objt.objeto
			hist.save()
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
def historico(request, code):
	total = Historico.objects.filter(code=code).count()
	his = list(Historico.objects.filter(code=code).order_by('-date'))
	
	paginator = Paginator(his, 10)
	page = request.GET.get('page')
	hist = paginator.get_page(page)
	
	if not hist:
		return render(request, '404.html')
	

	template_name = 'historico.html'
	return render(request, template_name, {'hist':hist, 'code':code, 'total':total })

'''
	Função 'GERAR_PDF' Gera relatório em formato PDF a partir de uma filtragem realizada previamente.
'''
@login_required
def gerar_pdf(request):
	
	sem = Objeto.objects.filter(objeto='').count()
	total = Objeto.objects.all().count()
	com = total - sem
	data_emissao = datetime.now()
	user = request.user

	filtro_select = request.POST.get('selectcode')
	option = request.POST.get('selectcampos')

	if filtro_select == 'todos':
		codigo = filtro_select
		hist = Historico.objects.all().order_by('-code')
	else:
		codigo = filtro_select
		hist = Historico.objects.filter(code=filtro_select).order_by('-code')


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
		form = ObjForm(request.POST)
		fml = form.save(commit=False)
		obj1 = Objeto.objects.filter(code=fml.code).first()
		# Verifica se existe algum objeto cadastrado com esse código
		if obj1:
			# Pega a data do objeto, converte para TIMESTAMP e subtrai pela data atual
		    timestamp = datetime.timestamp(obj1.date)
		    timesnow = datetime.timestamp(datetime.now())
		    result = (timesnow - timestamp)
		    print('Resultado: {} do Código: {} '.format(result, obj1.code))
			
		    # Se o resultado desse subtração for maior que 60(1 minuto) ele pode cadastrar
		    if result > 60:
		    	# Adicionando o atual objeto ao Historico antes de atualizá-lo
		    	hist = Historico()
		    	hist.server = fml.server
		    	hist.antena = fml.antena
		    	hist.code = fml.code
		    	hist.objeto = obj1.objeto
		    	hist.date = fml.date
		    	hist.save() 
		    	# Atualizando o objeto anterior, pelo que acabou de receber
		    	obj = Objeto.objects.get(code=fml.code)
		    	obj.server = fml.server
		    	obj.antena = fml.antena
		    	obj.code = fml.code
		    	obj.date = datetime.now()
		    	obj.save()
		    	return redirect('/') 

		    # Se o resultado for menor que 1 minuto
		    else:
		    	return redirect('/')

		# Se o objeto não existe, ele é cadastrado no ELSE
		else:
			hist = Historico()
			hist.server = fml.server
			hist.antena = fml.antena
			hist.code = fml.code
			hist.date = datetime.now()
			hist.save()
			fml.date = datetime.now()
			fml.save()

		return redirect('/')
	
	# Se o Formulário não for o método POST ele vem pro ELSE
	else:
		form = ObjForm()

	return render(request, template_name, {'log':log})