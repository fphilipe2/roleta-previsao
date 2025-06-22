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

st.set_page_config(page_title="Bot de Estratégias para Roleta", layout="wide")

# Sessões e histórico
if 'historico' not in st.session_state:
    st.session_state.historico = []
if 'reflexiva_seq' not in st.session_state:
    st.session_state.reflexiva_seq = []
if 'alternancia_dupla_seq' not in st.session_state:
    st.session_state.alternancia_dupla_seq = []

st.title("Bot de Estratégias para Roleta")

# Upload CSV
uploaded_file = st.file_uploader("Importar histórico (CSV)", type="csv")
if uploaded_file:
    st.session_state.historico = pd.read_csv(uploaded_file)['Número'].tolist()

# Inserir novo número
novo = st.number_input("Novo número da roleta", min_value=0, max_value=36, step=1)
col1, col2 = st.columns([1, 5])
with col1:
    if st.button("Adicionar número"):
        st.session_state.historico.append(novo)
        # Reflexiva
        if len(st.session_state.historico) >= 2:
            ant = st.session_state.historico[-2]
            atual = st.session_state.historico[-1]
            if ant in numeros_proibidos and atual in numeros_proibidos[ant]:
                res = 'X'
            else:
                res = '1'
            st.session_state.reflexiva_seq.append(res)
            if len(st.session_state.reflexiva_seq) > 250:
                st.session_state.reflexiva_seq.pop(0)

        # Alternância Dupla por grupo
        grupos = [
            [1, 4, 7, 10], [2, 5, 8, 11], [3, 6, 9, 12],
            [13, 16, 19, 22], [14, 17, 20, 23], [15, 18, 21, 24],
            [25, 28, 31, 34], [26, 29, 32, 35], [27, 30, 33, 36]
        ]
        if len(st.session_state.historico) >= 2:
            ant = st.session_state.historico[-2]
            atual = st.session_state.historico[-1]
            for grupo in grupos:
                if ant in grupo:
                    if atual in grupo:
                        st.session_state.alternancia_dupla_seq.append('1')
                    else:
                        st.session_state.alternancia_dupla_seq.append('X')
                    if len(st.session_state.alternancia_dupla_seq) > 250:
                        st.session_state.alternancia_dupla_seq.pop(0)
                    break

with col2:
    if st.button("Exportar histórico CSV"):
        df = pd.DataFrame({'Número': st.session_state.historico})
        df.to_csv("historico_atualizado.csv", index=False)
        st.success("Histórico exportado com sucesso!")

# Resultados por número (Reflexiva)
st.subheader("Resultados por Número (Reflexiva)")
por_numero = {n: deque(maxlen=20) for n in range(37)}
for i in range(1, len(st.session_state.historico)):
    ant = st.session_state.historico[i - 1]
    atual = st.session_state.historico[i]
    if ant in numeros_proibidos and atual in numeros_proibidos[ant]:
        por_numero[ant].append("X")
    else:
        por_numero[ant].append("1")
col1, col2, col3 = st.columns(3)
for i, col in zip(range(0, 37, 12), [col1, col2, col3]):
    with col:
        for j in range(i, i + 12):
            resultados = ' '.join(por_numero[j])
            st.write(f"{j} = {resultados}")

# Estratégia Reflexiva - sequência completa
st.subheader("Resultados Reflexiva - sequência completa")
def formatar_reflexiva(seq):
    res = []
    cont = 1
    for i, val in enumerate(seq):
        if val == 'X':
            res.append('<span style="color:red">X</span>')
            cont = 1
        else:
            res.append(str(cont))
            cont += 1
    linhas = [''.join(res[i:i+50]) for i in range(0, len(res), 50)]
    return '<br>'.join(linhas)
st.markdown(formatar_reflexiva(st.session_state.reflexiva_seq), unsafe_allow_html=True)

# Estratégia Alternância Dupla - Dúzia e Coluna
st.subheader("Resultados Estratégia de Alternância Dupla (Dúzia e Coluna)")
def formatar_estrategia(seq):
    res = []
    for v in seq:
        if v == 'X':
            res.append('<span style="color:red">X</span>')
        else:
            res.append(v)
    linhas = [''.join(res[i:i+50]) for i in range(0, len(res), 50)]
    return '<br>'.join(linhas)
st.markdown(formatar_estrategia(st.session_state.alternancia_dupla_seq), unsafe_allow_html=True)

# Estratégia: Padrão de 3 Números (Repetição em qualquer ordem)
st.subheader("Estratégia: Padrão de 3 Números (Repetição em qualquer ordem)")

if len(st.session_state.historico) >= 5:
    ultimos = st.session_state.historico[-3:]
    ultimos_set = set(ultimos)

    for i in range(len(st.session_state.historico) - 5):
        padrao = st.session_state.historico[i:i+3]
        if set(padrao) == ultimos_set:
            if i + 5 < len(st.session_state.historico):
                p1 = st.session_state.historico[i+3]
                p2 = st.session_state.historico[i+4]
                try:
                    viz1 = vizinhos(p1)
                    viz2 = vizinhos(p2)
                    viz = sorted(set(viz1 + viz2))
                    st.write(f"Padrão detectado: {set(padrao)}. V{p1}V{p2}: {viz}")
                except Exception as e:
                    st.error(f"Erro ao gerar vizinhos: {e}")
            break



