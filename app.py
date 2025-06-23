import streamlit as st
import pandas as pd
from collections import deque
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
duzias = {
    'D1': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,],
    'D2': [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
    'D3': [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]
}

colunas = {
    'C1': [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34],
    'C2': [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35],
    'C3': [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36]
}

numero_para_grupos = {}
for num in range(37):  # 0-36
    grupos_num = []
    # Verifica dúzia
    for d, nums in duzias.items():
        if num in nums:
            grupos_num.append(d)
    # Verifica coluna
    for c, nums in colunas.items():
        if num in nums:
            grupos_num.append(c)
    numero_para_grupos[num] = grupos_num
st.set_page_config(page_title="Bot de Estratégias para Roleta", layout="wide")

# Inicialização do session state
if 'historico' not in st.session_state:
    st.session_state.historico = []
if 'reflexiva_seq' not in st.session_state:
    st.session_state.reflexiva_seq = []
if 'alternancia_dupla_seq' not in st.session_state:
    st.session_state.alternancia_dupla_seq = []

# Função para atualizar todas as estratégias
def atualizar_estrategias():
    # Estratégia Reflexiva
# Estratégia Reflexiva (única verificação)
    if len(st.session_state.historico) >= 2:
        ant = st.session_state.historico[-2]
        atual = st.session_state.historico[-1]
        
        # Verificação única (não duplicada)
        if ant in numeros_proibidos and atual in numeros_proibidos[ant]:
            st.session_state.reflexiva_seq.append('X')
        else:
            st.session_state.reflexiva_seq.append('1')
            
        if len(st.session_state.reflexiva_seq) > 250:
            st.session_state.reflexiva_seq.pop(0)

    # Estratégia Alternância Dupla Modificada
    if len(st.session_state.historico) >= 2:
        ant = st.session_state.historico[-2]
        atual = st.session_state.historico[-1]
        res = 'X' if (ant in numeros_proibidos and atual in numeros_proibidos[ant]) else '1'
        st.session_state.reflexiva_seq.append(res)
        if len(st.session_state.reflexiva_seq) > 250:
            st.session_state.reflexiva_seq.pop(0)

    # Estratégia Alternância Dupla - VERSAO CORRIGIDA (único resultado)
    if len(st.session_state.historico) >= 2:
        ant = st.session_state.historico[-2]
        atual = st.session_state.historico[-1]
        
        if ant == 0:
            resultado = 'X'
        else:
            # Verifica APENAS UMA VEZ se compartilham QUALQUER grupo
            grupos_ant = numero_para_grupos[ant]
            grupos_atual = numero_para_grupos[atual]
            resultado = '1' if any(grupo in grupos_atual for grupo in grupos_ant) else 'X'
        
        # Adiciona APENAS UM RESULTADO à sequência
        st.session_state.alternancia_dupla_seq.append(resultado)
        
        if len(st.session_state.alternancia_dupla_seq) > 250:
                    st.session_state.alternancia_dupla_seq.pop(0)

# Funções de formatação
def formatar_reflexiva(seq):
    res = []
    cont = 1
    for val in seq:
        if val == 'X':
            res.append('<span style="color:red">X</span>')
            cont = 1
        else:
            res.append(str(cont))
            cont += 1
    return '<br>'.join([''.join(res[i:i+50]) for i in range(0, len(res), 50)])

def formatar_alternancia(seq):
    res = ['<span style="color:red">X</span>' if v == 'X' else v for v in seq]
    return '<br>'.join([''.join(res[i:i+50]) for i in range(0, len(res), 50)])

# Interface principal
st.title("Bot de Estratégias para Roleta")

# Upload CSV
uploaded_file = st.file_uploader("Importar histórico (CSV)", type="csv")
if uploaded_file:
    st.session_state.historico = pd.read_csv(uploaded_file)['Número'].tolist()
    atualizar_estrategias()

# Controles para adicionar/remover números
novo = st.number_input("Novo número da roleta", min_value=0, max_value=36, step=1)
col1, col2 = st.columns([1, 5])
with col1:
    if st.button("Adicionar número"):
        st.session_state.historico.append(novo)
        atualizar_estrategias()

if st.button("⛔ Excluir último número"):
    if st.session_state.historico:
        st.session_state.historico.pop()
        atualizar_estrategias()
        st.warning("Número removido do histórico.")
    else:
        st.warning("O histórico está vazio.")

# Exportar histórico
csv_export = pd.DataFrame({'Número': st.session_state.historico}).to_csv(index=False).encode('utf-8')
st.download_button("📥 Exportar histórico CSV", data=csv_export, file_name='historico.csv', mime='text/csv')

# Resultados por número (Reflexiva)
st.subheader("Resultados por Número (Reflexiva)")
por_numero = {n: deque(maxlen=20) for n in range(37)}
for i in range(1, len(st.session_state.historico)):
    ant, atual = st.session_state.historico[i-1], st.session_state.historico[i]
    por_numero[ant].append("X" if (ant in numeros_proibidos and atual in numeros_proibidos[ant]) else "1")

col1, col2, col3 = st.columns(3)
for i, col in zip(range(0, 37, 12), [col1, col2, col3]):
    with col:
        for j in range(i, i + 12):
            st.write(f"{j} = {' '.join(por_numero[j])}")

# Estratégia Reflexiva
st.subheader("Resultados Reflexiva - sequência completa")
st.markdown(formatar_reflexiva(st.session_state.reflexiva_seq), unsafe_allow_html=True)

# Estratégia Alternância Dupla
st.subheader("Resultados Estratégia de Alternância Dupla")
st.markdown(formatar_alternancia(st.session_state.alternancia_dupla_seq), unsafe_allow_html=True)

# Estratégia: Padrão de 3 Números
def vizinhos(numero):
    return [(numero + i) % 37 for i in range(-5, 6)]

st.subheader("Padrão de 3 Números")
if len(st.session_state.historico) >= 5:
    ultimos = set(st.session_state.historico[-3:])
    for i in range(len(st.session_state.historico) - 5):
        if set(st.session_state.historico[i:i+3]) == ultimos and i + 5 < len(st.session_state.historico):
            p1, p2 = st.session_state.historico[i+3], st.session_state.historico[i+4]
            viz = sorted(set(vizinhos(p1) + vizinhos(p2)))
            st.write(f"Padrão: {ultimos}. V{p1}V{p2}: {viz}")
            break




