import requests
import json

class Protocolo():
    
    def mine(self):
        r = requests.get('http://localhost:5000/mine')
        r = r.json()
        print(r)

    def nova_transacao(self):
        remetente = input("Remetente: ")
        destinatario = input("Destinatario: ")
        quantia = float(input("Quantia: "))

        transacao = {
            'remetente' : remetente,
            'destinatario' : destinatario,
            'quantia' : quantia
            }
        # transacao = jsonify(transacao), 200
        resposta = requests.get('http://localhost:5000/transaction/new', params=transacao)
        print(resposta)


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
