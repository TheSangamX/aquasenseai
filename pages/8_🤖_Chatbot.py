"""
AquaSense AI Chatbot - Gemini Powered
"""
import streamlit as st
import google.generativeai as genai
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import data_loader

# Set page config
st.set_page_config(
    page_title="AquaSense AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configure Gemini
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-2.5-flash")
    chat = model.start_chat(history=[])
except Exception as e:
    st.error(f"Error configuring Gemini: {e}")
    st.info("Please make sure your API key is set in .streamlit/secrets.toml")
    st.stop()

# Load and prepare data
@st.cache_data(ttl=3600)
def load_and_prepare_data():
    df = data_loader.load_reservoir_data("clean_reservoir_data.xls")
    df = data_loader.preprocess_data(df)
    
    # Calculate metrics
    latest_df = df.sort_values("Date").groupby("Reservoir_Name").last().reset_index()
    
    total_reservoirs = latest_df["Reservoir_Name"].nunique()
    
    # Flood risk
    def calculate_flood_risk(row):
        try:
            ratio = row["Level"] / row["Full_Reservoir_Level"]
            if ratio >= 0.95:
                return "Critical"
            elif ratio >= 0.85:
                return "High"
            elif ratio >= 0.7:
                return "Medium"
            else:
                return "Low"
        except:
            return "Unknown"
    latest_df["Flood_Risk"] = latest_df.apply(calculate_flood_risk, axis=1)
    critical_flood = len(latest_df[latest_df["Flood_Risk"] == "Critical"])
    high_flood = len(latest_df[latest_df["Flood_Risk"] == "High"])
    
    # Drought risk
    def calculate_drought_risk(row):
        storage_pct = row["Storage_Percentage"]
        if storage_pct < 20:
            return "Critical"
        elif storage_pct < 35:
            return "High"
        elif storage_pct < 50:
            return "Medium"
        else:
            return "Low"
    latest_df["Drought_Risk"] = latest_df.apply(calculate_drought_risk, axis=1)
    critical_drought = len(latest_df[latest_df["Drought_Risk"] == "Critical"])
    high_drought = len(latest_df[latest_df["Drought_Risk"] == "High"])
    
    # Health score
    def calculate_health(row):
        score = 0
        storage_pct = row["Storage_Percentage"]
        if storage_pct >= 80:
            score += 40
        elif storage_pct >= 60:
            score += 32
        elif storage_pct >= 40:
            score += 24
        elif storage_pct >= 20:
            score +=12
        else:
            score +=4
        
        try:
            level_ratio = row["Level"] / row["Full_Reservoir_Level"]
            if 0.4 <= level_ratio <= 0.8:
                score +=30
            elif 0.2 <= level_ratio < 0.4 or 0.8 < level_ratio <=0.95:
                score +=20
            else:
                score +=10
        except:
            score +=15
        
        capacity = row["Live_Capacity_FRL"]
        if capacity >1:
            score +=30
        elif capacity >0.5:
            score +=20
        else:
            score +=10
        
        return min(score, 100)
    
    latest_df["Health_Score"] = latest_df.apply(calculate_health, axis=1)
    healthy = len(latest_df[latest_df["Health_Score"] >=60])
    poor_health = len(latest_df[latest_df["Health_Score"] <40])
    
    # Most affected basin
    basin_stats = latest_df.groupby("Basin").agg(
        {"Health_Score":"mean", "Reservoir_Name":"count"}
    ).reset_index()
    basin_stats = basin_stats.sort_values("Health_Score", ascending=True)
    most_affected_basin = basin_stats.iloc[0]["Basin"] if len(basin_stats) >0 else "N/A"
    
    avg_storage = round(df["Storage"].mean(), 4)
    avg_level = round(df["Level"].mean(), 2)
    
    context = f"""
    AquaSense AI - Smart Reservoir Monitoring System Context
    
    Total Reservoirs Monitored: {total_reservoirs}
    Critical Flood Risk Reservoirs: {critical_flood}
    High Flood Risk Reservoirs: {high_flood}
    Critical Drought Risk Reservoirs: {critical_drought}
    High Drought Risk Reservoirs: {high_drought}
    Healthy Reservoirs (Score >=60): {healthy}
    Poor Health Reservoirs (Score <40): {poor_health}
    Most Affected Basin: {most_affected_basin}
    Average Storage: {avg_storage}
    Average Reservoir Level: {avg_level}
    
    You are AquaSense AI, an expert in reservoir monitoring, hydrology, and water resource management.
    Always provide answers in simple language, structured with:
    1. Answer
    2. Risk Level (if applicable)
    3. Recommendation (if applicable)
    """
    return context, latest_df

context, latest_df = load_and_prepare_data()

# Page UI
st.title("🤖 AquaSense AI Assistant")
st.subheader("Ask anything about reservoir data, risk, or predictions!")
st.markdown("---")

# Example questions
st.markdown("""
### 💡 Example Questions
- Which reservoirs need immediate attention?
- How many are at flood risk?
- What is the overall system health?
- Explain today's conditions.
- Which basin is most affected?
""")
st.markdown("---")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Welcome message
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Namaste! I'm your AquaSense AI Assistant. Ask me anything about reservoir data!"
    })

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
if user_input := st.chat_input("Ask about reservoir data..."):
    # Add user message to history
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                prompt = f"""
                You are AquaSense AI, an expert in reservoir monitoring and water resource management.
                Provide answers in clear, simple language.
                
                Context:
                {context}
                
                User Question:
                {user_input}
                
                Please respond with:
                1. Answer (main response)
                2. Risk Level (if applicable)
                3. Recommendation (if applicable)
                """
                
                response = chat.send_message(prompt)
                answer = response.text
                
                st.markdown(answer)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })
                
            except Exception as e:
                st.error(f"Oops! Something went wrong: {e}")

# Footer
st.markdown("---")
st.markdown("<center>Powered by Google Gemini 2.5 Flash</center>", unsafe_allow_html=True)
