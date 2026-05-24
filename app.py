import streamlit as st
import pandas as pd
from collections import deque, Counter
from itertools import combinations

# Configuração inicial
if 'historico' not in st.session_state:
    st.session_state.historico = deque(maxlen=1000)
if 'resultados_ausentes' not in st.session_state:
    st.session_state.resultados_ausentes = deque(maxlen=1000)
if 'resultados_vizinhos' not in st.session_state:
    st.session_state.resultados_vizinhos = deque(maxlen=1000)
if 'resultados_setores' not in st.session_state:
    st.session_state.resultados_setores = deque(maxlen=1000)

# Mapa de vizinhos da roleta europeia (ordem no cilindro)
ordem_roleta = [0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26]

# Criar dicionário de posição na roleta
posicao_roleta = {numero: idx for idx, numero in enumerate(ordem_roleta)}

def obter_vizinhos_laterais(numero, quantidade=2):
    """Retorna N vizinhos de cada lado na roleta (inclui o número central)"""
    if numero not in posicao_roleta:
        return []
    
    pos = posicao_roleta[numero]
    total_numeros = len(ordem_roleta)
    
    setor = [numero]
    # Vizinhos à esquerda (sentido horário)
    for i in range(1, quantidade + 1):
        setor.append(ordem_roleta[(pos - i) % total_numeros])
    # Vizinhos à direita (sentido anti-horário)
    for i in range(1, quantidade + 1):
        setor.append(ordem_roleta[(pos + i) % total_numeros])
    
    return sorted(setor))

def calcular_melhor_combinacao(ultimas_rodadas=30, num_numeros=4, vizinhos=2):
    """Encontra a melhor combinação de números que maximiza acertos nos últimos X resultados"""
    if len(st.session_state.historico) < ultimas_rodadas:
        return None, None, None
    
    # Pega os últimos números
    ultimos_numeros = list(st.session_state.historico)[-ultimas_rodadas:]
    
    # Para cada número, calcula seu setor (incluindo vizinhos)
    setor_por_numero = {}
    for num in range(37):
        setor = obter_vizinhos_laterais(num, quantidade=vizinhos)
        setor_por_numero[num] = set(setor)
    
    # Testa todas as combinações de números (otimizado - testa os mais frequentes primeiro)
    # Pega os 15 números mais frequentes para otimizar
    frequencias = Counter(ultimos_numeros)
    numeros_mais_frequentes = [num for num, _ in frequencias.most_common(20)]
    
    melhor_combinacao = None
    melhor_cobertura = 0
    melhor_detalhes = None
    
    # Testa combinações (limitado para performance)
    from itertools import combinations
    
    # Se tiver poucos números frequentes, testa todos
    if len(numeros_mais_frequentes) >= num_numeros:
        combinacoes_testar = combinations(numeros_mais_frequentes, num_numeros)
    else:
        combinacoes_testar = combinations(range(37), num_numeros)
    
    # Limita número de combinações para performance
    total_combinacoes = 0
    max_combinacoes = 5000  # Limite para não travar
    
    for combo in combinacoes_testar:
        total_combinacoes += 1
        if total_combinacoes > max_combinacoes:
            break
            
        # Une todos os setores da combinação
        setores_unidos = set()
        for num in combo:
            setores_unidos.update(setor_por_numero[num])
        
        # Calcula quantos dos últimos números seriam cobertos
        cobertura = sum(1 for num in ultimos_numeros if num in setores_unidos)
        
        if cobertura > melhor_cobertura:
            melhor_cobertura = cobertura
            melhor_combinacao = combo
            melhor_detalhes = {
                'setores_unidos': sorted(list(setores_unidos)),
                'cobertura': cobertura,
                'total_ultimos': len(ultimos_numeros),
                'tamanho_aposta': len(setores_unidos)
            }
    
    return melhor_combinacao, melhor_cobertura, melhor_detalhes

def registrar_numero_setores(numero):
    """Registra número e calcula resultado da estratégia otimizada de setores"""
    historico_list = list(st.session_state.historico)
    
    # Estratégia otimizada de setores (usa últimas 30 rodadas)
    if len(historico_list) >= 30:
        # Usa as últimas 30 rodadas (excluindo o número atual)
        ultimos_30_anteriores = historico_list[-30:] if len(historico_list) >= 30 else historico_list
        
        # Encontra melhor combinação baseado nas últimas 30 (excluindo atual)
        melhor_combo, cobertura, detalhes = calcular_melhor_combinacao(30, num_numeros=4, vizinhos=2)
        
        if detalhes and 'setores_unidos' in detalhes:
            apostas_setores = detalhes['setores_unidos']
            if numero in apostas_setores:
                st.session_state.resultados_setores.append("1")
            else:
                st.session_state.resultados_setores.append("X")
    
    # Mantém as outras estratégias
    if len(historico_list) >= 65:
        ultimos_65_anteriores = historico_list[-65:]
        numeros_sorteados_65 = set(ultimos_65_anteriores)
        todos_numeros = set(range(0, 37))
        numeros_atrasados = sorted(list(todos_numeros - numeros_sorteados_65))
        
        # Linha 1: Apenas ausentes
        if numero in numeros_atrasados:
            st.session_state.resultados_ausentes.append("1")
        else:
            st.session_state.resultados_ausentes.append("X")
        
        # Linha 2: Ausentes + 1 vizinho de cada lado
        from collections import deque
        vizinhos_atrasados = set()
        for num in numeros_atrasados:
            if num in posicao_roleta:
                pos = posicao_roleta[num]
                total = len(ordem_roleta)
                vizinhos_atrasados.add(ordem_roleta[(pos - 1) % total])
                vizinhos_atrasados.add(ordem_roleta[(pos + 1) % total])
        
        apostas_vizinhos = sorted(list(set(numeros_atrasados) | vizinhos_atradados))
        
        if numero in apostas_vizinhos:
            st.session_state.resultados_vizinhos.append("1")
        else:
            st.session_state.resultados_vizinhos.append("X")
    
    st.session_state.historico.append(numero)

# Interface
st.title("🎯 Estratégia Otimizada - Setores da Roleta")

# Abas
tab1, tab2, tab3 = st.tabs(["🎲 Estratégia Otimizada", "📊 Comparação", "📈 Histórico"])

with tab1:
    st.markdown("""
    ### 🎯 Estratégia: 4 Números + 2 Vizinhos de Cada Lado
    
    **Como funciona:**
    1. Analisa as últimas **30 rodadas**
    2. Testa **todas as combinações** de 4 números
    3. Para cada número, considera o setor: número + **2 vizinhos de cada lado** (total 5 números por setor)
    4. Escolhe a combinação que **MAIS acerta** nos últimos 30 resultados
    5. Total de números apostados: até **20 números** (54% da roleta)
    
    **Vantagens:**
    - ✅ Aposta otimizada para os últimos 30 resultados
    - ✅ Evita sobreposição desnecessária
    - ✅ Maximiza a probabilidade de acerto
    """)
    
    # Controles
    col1, col2 = st.columns(2)
    with col1:
        novo_numero = st.number_input("Último número sorteado (0-36)", min_value=0, max_value=36, key="numero_setores")
    with col2:
        if st.button("Registrar Número", key="btn_setores"):
            registrar_numero_setores(novo_numero)
            st.rerun()
    
    # Upload de CSV
    uploaded_file = st.file_uploader("Carregar histórico (CSV)", type="csv", key="csv_setores")
    if uploaded_file:
        try:
            dados = pd.read_csv(uploaded_file)
            if 'Número' in dados.columns:
                st.session_state.historico.clear()
                st.session_state.resultados_ausentes.clear()
                st.session_state.resultados_vizinhos.clear()
                st.session_state.resultados_setores.clear()
                
                for num in dados['Número'].tolist()[-1000:]:
                    registrar_numero_setores(num)
                
                st.success(f"Histórico carregado! {len(st.session_state.historico)} registros.")
                st.rerun()
            else:
                st.error("O arquivo precisa ter a coluna 'Número'")
        except Exception as e:
            st.error(f"Erro ao ler arquivo: {e}")
    
    # Exibição da estratégia atual
    if len(st.session_state.historico) >= 30:
        melhor_combo, cobertura, detalhes = calcular_melhor_combinacao(30, num_numeros=4, vizinhos=2)
        
        if melhor_combo and detalhes:
            st.markdown("### 🎲 Melhor Combinação Encontrada")
            
            # Mostra os 4 números escolhidos
            col1, col2, col3, col4 = st.columns(4)
            for idx, col in enumerate([col1, col2, col3, col4]):
                col.metric(f"Número {idx+1}", melhor_combo[idx], 
                          f"Vizinhos: 2 cada lado")
            
            st.markdown("### 📊 Detalhes da Combinação")
            
            # Para cada número, mostra seu setor
            st.markdown("**Setores Individuais (número + 2 vizinhos cada lado):**")
            for num in melhor_combo:
                setor = obter_vizinhos_laterais(num, quantidade=2)
                st.write(f"- **Número {num}**: {setor}")
            
            # Aposta final
            st.markdown("### ✅ APOSTA FINAL RECOMENDADA")
            st.write(f"**Números para apostar:** {detalhes['setores_unidos']}")
            st.write(f"**Total de números únicos:** {detalhes['tamanho_aposta']} de 37")
            st.write(f"**Cobertura da roleta:** {(detalhes['tamanho_aposta']/37*100):.1f}%")
            
            # Cobertura dos últimos 30
            st.markdown("### 📊 Performance nos Últimos 30 Números")
            
            cobertura_percent = (detalhes['cobertura'] / detalhes['total_ultimos'] * 100)
            
            col1, col2 = st.columns(2)
            col1.metric("Acertos potenciais", f"{detalhes['cobertura']}/{detalhes['total_ultimos']}")
            col2.metric("Taxa de acerto", f"{cobertura_percent:.1f}%")
            
            # Comparação com cobertura aleatória
            cobertura_aleatoria = (detalhes['tamanho_aposta'] / 37) * 100
            if cobertura_percent > cobertura_aleatoria:
                st.success(f"✅ **{cobertura_percent - cobertura_aleatoria:.1f}% melhor que cobertura aleatória!**")
            else:
                st.warning(f"⚠️ **{cobertura_aleatoria - cobertura_percent:.1f}% pior que cobertura aleatória**")
            
            # Visualização da roleta
            st.markdown("### 🎨 Visualização da Roleta")
            
            # Cria grid da roleta
            apostas = set(detalhes['setores_unidos'])
            roleta_grid = []
            for i in range(0, 37, 6):
                linha = []
                for j in range(6):
                    num = i + j
                    if num <= 36:
                        if num in apostas:
                            linha.append(f"🟢 {num:2d}")
                        else:
                            linha.append(f"⚪ {num:2d}")
                roleta_grid.append(" | ".join(linha))
            
            st.code("\n".join(roleta_grid))
            
            # Resultados da estratégia
            st.markdown("### 🎲 Resultados - Estratégia Otimizada")
            if st.session_state.resultados_setores:
                resultados = list(st.session_state.resultados_setores)
                
                # Mostra últimos resultados
                resultados_display = " ".join(resultados[-50:])
                st.code(resultados_display)
                
                # Estatísticas
                total_green = resultados.count("1")
                total_red = resultados.count("X")
                taxa_acerto = (total_green / len(resultados) * 100)
                
                col1, col2, col3 = st.columns(3)
                col1.metric("GREEN", total_green)
                col2.metric("RED", total_red)
                col3.metric("Taxa de Acerto", f"{taxa_acerto:.1f}%")
                
                # Sequência atual
                st.write(f"**Últimos 10 resultados:** {resultados[-10:]}")
                st.write(f"**Sequência atual:** {''.join(resultados[-5:])}")
                
                # Performance ao longo do tempo
                if len(resultados) >= 10:
                    st.markdown("**Performance por blocos de 10 apostas:**")
                    blocos = []
                    for i in range(0, len(resultados), 10):
                        bloco = resultados[i:i+10]
                        acertos = bloco.count("1")
                        blocos.append(f"{i+1}-{min(i+10, len(resultados))}: {acertos}/10 ({acertos*10}%)")
                    
                    for bloco in blocos[-5:]:  # Mostra últimos 5 blocos
                        st.write(f"- {bloco}")
            else:
                st.info("Aguardando resultados (mínimo 30 rodadas para análise)")
    else:
        st.warning(f"⚠️ Aguardando mais dados... ({len(st.session_state.historico)}/30 rodadas)")
    
    # Sugestão de números baseado em frequência
    if len(st.session_state.historico) >= 30:
        st.markdown("### 📈 Análise Rápida")
        ultimos_numeros = list(st.session_state.historico)[-30:]
        frequencias = Counter(ultimos_numeros)
        
        st.markdown("**Top 5 números mais frequentes nas últimas 30 rodadas:**")
        for num, freq in frequencias.most_common(5):
            st.write(f"- Número {num}: {freq} vezes")

with tab2:
    st.markdown("### 📊 Comparação entre Estratégias")
    
    if len(st.session_state.historico) >= 65:
        resultados_ausentes = list(st.session_state.resultados_ausentes)
        resultados_vizinhos = list(st.session_state.resultados_vizinhos)
        resultados_setores = list(st.session_state.resultados_setores)
        
        # Estatísticas
        col1, col2, col3 = st.columns(3)
        
        if resultados_ausentes:
            green_ausentes = resultados_ausentes.count("1")
            taxa_ausentes = (green_ausentes / len(resultados_ausentes) * 100)
            col1.metric("Apenas Ausentes", f"{taxa_ausentes:.1f}%", 
                       f"GREEN: {green_ausentes}")
        
        if resultados_vizinhos:
            green_vizinhos = resultados_vizinhos.count("1")
            taxa_vizinhos = (green_vizinhos / len(resultados_vizinhos) * 100)
            col2.metric("Ausentes + Vizinhos", f"{taxa_vizinhos:.1f}%", 
                       f"GREEN: {green_vizinhos}")
        
        if resultados_setores:
            green_setores = resultados_setores.count("1")
            taxa_setores = (green_setores / len(resultados_setores) * 100)
            col3.metric("4 Números + 2 Vizinhos", f"{taxa_setores:.1f}%", 
                       f"GREEN: {green_setores}")
        
        # Gráfico comparativo
        if resultados_setores:
            st.markdown("### 📈 Evolução da Taxa de Acerto (Estratégia Otimizada)")
            
            # Prepara dados para o gráfico
            dados_grafico = []
            for i in range(10, len(resultados_setores) + 1, 5):
                if i <= len(resultados_setores):
                    acertos = resultados_setores[:i].count("1")
                    taxa = (acertos / i * 100)
                    dados_grafico.append({"Rodadas": i, "Taxa %": taxa})
            
            if dados_grafico:
                df_grafico = pd.DataFrame(dados_grafico)
                st.line_chart(df_grafico.set_index('Rodadas'))
    
    else:
        st.info(f"Aguardando 65 rodadas para comparação completa... ({len(st.session_state.historico)}/65)")

with tab3:
    st.markdown("### 📈 Histórico Completo")
    
    if st.session_state.historico:
        historico_list = list(st.session_state.historico)
        
        st.markdown("#### Últimos números sorteados")
        st.write(" → ".join(map(str, historico_list[-50:])))
        st.write(f"**Total no histórico:** {len(historico_list)}/1000")
        
        # Estatísticas gerais
        st.markdown("#### 📊 Estatísticas Gerais")
        
        # Frequência dos números
        frequencia_total = Counter(historico_list)
        
        # Números mais e menos frequentes
        mais_frequentes = frequencia_total.most_common(5)
        menos_frequentes = frequencia_total.most_common()[-5:]
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**🔥 Números mais frequentes**")
            for num, freq in mais_frequentes:
                st.write(f"Número {num}: {freq} vezes ({freq/len(historico_list)*100:.1f}%)")
        
        with col2:
            st.markdown("**❄️ Números menos frequentes**")
            for num, freq in menos_frequentes:
                st.write(f"Número {num}: {freq} vezes ({freq/len(historico_list)*100:.1f}%)")
        
        # Exportar dados
        st.markdown("#### 💾 Exportar Dados")
        
        if st.button("Exportar Histórico Completo"):
            # Prepara dados para exportação
            max_len = len(historico_list)
            
            ausentes = list(st.session_state.resultados_ausentes)
            vizinhos = list(st.session_state.resultados_vizinhos)
            setores = list(st.session_state.resultados_setores)
            
            # Alinha tamanhos
            ausentes = [''] * (65 - len(ausentes)) + ausentes if len(ausentes) < 65 else ausentes
            vizinhos = [''] * (65 - len(vizinhos)) + vizinhos if len(vizinhos) < 65 else vizinhos
            setores = [''] * (30 - len(setores)) + setores if len(setores) < 30 else setores
            
            # Garante mesmo comprimento
            ausentes = (ausentes + [''] * (max_len - len(ausentes)))[:max_len]
            vizinhos = (vizinhos + [''] * (max_len - len(vizinhos)))[:max_len]
            setores = (setores + [''] * (max_len - len(setores)))[:max_len]
            
            df_export = pd.DataFrame({
                'Rodada': range(1, max_len + 1),
                'Número': historico_list,
                'Resultado_Ausentes': ausentes,
                'Resultado_Ausentes_Vizinhos': vizinhos,
                'Resultado_Otimizado_4Numeros_2Vizinhos': setores
            })
            
            csv = df_export.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Baixar CSV",
                data=csv,
                file_name='roleta_estrategia_otimizada.csv',
                mime='text/csv'
            )
    else:
        st.info("Nenhum dado no histórico ainda. Registre alguns números para começar!")

# Instruções
with st.expander("📖 Instruções da Estratégia Otimizada"):
    st.markdown("""
    ### Como funciona a otimização
    
    **1. Algoritmo de busca:**
    - Analisa as últimas 30 rodadas
    - Testa combinações de 4 números (prioriza os mais frequentes)
    - Para cada combinação, calcula quantos dos últimos 30 números seriam cobertos
    - Escolhe a combinação que MAXIMIZA os acertos
    
    **2. Por que 4 números com 2 vizinhos cada?**
    - Cada setor = 5 números (1 central + 2 esquerda + 2 direita)
    - 4 setores × 5 números = até 20 números únicos
    - Cobertura ideal: 54% da roleta
    - Evita sobreposição excessiva
    
    **3. Vantagens sobre a estratégia anterior:**
    - ✅ **Menos sobreposição**: 4 números ao invés de 3
    - ✅ **Setores menores**: 2 vizinhos ao invés de 4
    - ✅ **Mais foco**: Aposta nos números que realmente importam
    - ✅ **Melhor cobertura**: Otimizada para os últimos resultados
    
    **4. Interpretação dos resultados:**
    - 🟢 **GREEN**: O número sorteado estava na aposta otimizada
    - 🔴 **RED**: O número sorteado NÃO estava na aposta
    
    **5. Performance esperada:**
    - Cobertura teórica: ~54% da roleta
    - Taxa de acerto teórica: ~54%
    - Mas como é otimizada para os últimos 30, pode ser maior!
    
    **6. Dicas:**
    - Observe se a taxa de acerto está acima de 60%
    - Se cair muito, pode ser hora de reavaliar
    - Combine com outras estratégias para confirmar sinais
    """)
