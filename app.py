import streamlit as st 
from llm_agent import ConversationAgent


st.set_page_config(page_title="Jarvis")
st.title("Barbe-Quasar")

if "conversation_agent" not in st.session_state:
	st.session_state.conversation_agent = ConversationAgent()
st.session_state.setdefault("messages", [])

for message in st.session_state.messages:
	with st.chat_message(message["role"]):
		if message.get("image_bytes"):
			st.image(message["image_bytes"], caption=message["image_name"])
		if message["content"]:
			st.markdown(message["content"])

chat_input = st.chat_input(
	"Que veux tu moussaillon ?",
	accept_file=True,
	file_type=["jpg", "jpeg", "png", "webp"],
	accept_audio=True
	)

if chat_input:
	user_text = (chat_input.text or "").strip()
	user_audio = chat_input.audio
	image_file = chat_input.files[0] if chat_input.files else None

	if user_audio:
		with st.spinner("J'écoute moussaillon..."):
			audio_text = st.session_state.conversation_agent.transcribe_audio(
				user_audio
			).strip()
	else:
		audio_text = ""

	user_input = "\n\n".join(
		part for part in (user_text, audio_text) if part
	)

	if image_file and not user_input:
		user_input = "Décris cette image et indique ce qu'il faut remarquer."

	if not user_input and not image_file:
		st.warning("Je n'ai reçu ni texte, ni audio, ni image.")
		st.stop()

	message = {"role": "user", "content": user_input}
	if image_file:
		message.update(
			{
				"image_bytes": image_file.getvalue(),
				"image_name": image_file.name,
			}
		)
	st.session_state.messages.append(message)
	
	with st.chat_message("user"):
		if image_file:
			st.image(image_file, caption=image_file.name)
		if user_input:
			st.markdown(user_input)

	response = st.session_state.conversation_agent.ask_llm(
		user_input,
		image_file=image_file,
	)
	st.session_state.messages.append({"role": "assistant", "content": response})

	with st.chat_message("assistant"):
		st.markdown(response)