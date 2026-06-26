"""
Intelligent Analytics Page - AquaSense AI
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import data_loader
from utils.auth import require_login, render_auth_sidebar


# Set page config
st.set_page_config(
    page_title="Intelligent Analytics - AquaSense AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

require_login(post_login_page="pages/6_🧠_Intelligent_Analytics.py")
render_auth_sidebar()


# Load data with caching
@st.cache_data
def load_data():
    df = data_loader.load_reservoir_data("clean_reservoir_data.xls")
    df = data_loader.preprocess_data(df)
    return df


df = load_data()


# Sidebar
st.sidebar.title("⚙️ Analytics Settings")

selected_reservoir = st.sidebar.selectbox(
    "Select Reservoir",
    options=["All Reservoirs"] + sorted(df['Reservoir_Name'].unique()),
    index=0
)

st.sidebar.markdown("---")
st.sidebar.subheader("About the Scores")
st.sidebar.info("""
**Reservoir Health Score**: Combines storage percentage, level status, and consistency.

**Flood Risk Indicator**: Based on current level vs Full Reservoir Level.

**Water Scarcity Indicator**: Based on current storage vs live capacity.
""")


# Filter data
if selected_reservoir != "All Reservoirs":
    filtered_df = df[df['Reservoir_Name'] == selected_reservoir]
else:
    filtered_df = df

# Get latest data
latest_df = filtered_df.sort_values('Date').groupby('Reservoir_Name').last().reset_index()


# Page title
st.title("🧠 Intelligent Analytics")
st.markdown("---")


# ==========================================
# CALCULATE INTELLIGENT METRICS
# ==========================================

def calculate_reservoir_health_score(row):
    """Calculate a comprehensive health score (0-100)"""
    score = 0
    
    # 1. Storage percentage (40 points)
    storage_pct = row['Storage_Percentage']
    if storage_pct >= 80:
        score += 40
    elif storage_pct >= 60:
        score += 32
    elif storage_pct >= 40:
        score += 24
    elif storage_pct >= 20:
        score += 12
    else:
        score += 4
    
    # 2. Level status (30 points)
    try:
        level_ratio = row['Level'] / row['Full_Reservoir_Level']
        if 0.4 <= level_ratio <= 0.8:
            score += 30
        elif 0.2 <= level_ratio < 0.4 or 0.8 < level_ratio <= 0.95:
            score += 20
        elif level_ratio < 0.2 or level_ratio > 0.95:
            score += 10
    except:
        score += 15
    
    # 3. Capacity utilization (30 points)
    capacity = row['Live_Capacity_FRL']
    if capacity > 1:
        score += 30
    elif capacity > 0.5:
        score += 20
    else:
        score += 10
    
    return min(score, 100)


def get_health_status(score):
    if score >= 80:
        return "Excellent", "🟢"
    elif score >= 60:
        return "Good", "🟡"
    elif score >= 40:
        return "Fair", "🟠"
    else:
        return "Poor", "🔴"


def calculate_flood_risk_indicator(row):
    """Calculate flood risk indicator"""
    try:
        level_ratio = row['Level'] / row['Full_Reservoir_Level']
        if level_ratio >= 0.95:
            return "Critical", "🔴", 95
        elif level_ratio >= 0.85:
            return "High", "🟠", 75
        elif level_ratio >= 0.7:
            return "Medium", "🟡", 50
        elif level_ratio >= 0.5:
            return "Low", "🟢", 25
        else:
            return "Minimal", "✅", 10
    except:
        return "Unknown", "⚪", 0


def calculate_water_scarcity_indicator(row):
    """Calculate water scarcity indicator"""
    storage_pct = row['Storage_Percentage']
    if storage_pct < 10:
        return "Critical Shortage", "🔴", 95
    elif storage_pct < 25:
        return "Severe Shortage", "🟠", 75
    elif storage_pct < 40:
        return "Moderate Shortage", "🟡", 50
    elif storage_pct < 60:
        return "Stable", "🟢", 25
    else:
        return "Surplus", "✅", 10


# Calculate scores for latest data
latest_df['Health_Score'] = latest_df.apply(calculate_reservoir_health_score, axis=1)
latest_df['Health_Status'], latest_df['Health_Icon'] = zip(*latest_df['Health_Score'].apply(get_health_status))
latest_df['Flood_Risk_Level'], latest_df['Flood_Risk_Icon'], latest_df['Flood_Risk_Score'] = zip(*latest_df.apply(calculate_flood_risk_indicator, axis=1))
latest_df['Scarcity_Level'], latest_df['Scarcity_Icon'], latest_df['Scarcity_Score'] = zip(*latest_df.apply(calculate_water_scarcity_indicator, axis=1))


# ==========================================
# DISPLAY OVERALL METRICS (for all reservoirs)
# ==========================================

if selected_reservoir == "All Reservoirs":
    st.subheader("📊 Overall Reservoir System Health")
    
    col1, col2, col3, col4 = st.columns(4)
    
    avg_health = latest_df['Health_Score'].mean()
    overall_health_status, overall_health_icon = get_health_status(avg_health)
    
    critical_flood = len(latest_df[latest_df['Flood_Risk_Level'] == "Critical"])
    critical_scarcity = len(latest_df[latest_df['Scarcity_Level'] == "Critical Shortage"])
    
    with col1:
        st.metric(
            label=f"{overall_health_icon} System Health Score",
            value=f"{avg_health:.1f}/100",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            label=f"🔴 Critical Flood Risk",
            value=f"{critical_flood} Reservoirs"
        )
    
    with col3:
        st.metric(
            label=f"🔴 Critical Water Shortage",
            value=f"{critical_scarcity} Reservoirs"
        )
    
    with col4:
        st.metric(
            label=f"🟢 Healthy Reservoirs",
            value=f"{len(latest_df[latest_df['Health_Status'].isin(['Excellent', 'Good'])])} Reservoirs"
        )
    
    st.markdown("---")


# ==========================================
# GENERATE AI INSIGHTS
# ==========================================

def generate_insights(latest_data):
    """Generate AI-style insights from the data"""
    insights = []
    recommendations = []
    
    # Get critical reservoirs
    critical_flood = latest_data[latest_data['Flood_Risk_Level'] == "Critical"]
    critical_scarcity = latest_data[latest_data['Scarcity_Level'] == "Critical Shortage"]
    poor_health = latest_data[latest_data['Health_Status'] == "Poor"]
    
    # Flood insights
    if len(critical_flood) > 0:
        insights.append({
            "title": "🔴 High Flood Risk Alert",
            "description": f"Found {len(critical_flood)} reservoir(s) at critical flood risk. Immediate monitoring required.",
            "priority": "Critical",
            "reservoirs": critical_flood['Reservoir_Name'].tolist()
        })
        recommendations.append("⚠️ Release water gradually from reservoirs at critical flood risk")
        recommendations.append("📢 Activate flood alert systems for affected areas")
    
    # Scarcity insights
    if len(critical_scarcity) > 0:
        insights.append({
            "title": "🔴 Water Scarcity Emergency",
            "description": f"Detected {len(critical_scarcity)} reservoir(s) with critical water shortage. Immediate conservation needed.",
            "priority": "Critical",
            "reservoirs": critical_scarcity['Reservoir_Name'].tolist()
        })
        recommendations.append("💧 Implement strict water conservation measures")
        recommendations.append("🚜 Prioritize water allocation for essential needs")
    
    # Poor health insights
    if len(poor_health) > 0:
        insights.append({
            "title": "🟠 Poor Reservoir Health",
            "description": f"{len(poor_health)} reservoir(s) are in poor health condition and need attention.",
            "priority": "High",
            "reservoirs": poor_health['Reservoir_Name'].tolist()
        })
        recommendations.append("🔍 Conduct thorough inspection of reservoirs in poor health")
        recommendations.append("📊 Increase monitoring frequency for at-risk reservoirs")
    
    # Healthy insights
    healthy = latest_data[latest_data['Health_Status'].isin(['Excellent', 'Good'])]
    if len(healthy) > (len(latest_data) * 0.7):
        insights.append({
            "title": "✅ Healthy Reservoir System",
            "description": f"Most reservoirs ({len(healthy)}/{len(latest_data)}) are in good or excellent health.",
            "priority": "Low",
            "reservoirs": healthy['Reservoir_Name'].tolist()
        })
        recommendations.append("💚 Continue current maintenance practices for healthy reservoirs")
        recommendations.append("📈 Optimize water distribution from surplus reservoirs")
    
    if not insights:
        insights.append({
            "title": "✅ System Status Stable",
            "description": "All reservoirs are within normal operating parameters.",
            "priority": "Low",
            "reservoirs": []
        })
    
    return insights, recommendations


# Get insights
insights, recommendations = generate_insights(latest_df)


# ==========================================
# DISPLAY AI INSIGHTS CARDS
# ==========================================

st.subheader("🤖 AI Generated Insights")
for idx, insight in enumerate(insights):
    with st.container():
        # Determine card color based on priority
        card_color = {
            "Critical": "linear-gradient(135deg, #ff6b6b, #ee5a6f)",
            "High": "linear-gradient(135deg, #ffa502, #ff7f50)",
            "Medium": "linear-gradient(135deg, #ffd700, #ffed4e)",
            "Low": "linear-gradient(135deg, #2ed573, #7bed9f)"
        }.get(insight['priority'], "linear-gradient(135deg, #70a1ff, #1e90ff)")
        
        st.markdown(f"""
        <div style="
            background: {card_color};
            padding: 20px;
            border-radius: 12px;
            color: white;
            margin-bottom: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        ">
            <h3 style="margin: 0 0 10px 0; font-size: 18px;">{insight['title']}</h3>
            <p style="margin: 0 0 10px 0; font-size: 15px;">{insight['description']}</p>
            {f'<p style="margin: 0; font-size: 14px; opacity: 0.9;"><strong>Affected Reservoirs:</strong> {", ".join(insight["reservoirs"][:5])}{"..." if len(insight["reservoirs"]) > 5 else ""}</p>' if insight['reservoirs'] else ''}
        </div>
        """, unsafe_allow_html=True)


# ==========================================
# DISPLAY AUTOMATIC RECOMMENDATIONS
# ==========================================

st.subheader("💡 Automatic Recommendations")
rec_col1, rec_col2 = st.columns(2)

for idx, rec in enumerate(recommendations):
    col = rec_col1 if idx % 2 == 0 else rec_col2
    with col:
        st.markdown(f"""
        <div style="
            background-color: #f0f9ff;
            border-left: 4px solid #0ea5e9;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 10px;
        ">
            {rec}
        </div>
        """, unsafe_allow_html=True)


st.markdown("---")


# ==========================================
# RESERVOIR-SPECIFIC ANALYTICS (if single selected)
# ==========================================

if selected_reservoir != "All Reservoirs":
    st.subheader(f"📋 Detailed Analysis: {selected_reservoir}")
    res_latest = latest_df[latest_df['Reservoir_Name'] == selected_reservoir].iloc[0]
    
    # Status Cards Row
    status_col1, status_col2, status_col3 = st.columns(3)
    
    with status_col1:
        health_bg = {
            "Excellent": "linear-gradient(135deg, #2ed573, #7bed9f)",
            "Good": "linear-gradient(135deg, #7bed9f, #b8e994)",
            "Fair": "linear-gradient(135deg, #ffd700, #ffed4e)",
            "Poor": "linear-gradient(135deg, #ff6b6b, #ee5a6f)"
        }.get(res_latest['Health_Status'], "linear-gradient(135deg, #70a1ff, #1e90ff)")
        
        st.markdown(f"""
        <div style="
            background: {health_bg};
            padding: 25px;
            border-radius: 15px;
            color: white;
            text-align: center;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        ">
            <h3 style="margin: 0 0 10px 0; font-size: 16px;">Reservoir Health</h3>
            <div style="font-size: 48px; font-weight: bold; margin: 10px 0;">{res_latest['Health_Icon']} {res_latest['Health_Score']}/100</div>
            <div style="font-size: 20px; margin-top: 10px;">{res_latest['Health_Status']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with status_col2:
        flood_bg = {
            "Critical": "linear-gradient(135deg, #ff6b6b, #ee5a6f)",
            "High": "linear-gradient(135deg, #ffa502, #ff7f50)",
            "Medium": "linear-gradient(135deg, #ffd700, #ffed4e)",
            "Low": "linear-gradient(135deg, #2ed573, #7bed9f)",
            "Minimal": "linear-gradient(135deg, #2ed573, #7bed9f)"
        }.get(res_latest['Flood_Risk_Level'], "linear-gradient(135deg, #70a1ff, #1e90ff)")
        
        st.markdown(f"""
        <div style="
            background: {flood_bg};
            padding: 25px;
            border-radius: 15px;
            color: white;
            text-align: center;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        ">
            <h3 style="margin: 0 0 10px 0; font-size: 16px;">Flood Risk Indicator</h3>
            <div style="font-size: 48px; font-weight: bold; margin: 10px 0;">{res_latest['Flood_Risk_Icon']} {res_latest['Flood_Risk_Score']}</div>
            <div style="font-size: 20px; margin-top: 10px;">{res_latest['Flood_Risk_Level']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with status_col3:
        scarcity_bg = {
            "Critical Shortage": "linear-gradient(135deg, #ff6b6b, #ee5a6f)",
            "Severe Shortage": "linear-gradient(135deg, #ffa502, #ff7f50)",
            "Moderate Shortage": "linear-gradient(135deg, #ffd700, #ffed4e)",
            "Stable": "linear-gradient(135deg, #2ed573, #7bed9f)",
            "Surplus": "linear-gradient(135deg, #2ed573, #7bed9f)"
        }.get(res_latest['Scarcity_Level'], "linear-gradient(135deg, #70a1ff, #1e90ff)")
        
        st.markdown(f"""
        <div style="
            background: {scarcity_bg};
            padding: 25px;
            border-radius: 15px;
            color: white;
            text-align: center;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        ">
            <h3 style="margin: 0 0 10px 0; font-size: 16px;">Water Scarcity Indicator</h3>
            <div style="font-size: 48px; font-weight: bold; margin: 10px 0;">{res_latest['Scarcity_Icon']} {res_latest['Scarcity_Score']}</div>
            <div style="font-size: 20px; margin-top: 10px;">{res_latest['Scarcity_Level']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Detailed metrics
    st.subheader("📈 Detailed Metrics")
    detail_col1, detail_col2, detail_col3, detail_col4 = st.columns(4)
    
    with detail_col1:
        st.metric(
            label="Current Storage",
            value=f"{res_latest['Storage']:.4f}",
            delta=f"{res_latest['Storage_Percentage']:.1f}% of capacity"
        )
    
    with detail_col2:
        st.metric(
            label="Current Level",
            value=f"{res_latest['Level']:.2f}",
            delta=f"{res_latest['Full_Reservoir_Level']:.2f} (Max)"
        )
    
    with detail_col3:
        st.metric(
            label="Live Capacity",
            value=f"{res_latest['Live_Capacity_FRL']:.4f}"
        )
    
    with detail_col4:
        st.metric(
            label="Basin",
            value=f"{res_latest['Basin']}"
        )


# ==========================================
# DISTRIBUTION VISUALIZATION
# ==========================================

if selected_reservoir == "All Reservoirs":
    st.subheader("📊 Health Score Distribution")
    health_hist = px.histogram(
        latest_df,
        x='Health_Score',
        nbins=20,
        title='Distribution of Reservoir Health Scores',
        color_discrete_sequence=['#1e90ff'],
        labels={'Health_Score': 'Health Score (0-100)'}
    )
    st.plotly_chart(health_hist, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌊 Flood Risk Distribution")
        flood_counts = latest_df['Flood_Risk_Level'].value_counts().reset_index()
        flood_counts.columns = ['Risk Level', 'Count']
        fig_flood = px.pie(
            flood_counts,
            values='Count',
            names='Risk Level',
            title='Flood Risk Levels',
            color_discrete_map={
                'Critical': '#ff6b6b',
                'High': '#ffa502',
                'Medium': '#ffd700',
                'Low': '#2ed573',
                'Minimal': '#2ed573'
            }
        )
        st.plotly_chart(fig_flood, use_container_width=True)
    
    with col2:
        st.subheader("💧 Water Scarcity Distribution")
        scarcity_counts = latest_df['Scarcity_Level'].value_counts().reset_index()
        scarcity_counts.columns = ['Scarcity Level', 'Count']
        fig_scarcity = px.pie(
            scarcity_counts,
            values='Count',
            names='Scarcity Level',
            title='Water Scarcity Levels',
            color_discrete_map={
                'Critical Shortage': '#ff6b6b',
                'Severe Shortage': '#ffa502',
                'Moderate Shortage': '#ffd700',
                'Stable': '#2ed573',
                'Surplus': '#2ed573'
            }
        )
        st.plotly_chart(fig_scarcity, use_container_width=True)


# Footer
st.markdown("---")
st.markdown(
    "<center>© 2024 AquaSense AI - Intelligent Analytics Dashboard</center>",
    unsafe_allow_html=True
)
