import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import os
from pathlib import Path
import random
import time
import base64
from io import BytesIO

# --- PAGE CONFIG FOR MOBILE FIRST ---
st.set_page_config(
    page_title="Offshore Rig Workflow Tracker",
    page_icon="⛴️",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None
)

# --- MOBILE-RESPONSIVE CSS ---
st.markdown("""
<style>
    /* Base responsive design */
    @media (max-width: 768px) {
        .main-header {
            font-size: 1.8rem !important;
            text-align: center;
        }
        .metric-card {
            padding: 0.8rem !important;
            margin-bottom: 0.5rem;
        }
        .stMetric {
            padding: 0.3rem;
        }
        /* Stack columns on mobile */
        .element-container {
            margin-bottom: 0.5rem;
        }
        /* Better mobile table view */
        .dataframe {
            font-size: 11px;
        }
        /* Adjust sidebar for mobile */
        .sidebar .sidebar-content {
            width: 100% !important;
            transform: none !important;
        }
        /* Make buttons more touch-friendly */
        .stButton button {
            padding: 0.8rem 1rem;
            font-size: 14px;
        }
    }

    @media (min-width: 769px) {
        .sidebar .sidebar-content {
            width: 280px !important;
        }
    }

    /* Professional color scheme */
    :root {
        --primary: #1e3a8a;
        --secondary: #3b82f6;
        --accent: #10b981;
        --danger: #ef4444;
        --warning: #f59e0b;
        --light: #f8fafc;
        --dark: #0f172a;
    }

    .main {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    }

    .main-header {
        font-size: 2.5rem;
        color: var(--primary);
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 1rem;
    }

    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
        text-align: center;
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
    }

    .urgent-alert {
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid var(--danger);
        margin: 0.5rem 0;
        animation: pulse 2s infinite;
    }

    .info-alert {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid var(--accent);
        margin: 0.5rem 0;
    }

    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--primary) 0%, var(--secondary) 100%);
    }

    /* Button styling */
    .stButton button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        width: 100%;
        margin: 0.25rem 0;
    }

    /* Animation */
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.3); }
        70% { box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
        100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }

    /* Data table responsiveness */
    .dataframe {
        width: 100%;
        font-size: 14px;
    }

    /* Chart container responsiveness */
    .js-plotly-plot {
        width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)

# --- SIMPLIFIED LOGIN SCREEN ---
def login_screen():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 2rem; background: white; border-radius: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            <h1 style='font-size: 2.5rem; margin-bottom: 1rem;'>⛴️</h1>
            <h2 style='color: #1e3a8a; margin-bottom: 1rem;'>Offshore Operations Portal</h2>
            <p style='color: #64748b; margin-bottom: 2rem;'>Enterprise Rig Management System</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("👤 Username", value="admin")
            password = st.text_input("🔒 Password", type="password", value="••••••••")
            login_button = st.form_submit_button("🚀 Login to Dashboard")
            
            if login_button:
                if username == "admin" and password == "offshore2025":
                    with st.spinner("Authenticating..."):
                        time.sleep(1)
                    st.session_state.logged_in = True
                    st.experimental_rerun()
                else:
                    st.error("Invalid credentials")

# --- DATA MANAGEMENT ---
def load_data():
    data_file = Path("rig_data.csv")
    if data_file.exists():
        df = pd.read_csv(data_file, parse_dates=['Rig_Start', 'Rig_End', 'Start_Date', 'End_Date'])
    else:
        df = generate_sample_data()
        df.to_csv(data_file, index=False)
    return df

def generate_sample_data(num_rigs=8, num_requests_per_rig=2):
    rig_names = ["Deepwater Horizon", "Ocean Explorer", "Sea Guardian", "Marine Pioneer", 
                "Offshore Venture", "Blue Wave", "Pacific Driller", "Atlantic Explorer"]
    requestors = ["Client A", "Client B", "Supplier X", "Internal Team", "Regulatory Body"]
    actions = ["Supply Delivery", "Maintenance", "Safety Audit", "Personnel Change", "Data Submission"]
    data = []

    for i in range(num_rigs):
        rig = rig_names[i] if i < len(rig_names) else f"Rig_{i+1:03d}"
        rig_start = pd.Timestamp.now() - pd.Timedelta(days=random.randint(0, 30))
        rig_duration = pd.Timedelta(days=random.randint(15, 60))
        rig_end = rig_start + rig_duration
        overall_status = "Complete" if pd.Timestamp.now() > rig_end else "Active"

        for _ in range(random.randint(1, num_requests_per_rig)):
            req_start_offset = random.randint(0, (rig_end - rig_start).days)
            req_start = rig_start + pd.Timedelta(days=req_start_offset)
            req_duration = pd.Timedelta(days=random.randint(1, 14))
            req_end = req_start + req_duration
            req_status = "Complete" if pd.Timestamp.now() > req_end else "Active"

            request_data = {
                "Rig": rig, "Rig_Start": rig_start, "Rig_End": rig_end, "Rig_Status": overall_status,
                "Request_ID": f"REQ-{random.randint(1000, 9999)}", "Action_Requested": random.choice(actions),
                "Requestor": random.choice(requestors), "Start_Date": req_start, "End_Date": req_end,
                "Duration_Days": req_duration.days, "Action_Doable": random.choice([True, False]),
                "Action_Complete": req_status == "Complete", "Response_Provided": random.choice([True, False]) if req_status == "Complete" else False,
                "Priority": random.choice(["High", "Medium", "Low"])
            }
            data.append(request_data)

    return pd.DataFrame(data)

# --- CHECK LOGIN STATUS ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_screen()
    st.stop()

# --- MAIN APPLICATION ---
df = load_data()
date_columns = ['Rig_Start', 'Rig_End', 'Start_Date', 'End_Date']
for col in date_columns:
    df[col] = pd.to_datetime(df[col])

# Initialize filters with default values if they don't exist
if 'status_filter' not in st.session_state:
    st.session_state.status_filter = df['Rig_Status'].unique().tolist()
if 'rig_filter' not in st.session_state:
    st.session_state.rig_filter = []
if 'menu_open' not in st.session_state:
    st.session_state.menu_open = False

# --- MOBILE-FRIENDLY LAYOUT ---
st.markdown('<h1 class="main-header">⛴️ Offshore Rig Workflow Tracker</h1>', unsafe_allow_html=True)

# Mobile menu button
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if st.button("☰ Menu"):
        st.session_state.menu_open = not st.session_state.menu_open

# Sidebar for filters (collapsible on mobile)
if st.session_state.menu_open:
    with st.sidebar:
        st.markdown("### 📊 Filters")
        date_range = st.date_input("Date Range", value=(
            pd.Timestamp.now() - pd.Timedelta(days=30),
            pd.Timestamp.now() + pd.Timedelta(days=30)
        ))
        
        # Update to use session state
        st.session_state.status_filter = st.multiselect(
            "Rig Status", 
            options=df['Rig_Status'].unique(), 
            default=st.session_state.status_filter
        )
        st.session_state.rig_filter = st.multiselect(
            "Select Rigs", 
            options=sorted(df['Rig'].unique()),
            default=st.session_state.rig_filter
        )
        
        if st.button("Close Menu"):
            st.session_state.menu_open = False

# Apply filters
filtered_df = df.copy()
if st.session_state.status_filter:
    filtered_df = filtered_df[filtered_df['Rig_Status'].isin(st.session_state.status_filter)]
if st.session_state.rig_filter:
    filtered_df = filtered_df[filtered_df['Rig'].isin(st.session_state.rig_filter)]

# --- RESPONSIVE METRICS ROW ---
st.markdown("### 📈 Performance Overview")
metrics_cols = st.columns(2)  # 2 columns on mobile, will adjust automatically

with metrics_cols[0]:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Total Rigs", df['Rig'].nunique())
    st.markdown('</div>', unsafe_allow_html=True)

with metrics_cols[1]:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    month_requests = len(df[df['Start_Date'].dt.month == pd.Timestamp.now().month])
    st.metric("Monthly Requests", month_requests)
    st.markdown('</div>', unsafe_allow_html=True)

# Second row of metrics
metrics_cols2 = st.columns(2)
with metrics_cols2[0]:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    overdue = len(df[(df['End_Date'] < pd.Timestamp.now()) & (df['Action_Complete'] == False)])
    st.metric("Overdue Tasks", overdue, delta=f"{overdue} urgent")
    st.markdown('</div>', unsafe_allow_html=True)

with metrics_cols2[1]:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    upcoming = len(df[(df['End_Date'] > pd.Timestamp.now()) & (df['End_Date'] <= pd.Timestamp.now() + pd.Timedelta(days=7))])
    st.metric("Upcoming Tasks", upcoming)
    st.markdown('</div>', unsafe_allow_html=True)

# --- NOTIFICATIONS ---
st.markdown("### 🔔 Notifications")
urgent_tasks = df[(df['End_Date'] >= pd.Timestamp.now()) & (df['End_Date'] <= pd.Timestamp.now() + pd.Timedelta(days=3)) & (df['Action_Complete'] == False)]

if not urgent_tasks.empty:
    for _, task in urgent_tasks.iterrows():
        days_left = (task['End_Date'] - pd.Timestamp.now()).days
        st.markdown(f'''
        <div class="urgent-alert">
            <b>URGENT:</b> {task['Rig']} - {task['Action_Requested']}<br>
            Due in {days_left} days | Requested by: {task['Requestor']}
        </div>
        ''', unsafe_allow_html=True)
else:
    st.markdown('<div class="info-alert">No urgent actions required in the next 3 days</div>', unsafe_allow_html=True)

# --- GANTT CHART ---
st.markdown("### 📅 Timeline View")
gantt_data = []
for _, row in filtered_df.iterrows():
    gantt_data.append(dict(Task=row['Rig'], Start=row['Rig_Start'], Finish=row['Rig_End'], Resource="Rig Operation"))
    gantt_data.append(dict(Task=row['Rig'], Start=row['Start_Date'], Finish=row['End_Date'], Resource=row['Action_Requested']))

gantt_df = pd.DataFrame(gantt_data)
if not gantt_df.empty:
    fig = px.timeline(gantt_df, x_start="Start", x_end="Finish", y="Task", color="Resource", height=400)
    fig.update_yaxes(autorange="reversed")  # Fixed the typo here (autorrange -> autorange)
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data available for the selected filters")

# --- DATA TABLE ---
st.markdown("### 📋 Request Details")
detailed_view = filtered_df[["Rig", "Request_ID", "Action_Requested", "Requestor", "Start_Date", "End_Date", "Action_Complete"]].copy()
detailed_view['Start_Date'] = detailed_view['Start_Date'].dt.strftime('%Y-%m-%d')
detailed_view['End_Date'] = detailed_view['End_Date'].dt.strftime('%Y-%m-%d')

st.dataframe(detailed_view, use_container_width=True, height=300)

# --- EXPORT FUNCTIONALITY ---
st.markdown("### 📤 Export Data")
if st.button("Export Filtered Data to CSV"):
    csv = filtered_df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="rig_data_export.csv">Download CSV File</a>'
    st.markdown(href, unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #64748b; padding: 1rem;'>
    <p><strong>Offshore Rig Workflow Tracker v2.0</strong> | Built with Streamlit</p>
    <p style='font-size: 0.8rem;'>Optimized for all devices | Professional Edition</p>
</div>
""", unsafe_allow_html=True)
