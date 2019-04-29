import requests
import json
from flask import Flask, jsonify, request

class Protocolo():
    
    def mine(self):
        r = requests.get('http://localhost:5000/mine')
        r = r.json()
        print(r)

    def nova_transacao(self):
        """remetente = input("Remetente: ")
        destinatario = input("Destinatario: ")
        quantia = float(input("Quantia: "))"""

        transacao = {
            'remetente' : "ahsdfkajshdflasjdflsdjf",
            'destinatario' : "endereco",
            'quantia' : 5
            }
        resposta = requests.post('http://localhost:5000/transaction/new', data = transacao)
        print(resposta.text)


    def visualizar_cadeia(self):
        r = requests.get('http://localhost:5000/chain')
        r = r.json()
        print(r)

o = Protocolo()
while(True):
	i = input()
	if i == '1':
		o.mine()
	elif i == '2':
		o.nova_transacao()
	elif i == '3':
		o.visualizar_cadeia()
