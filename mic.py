import json
import time

import sounddevice as sd
from vosk import KaldiRecognizer, Model


def initialize():
    device = 1
    device_info = sd.query_devices(device, "input")
    samplerate = int(device_info["default_samplerate"])
    model = Model(model_path="model/vosk-model-small-en-us-0.15")
    recognizer = KaldiRecognizer(model, samplerate, '["again", "good", "show", "stop"]')
    stream = sd.RawInputStream(
        samplerate=samplerate,
        blocksize=8000,
        device=device,
        dtype="int16",
        channels=1,
    )
    return (device, samplerate, recognizer, stream)


def voice_control(
    stream: sd.RawInputStream,
    blocksize: int,
    recognizer: KaldiRecognizer,
    card_kind: str,
):
    timeout = 10
    start = time.time()
    while (time.time() - start) < timeout:
        data, _ = stream.read(blocksize)
        if recognizer.AcceptWaveform(bytes(data)):
            result = recognizer.Result()
            if result:
                result = json.loads(result)["text"]
                print(f"Speech recognizer: recognized text: {result}")
                if card_kind == "reviewQuestion":
                    if result == "show" or result == "stop":
                        return result
                elif card_kind == "reviewAnswer":
                    if result == "good" or result == "again":
                        return result
    return "timeout"
