import streamlit as st
import pandas as pd
import os

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

if not os.path.exists(ARQUIVO_REGRAS):
    regras_df = pd.DataFrame([{"anterior": k, "proibidos": ",".join(map(str, v))} for k, v in regras.items()])
    regras_df.to_csv(ARQUIVO_REGRAS, index=False)

st.title("Roleta - Previsão e Simulação de Banca")

# Upload de arquivo CSV
st.subheader("Upload de Resultados Anteriores")
uploaded_file = st.file_uploader("Envie um arquivo CSV com os resultados (números entre 0 e 36)", type="csv")
if uploaded_file:
    df_upload = pd.read_csv(uploaded_file)
    if 'numero' in df_upload.columns:
        historico_antigo = df_upload['numero'].astype(int).tolist()
        resultado_seq = []
        for i in range(1, len(historico_antigo)):
            ultimo = historico_antigo[i-1]
            atual = historico_antigo[i]
            resultado_seq.append("1" if atual not in regras.get(ultimo, []) else "X")
        df_historico = pd.DataFrame({"Numero": historico_antigo[1:], "Resultado": resultado_seq})
        df_historico.to_csv(ARQUIVO_ESTRATEGIAS, index=False)
        st.success("Arquivo carregado e processado com sucesso.")

# Entrada manual de resultado
st.subheader("Inserir novo número da roleta")
novo_resultado = st.number_input("Digite o número que saiu (0 a 36):", min_value=0, max_value=36, step=1)
if st.button("Registrar número"):
    if os.path.exists(ARQUIVO_ESTRATEGIAS):
        df = pd.read_csv(ARQUIVO_ESTRATEGIAS)
        if not df.empty:
            ultimo_num = int(df['Numero'].iloc[-1])
            resultado = "1" if novo_resultado not in regras.get(ultimo_num, []) else "X"
            novo = pd.DataFrame({"Numero": [novo_resultado], "Resultado": [resultado]})
            df = pd.concat([df, novo], ignore_index=True)
            df.to_csv(ARQUIVO_ESTRATEGIAS, index=False)
            st.success(f"Número {novo_resultado} registrado com resultado {resultado}.")
        else:
            st.warning("Base vazia. Faça upload inicial primeiro.")
    else:
        st.warning("Arquivo histórico não encontrado. Faça upload inicial.")

# Estratégia Reflexiva
st.subheader("Previsão - Estratégia Reflexiva")
def estrategia_reflexiva(historico):
    if len(historico) < 15:
        return "Aguardando mais resultados para análise."
    ultimos = historico[-15:]
    padrao_atual = "".join(ultimos)
    contagem_1 = 0
    contagem_total = 0
    for i in range(len(historico) - 15):
        trecho = historico[i:i+15]
        if trecho == ultimos and i+15 < len(historico):
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
        if len(proibidos) >= 2:
            return f"{texto} → V{proibidos[0]}V{proibidos[1]}"
    return texto

if os.path.exists(ARQUIVO_ESTRATEGIAS):
    df_hist = pd.read_csv(ARQUIVO_ESTRATEGIAS)
    if 'Resultado' in df_hist.columns:
        historico_resultado = df_hist['Resultado'].astype(str).tolist()
        st.info(estrategia_reflexiva(historico_resultado))
else:
    st.warning("Histórico insuficiente para análise.")
# Campo para inserir novo número da roleta manualmente
st.subheader("Inserir número manualmente")
novo_numero = st.number_input("Digite o número da roleta (0 a 36):", min_value=0, max_value=36, step=1)
if st.button("Salvar número"):
    if os.path.exists(ARQUIVO_RESULTADOS):
        df_resultados = pd.read_csv(ARQUIVO_RESULTADOS)
    else:
        df_resultados = pd.DataFrame(columns=["Numero"])

    df_resultados = pd.concat([df_resultados, pd.DataFrame([{"Numero": novo_numero}])], ignore_index=True)
    df_resultados.to_csv(ARQUIVO_RESULTADOS, index=False)
    st.success(f"Número {novo_numero} salvo com sucesso!")

# Mostra os últimos resultados
st.subheader("Últimos números registrados")
if os.path.exists(ARQUIVO_RESULTADOS):
    df_resultados = pd.read_csv(ARQUIVO_RESULTADOS)
    st.dataframe(df_resultados.tail(10))

    # Botão de download
    csv_download = df_resultados.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Baixar resultados da roleta",
        data=csv_download,
        file_name="resultados_roleta.csv",
        mime="text/csv"
    )
