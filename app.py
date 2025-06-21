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

# Lista de números proibidos (mesmo conteúdo)
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

st.title("Bot de Estratégias para Roleta")

uploaded_file = st.file_uploader("Importar histórico (CSV)", type="csv")
if uploaded_file:
    st.session_state.historico = pd.read_csv(uploaded_file)['Número'].tolist()

novo = st.number_input("Novo número da roleta", min_value=0, max_value=36, step=1)
col1, col2 = st.columns(2)
with col1:
    if st.button("Adicionar número"):
        st.session_state.historico.append(novo)
with col2:
    if st.button("Excluir último número") and st.session_state.historico:
        st.session_state.historico.pop()

if st.button("Exportar histórico CSV"):
    df = pd.DataFrame({'Número': st.session_state.historico})
    df.to_csv("historico_atualizado.csv", index=False)
    st.success("Histórico exportado com sucesso!")

resultado_reflexivo = [''] * len(st.session_state.historico)
por_numero = {n: deque(maxlen=20) for n in range(37)}
reflexiva_seq = deque(maxlen=250)

for i in range(1, len(st.session_state.historico)):
    ant = st.session_state.historico[i - 1]
    atual = st.session_state.historico[i]
    if ant in numeros_proibidos and atual in numeros_proibidos[ant]:
        resultado_reflexivo[i - 1] = "X"
        por_numero[ant].append("X")
        reflexiva_seq.append("<span style='color:red'>X</span>")
    else:
        resultado_reflexivo[i - 1] = "1"
        por_numero[ant].append("1")
        count = 1
        while len(reflexiva_seq) >= count and '1' in reflexiva_seq[-count]:
            count += 1
        reflexiva_seq.append(str(count))

st.subheader("Resultados por Número (Reflexiva)")
col1, col2, col3 = st.columns(3)

alarme_ativo = False

def mostrar_resultados(coluna, inicio, fim):
    global alarme_ativo
    with coluna:
        for n in range(inicio, fim + 1):
            ultimos = list(por_numero[n])
            alert_style = ""
            if ultimos[-2:] == ["X", "X"] or ultimos.count("X") >= 2 and len(ultimos) >= 3:
                alert_style = "background-color: #ffcccc; border: 2px solid red; padding: 4px;"
                alarme_ativo = True
            st.markdown(f"<div style='{alert_style}'><strong>{n}</strong> = {' '.join(ultimos)}</div>", unsafe_allow_html=True)

mostrar_resultados(col1, 0, 11)
mostrar_resultados(col2, 12, 24)
mostrar_resultados(col3, 25, 36)

if alarme_ativo:
    st.audio("https://www.soundjay.com/button/beep-07.wav", format="audio/wav")

st.subheader("Resultados Reflexiva - sequência completa")
chunks = ["".join(reflexiva_seq)[i:i+80] for i in range(0, len(reflexiva_seq), 80)]
for c in chunks:
    st.markdown(f"<div style='font-family:monospace'>{c}</div>", unsafe_allow_html=True)

st.subheader("Resultados Estratégia de Alternância Dupla (Dúzia e Coluna)")
if len(st.session_state.historico) >= 5:
    alt_dupla = []
    for i in range(2, len(st.session_state.historico)):
        d1, c1 = obter_duzia(st.session_state.historico[i - 2]), obter_coluna(st.session_state.historico[i - 2])
        d2, c2 = obter_duzia(st.session_state.historico[i - 1]), obter_coluna(st.session_state.historico[i - 1])
        d3, c3 = obter_duzia(st.session_state.historico[i]), obter_coluna(st.session_state.historico[i])
        if (d1 != d2 and d2 != d3 and d1 != d3) and (c1 != c2 and c2 != c3 and c1 != c3):
            alt_dupla.append((st.session_state.historico[i - 2:i + 1]))
    if alt_dupla:
        for s in alt_dupla[-3:]:
            st.markdown(f"Alternância Dupla detectada: {s}")
        st.audio("https://www.soundjay.com/button/beep-07.wav", format="audio/wav")

st.subheader("Alertas por repetição (a partir de 9 vezes)")
def alertar_repeticoes(tipo):
    if len(st.session_state.historico) < 2:
        return
    contagem = 1
    ultimo = tipo(st.session_state.historico[0])
    for n in st.session_state.historico[1:]:
        atual = tipo(n)
        if atual == ultimo:
            contagem += 1
            if contagem >= 9:
                st.warning(f"Alerta: {tipo.__name__} repetida {contagem} vezes seguidas")
        else:
            contagem = 1
            ultimo = atual

alertar_repeticoes(obter_duzia)
alertar_repeticoes(obter_coluna)
alertar_repeticoes(obter_cor)
alertar_repeticoes(obter_paridade)
alertar_repeticoes(obter_alto_baixo)
