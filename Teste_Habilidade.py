# Importando as dependêcias
import pandas as pd
import streamlit as st
import plotly.express as px
from sqlalchemy import create_engine

# Conexão com o banco de dados SQL Server
engine = create_engine("mssql+pyodbc://usuario:senha@servidor/AdventureWorks?driver=ODBC+Driver+17+for+SQL+Server")

# Consulta SQL para armazenar os dados de vendas
query = """
    SELECT soh.OrderDate, soh.TotalDue, a.StateProvinceID, p.Name as ProductName
    FROM Sales.SalesOrderHeader AS soh
    JOIN Sales.SalesOrderDetail AS sod ON soh.SalesOrderID = sod.SalesOrderID
    JOIN Production.Product AS p ON sod.ProductID = p.ProductID
    JOIN Person.Address AS a ON soh.ShipToAddressID = a.AddressID;
"""

# Armazenamento dados de vendas para o DataFrame
df = pd.read_sql_query(query, engine)

# Ajuste das colunas data para data/hora
df['OrderDate'] = pd.to_datetime(df['OrderDate'])
df['YearMonth'] = df['OrderDate'].dt.to_period('M')

# Resumo de vendas por região
v_regiao = df.groupby('StateProvinceID')['TotalDue'].sum().reset_index()

# Resumo de vendas por produto
v_produto = df.groupby('ProductName')['TotalDue'].sum().reset_index()

# Resumo por tempo
v_tempo = df.groupby('YearMonth')['TotalDue'].sum().reset_index()

# Início do Dashboard
st.title("Dashboard de Vendas - AdventureWorks")

# Filtros
data_inicial, data_final = st.date_input("Selecione o intervalo de datas", [])
produto_selecionado = st.selectbox("Selecione o Produto", df['ProductName'].unique())

# Filtro por data
df_filtrado = df[(df['OrderDate'] >= data_inicial) & (df['OrderDate'] <= data_final)]

if produto_selecionado:
    df_filtrado = df_filtrado[df_filtrado['ProductName'] == produto_selecionado]

# Gráfico de barras
fig_barras = px.bar(
    v_produto, 
    x='ProductName', 
    y='TotalDue', 
    title="Vendas por Produto",
    labels={'TotalDue': 'Valor Total de Vendas', 'ProductName': 'Produto'}
)

st.plotly_chart(fig_barras)

# Gráfico de linhas
fig_linhas = px.line(
    v_tempo, 
    x='YearMonth', 
    y='TotalDue', 
    title="Vendas por Tempo",
    labels={'TotalDue': 'Valor Total de Vendas', 'YearMonth': 'Período (Ano-Mês)'}
)

st.plotly_chart(fig_linhas)

# KPI 
total_vendas = df_filtrado['TotalDue'].sum()
st.metric("Total de Vendas no Período", f"R${total_vendas:,.2f}")