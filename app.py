import streamlit as st
import pandas as pd
import os

# Regras atualizadas conforme o histórico fornecido (poderão ser editadas abaixo)
ARQUIVO_REGRAS = "regras.csv"
ARQUIVO_RESULTADOS = "dados.csv"

# Carregar regras do arquivo ou usar padrão
if os.path.exists(ARQUIVO_REGRAS):
    regras_df = pd.read_csv(ARQUIVO_REGRAS)
    regras = {int(row['anterior']): list(map(int, str(row['proibidos']).split(','))) for _, row in regras_df.iterrows()}
else:
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
    regras_df = pd.DataFrame([{"anterior": k, "proibidos": ",".join(map(str, v))} for k, v in regras.items()])

st.title("Roleta - Previsão e Simulação de Banca")

# Nova seção: Editor de regras
st.subheader("Editar Regras de Previsão")
selected_anterior = st.selectbox("Escolha o número anterior para editar regras:", sorted(regras.keys()))
atual_lista = regras.get(selected_anterior, [])
nova_lista = st.multiselect("Escolha os números proibidos:", list(range(37)), default=atual_lista)
if st.button("Salvar Regras Atualizadas"):
    regras[selected_anterior] = nova_lista
    regras_df = pd.DataFrame([{"anterior": k, "proibidos": ",".join(map(str, v))} for k, v in regras.items()])
    regras_df.to_csv(ARQUIVO_REGRAS, index=False)
    st.success("Regras atualizadas com sucesso!")

# Estratégia 2 – Repetição de Dúzias
st.subheader("📌 Estratégia 2 – Repetição de Dúzias")
def get_duzia(num):
    if num == 0:
        return 'Z'
    elif 1 <= num <= 12:
        return 'D1'
    elif 13 <= num <= 24:
        return 'D2'
    elif 25 <= num <= 36:
        return 'D3'

if os.path.exists(ARQUIVO_RESULTADOS):
    df_resultados = pd.read_csv(ARQUIVO_RESULTADOS)
    df_resultados['Dúzia'] = df_resultados['numero'].apply(get_duzia)

    contagem = 0
    ultima_duzia = None
    alertas = []
    for i, d in enumerate(df_resultados['Dúzia']):
        if d == ultima_duzia:
            contagem += 1
        else:
            contagem = 1
            ultima_duzia = d
        alertas.append(contagem)

    df_resultados['Repetição Dúzia'] = alertas
    st.write(df_resultados[['numero', 'Dúzia', 'Repetição Dúzia']])

    if any(x >= 11 for x in alertas):
        st.warning("⚠️ Alerta: Dúzia repetida por 11 ou mais vezes!")
else:
    st.info("Carregue um arquivo de resultados para análise da Estratégia 2.")

# Estratégia 3 – Zig-Zag / Alternância
st.subheader("\ud83d\udccc Estratégia 3 – Zig-Zag / Alternância")
def get_color(num):
    vermelhos = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
    pretos = {2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35}
    if num in vermelhos:
        return 'V'
    elif num in pretos:
        return 'P'
    else:
        return 'Z'

def alternancia(lista):
    return all(a != b for a, b in zip(lista, lista[1:]))

if os.path.exists(ARQUIVO_RESULTADOS):
    df_resultados = pd.read_csv(ARQUIVO_RESULTADOS)
    if len(df_resultados) >= 14:
        ultimos = df_resultados.tail(14)
        alto_baixo = ['A' if x >= 19 else 'B' if x > 0 else 'Z' for x in ultimos['numero']]
        par_impar = ['P' if x % 2 == 0 else 'I' for x in ultimos['numero'] if x != 0]
        cor = [get_color(x) for x in ultimos['numero']]

        if alternancia(alto_baixo):
            st.warning("⚠️ Alerta: Alternância entre Alto/Baixo detectada!")
        if alternancia(par_impar):
            st.warning("⚠️ Alerta: Alternância entre Par/Ímpar detectada!")
        if alternancia(cor):
            st.warning("⚠️ Alerta: Alternância entre Vermelho/Preto detectada!")
    else:
        st.info("São necessários ao menos 14 resultados para a análise da Estratégia 3.")
