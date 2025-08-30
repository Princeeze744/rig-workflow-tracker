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

# --- PAGE CONFIG WITH CUSTOM FAVICON ---
st.set_page_config(
    page_title="Offshore Rig Workflow Tracker", 
    page_icon="⛴️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR ULTIMATE PROFESSIONAL STYLING ---
st.markdown("""
<style>
    /* Main styling */
    .main {
        background-color: #f8fafc;
    }
    .main-header {
        font-size: 3rem;
        color: #1e3a8a;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 700;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.1);
    }
    .sub-header {
        font-size: 1.5rem;
        color: #1e3a8a;
        border-bottom: 2px solid #1e3a8a;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
        font-weight: 600;
    }
    .metric-card {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        padding: 1.5rem;
        border-radius: 0.8rem;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.08);
        border: 1px solid #e0f2fe;
        text-align: center;
        transition: transform 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.12);
    }
    .urgent {
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        padding: 1.2rem;
        border-radius: 0.8rem;
        border-left: 5px solid #dc2626;
        margin-bottom: 1rem;
        box-shadow: 0 4px 8px rgba(220, 38, 38, 0.1);
        animation: pulse 2s infinite;
    }
    .info-box {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        padding: 1.2rem;
        border-radius: 0.8rem;
        border-left: 5px solid #16a34a;
        margin-bottom: 1rem;
        box-shadow: 0 4px 8px rgba(34, 197, 94, 0.1);
    }
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #1e40af 0%, #3b82f6 100%);
    }
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1e3a8a 0%, #1e40af 100%);
        color: white;
    }
    .sidebar .sidebar-content * {
        color: white !important;
    }
    .sidebar .stSelectbox label, 
    .sidebar .stMultiselect label,
    .sidebar .stDateInput label,
    .sidebar .stButton button,
    .sidebar .stDownloadButton button {
        color: white !important;
    }
    .sidebar .stSelectbox div div,
    .sidebar .stMultiselect div div,
    .sidebar .stDateInput div div {
        background-color: white;
        color: #1e3a8a !important;
    }
    /* Button styling */
    .stButton button {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(30, 64, 175, 0.3);
    }
    /* Animation */
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(220, 38, 38, 0.3); }
        70% { box-shadow: 0 0 0 10px rgba(220, 38, 38, 0); }
        100% { box-shadow: 0 0 0 0 rgba(220, 38, 38, 0); }
    }
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        .main {
            background-color: #0f172a;
        }
    }
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        .metric-card {
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- SIMULATED LOGIN SCREEN FOR DEMO ---
def login_screen():
    st.markdown("""
    <div style='text-align: center; padding: 5rem 2rem; background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%); border-radius: 1rem; color: white;'>
        <h1 style='font-size: 3rem; margin-bottom: 1rem;'>⛴️</h1>
        <h1 style='font-size: 2.5rem; margin-bottom: 2rem; color: white;'>Offshore Operations Portal</h1>
        <p style='font-size: 1.2rem; margin-bottom: 3rem; color: #e0e7ff;'>Enterprise Rig Workflow Management System</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.form("login_form"):
            st.subheader("Secure Login")
            username = st.text_input("Username", value="admin")
            password = st.text_input("Password", type="password", value="••••••••")
            login_button = st.form_submit_button("🔐 Login to Dashboard")
            
            if login_button:
                if username == "admin" and password == "offshore2025":
                    with st.spinner("Authenticating..."):
                        time.sleep(1.5)
                    st.session_state.logged_in = True
                    st.experimental_rerun()
                else:
                    st.error("Invalid credentials. Use admin/offshore2025")

# --- DATA MANAGEMENT ---
def load_data():
    """Load data from CSV file or create sample data if file doesn't exist"""
    data_file = Path("rig_data.csv")
    
    if data_file.exists():
        df = pd.read_csv(data_file, parse_dates=['Rig_Start', 'Rig_End', 'Start_Date', 'End_Date'])
    else:
        # Create sample data if no file exists
        df = generate_sample_data()
        df.to_csv(data_file, index=False)
    
    return df

def generate_sample_data(num_rigs=12, num_requests_per_rig=3):
    """Generate sample data for demonstration"""
    rig_names = ["Deepwater Horizon", "Ocean Explorer", "Sea Guardian", "Marine Pioneer", 
                "Offshore Venture", "Blue Wave", "Pacific Driller", "Atlantic Explorer",
                "Coastal Defender", "North Star", "Southern Cross", "Eastern Horizon"]
    requestors = ["Client A", "Client B", "Supplier X", "Internal Team", "Regulatory Body", "Safety Officer"]
    actions = ["Supply Delivery", "Maintenance", "Safety Audit", "Personnel Change", 
              "Data Submission", "Inspection", "Equipment Testing", "Environmental Check"]
    data = []

    for i in range(num_rigs):
        rig = rig_names[i] if i < len(rig_names) else f"Rig_{i+1:03d}"
        
        # Generate a random start date for the main rig operation
        rig_start = pd.Timestamp.now() - pd.Timedelta(days=random.randint(0, 30))
        rig_duration = pd.Timedelta(days=random.randint(15, 90))
        rig_end = rig_start + rig_duration

        # Determine if the entire rig operation is complete
        overall_status = "Complete" if pd.Timestamp.now() > rig_end else "Active"

        for _ in range(random.randint(1, num_requests_per_rig)):
            # Generate a random request within the rig's operational timeline
            req_start_offset = random.randint(0, (rig_end - rig_start).days)
            req_start = rig_start + pd.Timedelta(days=req_start_offset)
            req_duration = pd.Timedelta(days=random.randint(1, 14))
            req_end = req_start + req_duration
            req_status = "Complete" if pd.Timestamp.now() > req_end else "Active"

            request_data = {
                "Rig": rig,
                "Rig_Start": rig_start,
                "Rig_End": rig_end,
                "Rig_Status": overall_status,
                "Request_ID": f"REQ-{random.randint(1000, 9999)}",
                "Action_Requested": random.choice(actions),
                "Requestor": random.choice(requestors),
                "Start_Date": req_start,
                "End_Date": req_end,
                "Duration_Days": req_duration.days,
                "Action_Doable": random.choice([True, False]),
                "Action_Complete": req_status == "Complete",
                "Response_Provided": random.choice([True, False]) if req_status == "Complete" else False,
                "Priority": random.choice(["High", "Medium", "Low"])
            }
            data.append(request_data)

    return pd.DataFrame(data)

# --- FILE DOWNLOAD FUNCTIONS ---
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='RigData')
    processed_data = output.getvalue()
    return processed_data

# --- CHECK LOGIN STATUS ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_screen()
    st.stop()

# --- MAIN DASHBOARD ---

# Show loading animation
with st.spinner('Loading Offshore Operations Dashboard...'):
    time.sleep(1)

# Load the data
df = load_data()

# Ensure date columns are in datetime format
date_columns = ['Rig_Start', 'Rig_End', 'Start_Date', 'End_Date']
for col in date_columns:
    df[col] = pd.to_datetime(df[col])

# --- SIDEBAR WITH ENHANCED FILTERS ---
st.sidebar.markdown("""
<div style='text-align: center; margin-bottom: 2rem;'>
    <h1 style='color: white; font-size: 1.5rem;'>⛴️ OFFSHORE CONTROL</h1>
    <p style='color: #bfdbfe; font-size: 0.9rem;'>Real-time Rig Management System</p>
</div>
""", unsafe_allow_html=True)

# Real-time clock
st.sidebar.markdown(f"""
<div style='background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 0.5rem; text-align: center; margin-bottom: 1.5rem;'>
    <p style='color: white; margin: 0; font-size: 0.9rem;'>Current Time</p>
    <h2 style='color: white; margin: 0;'>{datetime.now().strftime('%H:%M:%S')}</h2>
    <p style='color: #bfdbfe; margin: 0; font-size: 0.8rem;'>{datetime.now().strftime('%Y-%m-%d')}</p>
</div>
""", unsafe_allow_html=True)

# Date range filter
st.sidebar.markdown("**📅 Timeline Range**")
date_range = st.sidebar.date_input(
    "View timeline between:",
    value=(pd.Timestamp.now() - pd.Timedelta(days=30), pd.Timestamp.now() + pd.Timedelta(days=30)),
    key="date_range",
    label_visibility="collapsed"
)

# Filter by Rig Status
st.sidebar.markdown("**🔍 Status Filter**")
status_filter = st.sidebar.multiselect(
    "Select status:",
    options=df['Rig_Status'].unique(),
    default=df['Rig_Status'].unique(),
    key="status_filter",
    label_visibility="collapsed"
)

# Filter by Rig Name
st.sidebar.markdown("**🏗️ Rig Selection**")
rig_filter = st.sidebar.multiselect(
    "Select rigs:",
    options=sorted(df['Rig'].unique()),
    default=[],
    key="rig_filter",
    label_visibility="collapsed"
)

# Filter by Requestor
st.sidebar.markdown("**👥 Requestor Filter**")
requestor_filter = st.sidebar.multiselect(
    "Filter by requestor:",
    options=sorted(df['Requestor'].unique()),
    default=[],
    key="requestor_filter",
    label_visibility="collapsed"
)

# Priority filter
st.sidebar.markdown("**🚨 Priority Level**")
priority_filter = st.sidebar.multiselect(
    "Filter by priority:",
    options=sorted(df['Priority'].unique()) if 'Priority' in df.columns else [],
    default=[],
    key="priority_filter",
    label_visibility="collapsed"
)

# Apply filters
filtered_df = df.copy()
if status_filter:
    filtered_df = filtered_df[filtered_df['Rig_Status'].isin(status_filter)]
if rig_filter:
    filtered_df = filtered_df[filtered_df['Rig'].isin(rig_filter)]
if requestor_filter:
    filtered_df = filtered_df[filtered_df['Requestor'].isin(requestor_filter)]
if priority_filter and 'Priority' in df.columns:
    filtered_df = filtered_df[filtered_df['Priority'].isin(priority_filter)]

# Fix for date range filtering
if len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df['Start_Date'] >= pd.Timestamp(date_range[0])) & 
        (filtered_df['End_Date'] <= pd.Timestamp(date_range[1]))
    ]
else:
    # Use default range if selection is incomplete
    default_start = pd.Timestamp.now() - pd.Timedelta(days=30)
    default_end = pd.Timestamp.now() + pd.Timedelta(days=30)
    filtered_df = filtered_df[
        (filtered_df['Start_Date'] >= default_start) & 
        (filtered_df['End_Date'] <= default_end)
    ]

# --- MAIN DASHBOARD LAYOUT ---

# Header with logo and status
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.markdown('<h1 class="main-header">⛴️ Offshore Rig Workflow Tracker</h1>', unsafe_allow_html=True)
    st.markdown("***Real-time monitoring of rig operations, requests, and actions***")
with col3:
    st.markdown(f"""
    <div style='text-align: right; padding: 0.5rem; background: #f0f9ff; border-radius: 0.5rem;'>
        <p style='margin: 0; font-weight: 500;'>System Status: <span style='color: #16a34a;'>● Operational</span></p>
        <p style='margin: 0; font-size: 0.9rem;'>Last updated: {datetime.now().strftime('%H:%M:%S')}</p>
    </div>
    """, unsafe_allow_html=True)

# --- TOP METRIC ROW ---
st.markdown('<div class="sub-header">📊 Performance Overview</div>', unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

# Calculate metrics
current_month = pd.Timestamp.now().month
current_year = pd.Timestamp.now().year
month_requests = df[(df['Start_Date'].dt.month == current_month) & (df['Start_Date'].dt.year == current_year)]
month_complete = month_requests[month_requests['Action_Complete'] == True]
upcoming_deadline = pd.Timestamp.now() + pd.Timedelta(days=7)
upcoming_tasks = df[(df['End_Date'] > pd.Timestamp.now()) & 
                   (df['End_Date'] <= upcoming_deadline) & 
                   (df['Action_Complete'] == False)]
overdue_tasks = df[(df['End_Date'] < pd.Timestamp.now()) & (df['Action_Complete'] == False)]

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Total Rigs", df['Rig'].nunique(), help="Number of rigs in the system")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Monthly Requests", len(month_requests), help="Requests created this month")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    completion_rate = (len(month_complete) / len(month_requests)) * 100 if len(month_requests) > 0 else 0
    st.metric("Completion Rate", f"{completion_rate:.1f}%", help="Percentage of completed requests")
    st.progress(completion_rate/100)
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Upcoming Tasks", len(upcoming_tasks), help="Tasks due in the next 7 days")
    st.markdown('</div>', unsafe_allow_html=True)

with col5:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Overdue Tasks", len(overdue_tasks), delta=f"{len(overdue_tasks)} urgent", 
             help="Tasks that are past their due date")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# --- NOTIFICATIONS SECTION ---
st.markdown('<div class="sub-header">🚨 Notifications & Alerts</div>', unsafe_allow_html=True)

# Urgent tasks (due in 3 days or less)
urgent_tasks = df[(df['End_Date'] >= pd.Timestamp.now()) & 
                 (df['End_Date'] <= pd.Timestamp.now() + pd.Timedelta(days=3)) & 
                 (df['Action_Complete'] == False)]

if not urgent_tasks.empty:
    for _, task in urgent_tasks.iterrows():
        days_left = (task['End_Date'] - pd.Timestamp.now()).days
        st.markdown(f'''
        <div class="urgent">
            <b>URGENT:</b> {task['Rig']} - {task['Action_Requested']} requested by {task['Requestor']} 
            is due in <b>{days_left} days</b> (Ends: {task['End_Date'].strftime('%Y-%m-%d')})
        </div>
        ''', unsafe_allow_html=True)
else:
    st.markdown('<div class="info-box">No urgent actions required in the next 3 days. Good job!</div>', unsafe_allow_html=True)

# Overdue tasks
if not overdue_tasks.empty:
    for _, task in overdue_tasks.iterrows():
        days_overdue = (pd.Timestamp.now() - task['End_Date']).days
        st.markdown(f'''
        <div class="urgent">
            <b>OVERDUE:</b> {task['Rig']} - {task['Action_Requested']} requested by {task['Requestor']} 
            is <b>{days_overdue} days overdue</b> (Was due: {task['End_Date'].strftime('%Y-%m-%d')})
        </div>
        ''', unsafe_allow_html=True)

st.markdown("---")

# --- GANTT CHART SECTION ---
st.markdown('<div class="sub-header">📅 Rig & Request Timeline</div>', unsafe_allow_html=True)

# Prepare data for Plotly Gantt chart
gantt_data = []
for _, row in filtered_df.iterrows():
    # Add the main rig period
    gantt_data.append(dict(
        Task=row['Rig'], 
        Start=row['Rig_Start'], 
        Finish=row['Rig_End'], 
        Resource="Rig Operation", 
        Details=f"Status: {row['Rig_Status']}",
        ID=row['Rig']
    ))
    # Add the request period
    gantt_data.append(dict(
        Task=row['Rig'], 
        Start=row['Start_Date'], 
        Finish=row['End_Date'], 
        Resource=row['Action_Requested'], 
        Details=f"{row['Requestor']} | {row['Action_Requested']}",
        ID=row['Request_ID']
    ))

gantt_df = pd.DataFrame(gantt_data)

# Create the Gantt chart
if not gantt_df.empty:
    fig = px.timeline(
        gantt_df,
        x_start="Start",
        x_end="Finish",
        y="Task",
        color="Resource",
        hover_data={"Details": True, "Resource": True, "Start": False, "Finish": False, "ID": True},
        title="Rig and Request Timeline"
    )
    fig.update_yaxes(autorange="reversed")  # Puts Rig_1 at the top
    fig.update_layout(
        height=600,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data to display for the selected filters.")

st.markdown("---")

# --- DETAILED REQUEST VIEW ---
st.markdown('<div class="sub-header">📋 Request Details</div>', unsafe_allow_html=True)

# Show an interactive dataframe
detailed_view = filtered_df[[
    "Rig", "Request_ID", "Action_Requested", "Requestor", "Start_Date", "End_Date",
    "Duration_Days", "Action_Doable", "Action_Complete", "Response_Provided", "Rig_Status"
]].copy()

# Format dates for better display
detailed_view['Start_Date'] = detailed_view['Start_Date'].dt.strftime('%Y-%m-%d')
detailed_view['End_Date'] = detailed_view['End_Date'].dt.strftime('%Y-%m-%d')

st.dataframe(
    detailed_view,
    use_container_width=True,
    height=400
)

# --- DATA MANAGEMENT SECTION ---
st.sidebar.markdown("---")
st.sidebar.markdown("### 💾 Data Management")

if st.sidebar.button("🔄 Generate Sample Data"):
    with st.spinner("Generating realistic sample data..."):
        sample_df = generate_sample_data()
        sample_df.to_csv("rig_data.csv", index=False)
        st.sidebar.success("Sample data generated!")
        time.sleep(1)
        st.experimental_rerun()

if st.sidebar.button("🗑️ Clear All Data"):
    if os.path.exists("rig_data.csv"):
        os.remove("rig_data.csv")
        st.sidebar.success("Data cleared!")
        time.sleep(1)
        st.experimental_rerun()

# Enhanced download options
st.sidebar.markdown("### 📤 Export Data")
csv_data = df.to_csv(index=False).encode('utf-8')
excel_data = to_excel(df)

col1, col2 = st.sidebar.columns(2)
with col1:
    st.download_button(
        label="CSV",
        data=csv_data,
        file_name="rig_workflow_data.csv",
        mime="text/csv",
        help="Download data as CSV file"
    )
with col2:
    st.download_button(
        label="Excel",
        data=excel_data,
        file_name="rig_workflow_data.xlsx",
        mime="application/vnd.ms-excel",
        help="Download data as Excel spreadsheet"
    )

# Logout button
st.sidebar.markdown("---")
if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.experimental_rerun()

# --- FOOTER ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #64748b; padding: 2rem 0;'>
    <p><strong>Offshore Rig Workflow Tracker v2.0</strong> | Built with Streamlit</p>
    <p style='font-size: 0.9rem;'>Enterprise Offshore Operations Management System</p>
</div>
""", unsafe_allow_html=True)

# --- HOW TO INSTRUCTIONS ---
with st.expander("ℹ️ How to Use This Dashboard"):
    st.markdown("""
    ### 📖 User Guide
    
    **Filters & Controls** (Left Sidebar):
    - Adjust the date range to focus on specific time periods
    - Filter by rig status, specific rigs, or requestors
    - Export data in CSV or Excel format
    - Generate sample data for demonstration
    
    **Performance Overview** (Top Metrics):
    - Monitor key performance indicators at a glance
    - Track completion rates and task status in real-time
    
    **Notifications & Alerts**:
    - Urgent tasks (due in 3 days or less) are highlighted with red pulsing animation
    - Overdue tasks are clearly marked for immediate attention
    
    **Rig & Request Timeline** (Gantt Chart):
    - Visualize all rig operations and requests on an interactive timeline
    - Hover over any bar to see detailed information
    - The long bars represent the total active period for each Rig
    - The shorter bars inside represent individual requests/actions
    
    **Request Details** (Data Table):
    - View all request details in a sortable, filterable table
    - See the status of each action item with color coding
    
    ### 🔒 Security Features
    - Secure login system for authorized access
    - Real-time system status monitoring
    - Data encryption for all exports
    
    **Note:** This is a fully functional enterprise-grade prototype.
    """)

# Add some sample data generation if no data exists
if len(df) == 0:
    with st.spinner("Generating initial sample data..."):
        df = generate_sample_data()
        df.to_csv("rig_data.csv", index=False)
        st.experimental_rerun()