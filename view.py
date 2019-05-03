from tkinter import *
from functools import partial
import json
import requests
import pickle
import hashlib
from tkinter import messagebox
from blockchain import Blockchain
from time import time
import socket

class User:
    def __init__(self):
        self.etiquetas = {}
        self.contatos = {}
        self.saldo_disponivel = 0
        self.saldo_pendente = 0
        self.transacoes = []
        self.index_atual = 0

        t = str(time())
        t = t.encode('utf-8')
        self.etiquetas['meuEndereco'] = hashlib.sha256(t).hexdigest()


class FlipWallter:
    def __init__(self, user=None, blockchain=None):
        self.janela = Tk()
        self.usuario = user or User()
        self.blockchain = blockchain or Blockchain()
        
        if not blockchain:
            self.sincronizar()
        if not user:
            self.atualizarSaldoDisponivel()
            self.atualizarSaldoPendente()

        self.inicializarJanela()
        
    def sincronizar(self):
        r = requests.get('http://localhost:5000/chain')
        r = r.json()
        self.blockchain.cadeia = r['cadeia']
        self.blockchain.transacoes_atuais = r['transacoes_atuais']
        
    def atualizarSaldoDisponivel(self):
        index = self.usuario.index_atual
        
        for i in range(index, len(self.blockchain.cadeia)):
            bloco = self.blockchain.cadeia[i]
            for transacao in bloco['transacoes']:
                if transacao['destinatario'] in self.usuario.etiquetas.values():
                    self.usuario.saldo_disponivel += float(transacao['quantia'])
                if transacao['remetente'] in self.usuario.etiquetas.values():
                    self.usuario.saldo_disponivel -= float(transacao['quantia'])
    
    def atualizarSaldoPendente(self):
        for transacao in self.blockchain.transacoes_atuais:
            if transacao['destinatario'] == self.usuario.etiquetas.values():
                self.usuario.saldo_pendente += transacao['quantia']
            if transacao['remetente'] == self.usuario.etiquetas.values():
                self.usuario.saldo_pendente -= transacao['quantia']
    
    def atualizar_saldos(self, lblSaldoDisponivel, lblSaldoPendente, lblSaldoTotal):
        lblSaldoDisponivel['text'] = "$FC " + str(self.usuario.saldo_disponivel)
        lblSaldoPendente['text'] = "$FC " + str(self.usuario.saldo_pendente)
        lblSaldoTotal['text'] = "$FC " + str(self.usuario.saldo_disponivel + self.usuario.saldo_pendente) 


    def janelaNovoHash(self):
        hash_window = Tk()
        hash_window.title("Adicionar um novo hash")
        
        lbletiqueta = Label(hash_window, text="Etiqueta:")
        lbletiqueta.place(x = 10, y = 10)
        
        etiquetaE = Entry(hash_window, width=64)
        etiquetaE.place(x = 70, y = 10)
        
        lblnew_hash = Label(hash_window, text="Hash criado:")
        lblnew_hash.place(x = 10, y = 40)

        new_hash = hashlib.sha256(str(time()) + str(socket.gethostbyname(socket.gethostname()))).hexdigest()

        lblhash_str = Label(hash_window, text=new_hash)
        lblhash_str.place(x = 100, y = 40)
        
        btnadicionarHash = Button(hash_window, text="adicionar hash")
        btnadicionarHash['command'] = partial(self.adicionarNovoHash, hash_window, etiquetaE, new_hash)
        btnadicionarHash.place(x = 473, y = 70)
        
        hash_window.geometry("600x100+200+100")
        hash_window.mainloop()

    def adicionarNovoHash(self, hash_window,etiqueta, hash):
        if etiqueta.get() == '':
            messagebox.showerror("Erro", "A etiqueta está vazia!")
        else:
            self.usuario.etiquetas[etiqueta] = hash
            hash_window.destroy()
    
    #def adicionarNovoHash(etiqueta, hash):
    #    self.minhas_etiquetas[etiqueta] = hash
    def registrar(self):
        nos = {
            'nos' : ['http://localhost:5000/']
        }

        resposta = requests.post('http://localhost:5000/nos/registrar', params = nos)
        print(resposta.text)

    def minerar(self):
        endereco = { "endereco" : self.usuario.etiquetas['meuEndereco'] }
        resposta = requests.get('http://localhost:5000/mine', params=endereco)

    def enviar(self, destinatarioE, etiquetaE, quantiaE):
        destinatario = None

        if etiquetaE.get() != '':
            
            if destinatarioE.get() != '':

                if etiquetaE.get() in self.usuario.contatos.keys():
                    destinatario = self.usuario.contatos[etiquetaE.get()]
                
                else:
                    self.usuario.contatos[etiquetaE.get()] = destinatarioE.get()
                    destinatario = destinatarioE.get()
            else:
                
                if etiquetaE.get() in self.usuario.contatos.keys():
                    destinatario = self.usuario.contatos[etiquetaE.get()]
                
                else:
                    messagebox.showerror("Erro", "Não existe nenhum endereço com esta etiqueta!")
                    return
        else:
            if destinatarioE.get() == '':
                messagebox.showerror("Erro", "Especifique um destinatário!")
                return
            else:
                destinatario = destinatarioE.get()
        
        if quantiaE.get() == '':
            messagebox.showerror("Erro", "Especifique a quantia a ser enviada!")
            return

        remetente = self.usuario.etiquetas['meuEndereco']
        quantia = float(quantiaE.get())
        transacao = {
                'remetente' : remetente,
                'destinatario' : destinatario,
                'quantia' : quantia
        }
        resposta = requests.post('http://localhost:5000/transaction/new', params=transacao)
        if resposta['mensagem'] != 'Deu errado':
            self.usuario.transacoes.append(transacao)

    def janelaHistorico(self):
        janelaHistorico = Tk()
        janelaHistorico.title("Histórico de transações")

        scrollbar = Scrollbar(janelaHistorico)
        scrollbar.pack(side = RIGHT, fill = Y)

        lista_transacoes = Listbox(janelaHistorico, width=73, height=30)
        lista_transacoes.place(x = 0, y = 0)

        lista_transacoes.insert(END, "DATA           REMETENTE             DESTINATÁRIO         QUANTIA")

        """for transacao in self.usuario.:
            data = bloco['timestamp']
            transacoes = bloco.get('transacoes')
            remetente = transacoes[1]
            destinatario = bloco['transacoes']['destinatario']
            quantia = bloco['transacoes']['quantia']
            string = data + " " + remetente + " " + destinatario + " " + quantia
        
            lista_transacoes.insert(END, )

        lista_transacoes.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=lista_transacoes.yview)

        janelaHistorico.resizable(0,0)
        janelaHistorico.geometry("600x450+200+100")
        janelaHistorico.mainloop()
        """
        ################################################################# Interface ###################################################################
    def inicializarJanela(self): 
        saldo = Label(self.janela, text="Saldos")
        saldo.place(x = 10, y = 20)

        disponivel = Label(self.janela, text="Disponível: ")
        disponivel.place(x = 10, y = 50)

        saldo_disponivel = Label(self.janela)
        saldo_disponivel.place(x = 550, y = 50)

        pendente = Label(self.janela, text="Pendente: ")
        pendente.place(x = 10, y = 80)

        saldo_pendente = Label(self.janela)
        saldo_pendente.place(x = 550, y = 80)

        total = Label(self.janela, text="Total: ")
        total.place(x = 10, y = 110)

        saldo_total = Label(self.janela)
        saldo_total.place(x = 550, y = 110)

        atualizarSaldos = Button(self.janela, text="Atualizar saldos")
        atualizarSaldos['command'] = partial(self.atualizar_saldos, saldo_disponivel, saldo_pendente, saldo_total)
        atualizarSaldos.place(x = 468, y = 140)

        self.atualizar_saldos(saldo_disponivel, saldo_pendente, saldo_total)

        line1 = Label(self.janela, text="------------------------------------------------------------------------------------------------------------------------------------------------")
        line1.place(x = 10, y = 170)

        lblenviar = Label(self.janela, text="Enviar")
        lblenviar.place(x = 10, y = 200)

        destinatario = Label(self.janela, text="Destinatário: ")
        destinatario.place(x = 10, y = 230)

        destinatarioE = Entry(self.janela, width=53)
        destinatarioE.place(x = 160, y = 230)

        etiqueta_enviar = Label(self.janela, text="Etiqueta: ")
        etiqueta_enviar.place(x = 10, y = 260)

        etiquetaE = Entry(self.janela, width=53)
        etiquetaE.place(x = 160, y = 260)

        quantia_enviar = Label(self.janela, text="Quantia: $FC")
        quantia_enviar.place(x = 10, y = 290)

        quantiaE = Entry(self.janela, width=53)
        quantiaE.place(x = 160, y = 290)

        comissao = Label(self.janela, text="Comissão da transação: ")
        comissao.place(x = 10, y = 320)

        comissaoE = Entry(self.janela, width=53)
        comissaoE.place(x = 160, y = 320)

        btnenviar = Button(self.janela, width=3, text="Enviar")
        btnenviar['command'] = partial(self.enviar,destinatarioE, etiquetaE, quantiaE)
        btnenviar.place(x = 537, y = 350)

        line2 = Label(self.janela, text="------------------------------------------------------------------------------------------------------------------------------------------------")
        line2.place(x = 10, y = 380)

        btnHistorico = Button(self.janela, text="Histórico")
        btnHistorico['command'] = partial(self.janelaHistorico)
        btnHistorico.place(x = 10, y = 410)

        btngerar_hash = Button(self.janela, text="gerar novo hash")
        btngerar_hash['command'] = partial(self.janelaNovoHash)
        btngerar_hash.place(x = 463, y = 410)

        self.janela.title("FlipWallet")
        self.janela.geometry("600x450+200+100")
        self.janela.resizable(0,0)  
        self.janela.mainloop()

FlipWallter()