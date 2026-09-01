class Conta:
    
  def __init__(self,numero,nome,senha):
      self.numero = numero
      self.nome = nome 
      self.senha = senha
      self.saldo = 0
    def depositar (self, valor):
    if valor > 0:
       self saldo += valor 
       return True
    return False
def sacar (self, valor):
    if valor > 0 and valor <= self.saldo:
       self.saldo -= valor
       return True
    return False
def consultar_salto(self):
    return self.saldo

