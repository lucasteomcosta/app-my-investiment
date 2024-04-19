from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import os

from . import ProcessarInvestimento


# from ..models import Carteira, Ativo
import pymongo

from ..Investimento import Investimento


class CreateDashboard:

    def obter_movimentacao(self):

        print("=========================New version=========================")
        invest = Investimento()
        df = self.ler_arquivo("ativos_valorizados_final.xlsx")
       # diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        #caminho_arquivo = os.path.join(diretorio_atual, 'movimentacao_saida.xlsx')
        #df = invest.obter_dados_carteiras()
        #df = pd.read_excel(caminho_arquivo)
        #df = invest.find_by_max_data_pre_carteira()


        # for _, row in df.iterrows():
        #   ativo = Ativo(**row.to_dict())
        #   #ativo.save()
        #   carteira.ativos.append(ativo)

        # Salve a carteira novamente para atualizar a lista de ativos
        # carteira.save()
        return df, invest

    def salvar_arquivo(self, ativos, nomeArquivo):
        diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_arquivo = os.path.join(diretorio_atual, "arquivos", nomeArquivo)
        ativos.to_excel(caminho_arquivo, index=False)

    def ler_arquivo(self, nomeArquivo):
        diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_arquivo = os.path.join(diretorio_atual, "arquivos",  nomeArquivo)
        return pd.read_excel(caminho_arquivo)

    def obter_dash_pizza_percetual_por_categoria(self, invest, df):


        # Obter dados do gráfico pizza
        pizza_percetual_por_categoria = invest.obter_dados_grafico_pizza_percentual_real_por_catgoria(df)

        # Filtrar categoria 'Outras'
        pizza_percetual_por_categoria_copy = pizza_percetual_por_categoria.copy()
        pizza_percetual_por_categoria_copy = pizza_percetual_por_categoria_copy[
            pizza_percetual_por_categoria_copy[ProcessarInvestimento.CATEGORIA] != ProcessarInvestimento.CATEGORIA_OUTRAS
            ]

        # Adicionar coluna com total por categoria
        pizza_percetual_por_categoria_copy['total_por_categoria'] = df.groupby(
            ProcessarInvestimento.CATEGORIA
        )[ProcessarInvestimento.VALOR_ATIVO_TOTAL].transform('sum')

        # Formatar rótulos do gráfico
        pizza_percetual_por_categoria_copy[ProcessarInvestimento.CATEGORIA] = (
                pizza_percetual_por_categoria_copy[ProcessarInvestimento.CATEGORIA]
                + ' ('
                + pizza_percetual_por_categoria_copy[ProcessarInvestimento.PERC_IDEAL_CAT].astype(str)
                + ') ('
                + pizza_percetual_por_categoria_copy['total_por_categoria'].astype(str)
                + ')'
        )

        # Criar o gráfico pizza
        fig_pizza_por_categoria = go.Figure(
            data=[
                go.Pie(
                    labels=pizza_percetual_por_categoria_copy[ProcessarInvestimento.CATEGORIA],
                    values=pizza_percetual_por_categoria_copy[ProcessarInvestimento.PERC_REAL_CAT],
                )
            ]
        )

        # Atualizar formatação do gráfico
        fig_pizza_por_categoria.update_traces(
            textinfo='label',
            textposition='inside',
            insidetextorientation='radial',
            insidetextfont=dict(color='white'),
        )
        fig_pizza_por_categoria.update_layout(
            showlegend=True,
            title='Composição da Carteira',
            template='plotly_dark',
            width=800,
            height=600,
            autosize=True,
        )
        print("=========================fig_pizza_por_categoria=========================")
        return fig_pizza_por_categoria


    def obter_dash_percetual_ajuste_categoria(self, invest, df):

        # Obter dados do gráfico
        bar_percetual_ajuste_categoria = invest.obter_dados_grafico_barras_percentual_ajuste_por_categoria(df)

        # Criar o gráfico
        fig_bar_percetual_ajuste_categoria = go.Figure(
            data=[
                go.Bar(
                    x=bar_percetual_ajuste_categoria[ProcessarInvestimento.CATEGORIA],
                    y=bar_percetual_ajuste_categoria['vs_perc_categoria'],
                )
            ]
        )

        # Atualizar layout
        fig_bar_percetual_ajuste_categoria.update_layout(
            title='Percentual de ajuste por Categoria',
            template='plotly_dark',
        )
        print("=========================fig_bar_percetual_ajuste_categoria=========================")
        return fig_bar_percetual_ajuste_categoria


    def obter_dash_bar_valor_ajuste_categoria(self, invest, df):
        # Obter dados do gráfico
        bar_valor_ajuste_categoria = invest.obter_dados_grafico_barras_percentual_ajuste_por_categoria(df)

        # Criar o gráfico
        fig_bar_valor_ajuste_categoria = go.Figure(
            data=[
                go.Bar(
                    x=bar_valor_ajuste_categoria[ProcessarInvestimento.CATEGORIA],
                    y=bar_valor_ajuste_categoria['ajuste_categoria_val'],
                    text=bar_valor_ajuste_categoria['ajuste_categoria_val'],
                )
            ]
        )

        # Atualizar layout e formatação
        fig_bar_valor_ajuste_categoria.update_traces(textposition='inside')
        fig_bar_valor_ajuste_categoria.update_layout(
            title='Valor de ajuste por Categoria',
            template='plotly_dark',
        )
        print("=========================fig_bar_valor_ajuste_categoria=========================")
        return fig_bar_valor_ajuste_categoria


    def obter_dash_bar_valor_ajuste_por_ativo(self, invest, df):
        bar_valor_ajuste_por_ativo = invest.obter_dados_grafico_barras_valor_de_ajuste_por_ativo(df)

        # Formatar rótulos
        bar_valor_ajuste_por_ativo['cat_valor_ativo'] = (
                bar_valor_ajuste_por_ativo[ProcessarInvestimento.CATEGORIA]
                + ' ('
                + bar_valor_ajuste_por_ativo['ajuste_ativo_val'].astype(str)
                + '%)'
        )

        # Criar o gráfico
        fig_bar_valor_ajuste_por_ativo = go.Figure(
            data=[
                go.Bar(
                    x=bar_valor_ajuste_por_ativo[ProcessarInvestimento.ATIVO],
                    y=bar_valor_ajuste_por_ativo['ajuste_ativo_val'],
                    text=bar_valor_ajuste_por_ativo['cat_valor_ativo'],
                )
            ]
        )

        # Atualizar layout e formatação
        fig_bar_valor_ajuste_por_ativo.update_traces(textposition='inside')
        fig_bar_valor_ajuste_por_ativo.update_layout(
            title='Valor de ajuste por Ativo',
            template='plotly_dark',
        )
        print("=========================fig_bar_valor_ajuste_por_ativo=========================")
        return fig_bar_valor_ajuste_por_ativo

