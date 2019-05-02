from tkinter import *
from functools import partial
import json
import requests
import pickle
import hashlib
from tkinter import messagebox
from blockchain import Blockchain

class FlipWallter:
    def __init__(self, master=None):
        self.janela = Tk()
        self.minhas_etiquetas = {}
        self.contatos = {}
        self.blockchain = Blockchain()

        def sincronizar():
            r = requests.get('http://localhost:5000/chain')
            r = r.json()
            self.blockchain.cadeia = r['cadeia']
            self.blockchain.transacoes_atuais = r['transacoes_atuais']
        
        def atualizarSaldoDisponivel():
            saldo_disponivel = 0
            
            for bloco in self.blockchain.cadeia:
                for transacao in bloco:
                    for etiqueta in self.minhas_etiquetas:
                        if transacao['destinatario'] == self.minhas_etiquetas[etiqueta]:
                            saldo_disponivel += transacao['quantia']
            
            return saldo_disponivel
        
        def atualizarSaldoPendente():
            saldo_pendente = 0

            for transacao in self.blockchain.transacoes_atuais:
                for etiqueta in self.minhas_etiquetas:
                    if transacao['destinatario'] == self.minhas_etiquetas[etiqueta]:
                        saldo_pendente += transacao['quantia']
            
            return saldo_pendente
        
        def atualizar_saldos(lblSaldoDisponivel, lblSaldoPendente, lblSaldoTotal):
            saldo_disponivel = 0
            
            for bloco in self.blockchain.cadeia:
                for transacao in bloco:
                    for etiqueta in self.minhas_etiquetas:
                        if transacao['destinatario'] == self.minhas_etiquetas[etiqueta]:
                            saldo_disponivel += transacao['quantia']
            
            lblSaldoDisponivel['text'] = "$FC " + str(saldo_disponivel)

            saldo_pendente = 0

            for transacao in self.blockchain.transacoes_atuais:
                for etiqueta in self.minhas_etiquetas:
                    if transacao['destinatario'] == self.minhas_etiquetas[etiqueta]:
                        saldo_pendente += transacao['quantia']
            
            lblSaldoPendente['text'] = "$FC " + str(saldo_pendente)

            lblSaldoTotal['text'] = "$FC " + str(saldo_disponivel + saldo_pendente) 


        def janelaNovoHash():
            hash_window = Tk()
            hash_window.title("Adicionar um novo hash")
            
            lbletiqueta = Label(hash_window, text="Etiqueta:")
            lbletiqueta.place(x = 10, y = 10)
            
            etiquetaE = Entry(hash_window, width=64)
            etiquetaE.place(x = 70, y = 10)
            
            lblnew_hash = Label(hash_window, text="Hash criado:")
            lblnew_hash.place(x = 10, y = 40)

            new_hash = hashlib.sha256()

            lblhash_str = Label(hash_window, text=new_hash.hexdigest())
            lblhash_str.place(x = 100, y = 40)
            
            btnadicionarHash = Button(hash_window, text="adicionar hash")
            btnadicionarHash['command'] = partial(adicionarNovoHash, hash_window, etiquetaE, new_hash)
            btnadicionarHash.place(x = 473, y = 70)
            
            hash_window.geometry("600x100+200+100")
            hash_window.mainloop()

        def adicionarNovoHash(hash_window,etiqueta, hash):
            if etiqueta.get() == '':
                messagebox.showerror("Erro", "A etiqueta está vazia!")
            else:
                self.minhas_etiquetas[etiqueta] = hash
                hash_window.destroy()
       
        #def adicionarNovoHash(etiqueta, hash):
        #    self.minhas_etiquetas[etiqueta] = hash

        def registrar():
            nos = {
                'nos' : ['http://localhost:5001/']
            }

            resposta = requests.post('http://localhost:5000/nos/registrar', params = nos)
            print(resposta.text)

        def enviar(destinatarioE, etiquetaE, quantiaE):
            destinatario = None

            if etiquetaE.get() != '':
                
                if destinatarioE.get() != '':

                    if etiquetaE.get() in self.contatos:
                        destinatario = self.contatos[etiquetaE.get()]
                    
                    else:
                        self.contatos[etiquetaE.get()] = destinatarioE.get()
                        destinatario = destinatarioE
                else:
                    
                    if etiquetaE.get() in self.contatos:
                        destinatario = self.contatos[etiquetaE.get()]
                    
                    else:
                        messagebox.showerror("Erro", "Não existe nenhum endereço com esta etiqueta!")
                        return
            else:
                if destinatarioE.get() == '':
                    messagebox.showerror("Erro", "Especifique um endereço!")
                    return
                else:
                    destinatario = destinatarioE.get()
            
            if quantiaE.get() == '':
                messagebox.showerror("Erro", "Especifique a quantia a ser enviada!")
                return

            remetente = "LocalHost"
            quantia = float(quantiaE.get())
            transacao = {
                    'remetente' : remetente,
                    'destinatario' : destinatario,
                    'quantia' : quantia
            }
            resposta = requests.get('http://localhost:5000/transaction/new', params=transacao)
            print(resposta.text)

        def janelaHistorico():
            janelaHistorico = Tk()
            janelaHistorico.title("Histórico de transações")

            scrollbar = Scrollbar(janelaHistorico)
            scrollbar.pack(side = RIGHT, fill = Y)

            lista_transacoes = Listbox(janelaHistorico, width=73, height=30)
            lista_transacoes.place(x = 0, y = 0)

            lista_transacoes.insert(END, "DATA           REMETENTE             DESTINATÁRIO         QUANTIA")

            for i in range(200):
                lista_transacoes.insert(END, i)

            """
            for bloco in self.blockchain.cadeia:
                data = bloco['timestamp']
                transacoes = bloco.get('transacoes')
                remetente = transacoes[1]
                destinatario = bloco['transacoes']['destinatario']
                quantia = bloco['transacoes']['quantia']
                string = data + " " + remetente + " " + destinatario + " " + quantia
            
                lista_transacoes.insert(END, )
            """

            lista_transacoes.config(yscrollcommand=scrollbar.set)
            scrollbar.config(command=lista_transacoes.yview)

            janelaHistorico.resizable(0,0)
            janelaHistorico.geometry("600x450+200+100")
            janelaHistorico.mainloop()

        sincronizar()

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
        atualizarSaldos['command'] = partial(atualizar_saldos, saldo_disponivel, saldo_pendente, saldo_total)
        atualizarSaldos.place(x = 468, y = 140)

        atualizar_saldos(saldo_disponivel, saldo_pendente, saldo_total)

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
        btnenviar['command'] = partial(enviar,destinatarioE, etiquetaE, quantiaE)
        btnenviar.place(x = 537, y = 350)

        line2 = Label(self.janela, text="------------------------------------------------------------------------------------------------------------------------------------------------")
        line2.place(x = 10, y = 380)

        btnHistorico = Button(self.janela, text="Histórico")
        btnHistorico['command'] = partial(janelaHistorico)
        btnHistorico.place(x = 10, y = 410)

        btngerar_hash = Button(self.janela, text="gerar novo hash")
        btngerar_hash['command'] = partial(janelaNovoHash)
        btngerar_hash.place(x = 463, y = 410)

        self.janela.title("FlipWallet")
        self.janela.geometry("600x450+200+100")
        self.janela.resizable(0,0)  
        self.janela.mainloop()

FlipWallter()