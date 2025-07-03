import streamlit as st
import pandas as pd
from collections import defaultdict, deque

# Configuração inicial
if 'historico' not in st.session_state:
    st.session_state.historico = []
if 'proximas_cores' not in st.session_state:
    st.session_state.proximas_cores = defaultdict(lambda: deque(maxlen=100))

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
    if len(st.session_state.historico) > 0:
        numero_anterior = st.session_state.historico[-1]
        cor_atual = CORES.get(numero, 'G')
        st.session_state.proximas_cores[numero_anterior].append(cor_atual)
    st.session_state.historico.append(numero)

# Função para formatar com cores
def formatar_cor(c):
    if c == 'R':
        return '<span style="color:red">R</span>'
    elif c == 'B':
        return '<span style="color:black">B</span>'
    else:  # G
        return '<span style="color:green">G</span>'

# Interface
st.title("Rastreamento de Cores Pós-Número")

# Entrada manual
col1, col2 = st.columns(2)
with col1:
    novo_numero = st.number_input("Número sorteado (0-36)", min_value=0, max_value=36)
with col2:
    if st.button("Registrar"):
        registrar_numero(novo_numero)

# Upload de CSV
uploaded_file = st.file_uploader("Carregar histórico (CSV)", type="csv")
if uploaded_file:
    try:
        dados = pd.read_csv(uploaded_file)
        if 'Número' in dados.columns:
            for num in dados['Número'].tolist():
                registrar_numero(num)
            st.success("Histórico carregado com sucesso!")
        else:
            st.error("O arquivo CSV precisa ter uma coluna chamada 'Número'")
    except Exception as e:
        st.error(f"Erro ao ler arquivo: {e}")

# Exibição organizada com cores
st.subheader("Últimas 100 cores após cada número")
cols = st.columns(4)
for numero in range(37):  # 0-36
    with cols[numero % 4]:
        # Formata cada caractere com sua cor
        historico_formatado = ''.join([formatar_cor(c) for c in st.session_state.proximas_cores[numero]])
        st.markdown(f"{numero}: {historico_formatado}", unsafe_allow_html=True)

# Visualização da sequência
st.subheader("Últimos números sorteados")
st.write(" → ".join(str(n) for n in st.session_state.historico[-50:]))
