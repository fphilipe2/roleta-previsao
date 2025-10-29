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
if 'multiplicador_atual' not in st.session_state:
    st.session_state.multiplicador_atual = 1  # Martingale starts at 1x

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

def criar_aposta_com_martingale(numero):
    """Cria apostas com multiplicador Martingale"""
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
    
    # Calcula fichas BASE (sem multiplicador)
    todas_apostas = numeros_aposta + vizinhos
    fichas_base = {}
    for n in todas_apostas:
        fichas_base[n] = fichas_base.get(n, 0) + 1
    
    custo_base = sum(fichas_base.values())
    
    # APLICA MULTIPLICADOR MARTINGALE nas fichas
    multiplicador = st.session_state.multiplicador_atual if st.session_state.modo_simulacao else 1
    fichas_com_multiplicador = {}
    for numero_ficha, quantidade_base in fichas_base.items():
        fichas_com_multiplicador[numero_ficha] = quantidade_base * multiplicador
    
    custo_com_multiplicador = sum(fichas_com_multiplicador.values())
    
    return {
        'numero_origem': numero,
        'numeros_aposta': numeros_aposta,
        'vizinhos': vizinhos,
        'fichas_base': fichas_base,
        'fichas_por_numero': fichas_com_multiplicador,
        'custo_base': custo_base,
        'custo_aposta': custo_com_multiplicador,
        'apostas_finais': list(set(todas_apostas)),
        'rodadas_apostadas': 0,
        'custo_acumulado': 0,
        'multiplicador': multiplicador
    }

def processar_numero_com_martingale(numero):
    """Processamento com Martingale"""
    # Se não há aposta, cria uma com o número atual
    if st.session_state.aposta_atual is None:
        aposta = criar_aposta_com_martingale(numero)
        if aposta:
            st.session_state.aposta_atual = aposta
            st.session_state.reds_consecutivos = 0
            st.session_state.proximo_numero_origem = None
            st.session_state.modo_simulacao = False
            st.session_state.multiplicador_atual = 1  # Começa com 1x
        else:
            st.session_state.resultados.append("N")
        return
    
    aposta = st.session_state.aposta_atual
    numero_origem_atual = aposta['numero_origem']
    
    # Verifica GREEN instantaneamente
    if numero in aposta['apostas_finais']:
        # Só contabiliza se estiver em modo simulação (após 3º RED)
        if st.session_state.modo_simulacao:
            fichas = aposta['fichas_por_numero'].get(numero, 0)
            premio = fichas * 36
            lucro = premio - aposta['custo_aposta']
            st.session_state.banca += lucro
            st.session_state.resultados.append("1")
            
            # GREEN com custo: RESETA Martingale para 1x
            st.session_state.multiplicador_atual = 1
        else:
            st.session_state.resultados.append("G")  # Green sem custo
        
        # GREEN: número que saiu vira nova origem
        novo_numero_origem = numero
        st.session_state.aposta_atual = criar_aposta_com_martingale(novo_numero_origem)
        st.session_state.reds_consecutivos = 0
        st.session_state.proximo_numero_origem = None
        st.session_state.ciclo_atual += 1
        
    else:
        # RED
        # Só contabiliza custo se estiver em modo simulação (após 3º RED)
        if st.session_state.modo_simulacao:
            st.session_state.banca -= aposta['custo_aposta']
            st.session_state.resultados.append("X")
            aposta['custo_acumulado'] += aposta['custo_aposta']
            
            # RED com custo: DOBRA o Martingale para o próximo ciclo
            st.session_state.multiplicador_atual *= 2
        else:
            st.session_state.resultados.append("R")  # Red sem custo
        
        aposta['rodadas_apostadas'] += 1
        
        # Incrementa contador de REDs
        st.session_state.reds_consecutivos += 1
        
        # Se é o PRIMEIRO RED, define o próximo número origem
        if st.session_state.reds_consecutivos == 1:
            # O próximo número origem é o número que ACABOU de sair (o RED atual)
            st.session_state.proximo_numero_origem = numero
        
        # Se chegou ao TERCEIRO RED, ativa modo simulação e faz a troca
        if st.session_state.reds_consecutivos == 3:
            # ATIVA MODO SIMULAÇÃO - A partir de agora contabiliza fichas
            st.session_state.modo_simulacao = True
            
            if st.session_state.proximo_numero_origem is not None:
                # Troca para o próximo número origem definido no 1º RED
                novo_numero_origem = st.session_state.proximo_numero_origem
                st.session_state.aposta_atual = criar_aposta_com_martingale(novo_numero_origem)
                st.session_state.reds_consecutivos = 0
                st.session_state.proximo_numero_origem = None

# Interface
st.title("⚡ Sistema com Martingale - Dobra a cada RED")

# Controles
numero = st.number_input("Número sorteado (0-36)", 0, 36, key="num_input")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🎯 Registrar", use_container_width=True):
        if numero is not None:
            st.session_state.historico.append(numero)
            processar_numero_com_martingale(numero)
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
        st.session_state.multiplicador_atual = 1
        st.rerun()
with col3:
    if st.button("📊 Stats", use_container_width=True):
        st.rerun()

# Upload rápido
uploaded_file = st.file_uploader("CSV rápido (apenas coluna 'Número')", type="csv")
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        if 'Número' in df.columns:
            numeros = df['Número'].tolist()
            
            # Limita a 1000 números para não travar
            if len(numeros) > 1000:
                numeros = numeros[:1000]
                st.warning(f"Limitado aos primeiros 1000 números de {len(df['Número'])}")
            
            # Reseta tudo
            st.session_state.historico = []
            st.session_state.resultados = []
            st.session_state.banca = 1000
            st.session_state.aposta_atual = None
            st.session_state.ciclo_atual = 1
            st.session_state.reds_consecutivos = 0
            st.session_state.proximo_numero_origem = None
            st.session_state.modo_simulacao = False
            st.session_state.multiplicador_atual = 1
            
            # Processa números
            progress_bar = st.progress(0)
            total_numeros = len(numeros)
            
            for i, num in enumerate(numeros):
                st.session_state.historico.append(num)
                processar_numero_com_martingale(num)
                progress_bar.progress((i + 1) / total_numeros)
            
            st.success(f"✅ {total_numeros} números processados!")
            st.rerun()
            
    except Exception as e:
        st.error(f"Erro: {str(e)}")

# Display do ciclo atual
st.markdown("---")
st.subheader("🔄 Status do Ciclo")

if st.session_state.aposta_atual:
    aposta = st.session_state.aposta_atual
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Ciclo", st.session_state.ciclo_atual)
    with col2:
        st.metric("Origem", aposta['numero_origem'])
    with col3:
        st.metric("REDs", f"{st.session_state.reds_consecutivos}/3")
    with col4:
        status_modo = "💰 ATIVO" if st.session_state.modo_simulacao else "⏳ AGUARDANDO"
        st.metric("Modo", status_modo)
    with col5:
        st.metric("Multiplicador", f"{st.session_state.multiplicador_atual}x")
    
    st.write(f"**Rodadas:** {aposta['rodadas_apostadas']} | **Custo acumulado:** ${aposta['custo_acumulado']:.2f}")
    
    # Mostra próximo número origem se definido
    if st.session_state.proximo_numero_origem is not None:
        st.info(f"📌 **Próxima origem (se 3º RED):** {st.session_state.proximo_numero_origem}")
    
    # Informação sobre modo simulação e Martingale
    if not st.session_state.modo_simulacao:
        st.warning("🔸 **MODO OBSERVAÇÃO:** Aguardando 3º RED para iniciar simulação")
    else:
        st.success(f"🎯 **MODO SIMULAÇÃO ATIVO:** Martingale {st.session_state.multiplicador_atual}x - Contabilizando fichas")
    
    with st.expander("📋 Detalhes da Aposta", expanded=False):
        st.write(f"**Números base:** {aposta['numeros_aposta']}")
        st.write(f"**Vizinhos:** {aposta['vizinhos']}")
        st.write(f"**Custo base:** ${aposta['custo_base']:.2f}")
        st.write(f"**Custo atual:** ${aposta['custo_aposta']:.2f} (x{aposta['multiplicador']})")
        st.write(f"**Total números:** {len(aposta['apostas_finais'])}")
        
        # Mostra distribuição de fichas
        st.write("**Distribuição de Fichas:**")
        for num, fichas in sorted(aposta['fichas_por_numero'].items()):
            fichas_base = aposta['fichas_base'].get(num, fichas / aposta['multiplicador'])
            st.write(f"- Número {num}: {fichas} fichas ({fichas_base:.0f} base × {aposta['multiplicador']}x)")
        
else:
    st.info("⏳ Aguardando primeiro número...")

# Resultados
st.markdown("---")
st.subheader("🎲 Resultados")

if st.session_state.resultados:
    # Mostra apenas os últimos 30 resultados
    ultimos = st.session_state.resultados[-30:] if len(st.session_state.resultados) > 30 else st.session_state.resultados
    
    # Formata em linhas de 10 resultados
    for i in range(0, len(ultimos), 10):
        linha = " ".join(ultimos[i:i+10])
        st.code(linha, language=None)
    
    # Estatísticas considerando apenas resultados com custo (X e 1)
    resultados_com_custo = [r for r in st.session_state.resultados if r in ['1', 'X']]
    greens = resultados_com_custo.count("1")
    reds = resultados_com_custo.count("X")
    total_com_custo = greens + reds
    
    # Todos os resultados (incluindo sem custo)
    todos_greens = st.session_state.resultados.count("1") + st.session_state.resultados.count("G")
    todos_reds = st.session_state.resultados.count("X") + st.session_state.resultados.count("R")
    total_geral = len(st.session_state.resultados)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🎯 GREEN", greens)
    with col2:
        st.metric("🔴 RED", reds)
    with col3:
        if total_com_custo > 0:
            st.metric("📈 Taxa", f"{(greens/total_com_custo*100):.1f}%")
        else:
            st.metric("📈 Taxa", "0%")
    with col4:
        st.metric("💰 Banca", f"${st.session_state.banca:.2f}")
    
    # Info sobre resultados sem custo
    if total_geral > total_com_custo:
        st.info(f"📊 Total geral: {todos_greens} GREEN / {todos_reds} RED (incluindo {total_geral - total_com_custo} sem custo)")

# Informações do histórico
if st.session_state.historico:
    st.markdown("---")
    st.write(f"📊 Histórico: {len(st.session_state.historico)} números")
    if len(st.session_state.historico) > 10:
        st.write(f"Últimos 10: {' → '.join(map(str, st.session_state.historico[-10:]))}")

# Legenda dos resultados
st.markdown("---")
st.subheader("📖 Legenda do Sistema")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.write("🎯 **1** = GREEN com custo")
    st.write("🔄 **Reset Martingale**")
with col2:
    st.write("🔴 **X** = RED com custo")  
    st.write("📈 **Dobra Martingale**")
with col3:
    st.write("🟢 **G** = GREEN sem custo")
    st.write("⚖️ Mantém estratégia")
with col4:
    st.write("⚫ **R** = RED sem custo")
    st.write("📊 Conta para 3º RED")

# Informações do Martingale
st.markdown("---")
st.subheader("🎰 Sistema Martingale")
st.write("**Regras do Martingale:**")
st.write("- 🔸 **Antes do 3º RED**: Sem custos, multiplicador 1x")
st.write("- 🎯 **GREEN com custo**: Reseta multiplicador para 1x")  
st.write("- 🔴 **RED com custo**: Dobra multiplicador para próximo ciclo")
st.write("- 📈 **Progressão**: 1x → 2x → 4x → 8x → 16x → ...")

# Histórico de multiplicadores (apenas os últimos)
if st.session_state.modo_simulacao:
    st.info(f"🔢 **Multiplicador atual:** {st.session_state.multiplicador_atual}x")
