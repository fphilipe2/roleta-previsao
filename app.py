import streamlit as st
import pandas as pd
from datetime import datetime
from collections import deque
import base64

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
from numeros_proibidos import numeros_proibidos

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

# Botão para excluir último número
if st.button("Excluir último número") and st.session_state.historico:
    st.session_state.historico.pop()

# Exportar histórico
if st.button("Exportar histórico CSV"):
    df = pd.DataFrame({'Número': st.session_state.historico})
    df.to_csv("historico_atualizado.csv", index=False)
    st.success("Histórico exportado com sucesso!")

# Estratégia Reflexiva - associar resultado ao número anterior
resultado_reflexivo = [''] * len(st.session_state.historico)
por_numero = {n: [] for n in range(37)}

for i in range(1, len(st.session_state.historico)):
    ant = st.session_state.historico[i - 1]
    atual = st.session_state.historico[i]
    if ant in numeros_proibidos and atual in numeros_proibidos[ant]:
        resultado_reflexivo[i - 1] = "X"
        por_numero[ant].append("X")
    else:
        resultado_reflexivo[i - 1] = "1"
        por_numero[ant].append("1")

    if len(por_numero[ant]) > 20:
        por_numero[ant].pop(0)

# Mostrar reflexiva por faixa (3 colunas)
st.subheader("Resultados por Número (Reflexiva)")
col1, col2, col3 = st.columns(3)

alarme_ativo = False

def mostrar_resultados(coluna, inicio, fim):
    global alarme_ativo
    with coluna:
        for n in range(inicio, fim + 1):
            ultimos = por_numero[n]
            alert_style = ""
            if ultimos[-2:] == ["X", "X"] or ultimos.count("X") >= 2 and len(ultimos) >= 3:
                alert_style = "background-color: #ffcccc; border: 2px solid red; padding: 4px;"
                alarme_ativo = True
            st.markdown(f"<div style='{alert_style}'><strong>{n}</strong> = {' '.join(ultimos)}</div>", unsafe_allow_html=True)

mostrar_resultados(col1, 0, 11)
mostrar_resultados(col2, 12, 24)
mostrar_resultados(col3, 25, 36)

# Som de alarme (uma vez por alerta)
if alarme_ativo:
    st.audio("https://www.soundjay.com/button/beep-07.wav", format="audio/wav")

# Exibir sequência completa com contagem e quebra de linha
st.subheader("Resultados Reflexiva - sequência completa")

sequencia = []
contador = 1

for res in resultado_reflexivo[-250:]:
    if res == '1':
        sequencia.append(str(contador))
        contador += 1
    elif res == 'X':
        sequencia.append('<span style="color:red;"><strong>X</strong></span>')
        contador = 1

# Agrupar por linha com até 50 caracteres
linhas = []
linha = ''
for s in sequencia:
    if len(linha) + len(s) > 50:
        linhas.append(linha)
        linha = ''
    linha += s
if linha:
    linhas.append(linha)

html = "<div style='font-family: monospace; line-height: 1.5;'>"
for linha in linhas:
    html += f"{linha}<br>"
html += "</div>"

st.markdown(html, unsafe_allow_html=True)

# Estratégias por alternância
st.subheader("Alertas por repetição (a partir de 9 vezes)")
def alertar_repeticoes(tipo):
    if len(st.session_state.historico) < 2:
        return
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
