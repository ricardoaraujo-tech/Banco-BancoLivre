#Variáveis definidas -> Nome, CPF, Telefone
 #editei pfv dar uma olhada oque voces acham, ps:layrton
class Cliente:
    def __init__(self, nome, cpf, telefone, senha):
        self.nome = nome
        self.cpf = cpf
        self.telefone = telefone
        self.senha = senha

def criar_cliente(nome, cpf, telefone):
    cliente = Cliente(nome, cpf, telefone, senha=None)
    return cliente

