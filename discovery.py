#!/usr/bin/env python

# Ferramenta para teste de resposta Multicast
# Rodrigo Ramiro - rodrigo.ramiro@intebras.com.br
# Alterou? Contribua! :)
#Alterações para python3 01/2023 - Rafael Mery

import time
import socket
import struct
#import binascii
import time
import json
from functools import reduce

MCAST_GRP = '233.89.188.1' 
MCAST_PORT = 10001
data_itb = struct.pack("BBBB", 0x49, 0x54, 0x42, 0x53)

def binaryToDevice(data):
        lst = []
        for ch in data:
            hv = hex(ch).replace('0x', '')
            if len(hv) == 1:
                hv = '0'+hv
            lst.append(hv)
            
        pos = 0;
        posEnd = 0;
        tam = 0;
        device = {}
        
        #COD
        posEnd = 4+pos;
        device['cod'] = reduce(lambda x,y:x+y, lst)[pos:posEnd]
        pos=posEnd;
        
        #MAC Origem
        posEnd = 12+pos;
        device['mac'] = reduce(lambda x,y:x+y, lst)[pos:posEnd]
        macFormat = ""
        for i in range(0,12,2):
            macFormat += device['mac'][i:i+2] + ":"
        device['mac'] = macFormat[:-1].upper()
        pos=posEnd;

        #MAC destino
        posEnd = 12+pos;
        device['mac_source'] = reduce(lambda x,y:x+y, lst)[pos:posEnd]
        macFormat = ""
        for i in range(0,12,2):
            macFormat += device['mac_source'][i:i+2] + ":"
        device['mac_source'] = macFormat[:-1].upper()
        pos=posEnd;

        #Modelo
        posEnd = 4+pos;
        tam = int(reduce(lambda x,y:x+y, lst)[pos:posEnd],16)*2
        pos=posEnd
            
        posEnd = tam+pos
        device['model'] = bytes.fromhex(reduce(lambda x,y:x+y, lst)[pos:posEnd]).decode()
        pos=posEnd
        #print(device['model'])
        
        #Versao
        posEnd = 4+pos;
        tam = int(reduce(lambda x,y:x+y, lst)[pos:posEnd],16)*2
        pos=posEnd;
            
        posEnd = tam+pos;
        device['version'] = bytes.fromhex(reduce(lambda x,y:x+y, lst)[pos:posEnd]).decode()
        pos=posEnd;
        
        #Porta
        posEnd = 4+pos;
        device['port'] = int(reduce(lambda x,y:x+y, lst)[pos:posEnd],16)
        pos=posEnd;
        
        #Description
        posEnd = 4+pos;
        pos=posEnd;
        
        posEnd = 16+pos;
        device['description'] = bytes.fromhex(reduce(lambda x,y:x+y, lst)[pos:posEnd]).decode()
        pos=posEnd;
        
        return device

# Uma vez
def find_aps():
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
  sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
  sock.sendto(data_itb, (MCAST_GRP, MCAST_PORT))
  #sock.sendto(data_dlb, (MCAST_GRP, MCAST_PORT))
  # sock.setblocking(0)
  sock.settimeout(5)
  find = {
    "aps":[]
    }
  while True:
    try:
      #print (sock.recv(10240))
      # sock.sendto(data_itb, (MCAST_GRP, MCAST_PORT))
      data, address = sock.recvfrom(1024)
      #print 'received %s bytes from %s ' % (len(data), address)
      dados = binaryToDevice(data)
      find['aps'].append({
        "address": address,
        "mac": dados['mac'],
        "version": dados['version'],
        "description":dados['description'],        
        "model": dados['model']
        })
      #json.dumps(find)
      #print(dados['description'])
      #print ('received %s bytes from %s : %s' % (len(data), address, binaryToDevice(data)))
      time.sleep(1)   
    except socket.timeout:   
      #print(find) 
      return json.dumps(find)
    except socket.error:
      time.sleep(1)

# Loop Continuo
# def main():
#   sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
#   sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
#   sock.sendto(data_itb, (MCAST_GRP, MCAST_PORT))
#   #sock.sendto(data_dlb, (MCAST_GRP, MCAST_PORT))
#   sock.setblocking(0)
#   while True:
#     try:
# 	   #print sock.recv(10240)
# 	   sock.sendto(data_itb, (MCAST_GRP, MCAST_PORT))
# 	   data, address = sock.recvfrom(1024)
# 	   #print 'received %s bytes from %s ' % (len(data), address)
# 	   print 'received %s bytes from %s : %s' % (len(data), address, binaryToDevice(data))
# 	   time.sleep(1)
#     except socket.error:
#         time.sleep(1)

#if __name__ == '__main__':
#  main()