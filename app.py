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
if 'multiplicador_aposta' not in st.session_state:
    st.session_state.multiplicador_aposta = 1
if 'historico_multiplicadores' not in st.session_state:
    st.session_state.historico_multiplicadores = []

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

def criar_aposta_com_multiplicador(numero, multiplicador=1):
    """Cria apostas com multiplicador de fichas"""
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
    
    # APLICA MULTIPLICADOR nas fichas
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
        'multiplicador_atual': multiplicador
    }

def processar_numero_com_martingale_controlado(numero):
    """Processa número com Martingale controlado (dobrar a cada 3 REDs)"""
    
    # Se não há aposta atual, cria uma baseada no número atual
    if st.session_state.aposta_atual is None:
        aposta = criar_aposta_com_multiplicador(numero, st.session_state.multiplicador_aposta)
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
        
        # Registra estatísticas do multiplicador
        st.session_state.historico_multiplicadores.append({
            'ciclo': st.session_state.ciclo_atual,
            'multiplicador': st.session_state.multiplicador_aposta,
            'resultado': 'GREEN',
            'lucro': lucro
        })
        
        # GREEN - Reseta multiplicador e inicia novo ciclo
        st.session_state.multiplicador_aposta = 1
        st.session_state.reds_consecutivos = 0
        
        st.session_state.ciclo_atual += 1
        nova_aposta = criar_aposta_com_multiplicador(numero, st.session_state.multiplicador_aposta)
        if nova_aposta:
            st.session_state.aposta_atual = nova_aposta
            st.session_state.ultimo_numero_apostado = numero
            st.success(f"🎉 GREEN! Multiplicador resetado para 1x")
            st.success(f"💰 Lucro: ${lucro:+.2f} | Iniciando ciclo {st.session_state.ciclo_atual}")
        
    else:
        # RED
        st.session_state.banca -= aposta['custo_aposta']
        st.session_state.resultados.append("X")
        aposta['rodadas_apostadas'] += 1
        aposta['custo_acumulado'] += aposta['custo_aposta']
        
        # Incrementa contador de REDs consecutivos
        st.session_state.reds_consecutivos += 1
        
        # VERIFICA SE PRECISA DOBRAR AS FICHAS (a cada 3 REDs consecutivos)
        if st.session_state.reds_consecutivos % 3 == 0:
            # DOBRA o multiplicador
            novo_multiplicador = st.session_state.multiplicador_aposta * 2
            st.session_state.multiplicador_aposta = novo_multiplicador
            
            # Registra aumento do multiplicador
            st.session_state.historico_multiplicadores.append({
                'ciclo': st.session_state.ciclo_atual,
                'multiplicador': novo_multiplicador,
                'resultado': 'DOUBLING',
                'reds_consecutivos': st.session_state.reds_consecutivos
            })
            
            # Cria NOVA aposta com multiplicador dobrado (mantém o mesmo número origem)
            nova_aposta = criar_aposta_com_multiplicador(aposta['numero_origem'], novo_multiplicador)
            if nova_aposta:
                st.session_state.aposta_atual = nova_aposta
                st.warning(f"🔥 MULTIPLICADOR AUMENTADO! Agora: {novo_multiplicador}x")
                st.warning(f"📊 {st.session_state.reds_consecutivos} REDs consecutivos")
                st.warning(f"💸 Nova aposta: ${nova_aposta['custo_aposta']:.2f} (base: ${nova_aposta['custo_base']:.2f})")

def registrar_numero(numero):
    """Registra um novo número"""
    st.session_state.historico.append(numero)
    processar_numero_com_martingale_controlado(numero)

# Interface
st.title("🎯 Sistema com Martingale Controlado (3 REDs = Dobrar)")

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
        st.session_state.multiplicador_aposta = 1
        st.session_state.historico_multiplicadores = []
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
            st.session_state.multiplicador_aposta = 1
            st.session_state.historico_multiplicadores = []
            
            # Processa com barra de progresso
            progress_bar = st.progress(0)
            total_numeros = len(numeros)
            
            for i, num in enumerate(numeros):
                st.session_state.historico.append(num)
                processar_numero_com_martingale_controlado(num)
                progress_bar.progress((i + 1) / total_numeros)
            
            st.success(f"✅ {total_numeros} números processados!")
            st.rerun()
            
    except Exception as e:
        st.error(f"Erro: {str(e)}")

# Ciclo Atual
st.markdown("## 🔄 Ciclo Atual")

if st.session_state.aposta_atual:
    aposta = st.session_state.aposta_atual
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Ciclo", st.session_state.ciclo_atual)
    with col2:
        st.metric("Número Origem", aposta['numero_origem'])
    with col3:
        st.metric("REDs Consecutivos", st.session_state.reds_consecutivos)
    with col4:
        st.metric("Multiplicador", f"{st.session_state.multiplicador_aposta}x")
    
    st.write(f"**Rodadas:** {aposta['rodadas_apostadas']} | **Custo acumulado:** ${aposta['custo_acumulado']:.2f}")
    
    with st.expander("📋 Detalhes da Aposta", expanded=True):
        st.write(f"**Números:** {aposta['numeros_aposta']}")
        st.write(f"**Vizinhos:** {aposta['vizinhos']}")
        
        # CORREÇÃO: Verifica se a chave existe antes de acessar
        if 'custo_base' in aposta:
            st.write(f"**Custo base:** ${aposta['custo_base']:.2f}")
            st.write(f"**Custo atual:** ${aposta['custo_aposta']:.2f} ({st.session_state.multiplicador_aposta}x)")
        else:
            # Calcula custo base se não existir
            custo_base = sum(aposta['fichas_base'].values()) if 'fichas_base' in aposta else aposta['custo_aposta'] / st.session_state.multiplicador_aposta
            st.write(f"**Custo base:** ${custo_base:.2f}")
            st.write(f"**Custo atual:** ${aposta['custo_aposta']:.2f} ({st.session_state.multiplicador_aposta}x)")
        
        st.write(f"**Números únicos:** {len(aposta['fichas_por_numero'])}")
        
        # Mostra distribuição de fichas (com verificação de segurança)
        st.write("**Distribuição de Fichas:**")
        fichas_base_dict = aposta.get('fichas_base', {})
        for num, fichas in sorted(aposta['fichas_por_numero'].items()):
            fichas_base = fichas_base_dict.get(num, fichas / st.session_state.multiplicador_aposta)
            st.write(f"- Número {num}: {fichas} fichas ({fichas_base:.0f} base × {st.session_state.multiplicador_aposta}x)")
        
        # Alerta visual para próximo aumento
        reds_para_proximo_aumento = 3 - (st.session_state.reds_consecutivos % 3)
        if st.session_state.reds_consecutivos > 0:
            if reds_para_proximo_aumento > 0:
                st.warning(f"⚠️ **{reds_para_proximo_aumento} RED(s) para próximo aumento do multiplicador**")
            else:
                st.error("🚨 **PRÓXIMO RED DOBRA O MULTIPLICADOR!**")
    
else:
    st.info("Aguardando primeiro número para iniciar ciclo...")

# Histórico de Multiplicadores
if st.session_state.historico_multiplicadores:
    st.markdown("## 📈 Histórico de Multiplicadores")
    
    ultimos_multiplicadores = st.session_state.historico_multiplicadores[-10:]  # Últimos 10
    for hist in ultimos_multiplicadores:
        if hist['resultado'] == 'DOUBLING':
            st.write(f"🔴 Ciclo {hist['ciclo']}: Multiplicador aumentou para {hist['multiplicador']}x após {hist['reds_consecutivos']} REDs")
        else:
            st.write(f"🟢 Ciclo {hist['ciclo']}: GREEN com multiplicador {hist['multiplicador']}x | Lucro: ${hist['lucro']:+.2f}")

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
    st.markdown("### 📊 Últimos números sorteados")
    ultimos_10 = st.session_state.historico[-10:] if len(st.session_state.historico) >= 10 else st.session_state.historico
    st.write(" → ".join(map(str, ultimos_10)))
