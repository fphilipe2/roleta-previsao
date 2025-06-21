import streamlit as st
import pandas as pd
from datetime import datetime
from collections import deque
import base64

# Funções auxiliares para análise

def vizinhos(numero):
    return [(numero + i) % 37 for i in range(-5, 6)]

def obter_duzia(numero):
    if numero == 0:
        return 0
    return (numero - 1) // 12 + 1

def obter_coluna(numero):
    if numero == 0:
        return 0
    return (numero - 1) % 3 + 1

def obter_cor(numero):
    vermelhos = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
    if numero == 0:
        return 'verde'
    return 'vermelho' if numero in vermelhos else 'preto'

def obter_paridade(numero):
    if numero == 0:
        return 'zero'
    return 'par' if numero % 2 == 0 else 'ímpar'

def obter_alto_baixo(numero):
    if numero == 0:
        return 'zero'
    return 'baixo' if numero <= 18 else 'alto'

# Lista de números proibidos
numeros_proibidos = {
    1: [3, 7, 8, 11, 12, 13, 28, 29, 30, 35, 36],
    36: [1, 2, 4, 14, 15, 16, 19, 20, 21, 24, 33],
    2: [3, 7, 8, 11, 12, 23, 26, 28, 30, 35, 36],
    20: [3, 7, 8, 11, 12, 23, 26, 28, 30, 35, 36],
    3: [1, 2, 9, 14, 17, 20, 21, 22, 25, 31, 34],
    8: [1, 2, 9, 14, 17, 20, 21, 22, 25, 31, 34],
    4: [7, 11, 12, 13, 18, 27, 28, 29, 30, 35, 36],
    33: [7, 11, 12, 13, 18, 27, 28, 29, 30, 35, 36],
    5: [6, 7, 9, 13, 17, 18, 22, 27, 29, 31, 34],
    32: [6, 7, 9, 13, 17, 18, 22, 27, 29, 31, 34],
    6: [0, 3, 5, 10, 15, 16, 19, 23, 24, 26, 32],
    18: [0, 3, 5, 10, 15, 16, 19, 23, 24, 26, 32],
    7: [1, 2, 4, 15, 16, 19, 20, 21, 24, 32, 33],
    9: [0, 3, 5, 8, 10, 23, 24, 26, 30, 32, 35],
    17: [0, 3, 5, 8, 10, 23, 24, 26, 30, 32, 35],
    10: [6, 9, 14, 17, 18, 22, 25, 27, 29, 31, 34],
    0: [6, 9, 14, 17, 18, 22, 25, 27, 29, 31, 34],
    11: [1, 2, 4, 14, 16, 19, 20, 21, 25, 31, 33],
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
    30: [1, 2, 4, 9, 14, 17, 20, 21, 25, 31, 33],
    35: [1, 2, 4, 9, 14, 17, 20, 21, 25, 31, 33],
    31: [0, 3, 5, 8, 10, 11, 12, 23, 26, 30, 35],
    34: [0, 3, 5, 8, 10, 23, 24, 26, 30, 32, 35],
}

# Armazenamento do histórico completo
if 'historico' not in st.session_state:
    st.session_state.historico = []
if 'reflexiva_resultados' not in st.session_state:
    st.session_state.reflexiva_resultados = []
if 'alternancia_resultados' not in st.session_state:
    st.session_state.alternancia_resultados = []

st.title("Bot de Estratégias para Roleta")

# Upload de CSV
uploaded_file = st.file_uploader("Importar histórico (CSV)", type="csv")
if uploaded_file:
    st.session_state.historico = pd.read_csv(uploaded_file)['Número'].tolist()

# Inserir novo número
novo = st.number_input("Novo número da roleta", min_value=0, max_value=36, step=1)
if st.button("Adicionar número"):
    st.session_state.historico.append(novo)

# Botão para limpar alertas
if st.button("Limpar Alertas"):
    st.session_state.reflexiva_resultados.clear()
    st.session_state.alternancia_resultados.clear()

# Exportar histórico
if st.button("Exportar histórico CSV"):
    df = pd.DataFrame({'Número': st.session_state.historico})
    df.to_csv("historico_atualizado.csv", index=False)
    st.success("Histórico exportado com sucesso!")

# Estratégia Reflexiva - associar resultado ao número anterior
por_numero = {n: deque(maxlen=20) for n in range(37)}
reflexiva_seq = deque(maxlen=250)

for i in range(1, len(st.session_state.historico)):
    ant = st.session_state.historico[i - 1]
    atual = st.session_state.historico[i]
    if ant in numeros_proibidos and atual in numeros_proibidos[ant]:
        por_numero[ant].append("X")
        reflexiva_seq.append("X")
    else:
        por_numero[ant].append("1")
        if reflexiva_seq and reflexiva_seq[-1].isdigit():
            reflexiva_seq[-1] = str(int(reflexiva_seq[-1]) + 1)
        else:
            reflexiva_seq.append("1")

# Mostrar reflexiva por faixa (3 colunas)
st.subheader("Resultados por Número (Reflexiva)")
col1, col2, col3 = st.columns(3)

def mostrar_resultados(coluna, inicio, fim):
    with coluna:
        for n in range(inicio, fim + 1):
            ultimos = list(por_numero[n])
            st.markdown(f"<strong>{n}</strong> = {' '.join(ultimos)}", unsafe_allow_html=True)

mostrar_resultados(col1, 0, 11)
mostrar_resultados(col2, 12, 24)
mostrar_resultados(col3, 25, 36)

# Sequência Reflexiva
st.subheader("Resultados Reflexiva - sequência completa")
bloco = ""
for i, val in enumerate(reflexiva_seq):
    if val == "X":
        bloco += f"<span style='color:red;'>X</span>"
    else:
        bloco += val
    if (i + 1) % 50 == 0:
        bloco += "<br>"
st.markdown(f"<div style='font-family:monospace;'>{bloco}</div>", unsafe_allow_html=True)

# Estratégia de Alternância Dupla (fixa por grupo)
st.subheader("Resultados Estratégia de Alternância Dupla (Dúzia e Coluna)")
grupos = [
    [1, 4, 7, 10], [2, 5, 8, 11], [3, 6, 9, 12],
    [13, 16, 19, 22], [14, 17, 20, 23], [15, 18, 21, 24],
    [25, 28, 31, 34], [26, 29, 32, 35], [27, 30, 33, 36]
]

alternancia_seq = deque(maxlen=250)
for i in range(1, len(st.session_state.historico)):
    prev = st.session_state.historico[i - 1]
    atual = st.session_state.historico[i]

    if prev == 0:
        continue

    grupo = next((g for g in grupos if prev in g), None)
    if grupo:
        if atual in grupo:
            alternancia_seq.append("1")
        else:
            alternancia_seq.append("X")

bloco_alt = ""
for i, val in enumerate(alternancia_seq):
    if val == "X":
        bloco_alt += f"<span style='color:red;'>X</span>"
    else:
        bloco_alt += val
    if (i + 1) % 50 == 0:
        bloco_alt += "<br>"
st.markdown(f"<div style='font-family:monospace;'>{bloco_alt}</div>", unsafe_allow_html=True)
