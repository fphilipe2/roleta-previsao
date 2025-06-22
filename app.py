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
                    0: [32, 15, 19, 4, 21, 2, 25, 17, 34, 6],
                    1: [20, 14, 31, 9, 22, 18, 29, 7, 28, 12],
                    2: [21, 4, 19, 15, 32, 0, 26, 3, 35, 12],
                    3: [26, 0, 32, 15, 19, 4, 21, 2, 25, 17],
                    4: [19, 15, 32, 0, 26, 3, 35, 12, 28, 7],
                    5: [24, 16, 33, 1, 20, 14, 31, 9, 22, 18],
                    6: [27, 13, 36, 11, 30, 8, 23, 10, 5, 24],
                    7: [28, 12, 5, 24, 16, 33, 1, 20, 14, 31],
                    8: [30, 11, 5, 24, 16, 33, 1, 20, 14, 31],
                    9: [22, 18, 29, 7, 28, 12, 5, 24, 16, 33],
                    10: [23, 8, 30, 11, 5, 24, 16, 33, 1, 20],
                    11: [30, 8, 23, 10, 5, 24, 16, 33, 1, 20],
                    12: [28, 7, 29, 18, 22, 9, 31, 14, 20, 1]
                }

                viz_p1 = vizinhos_roleta.get(p1, [])
                viz_p2 = vizinhos_roleta.get(p2, [])
                viz = list(set(viz_p1 + viz_p2 + [p1, p2]))

                st.write(f"Padrão detectado: {set(padrao_base)}. V{p1}V{p2}: {sorted(viz)}")

                contagem_fichas = {}
                for num in viz:
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


                contagem_fichas = {}
                for num in viz:
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
tentativas = 0
resultado = ""
ganho = 0

# Se houver palpite armazenado, simula a entrada
if 'padrao_3n_palpite' in st.session_state:
    alvo = st.session_state.padrao_3n_palpite  # lista com os 22 números
    jogadas = st.session_state.historico[-(len(gales)+1):]  # pega últimas jogadas

    for i, entrada in enumerate(gales):
        if len(jogadas) <= i:
            break  # ainda não houve essa jogada

        numero_sorteado = jogadas[-(len(gales) - i)]

        # Contar quantas fichas cada número recebeu
        contagem_fichas = {}
        for num in alvo:
            contagem_fichas[num] = contagem_fichas.get(num, 0) + entrada // 22

        fichas_no_sorteado = contagem_fichas.get(numero_sorteado, 0)
        if fichas_no_sorteado > 0:
            premio = 36 * fichas_no_sorteado
            ganho = premio
            resultado = f"🎯 GREEN no Gale {i} (nº {numero_sorteado}) com {fichas_no_sorteado} ficha(s)"
            break
        else:
            banca -= entrada
            resultado = f"❌ RED no Gale {i} (nº {numero_sorteado})"

    # Se houve ganho, computar saldo
    if ganho:
        banca += ganho

    st.markdown(f"**Resultado:** {resultado}")
    st.markdown(f"**Banca Atual:** R$ {banca:.2f}")
    st.markdown(f"**Ganho Líquido:** R$ {banca - banca_inicial:.2f}")




