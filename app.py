import streamlit as st
import pandas as pd
from collections import defaultdict, deque
from io import StringIO

# Configuração inicial
if 'historico' not in st.session_state:
    st.session_state.historico = []
if 'proximas_cores' not in st.session_state:
    st.session_state.proximas_cores = defaultdict(lambda: deque(maxlen=100))
if 'estrategia_especial' not in st.session_state:
    st.session_state.estrategia_especial = defaultdict(lambda: deque(maxlen=100))

# Números especiais para a nova estratégia
NUMEROS_ESPECIAIS = {2, 8, 11, 17, 20, 26, 29, 35}

# Mapeamento de cores (Roleta Europeia)
CORES = {
    0: 'G',  # Verde
    1: 'R', 2: 'B', 3: 'R', 4: 'B', 5: 'R', 6: 'B', 7: 'R', 8: 'B',
    9: 'R', 10: 'B', 11: 'B', 12: 'R', 13: 'B', 14: 'R', 15: 'B',
    16: 'R', 17: 'B', 18: 'R', 19: 'R', 20: 'B', 21: 'R', 22: 'B',
    23: 'R', 24: 'B', 25: 'R', 26: 'B', 27: 'R', 28: 'B', 29: 'B',
    30: 'R', 31: 'B', 32: 'R', 33: 'B', 34: 'R', 35: 'B', 36: 'R'
}

def registrar_numero(numero):
    # Registra para a estratégia de cores padrão
    if len(st.session_state.historico) > 0:
        numero_anterior = st.session_state.historico[-1]
        cor_atual = CORES.get(numero, 'G')
        st.session_state.proximas_cores[numero_anterior].append(cor_atual)
        
        # Registra para a nova estratégia especial
        if numero_anterior in NUMEROS_ESPECIAIS:
            resultado = 'R' if numero not in NUMEROS_ESPECIAIS else 'B'
            st.session_state.estrategia_especial[numero_anterior].append(resultado)
    
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
    if st.button("Registrar"):
        registrar_numero(novo_numero)

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

# Exibição da estratégia de cores padrão
st.subheader("Estratégia Padrão - Cores após cada número")
cols = st.columns(4)
for numero in range(37):
    with cols[numero % 4]:
        historico_formatado = ''.join([formatar_cor(c) for c in st.session_state.proximas_cores[numero]])
        st.markdown(f"{numero}: {historico_formatado}", unsafe_allow_html=True)

# Exibição da nova estratégia especial
st.subheader("Nova Estratégia - Números Especiais (2,8,11,17,20,26,29,35)")
st.write("R = Próximo número NÃO é especial | B = Próximo número É especial")

especiais_ordenados = sorted(NUMEROS_ESPECIAIS)
cols_especiais = st.columns(len(especiais_ordenados))
for i, num in enumerate(especiais_ordenados):
    with cols_especiais[i]:
        historico_formatado = ''.join([formatar_cor(c) for c in st.session_state.estrategia_especial[num]])
        st.markdown(f"{num}: {historico_formatado}", unsafe_allow_html=True)

# Visualização da sequência
st.subheader(f"Últimos {min(50, len(st.session_state.historico))} números sorteados")
st.write(" → ".join(str(n) for n in st.session_state.historico[-50:]))
