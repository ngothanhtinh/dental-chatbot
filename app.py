import re
import streamlit as st
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationEntityMemory
from langchain.chains.conversation.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE
from langchain.llms import OpenAI
from langchain.callbacks import get_openai_callback


def clear_text():
    st.session_state["temp"] = st.session_state["input"]
    st.session_state["input"] = ""


# Define function to get user input
def get_text():
    input_text = st.text_input("You: ", st.session_state["input"], key="input",
                               placeholder="Ask me anything ...",
                               on_change=clear_text,
                               label_visibility='hidden')
    input_text = st.session_state["temp"]
    return input_text


# Define function to start a new chat
def new_chat():
    save = []
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        save.append("User:" + st.session_state["past"][i])
        save.append("Bot:" + st.session_state["generated"][i])
    st.session_state["stored_session"].append(save)
    st.session_state["generated"] = []
    st.session_state["past"] = []
    st.session_state["input"] = ""
    st.session_state.entity_memory.store = {}
    st.session_state.entity_memory.buffer.clear()


MODEL = "gpt-3.5-turbo-1106"
K = 100

API_O = st.secrets["OPENAI_API_KEY"]
# Session state storage would be ideal
if API_O:
    # Create an OpenAI instance
    llm = OpenAI(temperature=0,
                 openai_api_key=API_O,
                 model_name=MODEL,
                 verbose=False)

    # Create a ConversationEntityMemory object if not already created
    if 'entity_memory' not in st.session_state:
        st.session_state.entity_memory = ConversationEntityMemory(llm=llm, k=K)

    # Create the ConversationChain object with the specified configuration
    Conversation = ConversationChain(
        llm=llm,
        prompt=ENTITY_MEMORY_CONVERSATION_TEMPLATE,
        memory=st.session_state.entity_memory
    )
else:
    st.sidebar.warning('API key required to try this app.The API key is not stored in any form.')

# Get the user input
user_input = get_text()


def is_four_digit_number(string):
    pattern = r'^\d{4}$'  # Matches exactly four digits
    return bool(re.match(pattern, string))


# Generate the output using the ConversationChain object and the user input, and add the input/output to the session
if user_input:
    if st.session_state["balance"] > -0.03:
        with get_openai_callback() as cb:
            output = Conversation.run(input=user_input)
            st.session_state.past.append(user_input)
            st.session_state.generated.append(output)
            st.session_state["balance"] -= cb.total_cost * 4
    else:
        st.session_state.past.append(user_input)
        if is_four_digit_number(user_input):
            st.session_state["balance"] += st.session_state["deposit"]
            st.session_state.generated.append("Câu hỏi 1")
        else:
            st.session_state.generated.append("Câu hỏi 2")


# Display stored conversation sessions in the sidebar
for i, sublist in enumerate(st.session_state.stored_session):
    with st.sidebar.expander(label=f"Conversation-Session:{i}"):
        st.write(sublist)


# Allow the user to clear all stored conversation sessions
if st.session_state.stored_session:
    if st.sidebar.checkbox("Clear-all"):
        del st.session_state.stored_session


