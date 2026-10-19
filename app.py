import streamlit as st 
from llm_agent import ConversationAgent


st.set_page_config(page_title="Jarvis")
st.title("Barbe-Quasar")

if "conversation_agent" not in st.session_state:
	st.session_state.conversation_agent = ConversationAgent()
st.session_state.setdefault("messages", [])

for message in st.session_state.messages:
	with st.chat_message(message["role"]):
		st.markdown(message["content"])

user_input = st.chat_input(
	"Que veux tu moussaillon ?",
	accept_file=False,
	accept_audio=False
	)

if user_input :
	st.session_state.messages.append({"role": "user", "content": user_input})
	
	with st.chat_message("user"):
		st.markdown(user_input)

	response = st.session_state.conversation_agent.ask_llm(user_input)
	st.session_state.messages.append({"role": "assistant", "content": response})

	with st.chat_message("assistant"):
		st.markdown(response)