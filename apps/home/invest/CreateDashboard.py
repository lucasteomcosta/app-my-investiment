from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import os

from .Investimento import Investimento


# from ..models import Carteira, Ativo
import pymongo

class CreateDashboard:

    def obter_movimentacao(self):

        print("=========================INIT=========================")
        invest = Investimento()

        diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_arquivo = os.path.join(diretorio_atual, 'movimentacao_saida.xlsx')
        df = invest.obter_dados_carteiras()
        #df = pd.read_excel(caminho_arquivo)
        #df = invest.find_by_max_data_pre_carteira()

        print("=========================SAVE=========================")
        # for _, row in df.iterrows():
        #   ativo = Ativo(**row.to_dict())
        #   #ativo.save()
        #   carteira.ativos.append(ativo)

        # Salve a carteira novamente para atualizar a lista de ativos
        # carteira.save()
        return df, invest



    def obter_dash_pizza_percetual_por_categoria(self, invest, df):
        pizza_percetual_por_categoria = invest.obter_dados_grafico_pizza_percentual_real_por_catgoria(df)


        pizza_percetual_por_categoria_copy = pizza_percetual_por_categoria.copy()
        pizza_percetual_por_categoria_copy = pizza_percetual_por_categoria_copy[pizza_percetual_por_categoria_copy['Categoria'] != 'Outras']
        pizza_percetual_por_categoria_copy['total_por_categoria'] = df.groupby('Categoria')['valor_ativo_total'].transform('sum')
        pizza_percetual_por_categoria_copy['Categoria'] = ((pizza_percetual_por_categoria_copy['Categoria'] +
                                                            ' (' + pizza_percetual_por_categoria_copy['perc_ideal_cat'].astype(str) + ')') +
                                                           ' (' + pizza_percetual_por_categoria_copy['total_por_categoria'].astype(str) + ')')




        fig_pizza_por_categoria = go.Figure(data=[go.Pie(labels=pizza_percetual_por_categoria_copy['Categoria'],
                                                         values=pizza_percetual_por_categoria_copy['perc_real_cat'])])
        fig_pizza_por_categoria.update_traces(textinfo='label', textposition='inside', insidetextorientation='radial',
                                              insidetextfont=dict(color='white'))
        fig_pizza_por_categoria.update_layout(showlegend=True,
            title='Composição da Carteira',
            template='plotly_dark', width=800, height=600, autosize=True)

        return fig_pizza_por_categoria

    def obter_dash_percetual_ajuste_categoria(self, invest, df):
        bar_percetual_ajuste_categoria = invest.obter_dados_grafico_barras_percentual_ajuste_por_categoria(df)
        fig_bar_percetual_ajuste_categoria = go.Figure(data=[go.Bar(x=bar_percetual_ajuste_categoria['Categoria'],
                                                                    y=bar_percetual_ajuste_categoria[
                                                                        'vs_perc_categoria'])])
        fig_bar_percetual_ajuste_categoria.update_layout(
            title='Percentual de ajuste por Categoria',
            template='plotly_dark')
        return fig_bar_percetual_ajuste_categoria

    def obter_dash_bar_valor_ajuste_categoria(self, invest, df):
        bar_valor_ajuste_categoria = invest.obter_dados_grafico_barras_percentual_ajuste_por_categoria(df)
        fig_bar_valor_ajuste_categoria = go.Figure(data=[
            go.Bar(x=bar_valor_ajuste_categoria['Categoria'], y=bar_valor_ajuste_categoria['ajuste_categoria_val'])])
        fig_bar_valor_ajuste_categoria.update_traces(text=bar_valor_ajuste_categoria['ajuste_categoria_val'],
                                                     textposition='inside')
        fig_bar_valor_ajuste_categoria.update_layout(
            title='Valor de ajuste por Categoria',
            template='plotly_dark')
        return fig_bar_valor_ajuste_categoria

    def obter_dash_bar_valor_ajuste_por_ativo(self, invest, df):
        bar_valor_ajuste_por_ativo = invest.obter_dados_grafico_barras_valor_de_ajuste_por_ativo(df)
        bar_valor_ajuste_por_ativo['cat_valor_ativo'] = bar_valor_ajuste_por_ativo['Categoria'] + ' (' + \
                                                        bar_valor_ajuste_por_ativo['ajuste_ativo_val'].astype(
                                                            str) + '%)'
        fig_bar_valor_ajuste_por_ativo = go.Figure(data=[
            go.Bar(x=bar_valor_ajuste_por_ativo['Ativo'], y=bar_valor_ajuste_por_ativo['ajuste_ativo_val'],
                   text=bar_valor_ajuste_por_ativo['cat_valor_ativo'])])

        # fig_bar_valor_ajuste_por_ativo.update_traces(text=bar_valor_ajuste_por_ativo['ajuste_ativo_val'], textposition='inside')
        fig_bar_valor_ajuste_por_ativo.update_layout(
            title='Valor de ajuste por Ativo',
            template='plotly_dark'
        )
        return fig_bar_valor_ajuste_por_ativo
