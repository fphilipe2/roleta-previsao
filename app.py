import streamlit as st
import pandas as pd
from collections import deque
num_registros_exibir = 1000  # Define quantos registros serão mostrados em todas as estratégias

# ... (o resto do código permanece igual até as seções de exibição)
# Lista de números proibidos
numeros_proibidos = {
    1: [3, 7, 8, 11, 12, 13, 28, 29, 30, 35, 36],
    36: [1, 2, 4, 14, 15, 16, 19, 20, 21, 24, 33],
    2: [3, 7, 8, 11, 12, 23, 26, 28, 30, 35, 36],
    20: [3, 7, 8, 11, 12, 23, 26, 28, 30, 35, 36],
    3: [1, 2, 9, 14, 17, 20, 21, 22, 25, 31, 34],
    8: [1, 2, 9, 14, 17, 20, 21, 22, 25, 31, 34],
    4: [7, 11, 12, 13, 18, 27, 28, 29, 30, 35, 36],
    33: [7, 11, 12, 13, 18, 27, 28, 29, 30, 35, 36],
    5: [6, 7, 9, 13, 17, 18, 22, 27, 29, 31, 34],
    32: [6, 7, 9, 13, 17, 18, 22, 27, 29, 31, 34],
    6: [0, 3, 5, 10, 15, 16, 19, 23, 24, 26, 32],
    18: [0, 3, 5, 10, 15, 16, 19, 23, 24, 26, 32],
    7: [1, 2, 4, 15, 16, 19, 20, 21, 24, 32, 33],
    9: [0, 3, 5, 8, 10, 23, 24, 26, 30, 32, 35],
    17: [0, 3, 5, 8, 10, 23, 24, 26, 30, 32, 35],
    10: [6, 9, 14, 17, 18, 22, 25, 27, 29, 31, 34],
    0: [6, 9, 14, 17, 18, 22, 25, 27, 29, 31, 34],
    11: [1, 2, 4, 14, 16, 19, 20, 21, 25, 31, 33],
    12: [1, 2, 4, 14, 16, 19, 20, 21, 25, 31, 33],
    13: [1, 4, 5, 15, 16, 19, 20, 21, 24, 32, 33],
    14: [0, 3, 8, 10, 11, 12, 23, 26, 28, 30, 35],
    25: [0, 3, 8, 10, 11, 12, 23, 26, 28, 30, 35],
    15: [6, 7, 9, 13, 18, 22, 27, 28, 29, 34, 36],
    24: [6, 7, 9, 13, 18, 22, 27, 28, 29, 34, 36],
    16: [6, 7, 11, 12, 13, 18, 22, 27, 28, 29, 36],
    19: [6, 7, 11, 12, 13, 18, 22, 27, 28, 29, 36],
    22: [0, 3, 5, 8, 10, 15, 16, 23, 24, 26, 32],
    23: [2, 6, 9, 14, 17, 18, 20, 22, 25, 31, 34],
    26: [2, 6, 9, 14, 17, 18, 20, 22, 25, 31, 34],
    27: [0, 1, 4, 5, 10, 15, 16, 19, 24, 32, 33],
    29: [0, 1, 4, 5, 10, 15, 16, 19, 24, 32, 33],
    28: [1, 2, 4, 14, 15, 16, 19, 20, 21, 24, 33],
    30: [1, 2, 4, 9, 14, 17, 20, 21, 25, 31, 33],
    35: [1, 2, 4, 9, 14, 17, 20, 21, 25, 31, 33],
    31: [0, 3, 5, 8, 10, 11, 12, 23, 26, 30, 35],
    34: [0, 3, 5, 8, 10, 23, 24, 26, 30, 32, 35],
}
duzias = {
    'D1': list(range(1, 13)),
    'D2': list(range(13, 25)),
    'D3': list(range(25, 37))
}

colunas = {
    'C1': [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34],
    'C2': [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35],
    'C3': [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36]
}
# Funções auxiliares para as NOVAS estratégias
def identificar_dúzia(num):
    if num == 0: return '0'
    if 1 <= num <= 12: return 'D1'
    if 13 <= num <= 24: return 'D2'
    return 'D3'

def identificar_coluna(num):
    if num == 0: return '0'
    col_map = {1:1,4:1,7:1,10:1,13:1,16:1,19:1,22:1,25:1,28:1,31:1,34:1,
               2:2,5:2,8:2,11:2,14:2,17:2,20:2,23:2,26:2,29:2,32:2,35:2,
               3:3,6:3,9:3,12:3,15:3,18:3,21:3,24:3,27:3,30:3,33:3,36:3}
    return f'C{col_map.get(num,0)}'

numero_para_grupos = {}
for num in range(37):  # 0-36
    grupos_num = []
    # Verifica dúzia
    for d, nums in duzias.items():
        if num in nums:
            grupos_num.append(d)
    # Verifica coluna
    for c, nums in colunas.items():
        if num in nums:
            grupos_num.append(c)
    numero_para_grupos[num] = grupos_num
st.set_page_config(page_title="Bot de Estratégias para Roleta", layout="wide")
def vizinhos(numero):
    """Retorna os 5 números vizinhos de cada lado do número na roleta"""
    return [(numero + i) % 37 for i in range(-5, 6)]  # %37 para garantir que fique entre 0-36

# Inicialização do session state
# Limite aumentado para 2500
if 'padrao_3_seq' not in st.session_state:
    st.session_state.padrao_3_seq = []
if 'historico' not in st.session_state:
    st.session_state.historico = []
if 'reflexiva_seq' not in st.session_state:
    st.session_state.reflexiva_seq = []
if 'alternancia_dupla_seq' not in st.session_state:
    st.session_state.alternancia_dupla_seq = []
if 'estrategia_2dz_seq' not in st.session_state:
    st.session_state.estrategia_2dz_seq = []
if 'estrategia_2cl_seq' not in st.session_state:
    st.session_state.estrategia_2cl_seq = []

# Função para atualizar todas as estratégias
def atualizar_estrategias():
    # Limpa as sequências antes de recalculá-las (importante ao carregar um novo CSV)
    st.session_state.reflexiva_seq = []
    st.session_state.alternancia_dupla_seq = []
    st.session_state.estrategia_2dz_seq = []
    st.session_state.estrategia_2cl_seq = []

    # Processa cada número no histórico para atualizar as estratégias
    for i in range(1, len(st.session_state.historico)):
        ant = st.session_state.historico[i-1]
        atual = st.session_state.historico[i]

        # Estratégia Reflexiva
        if ant in numeros_proibidos and atual in numeros_proibidos[ant]:
            st.session_state.reflexiva_seq.append('X')
        else:
            st.session_state.reflexiva_seq.append('1')

        # Estratégia Alternância Dupla
        if ant == 0:
            resultado = 'X'
        else:
            grupos_ant = numero_para_grupos[ant]
            grupos_atual = numero_para_grupos[atual]
            resultado = '1' if any(grupo in grupos_atual for grupo in grupos_ant) else 'X'
        st.session_state.alternancia_dupla_seq.append(resultado)

        # Estratégia 2DZ (Dúzias) - Requer pelo menos 3 números
        if i >= 2:
            ultimas_dz = []
            for num in reversed(st.session_state.historico[:i]):  # Pega os números anteriores
                dz = identificar_dúzia(num)
                if dz != '0' and dz not in ultimas_dz:
                    ultimas_dz.append(dz)
                    if len(ultimas_dz) == 2: break
            
            dz_atual = identificar_dúzia(atual)
            if dz_atual == '0':
                st.session_state.estrategia_2dz_seq.append('<span style="color:green">0</span>')
            elif dz_atual in ultimas_dz:
                st.session_state.estrategia_2dz_seq.append('1')
            else:
                st.session_state.estrategia_2dz_seq.append('<span style="color:red">X</span>')

        # Estratégia 2CL (Colunas) - Requer pelo menos 3 números
        if i >= 2:
            ultimas_cl = []
            for num in reversed(st.session_state.historico[:i]):  # Pega os números anteriores
                cl = identificar_coluna(num)
                if cl != '0' and cl not in ultimas_cl:
                    ultimas_cl.append(cl)
                    if len(ultimas_cl) == 2: break
            
            cl_atual = identificar_coluna(atual)
            if cl_atual == '0':
                st.session_state.estrategia_2cl_seq.append('<span style="color:green">0</span>')
            elif cl_atual in ultimas_cl:
                st.session_state.estrategia_2cl_seq.append('1')
            else:
                st.session_state.estrategia_2cl_seq.append('<span style="color:red">X</span>')

    # Limita o histórico a 2500 registros
    for seq in [
        st.session_state.reflexiva_seq,
        st.session_state.alternancia_dupla_seq,
        st.session_state.estrategia_2dz_seq,
        st.session_state.estrategia_2cl_seq
    ]:
        if len(seq) > 2500:
            seq = seq[-2500:]  # Mantém apenas os últimos 2500
                # ... (mantenha o código das outras estratégias)

# --- Estratégia Padrão de 3 Números ---
    st.session_state.padrao_3_seq = []
    if len(st.session_state.historico) >= 4:
        for i in range(2, len(st.session_state.historico)-1):
            num1, num2, num3 = st.session_state.historico[i-2], st.session_state.historico[i-1], st.session_state.historico[i]
            proximo = st.session_state.historico[i+1]
            
            # Pega vizinhos dos últimos 2 números do trio
            vizinhos_comb = set(vizinhos(num2)) | set(vizinhos(num3))
            
            if proximo in vizinhos_comb:
                st.session_state.padrao_3_seq.append("1")
            else:
                st.session_state.padrao_3_seq.append("X")
    
    if len(st.session_state.padrao_3_seq) > 2500:
        st.session_state.padrao_3_seq = st.session_state.padrao_3_seq[-2500:]


# Funções de formatação
def formatar_reflexiva(seq):
    res = []
    cont = 1
    for val in seq:
        if val == 'X':
            res.append('<span style="color:red">X</span>')
            cont = 1
        else:
            res.append(str(cont))
            cont += 1
    return '<br>'.join([''.join(res[i:i+50]) for i in range(0, len(res), 50)])

def formatar_alternancia(seq):
    res = ['<span style="color:red">X</span>' if v == 'X' else v for v in seq]
    return '<br>'.join([''.join(res[i:i+50]) for i in range(0, len(res), 50)])

# Interface principal
st.title("Bot de Estratégias para Roleta")

# Upload de CSV

uploaded_file = st.file_uploader("Importar histórico (CSV)", type="csv")
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        if 'Número' in df.columns:
            st.session_state.historico = df['Número'].tolist()
            if st.session_state.historico:
                atualizar_estrategias()
                st.success("Histórico carregado e estratégias atualizadas!")
            else:
                st.warning("O CSV está vazio ou não contém números válidos.")
        else:
            st.error("O arquivo CSV deve ter uma coluna chamada 'Número'.")
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")



# Controles de números
novo = st.number_input("Novo número da roleta", min_value=0, max_value=36, step=1)
col1, col2 = st.columns([1, 5])
with col1:
    if st.button("Adicionar número"):
        st.session_state.historico.append(novo)
        atualizar_estrategias(st.session_state.historico)

if st.button("⛔ Excluir último número"):
    if st.session_state.historico:
        st.session_state.historico.pop()
        atualizar_estrategias(st.session_state.historico)


# Exportar histórico
csv_export = pd.DataFrame({'Número': st.session_state.historico}).to_csv(index=False).encode('utf-8')
st.download_button("📥 Exportar histórico CSV", data=csv_export, file_name='historico.csv')

# ========== EXIBIÇÃO DOS RESULTADOS ==========
# Resultados por número (Reflexiva)
st.subheader("Resultados por Número (Reflexiva)")
por_numero = {n: deque(maxlen=20) for n in range(37)}
for i in range(1, len(st.session_state.historico)):
    ant, atual = st.session_state.historico[i-1], st.session_state.historico[i]
    por_numero[ant].append("X" if (ant in numeros_proibidos and atual in numeros_proibidos[ant]) else "1")
col1, col2, col3 = st.columns(3)
for i, col in zip(range(0, 37, 12), [col1, col2, col3]):
    with col:
        for j in range(i, i + 12):
            st.write(f"{j} = {' '.join(por_numero[j])}")

# Estratégia Reflexiva
# Aumente o número de registros exibidos (opcional)
num_registros_exibir = 1000  # Você pode ajustar para 500, 1000, etc.

st.subheader("Resultados Reflexiva - sequência completa")
st.markdown(''.join([
    '<span style="color:red">X</span>' if v == 'X' else v 
    for v in st.session_state.reflexiva_seq[:]
]), unsafe_allow_html=True)

# Repita o mesmo para as outras estratégias...

# Estratégia Alternância Dupla
st.subheader("Resultados Estratégia de Alternância Dupla")
st.markdown(''.join([
    '<span style="color:red">X</span>' if v == 'X' else v 
    for v in st.session_state.alternancia_dupla_seq[:]  # Alterado para usar a variável
]), unsafe_allow_html=True)

# ========== NOVAS ESTRATÉGIAS ==========
# Estratégia 2DZ (Dúzias)
st.subheader("Estratégia 2DZ (2 Últimas Dúzias + Zero)")
resultados_formatados = []
for item in st.session_state.estrategia_2dz_seq[:]:  # Alterado para usar a variável
    if item == '0':
        resultados_formatados.append('<span style="color:green">0</span>')
    elif item == 'X':
        resultados_formatados.append('<span style="color:red">X</span>')
    else:
        resultados_formatados.append(item)
st.markdown(''.join(resultados_formatados), unsafe_allow_html=True)

# Estratégia 2CL (Colunas)
st.subheader("Estratégia 2CL (2 Últimas Colunas + Zero)")
resultados_formatados = []
for item in st.session_state.estrategia_2cl_seq[:]:  # Alterado para usar a variável
    if item == '0':
        resultados_formatados.append('<span style="color:green">0</span>')
    elif item == 'X':
        resultados_formatados.append('<span style="color:red">X</span>')
    else:
        resultados_formatados.append(item)
st.markdown(''.join(resultados_formatados), unsafe_allow_html=True)

st.subheader("Padrão de 3 Números - Resultados")
if st.session_state.padrao_3_seq:
    html_resultados = ''.join([
        '<span style="color:green">1</span>' if v == '1' 
        else '<span style="color:red">X</span>' 
        for v in st.session_state.padrao_3_seq[-num_registros_exibir:]
    ])
    st.markdown(html_resultados, unsafe_allow_html=True)
else:
    st.write("Aguardando dados suficientes (mínimo 4 números no histórico)")




