import streamlit as st
import pandas as pd

# Configuração inicial
if 'historico' not in st.session_state:
    st.session_state.historico = []
if 'previsoes' not in st.session_state:
    st.session_state.previsoes = {n: [] for n in range(37)}

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
    # Verifica a previsão para o número anterior
    if len(st.session_state.historico) > 0:
        num_anterior = st.session_state.historico[-1]
        resultado = "1" if numero in ESTRATEGIA.get(num_anterior, []) else "X"
        
        # Armazena apenas os últimos 1000 resultados por número
        if len(st.session_state.previsoes[num_anterior]) >= 1000:
            st.session_state.previsoes[num_anterior].pop(0)
        st.session_state.previsoes[num_anterior].append(resultado)
    
    # Armazena o novo número (máximo 1000 no histórico para demonstração)
    if len(st.session_state.historico) >= 1000:
        st.session_state.historico.pop(0)
    st.session_state.historico.append(numero)

# Interface
st.title("Previsões de Roleta Corrigidas")

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
            for num in dados['Número']:
                registrar_numero(num)
            st.success(f"Histórico carregado! {len(dados)} registros.")
    except Exception as e:
        st.error(f"Erro ao ler arquivo: {e}")
# Exibição dos resultados
if len(st.session_state.historico) > 1:
    st.subheader("Resultados por Número")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("### 0-11")
        for n in range(0, 12):
            st.write(f"{n}: {' '.join(st.session_state.previsoes[n])}")
    
    with col2:
        st.write("### 12-24")
        for n in range(12, 25):
            st.write(f"{n}: {' '.join(st.session_state.previsoes[n])}")
    
    with col3:
        st.write("### 25-36")
        for n in range(25, 37):
            st.write(f"{n}: {' '.join(st.session_state.previsoes[n])}")
    
    # Exemplo com a sequência [1, 2, 3, 4, 2, 1]
    st.subheader("Exemplo Correto")
    st.write("Para a sequência [1, 2, 3, 4, 2, 1]:")
    st.write("1: 1 (porque 2 está na lista do 1)")
    st.write("2: 1 (porque 3 está na lista do 2)")
    st.write("3: X (porque 4 NÃO está na lista do 3)")
    st.write("4: X (porque 2 NÃO está na lista do 4)")
    st.write("2: 1 (porque 1 está na lista do 2)")
    
    if st.button("Limpar Histórico"):
        st.session_state.historico = []
        st.session_state.previsoes = {n: [] for n in range(37)}
        st.experimental_rerun()
else:
    st.info("Registre pelo menos 2 números para ver as previsões")
