import streamlit as st
from collections import deque

# Configuração real das cores da roleta europeia
CORES_ROULETTE = {
    0: 'G',  # Verde
    # Vermelhos
    1: 'R', 3: 'R', 5: 'R', 7: 'R', 9: 'R', 12: 'R', 
    14: 'R', 16: 'R', 18: 'R', 19: 'R', 21: 'R', 23: 'R',
    25: 'R', 27: 'R', 30: 'R', 32: 'R', 34: 'R', 36: 'R',
    # Pretos (todos os outros números de 1-36)
}

# Inicialização do session_state
if 'historico' not in st.session_state:
    st.session_state.historico = []
if 'historico_cores' not in st.session_state:
    st.session_state.historico_cores = {n: deque(maxlen=20) for n in range(37)}  # 0-36

def atualizar_historico():
    if st.session_state.historico:
        ultimo_numero = st.session_state.historico[-1]
        cor = CORES_ROULETTE.get(ultimo_numero, 'B')  # Padrão Preto se não estiver no dicionário
        st.session_state.historico_cores[ultimo_numero].append(cor)

# Interface
st.title("Histórico Realista de Cores da Roleta")

# Controles
novo_numero = st.number_input("Novo número (0-36)", min_value=0, max_value=36, step=1)
if st.button("Adicionar número"):
    if 0 <= novo_numero <= 36:
        st.session_state.historico.append(novo_numero)
        atualizar_historico()
    else:
        st.error("Número inválido! Deve ser entre 0 e 36")

# Exibição organizada
st.subheader("Últimos 20 resultados por número")

col1, col2, col3 = st.columns(3)
for numero in range(37):
    with col1 if numero < 12 else (col2 if numero < 24 else col3):
        cores = list(st.session_state.historico_cores[numero])
        
        # Formatação colorida
        display_text = []
        for cor in cores:
            if cor == 'R':
                display_text.append('<span style="color:red; font-weight:bold">R</span>')
            elif cor == 'B':
                display_text.append('<span style="color:black; font-weight:bold">B</span>')
            else:  # Verde
                display_text.append('<span style="color:green; font-weight:bold">G</span>')
        
        st.markdown(f"{numero}: {' '.join(display_text)}", unsafe_allow_html=True)

# Estatísticas (opcional)
if st.session_state.historico:
    total_vermelhos = sum(1 for num in st.session_state.historico if CORES_ROULETTE.get(num) == 'R')
    total_pretos = sum(1 for num in st.session_state.historico if CORES_ROULETTE.get(num, 'B') == 'B')
    total_verdes = sum(1 for num in st.session_state.historico if num == 0)
    
    st.write(f"Estatísticas: Vermelhos: {total_vermelhos} | Pretos: {total_pretos} | Verdes: {total_verdes}")
