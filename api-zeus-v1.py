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
from collections import OrderedDict

global IP_ADDRESS  #variável global com o endereço  IP
global TOKEN       #Variável que armazena o token do login
global SOURCE_CODE #Variável que armazena o código de requisição
global HEADERS     # Armazena os parametros de HEADER

clear = lambda: os.system('cls') #Função para limpar a tela (Windows)
#clear = lambda: os.system('clear') #Função para limpar a tela (Linux)

def user_confirmation(action):
    confirm = input('\nTem certeza que deseja {}? (s/n) '.format(action))
    if confirm == 's' or confirm == 'S':
        return True
    else:
        return False

def validate_ip_address(address):
    try:
        ip = ipaddress.ip_address(address)
        return True
    except :
        return False

def api_login():
    global IP_ADDRESS 
    global HEADERS
    
    while True:
        IP_ADDRESS = input('\n > Informe o endereço IP do dispositivo: ')
        if validate_ip_address(IP_ADDRESS):
            user = input(' > Usuário: ')
            password = getpass.getpass(' > Senha: ')   
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
        clear()
        print('\n >> Login feito com sucesso!')
        return (resposta.status_code)
  
    except requests.exceptions.Timeout:
        print('Tempo expirado')
        return None
    except:
        return (resposta.status_code)

def device_info():
    global IP_ADDRESS 
    global HEADERS
    global MAC_ADDRESS
    global DEVICE_MODEL
    global SVERSION

    url = 'http://{}/cgi-bin/api/v3/system/status'.format(IP_ADDRESS)  
    resposta = requests.get(url, headers = HEADERS)

    MAC_ADDRESS = resposta.json()['data']['lan']['ipv4']['mac_address']
    DEVICE_MODEL = resposta.json()['data']['device']['model']
    SVERSION = resposta.json()['data']['device']['version']

def menu_principal():
    global IP_ADDRESS 
    global HEADERS 
    global MAC_ADDRESS
    global DEVICE_MODEL
    global SVERSION
   
    print('                               API ZEUS Tool                              ')
    print('---------------------------------------------------------------------------')
    print('|      Modelo      |    Firmware    |        MAC        |        IP       |')
    print('| {2:^16} | {3:^14} | {1:^17} | {0:^15} |'.format(IP_ADDRESS, MAC_ADDRESS,DEVICE_MODEL,SVERSION))
    print('---------------------------------------------------------------------------')
    print('\n> Escolha uma das opções abaixo:')
    print('-------------------------------------------')
    print(' Gereciamento')
    print('   1  -> Informações básicas')
    print('   2  -> Reiniciar Equipamento')
    print('   3  -> Reset padrão de fábrica')
    print('   4  -> Habilitar SSH')
    print('   5  -> Alterar IP')
    print('\n Wireless')
    print('   6  -> Site Survey 2.4 Ghz')
    print('   7  -> Site Survey 5 Ghz')
    print('   8  -> Clientes Conectados 2.4Ghz')
    print('   9  -> Clientes Conectados 5 Ghz')  
    print('  10  -> SSIDs')
    print('\n Salvar')
    print('  11  -> Aplicar configurações')   
    print('-------------------------------------------')
    print('Digite "0" para Sair.\n') 

def enable_SSH():
    global IP_ADDRESS 
    global HEADERS 

    url = 'http://{}/cgi-bin/api/v3/service/ssh'.format(IP_ADDRESS)  
    print('>>> Habilitando SSH \n Obs.: SSH será habilitado na pota padrão 22')  
    print('\nCarregando...\n')

    comando = {
        'data': {
        'enabled' : True,
        'port' : 22,
        'wan_access': True,
    }}

    try:
        resposta = requests.put(url, json = comando, headers = HEADERS, timeout=5)
        clear()
        if resposta.status_code == 204:
            print('\n >> SSH habilitado com sucesso! (Porta: 22)\n')
            input(' \nEperte ENTER para voltar ao menu principal')
        else :
            print('\n >> Algo deu errado. Status: {}\n'.format(resposta.status_code))
            print(resposta.text)
            input(' \nEperte ENTER para voltar ao menu principal')  
    
    except requests.exceptions.Timeout:
        print('Tempo expirado')
        return None
    except:
        return (resposta.status_code)

def set_ip():
    global IP_ADDRESS 
    global HEADERS 

    url = 'http://{}/cgi-bin/api/v3/interface/lan/1'.format(IP_ADDRESS)  
    print('\n>>> Alterar endereço IP')  
    ip = input('\n > Endereço: ')
    mask = input(' > Máscara: ')
    gateway = input(' > Gateway: ')
    print('\nCarregando...\n')
    
    comando = {
    "data": {
        "ip_address": ip,
        "spanning": False,
        "netmask": mask,
        "mode": 'static',
        "gateway": gateway
    }}

    try:
        resposta = requests.put(url, json = comando, headers = HEADERS, timeout=5)
        clear()
        if resposta.status_code == 204:
            print('\n >> IP alterado com sucesso!')
            print('\n Aviso: Não esqueça de aplicar as configurações!')  
            input('\nEperte ENTER para voltar ao menu principal')       
        else:
            print('\n >> Algo deu errado. Status: {}\n'.format(resposta.status_code))
            print(resposta.text)
            input(' \nEperte ENTER para voltar ao menu principal')   
  
    except requests.exceptions.Timeout:
        print('Tempo expirado')
        return None
    except:
        print('\nResposta: '+resposta.status_code)
        input('\nEperte ENTER para voltar ao menu principal')

        
def clients_wifi0():
    global IP_ADDRESS 
    global HEADERS 

    url = 'http://{}/cgi-bin/api/v3/interface/wireless/wifi0/clients/wireless'.format(IP_ADDRESS)  
    resposta = requests.get(url, headers = HEADERS)     
    wifi_clients = json.loads(resposta.text)
    clear()
    print('>> Clientes conectados | 2.4 Ghz')
    print('-----------------------------------------------------------------------------------------')
    print('|              SSID              |         Host         |        MAC        |   SINAL   |')
    print('-----------------------------------------------------------------------------------------')

    
    for cliente in wifi_clients['data']['clients']:
        #print(rede['ssid'])        
        print('| {:^30} | {:^20} | {:^17} | {:^8} |'.format(cliente['ssid'], cliente['hostname'],cliente['mac_address'],cliente['signal']))
    
    print('-------------------------------------------------------------------------------')

    input(' \nEperte ENTER para voltar ao menu principal')

def clients_wifi1():
    global IP_ADDRESS 
    global HEADERS 

    try:
        url = 'http://{}/cgi-bin/api/v3/interface/wireless/wifi1/clients/wireless'.format(IP_ADDRESS)  
        resposta = requests.get(url, headers = HEADERS)  
        wifi_clients = json.loads(resposta.text)
        clear()
        print('>> Clientes conectados | 5 Ghz')
        print('-----------------------------------------------------------------------------------------')
        print('|              SSID              |         Host         |        MAC        |   SINAL   |')
        print('-----------------------------------------------------------------------------------------')

        
        for cliente in wifi_clients['data']['clients']:
            print('| {:^30} | {:^20} | {:^17} | {:^8} |'.format(cliente['ssid'], cliente['hostname'],cliente['mac_address'],cliente['signal']))
        
        print('-----------------------------------------------------------------------------------------')

        input(' \nEperte ENTER para voltar ao menu principal')

    except requests.exceptions.Timeout:
        print('Tempo expirado')
        input(' \nEperte ENTER para voltar ao menu principal')
    except:
        print ('Status:'+resposta.status_code)
        input(' \nEperte ENTER para voltar ao menu principal')

def ssid_list():
    global IP_ADDRESS 
    global HEADERS 

    try:
        url = 'http://{}/cgi-bin/api/v3/interface/wireless/ssids/interfaces'.format(IP_ADDRESS)  
        resposta = requests.get(url, headers = HEADERS)  
        ssids = json.loads(resposta.text)
        clear()
        print('>> SSIDs')
        print('\n >> 2.4 Ghz')
        
        for ssid in ssids['data']['radios'][0]['ssids']:
            print('  - {}'.format(ssid['ssid']))

        print('\n >> 5 Ghz')
        
        for ssid in ssids['data']['radios'][1]['ssids']:
            print('  - {}'.format(ssid['ssid']))
            
        input(' \nEperte ENTER para voltar ao menu principal')

    except requests.exceptions.Timeout:
        print('Tempo expirado')
        input(' \nEperte ENTER para voltar ao menu principal')
    except:
        print ('Status:'+resposta.status_code)
        input(' \nEperte ENTER para voltar ao menu principal')       


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
    input(' \nEperte ENTER para voltar ao menu principal')
    
def ap_reboot():
    global IP_ADDRESS 
    global HEADERS 
    global SOURCE_CODE

    if user_confirmation('reiniciar o equipamento'):
        url = 'http://{}/cgi-bin/api/v3/system/reboot'.format(IP_ADDRESS)
        resposta = requests.put(url, headers = HEADERS)
        if resposta.status_code == 200 or resposta.status_code == 204:
            print('Status code',resposta.status_code)
            print('>> Comando enviado com sucesso.')
            input('\n É necessário fazer login novamente. Aperte ENTER para continuar.')
            SOURCE_CODE = api_login()
        else:
            print('\nAlgo deu errado. Status:'+resposta.status_code)
            input('\nEperte ENTER para voltar ao menu principal')
    else:
        print('\n>>> Ação cancelada.')
        input('\nEperte ENTER para voltar ao menu principal')

def ap_reset():
    global IP_ADDRESS 
    global HEADERS 
    global SOURCE_CODE

    if user_confirmation('resetar padrão de fábrica'):
        url = 'http://{}/cgi-bin/api/v3/system/config'.format(IP_ADDRESS)
        resposta = requests.delete(url, headers = HEADERS)
        if resposta.status_code == 200 or resposta.status_code == 204:
            print('Status code',resposta.status_code)
            print('>> Comando enviado com sucesso.')
            input('\n É necessário fazer login novamente. Aperte ENTER para continuar.')
            SOURCE_CODE = api_login()
        else:
            print('\nAlgo deu errado. Status:'+resposta.status_code)
            input('\nEperte ENTER para voltar ao menu principal')
    else:
        print('\n>>> Ação cancelada.')
        input('\nEperte ENTER para voltar ao menu principal')

def show_top():
    print('     ___   ___  ____  ____  ______  ______')
    print('    / _ | / _ \/  _/ /_  / / __/ / / / __/')
    print('   / __ |/ ___// /    / /_/ _// /_/ /\ \  ')
    print('  /_/ |_/_/  /___/   /___/___/\____/___/  ')
    print('\n>>> Bem Vindo à ferramenta API Zeus OS - V 1.2 <<<')

def site_survey_wifi0():
    global IP_ADDRESS 
    global HEADERS 

    url = 'http://{}/cgi-bin/api/v3/interface/wireless/wifi0/survey'.format(IP_ADDRESS)
    resposta = requests.get(url, headers = HEADERS)
    wifi_networks = json.loads(resposta.text)
    clear()
    print('>> Site survey 2.4 Ghz')
    print('-------------------------------------------------------------------------------')
    print('|              SSID              |    Canal    |       BSSID       |   SINAL  |')
    print('-------------------------------------------------------------------------------')

    
    for rede in wifi_networks['data']:
        #print(rede['ssid'])        
        print('| {:^30} | {:^11} | {:^17} | {:^8} |'.format(rede['ssid'],rede['channel'],rede['bssid'],rede['signal']))
    
    print('-------------------------------------------------------------------------------')

    input(' \nEperte ENTER para voltar ao menu principal')


def site_survey_wifi1():
    global IP_ADDRESS 
    global HEADERS 

    url = 'http://{}/cgi-bin/api/v3/interface/wireless/wifi1/survey'.format(IP_ADDRESS)
    resposta = requests.get(url, headers = HEADERS)
    wifi_networks = json.loads(resposta.text)
    clear()
    print('>> Site survey 5 Ghz')
    print('-------------------------------------------------------------------------------')
    print('|              SSID              |    Canal    |       BSSID       |   SINAL  |')
    print('-------------------------------------------------------------------------------')

    
    for rede in wifi_networks['data']:
        print('| {:^30} | {:^11} | {:^17} | {:^8} |'.format(rede['ssid'],rede['channel'],rede['bssid'],rede['signal']))
    
    print('-------------------------------------------------------------------------------')
    input(' \nEperte ENTER para voltar ao menu principal')


def apply_config():
    global IP_ADDRESS 
    global HEADERS 
    global SOURCE_CODE

    url = 'http://{}/cgi-bin/api/v3/system/apply'.format(IP_ADDRESS)   

    try:
        if user_confirmation('aplicar configurações'):
            resposta = requests.post(url,headers = HEADERS, timeout=5)
            clear()
            if resposta.status_code == 200:
                print('\n >> Configurações aplicadas com sucesso!')
                input('\n É necessário fazer login novamente. Aperte ENTER para continuar.')
                
                SOURCE_CODE = api_login()
            else :
                print('\n >> Algo deu errado. Status: {}\n'.format(resposta.status_code))
                input('\nEperte ENTER para voltar ao menu principal')
        else:
            print('\n>>> Ação cancelada.')
            input('\nEperte ENTER para voltar ao menu principal')
  
    except requests.exceptions.Timeout:
        print('Tempo expirado')
        return None
    except:
        print('\n >> Algo deu errado. Status: {}\n'.format(resposta.status_code))
        input('\nEperte ENTER para voltar ao menu principal')
    
#---------------------------------
#       Início do programa 
#---------------------------------

clear()    #limpa a tela

show_top() #exibe logo

SOURCE_CODE = api_login() # solicita os parametros de login do usuário

while True:
    
    if SOURCE_CODE == 200:
        clear()
        device_info()
        menu_principal()  
        user_input = input('Opção: ')

        if user_input == '0':
            print('"So long, and thanks for all  the fish." - Desenvolvido por Rafael Mery')
            break

        if user_input == '1': # Informações básicas
            get_ap_status()

        if user_input == '2': # Reinicia AP
            ap_reboot()

        if user_input == '3': # Reseta AP para padrão de fábrica
            ap_reset()

        if user_input == '4': # Habilita SSH
            enable_SSH()

        if user_input == '5': # Altera o IPv4
            set_ip()

        if user_input == '6': # Scan na rede 2.4
            print('\nCarregando...')
            site_survey_wifi0()

        if user_input == '7': #Scan na rede 5ghz
            print('\nCarregando...')
            site_survey_wifi1()            

        if user_input == '8': # Lista clientes conectados 2.4
            print('\nCarregando...')
            clients_wifi0()            

        if user_input == '9': # Lista clientes conectados 5ghz
            print('\nCarregando...')
            clients_wifi1()       

        if user_input == '10': # Mostra SSIDs anunciados pelo AP
            print('\nCarregando...')
            ssid_list()   
            
        if user_input == '11': # Aplica Configurações
            apply_config()  
                
            
    else:
        print('\n>>> Falha no login: {}. Tente novamente.\n'.format(SOURCE_CODE))
        SOURCE_CODE = api_login()