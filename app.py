import streamlit as st
import pandas as pd
from collections import deque

# 1. Configuração Inicial
if 'historico' not in st.session_state:
    st.session_state.historico = []
if 'resultados_cores' not in st.session_state:
    st.session_state.resultados_cores = deque(maxlen=50)  # Limite de 50 resultados

# 2. Mapeamento de cores (exemplo simplificado)
cores_roleta = {
    1: 'vermelho', 2: 'preto', 3: 'vermelho', 4: 'preto',
    # ... (complete com todos os números 0-36)
    36: 'vermelho'
}

# 3. Função de Atualização
def atualizar_cores():
    if len(st.session_state.historico) >= 2:
        ultimo = st.session_state.historico[-1]
        penultimo = st.session_state.historico[-2]
        
        if cores_roleta.get(ultimo) == cores_roleta.get(penultimo):
            st.session_state.resultados_cores.append('1')  # Mesma cor
        else:
            st.session_state.resultados_cores.append('X')  # Cor diferente

# 4. Interface
st.title("Estratégia de Cores")

# Entrada de dados
novo_numero = st.number_input("Número (0-36)", min_value=0, max_value=36)
if st.button("Adicionar"):
    st.session_state.historico.append(novo_numero)
    atualizar_cores()

# Exibição dos últimos 50 resultados
st.subheader("Últimos 50 Resultados")
st.markdown(''.join([
    '<span style="color:green">1</span>' if v == '1' else '<span style="color:red">X</span>' 
    for v in st.session_state.resultados_cores
]), unsafe_allow_html=True)

# Estatísticas
if st.session_state.resultados_cores:
    acertos = list(st.session_state.resultados_cores).count('1')
    st.write(f"Acertos: {acertos}/50 ({acertos/50:.0%})")
