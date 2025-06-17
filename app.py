import streamlit as st
import pandas as pd
import os

# Regras atualizadas conforme o histórico fornecido
ARQUIVO_RESULTADOS = "dados.csv"

st.title("Roleta - Previsão e Simulação de Banca")

# Função para obter os 5 vizinhos anteriores e posteriores na roleta
vizinhanca_roleta = {
    0: [26, 32, 15, 19, 4, 21, 2, 25, 17, 34],
    1: [20, 14, 31, 9, 22], 2: [25, 21, 4, 19, 15], 3: [26, 0, 32, 15, 19],
    4: [19, 21, 2, 25, 17], 5: [10, 23, 8, 30, 11], 6: [27, 13, 36, 11, 30],
    7: [28, 12, 35, 3, 26], 8: [30, 5, 10, 23, 1], 9: [31, 22, 18, 29, 7],
    10: [23, 5, 8, 30, 11], 11: [30, 6, 36, 13, 27], 12: [35, 7, 28, 14, 20],
    13: [36, 6, 30, 11, 27], 14: [20, 12, 35, 7, 28], 15: [19, 4, 21, 2, 25],
    16: [33, 1, 20, 14, 31], 17: [34, 25, 2, 21, 4], 18: [29, 7, 28, 14, 20],
    19: [4, 21, 2, 25, 17], 20: [14, 31, 9, 22, 18], 21: [2, 25, 17, 34, 6],
    22: [18, 29, 7, 28, 14], 23: [8, 30, 11, 27, 13], 24: [16, 33, 1, 20, 14],
    25: [17, 34, 6, 36, 13], 26: [0, 32, 15, 19, 4], 27: [11, 30, 6, 36, 13],
    28: [7, 12, 35, 3, 26], 29: [9, 22, 18, 28, 14], 30: [11, 27, 13, 36, 6],
    31: [9, 22, 18, 29, 7], 32: [15, 19, 4, 21, 2], 33: [1, 20, 14, 31, 9],
    34: [25, 17, 2, 21, 4], 35: [12, 35, 7, 28, 14], 36: [13, 27, 11, 30, 6],
}

# Função para encontrar sequência e gerar palpite
def estrategia_nova(historico, ultimos_numeros):
    if len(historico) < 5:
        return "Histórico insuficiente."

    for i in range(len(historico) - 2):
        base = set(historico[i:i+3])
        if base == set(ultimos_numeros):
            if i+3 < len(historico) - 1:
                prox1 = historico[i+3]
                prox2 = historico[i+4] if i+4 < len(historico) else None

                aposta = [prox1] + vizinhanca_roleta.get(prox1, [])
                if prox2 is not None:
                    aposta += [prox2] + vizinhanca_roleta.get(prox2, [])
                aposta = sorted(set(aposta))

                return f"Sequência encontrada! Apostar nos números: {aposta}"

    return "Nenhuma sequência correspondente encontrada."

# Carregar histórico existente
if os.path.exists(ARQUIVO_RESULTADOS):
    df_hist = pd.read_csv(ARQUIVO_RESULTADOS)
else:
    df_hist = pd.DataFrame(columns=["Numero"])

# Upload de arquivo CSV
uploaded_file = st.file_uploader("Importar arquivo de histórico (.csv)", type=["csv"])
if uploaded_file is not None:
    novo_df = pd.read_csv(uploaded_file)
    df_hist = pd.concat([df_hist, novo_df]).drop_duplicates().reset_index(drop=True)
    df_hist.to_csv(ARQUIVO_RESULTADOS, index=False)
    st.success("Arquivo importado com sucesso!")

# Inserção de novo número da roleta
st.subheader("Inserir novo número da roleta")
novo_numero = st.number_input("Novo número:", min_value=0, max_value=36, step=1)
if st.button("Adicionar número"):
    df_hist = pd.concat([df_hist, pd.DataFrame([[novo_numero]], columns=["Numero"])]).reset_index(drop=True)
    df_hist.to_csv(ARQUIVO_RESULTADOS, index=False)
    st.success(f"Número {novo_numero} adicionado!")

# Mostrar histórico atual
st.subheader("Histórico de números")
st.dataframe(df_hist.tail(30))

# Estratégia nova
st.subheader("Estratégia: Análise de sequência de 3")
if len(df_hist) >= 3:
    ultimos = df_hist["Numero"].tolist()[-3:]
    historico = df_hist["Numero"].tolist()
    resultado = estrategia_nova(historico, ultimos)
    st.info(resultado)

# Exportar CSV
st.download_button(
    label="Exportar histórico CSV",
    data=df_hist.to_csv(index=False),
    file_name="dados_exportados.csv",
    mime="text/csv"
)

# Limpar histórico (opcional)
if st.button("Limpar histórico"):
    df_hist = pd.DataFrame(columns=["Numero"])
    df_hist.to_csv(ARQUIVO_RESULTADOS, index=False)
    st.warning("Histórico apagado!")
