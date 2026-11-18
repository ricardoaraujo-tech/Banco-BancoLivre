import json
import os
from dataclasses import asdict, dataclass, field
from typing import List, Optional
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
CAMINHO_ARQUIVO_DADOS = 'data/dados_bancos.json'

def validar_cpf(cpf):
    cpf_limpo = ''.join(filter(str.isdigit, str(cpf)))
    
    if len(cpf_limpo) != 11 or cpf_limpo == cpf_limpo[0] * 11:
        return False

    soma = 0
    for i in range(9):
        soma += int(cpf_limpo[i]) * (10 - i)
    digito1 = (soma * 10 % 11) % 10

    if digito1 != int(cpf_limpo[9]):
        return False

    soma = 0
    for i in range(10):
        soma += int(cpf_limpo[i]) * (11 - i)
    digito2 = (soma * 10 % 11) % 10
    
    if digito2 != int(cpf_limpo[10]):
        return False
        
    return True

@dataclass
class Cliente:
    nome: str
    cpf: str
    telefone: str
    endereco: str

    @classmethod
    def de_dicionario(cls, dados_cliente: dict) -> 'Cliente':
        return cls(
            nome=dados_cliente.get('nome', ''),
            cpf=dados_cliente.get('cpf', ''),
            telefone=dados_cliente.get('telefone', ''),
            endereco=dados_cliente.get('endereco', '')
        )

    def para_dicionario(self) -> dict:
        return asdict(self)

@dataclass
class Agencia:
    numero: str
    nome: str
    endereco: str

    @classmethod
    def de_dicionario(cls, dados_agencia: dict) -> 'Agencia':
        return cls(
            numero=dados_agencia.get('numero', ''),
            nome=dados_agencia.get('nome', ''),
            endereco=dados_agencia.get('endereco', '')
        )

    def para_dicionario(self) -> dict:
        return asdict(self)

@dataclass
class Conta:
    numero: str
    cpf_titular: str
    num_agencia: str
    senha: str
    saldo: float = 0.0
    tipo: str = ''

    @classmethod
    def de_dicionario(cls, dados_conta: dict) -> 'Conta':
        return cls(
            numero=dados_conta.get('numero', ''),
            cpf_titular=dados_conta.get('cpf_titular', ''),
            num_agencia=dados_conta.get('num_agencia', ''),
            senha=str(dados_conta.get('senha', '')),
            saldo=float(dados_conta.get('saldo', 0.0)),
            tipo=dados_conta.get('tipo', '')
        )

    def para_dicionario(self) -> dict:
        return asdict(self)

    def depositar(self, valor: float) -> None:
        self.saldo += valor

    def sacar(self, valor: float) -> None:
        self.saldo -= valor

@dataclass
class DadosBancarios:
    clientes: List[Cliente] = field(default_factory=list)
    agencias: List[Agencia] = field(default_factory=list)
    contas: List[Conta] = field(default_factory=list)

    @classmethod
    def de_dicionario(cls, dados: dict) -> 'DadosBancarios':
        agencias_carregadas = [
            Agencia.de_dicionario(dados_agencia)
            for dados_agencia in dados.get('agencias', [])
        ]
        if not agencias_carregadas:
            agencias_carregadas = [Agencia(numero="001", nome="Agência Principal", endereco="Matriz Central")]

        return cls(
            clientes=[
                Cliente.de_dicionario(dados_cliente)
                for dados_cliente in dados.get('clientes', [])
            ],
            agencias=agencias_carregadas,
            contas=[
                Conta.de_dicionario(dados_conta)
                for dados_conta in dados.get('contas', [])
            ]
        )

    def para_dicionario(self) -> dict:
        return {
            'clientes': [cliente.para_dicionario() for cliente in self.clientes],
            'agencias': [agencia.para_dicionario() for agencia in self.agencias],
            'contas': [conta.para_dicionario() for conta in self.contas]
        }

@dataclass
class Dashboard:
    num_clientes: int
    num_contas: int
    saldo_total: float
    saldo_medio: float
    maior_conta: Optional[Conta]
    menor_conta: Optional[Conta]

def carregar_dados() -> DadosBancarios:
    if os.path.exists(CAMINHO_ARQUIVO_DADOS):
        with open(CAMINHO_ARQUIVO_DADOS, 'r', encoding='utf-8') as arquivo_dados:
            dados_json = json.load(arquivo_dados)
            return DadosBancarios.de_dicionario(dados_json)

    return DadosBancarios(
        agencias=[Agencia(numero="001", nome="Agência Principal", endereco="Matriz Central")]
    )

def salvar_dados(dados_bancarios: DadosBancarios) -> None:
    os.makedirs(os.path.dirname(CAMINHO_ARQUIVO_DADOS), exist_ok=True)
    with open(CAMINHO_ARQUIVO_DADOS, 'w', encoding='utf-8') as arquivo_dados:
        json.dump(
            dados_bancarios.para_dicionario(),
            arquivo_dados,
            indent=4,
            ensure_ascii=False
        )

@app.route('/')
def index():
    dados_bancarios = carregar_dados()
    lista_clientes = dados_bancarios.clientes
    lista_agencias = dados_bancarios.agencias
    lista_contas = dados_bancarios.contas

    termo_busca = request.args.get('busca', '').lower().strip()

    if termo_busca:
        lista_clientes = [
            cliente for cliente in lista_clientes
            if termo_busca in cliente.nome.lower()
            or termo_busca in cliente.cpf
        ]

        contas_filtradas = [
            conta for conta in lista_contas
            if termo_busca in str(conta.numero)
            or termo_busca in conta.cpf_titular
        ]
    else:
        contas_filtradas = lista_contas

    contas_positivas = [
        conta for conta in contas_filtradas
        if conta.saldo > 0
    ]
    
    quantidade_clientes = len(dados_bancarios.clientes)
    quantidade_contas = len(dados_bancarios.contas)
    saldo_total = sum(conta.saldo for conta in dados_bancarios.contas)
    saldo_medio = (
        saldo_total / quantidade_contas
        if quantidade_contas > 0
        else 0.0
    )

    if dados_bancarios.contas:
        conta_com_maior_saldo = max(
            dados_bancarios.contas,
            key=lambda conta: conta.saldo
        )
        conta_com_menor_saldo = min(
            dados_bancarios.contas,
            key=lambda conta: conta.saldo
        )
    else:
        conta_com_maior_saldo = None
        conta_com_menor_saldo = None
        
    dashboard = Dashboard(
        num_clientes=quantidade_clientes,
        num_contas=quantidade_contas,
        saldo_total=saldo_total,
        saldo_medio=saldo_medio,
        maior_conta=conta_com_maior_saldo,
        menor_conta=conta_com_menor_saldo
    )
    return render_template(
        'index.html',
        clientes=lista_clientes,
        agencias=lista_agencias,
        contas_positivas=contas_positivas,
        dashboard=dashboard,
        termo_busca=termo_busca
    )

@app.route('/cadastrar_cliente', methods=['GET', 'POST'])
def cadastrar_cliente():
    if request.method == 'POST':
        nome_cliente = request.form.get('nome', '')
        cpf_digitado = request.form.get('cpf', '')
        telefone_cliente = request.form.get('telefone', '')
        endereco_cliente = request.form.get('endereco', '')

        if not validar_cpf(cpf_digitado):
            return render_template(
                'cadastrar_cliente.html',
                erro='CPF inválido. Verifique o formato e tente novamente.'
            )
        cpf_cliente = ''.join(filter(str.isdigit, cpf_digitado))
        dados_bancarios = carregar_dados()

        if any(
            cliente.cpf == cpf_cliente
            for cliente in dados_bancarios.clientes
        ):
            return render_template(
                'cadastrar_cliente.html',
                erro='CPF já cadastrado.'
            )
        novo_cliente = Cliente(
            nome=nome_cliente,
            cpf=cpf_cliente,
            telefone=telefone_cliente,
            endereco=endereco_cliente
        )
        dados_bancarios.clientes.append(novo_cliente)
        salvar_dados(dados_bancarios)
        return redirect(url_for('index'))
    return render_template('cadastrar_cliente.html')

@app.route('/cadastrar_conta', methods=['GET', 'POST'])
def cadastrar_conta():
    dados_bancarios = carregar_dados()
    lista_clientes = dados_bancarios.clientes
    lista_agencias = dados_bancarios.agencias
    lista_contas = dados_bancarios.contas
    
    if request.method == 'POST':
        numero_conta = request.form.get('numero', '')
        cpf_digitado = request.form.get('cpf_titular', '')
        senha_conta = request.form.get('senha', '')
        tipo_conta = request.form.get('tipo', '')
        
        cpf_titular = ''.join(filter(str.isdigit, cpf_digitado))
        
        if not any(
            cliente.cpf == cpf_titular
            for cliente in lista_clientes
        ):
            return render_template(
                'cadastrar_conta.html',
                erro=(
                    'Cliente não cadastrado. Por favor, cadastre o cliente '
                    'antes de criar a conta.'
                ),
                agencias=lista_agencias
            )
            
        if any(conta.numero == numero_conta for conta in lista_contas):
            return render_template(
                'cadastrar_conta.html',
                erro='O número desta conta já está em uso.',
                agencias=lista_agencias
            )

        num_agencia_unica = lista_agencias[0].numero if lista_agencias else "001"

        nova_conta = Conta(
            numero=numero_conta,
            cpf_titular=cpf_titular,
            num_agencia=num_agencia_unica,
            senha=senha_conta,
            saldo=0.0,
            tipo=tipo_conta
        )
        dados_bancarios.contas.append(nova_conta)
        salvar_dados(dados_bancarios)
        return redirect(url_for('index'))
        
    return render_template(
        'cadastrar_conta.html',
        clientes=lista_clientes,
        agencias=lista_agencias
    )

@app.route('/operacoes', methods=['GET', 'POST'])
def operacoes():
    mensagem_sucesso = None
    mensagem_erro = None
    if request.method == 'POST':
        numero_conta_origem = request.form.get('numero_conta', '')
        senha_informada = request.form.get('senha', '')
        tipo_operacao = request.form.get('tipo_operacao', '')
        try:
            valor_operacao = float(request.form.get('valor', 0))
        except (TypeError, ValueError):
            valor_operacao = 0.0
            
        dados_bancarios = carregar_dados()
        lista_contas = dados_bancarios.contas

        conta_origem = next(
            (
                conta for conta in lista_contas
                if conta.numero == numero_conta_origem
            ),
            None
        )
        if not conta_origem:
            mensagem_erro = 'Conta não encontrada no sistema.'
        elif str(conta_origem.senha) != str(senha_informada):
            mensagem_erro = 'Senha incorreta. Operação negada.'
        else:
            if tipo_operacao == 'saldo':
                mensagem_sucesso = (
                    'Consulta realizada. O seu saldo atual é de '
                    f'R$ {conta_origem.saldo:.2f}'
                )

            elif tipo_operacao == 'depositar':
                if valor_operacao > 0:
                    conta_origem.depositar(valor_operacao)
                    salvar_dados(dados_bancarios)
                    mensagem_sucesso = (
                        f'Depósito de R$ {valor_operacao:.2f} realizado com sucesso!'
                    )
                else:
                    mensagem_erro = 'Para depositar, o valor deve ser maior que zero.'

            elif tipo_operacao == 'sacar':
                if valor_operacao <= 0:
                    mensagem_erro = 'O valor do saque deve ser maior que zero.'
                elif conta_origem.saldo >= valor_operacao:
                    conta_origem.sacar(valor_operacao)
                    salvar_dados(dados_bancarios)
                    mensagem_sucesso = (
                        f'Saque de R$ {valor_operacao:.2f} realizado com sucesso!'
                    )
                else:
                    mensagem_erro = 'Saldo insuficiente para realizar este saque.'

            elif tipo_operacao == 'transferir':
                numero_conta_destino = request.form.get('conta_destino', '')
                conta_destino = next(
                    (
                        conta for conta in lista_contas
                        if conta.numero == numero_conta_destino
                    ),
                    None
                )
                if not conta_destino:
                    mensagem_erro = 'A conta de destino não existe.'
                elif numero_conta_origem == numero_conta_destino:
                    mensagem_erro = (
                        'Não é possível transferir dinheiro para a própria conta.'
                    )
                elif valor_operacao <= 0:
                    mensagem_erro = (
                        'O valor da transferência deve ser maior que zero.'
                    )
                elif conta_origem.saldo >= valor_operacao:
                    conta_origem.sacar(valor_operacao)
                    conta_destino.depositar(valor_operacao)
                    salvar_dados(dados_bancarios)
                    mensagem_sucesso = (
                        f'Transferência de R$ {valor_operacao:.2f} para a conta '
                        f'{numero_conta_destino} concluída!'
                    )
                else:
                    mensagem_erro = (
                        'Saldo insuficiente para realizar esta transferência.'
                    )

    return render_template(
        'operacoes.html',
        erro=mensagem_erro,
        sucesso=mensagem_sucesso
    )

@app.route('/excluir_cliente/<cpf>', methods=['POST'])
def excluir_cliente(cpf):
    dados_bancarios = carregar_dados()

    dados_bancarios.clientes = [
        cliente for cliente in dados_bancarios.clientes
        if cliente.cpf != cpf
    ]

    dados_bancarios.contas = [
        conta for conta in dados_bancarios.contas
        if conta.cpf_titular != cpf
    ]

    salvar_dados(dados_bancarios)
    return redirect(url_for('index'))

@app.route('/encerrar_conta/<numero>', methods=['POST'])
def encerrar_conta(numero):
    dados_bancarios = carregar_dados()

    dados_bancarios.contas = [
        conta for conta in dados_bancarios.contas
        if conta.numero != numero
    ]
    salvar_dados(dados_bancarios)
    return redirect(url_for('index'))

@app.route('/editar_cliente/<cpf>', methods=['GET', 'POST'])
def editar_cliente(cpf):
    dados_bancarios = carregar_dados()
    lista_clientes = dados_bancarios.clientes

    cliente_atual = next(
        (cliente for cliente in lista_clientes if cliente.cpf == cpf),
        None
    )
    if not cliente_atual:
        return redirect(url_for('index'))
    if request.method == 'POST':
        novo_nome = request.form.get('nome', '')
        novo_telefone = request.form.get('telefone', '')
        novo_endereco = request.form.get('endereco', '')
        cliente_atual.nome = novo_nome
        cliente_atual.telefone = novo_telefone
        cliente_atual.endereco = novo_endereco
        salvar_dados(dados_bancarios)
        return redirect(url_for('index'))
    return render_template('editar_cliente.html', cliente=cliente_atual)

if __name__ == '__main__':
    print('Iniciando o servidor Flask...')
    app.run(debug=True)
