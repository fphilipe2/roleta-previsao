import streamlit as st
import pandas as pd
from datetime import datetime
from collections import deque

# Funções auxiliares para análise

def vizinhos(numero):
    return [(numero + i) % 37 for i in range(-5, 6)]

def obter_duzia(numero):
    if numero == 0:
        return 0
    return (numero - 1) // 12 + 1

def obter_coluna(numero):
    if numero == 0:
        return 0
    return (numero - 1) % 3 + 1

def obter_cor(numero):
    vermelhos = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
    if numero == 0:
        return 'verde'
    return 'vermelho' if numero in vermelhos else 'preto'

def obter_paridade(numero):
    if numero == 0:
        return 'zero'
    return 'par' if numero % 2 == 0 else 'ímpar'

def obter_alto_baixo(numero):
    if numero == 0:
        return 'zero'
    return 'baixo' if numero <= 18 else 'alto'

# Lista de números proibidos (mesmo conteúdo)
numeros_proibidos = {
    1: [3, 8, 11, 12, 13, 28, 29, 30, 35, 36],
    36: [3, 8, 11, 12, 13, 28, 29, 30, 35, 36],
    2: [3, 7, 8, 11, 12, 23, 26, 28, 30, 35, 36],
    20: [3, 7, 8, 11, 12, 23, 26, 28, 30, 35, 36],
    3: [1, 2, 9, 14, 17, 20, 21, 22, 25, 31, 34],
    8: [1, 2, 9, 14, 17, 20, 21, 22, 25, 31, 34],
    4: [7, 11, 12, 13, 18, 27, 28, 29, 30, 35],
    33: [7, 11, 12, 13, 18, 27, 28, 29, 30, 35],
    5: [6, 7, 9, 13, 18, 27, 28, 29, 30, 35, 36],
    32: [6, 7, 9, 13, 18, 27, 28, 29, 30, 35, 36],
    6: [0, 3, 10, 15, 16, 19, 23, 24, 26, 32],
    18: [0, 3, 10, 15, 16, 19, 23, 24, 26, 32],
    7: [1, 2, 4, 15, 16, 19, 20, 21, 24, 32, 33],
    9: [0, 3, 5, 8, 10, 23, 24, 26, 30, 32, 35],
    17: [0, 3, 5, 8, 10, 23, 24, 26, 30, 32, 35],
    10: [6, 9, 14, 17, 18, 22, 25, 27, 29, 31, 34],
    0: [6, 9, 14, 17, 18, 22, 25, 27, 29, 31, 34],
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
    30: [1, 2, 4, 9, 14, 15, 17, 21, 25, 31, 33],
    35: [1, 2, 4, 9, 14, 15, 17, 21, 25, 31, 33],
    31: [0, 3, 5, 8, 10, 11, 12, 23, 26, 30, 35],
    34: [0, 3, 5, 8, 10, 23, 24, 26, 30, 32, 35],
}


# Armazenamento do histórico completo
if 'historico' not in st.session_state:
    st.session_state.historico = []

st.title("Bot de Estratégias para Roleta")

# Upload de CSV
uploaded_file = st.file_uploader("Importar histórico (CSV)", type="csv")
if uploaded_file:
    st.session_state.historico = pd.read_csv(uploaded_file)['Número'].tolist()

# Inserir novo número
novo = st.number_input("Novo número da roleta", min_value=0, max_value=36, step=1)
if st.button("Adicionar número"):
    st.session_state.historico.append(novo)

# Exportar histórico
if st.button("Exportar histórico CSV"):
    df = pd.DataFrame({'Número': st.session_state.historico})
    df.to_csv("historico_atualizado.csv", index=False)
    st.success("Histórico exportado com sucesso!")

# Estratégia Reflexiva
resultado_reflexivo = []
palpites = []
for i in range(1, len(st.session_state.historico)):
    ant = st.session_state.historico[i-1]
    atual = st.session_state.historico[i]
    if ant in numeros_proibidos and atual in numeros_proibidos[ant]:
        resultado_reflexivo.append("X")
    else:
        resultado_reflexivo.append("1")
        palpites.append((i, ant, [n for n in range(37) if n not in numeros_proibidos.get(ant, [])]))

st.subheader("Reflexiva (1 ou X)")
st.markdown(", ".join(resultado_reflexivo))

# Exibir os palpites mais recentes (até 5)
if palpites:
    st.subheader("Palpites de Jogo (últimos 5)")
    for idx, ant, sugestoes in palpites[-5:]:
        st.info(f"Após {ant}, evite {numeros_proibidos.get(ant, [])}. Sugestão: {sugestoes}")

# Histórico reflexivo por número anterior (últimos 5 resultados)
st.subheader("Resultados por Número (reflexiva atribuída ao número anterior)")

# Inicializar dicionário com listas
resultados_por_numero = {n: [] for n in range(37)}

# Preencher o dicionário com base no histórico (resultado vai para o número anterior)
for i in range(1, len(st.session_state.historico)):
    anterior = st.session_state.historico[i - 1]
    atual = st.session_state.historico[i]
    if anterior in numeros_proibidos and atual in numeros_proibidos[anterior]:
        resultados_por_numero[anterior].append("X")
    else:
        resultados_por_numero[anterior].append("1")

# Manter só os 5 mais recentes
for k in resultados_por_numero:
    resultados_por_numero[k] = resultados_por_numero[k][-5:]

# Organizar em 3 colunas: 0–11, 12–24, 25–36
col1, col2, col3 = st.columns(3)

faixa1 = range(0, 12)
faixa2 = range(12, 25)
faixa3 = range(25, 37)

with col1:
    st.markdown("**Números 0 a 11**")
    for n in faixa1:
        resultados = " ".join(resultados_por_numero[n])
        st.text(f"{n:2} = {resultados}")

with col2:
    st.markdown("**Números 12 a 24**")
    for n in faixa2:
        resultados = " ".join(resultados_por_numero[n])
        st.text(f"{n:2} = {resultados}")

with col3:
    st.markdown("**Números 25 a 36**")
    for n in faixa3:
        resultados = " ".join(resultados_por_numero[n])
        st.text(f"{n:2} = {resultados}")

# Estratégias por alternância
st.subheader("Alertas por repetição (a partir de 9 vezes)")
def alertar_repeticoes(tipo):
    contagem = 1
    ultimo = tipo(st.session_state.historico[0]) if st.session_state.historico else None
    for n in st.session_state.historico[1:]:
        atual = tipo(n)
        if atual == ultimo:
            contagem += 1
            if contagem >= 9:
                st.warning(f"Alerta: {tipo.__name__} repetida {contagem} vezes seguidas")
        else:
            contagem = 1
            ultimo = atual

alertar_repeticoes(obter_duzia)
alertar_repeticoes(obter_coluna)
alertar_repeticoes(obter_cor)
alertar_repeticoes(obter_paridade)
alertar_repeticoes(obter_alto_baixo)
