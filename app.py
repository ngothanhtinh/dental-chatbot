import streamlit as st
<<<<<<< HEAD
from streamlit_chat import message as st_message
from langchain.prompts import PromptTemplate
>>>>>>> 96a62537fbd2ccb4e28fb723fcb7a45b98754b7c
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS

# Initialize session states
if "generated" not in st.session_state:
    st.session_state["generated"] = []
if "past" not in st.session_state:
    st.session_state["past"] = []
if "input" not in st.session_state:
    st.session_state["input"] = ""
if "stored_session" not in st.session_state:
    st.session_state["stored_session"] = []
if "temp" not in st.session_state:
    st.session_state["temp"] = ""
if "history" not in st.session_state:
    st.session_state.history = []

# Set up the Streamlit app layout
st.title("Dental Care AI Chatbot")

hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)


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


template = """Welcome to the virtual assistance of DR DEE Dental Clinic! As a dental assistant chatbot, your primary role is to provide customers with accurate information about dental care. Follow these guidelines to ensure effective and professional customer service:
    Initial Response: Always start your reply with a friendly greeting using 'Dạ' to acknowledge the customer and express your readiness to assist.
    Clarity and Brevity: Keep your answers clear and concise. Aim to provide precise information in response to customer inquiries.
    Context-Driven Responses: Utilize the provided context to inform your responses. The context should guide you in giving accurate and relevant information.
    {context}
    Seek Clarification if Needed: If the customer's query is unclear or lacks specific details, politely ask for more information to better address their concerns.
    Professionalism: Maintain a friendly yet professional demeanor throughout the interaction.
    Handling Unknown Answers: If you encounter a question you cannot answer, respond with: 'Anh/Chị vui lòng để lại số điện thoại, đội ngũ bác sỹ chuyên môn sẽ gọi điện tư vấn cho Anh/Chị ạ.' Avoid providing speculative or made-up information.
    Chat History Reference: Use the chat history to keep track of the conversation and ensure continuity in your responses.
    {chat_history}
    Language Requirement: All your responses should be in Vietnamese.
    When you receive a question from a customer:
    {question}
    Provide your answer in Vietnamese, following these guidelines for a helpful and professional customer service experience.
"""

CUSTOM_QUESTION_PROMPT = PromptTemplate(input_variables=["context", "question", "chat_history"], template=template)

API_O = st.secrets["OPENAI_API_KEY"]
# Session state storage would be ideal
if API_O:
    embeddings = OpenAIEmbeddings()
    db = FAISS.load_local('db', embeddings)
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 4})

    # Create an OpenAI instance
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.0)

    # Create the ConversationChain object with the specified configuration
    qa = ConversationalRetrievalChain.from_llm(
        llm=llm,
        chain_type='stuff',
        retriever=retriever,
        combine_docs_chain_kwargs={"prompt": CUSTOM_QUESTION_PROMPT},
        return_source_documents=True,
        return_generated_question=True,
    )
else:
    st.sidebar.warning('API key required to try this app.The API key is not stored in any form.')

# Get the user input
user_input = st.session_state.input_text

# Generate the output using the ConversationChain object and the user input, and add the input/output to the session
if user_input:
    output = qa({"question": user_input, "chat_history": st.session_state.history})
    st.session_state.past.append(user_input)
    st.session_state.generated.append(output['answer'])
    st.session_state.history.append({"message": user_input, "is_user": True})
    st.session_state.history.append({"message": output['answer'], "is_user": False})


# Display stored conversation sessions in the sidebar
for i, sublist in enumerate(st.session_state.stored_session):
    with st.sidebar.expander(label=f"Conversation-Session:{i}"):
        st.write(sublist)


# Allow the user to clear all stored conversation sessions
if st.session_state.stored_session:
    if st.sidebar.checkbox("Clear-all"):
        del st.session_state.stored_session

for i, chat in enumerate(st.session_state.history):
    st_message(**chat, key=str(i)) #unpacking
