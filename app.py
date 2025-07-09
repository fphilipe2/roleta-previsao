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
if 'estrategia_especial1' not in st.session_state:  # Estratégia 1 (2,8,11...)
    st.session_state.estrategia_especial1 = defaultdict(lambda: deque(maxlen=100))
if 'sequencia_estrategia1' not in st.session_state:
    st.session_state.sequencia_estrategia1 = deque(maxlen=1000)
if 'estrategia_especial2' not in st.session_state:  # Estratégia 2 (7,12,35)
    st.session_state.estrategia_especial2 = defaultdict(lambda: deque(maxlen=100))
if 'sequencia_estrategia2' not in st.session_state:
    st.session_state.sequencia_estrategia2 = deque(maxlen=1000)
if 'ultimo_clique' not in st.session_state:    # Esta linha deve estar no mesmo nível das outras if
    st.session_state.ultimo_clique = 0         # Esta linha deve estar indentada com 4 espaços

# Números especiais para as estratégias
NUMEROS_ESPECIAIS_1 = {2, 8, 11, 17, 20, 26, 29, 35}
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

def registrar_numero(numero):
    # Proteção contra duplo clique (verifica se passou pelo menos 0.5 segundos)
    if time.time() - st.session_state.ultimo_clique < 0.5:
        st.warning("Aguarde 0.5 segundos entre os cliques!")
        return
    
    # Atualiza o tempo do último clique válido
    st.session_state.ultimo_clique = time.time()
    
    # Restante da função original (não mexa nessa parte)
    if len(st.session_state.historico) > 0:
        numero_anterior = st.session_state.historico[-1]
        cor_atual = CORES.get(numero, 'G')
        st.session_state.proximas_cores[numero_anterior].append(cor_atual)
        
        # Estratégia Especial 1
        if numero_anterior in NUMEROS_ESPECIAIS_1:
            resultado = 'R' if numero not in NUMEROS_ESPECIAIS_1 else 'B'
            st.session_state.estrategia_especial1[numero_anterior].append(resultado)
            st.session_state.sequencia_estrategia1.append(resultado)
            
        # Estratégia Especial 2
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
        registrar_numero(novo_numero)  # 4 espaços de indentação aqui)

# Upload de CSV
uploaded_file = st.file_uploader("Carregar histórico (CSV)", type="csv")
if uploaded_file:
    try:
        dados = pd.read_csv(uploaded_file)
        if 'Número' in dados.columns:
            for num in dados['Número'].tolist():
                registrar_numero(num)
            st.success("Histórico carregado com sucesso!")
        else:
            st.error("O arquivo CSV precisa ter uma coluna chamada 'Número'")
    except Exception as e:
        st.error(f"Erro ao ler arquivo: {e}")

# Exportar CSV
if st.button("📥 Exportar Histórico CSV"):
    if len(st.session_state.historico) > 0:
        df_export = pd.DataFrame({
            'Número': st.session_state.historico,
            'Cor': [CORES.get(num, 'G') for num in st.session_state.historico]
        })
        csv = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Baixar CSV",
            data=csv,
            file_name='historico_roleta.csv',
            mime='text/csv'
        )
    else:
        st.warning("Nenhum dado para exportar!")

# Estratégia Padrão (Cores)
st.subheader("Estratégia Padrão - Cores após cada número")
cols = st.columns(4)
for numero in range(37):
    with cols[numero % 4]:
        historico_formatado = ''.join([formatar_cor(c) for c in st.session_state.proximas_cores[numero]])
        st.markdown(f"{numero}: {historico_formatado}", unsafe_allow_html=True)

# Estratégia Especial 1
st.subheader("Estratégia 1 - Números Especiais (2,8,11,17,20,26,29,35)")
st.write("R = Próximo número NÃO é especial | B = Próximo número É especial")

cols_especiais1 = st.columns(len(NUMEROS_ESPECIAIS_1))
for i, num in enumerate(sorted(NUMEROS_ESPECIAIS_1)):
    with cols_especiais1[i]:
        historico_formatado = ''.join([formatar_cor(c) for c in st.session_state.estrategia_especial1[num]])
        st.markdown(f"{num}: {historico_formatado}", unsafe_allow_html=True)

st.markdown(f"**Sequência:** {''.join([formatar_cor(c) for c in st.session_state.sequencia_estrategia1])}", unsafe_allow_html=True)

# Estratégia Especial 2 (Nova)
st.subheader("Estratégia 2 - Números (7,12,35) seguidos de (8,11,13,29,35,26)")
st.write("R = Próximo número NÃO está na lista proibida | B = Próximo número está na lista proibida")

cols_especiais2 = st.columns(len(NUMEROS_ESPECIAIS_2))
for i, num in enumerate(sorted(NUMEROS_ESPECIAIS_2)):
    with cols_especiais2[i]:
        historico_formatado = ''.join([formatar_cor(c) for c in st.session_state.estrategia_especial2[num]])
        st.markdown(f"{num}: {historico_formatado}", unsafe_allow_html=True)

st.markdown(f"**Sequência:** {''.join([formatar_cor(c) for c in st.session_state.sequencia_estrategia2])}", unsafe_allow_html=True)

# Histórico de números
st.subheader(f"Últimos {min(50, len(st.session_state.historico))} números sorteados")
st.write(" → ".join(str(n) for n in st.session_state.historico[-50:]))
