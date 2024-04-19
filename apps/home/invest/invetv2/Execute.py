def calcular_quantidade(valor_total, valor):
    """
    Calcula a quantidade a partir do valor total e do valor unitário.

    Argumentos:
      valor_total: Valor total da compra.
      valor: Valor unitário do produto.

    Retorno:
      A quantidade de produtos que podem ser comprados com o valor total.
    """

    # Verifica se o valor unitário é positivo
    if valor <= 0:
        raise ValueError("O valor unitário deve ser positivo.")

    # Calcula a quantidade
    quantidade = valor_total / valor
    quantidade= round(quantidade, 2)
    return round(quantidade, 2)

# Exemplo de uso
valor_total = 5000

valor = 13010.22


quantidade = calcular_quantidade(valor_total, valor)

print(f"Quantidade: {quantidade}")