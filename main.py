import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Loja Seromo",
                   page_icon=":bar_chart:",
                   layout="wide"
                  )

# Carregar dados e tratar colunas
df = pd.read_excel(
    io='DadosLoja.xlsx',
    engine='openpyxl',
    sheet_name='Planilha1'
)

# Tratar nomes das colunas
df.columns = df.columns.str.strip().str.capitalize()
df["Tecido"] = df["Tecido"].fillna("Desconhecido")
df["Faturamento_total"] = df["Faturamento_total"].replace({'R\$ ': '', 'R$ ': ''}, regex=True).replace({',': '.'}, regex=True).astype(float)

# Configurar filtros na barra lateral
st.sidebar.header("Filtro")
tecido = st.sidebar.multiselect(
    "Selecione o Tecido:",
    options=df["Tecido"].unique(),
    default=df["Tecido"].unique()
)
cor = st.sidebar.multiselect(
    "Selecione a Cor:",
    options=df["Cor"].unique(),
    default=df["Cor"].unique()
)
df_selection = df.query(
    "Tecido in @tecido and Cor in @cor"
)

# Titulo
st.title("Loja de Tecidos Seromo")

# Exibir o DataFrame filtrado
st.dataframe(df_selection)

# Função para exibir gráficos interativos por tecido
def exibir_graficos_interativos(tecido_tipo):
    df_tecido = df_selection[df_selection["Tecido"] == tecido_tipo]
    if not df_tecido.empty:
        st.subheader(f"Gráficos Interativos para Tecido: {tecido_tipo}")

        # Gráfico de Barras Interativo com Preço Unitário
        fig_bar = px.bar(df_tecido, x="Cor", y="Total_unidades",
                         title=f"Quantidade de Produtos por Cor - {tecido_tipo}",
                         labels={"Total_unidades": "Total de Unidades", "Cor": "Cor"},
                         hover_data=["Preço_unitario"])
        st.plotly_chart(fig_bar, use_container_width=True)

        # Gráfico de Pizza Interativo com Preço Unitário
        fig_pie = px.pie(df_tecido, names="Cor", values="Total_unidades",
                         title=f"Distribuição de Produtos por Cor - {tecido_tipo}",
                         hover_data={"Preço_unitario": True})
        st.plotly_chart(fig_pie, use_container_width=True)

# Exibir gráficos interativos para cada tipo de tecido
for tecido_tipo in df["Tecido"].unique():
    exibir_graficos_interativos(tecido_tipo)

# Gráfico de Evolução do Faturamento por Cor
st.subheader("Evolução do Faturamento por Cor de Tecido")

# Agrupar os dados para o gráfico de evolução do faturamento
df_faturamento = df_selection.groupby(["Cor"])["Faturamento_total"].sum().reset_index()

# Ordenar os dados pelo Faturamento_total em ordem crescente
df_faturamento = df_faturamento.sort_values(by="Faturamento_total", ascending=True)

# Calcular o faturamento total
faturamento_total = df_faturamento["Faturamento_total"].sum()

# Exibir o faturamento total acima do gráfico
st.markdown(f"**Faturamento Total de Todos os Tecidos: R$ {faturamento_total:,.2f}**")

# Agrupar os dados para o gráfico de faturamento por cor e tecido
df_faturamento_por_tecido = df_selection.groupby(["Cor", "Tecido"])["Faturamento_total"].sum().reset_index()

# Criar gráfico de barras para faturamento por cor e tecido
fig_bar_faturamento_por_tecido = px.bar(df_faturamento_por_tecido, 
                                        x="Cor", 
                                        y="Faturamento_total", 
                                        color="Tecido",
                                        title="Individual",
                                        labels={"Faturamento_total": "Faturamento Total", "Cor": "Cor"},
                                        text="Faturamento_total")  # Adicionando os valores no interior das barras

# Criar gráfico de barras para evolução do faturamento total por cor
fig_bar_faturamento_total = px.bar(df_faturamento, 
                                   x="Cor", 
                                   y="Faturamento_total", 
                                   title="Total",
                                   labels={"Faturamento_total": "Faturamento Total", "Cor": "Cor"},
                                   text="Faturamento_total")  # Adicionando os valores no interior das barras


# Exibir gráfico de faturamento por cor e tecido com a chave única
st.plotly_chart(fig_bar_faturamento_por_tecido, use_container_width=True, key="faturamento_por_tecido")

# Exibir gráfico de faturamento total com a chave única
st.plotly_chart(fig_bar_faturamento_total, use_container_width=True, key="faturamento_total")