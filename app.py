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
    16: "Padrão de números baixos",
    17: "Sequência linear ascendente",
    18: "Foco em números pares",
    19: "Combinação de ímpares",
    20: "Mistura de extremos",
    21: "Números centrais",
    22: "Padrão diagonal",
    23: "Inclui zero e números altos",
    24: "Sequência mista",
    25: "Foco em colunas",
    26: "Dispersão uniforme",
    27: "Números primos e compostos",
    28: "Padrão circular",
    29: "Combinação estratégica",
    30: "Transição suave",
    31: "Números laterais",
    32: "Foco em dúzias",
    33: "Mistura balanceada",
    34: "Sequência alternada",
    35: "Padrão de finalização",
    36: "Combinação fechada com zero"
}

def registrar_numero(numero):
    st.session_state.historico.append(numero)

def analisar_ultimas_ocorrencias(numero_alvo):
    """Analisa as últimas 3 ocorrências do número no histórico"""
    ocorrencias = []
    
    # Encontra todas as posições do número no histórico
    posicoes = [i for i, num in enumerate(st.session_state.historico) if num == numero_alvo]
    
    # Pega as últimas 3 ocorrências (se existirem)
    ultimas_posicoes = posicoes[-3:] if len(posicoes) >= 3 else posicoes
    
    for pos in ultimas_posicoes:
        antes = st.session_state.historico[pos - 1] if pos > 0 else "N/A"
        depois = st.session_state.historico[pos + 1] if pos < len(st.session_state.historico) - 1 else "N/A"
        
        ocorrencias.append({
            'posicao': pos + 1,  # Posição humana (começa em 1)
            'antes': antes,
            'depois': depois
        })
    
    return ocorrencias

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

# Exibição da estratégia principal
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
    
    # NOVA ESTRATÉGIA: Análise das últimas ocorrências
    st.subheader("📊 Análise das Últimas Ocorrências")
    
    ocorrencias = analisar_ultimas_ocorrencias(ultimo_numero)
    
    if ocorrencias:
        st.write(f"**Número analisado:** {ultimo_numero}")
        st.write(f"**Total de ocorrências no histórico:** {st.session_state.historico.count(ultimo_numero)}")
        
        for i, ocor in enumerate(ocorrencias, 1):
            st.write(f"**Ocorrência {i} (posição {ocor['posicao']}):**")
            col_ant, col_dep = st.columns(2)
            with col_ant:
                st.write(f"**Antes:** {ocor['antes']}")
            with col_dep:
                st.write(f"**Depois:** {ocor['depois']}")
    else:
        st.write(f"O número {ultimo_numero} ainda não apareceu no histórico")
    
    # Visualização dos números no layout da roleta
    st.subheader("🎯 Visualização na Roleta")
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
        border: 1px solid #ccc;
    }
    .aposta {
        background-color: #4CAF50;
        color: white;
    }
    .atual {
        background-color: #2196F3;
        color: white;
    }
    .normal {
        background-color: #f0f0f0;
    }
    </style>
    <div style='text-align: center;'>
    """
    
    for num in range(37):
        if num == ultimo_numero:
            classe = "atual"
        elif num in numeros_aposta:
            classe = "aposta"
        else:
            classe = "normal"
        roleta_layout += f"<div class='number {classe}'>{num}</div>"
    
    roleta_layout += "</div>"
    st.markdown(roleta_layout, unsafe_allow_html=True)
    
    # Legenda
    st.write("**Legenda:**")
    col_leg1, col_leg2, col_leg3 = st.columns(3)
    with col_leg1:
        st.write("🔵 Número atual")
    with col_leg2:
        st.write("🟢 Números para apostar")
    with col_leg3:
        st.write("⚪ Outros números")
    
    # Histórico recente
    st.subheader("📈 Últimos números sorteados")
    st.write(" → ".join(map(str, st.session_state.historico[-15:])))
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
