"""
AquaSense AI Chatbot - OpenRouter Powered
"""
import streamlit as st
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

def get_fallback_response(user_input, metrics):
    user_input = user_input.lower()
    
    if any(keyword in user_input for keyword in ["flood", "flood risk", "flooding"]):
        return f"""
        1. **Answer**: There are **{metrics['critical_flood']} reservoirs at critical flood risk** and **{metrics['high_flood']} at high risk**.
        
        2. **Risk Level**: High
        
        3. **Recommendation**: Monitor these reservoirs closely, consider controlled water releases, and activate flood alert systems for nearby areas.
        """
    
    if any(keyword in user_input for keyword in ["drought", "water scarcity", "dry"]):
        return f"""
        1. **Answer**: There are **{metrics['critical_drought']} reservoirs at critical drought risk** and **{metrics['high_drought']} at high risk**.
        
        2. **Risk Level**: High
        
        3. **Recommendation**: Implement water conservation measures, prioritize essential water usage, and consider groundwater recharge programs.
        """
    
    if any(keyword in user_input for keyword in ["health", "system health", "healthy"]):
        return f"""
        1. **Answer**: Out of {metrics['total_reservoirs']} reservoirs, **{metrics['healthy']} are in good health** and **{metrics['poor_health']} need immediate attention**.
        
        2. **Risk Level**: Moderate
        
        3. **Recommendation**: Focus on reservoirs in poor health, conduct inspections, and optimize water allocation.
        """
    
    if any(keyword in user_input for keyword in ["basin", "basins", "most affected"]):
        return f"""
        1. **Answer**: The most affected basin is **{metrics['most_affected_basin']}**.
        
        2. **Risk Level**: High
        
        3. **Recommendation**: Increase monitoring in this basin and implement targeted water management strategies.
        """
    
    if any(keyword in user_input for keyword in ["attention", "immediate", "urgent"]):
        total_critical = metrics['critical_flood'] + metrics['critical_drought']
        return f"""
        1. **Answer**: There are **{total_critical} reservoirs** that need immediate attention (critical flood or drought risk).
        
        2. **Risk Level**: Critical
        
        3. **Recommendation**: Prioritize these reservoirs for inspection, monitoring, and intervention.
        """
    
    # Default
    return f"""
    1. **Answer**: Hi! Here are today's key stats:
    - Total reservoirs: {metrics['total_reservoirs']}
    - Healthy reservoirs: {metrics['healthy']}
    - Critical flood risk: {metrics['critical_flood']}
    - Critical drought risk: {metrics['critical_drought']}
    
    2. **Risk Level**: Moderate
    
    3. **Recommendation**: Keep monitoring the system, especially reservoirs in critical categories.
    """

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
    
    metrics = {
        "total_reservoirs": total_reservoirs,
        "critical_flood": critical_flood,
        "critical_drought": critical_drought,
        "high_flood": high_flood,
        "high_drought": high_drought,
        "healthy": healthy,
        "poor_health": poor_health,
        "most_affected_basin": most_affected_basin,
        "avg_storage": avg_storage,
        "avg_level": avg_level,
    }
    
    return metrics, latest_df

metrics, latest_df = load_and_prepare_data()

supabase_available = False
supabase = None
try:
    from supabase import create_client

    supabase_url = st.secrets.get("SUPABASE_URL")
    supabase_anon_key = st.secrets.get("SUPABASE_ANON_KEY")

    if supabase_url and supabase_anon_key:
        supabase = create_client(supabase_url, supabase_anon_key)
        supabase_available = True
except Exception:
    supabase_available = False


def _get_query_params():
    try:
        return dict(st.query_params)
    except Exception:
        return st.experimental_get_query_params()


def _clear_query_params():
    try:
        st.query_params.clear()
    except Exception:
        st.experimental_set_query_params()


def _get_app_base_url():
    base = st.secrets.get("APP_BASE_URL")
    if base:
        return str(base).rstrip("/")
    return "http://localhost:8502"


def _get_redirect_to():
    return f"{_get_app_base_url()}/Chatbot"


if not supabase_available:
    st.error("Supabase auth is not configured. Add SUPABASE_URL and SUPABASE_ANON_KEY in .streamlit/secrets.toml")
    st.stop()


params = _get_query_params()
oauth_code = params.get("code")
if isinstance(oauth_code, list):
    oauth_code = oauth_code[0] if oauth_code else None

oauth_error = params.get("error_description") or params.get("error")
if isinstance(oauth_error, list):
    oauth_error = oauth_error[0] if oauth_error else None

if oauth_error:
    st.error(f"Login failed: {oauth_error}")
    _clear_query_params()

if oauth_code and "supabase_user" not in st.session_state:
    try:
        auth_response = supabase.auth.exchange_code_for_session({"auth_code": oauth_code})
        user = getattr(auth_response, "user", None) or getattr(getattr(auth_response, "data", None), "user", None)
        st.session_state.supabase_user = user
        _clear_query_params()
        st.rerun()
    except Exception as e:
        st.error(f"Could not complete login: {str(e)[:200]}")
        _clear_query_params()

if "supabase_user" not in st.session_state:
    st.title("🔐 Sign in required")
    st.write("Continue with Google to access the AquaSense AI Assistant.")
    redirect_to = _get_redirect_to()
    if st.button("Continue with Google", type="primary", use_container_width=True):
        try:
            oauth = supabase.auth.sign_in_with_oauth(
                {"provider": "google", "options": {"redirect_to": redirect_to}}
            )
            url = getattr(oauth, "url", None) or getattr(getattr(oauth, "data", None), "url", None)
            if not url and hasattr(oauth, "get"):
                url = oauth.get("url")
            if not url:
                raise RuntimeError("OAuth URL not returned by Supabase.")
            st.session_state.oauth_url = url
        except Exception as e:
            st.error(f"Could not start Google login: {str(e)[:200]}")

    url = st.session_state.get("oauth_url")
    if url:
        st.link_button("Open Google Login", url, use_container_width=True)
        st.caption("After login, you will be redirected back automatically.")
    st.stop()

if st.sidebar.button("Logout", use_container_width=True):
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    for k in ["supabase_user", "oauth_url", "messages", "openrouter_messages"]:
        if k in st.session_state:
            del st.session_state[k]
    st.rerun()


# Configure OpenRouter
api_available = False
client = None
try:
    from openai import OpenAI

    openrouter_key = st.secrets.get("OPENROUTER_API_KEY")
    if openrouter_key:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=openrouter_key,
        )
        api_available = True
except Exception:
    api_available = False

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
    st.session_state.openrouter_messages = []
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
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    with st.chat_message("user"):
        st.markdown(user_input)
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                if api_available:
                    context = f"""
                    AquaSense AI - Smart Reservoir Monitoring System Context
                    Total Reservoirs Monitored: {metrics['total_reservoirs']}
                    Critical Flood Risk Reservoirs: {metrics['critical_flood']}
                    High Flood Risk Reservoirs: {metrics['high_flood']}
                    Critical Drought Risk Reservoirs: {metrics['critical_drought']}
                    High Drought Risk Reservoirs: {metrics['high_drought']}
                    Healthy Reservoirs (Score >=60): {metrics['healthy']}
                    Poor Health Reservoirs (Score <40): {metrics['poor_health']}
                    Most Affected Basin: {metrics['most_affected_basin']}
                    Average Storage: {metrics['avg_storage']}
                    Average Reservoir Level: {metrics['avg_level']}
                    
                    You are AquaSense AI, an expert in reservoir monitoring, hydrology, and water resource management.
                    Always provide answers in simple language, structured with:
                    1. Answer
                    2. Risk Level (if applicable)
                    3. Recommendation (if applicable)
                    """
                    
                    system_prompt = f"""
                    You are AquaSense AI, an expert in reservoir monitoring and water resource management.
                    Provide answers in clear, simple language.
                    
                    Context:
                    {context}
                    """
                    
                    # Build messages list
                    messages_for_api = [{"role": "system", "content": system_prompt}]
                    # Add history
                    for msg in st.session_state.openrouter_messages[-10:]: # last 10 messages
                        messages_for_api.append(msg)
                    messages_for_api.append({"role": "user", "content": user_input})
                    
                    response = client.chat.completions.create(
                        model="google/gemini-2.5-flash-preview-04-23",
                        messages=messages_for_api
                    )
                    answer = response.choices[0].message.content
                    st.session_state.openrouter_messages.append({"role": "user", "content": user_input})
                    st.session_state.openrouter_messages.append({"role": "assistant", "content": answer})
                else:
                    answer = get_fallback_response(user_input.lower(), metrics)
                
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
            except Exception as e:
                st.error(f"Oops! OpenRouter failed: {str(e)[:200]}")
                fallback_answer = get_fallback_response(user_input.lower(), metrics)
                st.markdown(fallback_answer)
                st.session_state.messages.append({"role": "assistant", "content": fallback_answer})

# Footer
st.markdown("---")
if api_available:
    st.markdown("<center>Powered by OpenRouter (Gemini 2.5 Flash)</center>", unsafe_allow_html=True)
else:
    st.markdown("<center>Powered by AquaSense AI Smart Responses</center>", unsafe_allow_html=True)
