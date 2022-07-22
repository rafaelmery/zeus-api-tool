# Ferramenta  para configuração de equipamentos com ZEUS OS
# Desenvolvido por Rafael Mery
# Email: rafael.freitas@intelbras.com.br
# Julho/22

import os
import json
import ipaddress 
import requests
import requests.exceptions 
import getpass

global IP_ADDRESS  #variável global com o endereço  IP
global TOKEN       #Variável que armazena o token do login
global SOURCE_CODE #Variável que armazena o código de requisição
global HEADERS 

clear = lambda: os.system('cls') #Função para limpar a tela (Windows)
#clear = lambda: os.system('clear') #Função para limpar a tela (Linux)

def validate_ip_address(address):
    try:
        ip = ipaddress.ip_address(address)
        return True
    except :
        return False

def api_login ():
    global IP_ADDRESS 
    global HEADES
    IP_ADDRESS = input(' Informe o endereço IP do dispositivo: ')
    while True:
        if validate_ip_address(IP_ADDRESS):
            user = input(' Usuário: ')
            password = getpass.getpass(' Senha: ')   
            break   
        else:
            print('\n>>> ERRO: Endereço IP {} inválido.\n'.format(IP_ADDRESS))     

    url_login = 'http://{}/cgi-bin/api/v3/system/login'.format(IP_ADDRESS)

    login_credentials = {
        'data': {
        'username' : user,
        'password': password
    }}

    try:
        resposta = requests.post(url_login, json = login_credentials, timeout=5)
        token = json.loads(resposta.text)
        TOKEN = token['data']['Token']
        HEADERS = {'Content-Type': 'application/json', 'Authorization' : 'Token {}'.format(TOKEN)}
        return (resposta.status_code)
  
    except requests.exceptions.Timeout:
        print('Tempo expirado')
        return None
    except:
        return (resposta.status_code)

def menu_principal():
    global IP_ADDRESS 
    
    print('\n===================== API ZEUS Tool =====================\n')
    print('Escolha uma das opções abaixo:')
    print('---------------------------------------------------------')
    print('1 - Informações básicas')
    print('2 - Reiniciar Equipamento')
    print('3 - Reset padrão de fábrica')
    print('0 - Sair') 
    print('---------------------------------------------------------\n')

def get_ap_status():
    global IP_ADDRESS 
    global HEADERS 
    url = 'http://{}/cgi-bin/api/v3/system/status'.format(IP_ADDRESS)  
    resposta = requests.get(url, headers = HEADERS)
    
    clear()
    print('------ Informações básicas do Dispositivo ------')
    print('>>  IPv4')
    print(' - Tipo IP: ', resposta.json()['data']['lan']['ipv4']['mode'])
    print(' - Endereço: ', resposta.json()['data']['lan']['ipv4']['ip_address'])
    print(' - Gateway: ', resposta.json()['data']['lan']['ipv4']['gateway'])
    print(' - MAC: ', resposta.json()['data']['lan']['ipv4']['mac_address'])
    print('')
    print('>>  Equipamento')    
    print(' - Modo de operação: ', resposta.json()['data']['device']['network_mode'])
    print(' - Firmware: ', resposta.json()['data']['device']['version'])
    print(' - Modelo: ', resposta.json()['data']['device']['model'])

def ap_reboot():
    global IP_ADDRESS 
    global HEADERS 
    url = 'http://{}/cgi-bin/api/v3/system/reboot'.format(IP_ADDRESS)
    resposta = requests.put(url, headers = HEADERS)
    print('Status code',resposta.status_code)
    print('Comando enviado com sucesso. É preciso autenticar novamente para continuar.')

def ap_reset():
    global IP_ADDRESS 
    global HEADERS 
    url = 'http://{}/cgi-bin/api/v3/system/config'.format(IP_ADDRESS)
    resposta = requests.delete(url, headers = HEADERS)
    print('Status code',resposta.status_code)
    print('Comando enviado com sucesso. É preciso autenticar novamente para continuar.')

def show_top():
    print('     ___   ___  ____  ____  ______  ______')
    print('    / _ | / _ \/  _/ /_  / / __/ / / / __/')
    print('   / __ |/ ___// /    / /_/ _// /_/ /\ \  ')
    print('  /_/ |_/_/  /___/   /___/___/\____/___/  ')
    print('\n>>> Bem Vindo à ferramenta API Zeus OS - V0.1<<<\n')
    
### Início do programa

clear()

show_top()

SOURCE_CODE = api_login()

while True:
    
    if SOURCE_CODE == 200:
        menu_principal()  
        user_input = input('Opção: ')

        if user_input == '0':
            print('"So long, and thanks for all  the fish." - Desenvolvido por Rafael Mery')
            break

        if user_input == '1':
            get_ap_status()

        if user_input == '2':
            ap_reboot()
    else:
        print('\n>>> Falha no login: {}. Tente novamente.\n'.format(SOURCE_CODE))
        SOURCE_CODE = api_login()
        




