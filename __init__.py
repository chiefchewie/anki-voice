import aqt.webview
from aqt import gui_hooks, mw
from aqt.operations import QueryOp

from .mic import initialize, voice_control

device, samplerate, recognizer, stream = initialize()


def on_webview_will_set_content(web_content: aqt.webview.WebContent, context) -> None:
    addon_package = mw.addonManager.addonFromModule(__name__)
    web_content.js.append(f"/_addons/{addon_package}/web/index.js")


def on_profile_did_open():
    stream.start()
    print("main: stream opened")


def on_profile_will_close():
    stream.stop()
    stream.close()
    print("main: stream closed")


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
        parent=mw,
        op=lambda _col: voice_control(stream, 8000, recognizer, kind),
        success=on_success,
    )
    op.with_progress('voice mode in progress... say "STOP" to stop').run_in_background()
    return text


gui_hooks.profile_did_open.append(on_profile_did_open)
gui_hooks.profile_will_close.append(on_profile_will_close)
gui_hooks.webview_will_set_content.append(on_webview_will_set_content)
gui_hooks.card_will_show.append(on_card_will_show)
