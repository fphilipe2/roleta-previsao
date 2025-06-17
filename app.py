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
from numeros_proibidos import numeros_proibidos  # Supondo que você mova esse dicionário para outro arquivo

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

# Estratégia de 3 números (em qualquer ordem)
st.subheader("Palpite por sequência de 3 números (qualquer ordem)")
if len(st.session_state.historico) >= 5:
    ultimos = set(st.session_state.historico[-3:])
    for i in range(len(st.session_state.historico) - 5):
        seq = set(st.session_state.historico[i:i+3])
        if seq == ultimos:
            p1 = st.session_state.historico[i+3]
            p2 = st.session_state.historico[i+4]
            viz = sorted(set(vizinhos(p1) + vizinhos(p2)))
            st.write(f"Palpite: V{p1}V{p2} => {viz}")
            break

# Estratégias por alternância
st.subheader("Alertas por repetição (a partir de 9 vezes)")
def alertar_repeticoes(tipo):
    contagem = 1
    ultimo = tipo(st.session_state.historico[0])
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
