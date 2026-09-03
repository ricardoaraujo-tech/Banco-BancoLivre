from cliente import Cliente
from conta import Conta

print("--- Cadastro de Cliente ---")
nome = input("Digite o nome do cliente: ")
cpf = input("Digite o CPF do cliente: ")
telefone = input("Digite o telefone do cliente: ")
endereco = input("Digite o endereço do cliente: ")

cliente = Cliente(nome, cpf, telefone, endereco)

print("--- Cadastro de Conta ---")
numero = input("Digite o número da conta: ")
senha = input("Crie a senha da conta (APENAS NÚMEROS): ")

conta_cliente = Conta(numero, cliente, senha)

print("Cliente e conta cadastrados com sucesso!")

while True:
    print("\n--- Menu ---")
    print("1. Depositar")
    print("2. Sacar")
    print("3. Consultar Saldo")
    print("4. Sair")

    opcao = input("Escolha uma opção: ")

    if opcao == "1":
        valor = float(input("Digite o valor a ser depositado: "))
        if conta_cliente.depositar(valor):
            print(f"Depósito de R${valor:.2f} realizado com sucesso!")
        else:
            print("Valor inválido para depósito.")

    elif opcao == "2":
        valor = float(input("Digite o valor a ser sacado: "))
        senha_informada = input("Digite a senha da conta: ")
        if conta_cliente.sacar(valor, senha_informada):
            print(f"Saque de R${valor:.2f} realizado com sucesso!")
        else:
            print("Saque não realizado. Verifique o valor ou a senha.")

    elif opcao == "3":
        saldo = conta_cliente.consultar_saldo()
        print(f"Saldo atual: R${saldo:.2f}")

    elif opcao == "4":
        print("Saindo do sistema...")
        break

    else:
        print("Opção inválida. Tente novamente.")
