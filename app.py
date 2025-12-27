import streamlit as st
import pandas as pd
from collections import deque

# Configuração inicial
if 'historico' not in st.session_state:
    st.session_state.historico = deque(maxlen=1000)  # Mantém últimos 1000 resultados
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

def obter_numeros_nao_sorteados(ultimas_rodadas=65):
    """Analisa os números que NÃO saíram nas últimas X rodadas"""
    if len(st.session_state.historico) < ultimas_rodadas:
        return []  # Não há dados suficientes
    
    # Pega as últimas X rodadas
    ultimos_numeros = list(st.session_state.historico)[-ultimas_rodadas:]
    
    # Todos os números possíveis (0-36)
    todos_numeros = set(range(0, 37))
    
    # Números que saíram nas últimas X rodadas
    numeros_sorteados = set(ultimos_numeros)
    
    # Números que NÃO saíram
    numeros_nao_sorteados = todos_numeros - numeros_sorteados
    
    return sorted(list(numeros_nao_sorteados))

def registrar_numero(numero):
    # Primeiro verifica o resultado da aposta anterior (se houver histórico suficiente)
    if len(st.session_state.historico) >= 65:
        # Obtém os números atrasados das últimas 65 rodadas (excluindo o último número)
        ultimos_65_anteriores = list(st.session_state.historico)[-66:-1]  # Pega 65 números anteriores ao último
        
        # Verifica se temos pelo menos 65 números
        if len(ultimos_65_anteriores) >= 65:
            # Pega exatamente os últimos 65 números antes do último
            ultimos_65_anteriores = ultimos_65_anteriores[-65:]
            
            # Calcula números não sorteados nas últimas 65 rodadas anteriores
            numeros_sorteados_65 = set(ultimos_65_anteriores)
            todos_numeros = set(range(0, 37))
            numeros_atrasados = sorted(list(todos_numeros - numeros_sorteados_65))
            
            # VERIFICAÇÃO MODIFICADA: 
            # Green apenas se o número sorteado for um dos números atrasados (não seus vizinhos)
            if numero in numeros_atrasados:
                st.session_state.resultados.append("1")  # GREEN
            else:
                st.session_state.resultados.append("X")  # RED
    
    # Adiciona o novo número ao histórico
    st.session_state.historico.append(numero)

# Interface
st.title("🎯 Estratégia de Apostas - Números Atrasados")

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
            # Limpa o histórico atual
            st.session_state.historico.clear()
            # Adiciona os números mantendo o limite de 1000
            for num in dados['Número'].tolist()[-1000:]:
                st.session_state.historico.append(num)
            st.success(f"Histórico carregado! {len(st.session_state.historico)} registros.")
            
            # Processa resultados para números existentes
            st.session_state.resultados.clear()
            for i in range(65, len(st.session_state.historico)):
                numero_atual = list(st.session_state.historico)[i]
                numeros_anteriores = list(st.session_state.historico)[i-65:i]
                
                # Calcula números não sorteados nos últimos 65
                numeros_sorteados_65 = set(numeros_anteriores)
                todos_numeros = set(range(0, 37))
                numeros_atrasados = sorted(list(todos_numeros - numeros_sorteados_65))
                
                # Verifica se o número atual está entre os atrasados
                if numero_atual in numeros_atrasados:
                    st.session_state.resultados.append("1")  # GREEN
                else:
                    st.session_state.resultados.append("X")  # RED
                    
            st.rerun()
        else:
            st.error("O arquivo precisa ter a coluna 'Número'")
    except Exception as e:
        st.error(f"Erro ao ler arquivo: {e}")

# Exibição da estratégia
if st.session_state.historico:
    ultimo_numero = list(st.session_state.historico)[-1] if st.session_state.historico else None
    
    st.subheader(f"Último número sorteado: {ultimo_numero}")
    
    # ESTRATÉGIA: Números Atrasados
    st.markdown("### 🎯 Estratégia: Números Atrasados (65 rodadas)")
    
    # Analisa números não sorteados nas últimas 65 rodadas
    numeros_atrasados = obter_numeros_nao_sorteados(65)
    
    if numeros_atrasados:
        st.markdown(f"**Números que NÃO saíram nas últimas 65 rodadas ({len(numeros_atrasados)} números):**")
        st.write(f"**{numeros_atrasados}**")
        
        # Calcula vizinhos dos números atrasados (apenas para exibição)
        vizinhos_atrasados = obter_vizinhos_roleta(numeros_atrasados)
        st.markdown("**Vizinhos dos números atrasados:**")
        st.write(f"**{vizinhos_atrasados}**")
        
        # NOTA IMPORTANTE: A aposta é APENAS nos números atrasados, não nos vizinhos
        st.markdown("**⚠️ APOSTA APENAS NOS NÚMEROS ATRASADOS (não nos vizinhos)**")
        st.write(f"**Números para apostar: {numeros_atrasados}**")
        
        # Estatísticas
        st.markdown("**📊 Estatísticas:**")
        st.write(f"- Total de números apostados: {len(numeros_atrasados)}")
        st.write(f"- Cobertura da roleta: {(len(numeros_atrasados)/37*100):.1f}%")
        
        # Probabilidade
        if len(numeros_atrasados) > 0:
            prob_ganhar = (len(numeros_atrasados) / 37) * 100
            st.write(f"- Probabilidade teórica de acerto: {prob_ganhar:.1f}%")
        
    else:
        if len(st.session_state.historico) < 65:
            st.write(f"⚠️ Aguardando mais dados... ({len(st.session_state.historico)}/65 rodadas)")
        else:
            st.write("🎉 Todos os números saíram nas últimas 65 rodadas!")
    
    # Histórico recente
    st.subheader("📈 Últimos números sorteados")
    historico_list = list(st.session_state.historico)
    st.write(" → ".join(map(str, historico_list[-20:])))
    st.write(f"Total no histórico: {len(historico_list)}/1000")
    
    # Resultados das Apostas
    st.subheader("🎲 Resultados das Apostas")
    if st.session_state.resultados:
        resultados_list = list(st.session_state.resultados)
        resultados_display = " ".join(resultados_list[-50:])
        st.write(resultados_display)
        st.write(f"Total de apostas registradas: {len(resultados_list)}")
        
        total_green = resultados_list.count("1")
        total_red = resultados_list.count("X")
        if len(resultados_list) > 0:
            taxa_acerto = (total_green / len(resultados_list)) * 100
            st.write(f"**GREEN: {total_green}** | **RED: {total_red}** | **Taxa de acerto: {taxa_acerto:.1f}%**")
            
            # Estatísticas adicionais
            if resultados_list:
                st.write(f"**Últimos 5 resultados:** {resultados_list[-5:]}")
                
                # Sequência atual
                if resultados_list[-5:]:
                    seq = "".join(resultados_list[-5:])
                    st.write(f"**Sequência atual:** {seq}")
    else:
        st.write("Aguardando próximos resultados... (mínimo 65 rodadas para análise)")

# Exportar histórico
if st.button("📥 Exportar Histórico"):
    if st.session_state.historico:
        resultados_export = list(st.session_state.resultados)
        
        # Cria DataFrame com histórico e resultados
        historico_list = list(st.session_state.historico)
        
        # Preenche resultados para alinhar com o histórico
        resultados_completos = [''] * 65 + resultados_export
        
        # Garante que temos o mesmo comprimento
        if len(resultados_completos) > len(historico_list):
            resultados_completos = resultados_completos[:len(historico_list)]
        elif len(resultados_completos) < len(historico_list):
            resultados_completos = resultados_completos + [''] * (len(historico_list) - len(resultados_completos))
        
        df = pd.DataFrame({
            'Número': historico_list,
            'Resultado_Aposta': resultados_completos
        })
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Baixar CSV",
            data=csv,
            file_name='historico_roleta_atrasados.csv',
            mime='text/csv'
        )
    else:
        st.warning("Nenhum dado para exportar")

# Instruções
st.markdown("---")
st.markdown("### 📋 Instruções:")
st.markdown("""
1. **Registre os números sorteados** manualmente ou carregue um arquivo CSV
2. **Estratégia**: Apostar apenas nos números que **NÃO saíram** nas últimas **65 rodadas**
3. **Regra de validação**: 
   - ✅ **GREEN (1)**: Se o número sorteado estiver entre os números atrasados
   - ❌ **RED (X)**: Se o número sorteado NÃO estiver entre os números atrasados
4. **Vizinhos**: São apenas para referência visual, NÃO fazem parte da aposta
5. **Histórico**: Mantém os últimos 1000 resultados
""")
