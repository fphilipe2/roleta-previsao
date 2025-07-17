import streamlit as st
import pandas as pd

# Configuração inicial
if 'historico' not in st.session_state:
    st.session_state.historico = []
if 'resultados' not in st.session_state:
    st.session_state.resultados = ""

# ESTRATÉGIA (com acento)
ESTRATÉGIA = {
    0: [0, 5, 9, 10, 17, 22, 23, 25, 26, 31, 32, 34],
    1: [1, 2, 4, 7, 11, 12, 13, 28, 20, 21, 33, 36],
    2: [1, 2, 3, 8, 11, 12, 14, 20, 21, 25, 30, 35],
    3: [3, 8, 9, 17, 23, 25, 26, 30, 31, 34, 35],
    4: [1, 4, 7, 9, 11, 12, 13, 16, 21, 28, 33, 36],
    5: [0, 5, 6, 9, 10, 15, 18, 22, 24, 27, 32, 34],
    6: [0, 5, 6, 9, 10, 15, 18, 22, 24, 27, 32, 34],
    7: [1, 4, 7, 9, 11, 13, 16, 21, 28, 29, 33, 36],
    8: [1, 3, 4, 8, 9, 16, 21, 23, 26, 30, 33, 35],
    9: [0, 3, 8, 19, 10, 17, 22, 23, 25, 26, 31, 34],
    10: [0, 5, 6, 9, 10, 17, 22, 23, 26, 31, 32, 34],
    11: [1, 2, 4, 11, 12, 20, 21, 28, 30, 33, 35, 36],
    12: [1, 2, 4, 11, 12, 20, 21, 28, 30, 33, 35, 36],
    13: [1, 4, 7, 13, 15, 16, 19, 27, 28, 29, 33, 36],
    14: [2, 3, 8, 14, 17, 20, 23, 25, 26, 30, 31, 35],
    15: [5, 6, 7, 15, 16, 18, 19, 24, 27, 29, 32, 34],
    16: [1, 4, 7, 13, 15, 16, 19, 27, 28, 29, 33, 36],
    17: [0, 3, 8, 9, 10, 17, 22, 23, 25, 26, 31, 34],
    18: [0, 5, 6, 10, 15, 18, 22, 24, 27, 29, 32, 34],
    19: [1, 4, 7, 13, 15, 16, 19, 27, 28, 29, 33, 36],
    20: [1, 2, 3, 8, 11, 12, 14, 20, 21, 25, 30, 35],
    21: [1, 2, 4, 7, 11, 12, 13, 28, 20, 21, 33, 36],
    22: [0, 5, 6, 9, 10, 15, 18, 22, 24, 27, 32, 34],
    23: [0, 3, 8, 9, 10, 17, 22, 23, 25, 26, 31, 34],
    24: [5, 6, 7, 15, 16, 18, 19, 24, 27, 29, 32, 34],
    25: [2, 3, 8, 14, 17, 20, 23, 25, 26, 30, 31, 35],
    26: [0, 3, 8, 9, 10, 17, 22, 23, 25, 26, 31, 34],
    27: [5, 6, 7, 15, 16, 18, 19, 24, 27, 29, 32, 34],
    28: [1, 2, 4, 7, 11, 12, 13, 28, 20, 21, 33, 36],
    29: [5, 6, 7, 15, 16, 18, 19, 24, 27, 29, 32, 34],
    30: [1, 2, 3, 8, 11, 12, 14, 20, 21, 25, 30, 35],
    31: [2, 3, 8, 9, 14, 17, 23, 25, 26, 30, 31, 35],
    32: [0, 5, 6, 9, 10, 15, 18, 22, 24, 27, 32, 34],
    33: [1, 4, 7, 9, 11, 12, 13, 16, 21, 28, 33, 36],
    34: [0, 5, 9, 10, 17, 22, 23, 25, 26, 31, 32, 34],
    35: [1, 2, 3, 8, 11, 12, 14, 20, 21, 25, 30, 35],
    36: [1, 2, 4, 7, 11, 12, 13, 28, 20, 21, 33, 36]
}

def registrar_numero(numero):
    st.session_state.historico.append(numero)
    # Atualiza a string de resultados
    if numero in ESTRATÉGIA.get(numero, []):
        st.session_state.resultados += "1" if numero == 0 else "X"
    else:
        st.session_state.resultados += "-"

# Interface
st.title("Sequência de Apostas na Roleta")

# Controles
numero = st.number_input("Último número sorteado (0-36)", min_value=0, max_value=36)
if st.button("Registrar"):
    registrar_numero(numero)

# Upload de CSV
uploaded_file = st.file_uploader("Carregar histórico (CSV)", type="csv")
if uploaded_file is not None:
    try:
        dados = pd.read_csv(uploaded_file)
        if 'Número' in dados.columns:
            st.session_state.historico = dados['Número'].tolist()
            st.session_state.resultados = ""
            for num in st.session_state.historico:
                if num in ESTRATÉGIA.get(num, []):
                    st.session_state.resultados += "1" if num == 0 else "X"
                else:
                    st.session_state.resultados += "-"
            st.success("Histórico carregado!")
    except Exception as e:
        st.error(f"Erro ao ler arquivo: {e}")

# Exibição dos resultados
if st.session_state.historico:
    st.subheader("Resultado por Número")
    col1, col2 = st.columns(2)
    
    with col1:
        for i, num in enumerate(st.session_state.historico[:len(st.session_state.historico)//2+1]):
            resultado = "1" if num == 0 else "X" if num in ESTRATÉGIA.get(num, []) else ""
            st.write(f"{num}: {resultado}")
    
    with col2:
        for i, num in enumerate(st.session_state.historico[len(st.session_state.historico)//2+1:]):
            resultado = "1" if num == 0 else "X" if num in ESTRATÉGIA.get(num, []) else ""
            st.write(f"{num}: {resultado}")
    
    st.subheader("Sequência Consolidada")
    st.code("".join([c for c in st.session_state.resultados if c in ('1', 'X')]))
    
    if st.button("Limpar Histórico"):
        st.session_state.historico = []
        st.session_state.resultados = ""
        st.experimental_rerun()
else:
    st.info("Registre um número ou carregue um histórico para começar")
