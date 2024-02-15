import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import pymongo
import requests
import yfinance as yf
from IPython.display import display
from babel.numbers import format_currency
import numpy as np
from tabulate import tabulate
import os

def ajustar_ativo_excedente_p7(self, dados_carteira_evol_df):
    print("-----------ajustar_ativo_excedente_p7---------------")
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_completo = os.path.join(diretorio_atual, 'movimentacao_todos_ativos.xlsx')
    dados_carteira_evol_df.to_excel(caminho_completo, index=False)

    self.imprimir_se(dados_carteira_evol_df,True)
    dados_carteira_evol_df.loc[
        dados_carteira_evol_df['Ativo'] == 'Tesouro Selic 2026', 'Quantidade'] = self.ajustar_excedente(
        'Tesouro Selic 2026', dados_carteira_evol_df, 'SELIC')
    dados_carteira_evol_df.loc[
        dados_carteira_evol_df['Ativo'] == 'Tesouro IPCA+ 2045', 'Quantidade'] = self.ajustar_excedente(
        'Tesouro IPCA+ 2045', dados_carteira_evol_df, 'IPCA')

    self.imprimir_se(dados_carteira_evol_df,True)
    return dados_carteira_evol_df

def ajustar_excedente(self, ativo, df, tipo):
    print('----- ajustar_excedente ------' + ativo)
    quantidade_ativo_excedente = df.loc[df['Ativo'] == ativo, 'Quantidade'].values[0]
    print("quantidade_ativo_excedente: " + str(quantidade_ativo_excedente))
    valor_ativo_excedente = df.loc[df['Ativo'] == ativo, 'valor_ativo_atual'].values[0]
    print("quantidade_ativo_excedente: " + str(quantidade_ativo_excedente))
    total_ativo_excedente = quantidade_ativo_excedente * valor_ativo_excedente
    print("total_ativo_excedente: " + str(total_ativo_excedente))
    if total_ativo_excedente > 5000 and tipo == 'IPCA':
        quantidade_ativo_ajustada = (quantidade_ativo_excedente * 5790) / total_ativo_excedente
        print("quantidade_ativo_ajustada: " + str(quantidade_ativo_ajustada))
        quantidade_restante = quantidade_ativo_excedente - quantidade_ativo_ajustada
        print("quantidade_ativo_ajustada: " + str(quantidade_ativo_ajustada))

    if total_ativo_excedente > 5000 and tipo == 'SELIC':
        quantidade_ativo_ajustada = (quantidade_ativo_excedente * 5790) / total_ativo_excedente
        print("quantidade_ativo_ajustada: " + str(quantidade_ativo_ajustada))
        quantidade_restante = quantidade_ativo_excedente - quantidade_ativo_ajustada
        print("quantidade_ativo_ajustada: " + str(quantidade_ativo_ajustada))

        return quantidade_ativo_ajustada
        # df.loc[df['Ativo'] == ativo, 'Quantidade'] = quantidade_ipca_ajustada
    return quantidade_ativo_excedente

