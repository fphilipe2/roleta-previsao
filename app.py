import streamlit as st
from collections import defaultdict, deque

# Configuração das cores da roleta (0 = verde)
CORES = {
    0: 'G',
    1: 'R', 3: 'R', 5: 'R', 7: 'R', 9: 'R', 12: 'R', 
    14: 'R', 16: 'R', 18: 'R', 19: 'R', 21: 'R', 23: 'R',
    25: 'R', 27: 'R', 30: 'R', 32: 'R', 34: 'R', 36: 'R'
    # Todos os outros são pretos (B)
}

# Inicialização
if 'historico' not in st.session_state:
    st.session_state.historico = []
if 'resultados' not in st.session_state:
    st.session_state.resultados = defaultdict(lambda: deque(maxlen=20))  # Número: [cores após ele]

def atualizar_resultados():
    if len(st.session_state.historico) > 1:
        ultimo_num = st.session_state.historico[-1]
        cor = CORES.get(ultimo_num, 'B')
        
        # Adiciona a cor ao número anterior
        num_anterior = st.session_state.historico[-2]
        st.session_state.resultados[num_anterior].append(cor)

# Interface
st.title("Estratégia de Cores Pós-Número")

# Controle
num = st.number_input("Novo número (0-36)", min_value=0, max_value=36)
if st.button("Adicionar"):
    st.session_state.historico.append(num)
    atualizar_resultados()

# Exibição
st.subheader("Cor do resultado APÓS cada número")

cols = st.columns(3)
for i in range(37):
    with cols[0] if i < 12 else (cols[1] if i < 24 else cols[2]):
        cores = st.session_state.resultados[i]
        display = []
        for c in cores:
            color = "red" if c == 'R' else ("green" if c == 'G' else "black")
            display.append(f'<span style="color:{color}; font-weight:bold">{c}</span>')
        st.markdown(f"{i}: {' '.join(display)}", unsafe_allow_html=True)
