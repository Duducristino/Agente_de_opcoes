import streamlit as st
import pandas as pd
import datetime as dt

st.set_page_config(page_title="Agente Autônomo de Opções", layout="centered")

st.title("🧠 Agente Autônomo de Opções")
st.write("Faça upload do arquivo `.csv` com os dados das opções (CALL e PUT) para começar.")

uploaded_file = st.file_uploader("Upload do arquivo .csv", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)

        # 1. Validar estrutura
        colunas_esperadas = {"tipo", "data_vencimento", "preco_exercicio", "preco_ativo", "valor_opcao"}
        if not colunas_esperadas.issubset(df.columns):
            st.error(f"Erro: O arquivo deve conter as colunas: {colunas_esperadas}")
        else:
            # 2. Conversão de datas
            df["data_vencimento"] = pd.to_datetime(df["data_vencimento"], errors="coerce")

            # 3. Cálculo do valor intrínseco
            def calcular_valor_intrinseco(row):
                if row["tipo"] == "CALL":
                    return max(0, row["preco_ativo"] - row["preco_exercicio"])
                elif row["tipo"] == "PUT":
                    return max(0, row["preco_exercicio"] - row["preco_ativo"])
                return 0

            df["valor_intrinseco"] = df.apply(calcular_valor_intrinseco, axis=1)

            # 4. Dias até o vencimento
            df["dias_restantes"] = (df["data_vencimento"] - dt.datetime.now()).dt.days

            # 5. Classificação ITM/ATM/OTM
            def classificar_opcao(row):
                if row["tipo"] == "CALL":
                    if row["preco_ativo"] > row["preco_exercicio"]:
                        return "ITM"
                    elif row["preco_ativo"] == row["preco_exercicio"]:
                        return "ATM"
                    else:
                        return "OTM"
                elif row["tipo"] == "PUT":
                    if row["preco_ativo"] < row["preco_exercicio"]:
                        return "ITM"
                    elif row["preco_ativo"] == row["preco_exercicio"]:
                        return "ATM"
                    else:
                        return "OTM"
                return "N/A"

            df["classificacao"] = df.apply(classificar_opcao, axis=1)

            # 6. ROI estimado
            df["roi_%"] = round((df["valor_intrinseco"] / df["valor_opcao"]) * 100, 2)

            # 7. Filtros interativos
            tipo_filtro = st.selectbox("Filtrar por tipo de opção", options=["TODAS", "CALL", "PUT"])
            if tipo_filtro != "TODAS":
                df = df[df["tipo"] == tipo_filtro]

            datas_unicas = sorted(df["data_vencimento"].dropna().dt.date.unique())
            data_escolhida = st.selectbox("Filtrar por data de vencimento", options=["Todas"] + [str(d) for d in datas_unicas])
            if data_escolhida != "Todas":
                df = df[df["data_vencimento"].dt.date == pd.to_datetime(data_escolhida).date()]

            st.subheader("📊 Dados das Opções")
            st.dataframe(df)

            # 8. Recomendações inteligentes
            st.subheader("🤖 Recomendações do Agente")
            for _, row in df.iterrows():
                recomendacao = ""
                if row["classificacao"] == "ITM" and row["roi_%"] > 15 and row["dias_restantes"] <= 30:
                    recomendacao = "Vale a pena exercer."
                elif row["classificacao"] == "OTM" and row["dias_restantes"] <= 5:
                    recomendacao = "Evite exercer, risco alto."
                elif row["classificacao"] == "ATM":
                    recomendacao = "Acompanhar de perto."
                else:
                    recomendacao = "Aguardar movimentação."

                st.markdown(
                    f"**{row['tipo']}** com vencimento em **{row['data_vencimento'].date()}** — "
                    f"ROI: **{row['roi_%']}%**, Classificação: **{row['classificacao']}** → **{recomendacao}**"
                )

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {str(e)}")
else:
    st.info("Por favor, envie um arquivo .csv para iniciar.")
