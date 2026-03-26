import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# CONFIGURAÇÃO DA PÁGINA - TEMA LIGHT MODERNO
st.set_page_config(page_title="Performance Dashboard", layout="wide", initial_sidebar_state="expanded")

# --- CSS CUSTOMIZADO PARA DESIGN PREMIUM ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #F8FAFC;
    }

    /* Estilização dos Cards de Métricas */
    .metric-card {
        background-color: white;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid #E2E8F0;
        text-align: center;
    }
    
    .metric-title { color: #64748B; font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
    .metric-value { color: #1E293B; font-size: 32px; font-weight: 700; margin: 8px 0; }
    
    /* Cabeçalho */
    .header-container {
        background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 100%);
        padding: 40px;
        border-radius: 20px;
        color: white;
        margin-bottom: 30px;
    }

    /* Ajuste de Tabs e Botões */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; background-color: transparent; border: none; font-weight: 600; color: #64748B;
    }
    .stTabs [aria-selected="true"] { color: #2563EB !important; border-bottom: 2px solid #2563EB !important; }

    /* Esconder o menu padrão do streamlit para parecer um App próprio */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- CABEÇALHO ---
st.markdown("""
    <div class="header-container">
        <h1 style='margin:0; font-size: 2.5rem;'>Professional Achievement Hub</h1>
        <p style='margin:0; opacity: 0.9; font-size: 1.1rem;'>Análise consolidada de performance e impacto operacional</p>
    </div>
    """, unsafe_allow_html=True)

# --- SIDEBAR ESTILIZADA ---
with st.sidebar:
    st.markdown("<h2 style='color: #1E293B;'>⚙️ Painel de Controle</h2>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload do relatório (CSV)", type="csv")
    st.markdown("---")
    st.markdown("### 💡 Dica de Mérito")
    st.info("Filtre períodos específicos para demonstrar evolução trimestral nas suas reuniões de feedback.")

if uploaded_file:
    # Lógica de processamento (idêntica à anterior, mas com nomes tratados)
    df = pd.read_csv(uploaded_file)
    for col in df.columns:
        if 'data' in col.lower() or 'date' in col.lower():
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    data_col = [col for col in df.columns if 'data' in col.lower()][0]
    df['Ano'] = df[data_col].dt.year
    df['Mês'] = df[data_col].dt.month_name()
    
    col_analista = [col for col in df.columns if 'analista' in col.lower() or 'responsavel' in col.lower()][0]
    analista_sel = st.sidebar.selectbox("Selecionar Colaborador", df[col_analista].unique())
    
    # Filtros de Data
    anos = st.sidebar.multiselect("Anos", sorted(df['Ano'].unique()), default=df['Ano'].unique())
    meses = st.sidebar.multiselect("Meses", df['Mês'].unique(), default=df['Mês'].unique())

    # Dados Filtrados
    df_f = df[(df[col_analista] == analista_sel) & (df['Ano'].isin(anos)) & (df['Mês'].isin(meses))]

    # --- KPIs EM CARDS ---
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown(f"""<div class="metric-card"><div class="metric-title">Resolvidos</div><div class="metric-value">{len(df_f)}</div></div>""", unsafe_allow_html=True)
    with c2:
        sla_col = [col for col in df.columns if 'sla' in col.lower()][0]
        sla_p = (df_f[sla_col].astype(str).str.contains('Sim|Dentro|1|True', case=False).sum() / len(df_f)) * 100 if len(df_f) > 0 else 0
        st.markdown(f"""<div class="metric-card"><div class="metric-title">SLA Atendido</div><div class="metric-value">{sla_p:.1f}%</div></div>""", unsafe_allow_html=True)
    with c3:
        csat_col = [col for col in df.columns if 'satisfacao' in col.lower() or 'csat' in col.lower() or 'nota' in col.lower()][0]
        st.markdown(f"""<div class="metric-card"><div class="metric-title">CSAT Médio</div><div class="metric-value">{df_f[csat_col].mean():.2f}</div></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card"><div class="metric-title">Nível de Entrega</div><div class="metric-value" style="color: #059669;">Excepcional</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- GRÁFICOS MODERNOS ---
    g1, g2 = st.columns([7, 3])

    with g1:
        st.markdown("### 📈 Tendência de Produtividade")
        prod_mensal = df_f.groupby('Mês').size().reset_index(name='Volume')
        fig = px.bar(prod_mensal, x='Mês', y='Volume', text_auto='.2s', template="simple_white")
        fig.update_traces(marker_color='#3B82F6', marker_line_color='#1E3A8A', marker_line_width=1, opacity=0.8)
        fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=350)
        st.plotly_chart(fig, use_container_width=True)

    with g2:
        st.markdown("### 🎯 Domínio Técnico")
        cat_col = [col for col in df.columns if 'categoria' in col.lower() or 'tipo' in col.lower()][0]
        cat_data = df_f[cat_col].value_counts().head(5)
        fig_pie = px.pie(values=cat_data.values, names=cat_data.index, hole=0.7)
        fig_pie.update_layout(showlegend=False, margin=dict(l=0, r=0, t=0, b=0), height=350)
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- SEÇÃO DE MÉRITO (O DIFERENCIAL) ---
    st.markdown("### 🏆 Vitrine de Reconhecimento")
    aba1, aba2 = st.tabs(["✨ Elogios e Feedbacks", "🧠 Artigos e Conhecimento"])
    
    with aba1:
        fb_col = [col for col in df.columns if 'comentario' in col.lower() or 'feedback' in col.lower()][0]
        top_fb = df_f.sort_values(by=csat_col, ascending=False).head(3)
        for _, row in top_fb.iterrows():
            st.markdown(f"""
                <div style="background-color: #F1F5F9; padding: 15px; border-radius: 12px; margin-bottom: 10px; border-left: 4px solid #F59E0B;">
                    <strong>Nota {row[csat_col]}/5</strong>: "{row[fb_col]}"
                </div>
            """, unsafe_allow_html=True)
            
    with aba2:
        st.markdown("""
            <div style="padding: 20px; border: 1px dashed #CBD5E1; border-radius: 12px;">
                <p>Neste período, o colaborador focou na redução de tickets recorrentes através da criação de documentação técnica 
                e melhoria de processos internos.</p>
                <strong>Projetos Ativos:</strong> Implementação de KB de Redes | Automação de Reset de Senha
            </div>
        """, unsafe_allow_html=True)

else:
    # TELA INICIAL "CLEAN"
    st.markdown("""
        <div style="text-align: center; padding: 100px 20px; background-color: white; border-radius: 20px; border: 2px dashed #E2E8F0;">
            <h2 style="color: #64748B;">Aguardando Importação de Dados</h2>
            <p style="color: #94A3B8;">Arraste seu arquivo CSV extraído do sistema na barra lateral para começar.</p>
        </div>
    """, unsafe_allow_html=True)
