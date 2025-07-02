import streamlit as st
from collections import defaultdict, deque
import pandas as pd

# Configuração das cores da roleta (0 = verde)
CORES = {
    0: 'G',
    1: 'R', 3: 'R', 5: 'R', 7: 'R', 9: 'R', 12: 'R', 
    14: 'R', 16: 'R', 18: 'R', 19: 'R', 21: 'R', 23: 'R',
    25: 'R', 27: 'R', 30: 'R', 32: 'R', 34: 'R', 36: 'R'
    # Todos os outros são pretos (B)
}

# Inicialização
if 'historico' not in st.session_state:
    st.session_state.historico = []
if 'resultados' not in st.session_state:
    st.session_state.resultados = defaultdict(lambda: deque(maxlen=20))  # Número: [cores após ele]

def atualizar_resultados():
    if len(st.session_state.historico) > 1:
        ultimo_num = st.session_state.historico[-1]
        cor = CORES.get(ultimo_num, 'B')
        
        # Adiciona a cor ao número anterior
        num_anterior = st.session_state.historico[-2]
        st.session_state.resultados[num_anterior].append(cor)

# Interface
st.title("Estratégia de Cores Pós-Número")

# Upload de CSV
uploaded_file = st.file_uploader("Importar histórico (CSV)", type="csv")
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        if 'Número' in df.columns:
            st.session_state.historico = df['Número'].tolist()
            # Processa todos os resultados do CSV
            for i in range(1, len(st.session_state.historico)):
                num_anterior = st.session_state.historico[i-1]
                cor_atual = CORES.get(st.session_state.historico[i], 'B')
                st.session_state.resultados[num_anterior].append(cor_atual)
            st.success("Histórico carregado com sucesso!")
    except Exception as e:
        st.error(f"Erro ao ler arquivo: {e}")

# Controle manual
col1, col2 = st.columns(2)
with col1:
    num = st.number_input("Novo número (0-36)", min_value=0, max_value=36)
with col2:
    st.write("")
    st.write("")
    if st.button("Adicionar número"):
        st.session_state.historico.append(num)
        atualizar_resultados()

# Exportar histórico
if st.session_state.historico:
    # Prepara dados para exportação
    export_data = []
    for i in range(1, len(st.session_state.historico)):
        num_anterior = st.session_state.historico[i-1]
        cor_resultado = CORES.get(st.session_state.historico[i], 'B')
        export_data.append({
            "Número_Anterior": num_anterior,
            "Cor_Resultado": cor_resultado,
            "Número_Sorteado": st.session_state.historico[i]
        })
    
    df_export = pd.DataFrame(export_data)
    csv = df_export.to_csv(index=False).encode('utf-8')
    
    st.download_button(
        label="📥 Exportar histórico completo",
        data=csv,
        file_name='historico_cores_posteriores.csv',
        mime='text/csv'
    )

# Exibição
st.subheader("Cor do resultado APÓS cada número")

cols = st.columns(3)
for i in range(37):
    with cols[0] if i < 12 else (cols[1] if i < 24 else cols[2]):
        cores = st.session_state.resultados[i]
        display = []
        for c in cores:
            color = "red" if c == 'R' else ("green" if c == 'G' else "black")
            display.append(f'<span style="color:{color}; font-weight:bold">{c}</span>')
        st.markdown(f"{i}: {' '.join(display)}", unsafe_allow_html=True)

# Exibição do histórico bruto (opcional)
with st.expander("Ver histórico completo"):
    st.write(st.session_state.historico)
