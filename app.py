import streamlit as st
import pandas as pd
import os

# Regras atualizadas conforme o histórico fornecido
regras = {
    1: [3, 8, 11, 12, 13, 28, 29, 30, 35, 36],
    36: [3, 8, 11, 12, 13, 28, 29, 30, 35, 36],
    2: [3, 7, 8, 11, 12, 23, 26, 28, 30, 35, 36],
    20: [3, 7, 8, 11, 12, 23, 26, 28, 30, 35, 36],
    3: [1, 2, 9, 14, 17, 20, 21, 22, 25, 31, 34],
    8: [1, 2, 9, 14, 17, 20, 21, 22, 25, 31, 34],
    4: [7, 11, 12, 13, 18, 27, 28, 29, 30, 35],
    33: [7, 11, 12, 13, 18, 27, 28, 29, 30, 35],
    5: [6, 7, 9, 13, 18, 27, 28, 29, 30, 35, 36],
    32: [6, 7, 9, 13, 18, 27, 28, 29, 30, 35, 36],
    6: [0, 3, 10, 15, 16, 19, 23, 24, 26, 32],
    18: [0, 3, 10, 15, 16, 19, 23, 24, 26, 32],
    7: [1, 2, 4, 15, 16, 19, 20, 21, 24, 32, 33],
    9: [0, 3, 5, 8, 10, 23, 24, 26, 30, 32, 35],
    17: [0, 3, 5, 8, 10, 23, 24, 26, 30, 32, 35],
    10: [6, 9, 14, 17, 18, 22, 25, 27, 29, 31, 34],
    0: [6, 9, 14, 17, 18, 22, 25, 27, 29, 31, 34],
    12: [1, 2, 4, 14, 16, 19, 20, 21, 25, 31, 33],
    13: [1, 4, 5, 15, 16, 19, 20, 21, 24, 32, 33],
    14: [0, 3, 8, 10, 11, 12, 23, 26, 28, 30, 35],
    25: [0, 3, 8, 10, 11, 12, 23, 26, 28, 30, 35],
    15: [6, 7, 9, 13, 18, 22, 27, 28, 29, 34, 36],
    24: [6, 7, 9, 13, 18, 22, 27, 28, 29, 34, 36],
    16: [6, 7, 11, 12, 13, 18, 22, 27, 28, 29, 36],
    19: [6, 7, 11, 12, 13, 18, 22, 27, 28, 29, 36],
    22: [0, 3, 5, 8, 10, 15, 16, 23, 24, 26, 32],
    23: [2, 6, 9, 14, 17, 18, 20, 22, 25, 31, 34],
    26: [2, 6, 9, 14, 17, 18, 20, 22, 25, 31, 34],
    27: [0, 1, 4, 5, 10, 15, 16, 19, 24, 32, 33],
    29: [0, 1, 4, 5, 10, 15, 16, 19, 24, 32, 33],
    28: [1, 2, 4, 14, 15, 16, 19, 20, 21, 24, 33],
    30: [1, 2, 4, 9, 14, 15, 17, 21, 25, 31, 33],
    35: [1, 2, 4, 9, 14, 15, 17, 21, 25, 31, 33],
    31: [0, 3, 5, 8, 10, 11, 12, 23, 26, 30, 35],
    34: [0, 3, 5, 8, 10, 23, 24, 26, 30, 32, 35],
}

def prever_resultado(num_anterior, num_atual):
    proibidos = regras.get(num_anterior, [])
    return "X" if num_atual in proibidos else "1"

st.title("Análise e Previsão - Roleta")

if "dados" not in st.session_state:
    st.session_state.dados = []

novo_numero = st.number_input("Digite o número que acabou de sair na roleta (0-36):", min_value=0, max_value=36, step=1)
if st.button("Adicionar Número"):
    st.session_state.dados.append(novo_numero)

# Mostrar dados atuais
st.subheader("Histórico de Números")
df = pd.DataFrame(st.session_state.dados, columns=["numero"])
st.dataframe(df)

# Gerar palpite com base nos últimos 14 pares
def gerar_palpite(df):
    if len(df) < 15:
        return None
    erros = 0
    for i in range(-14, -1):
        ant = df.iloc[i - 1]['numero']
        atual = df.iloc[i]['numero']
        prev = prever_resultado(ant, atual)
        real = prever_resultado(ant, atual)
        if prev != real:
            erros += 1
    if erros <= 2:
        return prever_resultado(df.iloc[-2]['numero'], df.iloc[-1]['numero'])
    return None

palpite = gerar_palpite(df)
if palpite:
    st.success(f"Palpite para o próximo número: {palpite}")
else:
    st.warning("Não há dados suficientes ou muitos erros nas últimas previsões.")

# Simulação de banca com base nas previsões
st.subheader("Simulação de Banca")
banca = 1000
historico_banca = []
tentativa = 0
valores = [26, 78, 312]

for i in range(1, len(df)):
    anterior = df.iloc[i - 1]['numero']
    atual = df.iloc[i]['numero']
    previsao = prever_resultado(anterior, atual)
    resultado = prever_resultado(anterior, atual)
    if tentativa >= 3:
        tentativa = 0
    aposta = valores[tentativa]
    banca -= aposta
    if previsao == resultado:
        ganho = 36 * (tentativa + 1)
        lucro = ganho - sum(valores[:tentativa+1])
        banca += ganho
        tentativa = 0
    else:
        tentativa += 1
    historico_banca.append(banca)

# Mostrar gráfico e tabela
if historico_banca:
    st.line_chart(historico_banca)
