from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import base64
import asyncio
import websockets
import pyaudio
from transformers import Wav2Vec2Processor

app = Flask(__name__)
CORS(app)

SAMPLE_RATE = 16000
FRAMES_PER_BUFFER = 3200
ASR_MODEL_NAME = "facebook/wav2vec2-large-960h-lv60-self"
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

tokenizer = Wav2Vec2Processor.from_pretrained(ASR_MODEL_NAME)

@app.route('/transcribe', methods=['POST'])
def transcribe():
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
                        await ws_connection.send(json.dumps({'audio_data': str(data)}))
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
                        # Process the transcription result as needed
                        print(transcription_text)
                    except Exception as e:
                        print(f'Something went wrong. Error code was {e.code}')
                        break

            await asyncio.gather(send_data(), receive_data())

    asyncio.run(speech_to_text())
    return jsonify({'message': 'Transcription started'})

if __name__ == '__main__':
    app.run()
