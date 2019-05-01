from tkinter import *
from functools import partial
import json
import requests
import pickle
import hashlib
from tkinter import messagebox
# from .blockchain import Blockchain

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
        minhas_etiquetas[etiqueta] = hash
        hash_window.destroy()

def adicionarNovoHash(etiqueta, hash):
    minhas_etiquetas[etiqueta] = hash

# Talvez não seja necessário
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

            if etiquetaE.get() in etiquetas_contatos:
                destinatario = etiquetas_contatos[etiquetaE.get()]
            
            else:
                etiquetas_contatos[etiquetaE.get()] = destinatarioE.get()
                destinatario = destinatarioE
        else:
            
            if etiquetaE.get() in etiquetas_contatos:
                destinatario = etiquetas_contatos[etiquetaE.get()]
            
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

def solicitar_pagamento():
    return 0

########################################################################################
janela = Tk()
janela.title("FlipWallet")

minhas_etiquetas = {}
etiquetas_contatos = {}

# cadeia = Blockchain()
########################################################################################

""" A distância entre os labels precisa ser
    no mínimo 30 pixels.
"""

saldo = Label(janela, text="Saldos")
saldo.place(x = 10, y = 20)

disponivel = Label(janela, text="Disponível: ")
disponivel.place(x = 10, y = 50)

pendente = Label(janela, text="Pendente: ")
pendente.place(x = 10, y = 80)

total = Label(janela, text="Total: ")
total.place(x = 10, y = 110)

line1 = Label(janela, text="------------------------------------------------------------------------------------------------------------------------------------------------")
line1.place(x = 10, y = 140)

lblenviar = Label(janela, text="Enviar")
lblenviar.place(x = 10, y = 170)

destinatario = Label(janela, text="Destinatário: ")
destinatario.place(x = 10, y = 200)

destinatarioE = Entry(janela, width=53)
destinatarioE.place(x = 160, y = 200)

etiqueta_enviar = Label(janela, text="Etiqueta: ")
etiqueta_enviar.place(x = 10, y = 230)

etiquetaE = Entry(janela, width=53)
etiquetaE.place(x = 160, y = 230)

quantia_enviar = Label(janela, text="Quantia: $FC")
quantia_enviar.place(x = 10, y = 260)

quantiaE = Entry(janela, width=53)
quantiaE.place(x = 160, y = 260)

comissao = Label(janela, text="Comissão da transação: ")
comissao.place(x = 10, y = 290)

comissaoE = Entry(janela, width=53)
comissaoE.place(x = 160, y = 290)

btnenviar = Button(janela, width=3, text="Enviar")
btnenviar['command'] = partial(enviar, destinatarioE, etiquetaE, quantiaE)
btnenviar.place(x = 537, y = 320)

line2 = Label(janela, text="------------------------------------------------------------------------------------------------------------------------------------------------")
line2.place(x = 10, y = 350)

receber = Label(janela, text="Receber")
receber.place(x = 10, y = 380)

etiqueta_receber = Label(janela, text="Etiqueta:")
etiqueta_receber.place(x = 10, y = 410)

etiquetaR = Entry(width=61)
etiquetaR.place(x = 95, y = 410)

quantia_receber = Label(janela, text="Quantia: $FC")
quantia_receber.place(x = 10, y = 440)

quantiaR = Entry(width=61)
quantiaR.place(x = 95, y = 440)

mensagem = Label(janela, text="Mensagem:")
mensagem.place(x = 10, y = 470)

mensagemR = Entry(width=61)
mensagemR.place(x = 95, y = 470)

btnreceber = Button(janela, width=13, text="solicitar pagamento", command=solicitar_pagamento)
btnreceber.place(x = 456, y = 500)

historio = Label(janela, text="Histórico de pagamentos:")

line3 = Label(janela, text="------------------------------------------------------------------------------------------------------------------------------------------------")
line3.place(x = 10, y = 530)

btnhistorico = Button(janela, text="Histórico")
btnhistorico.place(x = 10, y = 560)

btngerar_hash = Button(janela, text="gerar novo hash")
btngerar_hash['command'] = partial(janelaNovoHash)
btngerar_hash.place(x = 463, y = 560)

janela.geometry("600x600+200+100")

janela.mainloop()