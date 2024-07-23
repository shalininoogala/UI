import streamlit as st
from gtts import gTTS
from io import BytesIO
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr

def clear_chat():
    if 'messages' in st.session_state:
        del st.session_state['messages']

def new_chat():
    st.session_state.messages = []

# Initialize chat history if not present
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar with options
with st.sidebar:
    st.title("Options")
    if st.button("New Chat"):
        new_chat()
        st.experimental_rerun()
    
    st.markdown("### Overview")
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"*User:* {message['content']}")

st.title("Tally AI Assistant")

# Custom CSS for layout
st.markdown('''
<style>
    .chat-container {
        height: 5vh; /* Adjust chat container height */
    }
</style>
''', unsafe_allow_html=True)

# Main chat interface
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

def text_to_speech_and_display(text):
    tts = gTTS(text=text, lang='en')
    audio_fp = BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)
    st.audio(audio_fp, format="audio/mp3")

# Display chat messages from history 
def displayChat():
    for message in st.session_state.messages:
        if message["content"] != "":
            with st.chat_message(message["role"]):  # Ensure this is available in your Streamlit version
                st.markdown(message["content"])
                if message["role"] == "assistant":
                    text_to_speech_and_display(message["content"])

# Layout for text input and microphone
text_input_col, mic_col = st.columns([4, 1])  # Adjust proportions as needed

# Mic recorder setup
with mic_col:
    audioBytes = mic_recorder(key='my_recorder', format="wav", start_prompt="🎙️", stop_prompt="🔴", just_once=True)

# Input from user
with text_input_col:
    prompt = st.chat_input("Ask your CA Buddy")

# Ensure processing is controlled
if audioBytes and "bytes" in audioBytes:
    audio_bytes = audioBytes["bytes"]
    
    # Save audio file
    audio_location = "Test.wav"
    with open(audio_location, "wb") as f:
        f.write(audio_bytes)
    
    # Perform transcription
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_location) as source:
            audio_data = recognizer.record(source)
            transcribedText = recognizer.recognize_google(audio_data)
    except sr.UnknownValueError:
        transcribedText = "Sorry, I could not understand the audio."
    except sr.RequestError:
        transcribedText = "Sorry, there was an error with the speech recognition service."
    
    # Add transcribed text to messages
    if transcribedText:
        st.session_state.messages.append({"role": "user", "content": transcribedText})
        st.session_state.messages.append({"role": "assistant", "content": "This is a simulated response to the transcription."})

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "assistant", "content": "This is a simulated response."})

# Display chat messages
displayChat()
