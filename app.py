import streamlit as st
import pandas as pd
import time
from collections import defaultdict, deque
from io import StringIO

# 1. CONFIGURAÇÃO INICIAL COMPLETA
if 'historico' not in st.session_state:
    st.session_state.historico = []
if 'proximas_cores' not in st.session_state:
    st.session_state.proximas_cores = defaultdict(lambda: deque(maxlen=100))
if 'estrategia_c2' not in st.session_state:
    st.session_state.estrategia_c2 = defaultdict(lambda: deque(maxlen=100))
if 'sequencia_c2' not in st.session_state:
    st.session_state.sequencia_c2 = deque(maxlen=1000)
if 'estrategia_especial2' not in st.session_state:
    st.session_state.estrategia_especial2 = defaultdict(lambda: deque(maxlen=100))
if 'sequencia_estrategia2' not in st.session_state:
    st.session_state.sequencia_estrategia2 = deque(maxlen=1000)
if 'estrategia_duzias' not in st.session_state:  # Nova estratégia
    st.session_state.estrategia_duzias = deque(maxlen=1000)
if 'ultimo_clique' not in st.session_state:
    st.session_state.ultimo_clique = 0

# 2. DEFINIÇÃO DOS GRUPOS DE NÚMEROS
GRUPO_C2 = {2, 8, 11, 17, 20, 26, 29, 35}
NUMEROS_ESPECIAIS_2 = {7, 12, 35}
NUMEROS_PROIBIDOS_2 = {8, 11, 13, 29, 35, 26}

# 3. DEFINIÇÃO DAS DÚZIAS
D1 = set(range(1, 13))  # Dúzia 1: 1-12
D2 = set(range(13, 25)) # Dúzia 2: 13-24
D3 = set(range(25, 37)) # Dúzia 3: 25-36

# 4. MAPEAMENTO DE CORES
CORES = {
    0: 'G',  # 0 = Verde
    1: 'R', 2: 'B', 3: 'R', 4: 'B', 5: 'R', 6: 'B', 7: 'R', 8: 'B',
    9: 'R', 10: 'B', 11: 'B', 12: 'R', 13: 'B', 14: 'R', 15: 'B',
    16: 'R', 17: 'B', 18: 'R', 19: 'R', 20: 'B', 21: 'R', 22: 'B',
    23: 'R', 24: 'B', 25: 'R', 26: 'B', 27: 'R', 28: 'B', 29: 'B',
    30: 'R', 31: 'B', 32: 'R', 33: 'B', 34: 'R', 35: 'B', 36: 'R'
}

def identificar_duzia(num):
    if num == 0:
        return None  # Zero não pertence a nenhuma dúzia
    if num in D1:
        return 'D1'
    if num in D2:
        return 'D2'
    if num in D3:
        return 'D3'
    return None

# 5. FUNÇÃO PRINCIPAL (atualizada)
def registrar_numero(numero, ignore_clique=False):
    if not ignore_clique:
        if time.time() - st.session_state.ultimo_clique < 0.5:
            st.warning("Aguarde 0.5 segundos entre os cliques!")
            return
        st.session_state.ultimo_clique = time.time()
    
    # Registrar o número no histórico
    st.session_state.historico.append(numero)
    
    if len(st.session_state.historico) > 1:
        numero_anterior = st.session_state.historico[-2]
        cor_atual = CORES.get(numero, 'G')
        st.session_state.proximas_cores[numero_anterior].append(cor_atual)
        
        # Estratégia C2
        if numero_anterior in GRUPO_C2:
            resultado = 'B' if numero in GRUPO_C2 else 'R'
            st.session_state.estrategia_c2[numero_anterior].append(resultado)
            st.session_state.sequencia_c2.append(resultado)
            
        # Estratégia 2
        if numero_anterior in NUMEROS_ESPECIAIS_2:
            resultado = 'R' if numero not in NUMEROS_PROIBIDOS_2 else 'B'
            st.session_state.estrategia_especial2[numero_anterior].append(resultado)
            st.session_state.sequencia_estrategia2.append(resultado)
        
        # NOVA ESTRATÉGIA DE DÚZIAS
        if len(st.session_state.historico) >= 2:
            # Pegar as últimas dúzias distintas
            ultimas_duzias = []
            for num in reversed(st.session_state.historico[:-1]):
                duzia = identificar_duzia(num)
                if duzia and duzia not in ultimas_duzias:
                    ultimas_duzias.append(duzia)
                    if len(ultimas_duzias) == 2:
                        break
            
            if len(ultimas_duzias) == 2:
                duzia_atual = identificar_duzia(numero)
                if duzia_atual is None:  # Se sair o zero
                    st.session_state.estrategia_duzias.append('G')
                elif duzia_atual in ultimas_duzias:
                    st.session_state.estrategia_duzias.append('1')
                else:
                    st.session_state.estrategia_duzias.append('X')

def formatar_resultado_duzias(c):
    if c == '1':
        return '<span style="color:green">1</span>'
    elif c == 'X':
        return '<span style="color:red">X</span>'
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

# Upload de CSV (com limpeza do histórico)
uploaded_file = st.file_uploader("Carregar histórico (CSV)", type="csv")
if uploaded_file:
    try:
        dados = pd.read_csv(uploaded_file)
        if 'Número' in dados.columns:
            # Limpar históricos antes de carregar novo arquivo
            st.session_state.historico = []
            st.session_state.estrategia_duzias = deque(maxlen=1000)
            # Limpar outros históricos conforme necessário
            
            for num in dados['Número'].tolist():
                registrar_numero(num, ignore_clique=True)
            st.success(f"Histórico carregado! {len(dados)} registros processados.")
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

# Estratégia de Dúzias
st.subheader("Estratégia de Dúzias Distintas")
st.write("1 = Acerto (número está nas 2 últimas dúzias distintas) | X = Erro | G = Zero")

if st.session_state.estrategia_duzias:
    sequencia_formatada = ''.join([formatar_resultado_duzias(c) for c in st.session_state.estrategia_duzias])
    st.markdown(f"Sequência completa: {sequencia_formatada}", unsafe_allow_html=True)
else:
    st.write("Aguardando dados suficientes (mínimo 2 números)")

# ... (mantenha as outras seções de exibição existentes)
