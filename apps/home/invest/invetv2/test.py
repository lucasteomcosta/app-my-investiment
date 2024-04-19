from apps.home.invest.invetv2.ImportInvestment import ImportInvestment
from apps.home.invest.invetv2.ProcessarInvestimento import ProcessarInvestimento
from apps.home.invest.invetv2.Rentabilidade import Rentabilidade
import os
import pandas as pd



test = ProcessarInvestimento()
#test.importar_dados()
test.criar_resumo_atualizado()
test.definir_valor_total()
test.definir_percentual_categoria()
test.identificar_aportes()
test.gerar_valorizacao()