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
        0: [5, 15, 25],
        1: [3, 9, 27],
        2: [4, 12, 36],
        3: [1, 13, 35],
        4: [2, 14, 34],
        5: [0, 10, 30],
        6: [18, 24, 33],
        7: [19, 25, 28],
        8: [20, 26, 29],
        9: [1, 11, 31],
        10: [2, 22, 32],
        11: [3, 13, 23],
        12: [4, 14, 24],
        13: [5, 15, 25],
        14: [6, 16, 26],
        15: [7, 17, 27],
        16: [8, 18, 28],
        17: [9, 19, 29],
        18: [10, 20, 30],
        19: [11, 21, 31],
        20: [12, 22, 32],
        21: [13, 23, 33],
        22: [14, 24, 34],
        23: [15, 25, 35],
        24: [16, 26, 36],
        25: [0, 17, 27],
        26: [1, 18, 28],
        27: [2, 19, 29],
        28: [3, 20, 30],
        29: [4, 21, 31],
        30: [5, 22, 32],
        31: [6, 23, 33],
        32: [7, 24, 34],
        33: [8, 25, 35],
        34: [9, 26, 36],
        35: [10, 27, 0],
        36: [11, 28, 1],
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
        st.download_button("📥 Baixar resultados atuais", f, file_name="resultados_atualizados.csv")

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

        # Estratégia 2 – Repetição de Dúzias
        def get_dz(n): return 0 if n == 0 else (n - 1) // 12 + 1
        if len(df) >= 11:
            ult_dzs = [get_dz(n) for n in df['numero'].iloc[-11:]]
            if all(x == ult_dzs[0] for x in ult_dzs):
                st.warning("📌 Estratégia 2: 11 ou mais repetições da mesma dúzia detectadas!")

        # Estratégia 3 – Zig-Zag (Ímpar/Par e Vermelho/Preto - simplificado para Ímpar/Par)
        if len(df) >= 14:
            zigzag = [n % 2 for n in df['numero'].iloc[-14:]]
            alternando = all(zigzag[i] != zigzag[i+1] for i in range(len(zigzag)-1))
            if alternando:
                st.info("📌 Estratégia 3: Zig-Zag de ímpar/par detectado!")

        # Estratégia 4 – Gatilho Personalizado
        gatilho_personalizado = [7, 19, 36]
        if all(x in df['numero'].tolist()[-10:] for x in gatilho_personalizado):
            st.info("📌 Estratégia 4: Gatilho 7-19-36 detectado! Apostar em 3")

        # Estratégia 5 – Alterações entre Dúzias
        if len(df) >= 5:
            seq_dz = [get_dz(n) for n in df['numero'].iloc[-5:]]
            alteracoes = sum(1 for i in range(len(seq_dz)-1) if seq_dz[i] != seq_dz[i+1])
            if alteracoes >= 4:
                st.warning("📌 Estratégia 5: 4x alterações entre dúzias nas últimas jogadas!")

        # Histórico dos palpites por estratégia
        historico = pd.DataFrame({
            'numero': [numero_manual],
            'estrategia1': [resultado],
            'estrategia2': ['ALERTA' if all(x == ult_dzs[0] for x in ult_dzs) else ''],
            'estrategia3': ['ZIGZAG' if alternando else ''],
            'estrategia4': ['ATIVADO' if all(x in df['numero'].tolist()[-10:] for x in gatilho_personalizado) else ''],
            'estrategia5': ['ALERTA' if alteracoes >= 4 else '']
        })
        if os.path.exists(ARQUIVO_ESTRATEGIAS):
            hist_ant = pd.read_csv(ARQUIVO_ESTRATEGIAS)
            historico = pd.concat([hist_ant, historico], ignore_index=True)
        historico.to_csv(ARQUIVO_ESTRATEGIAS, index=False)
        st.dataframe(historico.tail(10))
