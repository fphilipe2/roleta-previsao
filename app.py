import streamlit as st
import pandas as pd
from collections import deque

# Configuração das cores da roleta (0 = verde, outros conforme padrão europeu)
cores_roleta = {
    0: 'G',  # Verde
    1: 'R', 2: 'B', 3: 'R', 4: 'B', 5: 'R', 6: 'B', 7: 'R', 8: 'B', 9: 'R', 10: 'B',
    11: 'B', 12: 'R', 13: 'B', 14: 'R', 15: 'B', 16: 'R', 17: 'B', 18: 'R', 19: 'R',
    20: 'B', 21: 'R', 22: 'B', 23: 'R', 24: 'B', 25: 'R', 26: 'B', 27: 'R', 28: 'B',
    29: 'B', 30: 'R', 31: 'B', 32: 'R', 33: 'B', 34: 'R', 35: 'B', 36: 'R'
}

# Inicialização do session_state
if 'historico' not in st.session_state:
    st.session_state.historico = []
if 'historico_cores' not in st.session_state:
    st.session_state.historico_cores = {n: deque(maxlen=20) for n in range(37)}  # 0-36

# Função para atualizar os históricos
def atualizar_historico():
    if st.session_state.historico:
        ultimo_numero = st.session_state.historico[-1]
        cor = cores_roleta[ultimo_numero]
        st.session_state.historico_cores[ultimo_numero].append(cor)

# Interface principal
st.title("Estratégia de Cores da Roleta")

# Upload de CSV
uploaded_file = st.file_uploader("Importar histórico (CSV)", type="csv")
if uploaded_file:
    dados = pd.read_csv(uploaded_file)
    if 'Número' in dados.columns:
        st.session_state.historico = dados['Número'].tolist()
        for num in st.session_state.historico:
            st.session_state.historico_cores[num].append(cores_roleta[num])

# Controles de números
novo = st.number_input("Novo número da roleta", min_value=0, max_value=36, step=1)
col1, col2 = st.columns([1, 5])
with col1:
    if st.button("Adicionar número"):
        st.session_state.historico.append(novo)
        atualizar_historico()

# Exibição dos resultados por número
st.subheader("Histórico de Cores por Número")

# Organiza em 3 colunas para melhor visualização
col1, col2, col3 = st.columns(3)
for i in range(0, 37):  # 0-36
    with col1 if i < 12 else (col2 if i < 24 else col3):
        cores = list(st.session_state.historico_cores[i])
        # Formata com cores: Vermelho (R), Preto (B), Verde (G)
        cores_formatadas = []
        for c in cores:
            if c == 'R':
                cores_formatadas.append('<span style="color:red">R</span>')
            elif c == 'B':
                cores_formatadas.append('<span style="color:black">B</span>')
            else:
                cores_formatadas.append('<span style="color:green">G</span>')
        st.markdown(f"{i}: {' '.join(cores_formatadas)}", unsafe_allow_html=True)

# Exportar histórico
if st.session_state.historico:
    csv_export = pd.DataFrame({
        'Número': st.session_state.historico,
        'Cor': [cores_roleta[num] for num in st.session_state.historico]
    }).to_csv(index=False).encode('utf-8')
    
    st.download_button(
        "📥 Exportar histórico CSV",
        data=csv_export,
        file_name='historico_cores_roleta.csv',
        mime='text/csv'
    )
