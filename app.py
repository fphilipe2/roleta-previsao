import streamlit as st
import pandas as pd
import os

ARQUIVO_RESULTADOS = "dados.csv"
ARQUIVO_ESTRATEGIAS = "historico_estrategias.csv"

st.title("Roleta - Previsão e Simulação de Banca")

# Função para identificar vizinhos
vizinho_roleta = {
    i: [(i + j) % 37 for j in range(-2, 3)] for i in range(37)
}

# Função nova: Estratégia baseada em combinação de 3 números
@st.cache_data(show_spinner=False)
def estrategia_sequencia(df):
    if len(df) < 5:
        return "Aguardando mais dados."

    ultimos = df[-3:]
    ultimos_set = set(ultimos)
    padroes = [set(df[i:i+3]) for i in range(len(df)-5)]

    for i, p in enumerate(padroes):
        if p == ultimos_set:
            candidatos = df[i+3:i+5]
            vizinhos = set()
            for n in candidatos:
                vizinhos.update(vizinho_roleta.get(n, []))
            recomendados = sorted(vizinhos.union(candidatos))
            return f"Palpite baseado na repetição de padrão: {recomendados}"

    return "Nenhum padrão de 3 encontrado no histórico."

# Estratégia de alternância (dúzias e colunas)
def estrategia_duzias_colunas(df):
    if len(df) < 3:
        return "Aguardando mais dados."

    duzias = {1: list(range(1, 13)), 2: list(range(13, 25)), 3: list(range(25, 37))}
    colunas = {1: list(range(1, 37, 3)), 2: list(range(2, 37, 3)), 3: list(range(3, 37, 3))}

    def get_duzia(n):
        for k, v in duzias.items():
            if n in v: return k
        return 0

    def get_coluna(n):
        for k, v in colunas.items():
            if n in v: return k
        return 0

    ultimos = df[::-1]  # Inverte para analisar do mais recente para o mais antigo
    duz_seq, col_seq = [], []

    for n in ultimos:
        if n == 0:
            if len(duz_seq) >= 2 and len(col_seq) >= 2:
                break
            continue

        d = get_duzia(n)
        c = get_coluna(n)

        if duz_seq and d == duz_seq[-1]:
            duz_seq = []
        else:
            duz_seq.append(d)

        if col_seq and c == col_seq[-1]:
            col_seq = []
        else:
            col_seq.append(c)

        if len(duz_seq) >= 2 and len(col_seq) >= 2:
            break

    return f"Alternância Dúzia: {duz_seq[::-1]}, Alternância Coluna: {col_seq[::-1]}"

# Interface
uploaded = st.file_uploader("Enviar novo resultado CSV da roleta", type="csv")
if uploaded:
    df_novo = pd.read_csv(uploaded)
    if os.path.exists(ARQUIVO_RESULTADOS):
        df_antigo = pd.read_csv(ARQUIVO_RESULTADOS)
        df_total = pd.concat([df_antigo, df_novo]).drop_duplicates().reset_index(drop=True)
    else:
        df_total = df_novo
    df_total.to_csv(ARQUIVO_RESULTADOS, index=False)
    st.success("Resultados atualizados com sucesso!")

if os.path.exists(ARQUIVO_RESULTADOS):
    df = pd.read_csv(ARQUIVO_RESULTADOS)
    if 'Numero' in df.columns:
        numeros = df['Numero'].astype(int).tolist()
        st.subheader("Previsão Estratégia de Padrão de 3 números")
        st.info(estrategia_sequencia(numeros))

        st.subheader("Previsão Alternância Dúzias e Colunas")
        st.info(estrategia_duzias_colunas(numeros))

        st.download_button("Download dos Números", data=df.to_csv(index=False), file_name="dados_atualizados.csv", mime="text/csv")
else:
    st.warning("Nenhum dado de roleta encontrado. Envie um CSV com a coluna 'Numero'.")
