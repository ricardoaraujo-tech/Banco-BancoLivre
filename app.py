import json
import os
from flask import Flask, render_template, request, redirect, url_for
from models.cliente import validar_cpf

app = Flask(__name__)

arquivo_dados = 'data/dados_bancos.json'

def carregar_dados():
    if os.path.exists(arquivo_dados):
        with open(arquivo_dados, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'clientes': [], 'agencias': [], 'contas': []}

def salvar_dados(dados):
    with open(arquivo_dados, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

@app.route('/')
def index():
    dados = carregar_dados()
    clientes = dados.get('clientes', [])
    agencias = dados.get('agencias', [])
    contas = dados.get('contas', [])

    contas_positivas = [c for c in contas if c.get('saldo', 0) > 0]

    num_clientes = len(clientes)
    num_contas = len(contas)
    saldo_total = sum(c.get('saldo', 0) for c in contas)
    saldo_medio = (saldo_total / num_contas) if num_contas > 0 else 0.0

    if contas:
        maior_conta = max(contas, key=lambda c: c.get('saldo', 0))
        menor_conta = min(contas, key=lambda c: c.get('saldo', 0))
    else:
        maior_conta = None
        menor_conta = None

    dashboard = {
        'num_clientes': num_clientes,
        'num_contas': num_contas,
        'saldo_total': saldo_total,
        'saldo_medio': saldo_medio,
        'maior_conta': maior_conta,
        'menor_conta': menor_conta,
    }

    return render_template('index.html',
                           clientes=clientes,
                           agencias=agencias,
                           contas_positivas=contas_positivas,
                           dashboard=dashboard)

@app.route('/cadastrar_cliente', methods=['GET', 'POST'])
def cadastrar_cliente():
    if request.method == 'POST':
        nome = request.form.get('nome')
        cpf_digitado = request.form.get('cpf')
        telefone = request.form.get('telefone')
        endereco = request.form.get('endereco')

        if not validar_cpf(cpf_digitado):
            return render_template('cadastrar_cliente.html', erro="CPF inválido. Veriique o formato e tente novamente.")

        cpf = ''.join(filter(str.isdigit, cpf_digitado))
        dados = carregar_dados()

        if any(c.get('cpf') == cpf for c in dados.get('clientes', [])):
            return render_template('cadastrar_cliente.html', erro="CPF já cadastrado.")

        novo_cliente = {
            'nome': nome,
            'cpf': cpf,
            'telefone': telefone,
            'endereco': endereco
        }

        dados.setdefault('clientes', []).append(novo_cliente)
        salvar_dados(dados)

        return redirect(url_for('index'))

    return render_template('cadastrar_cliente.html')

@app.route('/cadastrar_conta', methods=['GET', 'POST'])
def cadastrar_conta():
    dados = carregar_dados()
    clientes = dados.get('clientes', [])
    agencias = dados.get('agencias', [])
    contas = dados.get('contas', [])

    if request.method == 'POST':
        numero = request.form.get('numero')
        cpf_digitado = request.form.get('cpf_titular')
        num_agencia = request.form.get('num_agencia')
        senha = request.form.get('senha')
        tipo = request.form.get('tipo')

        cpf_titular = ''.join(filter(str.isdigit, cpf_digitado))

        if not any(c.get('cpf') == cpf_titular for c in clientes):
            return render_template('cadastrar_conta.html', 
                                   erro="Cliente não cadastrado. Por favor, cadastre o cliente antes de criar a conta.", 
                                   agencias=agencias)

        if any(c.get('numero') == numero for c in contas):
            return render_template('cadastrar_conta.html', 
                                   erro="O número desta conta já está em uso.", 
                                   agencias=agencias)

        nova_conta = {
            "numero": numero,
            "cpf_titular": cpf_titular,
            "num_agencia": num_agencia,
            "senha": senha,
            "saldo": 0.0,
            "tipo": tipo
        }

        dados.setdefault('contas', []).append(nova_conta)
        salvar_dados(dados)
        
        return redirect(url_for('index'))

    return render_template('cadastrar_conta.html', clientes=clientes, agencias=agencias)

if __name__ == '__main__':
    print("Iniciando o servidor Flask...")
    app.run(debug=True)