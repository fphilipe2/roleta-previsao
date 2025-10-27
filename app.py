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
if 'analise_vizinhos' not in st.session_state:
    st.session_state.analise_vizinhos = {}

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

def analisar_tempo_vizinhos():
    """Analisa quantas rodadas demorou para sair cada vizinho após cada número"""
    st.session_state.analise_vizinhos = {}
    
    if len(st.session_state.historico) < 2:
        return
    
    for i in range(len(st.session_state.historico) - 1):
        numero_atual = st.session_state.historico[i]
        vizinhos = vizinhos_map.get(numero_atual, [])
        
        if numero_atual not in st.session_state.analise_vizinhos:
            st.session_state.analise_vizinhos[numero_atual] = {}
        
        # Para cada vizinho, verifica quando ele saiu depois
        for vizinho in vizinhos:
            if vizinho not in st.session_state.analise_vizinhos[numero_atual]:
                st.session_state.analise_vizinhos[numero_atual][vizinho] = []
            
            # Procura a próxima ocorrência deste vizinho
            for j in range(i + 1, len(st.session_state.historico)):
                if st.session_state.historico[j] == vizinho:
                    tempo = j - i
                    st.session_state.analise_vizinhos[numero_atual][vizinho].append(tempo)
                    break

def calcular_estatisticas_vizinhos():
    """Calcula estatísticas dos tempos dos vizinhos"""
    estatisticas = {}
    
    for numero, vizinhos_data in st.session_state.analise_vizinhos.items():
        estatisticas[numero] = {}
        
        for vizinho, tempos in vizinhos_data.items():
            if tempos:
                estatisticas[numero][vizinho] = {
                    'media': sum(tempos) / len(tempos),
                    'min': min(tempos),
                    'max': max(tempos),
                    'qtd': len(tempos),
                    'ultimos_5': tempos[-5:] if len(tempos) >= 5 else tempos
                }
    
    return estatisticas

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
    
    for i in range(1, len(st.session_state.historico)):
        numero_atual = st.session_state.historico[i]
        numero_que_gerou_aposta = st.session_state.historico[i]
        
        numeros_aposta, vizinhos, apostas_com_duplicatas = calcular_apostas_para_numero(
            numero_que_gerou_aposta, excluir_ultima_ocorrencia=True
        )
        
        if not numeros_aposta:
            st.session_state.resultados.append("N")
            st.session_state.historico_banca.append(st.session_state.banca)
            continue
        
        fichas_por_numero = calcular_fichas_aposta(apostas_com_duplicatas)
        custo_aposta = calcular_custo_aposta(fichas_por_numero)
        
        if i < len(st.session_state.historico) - 1:
            proximo_numero = st.session_state.historico[i + 1]
            premio, lucro, is_green = calcular_premiacao(proximo_numero, fichas_por_numero, custo_aposta)
            
            st.session_state.banca += lucro
            st.session_state.historico_banca.append(st.session_state.banca)
            
            if is_green:
                st.session_state.resultados.append("1")
            else:
                st.session_state.resultados.append("X")
        else:
            st.session_state.resultados.append("-")
            st.session_state.historico_banca.append(st.session_state.banca)

def registrar_numero(numero):
    """Registra um novo número e verifica a aposta baseada no PRÓPRIO número"""
    st.session_state.historico.append(numero)
    
    if len(st.session_state.historico) >= 2:
        numero_que_gerou_aposta = st.session_state.historico[-2]
        
        numeros_aposta, vizinhos, apostas_com_duplicatas = calcular_apostas_para_numero(
            numero_que_gerou_aposta, excluir_ultima_ocorrencia=True
        )
        
        if not numeros_aposta:
            st.session_state.resultados.append("N")
            st.session_state.historico_banca.append(st.session_state.banca)
            return
        
        fichas_por_numero = calcular_fichas_aposta(apostas_com_duplicatas)
        custo_aposta = calcular_custo_aposta(fichas_por_numero)
        
        premio, lucro, is_green = calcular_premiacao(numero, fichas_por_numero, custo_aposta)
        
        st.session_state.banca += lucro
        st.session_state.historico_banca.append(st.session_state.banca)
        
        if is_green:
            st.session_state.resultados.append("1")
        else:
            st.session_state.resultados.append("X")

# Interface
st.title("🎯 Análise de Padrão de Vizinhos + Estratégia")

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

# Análise de Vizinhos
st.markdown("## 📊 Análise de Padrão de Vizinhos")

if st.button("🔍 Analisar Tempo dos Vizinhos"):
    if st.session_state.historico:
        analisar_tempo_vizinhos()
        st.success("Análise concluída!")
    else:
        st.warning("Carregue um histórico primeiro")

if st.session_state.analise_vizinhos:
    estatisticas = calcular_estatisticas_vizinhos()
    
    # Selecionar número para análise
    numero_analise = st.selectbox(
        "Selecione um número para análise detalhada:",
        sorted(estatisticas.keys())
    )
    
    if numero_analise:
        st.markdown(f"### 📈 Análise do Número {numero_analise}")
        
        vizinhos_data = estatisticas[numero_analise]
        
        # Tabela de estatísticas
        st.markdown("**Estatísticas dos Vizinhos:**")
        dados_tabela = []
        for vizinho, stats in vizinhos_data.items():
            dados_tabela.append({
                'Vizinho': vizinho,
                'Média (rodadas)': f"{stats['media']:.1f}",
                'Mínimo': stats['min'],
                'Máximo': stats['max'],
                'Ocorrências': stats['qtd'],
                'Últimos 5': str(stats['ultimos_5'])
            })
        
        if dados_tabela:
            df_estatisticas = pd.DataFrame(dados_tabela)
            st.dataframe(df_estatisticas, use_container_width=True)
            
            # Tabela simplificada para visualização rápida
            st.markdown("**Resumo por Vizinho:**")
            for vizinho, stats in vizinhos_data.items():
                st.write(f"**Vizinho {vizinho}:** Média {stats['media']:.1f} rodadas "
                        f"(min {stats['min']}, max {stats['max']}) - "
                        f"{stats['qtd']} ocorrências")
        
        # Tabela geral de todos os números
        st.markdown("### 📋 Visão Geral de Todos os Números")
        
        dados_gerais = []
        for numero in sorted(estatisticas.keys()):
            if estatisticas[numero]:
                media_geral = sum(stats['media'] for stats in estatisticas[numero].values()) / len(estatisticas[numero])
                vizinho_mais_rapido = min(estatisticas[numero].items(), key=lambda x: x[1]['media'])
                vizinho_mais_lento = max(estatisticas[numero].items(), key=lambda x: x[1]['media'])
                
                dados_gerais.append({
                    'Número': numero,
                    'Média Geral': f"{media_geral:.1f}",
                    'Vizinho Mais Rápido': f"{vizinho_mais_rapido[0]} ({vizinho_mais_rapido[1]['media']:.1f} rod)",
                    'Vizinho Mais Lento': f"{vizinho_mais_lento[0]} ({vizinho_mais_lento[1]['media']:.1f} rod)",
                    'Total Vizinhos': len(estatisticas[numero])
                })
        
        if dados_gerais:
            df_geral = pd.DataFrame(dados_gerais)
            st.dataframe(df_geral, use_container_width=True)

# Estratégia Principal
if st.session_state.historico:
    ultimo_numero = st.session_state.historico[-1]
    
    st.markdown("## 🎯 Estratégia Principal")
    st.subheader(f"Último número sorteado: {ultimo_numero}")
    
    numeros_aposta, vizinhos, apostas_com_duplicatas = calcular_apostas_para_numero(
        ultimo_numero, excluir_ultima_ocorrencia=True
    )
    fichas_por_numero = calcular_fichas_aposta(apostas_com_duplicatas)
    custo_aposta = calcular_custo_aposta(fichas_por_numero)
    
    ocorrencias = obter_ultimas_ocorrencias_anteriores(ultimo_numero, excluir_ultima=True)
    
    if ocorrencias:
        st.markdown("**Últimas ocorrências ANTERIORES:**")
        for i, ocorrencia in enumerate(ocorrencias, 1):
            antes = f"{ocorrencia['antes']} → " if ocorrencia['antes'] is not None else ""
            depois = f" → {ocorrencia['depois']}" if ocorrencia['depois'] is not None else ""
            st.write(f"{i}. {antes}{ocorrencia['numero']}{depois}")
    
    if numeros_aposta:
        st.markdown("**Próximas Apostas:**")
        st.write(f"**Números:** {numeros_aposta}")
        st.write(f"**Vizinhos:** {vizinhos}")
        st.write(f"**Custo:** ${custo_aposta:,.2f}")
        
        # Mostrar estatísticas dos vizinhos se disponível
        if (st.session_state.analise_vizinhos and 
            ultimo_numero in st.session_state.analise_vizinhos):
            
            st.markdown("**📊 Estatísticas dos Vizinhos (Histórico):**")
            vizinhos_stats = st.session_state.analise_vizinhos[ultimo_numero]
            for vizinho, tempos in vizinhos_stats.items():
                if tempos:
                    media = sum(tempos) / len(tempos)
                    st.write(f"- Vizinho {vizinho}: {len(tempos)}x, média {media:.1f} rodadas")

# Resultados
st.markdown("## 🎲 Resultados das Apostas")
if st.session_state.resultados:
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
        st.write(f"**Banca:** ${st.session_state.banca:,.2f} | **Lucro:** ${lucro_total:+.2f}")

# Botões de controle
col1, col2 = st.columns(2)
with col1:
    if st.button("🔄 Re-verificar Histórico"):
        if st.session_state.historico:
            verificar_apostas_do_historico()
            st.success("Histórico re-verificado!")
            st.rerun()
with col2:
    if st.button("🔄 Resetar Sistema"):
        st.session_state.banca = 1000
        st.session_state.historico_banca = [1000]
        st.session_state.resultados.clear()
        st.session_state.analise_vizinhos.clear()
        st.success("Sistema resetado!")
        st.rerun()
