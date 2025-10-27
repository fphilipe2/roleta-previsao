import streamlit as st
import pandas as pd
from collections import deque

# Configuração inicial
if 'historico' not in st.session_state:
    st.session_state.historico = []
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

# Mapa de simétricos (baseado nos seus exemplos)
simetricos_map = {
    0: 10, 1: 21, 2: 20, 3: 8, 4: 33, 5: 32, 6: 22, 7: 36, 8: 3, 9: 17,
    10: 0, 11: 12, 12: 11, 13: 7, 14: 25, 15: 24, 16: 19, 17: 9, 18: 6, 19: 16,
    20: 2, 21: 1, 22: 34, 23: 26, 24: 15, 25: 14, 26: 23, 27: 29, 28: 36, 29: 27,
    30: 35, 31: 25, 32: 5, 33: 4, 34: 9, 35: 30, 36: 28
}

def obter_vizinhos_roleta(numeros):
    """Retorna os vizinhos baseados no layout físico da roleta europeia"""
    todos_vizinhos = set()
    for numero in numeros:
        if numero in vizinhos_map:
            vizinhos = vizinhos_map[numero]
            todos_vizinhos.update(vizinhos)
    return sorted(list(todos_vizinhos))

def obter_simetricos(numeros):
    """Retorna os números simétricos dos números fornecidos"""
    simetricos = set()
    for numero in numeros:
        if numero in simetricos_map:
            simetrico = simetricos_map[numero]
            simetricos.add(simetrico)
    return sorted(list(simetricos))

def obter_numeros_nao_sorteados(ultimas_rodadas=75):
    """Analisa os números que NÃO saíram nas últimas X rodadas"""
    if len(st.session_state.historico) < ultimas_rodadas:
        return []  # Não há dados suficientes
    
    # Pega as últimas X rodadas
    ultimos_numeros = st.session_state.historico[-ultimas_rodadas:]
    
    # Todos os números possíveis (0-36)
    todos_numeros = set(range(0, 37))
    
    # Números que saíram nas últimas X rodadas
    numeros_sorteados = set(ultimos_numeros)
    
    # Números que NÃO saíram
    numeros_nao_sorteados = todos_numeros - numeros_sorteados
    
    return sorted(list(numeros_nao_sorteados))

def verificar_apostas_do_historico():
    """Verifica todas as apostas do histórico carregado"""
    st.session_state.resultados.clear()  # Limpa resultados anteriores
    
    if len(st.session_state.historico) <= 75:
        return  # Não há apostas para verificar
    
    # Para cada número a partir da posição 75, verifica a aposta
    for i in range(75, len(st.session_state.historico)):
        numero_atual = st.session_state.historico[i]
        
        # Pega as últimas 75 rodadas ANTES deste número
        inicio = max(0, i - 75)
        ultimos_75_anteriores = st.session_state.historico[inicio:i]
        
        # Calcula números atrasados
        numeros_sorteados_75 = set(ultimos_75_anteriores)
        todos_numeros = set(range(0, 37))
        numeros_atrasados = sorted(list(todos_numeros - numeros_sorteados_75))
        
        if numeros_atrasados:
            # NOVA ESTRATÉGIA: Números atrasados + Simétricos + Vizinhos de ambos
            simetricos = obter_simetricos(numeros_atrasados)
            
            # Combina números atrasados com seus simétricos
            todos_numeros_estrategia = set(numeros_atrasados) | set(simetricos)
            
            # Calcula vizinhos de todos os números da estratégia
            vizinhos = obter_vizinhos_roleta(list(todos_numeros_estrategia))
            
            # Apostas finais
            apostas_anteriores = sorted(list(todos_numeros_estrategia | set(vizinhos)))
            
            # Verifica resultado
            if numero_atual in apostas_anteriores:
                st.session_state.resultados.append("1")  # GREEN
            else:
                st.session_state.resultados.append("X")  # RED

def registrar_numero(numero):
    # Primeiro verifica o resultado da aposta anterior (se houver histórico suficiente)
    if len(st.session_state.historico) >= 75:
        # Obtém os números atrasados das últimas 75 rodadas (excluindo o último número)
        ultimos_75_anteriores = st.session_state.historico[-76:-1]  # Exclui o último número
        numeros_sorteados_75 = set(ultimos_75_anteriores)
        todos_numeros = set(range(0, 37))
        numeros_atrasados = sorted(list(todos_numeros - numeros_sorteados_75))
        
        # Calcula as apostas para a rodada anterior
        if numeros_atrasados:
            # NOVA ESTRATÉGIA: Números atrasados + Simétricos + Vizinhos de ambos
            simetricos = obter_simetricos(numeros_atrasados)
            
            # Combina números atrasados com seus simétricos
            todos_numeros_estrategia = set(numeros_atrasados) | set(simetricos)
            
            # Calcula vizinhos de todos os números da estratégia
            vizinhos = obter_vizinhos_roleta(list(todos_numeros_estrategia))
            
            # Apostas finais
            apostas_anteriores = sorted(list(todos_numeros_estrategia | set(vizinhos)))
            
            # Verifica se o NOVO número está nas apostas da rodada anterior
            if numero in apostas_anteriores:
                st.session_state.resultados.append("1")  # GREEN
            else:
                st.session_state.resultados.append("X")  # RED
    
    # Adiciona o novo número ao histórico
    st.session_state.historico.append(numero)

# Interface
st.title("🎯 Nova Estratégia - Números Atrasados + Simétricos")

# Controles
col1, col2 = st.columns(2)
with col1:
    novo_numero = st.number_input("Último número sorteado (0-36)", min_value=0, max_value=36)
with col2:
    if st.button("Registrar"):
        registrar_numero(novo_numero)

# Upload de CSV
uploaded_file = st.file_uploader("Carregar histórico (CSV)", type="csv")
if uploaded_file:
    try:
        dados = pd.read_csv(uploaded_file)
        if 'Número' in dados.columns:
            st.session_state.historico = dados['Número'].tolist()
            st.success(f"Histórico carregado! {len(dados)} registros.")
            
            # VERIFICA AUTOMATICAMENTE AS APOSTAS DO HISTÓRICO
            verificar_apostas_do_historico()
            st.success(f"Verificação concluída! {len(st.session_state.resultados)} apostas analisadas.")
            
        else:
            st.error("O arquivo precisa ter a coluna 'Número'")
    except Exception as e:
        st.error(f"Erro ao ler arquivo: {e}")

# Exibição da estratégia
if st.session_state.historico:
    ultimo_numero = st.session_state.historico[-1]
    
    st.subheader(f"Último número sorteado: {ultimo_numero}")
    
    # NOVA ESTRATÉGIA: Números Atrasados + Simétricos
    st.markdown("### 🎯 Nova Estratégia: Números Atrasados + Simétricos")
    
    # Analisa números não sorteados nas últimas 75 rodadas
    numeros_atrasados = obter_numeros_nao_sorteados(75)
    
    if numeros_atrasados:
        st.markdown(f"**Números que NÃO saíram nas últimas 75 rodadas ({len(numeros_atrasados)} números):**")
        st.write(f"**{numeros_atrasados}**")
        
        # Calcula simétricos
        simetricos = obter_simetricos(numeros_atrasados)
        st.markdown("**Simétricos dos números atrasados:**")
        st.write(f"**{simetricos}**")
        
        # Combina números atrasados + simétricos
        todos_numeros_estrategia = sorted(list(set(numeros_atrasados) | set(simetricos)))
        st.markdown("**Números da estratégia (Atrasados + Simétricos):**")
        st.write(f"**{todos_numeros_estrategia}**")
        
        # Calcula vizinhos
        vizinhos = obter_vizinhos_roleta(todos_numeros_estrategia)
        st.markdown("**Vizinhos da estratégia:**")
        st.write(f"**{vizinhos}**")
        
        # Apostas finais (números + vizinhos)
        apostas_finais = sorted(list(set(todos_numeros_estrategia) | set(vizinhos)))
        st.markdown("**Apostas Finais (Números + Simétricos + Vizinhos):**")
        st.write(f"**{apostas_finais}**")
        
        # Estatísticas
        st.markdown("**📊 Estatísticas:**")
        st.write(f"- Números atrasados: {len(numeros_atrasados)}")
        st.write(f"- Simétricos: {len(simetricos)}")
        st.write(f"- Total de números apostados: {len(apostas_finais)}")
        st.write(f"- Cobertura da roleta: {(len(apostas_finais)/37*100):.1f}%")
        
    else:
        if len(st.session_state.historico) < 75:
            st.write(f"⚠️ Aguardando mais dados... ({len(st.session_state.historico)}/75 rodadas)")
        else:
            st.write("🎉 Todos os números saíram nas últimas 75 rodadas!")
    
    # Histórico recente
    st.subheader("📈 Últimos números sorteados")
    st.write(" → ".join(map(str, st.session_state.historico[-10:])))
    
    # Resultados das Apostas
    st.subheader("🎲 Resultados das Apostas")
    if st.session_state.resultados:
        # Mostra TODOS os resultados
        resultados_display = " ".join(list(st.session_state.resultados))
        st.write(resultados_display)
        st.write(f"Total de apostas registradas: {len(st.session_state.resultados)}")
        
        total_green = list(st.session_state.resultados).count("1")
        total_red = list(st.session_state.resultados).count("X")
        if len(st.session_state.resultados) > 0:
            taxa_acerto = (total_green / len(st.session_state.resultados)) * 100
            st.write(f"**GREEN: {total_green}** | **RED: {total_red}** | **Taxa de acerto: {taxa_acerto:.1f}%**")
            
            # Mostrar também os últimos 20 para referência rápida
            if len(st.session_state.resultados) > 20:
                st.write(f"**Últimos 20 resultados:** {" ".join(list(st.session_state.resultados)[-20:])}")
    else:
        if len(st.session_state.historico) >= 75:
            st.write("Nenhuma aposta registrada. Use o botão 'Registrar' para começar.")
        else:
            st.write(f"Aguardando mais dados... ({len(st.session_state.historico)}/75 rodadas)")

# Botão para forçar re-verificação do histórico
if st.button("🔄 Re-verificar Histórico"):
    if st.session_state.historico:
        verificar_apostas_do_historico()
        st.success(f"Re-verificação concluída! {len(st.session_state.resultados)} apostas analisadas.")
    else:
        st.warning("Nenhum histórico para verificar")

# Exportar histórico
if st.button("📥 Exportar Histórico"):
    if st.session_state.historico:
        resultados_export = list(st.session_state.resultados)
        if len(resultados_export) < len(st.session_state.historico) - 75:
            resultados_export = [''] * (len(st.session_state.historico) - 75 - len(resultados_export)) + resultados_export
        
        df = pd.DataFrame({
            'Número': st.session_state.historico,
            'Resultado_Aposta': [''] * 75 + resultados_export  # Primeiros 75 sem resultado
        })
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Baixar CSV",
            data=csv,
            file_name='historico_roleta_nova_estrategia.csv',
            mime='text/csv'
        )
    else:
        st.warning("Nenhum dado para exportar")
