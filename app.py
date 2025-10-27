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
if 'analise_estrategia' not in st.session_state:
    st.session_state.analise_estrategia = {}

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

def analisar_desempenho_estrategia():
    """Analisa quanto tempo a estratégia demorou para dar GREEN em cada caso"""
    st.session_state.analise_estrategia = {}
    
    if len(st.session_state.historico) < 2:
        return
    
    for i in range(len(st.session_state.historico) - 1):
        numero_que_gerou_aposta = st.session_state.historico[i]
        
        # Calcula as apostas que seriam feitas naquele momento
        numeros_aposta, vizinhos, apostas_com_duplicatas = calcular_apostas_para_numero(
            numero_que_gerou_aposta, excluir_ultima_ocorrencia=True
        )
        
        if not numeros_aposta:
            continue  # Não havia apostas naquele momento
        
        # Cria uma chave única para esta configuração de apostas
        chave_estrategia = tuple(sorted(set(apostas_com_duplicatas)))
        
        if chave_estrategia not in st.session_state.analise_estrategia:
            st.session_state.analise_estrategia[chave_estrategia] = {
                'numeros_aposta': numeros_aposta,
                'vizinhos': vizinhos,
                'apostas_finais': sorted(list(set(apostas_com_duplicatas))),
                'tempos_green': [],
                'numero_origem': numero_que_gerou_aposta
            }
        
        # Procura quando deu GREEN (próximo número nas apostas)
        for j in range(i + 1, len(st.session_state.historico)):
            if st.session_state.historico[j] in apostas_com_duplicatas:
                tempo_green = j - i
                st.session_state.analise_estrategia[chave_estrategia]['tempos_green'].append(tempo_green)
                break

def calcular_estatisticas_estrategia():
    """Calcula estatísticas do desempenho da estratégia"""
    estatisticas = {}
    
    for chave, dados in st.session_state.analise_estrategia.items():
        if dados['tempos_green']:
            estatisticas[chave] = {
                'numero_origem': dados['numero_origem'],
                'numeros_aposta': dados['numeros_aposta'],
                'vizinhos': dados['vizinhos'],
                'apostas_finais': dados['apostas_finais'],
                'media_tempo': sum(dados['tempos_green']) / len(dados['tempos_green']),
                'min_tempo': min(dados['tempos_green']),
                'max_tempo': max(dados['tempos_green']),
                'qtd_greens': len(dados['tempos_green']),
                'taxa_sucesso': (len(dados['tempos_green']) / len(st.session_state.historico)) * 100 if st.session_state.historico else 0
            }
    
    return estatisticas

def encontrar_estrategia_similar(estrategia_atual, estatisticas):
    """Encontra estratégias similares no histórico"""
    estrategias_similares = []
    apostas_atuais_set = set(estrategia_atual)
    
    for chave, stats in estatisticas.items():
        apostas_historico_set = set(stats['apostas_finais'])
        
        # Calcula similaridade (quantos números em comum)
        numeros_comuns = len(apostas_atuais_set.intersection(apostas_historico_set))
        total_numeros = len(apostas_atuais_set.union(apostas_historico_set))
        similaridade = (numeros_comuns / total_numeros) * 100 if total_numeros > 0 else 0
        
        if similaridade > 50:  # Mais de 50% de similaridade
            estrategias_similares.append({
                'similaridade': similaridade,
                'estatisticas': stats
            })
    
    # Ordena por similaridade
    return sorted(estrategias_similares, key=lambda x: x['similaridade'], reverse=True)

def verificar_apostas_do_historico():
    """Verifica TODAS as apostas do histórico carregado"""
    st.session_state.resultados.clear()
    st.session_state.historico_banca = [1000]
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
st.title("🎯 Análise de Desempenho da Estratégia")

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

# Análise de Desempenho da Estratégia
st.markdown("## 📊 Análise de Desempenho da Estratégia")

if st.button("🔍 Analisar Desempenho da Estratégia"):
    if st.session_state.historico:
        analisar_desempenho_estrategia()
        st.success("Análise de desempenho concluída!")
    else:
        st.warning("Carregue um histórico primeiro")

# Estratégia Atual + Análise
if st.session_state.historico:
    ultimo_numero = st.session_state.historico[-1]
    
    st.markdown("## 🎯 Estratégia Atual")
    st.subheader(f"Último número sorteado: {ultimo_numero}")
    
    # Calcula a estratégia atual
    numeros_aposta, vizinhos, apostas_com_duplicatas = calcular_apostas_para_numero(
        ultimo_numero, excluir_ultima_ocorrencia=True
    )
    fichas_por_numero = calcular_fichas_aposta(apostas_com_duplicatas)
    custo_aposta = calcular_custo_aposta(fichas_por_numero)
    apostas_finais = sorted(list(set(apostas_com_duplicatas)))
    
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
        st.write(f"**Apostas Finais:** {apostas_finais}")
        st.write(f"**Custo:** ${custo_aposta:,.2f}")
        
        # Análise de desempenho para estratégia similar
        if st.session_state.analise_estrategia:
            estatisticas = calcular_estatisticas_estrategia()
            estrategias_similares = encontrar_estrategia_similar(apostas_finais, estatisticas)
            
            st.markdown("## 📈 Desempenho de Estratégias Similares")
            
            if estrategias_similares:
                st.markdown(f"**Encontradas {len(estrategias_similares)} estratégias similares no histórico:**")
                
                for i, estrategia in enumerate(estrategias_similares[:5], 1):  # Mostra as 5 mais similares
                    stats = estrategia['estatisticas']
                    st.markdown(f"**Estratégia Similar #{i}** ({estrategia['similaridade']:.1f}% similar)")
                    st.write(f"**Número de origem:** {stats['numero_origem']}")
                    st.write(f"**Tempo médio para GREEN:** {stats['media_tempo']:.1f} rodadas")
                    st.write(f"**Melhor caso:** {stats['min_tempo']} rodadas | **Pior caso:** {stats['max_tempo']} rodadas")
                    st.write(f"**Greens registrados:** {stats['qtd_greens']} | **Taxa de sucesso:** {stats['taxa_sucesso']:.1f}%")
                    st.write("---")
            else:
                st.info("Nenhuma estratégia similar encontrada no histórico.")
        
        # Estatísticas gerais da estratégia
        if st.session_state.analise_estrategia:
            estatisticas = calcular_estatisticas_estrategia()
            
            st.markdown("## 📋 Estatísticas Gerais da Estratégia")
            
            if estatisticas:
                # Calcula médias gerais
                todos_tempos = []
                for stats in estatisticas.values():
                    todos_tempos.extend(stats.get('tempos_green', []))
                
                if todos_tempos:
                    st.write(f"**Desempenho Geral da Estratégia:**")
                    st.write(f"- Tempo médio para GREEN: {sum(todos_tempos)/len(todos_tempos):.1f} rodadas")
                    st.write(f"- Melhor caso: {min(todos_tempos)} rodadas")
                    st.write(f"- Pior caso: {max(todos_tempos)} rodadas")
                    st.write(f"- Total de greens analisados: {len(todos_tempos)}")

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
        st.session_state.analise_estrategia.clear()
        st.success("Sistema resetado!")
        st.rerun()
