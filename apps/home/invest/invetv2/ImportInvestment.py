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

from apps.home.invest.ConexaoMongoDB import ConexaoMongoDB

import unidecode


class ImportInvestment:

    def process_excel_to_mongodb(self, origem_excel, excluir):
        # Conexão com o MongoDB
        conexao = ConexaoMongoDB()
        cliente, banco = conexao.conectar()
        dbMovimentacoes = banco['movimentacoes_base']
        if excluir:
            dbMovimentacoes.drop()
        # Leitura dos dados do Excel
        #diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        #caminho_arquivo = os.path.join(diretorio_atual, origem_excel)
        #mov_total_2023_df = pd.read_excel(caminho_arquivo)
        mov_total_2023_df = self.ler_arquivo(origem_excel)
        # Remover acentos, transformar em minúsculas e substituir espaços por hífens nos nomes das colunas
        mov_total_2023_df.columns = [unidecode.unidecode(col.lower()).replace(' ', '_') for col in
                                     mov_total_2023_df.columns]

        # Iteração sobre as linhas do DataFrame
        for index, row in mov_total_2023_df.iterrows():
            # Insere um novo registro
            dbMovimentacoes.insert_one(dict(row))
            print("Novo registro inserido:", row["data"], row["produto"])

        print("Processo concluído!")
    def ler_arquivo(self, nomeArquivo):
        diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_arquivo = os.path.join(diretorio_atual, "arquivos",  nomeArquivo)
        return pd.read_excel(caminho_arquivo)

    def get_all_movements(self):
        # Conexão com o MongoDB
        conexao = ConexaoMongoDB()
        cliente, banco = conexao.conectar()
        dbMovimentacoes = banco['movimentacoes_base']

        # Recupera todas as movimentações da coleção como um cursor
        all_movements_cursor = dbMovimentacoes.find()

        # Converte o cursor em um DataFrame do Pandas
        all_movements_df = pd.DataFrame(list(all_movements_cursor))

        # Retorna o DataFrame das movimentações
        return all_movements_df

    def get_all_resumo(self, dbNome):
        # Conexão com o MongoDB
        conexao = ConexaoMongoDB()
        cliente, banco = conexao.conectar()
        dbMovimentacoes = banco[dbNome]

        # Recupera todas as movimentações da coleção como um cursor
        all_movements_cursor = dbMovimentacoes.find()

        # Converte o cursor em um DataFrame do Pandas
        all_movements_df = pd.DataFrame(list(all_movements_cursor))

        # Retorna o DataFrame das movimentações
        return all_movements_df

    def salvar_resumo(self, excluir, dfResumo, dbNome):
        # Conexão com o MongoDB
        conexao = ConexaoMongoDB()
        cliente, banco = conexao.conectar()
        db = banco[dbNome]
        if excluir:
            db.drop()
        # Remover acentos, transformar em minúsculas e substituir espaços por hífens nos nomes das colunas
        dfResumo.columns = [unidecode.unidecode(col.lower()).replace(' ', '_') for col in dfResumo.columns]

        # Iteração sobre as linhas do DataFrame
        for index, row in dfResumo.iterrows():
            # Insere um novo registro
            db.insert_one(dict(row))
            print("Novo registro inserido:", row["data"], row["produto"])

        print("Processo concluído!")
