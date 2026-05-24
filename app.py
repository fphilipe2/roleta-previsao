import streamlit as st
import pandas as pd
from collections import deque
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

def obter_vizinhos_laterais(numero, quantidade=4):
    """Retorna N vizinhos de cada lado na roleta"""
    if numero not in posicao_roleta:
        return []
    
    pos = posicao_roleta[numero]
    total_numeros = len(ordem_roleta)
    
    vizinhos = []
    # Vizinhos à esquerda (sentido horário)
    for i in range(1, quantidade + 1):
        vizinhos.append(ordem_roleta[(pos - i) % total_numeros])
    # Vizinhos à direita (sentido anti-horário)
    for i in range(1, quantidade + 1):
        vizinhos.append(ordem_roleta[(pos + i) % total_numeros])
    
    return vizinhos

def encontrar_setores_quentes(ultimas_rodadas=30):
    """Encontra os 3 números mais frequentes e seus setores"""
    if len(st.session_state.historico) < ultimas_rodadas:
        return None, None, None
    
    # Pega as últimas X rodadas
    ultimos_numeros = list(st.session_state.historico)[-ultimas_rodadas:]
    
    # Conta frequência de cada número
    frequencias = {}
    for numero in ultimos_numeros:
        frequencias[numero] = frequencias.get(numero, 0) + 1
    
    # Ordena por frequência (mais frequentes primeiro)
    numeros_ordenados = sorted(frequencias.items(), key=lambda x: x[1], reverse=True)
    
    # Pega os 3 números mais frequentes (ou menos se não houver)
    top_3 = [num for num, freq in numeros_ordenados[:3]]
    
    # Para cada número, pega seus 4 vizinhos de cada lado
    setores = []
    todos_numeros_aposta = set()
    
    for numero in top_3:
        vizinhos = obter_vizinhos_laterais(numero, quantidade=4)
        setor = [numero] + vizinhos
        setores.append(sorted(setor))
        todos_numeros_aposta.update(setor)
    
    return top_3, setores, sorted(list(todos_numeros_aposta))

def calcular_cobertura_setores(apostas):
    """Calcula quantos números dos últimos 30 seriam cobertos pela aposta"""
    if len(st.session_state.historico) < 30:
        return 0, 0
    
    ultimos_numeros = list(st.session_state.historico)[-30:]
    acertos = sum(1 for num in ultimos_numeros if num in apostas)
    return acertos, len(ultimos_numeros)

def registrar_numero_setores(numero):
    """Registra número e calcula resultado da estratégia de setores"""
    historico_list = list(st.session_state.historico)
    
    # Estratégia de setores quentes (usa últimas 30 rodadas para definir aposta)
    if len(historico_list) >= 30:
        # Usa as últimas 30 rodadas (excluindo o número atual) para definir os setores
        ultimos_30_anteriores = historico_list[-31:-1] if len(historico_list) > 30 else historico_list[-30:]
        
        # Salva histórico temporário para análise
        temp_historico = st.session_state.historico.copy()
        # Remove o último número se já foi adicionado
        if len(temp_historico) > 0:
            ultimo = temp_historico.pop()
        
        # Analisa setores quentes baseado nas 30 anteriores
        top_3, setores, apostas_setores = encontrar_setores_quentes(30)
        
        if apostas_setores:
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
        
        # Linha 2: Ausentes + vizinhos
        vizinhos_atrasados = obter_vizinhos_laterais_setor(numeros_atrasados)
        apostas_vizinhos = sorted(list(set(numeros_atrasados) | set(vizinhos_atradados)))
        
        if numero in apostas_vizinhos:
            st.session_state.resultados_vizinhos.append("1")
        else:
            st.session_state.resultados_vizinhos.append("X")
    
    st.session_state.historico.append(numero)

def obter_vizinhos_laterais_setor(numeros):
    """Versão para múltiplos números - 1 vizinho de cada lado"""
    todos_vizinhos = set()
    for numero in numeros:
        if numero in posicao_roleta:
            pos = posicao_roleta[numero]
            total = len(ordem_roleta)
            # Apenas 1 vizinho de cada lado para manter a estratégia original
            todos_vizinhos.add(ordem_roleta[(pos - 1) % total])
            todos_vizinhos.add(ordem_roleta[(pos + 1) % total])
    return sorted(list(todos_vizinhos))

# Interface
st.title("🎯 Estratégia de Setores Quentes - Roleta Europeia")

# Abas para diferentes estratégias
tab1, tab2, tab3 = st.tabs(["🔥 Setores Quentes", "📊 Comparação Estratégias", "📈 Histórico"])

with tab1:
    st.markdown("""
    ### 🎲 Estratégia: Setores Mais Quentes
    
    **Como funciona:**
    1. Analisa as últimas **30 rodadas**
    2. Identifica os **3 números que mais saíram** (os mais quentes)
    3. Para cada número quente, aposta nele + **4 vizinhos de cada lado** na roleta
    4. Total: 3 números × 9 números (1 central + 4 esquerda + 4 direita) = **27 números**
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
        top_3, setores, apostas_setores = encontrar_setores_quentes(30)
        
        if top_3 and setores:
            st.markdown("### 🔥 Números Mais Quentes (últimas 30 rodadas)")
            
            # Mostra frequências
            ultimos_numeros = list(st.session_state.historico)[-30:]
            frequencias = {}
            for num in ultimos_numeros:
                frequencias[num] = frequencias.get(num, 0) + 1
            
            col1, col2, col3 = st.columns(3)
            for idx, (col, numero) in enumerate(zip([col1, col2, col3], top_3)):
                freq = frequencias.get(numero, 0)
                col.metric(f"#{idx+1} Número Quente", numero, f"{freq} vezes")
            
            st.markdown("### 🎯 Setores para Apostar (Número + 4 vizinhos cada lado)")
            
            for idx, (numero, setor) in enumerate(zip(top_3, setores)):
                with st.expander(f"Setor {idx+1}: Número {numero} e seus vizinhos"):
                    st.write(f"**Número central:** {numero}")
                    st.write(f"**Vizinhos:** {setor[1:]}")
                    st.write(f"**Total de números neste setor:** {len(setor)}")
            
            st.markdown("### ✅ APOSTA FINAL")
            st.write(f"**Números para apostar:** {apostas_setores}")
            st.write(f"**Total de números:** {len(apostas_setores)}")
            st.write(f"**Cobertura da roleta:** {(len(apostas_setores)/37*100):.1f}%")
            
            # Cobertura dos últimos 30
            cobertura, total = calcular_cobertura_setores(apostas_setores)
            st.markdown("### 📊 Cobertura dos Últimos 30 Números")
            st.write(f"**Acertos potenciais:** {cobertura} de {total} números")
            st.write(f"**Porcentagem de cobertura:** {(cobertura/total*100):.1f}%")
            
            # Visualização da roleta
            st.markdown("### 🎨 Visualização da Roleta")
            
            # Cria grid da roleta
            roleta_grid = []
            for i in range(0, 37, 6):
                linha = []
                for j in range(6):
                    num = i + j
                    if num <= 36:
                        if num in apostas_setores:
                            linha.append(f"🟢 {num:2d}")
                        else:
                            linha.append(f"⚪ {num:2d}")
                roleta_grid.append(" | ".join(linha))
            
            st.code("\n".join(roleta_grid))
            
            # Resultados da estratégia de setores
            st.markdown("### 🎲 Resultados - Estratégia de Setores")
            if st.session_state.resultados_setores:
                resultados_setores = list(st.session_state.resultados_setores)
                resultados_display = " ".join(resultados_setores[-50:])
                st.code(resultados_display)
                
                total_green = resultados_setores.count("1")
                total_red = resultados_setores.count("X")
                taxa_acerto = (total_green / len(resultados_setores) * 100) if len(resultados_setores) > 0 else 0
                
                col1, col2, col3 = st.columns(3)
                col1.metric("GREEN", total_green)
                col2.metric("RED", total_red)
                col3.metric("Taxa de Acerto", f"{taxa_acerto:.1f}%")
                
                # Sequência atual
                st.write(f"**Últimos 10 resultados:** {resultados_setores[-10:]}")
                st.write(f"**Sequência atual:** {''.join(resultados_setores[-5:])}")
            else:
                st.info("Aguardando resultados (mínimo 30 rodadas para análise)")
    else:
        st.warning(f"⚠️ Aguardando mais dados... ({len(st.session_state.historico)}/30 rodadas)")

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
            col1.metric("Apenas Ausentes (65 rodadas)", f"{taxa_ausentes:.1f}%", 
                       f"GREEN: {green_ausentes}")
        
        if resultados_vizinhos:
            green_vizinhos = resultados_vizinhos.count("1")
            taxa_vizinhos = (green_vizinhos / len(resultados_vizinhos) * 100)
            col2.metric("Ausentes + Vizinhos", f"{taxa_vizinhos:.1f}%", 
                       f"GREEN: {green_vizinhos}")
        
        if resultados_setores:
            green_setores = resultados_setores.count("1")
            taxa_setores = (green_setores / len(resultados_setores) * 100)
            col3.metric("Setores Quentes (30 rodadas)", f"{taxa_setores:.1f}%", 
                       f"GREEN: {green_setores}")
        
        # Gráfico comparativo
        st.markdown("### 📈 Evolução das Taxas de Acerto")
        
        # Prepara dados para o gráfico
        dados_grafico = []
        max_len = max(len(resultados_ausentes), len(resultados_vizinhos), len(resultados_setores))
        
        for i in range(10, max_len + 1, 10):
            ponto = {"Rodada": i}
            
            if i <= len(resultados_ausentes):
                acertos = resultados_ausentes[:i].count("1")
                ponto["Ausentes"] = (acertos / i * 100)
            
            if i <= len(resultados_vizinhos):
                acertos = resultados_vizinhos[:i].count("1")
                ponto["+ Vizinhos"] = (acertos / i * 100)
            
            if i <= len(resultados_setores):
                acertos = resultados_setores[:i].count("1")
                ponto["Setores"] = (acertos / i * 100)
            
            dados_grafico.append(ponto)
        
        if dados_grafico:
            df_grafico = pd.DataFrame(dados_grafico)
            st.line_chart(df_grafico.set_index('Rodada'))
    
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
        from collections import Counter
        frequencia_total = Counter(historico_list)
        
        # Números mais e menos frequentes
        mais_frequentes = frequencia_total.most_common(5)
        menos_frequentes = frequencia_total.most_common()[-5:]
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**🔥 Números mais frequentes (geral)**")
            for num, freq in mais_frequentes:
                st.write(f"Número {num}: {freq} vezes")
        
        with col2:
            st.markdown("**❄️ Números menos frequentes (geral)**")
            for num, freq in menos_frequentes:
                st.write(f"Número {num}: {freq} vezes")
        
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
                'Resultado_Setores_Quentes': setores
            })
            
            csv = df_export.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Baixar CSV",
                data=csv,
                file_name='roleta_todas_estrategias.csv',
                mime='text/csv'
            )
    else:
        st.info("Nenhum dado no histórico ainda. Registre alguns números para começar!")

# Instruções
with st.expander("📖 Instruções Detalhadas"):
    st.markdown("""
    ### Como usar o BOT de Setores Quentes
    
    **1. Estratégia de Setores Quentes:**
    - Analisa automaticamente as últimas 30 rodadas
    - Identifica os 3 números que mais saíram
    - Para cada número, aposta no número + 4 vizinhos de cada lado na roleta física
    - Ideal para aproveitar tendências de curto prazo
    
    **2. Por que 4 vizinhos de cada lado?**
    - Cobre um setor de 9 números por número quente
    - Total de 27 números (73% da roleta)
    - Alta probabilidade de acerto (teórica ~73%)
    
    **3. Como interpretar os resultados:**
    - 🟢 **GREEN (1)**: Número sorteado estava na aposta
    - 🔴 **RED (X)**: Número sorteado NÃO estava na aposta
    
    **4. Dicas de uso:**
    - Use para identificar tendências de curto prazo
    - Combine com outras estratégias (ausentes) para confirmar sinais
    - Acompanhe a taxa de acerto ao longo do tempo
    - Exporte os dados para análise externa
    
    **5. Limitações:**
    - Precisa de no mínimo 30 rodadas para começar
    - Estratégia de curto prazo (últimas 30 rodadas)
    - Resultados passados não garantem resultados futuros
    """)
