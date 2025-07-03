import streamlit as st
from collections import defaultdict, deque

# Configuração inicial
if 'historico' not in st.session_state:
    st.session_state.historico = []
if 'proximas_cores' not in st.session_state:
    st.session_state.proximas_cores = defaultdict(lambda: deque(maxlen=100))  # Limite de 100 registros por número

# Mapeamento de cores (Roleta Europeia)
CORES = {
    0: 'G',  # Verde
    1: 'R', 2: 'B', 3: 'R', 4: 'B', 5: 'R', 6: 'B', 7: 'R', 8: 'B',
    9: 'R', 10: 'B', 11: 'B', 12: 'R', 13: 'B', 14: 'R', 15: 'B',
    16: 'R', 17: 'B', 18: 'R', 19: 'R', 20: 'B', 21: 'R', 22: 'B',
    23: 'R', 24: 'B', 25: 'R', 26: 'B', 27: 'R', 28: 'B', 29: 'B',
    30: 'R', 31: 'B', 32: 'R', 33: 'B', 34: 'R', 35: 'B', 36: 'R'
}

def registrar_numero(numero):
    # Registra a cor do número que veio DEPOIS do anterior
    if len(st.session_state.historico) > 0:
        numero_anterior = st.session_state.historico[-1]
        cor_atual = CORES.get(numero, 'G')
        st.session_state.proximas_cores[numero_anterior].append(cor_atual)
    
    st.session_state.historico.append(numero)

# Interface
st.title("Rastreamento de Cores Pós-Número")

# Entrada de dados
col1, col2 = st.columns(2)
with col1:
    novo_numero = st.number_input("Número sorteado (0-36)", min_value=0, max_value=36)
with col2:
    if st.button("Registrar"):
        registrar_numero(novo_numero)
uploaded_file = st.file_uploader("Carregar histórico (CSV)", type="csv")
if uploaded_file:
    numeros = pd.read_csv(uploaded_file)['Número'].tolist()
    for num in numeros:
        registrar_numero(num)
# Exibição organizada em 4 colunas
st.subheader("Últimas 100 cores após cada número")
cols = st.columns(4)
for numero in range(37):  # 0-36
    with cols[numero % 4]:
        historico = ''.join(st.session_state.proximas_cores[numero])
        st.text(f"{numero}: {historico}")

# Visualização da sequência
st.subheader("Sequência completa")
st.write(" → ".join(str(n) for n in st.session_state.historico[-100:]))
