import os
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import plotly.express as px
import requests


# Configuração da página
st.set_page_config(
    page_title="🌱 Dashboard Sensores IoT",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS customizado - Compatível com light e dark mode
st.markdown("""
    <style>
    /* Main container adjustments */
    .main {
        padding: 1rem 2rem;
    }
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }
    
    /* Headers with better spacing */
    h1 {
        padding-bottom: 1rem;
        margin-bottom: 1.5rem;
        border-bottom: 3px solid #1f77b4;
    }
    
    h2, h3 {
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    /* Metric cards styling - adapts to theme */
    [data-testid="stMetric"] {
        background-color: var(--background-color);
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid var(--secondary-background-color);
    }
    
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
    }
    
    /* Expander styling - theme aware */
    [data-testid="stExpander"] {
        background-color: var(--secondary-background-color);
        border: 1px solid var(--secondary-background-color);
        border-radius: 0.5rem;
        margin-top: 1rem;
    }
    
    /* Button styling */
    .stButton button {
        border-radius: 0.5rem;
        font-weight: 500;
        padding: 0.5rem 1rem;
    }
    
    /* Selectbox improvements */
    div[data-baseweb="select"] > div {
        border-radius: 0.5rem;
    }
    
    /* Chart containers */
    .js-plotly-plot {
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    
    /* Spacing adjustments */
    .element-container {
        margin-bottom: 0.5rem;
    }
    
    /* Remove excessive padding from columns */
    [data-testid="column"] {
        padding: 0 0.5rem;
    }
    
    /* Dataframe styling */
    .dataframe {
        font-size: 0.9rem;
    }
    
    /* Download button */
    .stDownloadButton button {
        background-color: #4CAF50;
        color: white;
    }
    
    .stDownloadButton button:hover {
        background-color: #45a049;
    }
    
    /* Info boxes - ensure proper contrast */
    .stAlert {
        border-radius: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_db():
    """Inicializa conexão com Firebase (cached)"""
    try:
        if not firebase_admin._apps:
            cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "config/firebase-credentials.json")

            if not os.path.exists(cred_path):
                st.error(f"❌ Arquivo de credenciais não encontrado: {cred_path}")
                st.stop()

            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)

        db = firestore.client()
        return db
    except Exception as e:
        st.error(f"❌ Erro ao conectar com Firebase: {str(e)}")
        st.stop()


# NEW: Fetch data via API client
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
USE_API = os.getenv("USE_API", "0") in ["1", "true", "True", "TRUE"]


def fetch_via_api(limit: int = 100, device_id: str = None):
    """Busca dados chamando o endpoint FastAPI /sensor-data"""
    try:
        params = {"limit": limit}
        if device_id and device_id != "Todos":
            params["device_id"] = device_id
        url = f"{API_URL.rstrip('/')}/sensor-data"
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        payload = resp.json()
        # FastAPI retorna um dicionário com chave 'dados'
        return payload.get("dados", [])
    except Exception as e:
        st.error(f"❌ Erro ao consultar API ({API_URL}): {str(e)}")
        return []


# keep existing ver_dados but rename to fetch_firestore_data for clarity


def fetch_firestore_data(db, limit: int = 100, device_id: str = None):
    """Busca dados do Firebase (fallback)"""
    try:
        query = db.collection('sensor_readings')

        if device_id and device_id != "Todos":
            query = query.where('device_id', '==', device_id)

        docs = query.order_by('timestamp_recebido', direction=firestore.Query.DESCENDING).limit(limit).stream()

        resultados = []
        for doc in docs:
            dados = doc.to_dict()
            dados['id'] = doc.id
            resultados.append(dados)

        return resultados
    except Exception as e:
        st.error(f"❌ Erro ao consultar Firebase: {str(e)}")
        return []


# Adjust get_device_ids to optionally fetch from API

def get_device_ids(db):
    """Obtém lista de device IDs disponíveis"""
    try:
        if USE_API:
            # attempt to get device ids via API by requesting a small set
            docs = fetch_via_api(limit=100)
            device_ids = set()
            for entry in docs:
                if 'device_id' in entry:
                    device_ids.add(entry['device_id'])
            return sorted(list(device_ids))
        else:
            docs = db.collection('sensor_readings').limit(100).stream()
            device_ids = set()
            for doc in docs:
                dados = doc.to_dict()
                if 'device_id' in dados:
                    device_ids.add(dados['device_id'])
            return sorted(list(device_ids))
    except Exception as e:
        st.error(f"Erro ao buscar device IDs: {str(e)}")
        return []


def parse_dados_to_dataframe(dados):
    """Converte dados do Firebase para DataFrame pandas"""
    records = []
    
    for entry in dados:
        timestamp = pd.to_datetime(entry['timestamp'])
        sensors = entry.get('sensors', {})
        
        record = {
            'timestamp': timestamp,
            'device_id': entry.get('device_id', 'Unknown'),
            'dht11_temp': sensors.get('dht11', {}).get('temperature'),
            'dht11_humidity': sensors.get('dht11', {}).get('humidity'),
            'ds18b20_temp': sensors.get('ds18b20', {}).get('temperature'),
            'hl69_moisture': sensors.get('hl69', {}).get('soil_moisture'),
            'hl69_raw': sensors.get('hl69', {}).get('raw_value'),
            'hcsr04_distance': sensors.get('hcsr04', {}).get('distance'),
            'dht11_status': sensors.get('dht11', {}).get('status', 'unknown'),
            'ds18b20_status': sensors.get('ds18b20', {}).get('status', 'unknown'),
            'hl69_status': sensors.get('hl69', {}).get('status', 'unknown'),
            'hcsr04_status': sensors.get('hcsr04', {}).get('status', 'unknown'),
        }
        records.append(record)
    
    df = pd.DataFrame(records)
    if not df.empty:
        df = df.sort_values('timestamp')
    return df


def create_compact_overview_chart(df):
    """Cria um gráfico compacto com todos os sensores principais - theme aware"""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            '🌡️ Temperaturas', 
            '💧 Umidade do Ar', 
            '🌱 Umidade do Solo', 
            '📏 Distância'
        ),
        vertical_spacing=0.12,
        horizontal_spacing=0.10
    )
    
    # Temperaturas (DHT11 e DS18B20)
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'], 
            y=df['dht11_temp'], 
            mode='lines', 
            name='DHT11',
            line=dict(color='#FF6B6B', width=2.5),
            hovertemplate='<b>DHT11</b><br>%{y:.1f}°C<extra></extra>'
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'], 
            y=df['ds18b20_temp'], 
            mode='lines',
            name='DS18B20',
            line=dict(color='#4ECDC4', width=2.5),
            hovertemplate='<b>DS18B20</b><br>%{y:.1f}°C<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Umidade do Ar
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'], 
            y=df['dht11_humidity'], 
            mode='lines',
            name='Umidade Ar',
            line=dict(color='#2E86AB', width=2.5),
            fill='tozeroy', 
            fillcolor='rgba(46, 134, 171, 0.3)',
            hovertemplate='<b>Umidade Ar</b><br>%{y:.1f}%<extra></extra>'
        ),
        row=1, col=2
    )
    
    # Umidade do Solo
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'], 
            y=df['hl69_moisture'], 
            mode='lines',
            name='Umidade Solo',
            line=dict(color='#F77F00', width=2.5),
            fill='tozeroy', 
            fillcolor='rgba(247, 127, 0, 0.3)',
            hovertemplate='<b>Umidade Solo</b><br>%{y:.1f}%<extra></extra>'
        ),
        row=2, col=1
    )
    
    # Distância
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'], 
            y=df['hcsr04_distance'], 
            mode='lines',
            name='Distância',
            line=dict(color='#06A77D', width=2.5),
            hovertemplate='<b>Distância</b><br>%{y:.1f} cm<extra></extra>'
        ),
        row=2, col=2
    )
    
    # Update axes - no forced colors, let template handle it
    fig.update_xaxes(showticklabels=True, showgrid=True)
    fig.update_yaxes(title_text="°C", row=1, col=1, showgrid=True)
    fig.update_yaxes(title_text="%", row=1, col=2, showgrid=True)
    fig.update_yaxes(title_text="%", row=2, col=1, showgrid=True)
    fig.update_yaxes(title_text="cm", row=2, col=2, showgrid=True)
    
    # Use Streamlit's theme
    fig.update_layout(
        height=650,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=60, r=40, t=40, b=60),
        hovermode='x unified',
        template="plotly"  # Will adapt to Streamlit theme
    )
    
    return fig


def create_mini_gauge(value, title, min_val, max_val, color, unit):
    """Cria um mini gauge compacto - theme aware"""
    fig = go.Figure(go.Indicator(
        mode="number+gauge",
        value=value,
        domain={'x': [0, 1], 'y': [0.2, 1]},
        number={'suffix': unit, 'font': {'size': 28}},
        gauge={
            'axis': {'range': [min_val, max_val], 'tickwidth': 1},
            'bar': {'color': color, 'thickness': 0.75},
            'borderwidth': 2,
            'bordercolor': color,
            'steps': [
                {'range': [min_val, max_val], 'color': 'rgba(128, 128, 128, 0.2)'}
            ],
        },
        title={'text': title, 'font': {'size': 16}}
    ))
    
    fig.update_layout(
        height=200,
        margin=dict(l=20, r=20, t=40, b=20),
        template="plotly"  # Will adapt to Streamlit theme
    )
    
    return fig


def main():
    # Header
    col_title, col_controls = st.columns([4, 1])
    
    with col_title:
        st.title("🌱 Dashboard IoT - Telhado Verde")
    
    with col_controls:
        if st.button("🔄 Atualizar", type="primary"):
            st.cache_resource.clear()
            st.rerun()
    
    # Conecta ao Firebase apenas se necessário (fallback)
    db = None
    if not USE_API:
        db = get_db()

    # Filtros
    st.markdown("---")
    filter_col1, filter_col2, filter_col3 = st.columns([3, 2, 2])
    
    with filter_col1:
        device_ids = ["Todos"] + get_device_ids(db)
        selected_device = st.selectbox("📱 Selecione o Dispositivo", device_ids)
    
    with filter_col2:
        data_limit = st.select_slider(
            "📊 Número de Leituras", 
            options=[10, 25, 50, 100, 200, 500], 
            value=100
        )
    
    with filter_col3:
        auto_refresh = st.checkbox("🔄 Auto-refresh (10s)", value=False)
    
    st.markdown("---")
    
    # Busca dados
    with st.spinner("🔄 Carregando dados..."):
        device_param = None if selected_device == "Todos" else selected_device
        if USE_API:
            dados = fetch_via_api(limit=data_limit, device_id=device_param)
        else:
            dados = fetch_firestore_data(db, limit=data_limit, device_id=device_param)

        if not dados:
            st.warning("⚠️ Nenhum dado encontrado para os filtros selecionados.")
            st.stop()

        df = parse_dados_to_dataframe(dados)
    
    # Última leitura
    ultima_leitura = dados[0]
    sensors = ultima_leitura.get('sensors', {})
    
    # Métricas principais usando st.metric nativo
    st.subheader("📊 Leituras Atuais")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    dht11_temp = sensors.get('dht11', {}).get('temperature', 0)
    dht11_hum = sensors.get('dht11', {}).get('humidity', 0)
    ds18b20_temp = sensors.get('ds18b20', {}).get('temperature', 0)
    hl69_moisture = sensors.get('hl69', {}).get('soil_moisture', 0)
    hcsr04_dist = sensors.get('hcsr04', {}).get('distance', 0)
    
    with col1:
        status = "🟢" if sensors.get('dht11', {}).get('status') == "ok" else "🔴"
        st.metric(
            label=f"{status} Temp Ar (DHT11)",
            value=f"{dht11_temp:.1f}°C",
            delta=f"{dht11_temp - df['dht11_temp'].mean():.1f}°C"
        )
    
    with col2:
        status = "🟢" if sensors.get('dht11', {}).get('status') == "ok" else "🔴"
        st.metric(
            label=f"{status} Umidade Ar",
            value=f"{dht11_hum:.1f}%",
            delta=f"{dht11_hum - df['dht11_humidity'].mean():.1f}%"
        )
    
    with col3:
        status = "🟢" if sensors.get('ds18b20', {}).get('status') == "ok" else "🔴"
        st.metric(
            label=f"{status} Temp Solo (DS18B20)",
            value=f"{ds18b20_temp:.1f}°C",
            delta=f"{ds18b20_temp - df['ds18b20_temp'].mean():.1f}°C"
        )
    
    with col4:
        status = "🟢" if sensors.get('hl69', {}).get('status') == "ok" else "🔴"
        st.metric(
            label=f"{status} Umidade Solo",
            value=f"{hl69_moisture:.1f}%",
            delta=f"{hl69_moisture - df['hl69_moisture'].mean():.1f}%"
        )
    
    with col5:
        status = "🟢" if sensors.get('hcsr04', {}).get('status') == "ok" else "🔴"
        st.metric(
            label=f"{status} Distância",
            value=f"{hcsr04_dist:.1f} cm",
            delta=f"{hcsr04_dist - df['hcsr04_distance'].mean():.1f} cm"
        )
    
    # Gráfico principal
    st.subheader("📈 Histórico de Leituras")
    st.plotly_chart(create_compact_overview_chart(df), width='stretch')
    
    # Mini gauges
    st.subheader("🎯 Indicadores Visuais")
    gauge_col1, gauge_col2, gauge_col3, gauge_col4 = st.columns(4)
    
    with gauge_col1:
        st.plotly_chart(
            create_mini_gauge(dht11_temp, "Temp Ar", 0, 50, "#FF6B6B", "°C"), 
            width='stretch'
        )
    
    with gauge_col2:
        st.plotly_chart(
            create_mini_gauge(dht11_hum, "Umidade Ar", 0, 100, "#2E86AB", "%"), 
            width='stretch'
        )
    
    with gauge_col3:
        st.plotly_chart(
            create_mini_gauge(hl69_moisture, "Umidade Solo", 0, 100, "#F77F00", "%"), 
            width='stretch'
        )
    
    with gauge_col4:
        st.plotly_chart(
            create_mini_gauge(hcsr04_dist, "Distância", 0, 50, "#06A77D", " cm"), 
            width='stretch'
        )
    
    # Estatísticas
    with st.expander("📊 Estatísticas Detalhadas do Período", expanded=False):
        stats_col1, stats_col2 = st.columns(2)
        
        with stats_col1:
            st.markdown("**Sensores de Temperatura e Umidade**")
            stats_df1 = pd.DataFrame({
                'Sensor': ['DHT11 Temp (°C)', 'DHT11 Umid (%)', 'DS18B20 (°C)'],
                'Atual': [
                    f"{dht11_temp:.1f}",
                    f"{dht11_hum:.1f}",
                    f"{ds18b20_temp:.1f}"
                ],
                'Mínimo': [
                    f"{df['dht11_temp'].min():.1f}",
                    f"{df['dht11_humidity'].min():.1f}",
                    f"{df['ds18b20_temp'].min():.1f}"
                ],
                'Máximo': [
                    f"{df['dht11_temp'].max():.1f}",
                    f"{df['dht11_humidity'].max():.1f}",
                    f"{df['ds18b20_temp'].max():.1f}"
                ],
                'Média': [
                    f"{df['dht11_temp'].mean():.1f}",
                    f"{df['dht11_humidity'].mean():.1f}",
                    f"{df['ds18b20_temp'].mean():.1f}"
                ]
            })
            st.dataframe(stats_df1, width='stretch', hide_index=True)
        
        with stats_col2:
            st.markdown("**Sensores de Solo e Distância**")
            stats_df2 = pd.DataFrame({
                'Sensor': ['HL69 Umidade Solo (%)', 'HCSR04 Distância (cm)'],
                'Atual': [
                    f"{hl69_moisture:.1f}",
                    f"{hcsr04_dist:.1f}"
                ],
                'Mínimo': [
                    f"{df['hl69_moisture'].min():.1f}",
                    f"{df['hcsr04_distance'].min():.1f}"
                ],
                'Máximo': [
                    f"{df['hl69_moisture'].max():.1f}",
                    f"{df['hcsr04_distance'].max():.1f}"
                ],
                'Média': [
                    f"{df['hl69_moisture'].mean():.1f}",
                    f"{df['hcsr04_distance'].mean():.1f}"
                ]
            })
            st.dataframe(stats_df2, width='stretch', hide_index=True)
    
    # Dados brutos
    with st.expander("🔍 Visualizar Dados Brutos", expanded=False):
        st.dataframe(df, width='stretch', hide_index=True)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f'sensor_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
            mime='text/csv',
        )
    
    # Footer
    st.markdown("---")
    footer_col1, footer_col2, footer_col3 = st.columns(3)
    
    with footer_col1:
        st.info(f"**Device ID:** {ultima_leitura['device_id']}")
    
    with footer_col2:
        periodo = df['timestamp'].max() - df['timestamp'].min()
        st.info(f"**Leituras:** {len(df)} | **Período:** {periodo}")
    
    with footer_col3:
        st.info(f"**Última Atualização:** {datetime.now().strftime('%H:%M:%S')}")
    
    # Auto-refresh
    if auto_refresh:
        import time
        time.sleep(10)
        st.rerun()


if __name__ == "__main__":
    main()
