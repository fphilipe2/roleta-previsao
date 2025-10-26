import streamlit as st
import pandas as pd
from collections import defaultdict, deque

# Configuração inicial
if 'historico' not in st.session_state:
    st.session_state.historico = []
if 'resultados' not in st.session_state:
    st.session_state.resultados = deque(maxlen=1000)

# Mapa de vizinhos da roleta europeia
vizinhos_map = {
    0: [32, 26],
    1: [20, 33],
    2: [21, 25],
    3: [26, 35],
    4: [19, 21],
    5: [24, 10],
    6: [27, 34],
    7: [28, 29],
    8: [23, 30],
    9: [31, 22],
    10: [5, 16],
    11: [30, 36],
    12: [35, 28],
    13: [27, 36],
    14: [20, 31],
    15: [32, 19],
    16: [10, 24],
    17: [25, 34],
    18: [29, 22],
    19: [15, 4],
    20: [1, 14],
    21: [4, 2],
    22: [18, 31],
    23: [8, 33],
    24: [5, 16],
    25: [17, 2],
    26: [3, 0],
    27: [6, 13],
    28: [7, 12],
    29: [18, 7],
    30: [8, 11],
    31: [14, 9],
    32: [15, 0],
    33: [1, 23],
    34: [6, 17],
    35: [3, 12],
    36: [13, 11]
}

def obter_vizinhos_roleta(numeros):
    """Retorna os vizinhos baseados no layout físico da roleta europeia"""
    todos_vizinhos = set()
    for numero in numeros:
        if numero in vizinhos_map:
            vizinhos = vizinhos_map[numero]
            todos_vizinhos.update(vizinhos)
    return sorted(list(todos_vizinhos))

def obter_palpite_por_ocorrencias(numero_alvo):
    """Obtém o palpite baseado nas últimas 3 ocorrências do número"""
    numeros_palpite = set()
    
    # Encontra todas as posições do número no histórico
    posicoes = [i for i, num in enumerate(st.session_state.historico) if num == numero_alvo]
    
    # Pega as últimas 3 ocorrências
    ultimas_posicoes = posicoes[-3:] if len(posicoes) >= 3 else posicoes
    
    for pos in ultimas_posicoes:
        # Número antes
        if pos > 0:
            antes = st.session_state.historico[pos - 1]
            numeros_palpite.add(antes)
        
        # Próprio número (o que saiu)
        numeros_palpite.add(st.session_state.historico[pos])
        
        # Número depois
        if pos < len(st.session_state.historico) - 1:
            depois = st.session_state.historico[pos + 1]
            numeros_palpite.add(depois)
    
    return sorted(list(numeros_palpite))

def calcular_apostas_finais(numeros_palpite):
    """Combina números do palpite com seus vizinhos"""
    vizinhos = obter_vizinhos_roleta(numeros_palpite)
    apostas_finais = set(numeros_palpite)
    apostas_finais.update(vizinhos)
    return sorted(list(apostas_finais))

def verificar_resultado_aposta(numero_sorteado, apostas_finais):
    """Verifica se o número sorteado está nas apostas finais"""
    if numero_sorteado in apostas_finais:
        return "1"  # GREEN
    else:
        return "X"  # RED

def registrar_numero(numero):
    # Primeiro verifica o resultado da aposta anterior
    if len(st.session_state.historico) >= 1:
        ultimo_sorteado_anterior = st.session_state.historico[-1]
        numeros_palpite_anterior = obter_palpite_por_ocorrencias(ultimo_sorteado_anterior)
        apostas_finais_anterior = calcular_apostas_finais(numeros_palpite_anterior)
        
        resultado = verificar_resultado_aposta(numero, apostas_finais_anterior)
        st.session_state.resultados.append(resultado)
    
    # Depois adiciona o novo número ao histórico
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

# Exibição das estratégias
if st.session_state.historico:
    ultimo_numero = st.session_state.historico[-1]
    
    # Obter palpite baseado nas ocorrências
    numeros_palpite = obter_palpite_por_ocorrencias(ultimo_numero)
    
    # Calcular apostas finais
    apostas_finais = calcular_apostas_finais(numeros_palpite)
    
    st.subheader(f"Último número sorteado: {ultimo_numero}")
    
    # Estratégia Principal
    st.markdown("**🎯 Estratégia Principal**")
    st.write(f"**Números para apostar:** V{numeros_palpite}")
    
    # Vizinhos
    vizinhos = obter_vizinhos_roleta(numeros_palpite)
    st.write(f"**Vizinhos dos palpites:** {vizinhos}")
    
    # Apostas finais
    st.write(f"**APOSTAS FINAIS (Palpite + Vizinhos):** {apostas_finais}")
    
    # Histórico recente
    st.subheader("📈 Últimos números sorteados")
    st.write(" → ".join(map(str, st.session_state.historico[-10:])))
    
    # Resultados das Apostas
    st.subheader("📊 Resultados das Apostas")
    if st.session_state.resultados:
        resultados_display = " ".join(list(st.session_state.resultados)[-20:])
        st.write(resultados_display)
        st.write(f"Total de registros: {len(st.session_state.resultados)}")
        
        total_green = list(st.session_state.resultados).count("1")
        total_red = list(st.session_state.resultados).count("X")
        if len(st.session_state.resultados) > 0:
            st.write(f"GREEN: {total_green} | RED: {total_red} | Taxa de acerto: {(total_green/len(st.session_state.resultados)*100):.1f}%")
    else:
        st.write("Aguardando próximos resultados...")

# Exportar histórico
if st.button("📥 Exportar Histórico"):
    if st.session_state.historico:
        resultados_export = list(st.session_state.resultados)
        if len(resultados_export) < len(st.session_state.historico) - 1:
            resultados_export = [''] * (len(st.session_state.historico) - 1 - len(resultados_export)) + resultados_export
        
        df = pd.DataFrame({
            'Número': st.session_state.historico,
            'Resultado_Aposta': [''] + resultados_export  # Primeiro número não tem resultado
        })
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Baixar CSV",
            data=csv,
            file_name='historico_roleta.csv',
            mime='text/csv'
        )
    else:
        st.warning("Nenhum dado para exportar")
