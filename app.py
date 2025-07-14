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

# Mapeamento de cores (Roleta Europeia)
CORES = {
    0: 'G',  # Verde
    1: 'R', 2: 'B', 3: 'R', 4: 'B', 5: 'R', 6: 'B', 7: 'R', 8: 'B',
    9: 'R', 10: 'B', 11: 'B', 12: 'R', 13: 'B', 14: 'R', 15: 'B',
    16: 'R', 17: 'B', 18: 'R', 19: 'R', 20: 'B', 21: 'R', 22: 'B',
    23: 'R', 24: 'B', 25: 'R', 26: 'B', 27: 'R', 28: 'B', 29: 'B',
    30: 'R', 31: 'B', 32: 'R', 33: 'B', 34: 'R', 35: 'B', 36: 'R'
}

def registrar_numero(numero, ignore_clique=False):
    """
    ignore_clique: True para carregamento CSV (ignora proteção contra duplo clique)
    """
    if not ignore_clique:
        # Proteção contra duplo clique apenas para cliques manuais
        if time.time() - st.session_state.ultimo_clique < 0.5:
            st.warning("Aguarde 0.5 segundos entre os cliques!")
            return
        st.session_state.ultimo_clique = time.time()
    
    # Restante da função (mantenha igual)
    if len(st.session_state.historico) > 0:
        numero_anterior = st.session_state.historico[-1]
        cor_atual = CORES.get(numero, 'G')
        st.session_state.proximas_cores[numero_anterior].append(cor_atual)
        
        if numero_anterior in NUMEROS_ESPECIAIS_1:
            resultado = 'R' if numero not in NUMEROS_ESPECIAIS_1 else 'B'
            st.session_state.estrategia_especial1[numero_anterior].append(resultado)
            st.session_state.sequencia_estrategia1.append(resultado)
            
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

# Na interface, modifique a seção dos controles para:
col1, col2 = st.columns(2)
with col1:
    novo_numero = st.number_input("Número sorteado (0-36)", min_value=0, max_value=36)

with col2:
    if st.button("Registrar", key="botao_registrar_unico"):
        registrar_numero(novo_numero)  # Esta linha deve estar indentada com 4 espaços

# Controles
col1, col2 = st.columns(2)

with col1:
    novo_numero = st.number_input("Número sorteado (0-36)", min_value=0, max_value=36)

with col2:
    if st.button("Registrar", key="botao_registrar_unico"):
        registrar_numero(novo_numero)  # 4 espaços de indentação aqui

# Upload de CSV
uploaded_file = st.file_uploader("Carregar histórico (CSV)", type="csv")
if uploaded_file:
    try:
        dados = pd.read_csv(uploaded_file)
        if 'Número' in dados.columns:
            # Usamos ignore_clique=True para o carregamento CSV
            for num in dados['Número'].tolist():
                registrar_numero(num, ignore_clique=True)
            st.success("Histórico carregado com sucesso!")
        else:
            st.error("O arquivo CSV precisa ter uma coluna chamada 'Número'")
    except Exception as e:
        st.error(f"Erro ao ler arquivo: {e}")

# Exportar CSV
if st.button("📥 Exportar Histórico CSV"):
    if len(st.session_state.historico) > 0:
        # Cria DataFrame com duas colunas: Número e Cor
        df_export = pd.DataFrame({
            'Número': st.session_state.historico,
            'Cor': [CORES.get(num, 'G') for num in st.session_state.historico]
        })
        
        # Converte para CSV
        csv = df_export.to_csv(index=False).encode('utf-8')
        
        with col2:
    if st.button("Registrar", key="botao_registrar_unico"):
        registrar_numero(novo_numero)  # Aqui não usamos ignore_clique (proteção ativa)
        
    else:
        st.warning("Nenhum dado para exportar!")

# Exibição dos resultados
st.subheader("Últimas 100 cores após cada número")
cols = st.columns(4)
for numero in range(37):  # 0-36
    with cols[numero % 4]:
        historico_formatado = ''.join([formatar_cor(c) for c in st.session_state.proximas_cores[numero]])
        st.markdown(f"{numero}: {historico_formatado}", unsafe_allow_html=True)

# Visualização da sequência
st.subheader(f"Últimos {min(50, len(st.session_state.historico))} números sorteados")
st.write(" → ".join(str(n) for n in st.session_state.historico[-50:]))
