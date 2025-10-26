import streamlit as st
import pandas as pd
from collections import deque

# Configuração inicial
if 'historico' not in st.session_state:
    st.session_state.historico = []
if 'resultados' not in st.session_state:
    st.session_state.resultados = deque(maxlen=1000)

# Mapa de vizinhos da roleta europeia
vizinhos_map = {
    0: [32, 26], 1: [20, 33], 2: [21, 25], 3: [26, 35], 4: [19, 21],
    5: [24, 10], 6: [27, 34], 7: [28, 29], 8: [23, 30], 9: [31, 22],
    10: [5, 16], 11: [30, 36], 12: [35, 28], 13: [27, 36], 14: [20, 31],
    15: [32, 19], 16: [10, 24], 17: [25, 34], 18: [29, 22], 19: [15, 4],
    20: [1, 14], 21: [4, 2], 22: [18, 31], 23: [8, 33], 24: [5, 16],
    25: [17, 2], 26: [3, 0], 27: [6, 13], 28: [7, 12], 29: [18, 7],
    30: [8, 11], 31: [14, 9], 32: [15, 0], 33: [1, 23], 34: [6, 17],
    35: [3, 12], 36: [13, 11]
}

def obter_vizinhos_roleta(numeros):
    """Retorna os vizinhos baseados no layout físico da roleta europeia"""
    todos_vizinhos = set()
    for numero in numeros:
        if numero in vizinhos_map:
            vizinhos = vizinhos_map[numero]
            todos_vizinhos.update(vizinhos)
    return sorted(list(todos_vizinhos))

def obter_ultimas_ocorrencias(numero_alvo):
    """Obtém as últimas 3 ocorrências do número com seus vizinhos"""
    ocorrencias_com_vizinhos = []
    
    # Encontra todas as posições do número no histórico
    posicoes = [i for i, num in enumerate(st.session_state.historico) if num == numero_alvo]
    
    # Pega as últimas 3 ocorrências
    ultimas_posicoes = posicoes[-3:] if len(posicoes) >= 3 else posicoes
    
    for pos in ultimas_posicoes:
        ocorrencia = {
            'posicao': pos,
            'numero': st.session_state.historico[pos],
            'antes': st.session_state.historico[pos - 1] if pos > 0 else None,
            'depois': st.session_state.historico[pos + 1] if pos < len(st.session_state.historico) - 1 else None
        }
        ocorrencias_com_vizinhos.append(ocorrencia)
    
    return ocorrencias_com_vizinhos

def registrar_numero(numero):
    # Primeiro verifica o resultado da aposta anterior
    if len(st.session_state.historico) >= 1:
        ultimo_sorteado_anterior = st.session_state.historico[-1]
        ocorrencias_anterior = obter_ultimas_ocorrencias(ultimo_sorteado_anterior)
        
        # Coleta todos os números para apostar (antes, próprio, depois)
        numeros_aposta = set()
        for ocorrencia in ocorrencias_anterior:
            if ocorrencia['antes'] is not None:
                numeros_aposta.add(ocorrencia['antes'])
            numeros_aposta.add(ocorrencia['numero'])
            if ocorrencia['depois'] is not None:
                numeros_aposta.add(ocorrencia['depois'])
        
        # Calcula vizinhos
        vizinhos = obter_vizinhos_roleta(list(numeros_aposta))
        apostas_finais = sorted(list(set(numeros_aposta) | set(vizinhos)))
        
        # Verifica resultado
        if numero in apostas_finais:
            st.session_state.resultados.append("1")  # GREEN
        else:
            st.session_state.resultados.append("X")  # RED
    
    # Adiciona o novo número ao histórico
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

# Exibição simplificada
if st.session_state.historico:
    ultimo_numero = st.session_state.historico[-1]
    
    # Obtém as últimas ocorrências
    ocorrencias = obter_ultimas_ocorrencias(ultimo_numero)
    
    st.subheader(f"Último número sorteado: {ultimo_numero}")
    
    # Mostra as últimas ocorrências
    st.markdown("**Últimas vezes que saiu:**")
    for i, ocorrencia in enumerate(ocorrencias, 1):
        antes = f"{ocorrencia['antes']} → " if ocorrencia['antes'] is not None else ""
        depois = f" → {ocorrencia['depois']}" if ocorrencia['depois'] is not None else ""
        st.write(f"{i}. {antes}{ocorrencia['numero']}{depois}")
    
    # Coleta todos os números para apostar
    numeros_aposta = set()
    for ocorrencia in ocorrencias:
        if ocorrencia['antes'] is not None:
            numeros_aposta.add(ocorrencia['antes'])
        numeros_aposta.add(ocorrencia['numero'])
        if ocorrencia['depois'] is not None:
            numeros_aposta.add(ocorrencia['depois'])
    
    numeros_aposta = sorted(list(numeros_aposta))
    
    # Calcula vizinhos
    vizinhos = obter_vizinhos_roleta(numeros_aposta)
    
    # Apostas finais
    apostas_finais = sorted(list(set(numeros_aposta) | set(vizinhos)))
    
    st.markdown("**Apostar nos números:**")
    st.write(f"**V{numeros_aposta}**")
    
    st.markdown("**Vizinhos (1 de cada lado):**")
    st.write(f"**{vizinhos}**")
    
    # Histórico recente
    st.subheader("📈 Últimos números sorteados")
    st.write(" → ".join(map(str, st.session_state.historico[-10:])))
    
    # Resultados das Apostas
    st.subheader("📊 Resultados das Apostas")
    if st.session_state.resultados:
        resultados_display = " ".join(list(st.session_state.resultados)[-20:])
        st.write(resultados_display)
        st.write(f"Total de registros: {len(st.session_state.resultados)}")
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
            'Resultado_Aposta': [''] + resultados_export
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
