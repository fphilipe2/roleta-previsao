import streamlit as st
import pandas as pd
from collections import deque, defaultdict

# Configuração inicial
if 'historico' not in st.session_state:
    st.session_state.historico = []
if 'resultados' not in st.session_state:
    st.session_state.resultados = deque(maxlen=1000)
if 'banca' not in st.session_state:
    st.session_state.banca = 1000
if 'historico_banca' not in st.session_state:
    st.session_state.historico_banca = [1000]
if 'aposta_atual' not in st.session_state:
    st.session_state.aposta_atual = None
if 'ciclo_atual' not in st.session_state:
    st.session_state.ciclo_atual = 1
if 'numeros_apostados_ciclo' not in st.session_state:
    st.session_state.numeros_apostados_ciclo = []
if 'estatisticas_ciclos' not in st.session_state:
    st.session_state.estatisticas_ciclos = []

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

def iniciar_novo_ciclo(numero_inicial):
    """Inicia um novo ciclo de apostas baseado no número que saiu"""
    numeros_aposta, vizinhos, apostas_com_duplicatas = calcular_apostas_para_numero(
        numero_inicial, excluir_ultima_ocorrencia=True
    )
    
    if not numeros_aposta:
        return None
    
    fichas_por_numero = calcular_fichas_aposta(apostas_com_duplicatas)
    custo_aposta = calcular_custo_aposta(fichas_por_numero)
    apostas_finais = sorted(list(set(apostas_com_duplicatas)))
    
    st.session_state.aposta_atual = {
        'numero_origem': numero_inicial,
        'numeros_aposta': numeros_aposta,
        'vizinhos': vizinhos,
        'fichas_por_numero': fichas_por_numero,
        'custo_aposta': custo_aposta,
        'apostas_finais': apostas_finais,
        'rodadas_apostadas': 0,
        'custo_acumulado': 0
    }
    
    st.session_state.numeros_apostados_ciclo = []
    
    return st.session_state.aposta_atual

def processar_numero_sorteado(numero):
    """Processa um número sorteado no ciclo atual"""
    if st.session_state.aposta_atual is None:
        # Inicia primeiro ciclo
        aposta = iniciar_novo_ciclo(numero)
        if aposta is None:
            st.session_state.resultados.append("N")  # No Bet
        return
    
    # Adiciona número ao histórico do ciclo
    st.session_state.numeros_apostados_ciclo.append(numero)
    
    # Verifica se é GREEN
    fichas_por_numero = st.session_state.aposta_atual['fichas_por_numero']
    custo_aposta = st.session_state.aposta_atual['custo_aposta']
    
    premio, lucro, is_green = calcular_premiacao(numero, fichas_por_numero, custo_aposta)
    
    # Atualiza estatísticas do ciclo
    st.session_state.aposta_atual['rodadas_apostadas'] += 1
    st.session_state.aposta_atual['custo_acumulado'] += custo_aposta
    
    # Atualiza banca
    st.session_state.banca += lucro
    st.session_state.historico_banca.append(st.session_state.banca)
    
    if is_green:
        # GREEN - Finaliza ciclo com sucesso
        st.session_state.resultados.append("1")
        
        # Registra estatísticas do ciclo
        ciclo_info = {
            'ciclo': st.session_state.ciclo_atual,
            'numero_origem': st.session_state.aposta_atual['numero_origem'],
            'rodadas': st.session_state.aposta_atual['rodadas_apostadas'],
            'custo_total': st.session_state.aposta_atual['custo_acumulado'],
            'premio': premio,
            'lucro': lucro,
            'numeros_apostados': st.session_state.numeros_apostados_ciclo.copy()
        }
        st.session_state.estatisticas_ciclos.append(ciclo_info)
        
        # Inicia novo ciclo com o número que deu GREEN
        st.session_state.ciclo_atual += 1
        novo_ciclo = iniciar_novo_ciclo(numero)
        
        if novo_ciclo:
            st.success(f"🎉 CICLO {ciclo_info['ciclo']} CONCLUÍDO! GREEN em {ciclo_info['rodadas']} rodadas")
            st.success(f"💰 Lucro do ciclo: ${lucro:+.2f}")
            st.success(f"🔄 Iniciando CICLO {st.session_state.ciclo_atual} com número {numero}")
        else:
            st.warning("Não foi possível iniciar novo ciclo. Aguardando próximo número...")
            
    else:
        # RED - Continua no mesmo ciclo
        st.session_state.resultados.append("X")
        st.info(f"🔴 CICLO {st.session_state.ciclo_atual} - Rodada {st.session_state.aposta_atual['rodadas_apostadas']} - Prejuízo: ${-custo_aposta:.2f}")

def registrar_numero(numero):
    """Registra um novo número e processa no sistema de ciclos"""
    st.session_state.historico.append(numero)
    processar_numero_sorteado(numero)

def verificar_apostas_do_historico():
    """Verifica TODAS as apostas do histórico carregado no sistema de ciclos"""
    st.session_state.resultados.clear()
    st.session_state.historico_banca = [1000]
    st.session_state.banca = 1000
    st.session_state.aposta_atual = None
    st.session_state.ciclo_atual = 1
    st.session_state.numeros_apostados_ciclo = []
    st.session_state.estatisticas_ciclos = []
    
    if len(st.session_state.historico) <= 1:
        return
    
    # Processa cada número do histórico
    for i in range(len(st.session_state.historico)):
        numero = st.session_state.historico[i]
        processar_numero_sorteado(numero)

# Interface
st.title("🎯 Sistema de Apostas com Ciclos - Aposta Fixa até GREEN")

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
            
            verificar_apostas_do_historico()
            st.success(f"Verificação concluída! {len(st.session_state.resultados)} apostas analisadas.")
            
            st.rerun()
            
        else:
            st.error("O arquivo precisa ter a coluna 'Número'")
    except Exception as e:
        st.error(f"Erro ao ler arquivo: {e}")

# Informações do Ciclo Atual
st.markdown("## 🔄 Ciclo Atual")

if st.session_state.aposta_atual:
    aposta = st.session_state.aposta_atual
    
    st.markdown(f"### CICLO {st.session_state.ciclo_atual}")
    st.write(f"**Número de origem:** {aposta['numero_origem']}")
    st.write(f"**Rodadas apostadas:** {aposta['rodadas_apostadas']}")
    st.write(f"**Custo acumulado:** ${aposta['custo_acumulado']:,.2f}")
    
    st.markdown("### 🎯 Aposta Fixa do Ciclo")
    st.write(f"**Números para apostar:** {aposta['numeros_aposta']}")
    st.write(f"**Vizinhos:** {aposta['vizinhos']}")
    st.write(f"**Apostas Finais:** {aposta['apostas_finais']}")
    
    st.markdown("**Distribuição de Fichas:**")
    for numero, fichas in sorted(aposta['fichas_por_numero'].items()):
        st.write(f"- Número {numero}: {fichas} ficha{'s' if fichas > 1 else ''}")
    
    st.markdown("**💰 Informações Financeiras:**")
    st.write(f"- **Custo por rodada:** ${aposta['custo_aposta']:,.2f}")
    st.write(f"- **Números únicos apostados:** {len(aposta['fichas_por_numero'])}")
    
    # Próximos números que dão GREEN
    st.markdown("**🎯 Números que dão GREEN:**")
    st.write(f"**{aposta['apostas_finais']}**")
    
else:
    st.info("Aguardando primeiro número para iniciar ciclo...")

# Estatísticas dos Ciclos
if st.session_state.estatisticas_ciclos:
    st.markdown("## 📊 Estatísticas dos Ciclos Concluídos")
    
    df_ciclos = pd.DataFrame(st.session_state.estatisticas_ciclos)
    
    # Métricas gerais
    total_ciclos = len(st.session_state.estatisticas_ciclos)
    total_lucro = sum(ciclo['lucro'] for ciclo in st.session_state.estatisticas_ciclos)
    media_rodadas = sum(ciclo['rodadas'] for ciclo in st.session_state.estatisticas_ciclos) / total_ciclos
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Ciclos", total_ciclos)
    with col2:
        st.metric("Lucro Total", f"${total_lucro:+.2f}")
    with col3:
        st.metric("Média de Rodadas", f"{media_rodadas:.1f}")
    
    # Tabela detalhada
    st.markdown("**Detalhes dos Ciclos:**")
    st.dataframe(df_ciclos, use_container_width=True)

# Resultados
st.markdown("## 🎲 Resultados dos Ciclos")
if st.session_state.resultados:
    resultados_validos = [r for r in st.session_state.resultados if r in ['1', 'X']]
    resultados_display = " ".join(resultados_validos)
    st.write(resultados_display)
    st.write(f"Total de rodadas: {len(resultados_validos)}")
    
    if resultados_validos:
        total_green = resultados_validos.count("1")
        total_red = resultados_validos.count("X")
        taxa = (total_green / len(resultados_validos)) * 100
        st.write(f"**GREEN: {total_green}** | **RED: {total_red}** | **Taxa: {taxa:.1f}%**")
        
        lucro_total = st.session_state.banca - 1000
        st.write(f"**Banca:** ${st.session_state.banca:,.2f} | **Lucro Total:** ${lucro_total:+.2f}")

# Botões de controle
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🔄 Re-verificar Histórico"):
        if st.session_state.historico:
            verificar_apostas_do_historico()
            st.success("Histórico re-verificado!")
            st.rerun()
with col2:
    if st.button("🔄 Reiniciar Ciclo Atual"):
        if st.session_state.historico:
            ultimo_numero = st.session_state.historico[-1]
            iniciar_novo_ciclo(ultimo_numero)
            st.success("Ciclo reiniciado!")
            st.rerun()
with col3:
    if st.button("🔄 Resetar Sistema"):
        st.session_state.banca = 1000
        st.session_state.historico_banca = [1000]
        st.session_state.resultados.clear()
        st.session_state.aposta_atual = None
        st.session_state.ciclo_atual = 1
        st.session_state.numeros_apostados_ciclo = []
        st.session_state.estatisticas_ciclos = []
        st.success("Sistema resetado!")
        st.rerun()
