from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator 
from .models import Objeto, Historico
from .forms import ObjForm
from datetime import datetime
from django.contrib import messages

'''
	COM O LOGIN REQUIRED O CÓDIGO NÃO ESTÁ GUARDANDO OS DADOS RECEBIDOS DA ANTENA.

'''

def homepage(request):

	template_name = 'homepage.html'
	
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
		    print('Resultado: ', result)
		    # Se o resultado desse subtração for maior que 60(1 minuto) ele pode cadastrar
		    if result > 60:
		    	# Adicionando o atual objeto ao Historico antes de atualizá-lo
		    	hist = Historico()
		    	hist.server = obj1.server
		    	hist.antena = obj1.antena
		    	hist.code = obj1.code
		    	hist.objeto = obj1.objeto
		    	hist.date = obj1.date
		    	hist.save() 
		    	# Adicionando o novo objeto ao histórico
		    	hist1 = Historico()
		    	hist1.server = fml.server
		    	hist1.antena = fml.antena
		    	hist1.code = fml.code
		    	hist1.objeto = obj1.objeto
		    	hist1.date = datetime.now()
		    	hist1.save() 
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
			fml.date = datetime.now()
			fml.save()

		return redirect('/')
	
	# Se o Formulário não for o método POST ele vem pro ELSE
	else:
		form = ObjForm()

	return render(request, template_name)

@login_required
def listar(request):
	search = request.GET.get('search')
	filtro = request.GET.get('filter')
	sem = Objeto.objects.filter(objeto='').count()
	total = Objeto.objects.all().count()
	com = total - sem
	# If de Pesquisas e filtros
	if search:
		obj = Objeto.objects.filter(objeto__icontains=search) 

	elif filtro:
		if filtro == 'sem':
			obj = Objeto.objects.all().order_by('objeto')
		
		else:
			obj = Objeto.objects.all().order_by('-objeto')

	else:
		lista = Objeto.objects.all().order_by('-date')
		paginator = Paginator(lista, 10)
		page = request.GET.get('page')
		obj = paginator.get_page(page)


	template_name = 'index.html'

	return render(request, template_name, {'obj':obj, 'sem': sem, 'com': com, 'total':total})

@login_required
def deleteObj(request, id):
	obj = get_object_or_404(Objeto, pk=id)
	while Historico.objects.filter(code=obj.code):
		hist = Historico.objects.filter(code=obj.code)
		hist.delete()
	obj.delete()
	messages.info(request, 'Objeto deletado com sucesso')

	return redirect('/lista')

@login_required
def add(request, id):
	objt = get_object_or_404(Objeto, pk=id) 
	form = ObjForm(instance=objt)
	template_name = 'add.html'
	if request.method == 'POST':
		form = ObjForm(request.POST, instance=objt)
		if form.is_valid():
			objt.save()
			return redirect('/lista')
		else:
			return render(request, template_name, {'form':form})
	else:
		return render(request, template_name, {'form': form})

@login_required
def historico(request, code):
	hist = list(Historico.objects.filter(code=code).order_by('-date'))
	if not hist:
		return render(request, '404.html')
	# hist = get_list_or_404(Historico, code=code)
	template_name = 'historico.html'
	return render(request, template_name, {'hist':hist})
