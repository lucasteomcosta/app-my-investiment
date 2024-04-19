# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from plotly.offline import plot

from .invest.invetv2.CreateDashboard import CreateDashboard


@login_required(login_url="/login/")
def index(request):
    context = carregar_dashboard()
    print('------------plotly_pizza_percentual_real_por_catgoria---------------')

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    print('------------PASSOU AQUIIII---------------')
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))


def carregar_dashboard():

    gerar_deshboard = CreateDashboard()

    df, invest = gerar_deshboard.obter_movimentacao()

    total_investido = invest.obter_valor_total_investido(df)
    print("=========================INIT 3=========================")
    print(total_investido)
    fig_dados_grafico_pizza_percentual_real_por_catgoria = gerar_deshboard.obter_dash_pizza_percetual_por_categoria(
        invest, df)
    plotly_pizza_percentual_real_por_catgoria = plot({'data': fig_dados_grafico_pizza_percentual_real_por_catgoria},
                                                     output_type='div')

    fig_bar_valor_ajuste_categoria = gerar_deshboard.obter_dash_bar_valor_ajuste_categoria(invest, df)
    plotly_bar_valor_ajuste_categoria = plot({'data': fig_bar_valor_ajuste_categoria}, output_type='div')

    fig_bar_valor_ajuste_por_ativo = gerar_deshboard.obter_dash_bar_valor_ajuste_por_ativo(invest, df)
    plotly_bar_valor_ajuste_por_ativo = plot({'data': fig_bar_valor_ajuste_por_ativo}, output_type='div')

    #total_todos_investimentos = invest.obter_valor_total_todos_investimentos()

    #valor_total_ajuste = invest.obter_valor_total_ajuste(df)
    #total_investido = invest.obter_valor_total_investido(df)
    #total_compra = invest.obter_valor_total_compra(df)

    #percentual_rentabilidade = ((total_investido - total_compra)/total_compra) * 100
    #print(total_compra)
    print("=========================P4=========================")
    df_ativos = invest.obter_dados_df_ativo(df)
    itens_list = df_ativos.to_dict(orient='records')

    context = {'segment': 'index',
               'plotly_pizza_percentual_real_por_catgoria': plotly_pizza_percentual_real_por_catgoria,
               'plotly_bar_valor_ajuste_categoria': plotly_bar_valor_ajuste_categoria,
               'plotly_bar_valor_ajuste_por_ativo': plotly_bar_valor_ajuste_por_ativo,
               'total_investido': total_investido,
               'percentual_rentabilidade': 0,#percentual_rentabilidade,
               'total_compra': 0,#total_compra,
               'valor_total_ajuste': 0,#valor_total_ajuste,
               'total_todos_investimentos': 0,#total_todos_investimentos,
               'df_ativos': itens_list
               }

    return context
    # return render(request, 'invest/dashboard.html', context = context)

