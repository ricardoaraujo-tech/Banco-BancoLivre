import json
from cliente import Cliente, validar_cpf
from conta import Conta
from agencia import Agencia

clientes = {}
agencias = {}
contas = {}

try: 
    with open('dados_bancos.json', 'r') as arquivo:
        dados_salvos = json.load(arquivo)

        for cliente_data in dados_salvos.get("clientes", []):
            c = Cliente(cliente_data["nome"], cliente_data["cpf"], cliente_data["telefone"], cliente_data["endereco"])
            clientes[c.cpf] = c

        for agencia_data in dados_salvos.get("agencias", []):
            a = Agencia(agencia_data["numero"], agencia_data["nome"])
            agencias[a.numero] = a

        for conta_data in dados_salvos.get("contas", []):
            cpf_titular = conta_data["cpf_titular"]
            num_agencia = conta_data["num_agencia"]

            if cpf_titular in clientes and num_agencia in agencias:
                cliente_vinculado = clientes[cpf_titular]
                agencia_vinculada = agencias[num_agencia]

                conta_restaurada = Conta(conta_data["numero"], cliente_vinculado, agencia_vinculada, conta_data["senha"], conta_data["tipo"])
                conta_restaurada.saldo = conta_data["saldo"]
                contas[conta_restaurada.numero] = conta_restaurada

except FileNotFoundError:
    print('\nArquivo de dados não encontrado. Iniciando com listas vazias.')

print('\nBem-vindo ao sistema bancário!')

while True:
    print('\n======================')
    print('=== MENU DE OPÇÕES ===')
    print('Cadastrar Cliente (1)')
    print('Cadastrar Agência (2)')
    print('Cadastrar Conta (3)')
    print('Listar Clientes (4)')
    print('Listar Agências (5)')
    print('Listar Contas (6)')
    print('Depositar (7)')
    print('Sacar (8)')
    print('Transferir (9)')
    print('Consultar Saldo (10)')
    print('Relatorio do Banco (11)')
    print('Editar Cliente (12)')
    print('Excluir Cliente (13)')
    print('Encerrar Contas (14)')
    print('Buscar Cliente (15)')
    print('Buscar Conta (16)')
    print('Sair (0)')
    print('======================')

    opcao = input('\nEscolha uma opção: ')
    
    if opcao == '1':
        print('\n=== CADASTRO DE CLIENTE ===')
        nome = input('\nDigite o nome do cliente: ')

        while True: 
            cpf_digitado = input('Digite o CPF do cliente: ')
            if validar_cpf(cpf_digitado):
                cpf = ''.join(filter(str.isdigit, (cpf_digitado)))
                break
            else:
                print('\nCPF inválido. O CPF digitado deve ser real. Tente novamente.')
        telefone = input('Digite o telefone do cliente: ')
        endereco = input('Digite o endereço do cliente: ')

        novo_cliente = Cliente(nome, cpf, telefone, endereco)
        clientes[cpf] = novo_cliente
        print('\nCliente cadastrado com sucesso!')

    elif opcao == '2':
        print('\n=== CADASTRO DE AGÊNCIA ===')
        numero = input('\nDigite o número da agência: ')
        nome = input('Digite o nome da agência: ')

        nova_agencia = Agencia(numero, nome)
        agencias[numero] = nova_agencia
        print('\nAgência cadastrada com sucesso!')

    elif opcao == '3':
        print('\n=== CADASTRO DE CONTA ===')
        titular_cpf = input('\nDigite o CPF do titular da conta: ')

        if titular_cpf in clientes:
            cliente_encontrado = clientes[titular_cpf]
        else:
            print('\nCliente não encontrado. Cadastre o cliente antes de criar a conta.')
            continue

        agencia_busca = input('\nDigite o número da agência: ')

        if agencia_busca in agencias:
            agencia_encontrada = agencias[agencia_busca]
        else:
            print('\nAgência não encontrada. Cadastre a agência antes de criar a conta.')
            continue    

        numero = input('\nDigite o número da conta: ')
        senha = input('\nDigite a senha da conta: ')

        print('\nEscolha o tipo da conta:')
        print('1. Conta Corrente')
        print('2. Conta Poupança')
        print('3. Conta Salário')

        while True:
            escolha = input('Opção: ')

            if escolha == '1':
                tipo = 'Conta Corrente'
                break
            elif escolha == '2':
                tipo = 'Conta Poupança'
                break
            elif escolha == '3':
                tipo = 'Conta Salário'
                break
            else:
                print('\nOpção inválida! Digite 1, 2 ou 3 para escolher o tipo da conta.')

        nova_conta = Conta(numero, cliente_encontrado, agencia_encontrada, senha, tipo)
        contas[numero] = nova_conta
        print(f'\nConta cadastrada com sucesso! Titular: {cliente_encontrado.nome}, Agência: {agencia_encontrada.nome}, Número da Conta: {numero}')
    
    elif opcao == '4':
        print('\n=== LISTA DE CLIENTES ===')
        if not clientes:
            print('\nNenhum cliente cadastrado.')
        else:
            for cliente in clientes.values():
                print(f'\nNome: {cliente.nome}, CPF: {cliente.cpf}, Telefone: {cliente.telefone}, Endereço: {cliente.endereco}')

    elif opcao == '5':
        print('\n=== LISTA DE AGÊNCIAS ===')
        if not agencias:
            print('\nNenhuma agência cadastrada.')
        else:
            for agencia in agencias.values():
                print(f'\nNúmero: {agencia.numero}, Nome: {agencia.nome}')

    elif opcao == '6':
        print('\n=== LISTA DE CONTAS ===')
        if not contas:
            print('\nNenhuma conta cadastrada.')
        else:
            for conta in contas.values():
                print(f'\nNúmero: {conta.numero} | Tipo: {conta.tipo} | Agência: {conta.agencia.numero} - {conta.agencia.nome}')
                print(f'Titular: {conta.titular.nome} (CPF: {conta.titular.cpf})')
                print(f'Saldo: R${conta.saldo:.2f}')

    elif opcao == '7':
        print('\n=== DEPÓSITO ===')
        numero_conta = input('\nDigite o número da conta: ')

        if numero_conta in contas:
            conta = contas[numero_conta]
            valor = float(input('\nDigite o valor a ser depositado: '))

            if conta.depositar(valor):
                print(f'\nDepósito de R${valor:.2f} realizado com sucesso! Novo saldo: R${conta.saldo:.2f}')
            else:
                print('\nDepósito não realizado. O valor deve ser maior que zero.')
        else:
            print('\nConta não encontrada.')
    
    elif opcao == '8':
        print('\n=== SAQUE ===')
        numero_conta = input('\nDigite o número da conta: ')

        if numero_conta in contas:
            conta = contas[numero_conta]
            valor = float(input('\nDigite o valor a ser sacado: '))
            senha_informada = input('\nDigite a senha da conta: ')

            if conta.sacar(valor, senha_informada):
                print(f'\nSaque de R${valor:.2f} realizado com sucesso! Novo saldo: R${conta.saldo:.2f}')
            else:
                print('\nSaque não realizado. Verifique o valor e a senha informada.')
        else:
            print('\nConta não encontrada.')

    elif opcao == '9':
        print('\n=== TRANSFERÊNCIA ===')
        numero_conta_origem = input('\nDigite o número da conta de origem: ')

        if numero_conta_origem in contas:
            conta = contas[numero_conta_origem]
            numero_conta_destino = input('\nDigite o número da conta de destino: ')

            if numero_conta_destino in contas:
                conta_destino = contas[numero_conta_destino]
                valor = float(input('\nDigite o valor a ser transferido: '))
                senha_informada = input('\nDigite a senha da conta de origem: ')

                if conta.sacar(valor, senha_informada):
                    conta_destino.depositar(valor)
                    print(f'\nTransferência de R${valor:.2f} realizada com sucesso! Novo saldo da conta de origem: R${conta.saldo:.2f}')
                else:
                    print('\nTransferência não realizada. Verifique o valor e a senha informada.')
            else:
                print('\nConta de destino não encontrada.')
        else:
            print('\nConta de origem não encontrada.')            
                     
    elif opcao == '10':
        print('\n=== CONSULTA DE SALDO ===')
        numero_conta = input('\nDigite o número da conta: ')

        if numero_conta in contas:
            conta = contas[numero_conta]
            senha_informada = input('\nDigite a senha da conta: ')

            if senha_informada == conta.senha:
                saldo = conta.consultar_saldo()
                print(f'\nSaldo da conta {numero_conta}: R${saldo:.2f}')
            else:
                print('\nSenha incorreta. Não foi possível consultar o saldo.')
        else:
            print('\nConta não encontrada.')

    elif opcao == '11':
        print('\n=== RELATÓRIO DO BANCO ===')

        total_banco = 0.0
        for conta in contas.values():
            total_banco += conta.saldo
        print(f'\nMontante total do banco: R${total_banco:.2f}')    

        numero_agencia = input('\nDigite o número da agência para consultar o montante: ')

        if numero_agencia in agencias:
            agencia = agencias[numero_agencia]
            total_agencia = 0.0
            for conta in contas.values():
                if conta.agencia.numero == agencia.numero:
                    total_agencia += conta.saldo
            print(f'\nMontante total da agência {agencia.nome} (Número: {agencia.numero}): R${total_agencia:.2f}')
        else:
            print('\nAgência não encontrada.')

    elif opcao == '12':
        print('\n=== EDITAR CLIENTE ===')
        cpf_busca = input('\nDigite o CPF do cliente a ser editado: ')

        if cpf_busca in clientes:
            cliente = clientes[cpf_busca]
            print(f'\nCliente encontrado: {cliente.nome} (CPF: {cliente.cpf})')
            novo_nome = input('\nDigite o novo nome do cliente (ou pressione Enter para manter o atual): ')
            novo_telefone = input('Digite o novo telefone do cliente (ou pressione Enter para manter o atual): ')
            novo_endereco = input('Digite o novo endereço do cliente (ou pressione Enter para manter o atual): ')

            if novo_nome != '':
                cliente.nome = novo_nome

            if novo_telefone != '':
                cliente.telefone = novo_telefone

            if novo_endereco != '':
                cliente.endereco = novo_endereco

            print('\nCliente atualizado com sucesso!')
        else:
            print('\nCliente não encontrado.')

    elif opcao == '13':
        print('\n=== EXCLUIR CLIENTE ===') 
        cpf_busca = input('\nDigite o CPF do cliente a ser excluído: ')

        tem_conta_ativa = False
        for conta in contas.values():
            if conta.titular.cpf == cpf_busca:
                tem_conta_ativa = True
                break

        if tem_conta_ativa:
            print('\nNão é possível excluir o cliente. Ele possui contas ativas.')
        else: 
            if cpf_busca in clientes:
                del clientes[cpf_busca]
                print('\nCliente excluído com sucesso!')
            else:
                print('\nCliente não encontrado.')                

    elif opcao == '14':
        print('\n=== ENCERRAR CONTA ===')
        numero_busca = input('\nDigite o número da conta a ser encerrada: ')

        if numero_busca in contas:
            conta = contas[numero_busca]
            senha_digitada = input('\nDigite a senha da conta: ')

            if senha_digitada == conta.senha:
                if conta.saldo == 0:
                    del contas[numero_busca]
                    print(f'\nConta {conta.numero} encerrada com sucesso!')
                else:
                    print('\nNão é possível encerrar a conta. O saldo deve ser zero.')
                    print('\nVocê precisa zerar o saldo (SAQUE OU TRANSFIRA)')
            else:
                print('\nAcesso negado: Senha incorreta.')
        else:
            print('\nConta não encontrada.')

    elif opcao == '15':
        print('\n=== BUSCAR CLIENTE ===')
        cpf_busca = input('\nDigite o CPF do cliente que deseja buscar: ')

        if cpf_busca in clientes:
            cliente = clientes[cpf_busca]
            print(f'\n--- DADOS DO CLIENTE ---')
            print(f'Nome: {cliente.nome}')
            print(f'CPF: {cliente.cpf}')
            print(f'Telefone: {cliente.telefone}')
            print(f'Endereço: {cliente.endereco}')

            print('\n--- CONTAS VINCULADAS ---')
            contas_encontradas = 0

            for conta in contas.values():
                if conta.titular.cpf == cpf_busca:
                    print(f'\nAgência: {conta.agencia.numero} | Conta: {conta.numero} | Saldo: R$ {conta.saldo:.2f}')
                    contas_encontradas += 1

            if contas_encontradas == 0:
                print('\nO cliente não possui contas ativas no momento.')
        else:
            print('\nCliente não encontrado.')

    elif opcao == '16':
        print('\n=== BUSCAR CONTA ===')
        num_conta_busca = input('\nDigite o número da conta que deseja buscar: ')

        if num_conta_busca in contas:
            conta = contas[num_conta_busca]
            print(f'\n--- DADOS DA CONTA ---')
            print(f'Número da Conta: {conta.numero} | Tipo: {conta.tipo}')
            print(f'Agência: {conta.agencia.numero} - {conta.agencia.nome}')
            print(f'Titular: {conta.titular.nome} (CPF: {conta.titular.cpf})')
            print(f'Saldo: R$ {conta.saldo:.2f}')
        else:
            print('\nConta não encontrada.')

    elif opcao == '0':
        print('\nSalvando dados do sistema...')

        cliente_para_salvar = []
        for cliente in clientes.values():
            cliente_para_salvar.append({
                "nome": cliente.nome,
                "cpf": cliente.cpf,
                "telefone": cliente.telefone,
                "endereco": cliente.endereco
            })

        agencia_para_salvar = []
        for agencia in agencias.values():
            agencia_para_salvar.append({
                "numero": agencia.numero,
                "nome": agencia.nome
            })

        conta_para_salvar = []
        for conta in contas.values():
            conta_para_salvar.append({
                "numero": conta.numero,
                "cpf_titular": conta.titular.cpf,
                "num_agencia": conta.agencia.numero,
                "senha": conta.senha,
                "saldo": conta.saldo,
                "tipo": conta.tipo
            })

        pacote_final = {
            "clientes": cliente_para_salvar,
            "agencias": agencia_para_salvar,
            "contas": conta_para_salvar
        }

        with open('dados_bancos.json', 'w') as arquivo:
            json.dump(pacote_final, arquivo)

        print('\nDados salvos com sucesso!')
        break
