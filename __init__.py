import threading
import time
from typing import Any

import aqt.reviewer
import aqt.webview
import sounddevice as sd
from anki.collection import Collection
from aqt import gui_hooks, mw
from aqt.operations import QueryOp
from aqt.utils import showInfo

from .mic import foobar, initialize_speech_recognition, producer

mw.addonManager.setWebExports(__name__, r"web.*")

recognizer_event = threading.Event()
device, samplerate, recognizer = initialize_speech_recognition()

stream = sd.RawInputStream(
    samplerate=samplerate,
    blocksize=8000,
    device=device,
    dtype="int16",
    channels=1,
)

recog_thread = threading.Thread(
    target=producer,
    args=(recognizer_event, stream, 8000, recognizer, mw.reviewer),
)

PYCMD_IDENTIFIER = "py"


def on_reviewer_did_show_answer(_card):
    # reviewer = mw.reviewer
    # reviewer.bottom.web.eval("testFunction()")
    pass


def webview_message_handler(reviewer: aqt.reviewer.Reviewer, message: str):
    # print(f"!!! RECEIVED MESSAGE: {message}")
    pass


def on_webview_did_receive_js_message(
    handled: tuple[bool, Any], message: str, context: Any
):
    if not isinstance(context, aqt.reviewer.ReviewerBottomBar):
        return handled

    if not message.startswith(PYCMD_IDENTIFIER):
        return handled

    reviewer = context.reviewer
    response = webview_message_handler(reviewer, message)

    return (True, response)


def on_webview_will_set_content(web_content: aqt.webview.WebContent, context) -> None:
    addon_package = mw.addonManager.addonFromModule(__name__)
    web_content.js.append(f"/_addons/{addon_package}/web/index.js")


def on_profile_did_open():
    print("main: speech thread starting")
    stream.start()
    recognizer_event.clear()
    # recog_thread.start()
    print("main: speech thread started")


def on_profile_will_close():
    print("main: speech thread ending")
    stream.stop()
    stream.close()
    recognizer_event.set()
    # recog_thread.join()
    print("main: speech thread ended")


def on_success(op_val) -> None:
    print(f"on_success: op finished with return value {op_val}")
    if op_val == "show":
        mw.reviewer._showAnswer()
    elif op_val == "again":
        mw.reviewer._answerCard(1)
    elif op_val == "good":
        mw.reviewer._answerCard(mw.reviewer._defaultEase())


def on_card_will_show(text: str, card, kind: str):
    op = QueryOp(
        # the active window (main window in this case)
        parent=mw,
        # the operation is passed the collection for convenience; you can
        # ignore it if you wish
        op=lambda col: foobar(stream, 8000, recognizer, kind),
        # this function will be called if op completes successfully,
        # and it is given the return value of the op
        success=on_success,
    )
    op.with_progress('voice mode in progress... say "STOP" to stop').run_in_background()
    return text


gui_hooks.card_will_show.append(on_card_will_show)
gui_hooks.profile_did_open.append(on_profile_did_open)
gui_hooks.profile_will_close.append(on_profile_will_close)
gui_hooks.webview_will_set_content.append(on_webview_will_set_content)
gui_hooks.reviewer_did_show_answer.append(on_reviewer_did_show_answer)
gui_hooks.webview_did_receive_js_message.append(on_webview_did_receive_js_message)

# https://github.com/glutanimate/speed-focus-mode/
# automatically alert/show/again after x seconds
# can use what they did as inspiration
# to launch voice-recognizer process, and process voice cmd to show/answer accordingly

# basic idea:
# on_show_answer: from python hook, call a js function that sends a message (and also does the voice recognition)
# on_receive_js_msg: filter for the js message, determine the command (show/answer) and run it


# another idea:
# it looks like support for speech recognition libraries in javascript are sparse
#   does Anki support npm modules in their javascript files?
#   it looks like passing cardInfo to run on javascript might not work
#   or - use an npm project, and bundle it into raw js that gets exported to web/

# instead: make the add-on launch some sort of daemon that interfaces with anki connect
#   anki connect supports API calls such as answerCards or getCards
#   we will still need the hooks - for example, on_show_answer sends some sort of message
#   to the daemon so that the daemon knows what info to call anki-connect with
