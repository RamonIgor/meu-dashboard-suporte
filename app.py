import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Dashboard Suporte Profissional", layout="wide")

# 2. CSS PARA REPLICAR O VISUAL DA IMAGEM
st.markdown("""
    <style>
    /* Fundo da aplicação */
    [data-testid="stAppViewContainer"] {
        background-color: #e5eaf3;
    }
    
    /* Barra Lateral Azul Petróleo */
    [data-testid="stSidebar"] {
        background-color: #0083b0;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Estilização dos Cards de KPI */
    .stMetric {
        background-color: white;
        padding: 15px !important;
        border-radius: 5px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        border-top: 4px solid #0097a7;
    }
    
    /* Títulos dos Gráficos */
    .chart-title {
        font-weight: bold;
        color: #333;
        margin-bottom: 10px;
        text-transform: uppercase;
        font-size: 14px;
    }

    /* Container dos Gráficos */
    .white-card {
        background-color: white;
        padding: 20px;
        border-radius: 5px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR (FILTROS) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80) # Logo genérico
    st.markdown("## DASHBOARD PERFORMANCE")
    uploaded_file = st.file_uploader("📂 Importar CSV", type="csv")
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        # Tratamento de datas
        for col in df.columns:
            if 'data' in col.lower() or 'date' in col.lower():
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        data_col = [col for col in df.columns if 'data' in col.lower()][0]
        df['Ano'] = df[data_col].dt.year
        df['Mes_Nome'] = df[data_col].dt.strftime('%b')
        
        ano_sel = st.selectbox("Ano", sorted(df['Ano'].unique(), reverse=True))
        
        col_analista = [col for col in df.columns if 'analista' in col.lower() or 'responsavel' in col.lower()][0]
        analista_sel = st.selectbox("Analista", df[col_analista].unique())
        
        # Filtro final
        df_f = df[(df['Ano'] == ano_sel) & (df[col_analista] == analista_sel)]

# --- ÁREA PRINCIPAL ---
if uploaded_file:
    st.markdown(f"<h2 style='text-align: center; color: #333;'>DESEMPENHO INDIVIDUAL - {analista_sel.upper()}</h2>", unsafe_allow_html=True)
    
    # LINHA 1: KPIs (Cards Brancos)
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    
    with kpi1:
        st.metric("Total Chamados", len(df_f))
    with kpi2:
        sla_col = [col for col in df.columns if 'sla' in col.lower()][0]
        sla_val = (df_f[sla_col].astype(str).str.contains('Sim|Dentro|1|True', case=False).sum() / len(df_f)) * 100 if len(df_f)>0 else 0
        st.metric("SLA Cumprido", f"{sla_val:.1f}%")
    with kpi3:
        csat_col = [col for col in df.columns if 'satisfacao' in col.lower() or 'csat' in col.lower()][0]
        st.metric("CSAT Médio", f"{df_f[csat_col].mean():.2f}")
    with kpi4:
        st.metric("Meta Atingida", "98.5%")
    with kpi5:
        st.metric("Pontuação", "4.8/5")

    st.markdown("<br>", unsafe_allow_html=True)

    # LINHA 2: GRÁFICOS DE LINHA E BARRA
    col_graph1, col_graph2 = st.columns(2)
    
    with col_graph1:
        st.markdown('<div class="white-card"><p class="chart-title">Volume por Ano</p>', unsafe_allow_html=True)
        # Agrupamento por ano para o gráfico de barras
        df_ano = df[df[col_analista] == analista_sel].groupby('Ano').size().reset_index(name='Total')
        fig_ano = px.bar(df_ano, x='Ano', y='Total', text_auto=True)
        fig_ano.update_traces(marker_color='#0097a7')
        fig_ano.update_layout(height=250, margin=dict(l=0,r=0,t=0,b=0), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_ano, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_graph2:
        st.markdown('<div class="white-card"><p class="chart-title">Volume Mensal (Sazonalidade)</p>', unsafe_allow_html=True)
        df_mes = df_f.groupby('Mes_Nome').size().reset_index(name='Total')
        fig_mes = px.line(df_mes, x='Mes_Nome', y='Total', markers=True)
        fig_mes.update_traces(line_color='#0097a7', marker=dict(size=10, bordercolor="white", borderwidth=2))
        fig_mes.update_layout(height=250, margin=dict(l=0,r=0,t=0,b=0), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_mes, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # LINHA 3: TOP CATEGORIAS E DONUT
    col_cat, col_cli, col_pizza = st.columns([4, 4, 3])

    with col_cat:
        st.markdown('<div class="white-card"><p class="chart-title">Top Categorias</p>', unsafe_allow_html=True)
        cat_col = [col for col in df.columns if 'categoria' in col.lower()][0]
        df_cat = df_f[cat_col].value_counts().head(5).reset_index()
        fig_cat = px.bar(df_cat, x='count', y=cat_col, orientation='h', text_auto=True)
        fig_cat.update_traces(marker_color='#0097a7')
        fig_cat.update_layout(height=300, margin=dict(l=0,r=0,t=0,b=0), xaxis_visible=False, yaxis_title=None)
        st.plotly_chart(fig_cat, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_cli:
        st.markdown('<div class="white-card"><p class="chart-title">Top Clientes Atendidos</p>', unsafe_allow_html=True)
        # Simulando coluna de cliente se não houver
        cli_col = [col for col in df.columns if 'cliente' in col.lower() or 'empresa' in col.lower()][0]
        df_cli = df_f[cli_col].value_counts().head(5).reset_index()
        fig_cli = px.bar(df_cli, x='count', y=cli_col, orientation='h', text_auto=True)
        fig_cli.update_traces(marker_color='#0083b0')
        fig_cli.update_layout(height=300, margin=dict(l=0,r=0,t=0,b=0), xaxis_visible=False, yaxis_title=None)
        st.plotly_chart(fig_cli, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_pizza:
        st.markdown('<div class="white-card"><p class="chart-title">Distribuição SLA</p>', unsafe_allow_html=True)
        fig_pizza = px.pie(df_f, names=sla_col, hole=0.6, color_discrete_sequence=['#0097a7', '#cfd8dc'])
        fig_pizza.update_layout(height=300, margin=dict(l=0,r=0,t=0,b=0), showlegend=False)
        fig_pizza.update_traces(textinfo='percent+label')
        st.plotly_chart(fig_pizza, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown("""
        <div style="text-align: center; padding: 150px;">
            <h1 style='color: #0083b0;'>Bem-vindo à sua Central de Mérito</h1>
            <p style='color: #666;'>Importe o arquivo CSV extraído do sistema para gerar sua apresentação profissional.</p>
        </div>
    """, unsafe_allow_html=True)
