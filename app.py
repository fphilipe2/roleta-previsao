import streamlit as st
import pandas as pd
import os

ARQUIVO_RESULTADOS = "dados.csv"
ARQUIVO_ESTRATEGIAS = "historico_estrategias.csv"

st.title("Roleta - Previsão e Simulação de Banca")

# Função para carregar histórico
@st.cache_data

def carregar_historico():
    if os.path.exists(ARQUIVO_ESTRATEGIAS):
        df = pd.read_csv(ARQUIVO_ESTRATEGIAS)
        return df
    else:
        return pd.DataFrame(columns=["Numero"])

# Função para salvar novo número
def salvar_numero(numero):
    df = carregar_historico()
    novo = pd.DataFrame({"Numero": [numero]})
    df = pd.concat([df, novo], ignore_index=True)
    df.to_csv(ARQUIVO_ESTRATEGIAS, index=False)

# Função para pegar os 5 vizinhos de um número
def vizinhos(n):
    return [(n + i) % 37 for i in range(-2, 3)]

# Estratégia baseada em padrões de 3 números (ordem não importa)
def estrategia_padrao_3(historico):
    if len(historico) < 5:
        return "Histórico insuficiente para detectar padrões."

    ultimos_3 = set(historico[-3:])
    for i in range(len(historico) - 5):
        grupo = set(historico[i:i+3])
        if grupo == ultimos_3:
            alvos = historico[i+3:i+5]
            viz = set()
            for a in alvos:
                viz.update(vizinhos(a))
            return f"Padrão detectado: Apostar nos números: {sorted(viz.union(alvos))}"
    return "Nenhum padrão detectado."

# Estratégia alternância de Dúzias e Colunas

def estrategia_duzias_colunas(historico):
    if len(historico) < 3:
        return "Histórico insuficiente para alternância."

    def duzia(n):
        if n == 0: return 0
        return (n - 1) // 12 + 1

    def coluna(n):
        if n == 0: return 0
        return 1 + (n - 1) % 3

    ultimos_validos = [n for n in reversed(historico) if n != 0][:3]
    if len(ultimos_validos) < 2:
        return "Poucos números válidos para alternância."

    d1, d2 = duzia(ultimos_validos[1]), duzia(ultimos_validos[0])
    c1, c2 = coluna(ultimos_validos[1]), coluna(ultimos_validos[0])

    msg = f"Últimas dúzias: {d1}, {d2} → "
    if d1 == d2:
        msg += "Repetição detectada. Reiniciar sequência."
    else:
        msg += "Alternância OK."

    msg += f"\nÚltimas colunas: {c1}, {c2} → "
    if c1 == c2:
        msg += "Repetição detectada. Reiniciar sequência."
    else:
        msg += "Alternância OK."

    return msg

# Interface do usuário
st.subheader("Adicionar número da roleta")
novo_num = st.number_input("Número (0 a 36):", min_value=0, max_value=36, step=1)
if st.button("Adicionar número"):
    salvar_numero(novo_num)
    st.success(f"Número {novo_num} adicionado com sucesso!")

# Carregar histórico atualizado
df_hist = carregar_historico()
if not df_hist.empty:
    historico = df_hist["Numero"].astype(int).tolist()
    st.subheader("Estratégia - Padrão de 3 números")
    st.info(estrategia_padrao_3(historico))

    st.subheader("Estratégia - Alternância Dúzias e Colunas")
    st.info(estrategia_duzias_colunas(historico))
else:
    st.warning("Nenhum número no histórico ainda.")

# Botão para exportar histórico
st.download_button(
    label="📥 Exportar histórico da roleta",
    data=df_hist.to_csv(index=False).encode("utf-8"),
    file_name="historico_exportado.csv",
    mime="text/csv"
)
