import streamlit as st
import pandas as pd

# Configuração inicial
if 'historico' not in st.session_state:
    st.session_state.historico = []
if 'previsoes' not in st.session_state:
    st.session_state.previsoes = {n: [] for n in range(37)}
if 'sequencia_geral' not in st.session_state:
    st.session_state.sequencia_geral = ""


# Estratégia completa - ATENÇÃO: usar sempre ESTRATEGIA (sem acento)
ESTRATEGIA = {
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
    if numero not in range(37):
        st.error("Número inválido! Deve ser entre 0 e 36")
        return
    
    if len(st.session_state.historico) > 0:
        num_anterior = st.session_state.historico[-1]
        resultado = "1" if numero in ESTRATEGIA.get(num_anterior, []) else "X"
        
        if len(st.session_state.previsoes[num_anterior]) >= 20:
            st.session_state.previsoes[num_anterior].pop(0)
        st.session_state.previsoes[num_anterior].append(resultado)
        st.session_state.sequencia_geral += resultado
    
    st.session_state.historico.append(numero)
    if len(st.session_state.historico) > 1000:
        st.session_state.historico.pop(0)

# Interface principal
def main():
    st.title("Sistema de Previsão de Roleta")

    # Controles - usando keys únicas
    col1, col2 = st.columns(2)
    with col1:
        novo_numero = st.number_input("Último número (0-36)", 
                                    min_value=0, 
                                    max_value=36,
                                    key="num_input")
    with col2:
        if st.button("Registrar", key="registrar_btn"):
            registrar_numero(novo_numero)

    # Upload de CSV - com key única
    uploaded_file = st.file_uploader("Carregar histórico (CSV)", 
                                   type="csv",
                                   key="csv_uploader")
    
    if uploaded_file is not None:
        try:
            dados = pd.read_csv(uploaded_file)
            if 'Número' in dados.columns:
                st.session_state.historico = []
                st.session_state.previsoes = {n: [] for n in range(37)}
                st.session_state.sequencia_geral = ""
                
                for num in dados['Número']:
                    registrar_numero(num)
                st.success(f"Histórico carregado! {len(dados)} registros.")
        except Exception as e:
            st.error(f"Erro ao ler arquivo: {e}")
