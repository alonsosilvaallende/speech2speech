from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

import solara
from typing import List
from typing_extensions import TypedDict

class MessageDict(TypedDict):
    role: str
    content: str

import ipywebrtc
from ipywebrtc import AudioRecorder, CameraStream, AudioStream
from gtts import gTTS
import ipywidgets
from whispercpp import Whisper

w = Whisper('tiny')

import os
os.environ['OPENAI_API_BASE'] = "https://shale.live/v1"
os.environ['OPENAI_API_KEY'] = os.getenv("SHALE_API_KEY")

from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(temperature=0.7)

messages: solara.Reactive[List[MessageDict]] = solara.reactive([])
@solara.component
def Page():
    with solara.Column(style={"padding": "30px"}):
        solara.Title("Talk to Llama2")
        solara.Markdown("#Talk to Llama2")
        user_message_count = len([m for m in messages.value if m["role"] == "user"])
    
        def send(message):
            messages.value = [
                *messages.value,
                {"role": "user", "content": message},
            ]
    
        def response(message):
            messages.value = [
                *messages.value,
                {"role": "assistant", "content": llm.predict(message)}
            ]
            # recorder = ipywebrtc.AudioRecorder.element(filename='test', format='mp3')
            # display(recorder)
        def result():
            if messages.value !=[]: response(messages.value[-1]["content"])
    
        result = solara.use_memo(result, [user_message_count])
    
        print(messages.value)
    
        with solara.Column(style={"width": "70%"}):
            with solara.lab.ChatBox():
                for item in messages.value:
                    with solara.lab.ChatMessage(
                        user=item["role"] == "user",
                        name="Assistant" if item["role"] == "assistant" else "User",
                        avatar_background_color="#33cccc" if item["role"] == "assistant" else "#ff991f",
                        border_radius="20px",
                    ):
                        solara.Markdown(item["content"])
                if messages.value != []:
                    tts = gTTS(messages.value[-1]["content"], lang='en')
                    tts.save("hola.wav")
                    audio = ipywidgets.Audio.from_file(filename="hola.wav", autoplay=True, loop=False)
                    display(audio)
                camera = CameraStream(constraints={'audio': True,'video':False})
                recorder = AudioRecorder(stream=camera)
                display(recorder)
                print(recorder.audio.value)
                if len(recorder.audio.value)!=0: 
                    print("hola")
                    recorder.save('example1.mp3')
                    result = w.transcribe(f"example1.mp3", lang="en")
                    text = w.extract_text(result)
                    print(text[0])
                    solara.Markdown(f"{text[0]}")
            solara.lab.ChatInput(send_callback=send)
