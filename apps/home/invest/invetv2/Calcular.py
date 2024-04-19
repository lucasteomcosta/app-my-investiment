from apps.home.invest.invetv2 import ProcessarInvestimento
import pandas as pd
DEBITO = 'Debito'

CREDITO = 'Credito'


class Calcular:

    def calcular_quantidade_compra_venda(self, ativo, tipo, mov_total_2023_df):
        # Filtra os dados apenas para o ativo específico
        filtro_ativo = mov_total_2023_df[mov_total_2023_df['Ativo'] == ativo]

        # Soma as quantidades de compra (Crédito positivo) e venda (Débito negativo)
        if tipo == 'compra':
            return filtro_ativo.loc[
                filtro_ativo[ProcessarInvestimento.ENTRADA_SAIDA] == CREDITO, ProcessarInvestimento.QUANTIDADE].sum()
        if tipo == 'venda':
            return filtro_ativo.loc[filtro_ativo[ProcessarInvestimento.ENTRADA_SAIDA] == (
                DEBITO), ProcessarInvestimento.QUANTIDADE].sum()
        if tipo == 'pm':
            totalValOperacao = filtro_ativo.loc[filtro_ativo[
                                                    ProcessarInvestimento.ENTRADA_SAIDA] == CREDITO, ProcessarInvestimento.VALOR_DA_OPERACAO].sum()
            quantidadeTotal = filtro_ativo.loc[
                filtro_ativo[ProcessarInvestimento.ENTRADA_SAIDA] == CREDITO, ProcessarInvestimento.QUANTIDADE].sum()
            return totalValOperacao / quantidadeTotal
        if tipo == 'quantidade':
            compra = filtro_ativo.loc[
                filtro_ativo[ProcessarInvestimento.ENTRADA_SAIDA] == CREDITO, ProcessarInvestimento.QUANTIDADE].sum()
            venda = filtro_ativo.loc[
                filtro_ativo[ProcessarInvestimento.ENTRADA_SAIDA] == DEBITO, ProcessarInvestimento.QUANTIDADE].sum()
            return compra - venda
