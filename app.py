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
    numeros_aposta = set()
    
    for ocorrencia in ocorrencias:
        # Adiciona o próprio número
        numeros_aposta.add(ocorrencia['numero'])
        
        # Adiciona número antes (se existir)
        if ocorrencia['antes'] is not None:
            numeros_aposta.add(ocorrencia['antes'])
        
        # Adiciona número depois (se existir)
        if ocorrencia['depois'] is not None:
            numeros_aposta.add(ocorrencia['depois'])
    
    # Ordena os números
    numeros_aposta = sorted(list(numeros_aposta))
    
    # Calcula vizinhos
    vizinhos = obter_vizinhos_roleta(numeros_aposta)
    
    # Apostas finais (números + vizinhos)
    apostas_finais = sorted(list(set(numeros_aposta) | set(vizinhos)))
    
    return numeros_aposta, vizinhos, apostas_finais

def verificar_apostas_do_historico():
    """Verifica todas as apostas do histórico carregado"""
    st.session_state.resultados.clear()  # Limpa resultados anteriores
    
    if len(st.session_state.historico) <= 1:
        return  # Não há apostas para verificar
    
    # Para cada número a partir da posição 1, verifica a aposta
    for i in range(1, len(st.session_state.historico)):
        numero_atual = st.session_state.historico[i]
        numero_anterior = st.session_state.historico[i - 1]
        
        # Calcula apostas para o número anterior
        numeros_aposta, vizinhos, apostas_anteriores = calcular_apostas_para_numero(numero_anterior)
        
        # Verifica resultado
        if numero_atual in apostas_anteriores:
            st.session_state.resultados.append("1")  # GREEN
        else:
            st.session_state.resultados.append("X")  # RED

def registrar_numero(numero):
    # Primeiro verifica o resultado da aposta anterior (se houver histórico suficiente)
    if len(st.session_state.historico) >= 1:
        ultimo_sorteado_anterior = st.session_state.historico[-1]
        
        # Calcula apostas para o número anterior
        numeros_aposta, vizinhos, apostas_anteriores = calcular_apostas_para_numero(ultimo_sorteado_anterior)
        
        # Verifica se o NOVO número está nas apostas da rodada anterior
        if numero in apostas_anteriores:
            st.session_state.resultados.append("1")  # GREEN
        else:
            st.session_state.resultados.append("X")  # RED
    
    # Adiciona o novo número ao histórico
    st.session_state.historico.append(numero)

# Interface
st.title("🎯 Nova Estratégia - Padrão de Ocorrências")

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
    
    # ESTRATÉGIA: Padrão de Ocorrências
    st.markdown("### 🎯 Estratégia: Padrão de Ocorrências")
    
    # Calcula apostas para o último número
    numeros_aposta, vizinhos, apostas_finais = calcular_apostas_para_numero(ultimo_numero)
    
    # Mostra as últimas ocorrências
    ocorrencias = obter_ultimas_ocorrencias_com_vizinhos(ultimo_numero)
    
    if ocorrencias:
        st.markdown("**Últimas ocorrências:**")
        for i, ocorrencia in enumerate(ocorrencias, 1):
            antes = f"{ocorrencia['antes']} → " if ocorrencia['antes'] is not None else ""
            depois = f" → {ocorrencia['depois']}" if ocorrencia['depois'] is not None else ""
            st.write(f"{i}. {antes}{ocorrencia['numero']}{depois}")
    else:
        st.write("Número ainda não tem ocorrências anteriores")
    
    st.markdown("**Números para apostar:**")
    st.write(f"**{numeros_aposta}**")
    
    st.markdown("**Vizinhos (1 de cada lado):**")
    st.write(f"**{vizinhos}**")
    
    st.markdown("**Apostas Finais (Números + Vizinhos):**")
    st.write(f"**{apostas_finais}**")
    
    # Estatísticas
    st.markdown("**📊 Estatísticas:**")
    st.write(f"- Total de números apostados: {len(apostas_finais)}")
    st.write(f"- Cobertura da roleta: {(len(apostas_finais)/37*100):.1f}%")
    
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
        st.write("Aguardando próximos resultados...")

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
        if len(resultados_export) < len(st.session_state.historico) - 1:
            resultados_export = [''] * (len(st.session_state.historico) - 1 - len(resultados_export)) + resultados_export
        
        df = pd.DataFrame({
            'Número': st.session_state.historico,
            'Resultado_Aposta': [''] + resultados_export  # Primeiro número sem resultado
        })
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Baixar CSV",
            data=csv,
            file_name='historico_roleta_padrao_ocorrencias.csv',
            mime='text/csv'
        )
    else:
        st.warning("Nenhum dado para exportar")
