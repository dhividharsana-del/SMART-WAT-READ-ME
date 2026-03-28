import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import kagglehub
import os
import warnings
warnings.filterwarnings('ignore')

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SmartWatt — Steel Energy Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Share+Tech+Mono&family=Inter:wght@300;400;500&display=swap');

/* ── ROOT THEME ── */
:root {
    --bg-dark:     #0a0e1a;
    --bg-card:     #0f1629;
    --bg-panel:    #131d35;
    --accent:      #00e5ff;
    --accent2:     #ff6b35;
    --accent3:     #39ff14;
    --text-bright: #e8f4fd;
    --text-muted:  #6b8cba;
    --border:      rgba(0,229,255,0.15);
    --glow:        0 0 20px rgba(0,229,255,0.3);
}

/* ── BASE ── */
.stApp {
    background: var(--bg-dark) !important;
    font-family: 'Inter', sans-serif;
}

/* ── HIDE DEFAULT ELEMENTS ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem !important; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0e1a 0%, #0f1629 100%) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text-bright) !important; }

/* ── HEADER ── */
.dash-header {
    background: linear-gradient(135deg, #0f1629 0%, #131d35 50%, #0a0e1a 100%);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.dash-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent), var(--accent2), transparent);
}
.dash-header h1 {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.2rem;
    font-weight: 700;
    color: var(--accent) !important;
    margin: 0;
    letter-spacing: 2px;
    text-shadow: var(--glow);
}
.dash-header p {
    color: var(--text-muted) !important;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.8rem;
    margin: 0.3rem 0 0 0;
    letter-spacing: 1px;
}

/* ── KPI CARDS ── */
.kpi-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
}
.kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: var(--glow);
}
.kpi-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0; height: 3px;
    background: var(--accent);
}
.kpi-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    color: var(--text-muted);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.kpi-value {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: var(--accent);
    line-height: 1;
}
.kpi-unit {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.75rem;
    color: var(--text-muted);
    margin-top: 0.3rem;
}
.kpi-delta-pos { color: var(--accent3) !important; font-size: 0.8rem; }
.kpi-delta-neg { color: var(--accent2) !important; font-size: 0.8rem; }

/* ── SECTION TITLES ── */
.section-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--accent);
    letter-spacing: 3px;
    text-transform: uppercase;
    border-left: 3px solid var(--accent);
    padding-left: 0.8rem;
    margin: 1.5rem 0 1rem 0;
}

/* ── SELECTBOX / SLIDER ── */
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-bright) !important;
    border-radius: 6px !important;
}
.stSlider > div > div > div { background: var(--accent) !important; }

/* ── DATAFRAME ── */
.stDataFrame { border: 1px solid var(--border) !important; border-radius: 8px; }

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-card);
    border-radius: 8px;
    border: 1px solid var(--border);
    gap: 4px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-muted) !important;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.8rem;
    letter-spacing: 1px;
    border-radius: 6px !important;
}
.stTabs [aria-selected="true"] {
    background: var(--accent) !important;
    color: var(--bg-dark) !important;
}
</style>
""", unsafe_allow_html=True)

# ─── PLOTLY DARK THEME ───────────────────────────────────────────────────────
CHART_THEME = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(15,22,41,0.6)',
    font=dict(color='#6b8cba', family='Share Tech Mono'),
    xaxis=dict(gridcolor='rgba(0,229,255,0.07)', zerolinecolor='rgba(0,229,255,0.1)'),
    yaxis=dict(gridcolor='rgba(0,229,255,0.07)', zerolinecolor='rgba(0,229,255,0.1)'),
    colorway=['#00e5ff','#ff6b35','#39ff14','#a855f7','#fbbf24','#ec4899'],
)

# ─── LOAD DATA ───────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data():
    path = kagglehub.dataset_download("csafrit2/steel-industry-energy-consumption")
    csv_path = os.path.join(path, "Steel_industry_data.csv")
    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'], dayfirst=True)
    df['Hour']  = df['date'].dt.hour
    df['Month'] = df['date'].dt.month
    df['Month_Name'] = df['date'].dt.strftime('%b')
    df['Date_Only'] = df['date'].dt.date
    return df

with st.spinner("⚡ Loading energy data..."):
    df = load_data()

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0;'>
        <div style='font-family:Rajdhani,sans-serif; font-size:1.4rem; font-weight:700;
                    color:#00e5ff; letter-spacing:3px;'>⚡ SMARTWATT</div>
        <div style='font-family:Share Tech Mono,monospace; font-size:0.65rem;
                    color:#6b8cba; letter-spacing:2px; margin-top:4px;'>
            STEEL ENERGY INTELLIGENCE
        </div>
    </div>
    <hr style='border-color:rgba(0,229,255,0.15); margin:0.5rem 0 1rem 0;'>
    """, unsafe_allow_html=True)

    st.markdown("**📅 Date Range**")
    date_min = df['date'].min().date()
    date_max = df['date'].max().date()
    date_range = st.date_input("", [date_min, date_max],
                               min_value=date_min, max_value=date_max)

    st.markdown("**🏭 Load Type**")
    load_types = ['All'] + sorted(df['Load_Type'].unique().tolist())
    selected_load = st.selectbox("", load_types)

    st.markdown("**📆 Week Status**")
    week_options = ['All', 'Weekday', 'Weekend']
    selected_week = st.selectbox(" ", week_options)

    st.markdown("""
    <hr style='border-color:rgba(0,229,255,0.1); margin:1rem 0;'>
    <div style='font-family:Share Tech Mono,monospace; font-size:0.65rem;
                color:#6b8cba; text-align:center; letter-spacing:1px;'>
        SMARTWATT TECHNOLOGIES<br>Energy Analytics v2.0
    </div>
    """, unsafe_allow_html=True)

# ─── FILTER DATA ─────────────────────────────────────────────────────────────
filtered = df.copy()
if len(date_range) == 2:
    filtered = filtered[(filtered['date'].dt.date >= date_range[0]) &
                        (filtered['date'].dt.date <= date_range[1])]
if selected_load != 'All':
    filtered = filtered[filtered['Load_Type'] == selected_load]
if selected_week != 'All':
    filtered = filtered[filtered['WeekStatus'] == selected_week]

# ─── HEADER ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class='dash-header'>
    <h1>⚡ SMARTWATT ENERGY DASHBOARD</h1>
    <p>STEEL INDUSTRY · REAL-TIME ENERGY INTELLIGENCE · {len(filtered):,} RECORDS LOADED</p>
</div>
""", unsafe_allow_html=True)

# ─── KPI CARDS ───────────────────────────────────────────────────────────────
total_kwh    = filtered['Usage_kWh'].sum()
avg_kwh      = filtered['Usage_kWh'].mean()
total_co2    = filtered['CO2(tCO2)'].sum()
avg_pf_lag   = filtered['Lagging_Current_Power_Factor'].mean()
avg_pf_lead  = filtered['Leading_Current_Power_Factor'].mean()
peak_kwh     = filtered['Usage_kWh'].max()

col1, col2, col3, col4, col5, col6 = st.columns(6)

kpis = [
    (col1, "TOTAL ENERGY",    f"{total_kwh/1000:.1f}K", "kWh consumed",     "accent"),
    (col2, "AVG CONSUMPTION", f"{avg_kwh:.2f}",         "kWh per interval", "accent"),
    (col3, "TOTAL CO₂",       f"{total_co2:.1f}",       "tCO₂ emitted",     "accent2"),
    (col4, "PEAK DEMAND",     f"{peak_kwh:.2f}",        "kWh maximum",      "accent"),
    (col5, "LAG POWER FACTOR",f"{avg_pf_lag:.1f}%",     "average lagging",  "accent3"),
    (col6, "LEAD POWER FACTOR",f"{avg_pf_lead:.1f}%",   "average leading",  "accent3"),
]

colors = {'accent':'#00e5ff', 'accent2':'#ff6b35', 'accent3':'#39ff14'}
for col, label, value, unit, color_key in kpis:
    color = colors[color_key]
    with col:
        st.markdown(f"""
        <div class='kpi-card' style='border-bottom-color:{color};'>
            <div class='kpi-label'>{label}</div>
            <div class='kpi-value' style='color:{color};'>{value}</div>
            <div class='kpi-unit'>{unit}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📈  ENERGY TRENDS",
    "🔥  LOAD ANALYSIS",
    "⚙️  POWER QUALITY",
    "📊  STATISTICS"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — ENERGY TRENDS
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("<div class='section-title'>ENERGY CONSUMPTION OVER TIME</div>", unsafe_allow_html=True)

    # Daily aggregation
    daily = filtered.groupby('Date_Only').agg(
        Usage_kWh=('Usage_kWh','sum'),
        CO2=('CO2(tCO2)','sum')
    ).reset_index()

    fig1 = make_subplots(rows=2, cols=1, shared_xaxes=True,
                         row_heights=[0.65, 0.35], vertical_spacing=0.05)

    fig1.add_trace(go.Scatter(
        x=daily['Date_Only'], y=daily['Usage_kWh'],
        fill='tozeroy',
        fillcolor='rgba(0,229,255,0.08)',
        line=dict(color='#00e5ff', width=1.5),
        name='Daily kWh'
    ), row=1, col=1)

    # 7-day rolling avg
    daily['MA7'] = daily['Usage_kWh'].rolling(7).mean()
    fig1.add_trace(go.Scatter(
        x=daily['Date_Only'], y=daily['MA7'],
        line=dict(color='#ff6b35', width=2, dash='dot'),
        name='7-Day Avg'
    ), row=1, col=1)

    fig1.add_trace(go.Bar(
        x=daily['Date_Only'], y=daily['CO2'],
        marker_color='rgba(255,107,53,0.5)',
        name='CO₂ (tCO₂)'
    ), row=2, col=1)

    fig1.update_layout(**CHART_THEME, height=420,
                       legend=dict(orientation='h', y=1.05, x=0),
                       margin=dict(l=0,r=0,t=30,b=0))
    fig1.update_yaxes(title_text="kWh", row=1, col=1, title_font_color='#6b8cba')
    fig1.update_yaxes(title_text="tCO₂", row=2, col=1, title_font_color='#6b8cba')
    st.plotly_chart(fig1, use_container_width=True)

    # Hourly heatmap
    st.markdown("<div class='section-title'>HOURLY CONSUMPTION HEATMAP</div>", unsafe_allow_html=True)
    heatmap_data = filtered.groupby(['Day_of_week','Hour'])['Usage_kWh'].mean().reset_index()
    day_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    heatmap_pivot = heatmap_data.pivot(index='Day_of_week', columns='Hour', values='Usage_kWh')
    heatmap_pivot = heatmap_pivot.reindex([d for d in day_order if d in heatmap_pivot.index])

    fig_heat = go.Figure(go.Heatmap(
        z=heatmap_pivot.values,
        x=[f"{h:02d}:00" for h in heatmap_pivot.columns],
        y=heatmap_pivot.index.tolist(),
        colorscale=[[0,'#0a0e1a'],[0.3,'#003d4d'],[0.6,'#00e5ff'],[1,'#ff6b35']],
        showscale=True,
        colorbar=dict(tickfont=dict(color='#6b8cba'), title=dict(text='kWh', font=dict(color='#6b8cba')))
    ))
    fig_heat.update_layout(**CHART_THEME, height=280, margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig_heat, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — LOAD ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("<div class='section-title'>LOAD TYPE DISTRIBUTION</div>", unsafe_allow_html=True)
        load_dist = filtered['Load_Type'].value_counts().reset_index()
        load_dist.columns = ['Load_Type','Count']
        fig_pie = go.Figure(go.Pie(
            labels=load_dist['Load_Type'],
            values=load_dist['Count'],
            hole=0.6,
            marker=dict(colors=['#00e5ff','#ff6b35','#39ff14'],
                        line=dict(color='#0a0e1a', width=2)),
            textfont=dict(family='Share Tech Mono', color='#e8f4fd', size=11)
        ))
        fig_pie.add_annotation(text=f"<b>{len(filtered):,}</b><br><span style='font-size:10px'>Records</span>",
                               x=0.5, y=0.5, showarrow=False,
                               font=dict(color='#00e5ff', size=14, family='Rajdhani'))
        fig_pie.update_layout(**CHART_THEME, height=320,
                              showlegend=True,
                              legend=dict(font=dict(color='#6b8cba', family='Share Tech Mono')),
                              margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig_pie, use_container_width=True)

    with c2:
        st.markdown("<div class='section-title'>AVG ENERGY BY LOAD TYPE</div>", unsafe_allow_html=True)
        load_avg = filtered.groupby('Load_Type')['Usage_kWh'].mean().reset_index()
        fig_bar = go.Figure(go.Bar(
            x=load_avg['Load_Type'], y=load_avg['Usage_kWh'],
            marker=dict(
                color=['#00e5ff','#ff6b35','#39ff14'],
                line=dict(color='rgba(0,0,0,0)', width=0)
            ),
            text=load_avg['Usage_kWh'].round(2),
            textposition='outside',
            textfont=dict(color='#e8f4fd', family='Share Tech Mono', size=10)
        ))
        fig_bar.update_layout(**CHART_THEME, height=320,
                              margin=dict(l=0,r=0,t=10,b=0),
                              yaxis_title='Avg kWh')
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("<div class='section-title'>WEEKDAY vs WEEKEND ENERGY PATTERN</div>", unsafe_allow_html=True)
    hourly_week = filtered.groupby(['WeekStatus','Hour'])['Usage_kWh'].mean().reset_index()
    fig_week = go.Figure()
    for ws, color in [('Weekday','#00e5ff'),('Weekend','#ff6b35')]:
        d = hourly_week[hourly_week['WeekStatus']==ws]
        fig_week.add_trace(go.Scatter(
            x=d['Hour'], y=d['Usage_kWh'],
            mode='lines+markers',
            name=ws,
            line=dict(color=color, width=2),
            marker=dict(size=5, color=color),
            fill='tozeroy',
            fillcolor=f"rgba({'0,229,255' if ws=='Weekday' else '255,107,53'},0.07)"
        ))
    fig_week.update_layout(**CHART_THEME, height=300,
                           xaxis_title='Hour of Day',
                           yaxis_title='Avg kWh',
                           legend=dict(font=dict(color='#6b8cba')),
                           margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig_week, use_container_width=True)

    # Monthly breakdown
    st.markdown("<div class='section-title'>MONTHLY ENERGY BREAKDOWN</div>", unsafe_allow_html=True)
    monthly = filtered.groupby(['Month','Month_Name']).agg(
        Total_kWh=('Usage_kWh','sum'),
        Avg_kWh=('Usage_kWh','mean'),
        Total_CO2=('CO2(tCO2)','sum')
    ).reset_index().sort_values('Month')

    fig_month = go.Figure()
    fig_month.add_trace(go.Bar(
        x=monthly['Month_Name'], y=monthly['Total_kWh'],
        name='Total kWh',
        marker_color='rgba(0,229,255,0.7)',
        yaxis='y'
    ))
    fig_month.add_trace(go.Scatter(
        x=monthly['Month_Name'], y=monthly['Total_CO2'],
        name='Total CO₂',
        line=dict(color='#ff6b35', width=2),
        marker=dict(size=6),
        yaxis='y2'
    ))
    fig_month.update_layout(
        **CHART_THEME, height=320,
        yaxis=dict(title='kWh', gridcolor='rgba(0,229,255,0.07)'),
        yaxis2=dict(title='tCO₂', overlaying='y', side='right', gridcolor='rgba(255,107,53,0.05)'),
        legend=dict(font=dict(color='#6b8cba', family='Share Tech Mono')),
        margin=dict(l=0,r=0,t=10,b=0)
    )
    st.plotly_chart(fig_month, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — POWER QUALITY
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("<div class='section-title'>POWER FACTOR ANALYSIS</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        fig_pf = go.Figure()
        for col_name, color, label in [
            ('Lagging_Current_Power_Factor', '#00e5ff', 'Lagging PF'),
            ('Leading_Current_Power_Factor', '#ff6b35', 'Leading PF')
        ]:
            fig_pf.add_trace(go.Histogram(
                x=filtered[col_name],
                name=label,
                marker_color=color,
                opacity=0.65,
                nbinsx=40
            ))
        fig_pf.update_layout(**CHART_THEME, height=300, barmode='overlay',
                             xaxis_title='Power Factor (%)',
                             legend=dict(font=dict(color='#6b8cba')),
                             margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig_pf, use_container_width=True)

    with c2:
        fig_reactive = go.Figure()
        fig_reactive.add_trace(go.Scatter(
            x=filtered['Lagging_Current_Reactive.Power_kVarh'].sample(min(2000,len(filtered))),
            y=filtered['Usage_kWh'].sample(min(2000,len(filtered))),
            mode='markers',
            marker=dict(color='#00e5ff', size=3, opacity=0.4),
            name='Lagging Reactive vs Usage'
        ))
        fig_reactive.update_layout(**CHART_THEME, height=300,
                                   xaxis_title='Lagging Reactive Power (kVArh)',
                                   yaxis_title='Usage (kWh)',
                                   margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig_reactive, use_container_width=True)

    st.markdown("<div class='section-title'>CO₂ vs ENERGY CORRELATION</div>", unsafe_allow_html=True)
    sample_df = filtered.sample(min(3000, len(filtered)))
    fig_co2 = px.scatter(
        sample_df, x='Usage_kWh', y='CO2(tCO2)',
        color='Load_Type',
        color_discrete_map={'Light_Load':'#00e5ff','Medium_Load':'#ff6b35','Maximum_Load':'#39ff14'},
        opacity=0.6,
        size_max=8
    )
    fig_co2.update_layout(**CHART_THEME, height=350,
                          xaxis_title='Energy Usage (kWh)',
                          yaxis_title='CO₂ Emissions (tCO₂)',
                          legend=dict(font=dict(color='#6b8cba', family='Share Tech Mono')),
                          margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig_co2, use_container_width=True)

    # NSM Analysis
    st.markdown("<div class='section-title'>NSM (NUMBER OF SECONDS FROM MIDNIGHT)</div>", unsafe_allow_html=True)
    nsm_avg = filtered.groupby('NSM')['Usage_kWh'].mean().reset_index()
    fig_nsm = go.Figure(go.Scatter(
        x=nsm_avg['NSM'] / 3600,
        y=nsm_avg['Usage_kWh'],
        fill='tozeroy',
        fillcolor='rgba(57,255,20,0.06)',
        line=dict(color='#39ff14', width=1.5),
        name='Avg kWh'
    ))
    fig_nsm.update_layout(**CHART_THEME, height=260,
                          xaxis_title='Hour (from midnight)',
                          yaxis_title='Avg kWh',
                          margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig_nsm, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — STATISTICS
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("<div class='section-title'>DESCRIPTIVE STATISTICS</div>", unsafe_allow_html=True)

    num_cols = ['Usage_kWh','Lagging_Current_Reactive.Power_kVarh',
                'Leading_Current_Reactive_Power_kVarh','CO2(tCO2)',
                'Lagging_Current_Power_Factor','Leading_Current_Power_Factor']
    stats_df = filtered[num_cols].describe().round(3)
    st.dataframe(stats_df.style.background_gradient(cmap='Blues'), use_container_width=True)

    st.markdown("<div class='section-title'>BOX PLOT — ENERGY BY LOAD TYPE</div>", unsafe_allow_html=True)
    fig_box = go.Figure()
    for lt, color in [('Light_Load','#00e5ff'),('Medium_Load','#ff6b35'),('Maximum_Load','#39ff14')]:
        d = filtered[filtered['Load_Type']==lt]['Usage_kWh']
        if len(d):
            fig_box.add_trace(go.Box(
                y=d, name=lt,
                marker_color=color,
                line_color=color,
                fillcolor=f"rgba({color[1:3]},{color[3:5]},{color[5:7]},0.2)".replace(
                    f"rgba({color[1:3]},{color[3:5]},{color[5:7]},0.2)",
                    f"rgba(0,0,0,0.2)"
                ),
                boxmean='sd'
            ))
    fig_box.update_layout(**CHART_THEME, height=350,
                          yaxis_title='kWh',
                          legend=dict(font=dict(color='#6b8cba')),
                          margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig_box, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='section-title'>TOP 10 PEAK DEMAND HOURS</div>", unsafe_allow_html=True)
        top10 = filtered.nlargest(10, 'Usage_kWh')[['date','Usage_kWh','Load_Type','CO2(tCO2)']].reset_index(drop=True)
        top10['date'] = top10['date'].dt.strftime('%Y-%m-%d %H:%M')
        st.dataframe(top10, use_container_width=True)

    with c2:
        st.markdown("<div class='section-title'>LOAD TYPE SUMMARY</div>", unsafe_allow_html=True)
        summary = filtered.groupby('Load_Type').agg(
            Count=('Usage_kWh','count'),
            Avg_kWh=('Usage_kWh','mean'),
            Total_kWh=('Usage_kWh','sum'),
            Avg_CO2=('CO2(tCO2)','mean')
        ).round(3).reset_index()
        st.dataframe(summary, use_container_width=True)

# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.markdown("""
<hr style='border-color:rgba(0,229,255,0.1); margin:2rem 0 1rem 0;'>
<div style='text-align:center; font-family:Share Tech Mono,monospace;
            font-size:0.7rem; color:#6b8cba; letter-spacing:2px; padding-bottom:1rem;'>
    ⚡ SMARTWATT TECHNOLOGIES · STEEL ENERGY INTELLIGENCE DASHBOARD · 2026
</div>
""", unsafe_allow_html=True)
