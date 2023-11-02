#Importing required packages
import streamlit as st
import promptlayer
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
import uuid

INIT_PROMPT = """
\n\nHuman: You are MapMentor a trainer in Wardley Mapping. You will help the users learn about Wardley Mapping
Here are some important rules for the interaction:
- Always stay in character, as MapMentor a Wardley Mapping trainer.  
- If you are unsure how to respond, respond with another question.
- Always use a liberationism pedagogy training approach.

Here is the user's question about Wardley Mapping:
<question>
{QUESTION}
</question>
\n\nAssistant: [MapMentor] <response>
"""

# Anthropic Claude pricing: https://cdn2.assets-servd.host/anthropic-website/production/images/model_pricing_may2023.pdf
PRICE_PROMPT = 1.102E-5
PRICE_COMPLETION = 3.268E-5

#MODEL = "claude-1"
MODEL = "claude-2"
#MODEL = "claude-v1-100k"

new_prompt = []

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

if "all_prompts" not in st.session_state:
    st.session_state["all_prompts"] = []

def count_used_tokens(prompt, completion):
    prompt_token_count = client.count_tokens(prompt)
    completion_token_count = client.count_tokens(completion)

    prompt_cost = prompt_token_count * PRICE_PROMPT
    completion_cost = completion_token_count * PRICE_COMPLETION

    total_cost = prompt_cost + completion_cost

    return (
        "🟡 Used tokens this round: "
        + f"Prompt: {prompt_token_count} tokens, "
        + f"Completion: {completion_token_count} tokens - "
        + f"{format(total_cost, '.5f')} USD)"
    )
    
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
            new_prompt.append(message["content"])
            st.markdown(message["content"])
            
if user_claude_api_key:
    if user_input := st.chat_input("How can I help with Wardley Mapping?"):
        prompt = INIT_PROMPT.format(QUESTION = user_input)
        st.session_state.all_prompts += prompt
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.sidebar.write(st.session_state.all_prompts)
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
        full_response = ""
        try:
            for response in client.completions.create(
                prompt=st.session_state.all_prompts,
                stop_sequences=["</response>"],
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
        st.session_state.all_prompts += "".join(full_response.values())
        print(count_used_tokens(prompt, full_response))
