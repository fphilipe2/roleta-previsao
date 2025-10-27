import streamlit as st
import pandas as pd
from collections import deque

# Configuração inicial simplificada
if 'historico' not in st.session_state:
    st.session_state.historico = []
if 'resultados' not in st.session_state:
    st.session_state.resultados = []
if 'banca' not in st.session_state:
    st.session_state.banca = 1000
if 'aposta_atual' not in st.session_state:
    st.session_state.aposta_atual = None
if 'ciclo_atual' not in st.session_state:
    st.session_state.ciclo_atual = 1

# Mapa de vizinhos simplificado
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

def obter_ultimas_ocorrencias_anteriores(numero_alvo):
    """Obtém as últimas 3 ocorrências ANTERIORES do número"""
    ocorrencias_com_vizinhos = []
    
    # Encontra todas as posições do número no histórico
    posicoes = [i for i, num in enumerate(st.session_state.historico) if num == numero_alvo]
    
    # Remove a última ocorrência (a que acabou de sair)
    if posicoes:
        posicoes = posicoes[:-1]
    
    # Pega as últimas 3 ocorrências anteriores
    ultimas_posicoes = posicoes[-3:] if len(posicoes) >= 3 else posicoes
    
    for pos in ultimas_posicoes:
        ocorrencia = {
            'numero': st.session_state.historico[pos],
            'antes': st.session_state.historico[pos - 1] if pos > 0 else None,
            'depois': st.session_state.historico[pos + 1] if pos < len(st.session_state.historico) - 1 else None
        }
        ocorrencias_com_vizinhos.append(ocorrencia)
    
    return ocorrencias_com_vizinhos

def calcular_apostas_para_numero(numero_alvo):
    """Calcula as apostas para um número baseado nas últimas 3 ocorrências ANTERIORES"""
    ocorrencias = obter_ultimas_ocorrencias_anteriores(numero_alvo)
    
    if not ocorrencias:
        return None
    
    # Coleta todos os números para apostar
    numeros_aposta = []
    numeros_aposta.append(numero_alvo)  # Número alvo aparece apenas uma vez
    
    for ocorrencia in ocorrencias:
        if ocorrencia['antes'] is not None:
            numeros_aposta.append(ocorrencia['antes'])
        if ocorrencia['depois'] is not None:
            numeros_aposta.append(ocorrencia['depois'])
    
    # Calcula vizinhos
    numeros_unicos = list(set(numeros_aposta))
    vizinhos = obter_vizinhos_roleta(numeros_unicos)
    
    # Apostas finais (com duplicatas para cálculo de fichas)
    apostas_com_duplicatas = numeros_aposta + vizinhos
    
    # Calcula fichas
    fichas_por_numero = {}
    for numero in apostas_com_duplicatas:
        fichas_por_numero[numero] = fichas_por_numero.get(numero, 0) + 1
    
    custo_aposta = sum(fichas_por_numero.values())
    apostas_finais = sorted(list(set(apostas_com_duplicatas)))
    
    return {
        'numero_origem': numero_alvo,
        'numeros_aposta': numeros_aposta,
        'vizinhos': vizinhos,
        'fichas_por_numero': fichas_por_numero,
        'custo_aposta': custo_aposta,
        'apostas_finais': apostas_finais,
        'rodadas_apostadas': 0,
        'custo_acumulado': 0
    }

def iniciar_novo_ciclo(numero_inicial):
    """Inicia um novo ciclo de apostas"""
    aposta = calcular_apostas_para_numero(numero_inicial)
    if aposta:
        st.session_state.aposta_atual = aposta
        return aposta
    return None

def processar_numero_sorteado(numero):
    """Processa um número sorteado no ciclo atual"""
    # Se não há aposta atual, tenta iniciar ciclo
    if st.session_state.aposta_atual is None:
        aposta = iniciar_novo_ciclo(numero)
        if aposta is None:
            st.session_state.resultados.append("N")
        return
    
    aposta = st.session_state.aposta_atual
    fichas_por_numero = aposta['fichas_por_numero']
    custo_aposta = aposta['custo_aposta']
    
    # Verifica se é GREEN
    if numero in aposta['apostas_finais']:
        fichas_no_numero = fichas_por_numero.get(numero, 0)
        premio = fichas_no_numero * 36
        lucro = premio - custo_aposta
        
        # Atualiza banca
        st.session_state.banca += lucro
        st.session_state.resultados.append("1")
        
        # Mensagem de sucesso
        st.success(f"🎉 CICLO {st.session_state.ciclo_atual} CONCLUÍDO!")
        st.success(f"Rodadas: {aposta['rodadas_apostadas'] + 1} | Lucro: ${lucro:+.2f}")
        
        # Inicia novo ciclo
        st.session_state.ciclo_atual += 1
        novo_ciclo = iniciar_novo_ciclo(numero)
        if novo_ciclo:
            st.success(f"🔄 Iniciando CICLO {st.session_state.ciclo_atual}")
        
    else:
        # RED - Continua no mesmo ciclo
        st.session_state.banca -= custo_aposta
        st.session_state.resultados.append("X")
        aposta['rodadas_apostadas'] += 1
        aposta['custo_acumulado'] += custo_aposta

def registrar_numero(numero):
    """Registra um novo número"""
    st.session_state.historico.append(numero)
    processar_numero_sorteado(numero)

# Interface SIMPLIFICADA
st.title("🎯 Sistema de Ciclos - Aposta Fixa")

# Controles básicos
col1, col2 = st.columns(2)
with col1:
    novo_numero = st.number_input("Último número (0-36)", min_value=0, max_value=36, key="numero_input")
with col2:
    if st.button("Registrar", key="registrar_btn"):
        if novo_numero is not None:
            registrar_numero(novo_numero)
            st.rerun()

# Upload de CSV simplificado
uploaded_file = st.file_uploader("Carregar CSV", type="csv")
if uploaded_file:
    try:
        dados = pd.read_csv(uploaded_file)
        if 'Número' in dados.columns:
            st.session_state.historico = dados['Número'].tolist()
            st.session_state.resultados = []
            st.session_state.banca = 1000
            st.session_state.aposta_atual = None
            st.session_state.ciclo_atual = 1
            
            # Processa histórico
            for numero in st.session_state.historico:
                processar_numero_sorteado(numero)
                
            st.success(f"Histórico carregado! {len(dados)} números processados.")
            st.rerun()
    except Exception as e:
        st.error(f"Erro: {e}")

# Informações do Ciclo Atual
st.markdown("## 🔄 Ciclo Atual")

if st.session_state.aposta_atual:
    aposta = st.session_state.aposta_atual
    
    st.write(f"**CICLO {st.session_state.ciclo_atual}** | **Origem:** {aposta['numero_origem']}")
    st.write(f"**Rodadas:** {aposta['rodadas_apostadas']} | **Custo acumulado:** ${aposta['custo_acumulado']:.2f}")
    
    st.markdown("**🎯 Aposta Fixa:**")
    st.write(f"Números: {aposta['numeros_aposta']}")
    st.write(f"Vizinhos: {aposta['vizinhos']}")
    
    st.markdown("**💰 Custo por rodada:**")
    st.write(f"${aposta['custo_aposta']:.2f} | {len(aposta['fichas_por_numero'])} números únicos")
    
else:
    st.info("Aguardando número para iniciar ciclo...")

# Resultados simples
st.markdown("## 🎲 Resultados")
if st.session_state.resultados:
    # Mostra apenas últimos 20 resultados
    ultimos_resultados = st.session_state.resultados[-20:] if len(st.session_state.resultados) > 20 else st.session_state.resultados
    st.write(" ".join(ultimos_resultados))
    
    total_green = st.session_state.resultados.count("1")
    total_red = st.session_state.resultados.count("X")
    total_apostas = total_green + total_red
    
    if total_apostas > 0:
        taxa = (total_green / total_apostas) * 100
        st.write(f"**GREEN:** {total_green} | **RED:** {total_red} | **Taxa:** {taxa:.1f}%")
    
    st.write(f"**Banca:** ${st.session_state.banca:.2f}")

# Botão reset simples
if st.button("🔄 Resetar Sistema"):
    st.session_state.historico = []
    st.session_state.resultados = []
    st.session_state.banca = 1000
    st.session_state.aposta_atual = None
    st.session_state.ciclo_atual = 1
    st.success("Sistema resetado!")
    st.rerun()
