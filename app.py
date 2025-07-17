import streamlit as st
import pandas as pd
import os

# Regras atualizadas conforme o histórico fornecido
REGRAS_PERSONALIZADAS = {
    0: [0, 5, 9, 10, 17, 22, 23, 25, 26, 31, 32, 34],
    1: [1, 2, 4, 7, 11, 12, 13, 28, 20, 21, 33, 36],
    2: [1, 2, 3, 8, 11, 12, 14, 20, 21, 25, 30, 35],
    3: [3, 8, 9, 17, 23, 25, 26, 30, 31, 34, 35],
    4: [1, 4, 7, 9, 11, 12, 13, 16, 21, 28, 33, 36],
    5: [0, 5, 6, 9, 10, 15, 18, 22, 24, 27, 32, 34],
    6: [0, 5, 6, 9, 10, 15, 18, 22, 24, 27, 32, 34],
    7: [1, 4, 7, 9, 11, 13, 16, 21, 28, 29, 33, 36],
    8: [1, 3, 4, 8, 9, 16, 21, 23, 26, 30, 33, 35],
    9: [0, 3, 8, 19, 10, 17, 22, 23, 25, 26, 31, 34],
    10: [0, 5, 6, 9, 10, 17, 22, 23, 26, 31, 32, 34],
    11: [1, 2, 4, 11, 12, 20, 21, 28, 30, 33, 35, 36],
    12: [1, 2, 4, 11, 12, 20, 21, 28, 30, 33, 35, 36],
    13: [1, 4, 7, 13, 15, 16, 19, 27, 28, 29, 33, 36],
    14: [2, 3, 8, 14, 17, 20, 23, 25, 26, 30, 31, 35],
    15: [5, 6, 7, 15, 16, 18, 19, 24, 27, 29, 32, 34],
    16: [1, 4, 7, 13, 15, 16, 19, 27, 28, 29, 33, 36],
    17: [0, 3, 8, 9, 10, 17, 22, 23, 25, 26, 31, 34],
    18: [0, 5, 6, 10, 15, 18, 22, 24, 27, 29, 32, 34],
    19: [1, 4, 7, 13, 15, 16, 19, 27, 28, 29, 33, 36],
    20: [1, 2, 3, 8, 11, 12, 14, 20, 21, 25, 30, 35],
    21: [1, 2, 4, 7, 11, 12, 13, 28, 20, 21, 33, 36],
    22: [0, 5, 6, 9, 10, 15, 18, 22, 24, 27, 32, 34],
    23: [0, 3, 8, 9, 10, 17, 22, 23, 25, 26, 31, 34],
    24: [5, 6, 7, 15, 16, 18, 19, 24, 27, 29, 32, 34],
    25: [2, 3, 8, 14, 17, 20, 23, 25, 26, 30, 31, 35],
    26: [0, 3, 8, 9, 10, 17, 22, 23, 25, 26, 31, 34],
    27: [5, 6, 7, 15, 16, 18, 19, 24, 27, 29, 32, 34],
    28: [1, 2, 4, 7, 11, 12, 13, 28, 20, 21, 33, 36],
    29: [5, 6, 7, 15, 16, 18, 19, 24, 27, 29, 32, 34],
    30: [1, 2, 3, 8, 11, 12, 14, 20, 21, 25, 30, 35],
    31: [2, 3, 8, 9, 14, 17, 23, 25, 26, 30, 31, 35],
    32: [0, 5, 6, 9, 10, 15, 18, 22, 24, 27, 32, 34],
    33: [1, 4, 7, 9, 11, 12, 13, 16, 21, 28, 33, 36],
    34: [0, 5, 9, 10, 17, 22, 23, 25, 26, 31, 32, 34],
    35: [1, 2, 3, 8, 11, 12, 14, 20, 21, 25, 30, 35],
    36: [1, 2, 4, 7, 11, 12, 13, 28, 20, 21, 33, 36]
}

ARQUIVO_RESULTADOS = "dados.csv"
ARQUIVO_ESTRATEGIAS = "historico_estrategias.csv"

st.title("Roleta - Previsão e Simulação de Banca")

# Entrada manual
st.subheader("🎯 Inserir Número Manualmente")
numero_manual = st.number_input("Digite o número da roleta (0-36):", min_value=0, max_value=36, step=1)
if st.button("Adicionar Número"):
    if os.path.exists(ARQUIVO_RESULTADOS):
        df = pd.read_csv(ARQUIVO_RESULTADOS)
    else:
        df = pd.DataFrame(columns=['numero'])
    df = pd.concat([df, pd.DataFrame({'numero': [numero_manual]})], ignore_index=True)
    df.to_csv(ARQUIVO_RESULTADOS, index=False)
    st.success(f"Número {numero_manual} adicionado com sucesso!")

    if len(df) >= 2:
        anterior = df['numero'].iloc[-2]
        proibidos = REGRAS_PERSONALIZADAS.get(anterior, [])
        resultado = '1' if numero_manual not in proibidos else 'X'
        st.info(f"Resultado do número inserido: {'GREEN' if resultado == '1' else 'RED'}")

        historico = pd.DataFrame({
            'numero': [numero_manual],
            'estrategia1': [resultado]
        })
        if os.path.exists(ARQUIVO_ESTRATEGIAS):
            hist_ant = pd.read_csv(ARQUIVO_ESTRATEGIAS)
            historico = pd.concat([hist_ant, historico], ignore_index=True)
        historico.to_csv(ARQUIVO_ESTRATEGIAS, index=False)
        st.dataframe(historico.tail(10))
