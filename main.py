class Cliente:
    def __init__(self, nome, cpf, telefone, senha):
        self.nome = nome
        self.cpf = cpf
        self.telefone = telefone
        self.senha = senha


def criar_cliente(nome, cpf, telefone, senha):
    return Cliente(nome, cpf, telefone, senha)


class Conta:
    def __init__(self, numero, cliente):
        self.numero = numero
        self.cliente = cliente
        self.saldo = 0.0

    def depositar(self, valor):
        if valor > 0:
            self.saldo += valor
            return True
        return False

    def sacar(self, valor):
        if 0 < valor <= self.saldo:
            self.saldo -= valor
            return True
        return False

    def consultar_saldo(self):
        return self.saldo


def main():
    nome = input("Nome: ")
    cpf = input("CPF: ")
    telefone = input("Telefone: ")
    senha = input("Senha: ")

    novo_cliente = criar_cliente(nome, cpf, telefone, senha)
    nova_conta = Conta(numero="0001", cliente=novo_cliente)


if __name__ == "__main__":
    main()
