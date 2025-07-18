import streamlit as st
import pandas as pd

# Inicialização do estado da sessão
def init_state():
    if 'historico' not in st.session_state:
        st.session_state.historico = []
    if 'previsoes' not in st.session_state:
        st.session_state.previsoes = {n: [] for n in range(37)}
    if 'sequencia_geral' not in st.session_state:
        st.session_state.sequencia_geral = ""

# Estratégia completa
ESTRATEGIA = {
    0: [26, 32],
    1: [20, 33],
    2: [2, 3, 5, 6, 7, 9, 12, 13, 14, 16, 17, 19, 20, 21, 24, 26, 27, 28, 29, 31, 32, 33, 35, 36],
    3: [2, 3, 4, 5, 8, 9, 10, 13, 14, 16, 17, 20, 21, 24, 26, 27, 29, 30, 31, 33, 34, 35],
    4: [19, 21],
    5: [10, 24],
    6: [27, 34],
    7: [29, 29],
    8: [2, 3, 4, 5, 8, 9, 10, 13, 14, 16, 17, 20, 21, 24, 26, 27, 29, 30, 31, 33, 34, 35],
    9: [22, 31],
    10: [5, 23],
    11: [30, 36],
    12: [28, 35],
    13: [27, 36],
    14: [2, 3, 5, 6, 7, 9, 12, 13, 14, 16, 17, 19, 20, 21, 24, 26, 27, 28, 29, 31, 32, 33, 35, 36],
    15: [19, 32],
    16: [24, 33],
    17: [25, 34],
    18: [22, 29],
    19: [1, 2, 3, 4, 8, 10, 13, 14, 15, 16, 17, 21, 22, 23, 24, 25, 26, 27, 28, 29, 32, 33, 35],
    20: [2, 3, 5, 6, 7, 9, 12, 13, 14, 16, 17, 19, 20, 21, 24, 26, 27, 28, 29, 31, 32, 33, 35, 36],
    21: [2, 4],
    22: [9, 18],
    23: [8, 10],
    24: [5, 16],
    25: [2, 17],
    26: [0, 3],
    27: [2, 3, 5, 6, 7, 9, 12, 13, 14, 16, 17, 19, 20, 21, 24, 26, 27, 28, 29, 31, 32, 33, 35, 36],
    28: [7, 12],
    29: [2, 3, 5, 6, 7, 9, 12, 13, 14, 16, 17, 19, 20, 21, 24, 26, 27, 28, 29, 31, 32, 33, 35, 36],
    30: [8, 11],
    31: [2, 3, 5, 6, 7, 9, 12, 13, 14, 16, 17, 19, 20, 21, 24, 26, 27, 28, 29, 31, 32, 33, 35, 36],
    32: [0, 15],
    33: [1, 16],
    34: [6, 17],
    35: [3, 12],
    36: [11, 13]
}

def registrar_numero(numero):
    if numero not in range(37):
        st.error("Número inválido! Deve ser entre 0 e 36")
        return
    
    # Se já houver números no histórico, verifica a previsão
    if st.session_state.historico:
        ultimo_numero = st.session_state.historico[-1]
        resultado = "1" if numero in ESTRATEGIA[ultimo_numero] else "X"
        
        # Atualiza as previsões para o último número
        if len(st.session_state.previsoes[ultimo_numero]) >= 1000:
            st.session_state.previsoes[ultimo_numero].pop(0)
        st.session_state.previsoes[ultimo_numero].append(resultado)
        
        # Atualiza a sequência geral
        st.session_state.sequencia_geral += resultado
    
    # Adiciona o novo número ao histórico
    st.session_state.historico.append(numero)
    if len(st.session_state.historico) > 1000:
        st.session_state.historico.pop(0)

def mostrar_resultados():
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
    
    st.subheader("Sequência Geral")
    st.code(st.session_state.sequencia_geral)

def main():
    init_state()
    st.title("Sistema de Previsão de Roleta")
    
    # Controles
    with st.form(key='registro_form'):
        col1, col2 = st.columns(2)
        with col1:
            numero = st.number_input("Número sorteado (0-36)", 
                                   min_value=0, 
                                   max_value=36,
                                   key="num_input")
        with col2:
            submitted = st.form_submit_button("Registrar")
            if submitted:
                registrar_numero(numero)
                st.experimental_rerun()
    
    # Upload de arquivo
    uploaded_file = st.file_uploader("Carregar histórico (CSV)", 
                                   type=["csv"],
                                   key="file_uploader")
    
    if uploaded_file is not None:
        try:
            dados = pd.read_csv(uploaded_file)
            if 'Número' in dados.columns:
                # Reinicia o estado antes de carregar
                init_state()
                for num in dados['Número']:
                    registrar_numero(num)
                st.success(f"Histórico carregado: {len(dados)} registros")
                st.experimental_rerun()
        except Exception as e:
            st.error(f"Erro ao ler arquivo: {e}")
    
    # Exibição dos resultados
    if len(st.session_state.historico) > 1:
        mostrar_resultados()
        
        if st.button("Limpar Histórico"):
            init_state()
            st.experimental_rerun()
    else:
        st.info("Registre pelo menos 2 números para ver as previsões")

if __name__ == "__main__":
    main()
