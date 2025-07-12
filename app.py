import streamlit as st
import pandas as pd
import time
from collections import defaultdict, deque
from io import StringIO

# Configuração inicial
if 'historico' not in st.session_state:
    st.session_state.historico = []
if 'proximas_cores' not in st.session_state:
    st.session_state.proximas_cores = defaultdict(lambda: deque(maxlen=100))
if 'estrategia_c2' not in st.session_state:  # Estratégia C2 modificada
    st.session_state.estrategia_c2 = defaultdict(lambda: deque(maxlen=100))
if 'sequencia_c2' not in st.session_state:
    st.session_state.sequencia_c2 = deque(maxlen=1000)
if 'estrategia_especial2' not in st.session_state:  # Estratégia 2 (7,12,35)
    st.session_state.estrategia_especial2 = defaultdict(lambda: deque(maxlen=100))
if 'sequencia_estrategia2' not in st.session_state:
    st.session_state.sequencia_estrategia2 = deque(maxlen=1000)
if 'ultimo_clique' not in st.session_state:
    st.session_state.ultimo_clique = 0

# Números para as estratégias
GRUPO_C2 = {2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35}  # Estratégia C2
NUMEROS_ESPECIAIS_2 = {7, 12, 35}
NUMEROS_PROIBIDOS_2 = {8, 11, 13, 29, 35, 26}

# Mapeamento de cores
CORES = {
    0: 'G', 1: 'R', 2: 'B', 3: 'R', 4: 'B', 5: 'R', 6: 'B', 7: 'R', 8: 'B',
    9: 'R', 10: 'B', 11: 'B', 12: 'R', 13: 'B', 14: 'R', 15: 'B',
    16: 'R', 17: 'B', 18: 'R', 19: 'R', 20: 'B', 21: 'R', 22: 'B',
    23: 'R', 24: 'B', 25: 'R', 26: 'B', 27: 'R', 28: 'B', 29: 'B',
    30: 'R', 31: 'B', 32: 'R', 33: 'B', 34: 'R', 35: 'B', 36: 'R'
}

def registrar_numero(numero, ignore_clique=False):
    if not ignore_clique:
        if time.time() - st.session_state.ultimo_clique < 0.5:
            st.warning("Aguarde 0.5 segundos entre os cliques!")
            return
        st.session_state.ultimo_clique = time.time()
    
    if len(st.session_state.historico) > 0:
        numero_anterior = st.session_state.historico[-1]
        cor_atual = CORES.get(numero, 'G')
        st.session_state.proximas_cores[numero_anterior].append(cor_atual)
        
        # Estratégia C2 Modificada (verifica se o próximo está no grupo C2)
        if numero_anterior in GRUPO_C2:
            resultado = 'B' if numero in GRUPO_C2 else 'R'
            st.session_state.estrategia_c2[numero_anterior].append(resultado)
            st.session_state.sequencia_c2.append(resultado)
            
        # Estratégia 2 (mantida original)
        if numero_anterior in NUMEROS_ESPECIAIS_2:
            resultado = 'R' if numero not in NUMEROS_PROIBIDOS_2 else 'B'
            st.session_state.estrategia_especial2[numero_anterior].append(resultado)
            st.session_state.sequencia_estrategia2.append(resultado)
    
    st.session_state.historico.append(numero)

def formatar_cor(c):
    if c == 'R':
        return '<span style="color:red">R</span>'
    elif c == 'B':
        return '<span style="color:black">B</span>'
    else:  # G
        return '<span style="color:green">G</span>'

# Interface
st.title("Rastreamento de Estratégias de Roleta")

# Controles
col1, col2 = st.columns(2)
with col1:
    novo_numero = st.number_input("Número sorteado (0-36)", min_value=0, max_value=36)
with col2:
    if st.button("Registrar", key="botao_registrar_unico"):
        registrar_numero(novo_numero)

# Upload de CSV (com limpeza do histórico antes de carregar)
uploaded_file = st.file_uploader("Carregar histórico (CSV)", type="csv")
if uploaded_file:
    try:
        dados = pd.read_csv(uploaded_file)
        if 'Número' in dados.columns:
            # Limpa os históricos antes de carregar
            st.session_state.historico = []
            st.session_state.estrategia_c2 = defaultdict(lambda: deque(maxlen=100))
            st.session_state.sequencia_c2 = deque(maxlen=1000)
            st.session_state.estrategia_especial2 = defaultdict(lambda: deque(maxlen=100))
            st.session_state.sequencia_estrategia2 = deque(maxlen=1000)
            
            for num in dados['Número'].tolist():
                registrar_numero(num, ignore_clique=True)
            st.success(f"Histórico carregado! {len(dados)} registros processados.")
        else:
            st.error("O CSV deve ter uma coluna 'Número'")
    except Exception as e:
        st.error(f"Erro: {str(e)}")

# Exportar CSV (mantido igual)
if st.button("📥 Exportar Histórico CSV"):
    if st.session_state.historico:
        df = pd.DataFrame({
            'Número': st.session_state.historico,
            'Cor': [CORES.get(n, 'G') for n in st.session_state.historico]
        })
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Baixar CSV",
            data=csv,
            file_name='roleta_historico.csv',
            mime='text/csv'
        )
    else:
        st.warning("Nenhum dado para exportar")

# Estratégia C2 Modificada
st.subheader("Estratégia C2 - Números Especiais (2,8,11,17,20,26,29,35)")
st.write("B = Próximo número É do grupo C2 | R = Próximo número NÃO é do grupo C2")

cols = st.columns(4)
for i, num in enumerate(sorted(GRUPO_C2)):
    with cols[i % 4]:
        historico = ''.join([formatar_cor(c) for c in st.session_state.estrategia_c2[num]])
        st.markdown(f"{num}: {historico}", unsafe_allow_html=True)
    if i == 3:  # Quebra de linha após 4 números
        cols = st.columns(4)

st.markdown(f"**Sequência:** {''.join([formatar_cor(c) for c in st.session_state.sequencia_c2])}", 
            unsafe_allow_html=True)

# Estratégia 2 (mantida original)
st.subheader("Estratégia 2 - Números (7,12,35) seguidos de (8,11,13,29,35,26)")
st.write("R = Próximo número NÃO está na lista proibida | B = Próximo número está na lista proibida")

cols = st.columns(len(NUMEROS_ESPECIAIS_2))
for i, num in enumerate(sorted(NUMEROS_ESPECIAIS_2)):
    with cols[i]:
        historico = ''.join([formatar_cor(c) for c in st.session_state.estrategia_especial2[num]])
        st.markdown(f"{num}: {historico}", unsafe_allow_html=True)

st.markdown(f"**Sequência:** {''.join([formatar_cor(c) for c in st.session_state.sequencia_estrategia2])}",
            unsafe_allow_html=True)

# Histórico de números
st.subheader(f"Últimos {min(50, len(st.session_state.historico))} números")
st.write(" → ".join(map(str, st.session_state.historico[-50:])))
