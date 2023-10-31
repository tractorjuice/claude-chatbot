#Importing required packages
import streamlit as st
import promptlayer
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
import uuid

SYSTEM_PROMPT = """
\n\n Human:You are MapMentor a trainer in Wardley Mapping. You will help the users learn about Wardley Mapping
Here are some important rules for the interaction:
- Always stay in character, as MapMentor a Wardley Mapping trainer.  
- If you are unsure how to respond, respond with another question.
- Always use a liberationism pedagogy training approach.

Here is the user's question about Wardley Mapping:
<question>
{{QUESTION}}
</question>

Please respond to the user’s questions within <response></response> tags.

Assistant: [MapMentor] <response>
"""

#MODEL = "claude-1"
MODEL = "claude-2"
#MODEL = "claude-v1-100k"

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    
st.set_page_config(page_title="Anthropic - ChatBot")
st.sidebar.title("Anthropic - ChatBot")
st.sidebar.divider()
st.sidebar.markdown("Developed by Mark Craddock](https://twitter.com/mcraddock)", unsafe_allow_html=True)
st.sidebar.markdown("Current Version: 0.0.0")
st.sidebar.markdown("Using claude-2 API")
st.sidebar.markdown(st.session_state.session_id)
st.sidebar.divider()

# Check if the user has provided an API key, otherwise default to the secret
user_claude_api_key = st.sidebar.text_input("Enter your Anthropic API Key:", placeholder="sk-...", type="password")

if "claude_model" not in st.session_state:
    st.session_state["claude_model"] = MODEL

if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "prompts" not in st.session_state:
    st.session_state["prompts"] = []
    
if user_claude_api_key:
    # If the user has provided an API key, use it
    # Swap out Anthropic for promptlayer
    promptlayer.api_key = st.secrets["PROMPTLAYER"]
    anthropic = promptlayer.anthropic
    client=anthropic.Anthropic(
      # defaults to os.environ.get("ANTHROPIC_API_KEY")
      api_key=user_claude_api_key,
    )
else:
    st.warning("Please enter your Anthropic Claude API key", icon="⚠️")

for message in st.session_state.messages:
    if message["role"] in ["user", "assistant"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
if user_claude_api_key:
    if prompt := st.chat_input("How can I help with Wardley Mapping?"):
        # "My name is {fname}, I'm {age}".format(fname = "John", age = 36)
        aprompt = f"{SYSTEM_PROMPT}.format(QUESTION = prompt")
        st.session_state.prompts.append(aprompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
        full_response = ""
        try:
            for response in client.completions.create(
                prompt=aprompt,
                #stop_sequences=[anthropic.HUMAN_PROMPT],
                model=MODEL,
                max_tokens_to_sample=1000,
                stream=True,
                pl_tags=["anthropic-chatbot", st.session_state.session_id]
            ):
                full_response += response.completion
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        except anthropic.APIConnectionError as e:
            st.error("The server could not be reached")
            print(e.__cause__)  # an underlying Exception, likely raised within httpx.
        except anthropic.RateLimitError as e:
            st.error("A 429 status code was received; we should back off a bit.")
        except anthropic.APIStatusError as e:
            st.error("Another non-200-range status code was received")
            st.error(e.status_code)
            st.error(e.response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.session_state.prompts.append(full_response)
