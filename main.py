import streamlit as st
import pandas as pd
import plotly.express as px

# Configurações da página do Streamlit
st.set_page_config(
    page_title="Loja Seromo",
    page_icon=":bar_chart:",
    layout="wide"
)

# Carregar dados e tratar colunas
df = pd.read_excel(
    io='DadosLoja.xlsx',
    engine='openpyxl',
    sheet_name='Planilha1'
)

# Tratamento de nomes das colunas e preenchimento de valores nulos
df.columns = df.columns.str.strip().str.capitalize()
df["Tecido"] = df["Tecido"].fillna("Desconhecido")
df["Faturamento_total"] = (
    df["Faturamento_total"]
    .replace({'R\$ ': '', 'R$ ': ''}, regex=True)
    .replace({',': '.'}, regex=True)
    .astype(float)
)

# Filtros na barra lateral
st.sidebar.header("Filtro")

# Filtro para Tecidos com opção de Selecionar Todos
select_all_tecido = st.sidebar.checkbox("Selecionar Todos os Tecidos", value=True)
tecido_options = df["Tecido"].unique()
if select_all_tecido:
    tecido = st.sidebar.multiselect("Selecione o Tecido:", options=tecido_options, default=tecido_options)
else:
    tecido = st.sidebar.multiselect("Selecione o Tecido:", options=tecido_options)

# Filtro para Cores com opção de Selecionar Todos
select_all_cor = st.sidebar.checkbox("Selecionar Todas as Cores", value=True)
cor_options = df["Cor"].unique()
if select_all_cor:
    cor = st.sidebar.multiselect("Selecione a Cor:", options=cor_options, default=cor_options)
else:
    cor = st.sidebar.multiselect("Selecione a Cor:", options=cor_options)

# Aplicar filtros ao DataFrame
df_selection = df.query("Tecido in @tecido and Cor in @cor")

# Exibir o título e o DataFrame filtrado
st.title("Loja de Tecidos Seromo")
st.dataframe(df_selection)

# Calcular o estoque disponível
df_selection["Estoque_disponivel"] = df_selection["Total_unidades"] - df_selection["Unidades_kg"]

# Gráfico de Pizza de Estoque disponível por Tipo de Tecido
df_estoque = df_selection.groupby("Tecido")["Estoque_disponivel"].sum().reset_index()
fig_pizza_estoque = px.pie(
    df_estoque, 
    names="Tecido", 
    values="Estoque_disponivel",
    title="Estoque Disponível por Tipo de Tecido",
    labels={"Estoque_disponivel": "Estoque Disponível", "Tecido": "Tecido"}
)
st.plotly_chart(fig_pizza_estoque, use_container_width=True)

# Gráfico de Area de venda por Tipo de Tecido
df_saida_tecido = df_selection.groupby("Tecido")["Unidades_kg"].sum().reset_index()
fig_area_saida = px.area(
    df_saida_tecido, 
    x="Tecido", 
    y="Unidades_kg",
    title="Quantidade de Tecidos Vendidos por Tipo de Tecido",
    labels={"Unidades_kg": "Quantidade Vendida (Kg)", "Tecido": "Tipo de Tecido"},
)

st.plotly_chart(fig_area_saida, use_container_width=True)

# Função para exibir gráficos por tecido
def exibir_graficos_interativos(tecido_tipo):
    df_tecido = df_selection[df_selection["Tecido"] == tecido_tipo]
    if not df_tecido.empty:
        st.subheader(f"Gráficos de Tecido: {tecido_tipo}")

        # Gráfico de Barras com Unidades
        fig_bar = px.bar(
            df_tecido, 
            x="Cor", 
            y="Total_unidades",
            title=f"Quantidade Total de Tecidos por Cor - {tecido_tipo}",
            labels={"Total_unidades": "Total de Unidades", "Cor": "Cor"},
            hover_data=["Preço_unitario"])
        st.plotly_chart(fig_bar, use_container_width=True)

        # Gráfico de Pizza com Estoque Disponível por Cor
        fig_pie = px.pie(
            df_tecido, 
            names="Cor", 
            values="Estoque_disponivel",
            title=f"Distribuição de Estoque Disponível por Cor - {tecido_tipo}",
            hover_data={"Preço_unitario": True}
        )
        st.plotly_chart(fig_pie, use_container_width=True)

        # Identificar cores que estão em falta
        df_tecido["Estoque_disponivel"] = df_tecido["Total_unidades"] - df_tecido["Unidades_kg"]
        cores_em_falta = df_tecido[df_tecido["Estoque_disponivel"] <= 0]["Cor"].unique()

        # Exibir cores em falta (Abaixo do Gráfico de Pizza)
        if len(cores_em_falta) > 0:
            st.markdown(f"**Cores em falta no estoque:** {', '.join(cores_em_falta)}")
        else:
            st.markdown("**Não há cores em falta no estoque.**")

        # Gráfico de Área de Vendas por Cor
        fig_area_vendas = px.area(
            df_tecido,
            x="Cor",
            y="Unidades_kg",
            title=f"Quantidade Vendida por Cor - {tecido_tipo}",
            labels={"Unidades_kg": "Quantidade Vendida (Kg)", "Cor": "Cor"}
        )
        st.plotly_chart(fig_area_vendas, use_container_width=True)

        # Gráfico de Linha para Total de Unidades, Unidades Vendidas e Estoque Disponível
        st.subheader(f"Evolução do Estoque por Cor - {tecido_tipo}")

        df_line = df_tecido.groupby("Cor")[["Total_unidades", "Unidades_kg", "Estoque_disponivel"]].sum().reset_index()

        fig_line = px.line(
            df_line,
            x="Cor",
            y=["Total_unidades", "Unidades_kg", "Estoque_disponivel"],
            title=f"Total de Unidades, Unidades Vendidas e Estoque Disponível por Cor - {tecido_tipo}",
            labels={"Cor": "Cor do Tecido", "value": "Quantidade", "variable": "Legenda"},
            markers=True
        )

        st.plotly_chart(fig_line, use_container_width=True)

# Exibir função gráficos para cada tipo de tecido
for tecido_tipo in df["Tecido"].unique():
    exibir_graficos_interativos(tecido_tipo)

# Gráfico de Evolução do Faturamento por Cor
st.subheader("Evolução do Faturamento por Cor de Tecido")
df_faturamento = (
    df_selection.groupby("Cor")["Faturamento_total"].sum().reset_index()
    .sort_values(by="Faturamento_total", ascending=True)
)

# Calcular o faturamento total
faturamento_total = df_faturamento["Faturamento_total"].sum()
st.markdown(f"**Faturamento Total de Todos os Tecidos: R$ {faturamento_total:,.2f}**")

# Gráficos de Faturamento
df_faturamento_por_tecido = df_selection.groupby(["Cor", "Tecido"])["Faturamento_total"].sum().reset_index()

fig_bar_faturamento_por_tecido = px.bar(
    df_faturamento_por_tecido,
    x="Cor",
    y="Faturamento_total",
    color="Tecido",
    title="Faturamento por Cor e Tecido Individual",
    labels={"Faturamento_total": "Faturamento Total", "Cor": "Cor"},
    text="Faturamento_total"
)

fig_bar_faturamento_total = px.bar(
    df_faturamento,
    x="Cor",
    y="Faturamento_total",
    title="Faturamento Total por Cor",
    labels={"Faturamento_total": "Faturamento Total", "Cor": "Cor"},
    text="Faturamento_total"
)

# Exibir gráficos de faturamento
st.plotly_chart(fig_bar_faturamento_por_tecido, use_container_width=True, key="faturamento_por_tecido")

st.plotly_chart(fig_bar_faturamento_total, use_container_width=True, key="faturamento_total")
