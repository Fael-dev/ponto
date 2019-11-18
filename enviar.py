import requests
import random
import socket

antena = random.randint(1,5)
code = random.randint(1,10)
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)

def sendData(antena_id, code):
	url = 'http://127.0.0.1:8000/'
	result = requests.Session()
	result.get(url)

	if 'csrftoken' in result.cookies:
		csrftoken = result.cookies['csrftoken']
	else:
		csrftoken = result.cookies['csrf']


	dados = {
	 'csrfmiddlewaretoken':csrftoken,
	 'server': host_ip,
	 'antena': str(antena_id), 
	 'code': str(code),
	}

	response = result.post(url, data=dados)

	if response.status_code == 200:
		print("Enviado com sucesso!")
		print(response.status_code)
	else:
		print("Falha ao enviar!")
		print(response.status_code)
	print(host_ip)
	print(host_name)

sendData(antena, code)