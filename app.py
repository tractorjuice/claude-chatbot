#Importing required packages
import streamlit as st
import promptlayer
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
import uuid

MODEL = "claude-2"
#MODEL = "claude-v1-100k"

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    
st.set_page_config(page_title="Anthropic - Learn Wardley Mapping Bot")
st.sidebar.title("Anthropic - Learn Wardley Mapping")
st.sidebar.divider()
st.sidebar.markdown("Developed by Mark Craddock](https://twitter.com/mcraddock)", unsafe_allow_html=True)
st.sidebar.markdown("Current Version: 0.0.0")
st.sidebar.markdown("Using Anthropic Claude API")
st.sidebar.markdown(st.session_state.session_id)
st.sidebar.divider()
# Check if the user has provided an API key, otherwise default to the secret
user_claude_api_key = st.sidebar.text_input("Enter your Anthropic API Key:", placeholder="sk-...", type="password")

if "claude_model" not in st.session_state:
    st.session_state["claude_model"] = MODEL

if "messages" not in st.session_state:
    st.session_state["messages"] = []
    
if user_claude_api_key:
    # If the user has provided an API key, use it
    # Swap out Anthropic Claude for promptlayer
    promptlayer.api_key = st.secrets["PROMPTLAYER"]
    #client = promptlayer.anthropic_client
    anthropic = Anthropic(
      # defaults to os.environ.get("ANTHROPIC_API_KEY")
      api_key=user_claude_api_key,
    )
else:
    st.warning("Please enter your Anthropic Claude API key", icon="⚠️")

if user_claude_api_key:
    if prompt := st.chat_input("How can I help with Wardley Mapping?"):
        aprompt = f"{HUMAN_PROMPT} {prompt} {AI_PROMPT}"
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            response = anthropic.completions.create(
                prompt=aprompt,
                stop_sequences=[anthropic.HUMAN_PROMPT],
                model="claude-v1", #"claude-2" for Claude 2 model
                max_tokens_to_sample=100,
            )
            st.write("### Answer")
            st.write(response.completion)

            message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
