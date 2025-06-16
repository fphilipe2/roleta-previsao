import streamlit as st
import pandas as pd
import os

# Regras atualizadas conforme o histórico fornecido (poderão ser editadas abaixo)
ARQUIVO_REGRAS = "regras.csv"
ARQUIVO_RESULTADOS = "dados.csv"
ARQUIVO_ESTRATEGIAS = "historico_estrategias.csv"

# Carregar regras do arquivo ou usar padrão
if os.path.exists(ARQUIVO_REGRAS):
    regras_df = pd.read_csv(ARQUIVO_REGRAS)
    regras = {int(row['anterior']): list(map(int, str(row['proibidos']).split(','))) for _, row in regras_df.iterrows()}
else:
    regras = {
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
    regras_df = pd.DataFrame([{"anterior": k, "proibidos": ",".join(map(str, v))} for k, v in regras.items()])

st.title("Roleta - Previsão e Simulação de Banca")

# Editor de regras
st.subheader("Editar Regras de Previsão")
selected_anterior = st.selectbox("Escolha o número anterior para editar regras:", sorted(regras.keys()))
atual_lista = regras.get(selected_anterior, [])
nova_lista = st.multiselect("Escolha os números proibidos:", list(range(37)), default=atual_lista)
if st.button("Salvar Regras Atualizadas"):
    regras[selected_anterior] = nova_lista
    regras_df = pd.DataFrame([{"anterior": k, "proibidos": ",".join(map(str, v))} for k, v in regras.items()])
    regras_df.to_csv(ARQUIVO_REGRAS, index=False)
    st.success("Regras atualizadas com sucesso!")

# Upload / download
st.subheader("📂 Upload / Download de Resultados")
uploaded_file = st.file_uploader("Envie seu arquivo CSV com a coluna 'numero':", type="csv")
if uploaded_file:
    novos_resultados = pd.read_csv(uploaded_file)
    if 'numero' in novos_resultados.columns:
        if os.path.exists(ARQUIVO_RESULTADOS):
            df_antigo = pd.read_csv(ARQUIVO_RESULTADOS)
            df_completo = pd.concat([df_antigo, novos_resultados]).drop_duplicates().reset_index(drop=True)
        else:
            df_completo = novos_resultados
        df_completo.to_csv(ARQUIVO_RESULTADOS, index=False)
        st.success("Resultados adicionados com sucesso!")

if os.path.exists(ARQUIVO_RESULTADOS):
    with open(ARQUIVO_RESULTADOS, "rb") as f:
        st.download_button("📅 Baixar resultados atuais", f, file_name="resultados_atualizados.csv")

# Entrada manual
st.subheader("🎯 Inserir Número Manualmente")
numero_manual = st.number_input("Digite o número da roleta (0-36):", min_value=0, max_value=36, step=1)
if st.button("Adicionar Número"):
    if os.path.exists(ARQUIVO_RESULTADOS):
        df = pd.read_csv(ARQUIVO_RESULTADOS)
    else:
        df = pd.DataFrame(columns=['numero'])
    df = pd.concat([df, pd.DataFrame({'numero': [numero_manual]})], ignore_index=True)
    df.to_csv(ARQUIVO_RESULTADOS, index=False)
    st.success(f"Número {numero_manual} adicionado com sucesso!")

    if len(df) >= 14:
        ultimos = df['numero'].iloc[-14:].tolist()
        anterior = ultimos[-2]
        proibidos = regras.get(anterior, [])
        proximo = ultimos[-1]
        palpite = "1" if proximo not in proibidos else "X"
        resultado = 'GREEN' if palpite == '1' else 'RED'
        st.info(f"Resultado do número inserido: {resultado}")

        def get_dz(n): return 0 if n == 0 else (n - 1) // 12 + 1

        if len(df) >= 11:
            ult_dzs = [get_dz(n) for n in df['numero'].iloc[-11:]]
            if all(x == ult_dzs[0] for x in ult_dzs):
                st.warning("📌 Estratégia 2: 11 ou mais repetições da mesma dúzia detectadas!")

        if len(df) >= 14:
            zigzag = [n % 2 for n in df['numero'].iloc[-14:]]
            alternando = all(zigzag[i] != zigzag[i+1] for i in range(len(zigzag)-1))
            if alternando:
                st.info("📌 Estratégia 3: Zig-Zag de ímpar/par detectado!")

        gatilho_personalizado = [7, 19, 36]
        if all(x in df['numero'].tolist()[-10:] for x in gatilho_personalizado):
            st.info("📌 Estratégia 4: Gatilho 7-19-36 detectado! Apostar em 3")

        def duzia(numero):
            if numero == 0:
                return 'D0'
            elif 1 <= numero <= 12:
                return 'D1'
            elif 13 <= numero <= 24:
                return 'D2'
            else:
                return 'D3'

        def coluna(numero):
            if numero == 0:
                return 'C0'
            elif numero in [1,4,7,10,13,16,19,22,25,28,31,34]: return 'C1'
            elif numero in [2,5,8,11,14,17,20,23,26,29,32,35]: return 'C2'
            else: return 'C3'

        def contar_alteracoes(grupo):
            alteracoes = 0
            for i in range(2, len(grupo)):
                atual = grupo[i]
                prev1 = grupo[i - 1]
                prev2 = grupo[i - 2]
                if atual != prev1 and atual != prev2:
                    alteracoes += 1
            return alteracoes

        alerta_dz = False
        alerta_col = False

        if len(df) >= 6:
            dz_seq = [duzia(n) for n in df['numero'].iloc[-6:].tolist()]
            alt_dz = contar_alteracoes(dz_seq)
            alerta_dz = alt_dz >= 4
            if alerta_dz:
                ult_dz_validas = [d for d in dz_seq[-2:] if d != 'D0']
                palpite_dz = set(ult_dz_validas)
                palpite_dz.add('D0')
                st.warning(f"📌 Estratégia 5: 4x alterações de dúzias detectadas. Jogar: {', '.join(sorted(palpite_dz))}")

            col_seq = [coluna(n) for n in df['numero'].iloc[-6:].tolist()]
            alt_col = contar_alteracoes(col_seq)
            alerta_col = alt_col >= 4
            if alerta_col:
                ult_col_validas = [c for c in col_seq[-2:] if c != 'C0']
                palpite_col = set(ult_col_validas)
                palpite_col.add('C0')
                st.warning(f"📌 Estratégia 6: 4x alterações de colunas detectadas. Jogar: {', '.join(sorted(palpite_col))}")

        historico = pd.DataFrame({
            'numero': [numero_manual],
            'estrategia1': [resultado],
            'estrategia2': ['ALERTA' if all(x == ult_dzs[0] for x in ult_dzs) else ''],
            'estrategia3': ['ZIGZAG' if alternando else ''],
            'estrategia4': ['ATIVADO' if all(x in df['numero'].tolist()[-10:] for x in gatilho_personalizado) else ''],
            'estrategia5': ['ALERTA' if alerta_dz else ''],
            'estrategia6': ['ALERTA' if alerta_col else '']
        })

        if os.path.exists(ARQUIVO_ESTRATEGIAS):
            hist_ant = pd.read_csv(ARQUIVO_ESTRATEGIAS)
            historico = pd.concat([hist_ant, historico], ignore_index=True)
        historico.to_csv(ARQUIVO_ESTRATEGIAS, index=False)
        st.dataframe(historico.tail(10))
