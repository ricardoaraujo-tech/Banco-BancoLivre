 

class Cliente:
    def __init__(self, nome, cpf, telefone, endereco):
        self.nome = nome
        self.cpf = cpf
        self.telefone = telefone
        self.endereco = endereco

def Validar_cpf(cpf):
  if len(cpf) < 11 or len(cpf) > 11:
   return "Cpf inválido, deixe em 11 digitos"
  return cpf
