import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="Agente Autônomo de Opções", layout="centered")

st.title("🧠 Agente Autônomo de Opções")
st.markdown("Faça upload do arquivo `.csv` com os dados das opções (CALL e PUT) para começar.")

uploaded_file = st.file_uploader("Upload do arquivo .csv", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    df.columns = [col.strip().lower() for col in df.columns]
    df.rename(columns={
        'tipo': 'tipo',
        'data_vencimento': 'data_vencimento',
        'preco_exercicio': 'preco_exercicio',
        'preco_ativo': 'preco_ativo',
        'valor_opcao': 'valor_opcao',
        'ativo': 'ativo'
    }, inplace=True)

    df['data_vencimento'] = pd.to_datetime(df['data_vencimento'], errors='coerce')
    df['roi'] = ((abs(df['preco_exercicio'] - df['preco_ativo']) - df['valor_opcao']) / df['valor_opcao']) * 100

    def classificar_opcao(row):
        if row['tipo'].upper() == 'CALL':
            return 'ITM' if row['preco_ativo'] > row['preco_exercicio'] else 'OTM'
        elif row['tipo'].upper() == 'PUT':
            return 'ITM' if row['preco_ativo'] < row['preco_exercicio'] else 'OTM'
        return 'Desconhecido'

    df['classificacao'] = df.apply(classificar_opcao, axis=1)

    def recomendar(row):
        if row['classificacao'] == 'ITM' and row['roi'] >= 60:
            return 'Alta atratividade: avalie entrada imediata.'
        elif row['classificacao'] == 'ITM' and row['roi'] >= 40:
            return 'Aguardando confirmação: monitore sinais do ativo.'
        else:
            return 'Risco elevado: evite essa operação no momento.'

    df['recomendacao'] = df.apply(recomendar, axis=1)

    st.markdown("### 🔍 Filtrar por tipo de opção")
    tipo_filtro = st.selectbox("Filtrar por tipo", ['TODAS', 'CALL', 'PUT'])

    st.markdown("### 📅 Filtrar por data de vencimento")
    datas_disponiveis = sorted(df['data_vencimento'].dt.date.unique())
    data_filtro = st.selectbox("Filtrar por data", ['Todas'] + [str(d) for d in datas_disponiveis])

    st.markdown("### 🏷️ Filtrar por ativo")
    ativos_disponiveis = sorted(df['ativo'].unique())
    ativo_filtro = st.selectbox("Filtrar por ativo", ['Todos'] + ativos_disponiveis)

    df_filtrado = df.copy()

    if tipo_filtro != 'TODAS':
        df_filtrado = df_filtrado[df_filtrado['tipo'].str.upper() == tipo_filtro]

    if data_filtro != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['data_vencimento'].dt.date == datetime.datetime.strptime(data_filtro, '%Y-%m-%d').date()]

    if ativo_filtro != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['ativo'] == ativo_filtro]

    st.markdown("### 📊 Dados das Opções")
    st.dataframe(df_filtrado[['ativo', 'tipo', 'data_vencimento', 'preco_exercicio', 'preco_ativo', 'valor_opcao', 'roi', 'classificacao']])

    st.markdown("### 🤖 Recomendações do Agente")
    for _, row in df_filtrado.iterrows():
        st.markdown(f"""
        **{row['tipo']}** de **{row['ativo']}** com vencimento em **{row['data_vencimento'].date()}**  
        — ROI: **{row['roi']:.2f}%**, Classificação:
