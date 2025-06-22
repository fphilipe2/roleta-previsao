import streamlit as st
import pandas as pd
from datetime import datetime
from collections import deque
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

# Configurações iniciais
st.set_page_config(page_title="Bot de Estratégias para Roleta", layout="centered")

if 'historico' not in st.session_state:
    st.session_state.historico = []
if 'reflexiva_sequencia' not in st.session_state:
    st.session_state.reflexiva_sequencia = []
if 'alternancia_resultados' not in st.session_state:
    st.session_state.alternancia_resultados = []
if 'p3n_alerta' not in st.session_state:
    st.session_state.p3n_alerta = None

# Funções auxiliares
def obter_duzia(numero):
    if numero == 0:
        return 0
    return (numero - 1) // 12 + 1

def obter_coluna(numero):
    if numero == 0:
        return 0
    return (numero - 1) % 3 + 1

def vizinhos(numero):
    return [(numero + i) % 37 for i in range(-5, 6)]

# Interface
st.title("Bot de Estratégias para Roleta")
uploaded_file = st.file_uploader("Importar histórico (CSV)", type="csv")
if uploaded_file:
    st.session_state.historico = pd.read_csv(uploaded_file)['Número'].tolist()

novo = st.number_input("Novo número da roleta", min_value=0, max_value=36, step=1)
if st.button("Adicionar número"):
    st.session_state.historico.append(novo)

if st.button("Exportar histórico CSV"):
    df = pd.DataFrame({'Número': st.session_state.historico})
    df.to_csv("historico_atualizado.csv", index=False)
    st.success("Histórico exportado com sucesso!")

# Estratégia Reflexiva
por_numero = {n: [] for n in range(37)}
sequencia_reflexiva = []
historico = st.session_state.historico

for i in range(1, len(historico)):
    ant, atual = historico[i-1], historico[i]
    if ant in numeros_proibidos and atual in numeros_proibidos[ant]:
        por_numero[ant].append("X")
        sequencia_reflexiva.append("X")
    else:
        por_numero[ant].append("1")
        sequencia_reflexiva.append("1")
    if len(por_numero[ant]) > 20:
        por_numero[ant].pop(0)
if len(sequencia_reflexiva) > 250:
    sequencia_reflexiva = sequencia_reflexiva[-250:]

st.subheader("Resultados por Número (Reflexiva)")
col1, col2, col3 = st.columns(3)
for col, rng in zip([col1, col2, col3], [(0,11), (12,24), (25,36)]):
    with col:
        for n in range(*rng):
            valores = por_numero[n][-20:] if n in por_numero else []
            st.markdown(f"**{n} =** {' '.join(valores)}")

# Estratégia Reflexiva - Sequência
st.subheader("Resultados Reflexiva - sequência completa")
blocos = []
seq = []
cont = 0
for r in sequencia_reflexiva:
    if r == "X":
        if cont > 0:
            seq.append(str(cont))
            cont = 0
        seq.append('<span style="color:red">X</span>')
    else:
        cont += 1
if cont > 0:
    seq.append(str(cont))
for i in range(0, len(seq), 50):
    blocos.append(''.join(seq[i:i+50]))
for bloco in blocos:
    st.markdown(bloco, unsafe_allow_html=True)

# Estratégia Alternância Dupla (por grupo)
alternancia_grupos = [
    [1,4,7,10], [2,5,8,11], [3,6,9,12],
    [13,16,19,22], [14,17,20,23], [15,18,21,24],
    [25,28,31,34], [26,29,32,35], [27,30,33,36]
]
grupo_anterior = None
resultado_alternancia = st.session_state.alternancia_resultados
if len(historico) >= 2:
    for i in range(1, len(historico)):
        atual = historico[i]
        anterior = historico[i-1]
        if anterior == 0:
            grupo_anterior = None
            continue
        grupo_atual = next((g for g in alternancia_grupos if anterior in g), None)
        if grupo_atual:
            if atual in grupo_atual:
                resultado_alternancia.append("1")
            else:
                resultado_alternancia.append("<span style='color:red'>X</span>")
        if len(resultado_alternancia) > 250:
            resultado_alternancia = resultado_alternancia[-250:]
    st.session_state.alternancia_resultados = resultado_alternancia

st.subheader("Resultados Estratégia de Alternância Dupla (Dúzia e Coluna)")
for i in range(0, len(resultado_alternancia), 50):
    st.markdown(''.join(resultado_alternancia[i:i+50]), unsafe_allow_html=True)

# Estratégia Padrão de 3 Números (Vizinhos)
st.subheader("Estratégia: Padrão de 3 Números (Repetição em qualquer ordem)")
if len(historico) >= 5:
    ultimos3 = set(historico[-3:])
    for i in range(len(historico)-5):
        padrao = set(historico[i:i+3])
        if ultimos3 == padrao:
            p1, p2 = historico[i+3], historico[i+4]
            vizinhos1 = vizinhos(p1)
            vizinhos2 = vizinhos(p2)
            jogada = list(set(vizinhos1 + vizinhos2))
            st.info(f"Detectado padrão: {padrao} => Jogar V{p1} e V{p2}: {sorted(jogada)}")
            break
