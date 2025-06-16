import streamlit as st
import pandas as pd
import os

# Regras atualizadas conforme o histórico fornecido
ARQUIVO_REGRAS = "regras.csv"
ARQUIVO_RESULTADOS = "dados.csv"
ARQUIVO_ESTRATEGIAS = "historico_estrategias.csv"

# Conjuntos de números proibidos definidos (Estratégia Reflexiva)
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

# Se o arquivo de regras não existir, cria o CSV inicial
if not os.path.exists(ARQUIVO_REGRAS):
    regras_df = pd.DataFrame([{"anterior": k, "proibidos": ",".join(map(str, v))} for k, v in regras.items()])
    regras_df.to_csv(ARQUIVO_REGRAS, index=False)

st.title("Roleta - Previsão e Simulação de Banca")

# Estratégia Reflexiva (baseada em 15 últimas sequências)
def estrategia_reflexiva(historico):
    if len(historico) < 15:
        return "Aguardando mais resultados para análise."

    ultimos = historico[-15:]

    padrao_atual = "".join(ultimos)
    contagem_1 = 0
    contagem_total = 0

    for i in range(len(historico) - 15):
        trecho = historico[i:i+15]
        if trecho == ultimos:
            if i+15 < len(historico):
                proximo = historico[i+15]
                contagem_total += 1
                if proximo == "1":
                    contagem_1 += 1

    if contagem_total == 0:
        return "Sem correspondência suficiente para prever."

    prob = contagem_1 / contagem_total

    palpite = "1" if prob >= 0.5 else "X"
    texto = f"Palpite Estratégia Reflexiva: {palpite} (acerto {contagem_1}/{contagem_total})"

    if palpite == "1":
        ult_numero = int(historico[-1])
        proibidos = regras.get(ult_numero, [])
        return f"{texto} → V{proibidos[0]}V{proibidos[1]}"
    else:
        return texto

# Exibe palpite baseado no histórico de estratégias
if os.path.exists(ARQUIVO_ESTRATEGIAS):
    df_hist = pd.read_csv(ARQUIVO_ESTRATEGIAS)
    if 'Resultado' in df_hist.columns:
        historico_resultado = df_hist['Resultado'].astype(str).tolist()
        st.subheader("Previsão - Estratégia Reflexiva")
        st.info(estrategia_reflexiva(historico_resultado))
else:
    st.warning("Histórico insuficiente para análise.")
