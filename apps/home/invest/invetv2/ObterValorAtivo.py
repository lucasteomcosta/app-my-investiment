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


class ObterValorAtivo:

    def obter_valor_ativo(self, ativo):
        map_criptomoedas = {'BTC': 'bitcoin', 'ETH': 'ethereum', 'LINK': 'chainlink', 'DOT': 'polkadot'}
        try:
            if ativo.startswith('Tesouro'):
                if ativo.lower() == 'Tesouro Selic 2026'.lower():
                    return self.obter_valores_outros_ativos('SELIC_2026')
                if ativo.lower() == 'Tesouro IPCA+ 2045'.lower():
                    return self.obter_valores_outros_ativos('IPCA_2045')
                if ativo.lower() == 'TESOURO SELIC 2029'.lower():
                    return self.obter_valores_outros_ativos('SELIC_2029')
                if ativo.lower() == 'TESOURO SELIC 2027'.lower():
                    return self.obter_valores_outros_ativos('SELIC_2027')
                if ativo.lower() == 'TESOURO IPCA+ 2026'.lower():
                    return self.obter_valores_outros_ativos('IPCA_2026')
                else:
                    return 0
            if ativo in map_criptomoedas:
                print('----- cripto_moeda ------' + ativo)
                return self.obter_valores_outros_ativos(ativo)
            if ativo.find('GARDE_PORTHOS_FIC_FIM') != -1:
                return self.obter_valores_outros_ativos('PORTHOS')
            if ativo.find('KINEA_ATLAS_II_FIM') != -1:
                return self.obter_valores_outros_ativos('KINEA_ATLAS_II_FIM')
            if ativo.find('ABSOLUTE_VERTEX_FUNDO') != -1:
                return self.obter_valores_outros_ativos('ABSOLUTE_VERTEX_FUNDO')
            if ativo.find('INTER_ACCESS_LEGACY_CAPITAL_FIC_FIM') != -1:
                return self.obter_valores_outros_ativos('ACCESS_LEGACY')
            if ativo.find('CDB_BANCO_DAYCOVAL') != -1:
                # valor = self.obter_valores_outros_ativos('CDB_BANCO_DAYCOVAL')
                return 13589
            if ativo.find('WA_IMAB5_ATIVO_FI_RF') != -1:
                return self.obter_valores_outros_ativos('WA_IMAB5_ATIVO_FI_RF')

            ticker = yf.Ticker(ativo + ".SA")
            print('obetendo valor... ' + ativo)
            dados = ticker.history(period='1d')  # Obter os dados do dia
            return dados['Close'][0]  # Retornar o valor de fechamento do dia mais recente
        except:
            return None  # Caso não seja possível obter os dados do ativo, retornar None

    def obter_valores_outros_ativos(self, tipoAtivo):
        print('----- obter_valores_outros_ativos ------' + tipoAtivo)
        # def get_crypto_prices(crypto):
        url = 'https://9gsghuh581.execute-api.us-east-1.amazonaws.com/default/lambda-data-investment'

        # Parâmetros da API para obter os preços em reais (BRL)
        params = {
            'tipoAtivo': tipoAtivo
        }
        try:
            print('recuperando valor ativo.... ' + tipoAtivo)
            response = requests.get(url, params=params)
            response.raise_for_status()  # Verificar se a requisição foi bem-sucedida

            data = response.json()

            print(data)
            print('valor recuperado:  ' + tipoAtivo)
            if data is not None:
                # Converta x em um valor decimal usando o NumPy
                data = np.float64(data)
                print("valor convertido: " + str(data))
            return data

        except requests.exceptions.RequestException as e:
            print(f"Erro ao obter os dados: {e}")
