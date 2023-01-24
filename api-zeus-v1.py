# Ferramenta  para configuração de equipamentos com ZEUS OS - API V3
# Desenvolvido por Rafael Mery
# Email: mery.rafael@gmail.com
# Julho/22

import os
import json
import time
import ipaddress 
import requests
import requests.exceptions 
import getpass
from collections import OrderedDict
from discovery import find_aps

global IP_ADDRESS  #variável global com o endereço  IP
global TOKEN       #Variável que armazena o token do login
global SOURCE_CODE #Variável que armazena o código de requisição
global HEADERS     # Armazena os parametros de HEADER
global WIFI_DUALBAND   #Indica se AP é Single ou Dualband (false = single / true = Dual)

clear = lambda: os.system('cls') #Função para limpar a tela (Windows)
#clear = lambda: os.system('clear') #Função para limpar a tela (Linux)

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def lista_aps():
    encontrados =  json.loads(find_aps())
    num_aps = len(encontrados['aps'])
    if num_aps != 0 :
        for ap in encontrados['aps']:
            print(' - ',ap['address'],' Modelo: ',ap['model'],'Firmware: ', ap['version'],'(',ap['description'],')')    
    else:
        msg_warning('> Nenhum AP encontrado.')

def msg_sucess(text):
    print(f'{bcolors.OKGREEN}{text}{bcolors.ENDC}')

def msg_error(text):
    print(f'{bcolors.FAIL}{text}{bcolors.ENDC}')

def msg_warning(text):
    print(f'{bcolors.WARNING}{text}{bcolors.ENDC}')

def msg_header(text):
    print(f'{bcolors.HEADER}{text}{bcolors.ENDC}')

def volta():
    msg_warning(' \nPressione ENTER para continuar')
    input()

def user_confirmation(action):
    msg_warning('\n>> Tem certeza que deseja {}? (s/n) '.format(action))
    confirm = input()
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
            #user = input(' > Usuário: ')
            user = 'admin'
            password = getpass.getpass(' > Senha: ')   
            break   
        else:            
            print(f'{bcolors.FAIL}{bcolors.BOLD}\n>>> ERRO: Endereço IP {IP_ADDRESS} inválido.{bcolors.ENDC}')     

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
        msg_sucess('\n >> Login feito com sucesso!\n')
        time.sleep(1)
        return (resposta.status_code)
  
    except requests.exceptions.Timeout:
        msg_warning('>> Tempo expirado')
        return None
    except:
        return (resposta.status_code)

def device_info():
    global IP_ADDRESS 
    global HEADERS
    global MAC_ADDRESS
    global DEVICE_MODEL
    global SVERSION
    global WIFI_DUALBAND

    url = 'http://{}/cgi-bin/api/v3/system/status'.format(IP_ADDRESS)  
    resposta = requests.get(url, headers = HEADERS)

    MAC_ADDRESS = resposta.json()['data']['lan']['ipv4']['mac_address']
    DEVICE_MODEL = resposta.json()['data']['device']['model']
    SVERSION = resposta.json()['data']['device']['version']

    wifi_id = resposta.json()['data']['wireless']['radios'][0]['id']

    if wifi_id == 'radio0':
        WIFI_DUALBAND = False
    else: 
        WIFI_DUALBAND = True

def menu_principal():
    global IP_ADDRESS 
    global HEADERS 
    global MAC_ADDRESS
    global DEVICE_MODEL
    global SVERSION
   
    print(f'{bcolors.OKGREEN}                               API ZEUS Tool                              {bcolors.HEADER}')
    print('---------------------------------------------------------------------------')
    print(f'|      {bcolors.BOLD}Modelo{bcolors.HEADER}      |    {bcolors.BOLD}Firmware{bcolors.HEADER}    |        {bcolors.BOLD}MAC{bcolors.HEADER}        |        {bcolors.BOLD}IP{bcolors.HEADER}       |')
    print('| {2:^16} | {3:^14} | {1:^17} | {0:^15} |'.format(IP_ADDRESS, MAC_ADDRESS,DEVICE_MODEL,SVERSION)) 
    print(f'---------------------------------------------------------------------------{bcolors.ENDC}')
    print('\n> Escolha uma das opções abaixo:')
    print('-------------------------------------------')
    print(f'{bcolors.OKCYAN} Gereciamento{bcolors.ENDC}')
    print('   1  -> Informações básicas')
    print('   2  -> Reiniciar Equipamento')
    print('   3  -> Reset padrão de fábrica')
    print('   4  -> Habilitar SSH')
    print('   5  -> Alterar IP')
    print(f'{bcolors.OKCYAN}\n Wireless{bcolors.ENDC}')
    print('   6  -> Site Survey 2.4 Ghz')
    print('   7  -> Site Survey 5 Ghz')
    print('   8  -> Clientes Conectados 2.4Ghz')
    print('   9  -> Clientes Conectados 5 Ghz')  
    print('  10  -> SSIDs')
    print(f'{bcolors.OKCYAN}\n Salvar{bcolors.ENDC}')
    print(f'{bcolors.BOLD}  11  -> Aplicar configurações{bcolors.ENDC}')   
    print('-------------------------------------------')
    print(f'{bcolors.WARNING} Digite "0" para Sair.\n{bcolors.ENDC}') 

def enable_SSH():
    global IP_ADDRESS 
    global HEADERS 

    url = 'http://{}/cgi-bin/api/v3/service/ssh'.format(IP_ADDRESS)  
    msg_sucess('>>> Habilitando SSH \n Obs.: SSH será habilitado na pota padrão 22')  
    msg_warning('\nCarregando...\n')

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
            msg_sucess('\n >> SSH habilitado com sucesso! (Porta: 22)\n')
            volta()
        else :
            msg_error('\n >> Algo deu errado. Status: {}\n'.format(resposta.status_code))
            print(resposta.text)
            volta()
    
    except requests.exceptions.Timeout:
        msg_warning('> Tempo expirado')
        return None
    except:
        return (resposta.status_code)

def set_ip():
    global IP_ADDRESS 
    global HEADERS 

    url = 'http://{}/cgi-bin/api/v3/interface/lan/1'.format(IP_ADDRESS)  
    clear()
    msg_header('\n>>> Alterar endereço IP')  
    print ('> Informe o novo endereço IP')
    ip = input('\n > Endereço: ')
    mask = input(' > Máscara: ')
    gateway = input(' > Gateway: ')
    msg_warning('\nEnviando...\n')
    
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
            msg_sucess('\n >> IP alterado com sucesso!')
            msg_warning('\n Aviso: Não esqueça de aplicar as configurações!')  
            volta()     
        else:
            msg_error('\n >> Algo deu errado. Status: {}\n'.format(resposta.status_code))
            print(resposta.text)
            volta()
  
    except requests.exceptions.Timeout:
        msg_warning('Tempo expirado')
        return None
    except:
        msg_warning('\nResposta: '+resposta.status_code)
        volta()

        
def clients_wifi0():
    global IP_ADDRESS 
    global HEADERS 
    global WIFI_DUALBAND

    if WIFI_DUALBAND:
        url = 'http://{}/cgi-bin/api/v3/interface/wireless/wifi0/clients/wireless'.format(IP_ADDRESS)  
    else:
        url = 'http://{}/cgi-bin/api/v3/interface/wireless/radio0/clients/wireless'.format(IP_ADDRESS)  

    resposta = requests.get(url, headers = HEADERS)     
    wifi_clients = json.loads(resposta.text)
    clear()
    msg_header('>> Clientes conectados | 2.4 Ghz')
    print('-----------------------------------------------------------------------------------------')
    print('|             SSID              |        Host         |        MAC        |    SINAL    |')
    print('-----------------------------------------------------------------------------------------')
        
    for cliente in wifi_clients['data']['clients']:
        #print(rede['ssid'])        
        print('| {:^30} | {:^20} | {:^17} | {:^8} |'.format(cliente['ssid'], cliente['hostname'],cliente['mac_address'],cliente['signal']))
    
    print('-------------------------------------------------------------------------------')
    volta()

def clients_wifi1():
    global IP_ADDRESS 
    global HEADERS 
    global WIFI_DUALBAND

    if WIFI_DUALBAND:
        try:
            url = 'http://{}/cgi-bin/api/v3/interface/wireless/wifi1/clients/wireless'.format(IP_ADDRESS)  
            resposta = requests.get(url, headers = HEADERS)  
            wifi_clients = json.loads(resposta.text)
            clear()
            msg_header('>> Clientes conectados | 5 Ghz')
            print('-----------------------------------------------------------------------------------------')
            print('|              SSID              |         Host         |        MAC        |   SINAL   |')
            print('-----------------------------------------------------------------------------------------')

            
            for cliente in wifi_clients['data']['clients']:
                print('| {:^30} | {:^20} | {:^17} | {:^8} |'.format(cliente['ssid'], cliente['hostname'],cliente['mac_address'],cliente['signal']))
            
            print('-----------------------------------------------------------------------------------------')
            volta()

        except requests.exceptions.Timeout:
            msg_warning('> Tempo expirado')
            volta()
        except:
            msg_warning('Status:'+resposta.status_code)
            volta()
    else:
        msg_warning('> Equipamento não possui este recurso.')
        volta()

def ssid_list():
    global IP_ADDRESS 
    global HEADERS
    global WIFI_DUALBAND    

    try:
        url = 'http://{}/cgi-bin/api/v3/interface/wireless/status'.format(IP_ADDRESS)  
        resposta = requests.get(url, headers = HEADERS)  
        ssids = json.loads(resposta.text)
        clear()
        msg_header('>> SSIDs')
        
        if WIFI_DUALBAND:
            msg_header('\n >> Rede 5 Ghz ')
            print('| BSSID: {} | Bandwidth: {} Mhz | TX Power: {} dBm | Canal: {} |'.format(ssids['data'][0]['bssid'],ssids['data'][0]['bandwidth'],ssids['data'][0]['txpower'],ssids['data'][0]['channel']))
            for ssid in ssids['data'][0]['ssids']:
                print(f'{bcolors.OKBLUE}  - {ssid}{bcolors.ENDC}')

            msg_header('\n >> Rede 2.4 Ghz ')
            print('| BSSID: {} | Bandwidth: {}Mhz | TX Power: {}dBm | Canal: {} |'.format(ssids['data'][1]['bssid'],ssids['data'][1]['bandwidth'],ssids['data'][1]['txpower'],ssids['data'][1]['channel']))
            for ssid in ssids['data'][1]['ssids']:
                print(f'{bcolors.OKBLUE}  - {ssid}{bcolors.ENDC}')
        else:
            msg_header('\n >> Rede 2.4 Ghz ')
            print('| BSSID: {} | Bandwidth: {}Mhz | TX Power: {}dBm | Canal: {} |'.format(ssids['data'][0]['bssid'],ssids['data'][0]['bandwidth'],ssids['data'][0]['txpower'],ssids['data'][0]['channel']))
            for ssid in ssids['data'][0]['ssids']:
                print(f'{bcolors.OKBLUE}  - {ssid}{bcolors.ENDC}')
            
        volta()

    except requests.exceptions.Timeout:
        msg_warning('Tempo expirado')
        volta()
    except:
        msg_warning('Status:'+resposta.status_code)
        volta()     


def get_ap_status():
    global IP_ADDRESS 
    global HEADERS 

    url = 'http://{}/cgi-bin/api/v3/system/status'.format(IP_ADDRESS)  
    resposta = requests.get(url, headers = HEADERS)

    tipo_ip = resposta.json()['data']['lan']['ipv4']['mode']
    endereco_ip = resposta.json()['data']['lan']['ipv4']['ip_address']
    gateway = resposta.json()['data']['lan']['ipv4']['gateway']
    mac = resposta.json()['data']['lan']['ipv4']['mac_address']
    network_mode = resposta.json()['data']['device']['network_mode']
    firmware_version = resposta.json()['data']['device']['version']
    modelo = resposta.json()['data']['device']['model']

    
    clear()
    msg_header('------ Informações básicas do Dispositivo ------')
    print('>>  IPv4')
    print(f' - Tipo IP: {bcolors.WARNING}{tipo_ip}{bcolors.ENDC}')
    print(f' - Endereço: {bcolors.WARNING}{endereco_ip}{bcolors.ENDC}')
    print(f' - Gateway: {bcolors.WARNING}{gateway}{bcolors.ENDC}')
    print(f' - MAC: {bcolors.WARNING}{mac}{bcolors.ENDC}\n')
    print('>>  Equipamento')    
    print(f' - Modo de operação: {bcolors.WARNING}{network_mode}{bcolors.ENDC}')
    print(f' - Firmware: {bcolors.WARNING}{firmware_version}{bcolors.ENDC}')
    print(f' - Modelo: {bcolors.WARNING}{modelo}{bcolors.ENDC}')
    volta()
    
def ap_reboot():
    global IP_ADDRESS 
    global HEADERS 
    global SOURCE_CODE

    if user_confirmation('reiniciar o equipamento'):
        url = 'http://{}/cgi-bin/api/v3/system/reboot'.format(IP_ADDRESS)
        resposta = requests.put(url, headers = HEADERS)
        if resposta.status_code == 200 or resposta.status_code == 204:
            #print('Status code',resposta.status_code)
            msg_sucess('>> Comando enviado com sucesso.')
            msg_warning('\n   É necessário fazer login novamente.')
            volta()
            SOURCE_CODE = api_login()
        else:
            msg_error('\nAlgo deu errado. Status:'+resposta.status_code)
            volta()
    else:
        msg_warning('\n>>> Ação cancelada.')
        volta()

def ap_reset():
    global IP_ADDRESS 
    global HEADERS 
    global SOURCE_CODE

    if user_confirmation('resetar padrão de fábrica'):
        url = 'http://{}/cgi-bin/api/v3/system/config'.format(IP_ADDRESS)
        resposta = requests.delete(url, headers = HEADERS)
        if resposta.status_code == 200 or resposta.status_code == 204:
            #print('Status code',resposta.status_code)
            msg_sucess('>> Comando enviado com sucesso.')
            msg_warning('\n   É necessário fazer login novamente.')
            volta()
            SOURCE_CODE = api_login()
        else:
            msg_error('\nAlgo deu errado. Status: '+resposta.status_code)
            volta()
    else:
        msg_warning('\n>>> Ação cancelada.')
        volta()

def show_top():
    print(f'{bcolors.OKGREEN}        ___   ___  ____  ____  ______  ______{bcolors.ENDC}')
    print(f'{bcolors.OKGREEN}       / _ | / _ \/  _/ /_  / / __/ / / / __/{bcolors.ENDC}')
    print(f'{bcolors.OKGREEN}      / __ |/ ___// /    / /_/ _// /_/ /\ \  {bcolors.ENDC}')
    print(f'{bcolors.OKGREEN}     /_/ |_/_/  /___/   /___/___/\____/___/  {bcolors.ENDC}')
    print(f'{bcolors.OKCYAN}\n>>> {bcolors.OKBLUE}Bem Vindo à ferramenta API Zeus OS - V 2.1{bcolors.OKCYAN} <<<{bcolors.ENDC}')

def site_survey_wifi0():
    global IP_ADDRESS 
    global HEADERS
    global WIFI_DUALBAND
    
    if WIFI_DUALBAND: 
        url = 'http://{}/cgi-bin/api/v3/interface/wireless/wifi0/survey'.format(IP_ADDRESS)
    else:
        url = 'http://{}/cgi-bin/api/v3/interface/wireless/radio0/survey'.format(IP_ADDRESS)

    resposta = requests.get(url, headers = HEADERS)
    wifi_networks = json.loads(resposta.text)
    clear()
    msg_header('>> Site survey 2.4 Ghz')
    print('-------------------------------------------------------------------------------')
    print('|              SSID              |    Canal    |       BSSID       |   SINAL  |')
    print('-------------------------------------------------------------------------------')

    
    for rede in wifi_networks['data']:
        #print(rede['ssid'])        
        print('| {:^30} | {:^11} | {:^17} | {:^8} |'.format(rede['ssid'],rede['channel'],rede['bssid'],rede['signal']))
    
    print('-------------------------------------------------------------------------------')
    volta()

def site_survey_wifi1():
    global IP_ADDRESS 
    global HEADERS 
    global WIFI_DUALBAND
    
    if WIFI_DUALBAND: 
        url = 'http://{}/cgi-bin/api/v3/interface/wireless/wifi1/survey'.format(IP_ADDRESS)
        resposta = requests.get(url, headers = HEADERS)
        wifi_networks = json.loads(resposta.text)
        clear()
        msg_header('>> Site survey 5 Ghz')
        print('-------------------------------------------------------------------------------')
        print('|              SSID              |    Canal    |       BSSID       |   SINAL  |')
        print('-------------------------------------------------------------------------------')
        
        for rede in wifi_networks['data']:
            print('| {:^30} | {:^11} | {:^17} | {:^8} |'.format(rede['ssid'],rede['channel'],rede['bssid'],rede['signal']))
        
        print('-------------------------------------------------------------------------------')
        volta()
    else:
        msg_error('\n> Equipamento não possui este recurso.')
        volta()

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
                msg_sucess('\n >> Configurações aplicadas com sucesso!')
                msg_warning('\n   É necessário fazer login novamente.')
                volta()
                
                SOURCE_CODE = api_login()
            else :
                msg_error('\n >> Algo deu errado. Status: {}\n'.format(resposta.status_code))
                volta()
        else:
            msg_warning('\n>>> Ação cancelada.')
            volta()
  
    except requests.exceptions.Timeout:
        msg_warning('Tempo expirado')
        return None
    except:
        msg_error('\n >> Algo deu errado. Status: {}\n'.format(resposta.status_code))
        volta()
    
#---------------------------------
#       Início do programa 
#---------------------------------

clear()    #limpa a tela

show_top() #exibe logo
print('\nProcurando APs...\n')
lista_aps()

SOURCE_CODE = api_login() # solicita os parametros de login do usuário

while True:
    
    if SOURCE_CODE == 200:
        clear()
        device_info()
        menu_principal() 
        user_input = input('Opção: ')

        if user_input == '0':
            print(f'{bcolors.OKBLUE}"So long and thanks for all the fish."{bcolors.ENDC} - Desenvolvido por Rafael Mery')
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
            msg_warning('\nCarregando...')
            site_survey_wifi0()

        if user_input == '7': #Scan na rede 5ghz
            msg_warning('\nCarregando...')
            site_survey_wifi1()            

        if user_input == '8': # Lista clientes conectados 2.4
            msg_warning('\nCarregando...')
            clients_wifi0()            

        if user_input == '9': # Lista clientes conectados 5ghz
            msg_warning('\nCarregando...')
            clients_wifi1()       

        if user_input == '10': # Mostra SSIDs anunciados pelo AP
            msg_warning('\nCarregando...')
            ssid_list()   
            
        if user_input == '11': # Aplica Configurações
            apply_config()                  
            
    else:
        msg_error('\n>>> Falha no login: {}. Tente novamente.\n'.format(SOURCE_CODE))
        SOURCE_CODE = api_login()
