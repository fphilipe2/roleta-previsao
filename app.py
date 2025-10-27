import streamlit as st
import pandas as pd

# Configuração inicial
if 'historico' not in st.session_state:
    st.session_state.historico = []
if 'numero_origem' not in st.session_state:
    st.session_state.numero_origem = None
if 'reds_consecutivos' not in st.session_state:
    st.session_state.reds_consecutivos = 0
if 'ciclo_atual' not in st.session_state:
    st.session_state.ciclo_atual = 1

# Mapa de vizinhos
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

def obter_vizinhos(numeros):
    """Obtém vizinhos dos números"""
    vizinhos = set()
    for n in numeros:
        if n in vizinhos_map:
            vizinhos.update(vizinhos_map[n])
    return sorted(vizinhos)

def criar_aposta(numero_origem):
    """Cria aposta baseada no número origem"""
    if not st.session_state.historico:
        return None
    
    # Encontra as últimas 3 ocorrências do número origem
    ocorrencias = []
    for i in range(len(st.session_state.historico)-1, -1, -1):
        if st.session_state.historico[i] == numero_origem:
            ocorrencias.append(i)
            if len(ocorrencias) == 3:
                break
    
    if not ocorrencias:
        return None
    
    # Coleta números anteriores e posteriores
    numeros_aposta = [numero_origem]
    for pos in ocorrencias:
        if pos > 0:
            numeros_aposta.append(st.session_state.historico[pos-1])
        if pos < len(st.session_state.historico)-1:
            numeros_aposta.append(st.session_state.historico[pos+1])
    
    # Calcula vizinhos
    vizinhos = obter_vizinhos(set(numeros_aposta))
    
    # Números finais da aposta
    apostas_finais = list(set(numeros_aposta + vizinhos))
    
    return {
        'numero_origem': numero_origem,
        'apostas_finais': apostas_finais,
        'numeros_base': numeros_aposta,
        'vizinhos': vizinhos
    }

def encontrar_numero_seguinte(numero_origem):
    """Encontra o número IMEDIATAMENTE seguinte ao número origem no histórico"""
    if not st.session_state.historico:
        return None
    
    # Encontra a ÚLTIMA ocorrência do número origem
    ultima_posicao = None
    for i in range(len(st.session_state.historico)-1, -1, -1):
        if st.session_state.historico[i] == numero_origem:
            ultima_posicao = i
            break
    
    # Verifica se há um número seguinte
    if ultima_posicao is not None and ultima_posicao < len(st.session_state.historico) - 1:
        return st.session_state.historico[ultima_posicao + 1]
    
    return None

def processar_numero(numero):
    """Processa o número sorteado conforme a estratégia"""
    
    # Se não há número origem, usa o primeiro número como origem
    if st.session_state.numero_origem is None:
        st.session_state.numero_origem = numero
        st.session_state.reds_consecutivos = 0
        return "PRIMEIRO_NUMERO"
    
    aposta = criar_aposta(st.session_state.numero_origem)
    if not aposta:
        return "SEM_APOSTA"
    
    # Verifica se é GREEN
    if numero in aposta['apostas_finais']:
        # GREEN - novo número origem é o número que saiu
        novo_origem = numero
        st.session_state.numero_origem = novo_origem
        st.session_state.reds_consecutivos = 0
        st.session_state.ciclo_atual += 1
        return "GREEN"
    
    else:
        # RED
        st.session_state.reds_consecutivos += 1
        
        # Se chegou ao 3º RED, troca para o número seguinte
        if st.session_state.reds_consecutivos == 3:
            numero_seguinte = encontrar_numero_seguinte(st.session_state.numero_origem)
            
            if numero_seguinte is not None:
                st.session_state.numero_origem = numero_seguinte
                st.session_state.reds_consecutivos = 0
                return "TROCA_3_RED"
            else:
                return "TROCA_FALHOU"
        
        return "RED"

def registrar_numero(numero):
    """Registra um novo número"""
    st.session_state.historico.append(numero)
    resultado = processar_numero(numero)
    return resultado

# Interface
st.title("🎯 Estratégia de Apostas - Foco na Escolha do Número")

# Controles
numero = st.number_input("Último número sorteado (0-36)", 0, 36)

col1, col2 = st.columns(2)
with col1:
    if st.button("🎯 Registrar Número"):
        if numero is not None:
            resultado = registrar_numero(numero)
            
            # Mostra resultado
            if resultado == "GREEN":
                st.success(f"🎉 GREEN! Nova origem: {st.session_state.numero_origem}")
            elif resultado == "TROCA_3_RED":
                st.warning(f"🔄 Troca automática! Nova origem: {st.session_state.numero_origem}")
            elif resultado == "PRIMEIRO_NUMERO":
                st.info(f"🔰 Primeiro número registrado: {st.session_state.numero_origem}")
            elif resultado == "RED":
                st.error(f"❌ RED {st.session_state.reds_consecutivos}/3")
            
            st.rerun()

with col2:
    if st.button("🔄 Resetar"):
        st.session_state.historico = []
        st.session_state.numero_origem = None
        st.session_state.reds_consecutivos = 0
        st.session_state.ciclo_atual = 1
        st.rerun()

# Upload de CSV
uploaded_file = st.file_uploader("Carregar histórico (CSV)", type="csv")
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        if 'Número' in df.columns:
            numeros = df['Número'].tolist()[:100]  # Limita a 100 números para teste
            
            # Reseta
            st.session_state.historico = []
            st.session_state.numero_origem = None
            st.session_state.reds_consecutivos = 0
            st.session_state.ciclo_atual = 1
            
            # Processa
            for num in numeros:
                registrar_numero(num)
            
            st.success(f"✅ {len(numeros)} números processados!")
            st.rerun()
            
    except Exception as e:
        st.error(f"Erro: {str(e)}")

# Status Atual
st.markdown("## 📊 Status Atual")

if st.session_state.numero_origem is not None:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Número Origem", st.session_state.numero_origem)
    with col2:
        st.metric("REDs Consecutivos", st.session_state.reds_consecutivos)
    with col3:
        st.metric("Ciclo", st.session_state.ciclo_atual)
    
    # Detalhes da aposta atual
    aposta = criar_aposta(st.session_state.numero_origem)
    if aposta:
        with st.expander("📋 Detalhes da Aposta Atual"):
            st.write(f"**Números base:** {aposta['numeros_base']}")
            st.write(f"**Vizinhos:** {aposta['vizinhos']}")
            st.write(f"**Total números apostados:** {len(aposta['apostas_finais'])}")
            st.write(f"**Números:** {sorted(aposta['apostas_finais'])}")
    
    # Próximo número para troca
    if st.session_state.reds_consecutivos > 0:
        numero_seguinte = encontrar_numero_seguinte(st.session_state.numero_origem)
        if numero_seguinte is not None:
            st.info(f"📌 **Próximo número para troca:** {numero_seguinte} (aparece após {st.session_state.numero_origem})")
        
        reds_restantes = 3 - st.session_state.reds_consecutivos
        if reds_restantes > 0:
            st.warning(f"⚠️ **{reds_restantes} RED(s) para troca automática**")

# Histórico Recente
if st.session_state.historico:
    st.markdown("### 📈 Histórico Recente")
    ultimos_15 = st.session_state.historico[-15:] if len(st.session_state.historico) >= 15 else st.session_state.historico
    
    # Mostra histórico com destaque para o número origem atual
    historico_formatado = []
    for i, num in enumerate(ultimos_15):
        if num == st.session_state.numero_origem:
            historico_formatado.append(f"**[{num}]**")
        else:
            historico_formatado.append(str(num))
    
    st.write(" → ".join(historico_formatado))

# Debug: Mostra informações detalhadas
with st.expander("🔍 Debug - Informações Detalhadas"):
    if st.session_state.historico:
        st.write("**Histórico completo:**", st.session_state.historico)
        st.write("**Últimas posições do número origem:**")
        
        if st.session_state.numero_origem is not None:
            posicoes = []
            for i in range(len(st.session_state.historico)-1, -1, -1):
                if st.session_state.historico[i] == st.session_state.numero_origem:
                    posicoes.append(i)
                    if len(posicoes) == 3:
                        break
            
            st.write(f"Posições: {posicoes}")
            
            if posicoes:
                ultima_posicao = posicoes[0]
                if ultima_posicao < len(st.session_state.historico) - 1:
                    numero_seguinte = st.session_state.historico[ultima_posicao + 1]
                    st.write(f"**Número seguinte:** {numero_seguinte} (posição {ultima_posicao + 1})")
