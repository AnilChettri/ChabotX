import streamlit as st
import spacy
from chatbot import Chatbot
from database import ConversationDatabase

##############################################################################
# 1) (Optional) Caching for performance if using Streamlit >= 1.18
##############################################################################
@st.cache_resource
def load_spacy_model(model_name="en_core_web_sm"):
    """
    Load a spaCy model only once. 
    Disable unneeded pipeline components (parser, ner, tagger) for extra speed.
    """
    return spacy.load(model_name, disable=["parser", "ner", "tagger"])

@st.cache_resource
def create_chatbot(intents_file='intents.json', model_name='en_core_web_sm'):
    """
    Instantiate your Chatbot class that internally uses spaCy.
    """
    return Chatbot(intents_file=intents_file, model_name=model_name)

@st.cache_resource
def create_database(db_path='conversations.db'):
    """
    Returns an instance of your SQLite-based ConversationDatabase class.
    """
    return ConversationDatabase(db_path=db_path)

##############################################################################
# 2) Streamlit Page Config (must be the first Streamlit command)
##############################################################################
st.set_page_config(page_title="Friendly Chatbot", layout="centered")

##############################################################################
# 3) Initialize resources only once
##############################################################################
nlp = load_spacy_model("en_core_web_sm")
chatbot = create_chatbot("intents.json", "en_core_web_sm")
db = create_database("conversations.db")

##############################################################################
# 4) Helper function: show user/bot messages in colored "bubbles"
##############################################################################
def display_message_bubble(message, is_user=True):
    """
    Displays the message in a simple colored div. 
    """
    if is_user:
        st.markdown(
            f"""
            <div style='text-align: right; 
                        background-color: #c1ffc1; 
                        color: #000;
                        border-radius: 10px; 
                        margin: 10px; 
                        padding: 10px; 
                        display: inline-block; 
                        max-width: 60%;'>
                <strong>You:</strong> {message}
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div style='text-align: left; 
                        background-color: #add8e6; 
                        color: #000;
                        border-radius: 10px; 
                        margin: 10px; 
                        padding: 10px; 
                        display: inline-block; 
                        max-width: 60%;'>
                <strong>Bot:</strong> {message}
            </div>
            """,
            unsafe_allow_html=True
        )

##############################################################################
# 5) Main Streamlit logic
##############################################################################
def main():
    st.title("My Advanced Friendly Chatbot \U0001F916")
    st.write("A virtual friend that uses spaCy for advanced NLP and stores conversations in SQLite.")

    # A) Initialize in-memory message list from DB if needed
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
        recent_messages = db.get_recent_messages(limit=10)
        for timestamp, user_msg, bot_msg in recent_messages:
            st.session_state["messages"].append(("user", user_msg))
            st.session_state["messages"].append(("bot", bot_msg))

    # B) Optional: Show entire chat history
    if st.button("Show Chat History"):
        all_history = db.get_recent_messages(limit=50)
        st.write("### Full Conversation History (Last 50 Messages):")
        for timestamp, user_msg, bot_msg in all_history:
            display_message_bubble(user_msg, is_user=True)
            display_message_bubble(bot_msg, is_user=False)
        st.write("---")

    # C) Text input for the user message (no session key).
    user_text = st.text_input("Type your message here:")

    # D) Send button
    if st.button("Send"):
        text_stripped = user_text.strip()
        if text_stripped:
            # Get the bot's response
            bot_response = chatbot.chat(text_stripped)
            
            # Detect mood-based intents and provide additional responses
            if "I'm feeling" in text_stripped or "I'm sad" in text_stripped:
                bot_response += "\nRemember, it's okay to feel this way. I'm here for you!"

            db.add_message(text_stripped, bot_response)
            st.session_state["messages"].append(("user", text_stripped))
            st.session_state["messages"].append(("bot", bot_response))
        else:
            st.warning("Please enter some text before clicking Send.")

    # E) Clear Chat History button
    if st.button("Clear Chat History"):
        st.session_state["messages"] = []  # Clear in-memory history
        db.clear_all_messages()  # Clear database
        st.success("Chat history cleared successfully!")

    st.write("---")

    # F) Display the conversation from session_state
    for role, msg in st.session_state["messages"]:
        display_message_bubble(msg, is_user=(role == "user"))

##############################################################################
# 6) Run App
##############################################################################
if __name__ == "__main__":
    main()
