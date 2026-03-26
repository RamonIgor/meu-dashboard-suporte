import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Performance Analytics - Suporte", layout="wide")

# 2. CSS PARA ESTILO CORPORATIVO (TEAL & WHITE)
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #f0f2f6; }
    [data-testid="stSidebar"] { background-color: #0083b0; }
    [data-testid="stSidebar"] * { color: white !important; }
    
    .stMetric {
        background-color: white;
        padding: 20px !important;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-top: 5px solid #0097a7;
    }
    .white-card {
        background-color: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .chart-title {
        font-weight: bold; color: #333; margin-bottom: 15px; text-transform: uppercase; font-size: 13px; letter-spacing: 1px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DO BANCO DE DADOS EM MEMÓRIA ---
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame()

# --- SIDEBAR (UPLOAD E FILTROS) ---
with st.sidebar:
    st.markdown("## 📊 GESTÃO DE DADOS")
    
    # Seleção de período para o arquivo que será subido
    st.markdown("### 1. Definir Período do Arquivo")
    input_mes = st.selectbox("Mês do Relatório", ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"])
    input_ano = st.selectbox("Ano do Relatório", [2023, 2024, 2025])
    
    uploaded_files = st.file_uploader("2. Subir CSV(s)", type="csv", accept_multiple_files=True)
    
    if st.button("🚀 Processar e Consolidar"):
        if uploaded_files:
            temp_list = []
            for file in uploaded_files:
                df_temp = pd.read_csv(file, sep=None, engine='python')
                # Adiciona as colunas de data que não existem no CSV
                df_temp['Mes'] = input_mes
                df_temp['Ano'] = input_ano
                df_temp['Periodo_Ord'] = f"{input_ano}-{str(['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro'].index(input_mes)+1).zfill(2)}"
                temp_list.append(df_temp)
            
            st.session_state.db = pd.concat([st.session_state.db, pd.concat(temp_list)]).drop_duplicates()
            st.success("Dados consolidados!")

    if not st.session_state.db.empty:
        st.markdown("---")
        st.markdown("### 🔍 FILTROS GERAIS")
        # Filtro de Analista (Cedente)
        lista_analistas = sorted(st.session_state.db['Nome do cedente'].unique())
        analista_sel = st.selectbox("Selecionar Colaborador", lista_analistas)
        
        # Filtro de Ano para o Dashboard
        anos_disp = sorted(st.session_state.db['Ano'].unique(), reverse=True)
        ano_dashboard = st.multiselect("Anos no Gráfico", anos_disp, default=anos_disp)

# --- DASHBOARD PRINCIPAL ---
if not st.session_state.db.empty:
    # Filtrando a base para o analista e anos selecionados
    df_f = st.session_state.db[(st.session_state.db['Nome do cedente'] == analista_sel) & (st.session_state.db['Ano'].isin(ano_dashboard))]
    df_f = df_f.sort_values('Periodo_Ord')

    st.markdown(f"<h2 style='color: #1E3A8A; margin-bottom:20px;'>Performance Individual: {analista_sel}</h2>", unsafe_allow_html=True)

    # LINHA 1: MÉTRICAS (KPIs)
    k1, k2, k3, k4, k5 = st.columns(5)
    
    # Pegando o dado do último mês disponível para os cards
    last_month = df_f.iloc[-1] if not df_f.empty else None

    with k1:
        val = last_month['Resolvidos/Fechados'] if last_month is not None else 0
        st.metric("Resolvidos/Fechados", val)
    with k2:
        val = last_month['% FCR'] if last_month is not None else "0%"
        st.metric("FCR (1º Contato)", val)
    with k3:
        val = last_month['% Pontuação de Satisfação'] if last_month is not None else "0%"
        st.metric("Satisfação", val)
    with k4:
        val = last_month['Média Interações'] if last_month is not None else 0
        st.metric("Média Interações", val)
    with k5:
        st.metric("Status Mérito", "Destaque")

    st.markdown("<br>", unsafe_allow_html=True)

    # LINHA 2: GRÁFICO DE EVOLUÇÃO (A Métrica mais importante)
    st.markdown('<div class="white-card"><p class="chart-title">Evolução: Resolvidos/Fechados por Mês</p>', unsafe_allow_html=True)
    fig_evol = px.bar(df_f, x='Mes', y='Resolvidos/Fechados', color_discrete_sequence=['#0097a7'], text_auto=True)
    fig_evol.update_layout(height=350, margin=dict(l=20, r=20, t=10, b=10), plot_bgcolor='rgba(0,0,0,0)', xaxis_title=None)
    st.plotly_chart(fig_evol, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # LINHA 3: QUALIDADE E EFICIÊNCIA
    c_left, c_right = st.columns(2)

    with c_left:
        st.markdown('<div class="white-card"><p class="chart-title">Qualidade: FCR vs Satisfação</p>', unsafe_allow_html=True)
        # Limpeza simples de strings de porcentagem para números se necessário
        fig_qual = go.Figure()
        fig_qual.add_trace(go.Scatter(x=df_f['Mes'], y=df_f['% FCR'], name='% FCR', line=dict(color='#0083b0', width=3)))
        fig_qual.add_trace(go.Scatter(x=df_f['Mes'], y=df_f['% Pontuação de Satisfação'], name='% Satisfação', line=dict(color='#F59E0B', width=3)))
        fig_qual.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_qual, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c_right:
        st.markdown('<div class="white-card"><p class="chart-title">Espera do Solicitante (Horas)</p>', unsafe_allow_html=True)
        # Tratamento do nome longo da coluna
        col_espera = 'Tempo de espera do solicitante - Horário de funcionamento (horas)'
        fig_wait = px.area(df_f, x='Mes', y=col_espera, color_discrete_sequence=['#94A3B8'])
        fig_wait.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_wait, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # TABELA DE DADOS BRUTOS CONSOLIDADOS
    with st.expander("📄 Visualizar Tabela Consolidada de Mérito"):
        st.dataframe(df_f, use_container_width=True)

else:
    # TELA DE BOAS VINDAS
    st.markdown("""
        <div style="text-align: center; padding: 100px;">
            <h1 style='color: #0083b0;'>Sua Vitrine Profissional</h1>
            <p style='color: #666; font-size: 1.2rem;'>
                1. Selecione o <b>Mês/Ano</b> na barra lateral.<br>
                2. Suba o arquivo CSV correspondente.<br>
                3. Clique em <b>Processar</b> para construir seu histórico de conquistas.
            </p>
        </div>
    """, unsafe_allow_html=True)
