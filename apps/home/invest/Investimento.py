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


from apps.home.invest.Cateira import Carteira
from apps.home.invest.ConexaoMongoDB import ConexaoMongoDB


class Investimento:

    def importar_p1(self):
        print('----- IMPORTAR_P1 ------')
        diretorio_atual = os.path.dirname(os.path.abspath(__file__))

        caminho_arquivo = os.path.join(diretorio_atual, 'movimentacao.xlsx')
        mov_total_2023_df = pd.read_excel(caminho_arquivo)
        opcoes = ['Transferência - Liquidação', 'Venda', 'Compra']
        mov_total_2023_df = mov_total_2023_df.loc[
            mov_total_2023_df["Movimentação"].isin(opcoes), ["Entrada/Saída", "Data", "Produto", "Quantidade", "Preço unitário",
                                                             "Valor da Operação"]]
        return mov_total_2023_df
        # --------------------------- MERGE COM ALTERNATIVOS
    def merge_outros_ativos(self, mov_total_2023_df):
        print('----- MERGE_OUTROS_ATIVOS ------')

        diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_arquivo = os.path.join(diretorio_atual, 'outros_ativos.xlsx')
        alternativos_df = pd.read_excel(caminho_arquivo)
        # mov_total_2023_df = pd.concat([mov_total_2023_df, alternativos_df], ignore_index=True)
        mov_total_2023_df = mov_total_2023_df.loc[:,
                            ['Entrada/Saída', 'Data', 'Produto', 'Quantidade', 'Preço unitário', 'Valor da Operação']]
        mov_total_2023_df = pd.concat([mov_total_2023_df, alternativos_df], ignore_index=True)

        self.imprimir(mov_total_2023_df)
        return mov_total_2023_df

        # --------------------------- --------------------------- --------------------------- --------------------------- --------------------------- ---------------------------

    def imprimir(self, df):
       if False == True:
        display(tabulate(df, headers='keys', tablefmt='psql'))

    def imprimir_se(self, df, imprimir):
        if imprimir:
            display(tabulate(df, headers='keys', tablefmt='psql'))

    def cria_coluna_ativo_p2(self, mov_total_2023_df):
        # cria a coluna ativo e se for tesouro mantem o valor
        print('----------cria_coluna_ativo_p2-----------------')
        def tratar_ativo(valor):
            if valor.startswith('Tesouro'):
                return valor
            else:
                return valor.split()[0]

        # cria uma nova coluna ativo, pegando a primeira palavra da coluna produto e ou mantendo se for tesouro
        # mov_apenas_ativos_df['Ativo'] = mov_apenas_ativos_df['Produto'].apply(tratar_ativo)
        mov_total_2023_df.insert(mov_total_2023_df.columns.get_loc('Produto') + 1, 'Ativo',
                                 mov_total_2023_df['Produto'].apply(tratar_ativo))
        self.imprimir(mov_total_2023_df)
        #self.imprimir(mov_total_2023_df)
        return mov_total_2023_df
        # --------------------------- --------------------------- --------------------------- --------------------------- --------------------------- ---------------------------


        # --- cria tabela com  valor de compra, venda e preço medio

        # Função para calcular quantidade de compra/venda
    def calcular_quantidade_compra_venda(self, ativo, tipo, mov_total_2023_df):
        # Filtra os dados apenas para o ativo específico
        filtro_ativo = mov_total_2023_df[mov_total_2023_df['Ativo'] == ativo]

        # Soma as quantidades de compra (Crédito positivo) e venda (Débito negativo)
        if tipo == 'compra':
            return filtro_ativo.loc[filtro_ativo['Entrada/Saída'] == 'Credito', 'Quantidade'].sum()
        if tipo == 'venda':
            return filtro_ativo.loc[filtro_ativo['Entrada/Saída'] == 'Debito', 'Quantidade'].sum()
        if tipo == 'pm':
            totalValOperacao = filtro_ativo.loc[filtro_ativo['Entrada/Saída'] == 'Credito', 'Valor da Operação'].sum()
            quantidadeTotal = filtro_ativo.loc[filtro_ativo['Entrada/Saída'] == 'Credito', 'Quantidade'].sum()
            return totalValOperacao / quantidadeTotal
        if tipo == 'quantidade':
            compra = filtro_ativo.loc[filtro_ativo['Entrada/Saída'] == 'Credito', 'Quantidade'].sum()
            venda = filtro_ativo.loc[filtro_ativo['Entrada/Saída'] == 'Debito', 'Quantidade'].sum()
            return compra - venda

    def criar_colunas_compra_venda_preco_medio_p3(self, mov_total_2023_df):
        print('----- criar_colunas_compra_venda_preco_medio_p3 ------')
        # mov_ativo_comp_vend_df = mov_total_2023_df["Ativo"]
        dados_carteira_evol_df = mov_total_2023_df.loc[:, ["Ativo", 'Quantidade']]
        dados_carteira_evol_df = dados_carteira_evol_df.drop_duplicates(subset='Ativo')
        # print(dados_carteira_evol_df)

        # quant_final_df = calcular_quantidade_compra_venda(ativo_especifico)
        # df['Idade_Neg'] = df['Idade'].apply(lambda x: separar_valores_positivos_negativos(x)[1])

        dados_carteira_evol_df['Compra'] = dados_carteira_evol_df['Ativo'].apply( lambda ativo: self.calcular_quantidade_compra_venda(ativo, 'compra', mov_total_2023_df))
        dados_carteira_evol_df['Venda'] = dados_carteira_evol_df['Ativo'].apply(
            lambda ativo: self.calcular_quantidade_compra_venda(ativo, 'venda', mov_total_2023_df))
        dados_carteira_evol_df['Preco_medio'] = dados_carteira_evol_df['Ativo'].apply(
            lambda ativo: self.calcular_quantidade_compra_venda(ativo, 'pm', mov_total_2023_df))
        dados_carteira_evol_df['Quantidade'] = dados_carteira_evol_df['Ativo'].apply(
            lambda ativo: self.calcular_quantidade_compra_venda(ativo, 'quantidade', mov_total_2023_df))

        self.imprimir('VERSÃO CORRETA')
        self.imprimir(dados_carteira_evol_df)
        return dados_carteira_evol_df
        # --------------------------- --------------------------- --------------------------- --------------------------- --------------------------- ---------------------------
    def obter_template_carteira(self):
        diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_arquivo = os.path.join(diretorio_atual, 'carteira.xlsx')
        return  pd.read_excel(caminho_arquivo)


    # Função para calcular quantidade de compra/venda
    def setar_categorial(self, ativo, template_carteira):
        # Filtra os dados apenas para o ativo específico
        if ativo.startswith('Tesouro'):
            if ativo == 'Tesouro Selic 2026':
                return 'RENDA_FIXA_POS'
            if ativo == 'Tesouro IPCA+ 2045':
                return 'RENDA_FIXA_DINAMICA'
            else:
                return 'OUTRAS'

        filtro_ativo = template_carteira[template_carteira['Ativo'] == ativo]
        if filtro_ativo.empty:
            return 'OUTRAS'

        retorno = filtro_ativo.loc[filtro_ativo['Ativo'] == ativo, 'Categoria'].values[0]
        return retorno


    def adicionar_registros(self, tabela_principal, tabela_nova):
        print('----- adicionar_registros ------')
        colunas_faltantes = set(tabela_nova.columns) - set(tabela_principal.columns)

        for coluna in colunas_faltantes:
            tabela_principal[coluna] = 0

        registros_novos = tabela_nova[~tabela_nova['Ativo'].isin(tabela_principal['Ativo'])]
        registros_novos = registros_novos.loc[registros_novos['Ativo'] != 'TESOURO-IPCA-2045']
        registros_novos = registros_novos.loc[registros_novos['Ativo'] != 'TESOURO-SELIC-2026']

        #tabela_principal = tabela_principal.append(registros_novos, ignore_index=True)
        tabela_principal = pd.concat([tabela_principal, registros_novos], ignore_index=True)
        # Preenchendo com 0 nas colunas numéricas para converter valores NaN
        colunas_numericas = tabela_principal.select_dtypes(include=[float, int]).columns
        tabela_principal[colunas_numericas] = tabela_principal[colunas_numericas].fillna(0)

        return tabela_principal

    def adicionar_categoria_p4(self, dados_carteira_evol_df):
        print('----- adicionar_categoria_p4 ------')
        self.imprimir(dados_carteira_evol_df)
        template_carteira = self.obter_template_carteira()
        dados_carteira_evol_df.insert(0, 'Categoria', dados_carteira_evol_df['Ativo'].apply(lambda ativo: self.setar_categorial(ativo, template_carteira)))
        dados_carteira_evol_df = dados_carteira_evol_df.sort_values(by='Categoria')

        self.imprimir(dados_carteira_evol_df)
        dados_carteira_evol_df = self.adicionar_registros(dados_carteira_evol_df, template_carteira)
        dados_carteira_evol_df = dados_carteira_evol_df.sort_values(by='Categoria')
        self.imprimir(dados_carteira_evol_df)


        return dados_carteira_evol_df

        # --------------------------- --------------------------- --------------------------- --------------------------- --------------------------- ---------------------------

        # ---- Adiciona Percentual Ideal por ativo

    def setar_percentual(self, ativo):
        # Filtra os dados apenas para o ativo específico
        template_carteira = self.obter_template_carteira()
        if ativo.startswith('Tesouro'):
            if ativo == 'Tesouro Selic 2026':
                ativo = 'TESOURO-SELIC-2026'
            else:
                if ativo == 'Tesouro IPCA+ 2045':
                    ativo = 'TESOURO-IPCA-2045'
                else:
                    return 0

        filtro_ativo = template_carteira[template_carteira['Ativo'] == ativo]

        if filtro_ativo.empty:
            return 0

        retorno = filtro_ativo.loc[filtro_ativo['Ativo'] == ativo, 'Percentual'].values[0]

        return retorno

    def adicionar_percentual_ideal_p5(self, dados_carteira_evol_df):
        print('----- adicionar_percentual_ideal_p5 ------')
        dados_carteira_evol_df['Percentual'] = dados_carteira_evol_df['Ativo'].apply(lambda ativo: self.setar_percentual(ativo))
        dados_carteira_evol_df = dados_carteira_evol_df.sort_values(by='Categoria')
        self.imprimir(dados_carteira_evol_df)
        return dados_carteira_evol_df
        # --------------------------- --------------------------- --------------------------- --------------------------- --------------------------- ---------------------------

        # ----------------------------------- OBTER DADOS CRIPTOMOEDAS --------------------------------------

    def obter_valores_cripto(self, crypto):
        print('----- obter_valores_cripto ------')
        cryptos = ['bitcoin', 'ethereum', 'chainlink', 'polkadot']
        #def get_crypto_prices(crypto):
        url = 'https://api.coingecko.com/api/v3/simple/price'

        # Parâmetros da API para obter os preços em reais (BRL)
        params = {
            'ids': ','.join(cryptos),
            'vs_currencies': 'brl'
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Verificar se a requisição foi bem-sucedida

            data = response.json()
            return data[crypto]['brl']

        except requests.exceptions.RequestException as e:
            print(f"Erro ao obter os dados: {e}")

    def obter_valores_outros_ativos(self, tipoAtivo):
        print('----- obter_valores_outros_ativos ------' +  tipoAtivo)
        #def get_crypto_prices(crypto):
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

            print( data)
            print('valor recuperado:  ' + tipoAtivo )
            if data is not None:
                # Converta x em um valor decimal usando o NumPy
                data = np.float64(data)
                print("valor convertido: " +  str(data))
            return data

        except requests.exceptions.RequestException as e:
            print(f"Erro ao obter os dados: {e}")




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
                return self.obter_valores_cripto(map_criptomoedas.get(ativo))
            if ativo.find('GARDE_PORTHOS_FIC_FIM') != -1:
                return self.obter_valores_outros_ativos('PORTHOS')
            if ativo.find('KINEA_ATLAS_II_FIM') != -1:
                return self.obter_valores_outros_ativos('KINEA_ATLAS_II_FIM')
            if ativo.find('ABSOLUTE_VERTEX_FUNDO') != -1:
                return self.obter_valores_outros_ativos('ABSOLUTE_VERTEX_FUNDO')
            if ativo.find('INTER_ACCESS_LEGACY_CAPITAL_FIC_FIM') != -1:
                return self.obter_valores_outros_ativos('ACCESS_LEGACY')
            if ativo.find('CDB_BANCO_DAYCOVAL') != -1:
               #valor = self.obter_valores_outros_ativos('CDB_BANCO_DAYCOVAL')
               return 12021
            if ativo.find('WA_IMAB5_ATIVO_FI_RF') != -1:
                return self.obter_valores_outros_ativos('WA_IMAB5_ATIVO_FI_RF')

            ticker = yf.Ticker(ativo + ".SA")
            print('obetendo valor... ' + ativo )
            dados = ticker.history(period='1d')  # Obter os dados do dia
            return dados['Close'][0]  # Retornar o valor de fechamento do dia mais recente
            #return random.randint(1, 1000)
        except:
            return None  # Caso não seja possível obter os dados do ativo, retornar None


    def obter_valor_ativo2(self, ativo):
        map_criptomoedas = {'BTC': 'bitcoin', 'ETH': 'ethereum', 'LINK': 'chainlink', 'DOT': 'polkadot'}
        try:
            if ativo.startswith('Tesouro'):
                if ativo == 'Tesouro Selic 2026':
                    return 13707.44
                if ativo == 'Tesouro IPCA+ 2045':
                    return 1254.03
                if ativo.lower() == 'TESOURO SELIC 2029'.lower():
                    return 13657.22
                if ativo.lower() == 'TESOURO SELIC 2027'.lower():
                    return 13724.46
                if ativo.lower() == 'TESOURO IPCA+ 2026'.lower():
                    return 3562.07
                else:
                    return 0
            if ativo in map_criptomoedas:
                return self.obter_valores_cripto(map_criptomoedas.get(ativo))
            if ativo.find('GARDE_PORTHOS_FIC_FIM') != -1:
                return 1.3232 #self.obter_valores_garde_phorthos()
            if ativo.find('KINEA_ATLAS_II_FIM') != -1:
                return 2.0462
            if ativo.find('ABSOLUTE_VERTEX_FUNDO') != -1:
                return 1.3647
            if ativo.find('INTER_ACCESS_LEGACY_CAPITAL_FIC_FIM') != -1:
                return 1.4155
            if ativo.find('CDB_BANCO_DAYCOVAL') != -1:
                return 11606.12
            if ativo.find('WA_IMAB5_ATIVO_FI_RF') != -1:
                return 2.86

            ticker = yf.Ticker(ativo + ".SA")
            print('obetendo valor... ' + ativo )
            dados = ticker.history(period='1d')  # Obter os dados do dia
            return dados['Close'][0]  # Retornar o valor de fechamento do dia mais recente
            #return random.randint(1, 1000)
        except:
            return None  # Caso não seja possível obter os dados do ativo, retornar None

    def obter_valor_ativo_atual_p6(self, dados_carteira_evol_df):
        print('----- obter_valor_ativo_atual_p6 ------')
        #df_valores_recuperados =  dados_carteira_evol_df[['Categoria','Ativo']]
         # self.imprimir_se(df_valores_recuperados, True)

        #df_valores_recuperados['valor'] = df_valores_recuperados['Ativo'].apply(self.obter_valor_ativo)
        #self.imprimir_se(df_valores_recuperados, True)
        dados_carteira_evol_df['valor_ativo_atual'] = dados_carteira_evol_df['Ativo'].apply(self.obter_valor_ativo)


        # define valores não encontrado como zero
        dados_carteira_evol_df.loc[dados_carteira_evol_df['valor_ativo_atual'].isna(), 'valor_ativo_atual'] = 0
        print('----- dados_carteira_evol_df ------')
        self.imprimir_se(dados_carteira_evol_df, False)
        return dados_carteira_evol_df

        # --------------------------- --------------------------- --------------------------- --------------------------- --------------------------- ---------------------------

        # ---- Realizar ajuste de ativos excedentes

    def criar_linha_com_valor_execente(self, df, quantidade, ativo):
        print('----- criar_linha_com_valor_execente ------')
        # Verificar se já existe uma linha com a mesma categoria
        # if df[df['Categoria'] == categoria].empty:
        # Se não existir, cria uma nova linha com os dados informados
        preco_medio = df.loc[df['Ativo'] == ativo, 'Preco_medio'].values[0]
        valor_atual = df.loc[df['Ativo'] == ativo, 'Preco_medio'].values[0]

        nova_linha = {
            'Categoria': 'OUTRAS',
            'Ativo': ativo,
            'Quantidade': quantidade,
            'Compra': 0.0,
            'Venda': 0.0,
            'Preco_medio': preco_medio,
            'Percentual': 0.0,
            'valor_ativo_atual': valor_atual,
            'valor_ativo_total': 0.0
        }
        df = df.append(nova_linha, ignore_index=True)

        # else:
        # Se existir, atualiza a linha existente com a nova quantidade
        #   df.loc[df['Categoria'] == categoria, 'Quantidade'] = quantidade

        return df


    def ajustar_excedente(self, ativo, df):
        print('----- ajustar_excedente ------' + ativo)
        quantidade_ativo_excedente = df.loc[df['Ativo'] == ativo, 'Quantidade'].values[0]
        print("quantidade_ativo_excedente: " + str(quantidade_ativo_excedente))
        valor_ativo_excedente = df.loc[df['Ativo'] == ativo, 'valor_ativo_atual'].values[0]
        print("quantidade_ativo_excedente: " + str(quantidade_ativo_excedente))
        total_ativo_excedente = quantidade_ativo_excedente * valor_ativo_excedente
        print("total_ativo_excedente: " + str(total_ativo_excedente))
        if total_ativo_excedente > 5000:
            quantidade_ativo_ajustada = (quantidade_ativo_excedente * 5790) / total_ativo_excedente
            print("quantidade_ativo_ajustada: " + str(quantidade_ativo_ajustada))
            quantidade_restante = quantidade_ativo_excedente - quantidade_ativo_ajustada
            print("quantidade_ativo_ajustada: " + str(quantidade_ativo_ajustada))

            return quantidade_ativo_ajustada
            # df.loc[df['Ativo'] == ativo, 'Quantidade'] = quantidade_ipca_ajustada
        return quantidade_ativo_excedente

    def ajustar_ativo_excedente_p7(self, dados_carteira_evol_df):
        print("-----------ajustar_ativo_excedente_p7---------------")
        diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_completo = os.path.join(diretorio_atual, 'movimentacao_todos_ativos.xlsx')
        dados_carteira_evol_df.to_excel(caminho_completo, index=False)

        self.imprimir_se(dados_carteira_evol_df,True)
        dados_carteira_evol_df.loc[
            dados_carteira_evol_df['Ativo'] == 'Tesouro Selic 2026', 'Quantidade'] = self.ajustar_excedente(
            'Tesouro Selic 2026', dados_carteira_evol_df)
        dados_carteira_evol_df.loc[
            dados_carteira_evol_df['Ativo'] == 'Tesouro IPCA+ 2045', 'Quantidade'] = self.ajustar_excedente(
            'Tesouro IPCA+ 2045', dados_carteira_evol_df)

        self.imprimir_se(dados_carteira_evol_df,True)
        return dados_carteira_evol_df

        # --------------------------- --------------------------- --------------------------- --------------------------- --------------------------- ---------------------------

        # --- Adicionar valor total atualizado do ativo

    def setar_valor_atualizado_ativo(self, ativo, dados_carteira_evol_copy_df):
        # Filtra os dados apenas para o ativo específico
        filtro_ativo = dados_carteira_evol_copy_df[dados_carteira_evol_copy_df['Ativo'] == ativo]
        if filtro_ativo.empty:
            return 0
        retorno = filtro_ativo.loc[filtro_ativo['Ativo'] == ativo, 'Quantidade'].values[0] * \
                  filtro_ativo.loc[filtro_ativo['Ativo'] == ativo, 'valor_ativo_atual'].values[0]
        return retorno

    def atualizar_valor_ativo_p8(self, dados_carteira_evol_df):
        print('----- atualizar_valor_ativo_p8 ------')
        dados_carteira_evol_df['valor_ativo_total'] = dados_carteira_evol_df['Ativo'].apply(
            lambda ativo: self.setar_valor_atualizado_ativo(ativo, dados_carteira_evol_df))
        dados_carteira_evol_df = dados_carteira_evol_df.round(2)
        self.imprimir_se(dados_carteira_evol_df, False)

        return dados_carteira_evol_df
        # --------------------------- --------------------------- --------------------------- --------------------------- --------------------------- ---------------------------

        # --- Adicionar percentual ideal categoria

    def seta_percentual_ideal_categoria(self, categoria, groupby_percentual_ideal_categoria_df):
        # Filtra os dados apenas para o ativo específico

        percentual_ideal_por_categoria = groupby_percentual_ideal_categoria_df.loc[
            groupby_percentual_ideal_categoria_df['Categoria'] == categoria, 'Percentual'].values[0]

        return percentual_ideal_por_categoria

    def adicionar_percentual_ideal_categoria_p9(self, dados_carteira_evol_copy_df):
        print('----- adicionar_percentual_ideal_categoria_p9 ------')
        groupby_percentual_ideal_categoria_df = dados_carteira_evol_copy_df.groupby('Categoria', as_index=False)[
            'Percentual'].sum()
        print(groupby_percentual_ideal_categoria_df.loc[
                  groupby_percentual_ideal_categoria_df['Categoria'] != 'OUTRAS', 'Percentual'].sum())
        dados_carteira_evol_copy_df['perc_ideal_cat'] = dados_carteira_evol_copy_df['Categoria'].apply(
            lambda categoria: self.seta_percentual_ideal_categoria(categoria, groupby_percentual_ideal_categoria_df))

        self.imprimir_se(dados_carteira_evol_copy_df, False)
        return dados_carteira_evol_copy_df
        # --------------------------- --------------------------- --------------------------- --------------------------- --------------------------- ---------------------------

        # --- Adicionar percentual real categoria

    def seta_percentual_por_categoria(self, categoria, total_investido, groupby_categoria_ativo_df):
        total_por_categoria = \
            groupby_categoria_ativo_df.loc[groupby_categoria_ativo_df['Categoria'] == categoria, 'valor_ativo_total'].values[0]
        retorno = (total_por_categoria / total_investido) * 100
        return retorno

    def adicionar_percentual_real_categoria_p10(self, dados_carteira_evol_copy_df):
        print('----- adicionar_percentual_real_categoria_p10 ------')
        groupby_categoria_ativo_df = dados_carteira_evol_copy_df.groupby('Categoria', as_index=False)['valor_ativo_total'].sum()
        self.imprimir(groupby_categoria_ativo_df)
        total_investido = groupby_categoria_ativo_df.loc[
            groupby_categoria_ativo_df['Categoria'] != 'OUTRAS', 'valor_ativo_total'].sum()
        display(total_investido)
        print(groupby_categoria_ativo_df.loc[groupby_categoria_ativo_df['Categoria'] == 'OUTRAS', 'valor_ativo_total'].sum())

        dados_carteira_evol_copy_df['perc_real_cat'] = dados_carteira_evol_copy_df['Categoria'].apply(
            lambda categoria: self.seta_percentual_por_categoria(categoria, total_investido, groupby_categoria_ativo_df))
        dados_carteira_evol_copy_df = dados_carteira_evol_copy_df.sort_values(by='Categoria', ascending=False)
        self.imprimir(dados_carteira_evol_copy_df)
        return dados_carteira_evol_copy_df
        # --------------------------- --------------------------- --------------------------- --------------------------- --------------------------- ---------------------------

        # --- Adicionar percentual ideal do ativo vs percentual atual do ativo

    def seta_percentual_ativo_atualizado_categoria(self, ativo, total_investido, dados_carteira_evol_copy_df):
        # Filtra os dados apenas para o ativo específico

        filtro_ativo = dados_carteira_evol_copy_df[dados_carteira_evol_copy_df['Ativo'] == ativo]
        if filtro_ativo.empty:
            return 0

        valor_total_ativo =   dados_carteira_evol_copy_df.loc[dados_carteira_evol_copy_df['Ativo'] == ativo, 'valor_ativo_total'].values[0]
        retorno = (valor_total_ativo / total_investido) * 100
        return retorno

    def adicionar_percentual_ativo_ideal_vs_atual_p11(self, dados_carteira_evol_copy_df):
        print('----- adicionar_percentual_ativo_ideal_vs_atual_p11 ------')
        groupby_categoria_ativo_df = dados_carteira_evol_copy_df.groupby('Categoria', as_index=False)['valor_ativo_total'].sum()
        total_investido = groupby_categoria_ativo_df.loc[
            groupby_categoria_ativo_df['Categoria'] != 'OUTRAS', 'valor_ativo_total'].sum()

        dados_carteira_evol_copy_df['perc_real_ativo'] = dados_carteira_evol_copy_df['Ativo'].apply(
            lambda ativo: self.seta_percentual_ativo_atualizado_categoria(ativo, total_investido, dados_carteira_evol_copy_df))

        self.imprimir(dados_carteira_evol_copy_df)
        return dados_carteira_evol_copy_df

        # --------------------------- --------------------------- --------------------------- --------------------------- --------------------------- ---------------------------


        # ---  DIFERENÇA ENTRE PERCENTUAL CATEGORIA IDEAL E PERCENTUAL ATUAL DA CATEGORIA

    def adicionar_diferenca_percentual_categoria_ideal_vs_real_p12(self, dados_carteira_evol_copy_df):
        print('----- adicionar_diferenca_percentual_categoria_ideal_vs_real_p12 ------')
        dados_carteira_evol_copy_df['vs_perc_categoria'] = dados_carteira_evol_copy_df['perc_real_cat'] - \
                                                           dados_carteira_evol_copy_df['perc_ideal_cat']

      #  print(dados_carteira_evol_copy_df)
        return dados_carteira_evol_copy_df
        # --------------------------- --------------------------- --------------------------- --------------------------- --------------------------- ---------------------------


        # ---  DIFERENÇA ENTRE PERCENTUAL ativo IDEAL E PERCENTUAL ATUAL Do ativo

    def adicionar_diferenca_percentual_ativo_ideal_vs_real_p13(self, dados_carteira_evol_copy_df):
        print('----- adicionar_diferenca_percentual_ativo_ideal_vs_real_p13 ------')
        dados_carteira_evol_copy_df['vs_perc_ativo'] = dados_carteira_evol_copy_df['perc_real_ativo'] -  dados_carteira_evol_copy_df['Percentual']
        self.imprimir_se(dados_carteira_evol_copy_df, False)
        return dados_carteira_evol_copy_df
        # --------------------------- --------------------------- --------------------------- --------------------------- --------------------------- ---------------------------


        # --- Qual o valor investir por ativo para balancear

    def definir_valor_ajuste_ativo(selef,ativo, patrimonio, apenasValor, dados_carteira_evol_copy_df):
        # Filtra os dados apenas para o ativo específico
        vs_perc_ativo = \
            dados_carteira_evol_copy_df.loc[dados_carteira_evol_copy_df['Ativo'] == ativo, 'vs_perc_ativo'].values[0]
        if vs_perc_ativo >= 0:
            return 0
        valor_ativo_atual = \
            dados_carteira_evol_copy_df.loc[dados_carteira_evol_copy_df['Ativo'] == ativo, 'valor_ativo_atual'].values[0]
        valor_sobre_patrimonio = (patrimonio * vs_perc_ativo * -1) / 100
        if apenasValor == True:
            return valor_sobre_patrimonio.round(2)

        total_valor_ajuste = valor_sobre_patrimonio / valor_ativo_atual
        return total_valor_ajuste.round(2)

    def calcula_valor_ativo_balancear_p14(self, dados_carteira_evol_copy_df):
        print('----- calcula_valor_ativo_balancear_p14 ------')
        total_investido = dados_carteira_evol_copy_df.loc[ dados_carteira_evol_copy_df['Categoria'] != 'OUTRAS', 'valor_ativo_total'].sum()
        print(total_investido)
        dados_carteira_evol_copy_df['ajuste_ativo_qtd'] = dados_carteira_evol_copy_df['Ativo'].apply( lambda ativo: self.definir_valor_ajuste_ativo(ativo, total_investido, False, dados_carteira_evol_copy_df))
        dados_carteira_evol_copy_df['ajuste_ativo_val'] = dados_carteira_evol_copy_df['Ativo'].apply( lambda ativo: self.definir_valor_ajuste_ativo(ativo, total_investido, True, dados_carteira_evol_copy_df))
        dados_carteira_evol_copy_df['ajuste_categoria_val'] = dados_carteira_evol_copy_df['Categoria'].apply( lambda categoria: dados_carteira_evol_copy_df.loc[ dados_carteira_evol_copy_df['Categoria'] == categoria, 'ajuste_ativo_val'].sum())
        total_investido = dados_carteira_evol_copy_df.loc[ dados_carteira_evol_copy_df['Categoria'] != 'OUTRAS', 'valor_ativo_total'].sum()
        print('total_investido: ')
        print(total_investido)
        self.imprimir_se(dados_carteira_evol_copy_df, False)
        dados_carteira_evol_copy_df.to_excel("movimentacao_saida.xlsx", index=False)
        return dados_carteira_evol_copy_df

    def definir_valores_real(self, dados_carteira_evol_copy_df):
        print('----- definir_valores_real ------')
        dados_carteira_evol_real = dados_carteira_evol_copy_df.copy()
        def formatar_moeda(valor):
            return format_currency(valor, currency='', locale='pt_BR') if isinstance(valor, (int, float)) else valor
        dados_carteira_evol_real = dados_carteira_evol_real.applymap(formatar_moeda)
        self.imprimir(dados_carteira_evol_real)


    def obter_dados_grafico_pizza_percentual_real_por_catgoria(self, dados_carteira_evol_copy_df):
        perc_real_por_categoria_df = dados_carteira_evol_copy_df.loc[
            dados_carteira_evol_copy_df['Categoria'] != 'OUTRAS'].drop_duplicates(subset='Categoria')
        return perc_real_por_categoria_df

        # --------------------------- --------------------------- --------------------------- --------------------------- --------------------------- ---------------------------

    def obter_dados_grafico_barras_valor_de_ajuste_por_ativo(self, dados_carteira_evol_copy_df):
        dados_carteira_evol_copy_df = dados_carteira_evol_copy_df[dados_carteira_evol_copy_df['Categoria'] != 'OUTRAS']
        df_filtered = dados_carteira_evol_copy_df[dados_carteira_evol_copy_df['ajuste_ativo_val'] != 0]
        df_filtered = df_filtered.sort_values(by='vs_perc_categoria', ascending=True)
        return df_filtered

    def obter_percentual_investido(self, dados_carteira_evol_copy_df):
        df_filtered = dados_carteira_evol_copy_df[dados_carteira_evol_copy_df['Categoria'] != 'OUTRAS']
        self.imprimir_se(df_filtered, True)
        df_filtered['valorizacao'] = df_filtered['Ativo'].apply( lambda ativo: self.calcular_valorizacao_ativo(ativo, df_filtered))
        df_filtered['valorizacao_valor'] = df_filtered['Ativo'].apply( lambda ativo: self.calcular_valorizacao_valor_ativo(ativo, df_filtered))

        df_filtered = df_filtered.sort_values(by='vs_perc_categoria', ascending=True)
        #self.imprimir_se(df_filtered, True)
        return df_filtered

    def obter_dados_df_ativo(self, dados_carteira_evol_copy_df):
        df_filtered = dados_carteira_evol_copy_df[dados_carteira_evol_copy_df['Categoria'] != 'OUTRAS']
        self.imprimir_se(df_filtered, True)
        df_filtered['valorizacao'] = df_filtered['Ativo'].apply( lambda ativo: self.calcular_valorizacao_ativo(ativo, df_filtered))
        df_filtered['valorizacao_valor'] = df_filtered['Ativo'].apply( lambda ativo: self.calcular_valorizacao_valor_ativo(ativo, df_filtered))

        df_filtered = df_filtered.sort_values(by='vs_perc_categoria', ascending=True)
        #self.imprimir_se(df_filtered, True)
        return df_filtered

    def calcular_valorizacao_ativo(self, ativo, df_filtrado):
        valor_compra =  df_filtrado.loc[df_filtrado['Ativo'] == ativo, 'Preco_medio'].values[0]
        valor_ativo_atual =  df_filtrado.loc[df_filtrado['Ativo'] == ativo, 'valor_ativo_atual'].values[0]
        percentual_rentabilidade = ((valor_ativo_atual - valor_compra)/valor_compra) * 100

        return percentual_rentabilidade

    def calcular_valorizacao_valor_ativo(self, ativo, df_filtrado):
        valor_compra =  df_filtrado.loc[df_filtrado['Ativo'] == ativo, 'Preco_medio'].values[0]
        quantidade =  df_filtrado.loc[df_filtrado['Ativo'] == ativo, 'Quantidade'].values[0]
        valor_ativo_total =  df_filtrado.loc[df_filtrado['Ativo'] == ativo, 'valor_ativo_total'].values[0]
        valor_total_compra = quantidade * valor_compra
        rentabilidade_valor = valor_ativo_total - valor_total_compra
        return rentabilidade_valor

    def obter_dados_grafico_barras_percentual_ajuste_por_categoria(self, dados_carteira_evol_copy_df):
        df_filtered = dados_carteira_evol_copy_df[dados_carteira_evol_copy_df['Categoria'] != 'OUTRAS']
        df_filtered = df_filtered.drop_duplicates(subset='Categoria')
        return df_filtered


    def obter_valor_total_investido(self, dados_carteira_evol_copy_df):
        return dados_carteira_evol_copy_df.loc[
                           dados_carteira_evol_copy_df['Categoria'] != 'OUTRAS', 'valor_ativo_total'].sum()
    def obter_valor_total_ajuste(self, dados_carteira_evol_copy_df):
        return dados_carteira_evol_copy_df.loc[
            dados_carteira_evol_copy_df['Categoria'] != 'OUTRAS', 'ajuste_ativo_val'].sum()

    def obter_valor_total_todos_investimentos(self):
        diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_arquivo = os.path.join(diretorio_atual, 'movimentacao_todos_ativos.xlsx')
        df = pd.read_excel(caminho_arquivo)
        df = self.atualizar_valor_ativo_p8(df)
        df['compra_venda'] = df['Compra'] - df['Venda']
        resumo_df = df.loc[:, ['Categoria', 'Ativo', 'valor_ativo_total', 'Compra', 'Venda', 'compra_venda']]
        caminho_completo = os.path.join(diretorio_atual, 'movimentacao_todos_ativos_ajustado.xlsx')
        df.to_excel(caminho_completo, index=False)
        self.imprimir_se(resumo_df, False)

        return df.loc[
            df['compra_venda'] > 0, 'valor_ativo_total'].sum()

    def criar_valor_total_compra(self, dados_carteira_evol_copy_df):
        dados_carteira_evol_copy_df['ativo_valor_total_compra'] = dados_carteira_evol_copy_df['Ativo'].apply( lambda ativo: self.calcular_valor_total_compra(ativo, dados_carteira_evol_copy_df))
        print('------------------------criar_valor_total_compra----------------------------')
       # print(dados_carteira_evol_copy_df)
        return dados_carteira_evol_copy_df

    def obter_valor_total_compra(self, dados_carteira_evol_copy_df):
        dados_carteira_evol_copy_df = self.criar_valor_total_compra(dados_carteira_evol_copy_df)
        return dados_carteira_evol_copy_df.loc[
            dados_carteira_evol_copy_df['Categoria'] != 'OUTRAS', 'ativo_valor_total_compra'].sum()

    def calcular_valor_total_compra(self, ativo, dados_carteira_evol_copy_df):
        retorno_total =  dados_carteira_evol_copy_df.loc[dados_carteira_evol_copy_df['Ativo'] == ativo, 'Preco_medio'].values[0] * dados_carteira_evol_copy_df.loc[dados_carteira_evol_copy_df['Ativo'] == ativo, 'Quantidade'].values[0]
        return retorno_total
    def obter_dados_carteiras(self):
        investimento = Investimento();
        dados_investimento_df = investimento.importar_p1()
        dados_investimento_df = investimento.merge_outros_ativos(dados_investimento_df)
        dados_investimento_df = investimento.cria_coluna_ativo_p2(dados_investimento_df)
        dados_investimento_df = investimento.criar_colunas_compra_venda_preco_medio_p3(dados_investimento_df)
        dados_investimento_df = investimento.adicionar_categoria_p4(dados_investimento_df)
        dados_investimento_df = investimento.adicionar_percentual_ideal_p5(dados_investimento_df)
        dados_investimento_df = investimento.obter_valor_ativo_atual_p6(dados_investimento_df)
        dados_investimento_df = investimento.ajustar_ativo_excedente_p7(dados_investimento_df)
        dados_investimento_df = investimento.atualizar_valor_ativo_p8(dados_investimento_df)
        dados_investimento_df = investimento.adicionar_percentual_ideal_categoria_p9(dados_investimento_df)
        dados_investimento_df = investimento.adicionar_percentual_real_categoria_p10(dados_investimento_df)
        dados_investimento_df = investimento.adicionar_percentual_ativo_ideal_vs_atual_p11(dados_investimento_df)
        dados_investimento_df = investimento.adicionar_diferenca_percentual_categoria_ideal_vs_real_p12(
            dados_investimento_df)
        dados_investimento_df = investimento.adicionar_diferenca_percentual_ativo_ideal_vs_real_p13(dados_investimento_df)
        dados_investimento_df = investimento.calcula_valor_ativo_balancear_p14(dados_investimento_df)

        return dados_investimento_df

    def salvarPreCarteira(self, df):
        conexao = ConexaoMongoDB()
        cliente, banco = conexao.conectar()
        collectionPreCarteira = banco['pre_carteira']
        dados_dict = df.to_dict(orient='records')
        carreira = Carteira(dados_dict).to_dict()
        collectionPreCarteira.insert_one(carreira)
        conexao.desconectar()

    def find_by_max_data_pre_carteira(self):
        # Obtenha uma conexão com o MongoDB usando o método de classe
        conexao = ConexaoMongoDB()
        cliente, banco = conexao.conectar()
        colecao = banco['pre_carteira']
        # Consulte o documento com a maior data
        documento = colecao.find_one(sort=[("data", pymongo.DESCENDING)])

        # Se houver um DataFrame no documento, carregue-o
        dataframe = None
        if documento and 'df' in documento:
            dataframe = pd.DataFrame(documento['df'])

        # Feche a conexão com o MongoDB
        cliente.close()

        if documento:
            return dataframe
        else:
            return None