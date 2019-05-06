import hashlib
import json
import requests

from urllib.parse import urlparse
from time import time
from uuid import uuid4
from flask import Flask, jsonify, request

class Blockchain(object):

    def __init__(self):
        """
            cadeia: lista de blocos armazenados na blockchain.
            transacoes_atuais: transacoes ainda nao foram adicionadas a um bloco.
            nos: lista de urls conectados ao servidor.
        """
        self.cadeia = []
        self.transacoes_atuais = []
        self.nos = set()
        # Iniciando a cadeia com um bloco raiz.
        self.novo_bloco(prova = 100, hash_ant = 1)
           
    def novo_bloco(self, prova, hash_ant = None):
        """
            Adiciona um novo bloco a cadeia.
            :param prova: prova do trabalho.
            :param hash_ant: hash do bloco anterior.
            :return bloco recem criado.
        """
        bloco = {
            'index' : len(self.cadeia) + 1,
            'timestamp' : time(),
            'transacoes' : self.transacoes_atuais,
            'prova' : prova,
            'hash_ant' : hash_ant or self.hash(self.cadeia[-1])
        }
        
        self.transacoes_atuais = []
        self.cadeia.append(bloco)
        return bloco

    def nova_transacao(self, remetente, destinatario, quantia):
        """
            Adiciona uma transacao a lista de transacoes.
            :param remetente: pessoa que enviou a quantia.
            :param destinatario: pessoa recebendos a quantia.
            :param quantia: quantia em questao.
            :return index do bloco na qual essa transacao sera adicionada.
        """
        self.transacoes_atuais.append({
            'remetente' : remetente, 
            'destinatario' : destinatario,
            'quantia' : quantia 
            })
        
        return int(self.ultimo_bloco['index'] + 1)

    def prova_trabalho(self, ult_prova):
        """
           Algoritmo de prova de trabalho.
        """
        prova = 0
        
        while self.validar_prova(ult_prova, prova) is False:
            prova += 1

        return prova

    @property
    def ultimo_bloco(self):
        return self.cadeia[-1]

    @staticmethod
    def hash(block):
        string_bloco = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(string_bloco).hexdigest()
    
    @staticmethod
    def validar_prova(ult_prova, prova):
        tentativa = f'{ult_prova}{prova}'.encode()
        hash_tentativa = hashlib.sha256(tentativa).hexdigest()
        return hash_tentativa[:4] == "0000"


    # Metodos de descentralizacao.
    def registrar_no(self, endereco):
        url_formatado = urlparse(endereco)
        self.nos.add(url_formatado.netloc)

    def validar_cadeia(self, cadeia):
        ultimo_bloco = cadeia[0]
        index_atual = 1

        while index_atual < len(cadeia):
            bloco = cadeia[index_atual]
            print(f'{ultimo_bloco}')
            print(f'{bloco}')
            print("\n--------------\n")

            if bloco['hash_ant'] != self.hash(ultimo_bloco):
                return False

            if not self.validar_prova(ultimo_bloco['prova'], bloco['prova']):
                return False

            ultimo_bloco = bloco
            index_atual += 1

        return True

    def resolver_conflitos(self):
        vizinhos = self.nos
        nova_cadeia = None

        tam_max = len(self.cadeia)

        for no in vizinhos:
            resposta = requests.get(f'http://{no}/cadeia')

            if resposta.status_code == 200:
                tam = resposta.json()['length']
                cadeia = resposta.json()['cadeia']

                if tam > tam_max and self.validar_cadeia(cadeia):
                   tam_max = tam
                   nova_cadeia = cadeia

        if nova_cadeia:
            self.cadeia = nova_cadeia
            return True

        return False
    

#Flask:
app = Flask(__name__)

node_identifier = str(uuid4()).replace('-', '')

blockchain = Blockchain()

@app.route('/mine', methods=['POST'])
def mine():
    no = request.args.get('endereco')
    
    ult_bloco = blockchain.ultimo_bloco
    ult_prova = ult_bloco['prova']
    prova = blockchain.prova_trabalho(ult_prova)
    
    blockchain.nova_transacao(
        remetente = "0",
        destinatario = no,
        quantia = 1)

    hash_ant = blockchain.hash(ult_bloco)
    bloco = blockchain.novo_bloco(prova, hash_ant)

    resposta = {
        'message' : "Novo bloco forjado",
        'index' : bloco['index'],
        'transacao' : bloco['transacoes'],
        'prova' : bloco['prova'],
        'hash_ant' : bloco['hash_ant']
    }
    return jsonify(resposta), 200

@app.route('/transaction/new', methods=['POST'])
def nova_transacao():
    try:
        remetente = request.args.get('remetente')
        destinatario = request.args.get('destinatario')
        quantia = request.args.get('quantia')
        index = blockchain.nova_transacao(remetente, destinatario, quantia)
        print(len(blockchain.transacoes_atuais))
        resposta = {'mensagem' : f'A transacao sera adicionada ao bloco {index}'}
    except KeyError:
        resposta = {'mensagem' : 'Deu errado'}
            
    #if not all(k in valores for k in requerido):
    #    return 'Faltando valores', 40
    
    return jsonify(resposta), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    print(len(blockchain.cadeia))
    response = {
        'cadeia' : blockchain.cadeia,
        'transacoes_atuais' : blockchain.transacoes_atuais
    }
    return jsonify(response), 200

@app.route('/nos/registrar', methods = ['POST'])
def registrar_no():
    nos = request.form('nos')
    if nos is None:
        return "Erro: forneça uma lista de nós válidas", 400

    for no in nos:
        blockchain.registrar_no(no)

    resposta = {
          'menssagem' : 'Novos nós foram adicionados',
          'total_nos' : list(blockchain.nos),
          }

    return jsonify(resposta), 201

@app.route('/nos/resolver', methods=['GET'])
def consensus():
    
    substituido = blockchain.resolver_conflitos()

    if substituido:
        resposta = {
            'messagem' : 'Nossa cadeia foi substituída',
            'nova_cadeia' : blockchain.cadeia,
            }

    else:
        resposta = {
            'menssagem': 'Nossa cadeia esta atualizada',
            'cadeia': blockchain.cadeia
        }

    return jsonify(resposta), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)