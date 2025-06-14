import streamlit as st
import pandas as pd
import os

# Função para verificar resultado 1 ou X com base nas regras
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

arquivo = st.file_uploader("Carregar arquivo CSV de resultados", type="csv")

if arquivo:
    df = pd.read_csv(arquivo, names=["Anterior", "Atual", "Resultado"])
    df = df.dropna()
    df = df.astype({"Anterior": int, "Atual": int, "Resultado": str})

    df['Previsao'] = df.apply(lambda row: prever_resultado(row['Anterior'], row['Atual']), axis=1)
    df['Palpite'] = df.apply(lambda row: 'Green' if row['Previsao'] == row['Resultado'] else 'Red', axis=1)

    # Estatísticas
    total = len(df)
    greens = df['Palpite'].value_counts().get('Green', 0)
    reds = df['Palpite'].value_counts().get('Red', 0)
    percentual = round((greens / total) * 100, 2)

    st.subheader("Estatísticas")
    st.write(f"Total de palpites: {total}")
    st.write(f"Greens: {greens}")
    st.write(f"Reds: {reds}")
    st.write(f"Assertividade: {percentual}%")

    # Simulação de banca com estratégia 26-78-312
    st.subheader("Simulação de Banca")
    banca = 1000
    historico_banca = []
    tentativa = 0
    valores = [26, 78, 312]

    for resultado in df['Palpite']:
        if tentativa >= 3:
            tentativa = 0  # reset após 3 reds
        aposta = valores[tentativa]
        banca -= aposta
        if resultado == 'Green':
            ganho = 36 * (tentativa + 1)
            lucro = ganho - sum(valores[:tentativa+1])
            banca += ganho
            tentativa = 0
        else:
            tentativa += 1
        historico_banca.append(banca)

    df['Banca'] = historico_banca

    st.line_chart(df['Banca'])
    st.dataframe(df[['Anterior', 'Atual', 'Resultado', 'Previsao', 'Palpite', 'Banca']])

    csv_export = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Baixar CSV com Resultados", data=csv_export, file_name="analise_roleta.csv", mime='text/csv')
