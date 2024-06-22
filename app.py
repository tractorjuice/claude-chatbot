# Importing required packages
import uuid, os
import streamlit as st
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

# Initial prompts
INIT_PROMPT = """
\n\nHuman: You are MapMentor, a trainer in Wardley Mapping. You will help the users learn about Wardley Mapping.
Here are some important rules for the interaction:
- Always stay in character, as MapMentor, a Wardley Mapping trainer.
- If you are unsure how to respond, respond with another question.
- Always use a liberationism pedagogy training approach.
- Remember to state which module of the course we are currently learning.
"""

TRAINING_PROMPT = """
Here is an outline for a training course that you will give to the user. It covers the key principles of Wardley Mapping:

Module 1 - Introduction to Wardley Mapping
- Purpose and benefits of mapping
- Understanding value chains and situational awareness
- Overview of doctrine and foundational concepts

Module 2 - Structure of Wardley Maps
- Components, activities, and the value chain
- Evolution axis and commodity forms
- Anchors, chains, and dependencies

Module 3 - Developing Wardley Maps
- Gathering insight on activities, capabilities, and needs
- Positioning and classifying map elements
- Adding annotations and context

Module 4 - Using Maps for Decision Making
- Identifying structural vs situational change
- Applying doctrine to strategic planning
- Mapping out competing value chains
- Developing actionable insights from maps

Module 5 - Advanced Concepts
- Ecosystem models and community maps
- Climate patterns and their impact
- Mapping organizational culture
- Handling uncertainty and unknowns

Module 6 - Facilitating Wardley Mapping
- Workshops for collaborative mapping
- Engaging leadership and stakeholders
- Promoting adoption and managing skeptics

For each module, we would provide concepts, examples, hands-on exercises, and practice activities to build skills.
Please let me know if you would like me to expand on any part of this high-level curriculum outline for a Wardley Mapping training course.
I'm happy to provide more details on how to effectively teach this methodology.
"""

INTRO_PROMPT = """
Hello, I'm MapMentor.

This course is designed as an interactive learning experience to build your skills in Wardley Mapping from the ground up. We will cover the key principles, components, and steps for creating powerful maps.

The course is organized into 6 modules:

Module 1 provides an introduction to the purpose, benefits, and foundational concepts of mapping. We discuss how it helps with situational awareness and strategic planning.
Module 2 focuses on the structure of Wardley Maps - the components like activities, evolution axis, dependencies. You'll learn how to visualize your value chain.
Module 3 is all about developing maps hands-on. We'll practice gathering insights, positioning elements, adding annotations to create meaningful maps.
Module 4 shifts to using completed maps for strategic analysis and decision making. You'll apply doctrine to interpret maps and generate insights.
Module 5 covers more advanced concepts like mapping ecosystems, organizational culture, and handling uncertainty.
Finally, Module 6 is on facilitating mapping workshops and driving adoption.

Each module includes concepts, examples, exercises, and practice activities to build your skills. You'll have opportunities to create maps, iterate on them, and apply them to scenario-based challenges.

I'm looking forward to exploring all aspects of Wardley Mapping with you in this course! Please let me know if you would like me to elaborate on any part of the curriculum.
"""

REG_PROMPT = """
\n\nHuman: Here is the user's question about Wardley Mapping:
<question>
{QUESTION}
</question>
\n\nAssistant: [MapMentor] <response>
"""

# Model details
MODEL = "claude-3-5-sonnet-20240620"

# Initializing session state variables
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": INTRO_PROMPT}]

if "all_prompts" not in st.session_state:
    st.session_state["all_prompts"] = INIT_PROMPT + TRAINING_PROMPT

# Streamlit page configuration
st.set_page_config(page_title="Anthropic - ChatBot")
st.sidebar.title("Anthropic - ChatBot")
st.sidebar.title("Wardley Mapping Mentor")
st.sidebar.divider()
st.sidebar.markdown("[Developed by Mark Craddock](https://twitter.com/mcraddock)", unsafe_allow_html=True)
st.sidebar.markdown("Current Version: 0.0.3")
st.sidebar.markdown("Using claude-3.5 API")
st.sidebar.markdown(st.session_state.session_id)
st.sidebar.divider()

# Input for API key
user_claude_api_key = st.sidebar.text_input("Enter your Anthropic API Key:", placeholder="sk-...", type="password")

# Handling API key
if user_claude_api_key:
    os.environ["ANTHROPIC_API_KEY"] = user_claude_api_key
    llm = ChatAnthropic(
        api_key=user_claude_api_key,
        model=MODEL,
        temperature=0,
        max_tokens=500,
        timeout=None,
        max_retries=2,
    )
    prompt_template = ChatPromptTemplate(
        input_variables=["question"],
        template=REG_PROMPT
    )
    chain = LLMChain(
        llm=llm,
        prompt_template=prompt_template
    )
else:
    st.warning("Please enter your Anthropic API key", icon="⚠️")
else:
    st.warning("Please enter your Anthropic Claude API key", icon="⚠️")

# Displaying chat messages
new_prompt = []
for message in st.session_state.messages:
    if message["role"] in ["user", "assistant"]:
        with st.chat_message(message["role"]):
            new_prompt.append(message["content"])
            st.markdown(message["content"])

# Processing user input
if user_claude_api_key:
    if user_input := st.chat_input("How can I help with Wardley Mapping?"):
        prompt = REG_PROMPT.format(QUESTION=user_input)
        st.session_state.all_prompts += prompt
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
        full_response = ""
        try:
            for response in client.completions.create(
                prompt=st.session_state.all_prompts,
                stop_sequences=["</response>"],
                model=MODEL,
                max_tokens_to_sample=500,
                stream=True,
                tags=["anthropic-chatbot", st.session_state.session_id]
            ):
                full_response += response.completion
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        except anthropic.APIConnectionError:
            st.error("The server could not be reached")
        except anthropic.RateLimitError:
            st.error("Rate limit exceeded. Please try again later.")
        except anthropic.APIStatusError as e:
            st.error(f"API error: {e.status_code}")
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.session_state.all_prompts += full_response
        prompt_token_count, completion_token_count, total_cost = count_used_tokens(prompt, full_response)
        total_tokens.markdown(f"Prompt: {prompt_token_count}  \nCompletion: {completion_token_count}  \nTotal Cost: ${total_cost}")
