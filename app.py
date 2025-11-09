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

def obter_ultimas_ocorrencias_anteriores(numero_alvo, excluir_ultima=True):
    """Obtém as últimas 3 ocorrências ANTERIORES do número (excluindo a última ocorrência)"""
    ocorrencias_com_vizinhos = []
    
    # Encontra todas as posições do número no histórico
    posicoes = [i for i, num in enumerate(st.session_state.historico) if num == numero_alvo]
    
    # Se deve excluir a última ocorrência (a que acabou de sair)
    if excluir_ultima and posicoes:
        posicoes = posicoes[:-1]  # Remove a última ocorrência
    
    # Pega as últimas 3 ocorrências anteriores
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

def calcular_apostas_para_numero(numero_alvo, excluir_ultima_ocorrencia=True):
    """Calcula as apostas para um número baseado nas últimas 3 ocorrências ANTERIORES"""
    ocorrencias = obter_ultimas_ocorrencias_anteriores(numero_alvo, excluir_ultima_ocorrencia)
    
    # Coleta todos os números para apostar
    numeros_aposta = []
    
    # O NÚMERO ALVO aparece APENAS UMA VEZ (se tiver ocorrências anteriores)
    if ocorrencias:
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
    """Verifica TODAS as apostas do histórico carregado"""
    st.session_state.resultados.clear()
    st.session_state.historico_banca = [1000]  # Banca inicial
    st.session_state.banca = 1000
    
    if len(st.session_state.historico) <= 1:
        return
    
    # Para cada número a partir da posição 1, verifica as apostas baseadas no PRÓPRIO número
    for i in range(1, len(st.session_state.historico)):
        numero_atual = st.session_state.historico[i]
        numero_que_gerou_aposta = st.session_state.historico[i]  # O PRÓPRIO número atual
        
        # Calcula apostas para o PRÓPRIO número (excluindo a última ocorrência)
        numeros_aposta, vizinhos, apostas_com_duplicatas = calcular_apostas_para_numero(
            numero_que_gerou_aposta, excluir_ultima_ocorrencia=True
        )
        
        # Se não há ocorrências anteriores suficientes, não há aposta
        if not numeros_aposta:
            st.session_state.resultados.append("N")  # NO BET
            st.session_state.historico_banca.append(st.session_state.banca)
            continue
        
        # Calcula fichas e custo
        fichas_por_numero = calcular_fichas_aposta(apostas_com_duplicatas)
        custo_aposta = calcular_custo_aposta(fichas_por_numero)
        
        # Verifica resultado (o próximo número será verificado na próxima iteração)
        # Para a última posição, não há próximo número para verificar
        if i < len(st.session_state.historico) - 1:
            proximo_numero = st.session_state.historico[i + 1]
            premio, lucro, is_green = calcular_premiacao(proximo_numero, fichas_por_numero, custo_aposta)
            
            # Atualiza banca
            st.session_state.banca += lucro
            st.session_state.historico_banca.append(st.session_state.banca)
            
            # Registra resultado
            if is_green:
                st.session_state.resultados.append("1")
            else:
                st.session_state.resultados.append("X")
        else:
            # Último número do histórico - não tem próximo para verificar
            st.session_state.resultados.append("-")
            st.session_state.historico_banca.append(st.session_state.banca)

def registrar_numero(numero):
    """Registra um novo número e verifica a aposta baseada no PRÓPRIO número"""
    # Primeiro adiciona o número ao histórico
    st.session_state.historico.append(numero)
    
    # Para verificar a aposta, precisamos de pelo menos 2 números no histórico
    if len(st.session_state.historico) >= 2:
        # O número que vai gerar a aposta é o PENÚLTIMO (excluindo o que acabou de ser adicionado)
        numero_que_gerou_aposta = st.session_state.historico[-2]
        
        # Calcula apostas para o número ANTERIOR (excluindo a última ocorrência)
        numeros_aposta, vizinhos, apostas_com_duplicatas = calcular_apostas_para_numero(
            numero_que_gerou_aposta, excluir_ultima_ocorrencia=True
        )
        
        # Se não há ocorrências anteriores suficientes, não há aposta
        if not numeros_aposta:
            st.session_state.resultados.append("N")  # NO BET
            st.session_state.historico_banca.append(st.session_state.banca)
            return
        
        # Calcula fichas e custo
        fichas_por_numero = calcular_fichas_aposta(apostas_com_duplicatas)
        custo_aposta = calcular_custo_aposta(fichas_por_numero)
        
        # Verifica resultado com o número ATUAL (que acabou de ser adicionado)
        premio, lucro, is_green = calcular_premiacao(numero, fichas_por_numero, custo_aposta)
        
        # Atualiza banca
        st.session_state.banca += lucro
        st.session_state.historico_banca.append(st.session_state.banca)
        
        # Registra resultado
        if is_green:
            st.session_state.resultados.append("1")
        else:
            st.session_state.resultados.append("X")

# Interface
st.title("🎯 Estratégia Corrigida - Ocorrências Anteriores")

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
            st.session_state.historico = dados['Número'].tolist()
            st.success(f"Histórico carregado! {len(dados)} registros.")
            
            # VERIFICAÇÃO CORRIGIDA
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
    
    # ESTRATÉGIA - Mostra as apostas para o PRÓXIMO número baseado no ÚLTIMO número
    st.markdown("### 🎯 Próximas Apostas (baseadas no último número)")
    
    # Calcula apostas para o último número (excluindo a última ocorrência)
    numeros_aposta, vizinhos, apostas_com_duplicatas = calcular_apostas_para_numero(
        ultimo_numero, excluir_ultima_ocorrencia=True
    )
    fichas_por_numero = calcular_fichas_aposta(apostas_com_duplicatas)
    custo_aposta = calcular_custo_aposta(fichas_por_numero)
    
    # Mostra as últimas ocorrências ANTERIORES (excluindo a última)
    ocorrencias = obter_ultimas_ocorrencias_anteriores(ultimo_numero, excluir_ultima=True)
    
    if ocorrencias:
        st.markdown("**Últimas ocorrências ANTERIORES:**")
        for i, ocorrencia in enumerate(ocorrencias, 1):
            antes = f"{ocorrencia['antes']} → " if ocorrencia['antes'] is not None else ""
            depois = f" → {ocorrencia['depois']}" if ocorrencia['depois'] is not None else ""
            st.write(f"{i}. {antes}{ocorrencia['numero']}{depois}")
    else:
        st.write("Número não tem ocorrências anteriores suficientes para apostar")
    
    if numeros_aposta:
        st.markdown("**Números para apostar:**")
        st.write(f"**{numeros_aposta}**")
        
        st.markdown("**Vizinhos:**")
        st.write(f"**{vizinhos}**")
        
        st.markdown("**Distribuição de Fichas:**")
        for numero, fichas in sorted(fichas_por_numero.items()):
            st.write(f"- Número {numero}: {fichas} ficha{'s' if fichas > 1 else ''}")
        
        st.markdown("**💰 Próxima Aposta:**")
        st.write(f"- **Custo:** ${custo_aposta:,.2f}")
        st.write(f"- **Números únicos:** {len(fichas_por_numero)}")
    
    # Resultados
    st.subheader("🎲 Resultados das Apostas")
    if st.session_state.resultados:
        # Filtra apenas resultados 1/X (remove N e -)
        resultados_validos = [r for r in st.session_state.resultados if r in ['1', 'X']]
        resultados_display = " ".join(resultados_validos)
        st.write(resultados_display)
        st.write(f"Total de apostas: {len(resultados_validos)}")
        
        if resultados_validos:
            total_green = resultados_validos.count("1")
            total_red = resultados_validos.count("X")
            taxa = (total_green / len(resultados_validos)) * 100
            st.write(f"**GREEN: {total_green}** | **RED: {total_red}** | **Taxa: {taxa:.1f}%**")
            
            lucro_total = st.session_state.banca - 1000
            st.write(f"**Banca Atual:** ${st.session_state.banca:,.2f}")
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
