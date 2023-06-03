import streamlit as st
import asyncio
import websockets
import pyaudio
import json
import base64
from transformers import Wav2Vec2ForCTC, Wav2Vec2CTCTokenizer

SAMPLE_RATE = 16000
FRAMES_PER_BUFFER = 3200
ASSEMBLYAI_ENDPOINT = f'wss://api.assemblyai.com/v2/realtime/ws?sample_rate={SAMPLE_RATE}'

p = pyaudio.PyAudio()
audio_stream = p.open(
    frames_per_buffer=FRAMES_PER_BUFFER,
    rate=SAMPLE_RATE,
    format=pyaudio.paInt16,
    channels=1,
    input=True,
    start=False,
)

model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-large-960h-lv60-self")
tokenizer = Wav2Vec2CTCTokenizer.from_pretrained("facebook/wav2vec2-large-960h-lv60-self")

async def speech_to_text():
    """
    Asynchronous function used to perform real-time speech-to-text using Hugging Face ASR model
    """
    async with websockets.connect(
        ASSEMBLYAI_ENDPOINT,
        ping_interval=5,
        ping_timeout=20,
    ) as ws_connection:
        await asyncio.sleep(0.5)
        await ws_connection.recv()
        print('Websocket connection initialized')

        async def send_data():
            """
            Asynchronous function used for sending data
            """
            audio_stream.start_stream()
            while audio_stream.is_active():
                try:
                    data = audio_stream.read(FRAMES_PER_BUFFER)
                    data = base64.b64encode(data).decode('utf-8')
                    await ws_connection.send(json.dumps({'audio_data': data}))
                except Exception as e:
                    print(f'Something went wrong. Error code was {e.code}')
                    break
                await asyncio.sleep(0.5)

        async def receive_data():
            """
            Asynchronous function used for receiving data
            """
            while True:
                try:
                    received_msg = await ws_connection.recv()
                    transcription_text = json.loads(received_msg)['text']
                    st.text_area("Transcript", value=transcription_text, height=200)
                except Exception as e:
                    print(f'Something went wrong. Error code was {e.code}')
                    break

        await asyncio.gather(send_data(), receive_data())

def main():
    st.title("Real-Time Voice Transcription")

    if st.button("Start Transcription"):
        asyncio.run(speech_to_text())

if __name__ == '__main__':
    main()
