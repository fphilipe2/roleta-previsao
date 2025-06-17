import streamlit as st
import pandas as pd
import os

ARQUIVO_RESULTADOS = "dados.csv"
ARQUIVO_ESTRATEGIAS = "historico_estrategias.csv"

st.title("Roleta - Previsão e Simulação de Banca")

# Funções auxiliares

def vizinhos(numero):
    viz = []
    for i in range(-5, 6):
        n = (numero + i) % 37
        viz.append(n)
    return viz

def encontrar_palpite_sequencia(historico):
    if len(historico) < 5:
        return "Histórico insuficiente para gerar palpites."

    ultimos = historico[-3:]
    conjunto_ultimos = set(ultimos)
    for i in range(len(historico) - 5):
        bloco = historico[i:i+3]
        if set(bloco) == conjunto_ultimos:
            proximo1 = historico[i+3]
            proximo2 = historico[i+4]
            palpite_final = set(vizinhos(proximo1) + vizinhos(proximo2))
            return f"Palpite por sequência: V{proximo1}V{proximo2} → Jogar nos números: {sorted(palpite_final)}"

    return "Nenhuma sequência correspondente encontrada."

def obter_dozia(numero):
    if 1 <= numero <= 12:
        return "D1"
    elif 13 <= numero <= 24:
        return "D2"
    elif 25 <= numero <= 36:
        return "D3"
    else:
        return "D0"

def estrategia_duzias(historico):
    if len(historico) < 3:
        return "Histórico insuficiente para estratégia de dúzias."

    ultimos = historico[-3:]

    if 0 in ultimos:
        pos_0 = ultimos.index(0)
        if pos_0 < 2:
            ultimos = historico[-(3+pos_0):-1]

    duzias = [obter_dozia(n) for n in ultimos]

    if len(set(duzias)) == 3:
        return "Alternância completa detectada. Aguardar nova repetição."

    if len(set(duzias)) == 1:
        return "Dúzia repetida detectada. Zerar contagem."

    faltante = {"D1", "D2", "D3"} - set(duzias)
    if faltante:
        return f"Palpite por alternância: Apostar na dúzia {faltante.pop()}"
    return "Nenhum palpite gerado."

# Carrega histórico se existir
if os.path.exists(ARQUIVO_ESTRATEGIAS):
    df_hist = pd.read_csv(ARQUIVO_ESTRATEGIAS)
    historico = df_hist['Numero'].tolist()
else:
    df_hist = pd.DataFrame(columns=["Numero"])
    historico = []

# Upload de arquivo CSV
st.subheader("Importar histórico de números da roleta")
file = st.file_uploader("Escolha um arquivo CSV", type=["csv"])
if file is not None:
    df_importado = pd.read_csv(file)
    if 'Numero' in df_importado.columns:
        historico = df_importado['Numero'].tolist()
        df_hist = df_importado.copy()
        st.success("Histórico importado com sucesso.")
    else:
        st.error("O CSV deve conter uma coluna chamada 'Numero'.")

# Adição de novo número
st.subheader("Adicionar novo número da roleta")
novo_numero = st.number_input("Digite o número (0 a 36):", min_value=0, max_value=36, step=1)
if st.button("Adicionar número"):
    historico.append(novo_numero)
    df_hist = pd.DataFrame(historico, columns=["Numero"])
    df_hist.to_csv(ARQUIVO_ESTRATEGIAS, index=False)
    st.success("Número adicionado ao histórico.")

# Exibir histórico atualizado
st.subheader("Histórico Atual")
st.dataframe(df_hist.tail(30))

# Palpites
st.subheader("Palpites")
st.info(encontrar_palpite_sequencia(historico))
st.info(estrategia_duzias(historico))

# Download do histórico
st.subheader("Exportar Histórico")
st.download_button("Baixar histórico CSV", df_hist.to_csv(index=False).encode('utf-8'), file_name='historico_estrategias.csv', mime='text/csv')
