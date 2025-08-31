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
import json

# --- PAGE CONFIG WITH CUSTOM FAVICON ---
st.set_page_config(
    page_title="Offshore Rig Workflow Tracker",
    page_icon="⛴️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/Princeeze744/rig-workflow-tracker',
        'Report a bug': None,
        'About': "## Offshore Rig Workflow Tracker\nProfessional rig operations management system."
    }
)

# --- DARK/LIGHT MODE CSS ---
st.markdown("""
<style>
    :root {
        --primary: #1e3a8a;
        --secondary: #3b82f6;
        --accent: #10b981;
        --danger: #ef4444;
        --warning: #f59e0b;
        --text-primary: #0f172a;
        --text-secondary: #475569;
        --bg-primary: #ffffff;
        --bg-secondary: #f8fafc;
        --border-color: #e2e8f0;
        --card-bg: #ffffff;
        --sidebar-bg: #1e3a8a;
        --sidebar-text: #ffffff;
    }

    [data-theme="dark"] {
        --text-primary: #f1f5f9;
        --text-secondary: #cbd5e1;
        --bg-primary: #0f172a;
        --bg-secondary: #1e293b;
        --border-color: #334155;
        --card-bg: #1e293b;
        --sidebar-bg: #0f172a;
        --sidebar-text: #e2e8f0;
    }

    .main {
        background-color: var(--bg-primary);
        color: var(--text-primary);
        transition: all 0.3s ease;
    }

    .main-header {
        font-size: 2.5rem;
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 700;
        padding: 1rem;
    }

    .metric-card {
        background: var(--card-bg);
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid var(--border-color);
        text-align: center;
        transition: all 0.3s ease;
        color: var(--text-primary);
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
        color: #0f172a;
    }

    .info-alert {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid var(--accent);
        margin: 0.5rem 0;
        color: #0f172a;
    }

    .stButton button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(30, 64, 175, 0.3);
    }

    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: var(--sidebar-bg);
        color: var(--sidebar-text);
    }
    
    .sidebar-text {
        color: var(--sidebar-text) !important;
    }

    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem !important;
        }
        .metric-card {
            padding: 1rem !important;
            margin-bottom: 0.5rem;
        }
        .stMetric {
            padding: 0.5rem;
        }
        .sidebar .sidebar-content {
            width: 100% !important;
        }
    }

    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.3); }
        70% { box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
        100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: var(--bg-secondary);
    }
    ::-webkit-scrollbar-thumb {
        background: var(--primary);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: var(--secondary);
    }
</style>
""", unsafe_allow_html=True)

# --- THEME MANAGEMENT ---
def setup_theme():
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'
    
    # Add theme toggle to sidebar
    with st.sidebar:
        theme = st.selectbox("Theme", ["Light", "Dark"], index=0)
        if theme == "Dark":
            st.session_state.theme = 'dark'
        else:
            st.session_state.theme = 'light'

    # Apply theme
    if st.session_state.theme == 'dark':
        st.markdown('<div data-theme="dark">', unsafe_allow_html=True)
    else:
        st.markdown('<div data-theme="light">', unsafe_allow_html=True)

# --- PROFESSIONAL LOGIN SCREEN ---
def login_screen():
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 3rem; background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); 
                    border-radius: 1rem; color: white; margin: 2rem 0;'>
            <h1 style='font-size: 3.5rem; margin-bottom: 1rem;'>⛴️</h1>
            <h1 style='font-size: 2.5rem; margin-bottom: 1rem; color: white;'>Offshore Operations Portal</h1>
            <p style='font-size: 1.2rem; color: #e0f2fe; margin-bottom: 3rem;'>
                Enterprise Rig Workflow Management System
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.subheader("Secure Authentication")
            username = st.text_input("👤 Username", value="admin", 
                                   help="Enter your administrator username")
            password = st.text_input("🔒 Password", type="password", value="offshore2025",
                                   help="Enter your secure password")
            login_button = st.form_submit_button("🚀 Login to Dashboard", use_container_width=True)
            
            if login_button:
                if username == "admin" and password == "offshore2025":
                    with st.spinner("🔐 Authenticating..."):
                        time.sleep(1.5)
                        st.session_state.logged_in = True
                        st.session_state.login_time = datetime.now()
                        st.experimental_rerun()
                else:
                    st.error("❌ Invalid credentials. Please try again.")

# --- DATA MANAGEMENT WITH ENHANCED FEATURES ---
def load_data():
    data_file = Path("rig_data.csv")
    config_file = Path("app_config.json")
    
    # Load or create config
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
    else:
        config = {"last_update": datetime.now().isoformat(), "version": "2.0"}
        with open(config_file, 'w') as f:
            json.dump(config, f)
    
    if data_file.exists():
        df = pd.read_csv(data_file, parse_dates=['Rig_Start', 'Rig_End', 'Start_Date', 'End_Date'])
    else:
        df = generate_sample_data()
        df.to_csv(data_file, index=False)
    
    return df, config

def generate_sample_data(num_rigs=15, num_requests_per_rig=4):
    rig_names = [
        "Deepwater Horizon", "Ocean Explorer", "Sea Guardian", "Marine Pioneer", 
        "Offshore Venture", "Blue Wave", "Pacific Driller", "Atlantic Explorer",
        "Coastal Defender", "North Star", "Southern Cross", "Eastern Horizon",
        "Western Pioneer", "Arctic Explorer", "Pacific Guardian"
    ]
    
    requestors = [
        "Client A - Operations", "Client B - Procurement", "Supplier X - Logistics", 
        "Internal Team - Maintenance", "Regulatory Body - Compliance", "Safety Officer",
        "Technical Department", "Finance Division", "Environmental Team"
    ]
    
    actions = [
        "Supply Delivery", "Maintenance Schedule", "Safety Audit", "Personnel Change", 
        "Data Submission", "Equipment Inspection", "Environmental Check", "Emergency Drill",
        "System Upgrade", "Training Session", "Documentation Review", "Quality Assurance"
    ]
    
    data = []

    for i in range(num_rigs):
        rig = rig_names[i] if i < len(rig_names) else f"Rig_{i+1:03d}"
        
        # Generate rig operational period
        rig_start = pd.Timestamp.now() - pd.Timedelta(days=random.randint(0, 60))
        rig_duration = pd.Timedelta(days=random.randint(30, 120))
        rig_end = rig_start + rig_duration
        overall_status = "Complete" if pd.Timestamp.now() > rig_end else "Active"

        for _ in range(random.randint(1, num_requests_per_rig)):
            # Generate requests within rig operational timeline
            req_start_offset = random.randint(0, (rig_end - rig_start).days)
            req_start = rig_start + pd.Timedelta(days=req_start_offset)
            req_duration = pd.Timedelta(days=random.randint(1, 21))
            req_end = req_start + req_duration
            req_status = "Complete" if pd.Timestamp.now() > req_end else "Active"

            request_data = {
                "Rig": rig,
                "Rig_Start": rig_start,
                "Rig_End": rig_end,
                "Rig_Status": overall_status,
                "Request_ID": f"REQ-{random.randint(10000, 99999)}",
                "Action_Requested": random.choice(actions),
                "Requestor": random.choice(requestors),
                "Start_Date": req_start,
                "End_Date": req_end,
                "Duration_Days": req_duration.days,
                "Action_Doable": random.choice([True, False]),
                "Action_Complete": req_status == "Complete",
                "Response_Provided": random.choice([True, False]) if req_status == "Complete" else False,
                "Priority": random.choice(["High", "Medium", "Low"]),
                "Cost_Estimate": round(random.uniform(1000, 50000), 2),
                "Team_Size": random.randint(1, 12),
                "Risk_Level": random.choice(["Low", "Medium", "High"]),
                "Environmental_Impact": random.choice(["None", "Low", "Medium", "High"])
            }
            data.append(request_data)

    return pd.DataFrame(data)

# --- FILE EXPORT FUNCTIONS ---
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='RigOperations')
        
        # Add summary sheet
        summary_data = {
            'Metric': ['Total Rigs', 'Active Rigs', 'Completed Requests', 'Pending Actions'],
            'Value': [
                df['Rig'].nunique(),
                len(df[df['Rig_Status'] == 'Active']),
                len(df[df['Action_Complete'] == True]),
                len(df[df['Action_Complete'] == False])
            ]
        }
        pd.DataFrame(summary_data).to_excel(writer, index=False, sheet_name='Summary')
    
    processed_data = output.getvalue()
    return processed_data

# --- APPLICATION INITIALIZATION ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_screen()
    st.stop()

# --- MAIN APPLICATION ---
setup_theme()

# Show loading animation
with st.spinner('🚀 Loading Offshore Operations Dashboard...'):
    time.sleep(1)

# Load data
df, config = load_data()

# Ensure date columns are properly formatted
date_columns = ['Rig_Start', 'Rig_End', 'Start_Date', 'End_Date']
for col in date_columns:
    df[col] = pd.to_datetime(df[col])

# --- SIDEBAR WITH ENHANCED CONTROLS ---
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; margin-bottom: 2rem;'>
        <h1 style='color: var(--sidebar-text); font-size: 1.5rem;'>⛴️ OFFSHORE CONTROL</h1>
        <p style='color: var(--sidebar-text); font-size: 0.9rem;'>Real-time Rig Management System</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Real-time status
    st.markdown(f"""
    <div style='background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 0.5rem; text-align: center; margin-bottom: 1.5rem;'>
        <p style='color: var(--sidebar-text); margin: 0; font-size: 0.9rem;'>System Status</p>
        <p style='color: #4ade80; margin: 0; font-weight: bold;'>● OPERATIONAL</p>
        <p style='color: var(--sidebar-text); margin: 0; font-size: 0.8rem;'>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Advanced filters
    st.markdown("### 🎯 Dashboard Filters")
    
    date_range = st.date_input(
        "📅 Date Range",
        value=(pd.Timestamp.now() - pd.Timedelta(days=30), pd.Timestamp.now() + pd.Timedelta(days=30)),
        help="Select the date range for viewing operations"
    )
    
    st.session_state.status_filter = st.multiselect(
        "🔍 Rig Status",
        options=df['Rig_Status'].unique(),
        default=df['Rig_Status'].unique(),
        help="Filter by rig operational status"
    )
    
    st.session_state.rig_filter = st.multiselect(
        "🏗️ Select Rigs",
        options=sorted(df['Rig'].unique()),
        default=[],
        help="Select specific rigs to view"
    )
    
    priority_filter = st.multiselect(
        "🚨 Priority Level",
        options=sorted(df['Priority'].unique()),
        default=[],
        help="Filter by action priority level"
    )
    
    # Data management section
    st.markdown("---")
    st.markdown("### 💾 Data Management")
    
    if st.button("🔄 Generate Sample Data", help="Load demonstration data"):
        with st.spinner("Generating sample data..."):
            df = generate_sample_data()
            df.to_csv("rig_data.csv", index=False)
            st.success("Sample data loaded!")
            time.sleep(1)
            st.experimental_rerun()
    
    # Export options
    st.markdown("### 📤 Export Data")
    col1, col2 = st.columns(2)
    with col1:
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="CSV",
            data=csv_data,
            file_name="rig_operations.csv",
            mime="text/csv",
            help="Download data as CSV file"
        )
    with col2:
        excel_data = to_excel(df)
        st.download_button(
            label="Excel",
            data=excel_data,
            file_name="rig_operations.xlsx",
            mime="application/vnd.ms-excel",
            help="Download data as Excel workbook"
        )
    
    # User info
    st.markdown("---")
    st.markdown(f"""
    <div style='color: var(--sidebar-text); font-size: 0.8rem;'>
        <p>Logged in as: <strong>admin</strong></p>
        <p>Session start: {st.session_state.get('login_time', datetime.now()).strftime('%H:%M:%S')}</p>
        <p>Version: {config.get('version', '2.0')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()

# --- APPLY FILTERS ---
filtered_df = df.copy()
if st.session_state.get('status_filter'):
    filtered_df = filtered_df[filtered_df['Rig_Status'].isin(st.session_state.status_filter)]
if st.session_state.get('rig_filter'):
    filtered_df = filtered_df[filtered_df['Rig'].isin(st.session_state.rig_filter)]
if priority_filter:
    filtered_df = filtered_df[filtered_df['Priority'].isin(priority_filter)]

# Filter by date range
if len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df['Start_Date'] >= pd.Timestamp(date_range[0])) & 
        (filtered_df['End_Date'] <= pd.Timestamp(date_range[1]))
    ]

# --- MAIN DASHBOARD LAYOUT ---
st.markdown('<h1 class="main-header">⛴️ Offshore Rig Workflow Tracker</h1>', unsafe_allow_html=True)

# Quick stats row
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Rigs", df['Rig'].nunique(), help="Total number of rigs in the system")
with col2:
    active_rigs = len(df[df['Rig_Status'] == 'Active'])
    st.metric("Active Rigs", active_rigs, f"{active_rigs} operational", help="Currently active rigs")
with col3:
    completion_rate = (len(df[df['Action_Complete'] == True]) / len(df)) * 100
    st.metric("Completion Rate", f"{completion_rate:.1f}%", help="Overall action completion rate")

# --- PERFORMANCE METRICS ---
st.markdown("### 📊 Performance Overview")
metric_cols = st.columns(4)

with metric_cols[0]:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    monthly_requests = len(df[df['Start_Date'].dt.month == datetime.now().month])
    st.metric("Monthly Requests", monthly_requests, help="Requests created this month")
    st.markdown('</div>', unsafe_allow_html=True)

with metric_cols[1]:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    monthly_complete = len(df[(df['Action_Complete'] == True) & (df['End_Date'].dt.month == datetime.now().month)])
    st.metric("Monthly Completed", monthly_complete, help="Actions completed this month")
    st.markdown('</div>', unsafe_allow_html=True)

with metric_cols[2]:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    upcoming_tasks = len(df[(df['End_Date'] > pd.Timestamp.now()) & 
                          (df['End_Date'] <= pd.Timestamp.now() + pd.Timedelta(days=7)) & 
                          (df['Action_Complete'] == False)])
    st.metric("Upcoming Tasks", upcoming_tasks, help="Tasks due in the next 7 days")
    st.markdown('</div>', unsafe_allow_html=True)

with metric_cols[3]:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    overdue_tasks = len(df[(df['End_Date'] < pd.Timestamp.now()) & (df['Action_Complete'] == False)])
    st.metric("Overdue Tasks", overdue_tasks, delta=f"{overdue_tasks} urgent", help="Tasks that are past their due date")
    st.markdown('</div>', unsafe_allow_html=True)

# --- NOTIFICATIONS & ALERTS ---
st.markdown("### 🔔 Notifications & Alerts")

# Urgent tasks (due in 3 days or less)
urgent_tasks = df[(df['End_Date'] >= pd.Timestamp.now()) & 
                 (df['End_Date'] <= pd.Timestamp.now() + pd.Timedelta(days=3)) & 
                 (df['Action_Complete'] == False)]

if not urgent_tasks.empty:
    for _, task in urgent_tasks.iterrows():
        days_left = (task['End_Date'] - pd.Timestamp.now()).days
        st.markdown(f'''
        <div class="urgent-alert">
            <b>🚨 URGENT ACTION REQUIRED:</b> {task['Rig']} - {task['Action_Requested']}<br>
            <b>Due:</b> {days_left} days ({task['End_Date'].strftime('%Y-%m-%d')}) | 
            <b>Requested by:</b> {task['Requestor']} | 
            <b>Priority:</b> {task['Priority']}
        </div>
        ''', unsafe_allow_html=True)
else:
    st.markdown('<div class="info-alert">✅ No urgent actions required in the next 3 days</div>', unsafe_allow_html=True)

# Weekly overview
st.markdown("#### 📋 This Week's Overview")
weekly_tasks = df[(df['End_Date'] >= pd.Timestamp.now()) & 
                 (df['End_Date'] <= pd.Timestamp.now() + pd.Timedelta(days=7))]

if not weekly_tasks.empty:
    weekly_summary = weekly_tasks.groupby('Rig').agg({
        'Action_Requested': 'count',
        'Action_Complete': 'sum'
    }).rename(columns={'Action_Requested': 'Total', 'Action_Complete': 'Completed'})
    
    weekly_summary['Completion'] = (weekly_summary['Completed'] / weekly_summary['Total'] * 100).round(1)
    st.dataframe(weekly_summary, use_container_width=True)
else:
    st.info("No tasks scheduled for the upcoming week.")

# --- GANTT CHART VISUALIZATION ---
st.markdown("### 📅 Rig & Request Timeline")

gantt_data = []
for _, row in filtered_df.iterrows():
    # Main rig operational period
    gantt_data.append(dict(
        Task=row['Rig'], 
        Start=row['Rig_Start'], 
        Finish=row['Rig_End'], 
        Resource="Rig Operation", 
        Details=f"Status: {row['Rig_Status']}",
        ID=row['Rig'],
        Priority=row['Priority']
    ))
    # Individual requests
    gantt_data.append(dict(
        Task=row['Rig'], 
        Start=row['Start_Date'], 
        Finish=row['End_Date'], 
        Resource=row['Action_Requested'], 
        Details=f"{row['Requestor']} | {row['Action_Requested']}",
        ID=row['Request_ID'],
        Priority=row['Priority']
    ))

gantt_df = pd.DataFrame(gantt_data)

if not gantt_df.empty:
    fig = px.timeline(
        gantt_df,
        x_start="Start",
        x_end="Finish",
        y="Task",
        color="Resource",
        hover_data={"Details": True, "Resource": True, "Start": False, "Finish": False, "ID": True, "Priority": True},
        title="Rig and Request Timeline",
        height=600
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode='closest'
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data to display for the selected filters.")

# --- DETAILED REQUEST VIEW ---
st.markdown("### 📋 Detailed Request Overview")

detailed_view = filtered_df[[
    "Rig", "Request_ID", "Action_Requested", "Requestor", "Start_Date", "End_Date",
    "Duration_Days", "Priority", "Action_Doable", "Action_Complete", "Response_Provided", "Rig_Status"
]].copy()

# Format for display
detailed_view['Start_Date'] = detailed_view['Start_Date'].dt.strftime('%Y-%m-%d')
detailed_view['End_Date'] = detailed_view['End_Date'].dt.strftime('%Y-%m-%d')
detailed_view['Action_Doable'] = detailed_view['Action_Doable'].map({True: '✅', False: '❌'})
detailed_view['Action_Complete'] = detailed_view['Action_Complete'].map({True: '✅', False: '⏳'})
detailed_view['Response_Provided'] = detailed_view['Response_Provided'].map({True: '✅', False: '📝'})

st.dataframe(
    detailed_view,
    use_container_width=True,
    height=400
)

# --- FOOTER WITH ENHANCED INFO ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: var(--text-secondary); padding: 2rem 0;'>
    <p><strong>Offshore Rig Workflow Tracker v2.0</strong> | Professional Enterprise Edition</p>
    <p style='font-size: 0.9rem;'>
        Built with Streamlit • Optimized for all devices • Real-time monitoring
    </p>
    <p style='font-size: 0.8rem; color: var(--text-secondary);'>
        Last updated: {config.get('last_update', datetime.now().isoformat())} | 
        <a href='https://github.com/Princeeze744/rig-workflow-tracker' target='_blank' style='color: var(--secondary);'>GitHub Repository</a>
    </p>
</div>
""".format(config=config), unsafe_allow_html=True)

# --- HELP & DOCUMENTATION ---
with st.expander("ℹ️ How to Use This Dashboard"):
    st.markdown("""
    ### 📖 User Guide
    
    **Dashboard Overview:**
    - Monitor all rig operations in real-time
    - Track requests, actions, and completions
    - Receive urgent notifications and alerts
    
    **Key Features:**
    - **Timeline View**: Visual Gantt chart of all operations
    - **Performance Metrics**: Real-time KPIs and metrics
    - **Advanced Filtering**: Filter by date, rig, status, priority
    - **Data Export**: Download data in CSV or Excel format
    - **Mobile Responsive**: Works perfectly on all devices
    
    **Filtering Options:**
    - Use the sidebar to filter by date range, rig status, or specific rigs
    - Priority filtering for urgent actions
    - Real-time updates as you adjust filters
    
    **Data Management:**
    - Generate sample data for demonstration
    - Export current view to CSV or Excel
    - All data is automatically persisted
    
    **Theme Options:**
    - Switch between light and dark modes
    - Auto theme detection based on system preferences
    
    For support or questions, please contact your system administrator.
    """)

# Add theme application closing tag
st.markdown('</div>', unsafe_allow_html=True)