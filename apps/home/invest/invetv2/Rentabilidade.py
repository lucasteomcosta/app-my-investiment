import os

import pandas as pd
from IPython.core.display_functions import display
from tabulate import tabulate

from apps.home.invest.invetv2 import ProcessarInvestimento

VALORIZACAO = "valorizacao"
COL_VALORIZACAO_INDIVIDUAL = 'Valorizacao Individual'
COL_PESO_INDIVIDUAL = 'Peso Individual'
COL_PESO_CATEGORIA = 'Peso Categoria'
COL_VALORIZACAO_PONDERADA = 'Valorizacao Ponderada por Categoria'
import pandas as pd

class Rentabilidade:


   

    def __init__(self, data):
        self.df = data[data[ProcessarInvestimento.CATEGORIA] != ProcessarInvestimento.CATEGORIA_OUTRAS]
        self.df = self.df.round(2)
    def calcular_valorizacao_individual(self):
        self.df = self.df.copy()
        self.df[COL_VALORIZACAO_INDIVIDUAL] = (((self.df[ProcessarInvestimento.VALOR_ATIVO_ATUAL]
                                                 - self.df[ProcessarInvestimento.PRECO_MEDIO]) / self.df[ProcessarInvestimento.PRECO_MEDIO]) * 100).round(4)

    def calcular_peso_categoria(self):
        self.df = self.df.copy()
        total_ativos = self.df[ProcessarInvestimento.VALOR_ATIVO_TOTAL].sum()
        print(total_ativos)
        self.df[COL_PESO_INDIVIDUAL] = ((self.df[ProcessarInvestimento.VALOR_ATIVO_TOTAL] / total_ativos) * 100).round(4)
        self.df[COL_PESO_CATEGORIA] = self.df.groupby(ProcessarInvestimento.CATEGORIA)[COL_PESO_INDIVIDUAL].transform('sum').round(4)

    def calcular_valorizacao_ponderada_categoria(self):
        self.df = self.df.copy()
        self.df[COL_VALORIZACAO_PONDERADA] = (((self.df[COL_VALORIZACAO_INDIVIDUAL] * self.df[COL_PESO_CATEGORIA]) / 100)).round(4)

    def calcular_valorizacao_total_carteira(self):
        self.df = self.df.copy()
        # Calcular a média ponderada das taxas de retorno
        taxa_retorno_ponderada = ( self.df['Valorizacao Individual'] *  self.df['Peso Individual']).sum() /  self.df['Peso Individual'].sum()

        # Calcular o valor total da carteira
        valor_total_carteira = taxa_retorno_ponderada * self.df['Peso Individual'].sum()

        return valor_total_carteira / 100


    def relatorio_valorizacao_carteira(self):
        self.calcular_valorizacao_individual()
        self.calcular_peso_categoria()
        self.calcular_valorizacao_ponderada_categoria()
        valorizacao_total = self.calcular_valorizacao_total_carteira().round(4)
        display(tabulate(self.df, headers='keys', tablefmt='psql'))

        print(f"Com base nos cálculos, a valorização total da sua carteira de investimentos é de {valorizacao_total}%.")
        return self.df



    def salvar_arquivo(self, ativos, nomeArquivo):
        diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_arquivo = os.path.join(diretorio_atual, "arquivos", nomeArquivo)
        ativos.to_excel(caminho_arquivo, index=False)






