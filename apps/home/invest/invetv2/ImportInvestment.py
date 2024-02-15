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