import streamlit as st
import pandas as pd
import os

# Regras atualizadas conforme o histórico fornecido
REGRAS_PERSONALIZADAS = {
    0: [0, 5, 9, 10, 17, 22, 23, 25, 26, 31, 32, 34],
    1: [1, 2, 4, 7, 11, 12, 13, 28, 20, 21, 33, 36],
    2: [1, 2, 3, 8, 11, 12, 14, 20, 21, 25, 30, 35],
    3: [3, 8, 9, 17, 23, 25, 26, 30, 31, 34, 35],
    4: [1, 4, 7, 9, 11, 12, 13, 16, 21, 28, 33, 36],
    5: [0, 5, 6, 9, 10, 15, 18, 22, 24, 27, 32, 34],
    6: [0, 5, 6, 9, 10, 15, 18, 22, 24, 27, 32, 34],
    7: [1, 4, 7, 9, 11, 13, 16, 21, 28, 29, 33, 36],
    8: [1, 3, 4, 8, 9, 16, 21, 23, 26, 30, 33, 35],
    9: [0, 3, 8, 19, 10, 17, 22, 23, 25, 26, 31, 34],
    10: [0, 5, 6, 9, 10, 17, 22, 23, 26, 31, 32, 34],
    11: [1, 2, 4, 11, 12, 20, 21, 28, 30, 33, 35, 36],
    12: [1, 2, 4, 11, 12, 20, 21, 28, 30, 33, 35, 36],
    13: [1, 4, 7, 13, 15, 16, 19, 27, 28, 29, 33, 36],
    14: [2, 3, 8, 14, 17, 20, 23, 25, 26, 30, 31, 35],
    15: [5, 6, 7, 15, 16, 18, 19, 24, 27, 29, 32, 34],
    16: [1, 4, 7, 13, 15, 16, 19, 27, 28, 29, 33, 36],
    17: [0, 3, 8, 9, 10, 17, 22, 23, 25, 26, 31, 34],
    18: [0, 5, 6, 10, 15, 18, 22, 24, 27, 29, 32, 34],
    19: [1, 4, 7, 13, 15, 16, 19, 27, 28, 29, 33, 36],
    20: [1, 2, 3, 8, 11, 12, 14, 20, 21, 25, 30, 35],
    21: [1, 2, 4, 7, 11, 12, 13, 28, 20, 21, 33, 36],
    22: [0, 5, 6, 9, 10, 15, 18, 22, 24, 27, 32, 34],
    23: [0, 3, 8, 9, 10, 17, 22, 23, 25, 26, 31, 34],
    24: [5, 6, 7, 15, 16, 18, 19, 24, 27, 29, 32, 34],
    25: [2, 3, 8, 14, 17, 20, 23, 25, 26, 30, 31, 35],
    26: [0, 3, 8, 9, 10, 17, 22, 23, 25, 26, 31, 34],
    27: [5, 6, 7, 15, 16, 18, 19, 24, 27, 29, 32, 34],
    28: [1, 2, 4, 7, 11, 12, 13, 28, 20, 21, 33, 36],
    29: [5, 6, 7, 15, 16, 18, 19, 24, 27, 29, 32, 34],
    30: [1, 2, 3, 8, 11, 12, 14, 20, 21, 25, 30, 35],
    31: [2, 3, 8, 9, 14, 17, 23, 25, 26, 30, 31, 35],
    32: [0, 5, 6, 9, 10, 15, 18, 22, 24, 27, 32, 34],
    33: [1, 4, 7, 9, 11, 12, 13, 16, 21, 28, 33, 36],
    34: [0, 5, 9, 10, 17, 22, 23, 25, 26, 31, 32, 34],
    35: [1, 2, 3, 8, 11, 12, 14, 20, 21, 25, 30, 35],
    36: [1, 2, 4, 7, 11, 12, 13, 28, 20, 21, 33, 36]
}

def analisar_resultados(sequencia):
    resultado = []
    for i in range(len(sequencia) - 1):
        atual = sequencia[i]
        proximo = sequencia[i + 1]
        proibidos = estrategia_proibidos.get(atual, [])
        if proximo in proibidos:
            resultado.append("X")
        else:
            resultado.append("1")
    return ''.join(resultado)

st.title("Analisador de Estratégia Roleta")

opcao = st.radio("Escolha a forma de entrada:", ["Inserir manualmente", "Carregar arquivo CSV"])

if opcao == "Inserir manualmente":
    entrada = st.text_input("Digite a sequência de números separados por vírgula (ex: 1,2,3,4,5)")

    if st.button("Analisar"):
        try:
            numeros = list(map(int, entrada.split(",")))
            resultado = analisar_resultados(numeros)
            st.subheader("Resultado:")
            st.code(resultado)
        except:
            st.error("Entrada inválida. Verifique se digitou números separados por vírgula.")

else:
    arquivo = st.file_uploader("Envie um arquivo CSV com uma coluna chamada 'número'", type=["csv"])
    if arquivo:
        try:
            try:
    df = pd.read_csv(arquivo_carregado)
except UnicodeDecodeError:
    df = pd.read_csv(arquivo_carregado, encoding='ISO-8859-1')

            if "número" not in df.columns:
                st.error("O CSV deve conter uma coluna chamada 'número'")
            else:
                numeros = df["número"].dropna().astype(int).tolist()
                resultado = analisar_resultados(numeros)
                st.subheader("Resultado:")
                st.code(resultado)
        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {e}")
