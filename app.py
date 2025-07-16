import streamlit as st
import pandas as pd
from collections import deque

# Configuração inicial
if 'historico' not in st.session_state:
    st.session_state.historico = []
if 'ultimo_clique' not in st.session_state:
    st.session_state.ultimo_clique = 0

# Estratégia completa (0-36)
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
17: [0, 3 , 8, 9, 10, 17, 22, 23, 25, 26, 31, 34],
18: [0, 5, 6, 10, 15, 18, 22, 24, 27, 29, 32, 34],
19: [1, 4, 7, 13, 15, 16, 19, 27, 28, 29, 33, 36],
20: [1, 2, 3, 8, 11, 12, 14, 20, 21, 25, 30, 35],
21: [1, 2, 4, 7, 11, 12, 13, 28, 20, 21, 33, 36],
22: [0, 5, 6, 9, 10, 15, 18, 22, 24, 27, 32, 34],
23: [0, 3, 8, 9, 10, 17, 22, 23, 25, 26, 31, 34],
24: [5, 6, 7, 15, 16, 18, 19, 24, 27, 29, 32, 34],
25: [2, 3, 8, 14, 17, 20, 23, 25, 26, 30, 31, 35],
26: [0, 3 , 8, 9, 10, 17, 22, 23, 25, 26, 31, 34],
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

OBSERVACOES = {
    0: "Foco em números baixos e médios",
    1: "Mistura de baixos e altos",
    2: "Inclui números 'vizinhos' no cilindro",
    3: "Aposta em laterais e finais",
    4: "Dispersão equilibrada",
    5: "Transição para números médios",
    6: "Foco em colunas do meio",
    7: "Números laterais e primes",
    8: "Combinação de altos e baixos",
    9: "Aposta em diagonais virtuais",
    10: "Foco em terços superiores",
    11: "Mistura de colunas e dezenas",
    12: "Números centrais e finais",
    13: "Dispersão ampla",
    14: "Inclui o zero para cobertura extra",
    15: "Reinicia ciclo com números baixos",
    # ... (complete com as observações para 16-36)
    36: "Combinação fechada com zero"
}

def registrar_numero(numero):
    st.session_state.historico.append(numero)

# Interface
st.title("Estratégia de Apostas na Roleta")

# Controles
col1, col2 = st.columns(2)
with col1:
    novo_numero = st.number_input("Último número sorteado (0-36)", min_value=0, max_value=36)
with col2:
    if st.button("Registrar"):
        registrar_numero(novo_numero)

# Upload de CSV
uploaded_file = st.file_uploader("Carregar histórico (CSV)", type="csv")
if uploaded_file:
    try:
        dados = pd.read_csv(uploaded_file)
        if 'Número' in dados.columns:
            st.session_state.historico = dados['Número'].tolist()
            st.success(f"Histórico carregado! {len(dados)} registros.")
        else:
            st.error("O arquivo precisa ter a coluna 'Número'")
    except Exception as e:
        st.error(f"Erro ao ler arquivo: {e}")

# Exibição da estratégia
if st.session_state.historico:
    ultimo_numero = st.session_state.historico[-1]
    numeros_aposta = ESTRATEGIA.get(ultimo_numero, [])
    observacao = OBSERVACOES.get(ultimo_numero, "")
    
    st.subheader(f"Último número sorteado: {ultimo_numero}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Números para apostar:**")
        st.write(numeros_aposta)
    with col2:
        st.markdown("**Observações:**")
        st.write(observacao)
    
    # Visualização dos números no layout da roleta
    st.subheader("Visualização na Roleta")
    roleta_layout = """
    <style>
    .number {
        display: inline-block;
        width: 40px;
        height: 40px;
        margin: 2px;
        text-align: center;
        line-height: 40px;
        border-radius: 50%;
        font-weight: bold;
    }
    .aposta {
        background-color: #4CAF50;
        color: white;
    }
    .normal {
        background-color: #f0f0f0;
    }
    </style>
    <div style='text-align: center;'>
    """
    
    for num in range(37):
        classe = "aposta" if num in numeros_aposta else "normal"
        roleta_layout += f"<div class='number {classe}'>{num}</div>"
    
    roleta_layout += "</div>"
    st.markdown(roleta_layout, unsafe_allow_html=True)
    
    # Histórico recente
    st.subheader("Últimos números sorteados")
    st.write(" → ".join(map(str, st.session_state.historico[-10:])))
else:
    st.warning("Registre um número ou carregue um histórico para ver as apostas")

# Exportar histórico
if st.button("📥 Exportar Histórico"):
    if st.session_state.historico:
        df = pd.DataFrame({'Número': st.session_state.historico})
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Baixar CSV",
            data=csv,
            file_name='historico_roleta.csv',
            mime='text/csv'
        )
    else:
        st.warning("Nenhum dado para exportar")
