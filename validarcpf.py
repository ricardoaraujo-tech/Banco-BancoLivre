import re
def validar_cpf(cpf: str) -> bool:
    cpf = re.sub(r"[.\-\s]", "", cpf)
    # Verifica se contém exatamente 11 dígitos
    if not re.fullmatch(r"\d{11}", cpf):
        return False
    # Rejeita CPFs com todos os dígitos iguais
    if len(set(cpf)) == 1:
        return False
    numeros = [int(digito) for digito in cpf]
    # Calcula os dois dígitos verificadores
    for tamanho in (9, 10):
        soma = sum(numeros[i] * (tamanho + 1 - i) for i in range(tamanho))
        resto = (soma * 10) % 11
        digito_verificador = 0 if resto == 10 else resto
        if digito_verificador != numeros[tamanho]:
            return False
    return True
