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
    """Página principal com Dashboard, Listagens e Sistema de Busca Unificada."""
    dados = carregar_dados()
    clientes = dados.get('clientes', [])
    agencias = dados.get('agencias', [])
    contas = dados.get('contas', [])

    # 1. Captura o que o utilizador digitou na barra de pesquisa (se existir)
    termo_busca = request.args.get('busca', '').lower().strip()

    # 2. Se houver pesquisa, filtra as listas
    if termo_busca:
        # Filtra clientes se o nome ou CPF contiverem o termo
        clientes = [c for c in clientes if termo_busca in c.get('nome', '').lower() or termo_busca in c.get('cpf', '')]
        # Filtra contas se o número da conta ou CPF do titular contiverem o termo
        contas_filtradas = [c for c in contas if termo_busca in str(c.get('numero', '')) or termo_busca in c.get('cpf_titular', '')]
    else:
        contas_filtradas = contas

    contas_positivas = [c for c in contas_filtradas if c.get('saldo', 0) > 0]

    # 3. Matemática do Dashboard 
    num_clientes = len(dados.get('clientes', []))
    num_contas = len(dados.get('contas', []))
    saldo_total = sum(c.get('saldo', 0) for c in dados.get('contas', []))
    saldo_medio = (saldo_total / num_contas) if num_contas > 0 else 0.0
    
    if dados.get('contas'):
        maior_conta = max(dados.get('contas'), key=lambda c: c.get('saldo', 0))
        menor_conta = min(dados.get('contas'), key=lambda c: c.get('saldo', 0))
    else:
        maior_conta = None
        menor_conta = None

    dashboard = {
        'num_clientes': num_clientes,
        'num_contas': num_contas,
        'saldo_total': saldo_total,
        'saldo_medio': saldo_medio,
        'maior_conta': maior_conta,
        'menor_conta': menor_conta
    }

    return render_template('index.html', 
                           clientes=clientes, 
                           agencias=agencias, 
                           contas_positivas=contas_positivas, 
                           dashboard=dashboard,
                           termo_busca=termo_busca)

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

@app.route('/cadastrar_agencia', methods=['GET', 'POST'])
def cadastrar_agencia():
    if request.method == 'POST':
        numero = request.form.get('numero')
        nome = request.form.get('nome')
        endereco = request.form.get('endereco')

        dados = carregar_dados()
        agencias = dados.get('agencias', [])

        if any(a.get('numero') == numero for a in agencias):
            return render_template('cadastrar_agencia.html', 
                                   erro="Este número de agência já está registado no sistema.")

        nova_agencia = {
            "numero": numero,
            "nome": nome,
            "endereco": endereco
        }

        dados.setdefault('agencias', []).append(nova_agencia)
        salvar_dados(dados)
        
        return redirect(url_for('index'))

    return render_template('cadastrar_agencia.html')

@app.route('/operacoes', methods=['GET', 'POST'])
def operacoes():
    mensagem_sucesso = None
    mensagem_erro = None

    if request.method == 'POST':
        numero_conta = request.form.get('numero_conta')
        senha = request.form.get('senha')
        tipo_operacao = request.form.get('tipo_operacao')
        
        try:
            valor = float(request.form.get('valor', 0))
        except ValueError:
            valor = 0.0

        dados = carregar_dados()
        contas = dados.get('contas', [])

        # 1. Procura a conta e verifica a senha (Segurança)
        conta_origem = next((c for c in contas if c.get('numero') == numero_conta), None)

        if not conta_origem:
            mensagem_erro = "Conta não encontrada no sistema."
        elif str(conta_origem.get('senha')) != str(senha):
            mensagem_erro = "Senha incorreta. Operação negada."
        else:
            # 2. Executa a operação escolhida
            if tipo_operacao == 'saldo':
                mensagem_sucesso = f"Consulta realizada. O seu saldo atual é de R$ {conta_origem.get('saldo', 0):.2f}"
            
            elif tipo_operacao == 'depositar':
                if valor > 0:
                    conta_origem['saldo'] = conta_origem.get('saldo', 0) + valor
                    salvar_dados(dados)
                    mensagem_sucesso = f"Depósito de R$ {valor:.2f} realizado com sucesso!"
                else:
                    mensagem_erro = "Para depositar, o valor deve ser maior que zero."
            
            elif tipo_operacao == 'sacar':
                if valor <= 0:
                    mensagem_erro = "O valor do saque deve ser maior que zero."
                elif conta_origem.get('saldo', 0) >= valor:
                    conta_origem['saldo'] -= valor
                    salvar_dados(dados)
                    mensagem_sucesso = f"Saque de R$ {valor:.2f} realizado com sucesso!"
                else:
                    mensagem_erro = "Saldo insuficiente para realizar este saque."
            
            elif tipo_operacao == 'transferir':
                numero_destino = request.form.get('conta_destino')
                conta_destino = next((c for c in contas if c.get('numero') == numero_destino), None)
                
                if not conta_destino:
                    mensagem_erro = "A conta de destino não existe."
                elif numero_conta == numero_destino:
                    mensagem_erro = "Não é possível transferir dinheiro para a própria conta."
                elif valor <= 0:
                    mensagem_erro = "O valor da transferência deve ser maior que zero."
                elif conta_origem.get('saldo', 0) >= valor:
                    conta_origem['saldo'] -= valor
                    conta_destino['saldo'] = conta_destino.get('saldo', 0) + valor
                    salvar_dados(dados)
                    mensagem_sucesso = f"Transferência de R$ {valor:.2f} para a conta {numero_destino} concluída!"
                else:
                    mensagem_erro = "Saldo insuficiente para realizar esta transferência."

    return render_template('operacoes.html', erro=mensagem_erro, sucesso=mensagem_sucesso)

@app.route('/excluir_cliente/<cpf>', methods=['POST'])
def excluir_cliente(cpf):
    """Exclui um cliente e encerra todas as contas associadas a ele."""
    dados = carregar_dados()
    
    dados['clientes'] = [c for c in dados.get('clientes', []) if c.get('cpf') != cpf]
    
    dados['contas'] = [c for c in dados.get('contas', []) if c.get('cpf_titular') != cpf]
    
    salvar_dados(dados)
    return redirect(url_for('index'))

@app.route('/encerrar_conta/<numero>', methods=['POST'])
def encerrar_conta(numero):
    """Encerra uma conta específica baseada no número."""
    dados = carregar_dados()
    
    dados['contas'] = [c for c in dados.get('contas', []) if c.get('numero') != numero]
    
    salvar_dados(dados)
    return redirect(url_for('index'))

@app.route('/editar_cliente/<cpf>', methods=['GET', 'POST'])
def editar_cliente(cpf):
    dados = carregar_dados()
    clientes = dados.get('clientes', [])
    
    cliente_atual = next((c for c in clientes if c.get('cpf') == cpf), None)
    
    if not cliente_atual:
        return redirect(url_for('index'))

    if request.method == 'POST':
        novo_nome = request.form.get('nome')
        novo_telefone = request.form.get('telefone')
        novo_endereco = request.form.get('endereco')
        
        cliente_atual['nome'] = novo_nome
        cliente_atual['telefone'] = novo_telefone
        cliente_atual['endereco'] = novo_endereco
        
        salvar_dados(dados)
        return redirect(url_for('index'))

    return render_template('editar_cliente.html', cliente=cliente_atual)

if __name__ == '__main__':
    print("Iniciando o servidor Flask...")
    app.run(debug=True)