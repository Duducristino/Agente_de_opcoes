import streamlit as st
import pandas as pd
from datetime import datetime

st.title("Agente Autônomo de Opções")

# Upload do CSV
uploaded_file = st.file_uploader("Faça upload do arquivo .csv com os dados das opções", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # Conversões e limpeza
    df['data_vencimento'] = pd.to_datetime(df['data_vencimento'], errors='coerce')
    df['validade'] = df['data_vencimento']  # cópia para exibição

    st.subheader("Dados das Opções")
    st.dataframe(df)

    # Filtros
    st.markdown("### Selecione o tipo de opção")
    tipo_opcao = st.selectbox("Selecione o tipo de opção", df["tipo"].unique())

    st.markdown("### Filtrar por data de vencimento (opcional)")
    data_venc_input = st.text_input("YYYY/MM/DD")

    df_filtrado = df[df["tipo"] == tipo_opcao]

    if data_venc_input:
        try:
            data_formatada = datetime.strptime(data_venc_input, "%Y/%m/%d")
            df_filtrado = df_filtrado[df_filtrado["data_vencimento"] == data_formatada]
        except ValueError:
            st.error("Formato de data inválido. Use o formato YYYY/MM/DD.")

    st.subheader("Resultado do Filtro")
    st.dataframe(df_filtrado)

    # Recomendação
    st.subheader("Recomendações")
    for i, row in df_filtrado.iterrows():
        tipo = row['tipo']
        preco_ativo = row['preco_ativo']
        preco_exercicio = row['preco_exercicio']
        venc = row['data_vencimento'].date()

        if tipo == 'CALL':
            if preco_ativo > preco_exercicio:
                st.markdown(f"**CALL** com vencimento em {venc}: **Vale a pena exercer.**")
            else:
                st.markdown(f"**CALL** com vencimento em {venc}: Não vale a pena.")
        elif tipo == 'PUT':
            if preco_ativo < preco_exercicio:
                st.markdown(f"**PUT** com vencimento em {venc}: **Vale a pena exercer.**")
            else:
                st.markdown(f"**PUT** com vencimento em {venc}: Não vale a pena.")
else:
    st.warning("Por favor, envie um arquivo .csv para iniciar.")
