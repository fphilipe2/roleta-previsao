import streamlit as st
import pandas as pd
from datetime import datetime
from collections import deque

# Lista de números proibidos (mesmo conteúdo)
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

st.set_page_config(page_title="Bot de Estratégias para Roleta", layout="wide")

# Sessões e histórico
if 'historico' not in st.session_state:
    st.session_state.historico = []
if 'reflexiva_seq' not in st.session_state:
    st.session_state.reflexiva_seq = []
if 'alternancia_dupla_seq' not in st.session_state:
    st.session_state.alternancia_dupla_seq = []

st.title("Bot de Estratégias para Roleta")

# Upload CSV
uploaded_file = st.file_uploader("Importar histórico (CSV)", type="csv")
if uploaded_file:
    dados_csv = pd.read_csv(uploaded_file)['Número'].tolist()
    if 'historico' not in st.session_state or not st.session_state.historico:
        st.session_state.historico = dados_csv
    else:
        st.session_state.historico.extend(dados_csv)

# Inserir novo número
novo = st.number_input("Novo número da roleta", min_value=0, max_value=36, step=1)
col1, col2 = st.columns([1, 5])
with col1:
    if st.button("Adicionar número"):
        st.session_state.historico.append(novo)
        # Botão para remover o último número
if st.button("⛔ Excluir último número"):
    if st.session_state.historico:
        removido = st.session_state.historico.pop()
        st.warning(f"Número {removido} removido do histórico.")
    else:
        st.warning("O histórico está vazio.")

    # Reflexiva
    if len(st.session_state.historico) >= 2:
        ant = st.session_state.historico[-2]
        atual = st.session_state.historico[-1]
        if ant in numeros_proibidos and atual in numeros_proibidos[ant]:
            res = 'X'
        else:
            res = '1'
        st.session_state.reflexiva_seq.append(res)
        if len(st.session_state.reflexiva_seq) > 250:
            st.session_state.reflexiva_seq.pop(0)

    # Alternância Dupla por grupo
    grupos = [
        [1, 4, 7, 10], [2, 5, 8, 11], [3, 6, 9, 12],
        [13, 16, 19, 22], [14, 17, 20, 23], [15, 18, 21, 24],
        [25, 28, 31, 34], [26, 29, 32, 35], [27, 30, 33, 36]
    ]
    if len(st.session_state.historico) >= 2:
        ant = st.session_state.historico[-2]
        atual = st.session_state.historico[-1]
        for grupo in grupos:
            if ant in grupo:
                if atual in grupo:
                    st.session_state.alternancia_dupla_seq.append('1')
                else:
                    st.session_state.alternancia_dupla_seq.append('X')
                if len(st.session_state.alternancia_dupla_seq) > 250:
                    st.session_state.alternancia_dupla_seq.pop(0)
                break

# Exportar histórico com botão de download
df_export = pd.DataFrame({'Número': st.session_state.historico})
csv_export = df_export.to_csv(index=False).encode('utf-8')

st.download_button(
    label="📥 Exportar histórico CSV",
    data=csv_export,
    file_name='historico_atualizado.csv',
    mime='text/csv',
)

# Resultados por número (Reflexiva)
st.subheader("Resultados por Número (Reflexiva)")
por_numero = {n: deque(maxlen=20) for n in range(37)}
for i in range(1, len(st.session_state.historico)):
    ant = st.session_state.historico[i - 1]
    atual = st.session_state.historico[i]
    if ant in numeros_proibidos and atual in numeros_proibidos[ant]:
        por_numero[ant].append("X")
    else:
        por_numero[ant].append("1")
col1, col2, col3 = st.columns(3)
for i, col in zip(range(0, 37, 12), [col1, col2, col3]):
    with col:
        for j in range(i, i + 12):
            resultados = ' '.join(por_numero[j])
            st.write(f"{j} = {resultados}")

# Retorna os 5 vizinhos anteriores e 5 posteriores (com rotação de 0 a 36)
def vizinhos(numero):
    return [(numero + i) % 37 for i in range(-5, 6)]

st.subheader("📊 Simulação Completa - Estratégia: Padrão de 3 Números (Histórico)")

banca_inicial = 600
banca = banca_inicial
gales = [22, 44, 132, 396]
historico = st.session_state.historico
resultados_simulados = []

# Armazenar padrões já testados para evitar repetições
padroes_testados = set()

for i in range(len(historico) - 5):
    padrao_base = set(historico[i:i+3])
    if len(padrao_base) < 3 or tuple(sorted(padrao_base)) in padroes_testados:
        continue

    # Procurar nova ocorrência do padrão
    for j in range(i+3, len(historico) - 2):
        proximo_padrao = set(historico[j:j+3])
        if padrao_base == proximo_padrao:
            p1, p2 = historico[j], historico[j+1]
            padroes_testados.add(tuple(sorted(padrao_base)))
            
            try:
                vizinhos_roleta = {
    0: [0, 26, 3, 35, 12, 28, 32, 15, 19, 4, 21],
    1: [1, 33, 16, 24, 5, 10, 20, 14, 31, 9, 22],
    2: [2, 21, 4, 19, 15, 32, 25, 17, 34, 6, 27],
    3: [3, 35, 12, 28, 7, 29, 26, 0, 32, 15, 19],
    4: [4, 19, 15, 32, 0, 26, 21, 2, 25, 17, 34],
    5: [5, 24, 16, 33, 1, 20, 10, 23, 8, 30, 11],
    6: [6, 34, 17, 25, 2, 21, 27, 13, 36, 11, 30],
    7: [7, 29, 18, 22, 9, 31, 28, 12, 35, 3, 26],
    8: [8, 30, 11, 36, 13, 27, 23, 10, 5, 24, 16],
    9: [9, 31, 14, 20, 1, 33, 22, 18, 29, 7, 28],
    10:[10, 23, 8, 30, 11, 36, 5, 24, 16, 33, 1],
    11: [11, 36, 13, 27, 6, 34, 30, 8, 23, 10, 5],
    12: [12, 28, 7, 29, 18, 22, 35, 3, 26, 0, 32],
    13: [13, 27, 6, 34, 17, 25, 36, 11, 30, 8, 23],
    14: [14, 20, 1, 33, 16, 24, 31, 9, 22, 18, 29],
    15: [15, 32, 0, 26, 3, 35, 19, 4, 21, 2, 25],
    16: [16, 24, 5, 10, 23, 8, 33, 1, 20, 14, 31],
    17: [17, 25, 2, 21, 4, 19, 34, 6, 27, 13, 36],
    18: [18, 22, 9, 31, 14, 20, 29, 7, 28, 12, 35],
    19: [19, 15, 32, 0, 26, 3, 4, 21, 2, 25, 17],
    20: [20, 14, 31, 9, 22, 18, 1, 33, 16, 24, 5],
    21: [21, 4, 19, 15, 32, 0, 2, 25, 17, 34, 6],
    22: [22, 18, 29, 7, 28, 12, 9, 31, 14, 20, 1],
    23: [23, 10, 5, 24, 16, 33, 8, 30, 11, 36, 13],
    24: [24, 16, 33, 1, 20, 14, 5, 10, 23, 8, 30],
    25: [25, 2, 21, 4, 19, 15, 17, 34, 6, 27, 13],
    26: [26, 3, 35, 12, 28, 7, 0, 32, 15, 19, 4],
    27: [27, 6, 34, 17, 25, 2, 13, 36, 11, 30, 8],
    28: [28, 12, 35, 3, 26, 0, 7, 29, 18, 22, 9],
    29: [29, 7, 28, 12, 35, 3, 18, 22, 9, 31, 14],
    30: [30, 11, 36, 13, 27, 6, 8, 23, 10, 5, 24],
    31: [31, 9, 22, 18, 29, 7, 14, 20, 1, 33, 16],
    32: [32, 0, 26, 3, 35, 12, 15, 19, 4, 21, 2],
    33: [33, 1, 20, 14, 31, 9, 16, 24, 5, 10, 23],
    34: [34, 17, 25, 2, 21, 4, 6, 27, 13, 36, 11],
    35: [35, 12, 28, 7, 29, 18, 3, 26, 0, 32, 15],
    36: [36, 13, 27, 6, 34, 17, 11, 30, 8, 23, 10]
}

               def obter_vizinhos_completos(numero):
    """Retorna o número + 5 vizinhos de cada lado (11 números no total)"""
    return vizinhos_fisicos.get(numero, [numero])  # Fallback para o próprio número se não encontrado

# Na simulação:
for i in range(len(historico) - 5):
    padrao_base = historico[i:i+3]  # Sequência de 3 números
    
    # Busca padrão repetido
    for j in range(i+3, len(historico) - 2):
        if historico[j:j+3] == padrao_base:
            p1, p2 = historico[j+3], historico[j+4]  # Dois números após o padrão
            
            # Obter vizinhos de p1 e p2 (11 números cada)
            numeros_aposta = obter_vizinhos_completos(p1) + obter_vizinhos_completos(p2)
            
            # Remover duplicatas e ordenar
            viz = sorted(list(set(numeros_aposta)))
            
            st.write(f"Padrão detectado: {set(padrao_base)}. V{p1}V{p2}: {viz}")

                contagem_fichas = {}
                for num in numeros_aposta:
                    contagem_fichas[num] = contagem_fichas.get(num, 0) + 1

                resultado = ""
                tentativa_realizada = False

                for gale_index, valor in enumerate(gales):
                    sorteio_index = j + 2 + gale_index
                    if sorteio_index >= len(historico):
                        break
                    sorteado = historico[sorteio_index]
                    fichas = contagem_fichas.get(sorteado, 0)

                    if fichas > 0:
                        premio = 36 * fichas
                        saldo = premio - sum(gales[:gale_index + 1])
                        banca += saldo
                        resultado = f"✅ GREEN no Gale {gale_index} ({sorteado}) - Ganhou R$ {premio} (saldo {saldo:+})"
                        tentativa_realizada = True
                        break
                    else:
                        banca -= valor
                        resultado = f"❌ RED no Gale {gale_index} ({sorteado}) - Perdeu R$ {valor}"

                if tentativa_realizada or gale_index == len(gales) - 1:
                    resultados_simulados.append(f"Padrão: {padrao_base} - Palpite: V{p1}V{p2} - {resultado}")

            except Exception as e:
                st.error(f"Erro na simulação: {e}")

            break  # sair após encontrar uma repetição

# Mostrar resultados
for r in resultados_simulados[-5:]:
    st.write(r)

st.markdown(f"**Banca Inicial:** R$ {banca_inicial}")
st.markdown(f"**Banca Final:** R$ {banca:.2f}")
st.markdown(f"**Lucro/Prejuízo:** R$ {banca - banca_inicial:.2f}")

# Estratégia Reflexiva - sequência completa
st.subheader("Resultados Reflexiva - sequência completa")
def formatar_reflexiva(seq):
    res = []
    cont = 1
    for i, val in enumerate(seq):
        if val == 'X':
            res.append('<span style="color:red">X</span>')
            cont = 1
        else:
            res.append(str(cont))
            cont += 1
    linhas = [''.join(res[i:i+50]) for i in range(0, len(res), 50)]
    return '<br>'.join(linhas)
st.markdown(formatar_reflexiva(st.session_state.reflexiva_seq), unsafe_allow_html=True)

# Estratégia Alternância Dupla - Dúzia e Coluna
st.subheader("Resultados Estratégia de Alternância Dupla (Dúzia e Coluna)")
def formatar_estrategia(seq):
    res = []
    for v in seq:
        if v == 'X':
            res.append('<span style="color:red">X</span>')
        else:
            res.append(v)
    linhas = [''.join(res[i:i+50]) for i in range(0, len(res), 50)]
    return '<br>'.join(linhas)
st.markdown(formatar_estrategia(st.session_state.alternancia_dupla_seq), unsafe_allow_html=True)

# Estratégia: Padrão de 3 Números (Repetição em qualquer ordem)
st.subheader("Estratégia: Padrão de 3 Números (Repetição em qualquer ordem)")

if len(st.session_state.historico) >= 5:
    ultimos = st.session_state.historico[-3:]
    ultimos_set = set(ultimos)

    for i in range(len(st.session_state.historico) - 5):
        padrao = st.session_state.historico[i:i+3]
        if set(padrao) == ultimos_set:
            if i + 5 < len(st.session_state.historico):
                p1 = st.session_state.historico[i+3]
                p2 = st.session_state.historico[i+4]
                try:
                    viz1 = vizinhos(p1)
                    viz2 = vizinhos(p2)
                    viz = sorted(set(viz1 + viz2))
                    st.write(f"Padrão detectado: {set(padrao)}. V{p1}V{p2}: {viz}")
                except Exception as e:
                    st.error(f"Erro ao gerar vizinhos: {e}")
            break

# Estratégia: Padrão de 3 Números (Repetição em qualquer ordem) - SIMULAÇÃO DE BANCA
st.subheader("Simulação de Banca - Estratégia: Padrão de 3 Números (Repetição em qualquer ordem)")

banca_inicial = 600
banca = banca_inicial
gales = [22, 44, 132, 396]
resultados_simulados = []
padroes_testados = set()

# Função auxiliar para calcular contagem de fichas
def contar_fichas(numeros, total_fichas):
    contagem = {}
    for n in numeros:
        contagem[n] = contagem.get(n, 0) + total_fichas // len(numeros)
    return contagem

# Simulação com base no histórico
for i in range(len(historico) - 7):
    padrao = historico[i:i+3]
    if len(set(padrao)) < 3:
        continue

    for j in range(i+3, len(historico) - 5):
        if set(historico[j:j+3]) == set(padrao) and tuple(sorted(padrao)) not in padroes_testados:
            p1, p2 = historico[j+3], historico[j+4]

            # Obter vizinhos reais (usando mapa de 11 vizinhos reais se possível)
            viz1 = vizinhos(p1)
            viz2 = vizinhos(p2)
            palpite = sorted(set(viz1 + viz2 + [p1, p2]))

            padroes_testados.add(tuple(sorted(padrao)))
            st.write(f"Padrão detectado: {set(padrao)}. V{p1}V{p2}: {palpite}")

            resultado = ""
            tentativa_realizada = False
            contagem = {}

            for gale_index, entrada in enumerate(gales):
                idx_sorteio = j + 5 + gale_index
                if idx_sorteio >= len(historico):
                    break

                sorteado = historico[idx_sorteio]
                contagem = contar_fichas(palpite, entrada)
                fichas_sorteado = contagem.get(sorteado, 0)

                if fichas_sorteado > 0:
                    premio = fichas_sorteado * 36
                    custo = sum(gales[:gale_index + 1])
                    saldo = premio - custo
                    banca += saldo
                    resultado = f"✅ GREEN no Gale {gale_index} (nº {sorteado}) - Fichas: {fichas_sorteado} - Saldo: R$ {saldo}"
                    tentativa_realizada = True
                    break
                else:
                    banca -= entrada

            if not tentativa_realizada:
                resultado = f"❌ RED - Perdeu R$ {sum(gales)}"

            resultados_simulados.append(f"Padrão: {set(padrao)} - Palpite: V{p1}V{p2} - {resultado}")
            break  # vai para o próximo padrão base


    for r in resultados_simulados[-5:]:
    st.write(r)

st.markdown(f"**Banca Inicial:** R$ {banca_inicial}")
st.markdown(f"**Banca Final:** R$ {banca:.2f}")
st.markdown(f"**Lucro/Prejuízo:** R$ {banca - banca_inicial:.2f}")

