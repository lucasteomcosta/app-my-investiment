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

from apps.home.invest.Investimento import Investimento
from apps.home.invest.invetv2.Calcular import Calcular
from apps.home.invest.invetv2.ImportInvestment import ImportInvestment
from apps.home.invest.invetv2.ObterValorAtivo import ObterValorAtivo
from apps.home.invest.invetv2.Rentabilidade import Rentabilidade

AJUSTE_CATEGORIA_VAL = 'ajuste_categoria_val'

AJUSTE_ATIVO_VAL = 'ajuste_ativo_val'

AJUSTE_ATIVO_QTD = 'ajuste_ativo_qtd'

VS_PERC_ATIVO = 'vs_perc_ativo'

VS_PERC_CATEGORIA = 'vs_perc_categoria'

PERC_REAL_ATIVO = 'perc_real_ativo'

CATEGORIA_OUTRAS = 'OUTRAS'

PERC_IDEAL_CAT = 'perc_ideal_cat'

PERC_REAL_CAT = "perc_real_cat"

VALOR_ATIVO_ATUAL = 'valor_ativo_atual'

VALOR_ATIVO_TOTAL = 'valor_ativo_total'

PERCENTUAL = 'Percentual'

CATEGORIA = 'Categoria'

MOVIMENTACAO = "movimentacao"

PRECO_MEDIO = 'Preco_medio'

VENDA = 'Venda'

COMPRA = 'Compra'

ATIVO = "Ativo"

VALOR_DA_OPERACAO = "valor_da_operacao"

PRECO_UNITARIO = "preco_unitario"

QUANTIDADE = "quantidade"

DATA = "data"

ENTRADA_SAIDA = "entrada/saida"

PRODUTO = 'produto'

VALOR_ATIVO_ATUAL = "valor_ativo_atual"


class ProcessarInvestimento:
    calcular = Calcular()
    valorAtivo = ObterValorAtivo()

    def cria_coluna_ativo_p2(self, mov_total_2023_df):
        opcoes = ['Transferência - Liquidação', 'Venda', 'Compra']
        mov_total_2023_df = mov_total_2023_df.loc[
            mov_total_2023_df[MOVIMENTACAO].isin(opcoes), [ENTRADA_SAIDA, DATA, PRODUTO, QUANTIDADE, PRECO_UNITARIO,
                                                           VALOR_DA_OPERACAO]]
        # cria a coluna ativo e se for tesouro mantem o valor
        print('----------cria_coluna_ativo_p2-----------------')

        def tratar_ativo(valor):
            if valor.startswith('Tesouro'):
                return valor
            else:
                return valor.split()[0]

        # cria uma nova coluna ativo, pegando a primeira palavra da coluna produto e ou mantendo se for tesouro
        # mov_apenas_ativos_df['Ativo'] = mov_apenas_ativos_df['Produto'].apply(tratar_ativo)
        mov_total_2023_df.insert(mov_total_2023_df.columns.get_loc(PRODUTO) + 1, ATIVO,
                                 mov_total_2023_df[PRODUTO].apply(tratar_ativo))
        return mov_total_2023_df

    def criar_colunas_compra_venda_preco_medio_p3(self, mov_total_2023_df):
        print('----- criar_colunas_compra_venda_preco_medio_p3 ------')
        # mov_ativo_comp_vend_df = mov_total_2023_df["Ativo"]
        dados_carteira_evol_df = mov_total_2023_df.loc[:, [ATIVO, QUANTIDADE]]
        dados_carteira_evol_df = dados_carteira_evol_df.drop_duplicates(subset=ATIVO)
        # print(dados_carteira_evol_df)

        # quant_final_df = calcular_quantidade_compra_venda(ativo_especifico)
        # df['Idade_Neg'] = df['Idade'].apply(lambda x: separar_valores_positivos_negativos(x)[1])

        dados_carteira_evol_df[
            COMPRA] = dados_carteira_evol_df[ATIVO].apply(
            lambda ativo: self.calcular.calcular_quantidade_compra_venda(ativo, 'compra', mov_total_2023_df))
        dados_carteira_evol_df[VENDA] = dados_carteira_evol_df[ATIVO].apply(
            lambda ativo: self.calcular.calcular_quantidade_compra_venda(ativo, 'venda', mov_total_2023_df))
        dados_carteira_evol_df[PRECO_MEDIO] = dados_carteira_evol_df[ATIVO].apply(
            lambda ativo: self.calcular.calcular_quantidade_compra_venda(ativo, 'pm', mov_total_2023_df))
        dados_carteira_evol_df[QUANTIDADE] = dados_carteira_evol_df[ATIVO].apply(
            lambda ativo: self.calcular.calcular_quantidade_compra_venda(ativo, 'quantidade', mov_total_2023_df))

        return dados_carteira_evol_df

    def adicionar_categoria_p4(self, dados_carteira_evol_df):
        print('----- adicionar_categoria_p4 ------')
        template_carteira = self.obter_template_carteira()
        dados_carteira_evol_df.insert(0, CATEGORIA, dados_carteira_evol_df[ATIVO].apply(
            lambda ativo: self.setar_categorial(ativo, template_carteira)))

        dados_carteira_evol_df = dados_carteira_evol_df.sort_values(by=CATEGORIA)

        dados_carteira_evol_df = self.adicionar_registros(dados_carteira_evol_df, template_carteira)
        dados_carteira_evol_df = dados_carteira_evol_df.sort_values(by=CATEGORIA)

        dados_carteira_evol_df.insert(0, 'STATUS', dados_carteira_evol_df[ATIVO].apply(
            lambda ativo: self.definir_categorias_ativas_na_carteira(ativo, template_carteira)))

        return dados_carteira_evol_df

    def obter_template_carteira(self):
        diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_arquivo = os.path.join(diretorio_atual, 'carteira.xlsx')
        return pd.read_excel(caminho_arquivo)

    def adicionar_registros(self, tabela_principal, tabela_nova):
        print('----- adicionar_registros ------')
        colunas_faltantes = set(tabela_nova.columns) - set(tabela_principal.columns)

        for coluna in colunas_faltantes:
            tabela_principal[coluna] = 0

        registros_novos = tabela_nova[~tabela_nova[ATIVO].isin(tabela_principal[ATIVO])]
        registros_novos = registros_novos.loc[registros_novos[ATIVO] != 'TESOURO-IPCA-2045']
        registros_novos = registros_novos.loc[registros_novos[ATIVO] != 'TESOURO-SELIC-2029']

        # tabela_principal = tabela_principal.append(registros_novos, ignore_index=True)
        tabela_principal = pd.concat([tabela_principal, registros_novos], ignore_index=True)
        # Preenchendo com 0 nas colunas numéricas para converter valores NaN
        colunas_numericas = tabela_principal.select_dtypes(include=[float, int]).columns
        tabela_principal[colunas_numericas] = tabela_principal[colunas_numericas].fillna(0)

        return tabela_principal

    def setar_categorial(self, ativo, template_carteira):
        # Filtra os dados apenas para o ativo específico
        if ativo.startswith('Tesouro'):
            if ativo == 'Tesouro Selic 2029':
                return 'RENDA_FIXA_POS'
            if ativo == 'Tesouro IPCA+ 2045':
                return 'RENDA_FIXA_DINAMICA'
            else:
                return CATEGORIA_OUTRAS

        filtro_ativo = template_carteira[template_carteira[ATIVO] == ativo]
        if filtro_ativo.empty:
            return CATEGORIA_OUTRAS

        retorno = filtro_ativo.loc[filtro_ativo[ATIVO] == ativo, CATEGORIA].values[0]
        return retorno

    def definir_categorias_ativas_na_carteira(self, ativo, template_carteira):
        # Filtra os dados apenas para o ativo específico
        if ativo.startswith('Tesouro'):
            if ativo == 'Tesouro Selic 2029':
                return 'SIM'
            if ativo == 'Tesouro IPCA+ 2045':
                return 'SIM'
            else:
                return 'SIM'

        filtro_ativo = template_carteira[template_carteira[ATIVO] == ativo]
        if filtro_ativo.empty:
            return 'NAO'

        return 'SIM'

    def adicionar_percentual_ideal_p5(self, dados_carteira_evol_df):
        print('----- adicionar_percentual_ideal_p5 ------')
        dados_carteira_evol_df[PERCENTUAL] = dados_carteira_evol_df[ATIVO].apply(
            lambda ativo: self.setar_percentual(ativo))
        dados_carteira_evol_df = dados_carteira_evol_df.sort_values(by=CATEGORIA)
        return dados_carteira_evol_df

    def setar_percentual(self, ativo):
        # Filtra os dados apenas para o ativo específico
        template_carteira = self.obter_template_carteira()
        if ativo.startswith('Tesouro'):
            if ativo == 'Tesouro Selic 2029':
                ativo = 'TESOURO-SELIC-2029'
            else:
                if ativo == 'Tesouro IPCA+ 2045':
                    ativo = 'TESOURO-IPCA-2045'
                else:
                    return 0

        filtro_ativo = template_carteira[template_carteira['Ativo'] == ativo]

        if filtro_ativo.empty:
            return 0

        retorno = filtro_ativo.loc[filtro_ativo[ATIVO] == ativo, PERCENTUAL].values[0]

        return retorno

    def obter_valor_ativo_atual_p6(self, dados_carteira_evol_df):
        print('----- obter_valor_ativo_atual_p6 ------')
        dados_carteira_evol_df[VALOR_ATIVO_ATUAL] = dados_carteira_evol_df[ATIVO].apply(
            self.valorAtivo.obter_valor_ativo)

        # define valores não encontrado como zero
        dados_carteira_evol_df.loc[dados_carteira_evol_df[VALOR_ATIVO_ATUAL].isna(), VALOR_ATIVO_ATUAL] = 0
        self.salvar_arquivo(dados_carteira_evol_df, "ativos_valorizados.xlsx")
        return dados_carteira_evol_df

    def definir_valor_ativo_total8(self, dados_carteira_evol_df):
        print('----- atualizar_valor_ativo_p8 ------')
        dados_carteira_evol_df[VALOR_ATIVO_TOTAL] = dados_carteira_evol_df[ATIVO].apply(
            lambda ativo: self.setar_valor_atualizado_ativo(ativo, dados_carteira_evol_df))
        dados_carteira_evol_df = dados_carteira_evol_df.round(2)

        return dados_carteira_evol_df

    def setar_valor_atualizado_ativo(self, ativo, dados_carteira_evol_copy_df):
        # Filtra os dados apenas para o ativo específico
        filtro_ativo = dados_carteira_evol_copy_df[dados_carteira_evol_copy_df[ATIVO] == ativo]
        if filtro_ativo.empty:
            return 0
        retorno = filtro_ativo.loc[filtro_ativo[ATIVO] == ativo, QUANTIDADE].values[0] * \
                  filtro_ativo.loc[filtro_ativo[ATIVO] == ativo, VALOR_ATIVO_ATUAL].values[0]
        return retorno

    def atualizar_valor_ativo_p8(self, dados_carteira_evol_df):
        print('----- atualizar_valor_ativo_p8 ------')
        dados_carteira_evol_df[VALOR_ATIVO_ATUAL] = dados_carteira_evol_df[ATIVO].apply(
            lambda ativo: self.setar_valor_atualizado_ativo(ativo, dados_carteira_evol_df))
        dados_carteira_evol_df = dados_carteira_evol_df.round(2)

        return dados_carteira_evol_df

    def criar_linha_com_valor_execente(self, df, quantidade, ativo):

        nova_linha = df.loc[df[ATIVO] == ativo].copy()
        nova_linha[ATIVO] = ativo+'-EXEC'
        nova_linha[CATEGORIA] = CATEGORIA_OUTRAS
        nova_linha[QUANTIDADE] = quantidade
        df = pd.concat([df, nova_linha], ignore_index=True)

        return df

    def ajustar_excedente(self, ativo, df, valor_total):

        print('----- ajustar_excedente ------' + ativo)
        quantidade_ativo_excedente = df.loc[df[ATIVO] == ativo, QUANTIDADE].values[0]
        valor_ativo_atual = df.loc[df[ATIVO] == ativo, VALOR_ATIVO_ATUAL].values[0]
        #valor_total = valor_ativo_atual * quantidade_ativo_excedente
        quantidade_usar_carteira = self.calcular_quantidade(valor_total, valor_ativo_atual)
        print("----->quantidade_pre_definida: " + str(quantidade_usar_carteira))
        #percentual_ativo = df.loc[df[ATIVO] == ativo, PERCENTUAL].values[0]
        quantidade_restante = quantidade_ativo_excedente - quantidade_usar_carteira
        print("quantidade_restante: " + str(quantidade_restante))
        df = self.criar_linha_com_valor_execente(df, quantidade_restante, ativo)
        categoria_ativo_ajuste = df.loc[df[ATIVO] == ativo, CATEGORIA].values[0]
        df.loc[(df[ATIVO] == ativo) & (df[CATEGORIA] == categoria_ativo_ajuste), QUANTIDADE] = quantidade_usar_carteira

        return df

    def calcular_quantidade(self, valor_total, valor):

        # Verifica se o valor unitário é positivo
        if valor <= 0:
            raise ValueError("O valor unitário deve ser positivo.")

        # Calcula a quantidade
        quantidade = valor_total / valor

        return  round(quantidade, 2)

    def ajustar_ativo_excedente_p7(self, dados_carteira_evol_df):
        print("-----------ajustar_ativo_excedente_p7---------------")
        diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_completo = os.path.join(diretorio_atual, 'movimentacao_todos_ativos.xlsx')
        dados_carteira_evol_df.to_excel(caminho_completo, index=False)

        dados_carteira_evol_df = self.ajustar_excedente(
            'Tesouro Selic 2029', dados_carteira_evol_df, 6580)
        dados_carteira_evol_df = self.ajustar_excedente(
            'Tesouro IPCA+ 2045', dados_carteira_evol_df, 9900)
        display(tabulate(dados_carteira_evol_df, headers='keys', tablefmt='psql'))
        return dados_carteira_evol_df

    def adicionar_percentual_ideal_categoria_p9(self, dados_carteira_evol_copy_df):
        print('----- adicionar_percentual_ideal_categoria_p9 ------')
        groupby_percentual_ideal_categoria_df = dados_carteira_evol_copy_df.groupby(CATEGORIA, as_index=False)[
            PERCENTUAL].sum()

        display(tabulate(groupby_percentual_ideal_categoria_df, headers='keys', tablefmt='psql'))
        dados_carteira_evol_copy_df[PERC_IDEAL_CAT] = dados_carteira_evol_copy_df[CATEGORIA].apply(
            lambda categoria: self.seta_percentual_ideal_categoria(categoria, groupby_percentual_ideal_categoria_df))

        return dados_carteira_evol_copy_df
    def seta_percentual_ideal_categoria(self, categoria, groupby_percentual_ideal_categoria_df):

        if categoria == CATEGORIA_OUTRAS:
            return 0
        percentual_ideal_por_categoria = groupby_percentual_ideal_categoria_df.loc[
        (groupby_percentual_ideal_categoria_df[CATEGORIA] == categoria), PERCENTUAL].values[0]

        return percentual_ideal_por_categoria

    def adicionar_percentual_real_categoria_p10(self, dados_carteira_evol_copy_df):

        print('----- adicionar_percentual_real_categoria_p10 ------')

        # Agrupar por categoria e somar o valor total
        groupby_categoria_ativo_df = dados_carteira_evol_copy_df.groupby(CATEGORIA, as_index=False)[VALOR_ATIVO_TOTAL].sum()
        total_investido = groupby_categoria_ativo_df.loc[groupby_categoria_ativo_df[CATEGORIA] != CATEGORIA_OUTRAS, VALOR_ATIVO_TOTAL].sum()
        display(total_investido)
        valor_outras = groupby_categoria_ativo_df.loc[
            groupby_categoria_ativo_df[CATEGORIA] == CATEGORIA_OUTRAS, VALOR_ATIVO_TOTAL].sum()
        dados_carteira_evol_copy_df[PERC_REAL_CAT] = dados_carteira_evol_copy_df[CATEGORIA].apply(
            lambda categoria: self.seta_percentual_por_categoria(categoria, total_investido,
                                                                 groupby_categoria_ativo_df))
        dados_carteira_evol_copy_df = dados_carteira_evol_copy_df.sort_values(by=CATEGORIA, ascending=False)


        return dados_carteira_evol_copy_df

    def seta_percentual_por_categoria(self, categoria, total_investido, groupby_categoria_ativo_df):
        if categoria == CATEGORIA_OUTRAS:
            return 0
        total_por_categoria = \
            groupby_categoria_ativo_df.loc[groupby_categoria_ativo_df[CATEGORIA] == categoria, VALOR_ATIVO_TOTAL].values[0]
        return (total_por_categoria / total_investido) * 100

    def adicionar_percentual_ativo_ideal_vs_atual_p11(self, dados_carteira_evol_copy_df):
        print('----- adicionar_percentual_ativo_ideal_vs_atual_p11 ------')
        groupby_categoria_ativo_df = dados_carteira_evol_copy_df.groupby(CATEGORIA, as_index=False)[VALOR_ATIVO_TOTAL].sum()
        total_investido = groupby_categoria_ativo_df.loc[
            groupby_categoria_ativo_df[CATEGORIA] != CATEGORIA_OUTRAS, VALOR_ATIVO_TOTAL].sum()

        dados_carteira_evol_copy_df[PERC_REAL_ATIVO] = dados_carteira_evol_copy_df[ATIVO].apply(
            lambda ativo: self.seta_percentual_ativo_atualizado_categoria(ativo, total_investido, dados_carteira_evol_copy_df))

        return dados_carteira_evol_copy_df

    def seta_percentual_ativo_atualizado_categoria(self, ativo, total_investido, dados_carteira_evol_copy_df):
        # Filtra os dados apenas para o ativo específico

        filtro_ativo = dados_carteira_evol_copy_df[dados_carteira_evol_copy_df[ATIVO] == ativo]
        if filtro_ativo.empty:
            return 0

        valor_total_ativo =   dados_carteira_evol_copy_df.loc[dados_carteira_evol_copy_df[ATIVO] == ativo, VALOR_ATIVO_TOTAL].values[0]
        retorno = (valor_total_ativo / total_investido) * 100
        return retorno
    def adicionar_diferenca_percentual_categoria_ideal_vs_real_p12(self, dados_carteira_evol_copy_df):
        print('----- adicionar_diferenca_percentual_categoria_ideal_vs_real_p12 ------')
        dados_carteira_evol_copy_df[VS_PERC_CATEGORIA] = dados_carteira_evol_copy_df[PERC_IDEAL_CAT] - \
                                         dados_carteira_evol_copy_df[PERC_IDEAL_CAT]

        return dados_carteira_evol_copy_df

    def adicionar_diferenca_percentual_ativo_ideal_vs_real_p13(self, dados_carteira_evol_copy_df):
        print('----- adicionar_diferenca_percentual_ativo_ideal_vs_real_p13 ------')
        dados_carteira_evol_copy_df[VS_PERC_ATIVO] = dados_carteira_evol_copy_df[PERC_REAL_ATIVO] - dados_carteira_evol_copy_df[PERCENTUAL]
        return dados_carteira_evol_copy_df

    def calcula_valor_ativo_balancear_p14(self, dados_carteira_evol_copy_df):
        print('----- calcula_valor_ativo_balancear_p14 ------')

        total_investido = dados_carteira_evol_copy_df.loc[
            dados_carteira_evol_copy_df[CATEGORIA] != CATEGORIA_OUTRAS, VALOR_ATIVO_TOTAL].sum()

        print(total_investido)

        dados_carteira_evol_copy_df[AJUSTE_ATIVO_QTD] = dados_carteira_evol_copy_df[ATIVO].apply(
            lambda ativo: self.definir_valor_ajuste_ativo(ativo, total_investido, False, dados_carteira_evol_copy_df))

        dados_carteira_evol_copy_df[AJUSTE_ATIVO_VAL] = dados_carteira_evol_copy_df[ATIVO].apply(
            lambda ativo: self.definir_valor_ajuste_ativo(ativo, total_investido, True, dados_carteira_evol_copy_df))

        dados_carteira_evol_copy_df[AJUSTE_CATEGORIA_VAL] = dados_carteira_evol_copy_df[CATEGORIA].apply(
            lambda categoria: dados_carteira_evol_copy_df.loc[
                dados_carteira_evol_copy_df[CATEGORIA] == categoria, AJUSTE_ATIVO_VAL].sum())

        total_investido = dados_carteira_evol_copy_df.loc[
            dados_carteira_evol_copy_df[CATEGORIA] != CATEGORIA_OUTRAS, VALOR_ATIVO_TOTAL].sum()

        print('total_investido: ')
        print(total_investido)


        return dados_carteira_evol_copy_df

    def definir_valor_ajuste_ativo(selef,ativo, patrimonio, apenasValor, dados_carteira_evol_copy_df):
        # Filtra os dados apenas para o ativo específico
        vs_perc_ativo = \
            dados_carteira_evol_copy_df.loc[dados_carteira_evol_copy_df[ATIVO] == ativo, VS_PERC_ATIVO].values[0]
        if vs_perc_ativo >= 0:
            return 0
        valor_ativo_atual = \
            dados_carteira_evol_copy_df.loc[dados_carteira_evol_copy_df[ATIVO] == ativo, VALOR_ATIVO_ATUAL].values[0]
        valor_sobre_patrimonio = (patrimonio * vs_perc_ativo * -1) / 100
        if apenasValor == True:
            return valor_sobre_patrimonio.round(2)

        total_valor_ajuste = valor_sobre_patrimonio / valor_ativo_atual
        return total_valor_ajuste.round(2)

    def importar_dados(self):
        ii = ImportInvestment()
        #ii.process_excel_to_mongodb("movimentacao.xlsx", True)
        ii.process_excel_to_mongodb("outros_ativos.xlsx", False)

    def criar_resumo_atualizado(self):
        ii = ImportInvestment()
        df = ii.get_all_movements()

        df = self.cria_coluna_ativo_p2(df)
        i = Investimento()
        display(tabulate(df, headers='keys', tablefmt='psql'))
        df = self.criar_colunas_compra_venda_preco_medio_p3(df)



        df = self.obter_valor_ativo_atual_p6(df)
        #df.to_excel("preco_medio.xlsx", index=False)


    def definir_valor_total(self):
        df = self.ler_arquivo("ativos_valorizados.xlsx")
        df = self.adicionar_categoria_p4(df)
        df = self.adicionar_percentual_ideal_p5(df)
        df = self.ajustar_ativo_excedente_p7(df)
        #diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        #caminho_arquivo = os.path.join(diretorio_atual, 'preco_medio.xlsx')
        #df = pd.read_excel(caminho_arquivo)

        display(tabulate(df, headers='keys', tablefmt='psql'))
        df = self.definir_valor_ativo_total8(df)
        df = df.filter(regex='^(?!Unnamed)')
        display(tabulate(df, headers='keys', tablefmt='psql'))
        # ii.salvar_resumo(True, df);
        self.salvar_arquivo(df, "ativos_valorizados_etapas.xlsx")



    def definir_percentual_categoria(self):
        pi = ProcessarInvestimento()
        ativos = self.ler_arquivo('ativos_valorizados_etapas.xlsx')
        ativos = pi.adicionar_percentual_ideal_categoria_p9(ativos)
        ativos = pi.adicionar_percentual_real_categoria_p10(ativos)
        ativos = ativos.filter(regex='^(?!Unnamed)')
        display(tabulate(ativos, headers='keys', tablefmt='psql'))
        print(os.getcwd())
        self.salvar_arquivo(ativos, "ativos_valorizados_etapas.xlsx")

        diretorio_atual = os.getcwd()

        # Voltando um diretório
        print(os.getcwd())
        os.chdir(os.path.dirname(diretorio_atual))
        # Salvando o DataFrame no diretório anterior
        print(os.getcwd())
        #ativos.to_csv("/arquivos/meu_arquivo.csv")

        # Imprimindo o diretório atual

    def salvar_arquivo(self, ativos, nomeArquivo):
        diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_arquivo = os.path.join(diretorio_atual, "arquivos", nomeArquivo)
        ativos.to_excel(caminho_arquivo, index=False)

    def ler_arquivo(self, nomeArquivo):
        diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_arquivo = os.path.join(diretorio_atual, "arquivos",  nomeArquivo)
        return pd.read_excel(caminho_arquivo)


    def identificar_aportes(self):
        ativos = self.ler_arquivo('ativos_valorizados_etapas.xlsx')
        ativos = self.adicionar_percentual_ativo_ideal_vs_atual_p11(ativos)
        ativos = self.adicionar_diferenca_percentual_categoria_ideal_vs_real_p12(
            ativos)
        ativos = self.adicionar_diferenca_percentual_ativo_ideal_vs_real_p13(ativos)
        ativos = self.calcula_valor_ativo_balancear_p14(ativos)
        self.salvar_arquivo(ativos, "ativos_valorizados_etapas.xlsx")
        display(tabulate(ativos, headers='keys', tablefmt='psql'))

    def gerar_valorizacao(self):
        ativos = self.ler_arquivo('ativos_valorizados_etapas.xlsx')
        # Criando a carteira com os dados dos ativos
        rentabilidade = Rentabilidade(ativos)
        df = rentabilidade.relatorio_valorizacao_carteira()
        self.salvar_arquivo(df, "ativos_valorizados_final.xlsx")
