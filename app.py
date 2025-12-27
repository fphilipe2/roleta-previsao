import streamlit as st
import pandas as pd
from collections import deque

# Configuração inicial
if 'historico' not in st.session_state:
    st.session_state.historico = deque(maxlen=1000)
if 'resultados' not in st.session_state:
    st.session_state.resultados = deque(maxlen=1000)  # Linha 1: Apenas ausentes
if 'resultados_vizinhos' not in st.session_state:
    st.session_state.resultados_vizinhos = deque(maxlen=1000)  # Linha 2: Ausentes + vizinhos

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

def obter_numeros_nao_sorteados(ultimas_rodadas=65):
    """Analisa os números que NÃO saíram nas últimas X rodadas"""
    if len(st.session_state.historico) < ultimas_rodadas:
        return []
    
    ultimos_numeros = list(st.session_state.historico)[-ultimas_rodadas:]
    todos_numeros = set(range(0, 37))
    numeros_sorteados = set(ultimos_numeros)
    numeros_nao_sorteados = todos_numeros - numeros_sorteados
    
    return sorted(list(numeros_nao_sorteados))

def registrar_numero(numero):
    historico_list = list(st.session_state.historico)
    
    # Só valida se tivermos pelo menos 65 números no histórico
    if len(historico_list) >= 65:
        # Pega os 65 números anteriores ao atual
        ultimos_65_anteriores = historico_list[-65:]  # Inclui o número atual no final
        
        # LINHA 1: Validação APENAS números atrasados
        numeros_sorteados_65 = set(ultimos_65_anteriores)
        todos_numeros = set(range(0, 37))
        numeros_atrasados = sorted(list(todos_numeros - numeros_sorteados_65))
        
        if numero in numeros_atrasados:
            st.session_state.resultados.append("1")  # GREEN
        else:
            st.session_state.resultados.append("X")  # RED
        
        # LINHA 2: Validação números atrasados + vizinhos
        vizinhos_atrasados = obter_vizinhos_roleta(numeros_atrasados)
        apostas_vizinhos = sorted(list(set(numeros_atrasados) | set(vizinhos_atrasados)))
        
        if numero in apostas_vizinhos:
            st.session_state.resultados_vizinhos.append("1")  # GREEN
        else:
            st.session_state.resultados_vizinhos.append("X")  # RED
    
    # Adiciona o novo número ao histórico
    st.session_state.historico.append(numero)

def analisar_transicoes():
    """Analisa quantos REDs na linha 1 para obter um GREEN na linha 2"""
    resultados1 = list(st.session_state.resultados)
    resultados2 = list(st.session_state.resultados_vizinhos)
    
    if len(resultados1) != len(resultados2) or len(resultados1) == 0:
        return None
    
    transicoes = []
    contador_reds = 0
    
    for i in range(len(resultados1)):
        if resultados1[i] == "X":  # RED na linha 1
            contador_reds += 1
        else:  # GREEN na linha 1
            if i > 0 and resultados1[i-1] == "X":  # Se veio de um RED
                # Verifica o resultado correspondente na linha 2
                if i < len(resultados2):
                    transicoes.append((contador_reds, resultados2[i]))
                contador_reds = 0
    
    return transicoes

# Interface
st.title("🎯 Comparação de Estratégias - Números Atrasados")

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
            # Limpa os históricos
            st.session_state.historico.clear()
            st.session_state.resultados.clear()
            st.session_state.resultados_vizinhos.clear()
            
            # Adiciona números mantendo o limite de 1000
            for num in dados['Número'].tolist()[-1000:]:
                st.session_state.historico.append(num)
            
            # Processa resultados para números existentes
            historico_list = list(st.session_state.historico)
            for i in range(65, len(historico_list)):
                numero_atual = historico_list[i]
                numeros_anteriores = historico_list[i-65:i]
                
                # LINHA 1: Apenas ausentes
                numeros_sorteados_65 = set(numeros_anteriores)
                todos_numeros = set(range(0, 37))
                numeros_atrasados = sorted(list(todos_numeros - numeros_sorteados_65))
                
                if numero_atual in numeros_atrasados:
                    st.session_state.resultados.append("1")
                else:
                    st.session_state.resultados.append("X")
                
                # LINHA 2: Ausentes + vizinhos
                vizinhos_atrasados = obter_vizinhos_roleta(numeros_atrasados)
                apostas_vizinhos = sorted(list(set(numeros_atrasados) | set(vizinhos_atrasados)))
                
                if numero_atual in apostas_vizinhos:
                    st.session_state.resultados_vizinhos.append("1")
                else:
                    st.session_state.resultados_vizinhos.append("X")
            
            st.success(f"Histórico carregado! {len(historico_list)} registros.")
            st.rerun()
        else:
            st.error("O arquivo precisa ter a coluna 'Número'")
    except Exception as e:
        st.error(f"Erro ao ler arquivo: {e}")

# Exibição da estratégia
if st.session_state.historico:
    historico_list = list(st.session_state.historico)
    ultimo_numero = historico_list[-1]
    
    st.subheader(f"Último número sorteado: {ultimo_numero}")
    
    # ESTRATÉGIA: Números Atrasados
    st.markdown("### 🎯 Estratégia: Números Atrasados (65 rodadas)")
    
    numeros_atrasados = obter_numeros_nao_sorteados(65)
    
    if numeros_atrasados:
        # Cálculo dos vizinhos
        vizinhos_atrasados = obter_vizinhos_roleta(numeros_atrasados)
        apostas_vizinhos = sorted(list(set(numeros_atrasados) | set(vizinhos_atrasados)))
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**📊 Linha 1: Apenas Ausentes**")
            st.write(f"Números: {numeros_atrasados}")
            st.write(f"Total: {len(numeros_atrasados)} números")
            st.write(f"Cobertura: {(len(numeros_atrasados)/37*100):.1f}%")
        
        with col2:
            st.markdown("**📊 Linha 2: Ausentes + Vizinhos**")
            st.write(f"Números: {apostas_vizinhos}")
            st.write(f"Total: {len(apostas_vizinhos)} números")
            st.write(f"Cobertura: {(len(apostas_vizinhos)/37*100):.1f}%")
        
        # Análise comparativa
        st.markdown("### 🔍 Análise Comparativa das Estratégias")
        
        resultados1 = list(st.session_state.resultados)
        resultados2 = list(st.session_state.resultados_vizinhos)
        
        if resultados1 and resultados2:
            # Estatísticas básicas
            total1 = len(resultados1)
            green1 = resultados1.count("1")
            red1 = resultados1.count("X")
            taxa1 = (green1 / total1 * 100) if total1 > 0 else 0
            
            total2 = len(resultados2)
            green2 = resultados2.count("1")
            red2 = resultados2.count("X")
            taxa2 = (green2 / total2 * 100) if total2 > 0 else 0
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Linha 1 (Ausentes)", f"{taxa1:.1f}%", 
                         f"GREEN: {green1} | RED: {red1}")
            with col2:
                st.metric("Linha 2 (+Vizinhos)", f"{taxa2:.1f}%", 
                         f"GREEN: {green2} | RED: {red2}")
            with col3:
                diferenca = taxa2 - taxa1
                st.metric("Diferença", f"{diferenca:.1f}%")
            
            # ANÁLISE DE TRANSIÇÕES
            st.markdown("### 📈 Análise: RED na Linha 1 → GREEN na Linha 2")
            
            transicoes = analisar_transicoes()
            if transicoes:
                # Conta quantas vezes cada cenário ocorreu
                verde_apos_red = sum(1 for _, resultado2 in transicoes if resultado2 == "1")
                total_transicoes = len(transicoes)
                
                if total_transicoes > 0:
                    porcentagem = (verde_apos_red / total_transicoes * 100)
                    
                    st.write(f"**Quando a Linha 1 dá RED, a Linha 2 dá GREEN em:**")
                    st.write(f"**{verde_apos_red} de {total_transicoes} vezes ({porcentagem:.1f}%)**")
                    
                    # Análise por quantidade de REDs consecutivos
                    st.markdown("**Distribuição por REDs consecutivos:**")
                    
                    distribuicao = {}
                    for reds_count, resultado2 in transicoes:
                        if reds_count not in distribuicao:
                            distribuicao[reds_count] = {"total": 0, "green": 0}
                        distribuicao[reds_count]["total"] += 1
                        if resultado2 == "1":
                            distribuicao[reds_count]["green"] += 1
                    
                    # Ordena e exibe
                    for reds_count in sorted(distribuicao.keys()):
                        data = distribuicao[reds_count]
                        if data["total"] > 0:
                            perc = (data["green"] / data["total"] * 100)
                            st.write(f"- Após **{reds_count} RED(s)** consecutivo(s): {data['green']}/{data['total']} ({perc:.1f}%)")
                    
                    # Média de REDs necessários
                    if verde_apos_red > 0:
                        reds_necessarios = [reds for reds, resultado2 in transicoes if resultado2 == "1"]
                        media_reds = sum(reds_necessarios) / len(reds_necessarios)
                        st.write(f"**Média de REDs na Linha 1 antes de GREEN na Linha 2: {media_reds:.1f}**")
                else:
                    st.write("Aguardando mais dados para análise...")
            else:
                st.write("Aguardando dados para análise de transições...")
            
            # Exibição dos resultados lado a lado
            st.markdown("### 🎲 Resultados das Estratégias")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Linha 1: Apenas Ausentes**")
                resultados_display1 = " ".join(resultados1[-50:])
                st.code(resultados_display1)
                st.write(f"Sequência atual: {''.join(resultados1[-5:])}")
            
            with col2:
                st.markdown("**Linha 2: Ausentes + Vizinhos**")
                resultados_display2 = " ".join(resultados2[-50:])
                st.code(resultados_display2)
                st.write(f"Sequência atual: {''.join(resultados2[-5:])}")
            
            # Comparação direta
            st.markdown("**Comparação direta (últimos 20):**")
            comparacao = []
            for i in range(min(20, len(resultados1), len(resultados2))):
                idx = -20 + i
                comparacao.append(f"{resultados1[idx]}|{resultados2[idx]}")
            
            st.write(" → ".join(comparacao))
            st.caption("Formato: Linha1|Linha2 (ex: X|1 significa RED na Linha 1, GREEN na Linha 2)")
            
        else:
            st.write("Aguardando mais resultados para análise...")
    else:
        if len(historico_list) < 65:
            st.write(f"⚠️ Aguardando mais dados... ({len(historico_list)}/65 rodadas)")
        else:
            st.write("🎉 Todos os números saíram nas últimas 65 rodadas!")
    
    # Histórico recente
    st.markdown("---")
    st.subheader("📈 Últimos números sorteados")
    st.write(" → ".join(map(str, historico_list[-20:])))
    st.write(f"Total no histórico: {len(historico_list)}/1000")

# Exportar histórico
if st.button("📥 Exportar Histórico"):
    if st.session_state.historico:
        historico_list = list(st.session_state.historico)
        resultados1 = list(st.session_state.resultados)
        resultados2 = list(st.session_state.resultados_vizinhos)
        
        # Preenche resultados para alinhar
        resultados1_completos = [''] * 65 + resultados1
        resultados2_completos = [''] * 65 + resultados2
        
        # Garante mesmo comprimento
        max_len = len(historico_list)
        resultados1_completos = resultados1_completos[:max_len]
        resultados2_completos = resultados2_completos[:max_len]
        
        if len(resultados1_completos) < max_len:
            resultados1_completos = resultados1_completos + [''] * (max_len - len(resultados1_completos))
        if len(resultados2_completos) < max_len:
            resultados2_completos = resultados2_completos + [''] * (max_len - len(resultados2_completos))
        
        df = pd.DataFrame({
            'Número': historico_list,
            'Resultado_Apenas_Ausentes': resultados1_completos,
            'Resultado_Ausentes_Vizinhos': resultados2_completos
        })
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Baixar CSV",
            data=csv,
            file_name='comparacao_estrategias.csv',
            mime='text/csv'
        )
    else:
        st.warning("Nenhum dado para exportar")

# Instruções
st.markdown("---")
st.markdown("### 📋 Instruções:")
st.markdown("""
1. **Duas estratégias comparadas:**
   - **Linha 1**: Aposta apenas nos números **AUSENTES** (não sorteados nas últimas 65 rodadas)
   - **Linha 2**: Aposta nos números **AUSENTES + seus VIZINHOS** na roleta

2. **Análise principal:** 
   - Quantas vezes, em média, dá RED na Linha 1 até dar GREEN na Linha 2
   - Qual a porcentagem de vezes que a Linha 2 "salva" um RED da Linha 1

3. **Resultados:**
   - **1**: GREEN (número sorteado está entre as apostas)
   - **X**: RED (número sorteado NÃO está entre as apostas)

4. **Interpretação:**
   - Se a porcentagem de "RED→GREEN" for alta, pode valer a pena apostar nos vizinhos
   - Se for baixa, talvez seja melhor apostar apenas nos ausentes
""")
