import streamlit as st
import pandas as pd

# Configuração inicial
if 'historico' not in st.session_state:
    st.session_state.historico = []
if 'resultados' not in st.session_state:
    st.session_state.resultados = ""

# [Seu dicionário ESTRATEGIA completo aqui...]

def registrar_numero(numero):
    st.session_state.historico.append(numero)
    # Atualiza a string de resultados
    if numero in ESTRATEGIA.get(numero, []):
        st.session_state.resultados += "1" if numero == 0 else "X"
    else:
        st.session_state.resultados += "-"  # Para números não apostados

# Interface
st.title("Sequência de Apostas na Roleta")

# Controles
col1, col2 = st.columns(2)
with col1:
    novo_numero = st.number_input("Último número sorteado (0-36)", min_value=0, max_value=36)
with col2:
    if st.button("Registrar"):
        registrar_numero(novo_numero)

# Upload de CSV
uploaded_file = st.file_uploader("Carregar histórico (CSV)", type="csv")
if uploaded_file is not None:
    try:
        dados = pd.read_csv(uploaded_file)
        if 'Número' in dados.columns:
            st.session_state.historico = dados['Número'].tolist()
            st.session_state.resultados = ""
            for num in st.session_state.historico:
                if num in ESTRATEGIA.get(num, []):
                    st.session_state.resultados += "1" if num == 0 else "X"
                else:
                    st.session_state.resultados += "-"
            st.success("Histórico carregado!")
    except Exception as e:
        st.error(f"Erro ao ler arquivo: {e}")

# Exibição dos resultados
if st.session_state.historico:
    st.subheader("Resultado por Número")
    for i, num in enumerate(st.session_state.historico):
        resultado = ""
        if num in ESTRATEGIA.get(num, []):
            resultado = "1" if num == 0 else "X"
        st.write(f"{num}: {resultado}")
    
    st.subheader("Sequência Consolidada")
    st.code(st.session_state.resultados.replace("-", ""))  # Remove os não apostados
    
    # Botão para limpar resultados
    if st.button("Limpar Histórico"):
        st.session_state.historico = []
        st.session_state.resultados = ""
        st.experimental_rerun()
else:
    st.warning("Registre um número ou carregue um histórico para começar")
