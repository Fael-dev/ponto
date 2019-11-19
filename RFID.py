import requests
import serial
import time
import binascii

entrada = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.5)
#saida = serial.Serial('/dev/ttyS1', 9600, timeout=0.5)
val_entrada = 0
val_saida = 0

def sendData(antena_id, code): 

  url = 'http://172.16.8.107:8000/'

  result = requests.session()
  result.get(url)
  if 'csrftoken' in result.cookies:
    csrftoken = result.cookies['csrftoken']
  else:
    csrftoken = result.cookies['csrf']

  dados = {
  'csrfmiddlewaretoken':csrftoken,
  'server': '172.16.8.107',
  'antena': str(antena_id), 
  'code':str(code),
  }
  
  response = result.post(url , data=dados)

  if response.status_code == 200:
    print('Deu Certo!')
    print(response.status_code)
  else:
    print('Deu Errado')
    print(response.status_code)

while(True):
  valorEntrada = entrada.readline()
#  valorSaida = saida.readline()
  Entrada_hex = binascii.hexlify(valorEntrada).decode('utf-8')
#  Saida_hex = binascii.hexlify(valorSaida).decode('utf-8')
  if (str(valorEntrada) != str(val_entrada)) and (Entrada_hex != ""):
    print("Valor de Entrada: ",Entrada_hex)
    sendData(1, Entrada_hex)
    val_entrada = valorEntrada
    
'''
  if (str(valorSaida) != str(val_saida)) and (Saida_hex != ""):
    print("Valor de Saida  : ",Saida_hex)
    sendData(2, Saida_hex)
    val_saida = valorSaida 
'''
entrada.close()
#saida.close()
