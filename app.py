import streamlit as st
import pandas as pd
from collections import deque

# Configuração inicial
if 'historico' not in st.session_state:
    st.session_state.historico = []
if 'resultados' not in st.session_state:
    st.session_state.resultados = deque(maxlen=1000)
if 'banca' not in st.session_state:
    st.session_state.banca = 1000
if 'historico_banca' not in st.session_state:
    st.session_state.historico_banca = [1000]

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

def obter_ultimas_ocorrencias_com_vizinhos(numero_alvo):
    """Obtém as últimas 3 ocorrências do número com seus números antes/depois"""
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

def calcular_apostas_para_numero(numero_alvo):
    """Calcula as apostas para um número baseado nas últimas 3 ocorrências"""
    ocorrencias = obter_ultimas_ocorrencias_com_vizinhos(numero_alvo)
    
    # Coleta todos os números para apostar
    numeros_aposta = []
    
    # O NÚMERO ALVO aparece APENAS UMA VEZ
    numeros_aposta.append(numero_alvo)
    
    for ocorrencia in ocorrencias:
        # Adiciona número antes (se existir) - PODE REPETIR
        if ocorrencia['antes'] is not None:
            numeros_aposta.append(ocorrencia['antes'])
        
        # Adiciona número depois (se existir) - PODE REPETIR
        if ocorrencia['depois'] is not None:
            numeros_aposta.append(ocorrencia['depois'])
    
    # Calcula vizinhos
    numeros_unicos = list(set(numeros_aposta))
    vizinhos = obter_vizinhos_roleta(numeros_unicos)
    
    # Apostas finais (com duplicatas para cálculo de fichas)
    apostas_com_duplicatas = numeros_aposta + vizinhos
    
    return numeros_aposta, vizinhos, apostas_com_duplicatas

def calcular_fichas_aposta(apostas_com_duplicatas):
    """Calcula quantas fichas serão colocadas em cada número"""
    fichas_por_numero = {}
    
    for numero in apostas_com_duplicatas:
        if numero in fichas_por_numero:
            fichas_por_numero[numero] += 1
        else:
            fichas_por_numero[numero] = 1
    
    return fichas_por_numero

def calcular_custo_aposta(fichas_por_numero):
    """Calcula o custo total da aposta"""
    return sum(fichas_por_numero.values())

def calcular_premiacao(numero_sorteado, fichas_por_numero, custo_aposta):
    """Calcula a premiação se o número sorteado estiver nas apostas"""
    if numero_sorteado in fichas_por_numero:
        fichas_no_numero = fichas_por_numero[numero_sorteado]
        premio = fichas_no_numero * 36
        lucro = premio - custo_aposta
        return premio, lucro, True  # GREEN
    else:
        return 0, -custo_aposta, False  # RED

def verificar_apostas_do_historico():
    """Verifica TODAS as apostas do histórico carregado - MESMA LÓGICA DA INSERÇÃO MANUAL"""
    st.session_state.resultados.clear()
    st.session_state.historico_banca = [1000]  # Banca inicial
    st.session_state.banca = 1000
    
    if len(st.session_state.historico) <= 1:
        return
    
    # MESMA LÓGICA DA INSERÇÃO MANUAL: para cada novo número, verifica aposta do anterior
    for i in range(1, len(st.session_state.historico)):
        numero_atual = st.session_state.historico[i]
        numero_anterior = st.session_state.historico[i-1]
        
        # Calcula apostas para o número ANTERIOR (mesma lógica do registrar_numero)
        numeros_aposta, vizinhos, apostas_com_duplicatas = calcular_apostas_para_numero(numero_anterior)
        
        # Calcula fichas e custo
        fichas_por_numero = calcular_fichas_aposta(apostas_com_duplicatas)
        custo_aposta = calcular_custo_aposta(fichas_por_numero)
        
        # Verifica resultado
        premio, lucro, is_green = calcular_premiacao(numero_atual, fichas_por_numero, custo_aposta)
        
        # Atualiza banca
        st.session_state.banca += lucro
        st.session_state.historico_banca.append(st.session_state.banca)
        
        # Registra resultado
        if is_green:
            st.session_state.resultados.append("1")
        else:
            st.session_state.resultados.append("X")

def registrar_numero(numero):
    """LÓGICA ORIGINAL DA INSERÇÃO MANUAL (que estava funcionando)"""
    if len(st.session_state.historico) >= 1:
        ultimo_sorteado_anterior = st.session_state.historico[-1]
        
        # Calcula apostas para o número ANTERIOR
        numeros_aposta, vizinhos, apostas_com_duplicatas = calcular_apostas_para_numero(ultimo_sorteado_anterior)
        
        # Calcula fichas e custo
        fichas_por_numero = calcular_fichas_aposta(apostas_com_duplicatas)
        custo_aposta = calcular_custo_aposta(fichas_por_numero)
        
        # Verifica resultado
        premio, lucro, is_green = calcular_premiacao(numero, fichas_por_numero, custo_aposta)
        
        # Atualiza banca
        st.session_state.banca += lucro
        st.session_state.historico_banca.append(st.session_state.banca)
        
        # Registra resultado
        if is_green:
            st.session_state.resultados.append("1")
        else:
            st.session_state.resultados.append("X")
    
    # Adiciona o novo número ao histórico
    st.session_state.historico.append(numero)

# Interface
st.title("🎯 Estratégia com Simulação de Banca")

# Controles
col1, col2 = st.columns(2)
with col1:
    novo_numero = st.number_input("Último número sorteado (0-36)", min_value=0, max_value=36)
with col2:
    if st.button("Registrar"):
        registrar_numero(novo_numero)
        st.rerun()

# Upload de CSV
uploaded_file = st.file_uploader("Carregar histórico (CSV)", type="csv")
if uploaded_file:
    try:
        dados = pd.read_csv(uploaded_file)
        if 'Número' in dados.columns:
            # Salva o histórico atual temporariamente
            historico_anterior = st.session_state.historico.copy() if st.session_state.historico else []
            
            # Carrega novo histórico
            st.session_state.historico = dados['Número'].tolist()
            st.success(f"Histórico carregado! {len(dados)} registros.")
            
            # VERIFICAÇÃO DO HISTÓRICO COM MESMA LÓGICA DA INSERÇÃO MANUAL
            verificar_apostas_do_historico()
            st.success(f"Verificação concluída! {len(st.session_state.resultados)} apostas analisadas.")
            
            st.rerun()
            
        else:
            st.error("O arquivo precisa ter a coluna 'Número'")
    except Exception as e:
        st.error(f"Erro ao ler arquivo: {e}")

# Exibição da estratégia
if st.session_state.historico:
    ultimo_numero = st.session_state.historico[-1]
    
    st.subheader(f"Último número sorteado: {ultimo_numero}")
    
    # ESTRATÉGIA
    st.markdown("### 🎯 Estratégia: Padrão de Ocorrências")
    
    # Calcula apostas para o último número
    numeros_aposta, vizinhos, apostas_com_duplicatas = calcular_apostas_para_numero(ultimo_numero)
    fichas_por_numero = calcular_fichas_aposta(apostas_com_duplicatas)
    custo_aposta = calcular_custo_aposta(fichas_por_numero)
    
    # Mostra as últimas ocorrências
    ocorrencias = obter_ultimas_ocorrencias_com_vizinhos(ultimo_numero)
    
    if ocorrencias:
        st.markdown("**Últimas ocorrências:**")
        for i, ocorrencia in enumerate(ocorrencias, 1):
            antes = f"{ocorrencia['antes']} → " if ocorrencia['antes'] is not None else ""
            depois = f" → {ocorrencia['depois']}" if ocorrencia['depois'] is not None else ""
            st.write(f"{i}. {antes}{ocorrencia['numero']}{depois}")
    
    st.markdown("**Números para apostar:**")
    st.write(f"**{numeros_aposta}**")
    
    st.markdown("**Vizinhos:**")
    st.write(f"**{vizinhos}**")
    
    st.markdown("**Distribuição de Fichas:**")
    for numero, fichas in sorted(fichas_por_numero.items()):
        st.write(f"- Número {numero}: {fichas} ficha{'s' if fichas > 1 else ''}")
    
    st.markdown("**💰 Simulação de Banca:**")
    st.write(f"- **Banca Atual:** ${st.session_state.banca:,.2f}")
    st.write(f"- **Próxima Aposta:** ${custo_aposta:,.2f}")
    
    # Resultados
    st.subheader("🎲 Resultados das Apostas")
    if st.session_state.resultados:
        resultados_display = " ".join(list(st.session_state.resultados))
        st.write(resultados_display)
        st.write(f"Total de apostas: {len(st.session_state.resultados)}")
        
        total_green = list(st.session_state.resultados).count("1")
        total_red = list(st.session_state.resultados).count("X")
        if st.session_state.resultados:
            taxa = (total_green / len(st.session_state.resultados)) * 100
            st.write(f"**GREEN: {total_green}** | **RED: {total_red}** | **Taxa: {taxa:.1f}%**")
            
            lucro_total = st.session_state.banca - 1000
            st.write(f"**Lucro Total:** ${lucro_total:+.2f}")

# Botões de controle
col1, col2 = st.columns(2)
with col1:
    if st.button("🔄 Re-verificar Histórico"):
        if st.session_state.historico:
            verificar_apostas_do_historico()
            st.success("Histórico re-verificado!")
            st.rerun()
with col2:
    if st.button("🔄 Resetar Banca"):
        st.session_state.banca = 1000
        st.session_state.historico_banca = [1000]
        st.session_state.resultados.clear()
        st.success("Banca resetada!")
        st.rerun()
