import streamlit as st
import pandas as pd

# Configuração inicial
if 'historico' not in st.session_state:
    st.session_state.historico = []
if 'resultados' not in st.session_state:
    st.session_state.resultados = []
if 'banca' not in st.session_state:
    st.session_state.banca = 1000
if 'aposta_atual' not in st.session_state:
    st.session_state.aposta_atual = None
if 'ciclo_atual' not in st.session_state:
    st.session_state.ciclo_atual = 1
if 'reds_consecutivos' not in st.session_state:
    st.session_state.reds_consecutivos = 0
if 'ultimo_numero_apostado' not in st.session_state:
    st.session_state.ultimo_numero_apostado = None

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
    """Versão otimizada para obter vizinhos"""
    vizinhos = set()
    for n in numeros:
        if n in vizinhos_map:
            vizinhos.update(vizinhos_map[n])
    return sorted(vizinhos)

def criar_aposta_rapido(numero):
    """Cria apostas baseado no número"""
    if not st.session_state.historico:
        return None
    
    # Encontra as últimas 3 ocorrências anteriores
    ocorrencias = []
    count = 0
    for i in range(len(st.session_state.historico)-2, -1, -1):
        if st.session_state.historico[i] == numero:
            ocorrencias.append(i)
            count += 1
            if count == 3:
                break
    
    if not ocorrencias:
        return None
    
    # Coleta números rapidamente
    numeros_aposta = [numero]  # Número alvo
    
    for pos in ocorrencias:
        if pos > 0:
            numeros_aposta.append(st.session_state.historico[pos-1])
        if pos < len(st.session_state.historico)-1:
            numeros_aposta.append(st.session_state.historico[pos+1])
    
    # Calcula vizinhos
    vizinhos = obter_vizinhos(set(numeros_aposta))
    
    # Calcula fichas
    todas_apostas = numeros_aposta + vizinhos
    fichas = {}
    for n in todas_apostas:
        fichas[n] = fichas.get(n, 0) + 1
    
    custo = sum(fichas.values())
    
    return {
        'numero_origem': numero,
        'numeros_aposta': numeros_aposta,
        'vizinhos': vizinhos,
        'fichas_por_numero': fichas,
        'custo_aposta': custo,
        'apostas_finais': list(set(todas_apostas)),
        'rodadas_apostadas': 0,
        'custo_acumulado': 0
    }

def processar_numero_com_troca_automatica(numero):
    """Processa número com troca automática após 3 REDs consecutivos"""
    
    # Se não há aposta atual, cria uma baseada no número atual
    if st.session_state.aposta_atual is None:
        aposta = criar_aposta_rapido(numero)
        if aposta:
            st.session_state.aposta_atual = aposta
            st.session_state.ultimo_numero_apostado = numero
            st.session_state.reds_consecutivos = 0
        else:
            st.session_state.resultados.append("N")
        return
    
    aposta = st.session_state.aposta_atual
    
    # Verifica se é GREEN
    if numero in aposta['apostas_finais']:
        fichas = aposta['fichas_por_numero'].get(numero, 0)
        premio = fichas * 36
        lucro = premio - aposta['custo_aposta']
        
        st.session_state.banca += lucro
        st.session_state.resultados.append("1")
        st.session_state.reds_consecutivos = 0  # Reseta contador de REDs
        
        # GREEN - inicia novo ciclo com o número que deu GREEN
        st.session_state.ciclo_atual += 1
        nova_aposta = criar_aposta_rapido(numero)
        if nova_aposta:
            st.session_state.aposta_atual = nova_aposta
            st.session_state.ultimo_numero_apostado = numero
            st.success(f"🎉 GREEN! Iniciando ciclo {st.session_state.ciclo_atual} com número {numero}")
        
    else:
        # RED
        st.session_state.banca -= aposta['custo_aposta']
        st.session_state.resultados.append("X")
        aposta['rodadas_apostadas'] += 1
        aposta['custo_acumulado'] += aposta['custo_aposta']
        
        # Incrementa contador de REDs consecutivos
        st.session_state.reds_consecutivos += 1
        
        # VERIFICA SE PRECISA TROCAR DE ESTRATÉGIA (3 REDs consecutivos)
        if st.session_state.reds_consecutivos >= 3:
            # Troca para estratégia do número que acabou de sair
            nova_aposta = criar_aposta_rapido(numero)
            if nova_aposta:
                st.session_state.aposta_atual = nova_aposta
                st.session_state.ultimo_numero_apostado = numero
                st.session_state.reds_consecutivos = 0  # Reseta contador
                st.session_state.ciclo_atual += 1
                
                st.warning(f"🔄 TROCA AUTOMÁTICA! 3 REDs consecutivos")
                st.warning(f"📊 Saindo do número {aposta['numero_origem']} para o número {numero}")
                st.warning(f"🆕 Iniciando ciclo {st.session_state.ciclo_atual}")

def registrar_numero(numero):
    """Registra um novo número"""
    st.session_state.historico.append(numero)
    processar_numero_com_troca_automatica(numero)

# Interface
st.title("🎯 Sistema com Troca Automática (3 REDs)")

# Controles
numero = st.number_input("Último número sorteado (0-36)", 0, 36)

col1, col2 = st.columns(2)
with col1:
    if st.button("🎯 Registrar"):
        if numero is not None:
            registrar_numero(numero)
            st.rerun()
with col2:
    if st.button("🔄 Resetar Sistema"):
        st.session_state.historico = []
        st.session_state.resultados = []
        st.session_state.banca = 1000
        st.session_state.aposta_atual = None
        st.session_state.ciclo_atual = 1
        st.session_state.reds_consecutivos = 0
        st.session_state.ultimo_numero_apostado = None
        st.rerun()

# Upload de CSV
uploaded_file = st.file_uploader("Carregar histórico (CSV)", type="csv")
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        if 'Número' in df.columns:
            numeros = df['Número'].tolist()
            
            # Limita a 1000 números
            if len(numeros) > 1000:
                numeros = numeros[:1000]
                st.warning(f"Limitado aos primeiros 1000 números")
            
            # Reseta tudo
            st.session_state.historico = []
            st.session_state.resultados = []
            st.session_state.banca = 1000
            st.session_state.aposta_atual = None
            st.session_state.ciclo_atual = 1
            st.session_state.reds_consecutivos = 0
            st.session_state.ultimo_numero_apostado = None
            
            # Processa com barra de progresso
            progress_bar = st.progress(0)
            total_numeros = len(numeros)
            
            for i, num in enumerate(numeros):
                st.session_state.historico.append(num)
                processar_numero_com_troca_automatica(num)
                progress_bar.progress((i + 1) / total_numeros)
            
            st.success(f"✅ {total_numeros} números processados!")
            st.rerun()
            
    except Exception as e:
        st.error(f"Erro: {str(e)}")

# Ciclo Atual
st.markdown("## 🔄 Ciclo Atual")

if st.session_state.aposta_atual:
    aposta = st.session_state.aposta_atual
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Ciclo", st.session_state.ciclo_atual)
    with col2:
        st.metric("Número Origem", aposta['numero_origem'])
    with col3:
        st.metric("REDs Consecutivos", st.session_state.reds_consecutivos)
    
    st.write(f"**Rodadas:** {aposta['rodadas_apostadas']} | **Custo acumulado:** ${aposta['custo_acumulado']:.2f}")
    
    with st.expander("📋 Detalhes da Aposta", expanded=True):
        st.write(f"**Números:** {aposta['numeros_aposta']}")
        st.write(f"**Vizinhos:** {aposta['vizinhos']}")
        st.write(f"**Custo/rodada:** ${aposta['custo_aposta']:.2f}")
        st.write(f"**Números únicos:** {len(aposta['fichas_por_numero'])}")
        
        # Alerta visual para próximo RED
        reds_restantes = 3 - st.session_state.reds_consecutivos
        if st.session_state.reds_consecutivos > 0:
            if reds_restantes > 0:
                st.warning(f"⚠️ **{reds_restantes} RED(s) para troca automática**")
            else:
                st.error("🚨 **PRÓXIMO RED ATIVA TROCA AUTOMÁTICA!**")
    
else:
    st.info("Aguardando primeiro número para iniciar ciclo...")

# 🎲 RESULTADOS
st.markdown("## 🎲 Resultados das Apostas")

if st.session_state.resultados:
    # Limite de 1000 resultados em uma linha
    resultados_para_mostrar = st.session_state.resultados[-1000:]
    resultados_string = " ".join(resultados_para_mostrar)
    
    st.text_area("", resultados_string, height=100, key="resultados_area")
    
    # Estatísticas
    resultados_validos = [r for r in resultados_para_mostrar if r in ['1', 'X']]
    total_green = resultados_validos.count("1")
    total_red = resultados_validos.count("X")
    total_apostas = len(resultados_validos)
    
    if total_apostas > 0:
        taxa_acerto = (total_green / total_apostas) * 100
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("GREEN", total_green)
        with col2:
            st.metric("RED", total_red)
        with col3:
            st.metric("Taxa", f"{taxa_acerto:.1f}%")
        with col4:
            st.metric("Total", total_apostas)
    
    st.metric("💰 Banca", f"${st.session_state.banca:.2f}")

# Histórico recente
if st.session_state.historico:
    st.markdown("### 📈 Últimos números sorteados")
    ultimos_10 = st.session_state.historico[-10:] if len(st.session_state.historico) >= 10 else st.session_state.historico
    st.write(" → ".join(map(str, ultimos_10)))
