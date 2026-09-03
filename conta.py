#Variáveis definidas -> Número da conta, Titular da Conta, Senha e Saldo.

class Conta:
    def __init__(self, numero, titular, senha):
      self.numero = numero
      self.titular = titular
      self.senha = senha
      self.saldo = 0.0

    def depositar(self, valor):
       if valor > 0:
            self.saldo += valor 
            return True
       return False

    def sacar(self, valor, senha_informada):
        if senha_informada != self.senha:
            return False
        if valor > 0 and valor <= self.saldo:
            self.saldo -= valor
            return True
        return False

    def consultar_saldo(self):
        return self.saldo



