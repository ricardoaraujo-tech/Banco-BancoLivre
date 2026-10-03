from hypothesis import given, strategies as st
from cliente import validar_cpf
from conta import Conta

# Teste 1: Depósitos positivos devem sempre retornar True e somar ao saldo exato
@given(st.floats(min_value=0.01, max_value=10000.0, allow_nan=False, allow_infinity=False))
def test_propriedade_deposito_positivo(valor):
    conta = Conta("123", None, None, "senha", "Conta Corrente")
    saldo_inicial = conta.saldo
    resultado = conta.depositar(valor)
    assert resultado == True
    assert conta.saldo == saldo_inicial + valor

# Teste 2: CPFs formados pelo mesmo dígito repetido 11 vezes devem sempre retornar False
def test_propriedade_cpf_digitos_repetido(digito):
    cpf_repetido = str(digito) * 11
    assert validar_cpf(cpf_repetido) == False
if __name__ == "__main__":
    test_propriedade_deposito_positivo()
    test_propriedade_cpf_digitos_repetido(0)
    print("Todos os testes de propriedade passaram com sucesso!")
    
