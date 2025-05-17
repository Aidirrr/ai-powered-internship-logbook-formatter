import streamlit as st
import requests
from streamlit_option_menu import option_menu

st.set_page_config(page_title="AI-Powered Internship Logbook Formatter", layout="wide")

# Sidebar Navigation
with st.sidebar:
    selected = option_menu(
        menu_title="Navigation",
        options=["Daily Log Formatter", "2-Week Summary", "About"],
        icons=["file-earmark-text", "calendar2-week", "info-circle"],
        menu_icon="cast",
        default_index=0
    )

st.title("📘 AI-Powered Internship Logbook Formatter")
st.write("Format your daily logs for Universiti Teknologi PETRONAS or PETRONAS using AI.")

# Sidebar Inputs
api_key = st.sidebar.text_input("Enter your OpenRouter API Key", type="password")

@st.cache_data(show_spinner=False)
def get_models(api_key):
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        response = requests.get("https://openrouter.ai/api/v1/models", headers=headers)
        if response.status_code == 200:
            return [model["id"] for model in response.json().get("data", [])]
        else:
            return ["openrouter/gpt-4", "openrouter/gpt-3.5-turbo", "openrouter/mistral"]
    except Exception:
        return ["openrouter/gpt-4", "openrouter/gpt-3.5-turbo", "openrouter/mistral"]

if api_key:
    model_list = get_models(api_key)
else:
    model_list = ["openrouter/gpt-4", "openrouter/gpt-3.5-turbo", "openrouter/mistral"]

model_choice = st.sidebar.selectbox("Choose LLM Model (via OpenRouter)", model_list)

openrouter_api_url = "https://openrouter.ai/api/v1/chat/completions"

def call_openrouter_api(prompt, model, api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that formats internship logs."},
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(openrouter_api_url, headers=headers, json=body)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"❌ Error: {response.status_code} - {response.text}"

def generate_prompt(log_type, content):
    if log_type == "UTP":
        return f"""
Format the following daily internship log into this structure:

**Objective**: 3-4 bullet points
**Details of the Day**: bullet points of what was done, expanded clearly
**Follow-Up**: 3-4 bullet points

Daily Log:
{content}
"""
    else:
        return f"""
Format the following daily internship log into clear bullet points only. No objectives or follow-up.

Daily Log:
{content}
"""

def generate_summary_prompt(two_weeks_content):
    return f"""
Summarize the following 2-week daily internship logs into a short section titled:
**Brief Description of Daily Activities**

The summary should be concise and describe the general tasks and learning points from the logs below:

{two_weeks_content}
"""

# Pages
if selected == "Daily Log Formatter":
    logbook_type = st.selectbox("Select Logbook Type", ["UTP", "PETRONAS"])
    user_input = st.text_area("✍️ Paste your daily log here:", height=300)

    if st.button("🚀 Generate Formatted Log"):
        if not user_input.strip():
            st.warning("Please enter your daily log.")
        elif not api_key.strip():
            st.warning("Please enter your OpenRouter API key.")
        else:
            prompt = generate_prompt(logbook_type, user_input)
            formatted_output = call_openrouter_api(prompt, model_choice, api_key)

            st.subheader("📄 Formatted Output")
            st.markdown(formatted_output)

            st.download_button(
                label="💾 Download as .txt",
                data=formatted_output,
                file_name=f"{logbook_type}_logbook.txt",
                mime="text/plain"
            )

            st.code(formatted_output, language="markdown")

elif selected == "2-Week Summary":
    two_week_input = st.text_area("🗓️ Paste 2 weeks of daily logs (for summary):", height=300)

    if st.button("📝 Generate 2-Week Summary"):
        if not two_week_input.strip():
            st.warning("Please enter 2 weeks of daily log data.")
        elif not api_key.strip():
            st.warning("Please enter your OpenRouter API key.")
        else:
            summary_prompt = generate_summary_prompt(two_week_input)
            summary_output = call_openrouter_api(summary_prompt, model_choice, api_key)

            st.subheader("🗂️ Brief Description of Daily Activities")
            st.markdown(summary_output)

            st.code(summary_output, language="markdown")

elif selected == "About":
    st.header("ℹ️ About")
    st.markdown("""
    **AI-Powered Internship Logbook Formatter** helps UTP and PETRONAS interns format their daily logs into clear and professional entries using the OpenRouter LLM API.

    - Built with ❤️ using Streamlit
    - Select from various LLMs available on OpenRouter
    - Format logs for both UTP and PETRONAS requirements
    - Generate summaries for easier reporting
    
    **Made by Khaidhir**, who is currently an intern at **PETRONAS**.
    """)