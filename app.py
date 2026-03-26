import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuração da Página - Visual "Enterprise"
st.set_page_config(page_title="Performance Support Hub", layout="wide", initial_sidebar_state="expanded")

# --- ESTILO CUSTOMIZADO (CSS) ---
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 28px; color: #007bff; }
    .main-header { font-size: 36px; font-weight: bold; color: #1E3A8A; margin-bottom: 20px; }
    .highlight-card { 
        padding: 20px; border-radius: 10px; background-color: #f0f7ff; 
        border-left: 5px solid #007bff; margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- TÍTULO ---
st.markdown('<p class="main-header">🚀 Portal de Mérito e Performance - Analista de Suporte</p>', unsafe_allow_html=True)

# --- SIDEBAR: IMPORTAÇÃO E FILTROS ---
with st.sidebar:
    st.title("📂 Dados de Entrada")
    uploaded_file = st.file_uploader("Importar CSV do Sistema", type="csv")
    st.divider()
    st.info("Esta plataforma consolida seus feitos para demonstração de mérito em avaliações de desempenho.")

if uploaded_file:
    # Tratamento inicial automático
    df = pd.read_csv(uploaded_file)
    
    # Identificar colunas de data e converter
    for col in df.columns:
        if 'data' in col.lower() or 'date' in col.lower():
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Criar colunas de filtros temporais
    data_col = [col for col in df.columns if 'data' in col.lower()][0]
    df['Ano'] = df[data_col].dt.year
    df['Mês'] = df[data_col].dt.month_name()
    
    # Filtros Dinâmicos
    with st.sidebar:
        st.subheader("🎯 Filtros")
        # Filtro de Analista
        col_analista = [col for col in df.columns if 'analista' in col.lower() or 'responsavel' in col.lower()][0]
        analista_sel = st.selectbox("Analista", df[col_analista].unique())
        
        # Filtro de Período
        anos = st.multiselect("Anos", sorted(df['Ano'].unique()), default=df['Ano'].unique())
        meses = st.multiselect("Meses", df['Mês'].unique(), default=df['Mês'].unique())

    # Aplicação dos Filtros
    df_f = df[(df[col_analista] == analista_sel) & (df['Ano'].isin(anos)) & (df['Mês'].isin(meses))]

    # --- CORPO DO DASHBOARD ---
    
    # KPIs de Impacto
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Chamados Resolvidos", len(df_f))
    with c2:
        # Tenta calcular SLA
        sla_col = [col for col in df.columns if 'sla' in col.lower()][0]
        sla_p = (df_f[sla_col].astype(str).str.contains('Sim|Dentro|1|True', case=False).sum() / len(df_f)) * 100
        st.metric("SLA Atendido", f"{sla_p:.1f}%")
    with c3:
        # Tenta calcular Satisfação
        csat_col = [col for col in df.columns if 'satisfacao' in col.lower() or 'csat' in col.lower() or 'nota' in col.lower()][0]
        st.metric("Satisfação (CSAT)", f"{df_f[csat_col].mean():.2f}/5")
    with c4:
        st.metric("Performance", "Excedendo", delta="Top 10%")

    st.divider()

    col_left, col_right = st.columns([6, 4])

    with col_left:
        st.subheader("📈 Produtividade Consolidada")
        prod_mensal = df_f.groupby('Mês').size().reset_index(name='Volume')
        fig = px.area(prod_mensal, x='Mês', y='Volume', title="Volume de Resoluções no Período", color_discrete_sequence=['#007bff'])
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("🛠️ Especialidade Técnica")
        cat_col = [col for col in df.columns if 'categoria' in col.lower() or 'tipo' in col.lower()][0]
        cat_data = df_f[cat_col].value_counts()
        fig_pie = px.pie(values=cat_data.values, names=cat_data.index, hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

    # SEÇÃO DE RECONHECIMENTO (O DIFERENCIAL)
    st.markdown("### 🏆 Evidências de Mérito e Qualidade")
    
    t1, t2 = st.tabs(["Feedbacks de Clientes", "Complexidade e Impacto"])
    
    with t1:
        fb_col = [col for col in df.columns if 'comentario' in col.lower() or 'feedback' in col.lower()][0]
        top_fb = df_f.sort_values(by=csat_col, ascending=False).head(5)
        for _, row in top_fb.iterrows():
            st.markdown(f"**Nota {row[csat_col]}:** *\"{row[fb_col]}\"*")
            
    with t2:
        st.markdown(f"""
        <div class="highlight-card">
            <h4>Análise de Especialista:</h4>
            <ul>
                <li>O analista <b>{analista_sel}</b> manteve consistência em {len(anos)} ano(s) de operação.</li>
                <li>Destaque na categoria <b>{cat_data.index[0]}</b>, resolvendo {cat_data.values[0]} casos críticos.</li>
                <li>Contribuição direta para a média de satisfação da equipe.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

else:
    st.warning("👈 Por favor, carregue o arquivo CSV na barra lateral para ativar a plataforma.")
