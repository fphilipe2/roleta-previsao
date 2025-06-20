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

# Histórico em memória
if 'historico' not in st.session_state:
    st.session_state.historico = []

st.title("Bot de Estratégias para Roleta")

# Upload CSV
uploaded_file = st.file_uploader("Importar histórico (CSV)", type="csv")
if uploaded_file:
    st.session_state.historico = pd.read_csv(uploaded_file)['Número'].tolist()

# Inserir novo número
novo = st.number_input("Novo número da roleta", min_value=0, max_value=36, step=1)
add, delete = st.columns(2)
with add:
    if st.button("Adicionar número"):
        st.session_state.historico.append(novo)
with delete:
    if st.button("Excluir último número"):
        if st.session_state.historico:
            st.session_state.historico.pop()

# Exportar histórico
if st.button("Exportar histórico CSV"):
    df = pd.DataFrame({'Número': st.session_state.historico})
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(label="Download CSV", data=csv, file_name='historico_atualizado.csv', mime='text/csv')

# Estratégia Reflexiva
por_numero = {n: [] for n in range(37)}
for i in range(1, len(st.session_state.historico)):
    ant = st.session_state.historico[i - 1]
    atual = st.session_state.historico[i]
    if ant in numeros_proibidos and atual in numeros_proibidos[ant]:
        por_numero[ant].append("X")
    else:
        por_numero[ant].append("1")

# Mostrar reflexiva por faixa (3 colunas)
st.subheader("Resultados por Número (Reflexiva)")
col1, col2, col3 = st.columns(3)
alarme_ativo = False

def mostrar_resultados(coluna, inicio, fim):
    global alarme_ativo
    with coluna:
        for n in range(inicio, fim + 1):
            ultimos = por_numero[n][-5:]
            style = ""
            if len(ultimos) >= 2 and (ultimos[-2:] == ["X","X"] or ultimos.count("X")>=2):
                style = "background-color:#ffcccc; border:2px solid red; padding:4px;"
                alarme_ativo = True
            st.markdown(f"<div style='{style}'><strong>{n}</strong> = {' '.join(ultimos)}</div>", unsafe_allow_html=True)

mostrar_resultados(col1,0,11)
mostrar_resultados(col2,12,24)
mostrar_resultados(col3,25,36)

# Tocar som se alarme ativo
if alarme_ativo:
    st.audio("https://www.soundjay.com/button/beep-07.wav", format="audio/wav")

# Palpites de Jogo (últimos 5)
palpites = []
for i in range(1, len(st.session_state.historico)):
    ant = st.session_state.historico[i-1]
    atual = st.session_state.historico[i]
    if ant in numeros_proibidos and atual not in numeros_proibidos[ant]:
        palpites.append((i, ant, [n for n in range(37) if n not in numeros_proibidos.get(ant, [])]))
if palpites:
    st.subheader("Palpites de Jogo (últimos 5)")
    for idx, ant, sugestoes in palpites[-5:]:
        st.info(f"Após {ant}, evite {numeros_proibidos.get(ant, [])}. Sugestão: {sugestoes}")

# Palpite sequência de 3
st.subheader("Palpite por sequência de 3 números (qualquer ordem)")
if len(st.session_state.historico) >=5:
    ult3=set(st.session_state.historico[-3:])
    for i in range(len(st.session_state.historico)-5):
        if set(st.session_state.historico[i:i+3])==ult3:
            p1=st.session_state.historico[i+3]
            p2=st.session_state.historico[i+4]
            viz=sorted(set(vizinhos(p1)+vizinhos(p2)))
            st.write(f"Palpite: V{p1}V{p2} => {viz}")
            break

# Alertas repetição 9+
st.subheader("Alertas por repetição (a partir de 9 vezes)")
def alertar_repeticoes(tipo):
    if len(st.session_state.historico)<2: return
    cont=1
    ult=tipo(st.session_state.historico[0])
    for n in st.session_state.historico[1:]:
        at=tipo(n)
        if at==ult:
            cont+=1
            if cont>=9: st.warning(f"Alerta: {tipo.__name__} repetida {cont} vezes")
        else:
            cont=1; ult=at
alertar_repeticoes(obter_duzia)
alertar_repeticoes(obter_coluna)
alertar_repeticoes(obter_cor)
alertar_repeticoes(obter_paridade)
alertar_repeticoes(obter_alto_baixo)
