import json
import time

import sounddevice as sd
from vosk import KaldiRecognizer, Model


class AnkiCommandVocabulary:
    good: str
    again: str
    show: str
    stop: str

    def __init__(self, good, again, show, stop):
        self.good = good
        self.again = again
        self.show = show
        self.stop = stop

    def to_json(self):
        return json.dumps([self.good, self.again, self.show, self.stop])


def get_vocabulary(config: dict):
    good = config.get("good", "good")
    again = config.get("again", "again")
    show = config.get("show", "show")
    stop = config.get("stop", "stop")
    return AnkiCommandVocabulary(good, again, show, stop)


def initialize(vocab: AnkiCommandVocabulary):
    device = 1
    device_info = sd.query_devices(device, "input")
    samplerate = int(device_info["default_samplerate"])
    model = Model(model_path="model/vosk-model-small-en-us-0.15")
    stream = sd.RawInputStream(
        samplerate=samplerate,
        blocksize=8000,
        device=device,
        dtype="int16",
        channels=1,
    )
    recognizer = KaldiRecognizer(model, samplerate, vocab.to_json())
    return (device, samplerate, recognizer, stream)


def voice_control(
    stream: sd.RawInputStream,
    blocksize: int,
    recognizer: KaldiRecognizer,
    card_kind: str,
    vocab: AnkiCommandVocabulary,
    timeout: float
):
    start = time.time()
    while (time.time() - start) < timeout:
        data, _ = stream.read(blocksize)
        if recognizer.AcceptWaveform(bytes(data)):
            result = recognizer.Result()
            if result:
                result = json.loads(result)["text"]
                print(f"Speech recognizer: recognized text: {result}")
                if card_kind == "reviewQuestion":
                    if result == vocab.show or result == vocab.stop:
                        return result
                elif card_kind == "reviewAnswer":
                    if (
                        result == vocab.good
                        or result == vocab.again
                        or result == vocab.stop
                    ):
                        return result
    return "timeout"
