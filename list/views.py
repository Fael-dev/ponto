from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator 
from .models import Funcionario, Ponto, Diaria
from .forms import FuncForm, HistForm, CadFuncForm, DiaForm
import time
from datetime import datetime
from django.contrib import messages
from .utils import render_to_pdf 
from django.template.loader import get_template
from django.http import HttpResponse



'''
	Função 'HOMEPAGE' recebe as informações enviadas pela antena e 
	faz os tratamentos certos antes de salvar.
	add ao repositório do Pedro
'''
def homepage(request):
	template_name = 'homepage.html'
	dt_str = datetime.now()
	dt = dt_str.strftime('%d-%m-%Y')

	if request.method == 'POST':
		form = FuncForm(request.POST)
		fml = form.save(commit=False)
		func = Funcionario.objects.filter(codigo=fml.codigo).first()
		if func:
			pt = Ponto.objects.filter(codigo=fml.codigo, dia=dt).last()
			dtnow = datetime.timestamp(datetime.now())
			dtbatida = datetime.timestamp(pt.data)
			result = dtnow - dtbatida
			if result >= 600:
				hist = Ponto()
				hist.codigo = fml.codigo
				hist.data = datetime.now()
				hist.dia = dt
				hist.save()
				# IFs DE ENTRADA/SAIDA PARA PREENCHIMENTO DA TABELA DIÁRIA.
				p = Ponto.objects.filter(codigo=fml.codigo, dia=dt)
				print(len(p))
				if len(p) == 1: # SE O USUÁRIO PASSOU UMA VEZ, CADASTRA NO BANCO DIÁRIA A CHEGADA NA EMPRESA
					ent = Ponto.objects.get(codigo=fml.codigo, dia=dt)
					dia = Diaria()
					dia.entrada = ent.data
					dia.codigo = ent.codigo
					dia.data = dt
					dia.save()
					print('ENTRADA')
				elif len(p) == 3: # SE O USUÁRIO PASSOU TRES VEZES, É CALCULADO O INTERVALO DA SEGUNDA E TERCEIRA BATIDA E ACRESCENTADO NO BANCO DIÁRIA. 
					dia = Diaria.objects.get(codigo=fml.codigo, data=dt)
					p = Ponto.objects.filter(codigo=fml.codigo, dia=dt)
					saida = datetime.timestamp(p[1].data)
					chegada = datetime.timestamp(p[2].data)
					s = datetime.fromtimestamp(saida)
					c = datetime.fromtimestamp(chegada)
					dia.intervalo = c.hour - s.hour
					dia.save()
					print('INTERVALO')
				elif len(p) == 4: # SE O USUÁRIO PASSOU QUATRO VEZES, CADASTRA NO BANCO DIÁRIA O TÉRMINO DO EXPEDIENTE NA EMPRESA
					dia = Diaria.objects.get(codigo=fml.codigo, data=dt)
					inicio = datetime.timestamp(p[0].data)
					fim = datetime.timestamp(p[3].data)
					intervalo = float(dia.intervalo)
					total = fim - inicio
					t = datetime.fromtimestamp(total)
					i = datetime.fromtimestamp(intervalo)
					dia.saida = p[3].data
					dia.total_horas = t.hour
					dia.hrs_trabalhadas = t.hour - i.hour
					dia.hora_extra = dia.hrs_trabalhadas - func.carga_horaria
					dia.save()
					print('SAÍDA')
					
				else:
					print('else')
			else:
				form = FuncForm()

		else:
			fml.save()
	else:
		form = FuncForm()
	
	return render(request, template_name)

	
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

	return render(request, template_name, {'obj':obj, 'sem': sem, 'com': com, 'total':total})


'''
	Função 'DELETEOBJ' deleta os Funcionarios e o histórico relacionado automaticamente.
'''
@login_required
def deleteObj(request, id):
	obj = get_object_or_404(Funcionario, pk=id)
	while Ponto.objects.filter(codigo=obj.codigo):
		hist = Ponto.objects.filter(codigo=obj.codigo)
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

@login_required
def editarDia(request, id):
	dia = Diaria.objects.get(pk=id)
	p = Ponto.objects.filter(codigo=dia.codigo).first()
	form = DiaForm(instance=dia)
	template_name = 'editardia.html'
	if request.method == 'POST':
		form = DiaForm(request.POST, instance=dia)
		if form.is_valid():
			dia.save()
			return redirect('/lista')
		else:
			return redirect('/lista')
	else:
		return render(request, template_name, {'form':form, 'p':p })
	return render(request, template_name, {'form':form, 'p':p })

'''
	Função 'ADD' Relaciona Funcionarios a determinado código.
'''
@login_required
def add(request, id):
	objt = get_object_or_404(Funcionario, pk=id) 
	user = str(request.user)
	form = CadFuncForm(instance=objt)
	template_name = 'add.html'
	if request.method == 'POST':
		form = CadFuncForm(request.POST, instance=objt)
		if form.is_valid():
			objt.responsavel = user
			objt.save()
			return redirect('/lista')
		else:
			return render(request, template_name, {'form':form})
	else:
		return render(request, template_name, {'form': form})


'''
	Função 'Ponto' Lista todos os registros de um determinado código.
'''
@login_required
def historico(request, codigo):
	filtro_data = request.POST.get('filterdata')
	if filtro_data:
		hist = Ponto.objects.filter(codigo=codigo, dia=filtro_data)
		dia = Diaria.objects.filter(codigo=codigo, data=filtro_data).first()
	else:	
		dia = Diaria.objects.filter(codigo=codigo).last()
		hist = Ponto.objects.filter(codigo=codigo, dia=dia.data)

	individuo = Funcionario.objects.get(codigo=codigo)
	data = Diaria.objects.filter(codigo=codigo)
	if not hist:
		return render(request, '404.html')


	template_name = 'historico.html'
	return render(request, template_name, {'hist':hist,'individuo':individuo, 'dia':dia, 'data':data})

'''
	Função 'GERAR_PDF' Gera relatório em formato PDF a partir de uma filtragem realizada previamente.
'''
@login_required
def gerar_pdf(request, codigo):
	func = Funcionario.objects.get(codigo=codigo)
	data_emissao = datetime.now()
	filtro_select = request.POST.get('selectdata')
	option = request.POST.get('selectcampos')
	if filtro_select == 'todas': 
		dia = Diaria.objects.filter(codigo=codigo)
	else:
		dia = Diaria.objects.filter(codigo=codigo ,data=filtro_select)

	data = {'dia': dia, 'data_emissao':data_emissao, 'func':func, 'option':option, 'data':filtro_select}
	pdf = render_to_pdf('pdf.html', data)

	return HttpResponse(pdf, content_type='application/pdf')


