# prerequisites: as described in https://alphacephei.com/vosk/install and also python module `sounddevice` (simply run command `pip install sounddevice`)
# Example usage using Dutch (nl) recognition model: `python test_microphone.py -m nl`
# For more help run: `python test_microphone.py -h`

import concurrent
import concurrent.futures
import queue
import sys
import threading

import sounddevice as sd
from vosk import KaldiRecognizer, Model


def initialize_speech_recognition():
    device = 1
    device_info = sd.query_devices(device, "input")

    # # soundfile expects an int, sounddevice provides a float:
    samplerate = int(device_info["default_samplerate"])  # type: ignore

    model = Model(model_path="model/vosk-model-small-en-us-0.15")
    recognizer = KaldiRecognizer(model, samplerate)
    return (device, samplerate, recognizer)


def producer(
    queue: queue.Queue,
    event: threading.Event,
    stream: sd.RawInputStream,
    blocksize: int,
    recognizer: KaldiRecognizer,
):
    print("Speech recognizer: started listening")
    while not event.is_set():
        data, _overflowed = stream.read(blocksize)
        if recognizer.AcceptWaveform(bytes(data)):
            result = recognizer.Result()
            print(f"Speech recognizer: recognized text: {result}")
            print("result", result)
            queue.put(result)

def consumer(queue: queue.Queue, event: threading.Event):
    """Pretend we're saving a number in the database."""
    while not event.is_set() or not queue.empty():
        message = queue.get(timeout=0.5)
        print("Consumer storing message: %s (size=%d)", message, queue.qsize())
        print("received msg", message)
    print("Consumer received event. Exiting")


# if __name__ == "__main__":
#     mic_queue = queue.Queue()

#     def callback(indata, frames, time, status):
#         """This is called (from a separate thread) for each audio block."""
#         if status:
#             print(status, file=sys.stderr)
#         mic_queue.put(bytes(indata))

#     device, samplerate, recognizer = initialize_speech_recognition()
#     print("Main: initialization complete")

#     with sd.RawInputStream(
#         samplerate=samplerate,
#         blocksize=8000,
#         device=device,
#         dtype="int16",
#         channels=1,
#         callback=callback,
#     ):
#         pipeline = queue.Queue(maxsize=10)
#         event = threading.Event()

#         with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
#             producer_future = executor.submit(producer, pipeline, event, recognizer)
#             consumer_future = executor.submit(consumer, pipeline, event)

#             input("Main: press enter to stop listening")
#             print("Main: about to set event")
#             event.set()

#             done = False
#             while not done:
#                 done = True
#                 if producer_future.running():
#                     print("producer running")
#                     done = False
#                 if consumer_future.running():
#                     print("consumer running")
#                     done = False
