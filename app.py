import streamlit as st
import pandas as pd
from collections import defaultdict, deque

# Configuração inicial
if 'historico' not in st.session_state:
    st.session_state.historico = []
if 'ultimo_clique' not in st.session_state:
    st.session_state.ultimo_clique = 0

# Estratégia completa (0-36)
ESTRATEGIA = {
    0: [0, 5, 10, 23, 26, 32],
    1: [1, 2, 4, 20, 21, 33],
    2: [1, 2, 14, 20, 21, 25],
    3: [3, 8, 23, 26, 30, 35],
    4: [1, 4, 9, 16, 21, 33],
    5: [5, 6, 11, 17, 22, 34],
    6: [6, 9, 13, 18, 24, 29],
    7: [7, 12, 15, 19, 28, 31],
    8: [8, 11, 14, 22, 27, 36],
    9: [9, 10, 16, 23, 30, 34],
    10: [10, 13, 19, 25, 31, 35],
    11: [11, 12, 17, 24, 29, 36],
    12: [12, 15, 18, 26, 32, 35],
    13: [13, 14, 20, 27, 33, 36],
    14: [14, 16, 21, 28, 34, 0],
    15: [15, 17, 22, 29, 32, 1],
    16: [1, 3, 16, 19, 24, 30],
    17: [2, 5, 17, 20, 25, 31],
    18: [6, 9, 18, 21, 26, 32],
    19: [4, 7, 19, 22, 27, 33],
    20: [1, 8, 20, 23, 28, 34],
    21: [2, 9, 14, 21, 29, 35],
    22: [3, 10, 15, 22, 30, 36],
    23: [0, 5, 11, 16, 23, 31],
    24: [1, 6, 12, 17, 24, 32],
    25: [2, 7, 13, 18, 25, 33],
    26: [3, 8, 14, 19, 26, 34],
    27: [4, 9, 15, 20, 27, 35],
    28: [5, 10, 16, 21, 28, 36],
    29: [0, 6, 11, 17, 29, 33],
    30: [1, 7, 12, 18, 30, 34],
    31: [2, 8, 13, 19, 31, 35],
    32: [3, 9, 14, 20, 32, 36],
    33: [0, 4, 10, 15, 21, 33],
    34: [1, 5, 11, 16, 22, 34],
    35: [2, 6, 12, 17, 23, 35],
    36: [0, 2, 7, 13, 24, 36]
}

def registrar_numero(numero):
    st.session_state.historico.append(numero)

def obter_numeros_padrao(numero_alvo):
    """Obtém os 6 números (1 antes e 1 depois das últimas 3 ocorrências)"""
    numeros_padrao = []
    
    # Encontra todas as posições do número no histórico
    posicoes = [i for i, num in enumerate(st.session_state.historico) if num == numero_alvo]
    
    # Pega as últimas 3 ocorrências
    ultimas_posicoes = posicoes[-3:] if len(posicoes) >= 3 else posicoes
    
    for pos in ultimas_posicoes:
        # Número antes
        if pos > 0:
            antes = st.session_state.historico[pos - 1]
            if antes not in numeros_padrao:
                numeros_padrao.append(antes)
        
        # Número depois
        if pos < len(st.session_state.historico) - 1:
            depois = st.session_state.historico[pos + 1]
            if depois not in numeros_padrao:
                numeros_padrao.append(depois)
    
    return numeros_padrao[:6]  # Retorna no máximo 6 números

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

# Exibição das estratégias
if st.session_state.historico:
    ultimo_numero = st.session_state.historico[-1]
    
    # Estratégia principal
    numeros_aposta = ESTRATEGIA.get(ultimo_numero, [])
    
    # Nova estratégia - Padrão das últimas ocorrências
    numeros_padrao = obter_numeros_padrao(ultimo_numero)
    
    st.subheader(f"Último número sorteado: {ultimo_numero}")
    
    # Estratégia Principal
    st.markdown("**🎯 Estratégia Principal**")
    st.write(f"Números para apostar: {numeros_aposta}")
    
    # Nova Estratégia - Padrão
    st.markdown("**📊 Padrão das Últimas Ocorrências**")
    if numeros_padrao:
        st.write(f"Números (1 antes e 1 depois das últimas {min(3, st.session_state.historico.count(ultimo_numero))} saídas): {numeros_padrao}")
    else:
        st.write("Número ainda não tem ocorrências anteriores suficientes")
    
    # Histórico recente
    st.subheader("📈 Últimos números sorteados")
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
