import streamlit as st
from collections import defaultdict, deque

# Configuração inicial
if 'historico' not in st.session_state:
    st.session_state.historico = []
if 'cores_por_numero' not in st.session_state:
    st.session_state.cores_por_numero = defaultdict(lambda: deque(maxlen=100))

# Mapeamento completo de cores (0 = verde, outros conforme roleta europeia)
CORES = {
    0: 'G',
    1: 'R', 2: 'B', 3: 'R', 4: 'B', 5: 'R', 6: 'B', 7: 'R', 8: 'B',
    9: 'R', 10: 'B', 11: 'B', 12: 'R', 13: 'B', 14: 'R', 15: 'B',
    16: 'R', 17: 'B', 18: 'R', 19: 'R', 20: 'B', 21: 'R', 22: 'B',
    23: 'R', 24: 'B', 25: 'R', 26: 'B', 27: 'R', 28: 'B', 29: 'B',
    30: 'R', 31: 'B', 32: 'R', 33: 'B', 34: 'R', 35: 'B', 36: 'R'
}

def atualizar_cores(numero):
    cor = CORES.get(numero, 'G')
    st.session_state.cores_por_numero[numero].append(cor)
uploaded_file = st.file_uploader("Carregar CSV", type="csv")
if uploaded_file:
    numeros = pd.read_csv(uploaded_file)['Número'].tolist()
    for num in numeros:
        atualizar_cores(num)
# Interface
st.title("Estratégia de Cores - Roleta")

# Entrada de dados
col1, col2 = st.columns(2)
with col1:
    novo_numero = st.number_input("Número (0-36)", min_value=0, max_value=36)
with col2:
    if st.button("Adicionar"):
        st.session_state.historico.append(novo_numero)
        atualizar_cores(novo_numero)

# Exibição dos resultados
st.subheader("Histórico de Cores por Número")

# Organiza em 4 colunas para melhor visualização
cols = st.columns(4)
for i in range(37):  # 0-36
    with cols[i % 4]:
        historico = ''.join(st.session_state.cores_por_numero[i])
        st.text(f"{i}: {historico}")

# Histórico completo
st.subheader("Sequência Completa")
st.text(' → '.join(str(n) for n in st.session_state.historico[-100:]))
