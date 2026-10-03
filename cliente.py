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

class Cliente:
    def __init__(self, nome, cpf, telefone, endereco):
        self.nome = nome
        self.cpf = cpf
        self.telefone = telefone
        self.endereco = endereco

