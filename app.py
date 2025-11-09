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
if 'proximo_numero_origem' not in st.session_state:
    st.session_state.proximo_numero_origem = None
if 'modo_simulacao' not in st.session_state:
    st.session_state.modo_simulacao = False

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
    """Versão MUITO otimizada para obter vizinhos"""
    vizinhos = set()
    for n in numeros:
        if n in vizinhos_map:
            vizinhos.update(vizinhos_map[n])
    return sorted(vizinhos)

def criar_aposta_otimizada(numero):
    """Versão MEGA otimizada para criar apostas"""
    if len(st.session_state.historico) < 4:  # Mínimo para ter padrões
        return None
    
    # Busca RÁPIDA das últimas 3 ocorrências
    ocorrencias = []
    for i in range(len(st.session_state.historico)-1, -1, -1):
        if st.session_state.historico[i] == numero:
            ocorrencias.append(i)
            if len(ocorrencias) == 3:
                break
    
    if len(ocorrencias) < 1:  # Pelo menos 1 ocorrência
        return None
    
    # Coleta números de forma INTELIGENTE
    numeros_aposta = [numero]
    for pos in ocorrencias[:2]:  # Só usa as 2 primeiras para ser mais rápido
        if pos > 0:
            numeros_aposta.append(st.session_state.historico[pos-1])
        if pos < len(st.session_state.historico)-1:
            numeros_aposta.append(st.session_state.historico[pos+1])
    
    # Remove duplicatas e calcula vizinhos
    numeros_unicos = list(set(numeros_aposta))
    vizinhos = obter_vizinhos(numeros_unicos)
    
    # Calcula fichas de forma SIMPLES
    todas_apostas = numeros_unicos + vizinhos
    fichas = {num: 1 for num in set(todas_apostas)}  # 1 ficha por número
    
    custo = len(fichas)
    
    return {
        'numero_origem': numero,
        'numeros_aposta': numeros_unicos,
        'vizinhos': vizinhos,
        'fichas_por_numero': fichas,
        'custo_aposta': custo,
        'apostas_finais': list(set(todas_apostas)),
        'rodadas_apostadas': 0,
        'custo_acumulado': 0
    }

def processar_numero_otimizado(numero):
    """Processamento SUPER rápido"""
    # Se não há aposta, cria uma
    if st.session_state.aposta_atual is None:
        aposta = criar_aposta_otimizada(numero)
        if aposta:
            st.session_state.aposta_atual = aposta
            st.session_state.reds_consecutivos = 0
            st.session_state.proximo_numero_origem = None
            st.session_state.modo_simulacao = False
        return
    
    aposta = st.session_state.aposta_atual
    
    # Verifica GREEN
    if numero in aposta['apostas_finais']:
        if st.session_state.modo_simulacao:
            fichas = aposta['fichas_por_numero'].get(numero, 0)
            premio = fichas * 36
            lucro = premio - aposta['custo_aposta']
            st.session_state.banca += lucro
            st.session_state.resultados.append("1")
        else:
            st.session_state.resultados.append("G")
        
        # GREEN: novo ciclo
        st.session_state.aposta_atual = criar_aposta_otimizada(numero)
        st.session_state.reds_consecutivos = 0
        st.session_state.proximo_numero_origem = None
        st.session_state.modo_simulacao = False
        st.session_state.ciclo_atual += 1
        
    else:
        # RED
        if st.session_state.modo_simulacao:
            st.session_state.banca -= aposta['custo_aposta']
            st.session_state.resultados.append("X")
            aposta['custo_acumulado'] += aposta['custo_aposta']
        else:
            st.session_state.resultados.append("R")
        
        aposta['rodadas_apostadas'] += 1
        st.session_state.reds_consecutivos += 1
        
        # 1º RED: define próximo número
        if st.session_state.reds_consecutivos == 1:
            st.session_state.proximo_numero_origem = numero
        
        # 3º RED: ativa modo simulação
        if st.session_state.reds_consecutivos == 3:
            st.session_state.modo_simulacao = True
            if st.session_state.proximo_numero_origem is not None:
                st.session_state.aposta_atual = criar_aposta_otimizada(st.session_state.proximo_numero_origem)
                st.session_state.reds_consecutivos = 0
                st.session_state.proximo_numero_origem = None

# Interface
st.title("⚡ Sistema Rápido - Sem Travamentos")

# Controles
numero = st.number_input("Número sorteado (0-36)", 0, 36, key="num_input")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🎯 Registrar", use_container_width=True):
        if numero is not None:
            st.session_state.historico.append(numero)
            processar_numero_otimizado(numero)
            st.rerun()
with col2:
    if st.button("🔄 Resetar", use_container_width=True):
        st.session_state.historico = []
        st.session_state.resultados = []
        st.session_state.banca = 1000
        st.session_state.aposta_atual = None
        st.session_state.ciclo_atual = 1
        st.session_state.reds_consecutivos = 0
        st.session_state.proximo_numero_origem = None
        st.session_state.modo_simulacao = False
        st.rerun()
with col3:
    if st.button("📊 Stats", use_container_width=True):
        st.rerun()

# Upload OTIMIZADO
uploaded_file = st.file_uploader("CSV rápido (apenas coluna 'Número')", type="csv")
if uploaded_file:
    try:
        # Leitura RÁPIDA do CSV
        df = pd.read_csv(uploaded_file)
        
        # Detecta automaticamente a coluna de números
        coluna_numeros = None
        for col in df.columns:
            if 'número' in col.lower() or 'numero' in col.lower() or 'num' in col.lower():
                coluna_numeros = col
                break
        
        if coluna_numeros is None and len(df.columns) > 0:
            coluna_numeros = df.columns[0]  # Usa primeira coluna
        
        if coluna_numeros:
            # Converte para lista LIMPANDO dados
            numeros = pd.to_numeric(df[coluna_numeros], errors='coerce').dropna().astype(int).tolist()
            
            # Limita a 500 números para evitar travamento
            if len(numeros) > 500:
                numeros = numeros[:500]
                st.warning(f"⏰ Limitado aos primeiros 500 números (de {len(df)})")
            
            # Reseta TUDO
            st.session_state.historico = []
            st.session_state.resultados = []
            st.session_state.banca = 1000
            st.session_state.aposta_atual = None
            st.session_state.ciclo_atual = 1
            st.session_state.reds_consecutivos = 0
            st.session_state.proximo_numero_origem = None
            st.session_state.modo_simulacao = False
            
            # Processamento EM LOTE sem barra de progresso (mais rápido)
            placeholder = st.empty()
            placeholder.info("⚡ Processando números...")
            
            for num in numeros:
                if 0 <= num <= 36:  # Só números válidos
                    st.session_state.historico.append(num)
                    processar_numero_otimizado(num)
            
            placeholder.empty()
            st.success(f"✅ {len(numeros)} números processados instantaneamente!")
            st.rerun()
        else:
            st.error("❌ Não foi possível encontrar coluna com números")
            
    except Exception as e:
        st.error(f"❌ Erro: {str(e)}")

# Status do Ciclo
st.markdown("---")
st.subheader("🔄 Status do Ciclo")

if st.session_state.aposta_atual:
    aposta = st.session_state.aposta_atual
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Ciclo", st.session_state.ciclo_atual)
    with col2:
        st.metric("Origem", aposta['numero_origem'])
    with col3:
        st.metric("REDs", f"{st.session_state.reds_consecutivos}/3")
    with col4:
        modo = "💰 ATIVO" if st.session_state.modo_simulacao else "⏳ AGUARDANDO"
        st.metric("Modo", modo)
    
    st.write(f"**Rodadas:** {aposta['rodadas_apostadas']} | **Custo acumulado:** ${aposta['custo_acumulado']:.2f}")
    
    if st.session_state.proximo_numero_origem is not None:
        st.info(f"📌 Próxima origem: {st.session_state.proximo_numero_origem}")
    
    with st.expander("📋 Ver Aposta"):
        st.write(f"**Números base:** {aposta['numeros_aposta']}")
        st.write(f"**Vizinhos:** {aposta['vizinhos']}")
        st.write(f"**Custo/rodada:** ${aposta['custo_aposta']:.2f}")
        st.write(f"**Total números:** {len(aposta['apostas_finais'])}")
        
else:
    st.info("⏳ Aguardando primeiro número...")

# Resultados
st.markdown("---")
st.subheader("🎲 Resultados")

if st.session_state.resultados:
    # Mostra apenas os últimos 20 resultados
    ultimos = st.session_state.resultados[-20:]
    
    # Formatação simples
    for i in range(0, len(ultimos), 10):
        linha = " ".join(ultimos[i:i+10])
        st.text(linha)
    
    # Estatísticas rápidas
    greens = st.session_state.resultados.count("1")
    reds = st.session_state.resultados.count("X")
    total = greens + reds
    
    if total > 0:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🎯 GREEN", greens)
        with col2:
            st.metric("🔴 RED", reds)
        with col3:
            st.metric("📈 Taxa", f"{(greens/total*100):.1f}%")
    
    st.metric("💰 Banca", f"${st.session_state.banca:.2f}")

# Histórico
if st.session_state.historico:
    st.markdown("---")
    st.write(f"📊 Histórico: {len(st.session_state.historico)} números")
    if len(st.session_state.historico) > 8:
        st.write(f"Últimos 8: {' → '.join(map(str, st.session_state.historico[-8:]))}")

# Legenda
st.markdown("---")
st.write("**📖 Legenda:** 1=GREEN(custo) | X=RED(custo) | G=GREEN(sem) | R=RED(sem)")
