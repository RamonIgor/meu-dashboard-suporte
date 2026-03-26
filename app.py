import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Performance Analytics - Suporte", layout="wide")

# 2. CSS CORRIGIDO (Evita texto branco em fundo branco)
st.markdown("""
    <style>
    /* Fundo da aplicação */
    [data-testid="stAppViewContainer"] { background-color: #f0f2f6; }
    
    /* Barra Lateral Azul Petróleo */
    [data-testid="stSidebar"] { 
        background-color: #0083b0; 
    }
    
    /* Forçar apenas Títulos e Labels da Sidebar a serem brancos */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] .stMarkdown p { 
        color: white !important; 
    }

    /* Manter o texto dentro dos inputs (Selectbox) visível (escuro) */
    div[data-baseweb="select"] > div {
        color: #333 !important;
    }

    /* Estilização dos Cards de KPI */
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
    
    st.markdown("### 1. Definir Período do Arquivo")
    input_mes = st.selectbox("Mês do Relatório", 
                             ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                              "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"])
    
    # Adicionado 2026 e anos futuros
    input_ano = st.selectbox("Ano do Relatório", [2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030])
    
    uploaded_files = st.file_uploader("2. Subir CSV(s)", type="csv", accept_multiple_files=True)
    
    if st.button("🚀 Processar e Consolidar"):
        if uploaded_files:
            temp_list = []
            for file in uploaded_files:
                # O sep=None tenta detectar automaticamente se é vírgula ou ponto e vírgula
                df_temp = pd.read_csv(file, sep=None, engine='python')
                
                # Adiciona as colunas de data que não existem no seu CSV
                df_temp['Mes'] = input_mes
                df_temp['Ano'] = input_ano
                # Criar uma coluna oculta para ordenação correta dos meses nos gráficos
                meses_map = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                             "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
                df_temp['Periodo_Ord'] = f"{input_ano}-{str(meses_map.index(input_mes)+1).zfill(2)}"
                
                temp_list.append(df_temp)
            
            # Une os novos dados aos já existentes na sessão e remove duplicados
            new_data = pd.concat(temp_list)
            st.session_state.db = pd.concat([st.session_state.db, new_data]).drop_duplicates()
            st.success(f"Dados de {input_mes}/{input_ano} consolidados!")

    if not st.session_state.db.empty:
        st.markdown("---")
        st.markdown("### 🔍 FILTROS DO DASHBOARD")
        
        # Filtro de Analista (Cedente)
        lista_analistas = sorted(st.session_state.db['Nome do cedente'].unique())
        analista_sel = st.selectbox("Selecionar Colaborador", lista_analistas)
        
        # Filtro de Anos para visualização
        anos_disp = sorted(st.session_state.db['Ano'].unique(), reverse=True)
        ano_dashboard = st.multiselect("Anos no Gráfico", anos_disp, default=anos_disp)

# --- DASHBOARD PRINCIPAL ---
if not st.session_state.db.empty:
    # Filtrando a base para o analista e anos selecionados
    df_f = st.session_state.db[(st.session_state.db['Nome do cedente'] == analista_sel) & (st.session_state.db['Ano'].isin(ano_dashboard))]
    # Ordena pelo período para o gráfico de evolução ficar correto (Jan -> Fev -> Mar...)
    df_f = df_f.sort_values('Periodo_Ord')

    st.markdown(f"<h2 style='color: #1E3A8A; margin-bottom:20px;'>MÉRIITO E PERFORMANCE: {analista_sel}</h2>", unsafe_allow_html=True)

    # LINHA 1: MÉTRICAS (KPIs) - Mostra o consolidado ou o último mês
    k1, k2, k3, k4, k5 = st.columns(5)
    
    # Pegamos o último registro cronológico para os cartões de destaque
    last_record = df_f.iloc[-1] if not df_f.empty else None

    with k1:
        val = last_record['Resolvidos/Fechados'] if last_record is not None else 0
        st.metric("Resolvidos/Fechados", val)
    with k2:
        val = last_record['% FCR'] if last_record is not None else "0%"
        st.metric("FCR (1º Contato)", val)
    with k3:
        val = last_record['% Pontuação de Satisfação'] if last_record is not None else "0%"
        st.metric("Satisfação", val)
    with k4:
        val = last_record['Média Interações'] if last_record is not None else 0
        st.metric("Média Interações", val)
    with k5:
        # Cálculo de volume total no período filtrado
        total_periodo = df_f['Resolvidos/Fechados'].sum()
        st.metric("Total no Período", int(total_periodo))

    st.markdown("<br>", unsafe_allow_html=True)

    # LINHA 2: GRÁFICO DE EVOLUÇÃO (A Métrica mais importante para você)
    st.markdown('<div class="white-card"><p class="chart-title">Evolução de Entregas: Resolvidos/Fechados</p>', unsafe_allow_html=True)
    # Gráfico de barras teal
    fig_evol = px.bar(df_f, x='Mes', y='Resolvidos/Fechados', text_auto=True)
    fig_evol.update_traces(marker_color='#0097a7', marker_line_color='#006064', marker_line_width=1)
    fig_evol.update_layout(height=350, margin=dict(l=20, r=20, t=10, b=10), plot_bgcolor='rgba(0,0,0,0)', xaxis_title=None)
    st.plotly_chart(fig_evol, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # LINHA 3: QUALIDADE E EFICIÊNCIA
    c_left, c_right = st.columns(2)

    with c_left:
        st.markdown('<div class="white-card"><p class="chart-title">Indicadores de Qualidade (% FCR e Satisfação)</p>', unsafe_allow_html=True)
        fig_qual = go.Figure()
        fig_qual.add_trace(go.Scatter(x=df_f['Mes'], y=df_f['% FCR'], name='% FCR', line=dict(color='#0083b0', width=4)))
        fig_qual.add_trace(go.Scatter(x=df_f['Mes'], y=df_f['% Pontuação de Satisfação'], name='% Satisfação', line=dict(color='#F59E0B', width=4)))
        fig_qual.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_qual, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c_right:
        st.markdown('<div class="white-card"><p class="chart-title">Tempo de Espera (Eficiência Operacional)</p>', unsafe_allow_html=True)
        col_espera = 'Tempo de espera do solicitante - Horário de funcionamento (horas)'
        fig_wait = px.area(df_f, x='Mes', y=col_espera)
        fig_wait.update_traces(line_color='#0097a7', fillcolor='rgba(0, 151, 167, 0.2)')
        fig_wait.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_wait, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # TELA DE BOAS VINDAS
    st.markdown("""
        <div style="text-align: center; padding: 100px; background-color: white; border-radius: 15px; border: 2px dashed #0083b0;">
            <h1 style='color: #0083b0;'>Central de Mérito do Analista</h1>
            <p style='color: #444; font-size: 1.2rem;'>
                Para começar:<br><br>
                1. No menu ao lado, escolha o <b>Mês e Ano</b> do seu relatório CSV.<br>
                2. Faça o upload do arquivo.<br>
                3. Clique em <b>🚀 Processar e Consolidar</b>.<br><br>
                Você pode repetir o processo para vários meses para criar seu histórico anual!
            </p>
        </div>
    """, unsafe_allow_html=True)
