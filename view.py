from tkinter import *
from functools import partial
from tkinter import messagebox
from blockchain import Blockchain
from time import time
from datetime import date
import json
import requests
import pickle
import hashlib
import socket
import pickle

class User:
    def __init__(self):
        self.etiquetas = {}
        self.contatos = {}
        self.saldo_disponivel = 0
        self.saldo_pendente = 0
        self.transacoes = {}
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
        
        while index < len(self.blockchain.cadeia):
            bloco = self.blockchain.cadeia[index]
            for transacao in bloco['transacoes']:
                if transacao['destinatario'] in self.usuario.etiquetas.values():
                    self.usuario.saldo_disponivel += float(transacao['quantia'])
                    self.usuario.transacoes[bloco['timestamp']] = transacao
                if transacao['remetente'] in self.usuario.etiquetas.values():
                    self.usuario.saldo_disponivel -= float(transacao['quantia'])
                    self.usuario.transacoes[bloco['timestamp']] = transacao
            index += 1

        self.usuario.index_atual = index
    
    def atualizarSaldoPendente(self):
        for transacao in self.blockchain.transacoes_atuais:
            if transacao['destinatario'] == self.usuario.etiquetas.values():
                self.usuario.saldo_pendente += transacao['quantia']
            if transacao['remetente'] == self.usuario.etiquetas.values():
                self.usuario.saldo_pendente -= transacao['quantia']
    
    def atualizar_saldos(self, lblSaldoDisponivel, lblSaldoPendente, lblSaldoTotal):
        self.sincronizar()
        self.atualizarSaldoDisponivel()
        self.atualizarSaldoPendente()
        lblSaldoDisponivel['text'] = "$FC " + str(self.usuario.saldo_disponivel)
        lblSaldoPendente['text'] = "$FC " + str(self.usuario.saldo_pendente)
        lblSaldoTotal['text'] = "$FC " + str(self.usuario.saldo_disponivel + self.usuario.saldo_pendente) 

    def janelaNovoHash(self):
        hash_window = Tk()
        hash_window.title("Adicionar um novo hash")
        
        lbletiqueta = Label(hash_window, text="Etiqueta:")
        lbletiqueta.place(x = 10, y = 10)
        
        etiquetaE = Entry(hash_window, width=66)
        etiquetaE.place(x = 70, y = 10)
        
        lblnew_hash = Label(hash_window, text="Endereço gerado:")
        lblnew_hash.place(x = 10, y = 40)

        t = str(time())
        t = t.encode('utf-8')
        new_hash = hashlib.sha256(t).hexdigest()

        lblhash_str = Label(hash_window, text=new_hash)
        lblhash_str.place(x = 120, y = 40)
        
        btnadicionarHash = Button(hash_window, text="adicionar hash")
        btnadicionarHash['command'] = partial(self.adicionarNovoHash, hash_window, etiquetaE, new_hash)
        btnadicionarHash.place(x = 493, y = 70)
        
        hash_window.geometry("625x100+200+100")
        hash_window.mainloop()

    def adicionarNovoHash(self, hash_window,etiqueta, hash):
        if etiqueta.get() == '':
            messagebox.showerror("Erro", "A etiqueta está vazia!")
            hash_window.lift()
        else:
            self.usuario.etiquetas[etiqueta] = hash
            hash_window.destroy()
    
    def registrar(self):
        nos = {
            'nos' : ['http://localhost:5000/']
        }

        resposta = requests.post('http://localhost:5000/nos/registrar', params = nos)
        print(resposta.text)

    def minerar(self):
        endereco = { 'endereco' : self.usuario.etiquetas['meuEndereco'] }
        resposta = requests.post('http://localhost:5000/mine', params=endereco)
        resposta = resposta.json()
        if resposta['message'] == 'Novo bloco forjado':
            messagebox.showinfo("Recompesa", "Você ganhou 1 $FC")

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

        yscrollbar = Scrollbar(janelaHistorico)
        yscrollbar.pack(side = RIGHT, fill = Y)

        lista_transacoes = Listbox(janelaHistorico, width=73, height=30)
        lista_transacoes.place(x = 0, y = 0)

        for key in self.usuario.transacoes:
            data = date.isoformat(date.fromtimestamp(key))
            lista_transacoes.insert(END, " DATA: " + data)

            remetente = self.usuario.transacoes[key]['remetente']
            lista_transacoes.insert(END, " REMETENTE: " + remetente)
            
            destinatario = self.usuario.transacoes[key]['destinatario']
            lista_transacoes.insert(END, " DESTINATÁRIO: " + destinatario)

            quantia = str(self.usuario.transacoes[key]['quantia'])
            lista_transacoes.insert(END, " QUANTIA: " + quantia)

            lista_transacoes.insert(END, "\n")

        lista_transacoes.config(yscrollcommand=yscrollbar.set)
        yscrollbar.config(command=lista_transacoes.yview)

        janelaHistorico.resizable(0,0)
        janelaHistorico.geometry("601x450+200+100")
        janelaHistorico.mainloop()
    
    def janelaMeusEnderecos(self):
        janela_meus_end = Tk()
        janela_meus_end.title("Meus endereços")

        yscrollbar = Scrollbar(janela_meus_end)
        yscrollbar.pack(side = RIGHT, fill = Y)

        enderecos = Listbox(janela_meus_end, width=73, height=30)
        enderecos.place(x = 0, y = 0)

        for key in self.usuario.etiquetas:
            enderecos.insert(END, key + ": " + self.usuario.etiquetas[key])

        janela_meus_end.config(yscrollcommand=yscrollbar.set)
        yscrollbar.config(command=janela_meus_end.yview)

        janela_meus_end.resizable(0,0)
        janela_meus_end.geometry("601x450+200+100")
        janela_meus_end.mainloop()

    def inicializarJanela(self): 
        saldo = Label(self.janela, text="Saldos")
        saldo.place(x = 10, y = 20)

        disponivel = Label(self.janela, text="Disponível: ")
        disponivel.place(x = 10, y = 50)

        saldo_disponivel = Label(self.janela)
        saldo_disponivel.place(x = 540, y = 50)

        pendente = Label(self.janela, text="Pendente: ")
        pendente.place(x = 10, y = 80)

        saldo_pendente = Label(self.janela)
        saldo_pendente.place(x = 540, y = 80)

        total = Label(self.janela, text="Total: ")
        total.place(x = 10, y = 110)

        saldo_total = Label(self.janela)
        saldo_total.place(x = 540, y = 110)

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

        btngerar_hash = Button(self.janela, text="Gerar endereço")
        btngerar_hash['command'] = partial(self.janelaNovoHash)
        btngerar_hash.place(x = 469, y = 410)

        btnminerar = Button(self.janela, text='Minerar')
        btnminerar['command'] = partial(self.minerar)
        btnminerar.place(x = 95, y = 410)

        btnmeus_enderecos = Button(self.janela, text="Meus endereços")
        #btnmeus_enderecos['command'] = partial(self.janelaMeusEnderecos())
        btnmeus_enderecos.place(x = 341, y = 410)

        self.janela.title("FlipWallet")
        self.janela.geometry("600x450+200+100")
        self.janela.resizable(0,0)  
        self.janela.mainloop()

    def serializar(self):
        pickle.dump(self.blockchain,open('blockchain.pkl','wb'))
        pickle.dump(self.usuario,open('user.pkl','wb'))

######################deserializacao#########################
try:
    bc = pickle.load(open('blockchain.pkl','rb'))
    user = pickle.load(open('user.pkl','rb'))
    FlipWallter(user,bc)
except FileNotFoundError:
    FlipWallter()